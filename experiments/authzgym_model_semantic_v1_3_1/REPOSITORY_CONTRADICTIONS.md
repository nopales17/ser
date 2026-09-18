# Repository authority reconstruction and verified contradictions

Condition: `model-semantic-v1.3.1-N1`.
Status: **accepted** -- the corrections recorded below are adopted by ADR-0023,
2026-09-18, and applied prospectively to the living documents. No sealed
artifact, historical report or earlier ADR was edited, and no model or provider
call was made at any point.

Repository HEAD read: `995cf8b` ("Confirm AuthzGym v1.3 estimator compatibility"),
working tree clean at read time.

This document records what repository authority actually says, what re-derived
from the artifacts, and the contradictions the new decision must fix
prospectively. It edits nothing and seals nothing.

---

## 1. Re-derived hashes (all verified from the checkout)

| Artifact | Recorded | Re-derived | Match |
| --- | --- | --- | --- |
| `src/ser/authzgym/policies.py` | `092a7a87...4167393` | `092a7a87d1227c1a1c85ac46c7122e38ac1b6b24d7aaa90abee05abfe4167393` | yes |
| `src/ser/authzgym/policies_v1_3_1.py` (B-1 module) | `f9c92317...4d910d` | `f9c92317abc562ac5175f90074238c666de55d557b02e0de368841676f4d910d` | yes |
| B-1 component class source | `88b77c5f...ca7a048` | `88b77c5f343117b354b5039d571bf03bf8867fcd7fb4f8fc91c1e1aefca7a048` | yes |
| `DEVELOPMENT_REPORT.md` | `f0629d3b...df18638` | `f0629d3b78ba35258cc6d439e4b731c3682b76fa08e4155efbdad7cd0df18638` | yes |
| `src/ser/authzgym/generation.py` | `03bfe556...163461` | `03bfe556091e8da118c1c27058a8edaa393473c17c4fa45645837b08b7163461` | yes |
| `src/ser/authzgym/v1_3_population.py` | `ac4b8d47...470fca` | `ac4b8d47bd1369a16f4fed0d80abe7e0943c90317c0037bb6c8715882f470fca` | yes |
| `src/ser/evaluation/authz_v1_3.py` | `60b1cb5d...a098f6` (only in `FROZEN_INPUTS_V1_3_1.json`) | `60b1cb5df27346ce65c6400cd33583782e176ca888567c7c052d1037aea098f6` | yes |

Every hash ADR-0022 names re-derives exactly. The frozen estimator, the fixed
adapter, the generator, the converter, and the B-1 component are byte-unchanged.

## 2. Accepted scientific cursor, as the repository states it

- ADR-0019 froze AuthzGym v1.3 as a **new** instrument (f0--f16, four families,
  seven non-summary variants, five public relation categories, no hidden roles,
  no summary condition). V1.2 stays immutable and is qualified only by
  `PRIOR_RESULT_CORRIGENDUM.md`.
- v1.3 development answerability passes (56 cases, 2576 labels, certificate
  `d308e68b...`, checker `be7003ba...`); v1.3 firewall passes (six checks).
- The **unchanged historical estimator** passes the development canonical oracle
  gate (top-1 `0.625`, top-2 `0.875`, regret `0.175`) and **fails** the sealed
  fresh-confirmation canonical top-2 gate (`0.750` against `>= 0.80`).
  `ORACLE_BLOCKER.md` preserves that failure; it is not reinterpreted here.
- ADR-0020/ADR-0021 authorised and corrected `est-repair-v1.3.1`. It stopped at
  its first admissible pass, `est-repair-v1.3.1-B-1` (arm B, estimator-only),
  development canonical top-1 `0.75`, top-2 `1.0`, regret `0.116667`,
  ND-1/ND-2/ND-3 true, strict-unique-max `6` against frozen floor `4`,
  own-selection equivariance `40/40`, section-14 equivalence `40/40`,
  complexity `3` of `4`, zero failing leave-one-source-out folds.
- ADR-0022 authorised exactly one successor confirmation. It executed:
  `confirmation_v1_3_1`, layouts `42/43`, 8 sources, 56 cases, **0 provider
  calls**, answerability pass, firewall pass, one-shot oracle **pass** with
  top-1 `0.875`, top-2 `1.0`, regret `0.058333`, zero illegal targets,
  own-selection `40/40`, section-14 `40/40`, ND-1/ND-2/ND-3 true (reported
  only), sealed at `463d208f...`.
- Actual model production of the v1.3 semantic state remains **untested**.
  Closed-loop routing remains **untested**. This matches the accepted cursor
  supplied to this session.

## 3. Contradiction C-1 -- living state is stale with respect to the sealed confirmation (confirmed)

`experiments/authzgym_confirmation_v1_3_1/` exists, is sealed, and records a
pass. The living documents still instruct that it be executed:

- `state/STATUS.yaml` -> `authzgym_estimator_repair_v1_3_1.successor_confirmation_executed: false`,
  and `study_state: "stopped_at_step_1_corrected_and_resumed_under_ADR-0021"`.
- `state/STATUS.yaml` -> `roadmap.immediate_next_task` still reads "Execute only
  the ADR-0022-authorized section-8 successor confirmation ... generate and
  freeze confirmation_v1_3_1 at layouts 42/43 ...".
- `plan/ROADMAP.md` Phase 5 "current cursor" paragraph for ADR-0022 is written
  as an authorisation to execute, with no recorded outcome.
- `state/CONTEXT_PACKET.md` section 10 reproduces the stale next task.
- `MAP.md` has no row for `experiments/authzgym_confirmation_v1_3_1/`.
- `experiments/README.md` has no entry for the sealed confirmation.

Nothing in the sealed artifacts is wrong; the living projection of them is.
Astra identified this; it is confirmed against the checkout.

**Accepted prospective fix (ADR-0023 item D10, handoff step 14):** **after --
and only after -- ADR-0023 is accepted**, update `state/STATUS.yaml`,
`plan/ROADMAP.md`, `MAP.md` and `experiments/README.md` to record the executed,
sealed, passing successor confirmation and to set the next task, then regenerate
`state/CONTEXT_PACKET.md` with `tools/emit_context.py`. It is recorded as what
it is -- a separately versioned component/instrument compatibility confirmation
-- and never as a pass of AuthzGym v1.3 section 16. No sealed artifact, no ADR
and no historical report is edited.

## 4. Contradiction C-2 -- three different digests circulate as "the population hash" (confirmed, quantified)

Measured on `experiments/authzgym_semantic_contract_v1_3/DEVELOPMENT_PUBLIC_POPULATION.json`:

| Convention | Digest |
| --- | --- |
| raw file bytes, SHA-256 | `dda4e0c08a9c29a58a912fdcb5268ddf602aac79c47f6dd3fb94102b5dc8c365` |
| canonical JSON (`ser.core.types.content_hash`) | `1615b87ed2c05b41861f4765d31fdab0ef3124029496dd2f110a290ae6f2d000` |
| the file's own embedded `population_hash` field | `471c233d9c79ef61fe11bea070049d4fd62c8b03d2e697618b627a05da7dbdcf` |

The digest used throughout the repair study and the successor confirmation as
"the development population hash" -- `dda4e0c0...`, in
`REPAIR_STUDY_PREREGISTRATION.md` section 3.1, section 8.3 check 1, and
`CONFIRMATION_V1_3_1_FREEZE_RECORD.json` -- is the **raw-file-bytes** digest.
But v1.3 `PREREGISTRATION.md` section 12 states that "All JSON is hashed as
UTF-8 canonical JSON with sorted keys", and `content_hash` is the function that
implements that rule and is used for the population's own internal field.
The same collision appears on the confirmation side: `1321bcd1...` is reported
both as "population hash" and as "public population file SHA-256".

ADR-0022 already recorded one downstream symptom as a bookkeeping defect:
`freeze.report_json_sha256` (`444c76c0...`) "does not re-derive from
`DEVELOPMENT_REPORT.json` under canonical re-serialization".

The underlying artifacts are self-consistent; the **vocabulary** is not. Two
hashing conventions and one embedded provenance field share one name.

**Accepted prospective fix (ADR-0023 item D10, `PREREGISTRATION.md` section 5):**
**raw-file SHA-256 is the authoritative frozen-artifact byte hash** for every
new artifact. Where a canonicalized JSON digest is also useful it is recorded
separately and explicitly as `canonical_json_sha256`, never in place of a file
hash and never as an input to a gate. **Multiple digest types are never called
simply `population_hash`.** Inherited digests are restated -- not recomputed,
not edited -- with the convention that produced each one. No historical seal is
rewritten to match.

## 5. Contradiction C-3 -- access ledgers are stage-granular, not file-open-granular (confirmed)

`REPAIR_STUDY_PREREGISTRATION.md` section 8.5 requires
"one record per **open** of any confirmation path: timestamp, actor, path,
operation, tool hash".

`experiments/authzgym_confirmation_v1_3_1/CONFIRMATION_V1_3_1_ACCESS_LEDGER.jsonl`
contains 14 records. They are stage boundaries (`generation_start`,
`generation_complete`, per-written-file `write`, `validation_complete`,
`oracle_evaluation_start`, `sealed`) plus two `read` records, both for
`PUBLIC_CONTRACT.json`. The answerability checker, the firewall validator, the
annotation loader, and the oracle evaluation each opened confirmation
population, schedule, transformation-map and annotation files; none of those
opens is recorded. No record carries a `tool_hash` field.

Nothing here indicates a leak -- the isolation order was followed and the
outcome is recorded. The ledger simply does not have the granularity its own
specification requires, so it could not evidence the absence of a leak.

**Accepted prospective fix (ADR-0023 item D10, `PREREGISTRATION.md` section 6):**
file-open-level access logging is required for this condition. A single audited
reader is used by every stage, one record is emitted per open, and `tool_sha256`,
`process_id`, `file_sha256` and `authorization` are mandatory fields. A static
check rejects any path that bypasses the reader. **Historical ledgers are not
rewritten or backfilled.**

## 6. Contradiction C-4 -- v1.3 section 16 cannot be satisfied as written, and this is the decision the new ADR must make

v1.3 `PREREGISTRATION.md` section 16 requires, before **any** model/provider
call, that the v1.3 directory contain hash-frozen:

- `ORACLE_VALIDATION.json` **with full pass and unchanged estimator hash** --
  the file on disk has `"status": "blocked"` and a `blocking_gate` block, and
  section 14 forbids altering it;
- `CONFIRMATION_ELIGIBILITY.json` selecting reuse or fresh fallback -- the file
  on disk selects `fresh_confirmation_v1_3_layouts_40_41`, and that population
  is declared **spent** by `REPAIR_STUDY_PREREGISTRATION.md` section 0.8;
- `FROZEN_INPUTS.json` with clean/matched hashes -- **absent** from the v1.3
  directory;
- a copied freeze checklist with reviewer/date fields -- **absent**.

`state/STATUS.yaml` agrees: `population_frozen: false`,
`oracle_validation_complete: false`, `inference_authorized: false`,
`authzgym_v1_3_frozen_no_inference: false`.

So the literal section-16 gate is unsatisfiable without either editing frozen
v1.3 artifacts (forbidden by ADR-0019 and ADR-0020) or leaving the instrument
permanently unusable for any model condition.

This is **not** an implementation ambiguity and is not delegated. It is the one
governance decision the new ADR exists to make, and it has now been made.

**Accepted resolution (ADR-0023 items D3 and D4).** The resolution is narrower
than the one first drafted, and does not assert that anything historical passed:

1. **v1.3 section 16 is not claimed to have passed.** It was never satisfied,
   and no artifact, report or statement produced by this condition says or
   implies otherwise.
2. **The historical estimator's failed confirmation is permanently preserved.**
   Canonical top-2 `0.750` against `>= 0.80` stands. It is never rescored,
   re-aggregated, averaged with anything, explained away or superseded, and that
   component is not used in this condition.
3. **ADR-0019 and the v1.3 preregistration remain the semantic authority**,
   unchanged and unreinterpreted.
4. **The applicable downstream-compatibility prerequisite for this condition is
   the separately versioned, sealed B-1 successor confirmation**
   (`experiments/authzgym_confirmation_v1_3_1/`, one-shot oracle `pass`, seal
   `463d208f...`). It is already met, is not re-run, and is not extended to
   cover anything it did not measure.
5. **The condition's freeze artifacts and manifest are new and local**, in
   `experiments/authzgym_model_semantic_v1_3_1/`, referencing every inherited
   input by hash.
6. **Nothing requires retroactively creating a historical v1.3 freeze artifact
   or modifying a historical report**, and doing so is listed among the
   alternatives ADR-0023 rejects.

The effect is that the unsatisfiable section-16 gate is neither waived nor
faked: it remains unsatisfied for the historical instrument-level freeze, while
the prerequisite that actually governs a condition running B-1 is one that was
met prospectively and sealed before any model call existed.

## 7. Non-contradiction checked and cleared -- layout indices 44/45

`REPAIR_STUDY_PREREGISTRATION.md` section 8.2 reserved `44/45` then `46/47` as
**collision fallbacks** for `confirmation_v1_3_1`. `confirmation_v1_3_1` was
generated at `42/43` with no collision, so those reservations are discharged;
section 8.9 forbids generating a second population for B-1, so they cannot be
claimed by B-1 later.

Content-blind provenance, established by directory listing, manifest metadata
and grep over the checkout without opening any generated case content:

- layouts recorded anywhere in the repository: `0/1` (development sources, via
  `authzgym_static_v1_1`), `10--13` and `20+` (v1.1 evaluation/zero),
  `30/31` (v1.1 confirmation), `40/41` (spent `confirmation_v1_3`),
  `42/43` (sealed `confirmation_v1_3_1`);
- `44` and `45` appear **only** as the reserved-fallback literals in
  `REPAIR_STUDY_PREREGISTRATION.md` line 798, `DECISIONS.md` ADR-0022,
  `state/CONTEXT_PACKET.md`, and
  `CONFIRMATION_V1_3_1_FREEZE_RECORD.json.population.reserved_fallback_pairs`;
- no population, manifest, annotation, schedule, transformation map or
  certificate at layout `>= 44` exists.

Astra's prospective population rule -- 44/45 only if content-blind provenance
establishes they were never generated or inspected -- is therefore satisfied on
the evidence available without opening content.

## 8. What was and was not changed when ADR-0023 was accepted

Changed, prospectively and minimally: `state/STATUS.yaml`, `plan/ROADMAP.md`,
`MAP.md`, `experiments/README.md`, the one static Phase-5 sentence in
`tools/emit_context.py`, and the regenerated `state/CONTEXT_PACKET.md`.
`DECISIONS.md` gained ADR-0023 by append only.

Not changed: `CHARTER.md`, `AGENTS.md`, `theory/`, `reference/`, every artifact
under `experiments/authzgym_semantic_contract_v1_3/`,
`experiments/authzgym_estimator_repair_v1_3_1/` and
`experiments/authzgym_confirmation_v1_3_1/`, every earlier experiment directory,
every protected source file, every historical seal, ledger, report, response,
hash and classifier, and every earlier ADR. No preserved result is
reinterpreted, no historical v1.3 freeze artifact is created after the fact, no
historical ledger is backfilled, no historical seal is recomputed under the new
hashing convention, and no model or provider call was made.
