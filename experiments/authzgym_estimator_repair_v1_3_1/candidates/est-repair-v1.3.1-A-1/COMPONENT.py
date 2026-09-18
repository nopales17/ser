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
