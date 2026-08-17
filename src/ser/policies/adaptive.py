"""One myopic adaptive candidate and preregistered behavioral ablations."""

from __future__ import annotations

from dataclasses import replace

from ser.core.types import Budget

from .base import BeliefPolicy, BeliefState, DecisionContext


class AdaptiveBeliefPolicy(BeliefPolicy):
    name = "adaptive_belief"
    assumptions = BeliefPolicy.assumptions + (
        "maintains a posterior with the declared public observation model",
        "chooses the legal action with greatest one-step Bayes-risk reduction minus experiment-specific primary cost",
        "chooses STOP when no acquisition has positive myopic net value",
        "is a candidate experimental policy, not a canonical SER objective",
    )

    def scored(self, state: BeliefState, context: DecisionContext):
        return tuple(
            (self.one_step_score(state, item, context.view), item)
            for item in context.legal_actions
        )

    def should_stop(self, state: BeliefState, context: DecisionContext) -> bool:
        return (
            not context.legal_actions
            or context.step >= context.view.max_steps
            or max(score for score, _ in self.scored(state, context)) <= 1e-12
        )

    def select_action(self, state: BeliefState, context: DecisionContext):
        return max(self.scored(state, context), key=lambda pair: (pair[0], pair[1].action_id))[1]


class CostBlindPolicy(AdaptiveBeliefPolicy):
    name = "ablation_cost_blind"
    assumptions = BeliefPolicy.assumptions + (
        "uses adaptive expected Bayes-risk reduction but ignores resource cost",
    )

    def scored(self, state: BeliefState, context: DecisionContext):
        return tuple(
            (self.one_step_score(state, item, context.view, cost_weight=0.0), item)
            for item in context.legal_actions
        )


class NoAdaptationPolicy(AdaptiveBeliefPolicy):
    name = "ablation_no_adaptation"
    assumptions = BeliefPolicy.assumptions + (
        "receives the same public generative model, objective, costs, and budget as the adaptive candidate",
        "commits an open-loop acquisition plan from the prior before inspecting the episode's initial observation",
        "neither action ranking nor stopping length can change in response to realized observations",
        "released observations still inform the final answer so only acquisition control is ablated",
    )

    def reset(self, view, initial_observations, seed):
        state = super().reset(view, initial_observations, seed)
        planning_state = replace(state, belief=view.prior, acquisitions=0)
        budget = Budget.create(view.tests[0].cost.schema, dict(view.budget_limits))
        counts = {test.action_id: 0 for test in view.tests}
        plan: list[str] = []
        for _ in range(max(0, view.max_steps - 1)):
            legal = tuple(
                test.descriptor()
                for test in view.tests
                if counts[test.action_id] < test.repeat_limit
                and budget.can_afford(test.cost)
            )
            if not legal:
                break
            scored = tuple(
                (self.one_step_score(planning_state, item, view), item)
                for item in legal
            )
            score, descriptor = max(
                scored, key=lambda pair: (pair[0], pair[1].action_id)
            )
            if score <= 1e-12:
                break
            plan.append(descriptor.action_id)
            counts[descriptor.action_id] += 1
            budget = budget.charge(descriptor.cost)
        return replace(state, frozen_plan=tuple(plan))

    def should_stop(self, state: BeliefState, context: DecisionContext) -> bool:
        return (
            state.acquisitions >= len(state.frozen_plan)
            or not context.legal_actions
            or context.step >= context.view.max_steps
        )

    def select_action(self, state: BeliefState, context: DecisionContext):
        legal = {item.action_id: item for item in context.legal_actions}
        action_id = state.frozen_plan[state.acquisitions]
        if action_id not in legal:
            raise AssertionError("frozen open-loop action unexpectedly became illegal")
        return legal[action_id]


class NoAdaptiveStopPolicy(AdaptiveBeliefPolicy):
    name = "ablation_no_adaptive_stop"
    stop_after = 3
    assumptions = BeliefPolicy.assumptions + (
        "uses observation-conditioned adaptive routing",
        "cannot compare acquisition against STOP and instead stops after three acquisitions or exhaustion",
    )

    def should_stop(self, state: BeliefState, context: DecisionContext) -> bool:
        return (
            not context.legal_actions
            or state.acquisitions >= self.stop_after
            or context.step >= context.view.max_steps
        )
