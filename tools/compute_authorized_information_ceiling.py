#!/usr/bin/env python3
"""Tier-1 authorized-information ceiling for ``est-repair-v1.3.1`` (step 3).

Within a case every allowlisted input except the per-target relation matrix is
constant across legal targets, so any authorized-state function must assign
equal value to targets with identical category vectors. The attainable rankings
are therefore exactly the orderings of the category-vector classes, with the
frozen evaluator canonical-ordinal rule ordering targets inside a class.

This tool runs before any candidate exists and consumes no budget.
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
from typing import Callable, Mapping, Sequence

from ser.evaluation.authz_v1_3_1_harness import (
    REPAIR_DIR,
    build_component_input,
    load_development_bundle,
)


TIER1_TOP1_REQUIRED = 0.60
TIER1_TOP2_REQUIRED = 0.80


def exhaustive_ceiling(
    classes: Sequence[Sequence[int]],
    usefulness: Mapping[int, float],
) -> dict:
    """Best attainable top-1/top-2 over every ordering of ``classes``.

    ``classes`` are ordered tie classes, each already sorted by ascending frozen
    canonical ordinal. Targets inside a class cannot be separated by any
    authorized-state function.
    """

    legal = [slot for group in classes for slot in group]
    if sorted(legal) != sorted(usefulness):
        raise ValueError("class structure does not cover the legal target set")
    best = max(usefulness.values())
    oracle_best = {slot for slot in legal if abs(usefulness[slot] - best) <= 1e-12}
    top1 = False
    top2 = False
    for ordering in itertools.permutations(range(len(classes))):
        ranked = [slot for index in ordering for slot in classes[index]]
        if ranked[0] in oracle_best:
            top1 = True
        if set(ranked[:2]) & oracle_best:
            top2 = True
        if top1 and top2:
            break
    return {"top1": top1, "top2": top2}


def case_classes(bundle, case, response) -> tuple[list[list[int]], dict[int, float]]:
    """Category-vector classes for one case, ordered internally by ordinal."""

    sealed = build_component_input(case, response, bundle.contract)
    case_id = str(case["case_id"])
    ordinal = {
        int(slot[1:]): int(value)
        for slot, value in bundle.restricted[case_id][
            "canonical_source_ordinal_by_variant_slot"
        ].items()
    }
    usefulness = {
        int(slot[1:]): float(value)
        for slot, value in bundle.restricted[case_id][
            "usefulness_by_variant_target_slot"
        ].items()
    }
    grouped: dict[tuple[bool, ...], list[int]] = {}
    for slot in sealed.legal_target_slots:
        grouped.setdefault(sealed.category_vector(slot), []).append(slot)
    classes = [sorted(group, key=lambda slot: ordinal[slot]) for group in grouped.values()]
    classes.sort(key=lambda group: group[0])
    return classes, usefulness


def tier1(bundle) -> dict:
    per_case = []
    top1_hits = 0
    top2_hits = 0
    for case in bundle.canonical_cases():
        case_id = str(case["case_id"])
        response = bundle.response_for(case_id)
        classes, usefulness = case_classes(bundle, case, response)
        ceiling = exhaustive_ceiling(classes, usefulness)
        best = max(usefulness.values())
        best_slots = sorted(
            slot for slot in usefulness if abs(usefulness[slot] - best) <= 1e-12
        )
        class_sizes = {
            slot: len(next(group for group in classes if slot in group))
            for slot in best_slots
        }
        top1_hits += int(ceiling["top1"])
        top2_hits += int(ceiling["top2"])
        per_case.append(
            {
                "case_id": case_id,
                "source_episode_id": str(case["source_episode_id"]),
                "source_family": str(bundle.restricted[case_id]["source_family"]),
                "class_count": len(classes),
                "class_sizes": sorted(len(group) for group in classes),
                "classes_by_ordinal": [
                    sorted(
                        int(
                            bundle.restricted[case_id][
                                "canonical_source_ordinal_by_variant_slot"
                            ][f"t{slot}"]
                        )
                        for slot in group
                    )
                    for group in classes
                ],
                "maximum_usefulness_target_count": len(best_slots),
                "class_size_of_maximum_usefulness_targets": class_sizes,
                "attainable_top1": ceiling["top1"],
                "attainable_top2": ceiling["top2"],
            }
        )
    count = len(per_case)
    return {
        "case_count": count,
        "tier1_top1_ceiling": top1_hits / count,
        "tier1_top2_ceiling": top2_hits / count,
        "required_top1": TIER1_TOP1_REQUIRED,
        "required_top2": TIER1_TOP2_REQUIRED,
        "per_case": per_case,
    }


def _signature(phi: Callable[[object], object], case, response, bundle) -> str:
    sealed = build_component_input(case, response, bundle.contract)
    classes, _ = case_classes(bundle, case, response)
    return json.dumps(
        [phi(sealed), [[int(slot) for slot in group] for group in classes]],
        sort_keys=True,
        default=str,
    )


def tier2_grouped(records: Sequence[tuple[object, Sequence[Sequence[int]], Mapping[int, float]]]) -> dict:
    """Best achievable average when one ordering must serve a signature group."""

    groups: dict[str, list] = {}
    for key, classes, usefulness in records:
        groups.setdefault(json.dumps(key, sort_keys=True, default=str), []).append(
            (list(classes), usefulness)
        )
    total = sum(len(items) for items in groups.values())
    if total == 0:
        raise ValueError("tier 2 requires at least one case")
    best_top1 = 0.0
    best_top2 = 0.0
    for items in groups.values():
        classes = items[0][0]
        best_top1_group = 0.0
        best_top2_group = 0.0
        for ordering in itertools.permutations(range(len(classes))):
            ranked = [slot for index in ordering for slot in classes[index]]
            top1 = 0
            top2 = 0
            for _, usefulness in items:
                best = max(usefulness.values())
                oracle_best = {
                    slot
                    for slot in usefulness
                    if abs(usefulness[slot] - best) <= 1e-12
                }
                top1 += int(ranked[0] in oracle_best)
                top2 += int(bool(set(ranked[:2]) & oracle_best))
            best_top1_group = max(best_top1_group, top1 / len(items))
            best_top2_group = max(best_top2_group, top2 / len(items))
        best_top1 += best_top1_group * len(items)
        best_top2 += best_top2_group * len(items)
    return {
        "signature_group_count": len(groups),
        "case_count": total,
        "tier2_top1_ceiling": best_top1 / total,
        "tier2_top2_ceiling": best_top2 / total,
    }


def tier2(bundle, phi: Callable[[object], object]) -> dict:
    """Case-independent ceiling for a declared feature map (reported per candidate)."""

    records = []
    for case in bundle.canonical_cases():
        case_id = str(case["case_id"])
        response = bundle.response_for(case_id)
        key = _signature(phi, case, response, bundle)
        classes, usefulness = case_classes(bundle, case, response)
        records.append((key, classes, usefulness))
    return tier2_grouped(records)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPAIR_DIR / "INFORMATION_CEILING.json",
    )
    args = parser.parse_args()

    bundle = load_development_bundle()
    result = tier1(bundle)
    sufficient = (
        result["tier1_top2_ceiling"] >= TIER1_TOP2_REQUIRED
        and result["tier1_top1_ceiling"] >= TIER1_TOP1_REQUIRED
    )
    document = {
        "schema_version": 1,
        "condition_id": "est-repair-v1.3.1",
        "authorizing_adr": "ADR-0020",
        "correcting_adr": "ADR-0021",
        "stage": "step3_authorized_information_ceiling",
        "tier1_definition": (
            "Blocking absolute ceiling: partition each case's legal targets into "
            "classes by identical category vector (r0..r4); any authorized-state "
            "function assigns equal value within a class, so the attainable "
            "rankings are the orderings of classes with the frozen evaluator "
            "ascending canonical-ordinal rule applied inside each class."
        ),
        "tier2_definition": (
            "Reported case-independent ceiling for a declared feature map phi: "
            "cases sharing (phi(case), class structure) must receive the same "
            "class ordering. Computed per candidate at handoff steps 7-9."
        ),
        "tier1": result,
        "tier1_sufficient": sufficient,
        "outcome": (
            "ceiling_sufficient"
            if sufficient
            else "authorized-information-insufficient"
        ),
        "candidate_budget_consumed": 0,
        "inference_authorized": False,
        "confirmation_authorized": False,
    }
    args.output.write_text(
        json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"tier1 top-1 ceiling = {result['tier1_top1_ceiling']} (required >= {TIER1_TOP1_REQUIRED})")
    print(f"tier1 top-2 ceiling = {result['tier1_top2_ceiling']} (required >= {TIER1_TOP2_REQUIRED})")
    print(f"outcome = {document['outcome']}")
    return 0 if sufficient else 1


if __name__ == "__main__":
    raise SystemExit(main())
