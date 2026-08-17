"""Frozen MicroGym v1 family definitions.

Identifiers are deliberately opaque. Family semantics live in descriptions and
likelihood matrices, never in target-aware action names.
"""

from __future__ import annotations

from itertools import combinations

from .model import ProblemSpec, PublicTestModel, RESOURCE_SCHEMA, TestSpec


def _score(rows: tuple[tuple[float, ...], ...], cost_units: float) -> float:
    separations = [
        0.5 * sum(abs(left[index] - right[index]) for index in range(len(left)))
        for left, right in combinations(rows, 2)
    ]
    return (sum(separations) / len(separations)) / max(cost_units, 1e-9)


def _test(
    action_id: str,
    rows: tuple[tuple[float, ...], ...],
    units: float,
    *,
    outcomes: tuple[str, ...] | None = None,
    repeat: int = 1,
    failure: float = 0.0,
    failure_terminates: bool = False,
    slot: str | None = None,
    test_count: float = 1.0,
) -> TestSpec:
    normalized = tuple(tuple(float(value) for value in row) for row in rows)
    labels = outcomes or tuple(f"v{index}" for index in range(len(normalized[0])))
    public = PublicTestModel(
        action_id=action_id,
        outcomes=labels,
        likelihoods=normalized,
        cost=RESOURCE_SCHEMA.vector(
            {
                "tests": test_count,
                "synthetic_cost_units": units,
                "latency_steps": units,
            }
        ),
        repeat_limit=repeat,
        failure_probability=failure,
        failure_terminates=failure_terminates,
        public_score=_score(normalized, units),
    )
    return TestSpec(public, slot or f"slot-{action_id}")


def _symmetric(action_id: str, hypotheses: int, accuracy: float, units: float, **kwargs) -> TestSpec:
    off = (1.0 - accuracy) / (hypotheses - 1)
    rows = tuple(
        tuple(accuracy if row == column else off for column in range(hypotheses))
        for row in range(hypotheses)
    )
    return _test(action_id, rows, units, **kwargs)


def _neutral(hypotheses: int) -> TestSpec:
    return _test(
        "init",
        tuple((1.0,) for _ in range(hypotheses)),
        0.0,
        outcomes=("v0",),
        slot="initial",
        test_count=0.0,
    )


def _problem(
    family: str,
    regime: int,
    description: str,
    hypotheses: tuple[str, ...],
    initial: TestSpec,
    tests: tuple[TestSpec, ...],
    budget: float,
    cost_weight: float,
    *,
    max_steps: int = 5,
    abstain_loss: float = 0.35,
    assumptions: tuple[str, ...] = (),
) -> ProblemSpec:
    return ProblemSpec(
        problem_id=f"{family.lower()}-r{regime}",
        family=family,
        version="microgym-v1",
        description=description,
        hypotheses=hypotheses,
        prior=tuple(1.0 / len(hypotheses) for _ in hypotheses),
        initial_test=initial,
        tests=tests,
        budget_limits=(("synthetic_cost_units", budget), ("tests", float(max_steps))),
        primary_resource="synthetic_cost_units",
        cost_weight=cost_weight,
        abstain_loss=abstain_loss,
        max_steps=max_steps,
        assumptions=(
            "hypothesis labels, action IDs, and outcome IDs are opaque",
            "likelihoods and costs are policy-visible in this experimental condition",
        )
        + assumptions,
    )


def _family_a() -> list[ProblemSpec]:
    hypotheses = ("s0", "s1", "s2")
    settings = (
        (4.0, 0.08, 0.90, 0.88, 8.0),
        (4.0, 0.12, 0.82, 0.94, 7.0),
        (5.0, 0.08, 0.94, 0.80, 6.0),
        (6.0, 0.06, 0.86, 0.91, 5.0),
    )
    output = []
    for regime, (budget, weight, a_strength, b_strength, reveal_cost) in enumerate(settings):
        a = _test("a0", ((a_strength, 1-a_strength), (1-a_strength, a_strength), (0.5, 0.5)), 1.0)
        b = _test("a1", ((0.55, 0.45), (0.55, 0.45), (1-b_strength, b_strength)), 2.0)
        c = _symmetric("a2", 3, 0.97, reveal_cost)
        output.append(_problem("A", regime, "Unequal diagnostic value across differently priced tests.", hypotheses, _neutral(3), (a, b, c), budget, weight))
    return output


def _family_b() -> list[ProblemSpec]:
    hypotheses = ("s0", "s1", "s2")
    settings = (
        (0.58, 0.62, 0.94, 2.5, 3.0, 0.10),
        (0.72, 0.68, 0.90, 3.0, 4.0, 0.10),
        (0.80, 0.60, 0.92, 2.8, 4.0, 0.12),
        (0.55, 0.58, 0.97, 3.5, 4.0, 0.08),
    )
    return [
        _problem(
            "B",
            regime,
            "Cheap evidence ranges from misleadingly weak to genuinely cost-effective.",
            hypotheses,
            _neutral(3),
            (
                _symmetric("b0", 3, cheap_a, 1.0),
                _symmetric("b1", 3, cheap_b, 1.2),
                _symmetric("b2", 3, strong, strong_cost),
            ),
            budget,
            weight,
        )
        for regime, (cheap_a, cheap_b, strong, strong_cost, budget, weight) in enumerate(settings)
    ]


def _family_c() -> list[ProblemSpec]:
    hypotheses = ("s0", "s1", "s2")
    settings = (
        (0.90, 0.15, 4.0),
        (0.75, 0.10, 4.0),
        (0.65, 0.05, 4.0),
        (0.85, 0.20, 3.0),
    )
    return [
        _problem(
            "C",
            regime,
            "Initial evidence is sometimes sufficient; expensive confirmation remains available.",
            hypotheses,
            _symmetric("init", 3, initial_accuracy, 0.0, slot="initial", test_count=0.0),
            (_symmetric("c0", 3, 0.80, 1.0), _symmetric("c1", 3, 0.98, 3.0)),
            budget,
            weight,
            max_steps=4,
        )
        for regime, (initial_accuracy, weight, budget) in enumerate(settings)
    ]


def _family_d() -> list[ProblemSpec]:
    hypotheses = ("s0", "s1", "s2")
    settings = (
        (0.62, 0.90, 4.0, 0.10),
        (0.68, 0.88, 4.0, 0.10),
        (0.60, 0.94, 5.0, 0.08),
        (0.72, 0.86, 5.0, 0.12),
    )
    return [
        _problem(
            "D",
            regime,
            "Repeated conditionally independent noisy evidence has diminishing value.",
            hypotheses,
            _neutral(3),
            (
                _symmetric("d0", 3, repeated_accuracy, 1.0, repeat=4),
                _symmetric("d1", 3, strong_accuracy, 3.0),
                _symmetric("d2", 3, repeated_accuracy, 1.1, repeat=2),
            ),
            budget,
            weight,
            max_steps=6,
            assumptions=("repeated measurements are independent conditional on the hidden state",),
        )
        for regime, (repeated_accuracy, strong_accuracy, budget, weight) in enumerate(settings)
    ]


def _family_e() -> list[ProblemSpec]:
    hypotheses = ("s0", "s1", "s2", "s3")
    settings = (
        (0.90, 2.0, 2.0, 2.0, 0.10),
        (0.80, 1.8, 2.2, 2.2, 0.10),
        (0.70, 2.0, 2.0, 3.0, 0.08),
        (0.65, 1.5, 2.5, 3.0, 0.12),
    )
    output = []
    for regime, (branch_accuracy, left_cost, right_cost, budget, weight) in enumerate(settings):
        initial = _test(
            "init",
            (
                (branch_accuracy, 1-branch_accuracy),
                (branch_accuracy, 1-branch_accuracy),
                (1-branch_accuracy, branch_accuracy),
                (1-branch_accuracy, branch_accuracy),
            ),
            0.0,
            outcomes=("v0", "v1"),
            slot="initial",
            test_count=0.0,
        )
        left = _test("e0", ((0.90, 0.10), (0.10, 0.90), (0.50, 0.50), (0.50, 0.50)), left_cost)
        right = _test("e1", ((0.50, 0.50), (0.50, 0.50), (0.90, 0.10), (0.10, 0.90)), right_cost)
        generic = _symmetric("e2", 4, 0.78, 4.0)
        output.append(_problem("E", regime, "A free branch cue changes which targeted test deserves a hard budget.", hypotheses, initial, (left, right, generic), budget, weight, max_steps=3))
    return output


def _family_f() -> list[ProblemSpec]:
    hypotheses = ("s0", "s1", "s2")
    settings = (
        (0.25, False, 3.0, 0.10),
        (0.40, False, 3.0, 0.10),
        (0.25, True, 4.0, 0.08),
        (0.40, True, 4.0, 0.12),
    )
    return [
        _problem(
            "F",
            regime,
            "A cheap diagnostic may fail, consume cost, and sometimes terminate the environment.",
            hypotheses,
            _neutral(3),
            (
                _symmetric("f0", 3, 0.86, 1.0, failure=failure, failure_terminates=terminates),
                _symmetric("f1", 3, 0.80, 1.5),
                _symmetric("f2", 3, 0.96, 3.0),
            ),
            budget,
            weight,
            max_steps=4,
        )
        for regime, (failure, terminates, budget, weight) in enumerate(settings)
    ]


def build_problem_specs() -> tuple[ProblemSpec, ...]:
    """Return the preregistered MicroGym v1 problem regimes in stable order."""

    return tuple(_family_a() + _family_b() + _family_c() + _family_d() + _family_e() + _family_f())
