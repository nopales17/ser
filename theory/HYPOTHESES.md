# Working hypothesis families

The canonical statements, maturity, relations, and falsifiers live in
`theory/IDEA_MAP.yaml`. This document groups them for reading.

## Allocation and evaluation

- `H-001` asks whether organization of computation and evidence acquisition
  matters beyond total compute.
- `H-002` proposes, without fixing, a policy-level decision-relevant
  information utility. It is not part of the environment contract.
- `H-016` is the eventual resource-normalized advantage claim.
- `F-004` is the binding methodological constraint: matched simpler baselines
  can falsify architectural value.

## State, propagation, and compression

- `H-003` links explicit scope to allocation efficiency.
- `H-004` proposes sparse local rather than broadcast propagation.
- `H-005` asks whether history can be compressed without harming future
  epistemic decisions.
- The operator family `M-001` through `M-009` is preserved at `seed` and
  explicitly deferred. None is required in the first MicroGym; each may prove
  reducible to ordinary policy or updater behavior.

## Trajectories and environment dynamics

- `H-006` treats branch allocation as a possible exploration-exploitation
  problem.
- `H-007` defines oscillation rate and depth as measured properties derivable
  from optional action-mode metadata, not architectural constants.
- `H-008` asks whether environment coherence time should constrain internal
  reasoning depth.
- `H-009` distinguishes active interventions from passive observation.
- `H-010` asks whether hierarchical boundary selection transfers across domains.

## Environment and late-stage hypotheses

- `H-011`, `H-012`, and `H-013` preserve possible IDS, software/fuzzing, and
  remote-sensing environments with conservative scope and priority.
- `H-014` SERT and `H-015` a temporal graph policy/TGNN are late-stage seeds.
  They must not determine the first SER implementation.

No SER hypothesis currently has SER experimental support.

The four Phase 2 domain instantiations establish representational coverage only.
They do not validate allocation value, scope-aware routing, active investigation,
or cross-domain generalization.
