from __future__ import annotations

import json
import unittest
from pathlib import Path

from ser.authzgym.v1_3_contract import load_public_contract
from ser.evaluation.authz_v1_3 import (
    _metric,
    action_diagnostic,
    classify_validity,
    oracle_response_from_annotation,
    score_cases,
)


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "experiments/authzgym_semantic_contract_v1_3"


class AuthzGymV13ScoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = load_public_contract(EXPERIMENT / "PUBLIC_CONTRACT.json")
        cls.population = json.loads(
            (EXPERIMENT / "DEVELOPMENT_PUBLIC_POPULATION.json").read_text(
                encoding="utf-8"
            )
        )
        cls.annotations = {
            item["case_id"]: item
            for item in (
                json.loads(line)
                for line in (
                    EXPERIMENT / "annotations/development_annotations.jsonl"
                ).read_text(encoding="utf-8").splitlines()
                if line.strip()
            )
        }
        cls.restricted = {
            item["case_id"]: item
            for item in json.loads(
                (EXPERIMENT / "DEVELOPMENT_RESTRICTED_POPULATION.json").read_text(
                    encoding="utf-8"
                )
            )["cases"]
        }

    def test_hand_calculated_micro_metric(self):
        metric = _metric([(2, 4, 3), (1, 1, 2)])
        self.assertEqual(metric["true_positive"], 3)
        self.assertEqual(metric["false_positive"], 2)
        self.assertEqual(metric["false_negative"], 2)
        self.assertEqual(metric["precision"], 0.6)
        self.assertEqual(metric["recall"], 0.6)

    def test_zero_denominators_are_na_not_zero_or_one(self):
        metric = _metric([(0, 0, 0)])
        self.assertIsNone(metric["precision"])
        self.assertIsNone(metric["recall"])
        self.assertIsNone(metric["f1"])

    def test_missing_and_invalid_are_not_imputed_as_false(self):
        from ser.evaluation.authz_v1_3 import oracle_response_from_annotation

        case = self.population["cases"][0]
        result = score_cases(
            self.population,
            self.annotations,
            {},
            contract=self.contract,
            source_family_by_case={
                item["case_id"]: self.restricted[item["case_id"]][
                    "source_family"
                ]
                for item in self.population["cases"]
            },
        )
        self.assertEqual(result["observed"]["missing_case_count"], 112)
        self.assertEqual(result["facts"]["true_positive"], 0)
        del case, oracle_response_from_annotation

    def test_validity_precedence_blocks_later_layers(self):
        result = classify_validity(
            {
                "manifest": True,
                "answerability": False,
                "firewall": True,
                "oracle": True,
                "mechanical_response": True,
                "semantic_interface": True,
                "downstream": True,
            }
        )
        self.assertEqual(result["first_failure"], "answerability")
        self.assertEqual(result["classification"], "invalid")

    def test_scoring_report_labels_effects_non_independent(self):
        result = score_cases(
            self.population,
            self.annotations,
            {},
            contract=self.contract,
        )
        self.assertTrue(result["effect_metrics_are_non_independent"])
        self.assertIn("not a second independent", result["effect_non_independence_note"])

    def test_equal_usefulness_tie_is_nondiscriminating_and_scored_zero_regret(self):
        case = self.population["cases"][0]
        restricted = json.loads(json.dumps(self.restricted[case["case_id"]]))
        restricted["usefulness_by_variant_target_slot"] = {
            target: 1.0
            for target in restricted["usefulness_by_variant_target_slot"]
        }
        diagnostic = action_diagnostic(
            case,
            oracle_response_from_annotation(self.annotations[case["case_id"]]),
            restricted,
            contract=self.contract,
        )
        self.assertTrue(diagnostic["nondiscriminating"])
        self.assertTrue(diagnostic["top1"])
        self.assertTrue(diagnostic["top2"])
        self.assertEqual(diagnostic["mean_normalized_regret"], 0.0)


if __name__ == "__main__":
    unittest.main()
