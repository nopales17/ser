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
