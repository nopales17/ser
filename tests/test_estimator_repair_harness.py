from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from ser.authzgym.policies import AuthzEpistemicState
from ser.evaluation.authz_v1_3 import FROZEN_ESTIMATOR_SHA256, action_diagnostic
from ser.evaluation.authz_v1_3_1_harness import (
    FORBIDDEN_CONFIRMATION_PATHS,
    CANONICAL_VARIANT,
    ConfirmationAccessError,
    HistoricalEstimatorComponent,
    SelectionMetricError,
    V13_DIR,
    baseline_b0,
    build_component_input,
    load_development_bundle,
    read_json,
    read_jsonl,
    selection_cases,
    _slot_to_artifact_id,
)


ROOT = Path(__file__).resolve().parents[1]

# Step-0 integrity fixture: every non-confirmation file under the frozen v1.3
# instrument directory, hashed at the start of the authorized study.
PROTECTED_V13_FILES = {
    "ANSWERABILITY_VALIDATION.json": "d686745236ac756a95071eb72aaacdc0ef20f8d2281fe12ee83821d1f21eb54b",
    "DEVELOPMENT_PUBLIC_POPULATION.json": "dda4e0c08a9c29a58a912fdcb5268ddf602aac79c47f6dd3fb94102b5dc8c365",
    "DEVELOPMENT_RESTRICTED_POPULATION.json": "1e75338a76db9128fb67ae5d71864424f0075dde401bb661d7ba2abd90e7e675",
    "DEVELOPMENT_SCHEDULE.json": "6e8c4e80fe9df0ae58dd87d5131411c97663f369fce2bdbafee779ce1fa65224",
    "DEVELOPMENT_SOURCE_MANIFEST.json": "e9c2ac40a0c6c7e5116c539073eb3a476d8e976ae0df209bed830508541e1b01",
    "DEVELOPMENT_TRANSFORMATION_MAPS.json": "3a6ef5638485a225388348965339b66b9948a955170339d91b33802e01fc0465",
    "FIREWALL_VALIDATION.json": "f729c760f9fd87b6dbacfddf30fb2e7b1df0ad78a28e680fc7700408f12b4793",
    "IMPLEMENTATION_PLAN.md": "70462424871e1d6ec7bf9f6116c06c4e1aad7da960c5b849ee8af0086c189c97",
    "MODEL_TRANSPORT_CONFIG.json": "9077d32dc10a25419636bc21e9e1766cc7ebc37c872e4ea5e5efd17a3d91e7f2",
    "ORACLE_BLOCKER.md": "6aa2998086b2bed7d8d0e19c2ea8aa70126437a6b427e7d72450b3c156fc7ed5",
    "ORACLE_VALIDATION.json": "eb4172d80bf642f66de2a22011267d3c0a1e1805fe5f6d0c3f16feff3eefff24",
    "PREREGISTRATION.md": "56d60cd38a027c075a69631fe73f194f5baa22f60011d99d9c047b43ad355604",
    "PRIOR_RESULT_CORRIGENDUM.md": "ff29be12ff0f4d6861f5a9ba7f31dde5ef325f4f6fcb8d451796fb8276878404",
    "PUBLIC_BUNDLE/DEVELOPMENT_PUBLIC_POPULATION.json": "dda4e0c08a9c29a58a912fdcb5268ddf602aac79c47f6dd3fb94102b5dc8c365",
    "PUBLIC_BUNDLE/DEVELOPMENT_SCHEDULE.json": "6e8c4e80fe9df0ae58dd87d5131411c97663f369fce2bdbafee779ce1fa65224",
    "PUBLIC_BUNDLE/PUBLIC_CONTRACT.json": "95df3f56cfabadd3aefa50e7fd5a3e6d77b7625c7db0860649a92ff4f213bb26",
    "PUBLIC_BUNDLE/prompts/semantic_observation_v1_3.txt": "6921e45042f5f34f3fcb25ba1d2732e3bcbc89a8ae12f1f2cb867520534dff9e",
    "PUBLIC_BUNDLE/schemas/semantic_vocabulary_v1_3.json": "06dea1e26856b216e5476803f3db9a4dd299f61f9a7927481d78db0da62c56c0",
    "PUBLIC_BUNDLE_MANIFEST.json": "b20dd663ea6c638d1c0dc7879b07022961195cf2539b1100a3e907927ac5df67",
    "PUBLIC_CONTRACT.json": "95df3f56cfabadd3aefa50e7fd5a3e6d77b7625c7db0860649a92ff4f213bb26",
    "RESTRICTED_BUNDLE/DEVELOPMENT_RESTRICTED_POPULATION.json": "1e75338a76db9128fb67ae5d71864424f0075dde401bb661d7ba2abd90e7e675",
    "RESTRICTED_BUNDLE/DEVELOPMENT_TRANSFORMATION_MAPS.json": "3a6ef5638485a225388348965339b66b9948a955170339d91b33802e01fc0465",
    "RESTRICTED_BUNDLE/annotations/development_annotations.jsonl": "d308e68b72020380bed7680749dd5f5dfe58935a511be1da32074aa107e2b817",
    "RESTRICTED_BUNDLE_MANIFEST.json": "28f921889e06fa496025ad6c20849e4fc5abd91941e205d179d3b52bedb1b585",
    "annotations/development_annotations.jsonl": "d308e68b72020380bed7680749dd5f5dfe58935a511be1da32074aa107e2b817",
    "prompts/semantic_observation_v1_3.txt": "6921e45042f5f34f3fcb25ba1d2732e3bcbc89a8ae12f1f2cb867520534dff9e",
    "schemas/semantic_vocabulary_v1_3.json": "06dea1e26856b216e5476803f3db9a4dd299f61f9a7927481d78db0da62c56c0",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class EstimatorRepairHarnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load_development_bundle()
        cls.baseline = baseline_b0(cls.bundle)

    def test_baseline_reproduction(self):
        observed = self.baseline["observed"]
        self.assertAlmostEqual(observed["canonical_top1"], 0.625, places=12)
        self.assertAlmostEqual(observed["canonical_top2"], 0.875, places=12)
        self.assertAlmostEqual(observed["canonical_regret"], 0.175, places=12)
        self.assertEqual(observed["illegal_target_count"], 0)
        self.assertEqual(observed["equivalence_pairs"], 40)
        self.assertEqual(observed["equivalence_failures"], [])
        self.assertTrue(self.baseline["reproduces_acceptance_figures"])

    def test_longest_artifact_readout(self):
        observed = self.baseline["observed"]
        self.assertAlmostEqual(observed["longest_artifact_top1"], 0.125, places=12)
        self.assertAlmostEqual(observed["longest_artifact_top2"], 0.375, places=12)
        # Handoff step 1 requires this exact figure. It is recorded here as
        # written so a mismatch fails loudly instead of being substituted.
        self.assertAlmostEqual(observed["longest_artifact_regret"], 0.7833, places=12)

    def test_own_ranking_invariance_baseline(self):
        invariance = self.baseline["own_ranking_invariance"]
        self.assertEqual(invariance["selection_total"], 40)
        self.assertEqual(invariance["selection_pass"], 36)
        failures = {
            (item["source_episode_id"], item["variant"])
            for item in invariance["selection_failures"]
        }
        expected = {
            ("asv1-d-5e6417ce899f", "artifact_identifier_variation"),
            ("asv1-d-5e6417ce899f", "combined_permutation"),
            ("asv1-d-8883a56f6778", "artifact_identifier_variation"),
            ("asv1-d-8883a56f6778", "combined_permutation"),
        }
        self.assertEqual(failures, expected)
        for source in {item[0] for item in expected}:
            case_id = next(
                case["case_id"]
                for case in self.bundle.canonical_cases()
                if case["source_episode_id"] == source
            )
            self.assertEqual(
                self.bundle.restricted[case_id]["source_family"], "ownership"
            )

    def test_selection_metric_arity(self):
        identifiers = self.bundle.canonical_case_ids()
        self.assertEqual(len(selection_cases(self.bundle, identifiers)), 8)
        with self.assertRaises(SelectionMetricError):
            selection_cases(self.bundle, identifiers[:7])
        non_canonical = [
            case["case_id"]
            for case in self.bundle.cases
            if case["variant"] != CANONICAL_VARIANT
        ]
        with self.assertRaises(SelectionMetricError):
            selection_cases(self.bundle, identifiers[:7] + (non_canonical[0],))
        with self.assertRaises(SelectionMetricError):
            selection_cases(self.bundle, tuple(non_canonical[:8]))

    def test_confirmation_paths_blocked(self):
        for relative in FORBIDDEN_CONFIRMATION_PATHS:
            target = V13_DIR / relative
            with self.assertRaises(ConfirmationAccessError, msg=relative):
                read_json(target)
            with self.assertRaises(ConfirmationAccessError, msg=relative):
                read_jsonl(target)
        with self.assertRaises(ConfirmationAccessError):
            read_json(V13_DIR / "ORACLE_VALIDATION.json", block="confirmation")
        # The permitted development companion file stays readable.
        self.assertIn("development", read_json(V13_DIR / "ORACLE_VALIDATION.json"))

    def test_protected_hashes_unchanged(self):
        self.assertEqual(
            sha256(ROOT / "src/ser/authzgym/policies.py"), FROZEN_ESTIMATOR_SHA256
        )
        for relative, digest in PROTECTED_V13_FILES.items():
            self.assertEqual(
                sha256(V13_DIR / relative), digest, msg=f"protected file changed: {relative}"
            )
        present = {
            str(path.relative_to(V13_DIR))
            for path in V13_DIR.rglob("*")
            if path.is_file() and "confirmation" not in path.name.lower()
        }
        self.assertEqual(present, set(PROTECTED_V13_FILES))

    def test_component_interface_reproduces_frozen_estimator(self):
        component = HistoricalEstimatorComponent()
        for case in self.bundle.cases:
            case_id = str(case["case_id"])
            response = self.bundle.response_for(case_id)
            sealed = build_component_input(case, response, self.bundle.contract)
            values = component.values(sealed)
            frozen = action_diagnostic(
                case, response, self.bundle.restricted[case_id], contract=self.bundle.contract
            )
            slot_by_identifier = {
                identifier: slot for slot, identifier in _slot_to_artifact_id(case).items()
            }
            expected = {
                slot_by_identifier[identifier]: value
                for identifier, value in frozen["values"].items()
            }
            self.assertEqual(set(values), set(expected), msg=case_id)
            for slot in expected:
                self.assertAlmostEqual(values[slot], expected[slot], places=12, msg=case_id)

    def test_sealed_input_excludes_forbidden_surface(self):
        case = self.bundle.canonical_cases()[0]
        sealed = build_component_input(
            case, self.bundle.response_for(str(case["case_id"])), self.bundle.contract
        )
        for forbidden in ("line_count", "public_id", "path", "exported_symbols", "public_label"):
            self.assertFalse(hasattr(sealed, forbidden), msg=forbidden)
        self.assertEqual(set(sealed.legal_target_slots), set(range(1, 6)))
        self.assertEqual(sealed.legal_target_count, 5)
        self.assertEqual(
            len(sealed.candidate_hypotheses), 4
        )


if __name__ == "__main__":
    unittest.main()
