# AuthzGym v1.3 downstream component repair study -- development-only preregistration

Condition ID: `est-repair-v1.3.1`

Status: `proposed_pending_sol_astra_decision`

Authority chain: ADR-0019 ->
`experiments/authzgym_semantic_contract_v1_3/PREREGISTRATION.md` ->
`experiments/authzgym_semantic_contract_v1_3/ORACLE_BLOCKER.md` -> the accepted
external adjudication of the fresh-confirmation failure -> this document.

Date drafted: 2026-09-18

This document specifies a bounded, development-only study. It is a
specification, not an accepted decision. It authorizes nothing by itself; see
section 12. It does not modify AuthzGym v1.3 semantics, and no step in it runs a
model or provider call.

---

## 0. Fixed inheritance

The following are treated as fixed inputs and are not reopened anywhere in this
document or in any artifact it produces.

1. AuthzGym v1.3 source-local answerability passed on development
   (`ANSWERABILITY_VALIDATION.json`, certificate `d308e68b...`) and on the fresh
   confirmation population (`5887f8cb...`). Both remain valid.
2. The unchanged historical estimator passed the development canonical oracle
   gate (top-1 0.625, top-2 0.875, mean normalized regret 0.175, 0 illegal
   targets, 40/40 transformation equivalence within `1e-12`).
3. The same unchanged estimator failed the preregistered fresh-confirmation
   canonical top-2 gate at 0.750 against the frozen `>= 0.80` requirement
   (top-1 0.625, regret 0.242, 0 illegal targets, 40/40 equivalence).
4. That failed result is preserved without reinterpretation. It is not rescored,
   re-derived, re-aggregated, re-explained, or averaged with any other number.
5. The top-2 threshold remains `>= 0.80`. The top-1 `>= 0.60` and regret
   `<= 0.35` thresholds likewise remain unchanged.
6. V1.3 semantic rules, prompt, schemas, fact/effect/relation meanings, scoring,
   the usefulness definition, the tie rules, and the seven transformations
   remain frozen.
7. The historical estimator (`src/ser/authzgym/policies.py`, source SHA-256
   `092a7a87d1227c1a1c85ac46c7122e38ac1b6b24d7aaa90abee05abfe4167393`) and the
   fixed section-13 adapter (`src/ser/evaluation/authz_v1_3.py`) remain
   byte-preserved baseline artifacts.
8. The current confirmation population (`confirmation_v1_3`, layouts 40/41,
   population hash `ec4d05d8...`) is **spent** for confirming any revised
   estimator or adapter.
9. Any revised estimator/adapter is a separate, prospectively specified,
   separately versioned condition.
10. A newly frozen untouched confirmation population is required before any
    revised component can be accepted. Section 8 specifies it.
11. Model/provider inference remains unauthorized.

---

## 1. Hypothesis

### 1.1 The narrow hypothesis under test

> **H-R.** There exists a deterministic, case-independent function from the
> authorized v1.3 public semantic state of a single response -- `facts` f0--f16,
> `candidate_effects` c0--c3, `unresolved_targets` tN x r0--r4, together with the
> public candidate families and the legal-target set -- to a total preorder over
> the legal uninspected targets, which on the eight canonical development source
> instances attains top-1 `>= 0.60`, top-2 `>= 0.80`, and mean normalized regret
> `<= 0.35` under the frozen section-13 scoring and tie rules, while satisfying
> the invariance, non-degeneracy, complexity, and input-allowlist certificates
> defined in sections 2, 4, and 9.

H-R is a statement about **component/instrument compatibility**, not about
authorization reasoning, model capability, or architecture. See section 10.

The answer is not assumed to be yes. Two of the four sub-hypotheses below assert
that no such function exists, and section 1.3 records why they are live.

### 1.2 The four sub-questions

These are stated so that an outcome can be described more precisely than
pass/fail. They are **not** a partition and not a causal decomposition: H-R1 and
H-R2 are sufficiency claims that may both hold, H-R3 is a computable bound, and
H-R4 is an interpretation the report must argue rather than a hypothesis the
study decides. Nothing here licenses saying that one component caused the
preserved confirmation failure.

**H-R1 -- Estimator-side sufficiency.** A change confined to the estimator, with
the fixed adapter unchanged, is *sufficient* to meet the criterion.

H-R1 is a sufficiency claim, not an attribution claim. Confirming it shows that
the information the fixed adapter already delivers can be scored well enough by
some admissible estimator. It does **not** establish that the estimator was the
sole, the primary, or the causal locus of the observed shortfall, and it does not
falsify H-R2: an adapter-side change may be independently sufficient as well, and
the study does not test for that once it has stopped (section 4.6).

Motivating mechanism observation: `estimate_action_values` computes per-category
plausibility as
`max((max(0.0, support.get(item, 0.0)) for item in linked), default=0.0)`. The
`max(0.0, ...)` clamp makes `contradict`, `neutral`, and `unknown` mutually
indistinguishable at the value layer. Whenever no candidate family carries
`support`, every legal target receives the identical score `0.05 + 1.0 = 1.05`
and the ranking collapses entirely to the tie-break. This mode is directly
observable in development: it occurs in 2 of the 8 canonical cases (both
ownership-family sources, where f10 and f11 are both absent so c0 is `unknown`
and c1/c3 are `contradict`).

Test signature: an **adapter-preserving** estimator change, evaluated once,
clears the criterion. Recorded outcome label on success:
`estimator-only-change-sufficient`.

**H-R2 -- Adapter-side sufficiency.** A change confined to the section-13
adapter, with the estimator unchanged, is *sufficient* to meet the criterion.

H-R2 is likewise a sufficiency claim. Confirming it shows that restoring
information the fixed adapter currently discards is enough for the unchanged
estimator to meet the criterion. It does **not** establish that the adapter was
the sole or primary locus of the shortfall, and it does not falsify H-R1.
H-R1 and H-R2 are not mutually exclusive and are not jointly exhaustive; both
may hold, and the study stops before it could distinguish them (section 4.6).

Three motivating losses, each verifiable by reading the frozen code rather than
by fitting:

- *L1, unrepresentable category.* The adapter maps all five relation categories
  to internal tags, but `CandidateHypothesis.relation_tags` only ever carries
  `ownership_path`, `membership_path`, `role_path`, `context_path`. No candidate
  carries `general_dependency`. An `r4` reference therefore has an empty `linked`
  set and can never receive non-zero plausibility, permanently tying it with
  every unsupported category. In both ownership-family development cases the
  maximum-usefulness target is exactly the `r4` target.
- *L2, collapsed enum.* `EFFECT_SIGN` maps both `neutral` and `unknown` to
  `0.0`, discarding the published distinction between "mixed local cues present"
  and "no directional cue under this rubric."
- *L3, unused facts.* `adapter_observation` places the true fact slots into
  `SemanticObservation.facts`, but `estimate_action_values` never reads that
  field. All 17 fact booleans are discarded at the value layer.

Test signature: an **estimator-preserving** adapter change, evaluated once,
clears the criterion. Recorded outcome label on success:
`adapter-only-change-sufficient`.

A passing Arm C candidate is recorded as `joint-change-sufficient`, which
likewise asserts only that the versioned pair is sufficient, not that a
single-component change was impossible -- Arms A and B having been exhausted
within budget is a statement about the budget, not a proof of impossibility.

**H-R3 -- Insufficiency of the authorized semantic state.** No function of the
authorized state can attain the criterion, because the target-discriminating
content of that state is exhausted by the 5x5 target-by-category matrix.

Argument: within one case, `facts` and `candidate_effects` are properties of the
*current artifact only* and are therefore constant across all legal targets.
They can reweight categories; they cannot order two targets that share a
category vector. Any authorized-state function must assign equal value to
targets with identical category vectors, so the attainable ranking is a preorder
on the category partition, refined only by the frozen evaluator ordinal
tie-break.

This makes H-R3 **decidable in the negative direction before any candidate is
written**: compute the ceiling (section 4.7, implementation step 3). If the
ceiling on top-2 is below 0.80, H-R is false and the study terminates with no
search.

**H-R4 -- Interpretive question: compatibility with an authored hidden-role
target.** H-R4 is not a mechanically decidable hypothesis and the study does not
attempt to prove it. It is the interpretation the report must address in words:
*given that the usefulness target is authored from information the instrument
deliberately withholds, what does a passing or failing component actually mean?*

Ground: `src/ser/authzgym/generation.py::_episode` assigns
`usefulness = {entry: 0.40, guard: 0.25, resolver: 0.25, policy: 0.25,
service: 0.25, tests: 0.65}` and then sets
`usefulness[DISCRIMINATING_ROLE[mechanism]] = 1.0`. Usefulness is therefore a
pure function of the **hidden logical role** and the **hidden mechanism family**.
ADR-0019 retired f20--f24 for precisely this reason ("retired because test role
is hidden and the source does not identify a privileged implementation target")
and keeps roles hidden by design. The public channel is constructed not to carry
the variable the target is authored from.

Reporting obligation, not a test: the selected candidate's written mechanism
rationale must cite a *published v1.3 semantic rule*. Where the available
rationale is instead an observed correlation between hidden role and public call
context (or between hidden role and a public surface statistic), the report must
say so plainly and must qualify the pass as compatibility with a target authored
from hidden roles, whatever the score. This is a judgement recorded as an
interpretation with its evidence, not a causal diagnosis the study has proven.
The hidden-role/category contingency (section 3.2) is reported as the evidence
for that judgement; it does not by itself decide it.

### 1.3 Clean-failure conditions

The study is capable of failing cleanly, and three distinct clean failures are
pre-defined:

- the section-4.7 ceiling falls below the criterion (H-R3 confirmed, no search);
- the budget is exhausted with no admissible candidate meeting the criterion --
  neither an adapter-only nor an estimator-only change was *shown sufficient*
  within the admissible complexity boundary and the attempt budget, which is a
  bounded negative result about that class and budget, not a proof that no such
  component exists;
- a candidate meets the criterion only via a forbidden input or above the
  complexity bound (the H-R4 interpretation is recorded).

None of these outcomes authorizes any change to the instrument. See section 7.

### 1.4 A power limitation that must be stated up front

There are 8 canonical development cases and 8 canonical confirmation cases. The
top-2 gate at `>= 0.80` means `>= 7/8`. A component whose true per-case top-2
probability is 0.875 fails a one-shot 7/8 gate roughly one time in three. The
development study therefore **cannot** establish that a candidate will pass
confirmation; it can only eliminate candidates that fail development, and require
that any passing candidate's success be structural rather than numerical. This is
why the gate in section 4.2 includes a structural non-degeneracy requirement, and
why a higher point score is never treated as a better result (section 4.6).

---

## 2. Component boundary

### 2.1 What may change, and in what order

Exactly one component changes if possible. The arms are attempted in this fixed
order.

| Arm | Component that may change | Component held byte-frozen | Precondition |
| --- | --- | --- | --- |
| **A** (preferred) | the semantic-to-estimator adapter | the estimator (`policies.py`, hash `092a7a87...`) | none |
| **B** | the estimator | the fixed section-13 adapter | Arm A exhausted with no admissible pass |
| **C** (joint) | both, as one versioned unit | -- | Arms A and B both exhausted with no admissible pass, **and** a written justification that the defect is irreducibly split across the component boundary |

Arm C requires the justification to be mechanical, not numerical. The only
justification contemplated in advance is the L1/clamp pair: `general_dependency`
has no representable tag on the adapter side while the `max(0.0, ...)` clamp
destroys sign on the estimator side, so neither side alone can express a
direction for a category that has no candidate. If a different joint rationale
is proposed, it must be stated in the same form before any Arm C candidate is
written.

### 2.2 File placement and preservation

No existing file is edited. A revised component is a **new module**, so the
baseline artifacts stay byte-identical and independently runnable.

- Arm A adapter: `src/ser/evaluation/authz_v1_3_1_adapter.py`
- Arm B estimator: `src/ser/authzgym/policies_v1_3_1.py`
- Arm C: both of the above, versioned together as one condition.

`src/ser/authzgym/policies.py` and `src/ser/evaluation/authz_v1_3.py` are
protected files (implementation handoff, protected-file list).

### 2.3 Versioning

Every artifact carries the full identifier
`est-repair-v1.3.1-{A|B|C}-{k}`, where `k` is the attempt index within the arm.
The joint condition is versioned as a single unit; its two files are hashed
together and never reported as two independent results.

### 2.4 Permitted inputs -- exhaustive allowlist

The revised component may read exactly these, and nothing else:

1. `facts` f0--f16 of the current response;
2. `candidate_effects` c0--c3 of the current response;
3. `unresolved_targets`, i.e. the `tN` x `r0..r4` boolean matrix of the current
   response, restricted to legal targets;
4. the public `candidate_hypotheses` array: `slot`, `effect_family`, and the
   published `description` string;
5. frozen constants read from `PUBLIC_CONTRACT.json`: `fact_slots`,
   `effect_support_cues`, `effect_counter_cues`, `effect_values`,
   `relation_slots`, `relation_precedence`, `candidate_slots`;
6. `legal_uninspected_target_slots` and `current_artifact_slot` from
   `runner_control`;
7. the cardinality of the legal-target set.

Anything not on this list is forbidden, whether or not section 2.5 names it.

### 2.5 Forbidden inputs -- blocking

Each item below is a blocking violation. Detection is by the static and dynamic
checks in section 9, which are built before any candidate is written.

- **Retired labels.** f17--f24, in any form, including reconstruction from
  combinations of retained facts that reproduces a retired label's meaning
  (for example, deriving f17 as `f0 AND f10`).
- **Hidden roles.** `entry`, `guard`, `resolver`, `policy`, `service`, `tests`;
  `LOGICAL_ROLES`, `DISCRIMINATING_ROLE`, `logical_role_index`,
  `ArtifactSpec.role`, `AuthorizationTruth`, mechanism identifiers `h1`--`h4`.
- **Evaluator-only metadata.** Gold annotations, evidence certificates,
  `usefulness_by_variant_target_slot`, `source_family`,
  `public_id_by_canonical_artifact_id`, restricted transformation maps, any
  field of `*_RESTRICTED_POPULATION.json`.
- **Confirmation identifiers.** Any confirmation case id, public-input hash,
  population hash, schedule entry, certificate, count, or file path, from
  `confirmation_v1_3` or any successor population.
- **Restricted ordinals.** `canonical_source_ordinal_by_variant_slot` and
  `canonical_ordinal_by_variant_public_id`. The component must emit its own
  complete order, or emit an order with explicitly declared ties which the
  evaluator's frozen ordinal rule then breaks. The component may not read the
  ordinal in order to break its own ties.
- **Oracle priors.** Any non-empty initial epistemic state, any prior
  observation, any `current_epistemic_summary`, any v1.2 stored response or
  score, any oracle diagnostic output.
- **Case-specific hacks.** Any branch keyed on a case id, source episode id,
  public artifact id, path, exported symbol, candidate public label, variant
  name, population hash, or literal target slot index.
- **Non-semantic public surface statistics that correlate with hidden authoring
  roles.** Named specifically: `line_count`; inventory array position or order;
  and the lexical content of `public_id`, `path`, `exported_symbols`, or
  candidate `public_label`.

The last item is added by this specification and is **not** a new semantic rule:
preregistration section 2 already declares public IDs, paths, opaque candidate
labels, and inventory order to be "addressing data only," and declares exported
symbol spelling excluded from relation-category classification. The prohibition
on `line_count` is the one extension, and it is motivated by a measured hazard:

> On all eight development source instances, `argmax(line_count)` uniquely
> identifies a single artifact (26 lines, against 18--20 for every other), and
> that artifact's authored usefulness is exactly 0.65 -- the second rank -- in
> every case. A component that ranked the maximum-`line_count` artifact second
> would secure top-2 on every case with no semantic content whatsoever. That
> would clear the gate as a benchmark-surface exploit, not as a repair.

`line_count` retains its existing role in the frozen population builder (it
defines the `longest_artifact` variant). It is forbidden only as a component
input.

### 2.6 Invariance obligations on the revised component

The revised component's **own** value vector and **own** declared ranking must
be invariant, after mapping through the recorded transformation maps, under all
five equivalence variants: `artifact_reordering`, `symbol_renaming`,
`candidate_label_renaming`, `artifact_identifier_variation`, and
`combined_permutation`.

This is an addition to, not a relaxation of, the frozen section-14 check, and it
closes a gap this review measured:

> The historical estimator's own selection rule,
> `max(values, key=lambda item: (values[item], item))`, breaks ties by
> lexicographic artifact id and is therefore **not** invariant to identifier
> renaming. On the development population its own selection changes in 4 of 40
> equivalence checks -- `artifact_identifier_variation` and
> `combined_permutation` for both ownership-family sources, exactly the two
> fully degenerate cases. The frozen oracle harness does not detect this,
> because `action_diagnostic` re-ranks by the restricted canonical ordinal
> before scoring; the preregistered equivalence check validates action *values*
> and harness ranking, not the estimator's own argmax.

Both readings are correct and both are preserved: the section-14 check remains
exactly as frozen and continues to pass for the baseline, and the new
own-ranking check is reported separately as a property of each candidate,
including the baseline, where it is recorded as 36/40.

---

## 3. Development data and exposure

### 3.1 Permitted development data

- `experiments/authzgym_semantic_contract_v1_3/DEVELOPMENT_PUBLIC_POPULATION.json`
  (56 cases, population hash `dda4e0c0...`) and `DEVELOPMENT_SCHEDULE.json`.
- `annotations/development_annotations.jsonl` (certificate hash `d308e68b...`),
  used exactly as the frozen oracle validator uses it: as the gold semantic
  response fed through the adapter. No model response exists or is authorized.
- `DEVELOPMENT_RESTRICTED_POPULATION.json` -- **evaluator channel only.** The
  harness reads `usefulness_by_variant_target_slot` and
  `canonical_source_ordinal_by_variant_slot` to score and to break ties. The
  component never receives them, and section 9 proves it.
- `PUBLIC_CONTRACT.json`, `prompts/semantic_observation_v1_3.txt`,
  `schemas/semantic_vocabulary_v1_3.json`.
- `DEVELOPMENT_TRANSFORMATION_MAPS.json` -- evaluator channel only, for mapping
  variant outputs to canonical ordinals in invariance checks.
- The frozen estimator and adapter, as baselines.
- Synthetic implementation fixtures, if needed, authored from the published
  grammar in preregistration sections 3--6. A synthetic fixture may not copy,
  paraphrase, or be derived from any development or confirmation case content,
  and may not be used in any selection metric.

### 3.2 Permitted diagnostics

Per-case component value vectors and rankings; degeneracy census (count of cases
with non-unique maximum and non-unique second); the category-partition structure
of each case; the section-4.7 ceiling computations; family-macro summaries; the
`longest_artifact` non-canonical read-out; leave-one-source-out stability; and,
for reporting only, the contingency between hidden logical role and public call
category (evaluator channel, used to characterize H-R4, never to design a
candidate).

### 3.3 Forbidden exposure

Every confirmation path is excluded from the development harness by a filesystem
allowlist that fails closed:

`CONFIRMATION_PUBLIC_POPULATION.json`, `CONFIRMATION_RESTRICTED_POPULATION.json`,
`annotations/confirmation_annotations.jsonl`,
`CONFIRMATION_TRANSFORMATION_MAPS.json`, `CONFIRMATION_SCHEDULE.json`,
`CONFIRMATION_SOURCE_MANIFEST.json`, `CONFIRMATION_ELIGIBILITY.json`,
`CONFIRMATION_ANSWERABILITY_VALIDATION.json`,
`CONFIRMATION_ORACLE_VALIDATION.json`, `CONFIRMATION_ORACLE_BLOCKER.md`, and the
`confirmation` block of `ORACLE_VALIDATION.json`.

### 3.4 Motivation record, and the boundary around already-spent knowledge

This study was **motivated by an observed confirmation failure**. That fact is
recorded once, here and in the report header, so that no later reader mistakes
it for a prospectively planned investigation.

Two pieces of confirmation-derived knowledge already exist in the repository and
in the accepted adjudication, and cannot be unlearned:

1. the aggregate confirmation result (top-1 0.625, top-2 0.750, regret 0.242);
2. the mechanism sentence in `ORACLE_BLOCKER.md`: "several canonical
   confirmation gold responses contain only non-positive candidate effects. The
   unchanged estimator then assigns the same `1.05` score to every referenced
   legal target and falls back to canonical ordinal order."

Both are recorded as motivation and **must not be used to select or tune a
candidate**. The discipline that makes this enforceable is that the same
degenerate-tie mode is independently and fully visible in the development
population (2 of 8 canonical cases, section 1.2 H-R1). Every design decision in
this study must cite the development observation or a published v1.3 semantic
rule as its ground. No candidate rationale may cite the confirmation aggregate,
the confirmation mechanism sentence, or any inference about how many
confirmation cases are degenerate. A rationale that does so makes the candidate
inadmissible.

The spent confirmation population is not opened, counted, sampled, hashed
afresh, or characterized at any point in this study.

---

## 4. Development objective

### 4.1 Unit of evidence

The unit is the **source instance**: 8 of them, one canonical `base_entry` case
each. The 56-case population contains 8 x 7 cases, but 5 of the 7 variants are
semantic-equivalence transformations of `base_entry` and carry zero independent
information about whether a ranking rule is correct. They are invariance tests,
not samples.

`longest_artifact` is a genuinely different source-local question (different
current artifact, different facts, different relation matrix, and a target set
that includes the entry artifact with usefulness 0.40). It is reported as a
robustness read-out and is excluded from selection.

### 4.2 Primary criterion

All of the following, on the 8 canonical development entries, under the frozen
section-13 scoring, tie, and regret definitions:

| Metric | Requirement | Source |
| --- | --- | --- |
| canonical top-1 | `>= 0.60` | frozen, unchanged |
| canonical top-2 | `>= 0.80` | frozen, unchanged |
| mean normalized regret | `<= 0.35` | frozen, unchanged |
| illegal target/value count | `= 0` | frozen, unchanged |
| section-14 transformation action-value equivalence | 40/40 within `1e-12` | frozen, unchanged |
| component own-ranking invariance | 40/40 after ordinal mapping | new, section 2.6 |
| input-allowlist conformance | zero violations | new, section 9 |
| non-degeneracy requirement ND-1/ND-2/ND-3 | all three hold | new, section 4.2.1 |

The first five rows are the frozen engineering gate, unchanged in value and
definition. The last three are admissibility requirements on the component,
fixed before any candidate is written.

### 4.2.1 The non-degeneracy requirement

The failure that spent the confirmation population was rank collapse, not a
narrow numerical miss: with no candidate family carrying `support`, every legal
target received an identical value and the outcome was decided by the tie-break.
A component that met the point thresholds while remaining degenerate would
reproduce that exposure. The gate therefore includes, prospectively:

- **ND-1, no complete degeneracy.** In no canonical case do all legal targets
  receive a single common value.
- **ND-2, separable maximum.** In every canonical case, the set of targets
  attaining the component's maximum value is contained within a single
  category-vector equivalence class, as those classes are computed in section
  4.7 Tier 1. The component may leave tied only targets that no authorized-state
  function could separate; it may never leave separable targets tied for first.
- **ND-3, at least as strong as B2.** The component's strict non-degeneracy
  certificate count -- the number of canonical cases with a strictly unique
  maximum value -- must be greater than or equal to the count measured for
  baseline B2 on the same 8 canonical cases.

ND-3's numeric floor is B2's measured value. It is computed and frozen in
`BASELINES.json` at handoff step 4, **before any candidate is written**, and is
never adjusted afterwards. ND-1 and ND-2 are absolute and require no
measurement.

ND is strictly stronger than B2: B2 itself fails ND-1, because in a case where no
family carries `support` it assigns every target the same value. Baseline B1
fails ND-1 in all 8 cases and B0 fails it in 2.

ND-2 is deliberately bounded by the information ceiling so that the gate cannot
demand more separation than the authorized state contains. Where two targets
share a category vector, leaving them tied is correct behaviour, not degeneracy.

### 4.3 Metrics, weighting, tie handling

- **Weighting.** Equal weight per source instance, 1/8. No family, variant, or
  case reweighting. No repeat averaging applies: the oracle-conditioned
  diagnostic uses gold responses, one entry per case.
- **Tie handling.** Unchanged. The evaluator ranks by `(-value, canonical
  ordinal ascending)`. A case in which all legal targets have equal usefulness
  is `nondiscriminating`, scores top-1 and top-2 true with regret 0, and is
  excluded from threshold denominators. (No development case is
  nondiscriminating; all 8 are discriminating.)
- **Tie dependence, recorded separately.** A candidate is `tie-dependent` in a
  case if removing the evaluator's ordinal tie-break would change whether that
  case passes top-1 or top-2. Tie dependence is counted and reported for every
  candidate and every baseline. It does not change the score and it is not itself
  a gate; ND-1 and ND-2 are the gated form of the same concern.

### 4.4 Secondary reported metrics, non-selecting

Family-macro top-1/top-2/regret across the four families; the
`longest_artifact` read-out (the baseline's is top-1 0.125, top-2 0.375, regret
0.783, and is reproduced for every candidate); the degeneracy census; the
leave-one-source-out table.

### 4.5 Acceptable tradeoffs

None below the frozen floors: top-1 may not fall below 0.60 to buy top-2, and
regret may not exceed 0.35. There is no tradeoff *between* candidates, because
this study does not compare passing candidates (section 4.6). Every requirement
in section 4.2 is conjunctive: a candidate satisfies all of them or it does not
pass.

### 4.6 Existence study: stop at the first admissible pass

This is a minimal existence study, not a search for the best repair. Its question
is whether an admissible component exists at all, and the gate in section 4.2 is
the complete and final definition of "admissible pass."

**The study stops at the first candidate that satisfies every requirement in
section 4.2.** No further candidate is written, in that arm or any other, and no
remaining budget is spent. That candidate is the result.

There is consequently **no ranking among passing candidates and no comparison
rule**, because the design admits at most one passing candidate. Point score is
never treated as better or worse beyond pass/fail: with 8 canonical cases a
difference of 1/8 is one case, and preferring a higher score would be preferring
noise (section 1.4). The structural quality that would otherwise have been a
ranking key is instead a gate, as ND-1/ND-2/ND-3 in section 4.2.1.

Two consequences follow and must be stated in the report:

- A pass establishes **existence and sufficiency**, not optimality. Nothing in
  this study licenses the claim that the selected component is the best, the
  smallest, or the most principled admissible repair; better admissible
  components may exist and were not searched for.
- A pass in one arm leaves the other arm **untested**, not falsified. Stopping in
  Arm A says nothing about whether an estimator-only change would also have
  sufficed, and the reverse.

### 4.7 The information ceiling, computed before any search

Two tiers, both implemented in step 3 of the handoff.

**Tier 1 -- absolute ceiling (blocking).** Within a case, any authorized-state
function assigns equal value to two legal targets with identical category
vectors, because every other allowlisted input is constant across targets within
the case. Partition each case's legal targets into classes by category vector.
An achievable ranking is: choose an order over classes; within a class, the
evaluator's ascending canonical ordinal applies. Compute, per case, whether
*some* class ordering yields top-1, and whether *some* class ordering yields
top-2. Average over the 8 cases. This is an upper bound no authorized-state
function can exceed, even one allowed to be case-specific.

If Tier-1 top-2 `< 0.80` or Tier-1 top-1 `< 0.60`, H-R is false. The study
terminates with outcome `authorized-information-insufficient`, no candidate is
written, and no budget is consumed.

**Tier 2 -- case-independent ceiling for a declared feature map (reported per
candidate).** A real component is one function, not eight. Given a candidate's
declared feature map `phi` over the allowlisted inputs, group the 8 cases by
identical `(phi(case), class structure)` signature; a case-independent function
must order classes identically within a signature group. Compute the best
achievable average subject to that constraint. Tier 2 is reported alongside each
candidate's achieved score, so the report distinguishes "this candidate is
suboptimal" from "no candidate with this feature map can do better."

### 4.8 Complexity control

Complexity score:

```
complexity = (number of free numeric constants introduced)
           + 2 * (number of branches keyed on candidate effect_family)
           + 3 * (number of branches keyed on a specific relation category)
```

A candidate with complexity `> 4` is **inadmissible regardless of score**.

Rationale, stated so it is not mistaken for taste: the canonical development set
is 4 families x 2 layouts = 8 instances. A rule containing one clause per family
has 4 free choices over 8 instances and is saturated; its development score
cannot distinguish a semantic rule from memorization of the authoring pattern.
The bound of 4 permits a rule with sign handling plus one structural clause, and
forbids a per-family lookup table.

Constants inherited unchanged from the frozen code (`0.05`, `1.0`, the `1.5`
plausibility cap) are not counted as introduced. A candidate that differs from a
previous candidate only in the value of a numeric constant is inadmissible
(section 5.5).

### 4.9 Preventing tuning to transformed duplicates

Five mechanisms, all machine-enforced:

1. selection metrics are computed on `base_entry` cases only;
2. the harness asserts that the selection-metric function received exactly 8
   case ids, all with `variant == "base_entry"`, and raises otherwise;
3. the 5 equivalence variants enter only as pass/fail invariance checks and can
   never contribute to whether a candidate passes the section-4.2 gate;
4. `longest_artifact` is reported and is excluded from the section-4.2 gate;
5. **leave-one-source-out is mandatory and reported.** For each of the 8
   sources, recompute the criterion on the remaining 7. LOSO is a stability
   read-out, not a gate -- with 8 instances it cannot validate anything. A
   candidate that meets the criterion on all 8 while failing `>= 3` LOSO folds
   is labeled `fragile` in the report and in `CANDIDATE_LEDGER.jsonl`. The label
   does not change the pass, does not trigger further search, and is carried
   forward into any later confirmation authorization so that the fragility is
   visible to whoever decides it.

---

## 5. Search budget

### 5.1 What constitutes one attempt

One attempt is one named candidate `est-repair-v1.3.1-{arm}-{k}` consisting of:

- a complete component source file (or file pair, for Arm C), hashed;
- a written mechanism rationale of at most one paragraph, citing a published
  v1.3 semantic rule or a development-observed structural defect;
- exactly one evaluation against the development criterion.

Once the criterion has been evaluated for a candidate, that candidate is
**spent**. Editing it produces a new candidate and consumes budget.

Implementation iteration *before* the criterion is first evaluated -- making the
module import, fixing a crash, satisfying the allowlist checker, passing the
invariance harness -- is unlimited and consumes no budget.

### 5.2 Budget

| Arm | Maximum candidates |
| --- | --- |
| A (adapter-only) | 4 |
| B (estimator-only) | 4 |
| C (joint) | 2 |
| **Global maximum** | **10** |

### 5.3 Pre-search obligation

The section-4.7 Tier-1 ceiling is computed first and consumes no budget. If it
falls below the criterion, the study ends there.

### 5.4 Stopping rule

Stop at the first of:

1. Tier-1 ceiling below the criterion -- terminate before search;
2. **any candidate, in any arm, satisfies every requirement in section 4.2 --
   stop the whole study immediately**, do not open a later arm, do not write a
   further candidate in the current arm, and do not spend remaining budget
   looking for a better one;
3. Arm A exhausted without an admissible pass -- open Arm B;
4. Arms A and B exhausted without an admissible pass -- open Arm C, at most 2
   candidates;
5. the global maximum of 10 attempts is reached;
6. any candidate would require an input outside the allowlist, or a semantic
   ambiguity appears -- stop and record a blocker (handoff, stop conditions).

### 5.5 Anti-hill-climbing

- Candidate `k+1` must cite, in writing, a **mechanism-level** defect of
  candidate `k`, stated in terms of published v1.3 semantics or a
  development-observed structural property. "Scored 0.75, needs to be higher" is
  not an admissible rationale and the attempt is refused before it is evaluated.
- A candidate differing from a prior candidate only by the value of a numeric
  constant is inadmissible.
- No parameter scan, grid search, random search, or fitted weight of any kind.
- No candidate is deleted. Every attempt, including refused and failing ones, is
  recorded in `CANDIDATE_LEDGER.jsonl` with its hashes, rationale, metrics, and
  disposition.

### 5.6 Final selection

There is nothing to select. If the study stopped under rule 2, the single
candidate that triggered the stop is the result, by construction. If it stopped
under any other rule, no candidate passed and section 7 applies.

---

## 6. Baselines

All baselines run through the identical harness and appear in every table.

- **B0 -- preserved historical baseline.** Unchanged estimator (hash
  `092a7a87...`) with the fixed section-13 adapter. Expected reproduction:
  canonical top-1 0.625, top-2 0.875, regret 0.175, 0 illegal, 40/40 section-14
  equivalence, 36/40 own-ranking invariance, `longest_artifact` top-1 0.125 /
  top-2 0.375 / regret 0.783. Exact reproduction of the first five figures is the
  acceptance criterion for the harness itself (handoff step 1).
- **B1 -- degenerate null.** All targets receive an identical value; selection is
  the frozen ordinal tie-break alone. This is the correct null for the
  degenerate-tie mode and shows exactly what the tie-break alone buys.
- **B2 -- category-match floor.** Rank targets by whether their category set
  contains the relation category corresponding to the candidate family whose
  effect is `support`; leave all remaining ties declared. This is the smallest
  deterministic rule expressible from the authorized state. Its measured strict
  non-degeneracy certificate count fixes the ND-3 floor of section 4.2.1 and is
  frozen in `BASELINES.json` before any candidate is written.
- **B3 -- oracle usefulness ranking.** Evaluator-channel upper bound, reported so
  that regret denominators and the ceiling are legible. **Never a candidate**,
  never eligible for selection, and never described as achievable.

No broad architecture sweep. No parameterized family explored by scan. No
comparison to ReAct, fixed-order, monolithic, or any other architecture -- those
remain out of scope under ADR-0019 and the roadmap.

---

## 7. Failure interpretation

If no admissible candidate clears the development criterion, the recorded
outcome is chosen by this table, fixed in advance. It is not chosen by narrative
after the fact.

| Observation | Recorded outcome | Meaning |
| --- | --- | --- |
| Tier-1 ceiling `<` criterion | `authorized-information-insufficient` | The fixed v1.3 public channel cannot order the targets to the required precision. The limit is the instrument's declared scope, not the estimator family. |
| Ceiling `>=` criterion, no admissible candidate reaches it within budget | `no-sufficient-component-found-within-admissible-class-and-budget` | No adapter-only, estimator-only, or joint change was *shown sufficient* within the complexity boundary that 8 development instances can support and within the 10-attempt budget. The negative result is about that class and that budget. It does not attribute inadequacy to the estimator, to the adapter, or to either component family, and it is not a proof that no sufficient component exists. |
| Criterion reachable only via a forbidden input or complexity `> 4` | `target-alignment-mismatch-indicated` | Read as an indication, not a proof: the usefulness target appears reachable only through information the instrument deliberately withholds (hidden role/mechanism) or through generator surface regularities. The report states the supporting evidence and the residual uncertainty. |
| Criterion met but invariance, non-degeneracy, or allowlist certificates fail | `no-admissible-repair` | The candidate is not a component that could be confirmed, whatever it scored. |

### 7.1 What a failed study does not authorize

A failure of this study, in any of the four forms, does **not** authorize:

- redesigning AuthzGym v1.3 or any part of its semantics;
- re-authoring, re-weighting, retiring, or reinterpreting the usefulness labels;
- weakening or re-deriving the top-2, top-1, or regret thresholds;
- changing the fixed adapter category map, the relation precedence, or the
  effect truth table as a "semantic correction";
- re-running, re-reading, re-sampling, or reinterpreting the spent confirmation
  population;
- reinterpreting the preserved fresh-confirmation failure;
- generating a replacement confirmation population "to see";
- any model or provider inference.

A `target-alignment-mismatch` outcome in particular is an **input** to a future
instrument decision, not that decision. Whether an instrument whose usefulness
target is authored from hidden roles can support a downstream action-value
screen at all is a question for a separate ADR with its own preregistration.

### 7.2 What a failed study does not invalidate

Failure does not retroactively invalidate the v1.3 instrument, the passing
development and confirmation answerability results, the passing firewall result,
the preserved v1.2 corrigendum, or the preserved historical baseline.

---

## 8. New confirmation protocol

A revised component can only ever be accepted against a confirmation population
that is new, untouched, and frozen after the component is frozen. This section
specifies that population completely and in advance. **It specifies; it does not
authorize execution** (section 12).

### 8.1 Source and layout generation rule

- Generator: the unchanged frozen authoring method in
  `src/ser/authzgym/generation.py`, byte-unchanged, source hash recorded in the
  freeze record. No generator parameter, seed, template, or production is
  altered.
- Split label: `confirmation_v1_3_1`.
- Layout indices: **42 and 43**, disjoint from the development layouts and from
  the spent `confirmation_v1_3` layouts 40/41.
- Four mechanism families per layout, giving 8 source instances.
- Conversion: the already-frozen parameterized v1.3 conversion path, producing
  the same seven variants, 56 cases, and one scheduled call per case. The
  schedule is generated; **no call is authorized by this document**.

### 8.2 Content-independent selection

Layout indices are fixed here, before generation, by the successor rule: the
next unused indices in ascending order. No property of the generated content may
be inspected before freeze, and nothing about the population may be chosen after
generation. Reserved fallback pairs, in order, for the collision rule below:
44/45, then 46/47.

### 8.3 Duplicate and equivalence checks

All are blocking:

1. population hash differs from `dda4e0c0...` (development) and `0e20284b...`
   (spent confirmation public);
2. case-id sets pairwise disjoint across all three populations;
3. `public_input_sha256` sets pairwise disjoint;
4. no source-episode-id collision;
5. no byte-identical public input against any prior v1.3 population;
6. layout digests differ.

A collision is resolved by advancing to the next reserved layout pair recorded
in 8.2 -- **never** by inspecting content and choosing.

### 8.4 Immutable manifest

`CONFIRMATION_V1_3_1_SOURCE_MANIFEST.json`, separate public and restricted
bundle manifests, transformation maps, independent annotations and certificates,
and `FROZEN_INPUTS_V1_3_1.json`, all hashed under preregistration section 12
rules (UTF-8 canonical JSON, sorted keys, LF text, SHA-256; `manifest_sha256`
computed with its own field omitted, then stored).

### 8.5 Access ledger

`CONFIRMATION_V1_3_1_ACCESS_LEDGER.jsonl`, append-only, one record per open of
any confirmation path: timestamp, actor, path, operation, tool hash. Any read
recorded before the component freeze hash is written is a blocking violation
that spends the population immediately.

### 8.6 Isolation and custodian rules

Generation, conversion, certification, answerability, firewall, and oracle
validation run in an isolated process whose working directory contains no
development selection artifact and no candidate ledger. The runner emits only
aggregate pass/fail counts and hashes until the manifest is sealed.

The custodian -- the party that seals -- is a named party distinct from whoever
selected the candidate. Where the project cannot staff two parties, the
requirement is satisfied by the freeze ordering in 8.7, which seals the
component and publishes its hash *before* generation begins. That ordering is
required in either case.

### 8.7 Freeze timing

Strict order; each step's hash is recorded before the next begins:

1. development study complete; selected component source frozen and hashed;
   complete development report written and hashed;
2. a freeze record restating this section's parameters and naming those hashes;
3. generation, conversion, independent certification, answerability validation,
   and firewall validation of the new population;
4. the revised component's one-shot oracle gate on the new canonical entries;
5. seal.

Any deviation from this order spends the population.

### 8.8 One-shot evaluation

The revised component is evaluated **exactly once** on the 8 new canonical
confirmation entries against the unchanged gate: top-1 `>= 0.60`, top-2
`>= 0.80`, mean normalized regret `<= 0.35`, zero illegal targets, 40/40
section-14 action-value equivalence, plus the section-2.6 own-ranking invariance
check. One run, one record, pass or fail.

### 8.9 No case replacement after failure

A failing case is not replaced, repaired, regenerated, excluded, or reweighted.
A failed confirmation spends the population for that component **and every
derivative of it**, exactly as `confirmation_v1_3` is now spent. A later
component requires a further new population under this same protocol at the next
reserved layout indices.

### 8.10 No confirmation material influences development selection

Enforced by the ordering in 8.7, the ledger in 8.5, and a machine check in the
development harness whose filesystem allowlist excludes every `CONFIRMATION*`
path and fails closed on any access attempt.

---

## 9. Firewall requirements for the revised component

The existing `FIREWALL_VALIDATION.json` validates the v1.3 **normal
input/response** path: restricted-field mutation byte-equality over 56 cases,
public-only replay, import isolation, empty initial state, and channel
separation. It has limited demonstrated scope with respect to the **action-value
path**, which consumes the response and also touches restricted structures
(usefulness, canonical ordinals, transformation maps) inside the same harness.
The revised component therefore requires the following additional validation,
recorded as `FIREWALL_V1_3_1_VALIDATION.json`. All items are blocking.

1. **Input allowlist enforcement, static and dynamic.** Static: the component
   module's transitive import closure may not reach `ser.authzgym.generation`,
   `logical_role_index`, `AuthorizationTruth`, any restricted-population reader,
   any annotation/certificate loader, or any confirmation path. Dynamic: the
   component is invoked with a sealed input object exposing only the seven
   allowlisted items of section 2.4; any attribute access outside that set
   raises and is recorded as a failure.
2. **Restricted-field mutation over the action-value path.** Individually and
   all-at-once, mutate usefulness vectors, canonical ordinals, restricted
   transformation maps, `source_family`, hidden roles, mechanism identifiers,
   gold annotations, certificates, retired v1.2 expected tags, and confirmation
   identifiers. The component's emitted value vector and own declared ranking
   must be byte-identical across all 56 development cases under every mutation.
   (The evaluator's *score* legitimately changes when usefulness changes; the
   component's output must not.)
3. **Public-only replay of the action-value path.** From a bundle containing only
   the public population, the public contract, and the component, with
   restricted files absent from the filesystem and evaluator modules removed
   from the process path, the component reproduces byte-identical value and
   ranking output for all 56 cases.
4. **Ordinal non-consumption proof.** A static reference scan for
   `canonical_source_ordinal_by_variant_slot` and
   `canonical_ordinal_by_variant_public_id`, plus a runtime test in which those
   ordinals are permuted and the component's own ranking is unchanged.
5. **Surface-statistic non-consumption proof.** A targeted mutation battery on
   `line_count`, inventory order, `public_id`, `path`, `exported_symbols`
   spelling, and candidate `public_label`. Each is perturbed within the legal
   schema and the component's output must be byte-identical. This is the machine
   check for the forbidden class named in section 2.5 and is the gate that
   prevents the measured `line_count` exploit.
6. **Determinism and replay.** Two executions in different processes, different
   working directories, and different environment orderings produce byte-
   identical output. No dependence on wall clock, PID, hash seed, dict iteration
   order, or filesystem ordering.
7. **No writable shared state.** No module-level mutable cache in the component;
   a spy asserts that no oracle, gold, or annotation helper is called during
   component execution; normal and evaluator trace namespaces remain separate.
8. **Error-channel audit.** Exception messages, log lines, counts, and timing
   emitted by the component must not vary under the mutation battery of item 2.
9. **Recorded scope statement.** `FIREWALL_V1_3_1_VALIDATION.json` must state
   explicitly that it demonstrates isolation of the action-value path for these
   56 development cases and this specific component, and nothing broader. It
   does not supersede, extend, or re-run `FIREWALL_VALIDATION.json`, which
   remains byte-frozen with its own recorded scope.

---

## 10. Claim boundary

### 10.1 What a pass establishes

Exactly this, and it should be quoted in this form:

> Under the fixed, frozen AuthzGym v1.3 instrument -- its authored usefulness
> labels, its five-category adapter surface, its equal-weight canonical scoring,
> its frozen tie rule, and its preregistered engineering screen -- there exists a
> deterministic, case-independent, invariance-certified component of bounded
> complexity whose inspection-target ordering meets the existing engineering
> gate, and the section-4.2.1 non-degeneracy requirement, on the eight canonical
> development source instances, using only authorized public semantic outputs and
> no privileged information.

The claim is one of **existence and sufficiency**. A pass in a single-component
arm establishes that changing that one component is sufficient; it does not
establish that the other component was adequate, that the changed component was
the cause of the observed shortfall, or that the change is optimal, minimal, or
unique. The untested arm is untested, not falsified.

Artifact classifier: `development_component_compatibility_diagnostic`. It is not
an `E-*` evidence record.

### 10.2 What a pass must never be described as

- general authorization reasoning, or evidence about authorization competence;
- adaptive routing success, conditional routing, or action selection working;
- SER architecture superiority, or any comparison against ReAct, fixed-order,
  monolithic, or ordinary-agent baselines;
- realistic GitLab transfer, or transfer to any real repository;
- real-world action-value validity, or evidence that these values mean anything
  outside this fixture family;
- model or provider capability -- no inference is run at any point;
- validation of the usefulness target, the instrument, or the benchmark;
- a diagnosis of *the* cause of the preserved fresh-confirmation failure, or an
  attribution of that failure to the estimator, to the adapter, or to either
  component family;
- the best, smallest, or only admissible repair -- the study stops at the first
  admissible pass and does not search further;
- grounds to promote H-001, H-016, H-017, H-018, or M-013, or to change any
  concept maturity.

### 10.3 The development/confirmation distinction, stated in the claim itself

A development pass establishes compatibility **on the development instances
only**. It does not establish, and must not be reported as suggesting, that the
component will pass confirmation: 8 canonical cases against a `>= 7/8` gate
cannot support that inference (section 1.4). Only a one-shot pass on a newly
frozen untouched confirmation population under section 8 would establish the
corresponding *confirmed* compatibility claim -- and even that remains a
compatibility claim about a component and an instrument, never a capability
claim about reasoning, architecture, or transfer.

---

## 11. Implementation handoff

The ordered mechanical plan for DeepSeek is a separate document in this
directory: `IMPLEMENTATION_HANDOFF.md`. It specifies, per step, the files to add,
the protected files, the exact tests, the development artifacts, the acceptance
criterion, and the point at which implementation must stop if a semantic
ambiguity appears.

---

## 12. Authorization boundary

### 12.1 What this specification authorizes, if accepted

If -- and only if -- a Sol/Astra decision accepts this document and records that
acceptance as a new appended ADR, it authorizes:

- bounded offline development of the separately versioned component
  `est-repair-v1.3.1`, within the section-5 budget of at most 10 attempts;
- development-only evaluation of that component against the section-4 criterion,
  using the development population, its independent annotations, and its
  restricted evaluator channel;
- construction of the harness, ceiling computation, baselines, invariance
  checks, allowlist checkers, and firewall validation described in sections 6
  and 9;
- the writing of the development report, candidate ledger, and blocker records,
  whatever the outcome;
- generation and freezing of the future untouched confirmation package specified
  in section 8, **only if the accepting decision explicitly says so**, and only
  in the order fixed by section 8.7.

### 12.2 What it does not authorize, under any outcome

- model or provider inference of any kind;
- altering AuthzGym v1.3 semantics: rules, prompt, schemas, fact/effect/relation
  meanings, scoring, usefulness, tie rules, transformations, or populations;
- weakening, re-deriving, or reinterpreting the existing oracle gate, including
  the top-2 `>= 0.80` threshold;
- evaluating any candidate variant on the spent `confirmation_v1_3` population,
  or opening, sampling, counting, or characterizing it;
- reinterpreting the preserved fresh-confirmation failure;
- editing `src/ser/authzgym/policies.py`, `src/ser/evaluation/authz_v1_3.py`, or
  any artifact under `experiments/authzgym_semantic_contract_v1_3/`;
- Jev, architecture comparison, representation intervention, model escalation,
  graph policies, coupling operators, or any broader architecture change;
- automatic execution of the section-8 confirmation protocol -- executing it
  requires its own separate authorization naming the frozen component hash and
  the frozen development report hash;
- promotion of any concept, creation of any `E-*` evidence record, or any edit
  to `state/STATUS.yaml`, `plan/ROADMAP.md`, `CHARTER.md`, or `theory/`.

### 12.3 Status of this document

Proposed. No ADR has been appended, no canonical state document has been
edited, and no generated view has been regenerated. Acceptance is a Sol/Astra
decision, not an implementation choice.
