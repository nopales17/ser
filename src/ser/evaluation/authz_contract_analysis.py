"""Analysis for the development-only AuthzGym semantic contract v1.2 stress run."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from statistics import fmean
from typing import Iterable

from ser.authzgym.model import ArtifactDescriptor, AuthzEpisode, SemanticObservation
from ser.authzgym.policies import (
    AuthzEpistemicState,
    estimate_action_values,
    update_state,
)
from ser.authzgym.semantic_contract import (
    EFFECT_VALUES,
    RELATION_BY_SLOT,
    SEMANTIC_EQUIVALENCE_VARIANTS,
    episode_from_case,
    oracle_content,
    parse_content,
)


CONTRACT_THRESHOLDS = {
    "minimum_first_attempt_schema_valid_rate": 0.99,
    "minimum_post_retry_valid_rate": 1.0,
    "maximum_finish_reason_length": 0,
    "maximum_incomplete_json": 0,
    "maximum_illegal_artifact_references": 0,
    "maximum_illegal_hypothesis_references": 0,
    "maximum_illegal_relation_references": 0,
    "maximum_manual_repairs": 0,
    "maximum_information_boundary_violations": 0,
}
SEMANTIC_THRESHOLDS = {
    "minimum_fact_precision": 0.65,
    "minimum_fact_recall": 0.50,
    "minimum_effect_precision": 0.60,
    "minimum_effect_recall": 0.50,
    "minimum_unresolved_precision": 0.60,
    "minimum_unresolved_recall": 0.50,
    "minimum_action_top1": 0.60,
    "minimum_action_top2": 0.80,
    "maximum_action_normalized_regret": 0.35,
}


def _mean(values: Iterable[float]) -> float:
    values = tuple(values)
    return fmean(values) if values else 0.0


def _micro_counts(actual: set, expected: set) -> tuple[int, int, int]:
    return len(actual & expected), len(actual), len(expected)


def _metric(counts: list[tuple[int, int, int]]) -> dict:
    true_positive = sum(item[0] for item in counts)
    predicted = sum(item[1] for item in counts)
    expected = sum(item[2] for item in counts)
    return {
        "true_positive": true_positive,
        "predicted": predicted,
        "expected": expected,
        "precision": true_positive / predicted if predicted else 0.0,
        "recall": true_positive / expected if expected else 0.0,
    }


def _state_before(case: dict, episode: AuthzEpisode) -> AuthzEpistemicState:
    state = AuthzEpistemicState.initial(episode.candidates)
    prior_slots = tuple(case["runner_control"]["prior_artifact_slots"])
    for index, prior_slot in enumerate(prior_slots):
        legal = tuple(
            slot
            for slot in range(len(episode.artifact_order))
            if slot not in set(prior_slots[: index + 1])
        )
        content = oracle_content(episode, prior_slot, legal)
        observation, _ = parse_content(content, episode, legal)
        state = update_state(
            state, (episode.artifact_order[prior_slot],), observation
        )
    return state


def _action_diagnostic(
    case: dict, observation: SemanticObservation
) -> dict:
    episode = episode_from_case(case)
    current_slot = int(case["runner_control"]["current_artifact_slot"])
    state = _state_before(case, episode)
    state = update_state(
        state, (episode.artifact_order[current_slot],), observation
    )
    inventory = tuple(
        ArtifactDescriptor.from_dict(item)
        for item in episode.public_view()["artifact_inventory"]
    )
    values = estimate_action_values(state, inventory, episode.candidates)
    ranked = sorted(values, key=lambda item: (values[item], item), reverse=True)
    usefulness = {
        item.descriptor.artifact_id: item.evaluator_usefulness
        for item in episode.artifacts
    }
    best_value = max(usefulness[item] for item in ranked)
    lowest = min(usefulness[item] for item in ranked)
    oracle_best = {
        item for item in ranked if abs(usefulness[item] - best_value) <= 1e-12
    }
    selected = ranked[0]
    denominator = max(1e-12, best_value - lowest)
    return {
        "top1": selected in oracle_best,
        "top2": bool(set(ranked[:2]) & oracle_best),
        "selected_usefulness": usefulness[selected],
        "best_usefulness": best_value,
        "normalized_regret": (best_value - usefulness[selected]) / denominator,
    }


def _normalize(case: dict, content: dict) -> dict:
    episode = episode_from_case(case)
    effect_by_relation = {
        episode.candidates[index].relation_tags[0]: content["hypothesis_effects"][
            f"c{index}"
        ]
        for index in range(4)
    }
    roles = case["evaluator_only"]["logical_roles_by_slot"]
    unresolved = sorted(
        (roles[target], RELATION_BY_SLOT[relation_slot])
        for target, relations in content["unresolved_targets"].items()
        for relation_slot, present in relations.items()
        if present
    )
    return {
        "facts": dict(content["facts"]),
        "effects_by_relation": effect_by_relation,
        "unresolved_by_role": unresolved,
    }


def summarize(
    population: dict, runs: list[dict], responses: list[dict], validation: dict
) -> dict:
    cases = {item["case_id"]: item for item in population["cases"]}
    fact_counts = []
    effect_counts = []
    unresolved_counts = []
    model_actions = []
    unknown_values = 0
    total_effect_values = 0
    malformed = 0
    normalized = {}
    by_variant = defaultdict(lambda: {"runs": 0, "valid": 0})
    for run in runs:
        case = cases[run["case_id"]]
        variant = case["variant"]
        by_variant[variant]["runs"] += 1
        if not run["valid"]:
            malformed += 1
            continue
        by_variant[variant]["valid"] += 1
        content = run["result"]["parsed"]["provider_content"]
        expected = case["evaluator_only"]["expected_content"]
        actual_facts = {key for key, present in content["facts"].items() if present}
        expected_facts = {key for key, present in expected["facts"].items() if present}
        fact_counts.append(_micro_counts(actual_facts, expected_facts))
        actual_effects = {
            (key, value)
            for key, value in content["hypothesis_effects"].items()
            if value in ("support", "contradict")
        }
        expected_effects = {
            (key, value)
            for key, value in expected["hypothesis_effects"].items()
            if value in ("support", "contradict")
        }
        effect_counts.append(_micro_counts(actual_effects, expected_effects))
        actual_unresolved = {
            (target, relation_slot)
            for target, relations in content["unresolved_targets"].items()
            for relation_slot, present in relations.items()
            if present
        }
        expected_unresolved = {
            (target, relation_slot)
            for target, relations in expected["unresolved_targets"].items()
            for relation_slot, present in relations.items()
            if present
        }
        unresolved_counts.append(
            _micro_counts(actual_unresolved, expected_unresolved)
        )
        unknown_values += sum(
            value == "unknown" for value in content["hypothesis_effects"].values()
        )
        total_effect_values += len(content["hypothesis_effects"])
        observation = SemanticObservation.from_dict(
            run["result"]["parsed"]["semantic_observation"]
        )
        model_actions.append(_action_diagnostic(case, observation))
        normalized[(run["case_id"], run["repeat"])] = _normalize(case, content)

    canonical_cases = [
        item for item in population["cases"] if item["variant"] == "base_entry"
    ]
    oracle_actions = []
    for case in canonical_cases:
        episode = episode_from_case(case)
        expected = case["evaluator_only"]["expected_content"]
        observation, _ = parse_content(
            expected,
            episode,
            tuple(case["runner_control"]["legal_target_slots"]),
        )
        oracle_actions.append(_action_diagnostic(case, observation))

    semantic_pairs = []
    for case in canonical_cases:
        source_episode = case["source_episode_id"]
        peers = {
            item["variant"]: item
            for item in population["cases"]
            if item["source_episode_id"] == source_episode
        }
        for repeat in (1, 2):
            base_key = (peers["base_entry"]["case_id"], repeat)
            for variant in SEMANTIC_EQUIVALENCE_VARIANTS:
                other_key = (peers[variant]["case_id"], repeat)
                pair_valid = base_key in normalized and other_key in normalized
                semantic_pairs.append(
                    {
                        "source_episode_id": source_episode,
                        "repeat": repeat,
                        "variant": variant,
                        "both_valid": pair_valid,
                        "semantic_exact": pair_valid
                        and normalized[base_key] == normalized[other_key],
                    }
                )
    repeat_pairs = []
    for case in population["cases"]:
        left = (case["case_id"], 1)
        right = (case["case_id"], 2)
        pair_valid = left in normalized and right in normalized
        repeat_pairs.append(
            {
                "case_id": case["case_id"],
                "both_valid": pair_valid,
                "semantic_exact": pair_valid and normalized[left] == normalized[right],
            }
        )

    facts = _metric(fact_counts)
    effects = _metric(effect_counts)
    unresolved = _metric(unresolved_counts)
    model_action = {
        "observations": len(model_actions),
        "top1": _mean(float(item["top1"]) for item in model_actions),
        "top2": _mean(float(item["top2"]) for item in model_actions),
        "mean_normalized_regret": _mean(
            item["normalized_regret"] for item in model_actions
        ),
    }
    oracle_action = {
        "canonical_development_episodes": len(oracle_actions),
        "top1": _mean(float(item["top1"]) for item in oracle_actions),
        "top2": _mean(float(item["top2"]) for item in oracle_actions),
        "mean_normalized_regret": _mean(
            item["normalized_regret"] for item in oracle_actions
        ),
    }
    first_attempts = [item for item in responses if item["attempt"] == 1]
    first_valid = sum(item["contract_validation"]["valid"] for item in first_attempts)
    final_valid = sum(item["valid"] for item in runs)
    length_count = sum(
        item["contract_validation"]["finish_reason"] == "length"
        for item in responses
    )
    errors = Counter(
        item["contract_validation"]["error"]
        for item in responses
        if not item["contract_validation"]["valid"]
    )
    incomplete = sum(
        "not complete JSON" in str(error) for error in errors.elements()
    )
    illegal_artifact = sum(
        "artifact target slots" in str(error) for error in errors.elements()
    )
    illegal_hypothesis = sum(
        "candidate effect slots" in str(error) for error in errors.elements()
    )
    illegal_relation = sum(
        "unresolved relation" in str(error) for error in errors.elements()
    )
    contract_observed = {
        "scheduled_calls": len(population["schedule"]),
        "provider_attempts": len(responses),
        "first_attempt_valid": first_valid,
        "first_attempt_schema_valid_rate": first_valid / len(first_attempts)
        if first_attempts
        else 0.0,
        "post_retry_valid": final_valid,
        "post_retry_valid_rate": final_valid / len(runs) if runs else 0.0,
        "finish_reason_length": length_count,
        "incomplete_json": incomplete,
        "illegal_artifact_references": illegal_artifact,
        "illegal_hypothesis_references": illegal_hypothesis,
        "illegal_relation_references": illegal_relation,
        "manual_repairs": 0,
        "information_boundary_violations": validation["counts"][
            "information_boundary_violations"
        ],
    }
    contract_mechanical_pass = (
        contract_observed["first_attempt_schema_valid_rate"]
        >= CONTRACT_THRESHOLDS["minimum_first_attempt_schema_valid_rate"]
        and contract_observed["post_retry_valid_rate"]
        >= CONTRACT_THRESHOLDS["minimum_post_retry_valid_rate"]
        and contract_observed["finish_reason_length"] == 0
        and contract_observed["incomplete_json"] == 0
        and contract_observed["illegal_artifact_references"] == 0
        and contract_observed["illegal_hypothesis_references"] == 0
        and contract_observed["illegal_relation_references"] == 0
        and contract_observed["manual_repairs"] == 0
        and contract_observed["information_boundary_violations"] == 0
    )
    if validation["status"] != "pass":
        contract_classifier = "invalid"
    elif contract_mechanical_pass:
        contract_classifier = "contract_stable"
    else:
        contract_classifier = "contract_unstable"

    fact_reasonable = (
        facts["precision"] >= SEMANTIC_THRESHOLDS["minimum_fact_precision"]
        and facts["recall"] >= SEMANTIC_THRESHOLDS["minimum_fact_recall"]
    )
    implication_reasonable = (
        effects["precision"] >= SEMANTIC_THRESHOLDS["minimum_effect_precision"]
        and effects["recall"] >= SEMANTIC_THRESHOLDS["minimum_effect_recall"]
        and unresolved["precision"]
        >= SEMANTIC_THRESHOLDS["minimum_unresolved_precision"]
        and unresolved["recall"]
        >= SEMANTIC_THRESHOLDS["minimum_unresolved_recall"]
    )
    model_action_compatible = (
        model_action["top1"] >= SEMANTIC_THRESHOLDS["minimum_action_top1"]
        and model_action["top2"] >= SEMANTIC_THRESHOLDS["minimum_action_top2"]
        and model_action["mean_normalized_regret"]
        <= SEMANTIC_THRESHOLDS["maximum_action_normalized_regret"]
    )
    oracle_estimator_adequate = (
        oracle_action["top1"] >= SEMANTIC_THRESHOLDS["minimum_action_top1"]
        and oracle_action["top2"] >= SEMANTIC_THRESHOLDS["minimum_action_top2"]
        and oracle_action["mean_normalized_regret"]
        <= SEMANTIC_THRESHOLDS["maximum_action_normalized_regret"]
    )
    total_true_positive = (
        facts["true_positive"]
        + effects["true_positive"]
        + unresolved["true_positive"]
    )
    if fact_reasonable and implication_reasonable and model_action_compatible:
        semantic_classifier = "semantic_signal_promising"
    elif total_true_positive == 0:
        semantic_classifier = "semantic_signal_absent"
    else:
        semantic_classifier = "semantic_signal_weak"

    if contract_classifier != "contract_stable":
        next_experiment = "case_a_new_contract_version"
    elif not fact_reasonable:
        next_experiment = "case_b_same_v1_2_contract_next_stronger_inexpensive_model"
    elif not implication_reasonable:
        next_experiment = "case_c_isolate_fact_to_decision_implication"
    elif not oracle_estimator_adequate:
        next_experiment = "separate_deterministic_value_estimator_repair"
    elif not model_action_compatible:
        next_experiment = "isolate_semantic_reference_to_action_value_translation"
    else:
        next_experiment = "case_d_fresh_population_architecture_comparison"

    return {
        "schema_version": 1,
        "experiment": "authzgym-semantic-contract-v1.2",
        "population_hash": population["population_hash"],
        "contract": {
            "classification": contract_classifier,
            "thresholds": CONTRACT_THRESHOLDS,
            "observed": contract_observed,
            "response_error_counts": dict(sorted(errors.items(), key=lambda item: str(item[0]))),
        },
        "semantics": {
            "classification": semantic_classifier,
            "thresholds": SEMANTIC_THRESHOLDS,
            "facts": facts,
            "hypothesis_effects": effects,
            "unresolved_relations": unresolved,
            "unknown_effect_rate": unknown_values / total_effect_values
            if total_effect_values
            else 0.0,
            "malformed_run_rate": malformed / len(runs) if runs else 0.0,
            "fact_reasonable": fact_reasonable,
            "implication_reasonable": implication_reasonable,
        },
        "downstream_action_value": {
            "model_conditioned": model_action,
            "oracle_conditioned": oracle_action,
            "model_action_compatible": model_action_compatible,
            "existing_estimator_adequate_under_oracle": oracle_estimator_adequate,
        },
        "stability": {
            "semantic_equivalence_pairs": len(semantic_pairs),
            "semantic_equivalence_both_valid_rate": _mean(
                float(item["both_valid"]) for item in semantic_pairs
            ),
            "semantic_equivalence_exact_rate": _mean(
                float(item["semantic_exact"]) for item in semantic_pairs
            ),
            "repeat_pairs": len(repeat_pairs),
            "repeat_both_valid_rate": _mean(
                float(item["both_valid"]) for item in repeat_pairs
            ),
            "repeat_semantic_exact_rate": _mean(
                float(item["semantic_exact"]) for item in repeat_pairs
            ),
            "by_variant": dict(sorted(by_variant.items())),
        },
        "provider_accounting": {
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
        },
        "decision_rule": {
            "selected_next_experiment": next_experiment,
            "no_hypothesis_promotion": True,
        },
    }


def render_report(summary: dict, validation: dict, autopsy: dict) -> str:
    contract = summary["contract"]
    semantic = summary["semantics"]
    action = summary["downstream_action_value"]
    accounting = summary["provider_accounting"]
    stability = summary["stability"]
    old_roots = autopsy["dominant_root_causes"]
    lines = [
        "# AuthzGym semantic contract v1.2 report",
        "",
        "This development-only experiment tests the semantic wire contract and the cheap model's capability floor. It is not an SER-vs-ReAct comparison and admits no general SER finding.",
        "",
        f"Validation: **{validation['status']}**",
        f"Contract classifier: **`{contract['classification']}`**",
        f"Semantic diagnostic: **`{semantic['classification']}`**",
        "",
        "## Preserved v1 autopsy",
        "",
        f"The immutable 609-attempt run reproduced 336 valid and 273 invalid responses. Dominant invalid roots were {old_roots}. The 320-token ceiling caused 134 invalid length-finished attempts; the 1,280-token monolithic condition had zero length terminations and failed mainly on unconstrained public-symbol references.",
        "",
        "## Contract reliability",
        "",
        f"- Scheduled semantic calls: **{contract['observed']['scheduled_calls']}**; provider attempts: **{contract['observed']['provider_attempts']}**.",
        f"- First-attempt schema-valid: **{contract['observed']['first_attempt_valid']}/{contract['observed']['scheduled_calls']}** (`{contract['observed']['first_attempt_schema_valid_rate']:.6f}`).",
        f"- Valid after frozen retry: **{contract['observed']['post_retry_valid']}/{contract['observed']['scheduled_calls']}** (`{contract['observed']['post_retry_valid_rate']:.6f}`).",
        f"- Length terminations: **{contract['observed']['finish_reason_length']}**; incomplete JSON: **{contract['observed']['incomplete_json']}**.",
        f"- Illegal artifact/hypothesis/relation references: **{contract['observed']['illegal_artifact_references']}/{contract['observed']['illegal_hypothesis_references']}/{contract['observed']['illegal_relation_references']}**.",
        "- Manual repairs: **0**.",
        "",
        "## Semantic layers",
        "",
        "| Layer | Precision | Recall |",
        "| --- | ---: | ---: |",
        f"| Fact extraction | {semantic['facts']['precision']:.3f} | {semantic['facts']['recall']:.3f} |",
        f"| Hypothesis effect | {semantic['hypothesis_effects']['precision']:.3f} | {semantic['hypothesis_effects']['recall']:.3f} |",
        f"| Remaining unresolved relation | {semantic['unresolved_relations']['precision']:.3f} | {semantic['unresolved_relations']['recall']:.3f} |",
        "",
        f"Unknown hypothesis-effect rate: `{semantic['unknown_effect_rate']:.3f}`.",
        "",
        "## Downstream action-value decomposition",
        "",
        f"Model-conditioned top-1/top-2 and normalized regret: `{action['model_conditioned']['top1']:.3f}` / `{action['model_conditioned']['top2']:.3f}` / `{action['model_conditioned']['mean_normalized_regret']:.3f}`.",
        f"Oracle-conditioned top-1/top-2 and normalized regret on the eight canonical development entries: `{action['oracle_conditioned']['top1']:.3f}` / `{action['oracle_conditioned']['top2']:.3f}` / `{action['oracle_conditioned']['mean_normalized_regret']:.3f}`.",
        f"Existing estimator adequate under the preregistered oracle rule: **{str(action['existing_estimator_adequate_under_oracle']).lower()}**.",
        "",
        "## Protocol stability",
        "",
        f"- Semantic-equivalence exact pairs: `{stability['semantic_equivalence_exact_rate']:.3f}` across {stability['semantic_equivalence_pairs']} pairs.",
        f"- Repeated-call exact semantic stability: `{stability['repeat_semantic_exact_rate']:.3f}` across {stability['repeat_pairs']} pairs.",
        "",
        "## Resources and next experiment",
        "",
        f"Provider-reported input/output tokens: **{accounting['input_tokens']} / {accounting['output_tokens']}**.",
        f"Accounted spend: **${accounting['total_cost_usd']:.9f}** under the $1 hard ceiling.",
        f"Decision-rule result: **`{summary['decision_rule']['selected_next_experiment']}`**.",
        "",
        "No H-001, H-016, H-017, H-018, or new E-* finding is promoted from this development-only result.",
        "",
    ]
    return "\n".join(lines)


def render_interpretation(summary: dict) -> str:
    return (
        "# AuthzGym semantic contract v1.2 interpretation\n\n"
        f"The preregistered wire-contract classifier is **`{summary['contract']['classification']}`** "
        f"and the separate development-only semantic diagnostic is **`{summary['semantics']['classification']}`**.\n\n"
        "This can establish only mechanical response reliability under the named development stress protocol. "
        "It cannot establish SER architecture leverage, a confirmatory model result, GitLab readiness, or cross-domain competence.\n\n"
        f"The mechanical next experiment is **`{summary['decision_rule']['selected_next_experiment']}`**.\n"
    )
