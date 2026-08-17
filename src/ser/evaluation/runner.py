"""Deterministic experiment runner and evaluator/controller firewall."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, replace

from ser.core.types import (
    Action,
    ActionResult,
    Budget,
    Outcome,
    TerminationCause,
    TerminationEvent,
    Trace,
    Transition,
    canonical_json,
    content_hash,
)
from ser.microgym.environment import MicroGymEnvironment, evaluator_truth
from ser.microgym.model import (
    EpisodeSpec,
    POLICY_RANDOMNESS_MASTER_SEED,
    ProblemSpec,
    RESOURCE_SCHEMA,
    best_submission,
)
from ser.microgym.oracle import OracleSolver
from ser.policies.base import BeliefState, DecisionContext, update_for_observation


def _policy_seed(episode_id: str, policy_name: str) -> int:
    """Return policy-only randomness, independent of environment realization RNG."""

    payload = (
        f"microgym-policy-v1|{POLICY_RANDOMNESS_MASTER_SEED}|{episode_id}|{policy_name}"
    ).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


@dataclass(frozen=True)
class RunRecord:
    run_id: str
    episode_id: str
    problem_id: str
    family: str
    policy_name: str
    policy_access_class: str
    policy_assumptions: tuple[str, ...]
    policy_visible_model_access: str
    policy_randomness_seed: int
    trace: Trace
    final_submission: str | None
    valid: bool
    invalid_reason: str | None


def _terminate_trace(trace: Trace, event: TerminationEvent) -> Trace:
    return Trace(
        trace.schema_version,
        trace.episode_id,
        trace.initial_observations,
        trace.transitions,
        event,
    )


def run_episode(
    problem: ProblemSpec,
    episode: EpisodeSpec,
    policy,
    *,
    allow_evaluator_policy: bool = False,
) -> RunRecord:
    if policy.access_class != "public_episode" and not allow_evaluator_policy:
        raise PermissionError("evaluator-only policies cannot run as normal policies")
    environment = MicroGymEnvironment(problem, episode)
    interface = environment.reset()
    view = interface.view
    budget = interface.budget
    observations = list(interface.observations)
    trace = Trace(1, episode.episode_id, interface.observations)
    run_id = f"{episode.episode_id}--{policy.name}"
    valid = True
    invalid_reason = None
    submission = None
    try:
        state = policy.reset(
            view,
            interface.observations,
            _policy_seed(episode.episode_id, policy.name),
        )
    except Exception as exc:
        event = TerminationEvent(
            TerminationCause.RUNNER_EVALUATOR_TRUNCATION,
            0,
            "policy_reset_failure",
        )
        return RunRecord(
            run_id,
            episode.episode_id,
            problem.problem_id,
            problem.family,
            policy.name,
            policy.access_class,
            tuple(policy.assumptions),
            view.public_model_access,
            _policy_seed(episode.episode_id, policy.name),
            _terminate_trace(trace, event),
            None,
            False,
            f"policy_reset_failure:{type(exc).__name__}",
        )

    for step in range(1, problem.max_steps + 1):
        legal = environment.available_actions(budget)
        context = DecisionContext(view, legal, budget, tuple(observations), step)
        state_before_ref = content_hash(policy.state_record(state))
        budget_before = budget.remaining()
        try:
            action = policy.choose(state, context)
        except Exception as exc:
            event = TerminationEvent(
                TerminationCause.RUNNER_EVALUATOR_TRUNCATION,
                step,
                "policy_choose_failure",
            )
            trace = _terminate_trace(trace, event)
            valid = False
            invalid_reason = f"policy_choose_failure:{type(exc).__name__}"
            break
        if not isinstance(action, Action):
            action = Action(f"a-{step:03d}", "invalid")
        result = environment.execute(action, budget, step)
        if result.status == "rejected":
            valid = False
            invalid_reason = result.error or "rejected_action"
            result = replace(
                result,
                termination=TerminationEvent(
                    TerminationCause.RUNNER_EVALUATOR_TRUNCATION,
                    step,
                    "invalid_policy_action",
                ),
            )
        if not budget.can_afford(result.cost):
            valid = False
            invalid_reason = "actual_cost_exceeded_budget"
            result = replace(
                result,
                termination=TerminationEvent(
                    TerminationCause.RUNNER_EVALUATOR_TRUNCATION,
                    step,
                    "actual_cost_exceeded_budget",
                ),
            )
        else:
            budget = budget.charge(result.cost)
        if result.termination is None and step == problem.max_steps:
            result = replace(
                result,
                termination=TerminationEvent(
                    TerminationCause.RUNNER_EVALUATOR_TRUNCATION,
                    step,
                    "maximum_episode_steps",
                ),
            )
        try:
            next_state = policy.update(state, action, result, view)
        except Exception as exc:
            valid = False
            invalid_reason = f"policy_update_failure:{type(exc).__name__}"
            result = replace(
                result,
                termination=TerminationEvent(
                    TerminationCause.RUNNER_EVALUATOR_TRUNCATION,
                    step,
                    "policy_update_failure",
                ),
            )
            next_state = state
        observations.extend(result.observations)
        transition = Transition(
            transition_id=f"t-{step:03d}",
            step=step,
            state_before_ref=state_before_ref,
            action=action,
            result=result,
            state_after_ref=content_hash(policy.state_record(next_state)),
            budget_before=budget_before,
            budget_after=budget.remaining(),
            randomness_ref=content_hash(
                {
                    "episode_id": episode.episode_id,
                    "step": step,
                    "target": action.target_id,
                }
            ),
        )
        trace = trace.append(transition)
        state = next_state
        if action.kind == "stop":
            submission = action.submission
        if result.termination is not None:
            break

    if trace.termination is None:
        event = TerminationEvent(
            TerminationCause.RUNNER_EVALUATOR_TRUNCATION,
            problem.max_steps,
            "runner_fell_through_without_termination",
        )
        trace = _terminate_trace(trace, event)
        valid = False
        invalid_reason = invalid_reason or "runner_fell_through"
    return RunRecord(
        run_id,
        episode.episode_id,
        problem.problem_id,
        problem.family,
        policy.name,
        policy.access_class,
        tuple(policy.assumptions),
        view.public_model_access,
        _policy_seed(episode.episode_id, policy.name),
        trace,
        submission,
        valid,
        invalid_reason,
    )


def _raw_cost(trace: Trace):
    total = RESOURCE_SCHEMA.vector()
    for transition in trace.transitions:
        total = total + transition.result.cost
    return total


def _realized_loss(
    submission: str | None, hidden_state: str, abstain_loss: float
) -> tuple[bool, bool, float]:
    abstained = submission is None
    correct = submission == hidden_state
    if abstained:
        loss = abstain_loss
    else:
        loss = 0.0 if correct else 1.0
    return correct, abstained, loss


def _stopping_analysis(
    run: RunRecord,
    problem: ProblemSpec,
    episode: EpisodeSpec,
) -> tuple[float, bool, int, float]:
    view = problem.public_view(episode.action_order)
    belief = view.prior
    for observation in run.trace.initial_observations:
        belief = update_for_observation(belief, observation, view)
    counts = tuple((test.action_id, 0) for test in view.tests)
    budget = Budget.create(RESOURCE_SCHEMA, dict(view.budget_limits))
    solver = OracleSolver(view)
    stopping_regret = 0.0
    premature = False
    unnecessary = 0
    avoidable_cost = 0.0
    for transition in run.trace.transitions:
        oracle_value, oracle_action = solver.value(belief, counts, budget)
        if transition.action.kind == "stop" and oracle_action is not None:
            stop_value = best_submission(
                belief, view.hypotheses, view.abstain_loss
            )[1]
            stopping_regret += max(0.0, stop_value - oracle_value)
            premature = True
        elif transition.action.kind == "acquire" and oracle_action is None:
            unnecessary += 1
            avoidable_cost += transition.result.cost.get(view.primary_resource)
        budget = budget.charge(transition.result.cost)
        if transition.action.kind == "acquire" and transition.action.target_id:
            count_map = dict(counts)
            count_map[transition.action.target_id] += 1
            counts = tuple((test.action_id, count_map[test.action_id]) for test in view.tests)
        for observation in transition.result.observations:
            belief = update_for_observation(belief, observation, view)
    return stopping_regret, premature, unnecessary, avoidable_cost


def evaluate_run(
    run: RunRecord,
    oracle_run: RunRecord,
    problem: ProblemSpec,
    episode: EpisodeSpec,
) -> Outcome:
    """Evaluator-only outcome computation; never called from a policy path."""

    environment = MicroGymEnvironment(problem, episode)
    environment.reset()
    hidden_state = evaluator_truth(environment)
    correct, abstained, decision_loss = _realized_loss(
        run.final_submission, hidden_state, problem.abstain_loss
    )
    oracle_correct, oracle_abstained, oracle_loss = _realized_loss(
        oracle_run.final_submission, hidden_state, problem.abstain_loss
    )
    del oracle_correct, oracle_abstained
    resources = _raw_cost(run.trace)
    oracle_resources = _raw_cost(oracle_run.trace)
    combined = decision_loss + problem.cost_weight * resources.get(problem.primary_resource)
    oracle_combined = oracle_loss + problem.cost_weight * oracle_resources.get(problem.primary_resource)
    stop_regret, premature, unnecessary, avoidable = _stopping_analysis(
        run, problem, episode
    )
    return Outcome(
        valid=run.valid,
        invalid_reason=run.invalid_reason,
        submission=run.final_submission,
        correct=correct,
        abstained=abstained,
        decision_loss=decision_loss,
        raw_resources=resources,
        combined_objective=combined,
        decision_regret=decision_loss - oracle_loss,
        combined_regret=combined - oracle_combined,
        stopping_regret=stop_regret,
        premature_stop=premature,
        unnecessary_actions=unnecessary,
        avoidable_resource_cost=avoidable,
    )


def replay_trace(problem: ProblemSpec, episode: EpisodeSpec, trace: Trace) -> tuple[bool, str]:
    """Re-execute the frozen action sequence and compare public results/costs."""

    environment = MicroGymEnvironment(problem, episode)
    interface = environment.reset()
    if canonical_json(interface.observations) != canonical_json(trace.initial_observations):
        return False, "initial_observation_mismatch"
    budget = interface.budget
    if len(trace.transitions) > problem.max_steps:
        return False, "too_many_transitions"
    for expected in trace.transitions:
        actual = environment.execute(expected.action, budget, expected.step)
        if actual.termination is None and expected.step == problem.max_steps:
            actual = replace(
                actual,
                termination=TerminationEvent(
                    TerminationCause.RUNNER_EVALUATOR_TRUNCATION,
                    expected.step,
                    "maximum_episode_steps",
                ),
            )
        if expected.result.status == "rejected" and actual.termination is None:
            actual = replace(
                actual,
                termination=TerminationEvent(
                    TerminationCause.RUNNER_EVALUATOR_TRUNCATION,
                    expected.step,
                    "invalid_policy_action",
                ),
            )
        if canonical_json(actual) != canonical_json(expected.result):
            return False, f"result_mismatch_at_step_{expected.step}"
        if not budget.can_afford(actual.cost):
            return False, f"budget_mismatch_at_step_{expected.step}"
        budget = budget.charge(actual.cost)
    return True, "exact_public_replay"
