#!/usr/bin/env python3
"""Gold-adequacy and scoring for condition `model-semantic-v1.3.1-N1`.

Handoff step 5 is implemented here: ``--stage gold-adequacy --split
development`` runs the unchanged frozen `est-repair-v1.3.1-B-1` component on
certified gold semantics over the eight canonical development sources, computes
the section-4.2 choice sets ``G_i``, and refuses to continue if any canonical
``G_i`` equals the whole legal target set ``L_i``.

The preregistration section-8/10/12 scoring, gate and error-propagation stages
(handoff steps 8--10) are **implemented dormant at handoff step 6A** and are
executed only under a separate Step-7 authorization:

* ``--stage score``             -- choice sets, the per-repeat primary endpoint,
                                   absolute usefulness, S-13/S-14/S-15 and S-7;
* ``--stage error-propagation`` -- section-10 localization, the five classes
                                   and the evaluator-only D0--D4 substitutions;
* ``--stage gates``             -- the section-12/13.8 checklist, validity
                                   precedence and the section-15 outcome label;
* ``--stage development-report``-- the section-11 report structure.

Every stage refuses to run unless a genuinely measured response produced under a
Step-7 authorization exists at ``development/responses.jsonl``. Producing a
scored number from a real model response before that authorization is a
blocking violation; the refusal is the dormant guarantee.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ser.authzgym.policies_v1_3_1 import EstimatorV1SalientCategory  # noqa: E402
from ser.authzgym.v1_3_contract import parse_response  # noqa: E402
from ser.core.types import canonical_json, content_hash  # noqa: E402
from ser.evaluation.authz_model_semantic_v1_3_1 import (  # noqa: E402
    CONDITION_DIR,
    DiagnosticOnly,
    EvaluatorOnlySubstitution,
    V13_DIR,
    AuditedReader,
    absolute_usefulness_gate,
    assert_gate_input,
    choice_set,
    choice_set_record,
    classify_error_propagation,
    decision_preserved,
    development_primary,
    diagnostic_substitution,
    directional_continuity,
    directional_item_set,
    effect_self_consistency,
    eligibility_report,
    error_class_census,
    expected_effects_from_facts,
    localization_tables,
    own_selection_equivariance,
    paired_degradation,
    relative_path,
    substitution_table,
    validate_access_ledger,
)
from ser.evaluation.authz_v1_3_1_harness import (  # noqa: E402
    CANONICAL_VARIANT,
    EQUIVALENCE_VARIANTS,
    DegenerateNullComponent,
    _ordinal_by_slot,
    _usefulness_by_slot,
    build_component_input,
    bound_order,
    bound_values,
    criterion,
    diagnostic_for_case,
    load_development_bundle,
    own_ranking_invariance,
    readout,
    section_14_equivalence,
)
from ser.evaluation.authz_v1_3 import (  # noqa: E402
    aggregate_action_diagnostics,
    score_cases,
)


CONDITION_ID = "model-semantic-v1.3.1-N1"
AUTHORIZING_ADR = "ADR-0023"
TOOL_PATH = Path(__file__).resolve()
GOLD_ADEQUACY_PATH = CONDITION_DIR / "GOLD_ADEQUACY_DEVELOPMENT.json"
SCORING_AUTHORIZATION = (
    "ADR-0023 section 14.1; PREREGISTRATION.md sections 4.2, 4.3 and 8.2 gate "
    "S-3; IMPLEMENTATION_HANDOFF.md step 5"
)
EXPECTED = {
    "canonical_top1": 0.75,
    "canonical_top2": 1.0,
    "canonical_regret": 0.116667,
}
DEVELOPMENT_DIR = CONDITION_DIR / "development"
RESPONSES_PATH = DEVELOPMENT_DIR / "responses.jsonl"
ATTEMPTS_PATH = DEVELOPMENT_DIR / "attempts.jsonl"
SPEND_LEDGER_PATH = DEVELOPMENT_DIR / "spend_ledger.jsonl"
ELIGIBILITY_PATH = CONDITION_DIR / "ELIGIBILITY.json"
ERROR_PROPAGATION_PATH = CONDITION_DIR / "ERROR_PROPAGATION.json"
DEVELOPMENT_SCORE_PATH = CONDITION_DIR / "DEVELOPMENT_SCORE.json"
DEVELOPMENT_REPORT_PATH = CONDITION_DIR / "DEVELOPMENT_REPORT.json"
DEVELOPMENT_REPORT_MARKDOWN_PATH = CONDITION_DIR / "DEVELOPMENT_REPORT.md"
MANIFEST_PATH = CONDITION_DIR / "FROZEN_INPUTS_MODEL_V1_3_1.json"
ACCESS_LEDGER_PATH = CONDITION_DIR / "ACCESS_LEDGER.jsonl"
COST_GATE_PATH = CONDITION_DIR / "COST_GATE.json"

SCORING_STAGES = ("score", "error-propagation", "gates", "development-report")

STAGE_AUTHORIZATIONS = {
    "score": (
        "ADR-0023 section 14.1; PREREGISTRATION.md sections 4.2--4.4, 8.2--8.6; "
        "IMPLEMENTATION_HANDOFF.md step 8 (implemented dormant at step 6A)"
    ),
    "error-propagation": (
        "ADR-0023 section 14.1; PREREGISTRATION.md section 10; "
        "IMPLEMENTATION_HANDOFF.md step 9 (implemented dormant at step 6A)"
    ),
    "gates": (
        "ADR-0023 section 14.1; PREREGISTRATION.md sections 12, 12.1, 13.8 and 15; "
        "IMPLEMENTATION_HANDOFF.md step 10 (implemented dormant at step 6A)"
    ),
    "development-report": (
        "ADR-0023 section 14.1; PREREGISTRATION.md section 11 as implemented; "
        "IMPLEMENTATION_HANDOFF.md step 11"
    ),
}

HARD_SPEND_CEILING_USD = 2.50
SEMANTIC_FLOORS = {
    "fact_precision": 0.65,
    "fact_recall": 0.50,
    "directional_effect_precision": 0.60,
    "directional_effect_recall": 0.50,
    "relation_precision": 0.60,
    "relation_recall": 0.50,
}
FIRST_ATTEMPT_SCHEMA_FLOOR = 0.99
POST_RETRY_VALIDITY_FLOOR = 1.00
EXPECTED_LOGICAL_CALLS = 112


class GoldAdequacyError(RuntimeError):
    """A section-4.2/section-8.2 S-3 condition failed. Stop; do not tune."""


class DormantScoringRefusal(RuntimeError):
    """A scoring stage was invoked without an authorized measured response."""


def _json_write(path: Path, value: dict) -> str:
    payload = json.dumps(value, indent=2, sort_keys=True) + "\n"
    path.write_text(payload, encoding="utf-8")
    return __import__("hashlib").sha256(payload.encode("utf-8")).hexdigest()


def _register_reads(reader: AuditedReader) -> dict:
    """Log every development artifact this condition depends on.

    The frozen harness (``ser.evaluation.authz_v1_3_1_harness``) performs its own
    protected reads internally; those reads happen inside a protected,
    pre-existing module that section 6.1's static check does not cover. The
    condition's own accesses are logged here first, one record per open.
    """

    names = (
        "PUBLIC_CONTRACT.json",
        "DEVELOPMENT_PUBLIC_POPULATION.json",
        "DEVELOPMENT_RESTRICTED_POPULATION.json",
        "DEVELOPMENT_TRANSFORMATION_MAPS.json",
        "DEVELOPMENT_SCHEDULE.json",
        "DEVELOPMENT_SOURCE_MANIFEST.json",
        "ANSWERABILITY_VALIDATION.json",
        "FIREWALL_VALIDATION.json",
        "prompts/semantic_observation_v1_3.txt",
        "schemas/semantic_vocabulary_v1_3.json",
        "annotations/development_annotations.jsonl",
    )
    hashes = {}
    for name in names:
        record = reader.hash_file(
            V13_DIR / name, detail="step-5 gold-adequacy dependency"
        )
        hashes[name] = record["file_sha256"]
    hashes["component_module"] = reader.hash_file(
        ROOT / "src/ser/authzgym/policies_v1_3_1.py",
        detail="step-5 frozen B-1 component module",
    )["file_sha256"]
    hashes["sealed_input_module"] = reader.hash_file(
        ROOT / "src/ser/evaluation/authz_v1_3_1_sealed_input.py",
        detail="step-5 frozen sealed-input builder",
    )["file_sha256"]
    return hashes


def _round(values: dict[int, float], digits: int = 12) -> dict[int, float]:
    return {slot: round(float(value), digits) for slot, value in values.items()}


def gold_adequacy_development() -> dict:
    reader = AuditedReader(
        actor="implementation_agent",
        stage="gold-adequacy",
        tool_path=TOOL_PATH,
        authorization=SCORING_AUTHORIZATION,
    )
    source_hashes = _register_reads(reader)
    bundle = load_development_bundle()
    component = EstimatorV1SalientCategory()

    canonical = criterion(bundle, component)
    equivalence = section_14_equivalence(bundle, component)
    invariance = own_ranking_invariance(bundle, component)

    per_source = []
    g_equals_l = []
    for case in bundle.canonical_cases():
        case_id = str(case["case_id"])
        sealed = build_component_input(
            case, bundle.response_for(case_id), bundle.contract
        )
        values = _round(bound_values(component, sealed, case))
        legal = tuple(int(item) for item in sealed.legal_target_slots)
        maximum = max(values[slot] for slot in legal)
        g_i = tuple(sorted(slot for slot in legal if values[slot] == maximum))
        l_i = tuple(sorted(legal))
        occupies_everything = tuple(g_i) == l_i
        if occupies_everything:
            g_equals_l.append(case_id)
        per_source.append(
            {
                "case_id": case_id,
                "source_episode_id": str(case["source_episode_id"]),
                "variant": str(case["variant"]),
                "legal_target_count": len(l_i),
                "G_i": list(g_i),
                "L_i": list(l_i),
                "G_i_size": len(g_i),
                "G_i_equals_L_i": occupies_everything,
                "value_vector": {str(slot): values[slot] for slot in legal},
                "source_verdict": (
                    "blocker_degenerate_gold_choice_set"
                    if occupies_everything
                    else "pass"
                ),
            }
        )

    gates = {
        "canonical_top1": canonical["top1"] >= 0.60,
        "canonical_top2": canonical["top2"] >= 0.80,
        "canonical_regret": canonical["mean_normalized_regret"] <= 0.35,
        "illegal_target_count_zero": canonical["illegal_target_count"] == 0,
        "section_14_equivalence_40_40": (
            equivalence["pair_count"] == 40 and not equivalence["failures"]
        ),
        "own_selection_40_40": (
            invariance["selection_total"] == 40 and invariance["selection_pass"] == 40
        ),
        "ND_1_G_i_differs_from_L_i_for_all_8": not g_equals_l,
    }
    reproduction = {
        "canonical_top1": canonical["top1"],
        "canonical_top2": canonical["top2"],
        "canonical_regret": canonical["mean_normalized_regret"],
        "matches_recorded_development_report": (
            abs(canonical["top1"] - EXPECTED["canonical_top1"]) <= 1e-9
            and abs(canonical["top2"] - EXPECTED["canonical_top2"]) <= 1e-9
            and abs(
                canonical["mean_normalized_regret"] - EXPECTED["canonical_regret"]
            )
            <= 1e-6
        ),
        "recorded_expected": EXPECTED,
        "authority": (
            "experiments/authzgym_estimator_repair_v1_3_1/DEVELOPMENT_REPORT.md "
            "(frozen development figures for est-repair-v1.3.1-B-1)"
        ),
    }
    blockers = [name for name, ok in gates.items() if not ok]
    document = {
        "schema_version": 1,
        "condition_id": CONDITION_ID,
        "authorizing_adr": AUTHORIZING_ADR,
        "stage": "gold-adequacy",
        "split": "development",
        "population_split": "development",
        "population_file_sha256": source_hashes[
            "DEVELOPMENT_PUBLIC_POPULATION.json"
        ],
        "component": {
            "candidate_id": "est-repair-v1.3.1-B-1",
            "module": "ser.authzgym.policies_v1_3_1",
            "class_name": "EstimatorV1SalientCategory",
            "module_file_sha256": source_hashes["component_module"],
            "component_class_source_sha256": __import__("hashlib")
            .sha256(__import__("inspect").getsource(EstimatorV1SalientCategory).encode("utf-8"))
            .hexdigest(),
            "component_class_source_sha256_convention": (
                "SHA-256 of the class source text, the repository's recorded "
                "convention (B-1 = 88b77c5f...ca7a048)"
            ),
        },
        "dependency_file_sha256": source_hashes,
        "canonical_variant": CANONICAL_VARIANT,
        "canonical_case_count": len(per_source),
        "canonical_gold_aggregate": canonical,
        "section_14_equivalence": equivalence,
        "own_selection_equivariance": invariance,
        "per_source_choice_sets": per_source,
        "degenerate_gold_choice_set_sources": g_equals_l,
        "gates": gates,
        "recorded_figure_reproduction": reproduction,
        "errors": [],
        "blockers": blockers,
        "passes": not blockers,
        "paid_inference": False,
        "model_calls": 0,
        "authorization": SCORING_AUTHORIZATION,
    }
    document["gold_adequacy_canonical_json_sha256"] = content_hash(
        {key: value for key, value in document.items() if key != "gold_adequacy_canonical_json_sha256"}
    )
    file_sha256 = _json_write(GOLD_ADEQUACY_PATH, document)
    if blockers:
        raise GoldAdequacyError(
            "gold adequacy blocker: " + ", ".join(blockers)
        )
    document["_written_file_sha256"] = file_sha256
    return document


# ---------------------------------------------------------------------------
# Steps 8--10 -- dormant scoring, error-propagation and gate wiring.
#
# Implemented at handoff step 6A against the pure machinery of
# `ser.evaluation.authz_model_semantic_v1_3_1`. Every stage below refuses to run
# until a genuinely measured response produced under a separate Step-7
# authorization exists. No model or provider call is made by any stage.
# ---------------------------------------------------------------------------


def _stage_reader(stage: str) -> AuditedReader:
    return AuditedReader(
        actor="implementation_agent",
        stage=stage,
        tool_path=TOOL_PATH,
        authorization=STAGE_AUTHORIZATIONS.get(stage, SCORING_AUTHORIZATION),
    )


def _load_measured_responses(
    reader: AuditedReader,
) -> dict[tuple[str, int], dict | None]:
    """The measured response per logical call, or a fail-closed refusal."""

    if not RESPONSES_PATH.is_file():
        raise DormantScoringRefusal(
            "no measured model response exists: "
            f"{relative_path(RESPONSES_PATH)} is absent. Handoff step 7 "
            "(development inference) requires its own authorization; the step-6A "
            "scoring machinery is dormant and refuses to produce a scored result."
        )
    rows = reader.read_jsonl(RESPONSES_PATH, detail="frozen measured responses")
    measured: dict[tuple[str, int], dict | None] = {}
    for row in rows:
        measured[(str(row["case_id"]), int(row["repeat"]))] = row.get(
            "measured_response"
        )
    return measured


def _load_attempts(reader: AuditedReader) -> list[dict]:
    if not ATTEMPTS_PATH.is_file():
        return []
    return reader.read_jsonl(ATTEMPTS_PATH, detail="frozen attempt records")


def _family_by_slot(case: Mapping[str, object]) -> dict[str, str]:
    return {
        str(item["slot"]): str(item["effect_family"])
        for item in case["model_visible_input"]["candidate_hypotheses"]
    }


def _gold_values(bundle, case, component) -> dict[int, float]:
    sealed = build_component_input(
        case, bundle.response_for(str(case["case_id"])), bundle.contract
    )
    return _round(bound_values(component, sealed, case))


def _model_values(bundle, case, response, component) -> dict[int, float] | None:
    if response is None:
        return None
    sealed = build_component_input(case, response, bundle.contract)
    return _round(bound_values(component, sealed, case))


def _mapped_own_selection(bundle, case, response, component) -> list[int]:
    sealed = build_component_input(case, response, bundle.contract)
    groups = bound_order(component, sealed, case)
    ordinal = _ordinal_by_slot(bundle, str(case["case_id"]))
    return sorted(int(ordinal[slot]) for slot in groups[0])


def _fact_set(response: Mapping[str, object]) -> set[str]:
    return {str(slot) for slot, value in response["facts"].items() if value}


def _relation_item_set(bundle, case, response) -> set[tuple[int, str]]:
    ordinal = _ordinal_by_slot(bundle, str(case["case_id"]))
    return {
        (int(ordinal[int(str(target)[1:])]), str(relation_slot))
        for target, relations in response["unresolved_targets"].items()
        for relation_slot, present in relations.items()
        if present
    }


def _response_semantics_equal(
    bundle, base_case, base_response, case, response
) -> bool:
    if _fact_set(base_response) != _fact_set(response):
        return False
    if directional_item_set(
        base_response["candidate_effects"], _family_by_slot(base_case)
    ) != directional_item_set(response["candidate_effects"], _family_by_slot(case)):
        return False
    return _relation_item_set(bundle, base_case, base_response) == _relation_item_set(
        bundle, case, response
    )


def _hybrid_response(*, facts, effects, relations) -> dict:
    return {
        "facts": dict(facts["facts"]),
        "candidate_effects": dict(effects["candidate_effects"]),
        "unresolved_targets": {
            target: dict(vector)
            for target, vector in relations["unresolved_targets"].items()
        },
    }


def _canonical_scoring(bundle, component, responses) -> dict:
    """Section 4.2/4.3/4.4 plus S-11, S-12 and the non-gating read-outs."""

    per_repeat: dict[int, dict[str, dict]] = {1: {}, 2: {}}
    per_source = []
    per_repeat_absolute: dict[int, list[dict]] = {1: [], 2: []}
    averaged_rows: list[dict] = []
    missing_average_cases: list[str] = []
    nd_failures: dict[int, dict[str, list[str]]] = {
        1: {"nd1": [], "nd2": []},
        2: {"nd1": [], "nd2": []},
    }
    nd_strict_unique: dict[int, int] = {1: 0, 2: 0}
    for case in bundle.canonical_cases():
        case_id = str(case["case_id"])
        legal = tuple(int(slot) for slot in case["runner_control"]["legal_target_slots"])
        gold_values = _gold_values(bundle, case, component)
        gold_choice = choice_set(gold_values, legal)
        diagnostic_by_repeat: dict[int, dict | None] = {}
        for repeat in (1, 2):
            response = responses.get((case_id, repeat))
            model_values = _model_values(bundle, case, response, component)
            if model_values is None:
                diagnostic_by_repeat[repeat] = None
                row = {
                    "schema_version": 1,
                    "case_id": case_id,
                    "repeat": repeat,
                    "legal_target_slots": list(legal),
                    "L_i": list(legal),
                    "G_i": list(gold_choice),
                    "M_i": None,
                    "model_response_present": False,
                    "preserved": False,
                    "evaluator_ordinal_used": False,
                }
                classification = classify_error_propagation(
                    measured_response_present=False,
                    model_choice_set=None,
                    gold_choice_set=gold_choice,
                    legal_target_slots=legal,
                )
                nd_failures[repeat]["nd1"].append(f"{case_id}:malformed_or_missing")
                nd_failures[repeat]["nd2"].append(f"{case_id}:malformed_or_missing")
            else:
                row = choice_set_record(
                    case_id,
                    gold_values=gold_values,
                    model_values=model_values,
                    legal_target_slots=legal,
                )
                row["repeat"] = repeat
                row["model_response_present"] = True
                classification = classify_error_propagation(
                    measured_response_present=True,
                    model_choice_set=row["M_i"],
                    gold_choice_set=gold_choice,
                    legal_target_slots=legal,
                    model_values=model_values,
                    gold_values=gold_values,
                )
                diagnostic = diagnostic_for_case(
                    bundle, case, model_values, component=component
                )
                diagnostic_by_repeat[repeat] = diagnostic
                per_repeat_absolute[repeat].append(diagnostic)
                distinct = {round(model_values[slot], 12) for slot in legal}
                if len(distinct) <= 1:
                    nd_failures[repeat]["nd1"].append(case_id)
                maximum = max(model_values[slot] for slot in legal)
                argmax = {
                    slot for slot in legal if abs(model_values[slot] - maximum) <= 1e-12
                }
                if len(argmax) == 1:
                    nd_strict_unique[repeat] += 1
                sealed = build_component_input(case, response, bundle.contract)
                classes = {sealed.category_vector(slot): set() for slot in legal}
                for slot in legal:
                    classes[sealed.category_vector(slot)].add(slot)
                containing = {
                    frozenset(group) for group in classes.values() if argmax & group
                }
                if len(containing) != 1:
                    nd_failures[repeat]["nd2"].append(case_id)
            row["error_class"] = classification["error_class"]
            row["error_class_precedence"] = classification["precedence_ordinal"]
            per_repeat[repeat][case_id] = row
        if all(diagnostic_by_repeat[repeat] is not None for repeat in (1, 2)):
            averaged_rows.append(
                {
                    "top1": sum(
                        float(diagnostic_by_repeat[repeat]["top1"])
                        for repeat in (1, 2)
                    )
                    / 2,
                    "top2": sum(
                        float(diagnostic_by_repeat[repeat]["top2"])
                        for repeat in (1, 2)
                    )
                    / 2,
                    "mean_normalized_regret": sum(
                        float(diagnostic_by_repeat[repeat]["mean_normalized_regret"])
                        for repeat in (1, 2)
                    )
                    / 2,
                    "nondiscriminating": all(
                        diagnostic_by_repeat[repeat]["nondiscriminating"]
                        for repeat in (1, 2)
                    ),
                    "illegal_targets": [],
                }
            )
        else:
            missing_average_cases.append(case_id)
        per_source.append(
            {
                "case_id": case_id,
                "source_episode_id": str(case["source_episode_id"]),
                "G_i": list(gold_choice),
                "G_i_size": len(gold_choice),
                "L_i": list(legal),
                "M_i_repeat_1": per_repeat[1][case_id]["M_i"],
                "M_i_repeat_2": per_repeat[2][case_id]["M_i"],
                "error_class_repeat_1": per_repeat[1][case_id]["error_class"],
                "error_class_repeat_2": per_repeat[2][case_id]["error_class"],
                "preserved_repeat_1": per_repeat[1][case_id]["preserved"],
                "preserved_repeat_2": per_repeat[2][case_id]["preserved"],
                "gold_choice_set_is_legal_set": set(gold_choice) == set(legal),
            }
        )
    primary = development_primary(
        {
            repeat: {
                case_id: row["preserved"] for case_id, row in per_repeat[repeat].items()
            }
            for repeat in (1, 2)
        }
    )
    absolute = {
        "per_repeat": {
            str(repeat): aggregate_action_diagnostics(rows)
            for repeat, rows in per_repeat_absolute.items()
        },
        "two_repeat_average": aggregate_action_diagnostics(averaged_rows) if averaged_rows else None,
        "missing_two_repeat_cases": missing_average_cases,
        "illegal_target_count": sum(
            int(block["illegal_target_count"])
            for block in (
                aggregate_action_diagnostics(rows)
                for rows in per_repeat_absolute.values()
            )
        ),
    }
    auto = absolute["two_repeat_average"]
    absolute["gate"] = (
        absolute_usefulness_gate(
            auto["top1"], auto["top2"], auto["mean_normalized_regret"]
        )
        if auto is not None
        else {"passes": False, "reason": "no two-repeat complete canonical case"}
    )
    non_degeneracy = {
        "per_repeat": {
            str(repeat): {
                "nd1_pass": not nd_failures[repeat]["nd1"],
                "nd1_failures": nd_failures[repeat]["nd1"],
                "nd2_pass": not nd_failures[repeat]["nd2"],
                "nd2_failures": nd_failures[repeat]["nd2"],
                "nd3_strict_unique_maximum_count": nd_strict_unique[repeat],
                "nd3_has_no_threshold_in_this_condition": True,
            }
            for repeat in (1, 2)
        }
    }
    non_degeneracy["nd1_pass"] = all(
        block["nd1_pass"] for block in non_degeneracy["per_repeat"].values()
    )
    non_degeneracy["nd2_pass"] = all(
        block["nd2_pass"] for block in non_degeneracy["per_repeat"].values()
    )
    non_degeneracy["nd1_failures"] = sorted(
        {
            failure
            for block in non_degeneracy["per_repeat"].values()
            for failure in block["nd1_failures"]
        }
    )
    null_component = DegenerateNullComponent()
    null = {
        "canonical": criterion(bundle, null_component),
        "recorded_figures": {
            "top1": 0.375,
            "top2": 0.5,
            "mean_normalized_regret": 0.558333,
            "authority": "PREREGISTRATION.md section 8.5",
        },
        "is_a_gate": False,
    }
    longest_rows = [
        diagnostic_for_case(
            bundle,
            case,
            _model_values(bundle, case, responses.get((str(case["case_id"]), repeat)), component),
            component=component,
        )
        for case in bundle.cases
        if case["variant"] == "longest_artifact"
        for repeat in (1,)
        if responses.get((str(case["case_id"]), repeat)) is not None
    ]
    longest_gold = readout(bundle, component, "longest_artifact")
    return {
        "per_repeat": {
            str(repeat): {
                "per_source": {cid: row for cid, row in per_repeat[repeat].items()}
            }
            for repeat in (1, 2)
        },
        "per_source_table": per_source,
        "primary_endpoint": primary,
        "absolute_usefulness": absolute,
        "non_degeneracy": non_degeneracy,
        "b1_null": null,
        "longest_artifact": {
            "model_conditioned": aggregate_action_diagnostics(longest_rows)
            if longest_rows
            else None,
            "gold_conditioned": longest_gold,
            "is_a_diagnostic": True,
            "contributes_to_no_item": True,
        },
    }


def _score_s13(bundle, component, responses) -> dict:
    gold_rows = {}
    for case in bundle.canonical_cases():
        case_id = str(case["case_id"])
        diagnostic = diagnostic_for_case(
            bundle, case, _gold_values(bundle, case, component), component=component
        )
        gold_rows[case_id] = {
            "top1": float(diagnostic["top1"]),
            "top2": float(diagnostic["top2"]),
            "mean_normalized_regret": float(diagnostic["mean_normalized_regret"]),
        }
    per_repeat = {}
    for repeat in (1, 2):
        model_rows = {}
        for case in bundle.canonical_cases():
            case_id = str(case["case_id"])
            values = _model_values(
                bundle, case, responses.get((case_id, repeat)), component
            )
            if values is None:
                model_rows[case_id] = None
                continue
            diagnostic = diagnostic_for_case(bundle, case, values, component=component)
            model_rows[case_id] = {
                "top1": float(diagnostic["top1"]),
                "top2": float(diagnostic["top2"]),
                "mean_normalized_regret": float(
                    diagnostic["mean_normalized_regret"]
                ),
            }
        per_repeat[str(repeat)] = paired_degradation(gold_rows, model_rows)
    return {
        "s13": per_repeat,
        "passes": all(block["passes"] for block in per_repeat.values()),
        "evaluated_separately_on_each_repeat": True,
    }


def _score_s14(bundle, component, responses) -> dict:
    comparisons = []
    for repeat in (1, 2):
        for source in bundle.source_episode_ids():
            cases = bundle.cases_for_source(source)
            base = next(
                item for item in cases if item["variant"] == CANONICAL_VARIANT
            )
            base_id = str(base["case_id"])
            base_response = responses.get((base_id, repeat))
            for case in cases:
                if case["variant"] not in EQUIVALENCE_VARIANTS:
                    continue
                case_id = str(case["case_id"])
                response = responses.get((case_id, repeat))
                row = {
                    "source_episode_id": source,
                    "variant": str(case["variant"]),
                    "repeat": repeat,
                    "base_repeat": repeat,
                    "variant_response_present": response is not None,
                    "base_response_present": base_response is not None,
                }
                if response is not None and base_response is not None:
                    row["variant_selection"] = _mapped_own_selection(
                        bundle, case, response, component
                    )
                    row["base_selection"] = _mapped_own_selection(
                        bundle, base, base_response, component
                    )
                    row["value_vector_equal"] = all(
                        abs(
                            _model_values(bundle, base, base_response, component)[slot]
                            - _model_values(bundle, case, response, component)[slot]
                        )
                        <= 1e-12
                        for slot in case["runner_control"]["legal_target_slots"]
                        if slot in _model_values(bundle, base, base_response, component)
                        and slot in _model_values(bundle, case, response, component)
                    )
                    row["response_semantically_equal"] = _response_semantics_equal(
                        bundle, base, base_response, case, response
                    )
                comparisons.append(row)
    return own_selection_equivariance(comparisons, expected_total=80)


def _score_s15(bundle, responses) -> dict:
    cross_variant = []
    cross_repeat = []
    for repeat in (1, 2):
        for source in bundle.source_episode_ids():
            cases = bundle.cases_for_source(source)
            base = next(
                item for item in cases if item["variant"] == CANONICAL_VARIANT
            )
            base_id = str(base["case_id"])
            base_response = responses.get((base_id, repeat))
            for case in cases:
                if case["variant"] not in EQUIVALENCE_VARIANTS:
                    continue
                case_id = str(case["case_id"])
                response = responses.get((case_id, repeat))
                cross_variant.append(
                    {
                        "axis": "cross_variant",
                        "source_episode_id": source,
                        "variant": str(case["variant"]),
                        "repeat": repeat,
                        "reference_present": base_response is not None,
                        "compared_present": response is not None,
                        "reference_items": sorted(
                            directional_item_set(
                                base_response["candidate_effects"],
                                _family_by_slot(base),
                            )
                        )
                        if base_response is not None
                        else [],
                        "compared_items": sorted(
                            directional_item_set(
                                response["candidate_effects"], _family_by_slot(case)
                            )
                        )
                        if response is not None
                        else [],
                    }
                )
    for case in bundle.cases:
        case_id = str(case["case_id"])
        first = responses.get((case_id, 1))
        second = responses.get((case_id, 2))
        cross_repeat.append(
            {
                "axis": "cross_repeat",
                "case_id": case_id,
                "repeat": 2,
                "reference_present": first is not None,
                "compared_present": second is not None,
                "reference_items": sorted(
                    directional_item_set(
                        first["candidate_effects"], _family_by_slot(case)
                    )
                )
                if first is not None
                else [],
                "compared_items": sorted(
                    directional_item_set(
                        second["candidate_effects"], _family_by_slot(case)
                    )
                )
                if second is not None
                else [],
            }
        )
    return directional_continuity(cross_variant + cross_repeat)


def _score_s7(bundle, responses) -> dict:
    records = []
    for case in bundle.cases:
        case_id = str(case["case_id"])
        candidates = [
            dict(item)
            for item in case["model_visible_input"]["candidate_hypotheses"]
        ]
        for repeat in (1, 2):
            response = responses.get((case_id, repeat))
            if response is None:
                status = "missing"
                facts, effects = {}, {}
            else:
                try:
                    parsed = parse_response(
                        response,
                        bundle.contract,
                        case["runner_control"]["legal_target_slots"],
                    )
                except Exception:
                    status = "invalid"
                    facts, effects = {}, {}
                else:
                    status = "measured"
                    facts, effects = parsed["facts"], parsed["candidate_effects"]
            records.append(
                {
                    "case_id": case_id,
                    "split": "development",
                    "repeat": repeat,
                    "attempt_ordinal": 1,
                    "source_episode_id": str(case["source_episode_id"]),
                    "variant": str(case["variant"]),
                    "status": status,
                    "facts": facts,
                    "candidate_effects": effects,
                    "candidate_hypotheses": candidates,
                }
            )
    return effect_self_consistency(records, contract=bundle.contract)


def _score_error_propagation(bundle, component, responses) -> dict:
    localization_rows = []
    classes = []
    substitutions = []
    for case in bundle.canonical_cases():
        case_id = str(case["case_id"])
        legal = tuple(int(slot) for slot in case["runner_control"]["legal_target_slots"])
        gold_response = bundle.response_for(case_id)
        gold_values = _gold_values(bundle, case, component)
        gold_choice = choice_set(gold_values, legal)
        usefulness = _usefulness_by_slot(bundle, case_id)
        ordinal = _ordinal_by_slot(bundle, case_id)
        for repeat in (1, 2):
            response = responses.get((case_id, repeat))
            if response is None:
                classes.append("malformed_or_missing")
                continue
            model_values = _model_values(bundle, case, response, component)
            model_choice = choice_set(model_values, legal)
            classification = classify_error_propagation(
                measured_response_present=True,
                model_choice_set=model_choice,
                gold_choice_set=gold_choice,
                legal_target_slots=legal,
                model_values=model_values,
                gold_values=gold_values,
            )
            classes.append(classification["error_class"])
            localization_rows.append(
                {
                    "case_id": case_id,
                    "facts": response["facts"],
                    "gold_facts": gold_response["facts"],
                    "candidate_effects": response["candidate_effects"],
                    "gold_candidate_effects": gold_response["candidate_effects"],
                    "unresolved_targets": response["unresolved_targets"],
                    "gold_unresolved_targets": gold_response["unresolved_targets"],
                    "salient_tags_model": sorted(
                        directional_item_set(
                            response["candidate_effects"], _family_by_slot(case)
                        )
                    ),
                    "salient_tags_gold": sorted(
                        directional_item_set(
                            gold_response["candidate_effects"], _family_by_slot(case)
                        )
                    ),
                    "model_values": model_values,
                    "gold_values": gold_values,
                    "model_choice_set": model_choice,
                    "gold_choice_set": gold_choice,
                    "selected_model": None,
                    "selected_gold": None,
                    "top1_model": classification["preserved"],
                    "top1_gold": True,
                    "top2_model": None,
                    "top2_gold": None,
                    "regret_model": None,
                    "regret_gold": None,
                }
            )
            truth_table_effects = expected_effects_from_facts(
                bundle.contract,
                [
                    dict(item)
                    for item in case["model_visible_input"]["candidate_hypotheses"]
                ],
                response["facts"],
            )
            variants = {
                "D0": (response, True),
                "D1": (
                    _hybrid_response(
                        facts=response, effects=gold_response, relations=response
                    ),
                    False,
                ),
                "D2": (
                    _hybrid_response(
                        facts=response, effects=response, relations=gold_response
                    ),
                    False,
                ),
                "D3": (
                    {"facts": dict(response["facts"]),
                     "candidate_effects": dict(truth_table_effects),
                     "unresolved_targets": {
                         target: dict(vector)
                         for target, vector in response["unresolved_targets"].items()
                     }},
                    False,
                ),
                "D4": (gold_response, False),
            }
            labels = {
                "D0": ("model", "model", "the measured result (not a substitution)"),
                "D1": ("gold", "model", "the decision cost of the model's effect errors"),
                "D2": ("model", "gold", "the decision cost of the model's relation errors"),
                "D3": (
                    "effect_from_facts(model facts)",
                    "model",
                    "S-7 localization: effect errors downstream of facts or not",
                ),
                "D4": ("gold", "gold", "the gold reference"),
            }
            for identifier, (variant_response, measured) in variants.items():
                variant_values = _round(
                    bound_values(
                        component,
                        build_component_input(case, variant_response, bundle.contract),
                        case,
                    )
                )
                effects_source, relations_source, isolates = labels[identifier]
                substitutions.append(
                    diagnostic_substitution(
                        identifier=identifier,
                        case_id=f"{case_id}#repeat{repeat}",
                        values=variant_values,
                        legal_target_slots=legal,
                        gold_values=gold_values,
                        gold_choice_set=gold_choice,
                        usefulness_by_slot=usefulness,
                        evaluator_ordinal_by_slot=ordinal,
                        effects_source=effects_source,
                        relations_source=relations_source,
                        isolates=isolates,
                        measured=measured,
                    )
                )
    d0_d3 = []
    by_case = {}
    for row in substitutions:
        record = (
            row.as_record() if isinstance(row, EvaluatorOnlySubstitution) else dict(row)
        )
        by_case.setdefault(str(record["case_id"]), {})[str(record["identifier"])] = record
    for case_key, rows in sorted(by_case.items()):
        if "D0" in rows and "D3" in rows:
            d0_d3.append(
                {
                    "case_id": case_key,
                    "D0_choice_set": rows["D0"]["choice_set"],
                    "D3_choice_set": rows["D3"]["choice_set"],
                    "decision_level_contribution_of_s7_violations": (
                        rows["D0"]["preserved_equivalent"]
                        != rows["D3"]["preserved_equivalent"]
                    ),
                }
            )
    return {
        "localization": localization_tables(localization_rows),
        "error_class_census": error_class_census(classes),
        "error_classes_are_exhaustive_and_exclusive": True,
        "evaluator_only_diagnostic_substitution": substitution_table(substitutions),
        "D0_D3_localization": d0_d3,
    }


def _manifest_integrity(reader: AuditedReader) -> dict:
    manifest = reader.read_json(MANIFEST_PATH, detail="frozen manifest verification")
    mismatches, missing = [], []
    for name, recorded in manifest["files_sha256"].items():
        path = ROOT / name
        if not path.is_file():
            missing.append(name)
            continue
        observed = reader.hash_file(path, detail="frozen manifest verification")[
            "file_sha256"
        ]
        if observed != recorded:
            mismatches.append(name)
    return {
        "mismatches": sorted(mismatches),
        "missing": sorted(missing),
        "checked_file_count": len(manifest["files_sha256"]),
        "passes": not mismatches and not missing,
    }


def _development_items(
    reader: AuditedReader,
    bundle,
    responses,
    canonical,
    s13_block,
    s14_block,
    s15_block,
    s7_record,
) -> dict[int, dict]:
    """The section-12 items 1--23 with observed values and verdicts."""

    items: dict[int, dict] = {}

    def record(item: int, name: str, requirement: str, observed, passed: bool) -> None:
        items[item] = {
            "item": name,
            "requirement": requirement,
            "observed": observed,
            "pass": bool(passed),
        }

    integrity = _manifest_integrity(reader)
    record(
        1,
        "frozen-manifest integrity",
        "every protected and condition file matches its frozen file_sha256",
        integrity,
        integrity["passes"],
    )
    ledger = validate_access_ledger(ACCESS_LEDGER_PATH)
    record(
        2,
        "access ledger",
        "file-open granular, schema-complete, zero section-6.3 violations",
        {
            "record_count": ledger["record_count"],
            "never_open_open_count": ledger["never_open_open_count"],
            "retrospective_disclosure_count": ledger[
                "retrospective_disclosure_count"
            ],
            "schema_complete": ledger["schema_complete"],
        },
        ledger["passes"],
    )
    cost_gate = reader.read_json(COST_GATE_PATH, detail="gate 3 accounting")
    spend = (
        reader.read_jsonl(SPEND_LEDGER_PATH, detail="gate 3 spend ledger")
        if SPEND_LEDGER_PATH.is_file()
        else []
    )
    accumulated = max(
        (float(row.get("accumulated_cost_usd", 0.0)) for row in spend), default=0.0
    )
    record(
        3,
        "accounting",
        "every attempt recorded; accumulated cost <= $2.50; no unrecorded submission",
        {
            "spend_ledger_entries": len(spend),
            "accumulated_cost_usd": accumulated,
            "hard_spend_ceiling_usd": HARD_SPEND_CEILING_USD,
            "cost_gate_proceed": bool(cost_gate.get("proceed")),
        },
        bool(spend)
        and accumulated <= HARD_SPEND_CEILING_USD
        and bool(cost_gate.get("proceed")),
    )
    attempts = _load_attempts(reader)
    expected_calls = {
        (str(case["case_id"]), repeat)
        for case in bundle.cases
        for repeat in (1, 2)
    }
    observed_calls = {
        (
            str(row["call_context"]["case_id"]),
            int(row["call_context"]["repeat"]),
        )
        for row in attempts
    }
    record(
        4,
        "schedule completeness",
        "112 logical calls attempted; no case skipped, added or reordered",
        {
            "logical_calls_attempted": len(observed_calls),
            "expected_logical_calls": EXPECTED_LOGICAL_CALLS,
            "missing_logical_calls": sorted(
                f"{case_id}#repeat{repeat}"
                for case_id, repeat in expected_calls - observed_calls
            ),
            "unexpected_logical_calls": sorted(
                f"{case_id}#repeat{repeat}"
                for case_id, repeat in observed_calls - expected_calls
            ),
        },
        len(observed_calls) == EXPECTED_LOGICAL_CALLS
        and expected_calls == observed_calls,
    )
    answerability = reader.read_json(
        V13_DIR / "ANSWERABILITY_VALIDATION.json", detail="gate 5 answerability"
    )
    record(
        5,
        "answerability",
        "development pass, zero unsupported or ambiguous forms",
        {
            "status": answerability.get("status"),
            "unsupported_or_ambiguous": answerability.get("unsupported_or_ambiguous"),
        },
        answerability.get("status") == "pass"
        and int(answerability.get("unsupported_or_ambiguous", -1)) == 0,
    )
    firewall = reader.read_json(
        V13_DIR / "FIREWALL_VALIDATION.json", detail="gate 6 firewall"
    )
    record(
        6,
        "firewall",
        "development pass, zero failures",
        {"status": firewall.get("status")},
        firewall.get("status") == "pass"
        and all(bool(value) for value in firewall.get("checks", {}).values()),
    )
    gold = reader.read_json(
        CONDITION_DIR / "GOLD_ADEQUACY_DEVELOPMENT.json",
        detail="gate 7 gold adequacy (S-3)",
    )
    record(
        7,
        "gold-adequacy (S-3)",
        "B-1 on gold meets the frozen gate and G_i != L_i for all 8 sources",
        {
            "passes": gold["passes"],
            "degenerate_gold_choice_set_sources": gold[
                "degenerate_gold_choice_set_sources"
            ],
        },
        bool(gold["passes"]),
    )
    first_attempts = [row for row in attempts if int(row["attempt_ordinal"]) == 1]
    first_attempt_valid = len(
        [row for row in first_attempts if row.get("structurally_valid")]
    )
    first_rate = first_attempt_valid / len(first_attempts) if first_attempts else 0.0
    record(
        8,
        "first-attempt schema validity (S-4)",
        ">= 0.99",
        {"rate": first_rate, "first_attempts": len(first_attempts)},
        first_rate >= FIRST_ATTEMPT_SCHEMA_FLOOR,
    )
    measured_calls = sum(
        1 for value in responses.values() if value is not None
    )
    post_rate = measured_calls / len(expected_calls) if expected_calls else 0.0
    record(
        9,
        "post-permitted-retry validity (S-5)",
        "= 1.00",
        {"rate": post_rate, "measured_calls": measured_calls},
        post_rate >= POST_RETRY_VALIDITY_FLOOR,
    )
    illegal = int(canonical["absolute_usefulness"]["illegal_target_count"])
    record(
        10,
        "zero illegal values/targets (S-6)",
        "= 0",
        {"illegal_target_count": illegal},
        illegal == 0,
    )
    record(
        11,
        "effect self-consistency (S-7)",
        "diagnostic_only; no threshold and no veto (section 8.6)",
        {
            "disposition": s7_record["disposition"],
            "C_response": s7_record["C_response"],
            "C_field": s7_record["C_field"],
            "violation_count": s7_record["violation_count"],
        },
        False,
    )
    semantic = score_cases(
        {"cases": list(bundle.cases), "repeat_count": 2},
        bundle.annotations,
        responses,
        contract=bundle.contract,
    )
    observed = semantic["observed"]

    def clears(value, floor) -> bool:
        # Section 8.2: a zero denominator is NA, never 0 and never 1; NA cannot
        # clear a threshold.

        return value is not None and float(value) >= float(floor)

    record(
        12,
        "fact precision/recall (S-8)",
        ">= 0.65 / >= 0.50",
        {"precision": observed["precision"], "recall": observed["recall"]},
        clears(observed["precision"], SEMANTIC_FLOORS["fact_precision"])
        and clears(observed["recall"], SEMANTIC_FLOORS["fact_recall"]),
    )
    record(
        13,
        "directional effect precision/recall (S-9)",
        ">= 0.60 / >= 0.50",
        {
            "precision": observed["directional_effect_precision"],
            "recall": observed["directional_effect_recall"],
        },
        clears(
            observed["directional_effect_precision"],
            SEMANTIC_FLOORS["directional_effect_precision"],
        )
        and clears(
            observed["directional_effect_recall"],
            SEMANTIC_FLOORS["directional_effect_recall"],
        ),
    )
    record(
        14,
        "relation precision/recall (S-10)",
        ">= 0.60 / >= 0.50",
        {
            "precision": observed["relation_precision"],
            "recall": observed["relation_recall"],
        },
        clears(observed["relation_precision"], SEMANTIC_FLOORS["relation_precision"])
        and clears(observed["relation_recall"], SEMANTIC_FLOORS["relation_recall"]),
    )
    absolute = canonical["absolute_usefulness"]["gate"]
    record(
        15,
        "absolute model-conditioned B-1 (S-11)",
        "top-1 >= 0.60, top-2 >= 0.80, regret <= 0.35",
        canonical["absolute_usefulness"],
        bool(absolute["passes"]),
    )
    nd = canonical["non_degeneracy"]
    record(
        16,
        "non-degeneracy (S-12)",
        "ND-1/ND-2/ND-3 computed and recorded; ND-1 failures enumerated",
        nd,
        bool(nd.get("nd1_pass")) and bool(nd.get("nd2_pass")),
    )
    record(
        17,
        "paired degradation (S-13)",
        "top-1 decline <= 0.125, top-2 decline <= 0.125, mean positive excess <= 0.05",
        s13_block,
        bool(s13_block["passes"]),
    )
    record(
        18,
        "own-selection equivariance (S-14)",
        "80/80 repeat-matched development comparisons",
        {
            "comparisons_passed": s14_block["comparisons_passed"],
            "comparisons_total": s14_block["comparisons_total"],
        },
        bool(s14_block["passes"]),
    )
    record(
        19,
        "directional-effect continuity (S-15)",
        "precision >= 0.60, recall >= 0.50",
        s15_block["micro_aggregate"],
        bool(s15_block["passes"]),
    )
    primary = canonical["primary_endpoint"]["per_repeat"]
    record(
        20,
        "primary, repeat 1",
        "choice-set preservation >= 7/8 on repeat 1 alone",
        primary["1"],
        bool(primary["1"]["passes"]),
    )
    record(
        21,
        "primary, repeat 2",
        "choice-set preservation >= 7/8 on repeat 2 alone",
        primary["2"],
        bool(primary["2"]["passes"]),
    )
    record(
        22,
        "repeat agreement",
        "computed and reported separately; never averaged into 20 or 21",
        canonical["primary_endpoint"]["repeat_agreement"],
        True,
    )
    record(
        23,
        "longest_artifact",
        "separate diagnostic; contributes to no item above",
        canonical["longest_artifact"],
        True,
    )
    return items


def _development_outcome(stage: str = "score") -> dict:
    reader = _stage_reader(stage)
    responses = _load_measured_responses(reader)
    bundle = load_development_bundle()
    component = EstimatorV1SalientCategory()
    canonical = _canonical_scoring(bundle, component, responses)
    s13_block = _score_s13(bundle, component, responses)
    s14_block = _score_s14(bundle, component, responses)
    s15_block = _score_s15(bundle, responses)
    s7_record = _score_s7(bundle, responses)
    error_propagation = _score_error_propagation(bundle, component, responses)
    items = _development_items(
        reader, bundle, responses, canonical, s13_block, s14_block, s15_block, s7_record
    )
    outcome = eligibility_report(
        items,
        split="development",
        diagnostic_only={11: DiagnosticOnly(s7_record)},
    )
    return {
        "reader": reader,
        "bundle": bundle,
        "responses": responses,
        "canonical": canonical,
        "s13": s13_block,
        "s14": s14_block,
        "s15": s15_block,
        "s7": s7_record,
        "error_propagation": error_propagation,
        "items": items,
        "eligibility": outcome,
        "manifest_integrity": _manifest_integrity(reader),
    }


def stage_score() -> dict:
    context = _development_outcome("score")
    document = {
        "schema_version": 1,
        "condition_id": CONDITION_ID,
        "authorizing_adr": AUTHORIZING_ADR,
        "stage": "score",
        "split": "development",
        "choice_sets_and_primary": context["canonical"],
        "paired_degradation_s13": context["s13"],
        "own_selection_equivariance_s14": context["s14"],
        "directional_continuity_s15": context["s15"],
        "effect_self_consistency_s7": context["s7"],
        "s7_disposition": "diagnostic_only",
        "paid_inference": False,
        "model_calls_made_by_this_stage": 0,
        "authorization": STAGE_AUTHORIZATIONS["score"],
    }
    file_sha256 = _json_write(DEVELOPMENT_SCORE_PATH, document)
    return {
        "stage": "score",
        "primary_endpoint": context["canonical"]["primary_endpoint"],
        "paired_degradation_s13": context["s13"]["passes"],
        "own_selection_equivariance_s14": context["s14"]["passes"],
        "directional_continuity_s15": context["s15"]["passes"],
        "s7_C_response": context["s7"]["C_response"],
        "s7_C_field": context["s7"]["C_field"],
        "development_score_file_sha256": file_sha256,
        "model_calls_made_by_this_stage": 0,
    }


def stage_error_propagation() -> dict:
    context = _development_outcome("error-propagation")
    document = {
        "schema_version": 1,
        "condition_id": CONDITION_ID,
        "authorizing_adr": AUTHORIZING_ADR,
        "stage": "error-propagation",
        "split": "development",
        **context["error_propagation"],
        "paid_inference": False,
        "model_calls_made_by_this_stage": 0,
        "authorization": STAGE_AUTHORIZATIONS["error-propagation"],
    }
    file_sha256 = _json_write(ERROR_PROPAGATION_PATH, document)
    return {
        "stage": "error-propagation",
        "error_class_census": context["error_propagation"]["error_class_census"],
        "D0_D3_localization_cases": len(
            context["error_propagation"]["D0_D3_localization"]
        ),
        "error_propagation_file_sha256": file_sha256,
        "model_calls_made_by_this_stage": 0,
    }


def stage_gates() -> dict:
    context = _development_outcome("gates")
    document = {
        "schema_version": 1,
        "condition_id": CONDITION_ID,
        "authorizing_adr": AUTHORIZING_ADR,
        "stage": "gates",
        "split": "development",
        "items": {str(item): row for item, row in sorted(context["items"].items())},
        "eligibility": context["eligibility"],
        "paid_inference": False,
        "model_calls_made_by_this_stage": 0,
        "authorization": STAGE_AUTHORIZATIONS["gates"],
    }
    file_sha256 = _json_write(ELIGIBILITY_PATH, document)
    return {
        "stage": "gates",
        "verdict": context["eligibility"]["verdict"],
        "outcome_label": context["eligibility"]["outcome_label"],
        "failed_item_ids": context["eligibility"]["failed_item_ids"],
        "eligibility_file_sha256": file_sha256,
        "model_calls_made_by_this_stage": 0,
    }


def stage_development_report() -> dict:
    context = _development_outcome("development-report")
    sections = {
        "condition": {
            "condition_id": CONDITION_ID,
            "authorizing_adr": AUTHORIZING_ADR,
            "artifact_classifier": "model_semantic_compatibility_diagnostic",
        },
        "frozen_inheritance": context["manifest_integrity"],
        "model_condition": context["reader"].read_json(
            CONDITION_DIR / "MODEL_CONDITION.json", detail="report model condition"
        ),
        "schedule": {
            "logical_calls": EXPECTED_LOGICAL_CALLS,
            "schedule": "DEVELOPMENT_SCHEDULE.json, unchanged",
        },
        "accounting": context["items"][3]["observed"],
        "eligibility": context["eligibility"],
        "gates": {str(item): row for item, row in sorted(context["items"].items())},
        "primary_endpoint": context["canonical"]["primary_endpoint"],
        "per_source_choice_sets": context["canonical"]["per_source_table"],
        "repeat_agreement": context["canonical"]["primary_endpoint"][
            "repeat_agreement"
        ],
        "non_primary_metrics": {
            "b1_null": context["canonical"]["b1_null"],
            "longest_artifact": context["canonical"]["longest_artifact"],
            "error_class_census": context["error_propagation"]["error_class_census"],
        },
        "effect_self_consistency": context["s7"],
        "error_propagation": context["error_propagation"]["localization"],
        "evaluator_only_diagnostic_substitution": context["error_propagation"][
            "evaluator_only_diagnostic_substitution"
        ],
        "outcome": {
            "verdict": context["eligibility"]["verdict"],
            "outcome_label": context["eligibility"]["outcome_label"],
        },
        "claim_boundary": (
            "PREREGISTRATION.md section 16 governs. A pass establishes bounded "
            "compatibility of source artifact -> this model/configuration -> v1.3 "
            "semantics -> frozen B-1 inside this controlled generator, and nothing "
            "more."
        ),
    }
    document = {
        "schema_version": 1,
        "condition_id": CONDITION_ID,
        "authorizing_adr": AUTHORIZING_ADR,
        "stage": "development-report",
        "split": "development",
        **sections,
        "paid_inference": False,
        "model_calls_made_by_this_stage": 0,
        "authorization": STAGE_AUTHORIZATIONS["development-report"],
    }
    file_sha256 = _json_write(DEVELOPMENT_REPORT_PATH, document)
    markdown = (
        "# Development report -- `model-semantic-v1.3.1-N1`\n\n"
        f"- Outcome: `{document['outcome']['outcome_label']}`\n"
        f"- Verdict: `{document['outcome']['verdict']}`\n"
        f"- S-7 `C_response`: `{context['s7']['C_response']}` "
        f"(`diagnostic_only`, not a gate)\n"
        f"- Manifest integrity: `{context['manifest_integrity']['passes']}`\n"
        f"- Model or provider calls made by this stage: 0\n"
    )
    DEVELOPMENT_REPORT_MARKDOWN_PATH.write_text(markdown, encoding="utf-8")
    return {
        "stage": "development-report",
        "outcome_label": document["outcome"]["outcome_label"],
        "development_report_file_sha256": file_sha256,
        "development_report_markdown_file_sha256": hashlib.sha256(
            markdown.encode("utf-8")
        ).hexdigest(),
        "model_calls_made_by_this_stage": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage",
        choices=("gold-adequacy",) + SCORING_STAGES,
        required=True,
    )
    parser.add_argument("--split", choices=("development",), default="development")
    args = parser.parse_args()
    if args.stage in SCORING_STAGES:
        stage = {
            "score": stage_score,
            "error-propagation": stage_error_propagation,
            "gates": stage_gates,
            "development-report": stage_development_report,
        }[args.stage]
        try:
            result = stage()
        except DormantScoringRefusal as refusal:
            raise SystemExit(f"dormant scoring refused: {refusal}")
        print(canonical_json(result))
        return 0
    document = gold_adequacy_development()
    print(
        canonical_json(
            {
                "stage": document["stage"],
                "passes": document["passes"],
                "canonical_gold_aggregate": document["canonical_gold_aggregate"],
                "degenerate_gold_choice_set_sources": document[
                    "degenerate_gold_choice_set_sources"
                ],
                "recorded_figure_reproduction": document[
                    "recorded_figure_reproduction"
                ],
                "gold_adequacy_file_sha256": document.get(
                    "_written_file_sha256", ""
                ),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
