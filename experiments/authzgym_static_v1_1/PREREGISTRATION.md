# Static Semantic AuthzGym v1 calibration protocol 1.1

Date frozen: 2026-08-17

## Revision boundary

The v1 population and first calibration are preserved in
`experiments/authzgym_static_v1/`. That calibration correctly failed overall
validation because the degraded test double keyed deterministic omissions to
opaque artifact IDs. Protocol 1.1 changes only that mock omission schedule: it
is keyed to semantic fact/relation roles so opaque identifier renaming cannot
change which semantic capabilities are omitted.

The authored repositories, development/evaluation/perturbation split, candidate
hypotheses, raw code, prompt, parser rules, action-value policy, fixed/ReAct/SER
architectures, monolithic baseline, four-inspection budget, decision rule,
evaluator truth, metrics, and classifier thresholds are unchanged. This is a
benchmark integrity correction, not strategy tuning. No real-model result from
v1 was observed because no real model was called.

## Frozen experimental scope

The narrow future hypothesis remains:

> With the same inexpensive semantic model and evidence budget, an explicit
> routed architecture can use interpretations of purchased authorization-code
> artifacts to estimate which remaining inspection is decision-relevant better
> than matched fixed-order and ordinary tool-selection procedures.

This protocol runs deterministic mocks only and must be classified
`benchmark_calibration_only`. It cannot admit evidence for semantic extraction,
SER routing leverage, authorization competence, economics, or deployment.

The population remains:

- 8 development episodes;
- 24 primary evaluation episodes: 16 eligible counterfactual cases and 8
  zero-value controls;
- 24 paired identifier/symbol/candidate-label/order perturbations;
- six files and 100–500 lines per episode;
- four constrained hypotheses and four artifact inspections.

The only action is static inspection. Every semantic call receives exactly the
purchased artifact or the monolithic baseline's bounded four-artifact batch,
plus candidate hypotheses, public summary, public inventory, frozen prompt, and
mock configuration. It never receives evaluator truth, unpurchased source,
future evidence, oracle action values, or useful-action labels.

## Architectures and budgets

- `fixed_order_semantic`: common entry, then frozen public order;
- `react_like_semantic`: common entry, then first unresolved recent tool
  reference;
- `ser_explicit_value`: common entry, then maximum explicit value derived from
  extracted unresolved relations, candidate relation tags, and current support;
- `monolithic_semantic`: secondary one-call baseline over four public-order
  artifacts.

Fixed, ReAct-like, and SER each receive four calls, four artifacts, 6,000 input-
token proxies, and 2,000 output-token proxies. Monolithic receives four artifacts
in one call under the same total token ceilings. All raw resource dimensions are
recorded. No provider tokens, observed provider latency, or monetary expense are
claimed for mocks.

## Frozen real-model classifier

A later, separate real-model experiment may classify
`semantic_routing_supported` only if all integrity checks pass and:

1. fact precision ≥ 0.65 and recall ≥ 0.50;
2. useful-action top-1 recall ≥ 0.60 and top-2 recall ≥ 0.80;
3. mean normalized routing regret ≤ 0.35;
4. eligible-group branch rate ≥ 0.50;
5. oracle-consistent first-route rate ≥ 0.60;
6. zero-value spurious branch rate ≤ 0.25;
7. SER accuracy exceeds fixed by ≥ 2/24 and ReAct-like by ≥ 1/24;
8. SER mean input-plus-output tokens are ≤ 1.10 times the better primary control;
9. access, budget, replay, prompt/config, and perturbation checks pass.

Other labels remain `invalid`, `no_semantic_signal`,
`semantic_estimation_only`, `routing_without_value`, `negative`, and `null` as
defined in the v1 preregistration. Mock metrics remain diagnostic regardless of
whether they would numerically cross a future threshold.

## Readiness boundary

Phase 5B remains blocked until an actual inexpensive model extracts useful
facts, ranks inspections beyond trivial heuristics, routes conditionally, and
improves matched decision quality or efficiency. Real GitLab remains gated until
Phase 5B establishes useful active evidence generation and an economic case.
GitLab source, IDS, execution, mutation, tests, fuzzing, network activity, and
deployment remain outside this protocol.

