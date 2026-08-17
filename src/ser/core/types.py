"""Small immutable records for the Phase 2 semantic contracts.

These types intentionally implement only MicroGym's needs. They are not a
universal epistemic ontology and contain no graph, Signal, Scope algebra, or
confidence calculus.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import math
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


def _jsonable(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return {
            field.name: _jsonable(getattr(value, field.name))
            for field in dataclasses.fields(value)
        }
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in sorted(value.items())}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite floats are not serializable")
        return round(value, 12)
    if value is None or isinstance(value, (str, int, bool)):
        return value
    raise TypeError(f"unsupported deterministic value: {type(value).__name__}")


def canonical_json(value: Any) -> str:
    """Return the deterministic JSON representation used by traces/manifests."""

    return json.dumps(
        _jsonable(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )


def content_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ResourceDimension:
    name: str
    unit: str

    def __post_init__(self) -> None:
        if not self.name or not self.unit:
            raise ValueError("resource dimensions require a name and unit")


@dataclass(frozen=True)
class ResourceSchema:
    dimensions: tuple[ResourceDimension, ...]

    def __post_init__(self) -> None:
        names = [item.name for item in self.dimensions]
        if not names or len(names) != len(set(names)):
            raise ValueError("resource dimension names must be nonempty and unique")

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(item.name for item in self.dimensions)

    def vector(self, values: Mapping[str, float] | None = None) -> ResourceVector:
        supplied = dict(values or {})
        unknown = set(supplied) - set(self.names)
        if unknown:
            raise ValueError(f"dimensions absent from schema: {sorted(unknown)}")
        ordered = tuple((name, float(supplied.get(name, 0.0))) for name in self.names)
        return ResourceVector(self, ordered)


@dataclass(frozen=True)
class ResourceVector:
    schema: ResourceSchema
    values: tuple[tuple[str, float], ...]

    def __post_init__(self) -> None:
        if tuple(name for name, _ in self.values) != self.schema.names:
            raise ValueError("resource vector must follow its schema exactly")
        if any(value < 0 or not math.isfinite(value) for _, value in self.values):
            raise ValueError("resource quantities must be finite and nonnegative")

    def as_dict(self) -> dict[str, float]:
        return dict(self.values)

    def get(self, dimension: str) -> float:
        if dimension not in self.schema.names:
            raise KeyError(f"unmeasured resource dimension: {dimension}")
        return self.as_dict()[dimension]

    def __add__(self, other: ResourceVector) -> ResourceVector:
        if self.schema != other.schema:
            raise ValueError("cannot add vectors from different resource schemas")
        return self.schema.vector(
            {
                name: self.get(name) + other.get(name)
                for name in self.schema.names
            }
        )


@dataclass(frozen=True)
class Budget:
    schema: ResourceSchema
    limits: tuple[tuple[str, float], ...]
    spent: ResourceVector

    def __post_init__(self) -> None:
        names = [name for name, _ in self.limits]
        if len(names) != len(set(names)) or not set(names).issubset(self.schema.names):
            raise ValueError("budget limits must name a unique schema subset")
        if any(value < 0 or not math.isfinite(value) for _, value in self.limits):
            raise ValueError("budget limits must be finite and nonnegative")
        if self.spent.schema != self.schema:
            raise ValueError("budget and spent vector schemas differ")

    @classmethod
    def create(cls, schema: ResourceSchema, limits: Mapping[str, float]) -> Budget:
        ordered = tuple(
            (name, float(limits[name])) for name in schema.names if name in limits
        )
        return cls(schema, ordered, schema.vector())

    def can_afford(self, cost: ResourceVector) -> bool:
        if cost.schema != self.schema:
            return False
        limit_map = dict(self.limits)
        return all(
            self.spent.get(name) + cost.get(name) <= limit + 1e-12
            for name, limit in limit_map.items()
        )

    def charge(self, cost: ResourceVector) -> Budget:
        if not self.can_afford(cost):
            raise ValueError("resource cost exceeds remaining budget")
        return Budget(self.schema, self.limits, self.spent + cost)

    def remaining(self) -> tuple[tuple[str, float], ...]:
        return tuple(
            (name, limit - self.spent.get(name)) for name, limit in self.limits
        )


@dataclass(frozen=True)
class Observation:
    observation_id: str
    payload: Any
    provenance: str
    release_step: int
    source_result_id: str | None = None
    reliability: str | None = None


@dataclass(frozen=True)
class ActionDescriptor:
    action_id: str
    kind: str
    cost: ResourceVector
    repeat_limit: int
    public_score: float


@dataclass(frozen=True)
class Action:
    action_id: str
    kind: str
    target_id: str | None = None
    submission: str | None = None


class TerminationCause(str, Enum):
    CONTROLLER_STOP = "controller_stop"
    ENVIRONMENT_TERMINATION = "environment_termination"
    RUNNER_EVALUATOR_TRUNCATION = "runner_evaluator_truncation"


@dataclass(frozen=True)
class TerminationEvent:
    cause: TerminationCause
    step: int
    reason: str


@dataclass(frozen=True)
class ActionResult:
    result_id: str
    action_id: str
    status: str
    cost: ResourceVector
    observations: tuple[Observation, ...] = ()
    error: str | None = None
    termination: TerminationEvent | None = None


@dataclass(frozen=True)
class Transition:
    transition_id: str
    step: int
    state_before_ref: str
    action: Action
    result: ActionResult
    state_after_ref: str
    budget_before: tuple[tuple[str, float], ...]
    budget_after: tuple[tuple[str, float], ...]
    randomness_ref: str


@dataclass(frozen=True)
class Trace:
    schema_version: int
    episode_id: str
    initial_observations: tuple[Observation, ...]
    transitions: tuple[Transition, ...] = ()
    termination: TerminationEvent | None = None

    def append(self, transition: Transition) -> Trace:
        if self.termination is not None:
            raise ValueError("cannot append after trace termination")
        return Trace(
            self.schema_version,
            self.episode_id,
            self.initial_observations,
            self.transitions + (transition,),
            transition.result.termination,
        )


@dataclass(frozen=True)
class Outcome:
    valid: bool
    invalid_reason: str | None
    submission: str | None
    correct: bool
    abstained: bool
    decision_loss: float
    raw_resources: ResourceVector
    combined_objective: float
    decision_regret: float
    combined_regret: float
    stopping_regret: float
    premature_stop: bool
    unnecessary_actions: int
    avoidable_resource_cost: float
