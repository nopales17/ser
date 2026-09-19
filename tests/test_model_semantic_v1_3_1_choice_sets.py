"""Choice-set, primary-endpoint and ordinal-isolation tests for `model-semantic-v1.3.1-N1`.

Handoff step 6A. Authority: `PREREGISTRATION.md` sections 4.2, 4.3, 4.4 and
12.1; `IMPLEMENTATION_HANDOFF.md` step 6A. Every fixture here is synthetic:
hand-constructed value vectors and hand-constructed case/response objects. No
model response exists, none is read, and no model or provider call is made.
"""

from __future__ import annotations

import unittest

from ser.evaluation.authz_model_semantic_v1_3_1 import (
    ChoiceSetError,
    ScoringMachineryError,
    choice_set,
    choice_set_record,
    classify_error_propagation,
    decision_preserved,
    development_primary,
    primary_endpoint,
)


LEGAL = (1, 2, 3, 4, 5)
GOLD = {1: 1.0, 2: 1.0, 3: 0.0, 4: 0.0, 5: 0.0}


class _PoisonOrdinal:
    """Any access to the evaluator canonical ordinal must fail loudly."""

    def __getattr__(self, name: str) -> object:
        raise AssertionError(f"the choice-set path read the canonical ordinal ({name})")

    def __getitem__(self, key: object) -> object:
        raise AssertionError("the choice-set path read the canonical ordinal")

    def __iter__(self) -> object:
        raise AssertionError("the choice-set path read the canonical ordinal")

    def __contains__(self, item: object) -> object:
        raise AssertionError("the choice-set path read the canonical ordinal")

    def __eq__(self, other: object) -> object:
        raise AssertionError("the choice-set path read the canonical ordinal")

    def __repr__(self) -> str:  # pragma: no cover - representation only
        return "<poison-canonical-ordinal>"


class ChoiceSetTests(unittest.TestCase):
    def test_strict_subset_of_gold_is_preserved(self) -> None:
        model = {1: 1.0, 2: 0.5, 3: 0.0, 4: 0.0, 5: 0.0}
        self.assertEqual(choice_set(model, LEGAL), (1,))
        self.assertTrue(decision_preserved(choice_set(model, LEGAL), (1, 2)))

    def test_equal_sets_pass(self) -> None:
        self.assertTrue(decision_preserved((1, 2), (1, 2)))
        self.assertEqual(choice_set(GOLD, LEGAL), (1, 2))

    def test_one_target_outside_gold_fails(self) -> None:
        model = {1: 1.0, 2: 1.0, 3: 1.0, 4: 0.0, 5: 0.0}
        self.assertEqual(choice_set(model, LEGAL), (1, 2, 3))
        self.assertFalse(decision_preserved(choice_set(model, LEGAL), (1, 2)))

    def test_non_empty_requirement(self) -> None:
        self.assertFalse(decision_preserved((), (1, 2)))

    def test_ties_are_compared_after_rounding_to_twelve_places(self) -> None:
        model = {1: 0.1 + 1e-13, 2: 0.1, 3: 0.0, 4: 0.0, 5: 0.0}
        self.assertEqual(choice_set(model, LEGAL), (1, 2))

    def test_empty_legal_set_is_rejected(self) -> None:
        with self.assertRaises(ChoiceSetError):
            choice_set(GOLD, ())

    def test_missing_target_value_is_rejected(self) -> None:
        with self.assertRaises(ChoiceSetError):
            choice_set({1: 1.0}, LEGAL)


class ErrorClassFromChoiceSetsTests(unittest.TestCase):
    def test_m_equals_l_with_gold_proper_is_structurally_catastrophic(self) -> None:
        model = {slot: 1.0 for slot in LEGAL}
        classification = classify_error_propagation(
            measured_response_present=True,
            model_choice_set=choice_set(model, LEGAL),
            gold_choice_set=(1, 2),
            legal_target_slots=LEGAL,
            model_values=model,
            gold_values=GOLD,
        )
        self.assertEqual(classification["error_class"], "structurally_catastrophic")
        self.assertFalse(classification["preserved"])

    def test_missing_response_is_malformed_and_never_preserved(self) -> None:
        classification = classify_error_propagation(
            measured_response_present=False,
            model_choice_set=None,
            gold_choice_set=(1, 2),
            legal_target_slots=LEGAL,
        )
        self.assertEqual(classification["error_class"], "malformed_or_missing")
        self.assertFalse(classification["preserved"])


class CanonicalOrdinalIsolationTests(unittest.TestCase):
    """Section 4.2: the evaluator canonical ordinal cannot influence a choice set."""

    def test_poison_ordinal_is_never_read(self) -> None:
        baseline = choice_set_record(
            "synthetic-case",
            gold_values=GOLD,
            model_values={1: 1.0, 2: 0.5, 3: 0.0, 4: 0.0, 5: 0.0},
            legal_target_slots=LEGAL,
            evaluator_ordinal_by_case={1: 1, 2: 2, 3: 3, 4: 4, 5: 5},
        )
        poisoned = choice_set_record(
            "synthetic-case",
            gold_values=GOLD,
            model_values={1: 1.0, 2: 0.5, 3: 0.0, 4: 0.0, 5: 0.0},
            legal_target_slots=LEGAL,
            evaluator_ordinal_by_case=_PoisonOrdinal(),
        )
        self.assertEqual(baseline["G_i"], poisoned["G_i"])
        self.assertEqual(baseline["M_i"], poisoned["M_i"])
        self.assertFalse(poisoned["evaluator_ordinal_used"])

    def test_permuting_the_ordinal_leaves_both_sets_byte_identical(self) -> None:
        values = {1: 1.0, 2: 0.5, 3: 0.0, 4: 0.0, 5: 0.0}
        first = choice_set_record(
            "synthetic-case",
            gold_values=GOLD,
            model_values=values,
            legal_target_slots=LEGAL,
            evaluator_ordinal_by_case={1: 1, 2: 2, 3: 3, 4: 4, 5: 5},
        )
        second = choice_set_record(
            "synthetic-case",
            gold_values=GOLD,
            model_values=values,
            legal_target_slots=LEGAL,
            evaluator_ordinal_by_case={1: 5, 2: 4, 3: 3, 4: 2, 5: 1},
        )
        self.assertEqual(first, second)
        self.assertFalse(first["evaluator_ordinal_used"])


class PrimaryEndpointTests(unittest.TestCase):
    def _preserved(self, *failed: str) -> dict[str, bool]:
        rows = {f"s{index}": True for index in range(1, 9)}
        for source in failed:
            rows[source] = False
        return rows

    def test_seven_of_eight_passes(self) -> None:
        result = primary_endpoint(self._preserved("s8"))
        self.assertTrue(result["passes"])
        self.assertEqual(result["preserved_count"], 7)
        self.assertEqual(result["denominator"], 8)

    def test_six_of_eight_fails(self) -> None:
        result = primary_endpoint(self._preserved("s7", "s8"))
        self.assertFalse(result["passes"])
        self.assertEqual(result["preserved_count"], 6)

    def test_denominator_is_frozen_at_eight(self) -> None:
        with self.assertRaises(ScoringMachineryError):
            primary_endpoint({f"s{index}": True for index in range(1, 8)})

    def test_repeats_are_never_averaged(self) -> None:
        result = development_primary(
            {
                1: self._preserved(),
                2: self._preserved("s7", "s8"),
            }
        )
        self.assertTrue(result["per_repeat"]["1"]["passes"])
        self.assertFalse(result["per_repeat"]["2"]["passes"])
        self.assertFalse(result["passes"])
        self.assertEqual(result["repeat_agreement"]["paired_disagreements"], ["s7", "s8"])
        self.assertEqual(result["repeat_agreement"]["agreement_count"], 6)
        self.assertFalse(result["repeat_agreement"]["is_averaged_into_primary"])

    def test_both_repeats_must_independently_reach_threshold(self) -> None:
        rows = self._preserved()
        for source in ("s7", "s8"):
            rows[source] = False
        result = development_primary({1: rows, 2: self._preserved()})
        self.assertFalse(result["passes"])
        self.assertTrue(result["both_repeats_reach_threshold"] is False)


if __name__ == "__main__":
    unittest.main()
