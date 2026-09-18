from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ser.evaluation.authz_v1_3_1_harness import (
    CategoryMatchFloorComponent,
    Component,
    DegenerateNullComponent,
    HistoricalEstimatorComponent,
    load_development_bundle,
    oracle_usefulness_baseline,
)
from tools.validate_authzgym_v1_3_1_component_firewall import (
    CHECK_LABELS,
    check_1_allowlist,
    check_2_restricted_mutation,
    check_4_ordinal_non_consumption,
    check_5_surface_non_consumption,
    check_7_no_shared_state,
    validate,
)


class _LeakFixture(Component):
    """Base for negative controls: a firewall_fixture may see the live bundle."""

    firewall_fixture = True
    name = "leak_fixture"
    identifier = "leak_fixture"

    def __init__(self):
        self.bundle = None
        self.case = None

    def bind_bundle(self, bundle):
        self.bundle = bundle

    def bind_case(self, case):
        self.case = case

    def declared_ties(self, sealed):
        return [list(sealed.legal_target_slots)]


class LeakyLineCountFixture(_LeakFixture):
    """Reads the forbidden public surface statistic ``line_count``."""

    name = "fixture_reads_line_count"
    identifier = "fixture_reads_line_count"

    def values(self, sealed):
        inventory = self.case["model_visible_input"]["public_artifact_inventory"]
        counts = {int(item["slot"]): int(item["line_count"]) for item in inventory}
        return {slot: float(counts[slot]) for slot in sealed.legal_target_slots}


class LeakyOrdinalFixture(_LeakFixture):
    """Reads the restricted canonical ordinals."""

    name = "fixture_reads_ordinals"
    identifier = "fixture_reads_ordinals"

    def values(self, sealed):
        case_id = str(self.case["case_id"])
        ordinals = self.bundle.restricted[case_id][
            "canonical_source_ordinal_by_variant_slot"
        ]
        return {
            slot: float(ordinals[f"t{slot}"]) for slot in sealed.legal_target_slots
        }


class LeakyUsefulnessFixture(_LeakFixture):
    """Reads evaluator usefulness, which restricted mutation must not reach."""

    name = "fixture_reads_usefulness"
    identifier = "fixture_reads_usefulness"

    def values(self, sealed):
        case_id = str(self.case["case_id"])
        usefulness = self.bundle.restricted[case_id][
            "usefulness_by_variant_target_slot"
        ]
        return {slot: float(usefulness[f"t{slot}"]) for slot in sealed.legal_target_slots}


FIXTURE_WITH_MODULE_CACHE = '''
CACHE = {}


class CachingComponent:
    name = "fixture_module_cache"
    identifier = "fixture_module_cache"

    def values(self, sealed):
        CACHE.setdefault("seen", 0)
        CACHE["seen"] += 1
        return {slot: 0.0 for slot in sealed.legal_target_slots}

    def declared_ties(self, sealed):
        return [list(sealed.legal_target_slots)]
'''

FIXTURE_WITH_ORDINAL_REFERENCE = '''
TOKEN = "canonical_source_ordinal_by_variant_slot"


class OrdinalComponent:
    name = "fixture_ordinal_reference"
    identifier = "fixture_ordinal_reference"

    def values(self, sealed):
        return {slot: 0.0 for slot in sealed.legal_target_slots}

    def declared_ties(self, sealed):
        return [list(sealed.legal_target_slots)]
'''


class ComponentFirewallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load_development_bundle()

    def test_baselines_pass_the_full_suite(self):
        for component in (
            HistoricalEstimatorComponent(),
            DegenerateNullComponent(),
            CategoryMatchFloorComponent(),
        ):
            result = validate(component, component_name=type(component).__name__)
            failing = [
                label
                for label in CHECK_LABELS
                if not result["checks"][label]["passed"]
            ]
            self.assertTrue(result["passed"], msg=f"{component.identifier}: {failing}")

    def test_b3_is_exempt_by_definition(self):
        component = oracle_usefulness_baseline(self.bundle)
        self.assertTrue(component.upper_bound_only)
        self.assertFalse(component.gate_eligible)

    def test_line_count_fixture_is_rejected_by_check_5(self):
        result = check_5_surface_non_consumption(LeakyLineCountFixture())
        self.assertFalse(result["passed"])
        self.assertTrue(result["failing_modes"])

    def test_ordinal_fixture_is_rejected_by_check_4(self):
        result = check_4_ordinal_non_consumption(
            LeakyOrdinalFixture(), module_path=None
        )
        self.assertFalse(result["passed"])
        self.assertFalse(result["ordinal_permutation_stable"])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture_ordinal_reference.py"
            path.write_text(FIXTURE_WITH_ORDINAL_REFERENCE, encoding="utf-8")
            static = check_4_ordinal_non_consumption(
                HistoricalEstimatorComponent(), module_path=path
            )
            self.assertFalse(static["passed"])
            self.assertIn(
                "canonical_source_ordinal_by_variant_slot", static["static_violations"]
            )

    def test_restricted_leak_fixture_is_rejected_by_check_2(self):
        result = check_2_restricted_mutation(LeakyUsefulnessFixture())
        self.assertFalse(result["passed"])
        self.assertTrue(result["failing_mutations"])

    def test_module_cache_fixture_is_rejected_by_check_7(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture_module_cache.py"
            path.write_text(FIXTURE_WITH_MODULE_CACHE, encoding="utf-8")
            result = check_7_no_shared_state(
                HistoricalEstimatorComponent(), module_path=path
            )
            self.assertFalse(result["passed"])
            self.assertTrue(result["static_findings"])

    def test_forbidden_import_fixture_is_rejected_by_check_1(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture_bad_import.py"
            path.write_text(
                "from ser.authzgym.generation import LOGICAL_ROLES\n", encoding="utf-8"
            )
            result = check_1_allowlist(
                HistoricalEstimatorComponent(), module_path=path
            )
            self.assertFalse(result["passed"])
            self.assertFalse(result["parts"]["static_import_closure"]["passed"])


if __name__ == "__main__":
    unittest.main()
