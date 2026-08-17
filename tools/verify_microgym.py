#!/usr/bin/env python3
"""Recompute MicroGym artifacts and verify the committed evidence exactly."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "src"))

from ser.core.types import canonical_json
from ser.evaluation.adaptivity import audit_suite
from ser.evaluation.analysis import render_report, summarize
from ser.evaluation.artifacts import (
    load_population,
    oracle_artifact,
    read_jsonl,
    run_artifact,
    verify_record_hash,
)
from ser.evaluation.runner import evaluate_run, run_episode
from ser.evaluation.validation import validate_experiment
from ser.microgym.environment import MicroGymEnvironment, evaluator_truth
from ser.microgym.oracle import OracleReferencePolicy
from ser.policies import (
    AdaptiveBeliefPolicy,
    NoAdaptationPolicy,
    NoAdaptiveStopPolicy,
    policy_suite,
)


def require_equal(label: str, actual, expected) -> None:
    if canonical_json(actual) != canonical_json(expected):
        raise AssertionError(f"{label} does not reproduce exactly")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment-dir", type=Path, required=True)
    args = parser.parse_args()
    directory = args.experiment_dir
    population_path = directory / "population.json"
    problems, episodes, population_hash = load_population(population_path)
    problem_by_id = {problem.problem_id: problem for problem in problems}
    stored_oracles = read_jsonl(directory / "oracle.jsonl")
    stored_runs = read_jsonl(directory / "runs.jsonl")
    if not all(verify_record_hash(item) for item in [*stored_oracles, *stored_runs]):
        raise AssertionError("a stored record hash failed")

    oracle_runs = []
    normal_runs = []
    recomputed_oracles = []
    recomputed_runs = []
    for episode in episodes:
        problem = problem_by_id[episode.problem_id]
        oracle = run_episode(
            problem,
            episode,
            OracleReferencePolicy(),
            allow_evaluator_policy=True,
        )
        environment = MicroGymEnvironment(problem, episode)
        environment.reset()
        hidden_state = evaluator_truth(environment)
        oracle_runs.append(oracle)
        recomputed_oracles.append(
            oracle_artifact(
                oracle,
                hidden_state,
                episode.environment_seed,
                population_hash,
            )
        )
        for policy in policy_suite():
            run = run_episode(problem, episode, policy)
            normal_runs.append(run)
            recomputed_runs.append(
                run_artifact(
                    run,
                    evaluate_run(run, oracle, problem, episode),
                    hidden_state,
                    episode.environment_seed,
                    population_hash,
                )
            )

    require_equal("oracle artifacts", recomputed_oracles, stored_oracles)
    require_equal("normal run artifacts", recomputed_runs, stored_runs)
    validation = validate_experiment(
        problems,
        episodes,
        normal_runs,
        oracle_runs,
        recomputed_runs,
        recomputed_oracles,
        population_hash,
    )
    stored_validation = json.loads((directory / "validation.json").read_text())
    require_equal("validation", validation, stored_validation)
    summary = summarize(recomputed_runs, population_hash)
    stored_summary = json.loads((directory / "summary.json").read_text())
    require_equal("summary", summary, stored_summary)
    population = json.loads(population_path.read_text())
    report = render_report(summary, population, validation).rstrip() + "\n"
    if report != (directory / "REPORT.md").read_text():
        raise AssertionError("REPORT.md does not reproduce exactly")
    adaptivity = audit_suite(
        problems,
        (AdaptiveBeliefPolicy(), NoAdaptationPolicy(), NoAdaptiveStopPolicy()),
    )
    adaptivity["population_hash"] = population_hash
    stored_adaptivity = json.loads((directory / "adaptivity.json").read_text())
    require_equal("counterfactual adaptivity audit", adaptivity, stored_adaptivity)
    print(
        f"PASS: population {population_hash}; {len(episodes)} episodes; "
        f"{len(stored_runs)} normal runs; {len(stored_oracles)} oracle runs; "
        "all hashes, replays, validation, summaries, report, and adaptivity audit reproduce"
    )


if __name__ == "__main__":
    main()
