"""Fail-closed artifacts for the frozen MicroGym routing-v1 benchmark."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable, Mapping

from ser.core.types import canonical_json, content_hash
from ser.microgym.model import EpisodeSpec, ProblemSpec, RESOURCE_SCHEMA
from ser.microgym.routing import (
    ROUTING_ENVIRONMENT_REALIZATION_MASTER_SEED,
    ROUTING_EPISODES_PER_REGIME,
    ROUTING_POLICY_RANDOMNESS_MASTER_SEED,
    ROUTING_POPULATION_SEED,
    RoutingRegime,
)

from .artifacts import trace_dict, verify_record_hash, write_new_json, write_new_jsonl
from .routing import RoutingOracle, RoutingRun, compute_routing_oracle


BENCHMARK_NAME = "microgym-routing-v1"


def _derived_seed(master: int, label: str) -> int:
    payload = f"{BENCHMARK_NAME}|{master}|{label}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


def build_routing_episodes(
    regimes: Iterable[RoutingRegime],
) -> tuple[EpisodeSpec, ...]:
    episodes: list[EpisodeSpec] = []
    for regime in regimes:
        problem = regime.problem
        action_ids = tuple(test.public.action_id for test in problem.tests)
        for index in range(ROUTING_EPISODES_PER_REGIME):
            episode_id = f"mgr1-{problem.problem_id}-e{index:03d}"
            hidden_state = problem.hypotheses[index % len(problem.hypotheses)]
            order_digest = hashlib.sha256(
                f"{BENCHMARK_NAME}|{ROUTING_POPULATION_SEED}|{episode_id}|order".encode(
                    "utf-8"
                )
            ).digest()
            action_order = action_ids if order_digest[0] % 2 == 0 else tuple(reversed(action_ids))
            episodes.append(
                EpisodeSpec(
                    episode_id=episode_id,
                    problem_id=problem.problem_id,
                    hidden_state=hidden_state,
                    environment_seed=_derived_seed(
                        ROUTING_ENVIRONMENT_REALIZATION_MASTER_SEED,
                        f"{episode_id}|observation-noise",
                    ),
                    action_order=action_order,
                )
            )
    return tuple(episodes)


def oracle_dict(oracle: RoutingOracle) -> dict:
    return {
        "problem_id": oracle.problem_id,
        "loss_convention": "lower_is_better",
        "voa_convention": "open_loop_loss_minus_closed_loop_loss",
        "open_loop_loss": oracle.open_loop_loss,
        "open_loop_action": oracle.open_loop_action,
        "closed_loop_loss": oracle.closed_loop_loss,
        "closed_loop_actions": dict(oracle.closed_loop_actions),
        "value_of_adaptivity": oracle.value_of_adaptivity,
        "eligible_conditional_node": oracle.eligible_conditional_node,
    }


def _preregistration_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def routing_population_payload(
    regimes: Iterable[RoutingRegime],
    episodes: Iterable[EpisodeSpec],
    preregistration_path: Path,
) -> dict:
    regime_items = []
    for regime in regimes:
        problem = regime.problem
        view = problem.public_view(tuple(test.public.action_id for test in problem.tests))
        regime_items.append(
            {
                "problem": problem.to_dict(),
                "declared_voa_band": regime.declared_voa_band,
                "oracle_adaptivity_structure": oracle_dict(compute_routing_oracle(view)),
            }
        )
    return {
        "schema_version": 1,
        "benchmark": BENCHMARK_NAME,
        "visibility": "evaluator_only_experiment_definition",
        "frozen_before_candidate_aggregation": True,
        "preregistration_sha256": _preregistration_hash(preregistration_path),
        "primary_hypothesis": (
            "In regimes with positive oracle VOA, a same-model closed-loop policy "
            "can use a released cue to choose a better next acquisition than the "
            "best acquisition committed before that cue."
        ),
        "primary_objective": "terminal decision loss after one required acquisition",
        "fixed_acquisition_horizon": 1,
        "adaptive_stop_available": False,
        "voa_definition": "exact_open_loop_expected_loss_minus_exact_closed_loop_expected_loss",
        "seed_roles": {
            "population_regime_seed": ROUTING_POPULATION_SEED,
            "environment_realization_master_seed": ROUTING_ENVIRONMENT_REALIZATION_MASTER_SEED,
            "observation_noise_seed": (
                "episode-specific derivation from the evaluator-only environment master"
            ),
            "policy_randomness_master_seed": ROUTING_POLICY_RANDOMNESS_MASTER_SEED,
            "policy_receives_environment_seed": False,
        },
        "resource_schema": [
            {"name": item.name, "unit": item.unit} for item in RESOURCE_SCHEMA.dimensions
        ],
        "regimes": regime_items,
        "episodes": [episode.to_dict() for episode in episodes],
    }


def freeze_routing_population(
    path: Path,
    regimes: Iterable[RoutingRegime],
    episodes: Iterable[EpisodeSpec],
    preregistration_path: Path,
) -> str:
    payload = routing_population_payload(regimes, episodes, preregistration_path)
    digest = content_hash(payload)
    write_new_json(path, {**payload, "population_hash": digest})
    return digest


def load_routing_population(
    path: Path,
) -> tuple[tuple[RoutingRegime, ...], tuple[EpisodeSpec, ...], str, dict]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    digest = str(raw.pop("population_hash"))
    if content_hash(raw) != digest:
        raise ValueError("routing population manifest hash mismatch")
    regimes = tuple(
        RoutingRegime(
            ProblemSpec.from_dict(item["problem"]), str(item["declared_voa_band"])
        )
        for item in raw["regimes"]
    )
    episodes = tuple(EpisodeSpec.from_dict(item) for item in raw["episodes"])
    return regimes, episodes, digest, raw


def routing_run_artifact(
    run: RoutingRun,
    episode: EpisodeSpec,
    population_hash: str,
) -> dict:
    raw_resources = RESOURCE_SCHEMA.vector()
    for transition in run.trace.transitions:
        raw_resources = raw_resources + transition.result.cost
    artifact = {
        "schema_version": 1,
        "benchmark": BENCHMARK_NAME,
        "population_hash": population_hash,
        "public": {
            "run_id": run.run_id,
            "episode_id": run.episode_id,
            "problem_id": run.problem_id,
            "family": run.family,
            "policy": run.policy_name,
            "policy_access_class": run.policy_access_class,
            "policy_visible_model_access": run.policy_visible_model_access,
            "policy_randomness_seed": run.policy_randomness_seed,
            "fixed_acquisition_horizon": 1,
            "adaptive_stop_available": False,
            "valid": run.valid,
            "invalid_reason": run.invalid_reason,
            "trace": trace_dict(run.trace),
            "decision_diagnostic": run.public_diagnostic,
        },
        "restricted": {
            "visibility": "evaluator_only",
            "hidden_state": episode.hidden_state,
            "environment_realization_seed": episode.environment_seed,
            "outcome": {
                "correct": run.correct,
                "decision_loss": run.decision_loss,
                "submission": run.final_submission,
                "raw_resources": raw_resources.as_dict(),
            },
        },
    }
    artifact["record_hash"] = content_hash(artifact)
    return artifact


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def write_routing_runs(path: Path, records: Iterable[dict]) -> None:
    write_new_jsonl(path, records)


def verify_routing_record_hashes(records: Iterable[Mapping[str, object]]) -> bool:
    return all(verify_record_hash(record) for record in records)


def artifact_digest(value: object) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
