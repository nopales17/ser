from __future__ import annotations

import unittest

from tools.compute_authorized_information_ceiling import (
    TIER1_TOP1_REQUIRED,
    TIER1_TOP2_REQUIRED,
    exhaustive_ceiling,
    tier1,
    tier2,
    tier2_grouped,
)
from ser.evaluation.authz_v1_3_1_harness import load_development_bundle


class ExhaustiveCeilingTests(unittest.TestCase):
    def test_every_target_its_own_class_attains_both(self):
        ceiling = exhaustive_ceiling([[1], [2], [3]], {1: 0.2, 2: 0.5, 3: 1.0})
        self.assertTrue(ceiling["top1"])
        self.assertTrue(ceiling["top2"])

    def test_known_three_target_fixture(self):
        # Class [1, 2] keeps the ordinal order 1 then 2, so the best target 2 can
        # be placed second but never first; class [3] is separable.
        ceiling = exhaustive_ceiling([[1, 2], [3]], {1: 0.2, 2: 1.0, 3: 0.5})
        self.assertFalse(ceiling["top1"])
        self.assertTrue(ceiling["top2"])

    def test_single_class_ceiling_is_the_ordinal_tie_break(self):
        ceiling = exhaustive_ceiling(
            [[1, 2, 3]], {1: 0.1, 2: 0.2, 3: 0.3}
        )
        self.assertFalse(ceiling["top1"])
        self.assertFalse(ceiling["top2"])
        ceiling_reversed = exhaustive_ceiling(
            [[3, 2, 1]], {1: 0.1, 2: 0.2, 3: 0.3}
        )
        self.assertTrue(ceiling_reversed["top1"])
        self.assertTrue(ceiling_reversed["top2"])

    def test_class_structure_must_cover_legal_targets(self):
        with self.assertRaises(ValueError):
            exhaustive_ceiling([[1], [2]], {1: 1.0, 2: 0.5, 3: 0.0})


class TierCeilingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load_development_bundle()
        cls.result = tier1(cls.bundle)

    def test_tier1_is_the_frozen_recorded_ceiling(self):
        self.assertEqual(self.result["case_count"], 8)
        self.assertAlmostEqual(self.result["tier1_top1_ceiling"], 0.75, places=12)
        self.assertAlmostEqual(self.result["tier1_top2_ceiling"], 1.0, places=12)
        self.assertGreaterEqual(self.result["tier1_top1_ceiling"], TIER1_TOP1_REQUIRED)
        self.assertGreaterEqual(self.result["tier1_top2_ceiling"], TIER1_TOP2_REQUIRED)

    def test_tier1_records_class_structure_per_case(self):
        for row in self.result["per_case"]:
            self.assertEqual(
                sum(row["class_sizes"]), 5, msg=row["case_id"]
            )
            self.assertTrue(row["class_size_of_maximum_usefulness_targets"])
            for size in row["class_size_of_maximum_usefulness_targets"].values():
                self.assertGreaterEqual(size, 1)
                self.assertLessEqual(size, 5)
            self.assertEqual(len(row["classes_by_ordinal"]), row["class_count"])
            self.assertTrue(row["attainable_top2"], msg=row["case_id"])

    def test_tier2_collapses_cases_sharing_a_signature(self):
        shared = [
            ("sig", [[1], [2], [3]], {1: 0.2, 2: 0.5, 3: 1.0}),
            ("sig", [[1], [2], [3]], {1: 0.2, 2: 1.0, 3: 0.5}),
        ]
        collapsed = tier2_grouped(shared)
        self.assertEqual(collapsed["signature_group_count"], 1)
        self.assertAlmostEqual(collapsed["tier2_top1_ceiling"], 0.5, places=12)
        self.assertAlmostEqual(collapsed["tier2_top2_ceiling"], 1.0, places=12)
        split = tier2_grouped([("sig_a", *shared[0][1:]), ("sig_b", *shared[1][1:])])
        self.assertEqual(split["signature_group_count"], 2)
        self.assertAlmostEqual(split["tier2_top1_ceiling"], 1.0, places=12)

    def test_tier2_on_real_cases_is_bounded_by_tier1(self):
        result = tier2(self.bundle, lambda sealed: "constant")
        self.assertLessEqual(
            result["tier2_top1_ceiling"], self.result["tier1_top1_ceiling"] + 1e-12
        )
        self.assertLessEqual(
            result["tier2_top2_ceiling"], self.result["tier1_top2_ceiling"] + 1e-12
        )


if __name__ == "__main__":
    unittest.main()
