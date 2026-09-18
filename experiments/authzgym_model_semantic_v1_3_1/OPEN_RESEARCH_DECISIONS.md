# Research-semantic decisions -- all resolved

Condition: `model-semantic-v1.3.1-N1`.

The brief for this specification was to leave DeepSeek no research-semantic
choices, and to stop and surface any remaining choice rather than resolve it.
Seven items were surfaced. **All seven are now adjudicated and incorporated.
No unresolved research-semantic decision remains in this package.**

---

# RESOLVED AND INCORPORATED

## O-6 -- effect self-consistency: threshold and gating role -- RESOLVED

**Disposition: `diagnostic_only`**, adjudicated by Astra.

> Effect self-consistency remains a mandatory measured and reported
> semantic/interface diagnostic, but has no independent advancement threshold
> and no veto power over development eligibility or untouched-confirmation
> success.

This resolves the tension recorded when the item was surfaced: the accepted
design held it as a zero-tolerance interface gate at `= 1.00`, while ADR-0019
and `PREREGISTRATION.md` section 8.4 hold that candidate effects are
deterministic consequences of facts and are explicitly not independent
capability evidence. The adjudication keeps the measurement mandatory and
removes the veto, so a derived channel can no longer terminate a condition whose
primary endpoint may have passed -- while every inconsistency stays visible.

Incorporated as:

- `PREREGISTRATION.md` section 8 preamble -- S-7 sits **outside** the validity
  precedence chain and can never constitute the semantic/interface failure that
  blocks later layers;
- section 8.2 -- the S-7 row reads `diagnostic_only`, no threshold;
- section 8.6 -- the normative text, the exact metric
  (`I_rc = 1[E_rc = T_c(F_r)]`, `C_response`, `C_field`), the reporting scopes
  (development and confirmation separately, development repeats separately, with
  the case/source/variant/family breakdowns), and the four things S-7 may never
  do;
- section 10.3 -- the `D0`/`D3` pair is retained as the S-7 localization, and
  substitutions never satisfy a gate;
- section 4.1 -- B-1 receives the model's actual submitted effect values,
  asserted in the scoring path;
- section 12 item 11 and section 12.1 -- three machine-enforced structural
  guarantees that S-7 cannot gate;
- section 13.8 item 6 -- the same for confirmation;
- section 15 -- S-7 is excluded from the `semantic_screen_below_threshold` row,
  and S-7 violations are preserved in every label with a visible count;
- ADR-0023 item D7a.

Unchanged by this adjudication: the directional-effect-versus-gold gate S-9, the
directional-effect continuity gate S-15, the no-semantic-retry rule, the
no-repair rule, and every historical specification and result.

---

## O-1 -- paired degradation bound (S-13) -- RESOLVED

Supplied by the accepted Astra design: top-1 decline `<= 0.125`, top-2 decline
`<= 0.125`, mean positive excess regret `<= 0.05`. Incorporated at
`PREREGISTRATION.md` section 8.3 with the exact formulas, the fixed
eight-source denominator, per-source clamping of excess regret at zero before
averaging, the `malformed_or_missing` contribution, and separate evaluation on
each development repeat. Prospective engineering advancement screen, not a
population estimate.

## O-2 -- presentation/selection equivariance (S-14) -- RESOLVED

Supplied by the accepted Astra design and narrowed to
**model-conditioned own-selection equivariance**: `80/80` repeat-matched
development transformation comparisons and `40/40` confirmation comparisons.
Incorporated at `PREREGISTRATION.md` section 8.3, which fixes "repeat-matched"
normatively (variant `v` of source `s` at repeat `r` compares against
`base_entry(s, r)`), fixes the denominators at 80 and 40, makes a comparison
involving a missing response a failure rather than an exclusion, and demotes the
value-vector and response-semantic equivalence rates I had proposed to
non-gating diagnostics. Prospective engineering advancement screen.

## O-3 -- directional-effect continuity (S-15) -- RESOLVED

Supplied by the accepted Astra design: precision `>= 0.60`, recall `>= 0.50`.
Incorporated at `PREREGISTRATION.md` section 8.3, which fixes the measurement as
within-model continuity keyed by `effect_family` (families are transformation
invariant, candidate slots are not), micro-aggregated over both continuity axes
-- cross-variant repeat-matched, and cross-repeat -- with the frozen `NA` rules
applying unchanged and the two axes also reported separately as non-gating. The
floors are numerically the same pair as the gold-referenced gate S-9, but S-15
is a separate gate against a different reference set and neither substitutes for
the other. Prospective engineering advancement screen.

## O-4 -- degenerate gold choice set is a blocker, not a fallback trigger -- RESOLVED

Retained as frozen: fail-closed. A canonical gold choice set equal to the entire
legal target set is an instrument-validity blocker. Execution stops, the blocker
is recorded, the population is spent, new authority is requested, and the
content-blind layout fallback sequence is never advanced on a content-derived
property. `PREREGISTRATION.md` section 13.7.

## O-5 -- the v1.3 section-16 contradiction (C-4) -- RESOLVED

Resolved as directed, and the resolution is narrower and more honest than the
one I had drafted:

- v1.3 section 16 is **not claimed to have passed**, by this condition or
  anything in it;
- the historical estimator's failed confirmation is **permanently preserved**,
  never rescored, re-aggregated, averaged or superseded;
- ADR-0019 and the v1.3 preregistration remain the semantic authority,
  unchanged;
- the applicable downstream-compatibility prerequisite is the separately
  versioned, sealed B-1 successor confirmation, already met and not re-run;
- the condition's freeze artifacts and manifest are new and live in this
  directory;
- nothing requires retroactively creating a historical v1.3 freeze artifact or
  modifying a historical report.

Incorporated at `PREREGISTRATION.md` section 0 items 4--6 and section 18, and at
ADR-0023 items D3 and D4.

## O-7 -- scope of the development advancement gates -- RESOLVED

The broader reading is confirmed: the full supporting-gate list applies at
development at its stated thresholds, alongside the two per-repeat primary
items. Astra's own supply of a development-side `80/80` threshold for S-14
settles it directly. `PREREGISTRATION.md` section 12, items 1--21.

## O-8 (recorded, never blocking) -- the est-repair sufficiency label stays qualified

ADR-0022 records that Arm A was closed after 2 of its 4 budgeted attempts on a
written impossibility argument, so the adapter arm is **untested, not
falsified**. This condition inherits B-1 and therefore inherits the
qualification: nothing produced here may be read as evidence that the fixed
adapter is adequate, nor as an attribution of the historical estimator's
preserved confirmation failure to either component family.
