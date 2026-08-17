# Experiments

This directory is an evidence index, not permission to generalize a scoped run.
MicroGym v1 is the first SER experiment. Its frozen population, all traces,
validation, preregistered report, counterfactual adaptivity audit, and post-run
interpretation live in `microgym_v1/`. The separate fixed-horizon routing
falsification experiment lives in `microgym_routing_v1/`; it does not revise or
overwrite v1.

Before a SER run is admitted as evidence, its record should identify:

- experiment and protocol ID;
- hypothesis IDs and exact supported/falsified statements;
- environment, population, and scope;
- state/action/resource definitions used;
- fixed, random, exhaustive, frontier-reasoning, ordinary-agent, or other
  relevant baselines;
- resource-matching rule and all reported cost dimensions;
- preregistered metrics and stopping criteria where feasible;
- code/configuration/data provenance and immutable result paths;
- uncertainty, limitations, failed runs, and deviations.

Results update `evidence_refs` in the canonical idea map. They do not silently
change concept status. Negative results remain preserved, and an implementation
failure rejects only the mechanism or scope the protocol can actually test.

## Admitted evidence

- `E-002` / MicroGym v1: a model-aware myopic stopping policy reduced the frozen
  experiment-specific combined objective mainly by spending and deciding less.
  It did not exhibit observation-conditioned routing, so the general adaptive
  gating hypothesis remained unsupported after that experiment.
- `E-003` / MicroGym routing-v1: under a fixed one-acquisition horizon with no
  STOP, the unchanged candidate branched at 6/6 eligible nodes, matched the
  exact closed-loop route at 6/6, captured all exact one-step VOA across six
  positive regimes, and made 0/3 spurious zero-VOA branches. This supports only
  an explicit-likelihood one-step routing finding; semantic action-value
  estimation and real-domain value remain untested.
