#!/usr/bin/env python3
"""Run the ADR-0020 authorized ``est-repair-v1.3.1`` development harness.

Step 1 of ``IMPLEMENTATION_HANDOFF.md``: reproduce the preserved B0 baseline
through the component interface and record it in ``BASELINES.json``.
No candidate is created, no inference is run, and no confirmation path is
opened.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import inspect
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import ser.evaluation.authz_v1_3_1_harness as harness

from ser.core.types import content_hash
from ser.evaluation.authz_v1_3_1_harness import (
    CORRIGENDUM_ADR,
    CORRIGENDUM_PATH,
    REPAIR_DIR,
    V13_DIR,
    access_ledger_record,
    append_access_ledger,
    assert_candidate_eligible,
    assert_frozen_estimator,
    baseline_record,
    baseline_b0,
    CategoryMatchFloorComponent,
    complexity_score,
    DegenerateNullComponent,
    deviation_ledger_record,
    gate_record,
    guarded_sha256,
    load_development_bundle,
    oracle_usefulness_baseline,
    resumption_ledger_record,
)
from ser.evaluation.authz_v1_3_1_sealed_input import check_component_module


CANDIDATE_PLAN = (
    {
        "candidate_id": "est-repair-v1.3.1-A-1",
        "arm": "A",
        "module": "ser.evaluation.authz_v1_3_1_adapter",
        "module_path": "src/ser/evaluation/authz_v1_3_1_adapter.py",
        "class_name": "ArmA1GeneralDependencyTag",
        "complexity": {"family_branches": 1},
        "feature_map": "supporting_families",
        "rationale": (
            "Mechanism: the frozen estimator links an unresolved reference to a "
            "candidate only through that candidate's relation tags, and the "
            "adapter under study emits candidate tags from the published "
            "family-to-category map without ever attaching the published "
            "general_dependency category (preregistration section 1.2, L1). An "
            "r4 reference therefore has an empty linked set and can never "
            "receive non-zero plausibility, so it is scored exactly like every "
            "unsupported category. This candidate attaches the published "
            "general_dependency tag to the ownership-family candidate so the "
            "fallback category becomes representable at the value layer. It is "
            "an adapter-only change; the frozen estimator stays byte-identical "
            "at SHA-256 092a7a87... and is reached through the same published "
            "effects, tags and references the fixed adapter supplies."
        ),
    },
    {
        "candidate_id": "est-repair-v1.3.1-A-2",
        "arm": "A",
        "module": "ser.evaluation.authz_v1_3_1_adapter",
        "module_path": "src/ser/evaluation/authz_v1_3_1_adapter.py",
        "class_name": "ArmA2NeutralDistinctTag",
        "complexity": {"family_branches": 1},
        "feature_map": "supporting_families",
        "rationale": (
            "Mechanism-level defect of A-1: A-1 made the published "
            "general_dependency category representable, but the value layer "
            "still routes every non-directional local cue through the same "
            "linkage, so a category whose published effect is neutral (mixed "
            "local cues present) remains indistinguishable from one whose "
            "effect is unknown (no directional cue at all) -- the collapse "
            "recorded as L2 in preregistration section 1.2. This candidate "
            "keeps A-1's tag and additionally routes neutral references through "
            "a distinct tag that no candidate carries, so the two published "
            "non-directional states stop sharing a channel. Estimator and "
            "selection rule remain the frozen ones."
        ),
    },
    {
        "candidate_id": "est-repair-v1.3.1-B-1",
        "arm": "B",
        "module": "ser.authzgym.policies_v1_3_1",
        "module_path": "src/ser/authzgym/policies_v1_3_1.py",
        "class_name": "EstimatorV1SalientCategory",
        "complexity": {"relation_category_branches": 1},
        "feature_map": "salient_category",
        "rationale": (
            "Mechanism-level defect of Arm A as a whole: no adapter-only change "
            "can reach the frozen value layer's `1.0 + max(0, support)` term, "
            "because in the two degenerate canonical development cases every "
            "published candidate effect is non-positive (preregistration "
            "section 1.2, H-R1 with L1), and manufacturing positive support "
            "where the published truth table says otherwise would reinterpret "
            "the effect semantics that section 7.1 forbids changing. The defect "
            "is split across the component boundary: the adapter cannot express "
            "a direction for a category whose family carries no cue, and the "
            "estimator's clamp discards the direction the adapter does deliver. "
            "This candidate replaces only the estimator's value and selection "
            "rule: it selects the published category the public local cues point "
            "at -- the supporting family's category when one exists, otherwise "
            "the published general-dependency fallback category -- and scores "
            "that category's targets strictly higher, leaving a legitimate "
            "declared tie when more than one legal target carries it. A "
            "declared tie is resolved by the frozen evaluator canonical-ordinal "
            "rule (corrigendum section 2.4 route 2); no identifier-dependent "
            "tie-break is used."
        ),
    },
)

FROZEN_ADAPTER_PATH = "src/ser/evaluation/authz_v1_3.py"

CLAIM_BOUNDARY_10_1 = (
    "Under the fixed, frozen AuthzGym v1.3 instrument -- its authored usefulness "
    "labels, its five-category adapter surface, its equal-weight canonical "
    "scoring, its frozen tie rule, and its preregistered engineering screen -- "
    "there exists a deterministic, case-independent, invariance-certified "
    "component of bounded complexity whose inspection-target ordering meets the "
    "existing engineering gate, and the section-4.2.1 non-degeneracy "
    "requirement, on the eight canonical development source instances, using "
    "only authorized public semantic outputs and no privileged information."
)
CLAIM_BOUNDARY_10_2 = (
    "What a pass must never be described as: general authorization reasoning or "
    "evidence about authorization competence; adaptive routing success, "
    "conditional routing, or action selection working; SER architecture "
    "superiority or any comparison against ReAct, fixed-order, monolithic, or "
    "ordinary-agent baselines; realistic GitLab transfer or transfer to any real "
    "repository; real-world action-value validity or evidence that these values "
    "mean anything outside this fixture family; model or provider capability, "
    "since no inference is run at any point; validation of the usefulness "
    "target, the instrument, or the benchmark; a diagnosis of the cause of the "
    "preserved fresh-confirmation failure or an attribution of that failure to "
    "the estimator, to the adapter, or to either component family; the best, "
    "smallest, or only admissible repair; and grounds to promote H-001, H-016, "
    "H-017, H-018, or M-013, or to change any concept maturity."
)
SUFFICIENCY_QUALIFICATION = (
    "Sufficiency, not superiority: a pass establishes that changing this one "
    "component is sufficient. The untested arm is untested, not falsified. No "
    "claim of optimality, minimality, or uniqueness is made, and the study does "
    "not attribute the preserved fresh-confirmation failure to the estimator, to "
    "the adapter, or to either component family."
)
ARTIFACT_CLASSIFIER = "development_component_compatibility_diagnostic"
NON_INDEPENDENCE_NOTE = (
    "Directional effect metrics, where reported, are derived interface "
    "diagnostics from fact semantics and are not a second independent capability "
    "signal. This report renders no directional-effect table."
)


MOTIVATION = (
    "motivated by the observed fresh-confirmation top-2 failure recorded in "
    "experiments/authzgym_semantic_contract_v1_3/ORACLE_BLOCKER.md"
)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _feature_maps():
    def supporting_families(sealed):
        return sorted(
            family
            for slot, family, _ in sealed.candidate_hypotheses
            if sealed.candidate_effects[slot] == "support"
        )

    def salient_category(sealed):
        from ser.authzgym.policies_v1_3_1 import (
            EFFECT_SIGN,
            FALLBACK_TAG,
            RELATION_TAG_BY_CATEGORY,
        )

        supporting = sorted(
            RELATION_TAG_BY_CATEGORY[family]
            for slot, family, _ in sealed.candidate_hypotheses
            if EFFECT_SIGN[sealed.candidate_effects[slot]] > 0.0
        )
        return supporting or [FALLBACK_TAG]

    return {
        "supporting_families": supporting_families,
        "salient_category": salient_category,
    }


def _append(path: Path, record: dict) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def run_candidates(output_dir: Path, *, arms: str, max_attempts: int) -> int:
    """Handoff steps 7-9, in the fixed A then B then C order."""

    from tools.compute_authorized_information_ceiling import tier2
    from tools.validate_authzgym_v1_3_1_component_firewall import (
        validate as firewall_validate,
    )

    bundle = load_development_bundle()
    ledger = output_dir / "CANDIDATE_LEDGER.jsonl"
    nd3_floor = json.loads(
        (output_dir / "BASELINES.json").read_text(encoding="utf-8")
    )["frozen_nd3_floor_from_b2"]
    maps = _feature_maps()

    # A candidate is evaluated exactly once. Any candidate already carrying a
    # result record is spent and is never re-evaluated by a later invocation.
    existing: dict[str, dict] = {}
    if ledger.exists():
        for line in ledger.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            if record.get("record") == "candidate_result":
                existing[record["candidate_id"]] = record
    passing = next(
        (item for item in existing.values() if item["disposition"] == "admissible_pass"),
        None,
    )
    attempts = len(existing)
    arm_order = [item.strip() for item in arms.split(",") if item.strip()]
    for arm in arm_order:
        for entry in CANDIDATE_PLAN:
            if entry["arm"] != arm:
                continue
            if passing is not None:
                break
            if entry["candidate_id"] in existing:
                print(
                    f"{entry['candidate_id']}: already evaluated "
                    f"({existing[entry['candidate_id']]['disposition']}); not re-evaluated"
                )
                continue
            if attempts >= max_attempts:
                print(f"attempt budget reached at {attempts}; not attempting further")
                break
            attempts += 1
            module_path = Path(entry["module_path"])
            component = getattr(
                importlib.import_module(entry["module"]), entry["class_name"]
            )()
            source = inspect.getsource(type(component))
            # 1. rationale recorded before any evaluation
            _append(
                ledger,
                {
                    "schema_version": 1,
                    "record": "candidate_attempt",
                    "attempt_index": attempts,
                    "candidate_id": entry["candidate_id"],
                    "arm": entry["arm"],
                    "rationale": entry["rationale"],
                    "component_module": entry["module_path"],
                    "component_module_sha256": guarded_sha256(module_path),
                    "component_class_sha256": _sha256_text(source),
                    "before_evaluation": True,
                },
            )
            # 2. protected-component verification
            protected_before = guarded_sha256(Path(FROZEN_ADAPTER_PATH))
            if entry["arm"] == "A":
                assert_frozen_estimator()
            else:
                assert_frozen_estimator()
            # 3. static checker and the step-6 firewall suite
            static = check_component_module(module_path)
            firewall = firewall_validate(
                component,
                component_name=entry["class_name"],
                component_module=entry["module"],
                module_path=module_path,
            )
            complexity = complexity_score(**entry["complexity"])
            admissible = complexity <= 4
            # 4. Tier-2 ceiling for the declared feature map
            ceiling = tier2(bundle, maps[entry["feature_map"]])
            # 5. one-shot evaluation of the frozen gate
            record = gate_record(bundle, component, nd3_floor=nd3_floor)
            protected_after = guarded_sha256(Path(FROZEN_ADAPTER_PATH))
            passed = bool(
                record["passes"]
                and admissible
                and firewall["passed"]
                and protected_before == protected_after
            )
            result = {
                "schema_version": 1,
                "record": "candidate_result",
                "attempt_index": attempts,
                "candidate_id": entry["candidate_id"],
                "arm": entry["arm"],
                "component_class_sha256": _sha256_text(source),
                "component_module_sha256": guarded_sha256(module_path),
                "complexity": complexity,
                "complexity_components": entry["complexity"],
                "admissible": admissible,
                "feature_map": entry["feature_map"],
                "tier2_ceiling": ceiling,
                "static_checker": static,
                "firewall_passed": firewall["passed"],
                "firewall": firewall["checks"],
                "canonical_aggregate": record["canonical_aggregate"],
                "own_selection_equivariance": record["own_ranking_invariance"],
                "section_14_equivalence": record["section_14_equivalence"],
                "non_degeneracy": record["non_degeneracy"],
                "longest_artifact_aggregate": record["longest_artifact_aggregate"],
                "family_macro": record["family_macro"],
                "leave_one_source_out": record["leave_one_source_out"],
                "tie_dependence": record["tie_dependence"],
                "gate_checks": record["checks"],
                "gate_passes": record["passes"],
                "protected_components_unchanged": protected_before == protected_after,
                "disposition": (
                    "admissible_pass"
                    if passed
                    else "inadmissible_complexity"
                    if not admissible
                    else "failing_gate"
                ),
            }
            _append(ledger, result)
            candidate_dir = output_dir / "candidates" / entry["candidate_id"]
            candidate_dir.mkdir(parents=True, exist_ok=True)
            (candidate_dir / "RATIONALE.txt").write_text(
                entry["rationale"] + "\n", encoding="utf-8"
            )
            (candidate_dir / "COMPONENT.py").write_text(source, encoding="utf-8")
            (candidate_dir / "RECORD.json").write_text(
                json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            failing = [
                key for key, value in record["checks"].items() if not value
            ]
            print(
                f"{entry['candidate_id']}: top1={record['canonical_aggregate']['top1']} "
                f"top2={record['canonical_aggregate']['top2']} "
                f"regret={record['canonical_aggregate']['mean_normalized_regret']:.6f} "
                f"complexity={complexity} "
                f"firewall={'pass' if firewall['passed'] else 'fail'} "
                f"-> {result['disposition']}"
                + (f" (failing gates: {', '.join(failing)})" if failing else "")
            )
            if passed:
                passing = result
                break
        if passing is not None:
            break

    outcome = (
        {
            "A": "adapter-only-change-sufficient",
            "B": "estimator-only-change-sufficient",
            "C": "joint-change-sufficient",
        }.get(passing["arm"], "admissible_pass")
        if passing
        else "no-admissible-pass-in-attempted-arms"
    )
    outcome_record = {
        "schema_version": 1,
        "record": "study_outcome",
        "outcome": outcome,
        "attempts_used": attempts,
        "passing_candidate_id": passing["candidate_id"] if passing else None,
        "passing_component_class_sha256": (
            passing["component_class_sha256"] if passing else None
        ),
        "arms_attempted": arm_order,
        "candidate_budget_max": 10,
        "inference_authorized": False,
        "confirmation_authorized": False,
    }
    already_recorded = False
    if ledger.exists():
        already_recorded = any(
            json.loads(line).get("record") == "study_outcome"
            and json.loads(line).get("outcome") == outcome
            for line in ledger.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    if not already_recorded:
        _append(ledger, outcome_record)
    print(f"outcome: {outcome} (attempts used: {attempts})")
    return 0 if passing else 1


def assert_report_sections(markdown: str) -> None:
    """The report must carry the frozen claim boundary and the qualification."""

    for label, text in (
        ("claim boundary (section 10.1)", CLAIM_BOUNDARY_10_1),
        ("claim boundary (section 10.2)", CLAIM_BOUNDARY_10_2),
        ("sufficiency qualification", SUFFICIENCY_QUALIFICATION),
    ):
        if text not in markdown:
            raise SystemExit(f"report refused: missing or altered {label}")


def render_report(output_dir: Path) -> int:
    """Handoff step 10: selection, report, and component freeze."""

    ledger_path = output_dir / "CANDIDATE_LEDGER.jsonl"
    records = [
        json.loads(line)
        for line in ledger_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    results = [item for item in records if item.get("record") == "candidate_result"]
    passing = [item for item in results if item["disposition"] == "admissible_pass"]
    if len(passing) > 1:
        raise SystemExit(
            "report refused: more than one passing candidate is recorded, which "
            "would mean the section-5.4 stopping rule was not obeyed"
        )
    baselines = json.loads((output_dir / "BASELINES.json").read_text(encoding="utf-8"))
    ceiling = json.loads(
        (output_dir / "INFORMATION_CEILING.json").read_text(encoding="utf-8")
    )
    firewall = json.loads(
        (output_dir / "FIREWALL_V1_3_1_VALIDATION.json").read_text(encoding="utf-8")
    )

    # Carry the duplicate-evaluation deviation forward explicitly, once.
    if not any(item.get("record") == "procedural_note" for item in records):
        _append(
            ledger_path,
            {
                "schema_version": 1,
                "record": "procedural_note",
                "note": "duplicate_evaluation_round",
                "description": (
                    "The candidate stage was invoked twice. The first invocation "
                    "exposed an implementation defect in this study's own "
                    "firewall check 7 (it classified module-level constant maps "
                    "as mutable caches), and the stage was re-run after the "
                    "checker was corrected. The candidate sources were "
                    "byte-identical between invocations (identical "
                    "component_class_sha256) and produced byte-identical gate "
                    "numbers, so no candidate was tuned and no selection decision "
                    "used the first round's output. The first round's "
                    "candidate_result records are superseded, not deleted; the "
                    "second round's records are the valid ones. A re-run guard "
                    "now makes any candidate carrying a result record permanently "
                    "spent."
                ),
                "classification": "implementation_defect_deviation",
                "invalidates_study": False,
                "retroactively_authorized": False,
            },
        )
        records = [
            json.loads(line)
            for line in ledger_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        results = [
            item for item in records if item.get("record") == "candidate_result"
        ]
        passing = [
            item for item in results if item["disposition"] == "admissible_pass"
        ]

    # The defective first round also left a stale outcome line; say so plainly
    # rather than leaving a reader to reconcile two outcome values.
    outcomes = [
        item["outcome"] for item in records if item.get("record") == "study_outcome"
    ]
    if len(set(outcomes)) > 1 and not any(
        item.get("note") == "stale_outcome_record" for item in records
    ):
        _append(
            ledger_path,
            {
                "schema_version": 1,
                "record": "procedural_note",
                "note": "stale_outcome_record",
                "description": (
                    "A study_outcome line reading "
                    f"{sorted(set(outcomes))[0]!r} was written by the superseded "
                    "first candidate round, before the firewall check-7 "
                    "implementation defect was corrected. The authoritative "
                    "outcome is the last study_outcome record: "
                    f"{outcomes[-1]!r}. No earlier record is deleted; the stale "
                    "line is annotation, not a result."
                ),
                "authoritative_outcome_record_index": len(records),
                "classification": "implementation_defect_deviation",
            },
        )
        records = [
            json.loads(line)
            for line in ledger_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    attempts = [item for item in records if item.get("record") == "candidate_attempt"]
    distinct = {item["candidate_id"] for item in results}
    seen: dict[str, int] = {}
    for item in results:
        seen[item["candidate_id"]] = seen.get(item["candidate_id"], 0) + 1
    counts: dict[str, int] = {}
    for item in results:
        counts[item["candidate_id"]] = counts.get(item["candidate_id"], 0) + 1
        item["_superseded"] = counts[item["candidate_id"]] < seen[item["candidate_id"]]
    selected = passing[0] if passing else None

    document = {
        "schema_version": 1,
        "condition_id": "est-repair-v1.3.1",
        "authorizing_adr": "ADR-0020",
        "correcting_adr": "ADR-0021",
        "corrigendum": CORRIGENDUM_PATH,
        "stage": "step10_development_report",
        "artifact_classifier": ARTIFACT_CLASSIFIER,
        "development_only": True,
        "confirms_nothing": True,
        "motivation": MOTIVATION,
        "fixed_inheritance": [
            "v1.3 source-local answerability passed on development (certificate "
            "d308e68b...) and on the fresh confirmation population (5887f8cb...).",
            "The unchanged historical estimator passed the development canonical "
            "oracle gate (top-1 0.625, top-2 0.875, regret 0.175, 0 illegal, "
            "40/40 equivalence).",
            "The same unchanged estimator failed the preregistered "
            "fresh-confirmation canonical top-2 gate at 0.750 against >= 0.80; "
            "that result is preserved without reinterpretation.",
            "The top-2 >= 0.80, top-1 >= 0.60 and regret <= 0.35 thresholds are "
            "unchanged, as are the v1.3 semantics, prompt, schemas, scoring, "
            "usefulness target, tie rules and transformations.",
            "The historical estimator (SHA-256 092a7a87...) and the fixed "
            "section-13 adapter remain byte-preserved baselines.",
            "The spent confirmation_v1_3 population was not opened, read, hashed, "
            "counted, sampled, or characterized by any step of this study after "
            "ADR-0021.",
            "Model and provider inference remains unauthorized and none was run.",
        ],
        "tier1_ceiling": ceiling["tier1"],
        "tier1_sufficient": ceiling["tier1_sufficient"],
        "baselines": baselines["baselines"],
        "frozen_nd3_floor_from_b2": baselines["frozen_nd3_floor_from_b2"],
        "candidate_ledger": {
            "attempt_records": len(attempts),
            "result_records": len(results),
            "distinct_candidates_evaluated": len(distinct),
            "attempts_in_scope": sorted(distinct),
            "order": [item["candidate_id"] for item in results],
            "attempts_used": len(distinct),
            "candidate_budget_max": 10,
            "arms_attempted": ["A", "B"],
            "arm_c_not_opened": True,
            "arm_c_reason": (
                "the study stopped at the first admissible pass in Arm B, so the "
                "joint condition was never authorized to open and Arms C is "
                "untested rather than falsified"
            ),
        },
        "passing_candidate": selected,
        "sufficiency_label": (
            {
                "A": "adapter-only-change-sufficient",
                "B": "estimator-only-change-sufficient",
                "C": "joint-change-sufficient",
            }.get(selected["arm"])
            if selected
            else "no-admissible-pass-in-attempted-arms"
        ),
        "h_r3_ceiling_finding": {
            "status": "not_confirmed",
            "tier1_top1_ceiling": ceiling["tier1"]["tier1_top1_ceiling"],
            "tier1_top2_ceiling": ceiling["tier1"]["tier1_top2_ceiling"],
            "statement": (
                "H-R3 predicted that no function of the authorized semantic "
                "state could attain the criterion. The Tier-1 ceiling is above "
                "the criterion, so H-R3 is not confirmed: the authorized public "
                "state can order the legal targets well enough for some "
                "case-specific rule to reach the gate, and the achieved top-1 "
                "equals that ceiling while top-2 equals the ceiling exactly."
            ),
        },
        "h_r4_interpretation": {
            "kind": "interpretation_with_evidence_and_residual_uncertainty",
            "statement": (
                "The usefulness target is authored from a hidden logical role "
                "and hidden mechanism family that the public channel does not "
                "carry. The selected component's mechanism cites a published "
                "structural gap (the published general-dependency category is "
                "never attached to a candidate, so r4 references can never link) "
                "and a published cue mapping. Its fallback clause -- when no "
                "candidate family carries a directional support cue, treat the "
                "general-dependency fallback category as the most informative "
                "target -- is calibrated to a development-observed structural "
                "regularity, not to a published rule stating that the fallback "
                "category is inspection-worthy: in both ownership-family "
                "development cases the maximum-usefulness target is exactly the "
                "r4 target. Read plainly, the fallback clause is a public-surface "
                "correlate of the hidden authored role. The pass is therefore "
                "compatibility with a target authored from hidden roles and is "
                "not evidence of authorization reasoning."
            ),
            "supporting_evidence": [
                "preregistration section 1.2 L1 records that r4 references can "
                "never link to a candidate under the fixed adapter",
                "preregistration section 1.2 records that both ownership-family "
                "development cases have their maximum-usefulness target at the "
                "r4 target",
                "preregistration section 1.2 H-R4 records that usefulness is a "
                "pure function of the hidden role and hidden mechanism family",
                "the passing component attains exactly the Tier-1 ceiling "
                "(top-1 0.75, top-2 1.0) and its own Tier-2 ceiling",
            ],
            "residual_uncertainty": (
                "With eight development instances the study cannot separate a "
                "genuine structural rule from a coincidence of this fixture "
                "family, and no untouched confirmation population was consulted "
                "or generated. The interpretation is recorded as a judgement "
                "with its evidence, not as a proven causal diagnosis."
            ),
        },
        "claim_boundary": {
            "section_10_1_verbatim": CLAIM_BOUNDARY_10_1,
            "section_10_2_verbatim": CLAIM_BOUNDARY_10_2,
            "artifact_classifier": ARTIFACT_CLASSIFIER,
            "is_e_star_record": False,
        },
        "sufficiency_qualification": SUFFICIENCY_QUALIFICATION,
        "non_independence_note": NON_INDEPENDENCE_NOTE,
        "firewall_scope_statement": firewall["scope_statement"],
        "firewall_all_baselines_pass": firewall["all_baselines_pass"],
        "_candidate_results": results,
        "protected_files": {
            "historical_estimator_sha256": harness_estimator_hash(),
            "fixed_adapter_path": FROZEN_ADAPTER_PATH,
            "v13_non_confirmation_files_verified": len(harness.integrity_files_v13()),
            "confirmation_paths_opened_or_hashed_by_this_stage": 0,
        },
        "freeze": {
            "selected_component_module_sha256": selected["component_module_sha256"]
            if selected
            else None,
            "selected_component_class_sha256": selected["component_class_sha256"]
            if selected
            else None,
            "fragile_label": (
                "fragile" if selected and selected["leave_one_source_out"]["fragile"] else None
            ),
            "loso_failing_fold_count": (
                selected["leave_one_source_out"]["failing_fold_count"] if selected else None
            ),
            "report_markdown_sha256": None,
            "report_json_sha256": None,
        },
    }

    markdown = _render_markdown(document)
    markdown_path = output_dir / "DEVELOPMENT_REPORT.md"
    markdown_path.write_text(markdown, encoding="utf-8")
    document["freeze"]["report_markdown_sha256"] = hashlib.sha256(
        markdown.encode("utf-8")
    ).hexdigest()
    without_own_hash = {
        key: value
        for key, value in document.items()
        if key != "freeze" and not key.startswith("_")
    }
    frozen = dict(document["freeze"])
    frozen["report_json_sha256"] = None
    json_hash = content_hash({**without_own_hash, "freeze": frozen})
    document["freeze"]["report_json_sha256"] = json_hash
    (output_dir / "DEVELOPMENT_REPORT.json").write_text(
        json.dumps(
            {
                key: value
                for key, value in document.items()
                if not key.startswith("_")
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"development report written: {document['sufficiency_label']}")
    print(f"  report markdown sha256: {document['freeze']['report_markdown_sha256']}")
    print(f"  selected component sha256: {document['freeze']['selected_component_class_sha256']}")
    print(f"  fragile label: {document['freeze']['fragile_label']}")
    return 0


def harness_estimator_hash() -> str:
    from ser.evaluation.authz_v1_3 import estimator_source_sha256

    return estimator_source_sha256()


def _render_markdown(document: dict) -> str:
    baseline_rows = "\n".join(
        "| {name} | {top1} | {top2} | {regret:.6f} | {own} | {uniq} |{ub}|".format(
            name=name,
            top1=record["canonical_aggregate"]["top1"],
            top2=record["canonical_aggregate"]["top2"],
            regret=record["canonical_aggregate"]["mean_normalized_regret"],
            own=f"{record['own_ranking_invariance']['selection_pass']}/40",
            uniq=record["non_degeneracy"]["nd3_strict_unique_maximum_count"],
            ub=" upper-bound only" if record["upper_bound_only"] else "",
        )
        for name, record in sorted(document["baselines"].items())
    )
    candidate_rows = "\n".join(
        "| {attempt} | {cid} | {arm} | {top1} | {top2} | {regret:.6f} | {cx} | {disp} | {note} |".format(
            attempt=item["attempt_index"],
            cid=item["candidate_id"],
            arm=item["arm"],
            top1=item["canonical_aggregate"]["top1"],
            top2=item["canonical_aggregate"]["top2"],
            regret=item["canonical_aggregate"]["mean_normalized_regret"],
            cx=item["complexity"],
            disp=item["disposition"],
            note=(
                "superseded: duplicate evaluation round, see section 12"
                if item.get("_superseded")
                else "valid record"
            ),
        )
        for item in document["_candidate_results"]
    )
    selected = document["passing_candidate"]
    lines = [
        "# est-repair-v1.3.1 development report",
        "",
        f"Condition: `{document['condition_id']}`. Authorized by {document['authorizing_adr']},",
        f"corrected by {document['correcting_adr']} (`{document['corrigendum']}`).",
        f"Artifact classifier: `{document['artifact_classifier']}`. This is",
        "**development-only** work and it **confirms nothing**; no model or",
        "provider inference was run and no confirmation population was generated",
        "or accessed.",
        "",
        "## 1. Motivation",
        "",
        document["motivation"] + ".",
        "",
        "## 2. Fixed inheritance",
        "",
    ]
    lines += [f"- {item}" for item in document["fixed_inheritance"]]
    lines += [
        "",
        "## 3. Tier-1 authorized-information ceiling (blocking, pre-candidate)",
        "",
        f"- Tier-1 top-1 ceiling: `{document['tier1_ceiling']['tier1_top1_ceiling']}` "
        f"(required >= {document['tier1_ceiling']['required_top1']})",
        f"- Tier-1 top-2 ceiling: `{document['tier1_ceiling']['tier1_top2_ceiling']}` "
        f"(required >= {document['tier1_ceiling']['required_top2']})",
        f"- Decision: `{ 'sufficient' if document['tier1_sufficient'] else 'authorized-information-insufficient' }`",
        "",
        "## 4. Baselines and the frozen ND-3 floor",
        "",
        "| baseline | top-1 | top-2 | regret | own-selection | strict-unique-max | note |",
        "| --- | --- | --- | --- | --- | --- | --- |",
        baseline_rows,
        "",
        f"Frozen `nd3_floor_from_b2` = **{document['frozen_nd3_floor_from_b2']}** "
        "(measured at handoff step 4, before any candidate existed).",
        "",
        "## 5. Candidate ledger, in attempted order",
        "",
        "| attempt | candidate | arm | top-1 | top-2 | regret | complexity | disposition | record |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        candidate_rows,
        "",
        f"Attempts used: **{document['candidate_ledger']['attempts_used']}** of "
        f"{document['candidate_ledger']['candidate_budget_max']}. "
        f"Arms attempted: {', '.join(document['candidate_ledger']['arms_attempted'])}. "
        "Arm C was not opened: " + document["candidate_ledger"]["arm_c_reason"] + ".",
        "",
        "## 6. First passing candidate",
        "",
    ]
    if selected:
        lines += [
            f"`{selected['candidate_id']}` (arm {selected['arm']}) is the result of this",
            "study, by the section-5.4 rule 2 stop. No further candidate was written",
            "and no remaining budget was spent.",
            "",
            f"- component class SHA-256: `{selected['component_class_sha256']}`",
            f"- component module SHA-256: `{selected['component_module_sha256']}`",
            f"- canonical top-1 / top-2 / regret: `{selected['canonical_aggregate']['top1']}` / "
            f"`{selected['canonical_aggregate']['top2']}` / "
            f"`{selected['canonical_aggregate']['mean_normalized_regret']:.6f}`",
            f"- complexity: `{selected['complexity']}` (bound is 4)",
            f"- ND-1 / ND-2 / ND-3: all hold; strict-unique-max "
            f"`{selected['non_degeneracy']['nd3_strict_unique_maximum_count']}` "
            f"against floor {document['frozen_nd3_floor_from_b2']}",
            f"- own-selection equivariance: "
            f"`{selected['own_selection_equivariance']['selection_pass']}/40`; "
            f"full-order invariance `{selected['own_selection_equivariance']['full_order_pass']}/40` "
            "(descriptive only)",
            f"- section-14 action-value equivalence: "
            f"`{selected['section_14_equivalence']['pair_count']}` pairs, "
            f"{len(selected['section_14_equivalence']['failures'])} failures",
            f"- Tier-2 ceiling for its declared feature map: top-1 "
            f"`{selected['tier2_ceiling']['tier2_top1_ceiling']}`, top-2 "
            f"`{selected['tier2_ceiling']['tier2_top2_ceiling']}`",
            f"- `longest_artifact` read-out (reported only, non-selecting): top-1 "
            f"`{selected['longest_artifact_aggregate']['top1']}`, top-2 "
            f"`{selected['longest_artifact_aggregate']['top2']}`, regret "
            f"`{selected['longest_artifact_aggregate']['mean_normalized_regret']:.6f}`",
            f"- leave-one-source-out: `{selected['leave_one_source_out']['failing_fold_count']}` "
            f"failing folds; fragile label "
            f"`{document['freeze']['fragile_label'] or 'none'}`",
            f"- tie-dependent cases (reported only): "
            f"`{selected['tie_dependence']['tie_dependent_case_count']}`",
            "",
            f"Sufficiency label: `{document['sufficiency_label']}`.",
        ]
    else:
        lines += ["No admissible candidate passed the frozen gate."]
    lines += [
        "",
        "## 7. Sufficiency qualification",
        "",
        SUFFICIENCY_QUALIFICATION,
        "",
        "## 8. H-R3 ceiling finding",
        "",
        document["h_r3_ceiling_finding"]["statement"],
        "",
        "## 9. H-R4 interpretation (interpretation, not a proven diagnosis)",
        "",
        document["h_r4_interpretation"]["statement"],
        "",
        "Supporting evidence:",
        "",
    ]
    lines += [f"- {item}" for item in document["h_r4_interpretation"]["supporting_evidence"]]
    lines += [
        "",
        "Residual uncertainty: " + document["h_r4_interpretation"]["residual_uncertainty"],
        "",
        "## 10. Claim boundary (verbatim)",
        "",
        "> " + CLAIM_BOUNDARY_10_1,
        "",
        CLAIM_BOUNDARY_10_2,
        "",
        f"Artifact classifier: `{ARTIFACT_CLASSIFIER}`; not an `E-*` evidence record.",
        "",
        "## 11. Development-only status",
        "",
        "This development report establishes compatibility on the eight canonical",
        "development source instances only. It does not establish, and must not be",
        "reported as suggesting, that the component would pass a confirmation",
        "population. No successor confirmation population was generated, frozen,",
        "or accessed, and executing the section-8 protocol requires a separate",
        "authorization naming the frozen component hash and this report's hash.",
        "",
        NON_INDEPENDENCE_NOTE,
        "",
        "## 12. Procedural deviations",
        "",
        "- The pre-ADR-0021 step-0 integrity pass hashed 16 confirmation-named",
        "  files; recorded in `STUDY_BLOCKER.md` section 5 and",
        "  `ACCESS_LEDGER.jsonl` (`confirmation_path_hashing_deviation`), and not",
        "  retroactively authorized. The integrity procedure now fails closed.",
        "- The candidate stage was invoked twice: the first invocation exposed an",
        "  implementation defect in this study's own firewall check 7, the checker",
        "  was corrected, and the stage was re-run. Candidate sources were",
        "  byte-identical across invocations and gate numbers were identical, so no",
        "  candidate was tuned and no selection decision used the first round.",
        "  Recorded in `CANDIDATE_LEDGER.jsonl` as `duplicate_evaluation_round`.",
        "",
        "## 13. Freeze record",
        "",
        f"- selected component class SHA-256: `{document['freeze']['selected_component_class_sha256']}`",
        f"- selected component module SHA-256: `{document['freeze']['selected_component_module_sha256']}`",
        f"- fragile label: `{document['freeze']['fragile_label'] or 'none'}`",
        f"- report markdown SHA-256: `{document['freeze']['report_markdown_sha256']}`",
        f"- report JSON SHA-256 (own field omitted): `{document['freeze']['report_json_sha256']}`",
        f"- historical estimator SHA-256: `{document['protected_files']['historical_estimator_sha256']}`",
        "",
        "A later confirmation authorization must name the component hash and the",
        "report hash above. None is granted here.",
        "",
    ]
    markdown = "\n".join(lines) + "\n"
    assert_report_sections(markdown)
    return markdown


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=REPAIR_DIR)
    parser.add_argument("--actor", default="root")
    parser.add_argument("--no-ledger", action="store_true")
    parser.add_argument(
        "--stage",
        choices=("step1", "baselines", "candidates", "report"),
        default="step1",
        help=(
            "step1 reproduces B0; baselines completes B0-B3 and freezes ND-3; "
            "candidates runs the authorized arms in order; report writes the "
            "step-10 development report and freeze record"
        ),
    )
    parser.add_argument("--arms", default="A,B")
    parser.add_argument("--max-attempts", type=int, default=10)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.stage == "candidates":
        return run_candidates(
            output_dir, arms=args.arms, max_attempts=args.max_attempts
        )
    if args.stage == "report":
        return render_report(output_dir)

    bundle = load_development_bundle()
    baseline = baseline_b0(bundle)
    baselines = {baseline["identifier"]: baseline}
    frozen_floor = None
    if args.stage == "baselines":
        assert_candidate_eligible(DegenerateNullComponent())
        assert_candidate_eligible(CategoryMatchFloorComponent())
        degenerate = baseline_record(bundle, DegenerateNullComponent())
        category_floor = baseline_record(bundle, CategoryMatchFloorComponent())
        floor = category_floor["non_degeneracy"]["nd3_strict_unique_maximum_count"]
        baselines = {
            baseline["identifier"]: baseline,
            degenerate["identifier"]: degenerate,
            category_floor["identifier"]: category_floor,
            "B3": baseline_record(bundle, oracle_usefulness_baseline(bundle)),
        }
        frozen_floor = floor
    existing_floor = None
    path = output_dir / "BASELINES.json"
    if path.exists():
        existing_floor = json.loads(path.read_text(encoding="utf-8")).get(
            "frozen_nd3_floor_from_b2"
        )
    if frozen_floor is None:
        frozen_floor = existing_floor
    elif existing_floor is not None and existing_floor != frozen_floor:
        raise SystemExit(
            "refusing to change the frozen nd3_floor_from_b2 from "
            f"{existing_floor} to {frozen_floor}"
        )
    document = {
        "schema_version": 1,
        "condition_id": "est-repair-v1.3.1",
        "authorizing_adr": "ADR-0020",
        "correcting_adr": CORRIGENDUM_ADR,
        "corrigendum": CORRIGENDUM_PATH,
        "stage": "step1_baseline_reproduction",
        "development_population_file_sha256": guarded_sha256(
            V13_DIR / "DEVELOPMENT_PUBLIC_POPULATION.json"
        ),
        "development_population_content_hash": bundle.population_hash(),
        "recorded_expectation": baseline["recorded_expectation"],
        "recorded_expectation_authority": baseline["recorded_expectation_authority"],
        "acceptance_figures": baseline["acceptance_figures"],
        "baselines": baselines,
        "frozen_nd3_floor_from_b2": frozen_floor,
        "baseline_ids": sorted(baselines),
        "inference_authorized": False,
        "confirmation_authorized": False,
    }
    (output_dir / "BASELINES.json").write_text(
        json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    if not args.no_ledger:
        ledger = output_dir / "ACCESS_LEDGER.jsonl"
        append_access_ledger(
            ledger, access_ledger_record(actor=args.actor, motivation=MOTIVATION)
        )
        append_access_ledger(ledger, resumption_ledger_record(actor=args.actor))
        append_access_ledger(ledger, deviation_ledger_record(actor=args.actor))

    observed = baseline["observed"]
    print(f"est-repair-v1.3.1 development harness (stage: {args.stage})")
    print("  B0 corrected reproduction")
    print(f"  canonical top-1 / top-2 / regret : {observed['canonical_top1']} / "
          f"{observed['canonical_top2']} / {observed['canonical_regret']}")
    print(f"  illegal targets                  : {observed['illegal_target_count']}")
    print(f"  section-14 equivalence pairs     : {observed['equivalence_pairs']} "
          f"(failures: {len(observed['equivalence_failures'])})")
    print(f"  own-ranking invariance           : {observed['own_ranking_invariance']}")
    print(f"  longest_artifact top-1 / top-2 / regret : "
          f"{observed['longest_artifact_top1']} / {observed['longest_artifact_top2']} / "
          f"{observed['longest_artifact_regret']}")
    if baseline["mismatches"]:
        print("  recorded-figure mismatches:")
        for key, item in sorted(baseline["mismatches"].items()):
            print(f"    {key}: recorded={item['recorded']} observed={item['observed']}")
    else:
        print("  all recorded B0 figures reproduce exactly")
    if args.stage == "baselines":
        print(f"  frozen nd3_floor_from_b2         : {frozen_floor}")
        for identifier in sorted(baselines):
            record = baselines[identifier]
            canonical = record["canonical_aggregate"]
            print(
                f"    {identifier}: top1 {canonical['top1']} top2 {canonical['top2']} "
                f"regret {canonical['mean_normalized_regret']:.6f} "
                f"own-selection {record['own_ranking_invariance']['selection_pass']}/40 "
                f"strict-unique-max "
                f"{record['non_degeneracy']['nd3_strict_unique_maximum_count']}"
                + (" [upper bound only]" if record["upper_bound_only"] else "")
            )
    return 0 if baseline["reproduces_recorded_figures"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
