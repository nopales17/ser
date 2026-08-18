#!/usr/bin/env python3
"""Exact offline verifier for AuthzGym semantic contract v1.2."""

from __future__ import annotations

import json
from pathlib import Path

from autopsy_authzgym_realmodel import analyze as autopsy_analyze
from autopsy_authzgym_realmodel import render_report as render_autopsy_report
from run_authzgym_semantic_contract import (
    EXPERIMENT,
    SOURCE,
    _jsonl,
    _load_manifest,
    _paths,
    _project_cost,
    _record_hash_valid,
    _validate,
)
from ser.authzgym.realmodel import load_real_model_condition
from ser.authzgym.semantic_contract import stress_population_payload, vocabulary_payload
from ser.core.types import canonical_json, content_hash
from ser.evaluation.authz_artifacts import load_population
from ser.evaluation.authz_contract_analysis import (
    render_interpretation,
    render_report,
    summarize,
)


OLD_EXPERIMENT = Path(__file__).resolve().parents[1] / "experiments/authzgym_static_realmodel_v1"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def verify(experiment: Path) -> dict:
    paths = _paths(experiment)
    if _json(paths["vocabulary"]) != vocabulary_payload():
        raise ValueError("semantic vocabulary does not reproduce")
    development, source_hash, _ = load_population(
        SOURCE / "development_population.json"
    )
    expected_population = stress_population_payload(development)
    expected_population["source_development_population_hash"] = source_hash
    payload = dict(expected_population)
    payload.pop("population_hash")
    expected_population["population_hash"] = content_hash(payload)
    population = _json(paths["population"])
    if canonical_json(expected_population) != canonical_json(population):
        raise ValueError("stress population does not reproduce exactly")

    expected_autopsy = autopsy_analyze(OLD_EXPERIMENT)
    if expected_autopsy != _json(paths["autopsy_json"]):
        raise ValueError("offline v1 autopsy does not reproduce exactly")
    if render_autopsy_report(expected_autopsy) != paths["autopsy_report"].read_text(
        encoding="utf-8"
    ):
        raise ValueError("offline v1 autopsy report does not reproduce exactly")

    manifest, observed_hashes = _load_manifest(experiment)
    cost_gate = _json(paths["cost_gate"])
    if not _record_hash_valid(cost_gate):
        raise ValueError("cost gate record hash is invalid")
    condition = load_real_model_condition(paths["config"])
    expected_projection = _project_cost(condition, len(population["schedule"]))
    for key, value in expected_projection.items():
        if cost_gate[key] != value:
            raise ValueError(f"cost projection differs for {key}")

    runs = _jsonl(paths["runs"])
    responses = _jsonl(paths["responses"])
    validation = _validate(
        experiment, population, runs, responses, manifest, observed_hashes
    )
    summary = summarize(population, runs, responses, validation)
    expected_files = {
        "validation.json": json.dumps(validation, indent=2, sort_keys=True) + "\n",
        "summary.json": json.dumps(summary, indent=2, sort_keys=True) + "\n",
        "REPORT.md": render_report(summary, validation, expected_autopsy),
        "INTERPRETATION.md": render_interpretation(summary),
    }
    for name, expected in expected_files.items():
        actual = (experiment / name).read_text(encoding="utf-8")
        if actual != expected:
            raise ValueError(f"v1.2 artifact does not reproduce exactly: {name}")
    return {
        "population_hash": population["population_hash"],
        "stress_cases": len(population["cases"]),
        "scheduled_calls": len(population["schedule"]),
        "provider_attempts": len(responses),
        "validation": validation["status"],
        "contract": summary["contract"]["classification"],
        "semantics": summary["semantics"]["classification"],
        "next_experiment": summary["decision_rule"]["selected_next_experiment"],
        "accounted_spend_usd": summary["provider_accounting"]["total_cost_usd"],
        "frozen_inputs_manifest_hash": manifest["manifest_hash"],
    }


def main() -> None:
    print(canonical_json(verify(EXPERIMENT)))


if __name__ == "__main__":
    main()
