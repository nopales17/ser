from __future__ import annotations

import json
import unittest
from pathlib import Path

from ser.authzgym.v1_3_population import (
    SEMANTIC_EQUIVALENCE_VARIANTS,
    VARIANTS,
)
from ser.core.types import content_hash


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "experiments/authzgym_semantic_contract_v1_3"


class AuthzGymV13PopulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.public = json.loads(
            (EXPERIMENT / "DEVELOPMENT_PUBLIC_POPULATION.json").read_text(
                encoding="utf-8"
            )
        )
        cls.restricted = json.loads(
            (EXPERIMENT / "DEVELOPMENT_RESTRICTED_POPULATION.json").read_text(
                encoding="utf-8"
            )
        )
        cls.confirmation = json.loads(
            (EXPERIMENT / "CONFIRMATION_PUBLIC_POPULATION.json").read_text(
                encoding="utf-8"
            )
        )

    def test_exact_counts_and_schedule_order(self):
        self.assertEqual(len(self.public["cases"]), 56)
        self.assertEqual(len(self.public["schedule"]), 112)
        self.assertEqual(len(self.confirmation["cases"]), 56)
        self.assertEqual(len(self.confirmation["schedule"]), 56)
        expected = [
            (case["case_id"], repeat)
            for case in self.public["cases"]
            for repeat in (1, 2)
        ]
        self.assertEqual(
            [(item["case_id"], item["repeat"]) for item in self.public["schedule"]],
            expected,
        )
        self.assertTrue(
            all(
                item["repeat"] == 1
                for item in self.confirmation["schedule"]
            )
        )

    def test_source_and_variant_balance(self):
        by_source = {}
        for case in self.public["cases"]:
            by_source.setdefault(case["source_episode_id"], []).append(case["variant"])
        self.assertEqual(len(by_source), 8)
        for source, variants in by_source.items():
            self.assertEqual(tuple(variants), VARIANTS, source)
        self.assertEqual(
            set(SEMANTIC_EQUIVALENCE_VARIANTS),
            {
                "artifact_reordering",
                "symbol_renaming",
                "candidate_label_renaming",
                "artifact_identifier_variation",
                "combined_permutation",
            },
        )

    def test_public_bundle_contains_no_restricted_fields(self):
        rendered = json.dumps(self.public)
        for key in (
            "logical_role",
            "evaluator_usefulness",
            "expected_fact_keys",
            "mechanism_id",
            "restricted_truth",
            "correct_conclusion",
            "usefulness_by_variant_target_slot",
        ):
            self.assertNotIn(key, rendered)
        self.assertNotIn("current_epistemic_summary", rendered)

    def test_transformation_maps_are_reversible(self):
        for case in self.restricted["cases"]:
            maps = case["transformation_maps"]
            for key in ("artifact_id", "path", "symbol"):
                forward = maps[f"{key}_forward"]
                inverse = maps[f"{key}_inverse"]
                for original, transformed in forward.items():
                    self.assertEqual(inverse[transformed], original)
            self.assertEqual(
                len(maps["canonical_ordinal_by_variant_public_id"]),
                6,
            )

    def test_longest_artifact_is_unique_and_public_only(self):
        for case in self.public["cases"]:
            inventory = case["model_visible_input"]["public_artifact_inventory"]
            current = [
                item for item in inventory if item["inspection_status"] == "current"
            ]
            self.assertEqual(len(current), 1)
            if case["variant"] == "longest_artifact":
                counts = [item["line_count"] for item in inventory]
                self.assertEqual(counts.count(max(counts)), 1)
                self.assertEqual(current[0]["line_count"], max(counts))

    def test_population_hash_is_content_bound(self):
        payload = dict(self.public)
        digest = payload.pop("population_hash")
        self.assertEqual(content_hash(payload), digest)


if __name__ == "__main__":
    unittest.main()
