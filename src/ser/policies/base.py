"""Policy-private belief state and the explicit state-updater boundary."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, replace

from ser.core.types import Action, ActionDescriptor, ActionResult, Budget, Observation
from ser.microgym.model import (
    PublicProblemView,
    best_submission,
    expected_terminal_loss,
    posterior,
)


@dataclass(frozen=True)
class DecisionContext:
    view: PublicProblemView
    legal_actions: tuple[ActionDescriptor, ...]
    remaining_budget: Budget
    public_observations: tuple[Observation, ...]
    step: int


@dataclass(frozen=True)
class BeliefState:
    belief: tuple[float, ...]
    counts: tuple[tuple[str, int], ...]
    acquisitions: int
    seed: int
    frozen_plan: tuple[str, ...] = ()

    def count(self, action_id: str) -> int:
        return dict(self.counts).get(action_id, 0)


def update_for_observation(
    belief: tuple[float, ...], observation: Observation, view: PublicProblemView
) -> tuple[float, ...]:
    payload = observation.payload
    if not isinstance(payload, dict) or set(payload) != {"model_id", "value"}:
        raise ValueError("MicroGym observation payload is malformed")
    test = view.test(str(payload["model_id"]))
    return posterior(belief, test, str(payload["value"]))


def _stable_choice(seed: int, step: int, candidates: tuple[str, ...]) -> str:
    digest = hashlib.sha256(
        f"policy-choice|{seed}|{step}".encode("utf-8")
    ).digest()
    return candidates[int.from_bytes(digest[:8], "big") % len(candidates)]


class BeliefPolicy:
    """Common public Bayesian decision rule; routing remains policy-specific."""

    name = "belief_policy"
    access_class = "public_episode"
    stop_after = 3
    assumptions: tuple[str, ...] = (
        "uses only the declared public prior, likelihoods, costs, and released observations",
        "uses Bayes-optimal answer-or-abstain submission under declared decision loss",
    )

    def reset(
        self,
        view: PublicProblemView,
        initial_observations: tuple[Observation, ...],
        seed: int,
    ) -> BeliefState:
        belief = view.prior
        for observation in initial_observations:
            belief = update_for_observation(belief, observation, view)
        counts = tuple((test.action_id, 0) for test in view.tests)
        return BeliefState(belief, counts, 0, seed)

    def state_record(self, state: BeliefState) -> dict:
        return {
            "belief": state.belief,
            "counts": state.counts,
            "acquisitions": state.acquisitions,
            "seed": state.seed,
            "frozen_plan": state.frozen_plan,
        }

    def update(
        self,
        state: BeliefState,
        action: Action,
        result: ActionResult,
        view: PublicProblemView,
    ) -> BeliefState:
        belief = state.belief
        for observation in result.observations:
            belief = update_for_observation(belief, observation, view)
        counts = dict(state.counts)
        acquisitions = state.acquisitions
        if action.kind == "acquire" and action.target_id in counts:
            counts[action.target_id] += 1
            acquisitions += 1
        return replace(
            state,
            belief=belief,
            counts=tuple((test.action_id, counts[test.action_id]) for test in view.tests),
            acquisitions=acquisitions,
        )

    def submission(self, state: BeliefState, view: PublicProblemView) -> str | None:
        return best_submission(state.belief, view.hypotheses, view.abstain_loss)[0]

    def should_stop(self, state: BeliefState, context: DecisionContext) -> bool:
        return (
            not context.legal_actions
            or state.acquisitions >= self.stop_after
            or context.step >= context.view.max_steps
        )

    def select_action(
        self, state: BeliefState, context: DecisionContext
    ) -> ActionDescriptor:
        raise NotImplementedError

    def choose(self, state: BeliefState, context: DecisionContext) -> Action:
        if self.should_stop(state, context):
            return Action(
                action_id=f"a-{context.step:03d}",
                kind="stop",
                submission=self.submission(state, context.view),
            )
        descriptor = self.select_action(state, context)
        return Action(
            action_id=f"a-{context.step:03d}",
            kind="acquire",
            target_id=descriptor.action_id,
        )

    def one_step_score(
        self,
        state: BeliefState,
        descriptor: ActionDescriptor,
        view: PublicProblemView,
        *,
        cost_weight: float | None = None,
    ) -> float:
        stop_loss = best_submission(state.belief, view.hypotheses, view.abstain_loss)[1]
        test = view.test(descriptor.action_id)
        expected_loss = expected_terminal_loss(
            state.belief, test, view.hypotheses, view.abstain_loss
        )
        weight = view.cost_weight if cost_weight is None else cost_weight
        return stop_loss - expected_loss - weight * descriptor.cost.get(view.primary_resource)

    def seeded_choice(
        self, state: BeliefState, context: DecisionContext
    ) -> ActionDescriptor:
        identifiers = tuple(item.action_id for item in context.legal_actions)
        target = _stable_choice(state.seed, context.step, identifiers)
        return next(item for item in context.legal_actions if item.action_id == target)
