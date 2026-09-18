from __future__ import annotations

import unittest
from pathlib import Path

from tools import validate_authzgym_v1_3_firewall as firewall


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "experiments/authzgym_semantic_contract_v1_3"


class AuthzGymV13FirewallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = firewall.validate(EXPERIMENT / "PUBLIC_BUNDLE")

    def test_all_firewall_checks_pass(self):
        self.assertEqual(self.result["status"], "pass")
        for name, check in self.result["checks"].items():
            self.assertEqual(check["status"], "pass", name)

    def test_normal_entry_rejects_oracle_arguments(self):
        from ser.authzgym.v1_3_public_input import (
            PublicInputV13Error,
            normal_request_bytes,
        )

        contract, prompt, _ = __import__(
            "ser.authzgym.v1_3_public_input", fromlist=["load_public_bundle"]
        ).load_public_bundle(EXPERIMENT / "PUBLIC_BUNDLE")
        del contract
        cases = __import__("json").loads(
            (EXPERIMENT / "DEVELOPMENT_PUBLIC_POPULATION.json").read_text(
                encoding="utf-8"
            )
        )["cases"]
        with self.assertRaises(PublicInputV13Error):
            normal_request_bytes(cases[0], prompt, oracle_view={"gold": True})


if __name__ == "__main__":
    unittest.main()
