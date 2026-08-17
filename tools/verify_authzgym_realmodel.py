#!/usr/bin/env python3
"""Deterministically verify stored AuthzGym real-model empirical artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from ser.authzgym.realmodel import load_real_model_condition, semantic_response_schema
from ser.core.types import canonical_json, content_hash
from ser.evaluation.authz_artifacts import file_sha256, load_population
from ser.evaluation.authz_real_analysis import (
    render_interpretation,
    render_report,
    summarize_real,
    validate_real,
)


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "experiments/authzgym_static_realmodel_v1"
SOURCE = ROOT / "experiments/authzgym_static_v1_1"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _record_hash_valid(value: dict) -> bool:
    payload = dict(value)
    digest = payload.pop("record_hash", None)
    return isinstance(digest, str) and content_hash(payload) == digest


def verify(experiment: Path) -> dict:
    condition = load_real_model_condition(experiment / "model_config.json")
    schema = _json(experiment / "schemas/semantic_observation_v1.json")
    if schema != semantic_response_schema():
        raise ValueError("stored and implemented semantic schemas differ")
    _, _, _ = load_population(SOURCE / "development_population.json")
    evaluation, _, _ = load_population(SOURCE / "evaluation_population.json")
    perturbations, _, _ = load_population(SOURCE / "perturbation_population.json")
    manifest = _json(experiment / "FROZEN_INPUTS.json")
    manifest_payload = dict(manifest)
    manifest_hash = manifest_payload.pop("manifest_hash")
    if content_hash(manifest_payload) != manifest_hash:
        raise ValueError("frozen manifest hash mismatch")
    file_map = {
        "PREREGISTRATION.md": experiment / "PREREGISTRATION.md",
        "prompts/semantic_interpretation_v1.txt": experiment
        / "prompts/semantic_interpretation_v1.txt",
        "schemas/semantic_observation_v1.json": experiment
        / "schemas/semantic_observation_v1.json",
        "model_config.json": experiment / "model_config.json",
        "source/development_population.json": SOURCE / "development_population.json",
        "source/evaluation_population.json": SOURCE / "evaluation_population.json",
        "source/perturbation_population.json": SOURCE / "perturbation_population.json",
        "implementation/src/ser/authzgym/model.py": ROOT / "src/ser/authzgym/model.py",
        "implementation/src/ser/authzgym/policies.py": ROOT
        / "src/ser/authzgym/policies.py",
        "implementation/src/ser/authzgym/realmodel.py": ROOT
        / "src/ser/authzgym/realmodel.py",
        "implementation/src/ser/authzgym/real_runner.py": ROOT
        / "src/ser/authzgym/real_runner.py",
        "implementation/src/ser/evaluation/authz_real_analysis.py": ROOT
        / "src/ser/evaluation/authz_real_analysis.py",
        "implementation/tools/run_authzgym_realmodel.py": ROOT
        / "tools/run_authzgym_realmodel.py",
        "implementation/tools/verify_authzgym_realmodel.py": ROOT
        / "tools/verify_authzgym_realmodel.py",
    }
    observed_hashes = {name: file_sha256(path) for name, path in file_map.items()}
    evaluation_records = _jsonl(experiment / "evaluation_runs.jsonl")
    perturbation_records = _jsonl(experiment / "perturbation_runs.jsonl")
    response_records = _jsonl(experiment / "provider_responses.jsonl")
    development = _json(experiment / "development_call.json")
    cost_gate = _json(experiment / "COST_GATE.json")
    if not _record_hash_valid(development) or not _record_hash_valid(cost_gate):
        raise ValueError("development or cost-gate record hash mismatch")
    validation = validate_real(
        evaluation,
        perturbations,
        evaluation_records,
        perturbation_records,
        response_records,
        manifest["files"],
        observed_hashes,
        condition.hard_spend_ceiling_usd,
        float(development["cost_usd"]),
    )
    summary = summarize_real(
        evaluation,
        perturbations,
        evaluation_records,
        perturbation_records,
        response_records,
        validation,
    )
    report = render_report(
        summary,
        validation,
        {
            "provider_calls": development["provider_calls"],
            "input_tokens": development["input_tokens"],
            "output_tokens": development["output_tokens"],
            "cost_usd": development["cost_usd"],
            "projected_complete_cost_usd": cost_gate["projected_complete_cost_usd"],
        },
    )
    interpretation = render_interpretation(summary)
    exact = {
        "validation": validation == _json(experiment / "validation.json"),
        "summary": summary == _json(experiment / "summary.json"),
        "report": report == (experiment / "REPORT.md").read_text(encoding="utf-8"),
        "interpretation": interpretation
        == (experiment / "INTERPRETATION.md").read_text(encoding="utf-8"),
    }
    if not all(exact.values()):
        raise ValueError(f"stored real-model analysis does not replay exactly: {exact}")
    return {
        "status": validation["status"],
        "classification": summary["classifier"]["classification"],
        "exact_reanalysis": exact,
        "response_attempts": len(response_records),
        "complete_cost_usd": summary["provider_accounting"]["total_cost_usd"]
        + float(development["cost_usd"]),
        "frozen_inputs_manifest_hash": manifest_hash,
    }


def main() -> None:
    print(canonical_json(verify(EXPERIMENT)))


if __name__ == "__main__":
    main()
