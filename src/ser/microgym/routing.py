"""Frozen family definitions for the MicroGym routing-v1 falsification test.

The benchmark has one reset-time branch cue followed by exactly one acquired
observation.  All acquisition actions have the same raw cost, so the primary
comparison isolates which action is selected rather than stopping or thrift.
"""

from __future__ import annotations

from dataclasses import dataclass

from .model import ProblemSpec, PublicTestModel, RESOURCE_SCHEMA, TestSpec


ROUTING_POPULATION_SEED = 141_421_356
ROUTING_ENVIRONMENT_REALIZATION_MASTER_SEED = 173_205_080
ROUTING_POLICY_RANDOMNESS_MASTER_SEED = 223_606_797
ROUTING_EPISODES_PER_REGIME = 128


@dataclass(frozen=True)
class RoutingRegime:
    problem: ProblemSpec
    declared_voa_band: str


def _test(
    action_id: str,
    likelihoods: tuple[tuple[float, ...], ...],
    *,
    outcomes: tuple[str, ...],
    units: float,
    rng_slot: str,
    test_count: float = 1.0,
) -> TestSpec:
    return TestSpec(
        PublicTestModel(
            action_id=action_id,
            outcomes=outcomes,
            likelihoods=likelihoods,
            cost=RESOURCE_SCHEMA.vector(
                {
                    "tests": test_count,
                    "synthetic_cost_units": units,
                    "latency_steps": units,
                }
            ),
            public_score=0.0,
        ),
        rng_slot,
    )


def _cue(reliability: float) -> TestSpec:
    return _test(
        "q0",
        (
            (reliability, 1.0 - reliability),
            (reliability, 1.0 - reliability),
            (1.0 - reliability, reliability),
            (1.0 - reliability, reliability),
        ),
        outcomes=("v0", "v1"),
        units=0.0,
        rng_slot="cue",
        test_count=0.0,
    )


def _specialists(accuracy: float) -> tuple[TestSpec, TestSpec]:
    left = _test(
        "a0",
        (
            (accuracy, 1.0 - accuracy),
            (1.0 - accuracy, accuracy),
            (0.5, 0.5),
            (0.5, 0.5),
        ),
        outcomes=("v0", "v1"),
        units=1.0,
        rng_slot="left-specialist",
    )
    right = _test(
        "a1",
        (
            (0.5, 0.5),
            (0.5, 0.5),
            (accuracy, 1.0 - accuracy),
            (1.0 - accuracy, accuracy),
        ),
        outcomes=("v0", "v1"),
        units=1.0,
        rng_slot="right-specialist",
    )
    return left, right


def _symmetric(action_id: str, accuracy: float, slot: str) -> TestSpec:
    off = (1.0 - accuracy) / 3.0
    return _test(
        action_id,
        tuple(
            tuple(accuracy if row == column else off for column in range(4))
            for row in range(4)
        ),
        outcomes=("v0", "v1", "v2", "v3"),
        units=1.0,
        rng_slot=slot,
    )


def _problem(
    family: str,
    regime: int,
    description: str,
    cue_reliability: float,
    tests: tuple[TestSpec, TestSpec],
) -> ProblemSpec:
    return ProblemSpec(
        problem_id=f"{family.lower()}-r{regime}",
        family=family,
        version="microgym-routing-v1",
        description=description,
        hypotheses=("s0", "s1", "s2", "s3"),
        prior=(0.25, 0.25, 0.25, 0.25),
        initial_test=_cue(cue_reliability),
        tests=tests,
        budget_limits=(("synthetic_cost_units", 1.0), ("tests", 1.0)),
        primary_resource="synthetic_cost_units",
        cost_weight=0.0,
        abstain_loss=1.0,
        max_steps=1,
        assumptions=(
            "the reset cue and acquisition likelihoods are public",
            "all acquisition actions have equal declared cost",
            "the runner requires exactly one acquisition and then a final answer",
            "adaptive STOP is unavailable in the primary routing condition",
            "identifiers are opaque and action presentation order is counterbalanced",
        ),
    )


def build_routing_regimes() -> tuple[RoutingRegime, ...]:
    """Return the routing-v1 regimes frozen before candidate aggregation."""

    diagnostic = (
        RoutingRegime(
            _problem(
                "RA",
                0,
                "A reliable broad cue selects between two complementary specialists.",
                0.90,
                _specialists(0.95),
            ),
            "high",
        ),
        RoutingRegime(
            _problem(
                "RA",
                1,
                "A noisier broad cue still changes which high-quality specialist is useful.",
                0.75,
                _specialists(0.98),
            ),
            "high",
        ),
    )

    identical = _symmetric("a0", 0.78, "generic-0")
    identical_copy = TestSpec(
        PublicTestModel(
            action_id="a1",
            outcomes=identical.public.outcomes,
            likelihoods=identical.public.likelihoods,
            cost=identical.public.cost,
            public_score=0.0,
        ),
        "generic-1",
    )
    zero_controls = (
        RoutingRegime(
            _problem(
                "RB",
                0,
                "The cue changes belief, but two acquisitions are informationally identical.",
                0.90,
                (identical, identical_copy),
            ),
            "zero",
        ),
        RoutingRegime(
            _problem(
                "RB",
                1,
                "The cue changes belief, but one general acquisition dominates the other.",
                0.85,
                (
                    _symmetric("a0", 0.82, "dominant"),
                    _symmetric("a1", 0.68, "dominated"),
                ),
            ),
            "zero",
        ),
    )

    graded_settings = (
        (0.50, "zero"),
        (0.52, "low"),
        (0.60, "moderate"),
        (0.80, "high"),
        (0.95, "high"),
    )
    graded = tuple(
        RoutingRegime(
            _problem(
                "RC",
                regime,
                "Cue reliability controls how much value conditional specialist routing can add.",
                reliability,
                _specialists(0.90),
            ),
            band,
        )
        for regime, (reliability, band) in enumerate(graded_settings)
    )
    return diagnostic + zero_controls + graded
