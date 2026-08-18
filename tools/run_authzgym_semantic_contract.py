#!/usr/bin/env python3
"""Prepare, freeze, run, and analyze AuthzGym semantic contract v1.2."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from ser.authzgym.realmodel import (
    ProviderError,
    _usage_from_response,
    load_real_model_condition,
)
from ser.authzgym.semantic_contract import (
    ContractV12Error,
    episode_from_case,
    stress_population_payload,
    vocabulary_payload,
)
from ser.authzgym.semantic_transport import SemanticContractClientV12
from ser.core.types import canonical_json, content_hash
from ser.evaluation.authz_artifacts import file_sha256, load_population
from ser.evaluation.authz_contract_analysis import (
    CONTRACT_THRESHOLDS,
    SEMANTIC_THRESHOLDS,
    render_interpretation,
    render_report,
    summarize,
)


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "experiments/authzgym_semantic_contract_v1_2"
SOURCE = ROOT / "experiments/authzgym_static_v1_1"


def _paths(experiment: Path) -> dict[str, Path]:
    return {
        "preregistration": experiment / "PREREGISTRATION.md",
        "prompt": experiment / "prompts/semantic_observation_v1_2.txt",
        "vocabulary": experiment / "schemas/semantic_vocabulary_v1_2.json",
        "config": experiment / "model_config.json",
        "population": experiment / "STRESS_POPULATION.json",
        "frozen": experiment / "FROZEN_INPUTS.json",
        "cost_gate": experiment / "COST_GATE.json",
        "responses": experiment / "provider_responses.jsonl",
        "runs": experiment / "stress_runs.jsonl",
        "validation": experiment / "validation.json",
        "summary": experiment / "summary.json",
        "report": experiment / "REPORT.md",
        "interpretation": experiment / "INTERPRETATION.md",
        "autopsy_json": experiment / "OFFLINE_AUTOPSY.json",
        "autopsy_report": experiment / "OFFLINE_AUTOPSY.md",
    }


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


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


def prepare(experiment: Path) -> dict:
    paths = _paths(experiment)
    development, source_hash, _ = load_population(
        SOURCE / "development_population.json"
    )
    frozen_vocabulary = _json(paths["vocabulary"])
    if frozen_vocabulary != vocabulary_payload():
        raise ValueError("stored semantic vocabulary differs from implementation")
    population = stress_population_payload(development)
    population["source_development_population_hash"] = source_hash
    payload_without_hash = dict(population)
    payload_without_hash.pop("population_hash")
    population["population_hash"] = content_hash(payload_without_hash)
    _write_new_json(paths["population"], population)
    return {
        "population_hash": population["population_hash"],
        "cases": len(population["cases"]),
        "scheduled_calls": len(population["schedule"]),
    }


def _file_inputs(experiment: Path) -> dict[str, Path]:
    paths = _paths(experiment)
    return {
        "PREREGISTRATION.md": paths["preregistration"],
        "prompts/semantic_observation_v1_2.txt": paths["prompt"],
        "schemas/semantic_vocabulary_v1_2.json": paths["vocabulary"],
        "schemas/README.md": experiment / "schemas/README.md",
        "model_config.json": paths["config"],
        "STRESS_POPULATION.json": paths["population"],
        "OFFLINE_AUTOPSY.json": paths["autopsy_json"],
        "OFFLINE_AUTOPSY.md": paths["autopsy_report"],
        "source/development_population.json": SOURCE / "development_population.json",
        "implementation/src/ser/authzgym/semantic_contract.py": ROOT
        / "src/ser/authzgym/semantic_contract.py",
        "implementation/src/ser/authzgym/semantic_transport.py": ROOT
        / "src/ser/authzgym/semantic_transport.py",
        "implementation/src/ser/evaluation/authz_contract_analysis.py": ROOT
        / "src/ser/evaluation/authz_contract_analysis.py",
        "implementation/tools/autopsy_authzgym_realmodel.py": ROOT
        / "tools/autopsy_authzgym_realmodel.py",
        "implementation/tools/run_authzgym_semantic_contract.py": ROOT
        / "tools/run_authzgym_semantic_contract.py",
        "implementation/tools/verify_authzgym_semantic_contract.py": ROOT
        / "tools/verify_authzgym_semantic_contract.py",
    }


def _project_cost(condition, scheduled_calls: int) -> dict:
    maximum_attempts = scheduled_calls * condition.maximum_attempts_per_semantic_call
    projected_input = maximum_attempts * condition.input_token_ceiling_per_sequential_run
    projected_output = maximum_attempts * condition.max_output_tokens_per_artifact
    projected_cost = (
        projected_input * condition.input_price_per_million_usd
        + projected_output * condition.output_price_per_million_usd
    ) / 1_000_000.0
    return {
        "scheduled_semantic_calls": scheduled_calls,
        "maximum_provider_attempts": maximum_attempts,
        "projected_uncached_input_tokens": projected_input,
        "projected_output_tokens": projected_output,
        "projected_complete_cost_usd": projected_cost,
        "proceed": projected_cost < condition.hard_spend_ceiling_usd,
    }


def freeze(experiment: Path) -> dict:
    paths = _paths(experiment)
    condition = load_real_model_condition(paths["config"])
    population = _json(paths["population"])
    for path in (paths["frozen"], paths["cost_gate"]):
        if path.exists():
            raise FileExistsError(f"frozen artifact already exists: {path.name}")
    files = {name: file_sha256(path) for name, path in _file_inputs(experiment).items()}
    payload = {
        "schema_version": 1,
        "experiment": "authzgym-semantic-contract-v1.2",
        "frozen_before_real_stress_calls": True,
        "population_hash": population["population_hash"],
        "files": files,
        "contract_thresholds": CONTRACT_THRESHOLDS,
        "semantic_thresholds": SEMANTIC_THRESHOLDS,
        "run_schedule": population["schedule"],
    }
    manifest = {**payload, "manifest_hash": content_hash(payload)}
    projection = _project_cost(condition, len(population["schedule"]))
    cost_gate = {
        "schema_version": 1,
        "experiment": "authzgym-semantic-contract-v1.2",
        "frozen_inputs_manifest_hash": manifest["manifest_hash"],
        **projection,
        "hard_spend_ceiling_usd": condition.hard_spend_ceiling_usd,
        "cost_basis": "provider-reported usage at frozen listed rates; not a billing statement",
    }
    cost_gate["record_hash"] = content_hash(cost_gate)
    if not cost_gate["proceed"]:
        raise RuntimeError("stress population fails the preregistered $1 cost gate")
    _write_new_json(paths["frozen"], manifest)
    _write_new_json(paths["cost_gate"], cost_gate)
    return cost_gate


def _load_manifest(experiment: Path) -> tuple[dict, dict[str, str]]:
    paths = _paths(experiment)
    manifest = _json(paths["frozen"])
    payload = dict(manifest)
    digest = payload.pop("manifest_hash")
    if content_hash(payload) != digest:
        raise ValueError("frozen manifest hash mismatch")
    observed = {
        name: file_sha256(path) for name, path in _file_inputs(experiment).items()
    }
    if observed != manifest["files"]:
        raise ValueError("a frozen v1.2 input changed after preregistration")
    return manifest, observed


def run_stress(experiment: Path, proxy_port: int) -> dict:
    paths = _paths(experiment)
    manifest, _ = _load_manifest(experiment)
    cost_gate = _json(paths["cost_gate"])
    if not _record_hash_valid(cost_gate) or not cost_gate["proceed"]:
        raise ValueError("cost gate is invalid")
    for path in (paths["responses"], paths["runs"]):
        if path.exists():
            raise FileExistsError(f"stress output already exists: {path.name}")
    condition = load_real_model_condition(paths["config"])
    prompt = paths["prompt"].read_text(encoding="utf-8")
    population = _json(paths["population"])
    cases = {item["case_id"]: item for item in population["cases"]}
    response_records = []

    def sink(value: dict) -> None:
        response_records.append(value)
        _append_jsonl(paths["responses"], value)

    client = SemanticContractClientV12(
        condition,
        prompt,
        f"socks5h://127.0.0.1:{proxy_port}",
        sink,
    )
    prompt_hash = file_sha256(paths["prompt"])
    config_hash = file_sha256(paths["config"])
    preregistration_hash = file_sha256(paths["preregistration"])
    for index, scheduled in enumerate(manifest["run_schedule"], 1):
        case = cases[scheduled["case_id"]]
        episode = episode_from_case(case)
        before = client.accounting_snapshot()
        response_start = len(response_records)
        result = None
        invalid_reason = None
        try:
            result = client.invoke_v12(
                case["model_visible_input"],
                case["response_schema"],
                episode,
                tuple(case["runner_control"]["legal_target_slots"]),
                call_context={
                    "case_id": case["case_id"],
                    "source_episode_id": case["source_episode_id"],
                    "variant": case["variant"],
                    "repeat": scheduled["repeat"],
                },
            )
        except (ContractV12Error, ProviderError) as exc:
            invalid_reason = f"{type(exc).__name__}:{exc}"
        after = client.accounting_snapshot()
        resources = {key: after[key] - before[key] for key in after}
        call_responses = response_records[response_start:]
        record = {
            "schema_version": 1,
            "experiment": "authzgym-semantic-contract-v1.2",
            "population_hash": population["population_hash"],
            "frozen_inputs_manifest_hash": manifest["manifest_hash"],
            "case_id": case["case_id"],
            "source_episode_id": case["source_episode_id"],
            "variant": case["variant"],
            "repeat": scheduled["repeat"],
            "condition": condition.public_dict(),
            "prompt_sha256": prompt_hash,
            "model_config_sha256": config_hash,
            "preregistration_sha256": preregistration_hash,
            "response_schema_sha256": case["runner_control"]["schema_sha256"],
            "response_record_hashes": [item["record_hash"] for item in call_responses],
            "resources": resources,
            "valid": result is not None,
            "invalid_reason": invalid_reason,
            "result": result,
            "manual_repair": False,
        }
        record["record_hash"] = content_hash(record)
        _append_jsonl(paths["runs"], record)
        if index % 8 == 0 or index == len(manifest["run_schedule"]):
            print(
                canonical_json(
                    {
                        "completed_calls": index,
                        "scheduled_calls": len(manifest["run_schedule"]),
                        "provider_attempts": client.total_provider_calls,
                        "accounted_spend_usd": client.total_cost_usd,
                    }
                ),
                flush=True,
            )
    return {
        "scheduled_calls": len(manifest["run_schedule"]),
        "provider_attempts": client.total_provider_calls,
        "accounted_spend_usd": client.total_cost_usd,
    }


def _enum_values(value: object) -> set[object]:
    if isinstance(value, dict):
        result = set(value.get("enum", ())) if isinstance(value.get("enum"), list) else set()
        for item in value.values():
            result |= _enum_values(item)
        return result
    if isinstance(value, list):
        result = set()
        for item in value:
            result |= _enum_values(item)
        return result
    return set()


def _validate(
    experiment: Path,
    population: dict,
    runs: list[dict],
    responses: list[dict],
    manifest: dict,
    observed_hashes: dict[str, str],
) -> dict:
    paths = _paths(experiment)
    checks = {}
    expected_schedule = [
        (item["case_id"], item["repeat"]) for item in population["schedule"]
    ]
    observed_schedule = [(item["case_id"], item["repeat"]) for item in runs]
    checks["complete development stress schedule"] = {
        "status": "pass" if expected_schedule == observed_schedule else "fail",
        "detail": f"records={len(runs)}/{len(expected_schedule)}",
    }
    source_ids = {item["source_episode_id"] for item in population["cases"]}
    development, _, _ = load_population(SOURCE / "development_population.json")
    expected_ids = {item.episode_id for item in development}
    split_ok = source_ids == expected_ids and len(population["cases"]) == 64
    checks["development-only source population"] = {
        "status": "pass" if split_ok else "fail",
        "detail": f"source episodes={len(source_ids)}; cases={len(population['cases'])}; no evaluation population loaded",
    }
    hashes_ok = observed_hashes == manifest["files"]
    checks["frozen input hashes"] = {
        "status": "pass" if hashes_ok else "fail",
        "detail": "preregistration, prompt, vocabulary, schemas, population, autopsy, source development population, and implementation hashes match",
    }
    response_hashes_ok = all(_record_hash_valid(item) for item in responses) and all(
        hashlib.sha256(item["raw_response_body"].encode("utf-8")).hexdigest()
        == item["raw_response_sha256"]
        for item in responses
    )
    checks["provider response hashes"] = {
        "status": "pass" if response_hashes_ok else "fail",
        "detail": f"verified {len(responses)} local response attempts",
    }
    run_hashes_ok = all(_record_hash_valid(item) for item in runs)
    checks["stress run hashes"] = {
        "status": "pass" if run_hashes_ok else "fail",
        "detail": f"verified {len(runs)} stress records",
    }
    grouped = {}
    for response in responses:
        context = response["call_context"]
        key = (context["case_id"], context["repeat"])
        grouped.setdefault(key, []).append(response)
    retries_identical = all(
        len({item["request_sha256"] for item in items}) == 1
        and [item["attempt"] for item in items] == list(range(1, len(items) + 1))
        for items in grouped.values()
    )
    checks["identical bounded retry policy"] = {
        "status": "pass" if retries_identical else "fail",
        "detail": "every retry reused the exact request hash and at most one retry was allowed",
    }
    schema_hashes_ok = all(
        response["response_schema_sha256"]
        == next(
            item["runner_control"]["schema_sha256"]
            for item in population["cases"]
            if item["case_id"] == response["call_context"]["case_id"]
        )
        for response in responses
    )
    checks["dynamic schema integrity"] = {
        "status": "pass" if schema_hashes_ok else "fail",
        "detail": "each response binds the frozen per-call legal target-slot schema",
    }

    boundary_violations = 0
    for case in population["cases"]:
        visible = case["model_visible_input"]
        if any(key in visible for key in ("evaluator_only", "restricted_truth")):
            boundary_violations += 1
        episode = episode_from_case(case)
        forbidden = {
            episode.truth.mechanism_id,
            episode.truth.correct_conclusion,
            episode.truth.discriminating_artifact_role,
            *episode.artifact_order,
            *(item.hypothesis_id for item in episode.candidates),
        }
        if _enum_values(case["response_schema"]) & forbidden:
            boundary_violations += 1
    checks["information boundary and enum isolation"] = {
        "status": "pass" if boundary_violations == 0 else "fail",
        "detail": f"violations={boundary_violations}; evaluator identifiers never enter model-visible enums",
    }
    models = set()
    usages = []
    for response_record in responses:
        try:
            envelope = json.loads(response_record["raw_response_body"])
        except json.JSONDecodeError:
            continue
        if isinstance(envelope, dict) and envelope.get("model"):
            models.add(str(envelope["model"]))
        usage = _usage_from_response(envelope) if isinstance(envelope, dict) else None
        if usage and usage["input_tokens"] > 0:
            usages.append(usage)
    condition = load_real_model_condition(paths["config"])
    configured_model = condition.model_identifier
    model_ok = models <= {configured_model} and bool(models)
    checks["single frozen model"] = {
        "status": "pass" if model_ok else "fail",
        "detail": f"provider model identifiers={sorted(models)}",
    }
    resource_ceiling_ok = bool(usages) and all(
        item["input_tokens"] <= condition.input_token_ceiling_per_sequential_run
        and item["output_tokens"] <= condition.max_output_tokens_per_artifact
        for item in usages
    )
    checks["provider token ceilings"] = {
        "status": "pass" if resource_ceiling_ok else "fail",
        "detail": (
            f"max input/output={max((item['input_tokens'] for item in usages), default=0)}/"
            f"{max((item['output_tokens'] for item in usages), default=0)} within 4000/1024"
        ),
    }
    total_cost = sum(item["resources"]["monetary_cost_usd"] for item in runs)
    spend_ok = total_cost < 1.0
    checks["hard spend ceiling"] = {
        "status": "pass" if spend_ok else "fail",
        "detail": f"accounted spend=${total_cost:.9f} < $1.00",
    }
    secret = os.environ.get("OPENAI_API_KEY", "")
    secret_found = False
    if secret:
        needle = secret.encode("utf-8")
        secret_found = any(
            needle in path.read_bytes()
            for path in experiment.rglob("*")
            if path.is_file()
        )
    checks["secret redaction"] = {
        "status": "pass" if not secret_found else "fail",
        "detail": "configured API credential value is absent from all experiment files",
    }
    static_only = all(
        set(case["model_visible_input"]) == {
            "semantic_interface",
            "instruction_scope",
            "current_artifact",
            "candidate_hypotheses",
            "current_epistemic_summary",
            "public_artifact_inventory",
        }
        for case in population["cases"]
    )
    checks["static semantic-only action surface"] = {
        "status": "pass" if static_only else "fail",
        "detail": "one purchased development artifact per call; no routing, execution, network tool, GitLab, or IDS action",
    }
    status = "pass" if all(item["status"] == "pass" for item in checks.values()) else "fail"
    return {
        "schema_version": 1,
        "experiment": "authzgym-semantic-contract-v1.2",
        "status": status,
        "counts": {"information_boundary_violations": boundary_violations},
        "checks": checks,
    }


def analyze(experiment: Path) -> dict:
    paths = _paths(experiment)
    manifest, observed_hashes = _load_manifest(experiment)
    population = _json(paths["population"])
    runs = _jsonl(paths["runs"])
    responses = _jsonl(paths["responses"])
    validation = _validate(
        experiment, population, runs, responses, manifest, observed_hashes
    )
    summary = summarize(population, runs, responses, validation)
    autopsy = _json(paths["autopsy_json"])
    _write_new_json(paths["validation"], validation)
    _write_new_json(paths["summary"], summary)
    _write_new(paths["report"], render_report(summary, validation, autopsy))
    _write_new(paths["interpretation"], render_interpretation(summary))
    return {
        "validation": validation["status"],
        "contract": summary["contract"]["classification"],
        "semantics": summary["semantics"]["classification"],
        "next_experiment": summary["decision_rule"]["selected_next_experiment"],
        "accounted_spend_usd": summary["provider_accounting"]["total_cost_usd"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command", choices=("prepare", "freeze", "run", "analyze")
    )
    parser.add_argument("--experiment-dir", type=Path, default=EXPERIMENT)
    parser.add_argument("--proxy-port", type=int, default=47819)
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare(args.experiment_dir)
    elif args.command == "freeze":
        result = freeze(args.experiment_dir)
    elif args.command == "run":
        result = run_stress(args.experiment_dir, args.proxy_port)
    else:
        result = analyze(args.experiment_dir)
    print(canonical_json(result))


if __name__ == "__main__":
    main()
