"""Matched static AuthzGym architecture baselines and explicit routed state."""

from __future__ import annotations

import math
from dataclasses import dataclass, replace

from .model import (
    ArtifactDescriptor,
    CandidateHypothesis,
    SemanticObservation,
)


ARCHITECTURES = (
    "fixed_order_semantic",
    "react_like_semantic",
    "ser_explicit_value",
    "monolithic_semantic",
)


@dataclass(frozen=True)
class AuthzEpistemicState:
    hypothesis_support: tuple[tuple[str, float], ...]
    inspected_artifacts: tuple[str, ...]
    observations: tuple[SemanticObservation, ...]

    @classmethod
    def initial(
        cls, candidates: tuple[CandidateHypothesis, ...]
    ) -> AuthzEpistemicState:
        return cls(tuple((item.hypothesis_id, 0.0) for item in candidates), (), ())

    def support(self) -> dict[str, float]:
        return dict(self.hypothesis_support)

    def to_dict(self) -> dict:
        return {
            "hypothesis_support": dict(self.hypothesis_support),
            "inspected_artifacts": list(self.inspected_artifacts),
            "semantic_observations": [item.to_dict() for item in self.observations],
        }


def update_state(
    state: AuthzEpistemicState,
    artifact_ids: tuple[str, ...],
    observation: SemanticObservation,
) -> AuthzEpistemicState:
    support = state.support()
    for hypothesis_id, effect in observation.hypothesis_effects:
        support[hypothesis_id] = support.get(hypothesis_id, 0.0) + effect
    return replace(
        state,
        hypothesis_support=tuple(sorted(support.items())),
        inspected_artifacts=state.inspected_artifacts + artifact_ids,
        observations=state.observations + (observation,),
    )


def _available(
    inventory: tuple[ArtifactDescriptor, ...], state: AuthzEpistemicState
) -> tuple[ArtifactDescriptor, ...]:
    inspected = set(state.inspected_artifacts)
    return tuple(item for item in inventory if item.artifact_id not in inspected)


def estimate_action_values(
    state: AuthzEpistemicState,
    inventory: tuple[ArtifactDescriptor, ...],
    candidates: tuple[CandidateHypothesis, ...],
) -> dict[str, float]:
    """Estimate relevance from public semantic references; no evaluator input."""

    support = state.support()
    relation_to_hypotheses: dict[str, tuple[str, ...]] = {}
    for candidate in candidates:
        for tag in candidate.relation_tags:
            relation_to_hypotheses.setdefault(tag, ())
            relation_to_hypotheses[tag] += (candidate.hypothesis_id,)

    references = [
        reference
        for observation in state.observations
        for reference in observation.unresolved_references
    ]
    scores = {}
    for artifact in _available(inventory, state):
        score = 0.05
        for symbol in artifact.exported_symbols:
            for reference in references:
                if reference.symbol != symbol:
                    continue
                linked = relation_to_hypotheses.get(reference.relation_tag, ())
                plausibility = max(
                    (max(0.0, support.get(item, 0.0)) for item in linked),
                    default=0.0,
                )
                score += 1.0 + min(1.5, plausibility)
        scores[artifact.artifact_id] = score
    return scores


def select_next_artifact(
    architecture: str,
    state: AuthzEpistemicState,
    inventory: tuple[ArtifactDescriptor, ...],
    candidates: tuple[CandidateHypothesis, ...],
) -> tuple[str, dict[str, float] | None, str]:
    available = _available(inventory, state)
    if not available:
        raise ValueError("no artifact remains available")
    if architecture == "fixed_order_semantic":
        return available[0].artifact_id, None, "next artifact in frozen public order"
    if architecture == "react_like_semantic":
        available_by_symbol = {
            symbol: artifact.artifact_id
            for artifact in available
            for symbol in artifact.exported_symbols
        }
        for observation in reversed(state.observations):
            for reference in observation.unresolved_references:
                if reference.symbol in available_by_symbol:
                    return (
                        available_by_symbol[reference.symbol],
                        None,
                        "first unresolved tool reference in conversational state",
                    )
        return available[0].artifact_id, None, "public-order fallback"
    if architecture == "ser_explicit_value":
        values = estimate_action_values(state, inventory, candidates)
        target = max(values, key=lambda item: (values[item], item))
        return target, values, "maximum explicit policy-visible action-value estimate"
    raise ValueError(f"architecture does not select sequentially: {architecture}")


def final_conclusion(state: AuthzEpistemicState) -> tuple[str, dict]:
    ranked = sorted(
        state.hypothesis_support,
        key=lambda item: (item[1], item[0]),
        reverse=True,
    )
    best_id, best_score = ranked[0]
    second_score = ranked[1][1]
    sufficient = best_score >= 1.25 and best_score - second_score >= 0.50
    return (
        best_id if sufficient else "insufficient",
        {
            "ranking": [item[0] for item in ranked],
            "scores": dict(ranked),
            "sufficiency_threshold": 1.25,
            "margin_threshold": 0.50,
            "sufficient": sufficient,
        },
    )


def normalized_support(state: AuthzEpistemicState) -> dict[str, float]:
    values = state.support()
    exponentials = {key: math.exp(min(20.0, value)) for key, value in values.items()}
    total = sum(exponentials.values())
    return {key: value / total for key, value in exponentials.items()}
