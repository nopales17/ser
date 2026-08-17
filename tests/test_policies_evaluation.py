from __future__ import annotations

import unittest
from dataclasses import replace

from ser.core.types import Action, Budget, Observation
from ser.evaluation.runner import _policy_seed, replay_trace, run_episode
from ser.evaluation.adaptivity import audit_suite
from ser.evaluation.validation import (
    _permute_hidden_states,
    _scramble_identifiers,
    _behavior_signature,
)
from ser.microgym.families import build_problem_specs
from ser.microgym.model import (
    EpisodeSpec,
    ProblemSpec,
    PublicTestModel,
    RESOURCE_SCHEMA,
    TestSpec,
)
from ser.microgym.oracle import OracleReferencePolicy, OracleSolver
from ser.policies import AdaptiveBeliefPolicy, FixedOrderPolicy, NoAdaptationPolicy, policy_suite
from ser.policies.base import BeliefPolicy


def make_episode(problem, seed=9, order=None):
    return EpisodeSpec(
        "policy-episode",
        problem.problem_id,
        problem.hypotheses[0],
        seed,
        order or tuple(test.public.action_id for test in problem.tests),
    )


class AlwaysAcquirePolicy(BeliefPolicy):
    name = "always_acquire"

    def should_stop(self, state, context):
        return False

    def select_action(self, state, context):
        return context.legal_actions[0]


class PolicyAndEvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.problems = build_problem_specs()

    def test_all_registered_policies_remain_legal_and_within_budget(self):
        for problem in self.problems:
            episode = make_episode(problem)
            for policy in policy_suite():
                run = run_episode(problem, episode, policy)
                self.assertTrue(run.valid, (problem.problem_id, policy.name, run.invalid_reason))
                self.assertIn(run.trace.termination.cause.value, {"controller_stop", "environment_termination"})

    def test_oracle_cannot_run_as_normal_policy(self):
        problem = self.problems[0]
        with self.assertRaises(PermissionError):
            run_episode(problem, make_episode(problem), OracleReferencePolicy())

    def test_runner_truncation_is_distinct(self):
        base = next(problem for problem in self.problems if problem.problem_id == "d-r0")
        problem = replace(base, max_steps=1)
        run = run_episode(problem, make_episode(problem), AlwaysAcquirePolicy())
        self.assertEqual(run.trace.termination.cause.value, "runner_evaluator_truncation")

    def test_policy_seed_is_independent_of_environment_seed(self):
        problem = self.problems[0]
        first = make_episode(problem, seed=1)
        second = replace(first, environment_seed=999)
        first_run = run_episode(problem, first, FixedOrderPolicy())
        second_run = run_episode(problem, second, FixedOrderPolicy())
        self.assertEqual(first_run.policy_randomness_seed, second_run.policy_randomness_seed)
        self.assertNotEqual(first_run.policy_randomness_seed, first.environment_seed)
        self.assertNotEqual(_policy_seed(first.episode_id, "random"), _policy_seed(first.episode_id, "fixed"))

    def test_open_loop_model_aware_plan_ignores_initial_observation(self):
        problem = next(problem for problem in self.problems if problem.problem_id == "e-r0")
        view = problem.public_view(tuple(test.public.action_id for test in problem.tests))
        policy = NoAdaptationPolicy()
        left = Observation("o", {"model_id": "init", "value": "v0"}, "test", 0)
        right = replace(left, payload={"model_id": "init", "value": "v1"})
        left_state = policy.reset(view, (left,), 1)
        right_state = policy.reset(view, (right,), 1)
        self.assertEqual(left_state.frozen_plan, right_state.frozen_plan)
        self.assertNotEqual(left_state.belief, right_state.belief)

    def test_adaptive_policy_is_action_order_invariant(self):
        problem = next(problem for problem in self.problems if problem.problem_id == "e-r0")
        episode = make_episode(problem)
        reversed_episode = replace(episode, action_order=tuple(reversed(episode.action_order)))
        self.assertEqual(_behavior_signature(problem, episode), _behavior_signature(problem, reversed_episode))

    def test_identifier_scrambling_preserves_adaptive_outcome(self):
        problem = next(problem for problem in self.problems if problem.problem_id == "e-r0")
        episode = make_episode(problem)
        renamed_problem, renamed_episode = _scramble_identifiers(problem, episode)
        self.assertEqual(_behavior_signature(problem, episode), _behavior_signature(renamed_problem, renamed_episode))

    def test_hidden_state_permutation_preserves_adaptive_outcome(self):
        problem = self.problems[0]
        episode = make_episode(problem)
        permuted_problem, permuted_episode = _permute_hidden_states(problem, episode)
        self.assertEqual(_behavior_signature(problem, episode), _behavior_signature(permuted_problem, permuted_episode))

    def test_counterfactual_audit_exposes_candidate_non_adaptivity(self):
        from ser.policies import NoAdaptiveStopPolicy

        audit = audit_suite(
            self.problems,
            (AdaptiveBeliefPolicy(), NoAdaptationPolicy(), NoAdaptiveStopPolicy()),
        )
        self.assertEqual(
            audit["policies"]["adaptive_belief"][
                "observation_conditioned_branching_nodes"
            ],
            0,
        )
        self.assertEqual(
            audit["policies"]["ablation_no_adaptation"][
                "observation_conditioned_branching_nodes"
            ],
            0,
        )
        self.assertGreater(
            audit["policies"]["ablation_no_adaptive_stop"][
                "observation_conditioned_branching_nodes"
            ],
            0,
        )

    def test_oracle_solves_hand_checkable_problem(self):
        initial = TestSpec(
            PublicTestModel(
                "init",
                ("v0",),
                ((1.0,), (1.0,)),
                RESOURCE_SCHEMA.vector(),
            ),
            "initial-slot",
        )
        perfect = TestSpec(
            PublicTestModel(
                "x0",
                ("v0", "v1"),
                ((1.0, 0.0), (0.0, 1.0)),
                RESOURCE_SCHEMA.vector({"tests": 1, "synthetic_cost_units": 1, "latency_steps": 1}),
            ),
            "perfect-slot",
        )
        problem = ProblemSpec(
            "hand",
            "T",
            "v1",
            "hand-solvable perfect test",
            ("s0", "s1"),
            (0.5, 0.5),
            initial,
            (perfect,),
            (("tests", 1.0), ("synthetic_cost_units", 1.0)),
            "synthetic_cost_units",
            0.1,
            0.35,
            2,
            (),
        )
        view = problem.public_view(("x0",))
        value, action = OracleSolver(view).value(
            view.prior,
            (("x0", 0),),
            Budget.create(RESOURCE_SCHEMA, dict(view.budget_limits)),
        )
        self.assertEqual(action, "x0")
        self.assertAlmostEqual(value, 0.1)
        expensive_view = replace(view, cost_weight=0.5)
        self.assertIsNone(
            OracleSolver(expensive_view).value(
                expensive_view.prior,
                (("x0", 0),),
                Budget.create(RESOURCE_SCHEMA, dict(expensive_view.budget_limits)),
            )[1]
        )

    def test_replay_detects_seed_observation_cost_and_action_changes(self):
        problem = self.problems[0]
        episode = make_episode(problem)
        run = run_episode(problem, episode, FixedOrderPolicy())
        self.assertTrue(replay_trace(problem, episode, run.trace)[0])
        seed_mismatch_detected = any(
            not replay_trace(
                problem,
                replace(episode, environment_seed=episode.environment_seed + offset),
                run.trace,
            )[0]
            for offset in range(1, 100)
        )
        self.assertTrue(seed_mismatch_detected)
        changed_initial = replace(
            run.trace.initial_observations[0], payload={"model_id": "init", "value": "tampered"}
        )
        self.assertFalse(replay_trace(problem, episode, replace(run.trace, initial_observations=(changed_initial,)))[0])
        transition = run.trace.transitions[0]
        changed_cost = transition.result.cost.schema.vector(
            {**transition.result.cost.as_dict(), "synthetic_cost_units": transition.result.cost.get("synthetic_cost_units") + 0.5}
        )
        cost_trace = replace(
            run.trace,
            transitions=(replace(transition, result=replace(transition.result, cost=changed_cost)),) + run.trace.transitions[1:],
        )
        self.assertFalse(replay_trace(problem, episode, cost_trace)[0])
        action_trace = replace(
            run.trace,
            transitions=(replace(transition, action=replace(transition.action, target_id="a1")),) + run.trace.transitions[1:],
        )
        self.assertFalse(replay_trace(problem, episode, action_trace)[0])


if __name__ == "__main__":
    unittest.main()
