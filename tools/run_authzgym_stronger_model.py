#!/usr/bin/env python3
"""Prepare, freeze, execute, and analyze the stronger-model capability gate."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from statistics import fmean

from ser.authzgym.generation import (
    MECHANISMS,
    build_confirmation_episodes,
)
from ser.authzgym.model import SemanticObservation
from ser.authzgym.realmodel import ProviderError, _usage_from_response, load_real_model_condition
from ser.authzgym.semantic_contract import (
    SEMANTIC_EQUIVALENCE_VARIANTS,
    VARIANTS,
    ContractV12Error,
    build_stress_cases,
    episode_from_case,
    parse_content,
)
from ser.authzgym.supervised_transport import (
    SupervisedSemanticContractClientV12,
    TransportUnavailable,
)
from ser.authzgym.tunnel_supervisor import TunnelError, TunnelSupervisor, load_tunnel_policy
from ser.core.types import canonical_json, content_hash
from ser.evaluation.authz_artifacts import (
    file_sha256,
    freeze_population,
    load_population,
)
from ser.evaluation.authz_contract_analysis import (
    CONTRACT_THRESHOLDS,
    SEMANTIC_THRESHOLDS,
    _action_diagnostic,
    _normalize,
    summarize as summarize_semantic,
)


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "experiments/authzgym_stronger_model_v1"
CONTRACT_SOURCE = ROOT / "experiments/authzgym_semantic_contract_v1_2"
TRANSPORT_SOURCE = ROOT / "experiments/authzgym_transport_envelope_v1"
STATIC_SOURCE = ROOT / "experiments/authzgym_static_v1_1"
EXPERIMENT_ID = "authzgym-stronger-model-v1"
STAGES = ("smoke", "development", "confirmation")
DEVELOPMENT_SELECTION_INDICES = (0, 5, 2, 7)
GLOBAL_MAXIMUM_API_SUBMISSIONS = 304
PREFLIGHT_COST_USD = 0.012318
PREFLIGHT_API_SUBMISSIONS = 4


def _paths(experiment: Path) -> dict[str, Path]:
    return {
        "preregistration": experiment / "PREREGISTRATION.md",
        "model_selection": experiment / "MODEL_SELECTION.json",
        "config": experiment / "model_config.json",
        "confirmation_source": experiment / "confirmatory_source_population.json",
        "smoke_population": experiment / "SMOKE_POPULATION.json",
        "development_population": experiment / "DEVELOPMENT_POPULATION.json",
        "confirmation_population": experiment / "CONFIRMATORY_POPULATION.json",
        "frozen": experiment / "FROZEN_INPUTS.json",
        "cost_gate": experiment / "COST_GATE.json",
        "validation": experiment / "validation.json",
        "summary": experiment / "summary.json",
        "report": experiment / "REPORT.md",
        "interpretation": experiment / "INTERPRETATION.md",
        "implementation_notes": experiment / "IMPLEMENTATION_NOTES.md",
    }


def _verify_preflight_archive(experiment: Path) -> dict:
    archive = experiment / "preflight_attempt_1"
    expected_hashes = {
        "FROZEN_INPUTS.json": "4e78c257840daee32bdab93a769995a518e887535139d84ac50bd0050b2cfa1e",
        "COST_GATE.json": "2cf50dd3a940579681b38b36d6565f6a7921645c1f0ba8abd5bfeea83e68cf91",
        "smoke/execution.json": "4798b9e510285f1a112515d8aeefb6f99cf5f70ff45687ef34b56933e9855906",
        "smoke/provider_responses.jsonl": "8e3a47731a3c2d3ad48a76f2bab3eb2e17ca6eab388c415b6d3e0063d641b27f",
        "smoke/runs.jsonl": "7ad6708053c76fd0d7a0b667ff4bcfded772108a06b7e642dadad52439a320a4",
        "smoke/transport_attempts.jsonl": "d2233a5f8cb69e4b70d142138cf363b25ac3e03953bea6755a3d094cfe534c6f",
        "smoke/tunnel_events.jsonl": "9d20a14d7faac6427423cf6f3635c890930f58ed5f6b8cba4650f468cf9a721b",
    }
    observed = {
        name: file_sha256(archive / name) for name in expected_hashes
    }
    if observed != expected_hashes:
        raise ValueError("preserved smoke preflight hashes changed")
    manifest = _json(archive / "FROZEN_INPUTS.json")
    if manifest["manifest_hash"] != "525b2377d3ac71bb05c6ded88977a8d08a51a1f4577a685e57396a87b1b59ac6":
        raise ValueError("preserved smoke preflight manifest identity changed")
    execution = _json(archive / "smoke/execution.json")
    runs = _jsonl(archive / "smoke/runs.jsonl")
    if not (
        _record_hash_valid(execution)
        and len(runs) == 4
        and all(_record_hash_valid(item) and item["valid"] for item in runs)
        and execution["provider_attempts"] == PREFLIGHT_API_SUBMISSIONS
        and abs(execution["stage_cost_usd"] - PREFLIGHT_COST_USD) < 1e-12
    ):
        raise ValueError("preserved smoke preflight accounting changed")
    return {
        "manifest_hash": manifest["manifest_hash"],
        "runner_sha256": manifest["files"][
            "implementation/tools/run_authzgym_stronger_model.py"
        ],
        "provider_attempts": execution["provider_attempts"],
        "provider_responses": execution["provider_responses"],
        "valid_logical_responses": execution["valid_logical_responses"],
        "transport_failures": execution["raw_transport_failures"],
        "cost_usd": execution["stage_cost_usd"],
        "input_tokens": sum(item["resources"]["input_tokens"] for item in runs),
        "cached_input_tokens": sum(
            item["resources"]["cached_input_tokens"] for item in runs
        ),
        "output_tokens": sum(item["resources"]["output_tokens"] for item in runs),
        "reasoning_output_tokens": sum(
            item["resources"]["reasoning_output_tokens"] for item in runs
        ),
        "latency_ms": sum(item["resources"]["latency_ms"] for item in runs),
    }


def _stage_paths(experiment: Path, stage: str) -> dict[str, Path]:
    root = experiment / stage
    return {
        "root": root,
        "transport_attempts": root / "transport_attempts.jsonl",
        "responses": root / "provider_responses.jsonl",
        "tunnel_events": root / "tunnel_events.jsonl",
        "runs": root / "runs.jsonl",
        "execution": root / "execution.json",
    }


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def _write_new(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(text)


def _write_new_json(path: Path, value: dict) -> None:
    _write_new(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def _append_jsonl(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(canonical_json(value) + "\n")
        handle.flush()


def _record_hash_valid(value: dict) -> bool:
    payload = dict(value)
    digest = payload.pop("record_hash", None)
    return isinstance(digest, str) and content_hash(payload) == digest


def _population_hash_valid(population: dict) -> bool:
    payload = dict(population)
    digest = payload.pop("population_hash", None)
    return isinstance(digest, str) and content_hash(payload) == digest


def _capability_population(
    stage: str,
    cases: list[dict],
    schedule: list[dict],
    *,
    source_population_hash: str,
    exposed: bool,
) -> dict:
    payload = {
        "schema_version": 1,
        "experiment": EXPERIMENT_ID,
        "stage": stage,
        "exposed_before_experiment": exposed,
        "semantic_contract_version": "v1.2",
        "source_population_hash": source_population_hash,
        "source_episode_count": len({item["source_episode_id"] for item in cases}),
        "variant_count_per_episode": len({item["variant"] for item in cases}),
        "repeats_per_case": 1,
        "cases": cases,
        "schedule": schedule,
    }
    return {**payload, "population_hash": content_hash(payload)}


def _case_order(cases: list[dict], source_ids: list[str]) -> list[dict]:
    indexed = {
        (item["source_episode_id"], item["variant"]): item for item in cases
    }
    return [indexed[(source_id, variant)] for variant in VARIANTS for source_id in source_ids]


def _correct_confirmation_case_metadata(case: dict) -> dict:
    value = copy.deepcopy(case)
    value["episode"]["split"] = "confirmation"
    return value


def prepare(experiment: Path) -> dict:
    paths = _paths(experiment)
    generated = (
        paths["confirmation_source"],
        paths["smoke_population"],
        paths["development_population"],
        paths["confirmation_population"],
    )
    if any(path.exists() for path in generated):
        raise FileExistsError("a prepared population already exists")

    exposed_population = _json(CONTRACT_SOURCE / "STRESS_POPULATION.json")
    if not _population_hash_valid(exposed_population):
        raise ValueError("source semantic-contract population hash mismatch")
    development_episodes, source_hash, _ = load_population(
        STATIC_SOURCE / "development_population.json"
    )
    selected_episodes = tuple(
        development_episodes[index] for index in DEVELOPMENT_SELECTION_INDICES
    )
    if tuple(item.truth.mechanism_id for item in selected_episodes) != MECHANISMS:
        raise ValueError("balanced development selection no longer covers h1-h4 in order")
    selected_ids = [item.episode_id for item in selected_episodes]
    development_cases = _case_order(
        [
            copy.deepcopy(item)
            for item in exposed_population["cases"]
            if item["source_episode_id"] in set(selected_ids)
        ],
        selected_ids,
    )
    development_schedule = [
        {"case_id": item["case_id"], "repeat": 1} for item in development_cases
    ]
    development = _capability_population(
        "development",
        development_cases,
        development_schedule,
        source_population_hash=source_hash,
        exposed=True,
    )
    smoke_cases = [
        copy.deepcopy(item)
        for item in development_cases
        if item["variant"] == "base_entry"
    ]
    smoke = _capability_population(
        "smoke",
        smoke_cases,
        [{"case_id": item["case_id"], "repeat": 1} for item in smoke_cases],
        source_population_hash=source_hash,
        exposed=True,
    )

    confirmation_episodes = build_confirmation_episodes()
    confirmation_source_hash = freeze_population(
        paths["confirmation_source"],
        "confirmation",
        confirmation_episodes,
        paths["preregistration"],
        (CONTRACT_SOURCE / "prompts/semantic_observation_v1_2.txt",),
        paths["config"],
    )
    confirmation_ids = [item.episode_id for item in confirmation_episodes]
    confirmation_cases = _case_order(
        [
            _correct_confirmation_case_metadata(item)
            for item in build_stress_cases(confirmation_episodes)
        ],
        confirmation_ids,
    )
    confirmation = _capability_population(
        "confirmation",
        confirmation_cases,
        [{"case_id": item["case_id"], "repeat": 1} for item in confirmation_cases],
        source_population_hash=confirmation_source_hash,
        exposed=False,
    )

    exposed_episodes = []
    for name in (
        "development_population.json",
        "evaluation_population.json",
        "perturbation_population.json",
    ):
        episodes, _, _ = load_population(STATIC_SOURCE / name)
        exposed_episodes.extend(episodes)
    exposed_ids = {item.episode_id for item in exposed_episodes}
    exposed_public = {
        content_hash(item["model_visible_input"])
        for item in exposed_population["cases"]
    }
    confirmation_public = {
        content_hash(item["model_visible_input"])
        for item in confirmation_cases
    }
    if exposed_ids & set(confirmation_ids):
        raise ValueError("fresh confirmation source IDs overlap exposed episodes")
    if exposed_public & confirmation_public:
        raise ValueError("fresh confirmation model-visible inputs overlap exposed v1.2 cases")
    _write_new_json(paths["smoke_population"], smoke)
    _write_new_json(paths["development_population"], development)
    _write_new_json(paths["confirmation_population"], confirmation)
    return {
        "smoke_population_hash": smoke["population_hash"],
        "development_population_hash": development["population_hash"],
        "confirmation_source_population_hash": confirmation_source_hash,
        "confirmation_population_hash": confirmation["population_hash"],
        "logical_calls": {
            "smoke": len(smoke["schedule"]),
            "development": len(development["schedule"]),
            "confirmation": len(confirmation["schedule"]),
        },
        "confirmation_public_overlap_with_exposed": 0,
    }


def _file_inputs(experiment: Path) -> dict[str, Path]:
    paths = _paths(experiment)
    return {
        "PREREGISTRATION.md": paths["preregistration"],
        "MODEL_SELECTION.json": paths["model_selection"],
        "model_config.json": paths["config"],
        "SMOKE_POPULATION.json": paths["smoke_population"],
        "DEVELOPMENT_POPULATION.json": paths["development_population"],
        "CONFIRMATORY_POPULATION.json": paths["confirmation_population"],
        "confirmatory_source_population.json": paths["confirmation_source"],
        "PREFLIGHT_FAILURE.md": experiment / "PREFLIGHT_FAILURE.md",
        "preflight_attempt_1/FROZEN_INPUTS.json": experiment / "preflight_attempt_1/FROZEN_INPUTS.json",
        "preflight_attempt_1/COST_GATE.json": experiment / "preflight_attempt_1/COST_GATE.json",
        "preflight_attempt_1/smoke/execution.json": experiment / "preflight_attempt_1/smoke/execution.json",
        "preflight_attempt_1/smoke/provider_responses.jsonl": experiment / "preflight_attempt_1/smoke/provider_responses.jsonl",
        "preflight_attempt_1/smoke/runs.jsonl": experiment / "preflight_attempt_1/smoke/runs.jsonl",
        "preflight_attempt_1/smoke/transport_attempts.jsonl": experiment / "preflight_attempt_1/smoke/transport_attempts.jsonl",
        "preflight_attempt_1/smoke/tunnel_events.jsonl": experiment / "preflight_attempt_1/smoke/tunnel_events.jsonl",
        "semantic_contract/FROZEN_INPUTS.json": CONTRACT_SOURCE / "FROZEN_INPUTS.json",
        "semantic_contract/STRESS_POPULATION.json": CONTRACT_SOURCE / "STRESS_POPULATION.json",
        "semantic_contract/prompt.txt": CONTRACT_SOURCE / "prompts/semantic_observation_v1_2.txt",
        "semantic_contract/vocabulary.json": CONTRACT_SOURCE / "schemas/semantic_vocabulary_v1_2.json",
        "transport/transport_config.json": TRANSPORT_SOURCE / "transport_config.json",
        "source/development_population.json": STATIC_SOURCE / "development_population.json",
        "source/evaluation_population.json": STATIC_SOURCE / "evaluation_population.json",
        "source/perturbation_population.json": STATIC_SOURCE / "perturbation_population.json",
        "implementation/src/ser/authzgym/generation.py": ROOT / "src/ser/authzgym/generation.py",
        "implementation/src/ser/authzgym/semantic_contract.py": ROOT / "src/ser/authzgym/semantic_contract.py",
        "implementation/src/ser/authzgym/semantic_transport.py": ROOT / "src/ser/authzgym/semantic_transport.py",
        "implementation/src/ser/authzgym/supervised_transport.py": ROOT / "src/ser/authzgym/supervised_transport.py",
        "implementation/src/ser/authzgym/tunnel_supervisor.py": ROOT / "src/ser/authzgym/tunnel_supervisor.py",
        "implementation/src/ser/evaluation/authz_contract_analysis.py": ROOT / "src/ser/evaluation/authz_contract_analysis.py",
        "implementation/tools/run_authzgym_stronger_model.py": ROOT / "tools/run_authzgym_stronger_model.py",
        "implementation/tools/verify_authzgym_stronger_model.py": ROOT / "tools/verify_authzgym_stronger_model.py",
        "tests/test_authzgym_stronger_model.py": ROOT / "tests/test_authzgym_stronger_model.py",
    }


def _project_cost(condition, logical_calls: int) -> dict:
    maximum_submissions = logical_calls * 3
    projected_input = (
        maximum_submissions * condition.input_token_ceiling_per_sequential_run
    )
    projected_output = maximum_submissions * condition.max_output_tokens_per_artifact
    projected_cost = (
        projected_input * condition.input_price_per_million_usd
        + projected_output * condition.output_price_per_million_usd
    ) / 1_000_000.0
    return {
        "scheduled_logical_calls": logical_calls,
        "maximum_semantic_attempts_per_logical_call": condition.maximum_attempts_per_semantic_call,
        "maximum_transport_replays_per_logical_call": 1,
        "maximum_api_submissions": maximum_submissions,
        "projected_uncached_input_tokens": projected_input,
        "projected_output_tokens": projected_output,
        "projected_complete_cost_usd": projected_cost,
        "proceed": (
            maximum_submissions <= GLOBAL_MAXIMUM_API_SUBMISSIONS
            and projected_cost < condition.hard_spend_ceiling_usd
        ),
    }


def freeze(experiment: Path) -> dict:
    paths = _paths(experiment)
    for path in (paths["frozen"], paths["cost_gate"]):
        if path.exists():
            raise FileExistsError(f"frozen artifact already exists: {path.name}")
    populations = {
        stage: _json(paths[f"{stage}_population"])
        for stage in STAGES
    }
    if not all(_population_hash_valid(item) for item in populations.values()):
        raise ValueError("prepared population hash mismatch")
    expected = {"smoke": 4, "development": 32, "confirmation": 64}
    observed = {stage: len(item["schedule"]) for stage, item in populations.items()}
    if observed != expected:
        raise ValueError(f"unexpected stage schedule: {observed}")
    preflight = _verify_preflight_archive(experiment)
    files = {
        name: file_sha256(path) for name, path in _file_inputs(experiment).items()
    }
    payload = {
        "schema_version": 1,
        "experiment": EXPERIMENT_ID,
        "frozen_before_authzgym_inference": True,
        "semantic_contract_version": "v1.2",
        "selected_model": "patchersniper_praneeth/gpt-5.4-mini",
        "files": files,
        "population_hashes": {
            stage: population["population_hash"]
            for stage, population in populations.items()
        },
        "contract_thresholds": CONTRACT_THRESHOLDS,
        "semantic_thresholds": SEMANTIC_THRESHOLDS,
        "development_early_stop_checkpoints": [8, 16, 24],
        "confirmation_requires_development_pass": True,
        "confirmation_scored_only_after_complete_freeze": True,
        "preserved_nonsemantic_preflight": preflight,
        "run_schedules": {
            stage: population["schedule"] for stage, population in populations.items()
        },
    }
    manifest = {**payload, "manifest_hash": content_hash(payload)}
    condition = load_real_model_condition(paths["config"])
    projection = _project_cost(condition, sum(observed.values()))
    cost_gate = {
        "schema_version": 1,
        "experiment": EXPERIMENT_ID,
        "frozen_inputs_manifest_hash": manifest["manifest_hash"],
        **projection,
        "preserved_preflight_api_submissions": preflight["provider_attempts"],
        "preserved_preflight_cost_usd": preflight["cost_usd"],
        "projected_total_api_submissions_including_preflight": (
            projection["maximum_api_submissions"] + preflight["provider_attempts"]
        ),
        "projected_total_cost_usd_including_preflight": (
            projection["projected_complete_cost_usd"] + preflight["cost_usd"]
        ),
        "hard_spend_ceiling_usd": condition.hard_spend_ceiling_usd,
        "cost_basis": "official list pricing applied to provider-reported usage; not an institutional billing statement",
        "user_approved_ceiling_date": "2026-09-03",
    }
    cost_gate["proceed"] = (
        cost_gate["proceed"]
        and cost_gate["projected_total_api_submissions_including_preflight"]
        <= GLOBAL_MAXIMUM_API_SUBMISSIONS
        and cost_gate["projected_total_cost_usd_including_preflight"]
        < condition.hard_spend_ceiling_usd
    )
    cost_gate["record_hash"] = content_hash(cost_gate)
    if not cost_gate["proceed"]:
        raise RuntimeError("maximum staged workload fails the $2.50 cost gate")
    _write_new_json(paths["frozen"], manifest)
    _write_new_json(paths["cost_gate"], cost_gate)
    return cost_gate


def _load_manifest(experiment: Path) -> tuple[dict, dict[str, str]]:
    paths = _paths(experiment)
    manifest = _json(paths["frozen"])
    payload = dict(manifest)
    digest = payload.pop("manifest_hash", None)
    if content_hash(payload) != digest:
        raise ValueError("frozen manifest hash mismatch")
    observed = {
        name: file_sha256(path) for name, path in _file_inputs(experiment).items()
    }
    if observed != manifest["files"]:
        raise ValueError("a frozen stronger-model input changed")
    cost_gate = _json(paths["cost_gate"])
    if not _record_hash_valid(cost_gate) or not cost_gate["proceed"]:
        raise ValueError("cost gate is invalid")
    return manifest, observed


def _population_for_stage(experiment: Path, stage: str) -> dict:
    return _json(_paths(experiment)[f"{stage}_population"])


def _error_text(exc: Exception) -> str:
    value = f"{type(exc).__name__}:{exc}"
    secret = os.environ.get("OPENAI_API_KEY", "")
    return value.replace(secret, "[REDACTED]") if secret else value


def _semantic_item_sets(case: dict, run: dict) -> dict[str, tuple[set, set]]:
    expected = case["evaluator_only"]["expected_content"]
    content = run["result"]["parsed"]["provider_content"]
    return {
        "facts": (
            {key for key, present in content["facts"].items() if present},
            {key for key, present in expected["facts"].items() if present},
        ),
        "effects": (
            {
                (key, value)
                for key, value in content["hypothesis_effects"].items()
                if value in ("support", "contradict")
            },
            {
                (key, value)
                for key, value in expected["hypothesis_effects"].items()
                if value in ("support", "contradict")
            },
        ),
        "unresolved": (
            {
                (target, relation)
                for target, relations in content["unresolved_targets"].items()
                for relation, present in relations.items()
                if present
            },
            {
                (target, relation)
                for target, relations in expected["unresolved_targets"].items()
                for relation, present in relations.items()
                if present
            },
        ),
    }


def development_optimistic_bounds(
    population: dict, runs: list[dict], responses: list[dict]
) -> dict:
    total = len(population["schedule"])
    cases = {item["case_id"]: item for item in population["cases"]}
    completed = len(runs)
    remaining_schedule = population["schedule"][completed:]
    layer_thresholds = {
        "facts": (SEMANTIC_THRESHOLDS["minimum_fact_precision"], SEMANTIC_THRESHOLDS["minimum_fact_recall"]),
        "effects": (SEMANTIC_THRESHOLDS["minimum_effect_precision"], SEMANTIC_THRESHOLDS["minimum_effect_recall"]),
        "unresolved": (SEMANTIC_THRESHOLDS["minimum_unresolved_precision"], SEMANTIC_THRESHOLDS["minimum_unresolved_recall"]),
    }
    layers = {}
    reasons = []
    for layer, (precision_floor, recall_floor) in layer_thresholds.items():
        true_positive = predicted = expected_seen = 0
        for run in runs:
            if not run["valid"]:
                continue
            actual, expected = _semantic_item_sets(cases[run["case_id"]], run)[layer]
            true_positive += len(actual & expected)
            predicted += len(actual)
            expected_seen += len(expected)
        remaining_expected = 0
        for scheduled in remaining_schedule:
            expected = cases[scheduled["case_id"]]["evaluator_only"]["expected_content"]
            if layer == "facts":
                remaining_expected += sum(expected["facts"].values())
            elif layer == "effects":
                remaining_expected += sum(
                    value in ("support", "contradict")
                    for value in expected["hypothesis_effects"].values()
                )
            else:
                remaining_expected += sum(
                    present
                    for relations in expected["unresolved_targets"].values()
                    for present in relations.values()
                )
        optimistic_tp = true_positive + remaining_expected
        optimistic_predicted = predicted + remaining_expected
        optimistic_expected = expected_seen + remaining_expected
        max_precision = optimistic_tp / optimistic_predicted if optimistic_predicted else 1.0
        max_recall = optimistic_tp / optimistic_expected if optimistic_expected else 1.0
        layers[layer] = {
            "maximum_final_precision": max_precision,
            "maximum_final_recall": max_recall,
            "precision_threshold": precision_floor,
            "recall_threshold": recall_floor,
        }
        if max_precision < precision_floor:
            reasons.append(f"{layer}_precision_mathematically_unreachable")
        if max_recall < recall_floor:
            reasons.append(f"{layer}_recall_mathematically_unreachable")

    action_results = []
    for run in runs:
        if not run["valid"]:
            continue
        parsed_observation = run["result"]["parsed"]["semantic_observation"]
        action_results.append(
            _action_diagnostic(
                cases[run["case_id"]],
                SemanticObservation.from_dict(parsed_observation),
            )
        )
    remaining = total - completed
    top1_max = (
        sum(item["top1"] for item in action_results) + remaining
    ) / total
    top2_max = (
        sum(item["top2"] for item in action_results) + remaining
    ) / total
    regret_min = sum(item["normalized_regret"] for item in action_results) / total
    actions = {
        "maximum_final_top1": top1_max,
        "maximum_final_top2": top2_max,
        "minimum_final_mean_normalized_regret": regret_min,
    }
    if top1_max < SEMANTIC_THRESHOLDS["minimum_action_top1"]:
        reasons.append("action_top1_mathematically_unreachable")
    if top2_max < SEMANTIC_THRESHOLDS["minimum_action_top2"]:
        reasons.append("action_top2_mathematically_unreachable")
    if regret_min > SEMANTIC_THRESHOLDS["maximum_action_normalized_regret"]:
        reasons.append("action_regret_mathematically_unreachable")

    first_attempts = [item for item in responses if item["attempt"] == 1]
    first_valid = sum(item["contract_validation"]["valid"] for item in first_attempts)
    final_valid = sum(item["valid"] for item in runs)
    maximum_first_rate = (first_valid + total - len(first_attempts)) / total
    maximum_post_retry_rate = (final_valid + remaining) / total
    contract = {
        "maximum_final_first_attempt_valid_rate": maximum_first_rate,
        "maximum_final_post_retry_valid_rate": maximum_post_retry_rate,
    }
    if maximum_first_rate < CONTRACT_THRESHOLDS["minimum_first_attempt_schema_valid_rate"]:
        reasons.append("first_attempt_schema_validity_mathematically_unreachable")
    if maximum_post_retry_rate < CONTRACT_THRESHOLDS["minimum_post_retry_valid_rate"]:
        reasons.append("post_retry_validity_mathematically_unreachable")
    return {
        "completed_calls": completed,
        "remaining_calls": remaining,
        "layers": layers,
        "actions": actions,
        "contract": contract,
        "futile": bool(reasons),
        "reasons": reasons,
    }


def _prior_accounting(experiment: Path, stage: str) -> tuple[float, int]:
    preflight = _verify_preflight_archive(experiment)
    cost = preflight["cost_usd"]
    calls = preflight["provider_attempts"]
    for candidate in STAGES:
        if candidate == stage:
            break
        path = _stage_paths(experiment, candidate)["execution"]
        if path.exists():
            value = _json(path)
            cost += value["stage_cost_usd"]
            calls += value["provider_attempts"]
    return cost, calls


def _run_stage(experiment: Path, stage: str) -> dict:
    manifest, _ = _load_manifest(experiment)
    paths = _paths(experiment)
    stage_paths = _stage_paths(experiment, stage)
    if any(path.exists() for key, path in stage_paths.items() if key != "root"):
        raise FileExistsError(f"{stage} output already exists")
    population = _population_for_stage(experiment, stage)
    if population["population_hash"] != manifest["population_hashes"][stage]:
        raise ValueError(f"{stage} population does not match the frozen manifest")
    prior_cost, prior_calls = _prior_accounting(experiment, stage)
    condition = load_real_model_condition(paths["config"])
    policy = load_tunnel_policy(TRANSPORT_SOURCE / "transport_config.json")
    prompt = (CONTRACT_SOURCE / "prompts/semantic_observation_v1_2.txt").read_text(
        encoding="utf-8"
    )
    cases = {item["case_id"]: item for item in population["cases"]}
    responses: list[dict] = []
    transport_attempts: list[dict] = []
    tunnel_events: list[dict] = []
    runs: list[dict] = []

    def response_sink(value: dict) -> None:
        responses.append(value)
        _append_jsonl(stage_paths["responses"], value)

    def transport_sink(value: dict) -> None:
        transport_attempts.append(value)
        _append_jsonl(stage_paths["transport_attempts"], value)

    def event_sink(value: dict) -> None:
        tunnel_events.append(value)
        _append_jsonl(stage_paths["tunnel_events"], value)

    supervisor = TunnelSupervisor(policy, event_sink)
    client = SupervisedSemanticContractClientV12(
        condition,
        prompt,
        supervisor,
        policy,
        response_sink,
        transport_sink,
    )
    client.total_cost_usd = prior_cost
    prompt_hash = file_sha256(CONTRACT_SOURCE / "prompts/semantic_observation_v1_2.txt")
    config_hash = file_sha256(paths["config"])
    preregistration_hash = file_sha256(paths["preregistration"])
    transport_config_hash = file_sha256(TRANSPORT_SOURCE / "transport_config.json")
    startup_error = None
    early_stop = None
    checkpoint_bounds = []
    started = __import__("time").monotonic()
    try:
        try:
            supervisor.establish(client.connectivity_probe, reason=f"{stage}_startup")
        except TunnelError as exc:
            startup_error = _error_text(exc)
        if startup_error is None:
            for index, scheduled in enumerate(manifest["run_schedules"][stage], 1):
                if prior_calls + client.total_provider_calls >= GLOBAL_MAXIMUM_API_SUBMISSIONS:
                    raise ProviderError("global API-submission ceiling reached")
                case = cases[scheduled["case_id"]]
                call_context = {
                    "stage": stage,
                    "logical_request_index": index,
                    "case_id": case["case_id"],
                    "source_episode_id": case["source_episode_id"],
                    "variant": case["variant"],
                    "repeat": scheduled["repeat"],
                }
                before = client.accounting_snapshot()
                response_start = len(responses)
                transport_start = len(transport_attempts)
                event_start = len(tunnel_events)
                result = None
                invalid_reason = None
                permanent_transport_failure = False
                try:
                    supervisor.ensure_live(client.connectivity_probe)
                    result = client.invoke_v12(
                        case["model_visible_input"],
                        case["response_schema"],
                        episode_from_case(case),
                        tuple(case["runner_control"]["legal_target_slots"]),
                        call_context=call_context,
                    )
                except (TransportUnavailable, TunnelError) as exc:
                    invalid_reason = _error_text(exc)
                    permanent_transport_failure = True
                except (ContractV12Error, ProviderError) as exc:
                    invalid_reason = _error_text(exc)
                after = client.accounting_snapshot()
                resources = {key: after[key] - before[key] for key in after}
                record = {
                    "schema_version": 1,
                    "experiment": EXPERIMENT_ID,
                    "stage": stage,
                    "population_hash": population["population_hash"],
                    "frozen_inputs_manifest_hash": manifest["manifest_hash"],
                    **call_context,
                    "condition": condition.public_dict(),
                    "transport_policy": policy.public_dict(),
                    "prompt_sha256": prompt_hash,
                    "model_config_sha256": config_hash,
                    "preregistration_sha256": preregistration_hash,
                    "transport_config_sha256": transport_config_hash,
                    "response_schema_sha256": case["runner_control"]["schema_sha256"],
                    "response_record_hashes": [
                        item["record_hash"] for item in responses[response_start:]
                    ],
                    "transport_attempt_record_hashes": [
                        item["record_hash"] for item in transport_attempts[transport_start:]
                    ],
                    "tunnel_event_record_hashes": [
                        item["record_hash"] for item in tunnel_events[event_start:]
                    ],
                    "resources": resources,
                    "provider_response_received": bool(responses[response_start:]),
                    "permanent_transport_failure": permanent_transport_failure,
                    "valid": result is not None,
                    "invalid_reason": invalid_reason,
                    "result": result,
                    "manual_repair": False,
                }
                record["record_hash"] = content_hash(record)
                runs.append(record)
                _append_jsonl(stage_paths["runs"], record)
                if stage == "development" and index in (8, 16, 24):
                    bounds = development_optimistic_bounds(population, runs, responses)
                    checkpoint_bounds.append(bounds)
                    if bounds["futile"]:
                        early_stop = bounds
                        break
                if index % 8 == 0 or index == len(population["schedule"]):
                    print(
                        canonical_json(
                            {
                                "stage": stage,
                                "completed_logical_calls": index,
                                "scheduled_logical_calls": len(population["schedule"]),
                                "stage_api_submissions": client.total_provider_calls,
                                "global_api_submissions": prior_calls + client.total_provider_calls,
                                "global_accounted_spend_usd": client.total_cost_usd,
                            }
                        ),
                        flush=True,
                    )
    finally:
        supervisor.stop(reason=f"{stage}_runner_finally_cleanup")
    elapsed = (__import__("time").monotonic() - started) * 1000.0
    execution = {
        "schema_version": 1,
        "experiment": EXPERIMENT_ID,
        "stage": stage,
        "population_hash": population["population_hash"],
        "frozen_inputs_manifest_hash": manifest["manifest_hash"],
        "scheduled_logical_calls": len(population["schedule"]),
        "completed_logical_calls": len(runs),
        "provider_attempts": len(transport_attempts),
        "provider_responses": len(responses),
        "raw_transport_failures": sum(
            not item["provider_response_received"] for item in transport_attempts
        ),
        "semantic_retries": max(0, len(responses) - len(runs)),
        "transport_recoveries": sum(
            item["resources"]["transport_recoveries"] for item in runs
        ),
        "valid_logical_responses": sum(item["valid"] for item in runs),
        "invalid_logical_responses": sum(not item["valid"] for item in runs),
        "permanent_transport_failures": sum(
            item["permanent_transport_failure"] for item in runs
        ),
        "stage_cost_usd": client.total_cost_usd - prior_cost,
        "cumulative_cost_usd": client.total_cost_usd,
        "stage_wall_clock_ms": elapsed,
        "startup_error": startup_error,
        "development_checkpoint_bounds": checkpoint_bounds,
        "early_stop": early_stop,
    }
    execution["record_hash"] = content_hash(execution)
    _write_new_json(stage_paths["execution"], execution)
    return execution


def _stage_raw(experiment: Path, stage: str) -> dict | None:
    paths = _stage_paths(experiment, stage)
    if not paths["execution"].exists():
        return None
    return {
        "execution": _json(paths["execution"]),
        "runs": _jsonl(paths["runs"]),
        "responses": _jsonl(paths["responses"]),
        "transport_attempts": _jsonl(paths["transport_attempts"]),
        "tunnel_events": _jsonl(paths["tunnel_events"]),
    }


def _stage_integrity(experiment: Path, stage: str, population: dict, raw: dict) -> dict:
    execution = raw["execution"]
    runs = raw["runs"]
    responses = raw["responses"]
    transports = raw["transport_attempts"]
    events = raw["tunnel_events"]
    expected_schedule = [
        (item["case_id"], item["repeat"]) for item in population["schedule"]
    ]
    observed_schedule = [(item["case_id"], item["repeat"]) for item in runs]
    schedule_ok = observed_schedule == expected_schedule
    if execution["startup_error"] is not None and not runs:
        schedule_ok = True
    if stage == "development" and execution["early_stop"] is not None:
        schedule_ok = (
            observed_schedule == expected_schedule[: len(runs)]
            and len(runs) in (8, 16, 24)
            and execution["early_stop"]["futile"]
        )
    raw_hashes_ok = (
        _record_hash_valid(execution)
        and all(_record_hash_valid(item) for item in runs)
        and all(_record_hash_valid(item) for item in responses)
        and all(_record_hash_valid(item) for item in transports)
        and all(_record_hash_valid(item) for item in events)
        and all(
            hashlib.sha256(item["raw_response_body"].encode("utf-8")).hexdigest()
            == item["raw_response_sha256"]
            for item in responses
        )
    )
    response_hashes = {item["record_hash"] for item in responses}
    transport_hashes = {item["record_hash"] for item in transports}
    event_hashes = {item["record_hash"] for item in events}
    links_ok = all(
        set(item["response_record_hashes"]) <= response_hashes
        and set(item["transport_attempt_record_hashes"]) <= transport_hashes
        and set(item["tunnel_event_record_hashes"]) <= event_hashes
        for item in runs
    ) and all(
        item["transport_attempt_record_hash"] in transport_hashes
        for item in responses
    )
    cleanup = [item for item in events if item["event"] == "cleanup_complete"]
    cleanup_ok = (
        len(cleanup) == 1
        and cleanup[0]["process_exited"]
        and cleanup[0]["listener_closed"]
    )
    accounting_ok = (
        execution["completed_logical_calls"] == len(runs)
        and execution["provider_attempts"] == len(transports)
        and execution["provider_responses"] == len(responses)
        and execution["valid_logical_responses"] == sum(item["valid"] for item in runs)
        and abs(
            execution["stage_cost_usd"]
            - sum(item["resources"]["monetary_cost_usd"] for item in runs)
        ) < 1e-10
    )
    models = set()
    usages = []
    for item in responses:
        try:
            envelope = json.loads(item["raw_response_body"])
        except json.JSONDecodeError:
            continue
        if isinstance(envelope, dict) and envelope.get("model"):
            models.add(str(envelope["model"]))
        usage = _usage_from_response(envelope) if isinstance(envelope, dict) else None
        if usage and usage["input_tokens"] > 0:
            usages.append(usage)
    exact_model = models <= {"patchersniper_praneeth/gpt-5.4-mini"}
    token_ceilings = all(
        item["input_tokens"] <= 4000 and item["output_tokens"] <= 1024
        for item in usages
    )
    transport_scope = all(
        item["proxy_dns_mode"] == "socks5h_remote_resolution"
        and item["tls_verification"] is False
        and item["credential_delivery"] == "anonymous_pipe_curl_config"
        and item["http_connection_strategy"]
        == "fresh_curl_process_per_api_submission_no_shared_pool"
        for item in transports
    )
    status = all(
        (
            schedule_ok,
            raw_hashes_ok,
            links_ok,
            cleanup_ok,
            accounting_ok,
            exact_model,
            token_ceilings,
            transport_scope,
        )
    )
    return {
        "status": "pass" if status else "fail",
        "schedule_valid": schedule_ok,
        "record_hashes_valid": raw_hashes_ok,
        "cross_record_links_valid": links_ok,
        "cleanup_valid": cleanup_ok,
        "accounting_valid": accounting_ok,
        "exact_frozen_model": exact_model,
        "provider_models": sorted(models),
        "provider_token_ceilings_valid": token_ceilings,
        "dedicated_transport_scope_valid": transport_scope,
    }


def _oracle_diagnostic(population: dict) -> dict:
    actions = []
    for case in population["cases"]:
        if case["variant"] != "base_entry":
            continue
        episode = episode_from_case(case)
        observation, _ = parse_content(
            case["evaluator_only"]["expected_content"],
            episode,
            tuple(case["runner_control"]["legal_target_slots"]),
        )
        actions.append(_action_diagnostic(case, observation))
    result = {
        "canonical_episodes": len(actions),
        "top1": fmean(float(item["top1"]) for item in actions),
        "top2": fmean(float(item["top2"]) for item in actions),
        "mean_normalized_regret": fmean(
            item["normalized_regret"] for item in actions
        ),
    }
    result["passes"] = (
        result["top1"] >= SEMANTIC_THRESHOLDS["minimum_action_top1"]
        and result["top2"] >= SEMANTIC_THRESHOLDS["minimum_action_top2"]
        and result["mean_normalized_regret"]
        <= SEMANTIC_THRESHOLDS["maximum_action_normalized_regret"]
    )
    return result


def _stability(population: dict, runs: list[dict]) -> dict:
    cases = {item["case_id"]: item for item in population["cases"]}
    normalized = {}
    for run in runs:
        if run["valid"]:
            case = cases[run["case_id"]]
            normalized[(run["case_id"], run["repeat"])] = _normalize(
                case, run["result"]["parsed"]["provider_content"]
            )
    scheduled = {
        (item["case_id"], item["repeat"]) for item in population["schedule"]
    }
    by_source: dict[str, dict[str, dict]] = defaultdict(dict)
    for case in population["cases"]:
        by_source[case["source_episode_id"]][case["variant"]] = case
    equivalence = []
    for peers in by_source.values():
        if "base_entry" not in peers:
            continue
        for variant in SEMANTIC_EQUIVALENCE_VARIANTS:
            if variant not in peers:
                continue
            for repeat in (1, 2):
                left = (peers["base_entry"]["case_id"], repeat)
                right = (peers[variant]["case_id"], repeat)
                if left not in scheduled or right not in scheduled:
                    continue
                both = left in normalized and right in normalized
                equivalence.append(both and normalized[left] == normalized[right])
    repeat_pairs = []
    repeats_by_case: dict[str, set[int]] = defaultdict(set)
    for case_id, repeat in scheduled:
        repeats_by_case[case_id].add(repeat)
    for case_id, repeats in repeats_by_case.items():
        if {1, 2} <= repeats:
            left, right = (case_id, 1), (case_id, 2)
            repeat_pairs.append(
                left in normalized
                and right in normalized
                and normalized[left] == normalized[right]
            )
    return {
        "semantic_equivalence_pairs": len(equivalence),
        "semantic_equivalence_exact_rate": (
            fmean(float(item) for item in equivalence) if equivalence else None
        ),
        "repeat_pairs": len(repeat_pairs),
        "repeat_semantic_exact_rate": (
            fmean(float(item) for item in repeat_pairs) if repeat_pairs else None
        ),
        "repeat_status": "not_scheduled_under_cost_ceiling" if not repeat_pairs else "observed",
    }


def _stage_summary(experiment: Path, stage: str, population: dict, raw: dict) -> dict:
    integrity = _stage_integrity(experiment, stage, population, raw)
    runs = raw["runs"]
    effective = copy.deepcopy(population)
    effective["schedule"] = population["schedule"][: len(runs)]
    validation_stub = {
        "status": integrity["status"],
        "counts": {"information_boundary_violations": 0},
    }
    if stage == "smoke":
        responses = raw["responses"]
        first_attempts = [item for item in responses if item["attempt"] == 1]
        first_valid = sum(
            item["contract_validation"]["valid"] for item in first_attempts
        )
        final_valid = sum(item["valid"] for item in runs)
        errors = Counter(
            item["contract_validation"]["error"]
            for item in responses
            if not item["contract_validation"]["valid"]
        )
        observed = {
            "scheduled_calls": len(effective["schedule"]),
            "provider_attempts": len(responses),
            "first_attempt_valid": first_valid,
            "first_attempt_schema_valid_rate": (
                first_valid / len(first_attempts) if first_attempts else 0.0
            ),
            "post_retry_valid": final_valid,
            "post_retry_valid_rate": final_valid / len(runs) if runs else 0.0,
            "finish_reason_length": sum(
                item["contract_validation"]["finish_reason"] == "length"
                for item in responses
            ),
            "incomplete_json": sum(
                "not complete JSON" in str(error) for error in errors.elements()
            ),
            "illegal_artifact_references": sum(
                "artifact target slots" in str(error) for error in errors.elements()
            ),
            "illegal_hypothesis_references": sum(
                "candidate effect slots" in str(error) for error in errors.elements()
            ),
            "illegal_relation_references": sum(
                "unresolved relation" in str(error) for error in errors.elements()
            ),
            "manual_repairs": 0,
            "information_boundary_violations": 0,
        }
        mechanical = (
            observed["first_attempt_schema_valid_rate"]
            >= CONTRACT_THRESHOLDS["minimum_first_attempt_schema_valid_rate"]
            and observed["post_retry_valid_rate"]
            >= CONTRACT_THRESHOLDS["minimum_post_retry_valid_rate"]
            and all(
                observed[key] == 0
                for key in (
                    "finish_reason_length",
                    "incomplete_json",
                    "illegal_artifact_references",
                    "illegal_hypothesis_references",
                    "illegal_relation_references",
                    "manual_repairs",
                    "information_boundary_violations",
                )
            )
        )
        contract = {
            "classification": (
                "contract_stable"
                if integrity["status"] == "pass" and mechanical
                else "contract_unstable"
            ),
            "thresholds": CONTRACT_THRESHOLDS,
            "observed": observed,
            "response_error_counts": dict(
                sorted(errors.items(), key=lambda item: str(item[0]))
            ),
        }
        provider_accounting = {
            "calls": len(responses),
            "input_tokens": sum(item["resources"]["input_tokens"] for item in runs),
            "output_tokens": sum(item["resources"]["output_tokens"] for item in runs),
            "cached_input_tokens": sum(
                item["resources"]["cached_input_tokens"] for item in runs
            ),
            "reasoning_output_tokens": sum(
                item["resources"]["reasoning_output_tokens"] for item in runs
            ),
            "latency_ms": sum(item["resources"]["latency_ms"] for item in runs),
            "total_cost_usd": sum(
                item["resources"]["monetary_cost_usd"] for item in runs
            ),
        }
        semantic = {
            "contract": contract,
            "semantics": {"classification": "not_scored_smoke"},
            "downstream_action_value": {
                "model_conditioned": None,
                "oracle_conditioned": None,
                "model_action_compatible": None,
                "existing_estimator_adequate_under_oracle": None,
            },
            "stability": _stability(effective, runs),
            "provider_accounting": provider_accounting,
        }
    else:
        semantic = summarize_semantic(
            effective, runs, raw["responses"], validation_stub
        )
        semantic["stability"] = _stability(effective, runs)
        semantic["downstream_action_value"]["oracle_conditioned"] = _oracle_diagnostic(
            population
        )
        oracle = semantic["downstream_action_value"]["oracle_conditioned"]
        semantic["downstream_action_value"]["existing_estimator_adequate_under_oracle"] = oracle["passes"]
    execution = raw["execution"]
    transport_stable = (
        execution["startup_error"] is None
        and execution["permanent_transport_failures"] == 0
        and execution["provider_responses"] == execution["completed_logical_calls"]
        and integrity["cleanup_valid"]
    )
    return {
        "stage": stage,
        "population_hash": population["population_hash"],
        "exposed_before_experiment": population["exposed_before_experiment"],
        "integrity": integrity,
        "execution": execution,
        "transport": {
            "classification": "transport_stable" if transport_stable else "transport_unstable",
            "scheduled_logical_calls": execution["scheduled_logical_calls"],
            "completed_logical_calls": execution["completed_logical_calls"],
            "provider_attempts": execution["provider_attempts"],
            "provider_responses": execution["provider_responses"],
            "raw_transport_failures": execution["raw_transport_failures"],
            "transport_recoveries": execution["transport_recoveries"],
            "permanent_transport_failures": execution["permanent_transport_failures"],
        },
        "contract": semantic["contract"],
        "semantics": semantic["semantics"],
        "downstream_action_value": semantic["downstream_action_value"],
        "stability": semantic["stability"],
        "resources": {
            **semantic["provider_accounting"],
            "wall_clock_ms": execution["stage_wall_clock_ms"],
            "provider_attempts": execution["provider_attempts"],
            "provider_responses": execution["provider_responses"],
            "semantic_retries": execution["semantic_retries"],
            "transport_failures": execution["raw_transport_failures"],
        },
    }


def _semantic_gate(stage: dict) -> bool:
    return (
        stage["integrity"]["status"] == "pass"
        and stage["transport"]["classification"] == "transport_stable"
        and stage["contract"]["classification"] == "contract_stable"
        and stage["semantics"]["classification"] == "semantic_signal_promising"
        and stage["downstream_action_value"]["existing_estimator_adequate_under_oracle"]
        and stage["execution"]["early_stop"] is None
        and stage["execution"]["completed_logical_calls"]
        == stage["execution"]["scheduled_logical_calls"]
    )


def _require_smoke(experiment: Path) -> None:
    raw = _stage_raw(experiment, "smoke")
    if raw is None:
        raise RuntimeError("smoke stage has not run")
    population = _population_for_stage(experiment, "smoke")
    summary = _stage_summary(experiment, "smoke", population, raw)
    if not (
        summary["integrity"]["status"] == "pass"
        and summary["transport"]["classification"] == "transport_stable"
        and summary["contract"]["classification"] == "contract_stable"
    ):
        raise RuntimeError("smoke transport/schema gate did not pass")


def _require_development(experiment: Path) -> None:
    raw = _stage_raw(experiment, "development")
    if raw is None:
        raise RuntimeError("development stage has not run")
    population = _population_for_stage(experiment, "development")
    summary = _stage_summary(experiment, "development", population, raw)
    if not _semantic_gate(summary):
        raise RuntimeError("development semantic-capability gate did not pass")
    confirmation_oracle = _oracle_diagnostic(
        _population_for_stage(experiment, "confirmation")
    )
    if not confirmation_oracle["passes"]:
        raise RuntimeError("fresh confirmation oracle gate did not pass")


def run_stage(experiment: Path, stage: str) -> dict:
    if stage == "development":
        _require_smoke(experiment)
    elif stage == "confirmation":
        _require_smoke(experiment)
        _require_development(experiment)
    return _run_stage(experiment, stage)


def _population_validation(experiment: Path) -> dict:
    paths = _paths(experiment)
    populations = {
        stage: _json(paths[f"{stage}_population"]) for stage in STAGES
    }
    hashes = all(_population_hash_valid(item) for item in populations.values())
    confirmation_episodes, confirmation_source_hash, _ = load_population(
        paths["confirmation_source"]
    )
    exposed_episodes = []
    for name in (
        "development_population.json",
        "evaluation_population.json",
        "perturbation_population.json",
    ):
        episodes, _, _ = load_population(STATIC_SOURCE / name)
        exposed_episodes.extend(episodes)
    exposed_ids = {item.episode_id for item in exposed_episodes}
    confirmation_ids = {item.episode_id for item in confirmation_episodes}
    source_disjoint = not (exposed_ids & confirmation_ids)
    exposed_paths = {
        artifact.descriptor.path
        for episode in exposed_episodes
        for artifact in episode.artifacts
    }
    exposed_symbols = {
        symbol
        for episode in exposed_episodes
        for artifact in episode.artifacts
        for symbol in artifact.descriptor.exported_symbols
    }
    confirmation_paths = {
        artifact.descriptor.path
        for episode in confirmation_episodes
        for artifact in episode.artifacts
    }
    confirmation_symbols = {
        symbol
        for episode in confirmation_episodes
        for artifact in episode.artifacts
        for symbol in artifact.descriptor.exported_symbols
        if symbol != "handle_request"
    }
    exposed_symbols.discard("handle_request")
    public_identifiers_disjoint = (
        not (exposed_paths & confirmation_paths)
        and not (exposed_symbols & confirmation_symbols)
    )
    exposed_contract = _json(CONTRACT_SOURCE / "STRESS_POPULATION.json")
    exposed_public = {
        content_hash(item["model_visible_input"])
        for item in exposed_contract["cases"]
    }
    confirmation_public = {
        content_hash(item["model_visible_input"])
        for item in populations["confirmation"]["cases"]
    }
    public_disjoint = not (exposed_public & confirmation_public)
    case_ids_disjoint = not (
        {item["case_id"] for item in exposed_contract["cases"]}
        & {item["case_id"] for item in populations["confirmation"]["cases"]}
    )
    boundary_violations = 0
    allowed_visible = {
        "semantic_interface",
        "instruction_scope",
        "current_artifact",
        "candidate_hypotheses",
        "current_epistemic_summary",
        "public_artifact_inventory",
    }
    for population in populations.values():
        for case in population["cases"]:
            if set(case["model_visible_input"]) != allowed_visible:
                boundary_violations += 1
            if "evaluator_only" in case["model_visible_input"]:
                boundary_violations += 1
    expected_counts = {
        "smoke": (4, 4),
        "development": (32, 32),
        "confirmation": (64, 64),
    }
    counts_ok = all(
        (len(populations[stage]["cases"]), len(populations[stage]["schedule"]))
        == expected
        for stage, expected in expected_counts.items()
    )
    return {
        "population_hashes_valid": hashes,
        "expected_counts_valid": counts_ok,
        "confirmation_source_population_hash": confirmation_source_hash,
        "confirmation_source_ids_disjoint_from_all_exposed": source_disjoint,
        "confirmation_generated_paths_and_noninvariant_symbols_disjoint_from_all_exposed": public_identifiers_disjoint,
        "confirmation_model_visible_hashes_disjoint_from_exposed_v1_2": public_disjoint,
        "confirmation_case_ids_disjoint_from_exposed_v1_2": case_ids_disjoint,
        "information_boundary_violations": boundary_violations,
        "fresh_oracle": _oracle_diagnostic(populations["confirmation"]),
        "status": "pass" if all(
            (
                hashes,
                counts_ok,
                source_disjoint,
                public_identifiers_disjoint,
                public_disjoint,
                case_ids_disjoint,
                boundary_violations == 0,
            )
        ) else "fail",
    }


def build_results(experiment: Path) -> tuple[dict, dict, str, str, str]:
    manifest, observed_hashes = _load_manifest(experiment)
    paths = _paths(experiment)
    preflight = _verify_preflight_archive(experiment)
    population_validation = _population_validation(experiment)
    stages = {}
    for stage in STAGES:
        raw = _stage_raw(experiment, stage)
        if raw is not None:
            stages[stage] = _stage_summary(
                experiment, stage, _population_for_stage(experiment, stage), raw
            )
    smoke = stages.get("smoke")
    development = stages.get("development")
    confirmation = stages.get("confirmation")
    smoke_gate = bool(
        smoke
        and smoke["integrity"]["status"] == "pass"
        and smoke["transport"]["classification"] == "transport_stable"
        and smoke["contract"]["classification"] == "contract_stable"
    )
    development_gate = bool(development and _semantic_gate(development))
    confirmation_gate = bool(confirmation and _semantic_gate(confirmation))
    sequencing_ok = (
        (development is None or smoke_gate)
        and (confirmation is None or development_gate)
        and (development_gate or confirmation is None)
    )
    total_cost = preflight["cost_usd"] + sum(
        item["resources"]["total_cost_usd"] for item in stages.values()
    )
    total_attempts = preflight["provider_attempts"] + sum(
        item["resources"]["provider_attempts"] for item in stages.values()
    )
    total_responses = preflight["provider_responses"] + sum(
        item["resources"]["provider_responses"] for item in stages.values()
    )
    secret = os.environ.get("OPENAI_API_KEY", "")
    secret_found = False
    if secret:
        needle = secret.encode("utf-8")
        secret_found = any(
            needle in path.read_bytes()
            for path in experiment.rglob("*")
            if path.is_file()
        )
    cost_ok = total_cost < 2.5 and total_attempts <= GLOBAL_MAXIMUM_API_SUBMISSIONS
    stage_integrity_ok = all(
        item["integrity"]["status"] == "pass" for item in stages.values()
    )
    complete_result = bool(
        smoke
        and (
            (
                not smoke_gate
                and development is None
                and confirmation is None
            )
            or (
                development is not None
                and (
                    (not development_gate and confirmation is None)
                    or confirmation is not None
                )
            )
        )
    )
    validation_status = "pass" if all(
        (
            observed_hashes == manifest["files"],
            population_validation["status"] == "pass",
            population_validation["fresh_oracle"]["passes"],
            stage_integrity_ok,
            sequencing_ok,
            cost_ok,
            not secret_found,
            complete_result,
        )
    ) else "fail"
    validation = {
        "schema_version": 1,
        "experiment": EXPERIMENT_ID,
        "status": validation_status,
        "checks": {
            "frozen_input_hashes": observed_hashes == manifest["files"],
            "population_and_nonoverlap": population_validation,
            "stage_integrity": stage_integrity_ok,
            "stage_sequencing": sequencing_ok,
            "complete_terminal_result": complete_result,
            "global_cost_and_call_ceiling": {
                "pass": cost_ok,
                "provider_attempts": total_attempts,
                "maximum_provider_attempts": GLOBAL_MAXIMUM_API_SUBMISSIONS,
                "total_cost_usd": total_cost,
                "hard_spend_ceiling_usd": 2.5,
            },
            "credential_absent_from_artifacts": not secret_found,
        },
    }

    if population_validation["status"] != "pass" or not population_validation["fresh_oracle"]["passes"]:
        classification = "benchmark_invalid"
    elif validation_status != "pass":
        classification = "experiment_invalid"
    elif any(
        item["transport"]["classification"] != "transport_stable"
        for item in stages.values()
    ):
        classification = "transport_unstable"
    elif any(
        item["contract"]["classification"] != "contract_stable"
        for item in stages.values()
    ):
        classification = "response_contract_unstable"
    elif not development_gate:
        classification = "semantic_capability_below_threshold"
    elif not confirmation_gate:
        classification = "semantic_capability_development_only"
    else:
        classification = "semantic_capability_confirmed"

    if classification in ("transport_unstable", "response_contract_unstable"):
        next_decision = "remain_at_transport_or_contract"
    elif classification == "semantic_capability_below_threshold":
        oracle_repairs = bool(
            development
            and development["downstream_action_value"]["existing_estimator_adequate_under_oracle"]
            and not development["downstream_action_value"]["model_action_compatible"]
        )
        next_decision = (
            "investigate_semantic_representation_failure"
            if oracle_repairs
            else "test_separately_preregistered_alternative_inexpensive_model"
        )
    elif classification == "semantic_capability_development_only":
        next_decision = "investigate_semantic_representation_failure"
    elif classification == "semantic_capability_confirmed":
        next_decision = "proceed_to_separately_preregistered_ser_vs_ordinary_agent_comparison"
    else:
        next_decision = "investigate_benchmark_validity"

    failure_taxonomy = {
        "transport_failures": sum(
            item["transport"]["raw_transport_failures"] for item in stages.values()
        ),
        "permanent_transport_failures": sum(
            item["transport"]["permanent_transport_failures"] for item in stages.values()
        ),
        "response_contract_failures": sum(
            item["contract"]["observed"]["scheduled_calls"]
            - item["contract"]["observed"]["post_retry_valid"]
            for item in stages.values()
        ),
        "semantic_failure": bool(development and not development_gate),
        "downstream_estimator_failure": not population_validation["fresh_oracle"]["passes"],
        "benchmark_failure": population_validation["status"] != "pass",
    }
    resources = {
        "logical_calls": sum(
            item["execution"]["completed_logical_calls"] for item in stages.values()
        ) + preflight["valid_logical_responses"],
        "preserved_nonsemantic_preflight": preflight,
        "provider_attempts": total_attempts,
        "provider_responses": total_responses,
        "valid_responses": preflight["valid_logical_responses"] + sum(
            item["contract"]["observed"]["post_retry_valid"] for item in stages.values()
        ),
        "invalid_responses": sum(
            item["contract"]["observed"]["scheduled_calls"]
            - item["contract"]["observed"]["post_retry_valid"]
            for item in stages.values()
        ),
        "semantic_retries": sum(item["resources"]["semantic_retries"] for item in stages.values()),
        "input_tokens": preflight["input_tokens"] + sum(item["resources"]["input_tokens"] for item in stages.values()),
        "cached_input_tokens": preflight["cached_input_tokens"] + sum(item["resources"]["cached_input_tokens"] for item in stages.values()),
        "output_tokens": preflight["output_tokens"] + sum(item["resources"]["output_tokens"] for item in stages.values()),
        "reasoning_output_tokens": preflight["reasoning_output_tokens"] + sum(item["resources"]["reasoning_output_tokens"] for item in stages.values()),
        "total_cost_usd": total_cost,
        "aggregate_request_latency_ms": preflight["latency_ms"] + sum(item["resources"]["latency_ms"] for item in stages.values()),
        "stage_wall_clock_ms": {
            name: item["resources"]["wall_clock_ms"] for name, item in stages.items()
        },
        "per_logical_call_cost_usd": {
            name: {
                "minimum": min(
                    (run["resources"]["monetary_cost_usd"] for run in _stage_raw(experiment, name)["runs"]),
                    default=0.0,
                ),
                "mean": fmean(
                    run["resources"]["monetary_cost_usd"]
                    for run in _stage_raw(experiment, name)["runs"]
                ) if _stage_raw(experiment, name)["runs"] else 0.0,
                "maximum": max(
                    (run["resources"]["monetary_cost_usd"] for run in _stage_raw(experiment, name)["runs"]),
                    default=0.0,
                ),
            }
            for name in stages
        },
    }
    summary = {
        "schema_version": 1,
        "experiment": EXPERIMENT_ID,
        "frozen_inputs_manifest_hash": manifest["manifest_hash"],
        "selected_model": "patchersniper_praneeth/gpt-5.4-mini",
        "semantic_contract_version": "v1.2",
        "classification": classification,
        "preserved_nonsemantic_preflight": preflight,
        "stages": stages,
        "development_gate_passed": development_gate,
        "confirmation_executed": confirmation is not None,
        "confirmation_gate_passed": confirmation_gate,
        "fresh_oracle": population_validation["fresh_oracle"],
        "failure_taxonomy": failure_taxonomy,
        "resources": resources,
        "what_was_established": (
            "The frozen semantic channel cleared development and fresh confirmation capability floors."
            if classification == "semantic_capability_confirmed"
            else "The frozen semantic channel did not establish confirmatory semantic capability."
        ),
        "what_was_not_established": [
            "SER architecture advantage",
            "H-001",
            "H-016",
            "H-017",
            "H-018",
            "real-software authorization competence",
            "bug-finding capability",
        ],
        "next_empirical_decision": next_decision,
        "no_hypothesis_or_evidence_promotion": True,
    }
    return (
        validation,
        summary,
        render_report(summary, validation),
        render_interpretation(summary),
        render_implementation_notes(summary),
    )


def _metric_rows(stage: dict) -> list[str]:
    semantic = stage["semantics"]
    action = stage["downstream_action_value"]["model_conditioned"]
    return [
        f"| Fact precision | {semantic['facts']['precision']:.6f} | >= 0.65 | {'pass' if semantic['facts']['precision'] >= 0.65 else 'fail'} |",
        f"| Fact recall | {semantic['facts']['recall']:.6f} | >= 0.50 | {'pass' if semantic['facts']['recall'] >= 0.50 else 'fail'} |",
        f"| Effect precision | {semantic['hypothesis_effects']['precision']:.6f} | >= 0.60 | {'pass' if semantic['hypothesis_effects']['precision'] >= 0.60 else 'fail'} |",
        f"| Effect recall | {semantic['hypothesis_effects']['recall']:.6f} | >= 0.50 | {'pass' if semantic['hypothesis_effects']['recall'] >= 0.50 else 'fail'} |",
        f"| Unresolved precision | {semantic['unresolved_relations']['precision']:.6f} | >= 0.60 | {'pass' if semantic['unresolved_relations']['precision'] >= 0.60 else 'fail'} |",
        f"| Unresolved recall | {semantic['unresolved_relations']['recall']:.6f} | >= 0.50 | {'pass' if semantic['unresolved_relations']['recall'] >= 0.50 else 'fail'} |",
        f"| Useful-action top-1 | {action['top1']:.6f} | >= 0.60 | {'pass' if action['top1'] >= 0.60 else 'fail'} |",
        f"| Useful-action top-2 | {action['top2']:.6f} | >= 0.80 | {'pass' if action['top2'] >= 0.80 else 'fail'} |",
        f"| Mean normalized regret | {action['mean_normalized_regret']:.6f} | <= 0.35 | {'pass' if action['mean_normalized_regret'] <= 0.35 else 'fail'} |",
    ]


def render_report(summary: dict, validation: dict) -> str:
    lines = [
        "# AuthzGym stronger-model semantic capability v1 report",
        "",
        "This staged study changes only the model under semantic contract v1.2. It is not an architecture comparison.",
        "",
        f"Validation: **{validation['status']}**",
        f"Classification: **`{summary['classification']}`**",
        f"Selected model: **`{summary['selected_model']}`**",
        "",
        "The preserved initial smoke preflight made 4 valid non-semantic calls, cost $0.012318, and was superseded only because its offline base-only analyzer was incompatible with the smoke population. That cost remains included below.",
        "",
    ]
    for name in ("smoke", "development", "confirmation"):
        stage = summary["stages"].get(name)
        if stage is None:
            lines.extend([f"## {name.title()}", "", "Not executed under the frozen gate.", ""])
            continue
        transport = stage["transport"]
        contract = stage["contract"]
        lines.extend(
            [
                f"## {name.title()}",
                "",
                f"Population hash: `{stage['population_hash']}`.",
                f"Transport/contract: **`{transport['classification']}`** / **`{contract['classification']}`**.",
                f"Logical calls/provider attempts/provider responses: **{transport['completed_logical_calls']} / {transport['provider_attempts']} / {transport['provider_responses']}**.",
                f"Raw/permanent transport failures: **{transport['raw_transport_failures']} / {transport['permanent_transport_failures']}**.",
                f"First-attempt/post-retry valid rates: **{contract['observed']['first_attempt_schema_valid_rate']:.6f} / {contract['observed']['post_retry_valid_rate']:.6f}**.",
                "",
            ]
        )
        if name != "smoke":
            lines.extend(
                [
                    "| Metric | Observed | Threshold | Result |",
                    "| --- | ---: | ---: | --- |",
                    *_metric_rows(stage),
                    "",
                    f"Semantic classifier: **`{stage['semantics']['classification']}`**.",
                    f"Transformation-equivalence exact rate: **{stage['stability']['semantic_equivalence_exact_rate']}** across {stage['stability']['semantic_equivalence_pairs']} scheduled pairs.",
                    "Repeat exactness: **not scheduled under the $2.50 ceiling**.",
                    "",
                ]
            )
    oracle = summary["fresh_oracle"]
    resources = summary["resources"]
    lines.extend(
        [
            "## Fresh oracle diagnostic",
            "",
            f"Top-1/top-2/mean normalized regret: **{oracle['top1']:.6f} / {oracle['top2']:.6f} / {oracle['mean_normalized_regret']:.6f}** across {oracle['canonical_episodes']} canonical fresh episodes.",
            f"Oracle gate: **{'pass' if oracle['passes'] else 'fail'}**.",
            "",
            "## Failure taxonomy and resources",
            "",
            f"Failure taxonomy: `{canonical_json(summary['failure_taxonomy'])}`.",
            f"Provider-reported input/cached/output tokens: **{resources['input_tokens']} / {resources['cached_input_tokens']} / {resources['output_tokens']}**.",
            f"Logical calls/provider attempts/provider responses: **{resources['logical_calls']} / {resources['provider_attempts']} / {resources['provider_responses']}**.",
            f"Accounted spend: **${resources['total_cost_usd']:.9f}** under the **$2.50** hard ceiling.",
            "",
            "## Interpretation",
            "",
            summary["what_was_established"],
            "",
            "This result does not establish SER architecture advantage, any listed hypothesis, real-software competence, or bug-finding capability. No E-* item is admitted.",
            "",
            f"Next empirical decision: **`{summary['next_empirical_decision']}`**.",
            "",
        ]
    )
    return "\n".join(lines)


def render_interpretation(summary: dict) -> str:
    return (
        "# AuthzGym stronger-model semantic capability v1 interpretation\n\n"
        f"The preregistered classification is **`{summary['classification']}`**. "
        f"{summary['what_was_established']}\n\n"
        "The model change is only a capability prerequisite and supplies no SER architecture evidence, hypothesis promotion, or authorization finding.\n\n"
        f"The single next empirical decision is **`{summary['next_empirical_decision']}`**.\n"
    )


def render_implementation_notes(summary: dict) -> str:
    resources = summary["resources"]
    return (
        "# AuthzGym stronger-model semantic capability v1 implementation notes\n\n"
        "The experiment reused semantic contract v1.2 and the supervised transport envelope without changing semantic content. The sole intervention was `patchersniper_praneeth/gpt-5.4-mini`.\n\n"
        "The configured endpoint was accessed through the existing local SSH/SOCKS hop with the user-approved endpoint-scoped insecure TLS flag. The API credential remained in an anonymous local curl configuration pipe and was stripped from the SSH child environment. No live software target or remote workspace was used.\n\n"
        f"The terminal classification was `{summary['classification']}` after {resources['logical_calls']} logical calls and {resources['provider_attempts']} provider attempts, with ${resources['total_cost_usd']:.9f} accounted usage.\n\n"
        "All population, prompt, schema, configuration, implementation, raw-response, transport-attempt, run, and summary identities are content-addressed. No manual response repair or post-result tuning occurred.\n"
    )


def analyze(experiment: Path) -> dict:
    paths = _paths(experiment)
    for path in (
        paths["validation"],
        paths["summary"],
        paths["report"],
        paths["interpretation"],
        paths["implementation_notes"],
    ):
        if path.exists():
            raise FileExistsError(f"analysis output already exists: {path.name}")
    validation, summary, report, interpretation, notes = build_results(experiment)
    _write_new_json(paths["validation"], validation)
    _write_new_json(paths["summary"], summary)
    _write_new(paths["report"], report)
    _write_new(paths["interpretation"], interpretation)
    _write_new(paths["implementation_notes"], notes)
    return {
        "validation": validation["status"],
        "classification": summary["classification"],
        "development_gate_passed": summary["development_gate_passed"],
        "confirmation_executed": summary["confirmation_executed"],
        "confirmation_gate_passed": summary["confirmation_gate_passed"],
        "next_empirical_decision": summary["next_empirical_decision"],
        "accounted_spend_usd": summary["resources"]["total_cost_usd"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        choices=("prepare", "freeze", "smoke", "development", "confirmation", "analyze"),
    )
    parser.add_argument("--experiment-dir", type=Path, default=EXPERIMENT)
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare(args.experiment_dir)
    elif args.command == "freeze":
        result = freeze(args.experiment_dir)
    elif args.command in STAGES:
        result = run_stage(args.experiment_dir, args.command)
    else:
        result = analyze(args.experiment_dir)
    print(canonical_json(result))


if __name__ == "__main__":
    main()
