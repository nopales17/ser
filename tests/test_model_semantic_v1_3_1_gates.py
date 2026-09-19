"""Gate, eligibility and S-7 structural-protection tests for `model-semantic-v1.3.1-N1`.

Handoff step 6A / preregistration sections 8.3, 8.6, 12, 12.1 and 15.
Authority: `PREREGISTRATION.md` section 12.1's three machine-enforced
structural guarantees, plus section 8.3's S-13, S-14 and S-15 screens. Every
fixture is synthetic. No model response is read and no model or provider call
is made.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from ser.authzgym.policies_v1_3_1 import EstimatorV1SalientCategory
from ser.evaluation.authz_v1_3_1_harness import (
    CANONICAL_VARIANT,
    EQUIVALENCE_VARIANTS,
    DevelopmentBundle,
)
from ser.evaluation.authz_model_semantic_v1_3_1 import (
    DIAGNOSTIC_ONLY_CONFIRMATION_ITEM,
    DIAGNOSTIC_ONLY_DEVELOPMENT_ITEM,
    DiagnosticOnly,
    DiagnosticOnlyMisuse,
    GATED_CONFIRMATION_ITEMS,
    GATED_DEVELOPMENT_ITEMS,
    SubstitutionMisuse,
    directional_continuity,
    effect_self_consistency,
    eligibility_report,
    evaluate_eligibility,
    own_selection_equivariance,
    paired_degradation,
    primary_endpoint,
)
from tests.test_model_semantic_v1_3_1_error_classes import (
    CANDIDATE_HYPOTHESES,
    CONTRACT,
    LEGAL,
    synthetic_facts,
    synthetic_response,
    truth_table_effects,
)


SOURCES = tuple(f"s{index}" for index in range(1, 9))
ROOT = Path(__file__).resolve().parents[1]
THIS_TOOL = Path(__file__).resolve()


def all_pass_items() -> dict[int, dict]:
    return {
        item: {
            "item": f"section-12 item {item}",
            "requirement": "synthetic",
            "observed": "synthetic",
            "pass": True,
        }
        for item in range(1, 24)
    }


def total_s7_failure_record() -> dict:
    """Every measured response is effect-inconsistent: C_response = 0.0."""

    records = []
    for index in range(4):
        facts = synthetic_facts()
        effects = truth_table_effects(facts)
        effects["c0"] = "contradict"
        records.append(
            {
                "case_id": f"synthetic-case-{index}",
                "split": "development",
                "repeat": 1 + (index % 2),
                "attempt_ordinal": 1,
                "source_episode_id": f"synthetic-source-{index}",
                "variant": "base_entry",
                "status": "measured",
                "facts": facts,
                "candidate_effects": effects,
                "candidate_hypotheses": CANDIDATE_HYPOTHESES,
            }
        )
    return effect_self_consistency(records, contract=CONTRACT)


def s13_rows(*, model_overrides: dict[str, dict | None] | None = None) -> tuple[dict, dict]:
    gold = {
        source: {"top1": 0.5, "top2": 0.75, "mean_normalized_regret": 0.4}
        for source in SOURCES
    }
    model = {source: dict(row) for source, row in gold.items()}
    for source, row in (model_overrides or {}).items():
        model[source] = row
    return gold, model


def s14_rows() -> list[dict]:
    return [
        {
            "source_episode_id": source,
            "variant": variant,
            "repeat": repeat,
            "base_repeat": repeat,
            "variant_response_present": True,
            "base_response_present": True,
            "variant_selection": [1],
            "base_selection": [1],
            "value_vector_equal": True,
            "response_semantically_equal": True,
        }
        for source in SOURCES
        for variant in ("a", "b", "c", "d", "e")
        for repeat in (1, 2)
    ]


class Section121GuaranteeOneTests(unittest.TestCase):
    def test_gated_development_items_is_the_frozen_literal_set(self) -> None:
        self.assertEqual(
            GATED_DEVELOPMENT_ITEMS,
            frozenset(range(1, 11)) | frozenset(range(12, 22)),
        )
        self.assertNotIn(DIAGNOSTIC_ONLY_DEVELOPMENT_ITEM, GATED_DEVELOPMENT_ITEMS)
        self.assertNotIn(22, GATED_DEVELOPMENT_ITEMS)
        self.assertNotIn(23, GATED_DEVELOPMENT_ITEMS)

    def test_confirmation_gated_set_also_excludes_s7(self) -> None:
        self.assertEqual(
            GATED_CONFIRMATION_ITEMS, frozenset(range(1, 14)) - {DIAGNOSTIC_ONLY_CONFIRMATION_ITEM}
        )
        self.assertNotIn(6, GATED_CONFIRMATION_ITEMS)

    def test_eligibility_refuses_a_gated_diagnostic_only_item(self) -> None:
        with self.assertRaises(DiagnosticOnlyMisuse):
            evaluate_eligibility(
                all_pass_items(),
                split="development",
                diagnostic_only={11: DiagnosticOnly({"violation_count": 0})},
                gated_items=frozenset({1, 11}),
            )


class Section121GuaranteeTwoTests(unittest.TestCase):
    def test_verdict_attribute_raises(self) -> None:
        wrapper = DiagnosticOnly(total_s7_failure_record())
        with self.assertRaises(DiagnosticOnlyMisuse):
            wrapper.verdict
        with self.assertRaises(DiagnosticOnlyMisuse):
            wrapper.passes
        with self.assertRaises(DiagnosticOnlyMisuse):
            wrapper["verdict"]

    def test_an_eligibility_computation_that_reads_it_raises(self) -> None:
        wrapper = DiagnosticOnly(total_s7_failure_record())

        def naive_eligibility(s7) -> str:
            return "pass" if s7.verdict == "pass" else "fail"

        with self.assertRaises(DiagnosticOnlyMisuse):
            naive_eligibility(wrapper)

    def test_the_sanctioned_reporting_access_still_works(self) -> None:
        record = total_s7_failure_record()
        wrapper = DiagnosticOnly(record)
        self.assertEqual(wrapper.as_record()["C_response"], 0.0)
        self.assertFalse(wrapper.as_record()["gate_applies"])


class Section121GuaranteeThreeTests(unittest.TestCase):
    def test_total_s7_failure_still_passes_and_stays_eligible(self) -> None:
        record = total_s7_failure_record()
        self.assertEqual(record["C_response"], 0.0)
        self.assertEqual(record["violation_count"], 4)
        report = eligibility_report(
            all_pass_items(),
            split="development",
            diagnostic_only={DIAGNOSTIC_ONLY_DEVELOPMENT_ITEM: DiagnosticOnly(record)},
        )
        self.assertEqual(report["verdict"], "pass")
        self.assertEqual(report["base_label"], "development_eligible")
        self.assertEqual(report["outcome_label"], "development_eligible (S-7 violations: 4)")
        self.assertNotIn(DIAGNOSTIC_ONLY_DEVELOPMENT_ITEM, report["gated_items"])
        violations = report["effect_self_consistency"]["11"]["violations"]
        self.assertEqual(len(violations), 4)
        for violation in violations:
            for field in (
                "case_id",
                "split",
                "repeat",
                "attempt_ordinal",
                "candidate_slot",
                "public_family",
                "submitted_fact_vector",
                "submitted_effect",
                "truth_table_effect",
            ):
                self.assertIn(field, violation)

    def test_s7_failure_does_not_hide_a_real_gate_failure(self) -> None:
        items = all_pass_items()
        items[17]["pass"] = False
        report = eligibility_report(
            items,
            split="development",
            diagnostic_only={11: DiagnosticOnly(total_s7_failure_record())},
        )
        self.assertEqual(report["base_label"], "semantic_screen_below_threshold")
        self.assertEqual(report["verdict"], "fail")

    def test_an_ungated_item_11_record_cannot_change_the_verdict(self) -> None:
        items = all_pass_items()
        items[11] = {"item": "S-7", "requirement": "diagnostic_only", "observed": None, "pass": False}
        report = eligibility_report(
            items,
            split="development",
            diagnostic_only={11: DiagnosticOnly(total_s7_failure_record())},
        )
        self.assertEqual(report["verdict"], "pass")
        self.assertEqual(report["base_label"], "development_eligible")


class PairedDegradationTests(unittest.TestCase):
    def test_mean_positive_excess_ignores_a_source_where_the_model_beats_gold(self) -> None:
        gold, model = s13_rows(
            model_overrides={
                "s1": {"top1": 0.6, "top2": 0.9, "mean_normalized_regret": 0.2}
            }
        )
        result = paired_degradation(gold, model)
        self.assertEqual(result["observed"]["mean_positive_excess_regret"], 0.0)
        self.assertEqual(result["per_source"]["s1"]["positive_excess_regret"], 0.0)
        self.assertLess(result["per_source"]["s1"]["excess_regret"], 0.0)
        self.assertTrue(result["checks"]["mean_positive_excess"])

    def test_a_degrading_source_cannot_be_offset_and_fails_the_screen(self) -> None:
        gold, model = s13_rows(
            model_overrides={"s1": {"top1": 0.6, "top2": 0.9, "mean_normalized_regret": 0.2}},
        )
        other_gold, other_model = s13_rows(
            model_overrides={"s2": {"top1": 0.25, "top2": 0.5, "mean_normalized_regret": 1.0}}
        )
        del other_gold
        result = paired_degradation(gold, other_model)
        self.assertGreater(result["observed"]["mean_positive_excess_regret"], 0.05)
        self.assertFalse(result["passes"])

    def test_malformed_source_contributes_zeros_and_is_never_dropped(self) -> None:
        gold, model = s13_rows(model_overrides={"s1": None})
        result = paired_degradation(gold, model)
        row = result["per_source"]["s1"]
        self.assertEqual(row["top1_model"], 0.0)
        self.assertEqual(row["top2_model"], 0.0)
        self.assertEqual(row["regret_model"], 1.0)
        self.assertTrue(row["model_response_malformed_or_missing"])
        self.assertEqual(result["denominator"], 8)


class OwnSelectionEquivarianceTests(unittest.TestCase):
    def test_eighty_repeat_matched_comparisons_pass(self) -> None:
        result = own_selection_equivariance(s14_rows(), expected_total=80)
        self.assertEqual(result["comparisons_total"], 80)
        self.assertTrue(result["passes"])
        self.assertEqual(result["comparisons_passed"], 80)

    def test_cross_repeat_comparison_is_rejected_not_substituted(self) -> None:
        rows = s14_rows()
        rows[0]["base_repeat"] = 2
        rows[0]["repeat"] = 1
        with self.assertRaises(Exception) as context:
            own_selection_equivariance(rows, expected_total=80)
        self.assertIn("repeat-matched", str(context.exception))
        self.assertNotIsInstance(context.exception, AssertionError)

    def test_missing_response_fails_and_the_denominator_stays_eighty(self) -> None:
        rows = s14_rows()
        rows[0]["variant_response_present"] = False
        result = own_selection_equivariance(rows, expected_total=80)
        self.assertEqual(result["comparisons_total"], 80)
        self.assertEqual(result["comparisons_required"], 80)
        self.assertEqual(result["failures"][0]["reason"], "variant_response_missing")
        self.assertFalse(result["passes"])

    def test_selection_mismatch_fails(self) -> None:
        rows = s14_rows()
        rows[0]["variant_selection"] = [2]
        result = own_selection_equivariance(rows, expected_total=80)
        self.assertFalse(result["passes"])
        self.assertEqual(result["failures"][0]["reason"], "selection_mismatch")


class DirectionalContinuityTests(unittest.TestCase):
    def _row(self, axis: str, reference, compared):
        return {
            "axis": axis,
            "reference_present": reference is not None,
            "compared_present": compared is not None,
            "reference_items": list(reference or []),
            "compared_items": list(compared or []),
        }

    def test_perfect_continuity_clears_both_thresholds(self) -> None:
        item = [("role", "support")]
        result = directional_continuity(
            [
                self._row("cross_variant", item, item),
                self._row("cross_repeat", item, item),
            ]
        )
        self.assertTrue(result["passes"])
        self.assertEqual(result["micro_aggregate"]["precision"], 1.0)
        self.assertEqual(result["micro_aggregate"]["recall"], 1.0)

    def test_empty_axis_is_na_and_cannot_clear_a_threshold(self) -> None:
        result = directional_continuity([])
        self.assertEqual(result["per_axis"]["cross_variant"]["precision"], "NA")
        self.assertEqual(result["per_axis"]["cross_repeat"]["recall"], "NA")
        self.assertEqual(result["micro_aggregate"]["precision"], "NA")
        self.assertFalse(result["passes"])
        self.assertFalse(result["checks"]["precision"])
        self.assertFalse(result["checks"]["recall"])

    def test_a_missing_compared_response_contributes_an_empty_set(self) -> None:
        result = directional_continuity(
            [self._row("cross_variant", [("role", "support")], None)]
        )
        axis = result["per_axis"]["cross_variant"]
        self.assertEqual(axis["compared_item_count"], 0)
        self.assertEqual(axis["reference_item_count"], 1)
        self.assertEqual(axis["precision"], "NA")
        self.assertEqual(axis["recall"], 0.0)
        self.assertFalse(result["passes"])


class SubstitutedRowsNeverReachAGateTests(unittest.TestCase):
    def _substitution(self):
        from ser.evaluation.authz_model_semantic_v1_3_1 import diagnostic_substitution

        return diagnostic_substitution(
            identifier="D1",
            case_id="synthetic-case",
            values={1: 1.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0},
            legal_target_slots=LEGAL,
            gold_values={1: 1.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0},
            gold_choice_set=(1,),
            usefulness_by_slot={1: 1.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0},
            evaluator_ordinal_by_slot={1: 1, 2: 2, 3: 3, 4: 4, 5: 5},
            effects_source="gold",
            relations_source="model",
            isolates="the decision cost of the model's effect errors",
        )

    def test_s13_rejects_a_substituted_row(self) -> None:
        gold, model = s13_rows()
        model["s1"] = self._substitution()
        with self.assertRaises(SubstitutionMisuse):
            paired_degradation(gold, model)

    def test_s14_rejects_a_substituted_row(self) -> None:
        with self.assertRaises(SubstitutionMisuse):
            own_selection_equivariance([self._substitution()], expected_total=1)

    def test_s15_rejects_a_substituted_row(self) -> None:
        with self.assertRaises(SubstitutionMisuse):
            directional_continuity([self._substitution()])

    def test_primary_endpoint_rejects_a_substituted_row(self) -> None:
        flags = {source: True for source in SOURCES}
        flags["s1"] = self._substitution()
        with self.assertRaises(SubstitutionMisuse):
            primary_endpoint(flags)

    def test_tagged_mapping_rows_are_also_rejected(self) -> None:
        tagged = {"evaluator_only_diagnostic_substitution": True, "preserved": True}
        with self.assertRaises(SubstitutionMisuse):
            primary_endpoint({**{source: True for source in SOURCES}, "s1": tagged})


def annotation_from_response(response: dict) -> dict:
    return {
        "facts": {
            slot: {"value": bool(value)} for slot, value in response["facts"].items()
        },
        "candidate_effects": {
            slot: {"value": str(value)}
            for slot, value in response["candidate_effects"].items()
        },
        "unresolved_targets": {
            target: {
                relation: {"value": bool(flag)}
                for relation, flag in relations.items()
            }
            for target, relations in response["unresolved_targets"].items()
        },
    }


def synthetic_bundle():
    """A synthetic 8-source development bundle; no real population is read."""

    from ser.evaluation.authz_v1_3_1_harness import DevelopmentBundle

    gold = synthetic_response()
    annotation = annotation_from_response(gold)
    cases = []
    restricted = {}
    annotations = {}
    for source in SOURCES:
        for variant in (CANONICAL_VARIANT,) + tuple(EQUIVALENCE_VARIANTS):
            case_id = f"{source}--{variant}"
            cases.append(
                {
                    "case_id": case_id,
                    "variant": variant,
                    "source_episode_id": source,
                    "runner_control": {
                        "legal_target_slots": list(LEGAL),
                        "current_artifact_slot": 0,
                    },
                    "model_visible_input": {
                        "candidate_hypotheses": CANDIDATE_HYPOTHESES,
                        "public_artifact_inventory": [
                            {
                                "slot": slot,
                                "public_id": f"t{slot}",
                                "path": f"synthetic/path{slot}",
                                "exported_symbols": [f"synthetic_symbol_{slot}"],
                                "line_count": 10 + slot,
                            }
                            for slot in range(6)
                        ],
                    },
                }
            )
            restricted[case_id] = {
                "usefulness_by_variant_target_slot": {
                    "t1": 1.0,
                    "t2": 1.0,
                    "t3": 0.0,
                    "t4": 0.0,
                    "t5": 0.0,
                },
                "canonical_source_ordinal_by_variant_slot": {
                    f"t{slot}": slot for slot in LEGAL
                },
                "transformation_maps": {
                    "canonical_ordinal_by_variant_public_id": {
                        f"t{slot}": slot for slot in range(6)
                    }
                },
                "source_family": "synthetic",
            }
            annotations[case_id] = annotation
    return DevelopmentBundle(
        contract=CONTRACT,
        cases=tuple(cases),
        restricted=restricted,
        annotations=annotations,
        transformation_maps={},
    )


def measured_responses(bundle) -> dict:
    gold = bundle.response_for(str(bundle.cases[0]["case_id"]))
    return {
        (str(case["case_id"]), repeat): gold
        for case in bundle.cases
        for repeat in (1, 2)
    }


class DevelopmentWiringIntegrationTests(unittest.TestCase):
    """Handoff step 6A: the Step-8/9/10 wiring runs on synthetic fixtures only."""

    def test_scoring_error_propagation_and_gate_wiring_run_dormant(self) -> None:
        from tools.score_authzgym_model_semantic import (
            _canonical_scoring,
            _development_items,
            _score_error_propagation,
            _score_s13,
            _score_s14,
            _score_s15,
            _score_s7,
        )
        from ser.evaluation.authz_model_semantic_v1_3_1 import AuditedReader

        bundle = synthetic_bundle()
        component = EstimatorV1SalientCategory()
        responses = measured_responses(bundle)

        canonical = _canonical_scoring(bundle, component, responses)
        self.assertTrue(canonical["primary_endpoint"]["passes"])
        self.assertEqual(
            canonical["primary_endpoint"]["per_repeat"]["1"]["preserved_count"], 8
        )
        self.assertEqual(
            canonical["primary_endpoint"]["per_repeat"]["2"]["denominator"], 8
        )
        self.assertTrue(canonical["absolute_usefulness"]["gate"]["passes"])

        s13 = _score_s13(bundle, component, responses)
        self.assertTrue(s13["passes"])
        s14 = _score_s14(bundle, component, responses)
        self.assertEqual(s14["comparisons_total"], 80)
        self.assertTrue(s14["passes"])
        s15 = _score_s15(bundle, responses)
        self.assertTrue(s15["passes"])
        s7 = _score_s7(bundle, responses)
        self.assertEqual(s7["C_response"], 1.0)
        self.assertEqual(s7["violation_count"], 0)

        error_propagation = _score_error_propagation(bundle, component, responses)
        rows = error_propagation["evaluator_only_diagnostic_substitution"]["rows"]
        self.assertEqual(set(rows), {"D0", "D1", "D2", "D3", "D4"})
        self.assertTrue(rows["D0"]["measured_result"])
        self.assertFalse(rows["D3"]["measured_result"])

        with tempfile.TemporaryDirectory() as tmp:
            reader = AuditedReader(
                actor="test_runner",
                stage="integration",
                tool_path=THIS_TOOL,
                authorization="unit test (synthetic fixtures)",
                ledger_path=Path(tmp) / "ACCESS_LEDGER.jsonl",
            )
            items = _development_items(
                reader, bundle, responses, canonical, s13, s14, s15, s7
            )
            self.assertEqual(set(items), set(range(1, 24)))
            self.assertEqual(items[11]["requirement"].split(";")[0], "diagnostic_only")
            report = eligibility_report(
                items,
                split="development",
                diagnostic_only={11: DiagnosticOnly(s7)},
            )
            self.assertIn(report["verdict"], ("pass", "fail"))
            self.assertNotIn(11, report["gated_items"])
            self.assertEqual(report["effect_self_consistency"]["11"]["C_response"], 1.0)


if __name__ == "__main__":
    unittest.main()
