#!/usr/bin/env python3
"""Exact offline verifier for AuthzGym transport-envelope v1."""

from __future__ import annotations

import json
from pathlib import Path

from autopsy_authzgym_transport import analyze as reproduce_autopsy
from autopsy_authzgym_transport import render_report as render_autopsy_report
from run_authzgym_transport_envelope import (
    EXPERIMENT,
    SEMANTIC_SOURCE,
    _jsonl,
    _load_manifest,
    _paths,
    _project_cost,
    _record_hash_valid,
    _transport_validation,
    _verify_preflight_archive,
)
from ser.authzgym.realmodel import load_real_model_condition
from ser.authzgym.tunnel_supervisor import load_tunnel_policy
from ser.core.types import canonical_json
from ser.evaluation.authz_transport_analysis import (
    render_interpretation,
    render_report,
    summarize_transport,
)


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def verify(experiment: Path) -> dict:
    paths = _paths(experiment)
    preflight = _verify_preflight_archive(experiment)
    expected_autopsy = reproduce_autopsy(SEMANTIC_SOURCE)
    if expected_autopsy != _json(paths["autopsy_json"]):
        raise ValueError("transport autopsy does not reproduce exactly")
    if render_autopsy_report(expected_autopsy) != paths[
        "autopsy_report"
    ].read_text(encoding="utf-8"):
        raise ValueError("transport autopsy report does not reproduce exactly")

    manifest, observed_hashes = _load_manifest(experiment)
    population = _json(SEMANTIC_SOURCE / "STRESS_POPULATION.json")
    if canonical_json(manifest["run_schedule"]) != canonical_json(
        population["schedule"]
    ):
        raise ValueError("transport schedule differs from frozen semantic schedule")

    cost_gate = _json(paths["cost_gate"])
    if not _record_hash_valid(cost_gate):
        raise ValueError("cost gate record hash is invalid")
    condition = load_real_model_condition(
        SEMANTIC_SOURCE / "model_config.json"
    )
    policy = load_tunnel_policy(paths["transport_config"])
    expected_projection = _project_cost(
        condition, len(population["schedule"]), policy.maximum_api_submissions
    )
    for key, value in expected_projection.items():
        if cost_gate[key] != value:
            raise ValueError(f"cost projection differs for {key}")
    if cost_gate["projected_complete_cost_usd"] >= 1.0:
        raise ValueError("cost projection is not below the hard ceiling")

    runs = _jsonl(paths["runs"])
    responses = _jsonl(paths["responses"])
    transport_attempts = _jsonl(paths["transport_attempts"])
    tunnel_events = _jsonl(paths["tunnel_events"])
    validation = _transport_validation(
        experiment,
        population,
        runs,
        responses,
        transport_attempts,
        tunnel_events,
        manifest,
        observed_hashes,
    )
    summary = summarize_transport(
        population,
        runs,
        responses,
        transport_attempts,
        tunnel_events,
        validation,
    )
    oracle = summary["downstream_action_value"]["oracle_conditioned"]
    if oracle != {
        "canonical_development_episodes": 8,
        "top1": 1.0,
        "top2": 1.0,
        "mean_normalized_regret": 0.0,
    }:
        raise ValueError("oracle estimator diagnostic did not reproduce 1/1/0")

    expected_files = {
        "validation.json": json.dumps(validation, indent=2, sort_keys=True) + "\n",
        "summary.json": json.dumps(summary, indent=2, sort_keys=True) + "\n",
        "REPORT.md": render_report(summary, validation, expected_autopsy),
        "INTERPRETATION.md": render_interpretation(summary),
    }
    for name, expected in expected_files.items():
        actual = (experiment / name).read_text(encoding="utf-8")
        if actual != expected:
            raise ValueError(
                f"transport-envelope artifact does not reproduce exactly: {name}"
            )
    return {
        "population_hash": population["population_hash"],
        "scheduled_logical_calls": len(population["schedule"]),
        "api_submissions": len(transport_attempts),
        "provider_responses": summary["transport"][
            "logical_calls_with_provider_response"
        ],
        "validation": validation["status"],
        "transport": summary["transport"]["classification"],
        "contract": summary["semantic_contract"]["classification"],
        "semantics": summary["semantic_signal"]["classification"],
        "next_experiment": summary["decision_rule"]["selected_next_experiment"],
        "oracle_top1_top2_regret": [
            oracle["top1"],
            oracle["top2"],
            oracle["mean_normalized_regret"],
        ],
        "accounted_spend_usd": summary["provider_accounting"][
            "total_cost_usd"
        ],
        "frozen_inputs_manifest_hash": manifest["manifest_hash"],
        "preserved_zero_inference_preflight": preflight,
    }


def main() -> None:
    print(canonical_json(verify(EXPERIMENT)))


if __name__ == "__main__":
    main()
