# MicroGym v1 preregistration

Date frozen: 2026-08-17

MicroGym v1 tests whether a myopic belief-conditioned controller can improve
decision quality and synthetic resource use by changing acquisition and stopping
choices after legitimately released observations. It does not test semantic
reasoning, LLMs, graphs, learned routing, IDS, software investigation, GitLab, or
cross-domain generalization.

## Frozen population design

- 24 regimes: four parameter regimes in each of six families.
- 728 episodes: 120 each in families A, B, C, D, and F; 128 in family E.
- Every hidden state is balanced within a regime.
- Action order is deterministically permuted across episodes.
- Costs, informativeness/noise, budgets, failure behavior, and STOP tradeoffs
  vary across the frozen regimes.
- The exact episode specifications and evaluator-only hidden states are stored in
  `population.json`; its content hash is the population identity.

The six families test unequal diagnostic value, tempting cheap evidence,
adaptive stopping, repeated noisy evidence, budget-constrained branch routing,
and failed or terminating actions.

## Randomness isolation

Three named seed domains are fixed in the manifest:

1. the population-generation seed controls episode layout and action ordering;
2. the evaluator-only environment-realization seed controls observations and
   failures, with separate deterministic failure/outcome channels;
3. the policy-randomness seed is derived independently and is the only seed a
   normal policy receives.

Changing an environment-realization seed must not change a random policy's
routing randomness. Seeds and visibility classes are recorded in artifacts.

## Compared policies

The primary candidate is `adaptive_belief`: public-model Bayesian updating,
one-step expected decision-loss reduction minus the preregistered primary cost,
and STOP when no action has positive myopic net value.

Simple controls are fixed order, seeded random, cheap first, exhaustive, and a
fixed public diagnostic-score greedy rule. Behavioral ablations are cost blind,
information blind, no adaptive STOP, and no adaptation.

`ablation_no_adaptation` is the strong causal model-access control. It receives
the same public prior, likelihood model, costs, budget, and experiment-specific
objective as the adaptive candidate. Before inspecting the episode's initial
observation it commits to an open-loop acquisition sequence and stopping length
using the same one-step score. Realized observations may affect its final answer
but cannot alter its acquisition plan.

The exact dynamic-programming oracle is evaluator-only and is never a normal
policy information source.

## Outcomes and analysis

The MicroGym-only scalar objective is realized decision loss plus each regime's
frozen cost weight times `synthetic_cost_units`. Raw `tests`,
`synthetic_cost_units`, and `latency_steps` remain separately recorded and
reported.

The report will include correct/abstain rates, decision loss, raw resource means
and distributions, combined objective, oracle-reference regret, action count,
stopping behavior, observation-conditioned routing, matched ablations, leakage
checks, and family-level failures. “Sufficient evidence” means the exact oracle
selects STOP from the current public belief and budget, never that hidden truth
makes the answer obvious in hindsight.

All comparisons are paired on the exact frozen episode population. Population
means are the primary quantities. A deterministic paired bootstrap interval is
reported only as descriptive sensitivity, not as a p-value or significance
claim.

The evidence classifier is fixed before aggregation:

- `strong_enough_to_continue`: adaptive has lower mean combined objective than
  at least four of five simple controls and lower objective than the model-aware
  open-loop control by more than 0.0001;
- `narrow`: adaptive improves at least one simple control but misses the strong
  rule;
- `null`: adaptive is within 0.0001 of every simple control;
- `negative`: otherwise.

No family, policy, threshold, or classification rule will be tuned after this
population is frozen. A corrected or changed experiment must use a new identity
and preserve this run.
