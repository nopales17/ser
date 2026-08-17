"""Deterministic MicroGym environment with an explicit public projection."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from ser.core.types import (
    Action,
    ActionDescriptor,
    ActionResult,
    Budget,
    Observation,
    TerminationCause,
    TerminationEvent,
)

from .model import EpisodeSpec, ProblemSpec, PublicProblemView, RESOURCE_SCHEMA, TestSpec


def deterministic_uniform(seed: int, slot: str, occurrence: int, channel: str) -> float:
    payload = f"microgym-v1|{seed}|{slot}|{occurrence}|{channel}".encode("utf-8")
    integer = int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")
    return integer / 2**64


def _draw(probabilities: tuple[float, ...], uniform: float) -> int:
    cumulative = 0.0
    for index, probability in enumerate(probabilities):
        cumulative += probability
        if uniform < cumulative or index == len(probabilities) - 1:
            return index
    raise AssertionError("unreachable probability draw")


@dataclass(frozen=True)
class EpisodeInterface:
    observations: tuple[Observation, ...]
    budget: Budget
    view: PublicProblemView


class MicroGymEnvironment:
    """Environment-owned hidden truth; only ``public_view`` crosses the boundary."""

    version = "microgym-environment-v1"

    def __init__(self, problem: ProblemSpec, episode: EpisodeSpec):
        if episode.problem_id != problem.problem_id:
            raise ValueError("episode/problem mismatch")
        if episode.hidden_state not in problem.hypotheses:
            raise ValueError("episode hidden state is not in the problem")
        self._problem = problem
        self._episode = episode
        self._hidden_index = problem.hypotheses.index(episode.hidden_state)
        self._counts: dict[str, int] = {test.public.action_id: 0 for test in problem.tests}
        self._terminated = False
        self._view = problem.public_view(episode.action_order)

    @property
    def public_view(self) -> PublicProblemView:
        return self._view

    def _sample(self, test: TestSpec, occurrence: int) -> tuple[str, str | None]:
        failure_uniform = deterministic_uniform(
            self._episode.environment_seed, test.rng_slot, occurrence, "failure"
        )
        if failure_uniform < test.public.failure_probability:
            return "failed", None
        outcome_uniform = deterministic_uniform(
            self._episode.environment_seed, test.rng_slot, occurrence, "outcome"
        )
        row = test.public.likelihoods[self._hidden_index]
        return "completed", test.public.outcomes[_draw(row, outcome_uniform)]

    def reset(self) -> EpisodeInterface:
        if self._terminated:
            raise ValueError("cannot reset a terminated environment instance")
        status, outcome = self._sample(self._problem.initial_test, 0)
        if status != "completed" or outcome is None:
            raise ValueError("initial observation models cannot fail")
        observation = Observation(
            observation_id="o-000",
            payload={"model_id": self._problem.initial_test.public.action_id, "value": outcome},
            provenance="environment_reset",
            release_step=0,
            source_result_id=None,
            reliability="declared_likelihood_model",
        )
        budget = Budget.create(RESOURCE_SCHEMA, dict(self._problem.budget_limits))
        return EpisodeInterface((observation,), budget, self._view)

    def available_actions(self, budget: Budget) -> tuple[ActionDescriptor, ...]:
        if self._terminated:
            return ()
        output = []
        for public_test in self._view.tests:
            if (
                self._counts[public_test.action_id] < public_test.repeat_limit
                and budget.can_afford(public_test.cost)
            ):
                output.append(public_test.descriptor())
        return tuple(output)

    def execute(self, action: Action, budget: Budget, step: int) -> ActionResult:
        zero = RESOURCE_SCHEMA.vector()
        if self._terminated:
            return ActionResult(
                f"r-{step:03d}",
                action.action_id,
                "rejected",
                zero,
                error="environment_already_terminated",
                termination=TerminationEvent(
                    TerminationCause.ENVIRONMENT_TERMINATION,
                    step,
                    "environment_already_terminated",
                ),
            )
        if action.kind == "stop":
            self._terminated = True
            return ActionResult(
                f"r-{step:03d}",
                action.action_id,
                "completed",
                zero,
                termination=TerminationEvent(
                    TerminationCause.CONTROLLER_STOP, step, "policy_selected_stop"
                ),
            )
        legal = {item.action_id: item for item in self.available_actions(budget)}
        if action.kind != "acquire" or action.target_id not in legal:
            return ActionResult(
                f"r-{step:03d}",
                action.action_id,
                "rejected",
                zero,
                error="illegal_or_unaffordable_action",
            )
        test = self._problem.restricted_test(action.target_id)
        occurrence = self._counts[action.target_id]
        self._counts[action.target_id] += 1
        status, outcome = self._sample(test, occurrence)
        termination = None
        error = None
        observations: tuple[Observation, ...] = ()
        if status == "failed":
            error = "declared_action_failure"
            if test.public.failure_terminates:
                self._terminated = True
                termination = TerminationEvent(
                    TerminationCause.ENVIRONMENT_TERMINATION,
                    step,
                    "action_failure_terminated_environment",
                )
        else:
            result_id = f"r-{step:03d}"
            observations = (
                Observation(
                    observation_id=f"o-{step:03d}",
                    payload={"model_id": action.target_id, "value": outcome},
                    provenance=f"action_result:{result_id}",
                    release_step=step,
                    source_result_id=result_id,
                    reliability="declared_likelihood_model",
                ),
            )
        return ActionResult(
            f"r-{step:03d}",
            action.action_id,
            status,
            test.public.cost,
            observations,
            error,
            termination,
        )

    def restricted_truth(self, token: object) -> str:
        """Return truth only to the evaluator token owned by the runner."""

        if token is not _EVALUATOR_TOKEN:
            raise PermissionError("hidden truth requires evaluator-only access")
        return self._episode.hidden_state


_EVALUATOR_TOKEN = object()


def evaluator_truth(environment: MicroGymEnvironment) -> str:
    """Evaluator-side helper intentionally absent from the policy interface."""

    return environment.restricted_truth(_EVALUATOR_TOKEN)
