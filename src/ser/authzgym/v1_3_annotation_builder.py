"""Production-side source-rule derivation for v1.3 annotations.

The standalone answerability checker intentionally does not import this module.
"""

from __future__ import annotations

import ast
import hashlib
from collections import Counter
from typing import Iterable, Mapping

from ser.core.types import content_hash

from .v1_3_contract import effect_from_facts


ANNOTATION_VERSION = "authzgym-v1-3-annotations-1"


class AnnotationV13Error(ValueError):
    """The public source cannot be certified under the v1.3 grammar."""


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _span(node: ast.AST) -> dict:
    return {
        "line_start": int(node.lineno),
        "column_start": int(node.col_offset) + 1,
        "line_end": int(getattr(node, "end_lineno", node.lineno)),
        "column_end": int(getattr(node, "end_col_offset", node.col_offset)) + 1,
    }


def _dump(node: ast.AST) -> str:
    return ast.dump(node, include_attributes=False, annotate_fields=True)


def _witness(node: ast.AST, rule_id: str, production: str) -> dict:
    return {
        "rule_id": rule_id,
        "production": production,
        "span": _span(node),
        "node_dump": _dump(node),
    }


def _call_name(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _is_name(node: ast.AST, name: str) -> bool:
    return isinstance(node, ast.Name) and node.id == name


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


def _string_literals(node: ast.AST) -> list[str]:
    return [
        str(item.value)
        for item in ast.walk(node)
        if isinstance(item, ast.Constant) and isinstance(item.value, str)
    ]


def _contains_string(node: ast.AST, values: set[str]) -> bool:
    return any(item in values for item in _string_literals(node))


def _alternate_if(node: ast.AST) -> bool:
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


def _ownership_if(node: ast.AST) -> bool:
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


def _keyword(call: ast.Call, name: str) -> ast.keyword | None:
    return next((item for item in call.keywords if item.arg == name), None)


def _membership_api_call(call: ast.Call) -> bool:
    return (
        isinstance(call.func, ast.Attribute)
        and call.func.attr == "lookup"
        and _is_name(call.func.value, "membership_store")
    )


def _role_map_get(call: ast.Call) -> bool:
    return (
        isinstance(call.func, ast.Attribute)
        and call.func.attr == "get"
        and _is_name(call.func.value, "role_map")
    )


def _call_argument_tokens(call: ast.Call) -> list[str]:
    tokens: list[str] = []

    def collect(node: ast.AST) -> None:
        for item in ast.walk(node):
            if isinstance(item, ast.Name):
                tokens.append(item.id.lower())
            elif isinstance(item, ast.Attribute):
                tokens.append(item.attr.lower())
            elif isinstance(item, ast.Constant) and isinstance(item.value, str):
                tokens.append(item.value.lower())

    for argument in call.args:
        collect(argument)
    for keyword in call.keywords:
        if keyword.arg:
            tokens.extend(part.lower() for part in keyword.arg.split("_"))
            tokens.append(keyword.arg.lower())
        collect(keyword.value)
    return tokens


def _relation_category(call: ast.Call, contract: Mapping[str, object]) -> str:
    tokens = _call_argument_tokens(call)
    for rule in contract["relation_precedence"]:
        category = str(rule["category"])
        contains = tuple(str(item).lower() for item in rule.get("contains", ()))
        equals = {str(item).lower() for item in rule.get("equals", ())}
        if any(token in equals for token in tokens):
            return category
        if any(cue in token for token in tokens for cue in contains):
            return category
    return "general_dependency"


def _export_index(inventory: Iterable[Mapping[str, object]]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for item in inventory:
        for symbol in item["exported_symbols"]:
            result.setdefault(str(symbol), set()).add(str(item["public_id"]))
    return result


def _public_export_call(call: ast.Call, export_index: Mapping[str, set[str]]) -> bool:
    name = _call_name(call.func)
    return name is not None and name in export_index


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
        if argument.arg != "fallback_role":
            continue
        if index < offset:
            return False
        default = defaults[index - offset]
        return not _is_none(default)
    for argument, default in zip(function.args.kwonlyargs, function.args.kw_defaults):
        if argument.arg == "fallback_role" and default is not None:
            return not _is_none(default)
    return False


def _role_map_default(call: ast.Call) -> bool:
    if not _role_map_get(call):
        return False
    values = list(call.args[1:])
    values.extend(
        keyword.value for keyword in call.keywords if keyword.arg in (None, "default")
    )
    return any(_is_name(value, "fallback_role") for value in values)


def _role_map_extract(call: ast.Call) -> bool:
    return (
        _role_map_get(call)
        and len(call.args) == 2
        and not call.keywords
        and _is_name(call.args[0], "source_role")
        and _is_name(call.args[1], "fallback_role")
    )


def _apply_change_call(call: ast.Call) -> bool:
    return _call_name(call.func) == "apply_change" and len(call.args) == 2


def _function_apply_change_contexts(
    function: ast.FunctionDef | ast.AsyncFunctionDef,
) -> list[tuple[ast.Call, bool]]:
    results: list[tuple[ast.Call, bool]] = []

    def visit(node: ast.AST, guarded: bool) -> None:
        if isinstance(node, ast.Call) and _apply_change_call(node):
            results.append((node, guarded))
        if isinstance(node, ast.If):
            visit(node.test, guarded)
            child_guarded = guarded or _ownership_if(node)
            for child in node.body:
                visit(child, child_guarded)
            for child in node.orelse:
                visit(child, guarded)
            return
        for child in ast.iter_child_nodes(node):
            visit(child, guarded)

    for statement in function.body:
        visit(statement, False)
    return results


def _relevant_node_counts(tree: ast.AST) -> dict[str, int]:
    counter = Counter(type(node).__name__ for node in ast.walk(tree))
    keys = ("Assign", "Call", "Compare", "Constant", "Dict", "FunctionDef", "If")
    return {key: counter[key] for key in keys}


def _negative_certificate(
    source: str,
    tree: ast.AST,
    rule_id: str,
    call_sites: list[dict],
) -> dict:
    return {
        "kind": "negative",
        "rule_id": rule_id,
        "complete_inspected_scope": "complete fixture module",
        "source_sha256": _sha256_text(source),
        "relevant_ast_node_kinds": _relevant_node_counts(tree),
        "relevant_call_sites": call_sites,
        "no_witness_matched": True,
    }


def derive_annotations(case: Mapping[str, object], contract: Mapping[str, object]) -> dict:
    visible = case["model_visible_input"]
    source = str(visible["current_artifact"]["source"])
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        raise AnnotationV13Error(f"source parse failed: {error}") from error

    inventory = list(visible["public_artifact_inventory"])
    current_id = str(visible["current_artifact"]["public_id"])
    export_index = _export_index(inventory)
    ambiguous = {symbol: ids for symbol, ids in export_index.items() if len(ids) > 1}
    if ambiguous:
        raise AnnotationV13Error(f"ambiguous exported-symbol binding: {ambiguous}")
    other_symbols = {
        symbol
        for symbol, ids in export_index.items()
        if any(artifact_id != current_id for artifact_id in ids)
    }

    fact_slots = tuple(contract["fact_slots"])
    rule_ids = {slot: f"v1.3-{slot}-{contract['fact_slots'][slot]}" for slot in fact_slots}
    witnesses: dict[str, list[dict]] = {slot: [] for slot in fact_slots}
    call_sites = [
        {"simple_callee": _call_name(node.func), "span": _span(node)}
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
    ]

    for node in ast.walk(tree):
        if _alternate_if(node):
            witnesses["f0"].append(
                _witness(node.test, rule_ids["f0"], "exact alternate-channel if test")
            )

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        membership_call = _membership_api_call(node) or _public_export_call(
            node, export_index
        )
        authorization_call = _call_name(node.func) == "authorize" or _public_export_call(
            node, export_index
        )
        keyword = _keyword(node, "direct_only")
        if membership_call and keyword is not None and _is_true(keyword.value):
            witnesses["f1"].append(
                _witness(keyword.value, rule_ids["f1"], "direct_only=True")
            )
        keyword = _keyword(node, "include_inherited")
        if membership_call and keyword is not None and _is_true(keyword.value):
            witnesses["f2"].append(
                _witness(keyword.value, rule_ids["f2"], "include_inherited=True")
            )
        keyword = _keyword(node, "fallback_role")
        if keyword is not None:
            witnesses["f3"].append(
                _witness(keyword.value, rule_ids["f3"], "call keyword fallback_role")
            )
        if _role_map_default(node):
            witnesses["f3"].append(
                _witness(node, rule_ids["f3"], "role_map.get fallback_role default")
            )
        if authorization_call:
            keyword = _keyword(node, "token_scope")
            if keyword is not None and _is_none(keyword.value):
                witnesses["f6"].append(
                    _witness(keyword.value, rule_ids["f6"], "token_scope=None")
                )
            keyword = _keyword(node, "feature_context")
            if keyword is not None and _empty_dict(keyword.value):
                witnesses["f7"].append(
                    _witness(
                        keyword.value,
                        rule_ids["f7"],
                        "feature_context={} empty literal",
                    )
                )
            keyword = _keyword(node, "token_scope")
            if keyword is not None and (
                _is_name(keyword.value, "token_scope")
                or _is_attr(keyword.value, "request", "token", "scope")
            ):
                witnesses["f8"].append(
                    _witness(keyword.value, rule_ids["f8"], "forward token scope")
                )
            keyword = _keyword(node, "feature_context")
            if keyword is not None and (
                _is_name(keyword.value, "feature_context")
                or _is_attr(keyword.value, "request", "flags")
            ):
                witnesses["f9"].append(
                    _witness(
                        keyword.value,
                        rule_ids["f9"],
                        "forward feature context",
                    )
                )
        if _role_map_extract(node):
            assignment = None
            for candidate_parent in ast.walk(tree):
                if isinstance(candidate_parent, ast.Assign) and node in ast.walk(
                    candidate_parent.value
                ):
                    assignment = candidate_parent
                    break
            if (
                assignment is not None
                and any(
                    isinstance(target, ast.Name) and target.id == "propagated_role"
                    for target in assignment.targets
                )
            ):
                witnesses["f4"].append(
                    _witness(
                        assignment,
                        rule_ids["f4"],
                        "exact role_map.get role transformation assignment",
                    )
                )
        if _call_name(node.func) in other_symbols:
            witnesses["f16"].append(
                _witness(
                    node,
                    rule_ids["f16"],
                    "call to another public inventory export",
                )
            )

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if _fallback_default(node):
                witnesses["f3"].append(
                    _witness(
                        node,
                        rule_ids["f3"],
                        "function declaration with non-None fallback_role default",
                    )
                )
        assignment = _assignment_to(node, "propagated_role")
        if assignment is not None and _is_name(assignment.value, "source_role"):
            witnesses["f5"].append(
                _witness(
                    assignment,
                    rule_ids["f5"],
                    "exact propagated_role = source_role assignment",
                )
            )
        assignment = _assignment_to(node, "audit_record")
        if assignment is None:
            continue
        if _contains_string(assignment.value, {"owner", "ownership"}):
            witnesses["f12"].append(
                _witness(
                    assignment,
                    rule_ids["f12"],
                    "audit_record ownership literal",
                )
            )
        if _contains_string(assignment.value, {"membership"}):
            witnesses["f13"].append(
                _witness(
                    assignment,
                    rule_ids["f13"],
                    "audit_record membership literal",
                )
            )
        if _contains_string(assignment.value, {"role"}):
            witnesses["f14"].append(
                _witness(
                    assignment,
                    rule_ids["f14"],
                    "audit_record role literal",
                )
            )
        if _contains_string(assignment.value, {"context"}):
            witnesses["f15"].append(
                _witness(
                    assignment,
                    rule_ids["f15"],
                    "audit_record context literal",
                )
            )

    unguarded: list[dict] = []
    guarded: list[dict] = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for call, is_guarded in _function_apply_change_contexts(node):
            witness = _witness(
                call,
                rule_ids["f11"] if is_guarded else rule_ids["f10"],
                "apply_change inside ownership guard"
                if is_guarded
                else "apply_change outside an ownership guard",
            )
            (guarded if is_guarded else unguarded).append(witness)
    witnesses["f10"].extend(unguarded)
    witnesses["f11"].extend(guarded)

    fact_record = {}
    for slot in fact_slots:
        items = witnesses[slot]
        value = bool(items)
        fact_record[slot] = {
            "value": value,
            "rule_id": rule_ids[slot],
            "positive_witnesses": items,
            "certificate": (
                {"kind": "positive"}
                if items
                else _negative_certificate(source, tree, rule_ids[slot], call_sites)
            ),
        }
    facts = {slot: fact_record[slot]["value"] for slot in fact_slots}
    effects = effect_from_facts(contract, list(visible["candidate_hypotheses"]), facts)
    fact_vector_sha256 = content_hash(facts)
    effect_record = {}
    support_map = contract["effect_support_cues"]
    counter_map = contract["effect_counter_cues"]
    for candidate in visible["candidate_hypotheses"]:
        slot = str(candidate["slot"])
        family = str(candidate["effect_family"])
        support = any(facts[item] for item in support_map[family])
        counter = any(facts[item] for item in counter_map[family])
        effect_record[slot] = {
            "value": effects[slot],
            "candidate_slot": slot,
            "effect_family": family,
            "retained_fact_vector_sha256": fact_vector_sha256,
            "support_cue_booleans": {
                item: bool(facts[item]) for item in support_map[family]
            },
            "counter_cue_booleans": {
                item: bool(facts[item]) for item in counter_map[family]
            },
            "support_any": support,
            "counter_any": counter,
            "truth_table_row": (
                f"S={int(support)},C={int(counter)}->{effects[slot]}"
            ),
        }

    target_record = {}
    legal_targets = tuple(int(item) for item in visible["legal_uninspected_target_slots"])
    inventory_by_slot = {int(item["slot"]): item for item in inventory}
    relation_slots = tuple(contract["relation_slots"])
    for target_slot in legal_targets:
        item = inventory_by_slot[target_slot]
        if len(item["exported_symbols"]) != 1:
            raise AnnotationV13Error(
                f"target {target_slot} does not have exactly one exported symbol"
            )
        symbol = str(item["exported_symbols"][0])
        matching_calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and _call_name(node.func) == symbol
        ]
        categories: dict[str, list[dict]] = {slot: [] for slot in relation_slots}
        for call in matching_calls:
            category = _relation_category(call, contract)
            relation_slot = next(
                slot
                for slot, value in contract["relation_slots"].items()
                if value == category
            )
            categories[relation_slot].append(
                _witness(
                    call,
                    f"v1.3-{relation_slot}-{category}",
                    f"visible call classified as {category}",
                )
            )
        target_record[f"t{target_slot}"] = {}
        for relation_slot in relation_slots:
            items = categories[relation_slot]
            target_record[f"t{target_slot}"][relation_slot] = {
                "value": bool(items),
                "rule_id": f"v1.3-{relation_slot}-{contract['relation_slots'][relation_slot]}",
                "positive_witnesses": items,
                "certificate": (
                    {"kind": "positive"}
                    if items
                    else _negative_certificate(
                        source,
                        tree,
                        f"v1.3-{relation_slot}-{contract['relation_slots'][relation_slot]}",
                        [
                            {
                                "simple_callee": symbol,
                                "span": _span(call),
                                "observed_category": _relation_category(call, contract),
                            }
                            for call in matching_calls
                        ],
                    )
                ),
            }

    return {
        "schema_version": 1,
        "annotation_version": ANNOTATION_VERSION,
        "case_id": case["case_id"],
        "split": case["split"],
        "source_episode_id": case["source_episode_id"],
        "variant": case["variant"],
        "public_input_sha256": case["runner_control"]["public_input_sha256"],
        "source_sha256": _sha256_text(source),
        "facts": fact_record,
        "candidate_effects": effect_record,
        "unresolved_targets": target_record,
        "annotation_hash": "",
    }


def seal_annotation(annotation: dict) -> dict:
    sealed = dict(annotation)
    sealed["annotation_hash"] = ""
    sealed["annotation_hash"] = content_hash(sealed)
    return sealed


def derive_case_annotations(
    case: Mapping[str, object], contract: Mapping[str, object]
) -> dict:
    return seal_annotation(derive_annotations(case, contract))


def labels_from_annotation(annotation: Mapping[str, object]) -> dict:
    return {
        "facts": {
            slot: bool(item["value"])
            for slot, item in annotation["facts"].items()
        },
        "candidate_effects": {
            slot: str(item["value"])
            for slot, item in annotation["candidate_effects"].items()
        },
        "unresolved_targets": {
            target: {
                slot: bool(value["value"]) for slot, value in relations.items()
            }
            for target, relations in annotation["unresolved_targets"].items()
        },
    }
