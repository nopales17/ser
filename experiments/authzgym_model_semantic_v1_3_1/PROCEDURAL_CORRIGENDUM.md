# Procedural corrigendum -- `model-semantic-v1.3.1-N1`

Append-only. Authority: ADR-0024, 2026-09-19. This record corrects **statements
about** the locked N1 artifacts. It does not edit them: every artifact named
below remains byte-unchanged, and the hashes recorded here are the hashes of the
uncorrected files exactly as written by the run.

---

## 1. The incorrect `authorizing_adr` field

**Original field value, in every artifact listed in section 3:**
`"authorizing_adr": "ADR-0023"`, with the longer `authorization` strings citing
`ADR-0023 section 14.1`.

**Why it is incorrect.** ADR-0023 did not authorize Step 7. Its `Not authorized`
bullet reads: "model or provider inference of any kind; the 112 development
calls", and it states that "Development inference requires a further decision
after the freeze checklist passes." At execution time `DECISIONS.md` contained
no Step-7 authorization; the string "Step 7" did not appear in it at all.

The citation was not invented. Preregistration section 14.1 does list
"**development inference only**: the 112 logical calls of section 7" among what
acceptance authorizes. That sentence is a **latent defect of the
preregistration**: it was drafted when the package was expected to be accepted
whole, ADR-0023 then deliberately narrowed acceptance to zero-inference work,
and section 14.1 was never amended to match. A reader of the preregistration
alone could reach the run's conclusion. A reader of `MAP.md` could not: it makes
the condition directory non-authoritative for "authority to run inference", and
`DECISIONS.md` owns accepted governance decisions. ADR-0023 governs.

**Disposition.** The execution is a **procedural authorization deviation**. It
is not retroactively authorized.

## 2. ADR-0024's later acceptance, and its exact limit

ADR-0024 accepts the preserved run as the N1 development measurement, on the
strength of an independent re-verification of the frozen scientific and
acquisition condition -- including independent re-derivation of all 112 request
hashes from the frozen population, prompt and model condition.

**That acceptance does not convert the original execution into a properly
pre-authorized run.** Acceptance of a measurement and authorization of the act
that produced it are different things, and only the first is granted. Any later
description of N1 must carry the deviation. N1 must never be cited as an example
of the authorization boundary working, and the pattern -- citing a subordinate
document's stale clause against a governing ADR's explicit prohibition -- must
not be repeated.

**Prospective fix.** Preregistration section 14.1 is amended so it can no longer
be read as authorizing inference. The amendment is prospective and changes no
threshold, endpoint, gate, population or claim boundary.

## 3. Artifacts carrying the incorrect field

Byte-unchanged; hashes are of the uncorrected files.

| artifact | `file_sha256` |
| --- | --- |
| `DEVELOPMENT_SCORE.json` | `9ea2e95a1055a9a07b47168df650e9fbb15ea064db8ce93bcdc901852c9d05fc` |
| `ELIGIBILITY.json` | `4d4c605e825d50bcd20b995bd0d34ff5672d27fde289426115f8a576c74df8ba` |
| `ERROR_PROPAGATION.json` | `62d573c8ff82571dc66abe5aa01d053875ba040aace18881aac63aa3c8a72015` |
| `DEVELOPMENT_REPORT.json` | `daf8ac8a7b6456e6ca2a08f630c16f0ab50da8d03559e27e395310f544c0504d` |
| `DEVELOPMENT_REPORT.md` | `8be664ff2faaeaef96038c275b3cfe25b0881a8c38dbc8b8ccd8df9578e9ad64` |
| `development/RAW_RESPONSE_LOCK.json` | `4121dc3a6ab1f4468a8630e181851f6f474dcb1b5d6791ab149eeec8fff1c7b5` |

Locked raw inputs, also byte-unchanged and verified against the lock:
`development/responses.jsonl`
`841427ab8334f3fa7e89a21ae93a8e0ee678824c98fee80048b0294ac0bdd11e` (112 lines);
`development/attempts.jsonl`
`47a5a8c3d1bbbc90ae735081621c138b43832041f7339311b25d47210de04d23` (112);
`development/spend_ledger.jsonl`
`4ed23722564bbff99b4668e2fb45e7b4bd02e7879d1ade4fee006186931693b0` (112);
`development/transport_events.jsonl`
`0ecacd8ec8e2996c0705e6dd55e7f2c7a9adbd65c16ad53c81a3e5fc7c8b6582` (229);
`DEVELOPMENT_ACCESS_LEDGER.jsonl`
`2851515bf6fe6f6b1979e4657f3c6a47ff4fb3accf4545d33f3ff5a3c4741173` (24).

## 4. Reporting-stage wording

`DEVELOPMENT_REPORT.md` states:

> Model or provider calls made by this stage: 0

**This is true and is not a defect, but it is ambiguous when read alone.** It
means the **scoring and reporting stage** made zero model or provider calls. N1
**development acquisition** made **112 of 112** logical calls, as recorded in
`development/RAW_RESPONSE_LOCK.json`, `development/attempts.jsonl` and
`development/spend_ledger.jsonl`, at an accounted `$0.05775615`.

The finalized report is **not** overwritten. Future reports must use
unambiguous wording, naming the stage and giving the acquisition count
alongside, for example: "Provider calls made by this scoring/reporting stage: 0.
Provider calls made by N1 development acquisition: 112/112 (see the raw-response
lock)."

## 5. The D0--D4 serialization defect

Recorded exactly, and **not** a change to N1's registered verdict.

`substitution_table()` keys records **only by diagnostic identifier `D0`--`D4`**.
Later canonical-repeat rows therefore overwrite earlier rows in the serialized
table, even though the per-row computations occurred. Verified on disk:
`ERROR_PROPAGATION.json -> evaluator_only_diagnostic_substitution.rows` holds
exactly 5 entries, keyed `D0`--`D4`, each carrying the last row written
(`case_id` ending `#repeat2` of the final source), where 8 sources x 2 repeats x
5 diagnostics = **80 rows** were computed. The `error_class_census` totals 16
classified canonical-repeat rows, confirming the computations ran.

`ERROR_PROPAGATION.json` remains byte-unchanged. The complete rows are
re-derived into a separately named postmortem artifact under
`POSTMORTEM_SPECIFICATION.md`, using the already-frozen substitution
definitions. The defect is a serialization defect only: it did not affect any
gate, the primary endpoint, or the verdict, none of which read that table.

## 6. An observation surfaced by the ADR-0024 verification, recorded not acted on

Independent re-derivation found **54 distinct request hashes across the 56
development cases**. For two source instances --
`asv1-d-5e6417ce899f` and `asv1-d-8883a56f6778` -- the `longest_artifact`
variant's public input is **byte-identical to its `base_entry`**, because for
those sources the artifact with the greatest declared line count is the entry
artifact, making that variant a no-op.

This is a property of the **frozen v1.3 development population**, which predates
this condition and passed answerability validation; it is not a defect of the
N1 acquisition. It does not touch the primary endpoint (canonical `base_entry`
only), S-14 or S-15 (five equivalence variants, excluding `longest_artifact`).
It does mean the `longest_artifact` read-out duplicates `base_entry` for those
two sources. Recorded here for the postmortem to note; it changes nothing and
authorizes nothing.
