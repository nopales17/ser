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

import hashlib
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
from ser.evaluation.authz_v1_3_1_sealed_input import (
    SealedComponentInput,
    build_sealed_input,
)
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
CORRIGENDUM_PATH = "experiments/authzgym_estimator_repair_v1_3_1/CORRIGENDUM.md"
CORRIGENDUM_ADR = "ADR-0021"

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

# Preserved figures for baseline B0.
#
# Preregistration section 6 and handoff step 1 recorded the ``longest_artifact``
# regret as the *confirmation*-split value. ADR-0021 and CORRIGENDUM.md section
# 1.3 correct that transcription error: step-1 reproduction is authorized
# against the development-split value recorded below. The confirmation-split
# read-out is already-exposed spent-confirmation information (corrigendum
# section 1.5) and must not be used in any candidate rationale, design,
# selection, ceiling, or non-degeneracy computation. It is deliberately not
# restated anywhere in this module.
FROZEN_B0_RECORDED = {
    "canonical_top1": 0.625,
    "canonical_top2": 0.875,
    "canonical_regret": 0.175,
    "illegal_target_count": 0,
    "equivalence_pairs": 40,
    "own_ranking_invariance": "36/40",
    "longest_artifact_top1": 0.125,
    "longest_artifact_top2": 0.375,
    "longest_artifact_regret": 0.6583333333333333,
}
RECORDED_EXPECTATION_AUTHORITY = {
    "longest_artifact_regret": (
        f"{CORRIGENDUM_PATH} section 1.3 ({CORRIGENDUM_ADR}); the preregistration "
        "and handoff recorded the confirmation-split value, which is forbidden "
        "development information"
    ),
    "own_ranking_invariance": (
        f"{CORRIGENDUM_PATH} section 2.3 ({CORRIGENDUM_ADR}); own-selection "
        "equivariance with the recorded B0 36/40 fixture"
    ),
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


def is_confirmation_name(path: Path | str) -> bool:
    """The name predicate of preregistration section 3.3 and corrigendum 3.5.3."""

    return "confirmation" in Path(path).name.lower()


def guarded_sha256(path: Path | str) -> str:
    """Hash a protected file, failing closed on any confirmation-named path.

    Corrigendum section 3.5 amends handoff step 0: the development integrity
    pass must not open, read, or hash a confirmation-named path, including files
    inside ``PUBLIC_BUNDLE/``, ``RESTRICTED_BUNDLE/`` and ``annotations/``.
    """

    candidate = Path(path)
    if is_confirmation_name(candidate):
        raise ConfirmationAccessError(
            f"integrity check refused to hash confirmation path: {candidate.name}"
        )
    return hashlib.sha256(candidate.read_bytes()).hexdigest()


def integrity_files_v13() -> tuple[Path, ...]:
    """Every non-confirmation file under the frozen v1.3 instrument directory.

    Directory traversal and ``stat`` only: no confirmation-named path is ever
    opened, read, or hashed.
    """

    return tuple(
        path
        for path in sorted(V13_DIR.rglob("*"))
        if path.is_file() and not is_confirmation_name(path)
    )


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

    def case_ids(self) -> tuple[str, ...]:
        return tuple(str(item["case_id"]) for item in self.cases)

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


# Step 2 replaces the provisional container with the sealed, attribute-enforcing
# object. ``ComponentInput`` remains the name used by the component interface.
ComponentInput = SealedComponentInput
build_component_input = build_sealed_input


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
        relation_slots = sealed.contract_constants["relation_slots"]
        family_index = {
            str(name): int(str(slot)[1:]) for slot, name in relation_slots.items()
        }
        values = {}
        for slot in sealed.legal_target_slots:
            vector = sealed.category_vector(slot)
            matched = any(
                vector[family_index[family]]
                for family in supporting_categories
                if family in family_index
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
    gate_eligible = False

    def __init__(self, usefulness_by_case: Mapping[str, Mapping[str, float]]) -> None:
        self._usefulness = usefulness_by_case
        self._case_id = ""

    def for_case(self, case_id: str) -> "OracleUsefulnessComponent":
        clone = OracleUsefulnessComponent(self._usefulness)
        clone._case_id = case_id
        return clone

    def values(self, sealed: ComponentInput) -> dict[int, float]:
        usefulness = self._usefulness[self._case_id]
        return {slot: float(usefulness[slot]) for slot in sealed.legal_target_slots}

    def declared_ties(self, sealed: ComponentInput) -> list[list[int]]:
        values = self.values(sealed)
        levels = sorted({values[slot] for slot in sealed.legal_target_slots}, reverse=True)
        return [
            [slot for slot in sealed.legal_target_slots if values[slot] == level]
            for level in levels
        ]


class BaselineNotSelectableError(HarnessError):
    """B3 may never be submitted as a candidate."""


def assert_candidate_eligible(component: Component) -> None:
    if getattr(component, "upper_bound_only", False) or not getattr(
        component, "gate_eligible", True
    ):
        raise BaselineNotSelectableError(
            f"{component.identifier} is an evaluator-channel upper bound and is "
            "never eligible for selection"
        )


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


def bound_values(
    component: Component, sealed: ComponentInput, case: Mapping[str, object]
) -> dict[int, float]:
    """Evaluate one component on one case, binding the case where required.

    Only evaluator-channel-only baselines (B3) define ``for_case``; candidate
    components never do, so the sealed input remains their only information.
    """

    case_id = str(case["case_id"])
    bound = component.for_case(case_id) if hasattr(component, "for_case") else component
    return bound.values(sealed)


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
        rows.append(diagnostic_for_case(bundle, case, bound_values(component, sealed, case), component=component))
    return _aggregate(rows)


def readout(bundle: DevelopmentBundle, component: Component, variant: str) -> dict:
    rows = []
    for case in bundle.cases:
        if case["variant"] != variant:
            continue
        sealed = build_component_input(
            case, bundle.response_for(str(case["case_id"])), bundle.contract
        )
        rows.append(diagnostic_for_case(bundle, case, bound_values(component, sealed, case), component=component))
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
                diagnostic_for_case(bundle, case, bound_values(component, sealed, case), component=component)
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
        values = bound_values(component, sealed, case)
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


def bound_order(
    component: Component, sealed: ComponentInput, case: Mapping[str, object]
) -> list[list[int]]:
    bound = (
        component.for_case(str(case["case_id"]))
        if hasattr(component, "for_case")
        else component
    )
    return bound.own_order(sealed, case)


def own_ranking_invariance(bundle: DevelopmentBundle, component: Component) -> dict:
    """Section-2.6 obligation as resolved by CORRIGENDUM.md section 2.3.

    The gate is *own-selection-decision equivariance*: the target the
    component's own selection rule returns must be equivariant under the five
    equivalence transformations, compared after mapping through
    ``canonical_ordinal_by_variant_public_id``. A component may legitimately
    preserve a top tie and delegate it to the frozen evaluator canonical-ordinal
    rule (section 2.4 route 2); a declared top tie whose mapped ordinal set is
    identical therefore passes, and resolves to the same target. Breaking a top
    tie internally by an identifier-dependent rule is inadmissible and is what
    B0's recorded 36/40 fixture measures. Full-order invariance is descriptive
    only (section 2.3(f)) and is never a gate.
    """

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
            bundle, base, bound_order(component, base_sealed, base)
        )
        for case in cases:
            if case["variant"] not in EQUIVALENCE_VARIANTS:
                continue
            sealed = build_component_input(
                case, bundle.response_for(str(case["case_id"])), bundle.contract
            )
            groups = _mapped_order(bundle, case, bound_order(component, sealed, case))
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
            "own-selection-decision equivariance: the target the component's own "
            "selection rule returns, mapped through "
            "canonical_ordinal_by_variant_public_id, must agree with base_entry; "
            "a declared top tie delegated to the frozen canonical-ordinal rule is "
            "admissible (CORRIGENDUM.md section 2.3; recorded B0 value 36/40)"
        ),
        "gate_metric": "selection",
        "candidate_requirement": "40/40",
        "recorded_b0_fixture": "36/40",
        "authority": f"{CORRIGENDUM_PATH} section 2.3 ({CORRIGENDUM_ADR})",
        "selection_pass": selection_checks - len(selection_failures),
        "selection_total": selection_checks,
        "selection_failures": selection_failures,
        "full_order_pass": order_checks - len(order_failures),
        "full_order_total": order_checks,
        "full_order_failures": order_failures,
        "full_order_is_descriptive_only": True,
        "full_order_not_a_gate": True,
    }


def section_14_equivalence(bundle: DevelopmentBundle, component: Component) -> dict:
    """The frozen transformation action-value equivalence check."""

    failures: list[str] = []
    pair_count = 0
    for source in bundle.source_episode_ids():
        cases = bundle.cases_for_source(source)
        base = next(item for item in cases if item["variant"] == CANONICAL_VARIANT)
        base_sealed = build_component_input(
            base, bundle.response_for(str(base["case_id"])), bundle.contract
        )
        base_values = bound_values(component, base_sealed, base)
        base_diagnostic = diagnostic_for_case(
            bundle, base, base_values, component=component
        )
        base_ordinal = _ordinal_by_slot(bundle, str(base["case_id"]))
        base_mapped = {base_ordinal[slot]: base_values[slot] for slot in base_values}
        for case in cases:
            if case["variant"] not in EQUIVALENCE_VARIANTS:
                continue
            case_id = str(case["case_id"])
            sealed = build_component_input(
                case, bundle.response_for(case_id), bundle.contract
            )
            values = bound_values(component, sealed, case)
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
                diagnostic_for_case(bundle, case, bound_values(component, sealed, case), component=component)
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
        values = bound_values(component, sealed, case)
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
        values = bound_values(component, sealed, case)
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


def metric_block(
    bundle: DevelopmentBundle, component: Component, *, nd3_floor: int | None = None
) -> dict:
    """Every reported diagnostic, computed identically for every baseline."""

    canonical = criterion(bundle, component)
    longest = readout(bundle, component, READOUT_VARIANT)
    equivalence = section_14_equivalence(bundle, component)
    invariance = own_ranking_invariance(bundle, component)
    return {
        "canonical_aggregate": canonical,
        "longest_artifact_aggregate": longest,
        "section_14_equivalence": equivalence,
        "own_ranking_invariance": invariance,
        "degeneracy_census": degeneracy_census(bundle, component),
        "family_macro": family_macro(bundle, component),
        "leave_one_source_out": leave_one_source_out(bundle, component),
        "tie_dependence": tie_dependence(bundle, component),
        "non_degeneracy": is_non_degenerate(bundle, component, nd3_floor=nd3_floor),
        "upper_bound_only": bool(getattr(component, "upper_bound_only", False)),
        "gate_eligible": bool(getattr(component, "gate_eligible", True)),
    }


def baseline_b0(bundle: DevelopmentBundle) -> dict:
    assert_frozen_estimator()
    component = HistoricalEstimatorComponent()
    metrics = metric_block(bundle, component)
    canonical = metrics["canonical_aggregate"]
    longest = metrics["longest_artifact_aggregate"]
    equivalence = metrics["section_14_equivalence"]
    invariance = metrics["own_ranking_invariance"]
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
        **metrics,
        "component": component.name,
        "identifier": component.identifier,
        "recorded_expectation": dict(FROZEN_B0_RECORDED),
        "recorded_expectation_authority": dict(RECORDED_EXPECTATION_AUTHORITY),
        "acceptance_figures": list(FROZEN_GATE_ACCEPTANCE_FIGURES),
        "observed": observed,
        "reproduces_recorded_figures": not mismatches,
        "reproduces_acceptance_figures": all(
            _matches(FROZEN_B0_RECORDED[key], observed[key])
            for key in FROZEN_GATE_ACCEPTANCE_FIGURES
        ),
        "mismatches": mismatches,
    }


def baseline_record(
    bundle: DevelopmentBundle,
    component: Component,
    *,
    nd3_floor: int | None = None,
) -> dict:
    metrics = metric_block(bundle, component, nd3_floor=nd3_floor)
    return {
        **metrics,
        "component": component.name,
        "identifier": component.identifier,
    }


def oracle_usefulness_baseline(bundle: DevelopmentBundle) -> OracleUsefulnessComponent:
    return OracleUsefulnessComponent(
        {
            case_id: _usefulness_by_slot(bundle, case_id)
            for case_id in bundle.case_ids()
        }
    )


def freeze_nd3_floor(path: Path, floor: int) -> bool:
    """Write the B2-derived ND-3 floor exactly once (handoff step 4).

    Returns ``True`` when the value is written for the first time. A later call
    that would change the frozen value raises; a later call with the identical
    value performs no write and returns ``False``.
    """

    path = Path(path)
    if path.exists():
        existing = json.loads(path.read_text(encoding="utf-8"))
        frozen = existing.get("frozen_nd3_floor_from_b2")
        if frozen is not None:
            if frozen != floor:
                raise HarnessError(
                    "nd3_floor_from_b2 is already frozen at "
                    f"{frozen}; refusing to re-freeze it at {floor}"
                )
            return False
    document = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    document["frozen_nd3_floor_from_b2"] = floor
    path.write_text(
        json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return True


# Preregistration section 4.2, frozen and unchanged.
GATE = {
    "canonical_top1": (">=", 0.60),
    "canonical_top2": (">=", 0.80),
    "mean_normalized_regret": ("<=", 0.35),
    "illegal_target_count": ("==", 0),
    "section_14_equivalence": ("==", "40/40"),
    "own_selection_equivariance": ("==", "40/40"),
    "nd1": ("==", True),
    "nd2": ("==", True),
    "nd3": ("==", True),
}


def complexity_score(
    *,
    numeric_constants: int = 0,
    family_branches: int = 0,
    relation_category_branches: int = 0,
) -> int:
    """Preregistration section 4.8 complexity control.

    Counted: free numeric constants introduced (+1), conditionals testing a
    concrete candidate ``effect_family`` (+2), and conditionals testing or newly
    mapping a concrete published relation category (+3). Constants and the
    published relation-category map inherited unchanged from the frozen code are
    not counted, exactly as section 4.8 says for inherited constants.
    """

    return (
        int(numeric_constants)
        + 2 * int(family_branches)
        + 3 * int(relation_category_branches)
    )


def gate_record(
    bundle: DevelopmentBundle,
    component: Component,
    *,
    nd3_floor: int,
) -> dict:
    """The frozen section-4.2 criterion plus the structural admissibility gates."""

    metrics = metric_block(bundle, component, nd3_floor=nd3_floor)
    canonical = metrics["canonical_aggregate"]
    equivalence = metrics["section_14_equivalence"]
    invariance = metrics["own_ranking_invariance"]
    degeneracy = metrics["non_degeneracy"]
    checks = {
        "canonical_top1": canonical["top1"] >= 0.60,
        "canonical_top2": canonical["top2"] >= 0.80,
        "mean_normalized_regret": canonical["mean_normalized_regret"] <= 0.35,
        "illegal_target_count": canonical["illegal_target_count"] == 0,
        "section_14_equivalence": (
            equivalence["pair_count"] == 40 and not equivalence["failures"]
        ),
        "own_selection_equivariance": (
            invariance["selection_total"] == 40 and invariance["selection_pass"] == 40
        ),
        "nd1": degeneracy["nd1_pass"],
        "nd2": degeneracy["nd2_pass"],
        "nd3": degeneracy["nd3_pass"],
    }
    return {
        **metrics,
        "requirements": {
            key: {"requirement": GATE[key], "observed": checks[key]}
            for key in GATE
        },
        "checks": checks,
        "passes": all(checks.values()),
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
    """Append-only, idempotent per ``event``: no record is ever rewritten."""

    path = guard_path(path)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    marker = json.dumps(str(record["event"]))[1:-1]
    if f'"event": "{marker}"' in existing:
        return False
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    return True


def resumption_ledger_record(*, actor: str) -> dict:
    """Corrigendum section 5: the resumption is recorded by appending."""

    return {
        "schema_version": 1,
        "event": "study_resumption",
        "actor": actor,
        "operation": "resume:step1",
        "tool": "tools/run_estimator_repair_study.py",
        "condition_id": "est-repair-v1.3.1",
        "authorizing_adr": "ADR-0020",
        "correcting_adr": CORRIGENDUM_ADR,
        "corrigendum": CORRIGENDUM_PATH,
        "supersedes_blocker": "experiments/authzgym_estimator_repair_v1_3_1/STUDY_BLOCKER.md",
        "blocker_retained": True,
        "candidate_budget_consumed": 0,
        "inference_authorized": False,
        "confirmation_authorized": False,
        "repository_commit": repository_commit(),
    }


def deviation_ledger_record(*, actor: str) -> dict:
    """Corrigendum section 3.6: carry the step-0 deviation forward explicitly."""

    return {
        "schema_version": 1,
        "event": "confirmation_path_hashing_deviation",
        "actor": actor,
        "operation": "record:procedural_deviation",
        "tool": "handoff step 0 integrity pass (completed before ADR-0021)",
        "condition_id": "est-repair-v1.3.1",
        "authority": f"{CORRIGENDUM_PATH} section 3 ({CORRIGENDUM_ADR})",
        "description": (
            "The pre-corrigendum step-0 integrity pass computed SHA-256 over the "
            "16 confirmation-named files under the v1.3 directory, because "
            "handoff step 0 said to hash everything there. No confirmation "
            "content was parsed, scored, counted, retained, or used for any "
            "design or selection decision."
        ),
        "classification": "procedural_deviation_not_retroactively_authorized",
        "invalidates_study": False,
        "retroactively_authorized": False,
        "future_integrity_policy": "hash no confirmation-named path; fail closed",
    }
