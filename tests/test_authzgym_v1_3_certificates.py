from __future__ import annotations

import ast
import json
import unittest
from pathlib import Path

from ser.authzgym.v1_3_contract import load_public_contract


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "experiments/authzgym_semantic_contract_v1_3"


def _read_jsonl(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


class AuthzGymV13CertificateTests(unittest.TestCase):
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
            for item in _read_jsonl(
                EXPERIMENT / "annotations/development_annotations.jsonl"
            )
        }
        cls.cases = {item["case_id"]: item for item in cls.population["cases"]}

    def test_every_label_has_one_complete_certificate(self):
        for case_id, annotation in self.annotations.items():
            self.assertEqual(annotation["public_input_sha256"], self.cases[case_id]["runner_control"]["public_input_sha256"])
            for slot, record in annotation["facts"].items():
                self.assertIn("certificate", record)
                self.assertIn("rule_id", record)
                self.assertIn("value", record)
                self.assertIsInstance(record["value"], bool)
            for slot, record in annotation["candidate_effects"].items():
                for key in (
                    "candidate_slot",
                    "effect_family",
                    "retained_fact_vector_sha256",
                    "support_cue_booleans",
                    "counter_cue_booleans",
                    "truth_table_row",
                ):
                    self.assertIn(key, record)
            for target, relations in annotation["unresolved_targets"].items():
                for slot, record in relations.items():
                    self.assertIn("certificate", record)
                    self.assertIn("rule_id", record)

    def test_positive_witnesses_resolve_to_public_ast(self):
        for case_id, annotation in self.annotations.items():
            source = self.cases[case_id]["model_visible_input"]["current_artifact"]["source"]
            nodes = [
                node for node in ast.walk(ast.parse(source)) if hasattr(node, "lineno")
            ]
            for record in annotation["facts"].values():
                if not record["value"]:
                    continue
                for witness in record["positive_witnesses"]:
                    self.assertTrue(
                        any(
                            {
                                "line_start": node.lineno,
                                "column_start": node.col_offset + 1,
                                "line_end": getattr(node, "end_lineno", node.lineno),
                                "column_end": getattr(node, "end_col_offset", node.col_offset) + 1,
                            }
                            == witness["span"]
                            and ast.dump(
                                node,
                                include_attributes=False,
                                annotate_fields=True,
                            )
                            == witness["node_dump"]
                            for node in nodes
                        )
                    )

    def test_negative_certificates_cover_complete_scope(self):
        for annotation in self.annotations.values():
            for record in annotation["facts"].values():
                if record["value"]:
                    continue
                certificate = record["certificate"]
                self.assertEqual(certificate["kind"], "negative")
                self.assertEqual(
                    certificate["complete_inspected_scope"], "complete fixture module"
                )
                self.assertTrue(certificate["no_witness_matched"])
                self.assertIn("relevant_ast_node_kinds", certificate)
                self.assertIn("relevant_call_sites", certificate)

    def test_no_evaluator_role_or_mechanism_field_is_present(self):
        rendered = json.dumps(self.annotations)
        self.assertNotIn("mechanism_family", rendered)
        self.assertNotIn("logical_role", rendered)
        self.assertNotIn("correct_conclusion", rendered)
        self.assertNotIn("evaluator_usefulness", rendered)


if __name__ == "__main__":
    unittest.main()
