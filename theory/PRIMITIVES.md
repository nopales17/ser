# Candidate primitives

`theory/IDEA_MAP.yaml` owns identity and maturity. This document explains the
current vocabulary without freezing a runtime schema.

## The current set

- `P-001` **Explicit epistemic state:** the controller-entitled decision state.
  It may be raw public history, a summary, or a structured representation, but
  it is never latent world state or evaluator-only truth.
- `P-002` **Epistemic unit:** rejected as a universal required supertype for the
  Phase 2 core. Observation and optional Hypothesis remain distinct roles. The
  stable ID remains available if repeated implementations later justify a
  common infrastructure envelope.
- `P-003` **Scope:** optional domain-typed applicability metadata. It has no
  accepted universal algebra and is not required in the first MicroGym.
- `P-004` **Epistemic action:** a domain action that may acquire information,
  transform entitled state, intervene on the world, or stop. Its common
  envelope is minimal; descriptive action categories are not a universal enum.
- `P-005` **Epistemic resource:** named, unit-bearing, nonnegative vector costs
  and partial vector budgets. No universal scalar conversion is assumed.
- `P-006` **Cost, latency, and risk:** distinct burdens or constraints attached
  to actions and outcomes; only raw declared resource accounting is universal.
- `P-007` **Provenance:** recoverable origins and transformations for evidence
  and claims, including release provenance for externally acquired observations.
- `P-008` **Uncertainty and confidence:** possible annotations needed to choose
  further investigation and stopping. They remain optional, with no universal
  probabilistic semantics.
- `P-009` **Signal:** a preserved but explicitly deferred candidate. No semantic
  role has been found beyond Observation, ActionResult, derived state,
  relations, or reliability metadata.

The accepted semantic contracts are defined in `theory/CONTROL_PROBLEM.md` and
`theory/CONTRACTS.yaml`. Primitive status still comes only from the idea map;
formalizing a contract does not supply experimental support.

## Four things that must stay separate

`P-003` Scope is an optional primitive candidate. `H-003` says scope-aware
allocation may improve efficiency. `M-006` SCOPE_FILTER is one possible deferred
mechanism. A future class or function would be an implementation. Only a scoped
experiment comparing matched alternatives would be evidence.

Implementing the latter three does not establish the former, and a failed
mechanism does not necessarily reject the primitive or hypothesis.
