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
hypothesis, and says nothing about SER-vs-ReAct architecture leverage.

- `authzgym_stronger_model_v1/` retains contract v1.2 and changes only the model
  to `patchersniper_praneeth/gpt-5.4-mini`. Its corrected smoke and 16 executed
  development calls were all first-attempt schema-valid with zero transport
  failures or retries. The frozen optimistic rule stopped development at 16/32:
  fact precision, effect precision, unresolved-relation recall, action top-1,
  action top-2, and regret could no longer all pass even if the remaining calls
  were perfect. The fresh 64-call confirmation population was generated and
  hash-frozen but never queried. Evaluator-oracle observations reproduced
  top-1/top-2 1.0 and zero regret on both development and fresh canonical
  entries. The valid classifier is `semantic_capability_below_threshold`.

The frozen stronger-model classifier and stop remain historical facts, but
ADR-0019 withdraws a clean capability-floor interpretation because the
underlying v1.2 semantic target was defective. It is not an `E-*` finding or
architecture result.

- `authzgym_semantic_bottleneck_v1/` performs that diagnosis offline on all 16
  executed Mini development cases. Its prompt-grounded answerability audit found
  that source-direct facts are scored false and that test-specific labels require
  evaluator-only logical roles. All four frozen challenge cases therefore
  failed the answerability gate, so decomposed Mini and stronger-model probes
  were not run. The classifier is `benchmark_ambiguity_detected`; incremental
  calls and spend are zero, and the stronger-model confirmation remains
  untouched.

This localization result preserves genuine Mini unresolved-relation misses and
transformation instability as diagnostics, but the contaminated fact/effect
aggregate cannot attribute a capability floor. It creates no `E-*` finding,
promotes no hypothesis, and permits only separately versioned benchmark/task-
definition repair next.

## Accepted v1.3 specification, not yet an implemented or run experiment

- `authzgym_semantic_contract_v1_3/PREREGISTRATION.md` is the normative new
  instrument specification accepted by ADR-0019. It retains source-grounded
  f0--f16 facts, four mechanism families, seven non-summary variants, public
  deterministic local-cue effects, and five visible-call categories. It retires
  f17--f24, excludes hidden logical roles and the maximal-summary condition, and
  requires independent answerability, firewall, and unchanged-estimator oracle
  validation before inference.
- `authzgym_semantic_contract_v1_3/IMPLEMENTATION_PLAN.md` is the ordered
  mechanical handoff and complete freeze checklist. Its existence is not proof
  that the instrument, population, or checks have been implemented or frozen.
- `authzgym_semantic_contract_v1_3/PRIOR_RESULT_CORRIGENDUM.md` supplies the
  current append-only interpretation correction for v1.2. Historical files are
  not rewritten. Transport, wire/schema, accounting, cleanup, and stopping facts
  remain scoped observations. V1.2 semantic aggregates and futility results are
  conditional on the defective scorer; clean fact/effect capability-floor
  claims are withdrawn. The historical `contract_stable` classification now
  means wire reliability only, not a firewall-valid and answerable ordinary
  semantic condition.

No model/provider inference, architecture comparison, representation
intervention, or Jev condition is authorized by these documents.

## Sealed component/instrument confirmation, not admitted evidence

- `authzgym_confirmation_v1_3_1/` preserves the ADR-0022 one-shot successor
  confirmation of the frozen `est-repair-v1.3.1-B-1` component. A new untouched
  population was generated and frozen at layouts 42/43, certified and validated
  in the preregistered isolation order, and evaluated exactly once: canonical
  top-1 `0.875`, top-2 `1.0`, regret `0.058333`, zero illegal targets,
  own-selection equivariance `40/40`, section-14 equivalence `40/40`, and **zero
  provider calls**. Its classifier is confirmed component/instrument
  compatibility. It is not authorization reasoning, adaptive routing,
  architecture, transfer, model capability, instrument validation, a diagnosis
  of the preserved historical-estimator confirmation failure, or a pass of
  AuthzGym v1.3 preregistration section 16, which was never satisfied and is not
  claimed to have been. It creates no `E-*` entry and promotes no hypothesis.

## Accepted specification, not a run

- `authzgym_model_semantic_v1_3_1/` holds the ADR-0023-accepted condition
  `model-semantic-v1.3.1-N1`: the normative preregistration, the decision text,
  the mechanical implementation handoff, the adjudicated research-decision
  record, and the reconstructed-cursor and contradiction record. The condition
  changes exactly one link in the controlled chain, `gold semantic response ->
  actual model semantic response`, with v1.3 semantics, `est-repair-v1.3.1-B-1`,
  thresholds, endpoints, populations and retry policy frozen. Its primary
  endpoint is choice-set preservation at `>= 7/8` canonical sources, computed
  without the evaluator canonical ordinal. Effect self-consistency is
  `diagnostic_only`. ADR-0023 authorizes only zero-inference mechanical
  implementation through the pre-inference freeze boundary. No model or provider
  call, no development call, and no confirmation generation or access is
  authorized; there is no result here yet and no `E-*` entry.

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
