from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from ser.evaluation.artifacts import (
    freeze_population,
    load_population,
    verify_record_hash,
    write_new_json,
)
from ser.microgym.families import build_problem_specs
from ser.microgym.model import EpisodeSpec


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.problem = build_problem_specs()[0]
        self.episode = EpisodeSpec(
            "artifact-episode",
            self.problem.problem_id,
            self.problem.hypotheses[0],
            10,
            tuple(test.public.action_id for test in self.problem.tests),
        )

    def test_population_manifest_round_trip_and_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "population.json"
            digest = freeze_population(path, (self.problem,), (self.episode,))
            problems, episodes, loaded_digest = load_population(path)
            self.assertEqual(digest, loaded_digest)
            self.assertEqual(problems, (self.problem,))
            self.assertEqual(episodes, (self.episode,))

    def test_population_manifest_tampering_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "population.json"
            freeze_population(path, (self.problem,), (self.episode,))
            raw = json.loads(path.read_text())
            raw["episodes"][0]["environment_realization_seed"] += 1
            path.write_text(json.dumps(raw))
            with self.assertRaises(ValueError):
                load_population(path)

    def test_writes_fail_closed_instead_of_overwriting(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "value.json"
            write_new_json(path, {"value": 1})
            with self.assertRaises(FileExistsError):
                write_new_json(path, {"value": 2})

    def test_record_hash_detects_change(self):
        from ser.core.types import content_hash

        record = {"schema_version": 1, "value": 2}
        record["record_hash"] = content_hash(record)
        self.assertTrue(verify_record_hash(record))
        record["value"] = 3
        self.assertFalse(verify_record_hash(record))


if __name__ == "__main__":
    unittest.main()
