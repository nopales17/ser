#!/usr/bin/env python3
"""Freeze, run, and analyze the AuthzGym transport-envelope experiment."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from autopsy_authzgym_transport import analyze as reproduce_autopsy
from autopsy_authzgym_transport import render_report as render_autopsy_report
from run_authzgym_semantic_contract import (
    _load_manifest as load_semantic_manifest,
    _validate as validate_semantic_run,
)
from ser.authzgym.realmodel import (
    ProviderError,
    _usage_from_response,
    load_real_model_condition,
)
from ser.authzgym.semantic_contract import ContractV12Error, episode_from_case
from ser.authzgym.supervised_transport import (
    SupervisedSemanticContractClientV12,
    TransportUnavailable,
)
from ser.authzgym.tunnel_supervisor import (
    TunnelError,
    TunnelSupervisor,
    load_tunnel_policy,
)
from ser.core.types import canonical_json, content_hash
from ser.evaluation.authz_artifacts import file_sha256
from ser.evaluation.authz_contract_analysis import (
    CONTRACT_THRESHOLDS,
    SEMANTIC_THRESHOLDS,
    summarize as summarize_semantic,
)
from ser.evaluation.authz_transport_analysis import (
    render_interpretation,
    render_report,
    summarize_transport,
)


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "experiments/authzgym_transport_envelope_v1"
SEMANTIC_SOURCE = ROOT / "experiments/authzgym_semantic_contract_v1_2"
DEVELOPMENT_SOURCE = ROOT / "experiments/authzgym_static_v1_1"


def _paths(experiment: Path) -> dict[str, Path]:
    return {
        "preregistration": experiment / "PREREGISTRATION.md",
        "transport_config": experiment / "transport_config.json",
        "autopsy_json": experiment / "TRANSPORT_AUTOPSY.json",
        "autopsy_report": experiment / "TRANSPORT_AUTOPSY.md",
        "frozen": experiment / "FROZEN_INPUTS.json",
        "cost_gate": experiment / "COST_GATE.json",
        "transport_attempts": experiment / "transport_attempts.jsonl",
        "responses": experiment / "provider_responses.jsonl",
        "tunnel_events": experiment / "tunnel_events.jsonl",
        "runs": experiment / "stress_runs.jsonl",
        "validation": experiment / "validation.json",
        "summary": experiment / "summary.json",
        "report": experiment / "REPORT.md",
        "interpretation": experiment / "INTERPRETATION.md",
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


def _verify_preflight_archive(experiment: Path) -> dict:
    archive = experiment / "preflight_attempt_1"
    expected_hashes = {
        "FROZEN_INPUTS.json": "1f17598e747cc33e6652ccd7f8cebfe229dc5e0f27a823d8779407a1459b07b0",
        "COST_GATE.json": "a11f8a2255773bfdf7da7d3977180e565d3d5d24f63c22d86239c6e534e92cf1",
        "tunnel_events.jsonl": "78a6efe65c2793180a47079a7d1fd6c3e4e5ec46bf5e6a9a99c404c84eede10b",
    }
    observed_hashes = {
        name: file_sha256(archive / name) for name in expected_hashes
    }
    if observed_hashes != expected_hashes:
        raise ValueError("preserved zero-inference preflight hashes changed")
    initial_manifest = _json(archive / "FROZEN_INPUTS.json")
    if initial_manifest["manifest_hash"] != (
        "19033f0d4264448b5708edc213b0e647e18a56c8d38757c968b7e13d7d387936"
    ):
        raise ValueError("preserved initial manifest identity changed")
    events = _jsonl(archive / "tunnel_events.jsonl")
    probes = [item for item in events if item["event"] == "api_connectivity_probe"]
    cleanup = [item for item in events if item["event"] == "cleanup_complete"]
    if not (
        len(events) == 9
        and len(probes) == 2
        and all(
            item["probe"]["curl_returncode"] == 26
            and item["probe"]["paid_inference"] is False
            for item in probes
        )
        and len(cleanup) == 1
        and cleanup[0]["process_exited"]
        and cleanup[0]["listener_closed"]
    ):
        raise ValueError("preserved preflight evidence differs from recorded failure")
    return {
        "events": len(events),
        "probe_failures": len(probes),
        "paid_inferences": 0,
        "cleanup_confirmed": True,
        "initial_manifest_hash": initial_manifest["manifest_hash"],
    }


def _file_inputs(experiment: Path) -> dict[str, Path]:
    paths = _paths(experiment)
    semantic = SEMANTIC_SOURCE
    return {
        "PREREGISTRATION.md": paths["preregistration"],
        "transport_config.json": paths["transport_config"],
        "TRANSPORT_AUTOPSY.json": paths["autopsy_json"],
        "TRANSPORT_AUTOPSY.md": paths["autopsy_report"],
        "PREFLIGHT_FAILURE.md": experiment / "PREFLIGHT_FAILURE.md",
        "preflight_attempt_1/FROZEN_INPUTS.json": experiment
        / "preflight_attempt_1/FROZEN_INPUTS.json",
        "preflight_attempt_1/COST_GATE.json": experiment
        / "preflight_attempt_1/COST_GATE.json",
        "preflight_attempt_1/tunnel_events.jsonl": experiment
        / "preflight_attempt_1/tunnel_events.jsonl",
        "semantic_contract/FROZEN_INPUTS.json": semantic / "FROZEN_INPUTS.json",
        "semantic_contract/PREREGISTRATION.md": semantic / "PREREGISTRATION.md",
        "semantic_contract/model_config.json": semantic / "model_config.json",
        "semantic_contract/STRESS_POPULATION.json": semantic
        / "STRESS_POPULATION.json",
        "semantic_contract/prompts/semantic_observation_v1_2.txt": semantic
        / "prompts/semantic_observation_v1_2.txt",
        "semantic_contract/schemas/semantic_vocabulary_v1_2.json": semantic
        / "schemas/semantic_vocabulary_v1_2.json",
        "semantic_contract/schemas/README.md": semantic / "schemas/README.md",
        "source/development_population.json": DEVELOPMENT_SOURCE
        / "development_population.json",
        "implementation/src/ser/authzgym/semantic_contract.py": ROOT
        / "src/ser/authzgym/semantic_contract.py",
        "implementation/src/ser/authzgym/semantic_transport.py": ROOT
        / "src/ser/authzgym/semantic_transport.py",
        "implementation/src/ser/authzgym/tunnel_supervisor.py": ROOT
        / "src/ser/authzgym/tunnel_supervisor.py",
        "implementation/src/ser/authzgym/supervised_transport.py": ROOT
        / "src/ser/authzgym/supervised_transport.py",
        "implementation/src/ser/evaluation/authz_contract_analysis.py": ROOT
        / "src/ser/evaluation/authz_contract_analysis.py",
        "implementation/src/ser/evaluation/authz_transport_analysis.py": ROOT
        / "src/ser/evaluation/authz_transport_analysis.py",
        "implementation/tools/autopsy_authzgym_transport.py": ROOT
        / "tools/autopsy_authzgym_transport.py",
        "implementation/tools/run_authzgym_transport_envelope.py": ROOT
        / "tools/run_authzgym_transport_envelope.py",
        "implementation/tools/verify_authzgym_transport_envelope.py": ROOT
        / "tools/verify_authzgym_transport_envelope.py",
        "tests/test_authzgym_transport_envelope.py": ROOT
        / "tests/test_authzgym_transport_envelope.py",
    }


def _project_cost(condition, scheduled_calls: int, maximum_submissions: int) -> dict:
    projected_input = (
        maximum_submissions
        * condition.input_token_ceiling_per_sequential_run
    )
    projected_output = (
        maximum_submissions * condition.max_output_tokens_per_artifact
    )
    projected_cost = (
        projected_input * condition.input_price_per_million_usd
        + projected_output * condition.output_price_per_million_usd
    ) / 1_000_000.0
    return {
        "scheduled_logical_calls": scheduled_calls,
        "maximum_semantic_attempts_per_logical_call": condition.maximum_attempts_per_semantic_call,
        "maximum_transport_replays_per_logical_call": 1,
        "maximum_api_submissions": maximum_submissions,
        "projected_uncached_input_tokens": projected_input,
        "projected_output_tokens": projected_output,
        "projected_complete_cost_usd": projected_cost,
        "connectivity_probes_are_paid_inferences": False,
        "proceed": projected_cost < condition.hard_spend_ceiling_usd,
    }


def prepare(experiment: Path) -> dict:
    semantic_manifest, _ = load_semantic_manifest(SEMANTIC_SOURCE)
    population = _json(SEMANTIC_SOURCE / "STRESS_POPULATION.json")
    autopsy = reproduce_autopsy(SEMANTIC_SOURCE)
    if autopsy != _json(_paths(experiment)["autopsy_json"]):
        raise ValueError("transport autopsy does not reproduce")
    if render_autopsy_report(autopsy) != _paths(experiment)[
        "autopsy_report"
    ].read_text(encoding="utf-8"):
        raise ValueError("transport autopsy report does not reproduce")
    if population["population_hash"] != semantic_manifest["population_hash"]:
        raise ValueError("semantic population no longer matches its frozen manifest")
    preflight = _verify_preflight_archive(experiment)
    return {
        "semantic_manifest_hash": semantic_manifest["manifest_hash"],
        "population_hash": population["population_hash"],
        "cases": len(population["cases"]),
        "scheduled_calls": len(population["schedule"]),
        "autopsy_record_hash": autopsy["record_hash"],
        "preserved_preflight": preflight,
    }


def freeze(experiment: Path) -> dict:
    paths = _paths(experiment)
    for path in (paths["frozen"], paths["cost_gate"]):
        if path.exists():
            raise FileExistsError(f"frozen artifact already exists: {path.name}")
    prepared = prepare(experiment)
    condition = load_real_model_condition(
        SEMANTIC_SOURCE / "model_config.json"
    )
    policy = load_tunnel_policy(paths["transport_config"])
    population = _json(SEMANTIC_SOURCE / "STRESS_POPULATION.json")
    files = {
        name: file_sha256(path) for name, path in _file_inputs(experiment).items()
    }
    payload = {
        "schema_version": 1,
        "experiment": "authzgym-transport-envelope-v1",
        "frozen_before_api_calls": True,
        "semantic_contract_version": "v1.2",
        "source_semantic_manifest_hash": prepared["semantic_manifest_hash"],
        "population_hash": population["population_hash"],
        "files": files,
        "contract_thresholds": CONTRACT_THRESHOLDS,
        "semantic_thresholds": SEMANTIC_THRESHOLDS,
        "transport_classifiers": {
            "invalid_precedence": True,
            "stable_provider_responses": 128,
            "stable_permanent_transport_losses": 0,
            "stable_failed_tunnel_start_attempts": 0,
            "stable_reconnect_bookkeeping_one_for_one": True,
            "cleanup_required": True,
        },
        "run_schedule": population["schedule"],
    }
    manifest = {**payload, "manifest_hash": content_hash(payload)}
    projection = _project_cost(
        condition, len(population["schedule"]), policy.maximum_api_submissions
    )
    cost_gate = {
        "schema_version": 1,
        "experiment": "authzgym-transport-envelope-v1",
        "frozen_inputs_manifest_hash": manifest["manifest_hash"],
        **projection,
        "hard_spend_ceiling_usd": condition.hard_spend_ceiling_usd,
        "cost_basis": "provider-reported usage at frozen listed rates; not a billing statement",
    }
    cost_gate["record_hash"] = content_hash(cost_gate)
    if not cost_gate["proceed"]:
        raise RuntimeError("transport workload fails the preregistered $1 cost gate")
    _write_new_json(paths["frozen"], manifest)
    _write_new_json(paths["cost_gate"], cost_gate)
    return cost_gate


def _load_manifest(experiment: Path) -> tuple[dict, dict[str, str]]:
    paths = _paths(experiment)
    manifest = _json(paths["frozen"])
    payload = dict(manifest)
    digest = payload.pop("manifest_hash")
    if content_hash(payload) != digest:
        raise ValueError("frozen transport manifest hash mismatch")
    observed = {
        name: file_sha256(path) for name, path in _file_inputs(experiment).items()
    }
    if observed != manifest["files"]:
        raise ValueError("a frozen transport-envelope input changed")
    semantic_manifest, _ = load_semantic_manifest(SEMANTIC_SOURCE)
    if (
        semantic_manifest["manifest_hash"]
        != manifest["source_semantic_manifest_hash"]
    ):
        raise ValueError("the source semantic-contract manifest changed")
    return manifest, observed


def _error_text(exc: Exception) -> str:
    text = f"{type(exc).__name__}:{exc}"
    secret = os.environ.get("OPENAI_API_KEY", "")
    return text.replace(secret, "[REDACTED]") if secret else text


def run_stress(experiment: Path) -> dict:
    paths = _paths(experiment)
    manifest, _ = _load_manifest(experiment)
    cost_gate = _json(paths["cost_gate"])
    if not _record_hash_valid(cost_gate) or not cost_gate["proceed"]:
        raise ValueError("cost gate is invalid")
    output_paths = (
        paths["transport_attempts"],
        paths["responses"],
        paths["tunnel_events"],
        paths["runs"],
    )
    if any(path.exists() for path in output_paths):
        present = [path.name for path in output_paths if path.exists()]
        raise FileExistsError("transport output already exists: " + ", ".join(present))

    condition = load_real_model_condition(
        SEMANTIC_SOURCE / "model_config.json"
    )
    policy = load_tunnel_policy(paths["transport_config"])
    prompt = (
        SEMANTIC_SOURCE / "prompts/semantic_observation_v1_2.txt"
    ).read_text(encoding="utf-8")
    population = _json(SEMANTIC_SOURCE / "STRESS_POPULATION.json")
    cases = {item["case_id"]: item for item in population["cases"]}
    responses: list[dict] = []
    transport_attempts: list[dict] = []
    tunnel_events: list[dict] = []

    def response_sink(value: dict) -> None:
        responses.append(value)
        _append_jsonl(paths["responses"], value)

    def transport_sink(value: dict) -> None:
        transport_attempts.append(value)
        _append_jsonl(paths["transport_attempts"], value)

    def event_sink(value: dict) -> None:
        tunnel_events.append(value)
        _append_jsonl(paths["tunnel_events"], value)

    supervisor = TunnelSupervisor(policy, event_sink)
    client = SupervisedSemanticContractClientV12(
        condition,
        prompt,
        supervisor,
        policy,
        response_sink,
        transport_sink,
    )
    prompt_hash = file_sha256(
        SEMANTIC_SOURCE / "prompts/semantic_observation_v1_2.txt"
    )
    config_hash = file_sha256(SEMANTIC_SOURCE / "model_config.json")
    preregistration_hash = file_sha256(paths["preregistration"])
    transport_config_hash = file_sha256(paths["transport_config"])

    try:
        supervisor.establish(client.connectivity_probe, reason="initial_startup")
        for index, scheduled in enumerate(manifest["run_schedule"], 1):
            case = cases[scheduled["case_id"]]
            call_context = {
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
            except TransportUnavailable as exc:
                invalid_reason = _error_text(exc)
                permanent_transport_failure = True
            except TunnelError as exc:
                invalid_reason = _error_text(exc)
                permanent_transport_failure = True
            except (ContractV12Error, ProviderError) as exc:
                invalid_reason = _error_text(exc)
            after = client.accounting_snapshot()
            resources = {key: after[key] - before[key] for key in after}
            call_responses = responses[response_start:]
            call_transports = transport_attempts[transport_start:]
            call_events = tunnel_events[event_start:]
            record = {
                "schema_version": 1,
                "experiment": "authzgym-transport-envelope-v1",
                "population_hash": population["population_hash"],
                "frozen_inputs_manifest_hash": manifest["manifest_hash"],
                **call_context,
                "condition": condition.public_dict(),
                "transport_policy": policy.public_dict(),
                "prompt_sha256": prompt_hash,
                "model_config_sha256": config_hash,
                "preregistration_sha256": preregistration_hash,
                "transport_config_sha256": transport_config_hash,
                "response_schema_sha256": case["runner_control"][
                    "schema_sha256"
                ],
                "response_record_hashes": [
                    item["record_hash"] for item in call_responses
                ],
                "transport_attempt_record_hashes": [
                    item["record_hash"] for item in call_transports
                ],
                "tunnel_event_record_hashes": [
                    item["record_hash"] for item in call_events
                ],
                "resources": resources,
                "provider_response_received": bool(call_responses),
                "permanent_transport_failure": permanent_transport_failure,
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
                            "completed_logical_calls": index,
                            "scheduled_logical_calls": len(
                                manifest["run_schedule"]
                            ),
                            "api_submissions": client.total_provider_calls,
                            "provider_responses": client.total_provider_responses,
                            "transport_failures": client.total_transport_failures,
                            "tunnel_generation": supervisor.generation,
                            "accounted_spend_usd": client.total_cost_usd,
                        }
                    ),
                    flush=True,
                )
    finally:
        supervisor.stop(reason="runner_finally_cleanup")
    return {
        "scheduled_logical_calls": len(manifest["run_schedule"]),
        "api_submissions": client.total_provider_calls,
        "provider_responses": client.total_provider_responses,
        "transport_failures": client.total_transport_failures,
        "transport_recoveries": client.total_transport_recoveries,
        "tunnel_generations": supervisor.generation,
        "accounted_spend_usd": client.total_cost_usd,
    }


def _semantic_manifest_observed() -> tuple[dict, dict[str, str]]:
    return load_semantic_manifest(SEMANTIC_SOURCE)


def _transport_validation(
    experiment: Path,
    population: dict,
    runs: list[dict],
    responses: list[dict],
    transport_attempts: list[dict],
    tunnel_events: list[dict],
    manifest: dict,
    observed_hashes: dict[str, str],
) -> dict:
    paths = _paths(experiment)
    semantic_manifest, semantic_hashes = _semantic_manifest_observed()
    base = validate_semantic_run(
        SEMANTIC_SOURCE,
        population,
        runs,
        responses,
        semantic_manifest,
        semantic_hashes,
    )
    checks = dict(base["checks"])
    checks.pop("frozen input hashes", None)
    checks["frozen semantic and transport input hashes"] = {
        "status": "pass" if observed_hashes == manifest["files"] else "fail",
        "detail": "all frozen v1.2 semantic inputs and transport-only implementation inputs match",
    }
    checks["source semantic manifest identity"] = {
        "status": "pass"
        if semantic_manifest["manifest_hash"]
        == manifest["source_semantic_manifest_hash"]
        else "fail",
        "detail": semantic_manifest["manifest_hash"],
    }

    transport_hashes_ok = all(
        _record_hash_valid(item) for item in transport_attempts
    )
    event_hashes_ok = all(_record_hash_valid(item) for item in tunnel_events)
    checks["transport attempt hashes"] = {
        "status": "pass" if transport_hashes_ok else "fail",
        "detail": f"verified {len(transport_attempts)} API submissions",
    }
    checks["tunnel event hashes"] = {
        "status": "pass" if event_hashes_ok else "fail",
        "detail": f"verified {len(tunnel_events)} supervised tunnel events",
    }

    response_by_hash = {item["record_hash"]: item for item in responses}
    transport_by_hash = {item["record_hash"]: item for item in transport_attempts}
    event_by_hash = {item["record_hash"]: item for item in tunnel_events}
    links_ok = all(
        all(item in response_by_hash for item in run["response_record_hashes"])
        and all(
            item in transport_by_hash
            for item in run["transport_attempt_record_hashes"]
        )
        and all(item in event_by_hash for item in run["tunnel_event_record_hashes"])
        for run in runs
    ) and all(
        item["transport_attempt_record_hash"] in transport_by_hash
        for item in responses
    )
    checks["cross-record linkage"] = {
        "status": "pass" if links_ok else "fail",
        "detail": "run, provider-response, transport-attempt, and tunnel-event hashes link locally",
    }

    grouped_transport: dict[tuple, list[dict]] = {}
    grouped_responses: dict[tuple, list[dict]] = {}
    for item in transport_attempts:
        context = item["call_context"]
        key = (context["case_id"], context["repeat"])
        grouped_transport.setdefault(key, []).append(item)
    for item in responses:
        context = item["call_context"]
        key = (context["case_id"], context["repeat"])
        grouped_responses.setdefault(key, []).append(item)
    replay_ok = all(
        len(items) <= 3
        and len({item["request_sha256"] for item in items}) == 1
        and [item["transport_attempt"] for item in items]
        == list(range(1, len(items) + 1))
        and sum(not item["provider_response_received"] for item in items) <= 1
        for items in grouped_transport.values()
    ) and all(
        len(items) <= 2
        and [item["attempt"] for item in items]
        == list(range(1, len(items) + 1))
        for items in grouped_responses.values()
    )
    checks["separate bounded transport and semantic retries"] = {
        "status": "pass" if replay_ok else "fail",
        "detail": "at most three identical-byte submissions, one transport replay, and two semantic attempts per logical call",
    }

    accounted_api_submissions = sum(
        item["resources"]["provider_calls"] for item in runs
    )
    accounted_provider_responses = sum(
        item["resources"]["provider_responses"] for item in runs
    )
    accounted_transport_failures = sum(
        item["resources"]["transport_failures"] for item in runs
    )
    actual_transport_failures = sum(
        not item["provider_response_received"] for item in transport_attempts
    )
    accounting_ok = (
        accounted_api_submissions == len(transport_attempts)
        and accounted_provider_responses == len(responses)
        and accounted_transport_failures == actual_transport_failures
        and len(transport_attempts) <= 384
    )
    checks["transport accounting"] = {
        "status": "pass" if accounting_ok else "fail",
        "detail": (
            f"API submissions={len(transport_attempts)}/384; provider responses={len(responses)}; "
            f"raw transport failures={actual_transport_failures}"
        ),
    }

    cleanup = [item for item in tunnel_events if item["event"] == "cleanup_complete"]
    cleanup_ok = (
        len(cleanup) == 1
        and cleanup[0]["process_exited"]
        and cleanup[0]["listener_closed"]
    )
    checks["final tunnel cleanup"] = {
        "status": "pass" if cleanup_ok else "fail",
        "detail": "one final cleanup event confirms process exit and listener closure",
    }

    starts = [item for item in tunnel_events if item["event"] == "tunnel_start"]
    remote_pure_hop = bool(starts) and all(
        item["ssh_args"][1:3] == ["-N", "-T"]
        and item["ssh_args"][-1]
        == "nopales17@wiseau.seclab.cs.ucsb.edu"
        and item["remote_command"] is False
        and set(item["stripped_environment_names"])
        == {"OPENAI_API_KEY", "OPENAI_BASE_URL"}
        for item in starts
    )
    checks["wiseau pure network hop"] = {
        "status": "pass" if remote_pure_hop else "fail",
        "detail": "SSH uses -N/-T with no remote command; API environment names are stripped",
    }

    transport_scope_ok = all(
        item["proxy_dns_mode"] == "socks5h_remote_resolution"
        and item["tls_verification"] is False
        and item["credential_delivery"] == "anonymous_pipe_curl_config"
        and item["http_connection_strategy"]
        == "fresh_curl_process_per_api_submission_no_shared_pool"
        for item in transport_attempts
    )
    checks["dedicated transport scope"] = {
        "status": "pass" if transport_scope_ok else "fail",
        "detail": "fresh HTTP connection, remote SOCKS DNS, scoped TLS exception, and anonymous-pipe bearer delivery",
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
    checks["local credential redaction"] = {
        "status": "pass" if not secret_found else "fail",
        "detail": "configured credential value is absent from every local experiment artifact",
    }

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
    condition = load_real_model_condition(
        SEMANTIC_SOURCE / "model_config.json"
    )
    frozen_model_ok = models <= {condition.model_identifier} and bool(models)
    checks["exact frozen model"] = {
        "status": "pass" if frozen_model_ok else "fail",
        "detail": f"provider model identifiers={sorted(models)}",
    }
    ceilings_ok = bool(usages) and all(
        item["input_tokens"]
        <= condition.input_token_ceiling_per_sequential_run
        and item["output_tokens"] <= condition.max_output_tokens_per_artifact
        for item in usages
    )
    checks["provider token ceilings"] = {
        "status": "pass" if ceilings_ok else "fail",
        "detail": (
            f"max input/output={max((item['input_tokens'] for item in usages), default=0)}/"
            f"{max((item['output_tokens'] for item in usages), default=0)} within 4000/1024"
        ),
    }
    spend = sum(item["resources"]["monetary_cost_usd"] for item in runs)
    checks["hard spend ceiling"] = {
        "status": "pass" if spend < 1.0 else "fail",
        "detail": f"accounted spend=${spend:.9f} < $1.00",
    }

    oracle_expected = {
        "canonical_development_episodes": 8,
        "top1": 1.0,
        "top2": 1.0,
        "mean_normalized_regret": 0.0,
    }
    oracle_observed = summarize_semantic(
        population, runs, responses, base
    )["downstream_action_value"]["oracle_conditioned"]
    checks["oracle estimator reproduction"] = {
        "status": "pass" if oracle_observed == oracle_expected else "fail",
        "detail": canonical_json(oracle_observed),
    }
    status = "pass" if all(
        item["status"] == "pass" for item in checks.values()
    ) else "fail"
    return {
        "schema_version": 1,
        "experiment": "authzgym-transport-envelope-v1",
        "status": status,
        "counts": base["counts"],
        "checks": checks,
    }


def analyze(experiment: Path) -> dict:
    paths = _paths(experiment)
    manifest, observed_hashes = _load_manifest(experiment)
    population = _json(SEMANTIC_SOURCE / "STRESS_POPULATION.json")
    runs = _jsonl(paths["runs"])
    responses = _jsonl(paths["responses"])
    transport_attempts = _jsonl(paths["transport_attempts"])
    tunnel_events = _jsonl(paths["tunnel_events"])
    validation = _transport_validation(
        experiment,
        population,
        runs,
        responses,
        transport_attempts,
        tunnel_events,
        manifest,
        observed_hashes,
    )
    summary = summarize_transport(
        population,
        runs,
        responses,
        transport_attempts,
        tunnel_events,
        validation,
    )
    autopsy = _json(paths["autopsy_json"])
    _write_new_json(paths["validation"], validation)
    _write_new_json(paths["summary"], summary)
    _write_new(paths["report"], render_report(summary, validation, autopsy))
    _write_new(paths["interpretation"], render_interpretation(summary))
    return {
        "validation": validation["status"],
        "transport": summary["transport"]["classification"],
        "contract": summary["semantic_contract"]["classification"],
        "semantics": summary["semantic_signal"]["classification"],
        "next_experiment": summary["decision_rule"]["selected_next_experiment"],
        "accounted_spend_usd": summary["provider_accounting"][
            "total_cost_usd"
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("prepare", "freeze", "run", "analyze"))
    parser.add_argument("--experiment-dir", type=Path, default=EXPERIMENT)
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare(args.experiment_dir)
    elif args.command == "freeze":
        result = freeze(args.experiment_dir)
    elif args.command == "run":
        result = run_stress(args.experiment_dir)
    else:
        result = analyze(args.experiment_dir)
    print(canonical_json(result))


if __name__ == "__main__":
    main()
