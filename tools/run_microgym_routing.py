#!/usr/bin/env python3
"""Freeze and run the MicroGym routing-v1 falsification benchmark."""

from __future__ import annotations

import argparse
from pathlib import Path

from ser.core.types import canonical_json
from ser.evaluation.artifacts import write_new_json, write_new_jsonl
from ser.evaluation.routing_analysis import (
    build_oracle_records,
    build_run_records,
    render_routing_interpretation,
    render_routing_report,
    summarize_routing,
    validate_routing,
)
from ser.evaluation.routing_artifacts import (
    build_routing_episodes,
    freeze_routing_population,
    load_routing_population,
)
from ser.microgym.routing import build_routing_regimes


def _write_new_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(text)
        if not text.endswith("\n"):
            handle.write("\n")


def freeze(experiment_dir: Path) -> str:
    preregistration = experiment_dir / "PREREGISTRATION.md"
    if not preregistration.is_file():
        raise FileNotFoundError("PREREGISTRATION.md must exist before population freeze")
    regimes = build_routing_regimes()
    episodes = build_routing_episodes(regimes)
    return freeze_routing_population(
        experiment_dir / "population.json",
        regimes,
        episodes,
        preregistration,
    )


def run(experiment_dir: Path) -> dict:
    regimes, episodes, population_hash, raw_population = load_routing_population(
        experiment_dir / "population.json"
    )
    preregistration = experiment_dir / "PREREGISTRATION.md"
    import hashlib

    if hashlib.sha256(preregistration.read_bytes()).hexdigest() != raw_population[
        "preregistration_sha256"
    ]:
        raise ValueError("preregistration changed after population freeze")

    oracle_records = build_oracle_records(regimes, population_hash)
    run_records = build_run_records(regimes, episodes, population_hash)
    validation = validate_routing(
        regimes, episodes, oracle_records, run_records, population_hash
    )
    summary = summarize_routing(
        regimes,
        episodes,
        oracle_records,
        run_records,
        population_hash,
        validation_passed=validation["status"] == "pass",
    )
    report = render_routing_report(summary, validation)
    interpretation = render_routing_interpretation(summary)

    # Compute the complete result before any aggregate file is created. Files use
    # exclusive creation, so a rerun cannot silently overwrite the frozen run.
    write_new_jsonl(experiment_dir / "oracle.jsonl", oracle_records)
    write_new_jsonl(experiment_dir / "runs.jsonl", run_records)
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
        default=Path("experiments/microgym_routing_v1"),
    )
    args = parser.parse_args()
    if args.mode == "freeze":
        digest = freeze(args.experiment_dir)
        print(f"frozen routing population {digest}")
    else:
        summary = run(args.experiment_dir)
        print(
            canonical_json(
                {
                    "classification": summary["classifier"]["classification"],
                    "population_hash": summary["population_hash"],
                    "runs": summary["population"]["runs"],
                }
            )
        )


if __name__ == "__main__":
    main()
