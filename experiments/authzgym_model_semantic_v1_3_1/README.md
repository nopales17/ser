# `model-semantic-v1.3.1-N1` -- proposed condition

Status: **accepted** -- ADR-0023, 2026-09-18. Zero-inference implementation is
authorized through the preregistered pre-inference freeze boundary only. No
model or provider call has been made at any point.

The next experiment changes exactly one link in the controlled chain,
`gold semantic response -> actual model semantic response`, and leaves
everything downstream frozen. It asks whether one frozen inexpensive model
configuration can read the current AuthzGym source artifact and produce enough
valid v1.3 semantic information for the frozen `est-repair-v1.3.1-B-1` component
to preserve useful next-inspection choices.

## Files

| File | Role |
| --- | --- |
| `ADR_0023_PROPOSED.md` | the new decision text, in ADR form, for Sol to append to `DECISIONS.md` |
| `PREREGISTRATION.md` | the normative specification |
| `IMPLEMENTATION_HANDOFF.md` | the mechanical step order for DeepSeek |
| `OPEN_RESEARCH_DECISIONS.md` | the research-semantic choices deliberately **not** made here |
| `REPOSITORY_CONTRADICTIONS.md` | the reconstructed cursor, re-derived hashes, and the four verified contradictions |

## Where each required deliverable lives

| # | Deliverable | Location |
| --- | --- | --- |
| 1 | new ADR / decision text | `ADR_0023_PROPOSED.md` |
| 2 | normative preregistration | `PREREGISTRATION.md` |
| 3 | implementation handoff for DeepSeek | `IMPLEMENTATION_HANDOFF.md` |
| 4 | exact schemas / formulas / denominators | `PREREGISTRATION.md` sections 3, 4.2--4.4, 5, 6.2, 8.2--8.5 |
| 5 | development schedule | `PREREGISTRATION.md` section 7 |
| 6 | response / retry / accounting policy | `PREREGISTRATION.md` section 11 |
| 7 | error-propagation specification | `PREREGISTRATION.md` section 10 |
| 8 | model-condition verification procedure | `PREREGISTRATION.md` section 9 |
| 9 | development pass/fail and confirmation-eligibility checklist | `PREREGISTRATION.md` section 12 |
| 10 | prospective confirmation construction / access / freeze protocol | `PREREGISTRATION.md` section 13 |
| 11 | inference-authorization boundary | `PREREGISTRATION.md` section 14 |
| 12 | prior-result / claim boundary | `PREREGISTRATION.md` sections 15--17 |

## Resolved

The three thresholds previously surfaced as missing are supplied by the accepted
research design and are incorporated at `PREREGISTRATION.md` section 8.3, each
with its exact formula and denominator:

- **S-13 paired degradation** -- top-1 decline `<= 0.125`, top-2 decline
  `<= 0.125`, mean positive excess regret `<= 0.05`;
- **S-14 model-conditioned own-selection equivariance** -- `80/80`
  repeat-matched development comparisons, `40/40` confirmation comparisons;
- **S-15 directional-effect continuity** -- precision `>= 0.60`, recall
  `>= 0.50`.

All three are prospective engineering advancement screens over eight source
instances. None is a population estimate.

The v1.3 section-16 contradiction is resolved without claiming anything
historical passed: section 16 is not claimed to have passed, the historical
estimator's failed confirmation is permanently preserved, ADR-0019 remains the
semantic authority, the sealed B-1 successor confirmation is the applicable
downstream-compatibility prerequisite, the condition's freeze artifacts are new
and local, and no historical freeze artifact is created or report modified.

Governance findings are fixed prospectively only: living state is reconciled
**after** the decision is accepted; raw-file SHA-256 is authoritative for new
artifacts with `canonical_json_sha256` recorded separately where useful and no
digest type ever called simply `population_hash`; file-open-level access logging
is required for this condition; historical ledgers are not rewritten.

## Ready -- no unresolved research-semantic decisions remain

The final open item, **effect self-consistency (S-7)**, is adjudicated
`diagnostic_only`: it remains a mandatory measured and reported
semantic/interface diagnostic, with **no independent advancement threshold and
no veto power** over development eligibility or untouched-confirmation success.

It is computed exactly from the model's submitted facts and submitted effects
using the frozen public v1.3 truth table and the public candidate family;
`C_response` and `C_field` are both reported, development and confirmation
separately and each development repeat separately; every violation is
enumerated; invalid and missing responses are kept separate and never imputed
consistent. No repair, no semantic retry, no exclusion. B-1 receives the model's
actual submitted effect values. The `D0`/`D3` substitutions localize the
contribution of inconsistencies and never satisfy a gate. S-9 and S-15 are
unchanged. An S-7 violation is a semantic error and is preserved in every
outcome label, but by itself cannot produce `semantic_screen_below_threshold`,
suppress the primary or downstream result, or block `development_eligible` or
`bounded_model_semantic_compatibility_confirmed`.

See `PREREGISTRATION.md` sections 8.6 and 12.1, and ADR-0023 item D7a.

## Next step

Append ADR-0023 to `DECISIONS.md`. The package is then executable from
`IMPLEMENTATION_HANDOFF.md` step 1.
