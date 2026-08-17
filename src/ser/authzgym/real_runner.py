"""Frozen real-model execution layer for Static Semantic AuthzGym v1.1."""

from __future__ import annotations

from ser.core.types import content_hash

from .model import ArtifactDescriptor, AuthzEpisode, SemanticObservation
from .policies import (
    ARCHITECTURES,
    AuthzEpistemicState,
    final_conclusion,
    select_next_artifact,
    update_state,
)
from .realmodel import (
    CurlChatCompletionsClient,
    MalformedSemanticResponse,
    ProviderError,
    RealModelCondition,
)
from .runner import _failure_layers, _routing_quality, _semantic_quality


RESOURCE_NAMES = (
    "artifact_inspections",
    "semantic_decisions",
    "provider_calls",
    "input_tokens",
    "output_tokens",
    "cached_input_tokens",
    "reasoning_output_tokens",
    "latency_ms",
    "monetary_cost_usd",
)


def _delta(after: dict, before: dict) -> dict:
    return {key: after[key] - before[key] for key in after}


def _add_resources(total: dict, item: dict) -> None:
    for name in RESOURCE_NAMES:
        total[name] += item.get(name, 0)


def _visible_input(
    episode: AuthzEpisode,
    artifacts: tuple,
    state: AuthzEpistemicState,
    public_inventory: tuple[dict, ...],
    permitted_next: tuple[str, ...],
    recommendation_required: bool,
    prompt_version: str,
) -> dict:
    return {
        "semantic_interface": "authzgym_semantic_observation_v1",
        "prompt_version": prompt_version,
        "purchased_artifacts": [
            {
                "artifact_id": item.descriptor.artifact_id,
                "path": item.descriptor.path,
                "source": item.source,
            }
            for item in artifacts
        ],
        "candidate_hypotheses": [item.to_dict() for item in episode.candidates],
        "current_epistemic_summary": state.to_dict(),
        "public_artifact_inventory": list(public_inventory),
        "legal_next_artifact_ids": list(permitted_next),
        "recommendation_required": recommendation_required,
    }


def _resource_limits(
    condition: RealModelCondition, architecture: str, max_inspections: int
) -> dict:
    if architecture == "monolithic_semantic":
        return {
            "artifact_inspections": float(max_inspections),
            "semantic_decisions": 1.0,
            "provider_calls": float(condition.maximum_attempts_per_semantic_call),
            "input_tokens": float(condition.input_token_ceiling_per_monolithic_run),
            "output_tokens": float(condition.output_token_ceiling_per_monolithic_run),
            "monetary_cost_usd": condition.hard_spend_ceiling_usd,
        }
    return {
        "artifact_inspections": float(max_inspections),
        "semantic_decisions": float(max_inspections),
        "provider_calls": float(
            max_inspections * condition.maximum_attempts_per_semantic_call
        ),
        "input_tokens": float(condition.input_token_ceiling_per_sequential_run),
        "output_tokens": float(condition.output_token_ceiling_per_sequential_run),
        "monetary_cost_usd": condition.hard_spend_ceiling_usd,
    }


def _provider_call(
    client: CurlChatCompletionsClient,
    visible_input: dict,
    episode: AuthzEpisode,
    public_inventory: tuple[dict, ...],
    permitted_next: tuple[str, ...],
    recommendation_required: bool,
    artifacts_in_call: int,
    call_context: dict,
) -> tuple[dict, dict]:
    before = client.accounting_snapshot()
    try:
        result = client.invoke(
            visible_input,
            episode.candidates,
            public_inventory,
            permitted_next,
            recommendation_required,
            artifacts_in_call=artifacts_in_call,
            call_context=call_context,
        )
    except (ProviderError, MalformedSemanticResponse):
        after = client.accounting_snapshot()
        raise
    after = client.accounting_snapshot()
    resources = _delta(after, before)
    resources.update(
        {
            "artifact_inspections": float(artifacts_in_call),
            "semantic_decisions": 1.0,
        }
    )
    return result, resources


def run_real_authz_episode(
    episode: AuthzEpisode,
    architecture: str,
    condition: RealModelCondition,
    client: CurlChatCompletionsClient,
    prompt_version: str,
    prompt_hash: str,
    schema_hash: str,
    config_hash: str,
    preregistration_hash: str,
    frozen_inputs_hash: str,
    population_hash: str,
) -> dict:
    if architecture not in ARCHITECTURES:
        raise ValueError(f"unknown architecture: {architecture}")
    inventory = tuple(
        ArtifactDescriptor.from_dict(item)
        for item in episode.public_view()["artifact_inventory"]
    )
    public_inventory = tuple(item.to_dict() for item in inventory)
    state = AuthzEpistemicState.initial(episode.candidates)
    totals = {name: 0.0 for name in RESOURCE_NAMES}
    public_steps: list[dict] = []
    invalid_reason: str | None = None
    previous_recommendation: str | None = None

    if architecture == "monolithic_semantic":
        artifact_ids = episode.artifact_order[: episode.max_inspections]
        artifacts = tuple(episode.artifact(item) for item in artifact_ids)
        state_before = state.to_dict()
        visible_input = _visible_input(
            episode,
            artifacts,
            state,
            public_inventory,
            (),
            False,
            prompt_version,
        )
        before = client.accounting_snapshot()
        try:
            result, resources = _provider_call(
                client,
                visible_input,
                episode,
                public_inventory,
                (),
                False,
                len(artifacts),
                {
                    "split": episode.split,
                    "episode_id": episode.episode_id,
                    "architecture": architecture,
                    "step": 1,
                },
            )
            observation = SemanticObservation.from_dict(
                result["parsed_semantic_observation"]
            )
            state = update_state(state, artifact_ids, observation)
            _add_resources(totals, resources)
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
                    "semantic_call": {
                        **result,
                        "visible_input": visible_input,
                        "resource_use": resources,
                    },
                    "state_after_ref": content_hash(state.to_dict()),
                }
            )
        except (ProviderError, MalformedSemanticResponse) as exc:
            _add_resources(totals, _delta(client.accounting_snapshot(), before))
            totals["artifact_inspections"] += float(len(artifacts))
            totals["semantic_decisions"] += 1.0
            invalid_reason = f"provider_or_schema_failure:{type(exc).__name__}:{exc}"
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
            elif architecture == "react_like_semantic":
                if previous_recommendation not in available:
                    invalid_reason = "react_recommendation_missing_or_unavailable"
                    break
                target = previous_recommendation
                values = None
                basis = "model recommendation from accumulated tool-loop state"
            else:
                target, values, basis = select_next_artifact(
                    architecture, state, inventory, episode.candidates
                )
            artifact = episode.artifact(target)
            after_purchase = tuple(item for item in available if item != target)
            recommendation_required = step < episode.max_inspections
            permitted_next = after_purchase if recommendation_required else ()
            visible_input = _visible_input(
                episode,
                (artifact,),
                state,
                public_inventory,
                permitted_next,
                recommendation_required,
                prompt_version,
            )
            before = client.accounting_snapshot()
            try:
                result, resources = _provider_call(
                    client,
                    visible_input,
                    episode,
                    public_inventory,
                    permitted_next,
                    recommendation_required,
                    1,
                    {
                        "split": episode.split,
                        "episode_id": episode.episode_id,
                        "architecture": architecture,
                        "step": step,
                    },
                )
            except (ProviderError, MalformedSemanticResponse) as exc:
                _add_resources(totals, _delta(client.accounting_snapshot(), before))
                totals["artifact_inspections"] += 1.0
                totals["semantic_decisions"] += 1.0
                invalid_reason = f"provider_or_schema_failure:{type(exc).__name__}:{exc}"
                break
            observation = SemanticObservation.from_dict(
                result["parsed_semantic_observation"]
            )
            state = update_state(state, (target,), observation)
            previous_recommendation = result["recommended_next_artifact_id"]
            _add_resources(totals, resources)
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
                    "semantic_call": {
                        **result,
                        "visible_input": visible_input,
                        "resource_use": resources,
                    },
                    "state_after_ref": content_hash(state.to_dict()),
                }
            )

    conclusion, final_diagnostic = final_conclusion(state)
    expected_state = {item.hypothesis_id: 0.0 for item in episode.candidates}
    for observation in state.observations:
        for hypothesis_id, score in observation.hypothesis_effects:
            expected_state[hypothesis_id] += score
    final_diagnostic["state_update_consistent"] = all(
        abs(expected_state[key] - state.support()[key]) <= 1e-12
        for key in expected_state
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
        if architecture == "monolithic_semantic" or not public_steps
        else _routing_quality(episode, public_steps)
    )
    limits = _resource_limits(condition, architecture, episode.max_inspections)
    resource_valid = all(totals[name] <= limit + 1e-12 for name, limit in limits.items())
    complete = len(state.inspected_artifacts) == episode.max_inspections
    valid = invalid_reason is None and resource_valid and complete
    failures = _failure_layers(
        architecture,
        correct,
        semantic_quality,
        routing_quality,
        final_diagnostic,
        resource_valid,
    )
    if invalid_reason is not None:
        failures.append("provider_schema_api_failure")
    if not complete:
        failures.append("incomplete_run_failure")
    public = {
        "run_id": f"{episode.episode_id}--{condition.condition_id}--{architecture}",
        "episode_id": episode.episode_id,
        "split": episode.split,
        "architecture": architecture,
        "interpreter_condition": condition.public_dict(),
        "real_model_call": True,
        "prompt_version": prompt_version,
        "prompt_sha256": prompt_hash,
        "schema_sha256": schema_hash,
        "model_config_sha256": config_hash,
        "preregistration_sha256": preregistration_hash,
        "frozen_inputs_sha256": frozen_inputs_hash,
        "candidate_hypotheses": [item.to_dict() for item in episode.candidates],
        "artifact_inventory": list(public_inventory),
        "max_inspections": episode.max_inspections,
        "steps": public_steps,
        "final_epistemic_state": state.to_dict(),
        "final_conclusion": conclusion,
        "final_decision_diagnostic": final_diagnostic,
        "raw_resources": totals,
        "resource_limits": limits,
        "valid": valid,
        "invalid_reason": None
        if valid
        else invalid_reason or "resource_ceiling_or_completeness_failure",
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
            "failure_layers": list(dict.fromkeys(failures)),
        },
    }
    record = {
        "schema_version": 1,
        "benchmark": "authzgym-static-realmodel-v1",
        "source_benchmark": "authzgym-static-v1.1",
        "population_hash": population_hash,
        "public": public,
        "restricted": restricted,
    }
    record["record_hash"] = content_hash(record)
    return record

