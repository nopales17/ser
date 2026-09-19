"""Error-propagation and evaluator-only-substitution tests for `model-semantic-v1.3.1-N1`.

Handoff step 6A / preregistration section 10. Authority: `PREREGISTRATION.md`
sections 8.6, 10.1, 10.2 and 10.3; `IMPLEMENTATION_HANDOFF.md` steps 6A and 9.
Every fixture is synthetic: hand-constructed response objects authored from the
published v1.3 grammar. No model response exists and no model or provider call
is made.
"""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from ser.authzgym.v1_3_contract import load_public_contract
from ser.evaluation.authz_v1_3_1_sealed_input import build_sealed_input
from ser.evaluation.authz_model_semantic_v1_3_1 import (
    ERROR_CLASSES,
    EvaluatorOnlySubstitution,
    SubstitutionMisuse,
    classify_error_propagation,
    diagnostic_substitution,
)


ROOT = Path(__file__).resolve().parents[1]
V13_DIR = ROOT / "experiments" / "authzgym_semantic_contract_v1_3"
CONTRACT = load_public_contract(V13_DIR / "PUBLIC_CONTRACT.json")
LEGAL = (1, 2, 3, 4, 5)

CANDIDATE_HYPOTHESES = [
    {
        "slot": "c0",
        "effect_family": "ownership",
        "description": CONTRACT["candidate_descriptions"]["ownership"],
    },
    {
        "slot": "c1",
        "effect_family": "membership",
        "description": CONTRACT["candidate_descriptions"]["membership"],
    },
    {
        "slot": "c2",
        "effect_family": "role",
        "description": CONTRACT["candidate_descriptions"]["role"],
    },
    {
        "slot": "c3",
        "effect_family": "context",
        "description": CONTRACT["candidate_descriptions"]["context"],
    },
]


def synthetic_case(case_id: str = "synthetic-case") -> dict:
    return {
        "case_id": case_id,
        "variant": "base_entry",
        "source_episode_id": "synthetic-source",
        "runner_control": {"legal_target_slots": list(LEGAL), "current_artifact_slot": 0},
        "model_visible_input": {"candidate_hypotheses": CANDIDATE_HYPOTHESES},
    }


def synthetic_facts(*, ownership_support: bool = True) -> dict[str, bool]:
    facts = {f"f{index}": False for index in range(17)}
    facts[CONTRACT["effect_support_cues"]["ownership"][0]] = ownership_support
    return facts


def truth_table_effects(facts: dict[str, bool]) -> dict[str, str]:
    from ser.evaluation.authz_model_semantic_v1_3_1 import expected_effects_from_facts

    return expected_effects_from_facts(CONTRACT, CANDIDATE_HYPOTHESES, facts)


def synthetic_response(
    *,
    effects_override: dict[str, str] | None = None,
    facts: dict[str, bool] | None = None,
) -> dict:
    facts = dict(facts if facts is not None else synthetic_facts())
    effects = truth_table_effects(facts)
    effects.update(effects_override or {})
    return {
        "facts": facts,
        "candidate_effects": effects,
        "unresolved_targets": {
            f"t{slot}": {f"r{index}": False for index in range(5)} for slot in LEGAL
        },
    }


def response_bytes_hash(response: dict) -> str:
    payload = json.dumps(response, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


class ErrorClassTests(unittest.TestCase):
    """Section 10.2: mutually exclusive, exhaustive and precedence-ordered."""

    def _classify(self, **kwargs) -> str:
        return str(classify_error_propagation(**kwargs)["error_class"])

    def test_five_classes_are_mutually_exclusive_and_exhaustive(self) -> None:
        grid = {
            "malformed_or_missing": dict(
                measured_response_present=False,
                model_choice_set=None,
                gold_choice_set=(1, 2),
                legal_target_slots=LEGAL,
            ),
            "structurally_catastrophic": dict(
                measured_response_present=True,
                model_choice_set=LEGAL,
                gold_choice_set=(1, 2),
                legal_target_slots=LEGAL,
                model_values={slot: 1.0 for slot in LEGAL},
                gold_values={1: 1.0, 2: 1.0, 3: 0.0, 4: 0.0, 5: 0.0},
            ),
            "decision_changing": dict(
                measured_response_present=True,
                model_choice_set=(3,),
                gold_choice_set=(1, 2),
                legal_target_slots=LEGAL,
                model_values={1: 0.0, 2: 0.0, 3: 1.0, 4: 0.0, 5: 0.0},
                gold_values={1: 1.0, 2: 1.0, 3: 0.0, 4: 0.0, 5: 0.0},
            ),
            "value_harmless": dict(
                measured_response_present=True,
                model_choice_set=(1,),
                gold_choice_set=(1,),
                legal_target_slots=LEGAL,
                model_values={1: 1.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0},
                gold_values={1: 1.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0},
            ),
            "decision_harmless": dict(
                measured_response_present=True,
                model_choice_set=(1,),
                gold_choice_set=(1, 2),
                legal_target_slots=LEGAL,
                model_values={1: 1.0, 2: 0.5, 3: 0.0, 4: 0.0, 5: 0.0},
                gold_values={1: 1.0, 2: 1.0, 3: 0.0, 4: 0.0, 5: 0.0},
            ),
        }
        observed = {name: self._classify(**kwargs) for name, kwargs in grid.items()}
        self.assertEqual(set(observed.values()), set(ERROR_CLASSES))
        self.assertEqual(len(observed), len(ERROR_CLASSES))

    def test_every_case_carries_exactly_one_class(self) -> None:
        result = classify_error_propagation(
            measured_response_present=True,
            model_choice_set=(1,),
            gold_choice_set=(1, 2),
            legal_target_slots=LEGAL,
            model_values={1: 1.0, 2: 0.5, 3: 0.0, 4: 0.0, 5: 0.0},
            gold_values={1: 1.0, 2: 1.0, 3: 0.0, 4: 0.0, 5: 0.0},
        )
        self.assertIn(result["error_class"], ERROR_CLASSES)
        self.assertEqual(
            sum(1 for name in ERROR_CLASSES if name == result["error_class"]), 1
        )

    def test_precedence_class_2_beats_class_4(self) -> None:
        # Value vectors are identical, yet M_i == L_i with G_i proper: class 2 wins.
        observed = self._classify(
            measured_response_present=True,
            model_choice_set=LEGAL,
            gold_choice_set=(1, 2),
            legal_target_slots=LEGAL,
            model_values={slot: 0.0 for slot in LEGAL},
            gold_values={slot: 0.0 for slot in LEGAL},
        )
        self.assertEqual(observed, "structurally_catastrophic")

    def test_precedence_class_3_beats_class_4(self) -> None:
        # Identical vectors would be value_harmless, but the ordinal tie-break
        # cannot make M_i a subset of G_i here; class 3 is the first match.
        observed = self._classify(
            measured_response_present=True,
            model_choice_set=(3,),
            gold_choice_set=(1, 2),
            legal_target_slots=LEGAL,
            model_values={slot: 0.0 for slot in LEGAL},
            gold_values={slot: 0.0 for slot in LEGAL},
        )
        self.assertEqual(observed, "decision_changing")

    def test_missing_response_preserves_denominator_semantics(self) -> None:
        result = classify_error_propagation(
            measured_response_present=False,
            model_choice_set=None,
            gold_choice_set=(1, 2),
            legal_target_slots=LEGAL,
        )
        self.assertFalse(result["preserved"])
        self.assertEqual(result["precedence_ordinal"], 1)


class SubstitutionTests(unittest.TestCase):
    """Section 10.3: evaluator-only, no write-back, never a gate input."""

    def _rows(self, *, d0_values: dict[int, float], d3_values: dict[int, float]):
        gold_values = {1: 1.0, 2: 1.0, 3: 0.0, 4: 0.0, 5: 0.0}
        usefulness = dict(gold_values)
        ordinal = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5}
        shared = dict(
            case_id="synthetic-case",
            legal_target_slots=LEGAL,
            gold_values=gold_values,
            gold_choice_set=(1, 2),
            usefulness_by_slot=usefulness,
            evaluator_ordinal_by_slot=ordinal,
        )
        d0 = diagnostic_substitution(
            identifier="D0",
            values=d0_values,
            effects_source="model",
            relations_source="model",
            isolates="the measured result (not a substitution)",
            measured=True,
            **shared,
        )
        d1 = diagnostic_substitution(
            identifier="D1",
            values=d0_values,
            effects_source="gold",
            relations_source="model",
            isolates="the decision cost of the model's effect errors",
            **shared,
        )
        d2 = diagnostic_substitution(
            identifier="D2",
            values=d0_values,
            effects_source="model",
            relations_source="gold",
            isolates="the decision cost of the model's relation errors",
            **shared,
        )
        d3 = diagnostic_substitution(
            identifier="D3",
            values=d3_values,
            effects_source="effect_from_facts(model facts)",
            relations_source="model",
            isolates="S-7 localization: effect errors downstream of facts or not",
            **shared,
        )
        d4 = diagnostic_substitution(
            identifier="D4",
            values=gold_values,
            effects_source="gold",
            relations_source="gold",
            isolates="the gold reference",
            **shared,
        )
        return d0, d1, d2, d3, d4

    def test_d0_is_measured_and_d1_to_d4_are_substitutions(self) -> None:
        d0, d1, d2, d3, d4 = self._rows(
            d0_values={1: 0.0, 2: 0.0, 3: 1.0, 4: 0.0, 5: 0.0},
            d3_values={1: 1.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0},
        )
        self.assertIsInstance(d0, dict)
        self.assertTrue(d0["measured_result"])
        for row in (d1, d2, d3, d4):
            self.assertIsInstance(row, EvaluatorOnlySubstitution)
            self.assertTrue(row.as_record()["row_type"] == "evaluator_only_diagnostic_substitution")
            with self.assertRaises(SubstitutionMisuse):
                row.verdict

    def test_measuring_a_substitution_does_not_mutate_the_measured_response(self) -> None:
        response = synthetic_response(effects_override={"c0": "contradict"})
        before = response_bytes_hash(response)
        snapshot = json.dumps(response, sort_keys=True)
        self._rows(
            d0_values={1: 0.0, 2: 0.0, 3: 1.0, 4: 0.0, 5: 0.0},
            d3_values={1: 1.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0},
        )
        self.assertEqual(response_bytes_hash(response), before)
        self.assertEqual(json.dumps(response, sort_keys=True), snapshot)

    def test_d0_d3_gap_localizes_the_effect_self_consistency_violation(self) -> None:
        d0, _, _, d3, _ = self._rows(
            d0_values={1: 0.0, 2: 0.0, 3: 1.0, 4: 0.0, 5: 0.0},
            d3_values={1: 1.0, 2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0},
        )
        self.assertEqual(d0["choice_set"], [3])
        self.assertFalse(d0["preserved_equivalent"])
        self.assertEqual(d3.as_record()["choice_set"], [1])
        self.assertTrue(d3.as_record()["preserved_equivalent"])


class MeasuredEffectVectorTests(unittest.TestCase):
    """Section 4.1/8.6 consequence 8: B-1 receives the submitted effect vector."""

    def test_sealed_input_carries_the_submitted_effects_even_when_inconsistent(self) -> None:
        response = synthetic_response(effects_override={"c0": "contradict"})
        expected = truth_table_effects(response["facts"])
        self.assertNotEqual(expected["c0"], response["candidate_effects"]["c0"])
        sealed = build_sealed_input(synthetic_case(), response, CONTRACT)
        self.assertEqual(dict(sealed.candidate_effects), response["candidate_effects"])
        self.assertEqual(dict(sealed.facts), response["facts"])
        self.assertEqual(
            json.dumps(dict(sealed.candidate_effects), sort_keys=True),
            json.dumps(response["candidate_effects"], sort_keys=True),
        )


if __name__ == "__main__":
    unittest.main()
