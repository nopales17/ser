from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import ser.evaluation.routing as routing_module
from ser.core.types import TerminationCause, content_hash
from ser.evaluation.routing import (
    compute_routing_oracle,
    replay_routing_run,
    run_routing_episode,
    routing_policy_seed,
)
from ser.evaluation.routing_analysis import (
    _oracle_signature,
    _transformed_problem,
    build_oracle_records,
    build_run_records,
    summarize_routing,
)
from ser.evaluation.routing_artifacts import (
    build_routing_episodes,
    freeze_routing_population,
    load_routing_population,
    routing_run_artifact,
    verify_routing_record_hashes,
)
from ser.microgym.routing import build_routing_regimes
from ser.microgym.environment import MicroGymEnvironment


class RoutingOracleTests(unittest.TestCase):
    def setUp(self):
        self.regimes = build_routing_regimes()

    def oracle(self, regime_index: int, reverse: bool = False):
        problem = self.regimes[regime_index].problem
        action_ids = tuple(test.public.action_id for test in problem.tests)
        if reverse:
            action_ids = tuple(reversed(action_ids))
        return compute_routing_oracle(problem.public_view(action_ids))

    def test_voa_bands_and_exact_values(self):
        expected = (0.2025, 0.18, 0.0, 0.0, 0.0, 0.018, 0.09, 0.16, 0.19)
        actual = tuple(round(self.oracle(index).value_of_adaptivity, 6) for index in range(9))
        self.assertEqual(actual, expected)

    def test_candidate_captures_positive_voa(self):
        for index in (0, 1, 5, 6, 7, 8):
            oracle = self.oracle(index)
            self.assertTrue(oracle.eligible_conditional_node)
            self.assertEqual(oracle.candidate_actions, oracle.closed_loop_actions)
            self.assertAlmostEqual(oracle.adaptivity_capture, 1.0)

    def test_zero_voa_controls_do_not_branch(self):
        for index in (2, 3, 4):
            oracle = self.oracle(index)
            self.assertAlmostEqual(oracle.value_of_adaptivity, 0.0)
            self.assertEqual(len({action for _, action in oracle.candidate_actions}), 1)

    def test_action_order_does_not_change_values_or_branching(self):
        for index in range(9):
            self.assertEqual(
                _oracle_signature(self.oracle(index)),
                _oracle_signature(self.oracle(index, reverse=True)),
            )

    def test_identifier_and_hidden_label_permutations(self):
        for regime in self.regimes:
            problem = regime.problem
            base = compute_routing_oracle(
                problem.public_view(tuple(test.public.action_id for test in problem.tests))
            )
            for transformed in (
                _transformed_problem(problem, rename_actions=True),
                _transformed_problem(problem, permute_hidden=True),
            ):
                oracle = compute_routing_oracle(
                    transformed.public_view(
                        tuple(test.public.action_id for test in transformed.tests)
                    )
                )
                self.assertEqual(_oracle_signature(base), _oracle_signature(oracle))


class RoutingRunTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.regimes = build_routing_regimes()
        cls.episodes = build_routing_episodes(cls.regimes)

    def test_population_is_balanced_and_order_counterbalanced(self):
        for regime in self.regimes:
            episodes = [
                item for item in self.episodes if item.problem_id == regime.problem.problem_id
            ]
            self.assertEqual(len(episodes), 128)
            counts = {state: 0 for state in regime.problem.hypotheses}
            for episode in episodes:
                counts[episode.hidden_state] += 1
            self.assertEqual(set(counts.values()), {32})
            self.assertEqual(len({episode.action_order for episode in episodes}), 2)

    def test_primary_run_has_one_acquisition_and_no_stop(self):
        episode = self.episodes[0]
        problem = self.regimes[0].problem
        for policy in (
            "exact_open_loop",
            "adaptive_belief",
            "exact_closed_loop_oracle",
        ):
            run = run_routing_episode(problem, episode, policy)
            self.assertTrue(run.valid)
            self.assertEqual(len(run.trace.transitions), 1)
            self.assertEqual(run.trace.transitions[0].action.kind, "acquire")
            self.assertEqual(
                run.trace.termination.cause,
                TerminationCause.RUNNER_EVALUATOR_TRUNCATION,
            )
            self.assertEqual(
                run.trace.termination.reason, "fixed_routing_horizon_complete"
            )

    def test_open_loop_action_is_invariant_to_realized_cue(self):
        problem = self.regimes[0].problem
        target = compute_routing_oracle(
            problem.public_view(tuple(test.public.action_id for test in problem.tests))
        ).open_loop_action
        selected = set()
        for episode in self.episodes[:128]:
            run = run_routing_episode(problem, episode, "exact_open_loop")
            selected.add(run.trace.transitions[0].action.target_id)
            self.assertTrue(run.public_diagnostic["committed_before_observation"])
        self.assertEqual(selected, {target})

    def test_open_loop_plan_is_computed_before_reset_releases_cue(self):
        events = []
        real_compute = routing_module.compute_routing_oracle

        class OrderedEnvironment(MicroGymEnvironment):
            def reset(self):
                events.append("reset")
                return super().reset()

        def ordered_compute(view):
            events.append("plan")
            return real_compute(view)

        episode = self.episodes[0]
        with patch.object(routing_module, "MicroGymEnvironment", OrderedEnvironment), patch.object(
            routing_module, "compute_routing_oracle", side_effect=ordered_compute
        ):
            run_routing_episode(self.regimes[0].problem, episode, "exact_open_loop")
        self.assertEqual(events, ["plan", "reset"])

    def test_candidate_diagnostic_uses_released_cue(self):
        problem = self.regimes[0].problem
        observed = {}
        for episode in self.episodes[:128]:
            run = run_routing_episode(problem, episode, "adaptive_belief")
            cue = run.trace.initial_observations[0].payload["value"]
            observed.setdefault(cue, run.trace.transitions[0].action.target_id)
        self.assertEqual(observed, {"v0": "a0", "v1": "a1"})

    def test_policy_seed_is_independent_of_environment_seed(self):
        episode = self.episodes[0]
        first = routing_policy_seed(episode.episode_id, "adaptive_belief")
        self.assertNotEqual(first, episode.environment_seed)
        self.assertEqual(first, routing_policy_seed(episode.episode_id, "adaptive_belief"))

    def test_exact_replay(self):
        episode = self.episodes[0]
        problem = self.regimes[0].problem
        run = run_routing_episode(problem, episode, "adaptive_belief")
        self.assertEqual(replay_routing_run(problem, episode, run), (True, "exact_routing_replay"))

    def test_public_artifact_omits_restricted_truth_and_seed(self):
        episode = self.episodes[0]
        run = run_routing_episode(self.regimes[0].problem, episode, "adaptive_belief")
        artifact = routing_run_artifact(run, episode, "population")
        public = artifact["public"]
        self.assertNotIn("hidden_state", str(public))
        self.assertNotIn("environment_realization_seed", str(public))
        self.assertEqual(artifact["record_hash"], content_hash({k: v for k, v in artifact.items() if k != "record_hash"}))


class RoutingArtifactTests(unittest.TestCase):
    def test_population_freeze_and_load(self):
        regimes = build_routing_regimes()
        episodes = build_routing_episodes(regimes)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            preregistration = root / "PREREGISTRATION.md"
            preregistration.write_text("frozen\n", encoding="utf-8")
            digest = freeze_routing_population(
                root / "population.json", regimes, episodes, preregistration
            )
            loaded_regimes, loaded_episodes, loaded_digest, _ = load_routing_population(
                root / "population.json"
            )
            self.assertEqual(digest, loaded_digest)
            self.assertEqual(len(loaded_regimes), 9)
            self.assertEqual(loaded_episodes, episodes)

    def test_small_artifact_set_validates_and_summarizes(self):
        regimes = build_routing_regimes()
        all_episodes = build_routing_episodes(regimes)
        episodes = tuple(
            next(item for item in all_episodes if item.problem_id == regime.problem.problem_id)
            for regime in regimes
        )
        population_hash = "test-population"
        oracle_records = build_oracle_records(regimes, population_hash)
        run_records = build_run_records(regimes, episodes, population_hash)
        self.assertTrue(verify_routing_record_hashes(oracle_records + run_records))
        # Full population-size validation is intentionally tested by the frozen
        # experiment verifier; summary mechanics can be checked on this slice.
        summary = summarize_routing(
            regimes,
            episodes,
            oracle_records,
            run_records,
            population_hash,
            validation_passed=True,
        )
        self.assertEqual(summary["branch_audit"]["candidate_branch_nodes"], 6)
        self.assertEqual(summary["branch_audit"]["zero_voa_spurious_branch_nodes"], 0)
        self.assertEqual(summary["classifier"]["classification"], "routing_supported")


if __name__ == "__main__":
    unittest.main()
