from __future__ import annotations

import unittest

from ser.evaluation.authz_v1_3_1_harness import (
    Component,
    HistoricalEstimatorComponent,
    baseline_b0,
    build_component_input,
    degeneracy_census,
    is_non_degenerate,
    load_development_bundle,
    own_ranking_invariance,
    tie_dependence,
    leave_one_source_out,
)


class ConstantComponent(Component):
    """A component with no discriminating value at all."""

    identifier = "synthetic_constant"
    name = "synthetic_constant"

    def values(self, sealed):
        return {slot: 0.0 for slot in sealed.legal_target_slots}

    def declared_ties(self, sealed):
        return [list(sealed.legal_target_slots)]


class SlotIndexTieBreakComponent(Component):
    """Breaks its own top tie by raw slot index, which is not equivariant."""

    identifier = "synthetic_slot_tie_break"
    name = "synthetic_slot_tie_break"

    def values(self, sealed):
        return {slot: 0.0 for slot in sealed.legal_target_slots}

    def declared_ties(self, sealed):
        return [[slot] for slot in sorted(sealed.legal_target_slots)]


class DeclaredTieComponent(Component):
    """Legitimately declares the top tie and delegates it to the evaluator."""

    identifier = "synthetic_declared_tie"
    name = "synthetic_declared_tie"

    def values(self, sealed):
        return {slot: 0.0 for slot in sealed.legal_target_slots}

    def declared_ties(self, sealed):
        return [list(sealed.legal_target_slots)]


class LargestClassComponent(Component):
    """Ties exactly one category-vector class for first place."""

    identifier = "synthetic_largest_class"
    name = "synthetic_largest_class"

    def _classes(self, sealed):
        grouped: dict[tuple[bool, ...], list[int]] = {}
        for slot in sealed.legal_target_slots:
            grouped.setdefault(sealed.category_vector(slot), []).append(slot)
        return list(grouped.values())

    def values(self, sealed):
        classes = self._classes(sealed)
        top = max(classes, key=len)
        return {
            slot: (1.0 if slot in top else 0.0)
            for slot in sealed.legal_target_slots
        }

    def declared_ties(self, sealed):
        values = self.values(sealed)
        groups = {}
        for slot in sealed.legal_target_slots:
            groups.setdefault(values[slot], []).append(slot)
        return [groups[level] for level in sorted(groups, reverse=True)]


class SpanningClassComponent(Component):
    """Puts one target from each of two different classes at the top."""

    identifier = "synthetic_spanning_classes"
    name = "synthetic_spanning_classes"

    def values(self, sealed):
        classes = {}
        for slot in sealed.legal_target_slots:
            classes.setdefault(sealed.category_vector(slot), []).append(slot)
        top = [min(group) for group in classes.values()][:2]
        return {
            slot: (1.0 if slot in top else 0.0)
            for slot in sealed.legal_target_slots
        }

    def declared_ties(self, sealed):
        values = self.values(sealed)
        groups = {}
        for slot in sealed.legal_target_slots:
            groups.setdefault(values[slot], []).append(slot)
        return [groups[level] for level in sorted(groups, reverse=True)]


class InvarianceInstrumentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load_development_bundle()
        cls.b0 = baseline_b0(cls.bundle)

    def test_b0_selection_equivariance_fixture_still_holds(self):
        invariance = self.b0["own_ranking_invariance"]
        self.assertEqual(invariance["gate_metric"], "selection")
        self.assertEqual(invariance["selection_pass"], 36)
        self.assertEqual(invariance["selection_total"], 40)
        self.assertEqual(invariance["full_order_pass"], 25)
        self.assertTrue(invariance["full_order_is_descriptive_only"])

    def test_slot_index_tie_break_is_detected_as_non_equivariant(self):
        result = own_ranking_invariance(self.bundle, SlotIndexTieBreakComponent())
        self.assertLess(result["selection_pass"], 40)
        variants = {item["variant"] for item in result["selection_failures"]}
        # Slot-index tie-breaking is invariant to renaming but not to any
        # transformation that permutes inventory slots.
        self.assertIn("artifact_reordering", variants)
        self.assertIn("combined_permutation", variants)
        self.assertNotIn("symbol_renaming", variants)

    def test_declared_tie_delegating_to_the_evaluator_is_equivariant(self):
        result = own_ranking_invariance(self.bundle, DeclaredTieComponent())
        self.assertEqual(result["selection_pass"], 40)
        self.assertEqual(result["selection_total"], 40)

    def test_constant_component_fails_nd1_everywhere(self):
        result = is_non_degenerate(self.bundle, ConstantComponent(), nd3_floor=4)
        self.assertFalse(result["nd1_pass"])
        self.assertEqual(len(result["nd1_failures"]), 8)
        self.assertFalse(result["nd3_pass"])
        self.assertEqual(result["nd3_strict_unique_maximum_count"], 0)

    def test_single_class_tie_passes_nd2_and_spanning_tie_fails(self):
        inside = is_non_degenerate(
            self.bundle, LargestClassComponent(), nd3_floor=None
        )
        self.assertTrue(inside["nd2_pass"], msg=inside["nd2_failures"])
        self.assertTrue(inside["nd1_pass"])
        spanning = is_non_degenerate(
            self.bundle, SpanningClassComponent(), nd3_floor=None
        )
        self.assertFalse(spanning["nd2_pass"])
        self.assertEqual(len(spanning["nd2_failures"]), 8)

    def test_degeneracy_census_reports_unique_and_second_counts(self):
        census = degeneracy_census(self.bundle, ConstantComponent())
        self.assertEqual(census["strict_unique_maximum_count"], 0)
        self.assertEqual(census["non_unique_maximum_count"], 8)
        self.assertIn("strict_unique_second_count", census)
        baseline_census = degeneracy_census(self.bundle, HistoricalEstimatorComponent())
        self.assertEqual(baseline_census["strict_unique_maximum_count"], 4)

    def test_tie_dependence_and_loso_are_reported_not_gating(self):
        dependence = tie_dependence(self.bundle, HistoricalEstimatorComponent())
        self.assertEqual(dependence["tie_dependent_case_count"], 4)
        loso = leave_one_source_out(self.bundle, HistoricalEstimatorComponent())
        self.assertEqual(len(loso["folds"]), 8)
        self.assertFalse(loso["is_gate"])
        self.assertTrue(loso["fragile"])


if __name__ == "__main__":
    unittest.main()
