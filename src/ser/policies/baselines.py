"""Matched simple routing controls with documented, non-oracular rules."""

from __future__ import annotations

from .base import BeliefPolicy, BeliefState, DecisionContext


class RandomPolicy(BeliefPolicy):
    name = "random"
    assumptions = BeliefPolicy.assumptions + (
        "uniform seeded choice among legal acquisition actions",
        "fixed stop after three acquisitions or when none remain legal",
    )

    def select_action(self, state: BeliefState, context: DecisionContext):
        return self.seeded_choice(state, context)


class FixedOrderPolicy(BeliefPolicy):
    name = "fixed_order"
    assumptions = BeliefPolicy.assumptions + (
        "follows the episode's frozen presentation order independently of observations",
        "fixed stop after three acquisitions or when none remain legal",
    )

    def select_action(self, state: BeliefState, context: DecisionContext):
        legal = {item.action_id: item for item in context.legal_actions}
        for test in context.view.tests:
            if test.action_id in legal and state.count(test.action_id) == 0:
                return legal[test.action_id]
        for test in context.view.tests:
            if test.action_id in legal:
                return legal[test.action_id]
        raise AssertionError("select_action called without legal actions")


class CheapFirstPolicy(BeliefPolicy):
    name = "cheap_first"
    assumptions = BeliefPolicy.assumptions + (
        "selects minimum immediate primary-resource cost with opaque-ID tie-breaking",
        "fixed stop after three acquisitions or when none remain legal",
    )

    def select_action(self, state: BeliefState, context: DecisionContext):
        dimension = context.view.primary_resource
        return min(
            context.legal_actions,
            key=lambda item: (item.cost.get(dimension), item.action_id),
        )


class InformationBlindPolicy(CheapFirstPolicy):
    name = "ablation_information_blind"
    assumptions = CheapFirstPolicy.assumptions + (
        "registered as the cost-only adaptive-policy ablation",
    )


class ExhaustivePolicy(FixedOrderPolicy):
    name = "exhaustive"
    stop_after = 10**9
    assumptions = BeliefPolicy.assumptions + (
        "precommits to presentation order and acquires every action affordable under that order",
        "repeated tests are exhausted only after every test has been attempted once",
    )

    def should_stop(self, state: BeliefState, context: DecisionContext) -> bool:
        return not context.legal_actions or context.step >= context.view.max_steps


class GreedyPolicy(BeliefPolicy):
    name = "greedy"
    assumptions = BeliefPolicy.assumptions + (
        "uses a fixed public pairwise-separation-per-cost score",
        "does not recompute utility from observations",
        "fixed stop after three acquisitions or when none remain legal",
    )

    def select_action(self, state: BeliefState, context: DecisionContext):
        return max(
            context.legal_actions,
            key=lambda item: (item.public_score, item.action_id),
        )
