#!/usr/bin/env python3
"""Develop, freeze, execute, and analyze AuthzGym real-model v1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ser.authzgym.model import ArtifactDescriptor
from ser.authzgym.policies import ARCHITECTURES, AuthzEpistemicState
from ser.authzgym.real_runner import run_real_authz_episode
from ser.authzgym.realmodel import (
    CurlChatCompletionsClient,
    load_real_model_condition,
    semantic_response_schema,
    usage_cost_usd,
)
from ser.core.types import canonical_json, content_hash
from ser.evaluation.artifacts import write_new_json
from ser.evaluation.authz_artifacts import file_sha256, load_population
from ser.evaluation.authz_real_analysis import (
    CLASSIFIER_THRESHOLDS,
    render_interpretation,
    render_report,
    summarize_real,
    validate_real,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXPERIMENT = ROOT / "experiments/authzgym_static_realmodel_v1"
SOURCE_EXPERIMENT = ROOT / "experiments/authzgym_static_v1_1"
PROMPT_VERSION = "semantic_interpretation_v1"


def _paths(experiment_dir: Path) -> dict[str, Path]:
    return {
        "preregistration": experiment_dir / "PREREGISTRATION.md",
        "prompt": experiment_dir / "prompts/semantic_interpretation_v1.txt",
        "schema": experiment_dir / "schemas/semantic_observation_v1.json",
        "config": experiment_dir / "model_config.json",
        "frozen": experiment_dir / "FROZEN_INPUTS.json",
        "cost_gate": experiment_dir / "COST_GATE.json",
        "development": experiment_dir / "development_call.json",
        "development_responses": experiment_dir / "development_provider_responses.jsonl",
        "evaluation_runs": experiment_dir / "evaluation_runs.jsonl",
        "perturbation_runs": experiment_dir / "perturbation_runs.jsonl",
        "responses": experiment_dir / "provider_responses.jsonl",
        "validation": experiment_dir / "validation.json",
        "summary": experiment_dir / "summary.json",
        "report": experiment_dir / "REPORT.md",
        "interpretation": experiment_dir / "INTERPRETATION.md",
    }


def _write_new_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(value)
        if not value.endswith("\n"):
            handle.write("\n")


def _append_jsonl(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(canonical_json(value))
        handle.write("\n")
        handle.flush()


def _load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _load_inputs(experiment_dir: Path):
    paths = _paths(experiment_dir)
    condition = load_real_model_condition(paths["config"])
    prompt = paths["prompt"].read_text(encoding="utf-8")
    schema = json.loads(paths["schema"].read_text(encoding="utf-8"))
    if schema != semantic_response_schema():
        raise ValueError("frozen schema file differs from implemented provider schema")
    development, development_hash, _ = load_population(
        SOURCE_EXPERIMENT / "development_population.json"
    )
    evaluation, evaluation_hash, _ = load_population(
        SOURCE_EXPERIMENT / "evaluation_population.json"
    )
    perturbations, perturbation_hash, _ = load_population(
        SOURCE_EXPERIMENT / "perturbation_population.json"
    )
    return (
        paths,
        condition,
        prompt,
        schema,
        development,
        evaluation,
        perturbations,
        {
            "development": development_hash,
            "evaluation": evaluation_hash,
            "perturbation": perturbation_hash,
        },
    )


def development_call(experiment_dir: Path, proxy_port: int) -> dict:
    (
        paths,
        condition,
        prompt,
        schema,
        development,
        _,
        _,
        population_hashes,
    ) = _load_inputs(experiment_dir)
    for path in (paths["development"], paths["development_responses"]):
        if path.exists():
            raise FileExistsError(f"development artifact already exists: {path.name}")
    episode = development[0]
    artifact = episode.artifact(episode.entry_artifact_id)
    inventory = tuple(
        ArtifactDescriptor.from_dict(item).to_dict()
        for item in episode.public_view()["artifact_inventory"]
    )
    visible_input = {
        "semantic_interface": "authzgym_semantic_observation_v1",
        "prompt_version": PROMPT_VERSION,
        "purchased_artifacts": [
            {
                "artifact_id": artifact.descriptor.artifact_id,
                "path": artifact.descriptor.path,
                "source": artifact.source,
            }
        ],
        "candidate_hypotheses": [item.to_dict() for item in episode.candidates],
        "current_epistemic_summary": AuthzEpistemicState.initial(
            episode.candidates
        ).to_dict(),
        "public_artifact_inventory": list(inventory),
        "legal_next_artifact_ids": [],
        "recommendation_required": False,
    }
    client = CurlChatCompletionsClient(
        condition,
        prompt,
        schema,
        f"socks5h://127.0.0.1:{proxy_port}",
        lambda value: _append_jsonl(paths["development_responses"], value),
    )
    result = client.invoke(
        visible_input,
        episode.candidates,
        inventory,
        (),
        False,
        artifacts_in_call=1,
        call_context={
            "split": "development",
            "episode_id": episode.episode_id,
            "architecture": "integration_only",
            "step": 1,
        },
    )
    accounting = client.accounting_snapshot()
    value = {
        "schema_version": 1,
        "purpose": "single minimal connectivity/schema/usage development call; no accuracy tuning",
        "episode_id": episode.episode_id,
        "artifact_id": artifact.descriptor.artifact_id,
        "condition": condition.public_dict(),
        "population_hash": population_hashes["development"],
        "prompt_sha256": file_sha256(paths["prompt"]),
        "schema_sha256": file_sha256(paths["schema"]),
        "model_config_sha256": file_sha256(paths["config"]),
        "request_sha256": result["request_sha256"],
        "raw_response_sha256": result["raw_response_sha256"],
        "provider_model": result["provider_model"],
        "system_fingerprint": result["system_fingerprint"],
        "parsed_semantic_observation": result["parsed_semantic_observation"],
        "provider_calls": accounting["provider_calls"],
        "input_tokens": accounting["input_tokens"],
        "output_tokens": accounting["output_tokens"],
        "cached_input_tokens": accounting["cached_input_tokens"],
        "reasoning_output_tokens": accounting["reasoning_output_tokens"],
        "latency_ms": accounting["latency_ms"],
        "cost_usd": accounting["monetary_cost_usd"],
    }
    value["record_hash"] = content_hash(value)
    write_new_json(paths["development"], value)
    return value


def _file_inputs(experiment_dir: Path) -> dict[str, Path]:
    paths = _paths(experiment_dir)
    return {
        "PREREGISTRATION.md": paths["preregistration"],
        "prompts/semantic_interpretation_v1.txt": paths["prompt"],
        "schemas/semantic_observation_v1.json": paths["schema"],
        "model_config.json": paths["config"],
        "source/development_population.json": SOURCE_EXPERIMENT
        / "development_population.json",
        "source/evaluation_population.json": SOURCE_EXPERIMENT
        / "evaluation_population.json",
        "source/perturbation_population.json": SOURCE_EXPERIMENT
        / "perturbation_population.json",
        "implementation/src/ser/authzgym/model.py": ROOT
        / "src/ser/authzgym/model.py",
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


def _schedule(evaluation, perturbations) -> list[dict]:
    result = []
    for split, episodes in (("evaluation", evaluation), ("perturbation", perturbations)):
        for index, episode in enumerate(episodes):
            offset = index % len(ARCHITECTURES)
            order = ARCHITECTURES[offset:] + ARCHITECTURES[:offset]
            for architecture in order:
                result.append(
                    {
                        "split": split,
                        "episode_id": episode.episode_id,
                        "architecture": architecture,
                    }
                )
    return result


def _project_cost(condition, development: dict) -> dict:
    split_episodes = 48
    sequential_attempts = (
        split_episodes
        * 3
        * 4
        * condition.maximum_attempts_per_semantic_call
    )
    monolithic_attempts = (
        split_episodes * condition.maximum_attempts_per_semantic_call
    )
    sequential_input_per_attempt = max(
        int(development["input_tokens"]),
        condition.input_token_ceiling_per_sequential_run // 4,
    )
    monolithic_input_per_attempt = condition.input_token_ceiling_per_monolithic_run
    projected_input = (
        sequential_attempts * sequential_input_per_attempt
        + monolithic_attempts * monolithic_input_per_attempt
    )
    projected_output = (
        sequential_attempts * condition.max_output_tokens_per_artifact
        + monolithic_attempts
        * condition.max_output_tokens_per_artifact
        * 4
    )
    projected_frozen = (
        projected_input * condition.input_price_per_million_usd
        + projected_output * condition.output_price_per_million_usd
    ) / 1_000_000.0
    projected_complete = float(development["cost_usd"]) + projected_frozen
    return {
        "normal_semantic_decisions": split_episodes * (3 * 4 + 1),
        "maximum_provider_attempts": sequential_attempts + monolithic_attempts,
        "projected_input_tokens": projected_input,
        "projected_output_tokens": projected_output,
        "projected_frozen_cost_usd": projected_frozen,
        "projected_complete_cost_usd": projected_complete,
        "required_margin_below_hard_cap_usd": 1.0,
        "proceed": projected_complete < condition.hard_spend_ceiling_usd - 1.0,
    }


def freeze(experiment_dir: Path) -> dict:
    (
        paths,
        condition,
        _,
        _,
        _,
        evaluation,
        perturbations,
        population_hashes,
    ) = _load_inputs(experiment_dir)
    if paths["frozen"].exists() or paths["cost_gate"].exists():
        raise FileExistsError("frozen manifest or cost gate already exists")
    development = json.loads(paths["development"].read_text(encoding="utf-8"))
    if not verify_development_record(development):
        raise ValueError("development record hash is invalid")
    files = {name: file_sha256(path) for name, path in _file_inputs(experiment_dir).items()}
    payload = {
        "schema_version": 1,
        "experiment": "authzgym-static-realmodel-v1",
        "frozen_before_evaluation": True,
        "source_population_hashes": population_hashes,
        "files": files,
        "classifier_thresholds": CLASSIFIER_THRESHOLDS,
        "run_schedule": _schedule(evaluation, perturbations),
    }
    manifest_hash = content_hash(payload)
    manifest = {**payload, "manifest_hash": manifest_hash}
    projection = _project_cost(condition, development)
    cost_gate = {
        "schema_version": 1,
        "experiment": "authzgym-static-realmodel-v1",
        "frozen_inputs_manifest_hash": manifest_hash,
        "development_record_hash": development["record_hash"],
        "development_provider_calls": development["provider_calls"],
        "development_input_tokens": development["input_tokens"],
        "development_output_tokens": development["output_tokens"],
        "development_cost_usd": development["cost_usd"],
        **projection,
        "hard_spend_ceiling_usd": condition.hard_spend_ceiling_usd,
        "cost_basis": "provider-reported usage at frozen listed token rates; not a billing statement",
    }
    cost_gate["record_hash"] = content_hash(cost_gate)
    if not cost_gate["proceed"]:
        raise RuntimeError("complete frozen experiment fails the preregistered cost gate")
    write_new_json(paths["frozen"], manifest)
    write_new_json(paths["cost_gate"], cost_gate)
    return cost_gate


def verify_development_record(value: dict) -> bool:
    digest = value.get("record_hash")
    if not isinstance(digest, str):
        return False
    payload = dict(value)
    payload.pop("record_hash")
    return content_hash(payload) == digest


def _load_manifest(experiment_dir: Path) -> tuple[dict, dict[str, str]]:
    paths = _paths(experiment_dir)
    manifest = json.loads(paths["frozen"].read_text(encoding="utf-8"))
    digest = manifest.pop("manifest_hash")
    if content_hash(manifest) != digest:
        raise ValueError("FROZEN_INPUTS manifest hash mismatch")
    manifest["manifest_hash"] = digest
    observed = {
        name: file_sha256(path) for name, path in _file_inputs(experiment_dir).items()
    }
    if observed != manifest["files"]:
        raise ValueError("a frozen experiment input changed after preregistration")
    return manifest, observed


def run_frozen(experiment_dir: Path, proxy_port: int) -> dict:
    (
        paths,
        condition,
        prompt,
        schema,
        _,
        evaluation,
        perturbations,
        population_hashes,
    ) = _load_inputs(experiment_dir)
    manifest, _ = _load_manifest(experiment_dir)
    cost_gate = json.loads(paths["cost_gate"].read_text(encoding="utf-8"))
    if not cost_gate["proceed"] or not verify_development_record(
        json.loads(paths["development"].read_text(encoding="utf-8"))
    ):
        raise ValueError("development or cost gate is invalid")
    for path in (paths["evaluation_runs"], paths["perturbation_runs"], paths["responses"]):
        if path.exists():
            raise FileExistsError(f"frozen output already exists: {path.name}")
    client = CurlChatCompletionsClient(
        condition,
        prompt,
        schema,
        f"socks5h://127.0.0.1:{proxy_port}",
        lambda value: _append_jsonl(paths["responses"], value),
    )
    client.total_cost_usd = float(cost_gate["development_cost_usd"])
    episode_index = {
        "evaluation": {item.episode_id: item for item in evaluation},
        "perturbation": {item.episode_id: item for item in perturbations},
    }
    hashes = {
        "prompt": file_sha256(paths["prompt"]),
        "schema": file_sha256(paths["schema"]),
        "config": file_sha256(paths["config"]),
        "preregistration": file_sha256(paths["preregistration"]),
    }
    for index, scheduled in enumerate(manifest["run_schedule"], 1):
        split = scheduled["split"]
        episode = episode_index[split][scheduled["episode_id"]]
        record = run_real_authz_episode(
            episode,
            scheduled["architecture"],
            condition,
            client,
            PROMPT_VERSION,
            hashes["prompt"],
            hashes["schema"],
            hashes["config"],
            hashes["preregistration"],
            manifest["manifest_hash"],
            population_hashes["evaluation" if split == "evaluation" else "perturbation"],
        )
        output = paths["evaluation_runs"] if split == "evaluation" else paths["perturbation_runs"]
        _append_jsonl(output, record)
        if index % 8 == 0 or index == len(manifest["run_schedule"]):
            print(
                canonical_json(
                    {
                        "completed_runs": index,
                        "total_runs": len(manifest["run_schedule"]),
                        "provider_calls_including_development": client.total_provider_calls
                        + int(cost_gate["development_provider_calls"]),
                        "accounted_spend_usd": client.total_cost_usd,
                    }
                ),
                flush=True,
            )
    return {
        "runs": len(manifest["run_schedule"]),
        "provider_calls_including_development": client.total_provider_calls
        + int(cost_gate["development_provider_calls"]),
        "accounted_spend_usd": client.total_cost_usd,
    }


def analyze(experiment_dir: Path) -> dict:
    (
        paths,
        condition,
        _,
        _,
        _,
        evaluation,
        perturbations,
        _,
    ) = _load_inputs(experiment_dir)
    manifest, observed_hashes = _load_manifest(experiment_dir)
    evaluation_records = _load_jsonl(paths["evaluation_runs"])
    perturbation_records = _load_jsonl(paths["perturbation_runs"])
    response_records = _load_jsonl(paths["responses"])
    development = json.loads(paths["development"].read_text(encoding="utf-8"))
    cost_gate = json.loads(paths["cost_gate"].read_text(encoding="utf-8"))
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
    development_for_report = {
        "provider_calls": development["provider_calls"],
        "input_tokens": development["input_tokens"],
        "output_tokens": development["output_tokens"],
        "cost_usd": development["cost_usd"],
        "projected_complete_cost_usd": cost_gate["projected_complete_cost_usd"],
    }
    summary = summarize_real(
        evaluation,
        perturbations,
        evaluation_records,
        perturbation_records,
        response_records,
        validation,
    )
    write_new_json(paths["validation"], validation)
    write_new_json(paths["summary"], summary)
    _write_new_text(paths["report"], render_report(summary, validation, development_for_report))
    _write_new_text(paths["interpretation"], render_interpretation(summary))
    return {
        "validation": validation["status"],
        "classification": summary["classifier"]["classification"],
        "frozen_cost_usd": summary["provider_accounting"]["total_cost_usd"],
        "complete_cost_usd": summary["provider_accounting"]["total_cost_usd"]
        + float(development["cost_usd"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("dev", "freeze", "run", "analyze"))
    parser.add_argument("--experiment-dir", type=Path, default=DEFAULT_EXPERIMENT)
    parser.add_argument("--proxy-port", type=int)
    args = parser.parse_args()
    if args.mode in {"dev", "run"} and args.proxy_port is None:
        parser.error("--proxy-port is required for provider calls")
    if args.mode == "dev":
        result = development_call(args.experiment_dir, args.proxy_port)
        print(
            canonical_json(
                {
                    "provider_calls": result["provider_calls"],
                    "input_tokens": result["input_tokens"],
                    "output_tokens": result["output_tokens"],
                    "cost_usd": result["cost_usd"],
                    "parsed": True,
                }
            )
        )
    elif args.mode == "freeze":
        print(canonical_json(freeze(args.experiment_dir)))
    elif args.mode == "run":
        print(canonical_json(run_frozen(args.experiment_dir, args.proxy_port)))
    else:
        print(canonical_json(analyze(args.experiment_dir)))


if __name__ == "__main__":
    main()
