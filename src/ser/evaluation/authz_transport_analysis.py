"""Analysis for the transport-only AuthzGym envelope experiment."""

from __future__ import annotations

from collections import defaultdict
from statistics import fmean

from ser.authzgym.semantic_contract import SEMANTIC_EQUIVALENCE_VARIANTS
from ser.evaluation.authz_contract_analysis import (
    CONTRACT_THRESHOLDS,
    _normalize,
    summarize,
)


TRANSPORT_CLASSIFIERS = (
    "transport_stable",
    "transport_recoverable_but_unstable",
    "transport_unstable",
    "invalid",
)


def classify_transport(
    *,
    validation_status: str,
    provider_completed: int,
    permanently_failed: int,
    failed_tunnel_starts: int,
    reconnect_requests: int,
    successful_reconnects: int,
    cleanup_ok: bool,
) -> str:
    if validation_status != "pass":
        return "invalid"
    if (
        provider_completed == 128
        and permanently_failed == 0
        and failed_tunnel_starts == 0
        and reconnect_requests == successful_reconnects
        and cleanup_ok
    ):
        return "transport_stable"
    if provider_completed == 128 and permanently_failed == 0 and cleanup_ok:
        return "transport_recoverable_but_unstable"
    return "transport_unstable"


def _mean(values) -> float:
    values = tuple(values)
    return fmean(values) if values else 0.0


def _longest_successful_sequence(runs: list[dict]) -> int:
    longest = 0
    current = 0
    for run in runs:
        if run["provider_response_received"]:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def _latency_by_generation(responses: list[dict]) -> dict:
    grouped = defaultdict(list)
    for item in responses:
        grouped[str(item["transport"]["tunnel_generation"])].append(
            item["transport"]["latency_ms"]
        )
    return {
        generation: {
            "provider_responses": len(values),
            "mean_latency_ms": _mean(values),
            "maximum_latency_ms": max(values),
        }
        for generation, values in sorted(
            grouped.items(), key=lambda item: int(item[0])
        )
    }


def _latency_across_generation_changes(responses: list[dict]) -> list[dict]:
    result = []
    for before, after in zip(responses, responses[1:]):
        before_generation = before["transport"]["tunnel_generation"]
        after_generation = after["transport"]["tunnel_generation"]
        if before_generation == after_generation:
            continue
        result.append(
            {
                "before_generation": before_generation,
                "after_generation": after_generation,
                "before_latency_ms": before["transport"]["latency_ms"],
                "after_latency_ms": after["transport"]["latency_ms"],
                "after_minus_before_latency_ms": (
                    after["transport"]["latency_ms"]
                    - before["transport"]["latency_ms"]
                ),
            }
        )
    return result


def _transformation_stability(population: dict, runs: list[dict]) -> dict:
    cases = {item["case_id"]: item for item in population["cases"]}
    normalized = {}
    valid_by_case_repeat = {}
    for run in runs:
        key = (run["case_id"], run["repeat"])
        valid_by_case_repeat[key] = run["valid"]
        if not run["valid"]:
            continue
        case = cases[run["case_id"]]
        content = run["result"]["parsed"]["provider_content"]
        normalized[key] = _normalize(case, content)

    canonical = [
        item for item in population["cases"] if item["variant"] == "base_entry"
    ]
    variants = {}
    for variant in SEMANTIC_EQUIVALENCE_VARIANTS:
        pairs = []
        for base in canonical:
            peer = next(
                item
                for item in population["cases"]
                if item["source_episode_id"] == base["source_episode_id"]
                and item["variant"] == variant
            )
            for repeat in (1, 2):
                left = (base["case_id"], repeat)
                right = (peer["case_id"], repeat)
                both = left in normalized and right in normalized
                pairs.append((both, both and normalized[left] == normalized[right]))
        variants[variant] = {
            "pairs": len(pairs),
            "both_schema_valid_rate": _mean(float(item[0]) for item in pairs),
            "semantic_exact_rate": _mean(float(item[1]) for item in pairs),
        }

    repeat_by_variant = {}
    for variant in sorted({item["variant"] for item in population["cases"]}):
        pairs = []
        for case in population["cases"]:
            if case["variant"] != variant:
                continue
            left = (case["case_id"], 1)
            right = (case["case_id"], 2)
            both = left in normalized and right in normalized
            pairs.append((both, both and normalized[left] == normalized[right]))
        repeat_by_variant[variant] = {
            "pairs": len(pairs),
            "both_schema_valid_rate": _mean(float(item[0]) for item in pairs),
            "semantic_exact_rate": _mean(float(item[1]) for item in pairs),
        }
    return {
        "semantic_equivalence_by_transformation": variants,
        "repeat_stability_by_variant": repeat_by_variant,
    }


def _recompute_contract(summary: dict, runs: list[dict], responses: list[dict]) -> None:
    observed = summary["contract"]["observed"]
    scheduled = len(runs)
    first_valid = sum(
        item["attempt"] == 1 and item["contract_validation"]["valid"]
        for item in responses
    )
    observed["scheduled_calls"] = scheduled
    observed["provider_attempts"] = len(responses)
    observed["first_attempt_valid"] = first_valid
    observed["first_attempt_schema_valid_rate"] = (
        first_valid / scheduled if scheduled else 0.0
    )
    observed["post_retry_valid"] = sum(item["valid"] for item in runs)
    observed["post_retry_valid_rate"] = (
        observed["post_retry_valid"] / scheduled if scheduled else 0.0
    )
    mechanical_pass = (
        observed["first_attempt_schema_valid_rate"]
        >= CONTRACT_THRESHOLDS["minimum_first_attempt_schema_valid_rate"]
        and observed["post_retry_valid_rate"]
        >= CONTRACT_THRESHOLDS["minimum_post_retry_valid_rate"]
        and observed["finish_reason_length"] == 0
        and observed["incomplete_json"] == 0
        and observed["illegal_artifact_references"] == 0
        and observed["illegal_hypothesis_references"] == 0
        and observed["illegal_relation_references"] == 0
        and observed["manual_repairs"] == 0
        and observed["information_boundary_violations"] == 0
    )
    summary["contract"]["classification"] = (
        "contract_stable" if mechanical_pass else "contract_unstable"
    )


def summarize_transport(
    population: dict,
    runs: list[dict],
    provider_responses: list[dict],
    transport_attempts: list[dict],
    tunnel_events: list[dict],
    validation: dict,
) -> dict:
    semantic = summarize(population, runs, provider_responses, validation)
    _recompute_contract(semantic, runs, provider_responses)
    semantic["stability"].update(_transformation_stability(population, runs))

    request_failure_reconnects = sum(
        item["event"] == "reconnect_requested" for item in tunnel_events
    )
    successful_request_failure_reconnects = sum(
        item["event"] == "reconnect_complete" for item in tunnel_events
    )
    precall_reconnects = sum(
        item["event"] == "precall_liveness"
        and not (item["process_alive"] and item["listener_alive"])
        for item in tunnel_events
    )
    successful_precall_reconnects = sum(
        item["event"] == "tunnel_ready"
        and item.get("reason") == "precall_liveness_failure"
        for item in tunnel_events
    )
    reconnect_requests = request_failure_reconnects + precall_reconnects
    successful_reconnects = (
        successful_request_failure_reconnects + successful_precall_reconnects
    )
    failed_tunnel_starts = sum(
        item["event"] == "tunnel_start_failed" for item in tunnel_events
    )
    cleanup_events = [
        item for item in tunnel_events if item["event"] == "cleanup_complete"
    ]
    cleanup_ok = bool(cleanup_events) and all(
        item["process_exited"] and item["listener_closed"]
        for item in cleanup_events
    )
    provider_completed = sum(item["provider_response_received"] for item in runs)
    permanently_failed = sum(item["permanent_transport_failure"] for item in runs)
    raw_failures = sum(
        not item["provider_response_received"] for item in transport_attempts
    )
    generations = max(
        (int(item["generation"]) for item in tunnel_events), default=0
    )
    transport = {
        "scheduled_logical_calls": len(runs),
        "logical_calls_with_provider_response": provider_completed,
        "raw_transport_failures": raw_failures,
        "successful_tunnel_recoveries": successful_reconnects,
        "reconnect_requests": reconnect_requests,
        "request_failure_reconnects": request_failure_reconnects,
        "precall_liveness_reconnects": precall_reconnects,
        "permanently_failed_logical_calls": permanently_failed,
        "tunnel_generations": generations,
        "failed_tunnel_start_attempts": failed_tunnel_starts,
        "longest_successful_sequence": _longest_successful_sequence(runs),
        "cleanup_process_exited_and_listener_closed": cleanup_ok,
        "provider_response_latency_by_tunnel_generation": _latency_by_generation(
            provider_responses
        ),
        "provider_response_latency_across_generation_changes": (
            _latency_across_generation_changes(provider_responses)
        ),
    }

    classifier = classify_transport(
        validation_status=validation["status"],
        provider_completed=provider_completed,
        permanently_failed=permanently_failed,
        failed_tunnel_starts=failed_tunnel_starts,
        reconnect_requests=reconnect_requests,
        successful_reconnects=successful_reconnects,
        cleanup_ok=cleanup_ok,
    )
    transport["classification"] = classifier

    contract = semantic["contract"]["classification"]
    signal = semantic["semantics"]["classification"]
    if classifier != "transport_stable":
        next_experiment = "case_a_stay_at_transport_layer"
    elif contract != "contract_stable":
        next_experiment = "case_b_return_to_semantic_contract_engineering"
    elif signal != "semantic_signal_promising":
        next_experiment = "case_c_same_contract_next_stronger_inexpensive_model"
    else:
        next_experiment = "case_d_fresh_population_architecture_preregistration"

    return {
        "schema_version": 1,
        "experiment": "authzgym-transport-envelope-v1",
        "population_hash": population["population_hash"],
        "transport": transport,
        "semantic_contract": semantic["contract"],
        "semantic_signal": semantic["semantics"],
        "downstream_action_value": semantic["downstream_action_value"],
        "stability": semantic["stability"],
        "provider_accounting": semantic["provider_accounting"],
        "decision_rule": {
            "selected_next_experiment": next_experiment,
            "no_hypothesis_promotion": True,
        },
    }


def render_report(summary: dict, validation: dict, autopsy: dict) -> str:
    transport = summary["transport"]
    contract = summary["semantic_contract"]
    signal = summary["semantic_signal"]
    action = summary["downstream_action_value"]
    stability = summary["stability"]
    accounting = summary["provider_accounting"]
    return "\n".join(
        [
            "# AuthzGym transport-envelope v1 report",
            "",
            "This development-only study manipulates only local transport supervision. The semantic-contract v1.2 prompt, schema, model, population, parser, and estimator remain frozen.",
            "",
            f"Validation: **{validation['status']}**",
            f"Transport classifier: **`{transport['classification']}`**",
            f"Semantic-contract diagnostic: **`{contract['classification']}`**",
            f"Semantic-signal diagnostic: **`{signal['classification']}`**",
            "",
            "## Prior failure evidence",
            "",
            f"The immutable Phase 5A.4 sequence retained {autopsy['successful_prefix_attempts']} successful prefix attempts followed by {autopsy['curl_returncode_counts'].get('28', 0)} timeouts, {autopsy['curl_returncode_counts'].get('97', 0)} proxy-handshake failure, and {autopsy['curl_returncode_counts'].get('7', 0)} immediate connection failures. The strongest supported cause is the long-lived SSH/SOCKS forwarding path; the old logs cannot isolate remote DNS, wiseau egress, or endpoint health during the initial timeouts.",
            "",
            "## Transport completion",
            "",
            f"- Provider responses received: **{transport['logical_calls_with_provider_response']}/{transport['scheduled_logical_calls']}**.",
            f"- Raw transport failures: **{transport['raw_transport_failures']}**.",
            f"- Successful recoveries: **{transport['successful_tunnel_recoveries']}** of **{transport['reconnect_requests']}** requested.",
            f"- Permanent logical-call losses: **{transport['permanently_failed_logical_calls']}**.",
            f"- Tunnel generations: **{transport['tunnel_generations']}**; failed starts: **{transport['failed_tunnel_start_attempts']}**.",
            f"- Longest successful logical-call sequence: **{transport['longest_successful_sequence']}**.",
            f"- Final process/listener cleanup: **{str(transport['cleanup_process_exited_and_listener_closed']).lower()}**.",
            f"- Provider-response latency is grouped by tunnel generation in `summary.json`; **{len(transport['provider_response_latency_across_generation_changes'])}** before/after generation transition pairs were observed.",
            "",
            "## Frozen semantic-contract diagnostics",
            "",
            f"- First-attempt schema-valid: **{contract['observed']['first_attempt_valid']}/{contract['observed']['scheduled_calls']}** (`{contract['observed']['first_attempt_schema_valid_rate']:.6f}`).",
            f"- Valid after frozen semantic retry: **{contract['observed']['post_retry_valid']}/{contract['observed']['scheduled_calls']}** (`{contract['observed']['post_retry_valid_rate']:.6f}`).",
            f"- Length/incomplete JSON: **{contract['observed']['finish_reason_length']}/{contract['observed']['incomplete_json']}**.",
            f"- Illegal artifact/hypothesis/relation references: **{contract['observed']['illegal_artifact_references']}/{contract['observed']['illegal_hypothesis_references']}/{contract['observed']['illegal_relation_references']}**.",
            f"- Fact precision/recall: **{signal['facts']['precision']:.6f}/{signal['facts']['recall']:.6f}**.",
            f"- Hypothesis-effect precision/recall: **{signal['hypothesis_effects']['precision']:.6f}/{signal['hypothesis_effects']['recall']:.6f}**.",
            f"- Unresolved-relation precision/recall: **{signal['unresolved_relations']['precision']:.6f}/{signal['unresolved_relations']['recall']:.6f}**.",
            f"- Repeat exactness: **{stability['repeat_semantic_exact_rate']:.6f}**; transformation semantic equivalence: **{stability['semantic_equivalence_exact_rate']:.6f}**.",
            "",
            "## Oracle and resources",
            "",
            f"Oracle-conditioned top-1/top-2/regret: **{action['oracle_conditioned']['top1']:.6f}/{action['oracle_conditioned']['top2']:.6f}/{action['oracle_conditioned']['mean_normalized_regret']:.6f}**.",
            f"Provider-reported input/output tokens: **{accounting['input_tokens']}/{accounting['output_tokens']}**.",
            f"Accounted spend: **${accounting['total_cost_usd']:.9f}** under the $1 ceiling.",
            f"Decision-rule result: **`{summary['decision_rule']['selected_next_experiment']}`**.",
            "",
            "No H-001, H-016, H-017, H-018, or new E-* finding is promoted by this transport/development result.",
            "",
        ]
    )


def render_interpretation(summary: dict) -> str:
    return (
        "# AuthzGym transport-envelope v1 interpretation\n\n"
        f"The preregistered transport classifier is **`{summary['transport']['classification']}`**. "
        f"The separately computed frozen semantic-contract and semantic-signal diagnostics are **`{summary['semantic_contract']['classification']}`** and **`{summary['semantic_signal']['classification']}`**.\n\n"
        "This development-only result cannot establish architecture leverage, confirmatory model performance, GitLab readiness, or cross-domain competence.\n\n"
        f"The mechanical next experiment is **`{summary['decision_rule']['selected_next_experiment']}`**.\n"
    )
