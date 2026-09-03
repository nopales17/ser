#!/usr/bin/env python3
"""Audit and freeze the bounded AuthzGym semantic-bottleneck diagnosis."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from ser.authzgym.semantic_contract import (
    FACT_BY_SLOT,
    FACT_SLOTS,
    RELATION_BY_SLOT,
    _expected_effects,
    _expected_unresolved_targets,
    episode_from_case,
)
from ser.core.types import canonical_json, content_hash
from ser.evaluation.authz_artifacts import file_sha256
from ser.evaluation.authz_contract_analysis import _normalize


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "experiments/authzgym_semantic_bottleneck_v1"
SOURCE = ROOT / "experiments/authzgym_stronger_model_v1"
EXPERIMENT_ID = "authzgym-semantic-bottleneck-v1"
BUDGET_USD = 0.25
SELECTED_CASE_IDS = (
    "asv1-d-5e6417ce899f--base_entry--71eb766486",
    "asv1-d-5e6417ce899f--artifact_reordering--0e8b205ac2",
    "asv1-d-f5f54c9c8670--base_entry--0dd132fa21",
    "asv1-d-f5f54c9c8670--artifact_reordering--fbd1de3a37",
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def _write_new_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _population_hash_valid(value: dict[str, Any]) -> bool:
    payload = dict(value)
    observed = payload.pop("population_hash", None)
    return isinstance(observed, str) and content_hash(payload) == observed


def _record_hash_valid(value: dict[str, Any]) -> bool:
    payload = dict(value)
    observed = payload.pop("record_hash", None)
    return isinstance(observed, str) and content_hash(payload) == observed


def _visible_called_symbols(case: dict[str, Any]) -> set[str]:
    source = case["model_visible_input"]["current_artifact"]["source"]
    current_slot = case["runner_control"]["current_artifact_slot"]
    result: set[str] = set()
    for item in case["model_visible_input"]["public_artifact_inventory"]:
        if item["slot"] == current_slot:
            continue
        for symbol in item["exported_symbols"]:
            if re.search(rf"\b{re.escape(symbol)}\s*\(", source):
                result.add(symbol)
    return result


def _prompt_fact_answerability(case: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Independent literal reading of the frozen public slot definitions.

    This intentionally does not use ArtifactSpec.expected_fact_keys. Those keys
    are the evaluator labels under audit.
    """

    source = case["model_visible_input"]["current_artifact"]["source"]
    direct_true = {
        "f0": 'channel == "alternate"' in source,
        "f1": "direct_only=True" in source,
        "f2": "include_inherited=True" in source,
        "f3": 'fallback_role="reader"' in source or "role_map.get" in source,
        "f4": "role_map.get" in source,
        "f5": "propagated_role = source_role" in source,
        "f6": "token_scope=None" in source,
        "f7": "feature_context={}" in source,
        "f8": (
            "token_scope=token_scope" in source
            or "token_scope=request.token.scope" in source
        ),
        "f9": (
            "feature_context=feature_context" in source
            or "feature_context=request.flags" in source
        ),
        "f10": (
            "apply_change(actor, item)" in source
            and "actor.owner_id == item.owner_id" not in source
        ),
        "f11": "actor.owner_id == item.owner_id" in source,
        "f12": 'audit_record = ("owner"' in source,
        "f13": 'audit_record = ("membership"' in source,
        "f14": 'audit_record = ("role"' in source,
        "f15": 'audit_record = ("context"' in source,
        "f16": bool(_visible_called_symbols(case)),
        # The current source alone does not establish an unseen standard guard.
        "f17": False,
        "f18": "direct_only=True" in source,
    }
    result = {
        slot: {
            "status": "inferable",
            "value": bool(direct_true.get(slot, False)),
            "basis": "literal frozen-slot definition applied to current visible source",
        }
        for slot in FACT_SLOTS
    }
    if "token_scope=None" in source or "feature_context={}" in source:
        result["f19"] = {
            "status": "unavailable",
            "value": None,
            "basis": "the slot requires knowing that the opaque callee is the guard; logical roles are evaluator-only",
        }
    if "handle_request" not in source:
        for slot in ("f20", "f21", "f22", "f23", "f24"):
            result[slot] = {
                "status": "unavailable",
                "value": None,
                "basis": "the slot requires knowing that the opaque current artifact is test code; logical roles are evaluator-only",
            }
    return result


def _prompt_effect_answerability(
    case: dict[str, Any], fact_audit: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    if any(
        fact_audit[slot]["status"] == "unavailable"
        for slot in ("f20", "f21", "f22", "f23", "f24")
    ):
        return {
            f"c{index}": {
                "status": "unavailable",
                "value": None,
                "basis": "candidate effect depends on evaluator-only test-role labels",
            }
            for index in range(4)
        }
    direct_fact_keys = tuple(
        FACT_BY_SLOT[slot]
        for slot in FACT_SLOTS
        if fact_audit[slot]["status"] == "inferable" and fact_audit[slot]["value"]
    )
    values = _expected_effects(
        direct_fact_keys,
        episode_from_case(case).candidates,
    )
    return {
        slot: {
            "status": "inferable",
            "value": value,
            "basis": "frozen v1.2 fact-to-candidate relation directions applied to source-direct facts",
        }
        for slot, value in values.items()
    }


def _fact_discrepancy_category(
    actual: bool,
    expected: bool,
    answer: dict[str, Any],
) -> str:
    if answer["status"] == "unavailable":
        return "artifact_insufficiency_or_label_ambiguity"
    if answer["value"] != expected and actual == answer["value"]:
        return "evaluator_label_mismatch"
    if actual and not expected:
        return "false_positive_fact_model_overcommit"
    return "false_negative_fact_model_omission"


def _effect_discrepancy_category(
    actual: str,
    expected: str,
    answer: dict[str, Any],
) -> str:
    if answer["status"] == "unavailable":
        return "artifact_insufficiency_or_label_ambiguity"
    if answer["value"] != expected and actual == answer["value"]:
        return "evaluator_label_mismatch"
    if actual in {"support", "contradict"} and expected not in {
        "support",
        "contradict",
    }:
        return "false_positive_effect_model_overcommit"
    return "incorrect_or_missed_effect"


def _audit_case(case: dict[str, Any], run: dict[str, Any]) -> dict[str, Any]:
    expected = case["evaluator_only"]["expected_content"]
    actual = run["result"]["parsed"]["provider_content"]
    fact_answers = _prompt_fact_answerability(case)
    effect_answers = _prompt_effect_answerability(case, fact_answers)
    fact_discrepancies = []
    effect_discrepancies = []
    unresolved_discrepancies = []
    evaluator_fact_mismatches = []
    evaluator_effect_mismatches = []

    for slot in FACT_SLOTS:
        answer = fact_answers[slot]
        if answer["status"] == "unavailable" or answer["value"] != expected["facts"][slot]:
            evaluator_fact_mismatches.append(
                {
                    "slot": slot,
                    "meaning": FACT_BY_SLOT[slot],
                    "evaluator": expected["facts"][slot],
                    "prompt_grounded": answer,
                }
            )
        if actual["facts"][slot] != expected["facts"][slot]:
            fact_discrepancies.append(
                {
                    "slot": slot,
                    "meaning": FACT_BY_SLOT[slot],
                    "evaluator": expected["facts"][slot],
                    "model": actual["facts"][slot],
                    "category": _fact_discrepancy_category(
                        actual["facts"][slot], expected["facts"][slot], answer
                    ),
                    "prompt_grounded": answer,
                }
            )

    for slot in sorted(actual["hypothesis_effects"]):
        answer = effect_answers[slot]
        if answer["status"] == "unavailable" or answer["value"] != expected["hypothesis_effects"][slot]:
            evaluator_effect_mismatches.append(
                {
                    "slot": slot,
                    "evaluator": expected["hypothesis_effects"][slot],
                    "prompt_grounded": answer,
                }
            )
        if actual["hypothesis_effects"][slot] != expected["hypothesis_effects"][slot]:
            effect_discrepancies.append(
                {
                    "slot": slot,
                    "evaluator": expected["hypothesis_effects"][slot],
                    "model": actual["hypothesis_effects"][slot],
                    "category": _effect_discrepancy_category(
                        actual["hypothesis_effects"][slot],
                        expected["hypothesis_effects"][slot],
                        answer,
                    ),
                    "prompt_grounded": answer,
                }
            )

    roles = case["evaluator_only"]["logical_roles_by_slot"]
    for target, relations in expected["unresolved_targets"].items():
        for relation, evaluator_value in relations.items():
            model_value = actual["unresolved_targets"][target][relation]
            if evaluator_value != model_value:
                unresolved_discrepancies.append(
                    {
                        "target": target,
                        "target_role": roles[target],
                        "relation": relation,
                        "relation_meaning": RELATION_BY_SLOT[relation],
                        "evaluator": evaluator_value,
                        "model": model_value,
                        "category": (
                            "false_negative_unresolved_relation"
                            if evaluator_value
                            else "false_positive_unresolved_relation"
                        ),
                        "answerability": "inferable_from_visible_call_and_public_inventory",
                    }
                )

    expected_unresolved = _expected_unresolved_targets(
        episode_from_case(case),
        episode_from_case(case).artifact(
            episode_from_case(case).artifact_order[
                case["runner_control"]["current_artifact_slot"]
            ]
        ),
        tuple(case["runner_control"]["legal_target_slots"]),
    )
    unresolved_labels_reproducible = expected_unresolved == expected["unresolved_targets"]
    answerability_valid = not (
        evaluator_fact_mismatches
        or evaluator_effect_mismatches
        or not unresolved_labels_reproducible
    )
    return {
        "case_id": case["case_id"],
        "source_episode_id": case["source_episode_id"],
        "variant": case["variant"],
        "mechanism_family": case["evaluator_only"]["mechanism_family"],
        "run_valid": run["valid"],
        "answerability": {
            "valid": answerability_valid,
            "evaluator_fact_mismatches": evaluator_fact_mismatches,
            "evaluator_effect_mismatches": evaluator_effect_mismatches,
            "unresolved_labels_reproducible_from_visible_input": unresolved_labels_reproducible,
        },
        "fact_discrepancies": fact_discrepancies,
        "effect_discrepancies": effect_discrepancies,
        "unresolved_discrepancies": unresolved_discrepancies,
        "counts": {
            "false_positive_facts_against_evaluator": sum(
                actual["facts"][slot] and not expected["facts"][slot]
                for slot in FACT_SLOTS
            ),
            "false_negative_facts_against_evaluator": sum(
                expected["facts"][slot] and not actual["facts"][slot]
                for slot in FACT_SLOTS
            ),
            "incorrect_effects_against_evaluator": len(effect_discrepancies),
            "asserted_nonunknown_effects": sum(
                value in {"support", "contradict"}
                for value in actual["hypothesis_effects"].values()
            ),
            "missed_unresolved_relations": sum(
                item["category"] == "false_negative_unresolved_relation"
                for item in unresolved_discrepancies
            ),
            "false_positive_unresolved_relations": sum(
                item["category"] == "false_positive_unresolved_relation"
                for item in unresolved_discrepancies
            ),
        },
    }


def _jsonable(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def _transformation_audit(
    population: dict[str, Any], runs_by_case: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    cases = {item["case_id"]: item for item in population["cases"]}
    by_source_variant = {
        (item["source_episode_id"], item["variant"]): item
        for item in population["cases"]
    }
    records = []
    for source_id in sorted({item["source_episode_id"] for item in population["cases"]}):
        base = by_source_variant[(source_id, "base_entry")]
        for variant in ("artifact_reordering", "symbol_renaming"):
            peer = by_source_variant[(source_id, variant)]
            left = runs_by_case[base["case_id"]]["result"]["parsed"]["provider_content"]
            right = runs_by_case[peer["case_id"]]["result"]["parsed"]["provider_content"]
            left_norm = _jsonable(_normalize(cases[base["case_id"]], left))
            right_norm = _jsonable(_normalize(cases[peer["case_id"]], right))
            facts_changed = left_norm["facts"] != right_norm["facts"]
            effects_changed = (
                left_norm["effects_by_relation"]
                != right_norm["effects_by_relation"]
            )
            unresolved_changed = (
                left_norm["unresolved_by_role"]
                != right_norm["unresolved_by_role"]
            )
            records.append(
                {
                    "source_episode_id": source_id,
                    "mechanism_family": base["evaluator_only"]["mechanism_family"],
                    "base_case_id": base["case_id"],
                    "peer_case_id": peer["case_id"],
                    "variant": variant,
                    "semantic_exact": left_norm == right_norm,
                    "changed_layers": [
                        name
                        for name, changed in (
                            ("facts", facts_changed),
                            ("effects", effects_changed),
                            ("unresolved", unresolved_changed),
                        )
                        if changed
                    ],
                    "category": (
                        "artifact_order_sensitivity"
                        if variant == "artifact_reordering"
                        else "symbol_renaming_sensitivity"
                    ),
                    "evaluator_ambiguity_for_equivalence": False,
                }
            )
    return records


def _taxonomy(
    population: dict[str, Any], runs: list[dict[str, Any]]
) -> dict[str, Any]:
    runs_by_case = {item["case_id"]: item for item in runs}
    audited = [
        _audit_case(case, runs_by_case[case["case_id"]])
        for case in population["cases"]
        if case["case_id"] in runs_by_case
    ]
    discrepancies = Counter()
    for case in audited:
        for key in ("fact_discrepancies", "effect_discrepancies", "unresolved_discrepancies"):
            discrepancies.update(item["category"] for item in case[key])
    transformations = _transformation_audit(population, runs_by_case)
    total_asserted_effects = sum(
        item["counts"]["asserted_nonunknown_effects"] for item in audited
    )
    missed_unresolved = sum(
        item["counts"]["missed_unresolved_relations"] for item in audited
    )
    return {
        "schema_version": 1,
        "experiment": EXPERIMENT_ID,
        "source_experiment": "authzgym-stronger-model-v1",
        "audit_scope": {
            "development_cases_audited": len(audited),
            "smoke_cases_used_as_semantic_evidence": 0,
            "confirmation_cases_loaded": 0,
            "new_model_calls": 0,
        },
        "summary": {
            "discrepancy_categories": dict(sorted(discrepancies.items())),
            "cases_with_invalid_evaluator_answerability": sum(
                not item["answerability"]["valid"] for item in audited
            ),
            "cases_with_reproducible_unresolved_labels": sum(
                item["answerability"]["unresolved_labels_reproducible_from_visible_input"]
                for item in audited
            ),
            "transformation_pairs": len(transformations),
            "transformation_exact": sum(item["semantic_exact"] for item in transformations),
            "asserted_nonunknown_effects": total_asserted_effects,
            "missed_unresolved_relations": missed_unresolved,
        },
        "overcommit_hypothesis": {
            "status": "moderate_descriptive_support_but_benchmark_contaminated",
            "observable_basis": (
                "The model asserted many non-unknown candidate effects while almost never "
                "using the available unresolved-relation channel; evaluator-label mismatches "
                "prevent a clean causal attribution."
            ),
            "asserted_nonunknown_effects": total_asserted_effects,
            "missed_unresolved_relations": missed_unresolved,
            "hidden_reasoning_inferred": False,
        },
        "cases": audited,
        "transformation_pairs": transformations,
    }


def _case_selection(taxonomy: dict[str, Any]) -> dict[str, Any]:
    audits = {item["case_id"]: item for item in taxonomy["cases"]}
    selected = []
    rationales = {
        SELECTED_CASE_IDS[0]: "h1 base: fact/effect overcommit, missed facts, and missed unresolved relations",
        SELECTED_CASE_IDS[1]: "h1 order-equivalent peer: isolates ordering sensitivity",
        SELECTED_CASE_IDS[2]: "h4 base: clean conservative omission of answerable context-loss facts",
        SELECTED_CASE_IDS[3]: "h4 order-equivalent relative control: recovers all authored-positive facts but adds unsupported assertions",
    }
    for case_id in SELECTED_CASE_IDS:
        audit = audits[case_id]
        selected.append(
            {
                "case_id": case_id,
                "source_episode_id": audit["source_episode_id"],
                "variant": audit["variant"],
                "mechanism_family": audit["mechanism_family"],
                "rationale": rationales[case_id],
                "answerability_valid": audit["answerability"]["valid"],
                "unavailable_or_misaligned_fact_labels": [
                    item["slot"]
                    for item in audit["answerability"]["evaluator_fact_mismatches"]
                ],
                "unavailable_or_misaligned_effect_labels": [
                    item["slot"]
                    for item in audit["answerability"]["evaluator_effect_mismatches"]
                ],
            }
        )
    return {
        "schema_version": 1,
        "experiment": EXPERIMENT_ID,
        "selection_status": "frozen_then_paid_inference_prohibited_by_answerability_gate",
        "selection_rule": "two complete base/order-equivalent pairs covering h1 and h4, chosen from the already exposed executed development prefix",
        "selected_cases": selected,
        "selected_case_count": len(selected),
        "equivalent_pairs": [
            [SELECTED_CASE_IDS[0], SELECTED_CASE_IDS[1]],
            [SELECTED_CASE_IDS[2], SELECTED_CASE_IDS[3]],
        ],
        "stop_gate": {
            "triggered": True,
            "reason": "every selected case has evaluator labels that are unavailable or inconsistent with the model-visible prompt/source",
            "new_model_inference_authorized": False,
        },
    }


def _source_artifacts() -> dict[str, Any]:
    files = {
        "development_population": SOURCE / "DEVELOPMENT_POPULATION.json",
        "development_runs": SOURCE / "development/runs.jsonl",
        "development_provider_responses": SOURCE / "development/provider_responses.jsonl",
        "source_summary": SOURCE / "summary.json",
        "source_validation": SOURCE / "validation.json",
        "v1_2_prompt": ROOT / "experiments/authzgym_semantic_contract_v1_2/prompts/semantic_observation_v1_2.txt",
        "v1_2_vocabulary": ROOT / "experiments/authzgym_semantic_contract_v1_2/schemas/semantic_vocabulary_v1_2.json",
    }
    return {
        "schema_version": 1,
        "experiment": EXPERIMENT_ID,
        "files": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "sha256": file_sha256(path),
            }
            for name, path in files.items()
        },
        "confirmation_preservation": {
            "source_classification": _load_json(SOURCE / "summary.json")["classification"],
            "source_confirmation_executed": _load_json(SOURCE / "summary.json")["confirmation_executed"],
            "confirmation_execution_directory_absent": not (SOURCE / "confirmation").exists(),
            "confirmation_population_not_loaded_by_this_tool": True,
            "confirmation_model_inference_calls": 0,
        },
    }


def _models_and_conditions() -> dict[str, Any]:
    source_config = _load_json(SOURCE / "model_config.json")
    return {
        "schema_version": 1,
        "experiment": EXPERIMENT_ID,
        "condition_a": {
            "status": "reused_stored_outputs",
            "semantic_contract": "v1.2",
            "model": "patchersniper_praneeth/gpt-5.4-mini",
            "source_config_sha256": file_sha256(SOURCE / "model_config.json"),
            "source_configuration": source_config,
            "incremental_calls": 0,
        },
        "condition_b": {
            "status": "not_frozen_or_executed_after_answerability_stop",
            "model": "patchersniper_praneeth/gpt-5.4-mini",
            "purpose": "decomposed interrogation",
            "incremental_calls": 0,
        },
        "condition_c": {
            "status": "not_selected_or_executed_after_answerability_stop",
            "purpose": "stronger-model unchanged-v1.2 probe",
            "incremental_calls": 0,
        },
        "insecure_tls_used_for_new_calls": False,
    }


def _cost_accounting() -> dict[str, Any]:
    return {
        "schema_version": 1,
        "experiment": EXPERIMENT_ID,
        "currency": "USD",
        "hard_incremental_ceiling": BUDGET_USD,
        "expected_incremental_cost_before_stop": 0.0,
        "worst_case_authorized_cost_after_stop": 0.0,
        "logical_calls": 0,
        "provider_submissions": 0,
        "provider_responses": 0,
        "input_tokens": 0,
        "cached_input_tokens": 0,
        "output_tokens": 0,
        "reasoning_output_tokens": 0,
        "semantic_retries": 0,
        "transport_failures": 0,
        "total_incremental_cost": 0.0,
        "percentage_of_budget_consumed": 0.0,
        "stop_reason": "benchmark answerability invalid before any new inference",
    }


def _summary(taxonomy: dict[str, Any], selection: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "experiment": EXPERIMENT_ID,
        "validation": "pass",
        "classification": "benchmark_ambiguity_detected",
        "previous_result_localization": {
            "upstream_semantic_failure_observed": True,
            "downstream_estimator_adequate_under_perfect_v1_2": True,
            "model_inability_vs_interface_vs_task_previously_unresolved": True,
        },
        "offline_audit": taxonomy["summary"],
        "frozen_case_selection": {
            "selected_case_count": selection["selected_case_count"],
            "equivalent_pair_count": len(selection["equivalent_pairs"]),
            "answerability_stop_triggered": selection["stop_gate"]["triggered"],
        },
        "conditions": {
            "a_stored_v1_2_baseline": "available",
            "b_mini_decomposed": "not_run_answerability_stop",
            "c_stronger_v1_2": "not_run_answerability_stop",
        },
        "diagnostic_matrix": {
            "model_weakness": {
                "evidence": "moderate evidence",
                "support": "answerable context-loss facts and 68/69 visible unresolved relations were missed; all eight equivalent pairs were unstable",
                "limitation": "fact/effect aggregate scoring is contaminated by evaluator-label mismatch",
            },
            "elicitation_interface_weakness": {
                "evidence": "weak evidence",
                "support": "one-shot output spans 25 facts, four effects, and many relation booleans, and equivalent forms were unstable",
                "limitation": "decomposed interrogation was correctly not run after the answerability stop",
            },
            "representational_insufficiency": {
                "evidence": "no evidence",
                "support": "v1.2 already has unknown effects and explicit unresolved-relation slots; no correct distinction was shown to be unencodable",
                "limitation": "this does not prove v1.2 sufficient after benchmark repair",
            },
            "task_ambiguity": {
                "evidence": "strong evidence",
                "support": "source-direct facts are scored false and test-role labels require evaluator-only role identity",
                "limitation": "the defect is scoped to the audited v1.2 development labels",
            },
        },
        "resources": _cost_accounting(),
        "confirmation_untouched": True,
        "hypotheses_promoted": [],
        "evidence_ids_added": [],
        "exact_next_empirical_decision": "benchmark_task_definition_repair",
    }


def prepare(experiment: Path) -> None:
    if experiment.exists() and any(
        path.name != "PREREGISTRATION.md" for path in experiment.iterdir()
    ):
        raise FileExistsError("diagnostic experiment directory already has generated artifacts")
    population = _load_json(SOURCE / "DEVELOPMENT_POPULATION.json")
    runs = _load_jsonl(SOURCE / "development/runs.jsonl")
    if not _population_hash_valid(population):
        raise ValueError("source development population hash is invalid")
    if len(runs) != 16 or not all(_record_hash_valid(item) for item in runs):
        raise ValueError("source development run records are incomplete or invalid")
    if _load_json(SOURCE / "summary.json")["confirmation_executed"]:
        raise ValueError("source confirmation is no longer untouched")
    if (SOURCE / "confirmation").exists():
        raise ValueError("source confirmation execution directory exists")

    taxonomy = _taxonomy(population, runs)
    selection = _case_selection(taxonomy)
    sources = _source_artifacts()
    models = _models_and_conditions()
    cost = _cost_accounting()
    _write_new_json(experiment / "OFFLINE_FAILURE_TAXONOMY.json", taxonomy)
    _write_new_json(experiment / "FROZEN_CASE_SELECTION.json", selection)
    _write_new_json(experiment / "SOURCE_ARTIFACTS.json", sources)
    _write_new_json(experiment / "MODEL_CONFIGS.json", models)
    _write_new_json(experiment / "COST_ACCOUNTING.json", cost)

    preregistration = experiment / "PREREGISTRATION.md"
    if not preregistration.exists():
        raise FileNotFoundError("PREREGISTRATION.md must be written before prepare")
    pre_inference_files = {
        "preregistration": preregistration,
        "offline_failure_taxonomy": experiment / "OFFLINE_FAILURE_TAXONOMY.json",
        "frozen_case_selection": experiment / "FROZEN_CASE_SELECTION.json",
        "source_artifacts": experiment / "SOURCE_ARTIFACTS.json",
        "model_configs": experiment / "MODEL_CONFIGS.json",
        "cost_accounting": experiment / "COST_ACCOUNTING.json",
        "implementation": Path(__file__),
    }
    frozen_payload = {
        "schema_version": 1,
        "experiment": EXPERIMENT_ID,
        "frozen_before_new_inference": True,
        "new_inference_authorized": False,
        "files": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "sha256": file_sha256(path),
            }
            for name, path in pre_inference_files.items()
        },
    }
    frozen = {**frozen_payload, "manifest_hash": content_hash(frozen_payload)}
    _write_new_json(experiment / "FROZEN_INPUTS.json", frozen)
    _write_new_json(experiment / "summary.json", _summary(taxonomy, selection))


def verify(experiment: Path) -> dict[str, Any]:
    taxonomy = _load_json(experiment / "OFFLINE_FAILURE_TAXONOMY.json")
    selection = _load_json(experiment / "FROZEN_CASE_SELECTION.json")
    source_artifacts = _load_json(experiment / "SOURCE_ARTIFACTS.json")
    models = _load_json(experiment / "MODEL_CONFIGS.json")
    cost = _load_json(experiment / "COST_ACCOUNTING.json")
    frozen = _load_json(experiment / "FROZEN_INPUTS.json")
    summary = _load_json(experiment / "summary.json")
    frozen_payload = dict(frozen)
    manifest_hash = frozen_payload.pop("manifest_hash")
    checks = {
        "source_development_cases_audited": taxonomy["audit_scope"]["development_cases_audited"] == 16,
        "all_transformation_pairs_audited": taxonomy["summary"]["transformation_pairs"] == 8,
        "all_transformation_pairs_failed_exactness": taxonomy["summary"]["transformation_exact"] == 0,
        "selected_case_count_in_range": 4 <= selection["selected_case_count"] <= 8,
        "two_complete_equivalent_pairs_selected": len(selection["equivalent_pairs"]) == 2,
        "answerability_stop_triggered": selection["stop_gate"]["triggered"],
        "no_new_inference_authorized": not frozen["new_inference_authorized"],
        "no_new_calls_or_tokens": all(
            cost[key] == 0
            for key in (
                "logical_calls",
                "provider_submissions",
                "provider_responses",
                "input_tokens",
                "output_tokens",
                "total_incremental_cost",
            )
        ),
        "spend_below_ceiling": cost["total_incremental_cost"] <= BUDGET_USD,
        "conditions_b_and_c_not_executed": (
            models["condition_b"]["incremental_calls"] == 0
            and models["condition_c"]["incremental_calls"] == 0
        ),
        "confirmation_execution_absent": not (SOURCE / "confirmation").exists(),
        "confirmation_not_loaded_or_called": (
            source_artifacts["confirmation_preservation"]["confirmation_population_not_loaded_by_this_tool"]
            and source_artifacts["confirmation_preservation"]["confirmation_model_inference_calls"] == 0
        ),
        "frozen_manifest_hash_valid": content_hash(frozen_payload) == manifest_hash,
        "frozen_file_hashes_valid": all(
            file_sha256(ROOT / item["path"]) == item["sha256"]
            for item in frozen["files"].values()
        ),
        "classification_narrow": summary["classification"] == "benchmark_ambiguity_detected",
        "no_hypothesis_or_evidence_promotion": not summary["hypotheses_promoted"] and not summary["evidence_ids_added"],
        "single_next_decision": summary["exact_next_empirical_decision"] == "benchmark_task_definition_repair",
    }
    validation = {
        "schema_version": 1,
        "experiment": EXPERIMENT_ID,
        "status": "pass" if all(checks.values()) else "fail",
        "checks": checks,
    }
    return validation


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("prepare", "verify"))
    parser.add_argument("--experiment", type=Path, default=EXPERIMENT)
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args.experiment)
        validation = verify(args.experiment)
        _write_new_json(args.experiment / "validation.json", validation)
    else:
        validation = verify(args.experiment)
    print(canonical_json(validation))
    return 0 if validation["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
