"""Static, bounded AuthzGym execution and visibility-split run artifacts."""

from __future__ import annotations

from ser.core.types import content_hash

from .interpreters import InterpreterCondition, interpret_artifacts
from .model import (
    AUTHZ_RESOURCE_SCHEMA,
    ArtifactDescriptor,
    AuthzEpisode,
    SemanticObservation,
)
from .policies import (
    ARCHITECTURES,
    AuthzEpistemicState,
    final_conclusion,
    select_next_artifact,
    update_state,
)


def _add_resources(total: dict[str, float], item: dict[str, float]) -> None:
    for name in AUTHZ_RESOURCE_SCHEMA.names:
        total[name] += float(item.get(name, 0.0))


def _semantic_quality(
    episode: AuthzEpisode,
    inspected: tuple[str, ...],
    observations: tuple[SemanticObservation, ...],
) -> dict:
    expected = set()
    extracted = set()
    by_artifact = []
    if len(observations) == 1 and len(inspected) > 1:
        observation = observations[0]
        expected = {
            key
            for artifact_id in inspected
            for key in episode.artifact(artifact_id).expected_fact_keys
        }
        extracted = set(observation.fact_keys)
        true_positive = len(expected & extracted)
        return {
            "expected_facts": len(expected),
            "extracted_facts": len(extracted),
            "true_positive_facts": true_positive,
            "precision": true_positive / len(extracted) if extracted else 0.0,
            "recall": true_positive / len(expected) if expected else 0.0,
            "by_artifact": [],
            "consolidated": True,
        }
    for artifact_id, observation in zip(inspected, observations):
        artifact = episode.artifact(artifact_id)
        expected_here = set(artifact.expected_fact_keys)
        extracted_here = set(observation.fact_keys)
        expected |= expected_here
        extracted |= extracted_here
        true_here = expected_here & extracted_here
        by_artifact.append(
            {
                "artifact_id": artifact_id,
                "expected": len(expected_here),
                "extracted": len(extracted_here),
                "true_positive": len(true_here),
            }
        )
    true_positive = len(expected & extracted)
    precision = true_positive / len(extracted) if extracted else 0.0
    recall = true_positive / len(expected) if expected else 0.0
    return {
        "expected_facts": len(expected),
        "extracted_facts": len(extracted),
        "true_positive_facts": true_positive,
        "precision": precision,
        "recall": recall,
        "by_artifact": by_artifact,
    }


def _routing_quality(episode: AuthzEpisode, public_steps: list[dict]) -> dict:
    role_by_artifact = {
        item.descriptor.artifact_id: item.logical_role for item in episode.artifacts
    }
    usefulness = {
        item.descriptor.artifact_id: item.evaluator_usefulness
        for item in episode.artifacts
    }
    audits = []
    for step in public_steps[1:]:
        selected = step["action"]["artifact_id"]
        available = step["action"]["available_artifact_ids"]
        best_value = max(usefulness[item] for item in available)
        selected_value = usefulness[selected]
        lowest = min(usefulness[item] for item in available)
        denominator = max(1e-12, best_value - lowest)
        values = step["action"]["estimated_action_values"]
        top_two = []
        if values is not None:
            top_two = sorted(
                values,
                key=lambda item: (values[item], item),
                reverse=True,
            )[:2]
        oracle_best = sorted(
            (item for item in available if abs(usefulness[item] - best_value) <= 1e-12),
            reverse=True,
        )
        audits.append(
            {
                "step": step["step"],
                "selected_artifact_id": selected,
                "selected_logical_role": role_by_artifact[selected],
                "oracle_best_artifact_ids": oracle_best,
                "oracle_best_logical_roles": [role_by_artifact[item] for item in oracle_best],
                "selected_usefulness": selected_value,
                "best_available_usefulness": best_value,
                "routing_regret": best_value - selected_value,
                "normalized_routing_regret": (best_value - selected_value) / denominator,
                "estimated_top_two_contains_oracle": bool(set(top_two) & set(oracle_best)),
                "estimated_top_one_is_oracle": bool(top_two and top_two[0] in oracle_best),
            }
        )
    first = audits[0] if audits else None
    return {
        "post_entry_steps": audits,
        "first_post_entry_selected_role": None
        if first is None
        else first["selected_logical_role"],
        "first_post_entry_oracle_role": episode.truth.discriminating_artifact_role,
        "first_post_entry_correct": bool(
            first
            and first["selected_logical_role"]
            == episode.truth.discriminating_artifact_role
        ),
    }


def _failure_layers(
    architecture: str,
    correct: bool,
    semantic_quality: dict,
    routing_quality: dict,
    final_diagnostic: dict,
    resource_valid: bool,
) -> list[str]:
    failures = []
    if semantic_quality["recall"] < 0.50:
        failures.append("semantic_extraction_failure")
    if not final_diagnostic["state_update_consistent"]:
        failures.append("epistemic_update_failure")
    audits = routing_quality["post_entry_steps"]
    if architecture == "ser_explicit_value" and audits:
        if not audits[0]["estimated_top_two_contains_oracle"]:
            failures.append("action_value_estimation_failure")
        values = audits[0]
        if (
            values["estimated_top_one_is_oracle"]
            and values["selected_artifact_id"] not in values["oracle_best_artifact_ids"]
        ):
            failures.append("routing_failure")
    if not correct:
        failures.append("decision_failure")
    if not resource_valid:
        failures.append("cost_failure")
    return failures


def run_authz_episode(
    episode: AuthzEpisode,
    architecture: str,
    condition: InterpreterCondition,
    prompt_text: str,
    prompt_version: str,
    prompt_hash: str,
    config_hash: str,
    population_hash: str,
) -> dict:
    if architecture not in ARCHITECTURES:
        raise ValueError(f"unknown architecture: {architecture}")
    inventory = tuple(
        ArtifactDescriptor.from_dict(item) for item in episode.public_view()["artifact_inventory"]
    )
    public_inventory = tuple(item.to_dict() for item in inventory)
    state = AuthzEpistemicState.initial(episode.candidates)
    totals = {name: 0.0 for name in AUTHZ_RESOURCE_SCHEMA.names}
    public_steps: list[dict] = []

    if architecture == "monolithic_semantic":
        artifact_ids = episode.artifact_order[: episode.max_inspections]
        artifacts = tuple(episode.artifact(item) for item in artifact_ids)
        state_before = state.to_dict()
        call = interpret_artifacts(
            artifacts,
            episode.candidates,
            state_before,
            public_inventory,
            prompt_text,
            prompt_version,
            condition,
            consolidated=True,
        )
        observation = SemanticObservation.from_dict(call["parsed_semantic_observation"])
        state = update_state(state, artifact_ids, observation)
        _add_resources(totals, call["resource_use"])
        public_steps.append(
            {
                "step": 1,
                "state_before_ref": content_hash(state_before),
                "action": {
                    "kind": "inspect_artifacts_consolidated",
                    "artifact_ids": list(artifact_ids),
                    "available_artifact_ids": list(episode.artifact_order),
                    "estimated_action_values": None,
                    "selection_basis": "frozen public-order evidence slice",
                },
                "semantic_call": call,
                "state_after_ref": content_hash(state.to_dict()),
            }
        )
    else:
        for step in range(1, episode.max_inspections + 1):
            state_before = state.to_dict()
            available = tuple(
                item.artifact_id
                for item in inventory
                if item.artifact_id not in state.inspected_artifacts
            )
            if step == 1:
                target = episode.entry_artifact_id
                values = None
                basis = "required common entry artifact"
            else:
                target, values, basis = select_next_artifact(
                    architecture, state, inventory, episode.candidates
                )
            artifact = episode.artifact(target)
            call = interpret_artifacts(
                (artifact,),
                episode.candidates,
                state_before,
                public_inventory,
                prompt_text,
                prompt_version,
                condition,
            )
            observation = SemanticObservation.from_dict(call["parsed_semantic_observation"])
            state = update_state(state, (target,), observation)
            _add_resources(totals, call["resource_use"])
            public_steps.append(
                {
                    "step": step,
                    "state_before_ref": content_hash(state_before),
                    "action": {
                        "kind": "inspect_artifact",
                        "artifact_id": target,
                        "available_artifact_ids": list(available),
                        "estimated_action_values": values,
                        "selection_basis": basis,
                    },
                    "semantic_call": call,
                    "state_after_ref": content_hash(state.to_dict()),
                }
            )

    conclusion, final_diagnostic = final_conclusion(state)
    expected_state = {item.hypothesis_id: 0.0 for item in episode.candidates}
    for observation in state.observations:
        for hypothesis_id, score in observation.hypothesis_effects:
            expected_state[hypothesis_id] += score
    final_diagnostic["state_update_consistent"] = all(
        abs(expected_state[key] - state.support()[key]) <= 1e-12 for key in expected_state
    )
    correct = conclusion == episode.truth.correct_conclusion
    semantic_quality = _semantic_quality(
        episode, state.inspected_artifacts, state.observations
    )
    routing_quality = (
        {
            "post_entry_steps": [],
            "first_post_entry_selected_role": None,
            "first_post_entry_oracle_role": episode.truth.discriminating_artifact_role,
            "first_post_entry_correct": False,
        }
        if architecture == "monolithic_semantic"
        else _routing_quality(episode, public_steps)
    )
    limits = episode.public_view()["resource_limits"]
    resource_valid = all(totals[name] <= limit + 1e-12 for name, limit in limits.items())
    failures = _failure_layers(
        architecture,
        correct,
        semantic_quality,
        routing_quality,
        final_diagnostic,
        resource_valid,
    )
    public = {
        "run_id": f"{episode.episode_id}--{condition.condition_id}--{architecture}",
        "episode_id": episode.episode_id,
        "split": episode.split,
        "architecture": architecture,
        "interpreter_condition": condition.to_dict(),
        "real_model_call": False,
        "prompt_version": prompt_version,
        "prompt_sha256": prompt_hash,
        "model_config_sha256": config_hash,
        "candidate_hypotheses": [item.to_dict() for item in episode.candidates],
        "artifact_inventory": list(public_inventory),
        "max_inspections": episode.max_inspections,
        "steps": public_steps,
        "final_epistemic_state": state.to_dict(),
        "final_conclusion": conclusion,
        "final_decision_diagnostic": final_diagnostic,
        "raw_resources": totals,
        "valid": resource_valid,
        "invalid_reason": None if resource_valid else "resource_ceiling_exceeded",
    }
    restricted = {
        "visibility": "evaluator_only",
        "mechanism_id": episode.truth.mechanism_id,
        "authorization_explanation": episode.truth.explanation,
        "relevant_artifact_roles": list(episode.truth.relevant_artifact_roles),
        "relevant_functions": list(episode.truth.relevant_functions),
        "evidence_relationships": list(episode.truth.evidence_relationships),
        "discriminating_artifact_role": episode.truth.discriminating_artifact_role,
        "correct_conclusion": episode.truth.correct_conclusion,
        "decision_group": episode.truth.decision_group,
        "control_type": episode.truth.control_type,
        "outcome": {
            "correct": correct,
            "decision_loss": 0.0 if correct else 1.0,
            "semantic_quality": semantic_quality,
            "routing_quality": routing_quality,
            "failure_layers": failures,
        },
    }
    record = {
        "schema_version": 1,
        "benchmark": "authzgym-static-v1",
        "population_hash": population_hash,
        "public": public,
        "restricted": restricted,
    }
    record["record_hash"] = content_hash(record)
    return record
