# est-repair-v1.3.1 study blocker -- step 1 baseline reproduction

Status: **stopped**. No candidate was created, no budget was consumed, and no
confirmation path was opened by this study.

Authorizing decision: ADR-0020. Governing specification:
`REPAIR_STUDY_PREREGISTRATION.md`. Executed plan: `IMPLEMENTATION_HANDOFF.md`.

## 1. Stop condition that fired

Handoff step 1, **Stop if**: "B0 does not reproduce the recorded figures exactly.
That is a contradiction between this handoff and the frozen artifacts; record it
in `STUDY_BLOCKER.md` and stop. Do not adjust the harness to reach the figures."
This is also stop condition 3 of the handoff's blocking-ambiguity list.

The harness was implemented exactly as written and the recorded figure was
asserted verbatim rather than substituted. It fails.

## 2. Observed versus recorded

Measured through the harness (`tools/run_estimator_repair_study.py`,
`src/ser/evaluation/authz_v1_3_1_harness.py`) against the frozen development
population, restricted population, and independent annotations:

| Figure | Recorded in preregistration section 6 / handoff step 1 | Measured | Reproduces |
| --- | --- | --- | --- |
| canonical top-1 | 0.625 | 0.625 | yes |
| canonical top-2 | 0.875 | 0.875 | yes |
| canonical mean normalized regret | 0.175 | 0.175 | yes |
| canonical illegal targets | 0 | 0 | yes |
| section-14 equivalence | 40/40, zero failures | 40/40, zero failures | yes |
| B0 own-ranking invariance | 36/40 | 36/40 (4 failures at `artifact_identifier_variation` and `combined_permutation` for the two ownership-family sources) | yes |
| `longest_artifact` top-1 | 0.125 | 0.125 | yes |
| `longest_artifact` top-2 | 0.375 | 0.375 | yes |
| **`longest_artifact` regret** | **0.783** | **0.6583333333333333** | **no** |

The failing assertion is
`tests/test_estimator_repair_harness.py::EstimatorRepairHarnessTestCase::test_longest_artifact_readout`
(`0.6583333333333333 != 0.7833`, difference exactly `0.125`).

The five figures that preregistration section 6 names as *the acceptance
criterion for the harness itself* reproduce exactly. The single unreproduced
figure is the non-gating `longest_artifact` read-out, which section 4.2 excludes
from the criterion and section 4.9 excludes from the gate.

## 3. Provenance of the recorded 0.783 figure

0.7833333333333333 is the `mean_normalized_regret` of the
`longest_artifact_noncanonical_observed` block of the **confirmation** split, as
stored in the `confirmation` block of
`experiments/authzgym_semantic_contract_v1_3/ORACLE_VALIDATION.json`. The
development block of that same file records `0.6583333333333333`.

Preregistration section 3.3 lists "the `confirmation` block of
`ORACLE_VALIDATION.json`" as forbidden exposure. The figure written into the
accepted preregistration and repeated in handoff step 1 therefore appears to be
a transcription of a confirmation-split read-out in place of the development
read-out.

Consequence: the recorded figure cannot be reproduced on the authorized
development split. Satisfying it would require reading the confirmation
channel, which section 3.3 and section 8.10 forbid and which step 6 of the
handoff makes a blocking violation.

## 4. Second, non-blocking discrepancy recorded for the same review

Handoff step 5 describes the new check as "the component's own **full ranking**"
mapped through `canonical_ordinal_by_variant_public_id` and compared, reported as
`n/40`. Pre-registration section 2.6 defines the same check through the
component's "own selection" (`max(values, key=lambda item: (values[item], item))`)
and records the baseline at **36/40**, with the four failures located at
`artifact_identifier_variation` and `combined_permutation` for exactly the two
ownership-family sources. Handoff step 1 pins the same 36/40 regression fixture.

Measured under both readings for B0:

- own **selection** invariance (preregistration section 2.6, handoff step 1):
  **36/40**, failing exactly where recorded;
- own **full-order** invariance (handoff step 5 wording): **25/40**.

The two readings disagree, and only the selection reading reproduces the
recorded fixture. The harness therefore treats the section-2.6 selection reading
as the gate and additionally reports the full-order number as
`full_order_is_descriptive_only` in every record. This is recorded here because
it changes what `40/40` means for a candidate; it is not the stop condition.

## 5. What was and was not done

Done: step 0 protected-hash capture and re-verification, step 1 harness,
`BASELINES.json` (B0 block only), `ACCESS_LEDGER.jsonl` study-start record, and
the step-1 tests.

Not done: the Tier-1 information ceiling, the B1/B2/B3 baselines, the frozen
`nd3_floor_from_b2`, arm A/B/C candidates, the component firewall suite, the
development report, and section 8.

Two measurements produced without any privileged content: all 203 protected
non-confirmation files were byte-identical at step 0 and step 1; and two harness
runs from different working directories produced byte-identical `BASELINES.json`.

Disclosure: handoff step 0 instructs the worker to hash *everything* under
`experiments/authzgym_semantic_contract_v1_3/`, so the step-0 integrity pass also
computed SHA-256 over the 16 confirmation-named files in that directory. No
confirmation content was parsed, retained, scored, counted, or used for any
design or selection decision, and the harness itself refuses to open any
confirmation path. This is recorded because section 12.2 does not authorize
"opening" the spent population even for integrity purposes.

## 6. Minimum decision needed to proceed

One authority decision, recorded as a corrigendum or a new appended ADR (the
accepted preregistration must not be edited in response to outcomes):

> Either (a) confirm that the `longest_artifact` regret in preregistration
> section 6 and handoff step 1 is a transcription error for the confirmation
> split, and authorize the development study to proceed with the recorded
> check evaluated against the development-measured value
> `0.6583333333333333`, or (b) resolve the study differently.

No other step-1 requirement is in conflict, and no research semantics are in
question: the v1.3 instrument, its populations, thresholds, usefulness target,
and the frozen estimator and adapter are byte-unchanged. If (a) is chosen, the
same corrigendum should also fix the section-2.6/step-5 wording so the
own-ranking gate is stated in one reading.

Until that decision, execution stops here and nothing further is created.
