"""Structural interfaces that preserve environment/controller separation."""

from __future__ import annotations

from typing import Any, Protocol

from .types import Action, ActionDescriptor, ActionResult, Budget, Observation


class Environment(Protocol):
    def reset(self) -> Any: ...

    def available_actions(self, budget: Budget) -> tuple[ActionDescriptor, ...]: ...

    def execute(self, action: Action, budget: Budget, step: int) -> ActionResult: ...


class Policy(Protocol):
    name: str
    access_class: str

    def reset(self, view: Any, initial_observations: tuple[Observation, ...], seed: int) -> Any: ...

    def choose(self, state: Any, context: Any) -> Action: ...

    def update(self, state: Any, action: Action, result: ActionResult, view: Any) -> Any: ...

    def state_record(self, state: Any) -> Any: ...
