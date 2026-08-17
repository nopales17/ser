#!/usr/bin/env python3
"""Recompute every frozen MicroGym routing-v1 artifact exactly."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ser.core.types import canonical_json, content_hash
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
    load_routing_population,
    routing_population_payload,
)
from ser.microgym.routing import build_routing_regimes


def _json_text(value: object) -> str:
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n"


def _jsonl_text(values: list[dict]) -> str:
    return "".join(canonical_json(value) + "\n" for value in values)


def verify(experiment_dir: Path) -> dict:
    preregistration = experiment_dir / "PREREGISTRATION.md"
    regimes, episodes, population_hash, raw_population = load_routing_population(
        experiment_dir / "population.json"
    )

    current_regimes = build_routing_regimes()
    current_episodes = build_routing_episodes(current_regimes)
    expected_population = routing_population_payload(
        current_regimes, current_episodes, preregistration
    )
    if content_hash(expected_population) != population_hash:
        raise ValueError("current routing definitions do not reproduce the frozen population")
    if canonical_json(expected_population) != canonical_json(raw_population):
        raise ValueError("frozen population payload differs from current definitions")

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

    expected_files = {
        "oracle.jsonl": _jsonl_text(oracle_records),
        "runs.jsonl": _jsonl_text(run_records),
        "validation.json": _json_text(validation),
        "summary.json": _json_text(summary),
        "REPORT.md": report if report.endswith("\n") else report + "\n",
        "INTERPRETATION.md": (
            interpretation if interpretation.endswith("\n") else interpretation + "\n"
        ),
    }
    for name, expected in expected_files.items():
        actual = (experiment_dir / name).read_text(encoding="utf-8")
        if actual != expected:
            raise ValueError(f"artifact does not reproduce exactly: {name}")
    if validation["status"] != "pass":
        raise ValueError("recomputed routing validation failed")
    return {
        "population_hash": population_hash,
        "regimes": len(regimes),
        "episodes": len(episodes),
        "runs": len(run_records),
        "classification": summary["classifier"]["classification"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--experiment-dir",
        type=Path,
        default=Path("experiments/microgym_routing_v1"),
    )
    args = parser.parse_args()
    result = verify(args.experiment_dir)
    print(
        "PASS: routing population "
        f"{result['population_hash']}; {result['regimes']} regimes; "
        f"{result['episodes']} episodes; {result['runs']} runs; "
        f"classification {result['classification']}; all artifacts reproduce"
    )


if __name__ == "__main__":
    main()
