# MicroGym v1 evidence interpretation

This is the post-run scientific interpretation of the immutable MicroGym v1
population and run artifacts. It does not replace or rewrite the preregistered
summary. The population hash is
`a9234fa60b40d3628f6317284a964c95917bcd7442796d8961f18b14b9958b3d`.

## Classification

The preregistered mechanical classifier returned `strong_enough_to_continue`.
The scientifically admitted result is **narrow** and does **not** demonstrate
observation-conditioned adaptive epistemic routing.

The classifier required a lower combined objective than at least four simple
controls and the model-aware open-loop control. It did not independently require
the candidate to exhibit observation-conditioned action changes. That omission
matters here and is preserved as a Phase 3 admission-rule failure rather than
repaired after seeing the result.

## What happened

Across 728 matched episodes, the candidate had:

- combined objective `0.303159`;
- decision loss `0.231456`;
- mean synthetic cost `0.906593`;
- mean acquisition count `0.412088`;
- correct decision rate `0.438187` and abstention rate `0.508242`.

The five simple controls had combined objectives from `0.465220` to `0.481049`
but all had lower decision loss (`0.164011` to `0.217033`) and substantially
higher mean synthetic cost (`2.587363` to `3.135989`). Thus the candidate's
large scalar-objective advantage over those controls is a cost/abstention
tradeoff under the preregistered MicroGym scalarization, not superior decision
quality.

The strongest causal comparison is the model-aware open-loop control. It had
combined objective `0.311429`, decision loss `0.213599`, and cost `1.207418`.
Adaptive minus open-loop was:

- combined objective: `-0.008269` with paired descriptive interval
  `[-0.016554, -0.000198]`;
- decision loss: `+0.017857` (worse);
- synthetic cost: `-0.300824` (lower);
- paired objective outcomes: 70 candidate wins, 645 ties, and 13 losses.

The gap was confined to stopping/cost behavior in families C and F. The
candidate and open-loop control had identical family-mean objectives in A, B,
D, and E. In family E, designed to require branch-conditioned routing, the
candidate always stopped immediately and abstained.

## Adaptivity audit

The run-summary conditional-routing diagnostic reported zero for the candidate,
but it also produced nonzero values for fixed-order controls because it did not
condition on frozen action presentation order. It is therefore retained only as
a known-confounded diagnostic.

The post-run `adaptivity.json` audit instead exhaustively enumerates alternative
policy-visible outcomes at the same public decision node while holding
identifiers, presentation order, seed, and hidden truth out of the comparison.
It found:

- `adaptive_belief`: 0 observation-conditioned branches across 20 eligible
  counterfactual decision nodes;
- `ablation_no_adaptation`: 0 across 44 nodes;
- `ablation_no_adaptive_stop`: 2 across 139 nodes, both in family E, where the
  initial branch cue selected `e0` versus `e1`.

This shows that the policy implementation could route conditionally when STOP
was disabled, but the candidate's myopic stopping rule suppressed that behavior
in the actual benchmark.

## Stopping and failures

The candidate performed no post-sufficiency acquisitions but stopped prematurely
on 30/728 episodes (`0.041209`), all in family C. Mean exact stopping regret was
`0.000206`. The no-adaptive-STOP ablation used `2.002747` more synthetic cost
than the candidate and had `1.306319` unnecessary post-sufficiency actions per
episode, so adaptive STOP clearly controlled expenditure. It did not establish
conditional routing value.

All 7,280 normal policy runs were valid. The artifacts retain 265 declared
action failures and 144 environment terminations. The candidate lost to the
best simple control on 210 episodes across the six families, including 30
premature-stop cases and 15 failure-associated losses.

## Admitted finding and non-claims

MicroGym v1 supports only this scoped statement:

> Under the frozen explicit-likelihood MicroGym v1 population and its
> experiment-specific cost scalarization, a public-model myopic STOP rule reduced
> mean synthetic resource use enough to lower combined objective relative to
> simple fixed-spend controls and marginally relative to a matched model-aware
> open-loop plan.

It does not support the claim that realized observations improved routing. It
does not promote the general resource-normalized SER hypothesis, semantic
reasoning, scope-aware gating, graph/coupling mechanisms, learned routing, IDS
transfer, software investigation, GitLab authorization research, or
cross-substrate generalization.

## Next experiment

Phase 4 should remain synthetic and perform the smallest falsification follow-up:
preregister an admission rule that requires actual observation-conditioned
branching, repair or replace the myopic STOP/routing interaction, and compare it
again with the same-model open-loop control. The immutable v1 failures must stay
in the benchmark. IDS and controlled software are premature until this lower-level
routing question is resolved; GitLab authorization remains the practical trunk,
not the immediate experiment.
