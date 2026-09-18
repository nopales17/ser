from __future__ import annotations

import unittest
from pathlib import Path

from ser.evaluation.authz_v1_3 import (
    FROZEN_ESTIMATOR_SHA256,
    assert_frozen_estimator,
    estimator_source_sha256,
)
from tools import validate_authzgym_v1_3_oracle as oracle


class AuthzGymV13OracleTests(unittest.TestCase):
    def test_estimator_hash_is_unchanged(self):
        assert_frozen_estimator()
        self.assertEqual(estimator_source_sha256(), FROZEN_ESTIMATOR_SHA256)

    def test_development_canonical_oracle_passes(self):
        result = oracle.validate("development")
        self.assertEqual(result["status"], "pass")
        self.assertGreaterEqual(result["canonical_observed"]["top1"], 0.60)
        self.assertGreaterEqual(result["canonical_observed"]["top2"], 0.80)
        self.assertLessEqual(
            result["canonical_observed"]["mean_normalized_regret"], 0.35
        )
        self.assertEqual(result["equivalence_failures"], [])

    def test_confirmation_oracle_blocker_is_preserved(self):
        result = oracle.validate("confirmation_v1_3")
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["gates"]["top2"])
        self.assertEqual(result["canonical_observed"]["top2"], 0.75)
        self.assertEqual(result["equivalence_failures"], [])


if __name__ == "__main__":
    unittest.main()
