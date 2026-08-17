from __future__ import annotations

import unittest
from dataclasses import fields

from ser.core.types import Action
from ser.microgym.environment import MicroGymEnvironment, deterministic_uniform
from ser.microgym.families import build_problem_specs
from ser.microgym.model import EpisodeSpec, PublicProblemView, PublicTestModel


def episode(problem, *, hidden_index=0, environment_seed=1, order=None):
    return EpisodeSpec(
        "unit-episode",
        problem.problem_id,
        problem.hypotheses[hidden_index],
        environment_seed,
        order or tuple(test.public.action_id for test in problem.tests),
    )


class EnvironmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.problems = build_problem_specs()

    def test_six_families_and_twenty_four_regimes_exist(self):
        self.assertEqual(len(self.problems), 24)
        self.assertEqual({problem.family for problem in self.problems}, set("ABCDEF"))

    def test_public_projection_has_no_truth_or_rng_slot(self):
        problem = self.problems[0]
        view = MicroGymEnvironment(problem, episode(problem)).reset().view
        self.assertNotIn("hidden_state", {field.name for field in fields(PublicProblemView)})
        self.assertNotIn("rng_slot", {field.name for field in fields(PublicTestModel)})
        self.assertFalse(hasattr(view, "environment_seed"))

    def test_deterministic_uniform_is_repeatable_and_channel_separated(self):
        first = deterministic_uniform(7, "slot", 0, "outcome")
        self.assertEqual(first, deterministic_uniform(7, "slot", 0, "outcome"))
        self.assertNotEqual(first, deterministic_uniform(8, "slot", 0, "outcome"))
        self.assertNotEqual(first, deterministic_uniform(7, "slot", 0, "failure"))

    def test_reset_observation_has_release_metadata(self):
        problem = self.problems[0]
        observation = MicroGymEnvironment(problem, episode(problem)).reset().observations[0]
        self.assertEqual(observation.release_step, 0)
        self.assertEqual(observation.provenance, "environment_reset")
        self.assertIsNone(observation.source_result_id)

    def test_illegal_action_is_rejected_without_cost(self):
        problem = self.problems[0]
        environment = MicroGymEnvironment(problem, episode(problem))
        interface = environment.reset()
        result = environment.execute(Action("a1", "acquire", "not-legal"), interface.budget, 1)
        self.assertEqual(result.status, "rejected")
        self.assertEqual(sum(result.cost.as_dict().values()), 0)

    def test_stop_is_first_class(self):
        problem = self.problems[0]
        environment = MicroGymEnvironment(problem, episode(problem))
        interface = environment.reset()
        result = environment.execute(Action("a1", "stop", submission="s0"), interface.budget, 1)
        self.assertEqual(result.termination.cause.value, "controller_stop")
        self.assertEqual(result.cost.get("tests"), 0)

    def test_budget_filters_unaffordable_actions(self):
        problem = next(problem for problem in self.problems if problem.problem_id == "a-r0")
        environment = MicroGymEnvironment(problem, episode(problem))
        interface = environment.reset()
        legal = {item.action_id for item in environment.available_actions(interface.budget)}
        self.assertNotIn("a2", legal)

    def _find_failure(self, problem_id):
        problem = next(problem for problem in self.problems if problem.problem_id == problem_id)
        for seed in range(500):
            environment = MicroGymEnvironment(problem, episode(problem, environment_seed=seed))
            interface = environment.reset()
            result = environment.execute(Action("a1", "acquire", "f0"), interface.budget, 1)
            if result.status == "failed":
                return result
        self.fail("no deterministic failure found")

    def test_action_failure_consumes_declared_cost(self):
        result = self._find_failure("f-r0")
        self.assertEqual(result.cost.get("synthetic_cost_units"), 1.0)
        self.assertIsNone(result.termination)

    def test_failure_can_terminate_environment(self):
        result = self._find_failure("f-r2")
        self.assertEqual(result.termination.cause.value, "environment_termination")

    def test_repeated_test_limit_is_enforced(self):
        problem = next(problem for problem in self.problems if problem.problem_id == "d-r0")
        environment = MicroGymEnvironment(problem, episode(problem))
        interface = environment.reset()
        budget = interface.budget
        for step in range(1, 5):
            result = environment.execute(Action(f"a{step}", "acquire", "d0"), budget, step)
            budget = budget.charge(result.cost)
        self.assertNotIn("d0", {item.action_id for item in environment.available_actions(budget)})


if __name__ == "__main__":
    unittest.main()
