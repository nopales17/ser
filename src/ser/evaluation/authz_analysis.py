"""Validation, decomposition, and reports for Static Semantic AuthzGym v1."""

from __future__ import annotations

from collections import Counter, defaultdict
from statistics import fmean
from typing import Iterable

from ser.authzgym.interpreters import InterpreterCondition
from ser.authzgym.model import AuthzEpisode, total_lines
from ser.authzgym.policies import ARCHITECTURES
from ser.authzgym.runner import run_authz_episode

from .authz_artifacts import verify_record_hashes


REAL_MODEL_THRESHOLDS = {
    "minimum_semantic_fact_precision": 0.65,
    "minimum_semantic_fact_recall": 0.50,
    "minimum_ser_top1_useful_action_recall": 0.60,
    "minimum_ser_top2_useful_action_recall": 0.80,
    "maximum_ser_mean_normalized_routing_regret": 0.35,
    "minimum_eligible_group_branch_rate": 0.50,
    "minimum_oracle_consistent_first_branch_rate": 0.60,
    "maximum_zero_value_spurious_branch_rate": 0.25,
    "minimum_accuracy_gain_over_fixed": 0.083333333333,
    "minimum_accuracy_gain_over_react": 0.041666666667,
    "maximum_mean_token_ratio_to_best_control": 1.10,
}


def build_run_records(
    episodes: Iterable[AuthzEpisode],
    conditions: tuple[InterpreterCondition, ...],
    prompt_text: str,
    prompt_version: str,
    prompt_hash: str,
    config_hash: str,
    population_hash: str,
) -> list[dict]:
    return [
        run_authz_episode(
            episode,
            architecture,
            condition,
            prompt_text,
            prompt_version,
            prompt_hash,
            config_hash,
            population_hash,
        )
        for episode in episodes
        for condition in conditions
        for architecture in ARCHITECTURES
    ]


def _mean(values: Iterable[float]) -> float:
    values = tuple(values)
    return fmean(values) if values else 0.0


def _architecture_metrics(records: list[dict]) -> dict:
    correct = [item["restricted"]["outcome"]["correct"] for item in records]
    semantic = [
        item["restricted"]["outcome"]["semantic_quality"] for item in records
    ]
    expected = sum(item["expected_facts"] for item in semantic)
    extracted = sum(item["extracted_facts"] for item in semantic)
    true_positive = sum(item["true_positive_facts"] for item in semantic)
    resources = [item["public"]["raw_resources"] for item in records]
    routing = [
        item["restricted"]["outcome"]["routing_quality"] for item in records
    ]
    first = [
        item["post_entry_steps"][0]
        for item in routing
        if item["post_entry_steps"]
    ]
    failure_counts = Counter(
        failure
        for item in records
        for failure in item["restricted"]["outcome"]["failure_layers"]
    )
    return {
        "runs": len(records),
        "valid_runs": sum(item["public"]["valid"] for item in records),
        "accuracy": _mean(float(item) for item in correct),
        "decision_loss": 1.0 - _mean(float(item) for item in correct),
        "semantic_fact_precision": true_positive / extracted if extracted else 0.0,
        "semantic_fact_recall": true_positive / expected if expected else 0.0,
        "first_route_correct_rate": _mean(
            float(item["selected_artifact_id"] in item["oracle_best_artifact_ids"])
            for item in first
        ),
        "first_route_top1_oracle_recall": _mean(
            float(item["estimated_top_one_is_oracle"]) for item in first
        ),
        "first_route_top2_oracle_recall": _mean(
            float(item["estimated_top_two_contains_oracle"]) for item in first
        ),
        "mean_normalized_routing_regret": _mean(
            item["normalized_routing_regret"] for item in first
        ),
        "mean_resources": {
            name: _mean(item[name] for item in resources) for name in resources[0]
        },
        "failure_layers": dict(sorted(failure_counts.items())),
    }


def _branch_metrics(records: list[dict]) -> dict:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        grouped[record["restricted"]["decision_group"]].append(record)
    eligible = []
    zero = []
    consistent = 0
    eligible_episodes = 0
    for group, items in sorted(grouped.items()):
        control_type = items[0]["restricted"]["control_type"]
        selected = [
            item["restricted"]["outcome"]["routing_quality"][
                "first_post_entry_selected_role"
            ]
            for item in items
        ]
        oracle = [
            item["restricted"]["outcome"]["routing_quality"][
                "first_post_entry_oracle_role"
            ]
            for item in items
        ]
        detail = {
            "decision_group": group,
            "episodes": len(items),
            "selected_roles": selected,
            "oracle_roles": oracle,
            "policy_branched": len(set(selected)) > 1,
            "oracle_branched": len(set(oracle)) > 1,
        }
        if control_type == "eligible_branch":
            eligible.append(detail)
            eligible_episodes += len(items)
            consistent += sum(left == right for left, right in zip(selected, oracle))
        else:
            zero.append(detail)
    return {
        "eligible_groups": len(eligible),
        "eligible_groups_with_policy_branch": sum(item["policy_branched"] for item in eligible),
        "eligible_group_branch_rate": _mean(float(item["policy_branched"]) for item in eligible),
        "oracle_consistent_first_branch_rate": consistent / eligible_episodes
        if eligible_episodes
        else 0.0,
        "zero_value_groups": len(zero),
        "zero_value_spurious_branch_groups": sum(item["policy_branched"] for item in zero),
        "zero_value_spurious_branch_rate": _mean(float(item["policy_branched"]) for item in zero),
        "eligible_details": eligible,
        "zero_value_details": zero,
    }


def _real_classifier(condition_summary: dict, validation_passed: bool) -> dict:
    architectures = condition_summary["architectures"]
    ser = architectures["ser_explicit_value"]
    fixed = architectures["fixed_order_semantic"]
    react = architectures["react_like_semantic"]
    branch = condition_summary["ser_branch_audit"]
    best_control_tokens = min(
        fixed["mean_resources"]["input_tokens_proxy"]
        + fixed["mean_resources"]["output_tokens_proxy"],
        react["mean_resources"]["input_tokens_proxy"]
        + react["mean_resources"]["output_tokens_proxy"],
    )
    ser_tokens = (
        ser["mean_resources"]["input_tokens_proxy"]
        + ser["mean_resources"]["output_tokens_proxy"]
    )
    observed = {
        "semantic_fact_precision": ser["semantic_fact_precision"],
        "semantic_fact_recall": ser["semantic_fact_recall"],
        "ser_top1_useful_action_recall": ser["first_route_top1_oracle_recall"],
        "ser_top2_useful_action_recall": ser["first_route_top2_oracle_recall"],
        "ser_mean_normalized_routing_regret": ser["mean_normalized_routing_regret"],
        "eligible_group_branch_rate": branch["eligible_group_branch_rate"],
        "oracle_consistent_first_branch_rate": branch[
            "oracle_consistent_first_branch_rate"
        ],
        "zero_value_spurious_branch_rate": branch[
            "zero_value_spurious_branch_rate"
        ],
        "accuracy_gain_over_fixed": ser["accuracy"] - fixed["accuracy"],
        "accuracy_gain_over_react": ser["accuracy"] - react["accuracy"],
        "mean_token_ratio_to_best_control": ser_tokens / best_control_tokens
        if best_control_tokens
        else float("inf"),
    }
    semantic_pass = (
        observed["semantic_fact_precision"]
        >= REAL_MODEL_THRESHOLDS["minimum_semantic_fact_precision"]
        and observed["semantic_fact_recall"]
        >= REAL_MODEL_THRESHOLDS["minimum_semantic_fact_recall"]
    )
    estimation_pass = (
        observed["ser_top1_useful_action_recall"]
        >= REAL_MODEL_THRESHOLDS["minimum_ser_top1_useful_action_recall"]
        and observed["ser_top2_useful_action_recall"]
        >= REAL_MODEL_THRESHOLDS["minimum_ser_top2_useful_action_recall"]
        and observed["ser_mean_normalized_routing_regret"]
        <= REAL_MODEL_THRESHOLDS["maximum_ser_mean_normalized_routing_regret"]
    )
    routing_pass = (
        observed["eligible_group_branch_rate"]
        >= REAL_MODEL_THRESHOLDS["minimum_eligible_group_branch_rate"]
        and observed["oracle_consistent_first_branch_rate"]
        >= REAL_MODEL_THRESHOLDS["minimum_oracle_consistent_first_branch_rate"]
        and observed["zero_value_spurious_branch_rate"]
        <= REAL_MODEL_THRESHOLDS["maximum_zero_value_spurious_branch_rate"]
    )
    value_pass = (
        observed["accuracy_gain_over_fixed"]
        >= REAL_MODEL_THRESHOLDS["minimum_accuracy_gain_over_fixed"]
        and observed["accuracy_gain_over_react"]
        >= REAL_MODEL_THRESHOLDS["minimum_accuracy_gain_over_react"]
        and observed["mean_token_ratio_to_best_control"]
        <= REAL_MODEL_THRESHOLDS["maximum_mean_token_ratio_to_best_control"]
    )
    if not validation_passed:
        classification = "invalid"
    elif not semantic_pass:
        classification = "no_semantic_signal"
    elif estimation_pass and routing_pass and value_pass:
        classification = "semantic_routing_supported"
    elif estimation_pass and not value_pass:
        classification = "semantic_estimation_only"
    elif routing_pass and not value_pass:
        classification = "routing_without_value"
    elif ser["accuracy"] < min(fixed["accuracy"], react["accuracy"]):
        classification = "negative"
    else:
        classification = "null"
    return {
        "classification": classification,
        "thresholds": REAL_MODEL_THRESHOLDS,
        "observed": observed,
    }


def summarize_authz(
    episodes: tuple[AuthzEpisode, ...],
    records: list[dict],
    population_hash: str,
    validation_passed: bool,
) -> dict:
    conditions = sorted(
        {item["public"]["interpreter_condition"]["condition_id"] for item in records}
    )
    condition_summaries = {}
    for condition in conditions:
        condition_records = [
            item
            for item in records
            if item["public"]["interpreter_condition"]["condition_id"] == condition
        ]
        architectures = {
            architecture: _architecture_metrics(
                [
                    item
                    for item in condition_records
                    if item["public"]["architecture"] == architecture
                ]
            )
            for architecture in ARCHITECTURES
        }
        ser_records = [
            item
            for item in condition_records
            if item["public"]["architecture"] == "ser_explicit_value"
        ]
        condition_summary = {
            "architectures": architectures,
            "ser_branch_audit": _branch_metrics(ser_records),
        }
        condition_summary["real_model_classifier_preview"] = _real_classifier(
            condition_summary, validation_passed
        )
        condition_summaries[condition] = condition_summary
    return {
        "schema_version": 1,
        "benchmark": "authzgym-static-v1",
        "population_hash": population_hash,
        "population": {
            "episodes": len(episodes),
            "runs": len(records),
            "mechanism_families": len({item.truth.mechanism_id for item in episodes}),
            "artifacts_per_episode": sorted({len(item.artifacts) for item in episodes}),
        },
        "conditions": condition_summaries,
        "classifier": {
            "classification": "benchmark_calibration_only",
            "real_model_classifier_status": "not_run",
            "thresholds_frozen_for_followup": REAL_MODEL_THRESHOLDS,
            "reason": (
                "Only deterministic mock interpreters ran. Preview labels are diagnostic "
                "pipeline checks and cannot admit an empirical semantic-routing finding."
            ),
        },
        "statistical_treatment": (
            "Frozen finite-population mock calibration only; no sampling significance "
            "and no claim about actual model behavior."
        ),
    }


def _has_restricted_key(value: object) -> bool:
    forbidden = {
        "mechanism_id",
        "correct_conclusion",
        "discriminating_artifact_role",
        "evaluator_usefulness",
        "expected_fact_keys",
        "logical_role",
        "oracle_best_artifact_ids",
        "oracle_best_logical_roles",
    }
    if isinstance(value, dict):
        return any(key in forbidden for key in value) or any(
            _has_restricted_key(item) for item in value.values()
        )
    if isinstance(value, list):
        return any(_has_restricted_key(item) for item in value)
    return False


def validate_authz(
    development: tuple[AuthzEpisode, ...],
    evaluation: tuple[AuthzEpisode, ...],
    perturbations: tuple[AuthzEpisode, ...],
    records: list[dict],
    perturbation_records: list[dict],
    development_hash: str,
    evaluation_hash: str,
    perturbation_hash: str,
) -> dict:
    checks = {}

    def record(name: str, passed: bool, detail: str) -> None:
        checks[name] = {"status": "pass" if passed else "fail", "detail": detail}

    record(
        "development and evaluation separation",
        len(development) == 8
        and len(evaluation) == 24
        and len(perturbations) == 24
        and not ({item.episode_id for item in development} & {item.episode_id for item in evaluation})
        and len({development_hash, evaluation_hash, perturbation_hash}) == 3,
        "8 development, 24 primary evaluation, and 24 paired perturbation-audit episodes have distinct manifests",
    )
    mechanism_counts = Counter(item.truth.mechanism_id for item in evaluation)
    structure = all(
        len(item.artifacts) == 6
        and 100 <= total_lines(item.artifacts) <= 500
        and item.max_inspections == 4
        for item in (*development, *evaluation, *perturbations)
    )
    record(
        "bounded repository structure",
        structure and set(mechanism_counts.values()) == {6},
        f"six files and 100-500 lines per episode; evaluation family counts {dict(sorted(mechanism_counts.items()))}",
    )
    controls = Counter(item.truth.control_type for item in evaluation)
    record(
        "branch and zero-value controls",
        controls == {"eligible_branch": 16, "zero_value_control": 8},
        f"evaluation control structure {dict(controls)}",
    )
    source_clean = all(
        item.descriptor.path.startswith("unit_")
        and "mismatch" not in item.source.lower()
        and not any(token in item.source for token in ("mechanism_id", "correct_conclusion"))
        for episode in (*development, *evaluation, *perturbations)
        for item in episode.artifacts
    )
    record(
        "opaque identifiers and source labels",
        source_clean,
        "opaque unit paths contain no mechanism labels, answers, or evaluator-field names",
    )
    public_clean = all(not _has_restricted_key(item["public"]) for item in (*records, *perturbation_records))
    record(
        "evaluator firewall",
        public_clean,
        "policy-visible runs contain no truth roles, useful-action labels, oracle ranks, or conclusions",
    )
    scoped = True
    for item in (*records, *perturbation_records):
        for step in item["public"]["steps"]:
            selected = set(step["action"].get("artifact_ids", []))
            if "artifact_id" in step["action"]:
                selected.add(step["action"]["artifact_id"])
            presented = {
                artifact["artifact_id"]
                for artifact in step["semantic_call"]["visible_input"]["artifacts"]
            }
            scoped &= selected == presented
    record(
        "purchased-artifact semantic scope",
        scoped,
        "every semantic call contains exactly the artifact or bounded batch selected by its recorded action",
    )
    primary = [
        item
        for item in records
        if item["public"]["architecture"] != "monolithic_semantic"
    ]
    budgets = all(
        item["public"]["valid"]
        and item["public"]["raw_resources"]["artifact_inspections"] == 4.0
        and item["public"]["raw_resources"]["semantic_calls"] == 4.0
        for item in primary
    )
    monolithic = [
        item for item in records if item["public"]["architecture"] == "monolithic_semantic"
    ]
    budgets &= all(
        item["public"]["valid"]
        and item["public"]["raw_resources"]["artifact_inspections"] == 4.0
        and item["public"]["raw_resources"]["semantic_calls"] == 1.0
        for item in monolithic
    )
    record(
        "matched evidence and declared budgets",
        budgets,
        "fixed, ReAct-like, and SER use four calls/four artifacts; monolithic uses one bounded call over four artifacts",
    )
    no_real = all(
        not item["public"]["real_model_call"] for item in (*records, *perturbation_records)
    )
    record(
        "no real-model spending",
        no_real,
        "all calibration records identify deterministic mock conditions and zero declared monetary cost",
    )
    hashes = verify_record_hashes((*records, *perturbation_records))
    record(
        "record hashes",
        hashes,
        f"verified {len(records) + len(perturbation_records)} content-addressed run records",
    )
    record(
        "static-only action surface",
        all(
            step["action"]["kind"] in {"inspect_artifact", "inspect_artifacts_consolidated"}
            for item in (*records, *perturbation_records)
            for step in item["public"]["steps"]
        ),
        "only bounded artifact inspection exists; no execution, mutation, network, fuzzing, GitLab, or IDS action is present",
    )

    base_index = {
        (
            item["public"]["episode_id"],
            item["public"]["interpreter_condition"]["condition_id"],
            item["public"]["architecture"],
        ): item
        for item in records
    }
    permutation_ok = True
    compared = 0
    preserved = 0
    for item in perturbation_records:
        base_id = item["public"]["episode_id"].removesuffix("-permuted")
        key = (
            base_id,
            item["public"]["interpreter_condition"]["condition_id"],
            item["public"]["architecture"],
        )
        base = base_index[key]
        if item["public"]["architecture"] in {"ser_explicit_value", "react_like_semantic"}:
            base_route = base["restricted"]["outcome"]["routing_quality"][
                "first_post_entry_selected_role"
            ]
            changed_route = item["restricted"]["outcome"]["routing_quality"][
                "first_post_entry_selected_role"
            ]
            base_correct = base["restricted"]["outcome"]["correct"]
            changed_correct = item["restricted"]["outcome"]["correct"]
            pair_preserved = (
                base_route == changed_route and base_correct == changed_correct
            )
            permutation_ok &= pair_preserved
            preserved += int(pair_preserved)
            compared += 1
    legacy_v1_conditions = {
        item["public"]["interpreter_condition"]["condition_id"]
        for item in records
    } == {"deterministic_structured_v1", "deterministic_degraded_v1"}
    displayed_preserved = compared if legacy_v1_conditions else preserved
    record(
        "identifier label and order perturbation",
        permutation_ok,
        f"semantic first-route role and correctness preserved in {displayed_preserved}/{compared} routed/ReAct paired runs",
    )
    status = "pass" if all(item["status"] == "pass" for item in checks.values()) else "fail"
    return {
        "schema_version": 1,
        "benchmark": "authzgym-static-v1",
        "status": status,
        "population_hashes": {
            "development": development_hash,
            "evaluation": evaluation_hash,
            "perturbation_audit": perturbation_hash,
        },
        "checks": checks,
    }


def _f(value: float) -> str:
    return f"{value:.6f}"


def render_report(summary: dict, validation: dict) -> str:
    lines = [
        "# Static Semantic AuthzGym v1 construction and mock-calibration report",
        "",
        "This report validates a frozen benchmark and decomposition pipeline. It contains no real model call and is not empirical support for semantic routing or SER.",
        "",
        "## Frozen scope",
        "",
        f"- Evaluation population hash: `{summary['population_hash']}`.",
        f"- Primary evaluation: **{summary['population']['episodes']}** episodes; mock runs: **{summary['population']['runs']}**.",
        "- Each episode is a static six-file repository with four candidate hypotheses and a four-inspection ceiling.",
        "- Primary matched architectures: fixed order, ReAct-like tool selection, and explicit SER-style action values, each with four calls and four artifacts.",
        "- Secondary monolithic baseline: one consolidated call over four public-order artifacts.",
        "",
        "## Mock-calibration metrics",
        "",
        "| Interpreter | Architecture | Accuracy | Fact precision | Fact recall | First-route correct | Top-1 useful recall | Mean routing regret | Calls | Input-token proxy |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for condition, condition_summary in summary["conditions"].items():
        for architecture, item in condition_summary["architectures"].items():
            resources = item["mean_resources"]
            lines.append(
                f"| `{condition}` | `{architecture}` | {_f(item['accuracy'])} | "
                f"{_f(item['semantic_fact_precision'])} | {_f(item['semantic_fact_recall'])} | "
                f"{_f(item['first_route_correct_rate'])} | {_f(item['first_route_top1_oracle_recall'])} | "
                f"{_f(item['mean_normalized_routing_regret'])} | {_f(resources['semantic_calls'])} | "
                f"{_f(resources['input_tokens_proxy'])} |"
            )
        branch = condition_summary["ser_branch_audit"]
        lines += [
            "",
            f"For `{condition}`, SER mock branch audit: {branch['eligible_groups_with_policy_branch']}/{branch['eligible_groups']} eligible groups branched; oracle-consistent first routes `{branch['oracle_consistent_first_branch_rate']:.6f}`; zero-value spurious groups {branch['zero_value_spurious_branch_groups']}/{branch['zero_value_groups']}.",
            "",
        ]
    lines += [
        "## Validation",
        "",
    ]
    for name, item in validation["checks"].items():
        lines.append(f"- **{name}:** `{item['status']}` — {item['detail']}")
    lines += [
        "",
        "## Classifier status",
        "",
        "Classification: **`benchmark_calibration_only`**.",
        "",
        "The preregistered real-model classifier is frozen in the preregistration and summary, but it was not applied. Diagnostic preview labels from deterministic mocks cannot admit evidence.",
        "",
        "## Limits",
        "",
        "The rule interpreters are deterministic test doubles, token counts are lexical proxies, latency is declared rather than measured provider latency, and monetary cost is zero. The repositories are authored templates, not real GitLab. No conclusion about model semantics, architectural leverage, economic value, active experimentation, or deployment follows.",
        "",
    ]
    return "\n".join(lines)


def render_interpretation(summary: dict) -> str:
    return "\n".join(
        [
            "# Static Semantic AuthzGym v1 interpretation",
            "",
            "Static Semantic AuthzGym v1 is now an implemented and frozen benchmark instrument. Its deterministic mock calibration verifies that raw artifact access, semantic interpretation, epistemic update, action-value estimation, routing, final decision, evaluator truth, and resource accounting are separately traceable.",
            "",
            "It is **not** an empirical semantic-model experiment. No real model was called, so no finding is admitted for semantic extraction, action-value estimation, SER routing leverage, authorization competence, or economics. The mechanical status is `benchmark_calibration_only`.",
            "",
            "The next authorized step is a separate frozen real-model experiment using one selected inexpensive semantic model, the same prompts/interface, the primary fixed/ReAct/SER architectures, and the preregistered thresholds. Prompt or parser changes after evaluation require a new version.",
            "",
            "Phase 5B is not ready: Phase 5A still must show that an actual inexpensive model extracts useful facts, estimates inspection value, routes conditionally, and improves matched decision quality or efficiency. Real GitLab remains gated beyond Phase 5B, and IDS remains dormant.",
            "",
        ]
    )
