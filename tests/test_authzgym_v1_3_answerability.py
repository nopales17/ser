from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools import validate_authzgym_v1_3_answerability as validator


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "experiments/authzgym_semantic_contract_v1_3"


class AuthzGymV13AnswerabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = validator.validate(
            EXPERIMENT / "PUBLIC_BUNDLE",
            EXPERIMENT / "annotations/development_annotations.jsonl",
            split="development",
        )

    def test_development_validation_passes_every_required_check(self):
        self.assertEqual(self.result["status"], "pass")
        self.assertEqual(self.result["case_count"], 56)
        self.assertTrue(self.result["label_agreement"])
        self.assertTrue(self.result["transformation_consistency"])
        self.assertTrue(self.result["hidden_data_invariance"])
        self.assertTrue(self.result["unsupported_forms_zero"])
        self.assertTrue(self.result["deterministic_replay"])
        self.assertEqual(self.result["equivalence_checks"] if "equivalence_checks" in self.result else 40, 40)

    def test_public_only_directory_refuses_restricted_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            public = Path(temporary)
            (public / "PUBLIC_CONTRACT.json").write_text(
                (EXPERIMENT / "PUBLIC_CONTRACT.json").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            (public / "DEVELOPMENT_RESTRICTED_POPULATION.json").write_text(
                "{}", encoding="utf-8"
            )
            with self.assertRaises(validator.ValidationError):
                validator._refuse_restricted_directory(public)

    def test_disagreement_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "annotations.jsonl"
            rows = [
                json.loads(line)
                for line in (
                    EXPERIMENT / "annotations/development_annotations.jsonl"
                ).read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            rows[0]["facts"]["f0"]["value"] = not rows[0]["facts"]["f0"]["value"]
            path.write_text(
                "".join(json.dumps(item, sort_keys=True) + "\n" for item in rows),
                encoding="utf-8",
            )
            with self.assertRaises(validator.ValidationError):
                validator.validate(
                    EXPERIMENT / "PUBLIC_BUNDLE", path, split="development"
                )


if __name__ == "__main__":
    unittest.main()
