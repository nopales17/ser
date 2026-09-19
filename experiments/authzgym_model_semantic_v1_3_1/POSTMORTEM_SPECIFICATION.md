# N1 failure-localization postmortem -- specification

Condition under analysis: `model-semantic-v1.3.1-N1`.
Authority: ADR-0024, 2026-09-19. Status: authorized, not yet executed.

**This is exploratory evidence, not a new registered experimental condition.**
It has no hypothesis, no preregistered endpoint, no gate and no threshold. It
may not modify N1's verdict, satisfy or rerun any gate, create a threshold,
create an `E-*` record, alter B-1, v1.3, the model, the prompt, the retry policy
or any population, run model or provider inference, access or generate
confirmation, or authorize N2. Choosing or designing N2 is out of scope.

## 0. Inputs, exhaustively

Read-only, through the audited reader, with the confirmation never-open guard
active:

- the locked N1 development responses,
  `development/responses.jsonl` (`841427ab...`, 112 lines) and
  `development/attempts.jsonl` (`47a5a8c3...`), verified against
  `development/RAW_RESPONSE_LOCK.json` before any analysis;
- certified development gold semantics,
  `experiments/authzgym_semantic_contract_v1_3/annotations/development_annotations.jsonl`
  (certificate `d308e68b...`);
- the frozen v1.3 public contract and effect truth table
  (`effect_from_facts`), the development public and restricted populations, and
  the transformation maps;
- frozen B-1, `src/ser/authzgym/policies_v1_3_1.py` (`f9c92317...`);
- the existing frozen D0--D4 substitution definitions and the section-8/10/12
  diagnostic machinery, used **unchanged**.

Every frozen input's hash is verified before use and recorded. No N1 artifact is
edited. All outputs are separately named `POSTMORTEM_*` files.

## 1. D0--D4 re-derivation

Mechanically re-derive **all** D0--D4 canonical-repeat rows from the locked
responses using the already-frozen substitution definitions: 8 canonical sources
x 2 repeats x 5 diagnostics = **80 rows**.

`ERROR_PROPAGATION.json` remains byte-unchanged. Write
`POSTMORTEM_ERROR_PROPAGATION.json` with the complete row set, keyed by
`(case_id, repeat, diagnostic)` so no row can overwrite another.

Record the defect exactly, in these terms: `substitution_table()` keyed records
only by diagnostic identifier `D0`--`D4`, causing later canonical-repeat rows to
overwrite earlier rows in the serialized table even though the per-row
computations occurred. **This is not a change to N1's registered verdict** --
no gate, the primary endpoint and the verdict do not read that table.

## 2. Canonical decomposition

For all 8 canonical sources x 2 repeats, report per row:

- fact FP and FN, per slot f0--f16;
- effect-vs-gold errors, per candidate slot and public family;
- S-7 inconsistencies (`I_rc` per candidate, and the row's contribution to
  `C_response` and `C_field`);
- relation FP and FN by category (ownership, membership, role, context, general
  dependency) and by target;
- measured and gold B-1 value vectors;
- measured and gold argmax sets `M_i` and `G_i`;
- choice-set preservation (`M != {}` and `M subset of G`);
- top-1, top-2, normalized regret;
- the frozen error-propagation class;
- the D0--D4 readouts from section 1.

Output: `POSTMORTEM_CANONICAL_DECOMPOSITION.json`.

## 3. Minimum-correction diagnostics

Restoration predicate, frozen and unchanged:

```
M != {}  and  M subset of G        (G = the gold B-1 argmax set)
```

Run **four separately labelled searches** for each of the 16 canonical-repeat
rows. Never merge their results.

1. **effect-only raw-state search** -- edit submitted candidate-effect fields;
   each changed categorical field counts as one edit; facts and relations remain
   measured.
2. **relation-only raw-state search** -- flip unresolved-target relation Boolean
   fields; each bit flip counts as one edit; facts and effects remain measured.
3. **combined effect+relation raw-state search** -- permit both edit types;
   edit distance is the total number of changed fields and bits.
4. **fact-projection evaluator-only search** -- flip submitted fact Booleans;
   after each hypothetical fact edit set, deterministically recompute the four
   effects from those hypothetical facts using the frozen public v1.3 truth
   table; retain measured relations. **This is an evaluator-only counterfactual.
   It must never be described as the measured model state or as a permissible
   repair.**

For every search:

- enumerate deterministically by increasing edit distance;
- exhaust all candidates at distances 0, 1, 2, 3 and 4 as needed;
- stop at the first distance at which any restoring state exists;
- if a restoring state is found at `k <= 4`, report `k` as **exact** and retain
  one deterministic representative restoring edit set;
- if none exists through distance 4, report `>4`;
- **never infer a larger exact minimum.**

Also report, for each restoring intervention, whether it changes the B-1 value
vector, the argmax set and the usefulness readouts.

**These edit counts are exploratory localization diagnostics, not model-quality
metrics.** They must never be reported as a score, a rate, or a distance
between the model and competence.

Output: `POSTMORTEM_MINIMUM_CORRECTION.json`.

## 4. Relation-category decision relevance

For **every** measured relation FP or FN in the canonical-repeat rows:

- correct exactly that one relation bit toward gold;
- hold all other measured fields fixed;
- rerun frozen B-1;
- record whether the one-bit correction (1) changes any B-1 target value,
  (2) changes the argmax set, (3) alone restores the primary preservation
  predicate.

Aggregate the error count and each of those three sensitivity counts by
ownership, membership, role, context, general dependency, source and repeat.

Describe this as **single-error counterfactual sensitivity / decision
relevance**, never as causal attribution.

Output: `POSTMORTEM_RELATION_SENSITIVITY.json`.

## 5. S-7 localization

Reuse the accepted S-7 and D0/D3 machinery unchanged. Report:

- rows with S-7 violations;
- rows where the D0/D3 comparison changes B-1 decision behaviour;
- rows where the inconsistency is decision-harmless;
- whether the D3 substitution **alone** restores primary preservation.

S-7 remains `diagnostic_only` throughout: it has no threshold here either, and
nothing in this section may be reported as a gate result.

Output: `POSTMORTEM_S7_LOCALIZATION.json`.

## 6. Equivariance and repeats

Using the existing frozen readouts:

- decompose the S-14 failures (`24/80` passing) by transformation;
- identify which semantic fields changed under each failing transformation;
- distinguish value-changing, choice-changing and decision-harmless
  instability;
- compare each canonical source's two repeats at the facts, effects, relations,
  B-1-value and choice-set levels.

Output: `POSTMORTEM_EQUIVARIANCE_AND_REPEATS.json`.

## 7. Synthesis, and the only questions it may answer

`POSTMORTEM_SYNTHESIS.md` may answer these six and nothing else:

1. whether canonical failure is relation-dominated, fact/effect-dominated, or
   mixed;
2. whether S-7 repair or projection alone would restore any decisions;
3. how stable canonical failures are across repeats;
4. whether transformation instability appears additional to canonical failure;
5. whether any evidence contradicts the already-established adequacy of
   correctly populated v1.3 semantics + B-1 on the corresponding development
   instrument;
6. what empirical observations would distinguish insufficient N1 model
   capability, an unnecessarily difficult model-facing interface, or both.

Question 6 is answered as **observations that would distinguish**, never as a
verdict on which holds. The synthesis proposes no experiment, no interface
change and no model.

## 8. Claim boundary

The postmortem establishes nothing about model capability, the instrument's
adequacy, authorization reasoning, architecture, transfer or real-world value.
It is a localization of an already-frozen failure, produced from locked
responses under frozen definitions. N1's verdict `fail`, outcome
`semantic_screen_below_threshold`, `development_eligible: false`, and the 0/8
primary results on both repeats are fixed inputs to the analysis and are not
revisable by it. Confirmation, N2 and closed-loop work remain unauthorized.

A fresh Astra research-design adjudication may use the completed postmortem to
choose the next experiment. That choice is not made here.

## 9. Context the analysis should test rather than assume

Recorded so the analysis starts from observations, not from a narrative. Each is
a **pointer for section 7 to examine**, not a finding:

- model-conditioned B-1 scored top-1 `0.375`, top-2 `0.5`, regret `0.5583` --
  numerically identical to the recorded `B1` all-equal-value degenerate null
  (`0.375` / `0.5` / `0.558333`). Whether this reflects genuine rank collapse
  or coincidence is for section 2 and section 4 to establish;
- the frozen error-class census is `structurally_catastrophic: 9`,
  `decision_changing: 7`, and **zero** harmless rows of the 16;
- facts scored well above their screen (precision `0.9529`, recall `0.5376`)
  while effects (`0.2315`/`0.2098`) and relations (`0.5302`/`0.2460`) did not;
- S-7 `C_response` was `0.1696` with 189 violations, against `C_field`
  `0.578125`;
- repeat agreement was `8/8` -- the failure reproduced exactly across repeats;
- for two source instances the `longest_artifact` variant is byte-identical to
  `base_entry` (`PROCEDURAL_CORRIGENDUM.md` section 6), so its read-out
  duplicates `base_entry` there.
