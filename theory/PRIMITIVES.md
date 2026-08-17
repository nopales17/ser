# Candidate primitives

`theory/IDEA_MAP.yaml` owns identity and maturity. This document explains the
current vocabulary without freezing a runtime schema.

## The current set

- `P-001` **Explicit epistemic state:** a possible decision state containing
  observations, hypotheses, claims, unknowns, contradictions, uncertainty,
  provenance, scope, actions, and costs. The list is not a schema.
- `P-002` **Epistemic unit:** a possible substrate-independent carrier for
  evidence or knowledge. Whether observations and claims can truly share a
  common unit remains open.
- `P-003` **Scope:** applicability across semantic, structural, temporal,
  spatial, and observational dimensions. Scope is a candidate primitive, not an
  accepted implementation design.
- `P-004` **Epistemic action:** observe, retrieve, transform, hypothesize,
  compare, test, deepen, broaden, revise, abandon, or stop. Granularity remains
  unresolved.
- `P-005` **Epistemic resource:** tokens, model tiers, compute, retrieval,
  source inspection, execution, tests, sensing, time, and money. No universal
  scalar conversion is assumed.
- `P-006` **Cost, latency, and risk:** distinct burdens or constraints attached
  to actions and outcomes.
- `P-007` **Provenance:** recoverable origins and transformations for evidence
  and claims.
- `P-008` **Uncertainty and confidence:** possible annotations needed to choose
  further investigation and stopping. Their mathematical semantics are open.

## Four things that must stay separate

`P-003` Scope is a primitive candidate. `H-003` says scope-aware allocation may
improve efficiency. `M-006` SCOPE_FILTER is one possible mechanism. A future
class or function would be an implementation. Only a scoped experiment comparing
matched alternatives would be evidence.

Implementing the latter three does not establish the former, and a failed
mechanism does not necessarily reject the primitive or hypothesis.

