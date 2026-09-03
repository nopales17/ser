import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "run_authzgym_semantic_bottleneck",
    ROOT / "tools/run_authzgym_semantic_bottleneck.py",
)
assert SPEC is not None and SPEC.loader is not None
DIAGNOSTIC = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DIAGNOSTIC)


class AuthzGymSemanticBottleneckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.population = json.loads(
            (
                ROOT
                / "experiments/authzgym_stronger_model_v1/DEVELOPMENT_POPULATION.json"
            ).read_text(encoding="utf-8")
        )
        cls.runs = [
            json.loads(line)
            for line in (
                ROOT
                / "experiments/authzgym_stronger_model_v1/development/runs.jsonl"
            )
            .read_text(encoding="utf-8")
            .splitlines()
            if line
        ]

    def test_prompt_grounded_audit_does_not_reuse_evaluator_fact_keys(self):
        case = next(
            item
            for item in self.population["cases"]
            if item["case_id"] == DIAGNOSTIC.SELECTED_CASE_IDS[0]
        )
        answerability = DIAGNOSTIC._prompt_fact_answerability(case)
        expected = case["evaluator_only"]["expected_content"]["facts"]
        for slot in ("f2", "f8", "f9"):
            self.assertEqual(answerability[slot]["status"], "inferable")
            self.assertTrue(answerability[slot]["value"])
            self.assertFalse(expected[slot])

    def test_offline_taxonomy_covers_complete_executed_prefix(self):
        taxonomy = DIAGNOSTIC._taxonomy(self.population, self.runs)
        self.assertEqual(taxonomy["audit_scope"]["development_cases_audited"], 16)
        self.assertEqual(taxonomy["audit_scope"]["confirmation_cases_loaded"], 0)
        self.assertEqual(
            taxonomy["summary"]["cases_with_invalid_evaluator_answerability"],
            16,
        )
        self.assertEqual(taxonomy["summary"]["missed_unresolved_relations"], 68)
        self.assertEqual(taxonomy["summary"]["transformation_pairs"], 8)
        self.assertEqual(taxonomy["summary"]["transformation_exact"], 0)

    def test_answerability_gate_nulls_paid_conditions(self):
        taxonomy = DIAGNOSTIC._taxonomy(self.population, self.runs)
        selection = DIAGNOSTIC._case_selection(taxonomy)
        self.assertEqual(selection["selected_case_count"], 4)
        self.assertEqual(len(selection["equivalent_pairs"]), 2)
        self.assertTrue(selection["stop_gate"]["triggered"])
        self.assertFalse(selection["stop_gate"]["new_model_inference_authorized"])
        self.assertTrue(
            all(not item["answerability_valid"] for item in selection["selected_cases"])
        )

    def test_stopped_cost_is_zero_and_below_user_ceiling(self):
        accounting = DIAGNOSTIC._cost_accounting()
        self.assertEqual(accounting["logical_calls"], 0)
        self.assertEqual(accounting["provider_submissions"], 0)
        self.assertEqual(accounting["total_incremental_cost"], 0.0)
        self.assertLess(accounting["total_incremental_cost"], 0.25)


if __name__ == "__main__":
    unittest.main()
