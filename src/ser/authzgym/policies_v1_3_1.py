"""Arm B candidate for ``est-repair-v1.3.1``: revised estimator, fixed adapter.

The fixed section-13 adapter supplies, for each legal target, one reference per
published relation category present in the response (tagged with the published
category tag) plus the sign of each candidate family's published local-cue
effect. This module reproduces that view from the authorized sealed input and
replaces only the estimator's value rule and selection rule.

It reads no restricted field, no canonical ordinal, no identifier, and no
inventory order. The published family -> relation-category map and the effect
sign convention are restated here so the module has no evaluator import.
"""

from __future__ import annotations


RELATION_TAG_BY_CATEGORY = {
    "ownership": "ownership_path",
    "membership": "membership_path",
    "role": "role_path",
    "context": "context_path",
    "general_dependency": "general_dependency",
}
EFFECT_SIGN = {"support": 1.0, "contradict": -1.0, "neutral": 0.0, "unknown": 0.0}

# The published general-dependency category is the relation-precedence fallback:
# its `contains` list is empty, so it applies exactly when no other public
# category applies to the visible call.
FALLBACK_TAG = "general_dependency"


class EstimatorV1SalientCategory:
    """B-1: score targets by the published category the local cues select.

    Mechanism: the fixed adapter delivers the per-target reference tags and the
    published candidate-effect signs to the value layer, and the historical
    estimator reduces both to `1.0 + max(0, support)` per reference. Whenever no
    candidate family carries a directional `support` cue, every reference
    contributes identically and the whole ranking collapses (preregistration
    section 1.2, H-R1; the mode occurs in 2 of the 8 canonical development
    cases). This candidate instead selects the published category the public
    local cues point at -- the supporting family's category when one exists, and
    otherwise the general-dependency fallback category -- and gives that
    category's targets a strictly higher value.
    """

    name = "arm_b_1_salient_category"
    identifier = "B-1"

    def _tags_by_slot(self, sealed) -> dict[int, set[str]]:
        relation_slots = sealed.contract_constants["relation_slots"]
        return {
            slot: {
                RELATION_TAG_BY_CATEGORY[str(relation_slots[f"r{index}"])]
                for index, present in enumerate(sealed.category_vector(slot))
                if present
            }
            for slot in sealed.legal_target_slots
        }

    def _salient_tags(self, sealed) -> set[str]:
        supporting = {
            RELATION_TAG_BY_CATEGORY[family]
            for slot, family, _ in sealed.candidate_hypotheses
            if EFFECT_SIGN[sealed.candidate_effects[slot]] > 0.0
        }
        return supporting or {FALLBACK_TAG}

    def values(self, sealed) -> dict[int, float]:
        tags = self._tags_by_slot(sealed)
        salient = self._salient_tags(sealed)
        return {
            slot: 1.0 + (1.0 if tags[slot] & salient else 0.0)
            for slot in sealed.legal_target_slots
        }

    def declared_ties(self, sealed) -> list[list[int]]:
        values = self.values(sealed)
        levels = sorted({values[slot] for slot in sealed.legal_target_slots}, reverse=True)
        return [
            [slot for slot in sealed.legal_target_slots if values[slot] == level]
            for level in levels
        ]

    def own_order(self, sealed, case) -> list[list[int]]:
        # Equivariant by construction: the declared tie is resolved by the frozen
        # evaluator canonical-ordinal rule, never by an identifier or slot order.
        return self.declared_ties(sealed)


ARM_B_CANDIDATES = {
    "B-1": EstimatorV1SalientCategory,
}
