"""Public and restricted MicroGym generative-model records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from ser.core.types import (
    ActionDescriptor,
    ResourceDimension,
    ResourceSchema,
    ResourceVector,
)


RESOURCE_SCHEMA = ResourceSchema(
    (
        ResourceDimension("tests", "count"),
        ResourceDimension("synthetic_cost_units", "unit"),
        ResourceDimension("latency_steps", "step"),
    )
)

# Separate named randomness domains. The population seed chooses episode layout,
# the environment seed realizes observations/failures, and the policy seed is
# the only seed disclosed to a normal policy.
POPULATION_GENERATION_SEED = 31_415_926
ENVIRONMENT_REALIZATION_MASTER_SEED = 27_182_818
POLICY_RANDOMNESS_MASTER_SEED = 16_180_339


def _normalize(values: Iterable[float]) -> tuple[float, ...]:
    vector = tuple(float(value) for value in values)
    total = sum(vector)
    if total <= 0:
        raise ValueError("probability vector must have positive mass")
    return tuple(value / total for value in vector)


@dataclass(frozen=True)
class PublicTestModel:
    action_id: str
    outcomes: tuple[str, ...]
    likelihoods: tuple[tuple[float, ...], ...]
    cost: ResourceVector
    repeat_limit: int = 1
    failure_probability: float = 0.0
    failure_terminates: bool = False
    public_score: float = 0.0

    def __post_init__(self) -> None:
        if not self.action_id or not self.outcomes or self.repeat_limit < 1:
            raise ValueError("test model identity, outcomes, and repeat limit are required")
        if len(self.outcomes) != len(set(self.outcomes)):
            raise ValueError("test outcome identifiers must be unique")
        if not 0 <= self.failure_probability < 1:
            raise ValueError("failure probability must be in [0, 1)")
        for row in self.likelihoods:
            if len(row) != len(self.outcomes) or any(value < 0 for value in row):
                raise ValueError("likelihood rows must match outcomes and be nonnegative")
            if abs(sum(row) - 1.0) > 1e-9:
                raise ValueError("each likelihood row must sum to one")

    def descriptor(self) -> ActionDescriptor:
        return ActionDescriptor(
            self.action_id,
            "acquire",
            self.cost,
            self.repeat_limit,
            self.public_score,
        )

    def to_dict(self) -> dict:
        return {
            "action_id": self.action_id,
            "outcomes": list(self.outcomes),
            "likelihoods": [list(row) for row in self.likelihoods],
            "cost": self.cost.as_dict(),
            "repeat_limit": self.repeat_limit,
            "failure_probability": self.failure_probability,
            "failure_terminates": self.failure_terminates,
            "public_score": self.public_score,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, object]) -> PublicTestModel:
        return cls(
            action_id=str(raw["action_id"]),
            outcomes=tuple(str(item) for item in raw["outcomes"]),
            likelihoods=tuple(
                tuple(float(value) for value in row) for row in raw["likelihoods"]
            ),
            cost=RESOURCE_SCHEMA.vector(raw["cost"]),
            repeat_limit=int(raw["repeat_limit"]),
            failure_probability=float(raw["failure_probability"]),
            failure_terminates=bool(raw["failure_terminates"]),
            public_score=float(raw["public_score"]),
        )


@dataclass(frozen=True)
class TestSpec:
    public: PublicTestModel
    rng_slot: str

    def to_dict(self) -> dict:
        return {"public": self.public.to_dict(), "rng_slot": self.rng_slot}

    @classmethod
    def from_dict(cls, raw: Mapping[str, object]) -> TestSpec:
        return cls(PublicTestModel.from_dict(raw["public"]), str(raw["rng_slot"]))


@dataclass(frozen=True)
class PublicProblemView:
    problem_id: str
    family: str
    version: str
    hypotheses: tuple[str, ...]
    prior: tuple[float, ...]
    initial_test: PublicTestModel
    tests: tuple[PublicTestModel, ...]
    budget_limits: tuple[tuple[str, float], ...]
    primary_resource: str
    cost_weight: float
    abstain_loss: float
    max_steps: int
    public_model_access: str
    assumptions: tuple[str, ...]

    def test(self, action_id: str) -> PublicTestModel:
        if action_id == self.initial_test.action_id:
            return self.initial_test
        for test in self.tests:
            if test.action_id == action_id:
                return test
        raise KeyError(action_id)


@dataclass(frozen=True)
class ProblemSpec:
    problem_id: str
    family: str
    version: str
    description: str
    hypotheses: tuple[str, ...]
    prior: tuple[float, ...]
    initial_test: TestSpec
    tests: tuple[TestSpec, ...]
    budget_limits: tuple[tuple[str, float], ...]
    primary_resource: str
    cost_weight: float
    abstain_loss: float
    max_steps: int
    assumptions: tuple[str, ...]

    def __post_init__(self) -> None:
        if len(self.hypotheses) < 2 or len(self.hypotheses) != len(set(self.hypotheses)):
            raise ValueError("problems require at least two unique hypotheses")
        if len(self.prior) != len(self.hypotheses) or abs(sum(self.prior) - 1.0) > 1e-9:
            raise ValueError("prior must match hypotheses and sum to one")
        all_tests = (self.initial_test,) + self.tests
        if any(len(test.public.likelihoods) != len(self.hypotheses) for test in all_tests):
            raise ValueError("each test needs one likelihood row per hypothesis")
        action_ids = [test.public.action_id for test in all_tests]
        if len(action_ids) != len(set(action_ids)):
            raise ValueError("action identifiers must be unique")
        if self.primary_resource not in RESOURCE_SCHEMA.names:
            raise ValueError("primary resource must belong to the resource schema")
        if self.cost_weight < 0 or not 0 <= self.abstain_loss <= 1 or self.max_steps < 1:
            raise ValueError("invalid objective or stopping parameters")

    def public_view(self, action_order: tuple[str, ...]) -> PublicProblemView:
        tests_by_id = {test.public.action_id: test.public for test in self.tests}
        if set(action_order) != set(tests_by_id) or len(action_order) != len(tests_by_id):
            raise ValueError("episode action order must be a permutation of tests")
        return PublicProblemView(
            problem_id=self.problem_id,
            family=self.family,
            version=self.version,
            hypotheses=self.hypotheses,
            prior=self.prior,
            initial_test=self.initial_test.public,
            tests=tuple(tests_by_id[action_id] for action_id in action_order),
            budget_limits=self.budget_limits,
            primary_resource=self.primary_resource,
            cost_weight=self.cost_weight,
            abstain_loss=self.abstain_loss,
            max_steps=self.max_steps,
            public_model_access="full_declared_likelihoods",
            assumptions=self.assumptions,
        )

    def restricted_test(self, action_id: str) -> TestSpec:
        if action_id == self.initial_test.public.action_id:
            return self.initial_test
        for test in self.tests:
            if test.public.action_id == action_id:
                return test
        raise KeyError(action_id)

    def to_dict(self) -> dict:
        return {
            "problem_id": self.problem_id,
            "family": self.family,
            "version": self.version,
            "description": self.description,
            "hypotheses": list(self.hypotheses),
            "prior": list(self.prior),
            "initial_test": self.initial_test.to_dict(),
            "tests": [test.to_dict() for test in self.tests],
            "budget_limits": dict(self.budget_limits),
            "primary_resource": self.primary_resource,
            "cost_weight": self.cost_weight,
            "abstain_loss": self.abstain_loss,
            "max_steps": self.max_steps,
            "assumptions": list(self.assumptions),
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, object]) -> ProblemSpec:
        return cls(
            problem_id=str(raw["problem_id"]),
            family=str(raw["family"]),
            version=str(raw["version"]),
            description=str(raw["description"]),
            hypotheses=tuple(str(item) for item in raw["hypotheses"]),
            prior=_normalize(raw["prior"]),
            initial_test=TestSpec.from_dict(raw["initial_test"]),
            tests=tuple(TestSpec.from_dict(item) for item in raw["tests"]),
            budget_limits=tuple(
                (name, float(value)) for name, value in sorted(raw["budget_limits"].items())
            ),
            primary_resource=str(raw["primary_resource"]),
            cost_weight=float(raw["cost_weight"]),
            abstain_loss=float(raw["abstain_loss"]),
            max_steps=int(raw["max_steps"]),
            assumptions=tuple(str(item) for item in raw["assumptions"]),
        )


@dataclass(frozen=True)
class EpisodeSpec:
    episode_id: str
    problem_id: str
    hidden_state: str
    environment_seed: int
    action_order: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "episode_id": self.episode_id,
            "problem_id": self.problem_id,
            "hidden_state": self.hidden_state,
            "environment_realization_seed": self.environment_seed,
            "action_order": list(self.action_order),
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, object]) -> EpisodeSpec:
        return cls(
            str(raw["episode_id"]),
            str(raw["problem_id"]),
            str(raw["hidden_state"]),
            int(raw["environment_realization_seed"]),
            tuple(str(item) for item in raw["action_order"]),
        )


def outcome_probabilities(
    belief: tuple[float, ...], test: PublicTestModel
) -> tuple[tuple[str, float], ...]:
    success = 1.0 - test.failure_probability
    events = []
    if test.failure_probability:
        events.append(("__failure__", test.failure_probability))
    for outcome_index, outcome in enumerate(test.outcomes):
        probability = success * sum(
            belief[hypothesis_index] * test.likelihoods[hypothesis_index][outcome_index]
            for hypothesis_index in range(len(belief))
        )
        if probability > 1e-15:
            events.append((outcome, probability))
    return tuple(events)


def posterior(
    belief: tuple[float, ...], test: PublicTestModel, outcome: str
) -> tuple[float, ...]:
    if outcome == "__failure__":
        return belief
    outcome_index = test.outcomes.index(outcome)
    return _normalize(
        belief[index] * test.likelihoods[index][outcome_index]
        for index in range(len(belief))
    )


def best_submission(
    belief: tuple[float, ...], hypotheses: tuple[str, ...], abstain_loss: float
) -> tuple[str | None, float]:
    best_index = max(range(len(belief)), key=lambda index: belief[index])
    answer_loss = 1.0 - belief[best_index]
    if abstain_loss <= answer_loss + 1e-12:
        return None, abstain_loss
    return hypotheses[best_index], answer_loss


def expected_terminal_loss(
    belief: tuple[float, ...], test: PublicTestModel, hypotheses: tuple[str, ...], abstain_loss: float
) -> float:
    return sum(
        probability * best_submission(posterior(belief, test, event), hypotheses, abstain_loss)[1]
        for event, probability in outcome_probabilities(belief, test)
    )
