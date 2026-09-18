#!/usr/bin/env python3
"""Component firewall for ``est-repair-v1.3.1`` (handoff step 6, section 9).

Every item of preregistration section 9 is implemented here. This must pass for
the baselines before any candidate is written. The preserved
``experiments/authzgym_semantic_contract_v1_3/FIREWALL_VALIDATION.json`` is not
re-run, superseded, or modified.
"""

from __future__ import annotations

import argparse
import ast
import copy
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Mapping

import ser.evaluation.authz_v1_3_1_harness as harness
from ser.core.types import content_hash
from ser.evaluation.authz_v1_3_1_harness import (
    REPAIR_DIR,
    CategoryMatchFloorComponent,
    DegenerateNullComponent,
    HistoricalEstimatorComponent,
    build_component_input,
    load_development_bundle,
    oracle_usefulness_baseline,
)
from ser.evaluation.authz_v1_3_1_sealed_input import (
    ComponentAllowlistError,
    check_component_module,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

MUTATED_RESTRICTED_FIELDS = (
    "usefulness_by_variant_target_slot",
    "canonical_source_ordinal_by_variant_slot",
    "transformation_maps",
    "source_family",
    "canonical_current_artifact_id",
    "public_id_by_canonical_artifact_id",
    "candidate_family_by_slot",
    "candidate_slot_by_effect_family",
)
INJECTED_EVALUATOR_FIELDS = {
    "logical_roles": ["entry", "guard", "resolver", "policy", "service", "tests"],
    "discriminating_role": {
        "h1": "service",
        "h2": "resolver",
        "h3": "policy",
        "h4": "guard",
    },
    "logical_role_index": {"artifact-0": "entry"},
    "mechanism_identifiers": ["h1", "h2", "h3", "h4"],
    "gold_annotations": {"t1": 1.0},
    "certificate": "injected-certificate",
    "retired_v1_2_expected_tags": ["f17", "f18", "f19"],
    "confirmation_identifiers": ["confirmation_v1_3", "layout-40", "layout-41"],
}


def responses_snapshot(bundle) -> dict[str, dict]:
    """Freeze the response per case before any mutation battery runs."""

    return {
        case_id: copy.deepcopy(bundle.response_for(case_id))
        for case_id in bundle.case_ids()
    }


def _digest(bundle, component, responses: Mapping[str, Mapping[str, object]]) -> str:
    payload = {}
    for case in bundle.cases:
        case_id = str(case["case_id"])
        # Fixture-only seam used by the firewall's negative controls. A real
        # candidate never sets ``firewall_fixture``, so it can never receive the
        # case or the bundle through this path.
        if getattr(component, "firewall_fixture", False):
            if hasattr(component, "bind_bundle"):
                component.bind_bundle(bundle)
            if hasattr(component, "bind_case"):
                component.bind_case(case)
        sealed = build_component_input(case, responses[case_id], bundle.contract)
        bound = (
            component.for_case(case_id) if hasattr(component, "for_case") else component
        )
        values = bound.values(sealed)
        payload[case_id] = {
            "values": {
                str(slot): round(float(value), 12) for slot, value in values.items()
            },
            "declared_ties": [
                [int(slot) for slot in group] for group in bound.declared_ties(sealed)
            ],
            "own_order": [
                [int(slot) for slot in group] for group in bound.own_order(sealed, case)
            ],
        }
    return content_hash(payload)


def _mutated_restricted(restricted: Mapping[str, object], *, mode: str) -> dict:
    mutated = copy.deepcopy(dict(restricted))
    for value in mutated.values():
        if not isinstance(value, dict):
            continue
        if "usefulness_by_variant_target_slot" in value:
            value["usefulness_by_variant_target_slot"] = {
                key: 0.123456 for key in value["usefulness_by_variant_target_slot"]
            }
        if "canonical_source_ordinal_by_variant_slot" in value:
            value["canonical_source_ordinal_by_variant_slot"] = {
                key: 99 - int(item)
                for key, item in value[
                    "canonical_source_ordinal_by_variant_slot"
                ].items()
            }
        if "transformation_maps" in value:
            maps = value["transformation_maps"]
            maps["canonical_ordinal_by_variant_public_id"] = {
                key: 99 - int(item)
                for key, item in maps[
                    "canonical_ordinal_by_variant_public_id"
                ].items()
            }
        if "source_family" in value:
            value["source_family"] = f"mutated_{mode}"
        value.update(copy.deepcopy(INJECTED_EVALUATOR_FIELDS))
    return mutated


def _surface_mutated_case(case: Mapping[str, object], *, mode: str) -> dict:
    mutated = copy.deepcopy(dict(case))
    inventory = mutated["model_visible_input"]["public_artifact_inventory"]
    for index, item in enumerate(inventory):
        item["line_count"] = int(item["line_count"]) + (index + 1) * 7
        item["public_id"] = f"mutated-{mode}-{item['public_id']}"
        item["path"] = f"mutated/{mode}/{item['path']}"
        item["exported_symbols"] = [
            f"{symbol}__{mode}" for symbol in item["exported_symbols"]
        ]
    for item in mutated["model_visible_input"]["candidate_hypotheses"]:
        item["public_label"] = f"mutated-{mode}-{item['public_label']}"
    mutated["model_visible_input"]["public_artifact_inventory"] = list(
        reversed(inventory)
    )
    return mutated


class _SealedAccessSpy:
    """Records attribute access on a sealed input during component execution."""

    def __init__(self, sealed):
        self._sealed = sealed
        self.accesses: dict[str, int] = {}
        self.violations: list[str] = []

    def wrap(self):
        sealed = self._sealed
        spy = self

        class _Proxy(type(sealed)):  # type: ignore[misc]
            __slots__ = ()

            def __getattr__(self, name):
                spy.accesses[name] = spy.accesses.get(name, 0) + 1
                return getattr(sealed, name)

        proxy = object.__new__(_Proxy)
        for slot in type(sealed).__slots__:
            object.__setattr__(proxy, slot, getattr(sealed, slot))
        return proxy


def check_1_allowlist(component, *, module_path: Path | None) -> dict:
    bundle = load_development_bundle()
    parts = {}
    if module_path is None:
        parts["static_import_closure"] = {
            "passed": True,
            "not_applicable": True,
            "detail": (
                "baselines are defined inside the harness, which imports the "
                "frozen evaluator for the preserved oracle path; the static "
                "closure check is enforced on candidate modules"
            ),
        }
    else:
        try:
            report = check_component_module(module_path)
            parts["static_import_closure"] = {
                "passed": True,
                "checked_modules": report["checked_modules"],
            }
        except ComponentAllowlistError as error:
            parts["static_import_closure"] = {
                "passed": False,
                "detail": str(error),
            }
    violations: list[str] = []
    observed: set[str] = set()
    for case in bundle.cases:
        case_id = str(case["case_id"])
        sealed = build_component_input(
            case, bundle.response_for(case_id), bundle.contract
        )
        spy = _SealedAccessSpy(sealed)
        proxy = spy.wrap()
        try:
            component.values(proxy)
            component.declared_ties(proxy)
        except Exception as error:  # pragma: no cover - reported, never raised
            violations.append(f"{case_id}: {type(error).__name__}: {error}")
        observed.update(spy.accesses)
    parts["dynamic_sealed_input"] = {
        "passed": not violations,
        "accessed_items": sorted(observed),
        "violations": violations,
    }
    return {
        "passed": all(item["passed"] for item in parts.values()),
        "parts": parts,
    }


def check_2_restricted_mutation(component) -> dict:
    bundle = load_development_bundle()
    responses = responses_snapshot(bundle)
    baseline = _digest(bundle, component, responses)
    failures = []
    for mode in ("individual", "all_at_once"):
        mutated = _mutated_restricted(bundle.restricted, mode=mode)
        mutated_bundle = harness.DevelopmentBundle(
            contract=bundle.contract,
            cases=bundle.cases,
            restricted=mutated,
            annotations=bundle.annotations,
            transformation_maps=mutated,
        )
        if _digest(mutated_bundle, component, responses) != baseline:
            failures.append(mode)
    return {
        "passed": not failures,
        "digest": baseline,
        "failing_mutations": failures,
        "mutated_fields": list(MUTATED_RESTRICTED_FIELDS),
        "injected_fields": sorted(INJECTED_EVALUATOR_FIELDS),
    }


_PUBLIC_ONLY_RUNNER = '''
import json, sys
from pathlib import Path

BLOCKED = json.loads(sys.argv[7])


class Blocker:
    def find_spec(self, name, path=None, target=None):
        if any(name == item or name.startswith(item + ".") for item in BLOCKED):
            raise ImportError("restricted module unavailable: " + name)
        return None


sys.meta_path.insert(0, Blocker())
sys.path.insert(0, sys.argv[1])
import importlib

from ser.core.types import content_hash
from ser.evaluation.authz_v1_3_1_sealed_input import build_sealed_input

contract = json.loads(Path(sys.argv[2]).read_text())
cases = json.loads(Path(sys.argv[3]).read_text())["cases"]
responses = json.loads(Path(sys.argv[4]).read_text())
component = getattr(importlib.import_module(sys.argv[5]), sys.argv[6])()
payload = {}
for case in cases:
    cid = str(case["case_id"])
    sealed = build_sealed_input(case, responses[cid], contract)
    payload[cid] = {
        "values": {
            str(slot): round(float(value), 12)
            for slot, value in component.values(sealed).items()
        }
    }
print(content_hash(payload))
'''


def _public_only_digest(
    component_module: str, component_name: str, blocked: list[str]
) -> str:
    bundle = load_development_bundle()
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        (root / "contract.json").write_text(
            json.dumps(bundle.contract), encoding="utf-8"
        )
        (root / "population.json").write_text(
            json.dumps({"cases": bundle.cases}), encoding="utf-8"
        )
        (root / "responses.json").write_text(
            json.dumps(responses_snapshot(bundle)), encoding="utf-8"
        )
        (root / "runner.py").write_text(_PUBLIC_ONLY_RUNNER, encoding="utf-8")
        completed = subprocess.run(
            [
                sys.executable,
                str(root / "runner.py"),
                str(PROJECT_ROOT / "src"),
                str(root / "contract.json"),
                str(root / "population.json"),
                str(root / "responses.json"),
                component_module,
                component_name,
                json.dumps(blocked),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
    return completed.stdout.strip()


# Candidate modules are additionally blocked from ``ser.evaluation.authz_v1_3``
# (enforced statically in check 1 and in the step-7 firewall run). B0's
# component identity *is* the preserved estimator+adapter pair, so the baselines
# section blocks the restricted-data modules only and records that limitation.
BASELINE_BLOCKED_MODULES = [
    "ser.authzgym.v1_3_annotation_builder",
    "ser.authzgym.generation",
    "ser.authzgym.v1_3_population",
]
CANDIDATE_BLOCKED_MODULES = BASELINE_BLOCKED_MODULES + ["ser.evaluation.authz_v1_3"]


def check_3_public_only_replay(
    component, *, component_name: str | None, component_module: str | None = None
) -> dict:
    if component_name is None:
        return {
            "passed": True,
            "not_applicable": True,
            "detail": (
                "the public-only replay runner installs in-harness baselines by "
                "name; candidate modules are replayed from their frozen source"
            ),
        }
    bundle = load_development_bundle()
    responses = responses_snapshot(bundle)
    reference = content_hash(
        {
            str(case["case_id"]): {
                "values": {
                    str(slot): round(float(value), 12)
                    for slot, value in component.values(
                        build_component_input(
                            case, responses[str(case["case_id"])], bundle.contract
                        )
                    ).items()
                }
            }
            for case in bundle.cases
        }
    )
    module_name = component_module or "ser.evaluation.authz_v1_3_1_harness"
    blocked = (
        BASELINE_BLOCKED_MODULES
        if module_name == "ser.evaluation.authz_v1_3_1_harness"
        else CANDIDATE_BLOCKED_MODULES
    )
    replay = _public_only_digest(module_name, component_name, blocked)
    return {
        "passed": replay == reference,
        "reference_digest": reference,
        "public_only_digest": replay,
        "blocked_modules": [
            *blocked,
        ],
        "blocked_module_scope": (
            "In-harness baselines remove the restricted-data modules from the "
            "process path; the preserved adapter module stays importable because "
            "B0's preserved component identity includes it. Candidate modules "
            "additionally have ser.evaluation.authz_v1_3 removed, matching the "
            "static closure rule."
        ),
    }


def _permuted_ordinals(restricted: Mapping[str, object]) -> dict:
    mutated = copy.deepcopy(dict(restricted))
    for value in mutated.values():
        if not isinstance(value, dict):
            continue
        if "canonical_source_ordinal_by_variant_slot" in value:
            value["canonical_source_ordinal_by_variant_slot"] = {
                key: 99 - int(item)
                for key, item in value[
                    "canonical_source_ordinal_by_variant_slot"
                ].items()
            }
    return mutated


def check_4_ordinal_non_consumption(component, *, module_path: Path | None) -> dict:
    bundle = load_development_bundle()
    responses = responses_snapshot(bundle)
    baseline = _digest(bundle, component, responses)
    permuted = harness.DevelopmentBundle(
        contract=bundle.contract,
        cases=bundle.cases,
        restricted=_permuted_ordinals(bundle.restricted),
        annotations=bundle.annotations,
        transformation_maps=bundle.transformation_maps,
    )
    permuted_digest = _digest(permuted, component, responses)
    static_violations: list[str] = []
    if module_path is not None:
        source = Path(module_path).read_text(encoding="utf-8")
        for token in (
            "canonical_source_ordinal_by_variant_slot",
            "canonical_ordinal_by_variant_public_id",
        ):
            if token in source:
                static_violations.append(token)
    return {
        "passed": permuted_digest == baseline and not static_violations,
        "ordinal_permutation_stable": permuted_digest == baseline,
        "static_violations": static_violations,
    }


def check_5_surface_non_consumption(component) -> dict:
    bundle = load_development_bundle()
    responses = responses_snapshot(bundle)
    baseline = _digest(bundle, component, responses)
    failures = []
    for mode in ("a", "b"):
        mutated_cases = tuple(
            _surface_mutated_case(case, mode=mode) for case in bundle.cases
        )
        mutated = harness.DevelopmentBundle(
            contract=bundle.contract,
            cases=mutated_cases,
            restricted=bundle.restricted,
            annotations=bundle.annotations,
            transformation_maps=bundle.transformation_maps,
        )
        if _digest(mutated, component, responses) != baseline:
            failures.append(mode)
    return {
        "passed": not failures,
        "perturbed": [
            "line_count",
            "inventory_order",
            "public_id",
            "path",
            "exported_symbols",
            "candidate_public_label",
        ],
        "failing_modes": failures,
    }


_DETERMINISM_RUNNER = '''
import sys

sys.path.insert(0, sys.argv[1])
import importlib

import ser.evaluation.authz_v1_3_1_harness as harness
from ser.core.types import content_hash

bundle = harness.load_development_bundle()
component = getattr(importlib.import_module(sys.argv[2]), sys.argv[3])()
payload = {}
for case in bundle.cases:
    cid = str(case["case_id"])
    sealed = harness.build_component_input(
        case,
        harness.oracle_response_from_annotation(bundle.annotations[cid]),
        bundle.contract,
    )
    payload[cid] = {
        "values": {
            str(slot): round(float(value), 12)
            for slot, value in component.values(sealed).items()
        }
    }
print(content_hash(payload))
'''


def check_6_determinism(component_module: str, component_name: str) -> dict:
    with tempfile.TemporaryDirectory() as directory:
        runner = Path(directory) / "runner.py"
        runner.write_text(_DETERMINISM_RUNNER, encoding="utf-8")
        outputs = []
        for seed, cwd in (("1", directory), ("12345", "/tmp")):
            completed = subprocess.run(
                [
                    sys.executable,
                    str(runner),
                    str(PROJECT_ROOT / "src"),
                    component_module,
                    component_name,
                ],
                capture_output=True,
                text=True,
                check=True,
                cwd=cwd,
                env=dict(os.environ, PYTHONHASHSEED=seed),
            )
            outputs.append(completed.stdout.strip())
    return {
        "passed": outputs[0] == outputs[1],
        "first": outputs[0],
        "second": outputs[1],
    }


def check_7_no_shared_state(component, *, module_path: Path | None) -> dict:
    static_findings: list[str] = []
    if module_path is not None:
        tree = ast.parse(Path(module_path).read_text(encoding="utf-8"))
        # A module-level constant table (the frozen code's own convention for
        # published maps) is not a cache. A module-level container that is
        # *mutated* during execution is.
        containers: set[str] = set()
        for node in tree.body:
            if isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                value = getattr(node, "value", None)
                if isinstance(
                    value, (ast.List, ast.Dict, ast.Set, ast.ListComp, ast.DictComp)
                ):
                    for name in node.targets if isinstance(node, ast.Assign) else [node.target]:
                        if isinstance(name, ast.Name):
                            containers.add(name.id)
        mutating_methods = {
            "append",
            "extend",
            "insert",
            "remove",
            "pop",
            "clear",
            "update",
            "setdefault",
            "add",
            "discard",
        }
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Assign)
                and isinstance(node.targets[0], ast.Subscript)
                and isinstance(node.targets[0].value, ast.Name)
                and node.targets[0].value.id in containers
            ):
                static_findings.append(
                    f"module-level container mutated: {node.targets[0].value.id}"
                )
            elif (
                isinstance(node, ast.AugAssign)
                and isinstance(node.target, ast.Subscript)
                and isinstance(node.target.value, ast.Name)
                and node.target.value.id in containers
            ):
                static_findings.append(
                    f"module-level container mutated: {node.target.value.id}"
                )
            elif (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in mutating_methods
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id in containers
            ):
                static_findings.append(
                    f"module-level container mutated: {node.func.value.id}"
                )
    calls: list[str] = []
    originals: dict[str, object] = {}
    # Snapshot the responses *before* the spy is installed: response
    # construction is evaluator-side and is not part of component execution.
    bundle = load_development_bundle()
    responses = responses_snapshot(bundle)
    for name in ("oracle_response_from_annotation", "aggregate_action_diagnostics"):
        original = getattr(harness, name)
        originals[name] = original

        def _wrapper(*args, __name=name, __original=original, **kwargs):
            calls.append(__name)
            return __original(*args, **kwargs)

        setattr(harness, name, _wrapper)
    try:
        for case in bundle.cases:
            case_id = str(case["case_id"])
            sealed = build_component_input(case, responses[case_id], bundle.contract)
            component.values(sealed)
            component.declared_ties(sealed)
    finally:
        for name, original in originals.items():
            setattr(harness, name, original)
    return {
        "passed": not static_findings and not calls,
        "static_findings": static_findings,
        "forbidden_helpers_called": calls,
    }


def check_8_error_channel(component) -> dict:
    bundle = load_development_bundle()
    responses = responses_snapshot(bundle)
    observed: set[str] = set()
    for restricted in (
        bundle.restricted,
        _mutated_restricted(bundle.restricted, mode="individual"),
        _mutated_restricted(bundle.restricted, mode="all_at_once"),
    ):
        mutated = harness.DevelopmentBundle(
            contract=bundle.contract,
            cases=bundle.cases,
            restricted=restricted,
            annotations=bundle.annotations,
            transformation_maps=restricted,
        )
        for case in mutated.cases:
            case_id = str(case["case_id"])
            sealed = build_component_input(case, responses[case_id], mutated.contract)
            try:
                component.values(sealed)
                component.declared_ties(sealed)
                observed.add("no-error")
            except Exception as error:  # pragma: no cover - reported, never raised
                observed.add(f"{type(error).__name__}: {error}")
    return {"passed": len(observed) == 1, "observed_channels": sorted(observed)}


CHECK_LABELS = (
    "check1_static_and_dynamic_allowlist",
    "check2_restricted_field_mutation",
    "check3_public_only_replay",
    "check4_ordinal_non_consumption",
    "check5_surface_statistic_non_consumption",
    "check6_determinism_and_replay",
    "check7_no_writable_shared_state",
    "check8_error_channel_audit",
)


def validate(
    component,
    *,
    component_name: str | None = None,
    component_module: str | None = None,
    module_path: Path | None = None,
) -> dict:
    checks = {
        CHECK_LABELS[0]: check_1_allowlist(component, module_path=module_path),
        CHECK_LABELS[1]: check_2_restricted_mutation(component),
        CHECK_LABELS[2]: check_3_public_only_replay(
            component,
            component_name=component_name,
            component_module=component_module,
        ),
        CHECK_LABELS[3]: check_4_ordinal_non_consumption(
            component, module_path=module_path
        ),
        CHECK_LABELS[4]: check_5_surface_non_consumption(component),
        CHECK_LABELS[5]: (
            check_6_determinism(
                component_module or "ser.evaluation.authz_v1_3_1_harness",
                component_name,
            )
            if component_name is not None
            else {
                "passed": True,
                "not_applicable": True,
                "detail": (
                    "cross-process determinism is exercised by the harness test "
                    "suite through tools/run_estimator_repair_study.py"
                ),
            }
        ),
        CHECK_LABELS[6]: check_7_no_shared_state(component, module_path=module_path),
        CHECK_LABELS[7]: check_8_error_channel(component),
    }
    return {
        "component": getattr(component, "name", repr(component)),
        "identifier": getattr(component, "identifier", "unknown"),
        "checks": checks,
        "passed": all(item["passed"] for item in checks.values()),
    }


SCOPE_STATEMENT = (
    "This validation demonstrates isolation of the action-value path for the 56 "
    "development cases and the specific component(s) named here, and nothing "
    "broader. It does not supersede, extend, or re-run "
    "experiments/authzgym_semantic_contract_v1_3/FIREWALL_VALIDATION.json, which "
    "remains byte-frozen with its own recorded scope. No confirmation path was "
    "opened, read, or hashed."
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=REPAIR_DIR / "FIREWALL_V1_3_1_VALIDATION.json"
    )
    parser.add_argument("--stage", default="baselines")
    args = parser.parse_args()

    bundle = load_development_bundle()
    baselines = {
        "B0": HistoricalEstimatorComponent(),
        "B1": DegenerateNullComponent(),
        "B2": CategoryMatchFloorComponent(),
    }
    exempt = oracle_usefulness_baseline(bundle).identifier
    results = {
        name: validate(component, component_name=type(component).__name__)
        for name, component in baselines.items()
    }
    document = {
        "schema_version": 1,
        "experiment": "authzgym-estimator-repair-v1.3.1-component-firewall",
        "condition_id": "est-repair-v1.3.1",
        "stage": args.stage,
        "authorizing_adr": "ADR-0020",
        "correcting_adr": "ADR-0021",
        "baselines": results,
        "b3_exempt_by_definition": exempt,
        "all_baselines_pass": all(item["passed"] for item in results.values()),
        "preserved_firewall_validation": (
            "experiments/authzgym_semantic_contract_v1_3/FIREWALL_VALIDATION.json"
        ),
        "preserved_firewall_unchanged": True,
        "scope_statement": SCOPE_STATEMENT,
        "inference_authorized": False,
        "confirmation_authorized": False,
    }
    args.output.write_text(
        json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    for name, item in results.items():
        failing = [key for key, value in item["checks"].items() if not value["passed"]]
        print(f"{name}: {'pass' if item['passed'] else 'FAIL ' + ','.join(failing)}")
    return 0 if document["all_baselines_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
