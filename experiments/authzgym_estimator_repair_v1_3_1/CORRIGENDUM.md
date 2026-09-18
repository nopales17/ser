# est-repair-v1.3.1 corrigendum 1

Status: `accepted`

Authority: ADR-0021. Authorizing decision for the study itself: ADR-0020.

Date: 2026-09-18

Scope: this document corrects three defects in the `est-repair-v1.3.1`
specification text that were surfaced when the study executed handoff step 1 and
stopped (`STUDY_BLOCKER.md`). It is append-only. It does **not** edit
`REPAIR_STUDY_PREREGISTRATION.md`, `IMPLEMENTATION_HANDOFF.md`, ADR-0019,
ADR-0020, or any historical artifact in place. Where this corrigendum and the
accepted preregistration text differ, this corrigendum governs prospectively and
the preregistration text stands as the accepted record of what was originally
written.

It corrects **no** research semantics, gate, threshold, budget, arm order,
stopping rule, non-degeneracy requirement, input allowlist, firewall
requirement, or claim boundary. Section 4 establishes that ADR-0020's
authorization resumes unchanged.

---

## 1. Correction 1 -- `longest_artifact` development baseline transcription error

### 1.1 Verified facts

`experiments/authzgym_semantic_contract_v1_3/ORACLE_VALIDATION.json` records, in
its `longest_artifact_noncanonical_observed` blocks:

| Split | top-1 | top-2 | mean normalized regret |
| --- | --- | --- | --- |
| `development` | 0.125 | 0.375 | **0.6583333333333333** |
| `confirmation_v1_3` | 0.0 | 0.25 | **0.7833333333333333** |

`REPAIR_STUDY_PREREGISTRATION.md` section 6 and `IMPLEMENTATION_HANDOFF.md` step
1 recorded the B0 `longest_artifact` read-out as top-1 0.125, top-2 0.375,
regret 0.783. The top-1 and top-2 values are the development values and are
correct. The regret value is the confirmation value. A single field was
transcribed from the wrong split.

### 1.2 Adjudication

This is a **drafting/transcription error in the specification text**. It is not
an experimental outcome, not a change in any measurement, not a correction to any
stored result, and not evidence about anything. No stored number changes:
`ORACLE_VALIDATION.json` and every other v1.3 artifact remain byte-unchanged, and
both splits' recorded read-outs stand exactly as they are.

### 1.3 Authorized correction

Handoff step 1 baseline reproduction is authorized against the development-split
value:

```
longest_artifact regret = 0.6583333333333333
longest_artifact top-1  = 0.125      (unchanged)
longest_artifact top-2  = 0.375      (unchanged)
```

`BASELINES.json` must record `recorded_expectation.longest_artifact_regret` as
`0.6583333333333333` and cite this corrigendum as the authority for the value.

### 1.4 What does not change

No gating metric or threshold is altered. `longest_artifact` remains
**reported-only and non-selecting**: preregistration section 4.1 excludes it from
the unit of evidence, section 4.2 excludes it from the gate, section 4.4 lists it
among secondary non-selecting metrics, and section 4.9 item 4 excludes it from
candidate assessment. The five figures that preregistration section 6 names as
the acceptance criterion for the harness itself -- canonical top-1, top-2,
regret, illegal-target count, and section-14 equivalence -- were never in
question and already reproduce exactly.

### 1.5 Additional already-exposed spent-confirmation information

Preregistration section 3.4 records two pieces of confirmation-derived knowledge
that already exist in the repository and cannot be unlearned. This corrigendum
appends a third:

> 3. The confirmation-split `longest_artifact` read-out: top-1 0.0, top-2 0.25,
>    mean normalized regret 0.7833333333333333.

It is recorded as already exposed because it was transcribed into the accepted
specification text and is restated in section 1.1 above. It carries exactly the
section-3.4 prohibition, restated here in full force:

- it may **not** be used in any candidate rationale, in component design, in
  candidate selection, in the stopping rule, in ND-1/ND-2/ND-3, in the Tier-1 or
  Tier-2 ceiling, or in the interpretation of any future untouched confirmation
  result;
- a candidate rationale or report section citing it makes that candidate
  inadmissible;
- it is not a prior about, and may not be compared against, a successor
  confirmation population. The successor is generated at layout indices 42/43
  from different source instances (preregistration section 8.1), so no inference
  from this value to it is licensed.

---

## 2. Correction 2 -- own-ranking invariance obligation, resolved prospectively

### 2.1 The ambiguity

Preregistration section 2.6 states the obligation over the component's "own value
vector and own declared ranking" and pins B0's fixture at 36/40. Handoff step 5
states the same check over the component's "own **full ranking**". The two
readings are not equivalent, and a third reading (the argmax *set*) is also
available from the section-2.6 wording.

### 2.2 Measured for B0 on the authorized development split

| Reading | B0 |
| --- | --- |
| own **selection decision** -- the single target the selection rule returns | **36/40** |
| own **full order** over all legal targets | 25/40 |
| **argmax set**, compared as a set | 40/40 |

Only the selection reading reproduces the recorded 36/40 fixture, and it fails at
exactly the recorded locations: `artifact_identifier_variation` and
`combined_permutation` for the two ownership-family sources. The argmax-set
reading is also wrong, in the opposite direction -- under it B0 would score 40/40
and the recorded fixture would be unattainable as a *failure*.

### 2.3 Resolution -- prospective and binding

- **(a)** Mapped component **value-vector** equivalence remains required: 40/40
  within `1e-12` after mapping through the recorded transformation maps.
  Unchanged from preregistration section 2.6 and from the frozen section-14
  check.
- **(b)** The component's own **selection decision** -- the single target its
  selection rule returns -- must be **equivariant** under the five equivalence
  transformations, compared after mapping through
  `canonical_ordinal_by_variant_public_id`.
- **(c)** B0's regression fixture for (b) remains **36/40**, with the four
  failures at `artifact_identifier_variation` and `combined_permutation` for the
  two ownership-family sources.
- **(d)** A revised candidate must achieve **40/40** on (b).
- **(e)** An arbitrary full ordering among tied or equivalent targets is **not**
  required.
- **(f)** Full-order invariance may be computed and reported descriptively
  (B0: 25/40) and is **not** a gate. Every record carrying it must label it
  descriptive-only.

Handoff step 5's "full ranking" wording is superseded by (b) and (f).

### 2.4 How a candidate reaches 40/40 without inventing an unsupported order

Two admissible routes, both consistent with preregistration section 2.5 as
already written:

1. emit a unique argmax that is itself equivariant; or
2. **declare the tie** and let the evaluator's frozen canonical-ordinal
   tie-break resolve it. The canonical ordinal is invariant to public renaming
   and reordering by section-13 construction, so a declared tie resolves
   invariantly. Verified on the development split: declared tie plus evaluator
   tie-break yields selection invariance **40/40**.

What is inadmissible is resolving a top tie **internally** by an
identifier-dependent rule. That is precisely B0's defect:
`max(values, key=lambda item: (values[item], item))` breaks ties by lexicographic
artifact id, which is not equivariant. Preregistration section 2.5 already states
that the component "may not read the ordinal in order to break its own ties" and
may instead "emit an order with explicitly declared ties which the evaluator's
frozen ordinal rule then breaks"; route 2 is that provision, and this corrigendum
only makes it explicit that route 2 satisfies (b).

Reason for the resolution: targets that are indistinguishable under the
authorized representation may legitimately remain tied. Requiring a full order
would require the component to invent an ordering the public state does not
support, which is the opposite of what this study is testing.

### 2.5 What does not change

ND-1, ND-2, and ND-3 are **not** weakened. ND-2 continues to require that the
argmax set of every canonical case lie within a single category-vector
equivalence class; declaring a tie is how a candidate satisfies ND-2 without
inventing an order, not an exemption from it. ND-1 and the B2-derived ND-3 floor
are unchanged, and the floor is still measured and frozen at handoff step 4
before any candidate exists.

---

## 3. Correction 3 -- step-0 confirmation-path hashing procedural deviation

### 3.1 What happened

Handoff step 0 instructs the worker to hash "everything under
`experiments/authzgym_semantic_contract_v1_3/`". The step-0 integrity pass
therefore computed SHA-256 over the 16 confirmation-named files in that
directory, while preregistration sections 3.3 and 12.2 prohibit this study from
opening the spent confirmation population. The instruction and the prohibition
were in direct conflict. The worker followed the written instruction and
disclosed the access in `STUDY_BLOCKER.md` section 5.

### 3.2 Classification

This is recorded as a **procedural deviation**. It is **not** retroactively
authorized, and nothing in this corrigendum should be read as permission for it.

### 3.3 Verified facts

Each verified against the repository at commit `da56301`:

- **No candidate had been created.** No `candidates/` directory and no
  `CANDIDATE_LEDGER.jsonl` exist under
  `experiments/authzgym_estimator_repair_v1_3_1/`.
- **No candidate budget was consumed.** `BASELINES.json` records
  `stage = step1_baseline_reproduction`, contains only the B0 block, and carries
  `frozen_nd3_floor_from_b2 = null`.
- **Confirmation contents were not parsed, scored, counted, or used for a design
  decision.** No confirmation hash, count, case id, or field value appears in any
  study artifact. The harness fails closed on every confirmation-named path and
  on the `confirmation` block of `ORACLE_VALIDATION.json`, and its guard is a
  name predicate that covers all 16 confirmation-named files, not only the ten
  enumerated paths.
- **The population was already spent** for revised-estimator confirmation
  (ADR-0020; preregistration section 0 item 8).
- **No successor untouched confirmation population existed** at the time of the
  access, and none exists now.

### 3.4 Assessment

A file digest computed without parsing carries no case content, no ordering, no
identifiers, no gold, no usefulness, and no per-case oracle output. The v1.3
preregistration section 11 independently classifies "file SHA-256" as
content-blind metadata for its own pre-freeze regime, which corroborates that the
*class* of information obtained is content-blind -- though that regime governed a
different decision and confers no permission here.

On the verified facts of section 3.3, **the deviation does not invalidate the
`est-repair-v1.3.1` development study**. No artifact needs to be discarded,
regenerated, or re-derived, and no budget is forfeited.

That assessment rests on facts, not on permission. It is specific to this access,
this already-spent population, and this pre-candidate point in the study. It does
**not** extend to a successor confirmation population: preregistration section
8.5 makes any read of successor confirmation material before the component freeze
hash is written a blocking violation that spends that population, and section 3.5
below is what prevents the same conflict from recurring.

### 3.5 Prospective amendment to the integrity procedure

Binding on all future steps of this study:

1. The development harness's protected-file integrity pass **must not open, read,
   hash, or otherwise access any confirmation-named path**, and must not hash the
   `confirmation` block of `ORACLE_VALIDATION.json`.
2. The protected set for integrity purposes is every **non-confirmation** file
   under `experiments/authzgym_semantic_contract_v1_3/` together with the other
   paths listed in handoff section 0. Handoff step 0's "everything under" wording
   is superseded by this item.
3. The integrity tool must **fail closed** on a confirmation-named path, exactly
   as the harness already does, rather than hashing it. The guard is the name
   predicate, so it covers files inside `PUBLIC_BUNDLE/`, `RESTRICTED_BUNDLE/`,
   and `annotations/` as well as the directory root.
4. Confirmation-path immutability is verified by the successor confirmation
   protocol's custodian under preregistration section 8, not by this study.

### 3.6 Record retention

The access remains recorded in `STUDY_BLOCKER.md` section 5 and is carried
forward as an explicit deviation record in `ACCESS_LEDGER.jsonl`. It is not
erased, minimized, or reclassified.

---

## 4. Effect on ADR-0020

None of the three corrections alters a gate, a threshold, the attempt budget, the
arm order, the stopping rule, ND-1/ND-2/ND-3, the input allowlist, the firewall
requirements, the confirmation protocol, or the claim boundary:

- correction 1 restores a **non-gating, reported-only** figure to the value of
  the authorized development split;
- correction 2 selects between two readings of an obligation the preregistration
  already stated, choosing the reading that both documents' B0 fixture (36/40)
  already pinned, and confirms the compliance route section 2.5 already provided;
- correction 3 tightens an integrity procedure and forbids an access the
  preregistration already forbade.

**ADR-0020's authorization therefore resumes unchanged.** No re-authorization of
scope, budget, or method is required or given.

---

## 5. Resumption

DeepSeek is authorized to resume at handoff **step 1** under this corrigendum,
reproduce the corrected baseline, and continue in the specified order: step 1,
step 2, step 3 (Tier-1 ceiling, blocking), step 4 (baselines and the frozen
`nd3_floor_from_b2`), step 5, step 6, then arms A/B/C in order under the
unchanged budget and stopping rule.

`STUDY_BLOCKER.md` is retained as the record of the stop. It is superseded as a
blocker by this corrigendum and must not be deleted or rewritten; the resumption
is recorded by appending to `ACCESS_LEDGER.jsonl`.

Not authorized by this corrigendum, restating preregistration section 12.2 and
ADR-0020:

- editing `REPAIR_STUDY_PREREGISTRATION.md`, `IMPLEMENTATION_HANDOFF.md`,
  ADR-0019, ADR-0020, or any historical artifact in place;
- creating any candidate before the Tier-1 ceiling has been computed and recorded
  (handoff step 3 remains a blocking gate that precedes all candidate work);
- any access to the spent `confirmation_v1_3` population, including hashing;
- generating, converting, certifying, freezing, or executing a successor
  confirmation population;
- any model or provider inference;
- any change to AuthzGym v1.3 semantics, populations, or usefulness target;
- any change to the top-1, top-2, regret, or any other threshold;
- Jev, architecture comparison, representation intervention, or model
  escalation.

---

## 6. Provenance

The transcription error in section 1 and the two-reading ambiguity in section 2
originate in the specification text drafted for ADR-0020, not in the
implementation. The conflict in section 3 likewise originates in handoff step 0's
wording contradicting preregistration section 3.3.

The executing worker behaved as specified: it asserted the recorded figure
verbatim rather than substituting a convenient value, refused to reach the
recorded figure by reading the confirmation channel, reported both the blocking
discrepancy and the non-blocking wording discrepancy, disclosed the step-0
access, and stopped without creating a candidate or consuming budget. Stopping
was the correct behaviour under handoff step 1 and blocking-ambiguity item 3.
