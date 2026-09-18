"""Arm A candidates for ``est-repair-v1.3.1``: revised adapter, frozen estimator.

Each candidate here is an adapter-side transform from the authorized sealed
input to the observation the *unchanged* frozen estimator consumes. The frozen
estimator (``ser.authzgym.policies``, SHA-256 ``092a7a87...``) and the fixed
section-13 adapter (``ser.evaluation.authz_v1_3``) are never modified; the
frozen estimator's arithmetic is reached through the same published effects,
tags and references the fixed adapter supplies.
"""

from __future__ import annotations

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


# Published family -> relation-category tag map, restated so this module does not
# import the fixed adapter. Values are identical to the frozen adapter's map.
RELATION_TAG_BY_CATEGORY = {
    "ownership": "ownership_path",
    "membership": "membership_path",
    "role": "role_path",
    "context": "context_path",
    "general_dependency": "general_dependency",
}
# The frozen adapter's effect-sign convention.
EFFECT_SIGN = {"support": 1.0, "contradict": -1.0, "neutral": 0.0, "unknown": 0.0}


class _AdapterBase:
    """Shared plumbing: sealed input in, frozen-estimator values out."""

    name = "arm_a_adapter"
    identifier = "arm_a_adapter"

    def declared_ties(self, sealed):
        values = self.values(sealed)
        groups: list[list[int]] = []
        for level in sorted({values[slot] for slot in sealed.legal_target_slots}, reverse=True):
            groups.append(
                [slot for slot in sealed.legal_target_slots if values[slot] == level]
            )
        return groups

    def own_order(self, sealed, case):
        return self.declared_ties(sealed)

    def _candidate_tags(self, sealed) -> dict[str, tuple[str, ...]]:
        raise NotImplementedError

    def _reference_tag(self, sealed, slot, category, effects) -> str:
        return RELATION_TAG_BY_CATEGORY[category]

    def values(self, sealed) -> dict[int, float]:
        effects = {
            slot: EFFECT_SIGN[sealed.candidate_effects[slot]]
            for slot, _, _ in sealed.candidate_hypotheses
        }
        tags = self._candidate_tags(sealed)
        candidates = tuple(
            CandidateHypothesis(slot, description, tags[slot])
            for slot, _, description in sealed.candidate_hypotheses
        )
        relation_slots = sealed.contract_constants["relation_slots"]
        references = tuple(
            SemanticReference(
                f"t{slot}",
                self._reference_tag(
                    sealed,
                    slot,
                    str(relation_slots[f"r{index}"]),
                    effects,
                ),
            )
            for slot in sealed.legal_target_slots
            for index, present in enumerate(sealed.category_vector(slot))
            if present
        )
        inventory = tuple(
            ArtifactDescriptor(f"t{slot}", f"t{slot}", (f"t{slot}",), 0)
            for slot in (sealed.current_artifact_slot,)
            + tuple(sealed.legal_target_slots)
        )
        state = AuthzEpistemicState.initial(candidates)
        state = update_state(
            state,
            (f"t{sealed.current_artifact_slot}",),
            SemanticObservation(
                tuple(slot for slot, value in sealed.facts.items() if value),
                (),
                tuple((slot, effects[slot]) for slot, _, _ in sealed.candidate_hypotheses),
                references,
                (),
            ),
        )
        return {
            int(artifact_id[1:]): float(value)
            for artifact_id, value in estimate_action_values(
                state, inventory, candidates
            ).items()
        }


class ArmA1GeneralDependencyTag(_AdapterBase):
    """A-1: represent the published ``general_dependency`` category.

    Mechanism: the frozen estimator links a reference to a candidate through the
    candidate's relation tags, and the fixed adapter's tag set never carries
    ``general_dependency`` (preregistration section 1.2, L1). An ``r4`` reference
    therefore links to nothing and is scored exactly like an unsupported
    category. This candidate gives the ownership-family candidate the published
    ``general_dependency`` tag so an ``r4`` reference becomes representable.
    """

    name = "arm_a_1_general_dependency_tag"
    identifier = "A-1"

    def _candidate_tags(self, sealed):
        tags = {}
        for slot, family, _ in sealed.candidate_hypotheses:
            own = (RELATION_TAG_BY_CATEGORY[family],)
            if family == "ownership":
                own = own + ("general_dependency",)
            tags[slot] = own
        return tags


class ArmA2NeutralDistinctTag(_AdapterBase):
    """A-2: carry the published neutral/unknown distinction into the tag layer.

    Mechanism-level defect of A-1: A-1 made the fallback category representable
    but still routed every non-directional effect value through the same
    linkage, so a ``neutral`` local cue and an ``unknown`` one remain
    indistinguishable to the value layer (preregistration section 1.2, L2). This
    candidate keeps A-1's tag and additionally gives ``neutral`` references a
    distinct tag no candidate carries, so a mixed-cue category stops sharing a
    channel with a category that has no directional cue at all.
    """

    name = "arm_a_2_neutral_distinct_tag"
    identifier = "A-2"

    def _candidate_tags(self, sealed):
        tags = {}
        for slot, family, _ in sealed.candidate_hypotheses:
            own = (RELATION_TAG_BY_CATEGORY[family],)
            if family == "ownership":
                own = own + ("general_dependency",)
            tags[slot] = own
        return tags

    def _reference_tag(self, sealed, slot, category, effects):
        tag = RELATION_TAG_BY_CATEGORY[category]
        family_slot = next(
            (
                candidate_slot
                for candidate_slot, family, _ in sealed.candidate_hypotheses
                if family == category
            ),
            None,
        )
        if family_slot is not None and (
            effects[family_slot] == 0.0
            and sealed.candidate_effects[family_slot] == "neutral"
        ):
            return f"{tag}__neutral"
        return tag


ARM_A_CANDIDATES = {
    "A-1": ArmA1GeneralDependencyTag,
    "A-2": ArmA2NeutralDistinctTag,
}
