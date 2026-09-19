# Implementation handoff -- `model-semantic-v1.3.1-N1`

Audience: the implementation agent (DeepSeek).

Governing documents, in precedence order: `DECISIONS.md` (once ADR-0023 is
appended) -> `experiments/authzgym_model_semantic_v1_3_1/PREREGISTRATION.md` ->
this handoff. Where this handoff and the preregistration differ, the
preregistration governs and the difference is a blocker to record, not a
discretion to exercise.

**You have no research-semantic choices.** Every threshold, denominator,
population rule, retry rule and interpretation is fixed in the preregistration.
If a step would require you to choose one, stop at step 12 rather than choosing.

**Do not start** until ADR-0023 is appended to `DECISIONS.md`. Every
research-semantic decision is resolved; nothing else is pending.

**Currently authorized range: Steps 1 through 6D, stopping at Step 6D.** The
pre-inference freeze is a sequence -- Step 6 writes provisional artifacts, Step
6A implements the Steps 8--10 machinery *dormant* (synthetic fixtures only, no
model response), Step 6B re-runs the integrity, static and access checks, Step
6C finalizes the manifest and checklist, Step 6D stops. Steps 7 and beyond
require a separate later authorization. See
`IMPLEMENTATION_CLARIFICATION.md` sections 1--3 for why Step 6A is already
within ADR-0023's authorized scope and for the exhaustive list of what remains
unauthorized.

Every threshold is fixed. S-13, S-14 and S-15 now carry the numbers the
accepted research design supplies:

- **S-13 paired degradation:** top-1 decline `<= 0.125`, top-2 decline
  `<= 0.125`, mean positive excess regret `<= 0.05`;
- **S-14 model-conditioned own-selection equivariance:** `80/80` repeat-matched
  development comparisons, `40/40` confirmation comparisons;
- **S-15 directional-effect continuity:** precision `>= 0.60`, recall `>= 0.50`.

These are prospective engineering advancement screens over eight source
instances. Never report one as a population estimate, a success rate, or a
quantity with a confidence interval.

**The one field you must never gate on:** effect self-consistency (S-7), whose
adjudicated disposition is `diagnostic_only`. You compute it exactly, you report
`C_response` and `C_field`, you enumerate every violation, and you keep invalid
and missing responses separate without ever imputing them consistent. You do
**not** pick a threshold for it, do **not** let it gate, veto, block a later
layer, exclude a response, trigger a retry or a repair, or change what B-1
receives. B-1 gets the model's **actual submitted effect values**, inconsistent
or not. Steps 8, 9 and 10 make this structural rather than a matter of care.

---

## 0. Protected files -- byte-unchanged, verified at the start and end of every step

Compute `file_sha256` for each at step start and step end. Any difference halts
the study.

**One narrow exception, and only the one.** Four living-governance documents --
`MAP.md`, `plan/ROADMAP.md`, `state/STATUS.yaml`, `state/CONTEXT_PACKET.md` --
were changed after the Step-1 baseline by the governance reconciliation that
ADR-0023 item D10 itself mandates and by the accepted ordering clarification.
`IMPLEMENTATION_CLARIFICATION.md` section 6 accepts those four exact old->new
transitions, by hash, for the final freeze. They are **not** section-18 frozen
inputs -- the manifest's `files{}` set contains none of them -- and they are not
model-facing. Every other protected file, and any later change to these four,
remains a halting difference.

- Everything under `experiments/authzgym_semantic_contract_v1_3/` **except** the
  four `CONFIRMATION_*` names listed in section 0.2 as never-open. Directory
  traversal and `stat` only for those; they are neither opened nor hashed.
- Everything under `experiments/authzgym_estimator_repair_v1_3_1/`.
- Everything under `experiments/authzgym_confirmation_v1_3_1/`.
- `src/ser/authzgym/policies.py` == `092a7a87d1227c1a1c85ac46c7122e38ac1b6b24d7aaa90abee05abfe4167393`
- `src/ser/authzgym/policies_v1_3_1.py` == `f9c92317abc562ac5175f90074238c666de55d557b02e0de368841676f4d910d`
- `src/ser/evaluation/authz_v1_3.py` == `60b1cb5df27346ce65c6400cd33583782e176ca888567c7c052d1037aea098f6`
- `src/ser/authzgym/generation.py` == `03bfe556091e8da118c1c27058a8edaa393473c17c4fa45645837b08b7163461`
- `src/ser/authzgym/v1_3_population.py` == `ac4b8d47bd1369a16f4fed0d80abe7e0943c90317c0037bb6c8715882f470fca`
- `src/ser/authzgym/v1_3_contract.py`, `v1_3_public_input.py`,
  `v1_3_annotation_builder.py`, `model.py`
- `src/ser/evaluation/authz_v1_3_1_sealed_input.py`,
  `authz_v1_3_1_harness.py`
- `tools/validate_authzgym_v1_3_answerability.py`,
  `validate_authzgym_v1_3_firewall.py`, `validate_authzgym_v1_3_oracle.py`,
  `validate_authzgym_v1_3_1_component_firewall.py`,
  `prepare_authzgym_v1_3.py`, `run_authzgym_confirmation_v1_3_1.py`,
  `run_estimator_repair_study.py`
- `DECISIONS.md`, `CHARTER.md`, `MAP.md`, `AGENTS.md`, `README.md`,
  `plan/ROADMAP.md`, `state/STATUS.yaml`, `state/CONTEXT_PACKET.md`, everything
  under `theory/` and `reference/`, and every prior experiment directory.

### 0.1 Reference: hashes that must re-derive before step 1

`88b77c5f343117b354b5039d571bf03bf8867fcd7fb4f8fc91c1e1aefca7a048` (B-1 class
source text), `f0629d3b78ba35258cc6d439e4b731c3682b76fa08e4155efbdad7cd0df18638`
(`DEVELOPMENT_REPORT.md`),
`dda4e0c08a9c29a58a912fdcb5268ddf602aac79c47f6dd3fb94102b5dc8c365`
(`DEVELOPMENT_PUBLIC_POPULATION.json`),
`1321bcd190c2bfbef884aac55421669401fe321797345ad54556d0f55251787c`
(`confirmation_v1_3_1` public population),
`463d208f0e02fc17fc66dd52a211e365fc464cafcb8344c4d91955d4fb0986b8`
(`CONFIRMATION_V1_3_1_SEAL.json`).

### 0.2 Never open -- fail closed

- `experiments/authzgym_semantic_contract_v1_3/CONFIRMATION_PUBLIC_POPULATION.json`
- `experiments/authzgym_semantic_contract_v1_3/CONFIRMATION_RESTRICTED_POPULATION.json`
- `experiments/authzgym_semantic_contract_v1_3/CONFIRMATION_SCHEDULE.json`
- `experiments/authzgym_semantic_contract_v1_3/CONFIRMATION_TRANSFORMATION_MAPS.json`
- `experiments/authzgym_semantic_contract_v1_3/CONFIRMATION_*` (every remaining
  `CONFIRMATION_`-prefixed file in that directory, plus
  `annotations/confirmation_annotations.jsonl` and the `PUBLIC_BUNDLE/` and
  `RESTRICTED_BUNDLE/` copies), and the `confirmation` block of
  `ORACLE_VALIDATION.json`
- every file under `experiments/authzgym_confirmation_v1_3_1/` **except**
  `CONFIRMATION_V1_3_1_ORACLE_VALIDATION.json`, `CONFIRMATION_V1_3_1_SEAL.json`
  and `REPORT.md`, which are read once at step 1 for hash restatement only

The guard is a path predicate, is applied inside `AuditedReader`, raises on
violation, and is unit-tested with a negative test before any other step runs.

## 0.3 New files -- the complete set this condition may create

Nothing outside this list may be created or modified.

```
src/ser/evaluation/authz_model_semantic_v1_3_1.py        # audited reader, scoring wiring, classes
src/ser/authzgym/semantic_contract_v1_3.py               # v1.3 request body + response extraction
src/ser/authzgym/supervised_transport_v1_3.py            # supervised v1.3 client
tools/verify_authzgym_model_condition.py                 # step 2, zero inference
tools/run_authzgym_model_semantic_development.py         # steps 5-7
tools/score_authzgym_model_semantic.py                   # steps 8-10
tools/run_authzgym_model_semantic_confirmation.py        # step 13, gated
tests/test_model_semantic_v1_3_1_reader.py
tests/test_model_semantic_v1_3_1_client.py
tests/test_model_semantic_v1_3_1_choice_sets.py
tests/test_model_semantic_v1_3_1_retry.py
tests/test_model_semantic_v1_3_1_error_classes.py
tests/test_model_semantic_v1_3_1_gates.py
experiments/authzgym_model_semantic_v1_3_1/*             # artifacts named below
```

No `ADR` is appended, no canonical state document is edited, and no generated
view is regenerated by any step in this plan except step 14, which is separately
gated.

---

## Step 1 -- Integrity baseline and hash restatement

Create `tools/verify_authzgym_model_condition.py --stage integrity`.

1. Hash every section-0 protected file with `file_sha256`. Compare against
   section 0.1 where a value is given.
2. Traverse `experiments/authzgym_semantic_contract_v1_3/` with `stat` only;
   assert every section-0.2 name is present and that **no** read occurred for
   it. Assert `git status --porcelain` is empty apart from this condition's own
   directory.
3. Write `RESTATED_HASHES.json` exactly as `PREREGISTRATION.md` section 5.3
   specifies: recorded digest, recorded-as name, actual convention,
   re-derivation status. Raw-file SHA-256 is authoritative for every new
   artifact; a canonicalized JSON digest, where useful, goes in its own
   `*_canonical_json_sha256` field and never in place of a file hash; and no
   field carrying more than one digest type is ever named `population_hash`.
   Restate `0e20284b...` **only from records this handoff authorizes you to
   read** -- `CONFIRMATION_V1_3_1_ORACLE_VALIDATION.json`,
   `CONFIRMATION_V1_3_1_SEAL.json` or `REPORT.md` -- and **never** by opening
   `CONFIRMATION_V1_3_1_FREEZE_RECORD.json`, the spent `confirmation_v1_3`
   population, or any other section-0.2 path. Check existence with `stat` only.
   Mark the entry `re_derived: false, reason: "restated from authorized readable
   records; spent population never opened"`.
   (Corrected under `IMPLEMENTATION_CLARIFICATION.md` section 4.1, DEV-1: the
   earlier wording named a never-open path as the source.)
4. Write `INTEGRITY_BASELINE.json` with every hash and the repository commit.

**Acceptance:** every given hash re-derives; zero section-0.2 opens; the
canonical-versus-file convention for each restated digest is explicit.
**Stop if:** any protected hash differs, or the tree is dirty outside this
directory.

## Step 2 -- Zero-inference model-condition verification

Implement `PREREGISTRATION.md` section 9 steps 1--16 in
`tools/verify_authzgym_model_condition.py --stage model`.

- The only network operations permitted in this step are the supervised-hop
  establishment and `GET /models`. A chat/completions request in this step is a
  blocking violation.
- Assert `paid_inference: false` is recorded for the probe.
- Write `MODEL_CATALOG_SNAPSHOT.json`, `MODEL_CONDITION_VERIFICATION.json`,
  then `MODEL_CONDITION.json`, then `COST_GATE.json`, in that order, hashing
  each before writing the next.
- `COST_GATE.json` uses the section-9.5 formula with `max_submissions = 336`,
  the uncached input rate for every submission, and the **verified** tariff.

**Acceptance:** the route resolves; `patchersniper_praneeth/gpt-5.4-nano` is
present exactly once; every configuration field is within documented support;
`immutable_revision` is recorded or explicitly `unavailable_without_inference`
with the catalog snapshot hash; `proceed` is true.
**Stop if:** probe failure, identifier absent or duplicated, an undocumented
required capability, or `proceed` false. **Do not reduce the schedule and do not
change model.**

## Step 3 -- Audited reader and access ledger

In `src/ser/evaluation/authz_model_semantic_v1_3_1.py`:

- `AuditedReader` with `read_bytes`, `read_text`, `read_json`, `read_jsonl`,
  each emitting one `PREREGISTRATION.md` section-6.2 record per open.
- The section-0.2 path predicate, raising `SpentPopulationAccess`.
- A static check over this condition's own modules and tools rejecting bare
  `open(`, `Path.read_text`, `Path.read_bytes`, `json.load(` on a path, and any
  loader that bypasses `AuditedReader` for a protected or confirmation path.

`tests/test_model_semantic_v1_3_1_reader.py`: one record per open; every
required field present; `tool_sha256` equals the caller tool's own
`file_sha256`; a `confirmation_v1_3` path raises; a `confirmation_v1_3_1` path
raises; the static check fails on a deliberately bypassing fixture.

**Acceptance:** all tests pass; zero bypasses.

## Step 4 -- v1.3 client and the retry state machine

`src/ser/authzgym/semantic_contract_v1_3.py`:

- build the request body from `ser.authzgym.v1_3_public_input.build_normal_request`
  output plus the frozen `MODEL_CONDITION.json` fields; the per-case
  `response_schema` is taken from the population, unmodified;
- assert the request bytes hash is identical across every attempt of a logical
  call before each submission;
- extract the response content and record `finish_reason`,
  `system_fingerprint`, usage, and the raw bytes hash.

`src/ser/authzgym/supervised_transport_v1_3.py`: mirror
`ser.authzgym.supervised_transport` for v1.3, with client-side retries set to
zero and asserted, and with the section-11.2 bound of one transport replay plus
one structural retry per logical call.

`tests/test_model_semantic_v1_3_1_client.py` and
`tests/test_model_semantic_v1_3_1_retry.py`, all against recorded fixtures with
**no network**:

1. valid first attempt -> one submission, measured = attempt 1;
2. transport failure then valid -> two submissions, measured = attempt 2;
3. structurally invalid then valid -> two submissions, measured = attempt 2;
4. **structurally valid but semantically wrong -> exactly one submission**; no
   retry is issued under any circumstance;
5. invalid then invalid -> two submissions, no third, case recorded
   `malformed_or_missing`;
6. request bytes identical across all attempts, asserted by hash;
7. hidden client retries are zero, asserted;
8. every attempt is preserved with its full record, including discarded later
   attempts.

**Acceptance:** all eight hold. Test 4 is the one that encodes the frozen rule
"valid-but-semantically-wrong responses are never retried"; if it does not hold,
stop.

## Step 5 -- Gold-adequacy on the development population (blocking, before any call)

`tools/score_authzgym_model_semantic.py --stage gold-adequacy --split development`.

Using `ser.evaluation.authz_v1_3_1_harness` unchanged, and gold responses from
`ser.evaluation.authz_v1_3.oracle_response_from_annotation` over
`annotations/development_annotations.jsonl`:

- run B-1 on gold over the 8 canonical `base_entry` cases; require top-1
  `>= 0.60`, top-2 `>= 0.80`, regret `<= 0.35`, zero illegal, section-14
  equivalence `40/40`, own-selection `40/40`;
- compute `G_i` for each canonical source per `PREREGISTRATION.md` section 4.2
  and **require `G_i != L_i` for all 8**;
- write `GOLD_ADEQUACY_DEVELOPMENT.json` with `G_i`, `|G_i|`, `|L_i|`, and the
  per-source verdict.

**Acceptance:** all pass. Expected reproduction, from `DEVELOPMENT_REPORT.md`:
top-1 `0.75`, top-2 `1.0`, regret `0.116667`, ND-1 true. A mismatch against
those recorded figures is a harness defect, not a finding -- fix the harness
wiring, do not adjust anything frozen.
**Stop if:** any canonical `G_i == L_i`; that is an instrument-validity blocker
(`PREREGISTRATION.md` section 13.7).

## Step 6 -- Provisional freeze artifacts

Write `FROZEN_INPUTS_MODEL_V1_3_1.json` (`PREREGISTRATION.md` section 18) and
`FREEZE_CHECKLIST.md` with every item recorded and reviewer/date fields. Use the
section-5 convention throughout. Include the repository commit and dirty status.
Recompute the manifest hash with its own field omitted, then store it.

The freeze is a **sequence**, not a single step: sections 12.1 and 18 require
the scoring, gate and error-propagation machinery and its tests to exist before
model call 1, so `freeze_complete` stays `false` here and is finalized at Step
6C. Record any section-12.1 or section-18 item you cannot yet satisfy as
`not_satisfied` with its authority and reason, and continue to Step 6A.

**Acceptance:** every artifact that exists is present and matched; every
outstanding item is recorded with its authority. `freeze_complete: false`.
**No model call may be made at this step or at any of 6A--6D.**

## Step 6A -- Dormant implementation and tests required by sections 12.1 and 18

Authorized by ADR-0023's `Authorized scope` bullet ("scorer wiring,
error-propagation classification and tests") and ordered here by
`IMPLEMENTATION_CLARIFICATION.md` section 2. This step builds the Steps 8--10
machinery; it does **not** execute it against any model response.

Implement and unit-test, exactly as Steps 8, 9 and 10 specify them:

- the scoring wiring of Step 8, including choice-set computation, the per-repeat
  primary endpoint, S-7 as `diagnostic_only`, and gates S-13, S-14 and S-15;
- the error-propagation classification and the `D0`--`D4` evaluator-only
  substitutions of Step 9;
- the gate and eligibility machinery of Step 10, including the three
  `PREREGISTRATION.md` section-12.1 structural guarantees:
  `GATED_DEVELOPMENT_ITEMS` as a frozen literal set excluding `11`, the
  `DiagnosticOnly` wrapper whose `verdict` access raises `DiagnosticOnlyMisuse`,
  and the total-S-7-failure test that must still yield `pass` and
  `development_eligible`;
- every test file named in section 0.3:
  `tests/test_model_semantic_v1_3_1_choice_sets.py`,
  `tests/test_model_semantic_v1_3_1_error_classes.py`,
  `tests/test_model_semantic_v1_3_1_gates.py`.

**Dormant means dormant.** Exercise this machinery only against synthetic
fixtures authored from the published v1.3 grammar and hand-constructed response
objects. Do not run it against any model response -- none exists and none is
authorized to exist. Do not produce any scored number from a real response. The
only real-data computation authorized at this point remains the Step-5
gold-adequacy check, already complete.

**Acceptance:** all named modules and tests exist; the full test suite passes;
the three section-12.1 guarantees are demonstrated by passing tests, including
the total-failure test.
**Stop if:** a test would require a threshold, denominator or interpretation the
preregistration does not fix, or a fixture would have to be derived from a real
response.

## Step 6B -- Final integrity, static and access checks

Over the **complete** implementation set now on disk:

1. re-run the Step-1 integrity pass; every protected hash must still match and
   `git status` must still be clean outside this condition's directory;
2. re-run the Step-3 static check: no module or tool of this condition bypasses
   `AuditedReader` for a protected or confirmation path;
3. validate `ACCESS_LEDGER.jsonl` in full -- schema-complete, `tool_sha256`,
   `process_id`, `file_sha256` and `authorization` present on every record, and
   **zero** never-open opens for every stage that ran under the reader;
4. append the single `retrospective_disclosure` record for DEV-2 required by
   `IMPLEMENTATION_CLARIFICATION.md` section 4.2, with
   `occurred_before_audited_reader: true` and a `disclosed_at` timestamp. Do not
   fabricate an original timestamp and do not rewrite any existing record.

5. write `GOVERNANCE_REBASELINE.json` per `IMPLEMENTATION_CLARIFICATION.md`
   section 6, then re-run item 1 against **the original Step-1 baseline plus
   exactly these four accepted transitions**. For each of the four files record:
   `path`; `step1_file_sha256`; `current_file_sha256`; the authorized governance
   change responsible; `model_facing: false`; `accepted_for_final_freeze: true`.
   The record must also carry, as explicit fields, the seven statements of
   clarification section 6.3. Assert that each `current_file_sha256` equals the
   value section 6.2 records; a mismatch is **new drift** and halts.

**Acceptance:** all five pass, with the four-file drift resolved only through
the explicit rebaseline and every other baseline entry matching unchanged.
**Stop if:** any protected hash other than those four differs, any of the four
differs from its section-6.2 accepted value, any bypass is found, or any
never-open open is recorded for an audited stage. Do **not** restore the Step-1
versions of the four files, and do **not** edit `INTEGRITY_BASELINE.json`.

## Step 6C -- Finalize the frozen manifest and checklist

Rebuild `FROZEN_INPUTS_MODEL_V1_3_1.json` to include every module and test added
at Step 6A, then rebuild `FREEZE_CHECKLIST.md`:

- items 9 and 10 move to `pass` only when the section-12.1 guarantees and the
  complete section-18 implementation are present, tested and hashed;
- the protected-file item moves to `pass` only when the sole outstanding
  differences are the four accepted governance transitions, each matching
  `GOVERNANCE_REBASELINE.json`, and `GOVERNANCE_REBASELINE.json` itself is
  present and hashed into the manifest;
- item 13 moves to `acknowledged`, citing
  `IMPLEMENTATION_CLARIFICATION.md` section 4;
- `freeze_complete` becomes `true` **only if every item passes**. If any item is
  still outstanding, leave it `false`, record the item, and stop.

**Acceptance:** manifest matches the tree; checklist complete; reviewer and date
fields present; `freeze_complete: true`.

## Step 6D -- Stop

Stop here. Report: files created, hashes, checklist status, `freeze_complete`,
`git status`, and every blocker and deviation. Make **no** model or provider
call. Then wait for the separate Step-7 development-inference authorization.

## Step 7 -- Development inference, 112 logical calls (requires separate authorization)

`tools/run_authzgym_model_semantic_development.py`.

- Schedule order exactly as `DEVELOPMENT_SCHEDULE.json` gives it: source-manifest
  order, then the seven variants, then repeat 1 then repeat 2.
- Verify the frozen manifest before call 1 and after the final call.
- After **every** submission: append the attempt record; recompute accumulated
  cost from provider-reported usage at the verified tariff; append to the spend
  ledger; refuse any submission that would carry the total past `$2.50`.
- Compare `system_fingerprint` against `observed_fingerprint_first`; a change is
  a blocking integrity violation -- stop, keep everything.
- No futility stop. All 112 calls complete unless a section-11.5 stop fires.

Artifacts: `development/attempts.jsonl`, `development/responses.jsonl`,
`development/spend_ledger.jsonl`, `DEVELOPMENT_ACCESS_LEDGER.jsonl`,
`development/transport_events.jsonl`.

**Stop if:** integrity, access, identity drift, spend, or transport exhaustion.
None of these is permission to tune, escalate, reduce the schedule, or retry
semantics.

## Step 8 -- Scoring (implemented dormant at Step 6A; executed only under a separate Step-7 authorization)

Implement and test this step's content at **Step 6A**, against synthetic fixtures only. Execute it against real model responses only after Step 7 is separately authorized.

`tools/score_authzgym_model_semantic.py --stage score --split development`.

- Structural validity and the measured-response selection: the **first**
  structurally valid response in attempt order.
- Semantic layers: `ser.evaluation.authz_v1_3.score_cases`, unchanged, over all
  56 cases with the frozen two-repeat averaging and the frozen `NA` rules.
- Downstream: `build_sealed_input(case, measured_response, contract)` -> B-1 ->
  `diagnostic_for_case`, unchanged, for the absolute top-1/top-2/regret of gate
  S-11.
- Choice sets: `M_i` and `G_i` per `PREREGISTRATION.md` section 4.2, rounded to
  12 decimal places, computed **without** the canonical ordinal.
- `preserved(i)` per section 4.3, computed **separately for repeat 1 and repeat
  2**; a missing measured response makes it false.
- **S-7**, per `PREREGISTRATION.md` section 8.6, `diagnostic_only`: for every
  structurally valid measured response `r` and candidate slot `c`,
  `I_rc = 1[E_rc = T_c(F_r)]`, where `T_c` is
  `ser.authzgym.v1_3_contract.effect_from_facts` applied to the public contract,
  the case's public `candidate_hypotheses` and the response's **own submitted
  facts**, keyed by the candidate's public family. Report
  `C_response = (sum_r prod_c I_rc) / N` and `C_field = (sum_r sum_c I_rc) / (4N)`,
  with `N` the count of structurally valid measured responses in scope. Report
  development and confirmation separately and **each development repeat
  separately**, with the case, source, variant and family breakdowns. Invalid and
  missing responses are excluded from `N`, reported with their own counts, and
  **never counted as consistent and never as inconsistent**. Enumerate every
  violation. Do not gate on any of it.
- **S-13**, per `PREREGISTRATION.md` section 8.3: `top1_decline`,
  `top2_decline`, and `mean_positive_excess` regret with each source's excess
  clamped at zero before averaging; denominator fixed at 8; a
  `malformed_or_missing` source contributes `top1_model = top2_model = 0` and
  `regret_model = 1.0` and is never dropped; evaluated separately on each repeat.
- **S-14**, per section 8.3: the component's own selection decision under model
  semantics, mapped through `canonical_ordinal_by_variant_public_id`, compared
  **repeat-matched** -- variant `v` of source `s` at repeat `r` against
  `base_entry(s, r)`. Denominator fixed at 80 for development. A comparison whose
  variant response or whose repeat-matched base response is missing **fails**;
  it is never excluded. Report the value-vector and response-semantic
  equivalence rates alongside, non-gating.
- **S-15**, per section 8.3: directional item sets keyed by `effect_family`,
  micro-aggregated over both continuity axes -- cross-variant repeat-matched and
  cross-repeat -- into one precision and one recall; frozen `NA` rules apply; a
  missing response contributes `P = {}`. Report the two axes separately,
  non-gating.
- Report separately, never gating: exact argmax-set equality,
  evaluator-canonical selected-target agreement, top-two-set agreement, tie
  dependence, repeat agreement, the B1 null, and the `longest_artifact`
  read-out.

`tests/test_model_semantic_v1_3_1_gates.py` additionally asserts, on synthetic
fixtures with no network: `mean_positive_excess` ignores a source where the
model beats gold; an S-14 comparison against a **different** repeat is rejected
rather than substituted; an S-14 comparison with a missing response scores as a
failure and the denominator stays 80; an S-15 axis with an empty comparison set
yields `NA` and cannot clear a threshold; and every one of these three gates is
absent from any code path that could touch a `D1`--`D3` substituted row.

`tests/test_model_semantic_v1_3_1_choice_sets.py`: `M subset of G` with `M`
strict passes; `M == G` passes; `M` containing one target outside `G` fails;
`M == L` with `G` proper fails and classifies `structurally_catastrophic`;
missing response fails; the canonical ordinal is provably not read on the
choice-set path (permute it, assert byte-identical `M_i` and `G_i`).

## Step 9 -- Error propagation (implemented dormant at Step 6A; executed only under a separate Step-7 authorization)

Implement and test this step's content at **Step 6A**, against synthetic fixtures only. Execute it against real model responses only after Step 7 is separately authorized.

Implement `PREREGISTRATION.md` section 10 in
`src/ser/evaluation/authz_model_semantic_v1_3_1.py`:

- section 10.1 localization tables;
- the five classes of section 10.2, applied in precedence order, exactly one per
  case;
- the `D0`--`D4` evaluator-only substitutions of section 10.3, written to
  `ERROR_PROPAGATION.json` under a top-level key
  `evaluator_only_diagnostic_substitution`.

`tests/test_model_semantic_v1_3_1_error_classes.py`: the five classes are
mutually exclusive and exhaustive over a synthetic fixture grid; precedence
order is respected; and a substitution provably does not mutate the measured
response -- assert the response bytes hash before and after the whole
substitution pass.

The `D0`/`D3` pair is the **S-7 localization**: the gap between them is exactly
the decision-level contribution of the response's effect self-consistency
violations (`PREREGISTRATION.md` section 8.6, consequence 10). It is a
localization, never a repair -- `D3` does not become the measured result, does
not replace what B-1 received, and does not enter a gate.

**Hard rule:** no substituted result may satisfy any gate. The gate evaluator
must not be able to see substituted values; enforce this by passing only `D0`
rows into the gate function and unit-test that a substituted row raises if
passed. Add a test asserting that the effect vector B-1 receives is byte-equal
to the model's submitted effect vector for every case, including every case with
an S-7 violation.

## Step 10 -- Gates and eligibility (implemented dormant at Step 6A; executed only under a separate Step-7 authorization)

Implement and test this step's content at **Step 6A**, against synthetic fixtures only. Execute it against real model responses only after Step 7 is separately authorized.

`tests/test_model_semantic_v1_3_1_gates.py` plus
`tools/score_authzgym_model_semantic.py --stage gates`.

Evaluate the `PREREGISTRATION.md` section-12 checklist items 1--23 in order,
writing `ELIGIBILITY.json` with each item's observed value and verdict.
Thresholds come from section 8.2 for S-1--S-6 and S-8--S-12 and from section 8.3
for S-13--S-15.

**Item 11 (effect self-consistency, S-7) is recorded as `diagnostic_only`** with
its measured values and every violating response enumerated by case id, split,
repeat, attempt ordinal, candidate slot, public family, submitted fact vector,
submitted effect value and `T_c(F_r)`. It is not a pass, not a fail, and not an
input to any other item.

Implement the three structural guarantees of `PREREGISTRATION.md` section 12.1
and test them:

1. `GATED_DEVELOPMENT_ITEMS` is a frozen literal set of `1..10` and `12..21`,
   asserted not to contain `11`; the confirmation gated set is built the same
   way from section 13.8 and likewise excludes S-7.
2. The S-7 record reaches the eligibility function wrapped in `DiagnosticOnly`,
   whose `verdict` attribute raises `DiagnosticOnlyMisuse` on access; a test
   builds an eligibility computation that reads it and asserts the raise.
3. A test drives S-7 to total failure -- `C_response = 0.0`, every response
   enumerated violating -- holds every other item at pass, and asserts the
   verdict is still `pass`, the label is still `development_eligible`, and the
   violations appear in the report.

Apply the section-15 table, first matching row wins. S-7 is excluded from row 5
and can never trigger it. Whichever row matches, render the label with the
suffix `(S-7 violations: <count>)` when the count is non-zero, and carry
`effect_self_consistency` with `C_response`, `C_field`, the per-split and
per-repeat breakdowns and the full enumeration into the outcome record. Validity precedence (section 8 preamble) is enforced: a
later-layer number is computed and reported but is marked
`blocked_by: <earlier layer>` when an earlier layer failed.

Apply the section-15 interpretation table, first matching row wins, and record
the outcome label.

## Step 11 -- Development report

`DEVELOPMENT_REPORT.md` and `DEVELOPMENT_REPORT.json`, containing: the frozen
inheritance; the model condition and its verification; the schedule and
accounting; every gate with observed value, threshold and verdict; the primary
endpoint per repeat with the per-source `G_i`/`M_i`/class table; repeat
agreement; the separately reported non-primary metrics; the B1 null; the
`longest_artifact` diagnostic; the error-propagation classification and the
clearly separated substitution section; the outcome label; and the section-16
claim boundary quoted verbatim.

Hash both under the section-5 convention. `DEVELOPMENT_REPORT.json` must
re-derive under `file_sha256` -- verify it, since a failure of exactly this kind
is a recorded defect of the preceding study.

## Step 12 -- Stop after development scoring

Reached only under a separate Step-7 authorization. The **pre-inference** stop
point for the currently authorized work is Step 6D, not this step.

Stop here. Do **not** generate, list for content, open or call the confirmation
population. Report: files created, hashes, gates, outcome label, `git status`,
and every blocker and deviation. Then wait for the separate post-development
authorization of `PREREGISTRATION.md` section 14.2.

## Step 13 -- Confirmation (only after the separate authorization)

Model `tools/run_authzgym_model_semantic_confirmation.py` on
`tools/run_authzgym_confirmation_v1_3_1.py`: module-level `SPLIT`,
`LAYOUT_INDICES`, `RESERVED_FALLBACK_PAIRS` constants, staged subcommands that
refuse to run out of order, and a `guard()` path predicate.

```
SPLIT                   = "confirmation_model_v1_3_1"
LAYOUT_INDICES          = (44, 45)
RESERVED_FALLBACK_PAIRS = ((46, 47), (48, 49))
```

Stages, in the `PREREGISTRATION.md` section-13.4 order, each recording its
hashes before the next begins: `freeze-record`, `generate` (with the section
13.3 duplication checks and the content-blind collision rule), `validate`
(answerability, then firewall, then gold-adequacy S-3), `call` (56 logical
calls), `score`, `seal`.

- If a duplication check collides, advance to the next reserved pair. Never
  inspect content to choose.
- If all listed pairs fail the content-blind conditions, **stop and request new
  authority**; never extend the sequence.
- If gold-adequacy fails, **stop and record**; this is a blocker, not a fallback
  trigger.
- One call per case. No case replacement, repair, regeneration, exclusion or
  reweighting after a failure.
- Seal the outcome either way.

## Step 14 -- Prospective repository corrections (separately gated)

Only **after ADR-0023 has been appended to `DECISIONS.md`**, only on explicit
instruction, and never mixed with any other step:

1. `state/STATUS.yaml`: record the executed, sealed, passing B-1 successor
   confirmation --- `successor_confirmation_executed: true`, the sealed
   population and seal hashes, the confirmation oracle figures, and a
   `roadmap.immediate_next_task` that reflects reality rather than the completed
   instruction.
2. `plan/ROADMAP.md`: add the recorded outcome to the Phase 5 cursor.
3. `MAP.md`: add a row for `experiments/authzgym_confirmation_v1_3_1/`.
4. `experiments/README.md`: add its entry under the non-admitted-evidence
   headings.
5. Run `python3 tools/emit_context.py`, then
   `python3 tools/check_knowledge_coherence.py`.

No sealed artifact, no historical report and no ADR is edited. Do not rewrite
any historical seal or ledger to match the section-5 hashing or logging
convention, and do not retroactively create a historical v1.3 freeze artifact.
Record the sealed B-1 confirmation as what it is -- a separately versioned
component/instrument compatibility confirmation -- and never as a pass of
AuthzGym v1.3 section 16.

---

## Blocking ambiguities -- stop immediately, do not decide

Stop and record, without choosing, if any of these appears:

- a step would require a threshold, denominator, population rule, retry rule,
  access condition or interpretation the preregistration does not already fix;
- anyone or anything suggests giving effect self-consistency a threshold, a
  veto, or any gating role; excluding, repairing or retrying a response because
  it is effect-inconsistent; or passing B-1 a truth-table-corrected effect vector
  in place of the model's submitted one;
- a protected-file hash differs, or a section-0.2 path is reached;
- the recorded B-1 development figures do not reproduce at step 5 after the
  harness wiring is correct;
- the response schema, the prompt, the population or the schedule would need any
  modification to make a call succeed;
- a structurally valid response is semantically wrong and something suggests
  retrying it;
- the spend projection or the accumulated spend would require reducing the
  schedule;
- the catalog exposes the model under a changed identity, or the observed
  fingerprint changes mid-run;
- a confirmation layout pair sequence would need extending;
- anything at all suggests changing B-1, the adapter, the estimator, a v1.3
  semantic rule, a threshold, the usefulness target or the tie rule.

Recording a blocker is a successful outcome of this handoff. Choosing is not.
