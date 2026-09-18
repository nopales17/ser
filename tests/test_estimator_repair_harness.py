from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import tools.run_estimator_repair_study as study
from ser.authzgym.policies import AuthzEpistemicState
from ser.evaluation.authz_v1_3 import FROZEN_ESTIMATOR_SHA256, action_diagnostic
from ser.evaluation.authz_v1_3_1_harness import (
    BaselineNotSelectableError,
    CategoryMatchFloorComponent,
    CORRIGENDUM_ADR,
    DegenerateNullComponent,
    FORBIDDEN_CONFIRMATION_PATHS,
    CANONICAL_VARIANT,
    ConfirmationAccessError,
    HarnessError,
    HistoricalEstimatorComponent,
    SelectionMetricError,
    V13_DIR,
    assert_candidate_eligible,
    baseline_record,
    baseline_b0,
    build_component_input,
    freeze_nd3_floor,
    guarded_sha256,
    integrity_files_v13,
    load_development_bundle,
    oracle_usefulness_baseline,
    read_json,
    read_jsonl,
    selection_cases,
    _ordinal_by_slot,
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
        # CORRIGENDUM.md section 1.3: step-1 reproduction is authorized against
        # the development-split value, not the confirmation-split transcription.
        self.assertAlmostEqual(
            observed["longest_artifact_regret"], 0.6583333333333333, places=12
        )
        self.assertAlmostEqual(
            self.baseline["recorded_expectation"]["longest_artifact_regret"],
            0.6583333333333333,
            places=12,
        )
        authority = self.baseline["recorded_expectation_authority"]
        self.assertIn(CORRIGENDUM_ADR, authority["longest_artifact_regret"])
        self.assertIn("CORRIGENDUM.md", authority["longest_artifact_regret"])
        self.assertTrue(self.baseline["reproduces_recorded_figures"])

    def test_own_ranking_invariance_baseline(self):
        invariance = self.baseline["own_ranking_invariance"]
        self.assertEqual(invariance["gate_metric"], "selection")
        self.assertEqual(invariance["candidate_requirement"], "40/40")
        self.assertEqual(invariance["recorded_b0_fixture"], "36/40")
        self.assertTrue(invariance["full_order_is_descriptive_only"])
        self.assertTrue(invariance["full_order_not_a_gate"])
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
                guarded_sha256(V13_DIR / relative),
                digest,
                msg=f"protected file changed: {relative}",
            )
        present = {
            str(path.relative_to(V13_DIR)) for path in integrity_files_v13()
        }
        self.assertEqual(present, set(PROTECTED_V13_FILES))

    def test_integrity_check_refuses_confirmation_paths(self):
        for relative, digest in PROTECTED_V13_FILES.items():
            self.assertEqual(guarded_sha256(V13_DIR / relative), digest)
        guarded = {str(path.relative_to(V13_DIR)) for path in integrity_files_v13()}
        self.assertEqual(guarded, set(PROTECTED_V13_FILES))
        for relative in FORBIDDEN_CONFIRMATION_PATHS:
            with self.assertRaises(ConfirmationAccessError, msg=relative):
                guarded_sha256(V13_DIR / relative)

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


class BaselineFreezeTests(unittest.TestCase):
    """Handoff step 4: B1/B2/B3 and the frozen B2-derived ND-3 floor."""

    @classmethod
    def setUpClass(cls):
        cls.bundle = load_development_bundle()
        cls.b0 = baseline_b0(cls.bundle)
        cls.records = {
            "B1": baseline_record(cls.bundle, DegenerateNullComponent()),
            "B2": baseline_record(cls.bundle, CategoryMatchFloorComponent()),
            "B3": baseline_record(cls.bundle, oracle_usefulness_baseline(cls.bundle)),
        }
        cls.floor = cls.records["B2"]["non_degeneracy"][
            "nd3_strict_unique_maximum_count"
        ]

    def test_b1_is_the_pure_ordinal_tie_break(self):
        component = DegenerateNullComponent()
        for case in self.bundle.canonical_cases():
            case_id = str(case["case_id"])
            sealed = build_component_input(
                case, self.bundle.response_for(case_id), self.bundle.contract
            )
            values = component.values(sealed)
            self.assertEqual(len(set(values.values())), 1)
            ordinal = _ordinal_by_slot(self.bundle, case_id)
            expected = sorted(sealed.legal_target_slots, key=lambda slot: ordinal[slot])
            self.assertEqual(component.declared_ties(sealed), [list(sealed.legal_target_slots)])
            self.assertEqual(
                self.records["B1"]["canonical_aggregate"]["top1"],
                sum(
                    1
                    for item in self.bundle.canonical_cases()
                    if self._ordinal_top1(item)
                )
                / 8,
            )
            self.assertEqual(sorted(expected), sorted(sealed.legal_target_slots))

    def _ordinal_top1(self, case) -> bool:
        case_id = str(case["case_id"])
        usefulness = self.bundle.restricted[case_id]["usefulness_by_variant_target_slot"]
        ordinal = self.bundle.restricted[case_id][
            "canonical_source_ordinal_by_variant_slot"
        ]
        best = max(float(value) for value in usefulness.values())
        ordered = sorted(usefulness, key=lambda slot: int(ordinal[slot]))
        return abs(float(usefulness[ordered[0]]) - best) <= 1e-12

    def test_b2_is_expressible_from_the_sealed_input_alone(self):
        component = CategoryMatchFloorComponent()
        for case in self.bundle.canonical_cases():
            case_id = str(case["case_id"])
            sealed = build_component_input(
                case, self.bundle.response_for(case_id), self.bundle.contract
            )
            family_index = {
                str(name): int(str(slot)[1:])
                for slot, name in sealed.contract_constants["relation_slots"].items()
            }
            supporting = {
                family
                for slot, family, _ in sealed.candidate_hypotheses
                if sealed.candidate_effects[slot] == "support"
            }
            reference = {
                slot: (
                    1.0
                    if any(
                        sealed.category_vector(slot)[family_index[family]]
                        for family in supporting
                    )
                    else 0.0
                )
                for slot in sealed.legal_target_slots
            }
            self.assertEqual(component.values(sealed), reference)
            self.assertTrue(getattr(sealed, "legal_target_count"))

    def test_b3_is_the_evaluator_channel_upper_bound(self):
        record = self.records["B3"]
        self.assertTrue(record["upper_bound_only"])
        self.assertFalse(record["gate_eligible"])
        self.assertAlmostEqual(record["canonical_aggregate"]["top1"], 1.0, places=12)
        self.assertAlmostEqual(record["canonical_aggregate"]["top2"], 1.0, places=12)
        self.assertAlmostEqual(
            record["canonical_aggregate"]["mean_normalized_regret"], 0.0, places=12
        )

    def test_b3_cannot_be_submitted_as_a_candidate(self):
        component = oracle_usefulness_baseline(self.bundle)
        with self.assertRaises(BaselineNotSelectableError):
            assert_candidate_eligible(component)
        assert_candidate_eligible(CategoryMatchFloorComponent())

    def test_non_degeneracy_of_baselines(self):
        b0 = self.b0["non_degeneracy"]
        self.assertEqual(len(b0["nd1_failures"]), 2)
        self.assertFalse(b0["nd1_pass"])
        b1 = self.records["B1"]["non_degeneracy"]
        self.assertEqual(len(b1["nd1_failures"]), 8)
        b2 = self.records["B2"]["non_degeneracy"]
        self.assertFalse(b2["nd1_pass"])
        self.assertEqual(self.floor, 4)
        self.assertEqual(b2["nd3_strict_unique_maximum_count"], 4)
        self.assertEqual(
            self.records["B3"]["non_degeneracy"]["nd3_strict_unique_maximum_count"],
            8,
        )

    def test_nd3_floor_is_written_once_and_never_changed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "BASELINES.json"
            path.write_text("{}\n", encoding="utf-8")
            self.assertTrue(freeze_nd3_floor(path, self.floor))
            original = path.read_bytes()
            self.assertFalse(freeze_nd3_floor(path, self.floor))
            self.assertEqual(path.read_bytes(), original)
            with self.assertRaises(HarnessError):
                freeze_nd3_floor(path, self.floor + 1)
            self.assertEqual(path.read_bytes(), original)


class DevelopmentReportTests(unittest.TestCase):
    """Handoff step 10: the report renders deterministically and fails closed."""

    STUDY_DIR = (
        ROOT / "experiments" / "authzgym_estimator_repair_v1_3_1"
    )
    ARTIFACTS = (
        "BASELINES.json",
        "INFORMATION_CEILING.json",
        "FIREWALL_V1_3_1_VALIDATION.json",
        "CANDIDATE_LEDGER.jsonl",
    )

    def _staged_dir(self, parent: Path) -> Path:
        target = parent / "study"
        target.mkdir()
        for name in self.ARTIFACTS:
            shutil.copy(self.STUDY_DIR / name, target / name)
        return target

    def test_report_renders_deterministically(self):
        with tempfile.TemporaryDirectory() as directory:
            target = self._staged_dir(Path(directory))
            study.render_report(target)
            first = (target / "DEVELOPMENT_REPORT.md").read_bytes()
            study.render_report(target)
            self.assertEqual((target / "DEVELOPMENT_REPORT.md").read_bytes(), first)

    def test_report_refuses_two_passing_candidates(self):
        with tempfile.TemporaryDirectory() as directory:
            target = self._staged_dir(Path(directory))
            ledger = target / "CANDIDATE_LEDGER.jsonl"
            records = [
                json.loads(line)
                for line in ledger.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            passing = next(
                item
                for item in records
                if item.get("record") == "candidate_result"
                and item["disposition"] == "admissible_pass"
            )
            duplicate = dict(passing)
            duplicate["candidate_id"] = "est-repair-v1.3.1-C-1"
            duplicate["arm"] = "C"
            ledger.write_text(
                ledger.read_text(encoding="utf-8")
                + json.dumps(duplicate, sort_keys=True)
                + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(SystemExit):
                study.render_report(target)

    def test_report_refuses_altered_claim_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            target = self._staged_dir(Path(directory))
            study.render_report(target)
            original = (target / "DEVELOPMENT_REPORT.md").read_text(encoding="utf-8")
            study.assert_report_sections(original)
            for altered in (
                original.replace(study.CLAIM_BOUNDARY_10_1, "under some conditions"),
                original.replace(study.SUFFICIENCY_QUALIFICATION, "this is the best repair"),
                original.replace(study.CLAIM_BOUNDARY_10_2, "nothing is out of scope"),
            ):
                with self.assertRaises(SystemExit):
                    study.assert_report_sections(altered)


if __name__ == "__main__":
    unittest.main()
