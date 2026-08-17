from __future__ import annotations

import json
import unittest
from pathlib import Path

from ser.authzgym.generation import (
    DISCRIMINATING_ROLE,
    build_development_episodes,
    build_evaluation_episodes,
    build_perturbation_episodes,
    permuted_episode,
)
from ser.authzgym.interpreters import (
    INTERPRETER_CONDITIONS,
    conditions_from_config,
    interpret_artifacts,
)
from ser.authzgym.model import SemanticObservation, total_lines
from ser.authzgym.policies import (
    AuthzEpistemicState,
    estimate_action_values,
    update_state,
)
from ser.authzgym.runner import run_authz_episode
from ser.evaluation.authz_artifacts import verify_record_hashes


ROOT = Path(__file__).resolve().parents[1]
PROMPT = (
    ROOT / "experiments/authzgym_static_v1/prompts/interpret_artifact_v1.txt"
).read_text(encoding="utf-8")


class AuthzGenerationTests(unittest.TestCase):
    def test_splits_and_bounded_repositories(self):
        development = build_development_episodes()
        evaluation = build_evaluation_episodes()
        perturbations = build_perturbation_episodes()
        self.assertEqual(len(development), 8)
        self.assertEqual(len(evaluation), 24)
        self.assertEqual(len(perturbations), 24)
        self.assertFalse(
            {item.episode_id for item in development}
            & {item.episode_id for item in evaluation}
        )
        for episode in (*development, *evaluation, *perturbations):
            self.assertEqual(len(episode.artifacts), 6)
            self.assertGreaterEqual(total_lines(episode.artifacts), 100)
            self.assertLessEqual(total_lines(episode.artifacts), 500)
            self.assertEqual(episode.max_inspections, 4)

    def test_eval_families_and_controls(self):
        episodes = build_evaluation_episodes()
        family_counts = {
            mechanism: sum(item.truth.mechanism_id == mechanism for item in episodes)
            for mechanism in DISCRIMINATING_ROLE
        }
        self.assertEqual(set(family_counts.values()), {6})
        self.assertEqual(
            sum(item.truth.control_type == "eligible_branch" for item in episodes),
            16,
        )
        self.assertEqual(
            sum(item.truth.control_type == "zero_value_control" for item in episodes),
            8,
        )

    def test_public_view_omits_truth_and_unpurchased_source(self):
        episode = build_development_episodes()[0]
        public = episode.public_view()
        rendered = str(public)
        for forbidden in (
            "mechanism_id",
            "correct_conclusion",
            "evaluator_usefulness",
            "expected_fact_keys",
            "logical_role",
        ):
            self.assertNotIn(forbidden, rendered)
        self.assertNotIn("source", public["artifact_inventory"][0])

    def test_permutation_changes_identifiers_not_semantics(self):
        episode = build_development_episodes()[0]
        changed = permuted_episode(episode)
        self.assertNotEqual(episode.artifact_order, changed.artifact_order)
        self.assertNotEqual(
            tuple(item.hypothesis_id for item in episode.candidates),
            tuple(item.hypothesis_id for item in changed.candidates),
        )
        self.assertEqual(
            tuple(item.logical_role for item in episode.artifacts),
            tuple(item.logical_role for item in changed.artifacts),
        )


class AuthzInterpreterTests(unittest.TestCase):
    def test_interpreter_receives_only_purchased_artifact(self):
        episode = build_development_episodes()[0]
        artifact = episode.artifact(episode.entry_artifact_id)
        call = interpret_artifacts(
            (artifact,),
            episode.candidates,
            AuthzEpistemicState.initial(episode.candidates).to_dict(),
            tuple(episode.public_view()["artifact_inventory"]),
            PROMPT,
            "interpret_artifact_v1",
            INTERPRETER_CONDITIONS[0],
        )
        visible = call["visible_input"]["artifacts"]
        self.assertEqual(len(visible), 1)
        self.assertEqual(visible[0]["artifact_id"], episode.entry_artifact_id)
        self.assertNotIn("mechanism_id", str(call))

    def test_hypothesis_ids_are_derived_from_candidate_relation_tags(self):
        episode = permuted_episode(build_development_episodes()[0])
        artifact = episode.artifact(episode.entry_artifact_id)
        call = interpret_artifacts(
            (artifact,),
            episode.candidates,
            AuthzEpistemicState.initial(episode.candidates).to_dict(),
            tuple(episode.public_view()["artifact_inventory"]),
            PROMPT,
            "interpret_artifact_v1",
            INTERPRETER_CONDITIONS[0],
        )
        effects = call["parsed_semantic_observation"]["hypothesis_effects"]
        self.assertTrue(effects)
        self.assertTrue(set(effects).issubset({item.hypothesis_id for item in episode.candidates}))
        self.assertFalse(set(effects) & {"h1", "h2", "h3", "h4"})

    def test_action_values_use_public_state_and_references(self):
        episode = build_development_episodes()[0]
        state = AuthzEpistemicState.initial(episode.candidates)
        artifact = episode.artifact(episode.entry_artifact_id)
        call = interpret_artifacts(
            (artifact,),
            episode.candidates,
            state.to_dict(),
            tuple(episode.public_view()["artifact_inventory"]),
            PROMPT,
            "interpret_artifact_v1",
            INTERPRETER_CONDITIONS[0],
        )
        observation = SemanticObservation.from_dict(call["parsed_semantic_observation"])
        state = update_state(state, (episode.entry_artifact_id,), observation)
        inventory = tuple(
            item.public_descriptor() for item in episode.artifacts
        )
        values = estimate_action_values(state, inventory, episode.candidates)
        selected = max(values, key=lambda item: (values[item], item))
        self.assertEqual(
            episode.artifact(selected).logical_role,
            episode.truth.discriminating_artifact_role,
        )


class AuthzRunnerTests(unittest.TestCase):
    def test_primary_architectures_are_call_and_evidence_matched(self):
        episode = build_development_episodes()[0]
        for architecture in (
            "fixed_order_semantic",
            "react_like_semantic",
            "ser_explicit_value",
        ):
            record = run_authz_episode(
                episode,
                architecture,
                INTERPRETER_CONDITIONS[0],
                PROMPT,
                "interpret_artifact_v1",
                "prompt",
                "config",
                "population",
            )
            self.assertTrue(record["public"]["valid"])
            self.assertEqual(record["public"]["raw_resources"]["artifact_inspections"], 4.0)
            self.assertEqual(record["public"]["raw_resources"]["semantic_calls"], 4.0)
            self.assertTrue(verify_record_hashes((record,)))

    def test_monolithic_is_bounded_but_not_call_matched(self):
        episode = build_development_episodes()[0]
        record = run_authz_episode(
            episode,
            "monolithic_semantic",
            INTERPRETER_CONDITIONS[0],
            PROMPT,
            "interpret_artifact_v1",
            "prompt",
            "config",
            "population",
        )
        self.assertEqual(record["public"]["raw_resources"]["artifact_inspections"], 4.0)
        self.assertEqual(record["public"]["raw_resources"]["semantic_calls"], 1.0)
        visible = record["public"]["steps"][0]["semantic_call"]["visible_input"]["artifacts"]
        self.assertEqual(len(visible), 4)

    def test_identifier_order_and_candidate_permutation(self):
        episode = build_development_episodes()[0]
        changed = permuted_episode(episode)
        for architecture in ("react_like_semantic", "ser_explicit_value"):
            base = run_authz_episode(
                episode,
                architecture,
                INTERPRETER_CONDITIONS[0],
                PROMPT,
                "interpret_artifact_v1",
                "prompt",
                "config",
                "population",
            )
            permuted = run_authz_episode(
                changed,
                architecture,
                INTERPRETER_CONDITIONS[0],
                PROMPT,
                "interpret_artifact_v1",
                "prompt",
                "config",
                "population",
            )
            base_quality = base["restricted"]["outcome"]["routing_quality"]
            changed_quality = permuted["restricted"]["outcome"]["routing_quality"]
            self.assertEqual(
                base_quality["first_post_entry_selected_role"],
                changed_quality["first_post_entry_selected_role"],
            )
            self.assertEqual(
                base["restricted"]["outcome"]["correct"],
                permuted["restricted"]["outcome"]["correct"],
            )

    def test_revision_1_1_degraded_mock_is_permutation_invariant(self):
        config = json.loads(
            (
                ROOT
                / "experiments/authzgym_static_v1_1/model_conditions.json"
            ).read_text(encoding="utf-8")
        )
        degraded = conditions_from_config(config)[1]
        for episode in build_development_episodes():
            changed = permuted_episode(episode)
            for architecture in ("react_like_semantic", "ser_explicit_value"):
                records = [
                    run_authz_episode(
                        item,
                        architecture,
                        degraded,
                        PROMPT,
                        "interpret_artifact_v1",
                        "prompt",
                        "config",
                        "population",
                    )
                    for item in (episode, changed)
                ]
                outcomes = [item["restricted"]["outcome"] for item in records]
                self.assertEqual(
                    outcomes[0]["routing_quality"][
                        "first_post_entry_selected_role"
                    ],
                    outcomes[1]["routing_quality"][
                        "first_post_entry_selected_role"
                    ],
                )
                self.assertEqual(outcomes[0]["correct"], outcomes[1]["correct"])


if __name__ == "__main__":
    unittest.main()
