# est-repair-v1.3.1 development report

Condition: `est-repair-v1.3.1`. Authorized by ADR-0020,
corrected by ADR-0021 (`experiments/authzgym_estimator_repair_v1_3_1/CORRIGENDUM.md`).
Artifact classifier: `development_component_compatibility_diagnostic`. This is
**development-only** work and it **confirms nothing**; no model or
provider inference was run and no confirmation population was generated
or accessed.

## 1. Motivation

motivated by the observed fresh-confirmation top-2 failure recorded in experiments/authzgym_semantic_contract_v1_3/ORACLE_BLOCKER.md.

## 2. Fixed inheritance

- v1.3 source-local answerability passed on development (certificate d308e68b...) and on the fresh confirmation population (5887f8cb...).
- The unchanged historical estimator passed the development canonical oracle gate (top-1 0.625, top-2 0.875, regret 0.175, 0 illegal, 40/40 equivalence).
- The same unchanged estimator failed the preregistered fresh-confirmation canonical top-2 gate at 0.750 against >= 0.80; that result is preserved without reinterpretation.
- The top-2 >= 0.80, top-1 >= 0.60 and regret <= 0.35 thresholds are unchanged, as are the v1.3 semantics, prompt, schemas, scoring, usefulness target, tie rules and transformations.
- The historical estimator (SHA-256 092a7a87...) and the fixed section-13 adapter remain byte-preserved baselines.
- The spent confirmation_v1_3 population was not opened, read, hashed, counted, sampled, or characterized by any step of this study after ADR-0021.
- Model and provider inference remains unauthorized and none was run.

## 3. Tier-1 authorized-information ceiling (blocking, pre-candidate)

- Tier-1 top-1 ceiling: `0.75` (required >= 0.6)
- Tier-1 top-2 ceiling: `1.0` (required >= 0.8)
- Decision: `sufficient`

## 4. Baselines and the frozen ND-3 floor

| baseline | top-1 | top-2 | regret | own-selection | strict-unique-max | note |
| --- | --- | --- | --- | --- | --- | --- |
| B0 | 0.625 | 0.875 | 0.175000 | 36/40 | 4 ||
| B1 | 0.375 | 0.5 | 0.558333 | 40/40 | 0 ||
| B2 | 0.625 | 0.875 | 0.175000 | 40/40 | 4 ||
| B3 | 1.0 | 1.0 | 0.000000 | 40/40 | 8 | upper-bound only|

Frozen `nd3_floor_from_b2` = **4** (measured at handoff step 4, before any candidate existed).

## 5. Candidate ledger, in attempted order

| attempt | candidate | arm | top-1 | top-2 | regret | complexity | disposition | record |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | est-repair-v1.3.1-A-1 | A | 0.625 | 0.875 | 0.175000 | 2 | failing_gate | superseded: duplicate evaluation round, see section 12 |
| 2 | est-repair-v1.3.1-A-2 | A | 0.625 | 0.875 | 0.175000 | 2 | failing_gate | superseded: duplicate evaluation round, see section 12 |
| 3 | est-repair-v1.3.1-B-1 | B | 0.75 | 1.0 | 0.116667 | 3 | failing_gate | superseded: duplicate evaluation round, see section 12 |
| 1 | est-repair-v1.3.1-A-1 | A | 0.625 | 0.875 | 0.175000 | 2 | failing_gate | valid record |
| 2 | est-repair-v1.3.1-A-2 | A | 0.625 | 0.875 | 0.175000 | 2 | failing_gate | valid record |
| 3 | est-repair-v1.3.1-B-1 | B | 0.75 | 1.0 | 0.116667 | 3 | admissible_pass | valid record |

Attempts used: **3** of 10. Arms attempted: A, B. Arm C was not opened: the study stopped at the first admissible pass in Arm B, so the joint condition was never authorized to open and Arms C is untested rather than falsified.

## 6. First passing candidate

`est-repair-v1.3.1-B-1` (arm B) is the result of this
study, by the section-5.4 rule 2 stop. No further candidate was written
and no remaining budget was spent.

- component class SHA-256: `88b77c5f343117b354b5039d571bf03bf8867fcd7fb4f8fc91c1e1aefca7a048`
- component module SHA-256: `f9c92317abc562ac5175f90074238c666de55d557b02e0de368841676f4d910d`
- canonical top-1 / top-2 / regret: `0.75` / `1.0` / `0.116667`
- complexity: `3` (bound is 4)
- ND-1 / ND-2 / ND-3: all hold; strict-unique-max `6` against floor 4
- own-selection equivariance: `40/40`; full-order invariance `40/40` (descriptive only)
- section-14 action-value equivalence: `40` pairs, 0 failures
- Tier-2 ceiling for its declared feature map: top-1 `0.75`, top-2 `1.0`
- `longest_artifact` read-out (reported only, non-selecting): top-1 `0.25`, top-2 `0.5`, regret `0.600000`
- leave-one-source-out: `0` failing folds; fragile label `none`
- tie-dependent cases (reported only): `2`

Sufficiency label: `estimator-only-change-sufficient`.

## 7. Sufficiency qualification

Sufficiency, not superiority: a pass establishes that changing this one component is sufficient. The untested arm is untested, not falsified. No claim of optimality, minimality, or uniqueness is made, and the study does not attribute the preserved fresh-confirmation failure to the estimator, to the adapter, or to either component family.

## 8. H-R3 ceiling finding

H-R3 predicted that no function of the authorized semantic state could attain the criterion. The Tier-1 ceiling is above the criterion, so H-R3 is not confirmed: the authorized public state can order the legal targets well enough for some case-specific rule to reach the gate, and the achieved top-1 equals that ceiling while top-2 equals the ceiling exactly.

## 9. H-R4 interpretation (interpretation, not a proven diagnosis)

The usefulness target is authored from a hidden logical role and hidden mechanism family that the public channel does not carry. The selected component's mechanism cites a published structural gap (the published general-dependency category is never attached to a candidate, so r4 references can never link) and a published cue mapping. Its fallback clause -- when no candidate family carries a directional support cue, treat the general-dependency fallback category as the most informative target -- is calibrated to a development-observed structural regularity, not to a published rule stating that the fallback category is inspection-worthy: in both ownership-family development cases the maximum-usefulness target is exactly the r4 target. Read plainly, the fallback clause is a public-surface correlate of the hidden authored role. The pass is therefore compatibility with a target authored from hidden roles and is not evidence of authorization reasoning.

Supporting evidence:

- preregistration section 1.2 L1 records that r4 references can never link to a candidate under the fixed adapter
- preregistration section 1.2 records that both ownership-family development cases have their maximum-usefulness target at the r4 target
- preregistration section 1.2 H-R4 records that usefulness is a pure function of the hidden role and hidden mechanism family
- the passing component attains exactly the Tier-1 ceiling (top-1 0.75, top-2 1.0) and its own Tier-2 ceiling

Residual uncertainty: With eight development instances the study cannot separate a genuine structural rule from a coincidence of this fixture family, and no untouched confirmation population was consulted or generated. The interpretation is recorded as a judgement with its evidence, not as a proven causal diagnosis.

## 10. Claim boundary (verbatim)

> Under the fixed, frozen AuthzGym v1.3 instrument -- its authored usefulness labels, its five-category adapter surface, its equal-weight canonical scoring, its frozen tie rule, and its preregistered engineering screen -- there exists a deterministic, case-independent, invariance-certified component of bounded complexity whose inspection-target ordering meets the existing engineering gate, and the section-4.2.1 non-degeneracy requirement, on the eight canonical development source instances, using only authorized public semantic outputs and no privileged information.

What a pass must never be described as: general authorization reasoning or evidence about authorization competence; adaptive routing success, conditional routing, or action selection working; SER architecture superiority or any comparison against ReAct, fixed-order, monolithic, or ordinary-agent baselines; realistic GitLab transfer or transfer to any real repository; real-world action-value validity or evidence that these values mean anything outside this fixture family; model or provider capability, since no inference is run at any point; validation of the usefulness target, the instrument, or the benchmark; a diagnosis of the cause of the preserved fresh-confirmation failure or an attribution of that failure to the estimator, to the adapter, or to either component family; the best, smallest, or only admissible repair; and grounds to promote H-001, H-016, H-017, H-018, or M-013, or to change any concept maturity.

Artifact classifier: `development_component_compatibility_diagnostic`; not an `E-*` evidence record.

## 11. Development-only status

This development report establishes compatibility on the eight canonical
development source instances only. It does not establish, and must not be
reported as suggesting, that the component would pass a confirmation
population. No successor confirmation population was generated, frozen,
or accessed, and executing the section-8 protocol requires a separate
authorization naming the frozen component hash and this report's hash.

Directional effect metrics, where reported, are derived interface diagnostics from fact semantics and are not a second independent capability signal. This report renders no directional-effect table.

## 12. Procedural deviations

- The pre-ADR-0021 step-0 integrity pass hashed 16 confirmation-named
  files; recorded in `STUDY_BLOCKER.md` section 5 and
  `ACCESS_LEDGER.jsonl` (`confirmation_path_hashing_deviation`), and not
  retroactively authorized. The integrity procedure now fails closed.
- The candidate stage was invoked twice: the first invocation exposed an
  implementation defect in this study's own firewall check 7, the checker
  was corrected, and the stage was re-run. Candidate sources were
  byte-identical across invocations and gate numbers were identical, so no
  candidate was tuned and no selection decision used the first round.
  Recorded in `CANDIDATE_LEDGER.jsonl` as `duplicate_evaluation_round`.

## 13. Freeze record

- selected component class SHA-256: `88b77c5f343117b354b5039d571bf03bf8867fcd7fb4f8fc91c1e1aefca7a048`
- selected component module SHA-256: `f9c92317abc562ac5175f90074238c666de55d557b02e0de368841676f4d910d`
- fragile label: `none`
- report markdown SHA-256: `None`
- report JSON SHA-256 (own field omitted): `None`
- historical estimator SHA-256: `092a7a87d1227c1a1c85ac46c7122e38ac1b6b24d7aaa90abee05abfe4167393`

A later confirmation authorization must name the component hash and the
report hash above. None is granted here.

