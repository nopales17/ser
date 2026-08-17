#!/usr/bin/env python3
"""Freeze and mock-calibrate Static Semantic AuthzGym v1."""

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
from ser.core.types import canonical_json
from ser.evaluation.artifacts import write_new_json
from ser.evaluation.authz_analysis import (
    build_run_records,
    render_interpretation,
    render_report,
    summarize_authz,
    validate_authz,
)
from ser.evaluation.authz_artifacts import (
    file_sha256,
    freeze_population,
    load_population,
    write_run_records,
)


def _paths(experiment_dir: Path) -> tuple[Path, Path, Path]:
    return (
        experiment_dir / "PREREGISTRATION.md",
        experiment_dir / "prompts/interpret_artifact_v1.txt",
        experiment_dir / "model_conditions.json",
    )


def _write_new_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(value)
        if not value.endswith("\n"):
            handle.write("\n")


def _load_conditions(path: Path):
    raw = json.loads(path.read_text(encoding="utf-8"))
    conditions = conditions_from_config(raw)
    if raw["conditions"] != [item.to_dict() for item in conditions]:
        raise ValueError("model_conditions.json does not round-trip through its schema")
    return conditions


def freeze(experiment_dir: Path) -> dict:
    preregistration, prompt, config = _paths(experiment_dir)
    for path in (preregistration, prompt, config):
        if not path.is_file():
            raise FileNotFoundError(f"required frozen input missing: {path}")
    _load_conditions(config)
    development_hash = freeze_population(
        experiment_dir / "development_population.json",
        "development",
        build_development_episodes(),
        preregistration,
        (prompt,),
        config,
    )
    evaluation_hash = freeze_population(
        experiment_dir / "evaluation_population.json",
        "evaluation",
        build_evaluation_episodes(),
        preregistration,
        (prompt,),
        config,
    )
    perturbation_hash = freeze_population(
        experiment_dir / "perturbation_population.json",
        "perturbation_audit",
        build_perturbation_episodes(),
        preregistration,
        (prompt,),
        config,
    )
    return {
        "development": development_hash,
        "evaluation": evaluation_hash,
        "perturbation_audit": perturbation_hash,
    }


def run(experiment_dir: Path) -> dict:
    preregistration, prompt_path, config = _paths(experiment_dir)
    conditions = _load_conditions(config)
    development, development_hash, development_raw = load_population(
        experiment_dir / "development_population.json"
    )
    evaluation, evaluation_hash, evaluation_raw = load_population(
        experiment_dir / "evaluation_population.json"
    )
    perturbations, perturbation_hash, perturbation_raw = load_population(
        experiment_dir / "perturbation_population.json"
    )
    for raw in (development_raw, evaluation_raw, perturbation_raw):
        if raw["preregistration_sha256"] != file_sha256(preregistration):
            raise ValueError("preregistration changed after population freeze")
        if raw["prompt_hashes"][prompt_path.name] != file_sha256(prompt_path):
            raise ValueError("prompt changed after population freeze")
        if raw["model_config_sha256"] != file_sha256(config):
            raise ValueError("model configuration changed after population freeze")

    prompt_text = prompt_path.read_text(encoding="utf-8")
    prompt_hash = file_sha256(prompt_path)
    config_hash = file_sha256(config)
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
    report = render_report(summary, validation)
    interpretation = render_interpretation(summary)

    write_run_records(experiment_dir / "runs.jsonl", records)
    write_run_records(experiment_dir / "perturbation_runs.jsonl", perturbation_records)
    write_new_json(experiment_dir / "validation.json", validation)
    write_new_json(experiment_dir / "summary.json", summary)
    _write_new_text(experiment_dir / "REPORT.md", report)
    _write_new_text(experiment_dir / "INTERPRETATION.md", interpretation)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("freeze", "run"))
    parser.add_argument(
        "--experiment-dir",
        type=Path,
        default=Path("experiments/authzgym_static_v1"),
    )
    args = parser.parse_args()
    if args.mode == "freeze":
        print(canonical_json(freeze(args.experiment_dir)))
    else:
        summary = run(args.experiment_dir)
        print(
            canonical_json(
                {
                    "classification": summary["classifier"]["classification"],
                    "evaluation_population_hash": summary["population_hash"],
                    "episodes": summary["population"]["episodes"],
                    "runs": summary["population"]["runs"],
                }
            )
        )


if __name__ == "__main__":
    main()
