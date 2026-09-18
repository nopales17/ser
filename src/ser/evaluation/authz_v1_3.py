"""Evaluator-side scoring and the fixed v1.3 to historical-estimator adapter."""

from __future__ import annotations

import hashlib
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import fmean
from typing import Iterable, Mapping

from ser.authzgym.model import (
    ArtifactDescriptor,
    CandidateHypothesis,
    SemanticObservation,
    SemanticReference,
)
from ser.authzgym.policies import (
    AuthzEpistemicState,
    estimate_action_values,
    update_state,
)
from ser.authzgym.v1_3_contract import effect_from_facts, parse_response
from ser.core.types import content_hash


FROZEN_ESTIMATOR_SHA256 = (
    "092a7a87d1227c1a1c85ac46c7122e38ac1b6b24d7aaa90abee05abfe4167393"
)
RELATION_TAG_BY_CATEGORY = {
    "ownership": "ownership_path",
    "membership": "membership_path",
    "role": "role_path",
    "context": "context_path",
    "general_dependency": "general_dependency",
}
FAMILY_BY_INTERNAL_TAG = {
    "ownership_path": "ownership",
    "membership_path": "membership",
    "role_path": "role",
    "context_path": "context",
}
EFFECT_SIGN = {"support": 1.0, "contradict": -1.0, "neutral": 0.0, "unknown": 0.0}
SEMANTIC_THRESHOLDS = {
    "fact_precision": 0.65,
    "fact_recall": 0.50,
    "directional_effect_precision": 0.60,
    "directional_effect_recall": 0.50,
    "relation_precision": 0.60,
    "relation_recall": 0.50,
    "effect_self_consistency": 1.00,
    "action_top1": 0.60,
    "action_top2": 0.80,
    "action_normalized_regret": 0.35,
}
MECHANICAL_THRESHOLDS = {
    "first_attempt_schema_valid_rate": 0.99,
    "post_retry_valid_rate": 1.00,
    "length_terminations": 0,
    "incomplete_json": 0,
    "illegal_references": 0,
    "manual_repairs": 0,
    "secret_leaks": 0,
    "schedule_hash_spend_violations": 0,
}
VALIDITY_LAYERS = (
    "manifest",
    "answerability",
    "firewall",
    "oracle",
    "mechanical_response",
    "semantic_interface",
    "downstream",
)


class ScoringV13Error(ValueError):
    pass


def estimator_source_sha256() -> str:
    path = Path(__file__).resolve().parents[1] / "authzgym/policies.py"
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assert_frozen_estimator() -> None:
    observed = estimator_source_sha256()
    if observed != FROZEN_ESTIMATOR_SHA256:
        raise ScoringV13Error(
            f"unchanged estimator hash mismatch: {observed} != {FROZEN_ESTIMATOR_SHA256}"
        )


def _micro_counts(actual: set, expected: set) -> tuple[int, int, int]:
    return len(actual & expected), len(actual), len(expected)


def _metric(counts: Iterable[tuple[int, int, int]]) -> dict:
    values = list(counts)
    tp = sum(item[0] for item in values)
    predicted = sum(item[1] for item in values)
    expected = sum(item[2] for item in values)
    precision = tp / predicted if predicted else None
    recall = tp / expected if expected else None
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision is not None and recall is not None and precision + recall
        else None
    )
    return {
        "true_positive": tp,
        "false_positive": predicted - tp,
        "false_negative": expected - tp,
        "predicted": predicted,
        "expected": expected,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def _mean(values: Iterable[float]) -> float:
    values = tuple(values)
    return fmean(values) if values else 0.0


def adapter_candidates(case: Mapping[str, object]) -> tuple[CandidateHypothesis, ...]:
    candidates = []
    for item in case["model_visible_input"]["candidate_hypotheses"]:
        family = str(item["effect_family"])
        tag = RELATION_TAG_BY_CATEGORY[family]
        candidates.append(
            CandidateHypothesis(
                str(item["slot"]),
                str(item["description"]),
                (tag,),
            )
        )
    return tuple(candidates)


def adapter_inventory(case: Mapping[str, object]) -> tuple[ArtifactDescriptor, ...]:
    return tuple(
        ArtifactDescriptor(
            str(item["public_id"]),
            str(item["path"]),
            tuple(str(symbol) for symbol in item["exported_symbols"]),
            int(item["line_count"]),
        )
        for item in case["model_visible_input"]["public_artifact_inventory"]
    )


def adapter_observation(case: Mapping[str, object], response: Mapping[str, object]) -> SemanticObservation:
    candidates = adapter_candidates(case)
    effects = tuple(
        (
            candidate.hypothesis_id,
            EFFECT_SIGN[str(response["candidate_effects"][f"c{index}"])],
        )
        for index, candidate in enumerate(candidates)
    )
    inventory = {
        int(item["slot"]): item
        for item in case["model_visible_input"]["public_artifact_inventory"]
    }
    references = []
    for target, relations in response["unresolved_targets"].items():
        slot = int(target[1:])
        symbols = inventory[slot]["exported_symbols"]
        if len(symbols) != 1:
            raise ScoringV13Error(f"legal target {target} lacks exactly one symbol")
        symbol = str(symbols[0])
        for relation_slot, present in relations.items():
            if not present:
                continue
            category = _relation_category_for_slot(case, relation_slot)
            references.append(
                SemanticReference(symbol, RELATION_TAG_BY_CATEGORY[category])
            )
    return SemanticObservation(
        tuple(
            name
            for slot, name in _fact_slots(case).items()
            if response["facts"][slot]
        ),
        (),
        effects,
        tuple(references),
        (),
    )


def _fact_slots(case: Mapping[str, object]) -> dict[str, str]:
    schema = case["response_schema"]["properties"]["facts"]["properties"]
    return {str(slot): str(slot) for slot in schema}


def _relation_category_for_slot(case: Mapping[str, object], relation_slot: str) -> str:
    relation_properties = next(
        iter(
            case["response_schema"]["properties"]["unresolved_targets"]["properties"].values()
        )
    )["properties"]
    del relation_properties
    mapping = {
        "r0": "ownership",
        "r1": "membership",
        "r2": "role",
        "r3": "context",
        "r4": "general_dependency",
    }
    if relation_slot not in mapping:
        raise ScoringV13Error(f"unknown relation slot: {relation_slot}")
    return mapping[relation_slot]


def oracle_response_from_annotation(annotation: Mapping[str, object]) -> dict:
    return {
        "facts": {
            slot: bool(item["value"]) for slot, item in annotation["facts"].items()
        },
        "candidate_effects": {
            slot: str(item["value"])
            for slot, item in annotation["candidate_effects"].items()
        },
        "unresolved_targets": {
            target: {
                slot: bool(value["value"]) for slot, value in relations.items()
            }
            for target, relations in annotation["unresolved_targets"].items()
        },
    }


def action_diagnostic(
    case: Mapping[str, object],
    response: Mapping[str, object],
    restricted_case: Mapping[str, object],
    *,
    contract: Mapping[str, object],
) -> dict:
    """Call the unchanged estimator from an empty normal state and one response."""

    assert_frozen_estimator()
    legal = tuple(int(item) for item in case["runner_control"]["legal_target_slots"])
    parsed = parse_response(response, contract, legal)
    candidates = adapter_candidates(case)
    inventory = adapter_inventory(case)
    current_slot = int(case["runner_control"]["current_artifact_slot"])
    current_id = inventory[current_slot].artifact_id
    state = AuthzEpistemicState.initial(candidates)
    state = update_state(
        state, (current_id,), adapter_observation(case, parsed)
    )
    values = estimate_action_values(state, inventory, candidates)
    ordinal = {
        item.artifact_id: int(
            restricted_case["canonical_source_ordinal_by_variant_slot"][
                f"t{slot}"
            ]
        )
        for slot, item in enumerate(inventory)
        if slot != current_slot
    }
    usefulness = {
        item.artifact_id: float(
            restricted_case["usefulness_by_variant_target_slot"][f"t{slot}"]
        )
        for slot, item in enumerate(inventory)
        if slot != current_slot
    }
    ranked = sorted(
        values,
        key=lambda item: (-values[item], ordinal[item]),
    )
    if len(ranked) != len(usefulness):
        raise ScoringV13Error("adapter target legality mismatch")
    best = max(usefulness.values())
    lowest = min(usefulness.values())
    oracle_best = {
        item for item in ranked if abs(usefulness[item] - best) <= 1e-12
    }
    nondiscriminating = abs(best - lowest) <= 1e-12
    selected = ranked[0]
    regret = (
        0.0
        if nondiscriminating
        else (best - usefulness[selected]) / (best - lowest)
    )
    return {
        "values": values,
        "ranking": ranked,
        "selected": selected,
        "top1": bool(nondiscriminating or selected in oracle_best),
        "top2": bool(nondiscriminating or set(ranked[:2]) & oracle_best),
        "mean_normalized_regret": regret,
        "nondiscriminating": nondiscriminating,
        "illegal_targets": [],
    }


def aggregate_action_diagnostics(rows: list[dict]) -> dict:
    discriminating = [item for item in rows if not item["nondiscriminating"]]
    return {
        "case_count": len(rows),
        "discriminating_case_count": len(discriminating),
        "top1": _mean(float(item["top1"]) for item in discriminating),
        "top2": _mean(float(item["top2"]) for item in discriminating),
        "mean_normalized_regret": _mean(
            float(item["mean_normalized_regret"]) for item in discriminating
        ),
        "nondiscriminating_case_count": len(rows) - len(discriminating),
        "illegal_target_count": sum(len(item["illegal_targets"]) for item in rows),
    }


def _fact_set(response: Mapping[str, object]) -> set[str]:
    return {slot for slot, value in response["facts"].items() if value}


def _relation_sets(
    response: Mapping[str, object],
    gold: Mapping[str, object],
) -> tuple[set[tuple[str, str]], set[tuple[str, str]]]:
    actual = {
        (target, relation_slot)
        for target, relations in response["unresolved_targets"].items()
        for relation_slot, value in relations.items()
        if value
    }
    expected = {
        (target, relation_slot)
        for target, relations in gold["unresolved_targets"].items()
        for relation_slot, value in relations.items()
        if value
    }
    return actual, expected


def score_cases(
    public_population: Mapping[str, object],
    annotations: Mapping[str, Mapping[str, object]],
    responses: Mapping[tuple[str, int], Mapping[str, object]],
    *,
    contract: Mapping[str, object],
    source_family_by_case: Mapping[str, str] | None = None,
) -> dict:
    """Score valid responses; missing responses are counted, never imputed."""

    cases = list(public_population["cases"])
    repeats = int(public_population["repeat_count"])
    missing = 0
    invalid = 0
    fact_case_counts = []
    effect_case_counts = []
    relation_case_counts = []
    self_consistency = []
    by_variant = defaultdict(lambda: {"cases": 0, "missing": 0, "invalid": 0})
    by_family = defaultdict(lambda: {"cases": 0, "missing": 0, "invalid": 0})
    for case in cases:
        case_id = str(case["case_id"])
        annotation = annotations[case_id]
        gold = oracle_response_from_annotation(annotation)
        by_variant[str(case["variant"])]["cases"] += 1
        family = (
            str(source_family_by_case[case_id])
            if source_family_by_case is not None
            else "unreported"
        )
        by_family[family]["cases"] += 1
        responses_for_case = [
            responses.get((case_id, repeat)) for repeat in range(1, repeats + 1)
        ]
        if any(item is None for item in responses_for_case):
            missing += repeats - sum(item is not None for item in responses_for_case)
            by_variant[str(case["variant"])]["missing"] += 1
            by_family[family]["missing"] += 1
            continue
        try:
            parsed = [
                parse_response(
                    item,
                    contract,
                    tuple(case["runner_control"]["legal_target_slots"]),
                )
                for item in responses_for_case
            ]
        except Exception:
            invalid += 1
            by_variant[str(case["variant"])]["invalid"] += 1
            by_family[family]["invalid"] += 1
            continue
        fact_counts = []
        relation_counts = []
        effect_counts = []
        for response in parsed:
            actual_facts, expected_facts = _fact_set(response), _fact_set(gold)
            actual_relations, expected_relations = _relation_sets(
                response, gold
            )
            fact_counts.append(_micro_counts(actual_facts, expected_facts))
            relation_counts.append(_micro_counts(actual_relations, expected_relations))
            actual_effects = {
                (candidate_slot, str(value))
                for candidate_slot, value in response["candidate_effects"].items()
                if value in ("support", "contradict")
            }
            expected_effects = {
                (candidate_slot, str(value))
                for candidate_slot, value in gold["candidate_effects"].items()
                if value in ("support", "contradict")
            }
            effect_counts.append(
                _micro_counts(actual_effects, expected_effects)
            )
            self_consistency.append(
                effect_from_facts(
                    contract,
                    list(case["model_visible_input"]["candidate_hypotheses"]),
                    response["facts"],
                )
                == response["candidate_effects"]
            )
        fact_case_counts.append(
            (
                sum(item[0] for item in fact_counts) / repeats,
                sum(item[1] for item in fact_counts) / repeats,
                sum(item[2] for item in fact_counts) / repeats,
            )
        )
        relation_case_counts.append(
            (
                sum(item[0] for item in relation_counts) / repeats,
                sum(item[1] for item in relation_counts) / repeats,
                sum(item[2] for item in relation_counts) / repeats,
            )
        )
        effect_case_counts.append(
            (
                sum(item[0] for item in effect_counts) / repeats,
                sum(item[1] for item in effect_counts) / repeats,
                sum(item[2] for item in effect_counts) / repeats,
            )
        )
    facts = _metric(tuple(fact_case_counts))
    relations = _metric(tuple(relation_case_counts))
    effects = _metric(tuple(effect_case_counts))
    observed = {
        **facts,
        "relation_precision": relations["precision"],
        "relation_recall": relations["recall"],
        "directional_effect_precision": effects["precision"],
        "directional_effect_recall": effects["recall"],
        "effect_self_consistency": _mean(float(item) for item in self_consistency),
        "missing_case_count": missing,
        "invalid_case_count": invalid,
        "case_count": len(cases),
        "by_variant": {
            key: dict(value) for key, value in sorted(by_variant.items())
        },
        "by_family": {
            key: dict(value) for key, value in sorted(by_family.items())
        },
    }
    return {
        "schema_version": 1,
        "experiment": "authzgym-semantic-contract-v1.3-scoring",
        "population_hash": public_population.get("population_hash"),
        "facts": facts,
        "relations": relations,
        "directional_effects": effects,
        "effect_metrics_are_non_independent": True,
        "effect_non_independence_note": (
            "Directional effect metrics are derived interface diagnostics from "
            "fact semantics and are not a second independent capability signal."
        ),
        "observed": observed,
        "thresholds": dict(SEMANTIC_THRESHOLDS),
    }


def classify_validity(
    layer_status: Mapping[str, bool],
) -> dict:
    """Apply the preregistered validity precedence without promoting later layers."""

    first_failure = None
    for layer in VALIDITY_LAYERS:
        if layer not in layer_status:
            first_failure = layer
            break
        if not layer_status[layer]:
            first_failure = layer
            break
    if first_failure is None:
        classification = "valid"
    elif first_failure in ("semantic_interface", "downstream"):
        classification = "contract_unstable"
    else:
        classification = "invalid"
    return {
        "first_failure": first_failure,
        "classification": classification,
        "layers": {
            layer: bool(layer_status.get(layer, False))
            for layer in VALIDITY_LAYERS
        },
    }
