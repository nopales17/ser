# AuthzGym successor confirmation report -- `est-repair-v1.3.1-B-1`

Condition: `est-repair-v1.3.1-B-1`. Authorized by ADR-0022 under preregistration
section 8. Status: **sealed**, one-shot evaluation complete.

This is a confirmation of component/instrument compatibility. It is not an
architecture, capability, transfer, or model finding, and no model or
provider call was made at any point.

## 1. Frozen inputs

- component class SHA-256: `88b77c5f343117b354b5039d571bf03bf8867fcd7fb4f8fc91c1e1aefca7a048`
- component module SHA-256: `f9c92317abc562ac5175f90074238c666de55d557b02e0de368841676f4d910d`
- development report SHA-256: `f0629d3b78ba35258cc6d439e4b731c3682b76fa08e4155efbdad7cd0df18638`
- fragile label: none (zero failing leave-one-source-out folds)

## 2. Population

- split: `confirmation_v1_3_1`, layouts `[42, 43]`, selected
  before generation and never by inspecting content
- sources: 8 (7 variants each),
  cases: 56, scheduled calls: 56,
  repeats per case: 1
- generator and converter: byte-unchanged frozen code
- generator SHA-256: `03bfe556091e8da118c1c27058a8edaa393473c17c4fa45645837b08b7163461`
- converter SHA-256: `ac4b8d47bd1369a16f4fed0d80abe7e0943c90317c0037bb6c8715882f470fca`
- source manifest SHA-256: `ab13c8a47f8f5e967b861e3aab6580de4a1c2e9c06c7eee838748423e44a7c1f`
- public population file SHA-256: `1321bcd190c2bfbef884aac55421669401fe321797345ad54556d0f55251787c`
- provider calls authorized and made: **0**

## 3. Section-8.3 duplicate and equivalence checks

- population hash differs from development: True
- population hash differs from the spent confirmation: True
- case-id sets disjoint from development: True
- public-input-hash sets disjoint from development: True
- source-episode-id sets disjoint from development: True
- layout digests differ: True

Checks against the spent `confirmation_v1_3` population were verified by
construction, not by opening it: the split label, the layout indices, and the
identifier bijection are all disjoint by design, and the spent population was
never opened, read, counted, or characterized.

## 4. Validation gates

- independent public-only answerability: **pass** (56 cases, 2576 labels,
  label agreement True, 40 transformation checks,
  hidden-data invariance True, deterministic replay True)
- public-only firewall audit: **pass**
  - normal fields have public provenance: pass
  - normal initial state empty: pass
  - normal module import isolation: pass
  - oracle and normal channels separated: pass
  - public-only replay: pass
  - restricted-field mutation byte equality: pass

## 5. One-shot oracle evaluation

Exactly one evaluation was run, after both validation gates passed, on the
eight canonical confirmation entries.

| gate | requirement | result |
| --- | --- | --- |
| canonical_top1 | >= 0.60 | pass |
| canonical_top2 | >= 0.80 | pass |
| illegal_target_count | = 0 | pass |
| mean_normalized_regret | <= 0.35 | pass |
| own_selection_equivalence | 40/40 after ordinal mapping | pass |
| section_14_equivalence | 40/40 within 1e-12 | pass |

- canonical cases: 8
- top-1: **0.875**
- top-2: **1.0**
- mean normalized regret: **0.058333**
- illegal target/value count: 0
- section-14 equivalence: 40 pairs, 0 failures
- own-selection equivariance: 40/40
- **outcome: `pass`**

Reported-only diagnostics (not gates at confirmation): non-degeneracy ND-1 True, ND-2 True, ND-3 True; `longest_artifact` top-1 0.25, top-2 0.25, regret 0.600000; leave-one-source-out failing folds 0.

## 6. Claim boundary

The confirmed claim is the compatibility claim of preregistration section
10.1 on a newly frozen untouched confirmation population: under the fixed
instrument, the named component meets the existing engineering gate on those
instances using only authorized public semantic outputs. It remains a claim
about a component and an instrument. It is not general authorization
reasoning, adaptive routing, SER architecture superiority, GitLab or
real-world transfer, model capability, validation of the instrument, a
diagnosis of the earlier confirmation failure, or promotion of any concept.

## 7. Seal

- sealed: True (after the one-shot evaluation: True)
- population hash: `1321bcd190c2bfbef884aac55421669401fe321797345ad54556d0f55251787c`
- seal SHA-256: `463d208f0e02fc17fc66dd52a211e365fc464cafcb8344c4d91955d4fb0986b8`
- oracle status recorded at seal: `pass`

Not authorized and not performed: any further evaluation of this population,
any replacement population, any threshold or semantic change, any model or
provider inference, Jev, and adaptive-routing experiments.
