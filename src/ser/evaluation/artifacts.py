"""Deterministic, fail-closed population and run artifact serialization."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Mapping

from ser.core.types import Outcome, Trace, canonical_json, content_hash
from ser.microgym.model import (
    ENVIRONMENT_REALIZATION_MASTER_SEED,
    POPULATION_GENERATION_SEED,
    POLICY_RANDOMNESS_MASTER_SEED,
    EpisodeSpec,
    ProblemSpec,
    RESOURCE_SCHEMA,
)

from .runner import RunRecord


def population_payload(
    problems: Iterable[ProblemSpec], episodes: Iterable[EpisodeSpec]
) -> dict:
    return {
        "schema_version": 1,
        "benchmark": "microgym-v1",
        "visibility": "evaluator_only_experiment_definition",
        "frozen_before_aggregation": True,
        "seed_roles": {
            "population_generation_seed": POPULATION_GENERATION_SEED,
            "environment_realization_master_seed": ENVIRONMENT_REALIZATION_MASTER_SEED,
            "policy_randomness_master_seed": POLICY_RANDOMNESS_MASTER_SEED,
            "observation_noise_seed": "uses the environment realization seed with domain-separated outcome/failure channels",
            "policy_receives_environment_seed": False,
        },
        "resource_schema": [
            {"name": item.name, "unit": item.unit} for item in RESOURCE_SCHEMA.dimensions
        ],
        "problems": [problem.to_dict() for problem in problems],
        "episodes": [episode.to_dict() for episode in episodes],
    }


def freeze_population(
    path: Path, problems: Iterable[ProblemSpec], episodes: Iterable[EpisodeSpec]
) -> str:
    payload = population_payload(problems, episodes)
    digest = content_hash(payload)
    envelope = dict(payload)
    envelope["population_hash"] = digest
    write_new_json(path, envelope)
    return digest


def load_population(path: Path) -> tuple[tuple[ProblemSpec, ...], tuple[EpisodeSpec, ...], str]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    digest = str(raw.pop("population_hash"))
    if content_hash(raw) != digest:
        raise ValueError("population manifest hash mismatch")
    problems = tuple(ProblemSpec.from_dict(item) for item in raw["problems"])
    episodes = tuple(EpisodeSpec.from_dict(item) for item in raw["episodes"])
    return problems, episodes, digest


def write_new_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True))
        handle.write("\n")


def write_new_jsonl(path: Path, values: Iterable[object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        for value in values:
            handle.write(canonical_json(value))
            handle.write("\n")


def observation_dict(observation) -> dict:
    return {
        "observation_id": observation.observation_id,
        "payload": observation.payload,
        "provenance": observation.provenance,
        "release_step": observation.release_step,
        "source_result_id": observation.source_result_id,
        "reliability": observation.reliability,
    }


def action_dict(action) -> dict:
    return {
        "action_id": action.action_id,
        "kind": action.kind,
        "target_id": action.target_id,
        "submission": action.submission,
    }


def result_dict(result) -> dict:
    return {
        "result_id": result.result_id,
        "action_id": result.action_id,
        "status": result.status,
        "cost": result.cost.as_dict(),
        "observations": [observation_dict(item) for item in result.observations],
        "error": result.error,
        "termination": None
        if result.termination is None
        else {
            "cause": result.termination.cause.value,
            "step": result.termination.step,
            "reason": result.termination.reason,
        },
    }


def trace_dict(trace: Trace) -> dict:
    return {
        "schema_version": trace.schema_version,
        "episode_id": trace.episode_id,
        "initial_observations": [observation_dict(item) for item in trace.initial_observations],
        "transitions": [
            {
                "transition_id": transition.transition_id,
                "step": transition.step,
                "state_before_ref": transition.state_before_ref,
                "action": action_dict(transition.action),
                "result": result_dict(transition.result),
                "state_after_ref": transition.state_after_ref,
                "budget_before": dict(transition.budget_before),
                "budget_after": dict(transition.budget_after),
                "randomness_ref": transition.randomness_ref,
            }
            for transition in trace.transitions
        ],
        "termination": None
        if trace.termination is None
        else {
            "cause": trace.termination.cause.value,
            "step": trace.termination.step,
            "reason": trace.termination.reason,
        },
    }


def outcome_dict(outcome: Outcome) -> dict:
    return {
        "valid": outcome.valid,
        "invalid_reason": outcome.invalid_reason,
        "submission": outcome.submission,
        "correct": outcome.correct,
        "abstained": outcome.abstained,
        "decision_loss": outcome.decision_loss,
        "raw_resources": outcome.raw_resources.as_dict(),
        "combined_objective": outcome.combined_objective,
        "decision_regret": outcome.decision_regret,
        "combined_regret": outcome.combined_regret,
        "stopping_regret": outcome.stopping_regret,
        "premature_stop": outcome.premature_stop,
        "unnecessary_actions": outcome.unnecessary_actions,
        "avoidable_resource_cost": outcome.avoidable_resource_cost,
    }


def run_artifact(
    run: RunRecord,
    outcome: Outcome,
    hidden_state: str,
    environment_realization_seed: int,
    population_hash: str,
) -> dict:
    public = {
        "run_id": run.run_id,
        "episode_id": run.episode_id,
        "problem_id": run.problem_id,
        "family": run.family,
        "policy": run.policy_name,
        "policy_access_class": run.policy_access_class,
        "policy_assumptions": list(run.policy_assumptions),
        "policy_visible_model_access": run.policy_visible_model_access,
        "policy_randomness_seed": run.policy_randomness_seed,
        "valid": run.valid,
        "invalid_reason": run.invalid_reason,
        "trace": trace_dict(run.trace),
    }
    restricted = {
        "visibility": "evaluator_only",
        "hidden_state": hidden_state,
        "environment_realization_seed": environment_realization_seed,
        "outcome": outcome_dict(outcome),
    }
    artifact = {
        "schema_version": 1,
        "population_hash": population_hash,
        "public": public,
        "restricted": restricted,
    }
    artifact["record_hash"] = content_hash(artifact)
    return artifact


def oracle_artifact(
    run: RunRecord,
    hidden_state: str,
    environment_realization_seed: int,
    population_hash: str,
) -> dict:
    value = {
        "schema_version": 1,
        "population_hash": population_hash,
        "visibility": "evaluator_only",
        "episode_id": run.episode_id,
        "hidden_state": hidden_state,
        "environment_realization_seed": environment_realization_seed,
        "oracle_policy": run.policy_name,
        "valid": run.valid,
        "trace": trace_dict(run.trace),
        "final_submission": run.final_submission,
    }
    value["record_hash"] = content_hash(value)
    return value


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def verify_record_hash(record: Mapping[str, object]) -> bool:
    raw = dict(record)
    digest = raw.pop("record_hash", None)
    return digest == content_hash(raw)
