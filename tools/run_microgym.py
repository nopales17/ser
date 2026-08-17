#!/usr/bin/env python3
"""Freeze, run, and validate the deterministic MicroGym v1 benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from collections import Counter
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "src"))

from ser.evaluation.analysis import render_report, summarize
from ser.evaluation.artifacts import (
    freeze_population,
    load_population,
    oracle_artifact,
    run_artifact,
    write_new_json,
    write_new_jsonl,
)
from ser.evaluation.runner import evaluate_run, run_episode
from ser.evaluation.validation import validate_experiment
from ser.microgym.environment import MicroGymEnvironment, evaluator_truth
from ser.microgym.families import build_problem_specs
from ser.microgym.model import (
    ENVIRONMENT_REALIZATION_MASTER_SEED,
    POPULATION_GENERATION_SEED,
    EpisodeSpec,
)
from ser.microgym.oracle import OracleReferencePolicy
from ser.policies import policy_suite


def _integer_seed(*parts: object) -> int:
    payload = "|".join(str(part) for part in parts).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


def build_episodes() -> tuple[EpisodeSpec, ...]:
    episodes = []
    for problem in build_problem_specs():
        repetitions = 8 if len(problem.hypotheses) == 4 else 10
        index = 0
        action_ids = [test.public.action_id for test in problem.tests]
        for hypothesis_index, hidden_state in enumerate(problem.hypotheses):
            for repetition in range(repetitions):
                order = list(action_ids)
                random.Random(
                    _integer_seed(
                        POPULATION_GENERATION_SEED,
                        "order",
                        problem.problem_id,
                        hypothesis_index,
                        repetition,
                    )
                ).shuffle(order)
                episodes.append(
                    EpisodeSpec(
                        episode_id=f"mgv1-{problem.problem_id}-e{index:03d}",
                        problem_id=problem.problem_id,
                        hidden_state=hidden_state,
                        environment_seed=_integer_seed(
                            ENVIRONMENT_REALIZATION_MASTER_SEED,
                            "environment",
                            problem.problem_id,
                            hypothesis_index,
                            repetition,
                        ),
                        action_order=tuple(order),
                    )
                )
                index += 1
    return tuple(episodes)


def command_freeze(path: Path) -> None:
    problems = build_problem_specs()
    episodes = build_episodes()
    problem_by_id = {problem.problem_id: problem for problem in problems}
    counts = Counter(problem_by_id[episode.problem_id].family for episode in episodes)
    if len(problems) != 24 or len(counts) != 6 or min(counts.values()) < 100:
        raise RuntimeError("population does not satisfy the preregistered scale")
    digest = freeze_population(path, problems, episodes)
    print(
        json.dumps(
            {
                "population": str(path),
                "population_hash": digest,
                "problems": len(problems),
                "episodes": len(episodes),
                "episodes_by_family": dict(sorted(counts.items())),
            },
            sort_keys=True,
        )
    )


def command_run(population_path: Path, output_dir: Path) -> None:
    problems, episodes, population_hash = load_population(population_path)
    if population_path.parent.resolve() != output_dir.resolve():
        raise ValueError("population manifest and run artifacts must share one experiment directory")
    output_paths = (
        output_dir / "oracle.jsonl",
        output_dir / "runs.jsonl",
        output_dir / "validation.json",
        output_dir / "summary.json",
        output_dir / "REPORT.md",
    )
    existing = [str(path) for path in output_paths if path.exists()]
    if existing:
        raise FileExistsError(f"refusing to overwrite experiment artifacts: {existing}")

    problem_by_id = {problem.problem_id: problem for problem in problems}
    oracle_runs = []
    oracle_artifacts = []
    normal_runs = []
    normal_artifacts = []
    for episode_index, episode in enumerate(episodes, start=1):
        problem = problem_by_id[episode.problem_id]
        oracle = run_episode(
            problem,
            episode,
            OracleReferencePolicy(),
            allow_evaluator_policy=True,
        )
        if not oracle.valid:
            raise RuntimeError(f"oracle failed for {episode.episode_id}: {oracle.invalid_reason}")
        evaluator_environment = MicroGymEnvironment(problem, episode)
        evaluator_environment.reset()
        hidden_state = evaluator_truth(evaluator_environment)
        oracle_runs.append(oracle)
        oracle_artifacts.append(
            oracle_artifact(
                oracle,
                hidden_state,
                episode.environment_seed,
                population_hash,
            )
        )
        for policy in policy_suite():
            run = run_episode(problem, episode, policy)
            outcome = evaluate_run(run, oracle, problem, episode)
            normal_runs.append(run)
            normal_artifacts.append(
                run_artifact(
                    run,
                    outcome,
                    hidden_state,
                    episode.environment_seed,
                    population_hash,
                )
            )
        if episode_index % 100 == 0:
            print(f"completed {episode_index}/{len(episodes)} episodes", flush=True)

    validation = validate_experiment(
        problems,
        episodes,
        normal_runs,
        oracle_runs,
        normal_artifacts,
        oracle_artifacts,
        population_hash,
    )
    summary = summarize(normal_artifacts, population_hash)
    population = json.loads(population_path.read_text(encoding="utf-8"))
    report = render_report(summary, population, validation)

    write_new_jsonl(output_dir / "oracle.jsonl", oracle_artifacts)
    write_new_jsonl(output_dir / "runs.jsonl", normal_artifacts)
    write_new_json(output_dir / "validation.json", validation)
    write_new_json(output_dir / "summary.json", summary)
    with (output_dir / "REPORT.md").open("x", encoding="utf-8") as handle:
        handle.write(report.rstrip() + "\n")
    if validation["status"] != "pass":
        raise RuntimeError(
            f"experiment artifacts preserved but validation failed: {validation['failed_checks']}"
        )
    print(
        json.dumps(
            {
                "population_hash": population_hash,
                "evidence_classification": summary["evidence_classification"],
                "normal_runs": len(normal_runs),
                "oracle_runs": len(oracle_runs),
                "validation": validation["status"],
            },
            sort_keys=True,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    freeze = subparsers.add_parser("freeze")
    freeze.add_argument("--population", type=Path, required=True)
    run = subparsers.add_parser("run")
    run.add_argument("--population", type=Path, required=True)
    run.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "freeze":
        command_freeze(args.population)
    else:
        command_run(args.population, args.output_dir)


if __name__ == "__main__":
    main()
