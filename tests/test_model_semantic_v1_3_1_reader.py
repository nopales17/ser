"""Section-6 reader, ledger and static-bypass tests for `model-semantic-v1.3.1-N1`.

Handoff step 3. These tests run before any other stage and contain no network
access. The negative tests are the guard's own pre-condition: handoff section
0.2 requires the never-open predicate to be unit-tested before any other step
runs.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from ser.evaluation.authz_model_semantic_v1_3_1 import (
    AUDITED_READER_PATH,
    CONDITION_DIR,
    CONFIRMATION_DIR,
    NEVER_OPEN_V13_EXPLICIT,
    REQUIRED_RECORD_FIELDS,
    ROOT,
    V13_DIR,
    AccessLedgerError,
    AuditedReader,
    ReadBypassError,
    SpentPopulationAccess,
    check_static_read_bypass,
    file_sha256,
    is_never_open_path,
    never_open_v13_names,
    validate_access_ledger,
)


THIS_TOOL = Path(__file__).resolve()
DEVELOPMENT_POPULATION = V13_DIR / "DEVELOPMENT_PUBLIC_POPULATION.json"
CONFIRMATION_V13 = V13_DIR / "CONFIRMATION_PUBLIC_POPULATION.json"
CONFIRMATION_V13_1 = CONFIRMATION_DIR / "CONFIRMATION_PUBLIC_POPULATION.json"
CONFIRMATION_V13_1_SEAL = CONFIRMATION_DIR / "CONFIRMATION_V1_3_1_SEAL.json"


def _reader(ledger: Path, stage: str = "test") -> AuditedReader:
    return AuditedReader(
        actor="test_runner",
        stage=stage,
        tool_path=THIS_TOOL,
        authorization="unit test",
        ledger_path=ledger,
    )


class NeverOpenPredicateTests(unittest.TestCase):
    def test_v13_confirmation_names_are_never_open(self) -> None:
        for name in NEVER_OPEN_V13_EXPLICIT:
            self.assertTrue(is_never_open_path(V13_DIR / name), name)
        self.assertTrue(is_never_open_path(CONFIRMATION_V13))
        self.assertTrue(
            is_never_open_path(V13_DIR / "annotations" / "confirmation_annotations.jsonl")
        )
        self.assertTrue(
            is_never_open_path(V13_DIR / "PUBLIC_BUNDLE" / "CONFIRMATION_PUBLIC_POPULATION.json")
        )
        self.assertTrue(
            is_never_open_path(
                V13_DIR / "RESTRICTED_BUNDLE" / "CONFIRMATION_TRANSFORMATION_MAPS.json"
            )
        )

    def test_v13_development_paths_are_openable(self) -> None:
        self.assertFalse(is_never_open_path(DEVELOPMENT_POPULATION))
        self.assertFalse(is_never_open_path(V13_DIR / "PUBLIC_CONTRACT.json"))
        self.assertFalse(is_never_open_path(V13_DIR / "ORACLE_VALIDATION.json"))

    def test_confirmation_directory_predicate(self) -> None:
        self.assertFalse(is_never_open_path(CONFIRMATION_V13_1_SEAL))
        self.assertFalse(
            is_never_open_path(CONFIRMATION_DIR / "CONFIRMATION_V1_3_1_ORACLE_VALIDATION.json")
        )
        self.assertFalse(is_never_open_path(CONFIRMATION_DIR / "REPORT.md"))
        self.assertTrue(is_never_open_path(CONFIRMATION_V13_1))
        self.assertTrue(
            is_never_open_path(CONFIRMATION_DIR / "CONFIRMATION_V1_3_1_FREEZE_RECORD.json")
        )
        self.assertTrue(
            is_never_open_path(CONFIRMATION_DIR / "FROZEN_INPUTS_V1_3_1.json")
        )
        self.assertTrue(
            is_never_open_path(
                CONFIRMATION_DIR / "annotations" / "confirmation_v1_3_1_annotations.jsonl"
            )
        )

    def test_every_section_0_2_name_is_present(self) -> None:
        names = never_open_v13_names()
        self.assertIn("CONFIRMATION_PUBLIC_POPULATION.json", names)
        self.assertIn("CONFIRMATION_RESTRICTED_POPULATION.json", names)
        self.assertIn("CONFIRMATION_SCHEDULE.json", names)
        self.assertIn("CONFIRMATION_TRANSFORMATION_MAPS.json", names)
        self.assertIn("annotations/confirmation_annotations.jsonl", names)
        for name in names:
            self.assertTrue((V13_DIR / name).exists(), name)


class LedgerRecordTests(unittest.TestCase):
    def test_one_record_per_open_with_required_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ACCESS_LEDGER.jsonl"
            reader = _reader(ledger)
            reader.read_bytes(DEVELOPMENT_POPULATION)
            reader.hash_file(V13_DIR / "PUBLIC_CONTRACT.json")
            reader.read_json(V13_DIR / "MODEL_TRANSPORT_CONFIG.json")
            rows = [json.loads(line) for line in ledger.read_text().splitlines()]
            self.assertEqual(len(rows), 3)
            for row in rows:
                for name in REQUIRED_RECORD_FIELDS:
                    self.assertIn(name, row)
                self.assertEqual(row["tool_sha256"], file_sha256(THIS_TOOL))
                self.assertEqual(row["tool_path"], str(THIS_TOOL.relative_to(ROOT)))
                self.assertIsInstance(row["process_id"], int)
                self.assertGreater(row["process_id"], 0)
                self.assertTrue(row["timestamp_utc"])

    def test_tool_sha256_matches_caller_tool_file_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ACCESS_LEDGER.jsonl"
            _reader(ledger).read_bytes(DEVELOPMENT_POPULATION)
            row = json.loads(ledger.read_text().splitlines()[0])
            self.assertEqual(row["tool_sha256"], file_sha256(THIS_TOOL))

    def test_stat_only_does_not_open(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ACCESS_LEDGER.jsonl"
            reader = _reader(ledger)
            value = reader.stat_only(CONFIRMATION_V13_1)
            self.assertTrue(value["present"])
            self.assertTrue(value["never_open"])
            self.assertEqual(reader.never_open_opens, [])
            row = json.loads(ledger.read_text().splitlines()[0])
            self.assertEqual(row["operation"], "stat")
            self.assertEqual(row["file_sha256"], "")
            self.assertTrue(row["detail"].startswith("stat only"))
            # A stat of a never-open path is not an open and must validate.
            self.assertTrue(validate_access_ledger(ledger)["passes"])

    def test_confirmation_v1_3_path_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            reader = _reader(Path(tmp) / "ACCESS_LEDGER.jsonl")
            with self.assertRaises(SpentPopulationAccess):
                reader.read_bytes(CONFIRMATION_V13)
            with self.assertRaises(SpentPopulationAccess):
                reader.read_bytes(V13_DIR / "annotations" / "confirmation_annotations.jsonl")
            with self.assertRaises(SpentPopulationAccess):
                reader.hash_file(V13_DIR / "CONFIRMATION_SCHEDULE.json")
            self.assertFalse(Path(reader.ledger_path).exists())

    def test_confirmation_v1_3_1_path_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            reader = _reader(Path(tmp) / "ACCESS_LEDGER.jsonl")
            with self.assertRaises(SpentPopulationAccess):
                reader.read_bytes(CONFIRMATION_V13_1)
            with self.assertRaises(SpentPopulationAccess):
                reader.read_bytes(CONFIRMATION_DIR / "CONFIRMATION_V1_3_1_FREEZE_RECORD.json")
            with self.assertRaises(SpentPopulationAccess):
                reader.read_json(
                    CONFIRMATION_DIR / "annotations" / "confirmation_v1_3_1_annotations.jsonl"
                )

    def test_oracle_validation_confirmation_block_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            reader = _reader(Path(tmp) / "ACCESS_LEDGER.jsonl")
            with self.assertRaises(SpentPopulationAccess):
                reader.read_json(V13_DIR / "ORACLE_VALIDATION.json", block="confirmation")

    def test_ledger_validation_reports_never_open_opens(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ACCESS_LEDGER.jsonl"
            record = {name: "" for name in REQUIRED_RECORD_FIELDS}
            record.update(
                {
                    "schema_version": 1,
                    "path": str(CONFIRMATION_V13_1.relative_to(ROOT)),
                    "class": "confirmation",
                    "operation": "read",
                    "tool_sha256": file_sha256(THIS_TOOL),
                }
            )
            ledger.write_text(json.dumps(record, sort_keys=True) + "\n", encoding="utf-8")
            result = validate_access_ledger(ledger)
            self.assertEqual(result["never_open_open_count"], 1)
            self.assertFalse(result["passes"])

    def test_ledger_validation_flags_missing_required_field(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ACCESS_LEDGER.jsonl"
            ledger.write_text(json.dumps({"schema_version": 1}) + "\n", encoding="utf-8")
            result = validate_access_ledger(ledger)
            self.assertEqual(result["malformed_record_indices"], [0])
            self.assertFalse(result["passes"])


class StaticBypassTests(unittest.TestCase):
    def test_condition_modules_have_no_bypass(self) -> None:
        targets = [
            Path("src/ser/evaluation/authz_model_semantic_v1_3_1.py"),
            Path("src/ser/authzgym/semantic_contract_v1_3.py"),
            Path("src/ser/authzgym/supervised_transport_v1_3.py"),
            Path("tools/verify_authzgym_model_condition.py"),
            Path("tools/score_authzgym_model_semantic.py"),
            Path("tools/run_authzgym_model_semantic_development.py"),
        ]
        existing = [ROOT / item for item in targets if (ROOT / item).is_file()]
        self.assertTrue(existing)
        result = check_static_read_bypass(existing)
        self.assertTrue(result["passes"], result["violations"])
        self.assertIn(str(AUDITED_READER_PATH.relative_to(ROOT)), result["exempt_paths"])

    def test_static_check_fails_on_bypassing_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "bypass_fixture.py"
            fixture.write_text(
                "import json\n"
                "from pathlib import Path\n"
                "def leak(path):\n"
                "    raw = Path(path).read_bytes()\n"
                "    text = open(path).read()\n"
                "    value = json.load(open(path))\n"
                "    return raw, text, value\n",
                encoding="utf-8",
            )
            with self.assertRaises(ReadBypassError):
                from ser.evaluation.authz_model_semantic_v1_3_1 import assert_no_read_bypass

                assert_no_read_bypass([fixture])
            result = check_static_read_bypass([fixture])
            self.assertFalse(result["passes"])
            self.assertGreaterEqual(len(result["violations"]), 3)

    def test_write_only_open_is_not_a_read_bypass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp) / "writer_fixture.py"
            fixture.write_text(
                "def write(path, payload):\n"
                "    with open(path, 'w', encoding='utf-8') as handle:\n"
                "        handle.write(payload)\n",
                encoding="utf-8",
            )
            self.assertTrue(check_static_read_bypass([fixture])["passes"])

    def test_static_check_target_must_exist(self) -> None:
        with self.assertRaises(ReadBypassError):
            check_static_read_bypass([CONDITION_DIR / "does_not_exist.py"])


if __name__ == "__main__":
    unittest.main()
