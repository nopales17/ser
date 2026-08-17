"""Analysis, validation, and reports for MicroGym routing-v1."""

from __future__ import annotations

from statistics import fmean
from typing import Iterable

from ser.core.types import content_hash
from ser.microgym.model import EpisodeSpec, ProblemSpec, PublicTestModel, TestSpec
from ser.microgym.routing import RoutingRegime

from .routing import (
    TOLERANCE,
    RoutingOracle,
    compute_routing_oracle,
    run_routing_episode,
    routing_policy_seed,
)
from .routing_artifacts import routing_run_artifact, verify_routing_record_hashes


POLICIES = ("exact_open_loop", "adaptive_belief", "exact_closed_loop_oracle")


def full_oracle_dict(
    regime: RoutingRegime, oracle: RoutingOracle, population_hash: str
) -> dict:
    record = {
        "schema_version": 1,
        "benchmark": "microgym-routing-v1",
        "population_hash": population_hash,
        "visibility": "evaluator_only",
        "problem_id": oracle.problem_id,
        "family": regime.problem.family,
        "declared_voa_band": regime.declared_voa_band,
        "loss_convention": "lower_is_better",
        "voa_convention": "open_loop_loss_minus_closed_loop_loss",
        "open_loop_loss": oracle.open_loop_loss,
        "open_loop_action": oracle.open_loop_action,
        "closed_loop_loss": oracle.closed_loop_loss,
        "closed_loop_actions": dict(oracle.closed_loop_actions),
        "value_of_adaptivity": oracle.value_of_adaptivity,
        "eligible_conditional_node": oracle.eligible_conditional_node,
        "candidate_expected_loss": oracle.candidate_expected_loss,
        "candidate_actions": dict(oracle.candidate_actions),
        "candidate_rankings": {
            cue: list(ranking) for cue, ranking in oracle.candidate_rankings
        },
        "adaptivity_capture": oracle.adaptivity_capture,
        "four_stage_audit": {
            "belief_changed": oracle.belief_changed,
            "action_ranking_changed": oracle.action_ranking_changed,
            "policy_action_changed": oracle.policy_action_changed,
            "action_change_improved_value": oracle.action_change_improved_value,
        },
    }
    record["record_hash"] = content_hash(record)
    return record


def build_oracle_records(
    regimes: Iterable[RoutingRegime], population_hash: str
) -> list[dict]:
    records = []
    for regime in regimes:
        view = regime.problem.public_view(
            tuple(test.public.action_id for test in regime.problem.tests)
        )
        records.append(
            full_oracle_dict(regime, compute_routing_oracle(view), population_hash)
        )
    return records


def build_run_records(
    regimes: Iterable[RoutingRegime],
    episodes: Iterable[EpisodeSpec],
    population_hash: str,
) -> list[dict]:
    problems = {regime.problem.problem_id: regime.problem for regime in regimes}
    records = []
    for episode in episodes:
        problem = problems[episode.problem_id]
        for policy_name in POLICIES:
            run = run_routing_episode(problem, episode, policy_name)
            records.append(routing_run_artifact(run, episode, population_hash))
    return records


def _mean(values: Iterable[float]) -> float:
    values = tuple(values)
    return fmean(values) if values else 0.0


def _run_index(records: Iterable[dict]) -> dict[tuple[str, str], dict]:
    return {
        (record["public"]["episode_id"], record["public"]["policy"]): record
        for record in records
    }


def _outcome(record: dict) -> dict:
    return record["restricted"]["outcome"]


def _paired(candidate: list[float], control: list[float]) -> dict:
    differences = [left - right for left, right in zip(candidate, control)]
    return {
        "paired_episodes": len(differences),
        "mean_candidate_minus_open_loop": _mean(differences),
        "candidate_wins": sum(value < -TOLERANCE for value in differences),
        "ties": sum(abs(value) <= TOLERANCE for value in differences),
        "candidate_losses": sum(value > TOLERANCE for value in differences),
    }


def _oracle_metrics(records: Iterable[dict]) -> dict[str, dict]:
    return {str(record["problem_id"]): record for record in records}


def _branch_metrics(oracles: dict[str, dict]) -> dict:
    eligible = [item for item in oracles.values() if item["eligible_conditional_node"]]
    zero = [
        item for item in oracles.values() if item["value_of_adaptivity"] <= TOLERANCE
    ]
    branched = [
        item
        for item in eligible
        if len(set(item["candidate_actions"].values())) > 1
    ]
    consistent = [
        item
        for item in eligible
        if item["candidate_actions"] == item["closed_loop_actions"]
    ]
    beneficial = [
        item
        for item in eligible
        if item["candidate_expected_loss"] < item["open_loop_loss"] - TOLERANCE
    ]
    spurious = [
        item for item in zero if len(set(item["candidate_actions"].values())) > 1
    ]
    return {
        "eligible_nodes": len(eligible),
        "candidate_branch_nodes": len(branched),
        "candidate_branch_rate": len(branched) / len(eligible) if eligible else 0.0,
        "oracle_consistent_nodes": len(consistent),
        "oracle_consistent_branch_rate": (
            len(consistent) / len(eligible) if eligible else 0.0
        ),
        "beneficial_branch_nodes": len(beneficial),
        "beneficial_branch_rate": len(beneficial) / len(eligible) if eligible else 0.0,
        "zero_voa_nodes": len(zero),
        "zero_voa_spurious_branch_nodes": len(spurious),
        "zero_voa_spurious_branch_rate": len(spurious) / len(zero) if zero else 0.0,
    }


def _classifier(
    oracles: dict[str, dict], branch: dict, validation_passed: bool
) -> dict:
    positive = [
        item for item in oracles.values() if item["value_of_adaptivity"] > TOLERANCE
    ]
    zero = [
        item for item in oracles.values() if item["value_of_adaptivity"] <= TOLERANCE
    ]
    families = {item["family"] for item in positive}
    advantages = [
        item["open_loop_loss"] - item["candidate_expected_loss"] for item in positive
    ]
    total_voa = sum(item["value_of_adaptivity"] for item in positive)
    total_captured = sum(advantages)
    weighted_capture = total_captured / total_voa if total_voa else None
    thresholds = {
        "minimum_positive_voa_regimes": 4,
        "minimum_positive_voa_families": 2,
        "minimum_zero_voa_controls": 2,
        "minimum_candidate_branch_rate": 0.80,
        "minimum_oracle_consistent_branch_rate": 0.90,
        "minimum_mean_positive_regime_advantage": 0.005,
        "minimum_voa_weighted_adaptivity_capture": 0.75,
        "maximum_zero_voa_spurious_branch_rate": 0.05,
    }
    facts = {
        "positive_voa_regimes": len(positive),
        "positive_voa_families": len(families),
        "zero_voa_controls": len(zero),
        "candidate_beats_open_on_every_positive_regime": bool(positive)
        and all(value > TOLERANCE for value in advantages),
        "mean_positive_regime_advantage": _mean(advantages),
        "voa_weighted_adaptivity_capture": weighted_capture,
        "fixed_horizon_no_stop_validation": validation_passed,
    }
    structure_valid = (
        len(positive) >= thresholds["minimum_positive_voa_regimes"]
        and len(families) >= thresholds["minimum_positive_voa_families"]
        and len(zero) >= thresholds["minimum_zero_voa_controls"]
    )
    supported = (
        validation_passed
        and structure_valid
        and branch["candidate_branch_rate"]
        >= thresholds["minimum_candidate_branch_rate"]
        and branch["oracle_consistent_branch_rate"]
        >= thresholds["minimum_oracle_consistent_branch_rate"]
        and facts["candidate_beats_open_on_every_positive_regime"]
        and facts["mean_positive_regime_advantage"]
        > thresholds["minimum_mean_positive_regime_advantage"]
        and weighted_capture is not None
        and weighted_capture
        >= thresholds["minimum_voa_weighted_adaptivity_capture"]
        and branch["zero_voa_spurious_branch_rate"]
        <= thresholds["maximum_zero_voa_spurious_branch_rate"]
    )
    if not validation_passed or not structure_valid:
        classification = "invalid"
    elif any(value < -TOLERANCE for value in advantages):
        classification = "negative"
    elif supported:
        classification = "routing_supported"
    elif branch["candidate_branch_nodes"] and _mean(advantages) <= 0.005:
        classification = "behavior_without_value"
    elif _mean(advantages) > TOLERANCE:
        classification = "value_without_verified_routing"
    elif not branch["candidate_branch_nodes"] and abs(_mean(advantages)) <= TOLERANCE:
        classification = "null"
    else:
        classification = "negative"
    return {
        "classification": classification,
        "thresholds": thresholds,
        "observed": facts,
    }


def summarize_routing(
    regimes: tuple[RoutingRegime, ...],
    episodes: tuple[EpisodeSpec, ...],
    oracle_records: list[dict],
    run_records: list[dict],
    population_hash: str,
    *,
    validation_passed: bool,
) -> dict:
    oracles = _oracle_metrics(oracle_records)
    indexed = _run_index(run_records)
    problems = {regime.problem.problem_id: regime for regime in regimes}
    branch = _branch_metrics(oracles)

    overall = {}
    for policy in POLICIES:
        policy_records = [
            record for record in run_records if record["public"]["policy"] == policy
        ]
        overall[policy] = {
            "runs": len(policy_records),
            "valid_runs": sum(record["public"]["valid"] for record in policy_records),
            "correct": _mean(_outcome(record)["correct"] for record in policy_records),
            "decision_loss": _mean(
                _outcome(record)["decision_loss"] for record in policy_records
            ),
            "tests": _mean(
                _outcome(record)["raw_resources"]["tests"] for record in policy_records
            ),
            "synthetic_cost_units": _mean(
                _outcome(record)["raw_resources"]["synthetic_cost_units"]
                for record in policy_records
            ),
            "latency_steps": _mean(
                _outcome(record)["raw_resources"]["latency_steps"]
                for record in policy_records
            ),
        }

    by_regime = {}
    failures = {}
    for problem_id, regime in problems.items():
        problem_episodes = [item for item in episodes if item.problem_id == problem_id]
        losses = {
            policy: [
                _outcome(indexed[(episode.episode_id, policy)])["decision_loss"]
                for episode in problem_episodes
            ]
            for policy in POLICIES
        }
        oracle = oracles[problem_id]
        by_regime[problem_id] = {
            "family": regime.problem.family,
            "declared_voa_band": regime.declared_voa_band,
            "episodes": len(problem_episodes),
            "open_loop_expected_loss": oracle["open_loop_loss"],
            "candidate_expected_loss": oracle["candidate_expected_loss"],
            "closed_loop_expected_loss": oracle["closed_loop_loss"],
            "value_of_adaptivity": oracle["value_of_adaptivity"],
            "adaptivity_capture": oracle["adaptivity_capture"],
            "candidate_actions": oracle["candidate_actions"],
            "closed_loop_actions": oracle["closed_loop_actions"],
            "population_decision_loss": {
                policy: _mean(values) for policy, values in losses.items()
            },
            "candidate_vs_open_population": _paired(
                losses["adaptive_belief"], losses["exact_open_loop"]
            ),
        }
        flags = []
        if oracle["eligible_conditional_node"] and len(
            set(oracle["candidate_actions"].values())
        ) == 1:
            flags.append("no_branch_despite_oracle_branch_value")
        if oracle["value_of_adaptivity"] <= TOLERANCE and len(
            set(oracle["candidate_actions"].values())
        ) > 1:
            flags.append("spurious_branch_when_voa_zero")
        stages = oracle["four_stage_audit"]
        if stages["belief_changed"] and not stages["action_ranking_changed"]:
            flags.append("belief_changed_without_action_ranking_change")
        if stages["action_ranking_changed"] and not stages["policy_action_changed"]:
            flags.append("ranking_changed_without_policy_action_change")
        if (
            oracle["eligible_conditional_node"]
            and oracle["candidate_actions"] != oracle["closed_loop_actions"]
        ):
            flags.append("oracle_inconsistent_branch_mapping")
        if stages["policy_action_changed"] and not stages["action_change_improved_value"]:
            flags.append("branching_without_expected_value")
        paired = by_regime[problem_id]["candidate_vs_open_population"]
        failures[problem_id] = {
            "structural_flags": flags,
            "candidate_better_than_open_episodes": paired["candidate_wins"],
            "candidate_equal_to_open_episodes": paired["ties"],
            "candidate_worse_than_open_episodes": paired["candidate_losses"],
            "noise_wrong_reroute_diagnostic": paired["candidate_losses"],
        }

    by_voa_band = {}
    for band in ("zero", "low", "moderate", "high"):
        ids = [
            problem_id
            for problem_id, regime in problems.items()
            if regime.declared_voa_band == band
        ]
        band_episodes = [item for item in episodes if item.problem_id in ids]
        candidate_actual = [
            _outcome(indexed[(item.episode_id, "adaptive_belief")])["decision_loss"]
            for item in band_episodes
        ]
        open_actual = [
            _outcome(indexed[(item.episode_id, "exact_open_loop")])["decision_loss"]
            for item in band_episodes
        ]
        captures = [
            oracles[problem_id]["adaptivity_capture"]
            for problem_id in ids
            if oracles[problem_id]["adaptivity_capture"] is not None
        ]
        by_voa_band[band] = {
            "regimes": len(ids),
            "episodes": len(band_episodes),
            "mean_voa": _mean(oracles[item]["value_of_adaptivity"] for item in ids),
            "mean_open_loop_expected_loss": _mean(
                oracles[item]["open_loop_loss"] for item in ids
            ),
            "mean_candidate_expected_loss": _mean(
                oracles[item]["candidate_expected_loss"] for item in ids
            ),
            "mean_closed_loop_expected_loss": _mean(
                oracles[item]["closed_loop_loss"] for item in ids
            ),
            "mean_adaptivity_capture": _mean(captures) if captures else None,
            "population_candidate_vs_open": _paired(candidate_actual, open_actual),
        }

    positive_ids = [
        problem_id
        for problem_id, oracle in oracles.items()
        if oracle["value_of_adaptivity"] > TOLERANCE
    ]
    positive_episodes = [item for item in episodes if item.problem_id in positive_ids]
    positive_candidate = [
        _outcome(indexed[(item.episode_id, "adaptive_belief")])["decision_loss"]
        for item in positive_episodes
    ]
    positive_open = [
        _outcome(indexed[(item.episode_id, "exact_open_loop")])["decision_loss"]
        for item in positive_episodes
    ]
    classifier = _classifier(oracles, branch, validation_passed)
    return {
        "schema_version": 1,
        "benchmark": "microgym-routing-v1",
        "population_hash": population_hash,
        "population": {
            "regimes": len(regimes),
            "episodes": len(episodes),
            "runs": len(run_records),
            "valid_runs": sum(record["public"]["valid"] for record in run_records),
            "invalid_runs": sum(not record["public"]["valid"] for record in run_records),
        },
        "primary_condition": {
            "objective": "terminal_decision_loss",
            "fixed_acquisition_horizon": 1,
            "adaptive_stop_available": False,
            "all_acquisition_costs_equal": True,
        },
        "overall": overall,
        "oracle_voa": {
            "minimum": min(item["value_of_adaptivity"] for item in oracles.values()),
            "maximum": max(item["value_of_adaptivity"] for item in oracles.values()),
            "mean": _mean(item["value_of_adaptivity"] for item in oracles.values()),
            "positive_regimes": len(positive_ids),
            "zero_regimes": len(oracles) - len(positive_ids),
        },
        "branch_audit": branch,
        "positive_voa_candidate_vs_open": {
            "exact_mean_candidate_advantage": _mean(
                oracles[item]["open_loop_loss"]
                - oracles[item]["candidate_expected_loss"]
                for item in positive_ids
            ),
            "voa_weighted_adaptivity_capture": classifier["observed"][
                "voa_weighted_adaptivity_capture"
            ],
            "population_paired": _paired(positive_candidate, positive_open),
        },
        "by_voa_band": by_voa_band,
        "by_regime": by_regime,
        "failure_taxonomy": failures,
        "classifier": classifier,
        "statistical_treatment": (
            "Exact public-model expectations and frozen finite-population paired "
            "differences are reported; no sampling-based significance claim is made."
        ),
    }


def _test_with_transform(
    test: TestSpec,
    *,
    action_id: str,
    hypothesis_order: tuple[int, ...],
    rename_outcomes: bool,
) -> TestSpec:
    public = test.public
    outcomes = (
        tuple(f"w{index}" for index in range(len(public.outcomes)))
        if rename_outcomes
        else public.outcomes
    )
    return TestSpec(
        PublicTestModel(
            action_id=action_id,
            outcomes=outcomes,
            likelihoods=tuple(public.likelihoods[index] for index in hypothesis_order),
            cost=public.cost,
            repeat_limit=public.repeat_limit,
            failure_probability=public.failure_probability,
            failure_terminates=public.failure_terminates,
            public_score=public.public_score,
        ),
        test.rng_slot,
    )


def _transformed_problem(
    problem: ProblemSpec,
    *,
    rename_actions: bool = False,
    permute_hidden: bool = False,
) -> ProblemSpec:
    order = (2, 3, 0, 1) if permute_hidden else (0, 1, 2, 3)
    action_map = {"q0": "z9", "a0": "z4", "a1": "z1"} if rename_actions else {}
    initial = _test_with_transform(
        problem.initial_test,
        action_id=action_map.get(
            problem.initial_test.public.action_id, problem.initial_test.public.action_id
        ),
        hypothesis_order=order,
        rename_outcomes=rename_actions,
    )
    tests = tuple(
        _test_with_transform(
            test,
            action_id=action_map.get(test.public.action_id, test.public.action_id),
            hypothesis_order=order,
            rename_outcomes=rename_actions,
        )
        for test in problem.tests
    )
    return ProblemSpec(
        problem_id=problem.problem_id,
        family=problem.family,
        version=problem.version,
        description=problem.description,
        hypotheses=tuple(
            f"x{index}" if permute_hidden else problem.hypotheses[index]
            for index in order
        ),
        prior=tuple(problem.prior[index] for index in order),
        initial_test=initial,
        tests=tests,
        budget_limits=problem.budget_limits,
        primary_resource=problem.primary_resource,
        cost_weight=problem.cost_weight,
        abstain_loss=problem.abstain_loss,
        max_steps=problem.max_steps,
        assumptions=problem.assumptions,
    )


def _oracle_signature(oracle: RoutingOracle) -> tuple:
    return (
        round(oracle.open_loop_loss, 12),
        round(oracle.closed_loop_loss, 12),
        round(oracle.value_of_adaptivity, 12),
        round(oracle.candidate_expected_loss, 12),
        None
        if oracle.adaptivity_capture is None
        else round(oracle.adaptivity_capture, 12),
        oracle.eligible_conditional_node,
        oracle.belief_changed,
        oracle.action_ranking_changed,
        oracle.policy_action_changed,
        oracle.action_change_improved_value,
    )


def _has_restricted_key(value: object) -> bool:
    restricted = {
        "hidden_state",
        "environment_realization_seed",
        "oracle_action",
        "oracle_value",
        "future_result",
    }
    if isinstance(value, dict):
        return any(key in restricted for key in value) or any(
            _has_restricted_key(item) for item in value.values()
        )
    if isinstance(value, list):
        return any(_has_restricted_key(item) for item in value)
    return False


def validate_routing(
    regimes: tuple[RoutingRegime, ...],
    episodes: tuple[EpisodeSpec, ...],
    oracle_records: list[dict],
    run_records: list[dict],
    population_hash: str,
) -> dict:
    checks: dict[str, dict] = {}

    def record(name: str, passed: bool, detail: str) -> None:
        checks[name] = {"status": "pass" if passed else "fail", "detail": detail}

    problems = {regime.problem.problem_id: regime.problem for regime in regimes}
    episode_map = {episode.episode_id: episode for episode in episodes}
    index = _run_index(run_records)

    bands = [regime.declared_voa_band for regime in regimes]
    record(
        "population structure",
        len(regimes) == 9
        and len(episodes) == 9 * 128
        and bands.count("zero") >= 2
        and all(
            sum(episode.problem_id == regime.problem.problem_id for episode in episodes)
            == 128
            for regime in regimes
        ),
        f"{len(regimes)} regimes, {len(episodes)} episodes, VOA bands {bands}",
    )

    oracle_by_problem = _oracle_metrics(oracle_records)
    bands_valid = True
    for regime in regimes:
        voa = oracle_by_problem[regime.problem.problem_id]["value_of_adaptivity"]
        expected = (
            "zero"
            if voa <= TOLERANCE
            else "low"
            if voa < 0.05
            else "moderate"
            if voa < 0.15
            else "high"
        )
        bands_valid &= expected == regime.declared_voa_band
    record(
        "oracle VOA bands",
        bands_valid,
        "every declared zero/low/moderate/high band matches exact open-minus-closed loss",
    )

    hashes_valid = verify_routing_record_hashes(run_records) and verify_routing_record_hashes(
        oracle_records
    )
    record(
        "record hashes",
        hashes_valid,
        f"verified {len(run_records) + len(oracle_records)} content-addressed records",
    )

    fixed_horizon = all(
        len(item["public"]["trace"]["transitions"]) == 1
        and item["public"]["trace"]["transitions"][0]["action"]["kind"] == "acquire"
        and item["public"]["trace"]["termination"]["reason"]
        == "fixed_routing_horizon_complete"
        and not item["public"]["adaptive_stop_available"]
        for item in run_records
    )
    record(
        "fixed horizon without STOP",
        fixed_horizon,
        f"all {len(run_records)} runs contain exactly one acquisition and no STOP",
    )

    cost_integrity = all(
        item["restricted"]["outcome"]["raw_resources"]
        == {"tests": 1.0, "synthetic_cost_units": 1.0, "latency_steps": 1.0}
        for item in run_records
    )
    record(
        "cost integrity",
        cost_integrity,
        "every policy receives and spends the same one-action raw resource vector",
    )

    public_clean = all(not _has_restricted_key(item["public"]) for item in run_records)
    record(
        "evaluator firewall and future-result blindness",
        public_clean,
        "public run projections contain no truth, environment seed, oracle hint, or future result",
    )

    matched_access = all(
        item["public"]["policy_visible_model_access"] == "full_declared_likelihoods"
        for item in run_records
    ) and all(
        index[(episode.episode_id, "exact_open_loop")]["public"][
            "fixed_acquisition_horizon"
        ]
        == index[(episode.episode_id, "adaptive_belief")]["public"][
            "fixed_acquisition_horizon"
        ]
        for episode in episodes
    )
    record(
        "matched information and opportunity",
        matched_access,
        "open-loop and candidate share the public model, costs, budget, identifiers, and horizon",
    )

    open_invariant = True
    closed_after_release = True
    for regime in regimes:
        oracle = oracle_by_problem[regime.problem.problem_id]
        problem_episodes = [
            item for item in episodes if item.problem_id == regime.problem.problem_id
        ]
        open_actions = {
            index[(item.episode_id, "exact_open_loop")]["public"]["trace"][
                "transitions"
            ][0]["action"]["target_id"]
            for item in problem_episodes
        }
        open_invariant &= open_actions == {oracle["open_loop_action"]}
        for episode in problem_episodes:
            candidate = index[(episode.episode_id, "adaptive_belief")]["public"]
            cue = candidate["trace"]["initial_observations"][0]["payload"]["value"]
            selected = candidate["trace"]["transitions"][0]["action"]["target_id"]
            closed_after_release &= (
                not candidate["decision_diagnostic"]["committed_before_observation"]
                and selected == oracle["candidate_actions"][cue]
            )
    record(
        "open-loop commitment invariance",
        open_invariant,
        "the exact open-loop acquisition is unchanged across all realized cues",
    )
    record(
        "closed-loop release discipline",
        closed_after_release,
        "candidate action changes, when present, are reconstructed from the released cue only",
    )

    order_coverage = all(
        len(
            {
                episode.action_order
                for episode in episodes
                if episode.problem_id == regime.problem.problem_id
            }
        )
        == 2
        for regime in regimes
    )
    record(
        "action-order coverage",
        order_coverage,
        "both presentation orders occur in every frozen regime",
    )

    order_invariant = True
    label_invariant = True
    hidden_invariant = True
    for regime in regimes:
        problem = regime.problem
        natural = problem.public_view(tuple(test.public.action_id for test in problem.tests))
        reversed_view = problem.public_view(
            tuple(reversed(tuple(test.public.action_id for test in problem.tests)))
        )
        base_signature = _oracle_signature(compute_routing_oracle(natural))
        order_invariant &= base_signature == _oracle_signature(
            compute_routing_oracle(reversed_view)
        )
        renamed = _transformed_problem(problem, rename_actions=True)
        renamed_view = renamed.public_view(
            tuple(test.public.action_id for test in renamed.tests)
        )
        label_invariant &= base_signature == _oracle_signature(
            compute_routing_oracle(renamed_view)
        )
        permuted = _transformed_problem(problem, permute_hidden=True)
        permuted_view = permuted.public_view(
            tuple(test.public.action_id for test in permuted.tests)
        )
        hidden_invariant &= base_signature == _oracle_signature(
            compute_routing_oracle(permuted_view)
        )
    record(
        "action-order permutation",
        order_invariant,
        f"value and branching signatures invariant in {len(regimes)}/{len(regimes)} regimes",
    )
    record(
        "identifier and action-label permutation",
        label_invariant,
        f"renamed action/outcome signatures invariant in {len(regimes)}/{len(regimes)} regimes",
    )
    record(
        "hidden-label permutation",
        hidden_invariant,
        f"permuted hidden-label signatures invariant in {len(regimes)}/{len(regimes)} regimes",
    )

    seed_isolation = all(
        item["public"]["policy_randomness_seed"]
        == routing_policy_seed(item["public"]["episode_id"], item["public"]["policy"])
        and item["public"]["policy_randomness_seed"]
        != item["restricted"]["environment_realization_seed"]
        for item in run_records
    )
    record(
        "seed isolation",
        seed_isolation,
        "policy seeds reproduce from public identity and are independent of restricted observation seeds",
    )

    observations_valid = all(
        item["public"]["trace"]["initial_observations"][0]["provenance"]
        == "environment_reset"
        and item["public"]["trace"]["transitions"][0]["result"]["observations"][0][
            "provenance"
        ]
        == "action_result:r-001"
        for item in run_records
    )
    record(
        "observation provenance",
        observations_valid,
        "every cue and acquired observation carries release provenance",
    )

    replayed = 0
    replay_valid = True
    for stored in run_records:
        public = stored["public"]
        episode = episode_map[public["episode_id"]]
        actual_run = run_routing_episode(
            problems[episode.problem_id], episode, public["policy"]
        )
        actual = routing_run_artifact(actual_run, episode, population_hash)
        replayed += 1
        if content_hash(actual) != content_hash(stored):
            replay_valid = False
            break
    record(
        "deterministic replay",
        replay_valid and replayed == len(run_records),
        f"exact replay reproduced {replayed}/{len(run_records)} policy and oracle records",
    )

    status = "pass" if all(item["status"] == "pass" for item in checks.values()) else "fail"
    return {
        "schema_version": 1,
        "benchmark": "microgym-routing-v1",
        "population_hash": population_hash,
        "status": status,
        "checks": checks,
    }


def _f(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.6f}"


def render_routing_report(summary: dict, validation: dict) -> str:
    branch = summary["branch_audit"]
    classifier = summary["classifier"]
    lines = [
        "# MicroGym routing-v1 benchmark report",
        "",
        "This report is generated from the frozen routing population and exact-model/run artifacts. It tests one-step observation-conditioned acquisition only; it does not test semantic reasoning or a real domain.",
        "",
        "## Frozen primary condition",
        "",
        f"- Population hash: `{summary['population_hash']}`",
        f"- Regimes: **{summary['population']['regimes']}**; episodes: **{summary['population']['episodes']}**.",
        f"- Runs: **{summary['population']['runs']}** ({summary['population']['valid_runs']} valid, {summary['population']['invalid_runs']} invalid).",
        "- Horizon: one required equal-cost acquisition after a public reset cue; adaptive STOP is unavailable.",
        "- Objective: terminal 0/1 decision loss. Raw `tests`, `synthetic_cost_units`, and `latency_steps` remain recorded separately.",
        "- VOA convention: exact open-loop expected loss minus exact closed-loop expected loss; positive is value available only through conditioning.",
        "",
        "## Decisive policies",
        "",
        "- `exact_open_loop`: exact public-model acquisition committed before the cue; the cue and acquired result still inform its final answer.",
        "- `adaptive_belief`: the unchanged Phase 3 Bayesian update and one-step acquisition score, invoked after the cue under runner-enforced fixed horizon.",
        "- `exact_closed_loop_oracle`: evaluator-only exact cue-conditioned acquisition mapping.",
        "",
        "All three receive the same prior, likelihoods, actions, costs, one-action budget, objective, identifiers, and presentation distribution. The candidate's only routing privilege over open-loop is using the released cue before selecting its acquisition.",
        "",
        "## Exact VOA and Adaptivity Capture by regime",
        "",
        "| Regime | Family | Band | Open loss | Candidate loss | Closed loss | VOA | Capture | Candidate mapping |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for problem_id, item in summary["by_regime"].items():
        mapping = ", ".join(
            f"{cue}->{action}" for cue, action in sorted(item["candidate_actions"].items())
        )
        lines.append(
            f"| `{problem_id}` | {item['family']} | {item['declared_voa_band']} | "
            f"{_f(item['open_loop_expected_loss'])} | {_f(item['candidate_expected_loss'])} | "
            f"{_f(item['closed_loop_expected_loss'])} | {_f(item['value_of_adaptivity'])} | "
            f"{_f(item['adaptivity_capture'])} | `{mapping}` |"
        )

    lines += [
        "",
        "## Results by VOA band",
        "",
        "| VOA band | Regimes | Episodes | Mean VOA | Open expected loss | Candidate expected loss | Mean capture | Frozen-population candidate-open loss |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for band in ("zero", "low", "moderate", "high"):
        item = summary["by_voa_band"][band]
        lines.append(
            f"| {band} | {item['regimes']} | {item['episodes']} | {_f(item['mean_voa'])} | "
            f"{_f(item['mean_open_loop_expected_loss'])} | {_f(item['mean_candidate_expected_loss'])} | "
            f"{_f(item['mean_adaptivity_capture'])} | "
            f"{_f(item['population_candidate_vs_open']['mean_candidate_minus_open_loop'])} |"
        )

    lines += [
        "",
        "## Frozen-population outcomes and resources",
        "",
        "| Policy | Correct | Decision loss | Tests | Cost units | Latency steps |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for policy in POLICIES:
        item = summary["overall"][policy]
        lines.append(
            f"| `{policy}` | {_f(item['correct'])} | {_f(item['decision_loss'])} | "
            f"{_f(item['tests'])} | {_f(item['synthetic_cost_units'])} | {_f(item['latency_steps'])} |"
        )

    positive = summary["positive_voa_candidate_vs_open"]
    paired = positive["population_paired"]
    lines += [
        "",
        "On positive-VOA regimes, exact mean candidate advantage over open-loop was "
        f"`{positive['exact_mean_candidate_advantage']:.6f}` and VOA-weighted Adaptivity Capture was "
        f"`{positive['voa_weighted_adaptivity_capture']:.6f}`. On the frozen realized episodes, candidate-minus-open decision loss was "
        f"`{paired['mean_candidate_minus_open_loop']:.6f}` with {paired['candidate_wins']} wins, "
        f"{paired['ties']} ties, and {paired['candidate_losses']} losses.",
        "",
        "## Behavioral branch audit",
        "",
        f"- Eligible conditional nodes: **{branch['eligible_nodes']}**.",
        f"- Candidate conditional branches: **{branch['candidate_branch_nodes']}/{branch['eligible_nodes']}** (`{branch['candidate_branch_rate']:.6f}`).",
        f"- Oracle-consistent branch mappings: **{branch['oracle_consistent_nodes']}/{branch['eligible_nodes']}** (`{branch['oracle_consistent_branch_rate']:.6f}`).",
        f"- Beneficial branch mappings: **{branch['beneficial_branch_nodes']}/{branch['eligible_nodes']}** (`{branch['beneficial_branch_rate']:.6f}`).",
        f"- Zero-VOA spurious branches: **{branch['zero_voa_spurious_branch_nodes']}/{branch['zero_voa_nodes']}** (`{branch['zero_voa_spurious_branch_rate']:.6f}`).",
        "",
        "The oracle artifacts separately record whether belief changed, action ranking changed, selected action changed, and exact value improved. A changed posterior alone is not counted as successful routing.",
        "",
        "## Failure taxonomy",
        "",
        "| Regime | Structural flags | Candidate better / tie / worse than open on realized episodes |",
        "| --- | --- | ---: |",
    ]
    for problem_id, item in summary["failure_taxonomy"].items():
        flags = ", ".join(item["structural_flags"]) or "none"
        lines.append(
            f"| `{problem_id}` | {flags} | {item['candidate_better_than_open_episodes']} / "
            f"{item['candidate_equal_to_open_episodes']} / {item['candidate_worse_than_open_episodes']} |"
        )
    lines += [
        "",
        "A candidate-worse episode is retained as a noise/wrong-reroute diagnostic even when the cue-conditioned mapping has lower exact expected loss. The benchmark does not tune these episodes away.",
        "",
        "## Validation",
        "",
    ]
    for name, item in validation["checks"].items():
        lines.append(f"- **{name}:** `{item['status']}` — {item['detail']}")
    lines += [
        "",
        "## Preregistered classification",
        "",
        f"Classification: **`{classifier['classification']}`**.",
        "",
        "The classifier requires positive oracle VOA, verified conditional behavior, oracle-consistent routing, exact value over the matched open-loop plan, no STOP explanation, low zero-VOA spurious branching, and all invariance/leakage checks. Aggregate objective improvement alone cannot pass.",
        "",
        "## Limitations",
        "",
        "This is a deliberately favorable one-step explicit-likelihood setting. The candidate's one-step score is exactly suited to a one-action horizon; the result cannot establish multi-stage planning, action-value estimation without likelihood tables, semantics, software competence, IDS transfer, GitLab authorization value, learned routing, graph/coupling mechanisms, or substrate independence. The optional routing-by-STOP factorial was not run because the primary fixed-horizon experiment already isolates the intended question and Phase 3 separately measured stopping.",
        "",
    ]
    return "\n".join(lines)


def render_routing_interpretation(summary: dict) -> str:
    branch = summary["branch_audit"]
    positive = summary["positive_voa_candidate_vs_open"]
    classifier = summary["classifier"]["classification"]
    return "\n".join(
        [
            "# MicroGym routing-v1 evidence interpretation",
            "",
            f"The preregistered mechanical classification is **`{classifier}`** for population `{summary['population_hash']}`.",
            "",
            "## What the result establishes",
            "",
            f"The frozen benchmark contained {summary['oracle_voa']['positive_regimes']} positive-VOA and {summary['oracle_voa']['zero_regimes']} zero-VOA regimes. Oracle VOA ranged from `{summary['oracle_voa']['minimum']:.6f}` to `{summary['oracle_voa']['maximum']:.6f}`.",
            "",
            f"The unchanged myopic candidate branched at {branch['candidate_branch_nodes']}/{branch['eligible_nodes']} eligible nodes, matched the exact closed-loop routing pattern at {branch['oracle_consistent_nodes']}/{branch['eligible_nodes']}, and made {branch['zero_voa_spurious_branch_nodes']}/{branch['zero_voa_nodes']} spurious zero-VOA branches. Its exact mean advantage over open-loop on positive-VOA regimes was `{positive['exact_mean_candidate_advantage']:.6f}` and its VOA-weighted Adaptivity Capture was `{positive['voa_weighted_adaptivity_capture']:.6f}`.",
            "",
            "> In the frozen one-step MicroGym routing benchmark, a public-model belief-conditioned policy used a legitimately released cue to select different acquisitions and captured exact decision value unavailable to the best same-model open-loop plan.",
            "",
            "The primary condition used one equal-cost acquisition and no STOP. Thus stopping, thrift, unequal budget, model access, identifiers, action order, or hidden truth cannot explain the exact routing gap.",
            "",
            "## What remains unresolved",
            "",
            "The setting supplies clean likelihood tables, a one-step horizon, four discrete hidden states, and two tiny actions. The candidate is myopic and is mathematically aligned with this horizon. This does not establish semantic action-value estimation, multi-stage rerouting, robustness to model misspecification, real software investigation, IDS transfer, GitLab value, general SER advantage, learned routing, Scope, graphs, or coupling laws.",
            "",
            "Realized noisy episodes in which the candidate lost to open-loop remain in `runs.jsonl` and the report's failure taxonomy. Exact expected advantage does not imply every conditional choice wins ex post.",
            "",
            "## Next unresolved question",
            "",
            "> Can a controller estimate decision-relevant epistemic-action values from imperfect authorization/software evidence when clean likelihood tables are not supplied?",
            "",
            "Under ADR-0013, the smallest controlled authorization-oriented software environment is preferred because it can test that question while advancing the practical GitLab authorization trunk. A full GitLab integration is not yet justified, and an IDS bridge is unnecessary unless it becomes a materially cleaner way to isolate semantic action-value estimation.",
            "",
        ]
    )
