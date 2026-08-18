from __future__ import annotations

import json
import os
import subprocess
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from ser.authzgym.realmodel import load_real_model_condition
from ser.authzgym.semantic_contract import (
    FACT_KEYS,
    RELATION_SLOTS,
    build_stress_cases,
    episode_from_case,
    oracle_content,
    parse_content,
    response_schema,
    stress_population_payload,
    vocabulary_payload,
)
from ser.authzgym.semantic_transport import SemanticContractClientV12
from ser.evaluation.authz_artifacts import load_population
from ser.evaluation.authz_contract_analysis import summarize


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "experiments/authzgym_semantic_contract_v1_2"
SOURCE = ROOT / "experiments/authzgym_static_v1_1"


def enum_values(value):
    if isinstance(value, dict):
        result = set(value.get("enum", ())) if isinstance(value.get("enum"), list) else set()
        for item in value.values():
            result |= enum_values(item)
        return result
    if isinstance(value, list):
        result = set()
        for item in value:
            result |= enum_values(item)
        return result
    return set()


class SemanticContractV12Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.episodes, _, _ = load_population(SOURCE / "development_population.json")
        cls.cases = build_stress_cases(cls.episodes)

    def test_population_is_development_only_and_bounded(self):
        population = stress_population_payload(self.episodes)
        self.assertEqual(len(population["cases"]), 64)
        self.assertEqual(len(population["schedule"]), 128)
        self.assertEqual(
            {item["source_episode_id"] for item in population["cases"]},
            {item.episode_id for item in self.episodes},
        )
        self.assertTrue(all(item.split == "development" for item in self.episodes))
        self.assertTrue(
            all(
                len(case["model_visible_input"]["current_artifact"]["source"]) > 0
                for case in population["cases"]
            )
        )

    def test_schema_has_no_free_form_or_illegal_dynamic_identifiers(self):
        for case in self.cases:
            schema = case["response_schema"]
            rendered = json.dumps(schema)
            self.assertNotIn('"type": "array"', rendered)
            self.assertNotIn('"type": "number"', rendered)
            self.assertNotIn("recommended", rendered)
            episode = episode_from_case(case)
            forbidden = {
                episode.truth.mechanism_id,
                episode.truth.correct_conclusion,
                episode.truth.discriminating_artifact_role,
                *episode.artifact_order,
                *(item.hypothesis_id for item in episode.candidates),
            }
            self.assertFalse(enum_values(schema) & forbidden)
            targets = schema["properties"]["unresolved_targets"]
            self.assertEqual(
                set(targets["properties"]),
                {f"t{slot}" for slot in case["runner_control"]["legal_target_slots"]},
            )
            self.assertTrue(
                all(
                    set(item["properties"]) == set(RELATION_SLOTS)
                    and all(
                        relation["type"] == "boolean"
                        for relation in item["properties"].values()
                    )
                    for item in targets["properties"].values()
                )
            )

    def test_oracle_content_round_trips_through_slot_adapter(self):
        for case in self.cases:
            episode = episode_from_case(case)
            legal = tuple(case["runner_control"]["legal_target_slots"])
            expected = oracle_content(
                episode, case["runner_control"]["current_artifact_slot"], legal
            )
            observation, normalized = parse_content(expected, episode, legal)
            self.assertEqual(set(observation.fact_keys), {
                FACT_KEYS[int(slot[1:])]
                for slot, present in expected["facts"].items()
                if present
            })
            self.assertEqual(normalized["unresolved_targets"], expected["unresolved_targets"])

    def test_largest_summary_uses_three_prior_purchases(self):
        cases = [item for item in self.cases if item["variant"] == "maximal_public_summary"]
        self.assertEqual(len(cases), 8)
        for case in cases:
            summary = case["model_visible_input"]["current_epistemic_summary"]
            self.assertEqual(len(summary["inspected_artifact_slots"]), 3)
            self.assertEqual(
                case["model_visible_input"]["instruction_scope"],
                "current_artifact_only",
            )

    def test_frozen_vocabulary_and_output_ceiling(self):
        frozen = json.loads(
            (EXPERIMENT / "schemas/semantic_vocabulary_v1_2.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(frozen, vocabulary_payload())
        condition = load_real_model_condition(EXPERIMENT / "model_config.json")
        self.assertEqual(condition.max_output_tokens_per_artifact, 1024)
        self.assertEqual(condition.hard_spend_ceiling_usd, 1.0)
        self.assertEqual(condition.model_identifier, "patchersniper_praneeth/gpt-5.4-nano")

    def test_perfect_outputs_exercise_all_analysis_layers(self):
        population = stress_population_payload(self.episodes)
        cases = {item["case_id"]: item for item in population["cases"]}
        runs = []
        responses = []
        for scheduled in population["schedule"]:
            case = cases[scheduled["case_id"]]
            episode = episode_from_case(case)
            expected = case["evaluator_only"]["expected_content"]
            observation, normalized = parse_content(
                expected,
                episode,
                tuple(case["runner_control"]["legal_target_slots"]),
            )
            resources = {
                "provider_calls": 1,
                "input_tokens": 1,
                "output_tokens": 1,
                "cached_input_tokens": 0,
                "reasoning_output_tokens": 0,
                "latency_ms": 1.0,
                "monetary_cost_usd": 0.0,
            }
            runs.append(
                {
                    "case_id": case["case_id"],
                    "repeat": scheduled["repeat"],
                    "valid": True,
                    "resources": resources,
                    "result": {
                        "parsed": {
                            "provider_content": expected,
                            "normalized": normalized,
                            "semantic_observation": observation.to_dict(),
                        }
                    },
                }
            )
            responses.append(
                {
                    "attempt": 1,
                    "contract_validation": {
                        "valid": True,
                        "error": None,
                        "finish_reason": "stop",
                    },
                }
            )
        result = summarize(
            population,
            runs,
            responses,
            {"status": "pass", "counts": {"information_boundary_violations": 0}},
        )
        self.assertEqual(result["contract"]["classification"], "contract_stable")
        self.assertEqual(
            result["semantics"]["classification"], "semantic_signal_promising"
        )
        self.assertTrue(
            result["downstream_action_value"][
                "existing_estimator_adequate_under_oracle"
            ]
        )

    def test_secret_stays_out_of_args_and_response_record(self):
        case = self.cases[0]
        episode = episode_from_case(case)
        condition = load_real_model_condition(EXPERIMENT / "model_config.json")
        prompt = (EXPERIMENT / "prompts/semantic_observation_v1_2.txt").read_text(
            encoding="utf-8"
        )
        secret = "FAKE_V12_TEST_SECRET_DO_NOT_EXPOSE"
        content = case["evaluator_only"]["expected_content"]
        response = {
            "id": "v12-test-response",
            "model": condition.model_identifier,
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"role": "assistant", "content": json.dumps(content)},
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 10,
                "total_tokens": 20,
                "prompt_tokens_details": {"cached_tokens": 0},
                "completion_tokens_details": {"reasoning_tokens": 0},
            },
        }
        captured = []

        def fake_run(args, **kwargs):
            self.assertNotIn(secret, " ".join(args))
            config_fd = kwargs["pass_fds"][0]
            config = os.read(config_fd, 8192).decode("utf-8")
            self.assertIn(secret, config)
            return SimpleNamespace(
                returncode=0,
                stdout=json.dumps(response).encode("utf-8"),
                stderr=b"",
            )

        client = SemanticContractClientV12(
            condition,
            prompt,
            "socks5h://127.0.0.1:9999",
            captured.append,
            environment={
                condition.base_url_env: "https://example.invalid/v1",
                condition.api_key_env: secret,
            },
        )
        with patch.object(subprocess, "run", side_effect=fake_run):
            result = client.invoke_v12(
                case["model_visible_input"],
                case["response_schema"],
                episode,
                tuple(case["runner_control"]["legal_target_slots"]),
                call_context={"test": True},
            )
        self.assertEqual(result["call_id"], "v12-test-response")
        self.assertNotIn(secret, json.dumps(captured))


if __name__ == "__main__":
    unittest.main()
