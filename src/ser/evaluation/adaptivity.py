"""Counterfactual audit of whether realized observations change policy choices."""

from __future__ import annotations

from collections import defaultdict

from ser.core.types import (
    ActionResult,
    Budget,
    Observation,
    TerminationCause,
    TerminationEvent,
)
from ser.microgym.model import ProblemSpec, outcome_probabilities
from ser.policies.base import DecisionContext


def _choice(action) -> str:
    return "STOP" if action.kind == "stop" else str(action.target_id)


def _legal(view, state, budget):
    return tuple(
        test.descriptor()
        for test in view.tests
        if state.count(test.action_id) < test.repeat_limit
        and budget.can_afford(test.cost)
    )


def audit_policy(problem: ProblemSpec, policy, policy_seed: int = 12345) -> dict:
    """Enumerate reachable public outcomes and count observation-dependent choices."""

    order = tuple(test.public.action_id for test in problem.tests)
    view = problem.public_view(order)
    budget = Budget.create(view.tests[0].cost.schema, dict(view.budget_limits))
    branching_nodes = 0
    decision_nodes = 0
    examples: list[dict] = []
    visited_paths = 0

    def choose(state, current_budget, observations, step):
        context = DecisionContext(
            view,
            _legal(view, state, current_budget),
            current_budget,
            tuple(observations),
            step,
        )
        return policy.choose(state, context)

    def descend(state, current_budget, observations, step, path):
        nonlocal branching_nodes, decision_nodes, visited_paths
        if step > view.max_steps:
            return
        action = choose(state, current_budget, observations, step)
        if action.kind == "stop":
            return
        test = view.test(action.target_id)
        children = []
        for event, probability in outcome_probabilities(state.belief, test):
            if probability <= 1e-15:
                continue
            termination = None
            released = ()
            status = "completed"
            error = None
            if event == "__failure__":
                status = "failed"
                error = "declared_action_failure"
                if test.failure_terminates:
                    termination = TerminationEvent(
                        TerminationCause.ENVIRONMENT_TERMINATION,
                        step,
                        "counterfactual_declared_failure",
                    )
            else:
                released = (
                    Observation(
                        f"cf-o-{step}",
                        {"model_id": action.target_id, "value": event},
                        "counterfactual_public_model",
                        step,
                        f"cf-r-{step}",
                        "declared_likelihood_model",
                    ),
                )
            result = ActionResult(
                f"cf-r-{step}",
                action.action_id,
                status,
                test.cost,
                released,
                error,
                termination,
            )
            next_state = policy.update(state, action, result, view)
            next_budget = current_budget.charge(test.cost)
            next_observations = [*observations, *released]
            if termination is None and step + 1 <= view.max_steps:
                next_action = choose(
                    next_state,
                    next_budget,
                    next_observations,
                    step + 1,
                )
                children.append(
                    (event, _choice(next_action), next_state, next_budget, next_observations)
                )
        if len(children) >= 2:
            decision_nodes += 1
            choices = {item[1] for item in children}
            if len(choices) > 1:
                branching_nodes += 1
                if len(examples) < 10:
                    examples.append(
                        {
                            "path": list(path),
                            "action": action.target_id,
                            "outcome_to_next_choice": {
                                event: next_choice for event, next_choice, *_ in children
                            },
                        }
                    )
        for event, _, next_state, next_budget, next_observations in children:
            visited_paths += 1
            descend(
                next_state,
                next_budget,
                next_observations,
                step + 1,
                (*path, f"{action.target_id}={event}"),
            )

    root_children = []
    initial = view.initial_test
    for event, probability in outcome_probabilities(view.prior, initial):
        if event == "__failure__" or probability <= 1e-15:
            continue
        observation = Observation(
            "cf-o-0",
            {"model_id": initial.action_id, "value": event},
            "counterfactual_initial_model",
            0,
            None,
            "declared_likelihood_model",
        )
        state = policy.reset(view, (observation,), policy_seed)
        action = choose(state, budget, [observation], 1)
        root_children.append((event, _choice(action), state, [observation]))
    if len(root_children) >= 2:
        decision_nodes += 1
        choices = {item[1] for item in root_children}
        if len(choices) > 1:
            branching_nodes += 1
            examples.append(
                {
                    "path": [],
                    "action": "initial_observation",
                    "outcome_to_next_choice": {
                        event: next_choice for event, next_choice, *_ in root_children
                    },
                }
            )
    for event, _, state, observations in root_children:
        visited_paths += 1
        descend(state, budget, observations, 1, (f"initial={event}",))
    return {
        "problem_id": problem.problem_id,
        "family": problem.family,
        "counterfactual_decision_nodes": decision_nodes,
        "observation_conditioned_branching_nodes": branching_nodes,
        "branching_rate": branching_nodes / decision_nodes if decision_nodes else 0.0,
        "visited_public_paths": visited_paths,
        "examples": examples,
    }


def audit_suite(problems: tuple[ProblemSpec, ...], policies: tuple) -> dict:
    per_policy = {}
    for policy in policies:
        records = [audit_policy(problem, policy) for problem in problems]
        decisions = sum(item["counterfactual_decision_nodes"] for item in records)
        branches = sum(item["observation_conditioned_branching_nodes"] for item in records)
        per_family = defaultdict(lambda: {"decision_nodes": 0, "branching_nodes": 0})
        for item in records:
            per_family[item["family"]]["decision_nodes"] += item[
                "counterfactual_decision_nodes"
            ]
            per_family[item["family"]]["branching_nodes"] += item[
                "observation_conditioned_branching_nodes"
            ]
        per_policy[policy.name] = {
            "counterfactual_decision_nodes": decisions,
            "observation_conditioned_branching_nodes": branches,
            "branching_rate": branches / decisions if decisions else 0.0,
            "by_family": dict(sorted(per_family.items())),
            "examples": [
                {"problem_id": item["problem_id"], **example}
                for item in records
                for example in item["examples"]
            ][:20],
        }
    return {
        "schema_version": 1,
        "method": "exhaustively enumerate policy-visible outcomes in the declared public model and test whether alternative realized outcomes at the same public decision node change the next policy action",
        "interpretation": "This counterfactual audit controls identifiers, presentation order, environment seed, and hidden truth. It is a structural diagnostic, not an outcome estimate.",
        "policies": per_policy,
    }
