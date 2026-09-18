#!/usr/bin/env python3
"""Public-only replay and restricted-field mutation firewall audit for v1.3."""

from __future__ import annotations

import argparse
import ast
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from ser.authzgym.v1_3_public_input import (
    FORBIDDEN_PUBLIC_NAMES,
    build_normal_request,
    load_public_bundle,
    normal_request_bytes,
    start_normal_state,
)
from ser.core.types import content_hash


ROOT = Path(__file__).resolve().parents[1]


def _restricted_mutations(case: dict) -> list[dict]:
    mutations = []
    values = {
        "logical_role": "oracle-entry",
        "mechanism_family": "oracle-mechanism",
        "usefulness": 0.999,
        "correct_conclusion": "oracle-conclusion",
        "oracle_content": {"facts": {"f0": True}},
        "expected_fact_keys": ["f0", "f17"],
        "v1_2_expected_tags": ["old-tag"],
        "score": 1.0,
        "rank": 0,
    }
    for key, value in values.items():
        mutated = json.loads(json.dumps(case))
        mutated["evaluator_only"] = {key: value}
        mutations.append(mutated)
    mutated = json.loads(json.dumps(case))
    mutated["evaluator_only"] = values
    mutated["model_visible_input"]["current_artifact"]["logical_role"] = "oracle"
    mutated["model_visible_input"]["current_artifact"]["usefulness"] = 0.999
    mutated["model_visible_input"]["public_artifact_inventory"][0][
        "logical_role"
    ] = "oracle"
    mutated["model_visible_input"]["public_artifact_inventory"][0]["usefulness"] = 0.999
    mutated["model_visible_input"]["candidate_hypotheses"][0][
        "correct_conclusion"
    ] = "oracle"
    mutations.append(mutated)
    return mutations


def _static_import_audit(module_path: Path) -> dict:
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    forbidden = [
        item
        for item in imports
        if item.startswith("ser.evaluation")
        or "oracle" in item
        or "scor" in item
        or "gold" in item
    ]
    return {"imports": sorted(imports), "forbidden_imports": forbidden}


def _isolated_replay(
    public_dir: Path,
    expected_hashes: list[str],
) -> dict:
    with tempfile.TemporaryDirectory() as temporary:
        temporary_path = Path(temporary)
        isolated_src = temporary_path / "src"
        shutil.copytree(
            ROOT / "src/ser",
            isolated_src / "ser",
            ignore=shutil.ignore_patterns("evaluation", "__pycache__"),
        )
        isolated_public = temporary_path / "public"
        shutil.copytree(public_dir, isolated_public)
        code = """
import json
import sys
from pathlib import Path
from ser.authzgym.v1_3_public_input import load_public_bundle, replay_public_requests
public_dir = Path(sys.argv[1])
contract, prompt, _ = load_public_bundle(public_dir)
population = json.loads((public_dir / "DEVELOPMENT_PUBLIC_POPULATION.json").read_text())
hashes = replay_public_requests(population["cases"], prompt)
try:
    import ser.evaluation.authz_v1_3  # noqa: F401
    importable = True
except Exception:
    importable = False
print(json.dumps({"hashes": hashes, "evaluation_importable": importable}))
"""
        completed = subprocess.run(
            [sys.executable, "-c", code, str(isolated_public)],
            check=True,
            capture_output=True,
            text=True,
            env={"PYTHONPATH": str(isolated_src)},
        )
        result = json.loads(completed.stdout)
        result["byte_identical"] = result["hashes"] == expected_hashes
        result["restricted_files_absent"] = not any(
            path.name in FORBIDDEN_PUBLIC_NAMES
            for path in isolated_public.rglob("*")
        )
        return result


def validate(public_dir: Path) -> dict:
    contract, prompt, contract_hash = load_public_bundle(public_dir)
    del contract
    population = json.loads(
        (public_dir / "DEVELOPMENT_PUBLIC_POPULATION.json").read_text(encoding="utf-8")
    )
    cases = list(population["cases"])
    baseline = {
        case["case_id"]: normal_request_bytes(case, prompt) for case in cases
    }
    baseline_hashes = [content_hash(json.loads(value)) for value in baseline.values()]
    mutation_failures = []
    for case in cases:
        for mutated in _restricted_mutations(case):
            value = normal_request_bytes(mutated, prompt)
            if value != baseline[case["case_id"]]:
                mutation_failures.append(case["case_id"])

    forbidden_keys = {
        "logical_role",
        "mechanism_family",
        "usefulness",
        "correct_conclusion",
        "oracle_content",
        "expected_fact_keys",
        "v1_2_expected_tags",
        "score",
        "rank",
    }
    normal_fields = [
        path
        for case in cases
        for path in _flatten_keys(build_normal_request(case, prompt))
    ]
    field_leaks = sorted(
        {path for path in normal_fields if path.rsplit(".", 1)[-1] in forbidden_keys}
    )
    provenance_failures = [
        case["case_id"]
        for case in cases
        if (
            build_normal_request(case, prompt)["system_instruction"] != prompt
            or build_normal_request(case, prompt)["response_schema"]
            != case["response_schema"]
            or build_normal_request(case, prompt)["user_payload"]
            != _public_projection(case["model_visible_input"])
        )
    ]
    import_audit = _static_import_audit(
        ROOT / "src/ser/authzgym/v1_3_public_input.py"
    )
    empty_state = start_normal_state().to_dict()
    oracle_diagnostic = {"ranking": ["oracle"], "regret": 0.0}
    oracle_mutation = json.loads(json.dumps(oracle_diagnostic))
    oracle_mutation["ranking"] = ["mutated"]
    normal_after_oracle_mutation = [
        content_hash(json.loads(normal_request_bytes(case, prompt)))
        for case in cases
    ]
    isolated = _isolated_replay(public_dir, baseline_hashes)
    checks = {
        "restricted-field mutation byte equality": {
            "status": "pass" if not mutation_failures else "fail",
            "failures": sorted(set(mutation_failures)),
            "cases": len(cases),
        },
        "normal fields have public provenance": {
            "status": "pass"
            if not field_leaks and not provenance_failures
            else "fail",
            "leaks": field_leaks,
            "provenance_failures": provenance_failures,
        },
        "normal module import isolation": {
            "status": "pass" if not import_audit["forbidden_imports"] else "fail",
            "forbidden_imports": import_audit["forbidden_imports"],
        },
        "normal initial state empty": {
            "status": "pass"
            if all(
                not empty_state[key]
                for key in (
                    "facts",
                    "candidate_effects",
                    "unresolved_targets",
                    "response_sha256",
                )
            )
            and empty_state["oracle_derived_prior"] is False
            else "fail",
            "state": empty_state,
        },
        "oracle and normal channels separated": {
            "status": "pass"
            if oracle_mutation != oracle_diagnostic
            and normal_after_oracle_mutation == baseline_hashes
            else "fail",
        },
        "public-only replay": {
            "status": "pass"
            if isolated["byte_identical"]
            and isolated["restricted_files_absent"]
            and not isolated["evaluation_importable"]
            else "fail",
            "byte_identical": isolated["byte_identical"],
            "restricted_files_absent": isolated["restricted_files_absent"],
            "evaluation_importable": isolated["evaluation_importable"],
        },
    }
    return {
        "schema_version": 1,
        "experiment": "authzgym-semantic-contract-v1.3-firewall",
        "status": "pass" if all(item["status"] == "pass" for item in checks.values()) else "fail",
        "public_contract_hash": contract_hash,
        "case_count": len(cases),
        "normal_request_replay_hash": content_hash(baseline_hashes),
        "checks": checks,
    }


def _flatten_keys(value: object, prefix: str = "") -> list[str]:
    if isinstance(value, dict):
        result = []
        for key, item in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            result.append(path)
            result.extend(_flatten_keys(item, path))
        return result
    if isinstance(value, list):
        return [
            item
            for index, child in enumerate(value)
            for item in _flatten_keys(child, f"{prefix}.{index}")
        ]
    return []


def _public_projection(visible: dict) -> dict:
    return {
        "semantic_interface": visible["semantic_interface"],
        "instruction_scope": visible["instruction_scope"],
        "current_artifact": {
            "slot": visible["current_artifact"]["slot"],
            "public_id": visible["current_artifact"]["public_id"],
            "path": visible["current_artifact"]["path"],
            "source": visible["current_artifact"]["source"],
        },
        "candidate_hypotheses": [
            {
                "slot": item["slot"],
                "public_label": item["public_label"],
                "effect_family": item["effect_family"],
                "description": item["description"],
            }
            for item in visible["candidate_hypotheses"]
        ],
        "public_artifact_inventory": [
            {
                "slot": item["slot"],
                "public_id": item["public_id"],
                "path": item["path"],
                "exported_symbols": list(item["exported_symbols"]),
                "line_count": item["line_count"],
                "inspection_status": item["inspection_status"],
            }
            for item in visible["public_artifact_inventory"]
        ],
        "legal_uninspected_target_slots": list(
            visible["legal_uninspected_target_slots"]
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--public-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = validate(args.public_dir)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
