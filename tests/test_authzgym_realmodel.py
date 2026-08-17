from __future__ import annotations

import json
import os
import subprocess
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from ser.authzgym.generation import build_development_episodes
from ser.authzgym.realmodel import (
    CurlChatCompletionsClient,
    MalformedSemanticResponse,
    load_real_model_condition,
    parse_semantic_content,
    semantic_response_schema,
)


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "experiments/authzgym_static_realmodel_v1"


class RealModelContractTests(unittest.TestCase):
    def setUp(self):
        self.episode = build_development_episodes()[0]
        self.inventory = tuple(self.episode.public_view()["artifact_inventory"])

    def test_frozen_schema_and_config_round_trip(self):
        frozen = json.loads(
            (EXPERIMENT / "schemas/semantic_observation_v1.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(frozen, semantic_response_schema())
        condition = load_real_model_condition(EXPERIMENT / "model_config.json")
        self.assertFalse(condition.tls_verification)
        self.assertLessEqual(condition.hard_spend_ceiling_usd, 5.0)

    def test_parser_rejects_unavailable_recommendation(self):
        value = {
            "fact_keys": [],
            "facts": [],
            "hypothesis_effects": [],
            "unresolved_references": [],
            "uncertainty_flags": [],
            "recommended_next_artifact_id": "not-public",
        }
        with self.assertRaises(MalformedSemanticResponse):
            parse_semantic_content(
                json.dumps(value),
                self.episode.candidates,
                self.inventory,
                (self.inventory[1]["artifact_id"],),
                True,
            )

    def test_api_key_never_enters_subprocess_arguments_or_response_artifact(self):
        condition = load_real_model_condition(EXPERIMENT / "model_config.json")
        prompt = (EXPERIMENT / "prompts/semantic_interpretation_v1.txt").read_text(
            encoding="utf-8"
        )
        secret = "FAKE_TEST_SECRET_DO_NOT_EXPOSE"
        response_content = {
            "fact_keys": [],
            "facts": [],
            "hypothesis_effects": [],
            "unresolved_references": [],
            "uncertainty_flags": ["test"],
            "recommended_next_artifact_id": None,
        }
        response = {
            "id": "test-response",
            "model": condition.model_identifier,
            "choices": [
                {"message": {"role": "assistant", "content": json.dumps(response_content)}}
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 10,
                "total_tokens": 20,
                "prompt_tokens_details": {"cached_tokens": 0},
                "completion_tokens_details": {"reasoning_tokens": 0},
            },
        }
        captured_records = []

        def fake_run(args, **kwargs):
            rendered_args = " ".join(args)
            self.assertNotIn(secret, rendered_args)
            config_fd = kwargs["pass_fds"][0]
            config = os.read(config_fd, 8192).decode("utf-8")
            self.assertIn(secret, config)
            return SimpleNamespace(
                returncode=0,
                stdout=json.dumps(response).encode("utf-8"),
                stderr=b"",
            )

        client = CurlChatCompletionsClient(
            condition,
            prompt,
            semantic_response_schema(),
            "socks5h://127.0.0.1:9999",
            captured_records.append,
            environment={
                condition.base_url_env: "https://example.invalid/v1",
                condition.api_key_env: secret,
            },
        )
        with patch.object(subprocess, "run", side_effect=fake_run):
            result = client.invoke(
                {
                    "purchased_artifacts": [],
                    "candidate_hypotheses": [],
                    "current_epistemic_summary": {},
                    "public_artifact_inventory": list(self.inventory),
                    "legal_next_artifact_ids": [],
                    "recommendation_required": False,
                },
                self.episode.candidates,
                self.inventory,
                (),
                False,
                artifacts_in_call=1,
                call_context={"test": True},
            )
        self.assertEqual(result["call_id"], "test-response")
        self.assertNotIn(secret, json.dumps(captured_records))


if __name__ == "__main__":
    unittest.main()
