#!/usr/bin/env python3
"""Reproduce every Static Semantic AuthzGym v1 construction artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ser.authzgym.generation import (
    build_development_episodes,
    build_evaluation_episodes,
    build_perturbation_episodes,
)
from ser.authzgym.interpreters import conditions_from_config
from ser.core.types import canonical_json, content_hash
from ser.evaluation.authz_analysis import (
    build_run_records,
    render_interpretation,
    render_report,
    summarize_authz,
    validate_authz,
)
from ser.evaluation.authz_artifacts import (
    file_sha256,
    load_population,
    population_payload,
)


def _json_text(value: object) -> str:
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n"


def _jsonl_text(values: list[dict]) -> str:
    return "".join(canonical_json(value) + "\n" for value in values)


def verify(experiment_dir: Path) -> dict:
    preregistration = experiment_dir / "PREREGISTRATION.md"
    prompt_path = experiment_dir / "prompts/interpret_artifact_v1.txt"
    config = experiment_dir / "model_conditions.json"
    prompt_text = prompt_path.read_text(encoding="utf-8")
    prompt_hash = file_sha256(prompt_path)
    config_hash = file_sha256(config)
    conditions = conditions_from_config(json.loads(config.read_text(encoding="utf-8")))
    definitions = (
        ("development", build_development_episodes(), "development_population.json"),
        ("evaluation", build_evaluation_episodes(), "evaluation_population.json"),
        (
            "perturbation_audit",
            build_perturbation_episodes(),
            "perturbation_population.json",
        ),
    )
    loaded = {}
    for split, current, name in definitions:
        episodes, digest, raw = load_population(experiment_dir / name)
        expected = population_payload(
            split, current, preregistration, (prompt_path,), config
        )
        if content_hash(expected) != digest or canonical_json(expected) != canonical_json(raw):
            raise ValueError(f"current definitions do not reproduce {name}")
        loaded[split] = (episodes, digest)

    development, development_hash = loaded["development"]
    evaluation, evaluation_hash = loaded["evaluation"]
    perturbations, perturbation_hash = loaded["perturbation_audit"]
    records = build_run_records(
        evaluation,
        conditions,
        prompt_text,
        "interpret_artifact_v1",
        prompt_hash,
        config_hash,
        evaluation_hash,
    )
    perturbation_records = build_run_records(
        perturbations,
        conditions,
        prompt_text,
        "interpret_artifact_v1",
        prompt_hash,
        config_hash,
        perturbation_hash,
    )
    validation = validate_authz(
        development,
        evaluation,
        perturbations,
        records,
        perturbation_records,
        development_hash,
        evaluation_hash,
        perturbation_hash,
    )
    summary = summarize_authz(
        evaluation,
        records,
        evaluation_hash,
        validation_passed=validation["status"] == "pass",
    )
    expected_files = {
        "runs.jsonl": _jsonl_text(records),
        "perturbation_runs.jsonl": _jsonl_text(perturbation_records),
        "validation.json": _json_text(validation),
        "summary.json": _json_text(summary),
        "REPORT.md": render_report(summary, validation),
        "INTERPRETATION.md": render_interpretation(summary),
    }
    for name in ("REPORT.md", "INTERPRETATION.md"):
        if not expected_files[name].endswith("\n"):
            expected_files[name] += "\n"
    for name, expected in expected_files.items():
        if (experiment_dir / name).read_text(encoding="utf-8") != expected:
            raise ValueError(f"artifact does not reproduce exactly: {name}")
    preserved_invalid = (
        experiment_dir.name == "authzgym_static_v1"
        and (experiment_dir / "FIRST_RUN_FAILURE.json").is_file()
        and validation["checks"]["identifier label and order perturbation"]["status"]
        == "fail"
    )
    if validation["status"] != "pass" and not preserved_invalid:
        raise ValueError("recomputed AuthzGym validation failed")
    return {
        "development_episodes": len(development),
        "evaluation_episodes": len(evaluation),
        "perturbation_episodes": len(perturbations),
        "runs": len(records),
        "perturbation_runs": len(perturbation_records),
        "evaluation_population_hash": evaluation_hash,
        "classification": summary["classifier"]["classification"],
        "validation_status": validation["status"],
        "preserved_invalid": preserved_invalid,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--experiment-dir",
        type=Path,
        default=Path("experiments/authzgym_static_v1"),
    )
    args = parser.parse_args()
    result = verify(args.experiment_dir)
    print(
        "PASS: AuthzGym static population "
        f"{result['evaluation_population_hash']}; "
        f"{result['development_episodes']} development, "
        f"{result['evaluation_episodes']} evaluation, "
        f"{result['perturbation_episodes']} perturbation episodes; "
        f"{result['runs'] + result['perturbation_runs']} mock records; "
        f"classification {result['classification']}; validation {result['validation_status']}; "
        f"all artifacts reproduce"
    )


if __name__ == "__main__":
    main()
