"""Exact-population summaries, paired descriptive intervals, and failure analysis."""

from __future__ import annotations

import math
import random
from collections import Counter, defaultdict
from statistics import mean


BASELINES = ("fixed_order", "random", "cheap_first", "exhaustive", "greedy")
ABLATIONS = (
    "ablation_no_adaptation",
    "ablation_cost_blind",
    "ablation_information_blind",
    "ablation_no_adaptive_stop",
)
ADAPTIVE = "adaptive_belief"


def _row(record: dict) -> dict:
    public = record["public"]
    outcome = record["restricted"]["outcome"]
    transitions = public["trace"]["transitions"]
    return {
        "episode_id": public["episode_id"],
        "problem_id": public["problem_id"],
        "family": public["family"],
        "policy": public["policy"],
        "valid": outcome["valid"],
        "correct": float(outcome["correct"]),
        "abstained": float(outcome["abstained"]),
        "decision_loss": float(outcome["decision_loss"]),
        "combined_objective": float(outcome["combined_objective"]),
        "decision_regret": float(outcome["decision_regret"]),
        "combined_regret": float(outcome["combined_regret"]),
        "stopping_regret": float(outcome["stopping_regret"]),
        "premature_stop": float(outcome["premature_stop"]),
        "unnecessary_actions": float(outcome["unnecessary_actions"]),
        "avoidable_resource_cost": float(outcome["avoidable_resource_cost"]),
        "tests": float(outcome["raw_resources"]["tests"]),
        "synthetic_cost_units": float(outcome["raw_resources"]["synthetic_cost_units"]),
        "latency_steps": float(outcome["raw_resources"]["latency_steps"]),
        "actions": float(sum(item["action"]["kind"] == "acquire" for item in transitions)),
        "failed_actions": float(sum(item["result"]["status"] == "failed" for item in transitions)),
        "environment_termination": float(
            public["trace"]["termination"] is not None
            and public["trace"]["termination"]["cause"] == "environment_termination"
        ),
        "trace": public["trace"],
    }


def _aggregate(rows: list[dict]) -> dict:
    numeric = (
        "correct",
        "abstained",
        "decision_loss",
        "combined_objective",
        "decision_regret",
        "combined_regret",
        "stopping_regret",
        "premature_stop",
        "unnecessary_actions",
        "avoidable_resource_cost",
        "tests",
        "synthetic_cost_units",
        "latency_steps",
        "actions",
        "failed_actions",
        "environment_termination",
    )
    distributions = {}
    for field in ("tests", "synthetic_cost_units", "latency_steps", "actions"):
        values = [item[field] for item in rows]
        distributions[field] = {
            "min": min(values),
            "p10": _percentile(values, 0.10),
            "p50": _percentile(values, 0.50),
            "p90": _percentile(values, 0.90),
            "max": max(values),
        }
    return {
        "runs": len(rows),
        "valid_runs": sum(bool(item["valid"]) for item in rows),
        "invalid_runs": sum(not bool(item["valid"]) for item in rows),
        **{field: mean(item[field] for item in rows) for field in numeric},
        "distributions": distributions,
    }


def _percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = probability * (len(ordered) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def _paired_effect(
    adaptive: dict[str, dict], baseline: dict[str, dict], field: str, seed: int
) -> dict:
    episode_ids = sorted(set(adaptive) & set(baseline))
    differences = [adaptive[item][field] - baseline[item][field] for item in episode_ids]
    rng = random.Random(seed)
    bootstrap = []
    for _ in range(1000):
        bootstrap.append(mean(differences[rng.randrange(len(differences))] for _ in differences))
    wins = sum(value < -1e-12 for value in differences)
    ties = sum(abs(value) <= 1e-12 for value in differences)
    losses = len(differences) - wins - ties
    return {
        "paired_episodes": len(differences),
        "mean_adaptive_minus_control": mean(differences),
        "descriptive_bootstrap_95": [_percentile(bootstrap, 0.025), _percentile(bootstrap, 0.975)],
        "adaptive_lower_wins": wins,
        "ties": ties,
        "adaptive_lower_losses": losses,
    }


def _conditional_routing(rows: list[dict]) -> dict[str, float]:
    grouped: dict[tuple[str, str, tuple[str, ...]], dict[str, list[str]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for row in rows:
        trace = row["trace"]
        initial = trace["initial_observations"][0]["payload"]["value"]
        prefix: tuple[str, ...] = ()
        condition = str(initial)
        for transition in trace["transitions"]:
            action = transition["action"]
            choice = "STOP" if action["kind"] == "stop" else str(action["target_id"])
            grouped[(row["policy"], row["problem_id"], prefix)][condition].append(choice)
            if action["kind"] != "acquire":
                break
            prefix = prefix + (str(action["target_id"]),)
            observations = transition["result"]["observations"]
            condition = (
                str(observations[-1]["payload"]["value"])
                if observations
                else "__failure__"
            )
    eligible: Counter[str] = Counter()
    adaptive_groups: Counter[str] = Counter()
    for (policy, _, _), by_condition in grouped.items():
        usable = {condition: values for condition, values in by_condition.items() if len(values) >= 2}
        if len(usable) < 2:
            continue
        modes = []
        concentrations = []
        for values in usable.values():
            count = Counter(values)
            mode, frequency = count.most_common(1)[0]
            modes.append(mode)
            concentrations.append(frequency / len(values))
        eligible[policy] += 1
        if len(set(modes)) > 1 and mean(concentrations) >= 0.70:
            adaptive_groups[policy] += 1
    return {
        policy: adaptive_groups[policy] / eligible[policy] if eligible[policy] else 0.0
        for policy in set(eligible) | set(adaptive_groups)
    }


def _trajectory_signature(row: dict) -> tuple[tuple[str, str | None], ...]:
    return tuple(
        (item["action"]["kind"], item["action"]["target_id"])
        for item in row["trace"]["transitions"]
    )


def _failure_analysis(rows: list[dict]) -> dict:
    by_episode_policy = {(item["episode_id"], item["policy"]): item for item in rows}
    episodes = sorted({item["episode_id"] for item in rows})
    families = sorted({item["family"] for item in rows})
    family_counts: dict[str, Counter] = {family: Counter() for family in families}
    examples: dict[str, list[dict]] = defaultdict(list)
    for episode_id in episodes:
        adaptive = by_episode_policy[(episode_id, ADAPTIVE)]
        controls_by_name = {
            policy: by_episode_policy[(episode_id, policy)] for policy in BASELINES
        }
        controls = list(controls_by_name.values())
        best = min(controls, key=lambda item: (item["combined_objective"], item["synthetic_cost_units"]))
        family = adaptive["family"]
        delta = adaptive["combined_objective"] - best["combined_objective"]
        reasons = []
        if adaptive["combined_objective"] > controls_by_name["cheap_first"]["combined_objective"] + 1e-12:
            family_counts[family]["loses_to_cheap_first"] += 1
        if adaptive["combined_objective"] > controls_by_name["fixed_order"]["combined_objective"] + 1e-12:
            family_counts[family]["loses_to_fixed_order"] += 1
        if delta > 1e-12:
            family_counts[family]["loses_to_best_simple"] += 1
            reasons.append("higher_combined_objective")
        if not adaptive["correct"] and best["correct"]:
            family_counts[family]["wrong_when_simple_correct"] += 1
            reasons.append("wrong_when_simple_correct")
        if adaptive["synthetic_cost_units"] > best["synthetic_cost_units"] + 1e-12:
            family_counts[family]["spends_more"] += 1
            reasons.append("spends_more")
        if adaptive["failed_actions"] and delta > 1e-12:
            family_counts[family]["failed_action_loss"] += 1
            reasons.append("failed_action")
        if adaptive["premature_stop"]:
            family_counts[family]["stops_incorrectly"] += 1
            reasons.append("premature_stop")
        if adaptive["unnecessary_actions"]:
            family_counts[family]["spends_after_sufficiency"] += 1
            reasons.append("post_sufficiency_action")
        if not adaptive["correct"] and any(control["correct"] for control in controls):
            family_counts[family]["misled_on_noisy_episode"] += 1
        if any(_trajectory_signature(adaptive) == _trajectory_signature(control) for control in controls):
            family_counts[family]["matches_simple_trajectory"] += 1
            reasons.append("matches_simple_trajectory")
        if delta > 1e-12:
            examples[family].append(
                {
                    "episode_id": episode_id,
                    "best_simple_policy": best["policy"],
                    "adaptive_minus_best_objective": delta,
                    "reasons": reasons,
                }
            )
    return {
        "operational_definitions": {
            "misled_on_noisy_episode": "adaptive decision was wrong while at least one matched simple control was correct; this is an episode-level diagnostic, not a causal attribution to a specific observation",
            "stops_incorrectly": "the exact public-state oracle preferred an acquisition when the adaptive policy selected STOP",
            "spends_after_sufficiency": "the adaptive policy acquired evidence when the exact public-state oracle selected STOP",
        },
        "counts_by_family": {
            family: {
                key: family_counts[family][key]
                for key in (
                    "loses_to_cheap_first",
                    "loses_to_fixed_order",
                    "loses_to_best_simple",
                    "spends_more",
                    "spends_after_sufficiency",
                    "stops_incorrectly",
                    "misled_on_noisy_episode",
                    "failed_action_loss",
                    "matches_simple_trajectory",
                )
            }
            for family in families
        },
        "worst_examples_by_family": {
            family: sorted(items, key=lambda item: item["adaptive_minus_best_objective"], reverse=True)[:3]
            for family, items in sorted(examples.items())
        },
    }


def summarize(records: list[dict], population_hash: str) -> dict:
    rows = [_row(record) for record in records]
    by_policy: dict[str, list[dict]] = defaultdict(list)
    by_family_policy: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        by_policy[row["policy"]].append(row)
        by_family_policy[(row["family"], row["policy"])].append(row)
    overall = {policy: _aggregate(items) for policy, items in sorted(by_policy.items())}
    by_family = {
        family: {
            policy: _aggregate(by_family_policy[(family, policy)])
            for policy in sorted(by_policy)
        }
        for family in sorted({row["family"] for row in rows})
    }
    indexed = {
        policy: {item["episode_id"]: item for item in items}
        for policy, items in by_policy.items()
    }
    paired = {
        policy: {
            "combined_objective": _paired_effect(indexed[ADAPTIVE], indexed[policy], "combined_objective", 100 + index),
            "decision_loss": _paired_effect(indexed[ADAPTIVE], indexed[policy], "decision_loss", 200 + index),
            "synthetic_cost_units": _paired_effect(indexed[ADAPTIVE], indexed[policy], "synthetic_cost_units", 300 + index),
        }
        for index, policy in enumerate(BASELINES + ABLATIONS)
    }
    routing = _conditional_routing(rows)
    improved_baselines = sum(
        overall[ADAPTIVE]["combined_objective"] < overall[policy]["combined_objective"] - 1e-12
        for policy in BASELINES
    )
    no_adaptation_delta = (
        overall[ADAPTIVE]["combined_objective"]
        - overall["ablation_no_adaptation"]["combined_objective"]
    )
    if improved_baselines >= 4 and no_adaptation_delta < -1e-4:
        classification = "strong_enough_to_continue"
    elif improved_baselines >= 1:
        classification = "narrow"
    elif improved_baselines == 0 and all(
        abs(overall[ADAPTIVE]["combined_objective"] - overall[p]["combined_objective"]) <= 1e-4
        for p in BASELINES
    ):
        classification = "null"
    else:
        classification = "negative"
    return {
        "schema_version": 1,
        "benchmark": "microgym-v1",
        "population_hash": population_hash,
        "population_interpretation": "Frozen deterministic benchmark population; differences are population quantities. Bootstrap intervals are paired descriptive sensitivity intervals, not significance claims.",
        "run_count": len(rows),
        "valid_run_count": sum(bool(row["valid"]) for row in rows),
        "invalid_run_count": sum(not bool(row["valid"]) for row in rows),
        "overall": overall,
        "by_family": by_family,
        "paired_effects": paired,
        "matched_model_aware_open_loop_comparison": paired["ablation_no_adaptation"],
        "conditional_routing_rate": routing,
        "failure_analysis": _failure_analysis(rows),
        "evidence_classification": classification,
    }


def _fmt(value: float) -> str:
    return f"{value:.4f}"


def render_report(summary: dict, population: dict, validation: dict) -> str:
    policies = list(summary["overall"])
    lines = [
        "# MicroGym v1 benchmark report",
        "",
        "This report is generated from the frozen population and run artifacts. It evaluates a synthetic, explicit-likelihood control problem; it does not test semantic reasoning or real-domain generalization.",
        "",
        "## Frozen experiment definition",
        "",
        f"- Population hash: `{summary['population_hash']}`",
        f"- Problem regimes: **{len(population['problems'])}** across **{len({item['family'] for item in population['problems']})}** families.",
        f"- Episodes: **{len(population['episodes'])}**; the population was frozen before aggregation.",
        f"- Normal policy runs: **{summary['run_count']}** ({summary['valid_run_count']} valid, {summary['invalid_run_count']} invalid).",
        "- Raw resources: `tests` (count), `synthetic_cost_units` (unit), and `latency_steps` (step).",
        "- MicroGym-only objective: decision loss + the regime's preregistered cost weight × synthetic cost units.",
        "- Sufficient evidence: the exact evaluator oracle selects STOP at the current public belief/budget state; hidden-state hindsight is not used.",
        f"- Randomness domains: population generation `{population['seed_roles']['population_generation_seed']}`, environment realization master `{population['seed_roles']['environment_realization_master_seed']}`, and policy randomness master `{population['seed_roles']['policy_randomness_master_seed']}`. Normal policies never receive the environment seed.",
        "",
        "## Policy definitions",
        "",
    ]
    for policy, assumptions in sorted(validation["policy_assumptions"].items()):
        lines.append(f"- `{policy}`: " + "; ".join(assumptions))
    lines.extend(
        [
            "",
            "## Overall results",
            "",
            "| Policy | Correct | Abstain | Decision loss | Cost units | Tests | Combined objective | Combined regret | Actions |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for policy in policies:
        item = summary["overall"][policy]
        lines.append(
            f"| `{policy}` | {_fmt(item['correct'])} | {_fmt(item['abstained'])} | {_fmt(item['decision_loss'])} | {_fmt(item['synthetic_cost_units'])} | {_fmt(item['tests'])} | {_fmt(item['combined_objective'])} | {_fmt(item['combined_regret'])} | {_fmt(item['actions'])} |"
        )
    lines.extend(
        [
            "",
            "### Raw resource distributions",
            "",
            "Cells show mean [p10, p50, p90]; all dimensions remain separate.",
            "",
            "| Policy | Tests | Synthetic cost units | Latency steps |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for policy in policies:
        item = summary["overall"][policy]
        cells = []
        for field in ("tests", "synthetic_cost_units", "latency_steps"):
            distribution = item["distributions"][field]
            cells.append(
                f"{_fmt(item[field])} [{_fmt(distribution['p10'])}, {_fmt(distribution['p50'])}, {_fmt(distribution['p90'])}]"
            )
        lines.append(f"| `{policy}` | " + " | ".join(cells) + " |")
    lines.extend(["", "## Results by family", ""])
    for family, values in summary["by_family"].items():
        lines.extend(
            [
                f"### Family {family}",
                "",
                "| Policy | Correct | Decision loss | Cost | Objective | Regret |",
                "| --- | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for policy in policies:
            item = values[policy]
            lines.append(
                f"| `{policy}` | {_fmt(item['correct'])} | {_fmt(item['decision_loss'])} | {_fmt(item['synthetic_cost_units'])} | {_fmt(item['combined_objective'])} | {_fmt(item['combined_regret'])} |"
            )
        lines.append("")
    lines.extend(
        [
            "## Paired adaptive comparisons",
            "",
            "Negative adaptive-minus-control objective/cost differences favor the adaptive candidate. Intervals are deterministic paired bootstrap descriptions of this frozen population, not p-values.",
            "",
            "| Control | Objective Δ | 95% descriptive interval | Wins / ties / losses | Decision-loss Δ | Cost Δ |",
            "| --- | ---: | --- | ---: | ---: | ---: |",
        ]
    )
    for policy, fields in summary["paired_effects"].items():
        objective = fields["combined_objective"]
        interval = objective["descriptive_bootstrap_95"]
        lines.append(
            f"| `{policy}` | {_fmt(objective['mean_adaptive_minus_control'])} | [{_fmt(interval[0])}, {_fmt(interval[1])}] | {objective['adaptive_lower_wins']} / {objective['ties']} / {objective['adaptive_lower_losses']} | {_fmt(fields['decision_loss']['mean_adaptive_minus_control'])} | {_fmt(fields['synthetic_cost_units']['mean_adaptive_minus_control'])} |"
        )
    lines.extend(
        [
            "",
            "The `ablation_no_adaptation` comparison is the causal model-access control: it receives the same public generative model, costs, budget, and scoring objective, but commits its acquisition sequence and stopping length from the prior before inspecting the episode's initial observation.",
        ]
    )
    lines.extend(
        [
            "",
            "## Stopping and adaptivity",
            "",
            "| Policy | Premature stop rate | Stopping regret | Unnecessary actions | Avoidable cost | Conditional routing rate |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for policy in policies:
        item = summary["overall"][policy]
        lines.append(
            f"| `{policy}` | {_fmt(item['premature_stop'])} | {_fmt(item['stopping_regret'])} | {_fmt(item['unnecessary_actions'])} | {_fmt(item['avoidable_resource_cost'])} | {_fmt(summary['conditional_routing_rate'].get(policy, 0.0))} |"
        )
    lines.extend(["", "## Leakage, replay, and invariance checks", ""])
    for name, item in sorted(validation["checks"].items()):
        lines.append(f"- **{name}:** `{item['status']}` — {item['detail']}")
    lines.extend(["", "## Failure analysis", ""])
    for family, counts in summary["failure_analysis"]["counts_by_family"].items():
        lines.append(
            f"- **Family {family}:** " + ", ".join(f"{key}={value}" for key, value in sorted(counts.items()))
        )
        for example in summary["failure_analysis"]["worst_examples_by_family"].get(family, []):
            lines.append(
                f"  - `{example['episode_id']}` lost to `{example['best_simple_policy']}` by {_fmt(example['adaptive_minus_best_objective'])}: {', '.join(example['reasons'])}."
            )
    lines.extend(
        [
            "",
            "## Evidence classification and limitations",
            "",
            f"Classification: **`{summary['evidence_classification']}`**.",
            "",
            "The candidate is myopic and knows the declared likelihood model. MicroGym labels and observations are opaque but mathematically clean. The result cannot establish semantic reasoning, real-domain transfer, Scope-aware gating, graph value, coupling laws, learned routing, LLM value, IDS performance, or software-investigation performance. Failed actions and adaptive losses remain in the run artifacts.",
            "",
        ]
    )
    return "\n".join(lines)
