"""Scientific-validity checks for a completed frozen MicroGym sweep."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import fields, replace

from ser.microgym.environment import MicroGymEnvironment
from ser.microgym.model import (
    EpisodeSpec,
    ProblemSpec,
    PublicProblemView,
    PublicTestModel,
    TestSpec,
)
from ser.microgym.oracle import OracleReferencePolicy
from ser.policies import AdaptiveBeliefPolicy, RandomPolicy, policy_suite
from ser.policies.base import BeliefPolicy

from .artifacts import verify_record_hash
from .runner import RunRecord, evaluate_run, replay_trace, run_episode


def _check(status: bool, detail: str) -> dict[str, str]:
    return {"status": "pass" if status else "fail", "detail": detail}


def _cost_dict(trace) -> dict[str, float]:
    if trace.transitions:
        schema = trace.transitions[0].result.cost.schema
    else:
        raise ValueError("a valid policy trace must contain STOP or a termination")
    total = schema.vector()
    for transition in trace.transitions:
        total = total + transition.result.cost
    return total.as_dict()


def _behavior_signature(problem: ProblemSpec, episode: EpisodeSpec) -> tuple:
    oracle = run_episode(
        problem,
        episode,
        OracleReferencePolicy(),
        allow_evaluator_policy=True,
    )
    run = run_episode(problem, episode, AdaptiveBeliefPolicy())
    outcome = evaluate_run(run, oracle, problem, episode)
    return (
        outcome.correct,
        outcome.abstained,
        round(outcome.decision_loss, 12),
        tuple(outcome.raw_resources.values),
        round(outcome.combined_objective, 12),
        len(run.trace.transitions),
        run.trace.termination.cause.value if run.trace.termination else None,
    )


def _rename_test(
    test: TestSpec,
    action_names: dict[str, str],
    outcome_prefix: str,
) -> TestSpec:
    outcomes = tuple(
        f"{outcome_prefix}{len(test.public.outcomes) - index - 1}"
        for index in range(len(test.public.outcomes))
    )
    return replace(
        test,
        public=replace(
            test.public,
            action_id=action_names[test.public.action_id],
            outcomes=outcomes,
        ),
    )


def _scramble_identifiers(
    problem: ProblemSpec, episode: EpisodeSpec
) -> tuple[ProblemSpec, EpisodeSpec]:
    all_tests = (problem.initial_test,) + problem.tests
    original_actions = [test.public.action_id for test in all_tests]
    action_names = {
        action_id: f"q{len(original_actions) - index - 1}"
        for index, action_id in enumerate(original_actions)
    }
    hypothesis_names = {
        hypothesis: f"h{len(problem.hypotheses) - index - 1}"
        for index, hypothesis in enumerate(problem.hypotheses)
    }
    renamed_initial = _rename_test(problem.initial_test, action_names, "i")
    renamed_tests = tuple(
        _rename_test(test, action_names, f"z{index}-")
        for index, test in enumerate(problem.tests)
    )
    renamed_problem = replace(
        problem,
        hypotheses=tuple(hypothesis_names[item] for item in problem.hypotheses),
        initial_test=renamed_initial,
        tests=renamed_tests,
    )
    renamed_episode = replace(
        episode,
        hidden_state=hypothesis_names[episode.hidden_state],
        action_order=tuple(action_names[item] for item in episode.action_order),
    )
    return renamed_problem, renamed_episode


def _permute_hidden_states(
    problem: ProblemSpec, episode: EpisodeSpec
) -> tuple[ProblemSpec, EpisodeSpec]:
    def reorder(test: TestSpec) -> TestSpec:
        return replace(
            test,
            public=replace(test.public, likelihoods=tuple(reversed(test.public.likelihoods))),
        )

    return (
        replace(
            problem,
            hypotheses=tuple(reversed(problem.hypotheses)),
            prior=tuple(reversed(problem.prior)),
            initial_test=reorder(problem.initial_test),
            tests=tuple(reorder(test) for test in problem.tests),
        ),
        episode,
    )


def _invariance_checks(
    problems: tuple[ProblemSpec, ...], episodes: tuple[EpisodeSpec, ...]
) -> dict[str, dict[str, str]]:
    by_problem = {problem.problem_id: problem for problem in problems}
    representatives: list[EpisodeSpec] = []
    seen_families: set[str] = set()
    for episode in episodes:
        family = by_problem[episode.problem_id].family
        if family not in seen_families:
            seen_families.add(family)
            representatives.append(episode)
    identifier_matches = 0
    order_matches = 0
    hidden_matches = 0
    for episode in representatives:
        problem = by_problem[episode.problem_id]
        reference = _behavior_signature(problem, episode)
        scrambled_problem, scrambled_episode = _scramble_identifiers(problem, episode)
        identifier_matches += _behavior_signature(scrambled_problem, scrambled_episode) == reference
        reversed_episode = replace(episode, action_order=tuple(reversed(episode.action_order)))
        order_matches += _behavior_signature(problem, reversed_episode) == reference
        permuted_problem, permuted_episode = _permute_hidden_states(problem, episode)
        hidden_matches += _behavior_signature(permuted_problem, permuted_episode) == reference
    count = len(representatives)
    return {
        "identifier scrambling": _check(
            identifier_matches == count,
            f"adaptive outcome/resource signatures invariant in {identifier_matches}/{count} family representatives after renaming hypotheses, actions, and outcomes",
        ),
        "action-order permutation": _check(
            order_matches == count,
            f"adaptive outcome/resource signatures invariant in {order_matches}/{count} family representatives after reversing presentation order",
        ),
        "hidden-state permutation": _check(
            hidden_matches == count,
            f"adaptive outcome/resource signatures invariant in {hidden_matches}/{count} family representatives after permuting hypothesis rows and labels",
        ),
    }


class _FirewallProbePolicy(BeliefPolicy):
    name = "firewall_probe"

    def reset(self, view, initial_observations, seed):
        getattr(view, "hidden_state")
        return super().reset(view, initial_observations, seed)


def validate_experiment(
    problems: tuple[ProblemSpec, ...],
    episodes: tuple[EpisodeSpec, ...],
    runs: list[RunRecord],
    oracle_runs: list[RunRecord],
    run_artifacts: list[dict],
    oracle_artifacts: list[dict],
    population_hash: str,
) -> dict:
    """Run replay, boundary, hash, accounting, and invariance checks."""

    del population_hash
    problem_by_id = {problem.problem_id: problem for problem in problems}
    episode_by_id = {episode.episode_id: episode for episode in episodes}
    artifacts_by_id = {item["public"]["run_id"]: item for item in run_artifacts}
    first_problem = problems[0]
    first_episode = episodes[0]
    checks: dict[str, dict[str, str]] = {}

    family_episodes = Counter(
        problem_by_id[episode.problem_id].family for episode in episodes
    )
    checks["population scale"] = _check(
        len(problems) >= 20
        and len(family_episodes) >= 5
        and min(family_episodes.values()) >= 100,
        f"{len(problems)} regimes, {len(episodes)} episodes, family counts {dict(sorted(family_episodes.items()))}",
    )

    replay_failures: list[str] = []
    for run in [*oracle_runs, *runs]:
        episode = episode_by_id[run.episode_id]
        problem = problem_by_id[episode.problem_id]
        replayed, detail = replay_trace(problem, episode, run.trace)
        if not replayed:
            replay_failures.append(f"{run.run_id}:{detail}")
    total_replays = len(oracle_runs) + len(runs)
    checks["deterministic replay"] = _check(
        not replay_failures,
        f"exact public replay passed for {total_replays}/{total_replays} oracle and policy traces"
        if not replay_failures
        else "; ".join(replay_failures[:5]),
    )

    all_artifacts = [*run_artifacts, *oracle_artifacts]
    valid_hashes = sum(verify_record_hash(item) for item in all_artifacts)
    checks["record hashes"] = _check(
        valid_hashes == len(all_artifacts),
        f"verified {valid_hashes}/{len(all_artifacts)} content-addressed records",
    )

    cost_errors: list[str] = []
    release_errors: list[str] = []
    model_access = set()
    action_failures = 0
    environment_terminations = 0
    for run in runs:
        artifact = artifacts_by_id[run.run_id]
        model_access.add(run.policy_visible_model_access)
        raw = artifact["restricted"]["outcome"]["raw_resources"]
        if _cost_dict(run.trace) != raw:
            cost_errors.append(f"{run.run_id}:raw_total")
        for observation in run.trace.initial_observations:
            if observation.release_step != 0 or observation.source_result_id is not None:
                release_errors.append(f"{run.run_id}:{observation.observation_id}")
        for transition in run.trace.transitions:
            if transition.result.status == "failed":
                action_failures += 1
            if (
                transition.result.termination is not None
                and transition.result.termination.cause.value == "environment_termination"
            ):
                environment_terminations += 1
            before = dict(transition.budget_before)
            after = dict(transition.budget_after)
            for dimension in before:
                expected = before[dimension] - transition.result.cost.get(dimension)
                if abs(after[dimension] - expected) > 1e-9:
                    cost_errors.append(
                        f"{run.run_id}:budget:{transition.transition_id}:{dimension}"
                    )
            for observation in transition.result.observations:
                if (
                    observation.release_step != transition.step
                    or observation.source_result_id != transition.result.result_id
                ):
                    release_errors.append(f"{run.run_id}:{observation.observation_id}")
    checks["cost integrity"] = _check(
        not cost_errors,
        f"trace costs, componentwise budgets, and evaluator totals agree across {len(runs)} runs"
        if not cost_errors
        else "; ".join(cost_errors[:5]),
    )
    checks["observation release"] = _check(
        not release_errors,
        f"all released observations carry step and result provenance across {len(runs)} runs"
        if not release_errors
        else "; ".join(release_errors[:5]),
    )
    checks["failed-run preservation"] = _check(
        action_failures > 0 and environment_terminations > 0,
        f"artifacts retain {action_failures} failed actions and {environment_terminations} environment terminations; validity remains explicit",
    )
    checks["matched public model access"] = _check(
        model_access == {"full_declared_likelihoods"}
        and all(run.policy_access_class == "public_episode" for run in runs),
        "all normal policies received the same public prior, declared likelihoods, costs, legal actions, released history, and budget projection",
    )

    artifact_seed_errors = []
    for run in runs:
        episode = episode_by_id[run.episode_id]
        artifact = artifacts_by_id[run.run_id]
        if artifact["public"]["policy_randomness_seed"] != run.policy_randomness_seed:
            artifact_seed_errors.append(f"{run.run_id}:policy_seed")
        if (
            artifact["restricted"]["environment_realization_seed"]
            != episode.environment_seed
        ):
            artifact_seed_errors.append(f"{run.run_id}:environment_seed")
        if run.policy_randomness_seed == episode.environment_seed:
            artifact_seed_errors.append(f"{run.run_id}:seed_collision")
    for artifact in oracle_artifacts:
        episode = episode_by_id[artifact["episode_id"]]
        if artifact["environment_realization_seed"] != episode.environment_seed:
            artifact_seed_errors.append(f"{artifact['episode_id']}:oracle_environment_seed")
    changed_environment = replace(
        first_episode,
        environment_seed=first_episode.environment_seed + 1,
    )
    original_random = run_episode(first_problem, first_episode, RandomPolicy())
    changed_random = run_episode(first_problem, changed_environment, RandomPolicy())
    original_targets = tuple(
        item.action.target_id
        for item in original_random.trace.transitions
        if item.action.kind == "acquire"
    )
    changed_targets = tuple(
        item.action.target_id
        for item in changed_random.trace.transitions
        if item.action.kind == "acquire"
    )
    policy_rng_uncoupled = (
        original_random.policy_randomness_seed == changed_random.policy_randomness_seed
        and original_targets == changed_targets
    )
    checks["seed isolation"] = _check(
        not artifact_seed_errors and policy_rng_uncoupled,
        "population, hidden environment realization, and policy randomness use named domains; evaluator seeds are restricted, policy seeds are public, and perturbing the environment seed leaves random-policy routing unchanged"
        if not artifact_seed_errors and policy_rng_uncoupled
        else "; ".join(artifact_seed_errors[:5]) or "environment perturbation changed policy routing",
    )

    view_fields = {field.name for field in fields(PublicProblemView)}
    test_fields = {field.name for field in fields(PublicTestModel)}
    forbidden = {"hidden_state", "seed", "rng_slot", "future_result", "oracle_action"}
    public_projection_safe = not (forbidden & (view_fields | test_fields))
    probe = run_episode(first_problem, first_episode, _FirewallProbePolicy())
    oracle_rejected = False
    try:
        run_episode(first_problem, first_episode, OracleReferencePolicy())
    except PermissionError:
        oracle_rejected = True
    environment = MicroGymEnvironment(first_problem, first_episode)
    environment.reset()
    token_rejected = False
    try:
        environment.restricted_truth(object())
    except PermissionError:
        token_rejected = True
    checks["evaluator firewall"] = _check(
        public_projection_safe
        and not probe.valid
        and probe.invalid_reason == "policy_reset_failure:AttributeError"
        and oracle_rejected
        and token_rejected,
        "public projections omit truth/realization fields; a hidden-state probe fails; evaluator policies and invalid truth tokens are rejected",
    )
    checks["future-result blindness"] = _check(
        "seed" not in view_fields
        and "rng_slot" not in test_fields
        and "future_result" not in view_fields,
        "normal policies receive separate policy-only randomness plus distributions, never the environment seed, RNG slot, or sampled future result",
    )
    opaque = all(
        "test_for" not in test.public.action_id.lower()
        and not any(hypothesis.lower() in test.public.action_id.lower() for hypothesis in problem.hypotheses)
        for problem in problems
        for test in problem.tests
    )
    checks["opaque identifiers"] = _check(
        opaque,
        "action IDs are opaque and contain no hypothesis-target labels",
    )
    orders_by_problem: dict[str, set[tuple[str, ...]]] = defaultdict(set)
    for episode in episodes:
        orders_by_problem[episode.problem_id].add(episode.action_order)
    checks["action-order coverage"] = _check(
        all(len(orders) > 1 for orders in orders_by_problem.values()),
        f"all {len(orders_by_problem)} regimes contain multiple frozen action presentation orders",
    )
    checks.update(_invariance_checks(problems, episodes))

    failed_checks = [name for name, item in checks.items() if item["status"] != "pass"]
    return {
        "schema_version": 1,
        "benchmark": "microgym-v1",
        "status": "pass" if not failed_checks else "fail",
        "failed_checks": failed_checks,
        "policy_assumptions": {
            policy.name: list(policy.assumptions) for policy in policy_suite()
        },
        "oracle_assumptions": list(OracleReferencePolicy.assumptions),
        "counts": {
            "problems": len(problems),
            "episodes": len(episodes),
            "normal_runs": len(runs),
            "oracle_runs": len(oracle_runs),
            "valid_normal_runs": sum(run.valid for run in runs),
            "invalid_normal_runs": sum(not run.valid for run in runs),
            "failed_actions": action_failures,
            "environment_terminations": environment_terminations,
        },
        "checks": checks,
    }
