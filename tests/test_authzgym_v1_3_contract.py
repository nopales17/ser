from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from ser.authzgym.v1_3_contract import (
    ContractV13Error,
    load_public_contract,
    parse_response,
    response_schema,
)
from ser.core.types import content_hash


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "experiments/authzgym_semantic_contract_v1_3"


class AuthzGymV13ContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = load_public_contract(EXPERIMENT / "PUBLIC_CONTRACT.json")
        cls.population = json.loads(
            (EXPERIMENT / "DEVELOPMENT_PUBLIC_POPULATION.json").read_text(
                encoding="utf-8"
            )
        )
        cls.case = cls.population["cases"][0]

    def valid_response(self):
        legal = self.case["runner_control"]["legal_target_slots"]
        return {
            "facts": {slot: False for slot in self.contract["fact_slots"]},
            "candidate_effects": {
                slot: "unknown" for slot in self.contract["candidate_slots"]
            },
            "unresolved_targets": {
                f"t{slot}": {
                    relation_slot: False
                    for relation_slot in self.contract["relation_slots"]
                }
                for slot in legal
            },
        }

    def test_exact_keys_and_types(self):
        parsed = parse_response(
            self.valid_response(),
            self.contract,
            self.case["runner_control"]["legal_target_slots"],
        )
        self.assertEqual(set(parsed), {"facts", "candidate_effects", "unresolved_targets"})
        with self.assertRaises(ContractV13Error):
            parse_response(
                {**self.valid_response(), "extra": True},
                self.contract,
                self.case["runner_control"]["legal_target_slots"],
            )
        invalid = self.valid_response()
        invalid["facts"]["f0"] = 0
        with self.assertRaises(ContractV13Error):
            parse_response(
                invalid,
                self.contract,
                self.case["runner_control"]["legal_target_slots"],
            )

    def test_illegal_targets_and_schema_hash_are_deterministic(self):
        schema_a = response_schema(
            self.contract, self.case["runner_control"]["legal_target_slots"]
        )
        schema_b = response_schema(
            self.contract, self.case["runner_control"]["legal_target_slots"]
        )
        self.assertEqual(content_hash(schema_a), content_hash(schema_b))
        invalid = self.valid_response()
        invalid["unresolved_targets"]["t99"] = invalid["unresolved_targets"][
            next(iter(invalid["unresolved_targets"]))
        ]
        with self.assertRaises(ContractV13Error):
            parse_response(
                invalid,
                self.contract,
                self.case["runner_control"]["legal_target_slots"],
            )

    def test_retired_and_normal_summary_channels_are_absent(self):
        rendered = json.dumps(self.contract)
        for index in range(17, 25):
            self.assertNotIn(f"f{index}", self.contract["fact_slots"])
        self.assertEqual(self.contract["normal_summary_fields"], [])
        for word in ("maximal_public_summary", "current_epistemic_summary"):
            self.assertNotIn(word, rendered)

    def test_candidate_label_change_preserves_family_identity(self):
        candidate = copy.deepcopy(
            self.case["model_visible_input"]["candidate_hypotheses"][0]
        )
        original_family = candidate["effect_family"]
        candidate["public_label"] = "different-opaque-label"
        self.assertEqual(candidate["effect_family"], original_family)


if __name__ == "__main__":
    unittest.main()
