"""Development-only harness for the ADR-0020 ``est-repair-v1.3.1`` study.

This module implements handoff step 1. It reproduces the preserved B0
baseline, exposes the two-operation component interface, and computes every
reported diagnostic through that interface.

Nothing here modifies, subclasses, or monkey-patches the frozen estimator
(``ser.authzgym.policies``) or the fixed adapter (``ser.evaluation.authz_v1_3``);
the harness imports both for the B0 baseline exactly as the preserved oracle
validator does. No confirmation path is opened: reads fail closed.
"""

from __future__ import annotations

import json
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

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
from ser.authzgym.v1_3_contract import load_public_contract, parse_response
from ser.core.types import content_hash
from ser.evaluation.authz_v1_3 import (
    EFFECT_SIGN,
    RELATION_TAG_BY_CATEGORY,
    adapter_candidates,
    adapter_inventory,
    adapter_observation,
    aggregate_action_diagnostics,
    assert_frozen_estimator,
    oracle_response_from_annotation,
)


ROOT = Path(__file__).resolve().parents[3]
V13_DIR = ROOT / "experiments" / "authzgym_semantic_contract_v1_3"
REPAIR_DIR = ROOT / "experiments" / "authzgym_estimator_repair_v1_3_1"

CANONICAL_VARIANT = "base_entry"
READOUT_VARIANT = "longest_artifact"
EQUIVALENCE_VARIANTS = (
    "artifact_reordering",
    "symbol_renaming",
    "candidate_label_renaming",
    "artifact_identifier_variation",
    "combined_permutation",
)
CANONICAL_SOURCE_COUNT = 8

# Preserved figures recorded in preregistration section 6 for baseline B0.
# ``longest_artifact_regret`` is the figure as written in the accepted
# preregistration and handoff step 1; it is recorded here verbatim so the
# reproduction check can fail rather than silently substitute a value.
FROZEN_B0_RECORDED = {
    "canonical_top1": 0.625,
    "canonical_top2": 0.875,
    "canonical_regret": 0.175,
    "illegal_target_count": 0,
    "equivalence_pairs": 40,
    "own_ranking_invariance": "36/40",
    "longest_artifact_top1": 0.125,
    "longest_artifact_top2": 0.375,
    "longest_artifact_regret": 0.783,
}
FROZEN_GATE_ACCEPTANCE_FIGURES = (
    "canonical_top1",
    "canonical_top2",
    "canonical_regret",
    "illegal_target_count",
    "equivalence_pairs",
)

# Preregistration section 3.3: every path below is a blocking violation to open.
FORBIDDEN_CONFIRMATION_PATHS = (
    "CONFIRMATION_PUBLIC_POPULATION.json",
    "CONFIRMATION_RESTRICTED_POPULATION.json",
    "annotations/confirmation_annotations.jsonl",
    "CONFIRMATION_TRANSFORMATION_MAPS.json",
    "CONFIRMATION_SCHEDULE.json",
    "CONFIRMATION_SOURCE_MANIFEST.json",
    "CONFIRMATION_ELIGIBILITY.json",
    "CONFIRMATION_ANSWERABILITY_VALIDATION.json",
    "CONFIRMATION_ORACLE_VALIDATION.json",
    "CONFIRMATION_ORACLE_BLOCKER.md",
)
FORBIDDEN_BLOCKS = {
    "ORACLE_VALIDATION.json": ("confirmation",),
}


class HarnessError(RuntimeError):
    """The harness or a component violated a frozen study requirement."""


class ConfirmationAccessError(HarnessError):
    """A forbidden confirmation path or block was requested."""


class SelectionMetricError(HarnessError):
    """The selection-metric entry point received the wrong unit of evidence."""


def guard_path(path: Path | str) -> Path:
    """Fail closed on any confirmation path (preregistration section 3.3)."""

    candidate = Path(path)
    if "confirmation" in candidate.name.lower():
        raise ConfirmationAccessError(f"forbidden confirmation path: {candidate.name}")
    return candidate


def read_json(path: Path | str, *, block: str | None = None) -> dict:
    candidate = guard_path(path)
    if block is not None and block in FORBIDDEN_BLOCKS.get(candidate.name, ()):
        raise ConfirmationAccessError(
            f"forbidden block {block!r} in {candidate.name}"
        )
    return json.loads(candidate.read_text(encoding="utf-8"))


def read_jsonl(path: Path | str) -> dict[str, dict]:
    candidate = guard_path(path)
    return {
        item["case_id"]: item
        for item in (
            json.loads(line)
            for line in candidate.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }


def repository_commit() -> str:
    return (
        subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )


@dataclass(frozen=True)
class DevelopmentBundle:
    """The permitted development data of preregistration section 3.1."""

    contract: Mapping[str, object]
    cases: tuple[Mapping[str, object], ...]
    restricted: Mapping[str, Mapping[str, object]]
    annotations: Mapping[str, Mapping[str, object]]
    transformation_maps: Mapping[str, object]

    def case(self, case_id: str) -> Mapping[str, object]:
        for case in self.cases:
            if case["case_id"] == case_id:
                return case
        raise HarnessError(f"unknown case id: {case_id}")

    def canonical_cases(self) -> tuple[Mapping[str, object], ...]:
        return tuple(item for item in self.cases if item["variant"] == CANONICAL_VARIANT)

    def canonical_case_ids(self) -> tuple[str, ...]:
        return tuple(item["case_id"] for item in self.canonical_cases())

    def cases_for_source(self, source_episode_id: str) -> tuple[Mapping[str, object], ...]:
        return tuple(
            item for item in self.cases if item["source_episode_id"] == source_episode_id
        )

    def source_episode_ids(self) -> tuple[str, ...]:
        seen: list[str] = []
        for case in self.cases:
            if case["source_episode_id"] not in seen:
                seen.append(case["source_episode_id"])
        return tuple(seen)

    def response_for(self, case_id: str) -> dict:
        """The gold semantic response, used exactly as the frozen validator does."""

        return oracle_response_from_annotation(self.annotations[case_id])

    def population_hash(self) -> str:
        return content_hash(list(self.cases))


def load_development_bundle() -> DevelopmentBundle:
    """Load only the development artifacts named in preregistration section 3.1."""

    contract = load_public_contract(guard_path(V13_DIR / "PUBLIC_CONTRACT.json"))
    population = read_json(V13_DIR / "DEVELOPMENT_PUBLIC_POPULATION.json")
    restricted = {
        item["case_id"]: item
        for item in read_json(V13_DIR / "DEVELOPMENT_RESTRICTED_POPULATION.json")["cases"]
    }
    annotations = read_jsonl(V13_DIR / "annotations" / "development_annotations.jsonl")
    transformation_maps = read_json(V13_DIR / "DEVELOPMENT_TRANSFORMATION_MAPS.json")
    read_json(V13_DIR / "DEVELOPMENT_SCHEDULE.json")
    if len(population["cases"]) != 56:
        raise HarnessError("development population is not the frozen 56-case population")
    if set(restricted) != {item["case_id"] for item in population["cases"]}:
        raise HarnessError("restricted and public development populations disagree")
    if set(annotations) != set(restricted):
        raise HarnessError("development annotations do not cover the population")
    return DevelopmentBundle(
        contract=contract,
        cases=tuple(population["cases"]),
        restricted=restricted,
        annotations=annotations,
        transformation_maps=transformation_maps,
    )


@dataclass(frozen=True)
class ComponentInput:
    """The seven allowlisted items of preregistration section 2.4.

    Step 2 replaces this provisional container with an attribute-enforcing
    sealed object; the exposed fields are deliberately identical.
    """

    facts: Mapping[str, bool]
    candidate_effects: Mapping[str, str]
    unresolved_targets: Mapping[int, tuple[bool, bool, bool, bool, bool]]
    candidate_hypotheses: tuple[tuple[str, str, str], ...]
    contract_constants: Mapping[str, object]
    legal_target_slots: tuple[int, ...]
    current_artifact_slot: int

    @property
    def legal_target_count(self) -> int:
        return len(self.legal_target_slots)

    def category_vector(self, slot: int) -> tuple[bool, bool, bool, bool, bool]:
        return self.unresolved_targets[slot]


def build_component_input(
    case: Mapping[str, object],
    response: Mapping[str, object],
    contract: Mapping[str, object],
) -> ComponentInput:
    legal = tuple(int(item) for item in case["runner_control"]["legal_target_slots"])
    parsed = parse_response(response, contract, legal)
    targets = {
        slot: tuple(bool(parsed["unresolved_targets"][f"t{slot}"][f"r{index}"]) for index in range(5))
        for slot in legal
    }
    return ComponentInput(
        facts={slot: bool(value) for slot, value in parsed["facts"].items()},
        candidate_effects={slot: str(value) for slot, value in parsed["candidate_effects"].items()},
        unresolved_targets=targets,
        candidate_hypotheses=tuple(
            (str(item["slot"]), str(item["effect_family"]), str(item["description"]))
            for item in case["model_visible_input"]["candidate_hypotheses"]
        ),
        contract_constants={
            "fact_slots": contract["fact_slots"],
            "effect_support_cues": contract["effect_support_cues"],
            "effect_counter_cues": contract["effect_counter_cues"],
            "effect_values": contract["effect_values"],
            "relation_slots": contract["relation_slots"],
            "relation_precedence": contract["relation_precedence"],
            "candidate_slots": contract["candidate_slots"],
        },
        legal_target_slots=legal,
        current_artifact_slot=int(case["runner_control"]["current_artifact_slot"]),
    )


class Component:
    """Two operations only (handoff step 1)."""

    name = "component"
    identifier = "component"

    def values(self, sealed: ComponentInput) -> dict[int, float]:  # pragma: no cover
        raise NotImplementedError

    def declared_ties(self, sealed: ComponentInput) -> list[list[int]]:  # pragma: no cover
        raise NotImplementedError

    # Own ordering used by the section-2.6 check. Candidate components must
    # derive it from ``sealed`` alone; B0's preserved identifier tie-break is
    # supplied by the harness as a recorded property of the baseline.
    def own_order(self, sealed: ComponentInput, case: Mapping[str, object]) -> list[list[int]]:
        groups = self.declared_ties(sealed)
        return [list(group) for group in groups]


def _surrogate_inventory(sealed: ComponentInput) -> tuple[ArtifactDescriptor, ...]:
    slots = (sealed.current_artifact_slot,) + tuple(sealed.legal_target_slots)
    return tuple(
        ArtifactDescriptor(f"t{slot}", f"t{slot}", (f"t{slot}",), 0) for slot in slots
    )


def _surrogate_candidates(sealed: ComponentInput) -> tuple[CandidateHypothesis, ...]:
    return tuple(
        CandidateHypothesis(
            slot,
            description,
            (RELATION_TAG_BY_CATEGORY[family],),
        )
        for slot, family, description in sealed.candidate_hypotheses
    )


def _surrogate_observation(
    sealed: ComponentInput, candidates: tuple[CandidateHypothesis, ...]
) -> SemanticObservation:
    effects = tuple(
        (
            candidate.hypothesis_id,
            EFFECT_SIGN[sealed.candidate_effects[candidate.hypothesis_id]],
        )
        for candidate in candidates
    )
    references = tuple(
        SemanticReference(f"t{slot}", RELATION_TAG_BY_CATEGORY[relation])
        for slot, vector in sorted(sealed.unresolved_targets.items())
        for index, present in enumerate(vector)
        if present
        for relation in (sealed.contract_constants["relation_slots"][f"r{index}"],)
    )
    return SemanticObservation((), (), effects, references, ())


class HistoricalEstimatorComponent(Component):
    """B0: the unchanged frozen estimator, addressed through the sealed input."""

    name = "B0_preserved_historical_baseline"
    identifier = "B0"

    def values(self, sealed: ComponentInput) -> dict[int, float]:
        # The frozen estimator ranks by *public inventory id* in the preserved
        # adapter. Symbol spelling is addressing-only (preregistration section
        # 2.5), so the harness supplies a slot-addressed surrogate inventory and
        # compares the result against the preserved diagnostic in the tests.
        candidates = _surrogate_candidates(sealed)
        inventory = _surrogate_inventory(sealed)
        state = AuthzEpistemicState.initial(candidates)
        state = update_state(
            state,
            (f"t{sealed.current_artifact_slot}",),
            _surrogate_observation(sealed, candidates),
        )
        return {
            int(artifact_id[1:]): float(value)
            for artifact_id, value in estimate_action_values(
                state, inventory, candidates
            ).items()
        }

    def own_order(
        self, sealed: ComponentInput, case: Mapping[str, object]
    ) -> list[list[int]]:
        # Recorded property of the preserved baseline: its own selection uses
        # ``max(values, key=lambda item: (values[item], item))`` over real
        # artifact ids (preregistration section 2.6), which is exactly the
        # identifier-dependent tie-break the new check measures.
        values = self.values(sealed)
        by_slot = _slot_to_artifact_id(case)
        # ``max(values, key=lambda item: (values[item], item))`` of the frozen
        # selector returns the lexicographically *greatest* artifact id among
        # equal values; reproduce that convention exactly.
        by_identifier = sorted(values, key=lambda slot: by_slot[slot], reverse=True)
        ordered = sorted(by_identifier, key=lambda slot: -values[slot])
        return [[slot] for slot in ordered]

    def declared_ties(self, sealed: ComponentInput) -> list[list[int]]:
        values = self.values(sealed)
        return [
            [slot]
            for slot in sorted(values, key=lambda slot: (-values[slot], slot))
        ]


class DegenerateNullComponent(Component):
    """B1: identical value for every legal target."""

    name = "B1_degenerate_null"
    identifier = "B1"

    def values(self, sealed: ComponentInput) -> dict[int, float]:
        return {slot: 0.0 for slot in sealed.legal_target_slots}

    def declared_ties(self, sealed: ComponentInput) -> list[list[int]]:
        return [list(sealed.legal_target_slots)]


class CategoryMatchFloorComponent(Component):
    """B2: the smallest deterministic rule expressible from the sealed input."""

    name = "B2_category_match_floor"
    identifier = "B2"

    def values(self, sealed: ComponentInput) -> dict[int, float]:
        supporting_categories = {
            family
            for slot, family, _ in sealed.candidate_hypotheses
            if sealed.candidate_effects[slot] == "support"
        }
        indices = {
            str(relation): index
            for index, relation in enumerate(
                sorted(sealed.contract_constants["relation_slots"], key=lambda r: int(r[1:]))
            )
        }
        values = {}
        for slot in sealed.legal_target_slots:
            vector = sealed.category_vector(slot)
            matched = any(
                vector[indices[relation]]
                for relation in supporting_categories
                if relation in indices
            )
            values[slot] = 1.0 if matched else 0.0
        return values

    def declared_ties(self, sealed: ComponentInput) -> list[list[int]]:
        values = self.values(sealed)
        groups: list[list[int]] = []
        for level in (1.0, 0.0):
            group = [slot for slot in sealed.legal_target_slots if values[slot] == level]
            if group:
                groups.append(group)
        return groups


class OracleUsefulnessComponent(Component):
    """B3: evaluator-channel upper bound. Never a candidate."""

    name = "B3_oracle_usefulness_upper_bound"
    identifier = "B3"
    upper_bound_only = True

    def __init__(self, usefulness_by_case: Mapping[str, Mapping[str, float]]) -> None:
        self._usefulness = usefulness_by_case
        self._case_id = ""

    def for_case(self, case_id: str) -> "OracleUsefulnessComponent":
        clone = OracleUsefulnessComponent(self._usefulness)
        clone._case_id = case_id
        return clone

    def values(self, sealed: ComponentInput) -> dict[int, float]:
        usefulness = self._usefulness[self._case_id]
        return {
            slot: float(usefulness[f"t{slot}"]) for slot in sealed.legal_target_slots
        }

    def declared_ties(self, sealed: ComponentInput) -> list[list[int]]:
        values = self.values(sealed)
        levels = sorted({values[slot] for slot in sealed.legal_target_slots}, reverse=True)
        return [
            [slot for slot in sealed.legal_target_slots if values[slot] == level]
            for level in levels
        ]


def _slot_to_artifact_id(case: Mapping[str, object]) -> dict[int, str]:
    return {
        int(item["slot"]): str(item["public_id"])
        for item in case["model_visible_input"]["public_artifact_inventory"]
    }


def _ordinal_by_slot(
    bundle: DevelopmentBundle, case_id: str
) -> dict[int, int]:
    case = bundle.case(case_id)
    mapping = bundle.restricted[case_id]["transformation_maps"][
        "canonical_ordinal_by_variant_public_id"
    ]
    return {
        slot: int(mapping[artifact_id])
        for slot, artifact_id in _slot_to_artifact_id(case).items()
    }


def _usefulness_by_slot(bundle: DevelopmentBundle, case_id: str) -> dict[int, float]:
    raw = bundle.restricted[case_id]["usefulness_by_variant_target_slot"]
    return {int(slot[1:]): float(value) for slot, value in raw.items()}


def diagnostic_for_case(
    bundle: DevelopmentBundle,
    case: Mapping[str, object],
    values: Mapping[int, float],
    *,
    component: Component,
) -> dict:
    """Score one case under the frozen section-13 rules."""

    case_id = str(case["case_id"])
    legal = tuple(int(item) for item in case["runner_control"]["legal_target_slots"])
    if set(values) != set(legal):
        raise HarnessError(
            f"{component.identifier}: target set is not the legal uninspected set for {case_id}"
        )
    for slot, value in values.items():
        if not isinstance(value, float) or not math.isfinite(value):
            raise HarnessError(f"{component.identifier}: non-finite value at target {slot}")
    usefulness = _usefulness_by_slot(bundle, case_id)
    ordinal = bundle.restricted[case_id]["canonical_source_ordinal_by_variant_slot"]
    ranked = sorted(legal, key=lambda slot: (-values[slot], int(ordinal[f"t{slot}"])))
    best = max(usefulness[slot] for slot in legal)
    lowest = min(usefulness[slot] for slot in legal)
    oracle_best = {slot for slot in legal if abs(usefulness[slot] - best) <= 1e-12}
    nondiscriminating = abs(best - lowest) <= 1e-12
    selected = ranked[0]
    regret = (
        0.0
        if nondiscriminating
        else (best - usefulness[selected]) / (best - lowest)
    )
    return {
        "case_id": case_id,
        "slot_values": {slot: values[slot] for slot in legal},
        "ranking": ranked,
        "selected": selected,
        "top1": bool(nondiscriminating or selected in oracle_best),
        "top2": bool(nondiscriminating or set(ranked[:2]) & oracle_best),
        "mean_normalized_regret": regret,
        "nondiscriminating": nondiscriminating,
        "illegal_targets": [],
    }


def selection_cases(
    bundle: DevelopmentBundle, case_ids: Sequence[str]
) -> tuple[Mapping[str, object], ...]:
    """The selection-metric entry point (preregistration section 4.9.2)."""

    identifiers = tuple(case_ids)
    if len(identifiers) != CANONICAL_SOURCE_COUNT:
        raise SelectionMetricError(
            f"selection metrics require exactly {CANONICAL_SOURCE_COUNT} case ids, "
            f"received {len(identifiers)}"
        )
    cases = tuple(bundle.case(item) for item in identifiers)
    wrong = [str(item["case_id"]) for item in cases if item["variant"] != CANONICAL_VARIANT]
    if wrong:
        raise SelectionMetricError(
            "selection metrics admit base_entry cases only: " + ", ".join(wrong)
        )
    return cases


def _aggregate(rows: Iterable[dict]) -> dict:
    return aggregate_action_diagnostics(list(rows))


def criterion(bundle: DevelopmentBundle, component: Component) -> dict:
    """The frozen section-4.2 criterion on the 8 canonical development entries."""

    cases = selection_cases(bundle, bundle.canonical_case_ids())
    rows = []
    for case in cases:
        sealed = build_component_input(
            case, bundle.response_for(str(case["case_id"])), bundle.contract
        )
        rows.append(diagnostic_for_case(bundle, case, component.values(sealed), component=component))
    return _aggregate(rows)


def readout(bundle: DevelopmentBundle, component: Component, variant: str) -> dict:
    rows = []
    for case in bundle.cases:
        if case["variant"] != variant:
            continue
        sealed = build_component_input(
            case, bundle.response_for(str(case["case_id"])), bundle.contract
        )
        rows.append(diagnostic_for_case(bundle, case, component.values(sealed), component=component))
    return _aggregate(rows)


def family_macro(bundle: DevelopmentBundle, component: Component) -> dict[str, dict]:
    summary: dict[str, dict] = {}
    for family in sorted(
        {
            str(bundle.restricted[case_id]["source_family"])
            for case_id in bundle.canonical_case_ids()
        }
    ):
        rows = []
        for case in bundle.canonical_cases():
            case_id = str(case["case_id"])
            if str(bundle.restricted[case_id]["source_family"]) != family:
                continue
            sealed = build_component_input(case, bundle.response_for(case_id), bundle.contract)
            rows.append(
                diagnostic_for_case(bundle, case, component.values(sealed), component=component)
            )
        summary[family] = _aggregate(rows)
    return summary


def degeneracy_census(bundle: DevelopmentBundle, component: Component) -> dict:
    unique_max = 0
    unique_second = 0
    non_unique_max = 0
    non_unique_second = 0
    for case in bundle.canonical_cases():
        case_id = str(case["case_id"])
        sealed = build_component_input(case, bundle.response_for(case_id), bundle.contract)
        values = component.values(sealed)
        counts: dict[float, int] = {}
        for slot in sealed.legal_target_slots:
            counts[round(values[slot], 12)] = counts.get(round(values[slot], 12), 0) + 1
        ordered = sorted(counts.items(), key=lambda item: -item[0])
        if ordered[0][1] == 1:
            unique_max += 1
        else:
            non_unique_max += 1
        if len(ordered) > 1 and ordered[1][1] == 1:
            unique_second += 1
        elif len(ordered) > 1:
            non_unique_second += 1
    return {
        "canonical_case_count": len(bundle.canonical_cases()),
        "strict_unique_maximum_count": unique_max,
        "non_unique_maximum_count": non_unique_max,
        "strict_unique_second_count": unique_second,
        "non_unique_second_count": non_unique_second,
    }


def _mapped_order(
    bundle: DevelopmentBundle,
    case: Mapping[str, object],
    groups: Sequence[Sequence[int]],
) -> list[list[int]]:
    ordinal = _ordinal_by_slot(bundle, str(case["case_id"]))
    return [[ordinal[slot] for slot in group] for group in groups]


def own_ranking_invariance(bundle: DevelopmentBundle, component: Component) -> dict:
    """Preregistration section 2.6, in both recorded and descriptive readings."""

    selection_checks = 0
    selection_failures: list[dict] = []
    order_checks = 0
    order_failures: list[dict] = []
    for source in bundle.source_episode_ids():
        cases = bundle.cases_for_source(source)
        base = next(item for item in cases if item["variant"] == CANONICAL_VARIANT)
        base_sealed = build_component_input(
            base, bundle.response_for(str(base["case_id"])), bundle.contract
        )
        base_groups = _mapped_order(
            bundle, base, component.own_order(base_sealed, base)
        )
        for case in cases:
            if case["variant"] not in EQUIVALENCE_VARIANTS:
                continue
            sealed = build_component_input(
                case, bundle.response_for(str(case["case_id"])), bundle.contract
            )
            groups = _mapped_order(bundle, case, component.own_order(sealed, case))
            selection_checks += 1
            if set(groups[0]) != set(base_groups[0]):
                selection_failures.append(
                    {
                        "source_episode_id": source,
                        "variant": str(case["variant"]),
                        "base_first": sorted(base_groups[0]),
                        "variant_first": sorted(groups[0]),
                    }
                )
            order_checks += 1
            if [sorted(group) for group in groups] != [
                sorted(group) for group in base_groups
            ] or [len(group) for group in groups] != [len(group) for group in base_groups]:
                order_failures.append(
                    {
                        "source_episode_id": source,
                        "variant": str(case["variant"]),
                    }
                )
    return {
        "definition": (
            "own-selection invariance: the component's own first choice, mapped "
            "through canonical_ordinal_by_variant_public_id, must agree with "
            "base_entry (preregistration section 2.6; recorded B0 value 36/40)"
        ),
        "selection_pass": selection_checks - len(selection_failures),
        "selection_total": selection_checks,
        "selection_failures": selection_failures,
        "full_order_pass": order_checks - len(order_failures),
        "full_order_total": order_checks,
        "full_order_failures": order_failures,
        "full_order_is_descriptive_only": True,
    }


def section_14_equivalence(bundle: DevelopmentBundle, component: Component) -> dict:
    """The frozen transformation action-value equivalence check."""

    failures: list[str] = []
    pair_count = 0
    for source in bundle.source_episode_ids():
        cases = bundle.cases_for_source(source)
        base = next(item for item in cases if item["variant"] == CANONICAL_VARIANT)
        base_values = component.values(
            build_component_input(
                base, bundle.response_for(str(base["case_id"])), bundle.contract
            )
        )
        base_diagnostic = diagnostic_for_case(
            bundle, base, base_values, component=component
        )
        base_ordinal = _ordinal_by_slot(bundle, str(base["case_id"]))
        base_mapped = {base_ordinal[slot]: base_values[slot] for slot in base_values}
        for case in cases:
            if case["variant"] not in EQUIVALENCE_VARIANTS:
                continue
            case_id = str(case["case_id"])
            values = component.values(
                build_component_input(case, bundle.response_for(case_id), bundle.contract)
            )
            diagnostic = diagnostic_for_case(bundle, case, values, component=component)
            ordinal = _ordinal_by_slot(bundle, case_id)
            mapped = {ordinal[slot]: values[slot] for slot in values}
            pair_count += 1
            if set(mapped) != set(base_mapped):
                failures.append(f"{case_id}: target set mismatch")
                continue
            for key in sorted(base_mapped):
                if abs(base_mapped[key] - mapped[key]) > 1e-12:
                    failures.append(f"{case_id}: action value mismatch at ordinal {key}")
            if (
                bool(base_diagnostic["top1"]) != bool(diagnostic["top1"])
                or bool(base_diagnostic["top2"]) != bool(diagnostic["top2"])
                or abs(
                    base_diagnostic["mean_normalized_regret"]
                    - diagnostic["mean_normalized_regret"]
                )
                > 1e-12
            ):
                failures.append(f"{case_id}: ranking mismatch")
    return {"pair_count": pair_count, "failures": failures}


def leave_one_source_out(bundle: DevelopmentBundle, component: Component) -> dict:
    folds = {}
    for excluded in bundle.canonical_case_ids():
        rows = []
        for case in bundle.canonical_cases():
            if str(case["case_id"]) == excluded:
                continue
            sealed = build_component_input(
                case, bundle.response_for(str(case["case_id"])), bundle.contract
            )
            rows.append(
                diagnostic_for_case(bundle, case, component.values(sealed), component=component)
            )
        folds[excluded] = _aggregate(rows)
    failing = [
        case_id
        for case_id, row in folds.items()
        if row["top1"] < 0.60 or row["top2"] < 0.80 or row["mean_normalized_regret"] > 0.35
    ]
    return {
        "folds": folds,
        "failing_fold_count": len(failing),
        "failing_folds": sorted(failing),
        "fragile": len(failing) >= 3,
        "is_gate": False,
    }


def tie_dependence(bundle: DevelopmentBundle, component: Component) -> dict:
    """Per case: would dropping the frozen ordinal tie-break change top-1/top-2?"""

    dependent: list[str] = []
    for case in bundle.canonical_cases():
        case_id = str(case["case_id"])
        sealed = build_component_input(case, bundle.response_for(case_id), bundle.contract)
        values = component.values(sealed)
        usefulness = _usefulness_by_slot(bundle, case_id)
        legal = tuple(sealed.legal_target_slots)
        best = max(usefulness[slot] for slot in legal)
        oracle_best = {slot for slot in legal if abs(usefulness[slot] - best) <= 1e-12}
        if len(oracle_best) >= 2:
            continue
        top_value = max(values[slot] for slot in legal)
        tied_top = {slot for slot in legal if abs(values[slot] - top_value) <= 1e-12}
        if tied_top & oracle_best:
            if len(tied_top) > 1:
                dependent.append(case_id)
            continue
        dependent.append(case_id)
    return {"tie_dependent_case_count": len(dependent), "tie_dependent_cases": dependent}


def is_non_degenerate(
    bundle: DevelopmentBundle,
    component: Component,
    *,
    nd3_floor: int | None,
) -> dict:
    """ND-1, ND-2, ND-3 of preregistration section 4.2.1."""

    nd1_failures: list[str] = []
    nd2_failures: list[str] = []
    strict_unique = 0
    for case in bundle.canonical_cases():
        case_id = str(case["case_id"])
        sealed = build_component_input(case, bundle.response_for(case_id), bundle.contract)
        values = component.values(sealed)
        legal = tuple(sealed.legal_target_slots)
        distinct = {round(values[slot], 12) for slot in legal}
        if len(distinct) <= 1:
            nd1_failures.append(case_id)
        maximum = max(values[slot] for slot in legal)
        argmax = {slot for slot in legal if abs(values[slot] - maximum) <= 1e-12}
        if len(argmax) == 1:
            strict_unique += 1
        classes = {
            sealed.category_vector(slot): set() for slot in legal
        }
        for slot in legal:
            classes[sealed.category_vector(slot)].add(slot)
        containing = {
            frozenset(group)
            for group in classes.values()
            if argmax & group
        }
        if len(containing) != 1:
            nd2_failures.append(case_id)
    nd3_ok = nd3_floor is None or strict_unique >= nd3_floor
    return {
        "nd1_pass": not nd1_failures,
        "nd1_failures": nd1_failures,
        "nd2_pass": not nd2_failures,
        "nd2_failures": nd2_failures,
        "nd3_strict_unique_maximum_count": strict_unique,
        "nd3_floor_from_b2": nd3_floor,
        "nd3_pass": nd3_ok,
        "pass": (not nd1_failures) and (not nd2_failures) and nd3_ok,
    }


def baseline_b0(bundle: DevelopmentBundle) -> dict:
    assert_frozen_estimator()
    component = HistoricalEstimatorComponent()
    canonical = criterion(bundle, component)
    longest = readout(bundle, component, READOUT_VARIANT)
    equivalence = section_14_equivalence(bundle, component)
    invariance = own_ranking_invariance(bundle, component)
    observed = {
        "canonical_top1": canonical["top1"],
        "canonical_top2": canonical["top2"],
        "canonical_regret": canonical["mean_normalized_regret"],
        "illegal_target_count": canonical["illegal_target_count"],
        "equivalence_pairs": equivalence["pair_count"],
        "equivalence_failures": equivalence["failures"],
        "own_ranking_invariance": f"{invariance['selection_pass']}/{invariance['selection_total']}",
        "longest_artifact_top1": longest["top1"],
        "longest_artifact_top2": longest["top2"],
        "longest_artifact_regret": longest["mean_normalized_regret"],
    }
    mismatches = {
        key: {"recorded": FROZEN_B0_RECORDED[key], "observed": observed[key]}
        for key in FROZEN_B0_RECORDED
        if not _matches(FROZEN_B0_RECORDED[key], observed[key])
    }
    return {
        "component": component.name,
        "identifier": component.identifier,
        "recorded_expectation": dict(FROZEN_B0_RECORDED),
        "acceptance_figures": list(FROZEN_GATE_ACCEPTANCE_FIGURES),
        "observed": observed,
        "canonical_aggregate": canonical,
        "longest_artifact_aggregate": longest,
        "reproduces_recorded_figures": not mismatches,
        "reproduces_acceptance_figures": all(
            _matches(FROZEN_B0_RECORDED[key], observed[key])
            for key in FROZEN_GATE_ACCEPTANCE_FIGURES
        ),
        "mismatches": mismatches,
        "section_14_equivalence": equivalence,
        "own_ranking_invariance": invariance,
        "degeneracy_census": degeneracy_census(bundle, component),
        "family_macro": family_macro(bundle, component),
        "leave_one_source_out": leave_one_source_out(bundle, component),
        "tie_dependence": tie_dependence(bundle, component),
    }


def _matches(recorded: object, observed: object) -> bool:
    if isinstance(recorded, float) and isinstance(observed, float):
        return abs(recorded - observed) <= 1e-12
    return recorded == observed


def access_ledger_record(*, actor: str, motivation: str) -> dict:
    return {
        "schema_version": 1,
        "event": "study_start",
        "actor": actor,
        "operation": "open:development_only",
        "tool": "tools/run_estimator_repair_study.py",
        "motivation": motivation,
        "repository_commit": repository_commit(),
        "condition_id": "est-repair-v1.3.1",
        "authorizing_adr": "ADR-0020",
        "inference_authorized": False,
        "confirmation_authorized": False,
    }


def append_access_ledger(path: Path, record: Mapping[str, object]) -> bool:
    """Append-only, idempotent: the study-start record is written once."""

    path = guard_path(path)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if '"event": "study_start"' in existing:
        return False
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    return True
