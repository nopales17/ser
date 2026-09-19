# Implementation clarification and deviation record -- `model-semantic-v1.3.1-N1`

Append-only. Authority: ADR-0023, unchanged. Date: 2026-09-18.

This document does two things and nothing else: it removes a **mechanical
step-ordering ambiguity** in `IMPLEMENTATION_HANDOFF.md`, and it records the
prospective acknowledgement of two disclosed deviations. It changes no
experimental semantics, no gate, no threshold, no endpoint, no denominator, no
population, no retry policy, no model condition, and no authorization scope.

---

## 1. Governance determination -- no new ADR is required

The question is whether authorizing "handoff Steps 8--10 implementation and
tests, without model inference or scoring of real model responses, solely to
complete the pre-inference freeze" needs its own appended ADR.

It does not, because **ADR-0023 already authorizes exactly that work**. Its
`Authorized scope` bullet reads, verbatim:

> the zero-inference model-condition verification of preregistration section 9;
> construction of the condition's runner, audited reader, sealed-input wiring,
> **scorer wiring, error-propagation classification and tests**; the
> gold-adequacy computation on the existing development population; and the
> writing of [the named artifacts]. Implementation stops at the freeze boundary.

The scoring, gating and error-propagation machinery that
`PREREGISTRATION.md` sections 12.1 and 18 require before model call 1 is the
"scorer wiring, error-propagation classification and tests" that sentence
already names. Nothing needs to be granted that has not been granted.

What is actually wrong is narrower: the **handoff** placed that machinery in
Steps 8--10, after Step 7, and Step 7 is the development-inference stage. So the
handoff's step order implied that the freeze could only be completed after an
inference stage that the freeze itself gates. That is a defect in a warm
implementation document, not in the decision or the specification.

`MAP.md` assigns an implementation handoff authority over "mechanical step
order, protected files, tests, acceptance criteria, artifacts, and stop
conditions", and explicitly **not** over "research semantics, gate definitions,
or authorization scope". Correcting a step order inside the handoff is therefore
an edit within that document's own authority. `AGENTS.md` requires an appended
ADR for a research boundary or invariant, for changing an accepted architectural
constraint, and for changing the evaluator/controller firewall. None of those
changes here.

**Determination: record the clarification here and fix the order in the
handoff. Do not append an ADR for numbering.** Section 3 states precisely what
remains unauthorized, so the narrowness is auditable rather than asserted.

### 1.1 Why the blockers were correct, not a stop to be waived

`FREEZE_CHECKLIST.md` items 9 and 10 are `not_satisfied` and `freeze_complete`
is `false`. Both are correct and neither is waived by this clarification. The
resolution is to **do** the missing work, under authority that already exists,
before the freeze is finalized -- not to declare the freeze complete without it.

---

## 2. The corrected mechanical order

Authorized and required, in this order:

1. **Steps 1--6** -- zero-inference setup. Complete.
2. **Step 6A** -- the dormant implementation and tests required by
   preregistration sections 12.1 and 18, described in handoff Steps 8--10:
   the scoring, gate, choice-set, error-propagation and reporting machinery,
   the S-7 structural non-gating guarantees, and their unit tests. **Dormant**:
   built and tested against synthetic fixtures only, executed against no model
   response, with no model or provider call.
3. **Step 6B** -- final integrity, static and access checks over the complete
   implementation set.
4. **Step 6C** -- rebuild and finalize `FROZEN_INPUTS_MODEL_V1_3_1.json` and
   `FREEZE_CHECKLIST.md`, including the newly added modules and tests, and set
   `freeze_complete` to `true` only if every item passes.
5. **Step 6D** -- stop.
6. **Step 7** -- development inference, requiring its own separate later
   authorization. Steps 8--10 then **execute** against real responses under that
   authorization; they are only **implemented** at Step 6A.

### 2.1 What "dormant" means, normatively

At Step 6A the Steps 8--10 machinery may be exercised **only** against synthetic
fixtures authored from the published v1.3 grammar and from hand-constructed
response objects. It may not be run against any model response, because none
exists and none is authorized to exist. It may not be run against the
development or confirmation populations to produce any scored result other than
the already-authorized section-8.2 S-3 gold-adequacy computation of Step 5.
Producing a scored number from a real model response at Step 6A is a blocking
violation.

---

## 3. What this clarification does not authorize

Unchanged and still prohibited: model or provider inference of any kind; the 112
development calls; confirmation generation, access or inference; scoring or
analysis of actual model responses; any change to AuthzGym v1.3 semantics,
prompt, schemas, populations or scoring; any change to `est-repair-v1.3.1-B-1`;
any change to a threshold, denominator, endpoint or gate definition; model
substitution or escalation; prompt tuning; retry-policy changes; Jev; and
closed-loop execution or architecture work.

ADR-0023's `Not authorized` bullet and its `Revisit when` clause are untouched.
Development inference still requires a further decision after the freeze
checklist passes with `freeze_complete: true`.

---

## 4. Deviation acknowledgements, prospective

Both were disclosed by the implementation agent and are acknowledged here. Both
keep their recorded characterization. Neither is retroactively authorized, and
neither is erased.

### 4.1 DEV-1 -- handoff named a never-open path as a restatement source

**Recorded difference.** Handoff Step 1 item 3 named
`experiments/authzgym_confirmation_v1_3_1/CONFIRMATION_V1_3_1_FREEZE_RECORD.json`
as the source from which to restate `0e20284b...`, while handoff section 0.2
classifies that path as never-open and preregistration sections 6.3 and 14.2
make any open of a `confirmation_v1_3_1` path a blocking violation. The handoff
contradicted itself.

**Resolution applied by the implementation, and preserved:** fail closed.
Existence was checked with `stat`; the protected file was **not opened**; the
digest was carried from records already authorized as readable; and
`RESTATED_HASHES.json` records `re_derived: false` for that entry.

**Acknowledged as correct.** This is the behaviour the specification intends
when two of its documents disagree: take the restrictive reading, record the
conflict, proceed without the prohibited access. The file is **not** to be
opened retroactively to "complete" the restatement. `0e20284b...` remains a
restated, not re-derived, digest, and any later record that carries it must say
so.

The handoff's Step 1 item 3 wording is corrected prospectively (section 5) so
the instruction no longer names a never-open path.

### 4.2 DEV-2 -- a procedural never-open violation

**Classification: procedural never-open violation, not retroactively
authorized.** Before the condition's `AuditedReader` existed, repository
reconnaissance computed the raw-file SHA-256 of
`experiments/authzgym_confirmation_v1_3_1/CONFIRMATION_PUBLIC_POPULATION.json`,
a section-0.2 never-open path, yielding `1321bcd1...`.

This is recorded as a violation. It is not described as authorized, is not
treated as a satisfied re-derivation, and is not erased.

**Evidentiary scope, stated precisely.** What the records establish:

- the operation was a **raw-byte hash**; no parse, decode, or field access of
  population content is recorded;
- the digest produced, `1321bcd1...`, was **already published** in eight
  readable records of the sealed directory, including `REPORT.md`,
  `CONFIRMATION_V1_3_1_SEAL.json` and
  `CONFIRMATION_V1_3_1_ORACLE_VALIDATION.json`, three of which handoff section
  0.2 explicitly permits reading. The operation therefore produced **no
  information that authorized records did not already carry**;
- the population was **already spent and sealed** under ADR-0022 before this
  condition existed, so it was not available to influence anything in it;
- no design artifact of this condition changed after the operation: the model
  condition, prompt, thresholds, endpoints, estimator, B-1, populations,
  schedule and retry policy are all fixed by ADR-0023 and the preregistration,
  which predate it;
- the condition's audited harness now **refuses** that path, and
  `ACCESS_LEDGER.jsonl` records zero never-open opens for every stage that ran
  under it.

What the records **do not** establish, and what is therefore not claimed: they
do not constitute positive proof that no population content was ever incidentally
observed by the agent performing the reconnaissance. The claim supported is the
narrower one -- that the recorded operation was a byte hash, that its output was
already public within the authorized record set, and that nothing in this
condition's design is downstream of it. Anyone reading a later result should
weigh the deviation on that basis rather than on an assurance the ledger cannot
give.

**Required record-keeping.** One `retrospective_disclosure` record is appended
to `ACCESS_LEDGER.jsonl` describing this operation, marked
`occurred_before_audited_reader: true` with a `disclosed_at` timestamp and no
fabricated original timestamp. The ledger is not otherwise rewritten, and no
historical ledger elsewhere in the repository is backfilled.

### 4.3 Checklist disposition

`FREEZE_CHECKLIST.md` item 13 moves from `recorded_requires_acknowledgement` to
`acknowledged`, citing this section. Items 9 and 10 remain `not_satisfied` until
Step 6C.

---

## 5. Prospective corrections to `IMPLEMENTATION_HANDOFF.md`

Applied in the handoff, which owns mechanical step order:

1. Steps 6A--6D are inserted between Step 6 and Step 7, per section 2.
2. Steps 8--10 are relabelled to state that they are **implemented dormant at
   Step 6A** and **executed only under a separate Step-7 authorization**.
3. Step 1 item 3's restatement instruction no longer names a never-open path; it
   names the authorized readable records and requires `re_derived: false`.
4. The stop point named in Step 12 and in the living cursor becomes Step 6D.

No other handoff content changes. `PREREGISTRATION.md` is not edited: sections
12.1 and 18 already required this machinery, and they were right.

---

## 6. PENDING-3 -- governance-file rebaseline for the final freeze

Appended 2026-09-18. Authority: ADR-0023, unchanged. No experimental semantics,
gate, threshold, endpoint, denominator, model condition, retry rule, B-1
behaviour, population or claim boundary changes.

### 6.1 Governance determination -- no new ADR is required

Four living-governance documents differ from their Step-1 integrity baseline:
`MAP.md`, `plan/ROADMAP.md`, `state/STATUS.yaml`, `state/CONTEXT_PACKET.md`.

Handoff section 0 says any difference in a protected file halts the study. That
rule is a **mechanical acceptance criterion and stop condition**, which `MAP.md`
assigns to the warm implementation handoff and explicitly **not** to
authorization scope. The changes it is halting on are changes **ADR-0023 item
D10 itself mandates**: "reconcile the living `state/STATUS.yaml`,
`plan/ROADMAP.md`, `MAP.md`, `experiments/README.md` and the regenerated
`state/CONTEXT_PACKET.md`", plus the cursor updates the accepted ordering
clarification required.

A change an accepted decision requires cannot simultaneously be forbidden drift.
The defect is that the handoff's blanket rule does not distinguish an
unauthorized mutation of a protected file from an ADR-mandated living-state
reconciliation. Correcting that distinction, for these four files only and by
exact hash, is an edit within the handoff's own authority. `AGENTS.md` requires
an appended ADR for a research boundary or invariant, for changing an accepted
architectural constraint, and for changing the evaluator/controller firewall.
None changes here. **No ADR is appended.**

Two independently verified facts make the acceptance narrow rather than
convenient:

1. **Scope.** Recomputation over the Step-1 baseline finds **4 differing files
   of 233**, none missing. The other 229 match byte-for-byte, including every
   model-facing and experiment-semantic input: the development population, the
   prompt, the schemas, `PUBLIC_CONTRACT.json`, the v1.3 contract code,
   `policies_v1_3_1.py` (B-1), the thresholds, `MODEL_CONDITION.json` and the
   retry machinery.
2. **Class.** None of the four is a section-18 frozen input. The manifest's
   `files{}` set holds **52** entries and contains none of them; they appear in
   `FROZEN_INPUTS_MODEL_V1_3_1.json` only under `dirty_status`,
   `outstanding_items` and `protected_file_recheck` -- that is, as an integrity
   *finding*, never as a frozen scientific input. Accepting their new bytes
   therefore re-baselines a tamper check and changes no frozen input to the
   experiment.

DeepSeek did not silently re-baseline them, and this disposition does not
reward it for having done so: the acceptance is recorded, hash-pinned and
bounded below.

### 6.2 The four accepted transitions, by exact hash

These and only these old->new transitions are accepted for the final
pre-inference freeze:

| path | Step-1 `file_sha256` | accepted current `file_sha256` | authorized governance change | `model_facing` | `accepted_for_final_freeze` |
| --- | --- | --- | --- | --- | --- |
| `MAP.md` | `140c7317f37c572c1fb431def598333bd8188492ee53c9695b996187a84d5723` | `15a3eb2eef3fcbc7c91399f4120cc1cda55dc9af53927acafbb60639bca959a6` | ADR-0023 item D10 authority-index rows for the sealed confirmation and the condition directory; clarification section 5 listing | `false` | `true` |
| `plan/ROADMAP.md` | `d04fcaae5d7cdcf48686cd83b5b2bcf36edd08a39f60149ed2ddc96e83b202da` | `0ccc0c74936abcd01696e9c2b7b0810ae74cedcc1fd3b5ea4d02d43aae2cae93` | ADR-0023 item D10 cursor reconciliation; ordering clarification 6A->6B->6C->6D; DEV-1/DEV-2 record; PENDING-3 record | `false` | `true` |
| `state/STATUS.yaml` | `53adf3444881e53ef3cb9df2f133d13a3436af125c1e88820fcaceecafba892a` | `4f22bf6f824a867eb4905864fdfc4f563f748730332590acf36c236575f83fe0` | ADR-0023 item D10 cursor reconciliation; ordering clarification; DEV-1/DEV-2 acknowledgement; PENDING-3 rebaseline record | `false` | `true` |
| `state/CONTEXT_PACKET.md` | `cedf6170917dcbda550ff0b4e3993b600f9d09baf192536c841a7e7b0cc99bcc` | `f06f8f35f2d1b05153b084fb39ee397520c11478dfcda3b8642e3414e9a0f1fb` | deterministic regeneration by `tools/emit_context.py` from the reconciled canonical sources; never hand-edited | `false` | `true` |

`state/CONTEXT_PACKET.md` is a generated view. Its acceptance is acceptance of
the deterministic render of the accepted sources, not of an independent edit.

### 6.3 The seven statements, normative

`GOVERNANCE_REBASELINE.json` must carry each of these as an explicit field, and
each is true of this disposition:

1. the original Step-1 integrity baseline remains preserved, unaltered, as
   historical evidence -- `INTEGRITY_BASELINE.json` is **not** edited,
   regenerated or overwritten;
2. only these four exact old->new hash transitions are accepted;
3. this waives integrity checking for **no** other protected file; the remaining
   229 baseline entries are verified unchanged exactly as before;
4. any subsequent change to these four files after this rebaseline is **new
   drift** and must halt the study again;
5. **no model-facing input is re-baselined** -- no population, prompt, schema,
   contract, estimator, B-1 source, threshold, model condition or retry rule;
6. this is **not** retroactive authorization of DEV-2, which remains a recorded
   procedural never-open violation under section 4.2 with its evidentiary scope
   stated there and not broadened here;
7. no experiment semantic, gate, threshold, model condition, retry rule, B-1
   behaviour, population or claim boundary changes.

### 6.4 What is authorized next, exhaustively

Only these five things, in this order:

1. create `GOVERNANCE_REBASELINE.json` per sections 6.2 and 6.3;
2. re-run the Step-6B integrity, static and access checks against the original
   Step-1 baseline **plus** the explicit four-file rebaseline, asserting each
   current hash equals the value recorded in section 6.2;
3. rebuild the Step-6C freeze manifest and checklist, hashing
   `GOVERNANCE_REBASELINE.json` into the manifest;
4. set `freeze_complete: true` **only if** every other requirement still passes;
5. stop at Step 6D.

Still prohibited, unchanged: model or provider inference of any kind; Step 7 and
the 112 development calls; scoring or analysis of actual model responses;
confirmation generation or access; restoring the Step-1 versions of the four
files; editing `INTEGRITY_BASELINE.json`; re-baselining anything else; and every
item in section 3.

If any protected file other than those four differs, or any of the four differs
from its section-6.2 accepted hash, the run **halts and records a blocker**. It
does not re-baseline again.
