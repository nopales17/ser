"""Baseline, ablation, and candidate policies for MicroGym."""

from .adaptive import (
    AdaptiveBeliefPolicy,
    CostBlindPolicy,
    NoAdaptationPolicy,
    NoAdaptiveStopPolicy,
)
from .baselines import (
    CheapFirstPolicy,
    ExhaustivePolicy,
    FixedOrderPolicy,
    GreedyPolicy,
    InformationBlindPolicy,
    RandomPolicy,
)


def policy_suite():
    return (
        FixedOrderPolicy(),
        RandomPolicy(),
        CheapFirstPolicy(),
        ExhaustivePolicy(),
        GreedyPolicy(),
        AdaptiveBeliefPolicy(),
        NoAdaptationPolicy(),
        CostBlindPolicy(),
        InformationBlindPolicy(),
        NoAdaptiveStopPolicy(),
    )


__all__ = [
    "AdaptiveBeliefPolicy",
    "CheapFirstPolicy",
    "CostBlindPolicy",
    "ExhaustivePolicy",
    "FixedOrderPolicy",
    "GreedyPolicy",
    "InformationBlindPolicy",
    "NoAdaptationPolicy",
    "NoAdaptiveStopPolicy",
    "RandomPolicy",
    "policy_suite",
]
