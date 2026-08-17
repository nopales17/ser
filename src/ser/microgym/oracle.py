"""Exact evaluator-only dynamic-programming reference for tiny MicroGym tasks."""

from __future__ import annotations

from functools import lru_cache

from ser.core.types import Action, Budget
from ser.policies.base import BeliefPolicy, BeliefState, DecisionContext

from .model import PublicProblemView, best_submission, outcome_probabilities, posterior


class OracleSolver:
    """Minimize expected decision loss plus the experiment-specific cost term."""

    def __init__(self, view: PublicProblemView):
        self.view = view
        self._tests = tuple(view.tests)

    @staticmethod
    def _belief_key(belief: tuple[float, ...]) -> tuple[float, ...]:
        return tuple(round(value, 12) for value in belief)

    def value(
        self,
        belief: tuple[float, ...],
        counts: tuple[tuple[str, int], ...],
        budget: Budget,
    ) -> tuple[float, str | None]:
        return self._value(
            self._belief_key(belief),
            tuple(counts),
            tuple(budget.spent.values),
        )

    @lru_cache(maxsize=None)
    def _value(
        self,
        belief: tuple[float, ...],
        counts: tuple[tuple[str, int], ...],
        spent_values: tuple[tuple[str, float], ...],
    ) -> tuple[float, str | None]:
        budget = Budget(
            self._tests[0].cost.schema,
            self.view.budget_limits,
            self._tests[0].cost.schema.vector(dict(spent_values)),
        )
        _, stop_value = best_submission(
            belief, self.view.hypotheses, self.view.abstain_loss
        )
        best_value = stop_value
        best_action: str | None = None
        count_map = dict(counts)
        if sum(count_map.values()) >= self.view.max_steps - 1:
            return best_value, best_action
        for test in self._tests:
            if count_map[test.action_id] >= test.repeat_limit or not budget.can_afford(test.cost):
                continue
            next_budget = budget.charge(test.cost)
            next_counts_map = dict(count_map)
            next_counts_map[test.action_id] += 1
            next_counts = tuple(
                (item.action_id, next_counts_map[item.action_id]) for item in self._tests
            )
            future = 0.0
            for event, probability in outcome_probabilities(belief, test):
                if event == "__failure__" and test.failure_terminates:
                    event_value = self.view.abstain_loss
                else:
                    next_belief = posterior(belief, test, event)
                    event_value = self._value(
                        self._belief_key(next_belief),
                        next_counts,
                        tuple(next_budget.spent.values),
                    )[0]
                future += probability * event_value
            candidate = (
                self.view.cost_weight * test.cost.get(self.view.primary_resource)
                + future
            )
            if candidate < best_value - 1e-12:
                best_value = candidate
                best_action = test.action_id
        return best_value, best_action


class OracleReferencePolicy(BeliefPolicy):
    """Evaluation instrument; never part of the normal policy suite."""

    name = "oracle_reference"
    access_class = "evaluator_only"
    assumptions = (
        "exact dynamic programming over the frozen small public generative model",
        "used only by evaluation and never exposed as a normal policy input",
    )

    def __init__(self):
        self.solver: OracleSolver | None = None

    def reset(self, view, initial_observations, seed):
        self.solver = OracleSolver(view)
        return super().reset(view, initial_observations, seed)

    def should_stop(self, state: BeliefState, context: DecisionContext) -> bool:
        if self.solver is None:
            raise RuntimeError("oracle solver was not initialized")
        return self.solver.value(state.belief, state.counts, context.remaining_budget)[1] is None

    def select_action(self, state: BeliefState, context: DecisionContext):
        if self.solver is None:
            raise RuntimeError("oracle solver was not initialized")
        action_id = self.solver.value(
            state.belief, state.counts, context.remaining_budget
        )[1]
        if action_id is None:
            raise AssertionError("select_action called when oracle chose STOP")
        return next(item for item in context.legal_actions if item.action_id == action_id)
