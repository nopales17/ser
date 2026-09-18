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
