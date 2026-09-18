#!/usr/bin/env python3
"""Validate the unchanged estimator on independently certified v1.3 gold."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ser.authzgym.v1_3_contract import load_public_contract
from ser.evaluation.authz_v1_3 import (
    FROZEN_ESTIMATOR_SHA256,
    action_diagnostic,
    aggregate_action_diagnostics,
    assert_frozen_estimator,
    estimator_source_sha256,
    oracle_response_from_annotation,
)
from ser.core.types import content_hash


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "experiments/authzgym_semantic_contract_v1_3"
EQUIVALENCE_VARIANTS = (
    "artifact_reordering",
    "symbol_renaming",
    "candidate_label_renaming",
    "artifact_identifier_variation",
    "combined_permutation",
)
CANONICAL_VARIANTS = ("base_entry",)


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> dict[str, dict]:
    return {
        item["case_id"]: item
        for item in (
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }


def validate(split: str) -> dict:
    assert_frozen_estimator()
    contract = load_public_contract(EXPERIMENT / "PUBLIC_CONTRACT.json")
    population_name = (
        "DEVELOPMENT_PUBLIC_POPULATION.json"
        if split == "development"
        else "CONFIRMATION_PUBLIC_POPULATION.json"
    )
    restricted_name = (
        "DEVELOPMENT_RESTRICTED_POPULATION.json"
        if split == "development"
        else "CONFIRMATION_RESTRICTED_POPULATION.json"
    )
    annotation_name = (
        "development_annotations.jsonl"
        if split == "development"
        else "confirmation_annotations.jsonl"
    )
    population = _read_json(EXPERIMENT / population_name)
    restricted = {
        item["case_id"]: item
        for item in _read_json(EXPERIMENT / restricted_name)["cases"]
    }
    annotations = _read_jsonl(EXPERIMENT / "annotations" / annotation_name)
    rows = []
    diagnostics = {}
    for case in population["cases"]:
        case_id = case["case_id"]
        response = oracle_response_from_annotation(annotations[case_id])
        diagnostic = action_diagnostic(
            case,
            response,
            restricted[case_id],
            contract=contract,
        )
        diagnostics[case_id] = diagnostic
        rows.append(diagnostic)
    canonical_rows = [
        diagnostics[case["case_id"]]
        for case in population["cases"]
        if case["variant"] in CANONICAL_VARIANTS
    ]
    aggregate = aggregate_action_diagnostics(canonical_rows)
    longest_rows = [
        diagnostics[case["case_id"]]
        for case in population["cases"]
        if case["variant"] == "longest_artifact"
    ]
    longest_observed = aggregate_action_diagnostics(longest_rows)
    gates = {
        "top1": aggregate["top1"] >= 0.60,
        "top2": aggregate["top2"] >= 0.80,
        "regret": aggregate["mean_normalized_regret"] <= 0.35,
        "illegal_targets_zero": aggregate["illegal_target_count"] == 0,
    }
    equivalence_failures = []
    equivalence_checks = 0
    cases_by_source: dict[str, dict] = {}
    for case in population["cases"]:
        if case["variant"] == "base_entry":
            cases_by_source[case["source_episode_id"]] = case
    for case in population["cases"]:
        if case["variant"] not in EQUIVALENCE_VARIANTS:
            continue
        base_case = cases_by_source[case["source_episode_id"]]
        base_diagnostic = diagnostics[base_case["case_id"]]
        variant_diagnostic = diagnostics[case["case_id"]]
        base_values = {
            restricted[base_case["case_id"]]["transformation_maps"][
                "canonical_ordinal_by_variant_public_id"
            ][artifact_id]: value
            for artifact_id, value in base_diagnostic["values"].items()
        }
        variant_values = {
            restricted[case["case_id"]]["transformation_maps"][
                "canonical_ordinal_by_variant_public_id"
            ][artifact_id]: value
            for artifact_id, value in variant_diagnostic["values"].items()
        }
        if set(base_values) != set(variant_values):
            equivalence_failures.append(f"{case['case_id']}: target set mismatch")
            continue
        for key in base_values:
            if abs(float(base_values[key]) - float(variant_values[key])) > 1e-12:
                equivalence_failures.append(
                    f"{case['case_id']}: action value mismatch at ordinal {key}"
                )
        if (
            bool(base_diagnostic["top1"]) != bool(variant_diagnostic["top1"])
            or bool(base_diagnostic["top2"]) != bool(variant_diagnostic["top2"])
            or abs(
                float(base_diagnostic["mean_normalized_regret"])
                - float(variant_diagnostic["mean_normalized_regret"])
            )
            > 1e-12
        ):
            equivalence_failures.append(f"{case['case_id']}: ranking mismatch")
        equivalence_checks += 1
    status = (
        "pass"
        if all(gates.values()) and not equivalence_failures
        else "blocked"
    )
    return {
        "schema_version": 1,
        "experiment": "authzgym-semantic-contract-v1.3-oracle",
        "split": split,
        "status": status,
        "inference_authorized": False,
        "estimator_source_sha256": estimator_source_sha256(),
        "frozen_estimator_sha256": FROZEN_ESTIMATOR_SHA256,
        "estimator_hash_matches": estimator_source_sha256() == FROZEN_ESTIMATOR_SHA256,
        "canonical_variants": list(CANONICAL_VARIANTS),
        "canonical_observed": aggregate,
        "longest_artifact_noncanonical_observed": longest_observed,
        "gates": gates,
        "equivalence_pair_count": equivalence_checks,
        "equivalence_failures": equivalence_failures,
        "all_case_diagnostic_hash": content_hash(
            {
                case_id: {
                    "values": diagnostic["values"],
                    "ranking": diagnostic["ranking"],
                    "top1": diagnostic["top1"],
                    "top2": diagnostic["top2"],
                    "regret": diagnostic["mean_normalized_regret"],
                    "nondiscriminating": diagnostic["nondiscriminating"],
                }
                for case_id, diagnostic in diagnostics.items()
            }
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=("development", "confirmation_v1_3"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--blocker", type=Path)
    args = parser.parse_args()
    result = validate(args.split)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if result["status"] != "pass" and args.blocker is not None:
        args.blocker.write_text(
            "# AuthzGym v1.3 oracle blocker\n\n"
            "The unchanged estimator failed a preregistered oracle gate or "
            "transformation-equivalence check. No estimator, gold, source, or "
            "scoring change is authorized by this failure. Inference remains "
            "unauthorized.\n",
            encoding="utf-8",
        )
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
