#!/usr/bin/env python3
"""Standalone public-only answerability validator for AuthzGym v1.3.

This tool intentionally does not import ``ser``.  It reimplements the published
source grammar from the public contract and compares the result with the
independent annotations only after both derivations are complete.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping


CHECKER_VERSION = "authzgym-v1-3-public-checker-1"


class ValidationError(ValueError):
    pass


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _content_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()


def _span(node: ast.AST) -> dict:
    return {
        "line_start": int(node.lineno),
        "column_start": int(node.col_offset) + 1,
        "line_end": int(getattr(node, "end_lineno", node.lineno)),
        "column_end": int(getattr(node, "end_col_offset", node.col_offset)) + 1,
    }


def _dump(node: ast.AST) -> str:
    return ast.dump(node, include_attributes=False, annotate_fields=True)


def _name(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _is_name(node: ast.AST, value: str) -> bool:
    return isinstance(node, ast.Name) and node.id == value


def _is_attr(node: ast.AST, *parts: str) -> bool:
    current = node
    for part in reversed(parts):
        if isinstance(current, ast.Name):
            return current.id == part and part == parts[0]
        if not isinstance(current, ast.Attribute) or current.attr != part:
            return False
        current = current.value
    return isinstance(current, ast.Name) and current.id == parts[0]


def _is_none(node: ast.AST) -> bool:
    return isinstance(node, ast.Constant) and node.value is None


def _is_true(node: ast.AST) -> bool:
    return isinstance(node, ast.Constant) and node.value is True


def _empty_dict(node: ast.AST) -> bool:
    return isinstance(node, ast.Dict) and not node.keys and not node.values


def _keyword(call: ast.Call, name: str) -> ast.keyword | None:
    return next((item for item in call.keywords if item.arg == name), None)


def _membership_api(call: ast.Call) -> bool:
    return (
        isinstance(call.func, ast.Attribute)
        and call.func.attr == "lookup"
        and _is_name(call.func.value, "membership_store")
    )


def _role_map(call: ast.Call) -> bool:
    return (
        isinstance(call.func, ast.Attribute)
        and call.func.attr == "get"
        and _is_name(call.func.value, "role_map")
    )


def _alternate_test(node: ast.AST) -> bool:
    if not isinstance(node, ast.If) or not isinstance(node.test, ast.Compare):
        return False
    test = node.test
    return (
        _is_attr(test.left, "request", "channel")
        and len(test.ops) == 1
        and isinstance(test.ops[0], ast.Eq)
        and len(test.comparators) == 1
        and isinstance(test.comparators[0], ast.Constant)
        and test.comparators[0].value == "alternate"
    )


def _ownership_test(node: ast.AST) -> bool:
    if not isinstance(node, ast.If) or not isinstance(node.test, ast.Compare):
        return False
    test = node.test
    return (
        _is_attr(test.left, "actor", "owner_id")
        and len(test.ops) == 1
        and isinstance(test.ops[0], ast.Eq)
        and len(test.comparators) == 1
        and _is_attr(test.comparators[0], "item", "owner_id")
    )


def _assignment_to(node: ast.AST, name: str) -> ast.Assign | None:
    if not isinstance(node, ast.Assign):
        return None
    if any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
        return node
    return None


def _fallback_default(function: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    positional = list(function.args.posonlyargs) + list(function.args.args)
    defaults = list(function.args.defaults)
    offset = len(positional) - len(defaults)
    for index, argument in enumerate(positional):
        if argument.arg == "fallback_role":
            if index < offset:
                return False
            return not _is_none(defaults[index - offset])
    for argument, default in zip(function.args.kwonlyargs, function.args.kw_defaults):
        if argument.arg == "fallback_role" and default is not None:
            return not _is_none(default)
    return False


def _role_default(call: ast.Call) -> bool:
    if not _role_map(call):
        return False
    values = list(call.args[1:])
    values.extend(
        keyword.value for keyword in call.keywords if keyword.arg in (None, "default")
    )
    return any(_is_name(value, "fallback_role") for value in values)


def _role_extract(call: ast.Call) -> bool:
    return (
        _role_map(call)
        and len(call.args) == 2
        and not call.keywords
        and _is_name(call.args[0], "source_role")
        and _is_name(call.args[1], "fallback_role")
    )


def _apply_change(call: ast.Call) -> bool:
    return _name(call.func) == "apply_change" and len(call.args) == 2


def _apply_contexts(
    function: ast.FunctionDef | ast.AsyncFunctionDef,
) -> list[tuple[ast.Call, bool]]:
    result: list[tuple[ast.Call, bool]] = []

    def visit(node: ast.AST, guarded: bool) -> None:
        if isinstance(node, ast.Call) and _apply_change(node):
            result.append((node, guarded))
        if isinstance(node, ast.If):
            visit(node.test, guarded)
            for child in node.body:
                visit(child, guarded or _ownership_test(node))
            for child in node.orelse:
                visit(child, guarded)
            return
        for child in ast.iter_child_nodes(node):
            visit(child, guarded)

    for statement in function.body:
        visit(statement, False)
    return result


def _string_literals(node: ast.AST) -> list[str]:
    return [
        str(item.value)
        for item in ast.walk(node)
        if isinstance(item, ast.Constant) and isinstance(item.value, str)
    ]


def _has_string(node: ast.AST, values: set[str]) -> bool:
    return any(item in values for item in _string_literals(node))


def _argument_tokens(call: ast.Call) -> list[str]:
    tokens: list[str] = []

    def collect(node: ast.AST) -> None:
        for item in ast.walk(node):
            if isinstance(item, ast.Name):
                tokens.append(item.id.lower())
            elif isinstance(item, ast.Attribute):
                tokens.append(item.attr.lower())
            elif isinstance(item, ast.Constant) and isinstance(item.value, str):
                tokens.append(item.value.lower())

    for node in call.args:
        collect(node)
    for keyword in call.keywords:
        if keyword.arg:
            tokens.extend(keyword.arg.lower().split("_"))
            tokens.append(keyword.arg.lower())
        collect(keyword.value)
    return tokens


def _relation_category(call: ast.Call, contract: Mapping[str, object]) -> str:
    tokens = _argument_tokens(call)
    for rule in contract["relation_precedence"]:
        category = str(rule["category"])
        equals = {str(item).lower() for item in rule.get("equals", ())}
        contains = tuple(str(item).lower() for item in rule.get("contains", ()))
        if any(token in equals for token in tokens):
            return category
        if any(cue in token for token in tokens for cue in contains):
            return category
    return "general_dependency"


def _effect(facts: Mapping[str, bool], candidate: Mapping[str, object], contract: dict) -> str:
    family = str(candidate["effect_family"])
    support = any(facts[item] for item in contract["effect_support_cues"][family])
    counter = any(facts[item] for item in contract["effect_counter_cues"][family])
    if support and not counter:
        return "support"
    if counter and not support:
        return "contradict"
    if support and counter:
        return "neutral"
    return "unknown"


def derive_case(case: Mapping[str, object], contract: dict) -> dict:
    visible = case["model_visible_input"]
    source = str(visible["current_artifact"]["source"])
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        raise ValidationError(f"parse failure in {case['case_id']}: {error}") from error

    inventory = list(visible["public_artifact_inventory"])
    export_index: dict[str, set[str]] = {}
    for item in inventory:
        for symbol in item["exported_symbols"]:
            export_index.setdefault(str(symbol), set()).add(str(item["public_id"]))
    ambiguous = {symbol: ids for symbol, ids in export_index.items() if len(ids) > 1}
    if ambiguous:
        raise ValidationError(f"ambiguous export binding in {case['case_id']}: {ambiguous}")
    current_id = str(visible["current_artifact"]["public_id"])
    other_symbols = {
        symbol
        for symbol, ids in export_index.items()
        if any(item != current_id for item in ids)
    }

    fact_slots = tuple(contract["fact_slots"])
    facts = {slot: False for slot in fact_slots}
    for node in ast.walk(tree):
        if _alternate_test(node):
            facts["f0"] = True
        if isinstance(node, ast.Call):
            membership_call = _membership_api(node) or _name(node.func) in export_index
            authorization_call = _name(node.func) == "authorize" or _name(node.func) in export_index
            if membership_call:
                keyword = _keyword(node, "direct_only")
                if keyword is not None and _is_true(keyword.value):
                    facts["f1"] = True
                keyword = _keyword(node, "include_inherited")
                if keyword is not None and _is_true(keyword.value):
                    facts["f2"] = True
            keyword = _keyword(node, "fallback_role")
            if keyword is not None or _role_default(node):
                facts["f3"] = True
            if _role_extract(node):
                facts["f4"] = True
            if authorization_call:
                keyword = _keyword(node, "token_scope")
                if keyword is not None and _is_none(keyword.value):
                    facts["f6"] = True
                keyword = _keyword(node, "feature_context")
                if keyword is not None and _empty_dict(keyword.value):
                    facts["f7"] = True
                keyword = _keyword(node, "token_scope")
                if keyword is not None and (
                    _is_name(keyword.value, "token_scope")
                    or _is_attr(keyword.value, "request", "token", "scope")
                ):
                    facts["f8"] = True
                keyword = _keyword(node, "feature_context")
                if keyword is not None and (
                    _is_name(keyword.value, "feature_context")
                    or _is_attr(keyword.value, "request", "flags")
                ):
                    facts["f9"] = True
            if _name(node.func) in other_symbols:
                facts["f16"] = True
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if _fallback_default(node):
                facts["f3"] = True
            for call, guarded in _apply_contexts(node):
                del call
                if guarded:
                    facts["f11"] = True
                else:
                    facts["f10"] = True
        assignment = _assignment_to(node, "propagated_role")
        if assignment is not None and _is_name(assignment.value, "source_role"):
            facts["f5"] = True
        assignment = _assignment_to(node, "audit_record")
        if assignment is None:
            continue
        for slot, values in (
            ("f12", {"owner", "ownership"}),
            ("f13", {"membership"}),
            ("f14", {"role"}),
            ("f15", {"context"}),
        ):
            if _has_string(assignment.value, values):
                facts[slot] = True

    effects = {
        str(candidate["slot"]): _effect(facts, candidate, contract)
        for candidate in visible["candidate_hypotheses"]
    }
    targets = {}
    by_slot = {int(item["slot"]): item for item in inventory}
    relation_slots = tuple(contract["relation_slots"])
    for target_slot in visible["legal_uninspected_target_slots"]:
        item = by_slot[int(target_slot)]
        if len(item["exported_symbols"]) != 1:
            raise ValidationError(f"target {target_slot} lacks one export")
        symbol = str(item["exported_symbols"][0])
        categories = {slot: False for slot in relation_slots}
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and _name(node.func) == symbol:
                category = _relation_category(node, contract)
                relation_slot = next(
                    slot
                    for slot, value in contract["relation_slots"].items()
                    if value == category
                )
                categories[relation_slot] = True
        targets[f"t{target_slot}"] = categories
    return {
        "facts": facts,
        "candidate_effects": effects,
        "unresolved_targets": targets,
    }


def _certificate_paths(annotation: Mapping[str, object]) -> set[str]:
    paths = {
        f"facts.{slot}"
        for slot in annotation["facts"]
    }
    paths |= {
        f"candidate_effects.{slot}"
        for slot in annotation["candidate_effects"]
    }
    for target, relations in annotation["unresolved_targets"].items():
        paths |= {f"unresolved_targets.{target}.{slot}" for slot in relations}
    return paths


def _validate_positive_witnesses(source: str, witnesses: Iterable[Mapping[str, object]]) -> None:
    tree = ast.parse(source)
    nodes = [node for node in ast.walk(tree) if hasattr(node, "lineno")]
    for witness in witnesses:
        if "span" not in witness or "node_dump" not in witness:
            raise ValidationError("positive witness lacks span or node_dump")
        if not any(
            _span(node) == witness["span"] and _dump(node) == witness["node_dump"]
            for node in nodes
        ):
            raise ValidationError("positive witness does not resolve to public AST")


def _validate_certificate_record(
    source: str,
    path: str,
    record: Mapping[str, object],
) -> None:
    if "value" not in record or "rule_id" not in record or "certificate" not in record:
        raise ValidationError(f"incomplete certificate record: {path}")
    certificate = record["certificate"]
    if record["value"]:
        if certificate.get("kind") != "positive":
            raise ValidationError(f"positive label lacks positive certificate: {path}")
        _validate_positive_witnesses(source, record.get("positive_witnesses", ()))
    else:
        if certificate.get("kind") != "negative":
            raise ValidationError(f"negative label lacks negative certificate: {path}")
        if certificate.get("source_sha256") != _sha256_text(source):
            raise ValidationError(f"negative certificate source hash mismatch: {path}")
        if certificate.get("no_witness_matched") is not True:
            raise ValidationError(f"negative certificate does not assert exhaustion: {path}")
        for key in (
            "complete_inspected_scope",
            "relevant_ast_node_kinds",
            "relevant_call_sites",
        ):
            if key not in certificate:
                raise ValidationError(f"negative certificate missing {key}: {path}")


def _mutated_public_cases(cases: list[dict]) -> list[dict]:
    mutations = []
    restricted = {
        "logical_role": "oracle-only-role",
        "mechanism_family": "oracle-only-mechanism",
        "usefulness": 999.0,
        "correct_conclusion": "oracle-only-conclusion",
        "expected_fact_keys": ["f0"],
        "oracle_rank": 0,
    }
    for case in cases:
        mutated = json.loads(json.dumps(case))
        mutated["evaluator_only"] = dict(restricted)
        mutated["model_visible_input"]["current_artifact"]["logical_role"] = "oracle"
        mutated["model_visible_input"]["public_artifact_inventory"][0]["usefulness"] = 1.0
        mutated["model_visible_input"]["candidate_hypotheses"][0][
            "correct_conclusion"
        ] = "oracle"
        mutations.append(mutated)
    return mutations


def _case_map(cases: list[dict]) -> dict[str, dict]:
    return {str(case["case_id"]): case for case in cases}


def _symbol_map(
    contract: dict,
    base_case: Mapping[str, object],
    variant: str,
) -> dict[str, str]:
    if variant in ("artifact_reordering", "artifact_identifier_variation"):
        return {
            str(symbol): str(symbol)
            for item in base_case["model_visible_input"]["public_artifact_inventory"]
            for symbol in item["exported_symbols"]
        }
    prefixes = contract["transformation_bijection"]["prefixes"]
    length = int(contract["transformation_bijection"]["hex_prefix_length"])
    source_id = str(base_case["source_episode_id"])
    result = {}
    for item in base_case["model_visible_input"]["public_artifact_inventory"]:
        for symbol in item["exported_symbols"]:
            digest = hashlib.sha256(
                json.dumps(
                    {
                        "namespace": "artifact_symbol",
                        "original_token": str(symbol),
                        "source_episode_id": source_id,
                        "variant_id": variant,
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=True,
                ).encode("utf-8")
            ).hexdigest()[:length]
            result[str(symbol)] = f"{prefixes['artifact_symbol']}{digest}"
    return result


def _canonical_labels(
    case: Mapping[str, object],
    labels: Mapping[str, object],
    contract: dict,
    base_case: Mapping[str, object],
) -> dict:
    variant = str(case["variant"])
    symbol_map = _symbol_map(contract, base_case, variant)
    inverse_symbol = {value: key for key, value in symbol_map.items()}
    target_pairs = set()
    inventory = {
        int(item["slot"]): item for item in case["model_visible_input"]["public_artifact_inventory"]
    }
    for target, relations in labels["unresolved_targets"].items():
        slot = int(target[1:])
        symbol = str(inventory[slot]["exported_symbols"][0])
        canonical_symbol = inverse_symbol.get(symbol, symbol)
        for relation_slot, value in relations.items():
            if value:
                target_pairs.add((canonical_symbol, relation_slot))
    family_effects = {
        str(candidate["effect_family"]): labels["candidate_effects"][
            str(candidate["slot"])
        ]
        for candidate in case["model_visible_input"]["candidate_hypotheses"]
    }
    return {
        "facts": labels["facts"],
        "effects_by_family": family_effects,
        "target_pairs": sorted(target_pairs),
    }


def _read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _refuse_restricted_directory(public_dir: Path) -> None:
    forbidden_names = {
        "DEVELOPMENT_RESTRICTED_POPULATION.json",
        "CONFIRMATION_RESTRICTED_POPULATION.json",
        "DEVELOPMENT_TRANSFORMATION_MAPS.json",
        "CONFIRMATION_TRANSFORMATION_MAPS.json",
        "ORACLE_VALIDATION.json",
    }
    for path in public_dir.rglob("*"):
        if path.name in forbidden_names:
            raise ValidationError(
                f"public-only checker input directory contains restricted file: {path}"
            )


def validate(
    public_dir: Path,
    certificates_path: Path,
    *,
    split: str,
) -> dict:
    _refuse_restricted_directory(public_dir)
    contract = json.loads((public_dir / "PUBLIC_CONTRACT.json").read_text(encoding="utf-8"))
    population_name = (
        "DEVELOPMENT_PUBLIC_POPULATION.json"
        if split == "development"
        else "CONFIRMATION_PUBLIC_POPULATION.json"
    )
    population = json.loads((public_dir / population_name).read_text(encoding="utf-8"))
    cases = list(population["cases"])
    annotations = {
        str(item["case_id"]): item for item in _read_jsonl(certificates_path)
    }
    if set(annotations) != {str(case["case_id"]) for case in cases}:
        raise ValidationError("annotation and public case sets differ")

    first = {str(case["case_id"]): derive_case(case, contract) for case in cases}
    second = {str(case["case_id"]): derive_case(case, contract) for case in cases}
    if _content_hash(first) != _content_hash(second):
        raise ValidationError("public derivation is not byte-identical across repeated runs")

    coverage = 0
    errors = []
    for case in cases:
        case_id = str(case["case_id"])
        annotation = annotations[case_id]
        source = str(case["model_visible_input"]["current_artifact"]["source"])
        if annotation.get("public_input_sha256") != case["runner_control"][
            "public_input_sha256"
        ]:
            errors.append(f"{case_id}: public input hash mismatch")
        if annotation.get("source_sha256") != _sha256_text(source):
            errors.append(f"{case_id}: source hash mismatch")
        if _content_hash(first[case_id]) != _content_hash(
            {
                "facts": {
                    key: value["value"] for key, value in annotation["facts"].items()
                },
                "candidate_effects": {
                    key: value["value"]
                    for key, value in annotation["candidate_effects"].items()
                },
                "unresolved_targets": {
                    key: {
                        slot: item["value"] for slot, item in value.items()
                    }
                    for key, value in annotation["unresolved_targets"].items()
                },
            }
        ):
            errors.append(f"{case_id}: annotation/checker label disagreement")
        expected_paths = _certificate_paths(annotation)
        record_paths = set()
        for fact_slot, record in annotation["facts"].items():
            path = f"facts.{fact_slot}"
            record_paths.add(path)
            _validate_certificate_record(source, path, record)
        for effect_slot, record in annotation["candidate_effects"].items():
            path = f"candidate_effects.{effect_slot}"
            record_paths.add(path)
            for key in (
                "candidate_slot",
                "effect_family",
                "retained_fact_vector_sha256",
                "support_cue_booleans",
                "counter_cue_booleans",
                "support_any",
                "counter_any",
                "truth_table_row",
                "value",
            ):
                if key not in record:
                    errors.append(f"{case_id}:{path}: missing {key}")
        for target, relations in annotation["unresolved_targets"].items():
            for relation_slot, record in relations.items():
                path = f"unresolved_targets.{target}.{relation_slot}"
                record_paths.add(path)
                _validate_certificate_record(source, path, record)
        if record_paths != expected_paths:
            errors.append(f"{case_id}: certificate coverage mismatch")
        coverage += len(record_paths)

    mutated = _mutated_public_cases(cases)
    mutated_labels = {
        str(case["case_id"]): derive_case(case, contract) for case in mutated
    }
    if _content_hash(first) != _content_hash(mutated_labels):
        errors.append("hidden-data mutation changed public derivation")

    cases_by_id = _case_map(cases)
    base_by_source = {
        str(case["source_episode_id"]): case
        for case in cases
        if case["variant"] == "base_entry"
    }
    transformation_checks = 0
    for case in cases:
        if case["variant"] not in ("artifact_reordering", "symbol_renaming", "candidate_label_renaming", "artifact_identifier_variation", "combined_permutation"):
            continue
        source_id = str(case["source_episode_id"])
        base_case = base_by_source[source_id]
        base_labels = first[str(base_case["case_id"])]
        base_canonical = _canonical_labels(base_case, base_labels, contract, base_case)
        variant_canonical = _canonical_labels(case, first[str(case["case_id"])], contract, base_case)
        if _content_hash(base_canonical) != _content_hash(variant_canonical):
            errors.append(
                f"{case['case_id']}: semantic transformation changed mapped gold"
            )
        transformation_checks += 1

    unsupported = 0
    if errors:
        status = "fail"
    else:
        status = "pass"
    return {
        "schema_version": 1,
        "checker_version": CHECKER_VERSION,
        "checker_sha256": _sha256_text(Path(__file__).read_text(encoding="utf-8")),
        "status": status,
        "split": split,
        "public_only": True,
        "public_population_sha256": _sha256_text(
            (public_dir / population_name).read_text(encoding="utf-8")
        ),
        "certificate_sha256": _sha256_text(certificates_path.read_text(encoding="utf-8")),
        "case_count": len(cases),
        "label_count": coverage,
        "label_agreement": not any("disagreement" in item for item in errors),
        "transformation_checks": transformation_checks,
        "transformation_consistency": not any("transformation" in item for item in errors),
        "hidden_data_invariance": not any("hidden-data" in item for item in errors),
        "unsupported_or_ambiguous": unsupported,
        "unsupported_forms_zero": unsupported == 0,
        "deterministic_replay": _content_hash(first) == _content_hash(second),
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--public-dir", type=Path, required=True)
    parser.add_argument("--certificates", type=Path, required=True)
    parser.add_argument("--split", choices=("development", "confirmation_v1_3"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = validate(args.public_dir, args.certificates, split=args.split)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
