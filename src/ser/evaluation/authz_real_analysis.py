"""Analysis and integrity checks for the frozen AuthzGym real-model run."""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from statistics import fmean
from typing import Iterable, Mapping

from ser.authzgym.interpreters import _relation_tag
from ser.authzgym.model import AuthzEpisode
from ser.authzgym.policies import ARCHITECTURES
from ser.core.types import canonical_json

from .artifacts import verify_record_hash
from .authz_analysis import REAL_MODEL_THRESHOLDS, _branch_metrics


FACT_RELATION_DIRECTIONS = {
    "alternate-entry": ("ownership_path", 1),
    "direct-only-membership": ("membership_path", 1),
    "inherited-membership-included": ("membership_path", -1),
    "role-fallback": ("role_path", 1),
    "role-map-transform": ("role_path", 1),
    "role-preserved": ("role_path", -1),
    "missing-token-scope": ("context_path", 1),
    "missing-feature-context": ("context_path", 1),
    "token-scope-forwarded": ("context_path", -1),
    "feature-context-forwarded": ("context_path", -1),
    "sensitive-without-owner-check": ("ownership_path", 1),
    "ownership-compared": ("ownership_path", -1),
    "weak-ownership-audit": ("ownership_path", 1),
    "weak-membership-audit": ("membership_path", 1),
    "weak-role-audit": ("role_path", 1),
    "weak-context-audit": ("context_path", 1),
}


CLASSIFIER_THRESHOLDS = {
    **REAL_MODEL_THRESHOLDS,
    "maximum_malformed_response_rate": 0.05,
    "minimum_effect_direction_precision": 0.60,
    "minimum_effect_direction_recall": 0.50,
    "minimum_material_routing_regret_reduction_vs_react": 0.10,
    "minimum_material_useful_acquisition_gain_vs_react": 0.10,
    "minimum_material_cost_reduction_vs_react": 0.10,
    "maximum_acceptable_accuracy_degradation_vs_react": 1.0 / 24.0,
    "maximum_acceptable_cost_ratio_vs_react": 1.25,
    "minimum_perturbation_pair_stability": 0.90,
}


def _mean(values: Iterable[float]) -> float:
    values = tuple(values)
    return fmean(values) if values else 0.0


def _ratio(numerator: float, denominator: float) -> float | None:
    return numerator / denominator if denominator else None


def _sign(value: float) -> int:
    return 1 if value > 0 else -1 if value < 0 else 0


def _selected_ids(step: dict) -> tuple[str, ...]:
    action = step["action"]
    if "artifact_id" in action:
        return (action["artifact_id"],)
    return tuple(action.get("artifact_ids", ()))


def _expected_references(
    episode: AuthzEpisode, artifact_ids: tuple[str, ...]
) -> set[tuple[str, str]]:
    symbol_index = {
        symbol: artifact.descriptor.artifact_id
        for artifact in episode.artifacts
        for symbol in artifact.descriptor.exported_symbols
    }
    expected: set[tuple[str, str]] = set()
    selected = set(artifact_ids)
    for artifact_id in artifact_ids:
        source = episode.artifact(artifact_id).source
        for line in source.splitlines():
            for symbol, target_id in symbol_index.items():
                if target_id in selected:
                    continue
                if re.search(rf"\b{re.escape(symbol)}\s*\(", line):
                    expected.add((symbol, _relation_tag(line)))
    return expected


def _semantic_relation_counts(
    records: list[dict], episode_index: Mapping[str, AuthzEpisode]
) -> dict:
    effect_expected: set[tuple[str, int, str, int]] = set()
    effect_predicted: set[tuple[str, int, str, int]] = set()
    reference_expected: set[tuple[str, int, str, str]] = set()
    reference_predicted: set[tuple[str, int, str, str]] = set()
    for record in records:
        run_id = record["public"]["run_id"]
        episode = episode_index[record["public"]["episode_id"]]
        relation_to_hypothesis = {
            tag: candidate.hypothesis_id
            for candidate in episode.candidates
            for tag in candidate.relation_tags
        }
        for step in record["public"]["steps"]:
            step_number = int(step["step"])
            artifact_ids = _selected_ids(step)
            expected_by_hypothesis: dict[str, int] = {}
            for artifact_id in artifact_ids:
                for key in episode.artifact(artifact_id).expected_fact_keys:
                    relation_direction = FACT_RELATION_DIRECTIONS.get(key)
                    if relation_direction is None:
                        continue
                    relation, direction = relation_direction
                    hypothesis_id = relation_to_hypothesis.get(relation)
                    if hypothesis_id is not None:
                        expected_by_hypothesis[hypothesis_id] = direction
            for hypothesis_id, direction in expected_by_hypothesis.items():
                effect_expected.add((run_id, step_number, hypothesis_id, direction))
            effects = step["semantic_call"]["parsed_semantic_observation"][
                "hypothesis_effects"
            ]
            for hypothesis_id, value in effects.items():
                direction = _sign(float(value))
                if direction:
                    effect_predicted.add(
                        (run_id, step_number, hypothesis_id, direction)
                    )
            for symbol, relation in _expected_references(episode, artifact_ids):
                reference_expected.add((run_id, step_number, symbol, relation))
            references = step["semantic_call"]["parsed_semantic_observation"][
                "unresolved_references"
            ]
            for item in references:
                reference_predicted.add(
                    (run_id, step_number, item["symbol"], item["relation_tag"])
                )
    effect_tp = len(effect_expected & effect_predicted)
    reference_tp = len(reference_expected & reference_predicted)
    return {
        "hypothesis_effect_direction": {
            "expected": len(effect_expected),
            "predicted": len(effect_predicted),
            "true_positive": effect_tp,
            "precision": _ratio(effect_tp, len(effect_predicted)) or 0.0,
            "recall": _ratio(effect_tp, len(effect_expected)) or 0.0,
        },
        "unresolved_relation": {
            "expected": len(reference_expected),
            "predicted": len(reference_predicted),
            "true_positive": reference_tp,
            "precision": _ratio(reference_tp, len(reference_predicted)) or 0.0,
            "recall": _ratio(reference_tp, len(reference_expected)) or 0.0,
        },
    }


def _architecture_metrics(
    records: list[dict], episode_index: Mapping[str, AuthzEpisode]
) -> dict:
    correct = [bool(item["restricted"]["outcome"]["correct"]) for item in records]
    semantic = [item["restricted"]["outcome"]["semantic_quality"] for item in records]
    expected = sum(item["expected_facts"] for item in semantic)
    extracted = sum(item["extracted_facts"] for item in semantic)
    true_positive = sum(item["true_positive_facts"] for item in semantic)
    resources = [item["public"]["raw_resources"] for item in records]
    audits = []
    for item in records:
        restricted_audits = item["restricted"]["outcome"]["routing_quality"][
            "post_entry_steps"
        ]
        post_entry_steps = item["public"]["steps"][1:]
        for audit, step in zip(restricted_audits, post_entry_steps):
            audits.append(
                {
                    **audit,
                    "estimated_action_values": step["action"].get(
                        "estimated_action_values"
                    ),
                }
            )
    first_audits = [
        item["restricted"]["outcome"]["routing_quality"]["post_entry_steps"][0]
        for item in records
        if item["restricted"]["outcome"]["routing_quality"]["post_entry_steps"]
    ]
    ranks = []
    useful = 0
    for audit in audits:
        values = audit.get("estimated_action_values")
        if values:
            ranking = sorted(values, key=lambda key: (values[key], key), reverse=True)
            oracle = set(audit["oracle_best_artifact_ids"])
            rank = next(
                (index for index, artifact_id in enumerate(ranking, 1) if artifact_id in oracle),
                len(ranking) + 1,
            )
            ranks.append(rank)
        useful += int(audit["selected_usefulness"] > 0.0)
    total_cost = sum(float(item["monetary_cost_usd"]) for item in resources)
    total_correct = sum(correct)
    relation = _semantic_relation_counts(records, episode_index)
    total_provider_calls = sum(int(item["provider_calls"]) for item in resources)
    valid_semantic_calls = sum(len(item["public"]["steps"]) for item in records)
    failure_counts = Counter(
        failure
        for item in records
        for failure in item["restricted"]["outcome"]["failure_layers"]
    )
    return {
        "runs": len(records),
        "valid_runs": sum(bool(item["public"]["valid"]) for item in records),
        "invalid_runs": sum(not bool(item["public"]["valid"]) for item in records),
        "correct_episodes": total_correct,
        "accuracy": _mean(float(item) for item in correct),
        "semantic_fact_precision": _ratio(true_positive, extracted) or 0.0,
        "semantic_fact_recall": _ratio(true_positive, expected) or 0.0,
        "semantic_relation_quality": relation,
        "valid_model_responses": valid_semantic_calls,
        "invalid_model_responses": total_provider_calls - valid_semantic_calls,
        "malformed_response_rate": _ratio(
            total_provider_calls - valid_semantic_calls, total_provider_calls
        )
        or 0.0,
        "first_route_correct_rate": _mean(
            float(item["selected_artifact_id"] in item["oracle_best_artifact_ids"])
            for item in first_audits
        ),
        "all_post_entry_route_correct_rate": _mean(
            float(item["selected_artifact_id"] in item["oracle_best_artifact_ids"])
            for item in audits
        ),
        "useful_evidence_acquisitions": useful,
        "useful_evidence_acquisition_rate": _ratio(useful, len(audits)) or 0.0,
        "action_value_top1_recall": _mean(
            float(item["estimated_top_one_is_oracle"])
            for item in audits
            if item.get("estimated_action_values")
        ),
        "action_value_top2_recall": _mean(
            float(item["estimated_top_two_contains_oracle"])
            for item in audits
            if item.get("estimated_action_values")
        ),
        "action_value_mean_reciprocal_rank": _mean(1.0 / item for item in ranks),
        "mean_normalized_routing_regret": _mean(
            float(item["normalized_routing_regret"]) for item in audits
        ),
        "mean_first_routing_regret": _mean(
            float(item["normalized_routing_regret"]) for item in first_audits
        ),
        "resources": {
            "totals": {
                name: sum(float(item[name]) for item in resources)
                for name in resources[0]
            },
            "means_per_episode": {
                name: _mean(float(item[name]) for item in resources)
                for name in resources[0]
            },
            "cost_per_episode_usd": _ratio(total_cost, len(records)),
            "cost_per_correct_episode_usd": _ratio(total_cost, total_correct),
            "correct_episodes_per_dollar": _ratio(total_correct, total_cost),
            "useful_evidence_acquisitions_per_dollar": _ratio(useful, total_cost),
        },
        "failure_layers": dict(sorted(failure_counts.items())),
    }


def _paired_comparison(
    left_records: list[dict], right_records: list[dict], left_name: str, right_name: str
) -> dict:
    right = {item["public"]["episode_id"]: item for item in right_records}
    rows = []
    for item in sorted(left_records, key=lambda value: value["public"]["episode_id"]):
        peer = right[item["public"]["episode_id"]]
        left_correct = bool(item["restricted"]["outcome"]["correct"])
        right_correct = bool(peer["restricted"]["outcome"]["correct"])
        rows.append(
            {
                "episode_id": item["public"]["episode_id"],
                f"{left_name}_correct": left_correct,
                f"{right_name}_correct": right_correct,
                "correctness_difference": int(left_correct) - int(right_correct),
                "cost_difference_usd": item["public"]["raw_resources"][
                    "monetary_cost_usd"
                ]
                - peer["public"]["raw_resources"]["monetary_cost_usd"],
            }
        )
    return {
        "episodes": len(rows),
        f"{left_name}_wins": sum(item["correctness_difference"] > 0 for item in rows),
        f"{right_name}_wins": sum(item["correctness_difference"] < 0 for item in rows),
        "ties": sum(item["correctness_difference"] == 0 for item in rows),
        "mean_accuracy_difference": _mean(
            float(item["correctness_difference"]) for item in rows
        ),
        "mean_cost_difference_usd": _mean(float(item["cost_difference_usd"]) for item in rows),
        "per_episode": rows,
    }


def _role_route(record: dict, episode: AuthzEpisode) -> tuple[str, ...]:
    role_by_id = {
        item.descriptor.artifact_id: item.logical_role for item in episode.artifacts
    }
    return tuple(
        role_by_id[item]
        for step in record["public"]["steps"]
        for item in _selected_ids(step)
    )


def perturbation_stability(
    evaluation_records: list[dict],
    perturbation_records: list[dict],
    evaluation_index: Mapping[str, AuthzEpisode],
    perturbation_index: Mapping[str, AuthzEpisode],
) -> dict:
    base = {
        (item["public"]["episode_id"], item["public"]["architecture"]): item
        for item in evaluation_records
    }
    by_architecture: dict[str, list[dict]] = defaultdict(list)
    for changed in perturbation_records:
        changed_id = changed["public"]["episode_id"]
        base_id = changed_id.removesuffix("-permuted")
        architecture = changed["public"]["architecture"]
        original = base[(base_id, architecture)]
        original_facts = {
            key
            for step in original["public"]["steps"]
            for key in step["semantic_call"]["parsed_semantic_observation"]["fact_keys"]
        }
        changed_facts = {
            key
            for step in changed["public"]["steps"]
            for key in step["semantic_call"]["parsed_semantic_observation"]["fact_keys"]
        }
        row = {
            "base_episode_id": base_id,
            "perturbed_episode_id": changed_id,
            "correctness_preserved": original["restricted"]["outcome"]["correct"]
            == changed["restricted"]["outcome"]["correct"],
            "logical_route_preserved": _role_route(
                original, evaluation_index[base_id]
            )
            == _role_route(changed, perturbation_index[changed_id]),
            "semantic_fact_set_preserved": original_facts == changed_facts,
        }
        row["jointly_stable"] = all(row[key] for key in row if key.endswith("preserved"))
        by_architecture[architecture].append(row)
    return {
        architecture: {
            "pairs": len(rows),
            "correctness_stability": _mean(
                float(item["correctness_preserved"]) for item in rows
            ),
            "logical_route_stability": _mean(
                float(item["logical_route_preserved"]) for item in rows
            ),
            "semantic_fact_set_stability": _mean(
                float(item["semantic_fact_set_preserved"]) for item in rows
            ),
            "joint_stability": _mean(float(item["jointly_stable"]) for item in rows),
            "per_pair": rows,
        }
        for architecture, rows in sorted(by_architecture.items())
    }


def _classifier(summary: dict, validation: dict) -> dict:
    arch = summary["evaluation"]["architectures"]
    ser = arch["ser_explicit_value"]
    react = arch["react_like_semantic"]
    fixed = arch["fixed_order_semantic"]
    branch = summary["evaluation"]["ser_branch_audit"]
    effect = ser["semantic_relation_quality"]["hypothesis_effect_direction"]
    perturb = summary["perturbation_stability"]
    minimum_stability = min(
        perturb[item]["joint_stability"]
        for item in ("ser_explicit_value", "react_like_semantic")
    )
    observed = {
        "semantic_fact_precision": ser["semantic_fact_precision"],
        "semantic_fact_recall": ser["semantic_fact_recall"],
        "effect_direction_precision": effect["precision"],
        "effect_direction_recall": effect["recall"],
        "malformed_response_rate": ser["malformed_response_rate"],
        "ser_top1_useful_action_recall": ser["action_value_top1_recall"],
        "ser_top2_useful_action_recall": ser["action_value_top2_recall"],
        "ser_mean_normalized_routing_regret": ser[
            "mean_normalized_routing_regret"
        ],
        "eligible_group_branch_rate": branch["eligible_group_branch_rate"],
        "oracle_consistent_first_branch_rate": branch[
            "oracle_consistent_first_branch_rate"
        ],
        "zero_value_spurious_branch_rate": branch[
            "zero_value_spurious_branch_rate"
        ],
        "accuracy_gain_over_fixed": ser["accuracy"] - fixed["accuracy"],
        "accuracy_gain_over_react": ser["accuracy"] - react["accuracy"],
        "routing_regret_reduction_vs_react": react[
            "mean_normalized_routing_regret"
        ]
        - ser["mean_normalized_routing_regret"],
        "useful_acquisition_gain_vs_react": ser[
            "useful_evidence_acquisition_rate"
        ]
        - react["useful_evidence_acquisition_rate"],
        "cost_reduction_vs_react": 1.0
        - ser["resources"]["totals"]["monetary_cost_usd"]
        / react["resources"]["totals"]["monetary_cost_usd"],
        "cost_ratio_vs_react": ser["resources"]["totals"]["monetary_cost_usd"]
        / react["resources"]["totals"]["monetary_cost_usd"],
        "minimum_perturbation_joint_stability": minimum_stability,
    }
    semantic_pass = (
        observed["semantic_fact_precision"]
        >= CLASSIFIER_THRESHOLDS["minimum_semantic_fact_precision"]
        and observed["semantic_fact_recall"]
        >= CLASSIFIER_THRESHOLDS["minimum_semantic_fact_recall"]
        and observed["effect_direction_precision"]
        >= CLASSIFIER_THRESHOLDS["minimum_effect_direction_precision"]
        and observed["effect_direction_recall"]
        >= CLASSIFIER_THRESHOLDS["minimum_effect_direction_recall"]
        and observed["malformed_response_rate"]
        <= CLASSIFIER_THRESHOLDS["maximum_malformed_response_rate"]
    )
    estimation_pass = (
        observed["ser_top1_useful_action_recall"]
        >= CLASSIFIER_THRESHOLDS["minimum_ser_top1_useful_action_recall"]
        and observed["ser_top2_useful_action_recall"]
        >= CLASSIFIER_THRESHOLDS["minimum_ser_top2_useful_action_recall"]
        and observed["ser_mean_normalized_routing_regret"]
        <= CLASSIFIER_THRESHOLDS["maximum_ser_mean_normalized_routing_regret"]
    )
    routing_pass = (
        observed["eligible_group_branch_rate"]
        >= CLASSIFIER_THRESHOLDS["minimum_eligible_group_branch_rate"]
        and observed["oracle_consistent_first_branch_rate"]
        >= CLASSIFIER_THRESHOLDS["minimum_oracle_consistent_first_branch_rate"]
        and observed["zero_value_spurious_branch_rate"]
        <= CLASSIFIER_THRESHOLDS["maximum_zero_value_spurious_branch_rate"]
    )
    no_unacceptable_degradation = (
        observed["accuracy_gain_over_react"]
        >= -CLASSIFIER_THRESHOLDS[
            "maximum_acceptable_accuracy_degradation_vs_react"
        ]
        and observed["cost_ratio_vs_react"]
        <= CLASSIFIER_THRESHOLDS["maximum_acceptable_cost_ratio_vs_react"]
    )
    material_gain = (
        observed["accuracy_gain_over_react"]
        >= CLASSIFIER_THRESHOLDS["minimum_accuracy_gain_over_react"]
        or observed["routing_regret_reduction_vs_react"]
        >= CLASSIFIER_THRESHOLDS[
            "minimum_material_routing_regret_reduction_vs_react"
        ]
        or observed["useful_acquisition_gain_vs_react"]
        >= CLASSIFIER_THRESHOLDS[
            "minimum_material_useful_acquisition_gain_vs_react"
        ]
        or observed["cost_reduction_vs_react"]
        >= CLASSIFIER_THRESHOLDS["minimum_material_cost_reduction_vs_react"]
    )
    fixed_valid = fixed["valid_runs"] == fixed["runs"]
    integrity_pass = (
        validation["status"] == "pass"
        and observed["minimum_perturbation_joint_stability"]
        >= CLASSIFIER_THRESHOLDS["minimum_perturbation_pair_stability"]
        and fixed_valid
    )
    materially_worse = (
        observed["accuracy_gain_over_react"] < -1.0 / 24.0
        or observed["cost_ratio_vs_react"]
        > CLASSIFIER_THRESHOLDS["maximum_acceptable_cost_ratio_vs_react"]
    )
    if not integrity_pass:
        classification = "invalid"
    elif not semantic_pass:
        classification = "no_semantic_signal"
    elif not estimation_pass:
        classification = "semantic_signal_only"
    elif routing_pass and material_gain and no_unacceptable_degradation:
        classification = "semantic_routing_supported"
    elif materially_worse:
        classification = "negative"
    elif routing_pass:
        classification = "routing_without_value"
    else:
        classification = "semantic_estimation_supported_no_architecture_leverage"
    return {
        "classification": classification,
        "thresholds": CLASSIFIER_THRESHOLDS,
        "observed": observed,
        "gates": {
            "integrity_pass": integrity_pass,
            "semantic_pass": semantic_pass,
            "estimation_pass": estimation_pass,
            "routing_pass": routing_pass,
            "material_gain": material_gain,
            "no_unacceptable_degradation": no_unacceptable_degradation,
            "fixed_comparison_valid": fixed_valid,
        },
    }


def summarize_real(
    evaluation_episodes: tuple[AuthzEpisode, ...],
    perturbation_episodes: tuple[AuthzEpisode, ...],
    evaluation_records: list[dict],
    perturbation_records: list[dict],
    response_records: list[dict],
    validation: dict,
) -> dict:
    eval_index = {item.episode_id: item for item in evaluation_episodes}
    perturb_index = {item.episode_id: item for item in perturbation_episodes}
    architectures = {
        architecture: _architecture_metrics(
            [
                item
                for item in evaluation_records
                if item["public"]["architecture"] == architecture
            ],
            eval_index,
        )
        for architecture in ARCHITECTURES
    }
    perturb_architectures = {
        architecture: _architecture_metrics(
            [
                item
                for item in perturbation_records
                if item["public"]["architecture"] == architecture
            ],
            perturb_index,
        )
        for architecture in ARCHITECTURES
    }
    ser_eval = [
        item
        for item in evaluation_records
        if item["public"]["architecture"] == "ser_explicit_value"
    ]
    summary = {
        "schema_version": 1,
        "benchmark": "authzgym-static-realmodel-v1",
        "population": {
            "evaluation_episodes": len(evaluation_episodes),
            "perturbation_episodes": len(perturbation_episodes),
            "evaluation_runs": len(evaluation_records),
            "perturbation_runs": len(perturbation_records),
            "provider_response_attempts": len(response_records),
        },
        "evaluation": {
            "architectures": architectures,
            "ser_branch_audit": _branch_metrics(ser_eval),
            "paired": {
                "ser_vs_react": _paired_comparison(
                    ser_eval,
                    [
                        item
                        for item in evaluation_records
                        if item["public"]["architecture"]
                        == "react_like_semantic"
                    ],
                    "ser",
                    "react",
                ),
                "ser_vs_fixed": _paired_comparison(
                    ser_eval,
                    [
                        item
                        for item in evaluation_records
                        if item["public"]["architecture"]
                        == "fixed_order_semantic"
                    ],
                    "ser",
                    "fixed",
                ),
            },
        },
        "perturbation": {"architectures": perturb_architectures},
        "perturbation_stability": perturbation_stability(
            evaluation_records,
            perturbation_records,
            eval_index,
            perturb_index,
        ),
        "provider_accounting": {
            "total_calls": sum(
                int(item["public"]["raw_resources"]["provider_calls"])
                for item in (*evaluation_records, *perturbation_records)
            ),
            "total_input_tokens": sum(
                int(item["public"]["raw_resources"]["input_tokens"])
                for item in (*evaluation_records, *perturbation_records)
            ),
            "total_output_tokens": sum(
                int(item["public"]["raw_resources"]["output_tokens"])
                for item in (*evaluation_records, *perturbation_records)
            ),
            "total_cached_input_tokens": sum(
                int(item["public"]["raw_resources"]["cached_input_tokens"])
                for item in (*evaluation_records, *perturbation_records)
            ),
            "total_latency_ms": sum(
                float(item["public"]["raw_resources"]["latency_ms"])
                for item in (*evaluation_records, *perturbation_records)
            ),
            "total_cost_usd": sum(
                float(item["public"]["raw_resources"]["monetary_cost_usd"])
                for item in (*evaluation_records, *perturbation_records)
            ),
        },
        "statistical_treatment": (
            "Descriptive paired results over the frozen finite population of 24 "
            "episodes; no population-level superiority claim."
        ),
    }
    summary["classifier"] = _classifier(summary, validation)
    return summary


def validate_real(
    evaluation_episodes: tuple[AuthzEpisode, ...],
    perturbation_episodes: tuple[AuthzEpisode, ...],
    evaluation_records: list[dict],
    perturbation_records: list[dict],
    response_records: list[dict],
    expected_hashes: Mapping[str, str],
    observed_hashes: Mapping[str, str],
    hard_spend_ceiling_usd: float,
    development_cost_usd: float,
) -> dict:
    checks: dict[str, dict] = {}

    def add(name: str, passed: bool, detail: str) -> None:
        checks[name] = {"status": "pass" if passed else "fail", "detail": detail}

    add(
        "frozen input hashes",
        dict(expected_hashes) == dict(observed_hashes),
        "all preregistration, prompt, schema, model-config, and v1.1 population hashes match the pre-run manifest",
    )
    add(
        "complete frozen populations",
        len(evaluation_episodes) == 24
        and len(perturbation_episodes) == 24
        and len(evaluation_records) == 24 * len(ARCHITECTURES)
        and len(perturbation_records) == 24 * len(ARCHITECTURES),
        f"evaluation records={len(evaluation_records)}; perturbation records={len(perturbation_records)}",
    )
    all_records = [*evaluation_records, *perturbation_records]
    add(
        "record hashes",
        all(verify_record_hash(item) for item in all_records),
        f"verified {len(all_records)} content-addressed run records",
    )
    response_hashes_valid = all(
        hashlib.sha256(item["raw_response_body"].encode("utf-8")).hexdigest()
        == item["raw_response_sha256"]
        and verify_record_hash(item)
        for item in response_records
    )
    add(
        "provider response hashes",
        response_hashes_valid,
        f"verified {len(response_records)} locally stored raw provider-response attempts",
    )
    model_ids = {
        item["public"]["interpreter_condition"]["model_identifier"]
        for item in all_records
    }
    add(
        "single frozen semantic model",
        len(model_ids) == 1 and all(item["public"]["real_model_call"] for item in all_records),
        f"model identifiers={sorted(model_ids)}",
    )
    scope_ok = True
    no_truth = True
    for record in all_records:
        for step in record["public"]["steps"]:
            selected = set(_selected_ids(step))
            visible = step["semantic_call"]["visible_input"]
            presented = {
                item["artifact_id"] for item in visible["purchased_artifacts"]
            }
            scope_ok &= selected == presented
            rendered = canonical_json(visible)
            no_truth &= not any(
                key in rendered
                for key in (
                    "mechanism_id",
                    "correct_conclusion",
                    "discriminating_artifact_role",
                    "evaluator_usefulness",
                    "expected_fact_keys",
                    "logical_role",
                )
            )
    add(
        "purchased evidence scope",
        scope_ok and no_truth,
        "each call contains exactly purchased source plus public inventory/state and no evaluator-only fields",
    )
    complete_valid = all(item["public"]["valid"] for item in all_records)
    add(
        "provider schema and run validity",
        complete_valid,
        f"valid runs={sum(item['public']['valid'] for item in all_records)}/{len(all_records)}",
    )
    frozen_cost = sum(
        float(item["public"]["raw_resources"]["monetary_cost_usd"])
        for item in all_records
    )
    total_cost = development_cost_usd + frozen_cost
    add(
        "hard provider spend ceiling",
        total_cost < hard_spend_ceiling_usd <= 5.0,
        f"development+frozen accounted cost=${total_cost:.9f} < ${hard_spend_ceiling_usd:.2f}",
    )
    action_surface = all(
        step["action"]["kind"]
        in {"inspect_artifact", "inspect_artifacts_consolidated"}
        for item in all_records
        for step in item["public"]["steps"]
    )
    add(
        "static-only action surface",
        action_surface,
        "only bounded static artifact inspection occurred",
    )
    status = "pass" if all(item["status"] == "pass" for item in checks.values()) else "fail"
    return {
        "schema_version": 1,
        "benchmark": "authzgym-static-realmodel-v1",
        "status": status,
        "checks": checks,
    }


def render_report(summary: dict, validation: dict, development: dict) -> str:
    lines = [
        "# Static Semantic AuthzGym real-model v1 report",
        "",
        f"Validation: **{validation['status']}**",
        f"Preregistered classification: **{summary['classifier']['classification']}**",
        "",
        "This is a 24-episode frozen finite-population pilot. Results are descriptive, not a population-level superiority claim.",
        "",
        "## Development and cost gate",
        "",
        f"- Development inference calls: {development['provider_calls']}",
        f"- Development input/output tokens: {development['input_tokens']}/{development['output_tokens']}",
        f"- Development accounted spend: ${development['cost_usd']:.9f}",
        f"- Projected complete worst-policy spend before evaluation: ${development['projected_complete_cost_usd']:.6f}",
        "",
        "## Frozen evaluation",
        "",
        "| Architecture | Correct | Precision | Recall | Useful acquisition | Routing regret | Input tokens | Output tokens | Calls | Cost (USD) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for architecture in ARCHITECTURES:
        item = summary["evaluation"]["architectures"][architecture]
        resources = item["resources"]["totals"]
        lines.append(
            f"| `{architecture}` | {item['correct_episodes']}/24 | {item['semantic_fact_precision']:.3f} | {item['semantic_fact_recall']:.3f} | {item['useful_evidence_acquisition_rate']:.3f} | {item['mean_normalized_routing_regret']:.3f} | {int(resources['input_tokens'])} | {int(resources['output_tokens'])} | {int(resources['provider_calls'])} | {resources['monetary_cost_usd']:.9f} |"
        )
    classifier = summary["classifier"]
    lines.extend(
        [
            "",
            "## SER action value and conditional routing",
            "",
            f"- Useful-action top-1: {classifier['observed']['ser_top1_useful_action_recall']:.3f}",
            f"- Useful-action top-2: {classifier['observed']['ser_top2_useful_action_recall']:.3f}",
            f"- Mean normalized routing regret: {classifier['observed']['ser_mean_normalized_routing_regret']:.3f}",
            f"- Eligible-group branch rate: {classifier['observed']['eligible_group_branch_rate']:.3f}",
            f"- Oracle-consistent first branch rate: {classifier['observed']['oracle_consistent_first_branch_rate']:.3f}",
            f"- Zero-value spurious branch rate: {classifier['observed']['zero_value_spurious_branch_rate']:.3f}",
            "",
            "## Paired architecture comparisons",
            "",
        ]
    )
    for name, item in summary["evaluation"]["paired"].items():
        opponent = "react" if name == "ser_vs_react" else "fixed"
        lines.append(
            f"- `{name}`: SER wins {item['ser_wins']}, {opponent} wins {item[opponent + '_wins']}, ties {item['ties']}, mean accuracy difference {item['mean_accuracy_difference']:.3f}."
        )
    lines.extend(
        [
            "",
            "## Perturbation stability",
            "",
        ]
    )
    for architecture, item in summary["perturbation_stability"].items():
        lines.append(
            f"- `{architecture}`: joint {item['joint_stability']:.3f}, correctness {item['correctness_stability']:.3f}, logical route {item['logical_route_stability']:.3f}, semantic fact set {item['semantic_fact_set_stability']:.3f}."
        )
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "The provider outputs are frozen empirical observations. Deterministic reanalysis consumes those local outputs; replay does not claim the provider will emit identical text again.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_interpretation(summary: dict) -> str:
    classification = summary["classifier"]["classification"]
    observed = summary["classifier"]["observed"]
    return (
        "# Static Semantic AuthzGym real-model v1 interpretation\n\n"
        f"The preregistered classifier returned **`{classification}`**. "
        f"The cheap model's SER-condition semantic fact precision/recall were "
        f"{observed['semantic_fact_precision']:.3f}/{observed['semantic_fact_recall']:.3f}; "
        f"SER useful-action top-1/top-2 were "
        f"{observed['ser_top1_useful_action_recall']:.3f}/"
        f"{observed['ser_top2_useful_action_recall']:.3f}.\n\n"
        "This pilot can update only the narrow static semantic-routing hypotheses. "
        "It does not validate executable authorization testing, historical-case transfer, "
        "GitLab readiness, IDS reuse, bounty economics, coupling laws, or a general SER runtime.\n"
    )
