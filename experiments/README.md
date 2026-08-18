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

## Construction calibrations, not admitted evidence

- `authzgym_static_v1/` preserves the initial frozen Static Semantic AuthzGym
  population and deterministic calibration. Overall validation failed because
  the degraded test double's omission schedule depended on opaque artifact IDs;
  the failure and the preceding output-ceiling correction are preserved.
- `authzgym_static_v1_1/` freezes the integrity correction that keys mock
  omissions to semantic roles. It contains 8 development, 24 primary
  evaluation, and 24 paired perturbation episodes; all 11 validation safeguards
  pass, including 96/96 routed/ReAct perturbation comparisons. Its 384 records
  are deterministic mock traces, so its classifier is
  `benchmark_calibration_only` and it is not an `E-*` finding.

Any actual inexpensive-model evaluation must be a separate frozen experiment.
Phase 5B and real GitLab remain gated.

## Preserved real-model failures, not admitted evidence

- `authzgym_static_realmodel_v1/` preserves the first complete real-model
  architecture schedule. Its classifier is `invalid`: 273/609 frozen attempts
  failed the semantic contract, chiefly from the 320-token output ceiling and
  unconstrained dynamic identifiers. Its diagnostic semantic and architecture
  metrics are not admitted findings.
- `authzgym_semantic_contract_v1_2/` preserves the subsequent development-only
  interface stress study. It removed prose and generated identifiers, used a
  1,024-token safety ceiling, and scheduled 128 calls across only the eight
  development episodes. The egress SSH connection failed after eight valid
  calls; 240 later attempts had transport failures, so only 8/128 calls were
  valid and the classifier is `contract_unstable`. Zero observed length or
  illegal-reference failures in the successful prefix do not establish channel
  stability or nano capability. The oracle-only estimator diagnostic is not
  model evidence.

Neither failure creates an `E-*` entry or promotes H-001, H-016, H-017, or
H-018.

## Development diagnostics, not admitted architecture evidence

- `authzgym_transport_envelope_v1/` retains semantic contract v1.2, the nano
  model, and the exact 128-call development schedule while adding only local
  SSH/SOCKS supervision and transport accounting. A preserved zero-inference
  preflight exposed an unsupported redundant curl option before paid work. The
  corrected frozen run then obtained 128/128 provider responses through one
  tunnel with zero transport failures, zero recoveries, successful cleanup, and
  $0.086505640 accounted spend. All 128 responses were first-attempt schema-
  valid, so its classifiers are `transport_stable` and `contract_stable`.
  Nano's semantic diagnostic is `semantic_signal_weak`: fact, implication, and
  unresolved-relation quality plus repeat/transformation equivalence remained
  below the frozen thresholds. The oracle-conditioned unchanged estimator
  reproduced top-1/top-2 1.0 and zero regret.

This result removes transport and wire-contract reliability as confounders only
for the exact development protocol. It creates no `E-*` finding, promotes no
hypothesis, and says nothing about SER-vs-ReAct architecture leverage. Under
ADR-0018 and the preregistered Case C rule, the next experiment retains contract
v1.2 and separately tests the next stronger inexpensive model with a fresh
untouched confirmatory population; the old 24 evaluation episodes cannot be
used as confirmation.

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
