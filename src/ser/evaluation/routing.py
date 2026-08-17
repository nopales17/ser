"""Exact planning and fixed-horizon execution for MicroGym routing-v1."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, replace

from ser.core.types import (
    Action,
    Budget,
    Observation,
    TerminationCause,
    TerminationEvent,
    Trace,
    Transition,
    content_hash,
)
from ser.microgym.environment import MicroGymEnvironment, evaluator_truth
from ser.microgym.model import (
    EpisodeSpec,
    ProblemSpec,
    PublicProblemView,
    RESOURCE_SCHEMA,
    best_submission,
    expected_terminal_loss,
    outcome_probabilities,
    posterior,
)
from ser.microgym.routing import ROUTING_POLICY_RANDOMNESS_MASTER_SEED
from ser.policies.adaptive import AdaptiveBeliefPolicy
from ser.policies.base import BeliefState, DecisionContext


TOLERANCE = 1e-12


@dataclass(frozen=True)
class RoutingOracle:
    problem_id: str
    open_loop_loss: float
    open_loop_action: str
    closed_loop_loss: float
    closed_loop_actions: tuple[tuple[str, str], ...]
    value_of_adaptivity: float
    eligible_conditional_node: bool
    candidate_expected_loss: float
    candidate_actions: tuple[tuple[str, str], ...]
    candidate_rankings: tuple[tuple[str, tuple[str, ...]], ...]
    adaptivity_capture: float | None
    belief_changed: bool
    action_ranking_changed: bool
    policy_action_changed: bool
    action_change_improved_value: bool


@dataclass(frozen=True)
class RoutingRun:
    run_id: str
    episode_id: str
    problem_id: str
    family: str
    policy_name: str
    policy_access_class: str
    policy_visible_model_access: str
    policy_randomness_seed: int
    trace: Trace
    final_submission: str | None
    valid: bool
    invalid_reason: str | None
    public_diagnostic: dict
    decision_loss: float
    correct: bool


def routing_policy_seed(episode_id: str, policy_name: str) -> int:
    payload = (
        f"microgym-routing-policy-v1|{ROUTING_POLICY_RANDOMNESS_MASTER_SEED}|"
        f"{episode_id}|{policy_name}"
    ).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


def _budget(view: PublicProblemView) -> Budget:
    return Budget.create(RESOURCE_SCHEMA, dict(view.budget_limits))


def _counts(view: PublicProblemView) -> tuple[tuple[str, int], ...]:
    return tuple((test.action_id, 0) for test in view.tests)


def _cue_observation(view: PublicProblemView, cue: str) -> Observation:
    return Observation(
        observation_id="counterfactual-cue",
        payload={"model_id": view.initial_test.action_id, "value": cue},
        provenance="counterfactual_public_model",
        release_step=0,
    )


def _belief_after_cue(view: PublicProblemView, cue: str) -> tuple[float, ...]:
    return posterior(view.prior, view.initial_test, cue)


def _action_loss(
    view: PublicProblemView, belief: tuple[float, ...], action_id: str
) -> float:
    return expected_terminal_loss(
        belief,
        view.test(action_id),
        view.hypotheses,
        view.abstain_loss,
    )


def _best_action(losses: dict[str, float]) -> tuple[str, float]:
    best_loss = min(losses.values())
    action_id = max(
        action for action, loss in losses.items() if abs(loss - best_loss) <= TOLERANCE
    )
    return action_id, best_loss


def _candidate_choice(
    view: PublicProblemView, cue: str
) -> tuple[str, tuple[str, ...], dict[str, float], tuple[float, ...]]:
    policy = AdaptiveBeliefPolicy()
    observation = _cue_observation(view, cue)
    state = policy.reset(view, (observation,), seed=0)
    context = DecisionContext(
        view,
        tuple(test.descriptor() for test in view.tests),
        _budget(view),
        (observation,),
        1,
    )
    scores = {
        descriptor.action_id: policy.one_step_score(state, descriptor, view)
        for descriptor in context.legal_actions
    }
    ranking = tuple(
        sorted(scores, key=lambda action: (scores[action], action), reverse=True)
    )
    return policy.select_action(state, context).action_id, ranking, scores, state.belief


def compute_routing_oracle(view: PublicProblemView) -> RoutingOracle:
    """Compute exact open, closed, and unchanged-candidate model values."""

    cue_events = outcome_probabilities(view.prior, view.initial_test)
    if any(cue == "__failure__" for cue, _ in cue_events):
        raise ValueError("routing cues may not fail")

    per_action_open_loss: dict[str, float] = {}
    for test in view.tests:
        per_action_open_loss[test.action_id] = sum(
            cue_probability
            * _action_loss(view, _belief_after_cue(view, cue), test.action_id)
            for cue, cue_probability in cue_events
        )
    open_action, open_loss = _best_action(per_action_open_loss)

    closed_actions: list[tuple[str, str]] = []
    candidate_actions: list[tuple[str, str]] = []
    candidate_rankings: list[tuple[str, tuple[str, ...]]] = []
    closed_loss = 0.0
    candidate_loss = 0.0
    posteriors: list[tuple[float, ...]] = []
    for cue, cue_probability in cue_events:
        belief = _belief_after_cue(view, cue)
        posteriors.append(belief)
        losses = {
            test.action_id: _action_loss(view, belief, test.action_id)
            for test in view.tests
        }
        closed_action, cue_closed_loss = _best_action(losses)
        candidate_action, ranking, _, candidate_belief = _candidate_choice(view, cue)
        if any(abs(left - right) > TOLERANCE for left, right in zip(belief, candidate_belief)):
            raise AssertionError("candidate and exact public posterior disagree")
        closed_actions.append((cue, closed_action))
        candidate_actions.append((cue, candidate_action))
        candidate_rankings.append((cue, ranking))
        closed_loss += cue_probability * cue_closed_loss
        candidate_loss += cue_probability * losses[candidate_action]

    voa = max(0.0, open_loss - closed_loss)
    eligible = voa > TOLERANCE and len({action for _, action in closed_actions}) > 1
    action_changed = len({action for _, action in candidate_actions}) > 1
    ranking_changed = len({ranking for _, ranking in candidate_rankings}) > 1
    belief_changed = len({tuple(round(value, 12) for value in item) for item in posteriors}) > 1
    improved = candidate_loss < open_loss - TOLERANCE
    capture = None if voa <= TOLERANCE else (open_loss - candidate_loss) / voa
    return RoutingOracle(
        problem_id=view.problem_id,
        open_loop_loss=open_loss,
        open_loop_action=open_action,
        closed_loop_loss=closed_loss,
        closed_loop_actions=tuple(closed_actions),
        value_of_adaptivity=voa,
        eligible_conditional_node=eligible,
        candidate_expected_loss=candidate_loss,
        candidate_actions=tuple(candidate_actions),
        candidate_rankings=tuple(candidate_rankings),
        adaptivity_capture=capture,
        belief_changed=belief_changed,
        action_ranking_changed=ranking_changed,
        policy_action_changed=action_changed,
        action_change_improved_value=improved,
    )


def _prior_landscape(view: PublicProblemView) -> tuple[dict[str, float], tuple[str, ...]]:
    policy = AdaptiveBeliefPolicy()
    state = BeliefState(view.prior, _counts(view), 0, 0)
    descriptors = tuple(test.descriptor() for test in view.tests)
    scores = {
        descriptor.action_id: policy.one_step_score(state, descriptor, view)
        for descriptor in descriptors
    }
    ranking = tuple(
        sorted(scores, key=lambda action: (scores[action], action), reverse=True)
    )
    return scores, ranking


def run_routing_episode(
    problem: ProblemSpec,
    episode: EpisodeSpec,
    policy_name: str,
) -> RoutingRun:
    """Run exactly one acquisition; STOP is never presented to the policy."""

    allowed = {
        "exact_open_loop": "public_episode",
        "adaptive_belief": "public_episode",
        "exact_closed_loop_oracle": "evaluator_only",
    }
    if policy_name not in allowed:
        raise ValueError(f"unknown routing policy: {policy_name}")

    environment = MicroGymEnvironment(problem, episode)
    # The open-loop plan is genuinely committed from the public experiment
    # definition before reset releases the realized cue.  Computing the same
    # invariant action after reset would be behaviorally equivalent but would
    # weaken the causal implementation boundary this benchmark is testing.
    pre_observation_view = problem.public_view(episode.action_order)
    oracle = compute_routing_oracle(pre_observation_view)
    committed_open_action = oracle.open_loop_action
    interface = environment.reset()
    view = interface.view
    if view != pre_observation_view:
        raise AssertionError("reset changed the precommitted public problem view")
    cue = str(interface.observations[0].payload["value"])
    policy = AdaptiveBeliefPolicy()
    seed = routing_policy_seed(episode.episode_id, policy_name)
    state = policy.reset(view, interface.observations, seed)
    legal = environment.available_actions(interface.budget)
    context = DecisionContext(
        view,
        legal,
        interface.budget,
        interface.observations,
        1,
    )
    prior_scores, prior_ranking = _prior_landscape(view)
    posterior_scores = {
        item.action_id: policy.one_step_score(state, item, view) for item in legal
    }
    posterior_ranking = tuple(
        sorted(
            posterior_scores,
            key=lambda action: (posterior_scores[action], action),
            reverse=True,
        )
    )

    if policy_name == "exact_open_loop":
        target = committed_open_action
        committed_before_observation = True
    elif policy_name == "adaptive_belief":
        target = policy.select_action(state, context).action_id
        committed_before_observation = False
    else:
        target = dict(oracle.closed_loop_actions)[cue]
        committed_before_observation = False

    action = Action("a-001", "acquire", target_id=target)
    state_before_ref = content_hash(policy.state_record(state))
    result = environment.execute(action, interface.budget, 1)
    valid = result.status == "completed" and len(result.observations) == 1
    invalid_reason = None if valid else (result.error or "routing_acquisition_failed")
    result = replace(
        result,
        termination=TerminationEvent(
            TerminationCause.RUNNER_EVALUATOR_TRUNCATION,
            1,
            "fixed_routing_horizon_complete",
        ),
    )
    budget_after = interface.budget.charge(result.cost)
    next_state = policy.update(state, action, result, view)
    trace = Trace(1, episode.episode_id, interface.observations).append(
        Transition(
            transition_id="t-001",
            step=1,
            state_before_ref=state_before_ref,
            action=action,
            result=result,
            state_after_ref=content_hash(policy.state_record(next_state)),
            budget_before=interface.budget.remaining(),
            budget_after=budget_after.remaining(),
            randomness_ref=content_hash(
                {
                    "benchmark": "microgym-routing-v1",
                    "episode_id": episode.episode_id,
                    "step": 1,
                    "target": target,
                }
            ),
        )
    )
    submission = policy.submission(next_state, view)
    hidden_state = evaluator_truth(environment)
    correct = submission == hidden_state
    decision_loss = 0.0 if correct else 1.0
    diagnostic = {
        "visibility": "public_episode",
        "cue_observation_id": interface.observations[0].observation_id,
        "belief_before_cue": list(view.prior),
        "belief_after_cue": list(state.belief),
        "action_scores_before_cue": prior_scores,
        "action_scores_after_cue": posterior_scores,
        "action_ranking_before_cue": list(prior_ranking),
        "action_ranking_after_cue": list(posterior_ranking),
        "selected_action": target,
        "committed_before_observation": committed_before_observation,
        "fixed_acquisition_horizon": 1,
        "adaptive_stop_available": False,
    }
    return RoutingRun(
        run_id=f"{episode.episode_id}--{policy_name}",
        episode_id=episode.episode_id,
        problem_id=problem.problem_id,
        family=problem.family,
        policy_name=policy_name,
        policy_access_class=allowed[policy_name],
        policy_visible_model_access=view.public_model_access,
        policy_randomness_seed=seed,
        trace=trace,
        final_submission=submission,
        valid=valid,
        invalid_reason=invalid_reason,
        public_diagnostic=diagnostic,
        decision_loss=decision_loss,
        correct=correct,
    )


def replay_routing_run(
    problem: ProblemSpec, episode: EpisodeSpec, expected: RoutingRun
) -> tuple[bool, str]:
    actual = run_routing_episode(problem, episode, expected.policy_name)
    if content_hash(actual) != content_hash(expected):
        return False, "routing_run_mismatch"
    return True, "exact_routing_replay"
