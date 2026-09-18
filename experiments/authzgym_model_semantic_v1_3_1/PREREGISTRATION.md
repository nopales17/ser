# Model-semantic condition `model-semantic-v1.3.1-N1` -- normative preregistration

Condition ID: `model-semantic-v1.3.1-N1`

Status: `accepted` -- ADR-0023, 2026-09-18. Zero-inference implementation authorized through the section-18 freeze boundary only.

Authority chain: ADR-0019 ->
`experiments/authzgym_semantic_contract_v1_3/PREREGISTRATION.md` -> ADR-0020 ->
ADR-0021 -> ADR-0022 ->
`experiments/authzgym_estimator_repair_v1_3_1/DEVELOPMENT_REPORT.md` ->
`experiments/authzgym_confirmation_v1_3_1/REPORT.md` -> the accepted Astra
research design and the accepted choice-set-primary clarification -> proposed
ADR-0023 -> this document.

This document freezes the research semantics of the condition. It authorizes
nothing by itself (section 14). It changes no AuthzGym v1.3 semantics, does not
change B-1, and introduces no closed-loop routing, no Jev, and no richer SER
architecture. No step in it may be reordered by an implementation agent. If an
implementation would require choosing a new meaning, threshold, population rule,
or access condition, the implementation stops and records a blocker; it does not
choose (section 14.4).

---

## 0. Fixed inheritance

Not reopened anywhere in this document or any artifact it produces.

1. AuthzGym v1.3 semantics: the public request/response shape, the f0--f16 fact
   rules, the candidate-effect truth table, the five-category unresolved-target
   rule, the seven variants, the transformation bijections, the scoring
   definitions, the usefulness target, and the frozen tie rule. Byte-unchanged.
2. `src/ser/authzgym/policies.py` (SHA-256 `092a7a87...4167393`) and
   `src/ser/evaluation/authz_v1_3.py` (SHA-256 `60b1cb5d...a098f6`) are
   protected baselines.
3. The decision component is `est-repair-v1.3.1-B-1`,
   `src/ser/authzgym/policies_v1_3_1.py` (module SHA-256 `f9c92317...4d910d`,
   component class SHA-256 `88b77c5f...ca7a048`). It is not changed, retuned,
   re-derived, parameterized, or wrapped.
4. The historical estimator's preserved fresh-confirmation failure (canonical
   top-2 `0.750` against `>= 0.80`) stands, unreinterpreted and **permanently
   preserved**. It is never rescored, re-aggregated, averaged with anything,
   explained away or superseded. That component is not used in this condition.
5. AuthzGym v1.3 preregistration section 16 was **never satisfied**, and this
   condition does **not** claim that it was. No historical v1.3 freeze artifact
   is retroactively created and no historical report is modified to make it
   appear satisfied. ADR-0019 and the v1.3 preregistration remain the semantic
   authority for this condition, unchanged and unreinterpreted.
6. The applicable **downstream-compatibility prerequisite** for this condition
   is the separately versioned, sealed `est-repair-v1.3.1-B-1` successor
   confirmation (`experiments/authzgym_confirmation_v1_3_1/`, one-shot oracle
   `pass`, seal `463d208f...`). It is already met, is not re-run, and is not
   extended to cover anything it did not measure. The condition's own freeze
   artifacts and manifest are new and live in this directory (section 18).
7. The spent `confirmation_v1_3` population (layouts 40/41, public file SHA-256
   `0e20284b...`) is never opened, read, counted, sampled, hashed afresh, or
   characterized.
8. The sealed `confirmation_v1_3_1` population (layouts 42/43, public file
   SHA-256 `1321bcd1...`, seal `463d208f...`) is spent for B-1's oracle
   confirmation. It is **not** a model population, is not reused as one, and is
   not reopened by this condition for any purpose.
9. B-1's gold-conditioned adequacy on this instrument is already established and
   is not re-litigated: development canonical top-1 `0.75` / top-2 `1.0` /
   regret `0.116667`; sealed confirmation canonical top-1 `0.875` / top-2 `1.0`
   / regret `0.058333`; ND-1/ND-2/ND-3 true on both; own-selection equivariance
   `40/40` on both.
10. The development population is the existing v1.3 development population,
   8 sources x 7 variants = 56 cases, raw-file SHA-256 `dda4e0c0...`, whose
   answerability (certificate `d308e68b...`) and firewall validations pass.
11. Model and provider inference is unauthorized until section 14.2 is
    satisfied.

---

## 1. The question, the scope, and the non-claims

### 1.1 The question

> Can one frozen inexpensive model configuration read the current AuthzGym
> source artifact and produce enough valid v1.3 semantic information for the
> frozen `est-repair-v1.3.1-B-1` component to preserve useful next-inspection
> choices?

This changes exactly one link: `gold semantic response -> actual model semantic
response`. Everything downstream of the response is frozen.

### 1.2 Scope

One model, one configuration, one instrument, one component, one generator
family. Bounded extraction of published source-local authorization facts,
deterministic classification of their local candidate cues, and visible
unresolved calls to uninspected public inventory definitions -- nothing else.

### 1.3 Non-claims, in force whatever the outcome

The condition does not measure and may never be reported as measuring:
authorization competence; general code understanding; closed-loop routing;
adaptive-routing advantage; SER architecture superiority or any comparison
against ReAct, fixed-order, monolithic or ordinary-agent baselines; GitLab or
any real-repository transfer; real-world action value; complete vulnerability
diagnosis; posterior belief; or general model capability beyond this exact
configuration on this exact fixture family. It produces no `E-*` evidence record
and promotes no concept.

---

## 2. The model condition

### 2.1 One condition, frozen before any call

Exactly one inexpensive configuration on the repository's previously exercised
Nano-tier route. The condition record is
`MODEL_CONDITION.json` in this directory, written and hash-frozen **after** the
section-9 verification completes and **before** any call.

Required fields, all fixed before the first call and none re-chosen afterwards:

| Field | Value |
| --- | --- |
| `route_model_identifier` | `patchersniper_praneeth/gpt-5.4-nano` |
| `official_model_id` | recorded from official documentation at verification time |
| `endpoint_label` | configured OpenAI-compatible institutional endpoint via the approved UCSB egress hop |
| `api_style` | `openai_chat_completions_json_schema` |
| `immutable_revision` | the provider-exposed immutable revision or fingerprint if the catalog exposes one without inference; otherwise the literal `unavailable_without_inference` plus the catalog-snapshot hash |
| `reasoning_effort` | `none` |
| `temperature` | `null` (provider default not overridden) |
| `top_p`, `seed`, `stop`, `n` | not sent |
| `response_format` | JSON schema, the per-case `response_schema` already frozen in the population |
| `maximum_output_tokens` | `1024` (inherited from `MODEL_TRANSPORT_CONFIG.json` `limits.maximum_output_tokens`) |
| `maximum_input_tokens` | `4000` (inherited, same file) |
| `request_timeout_seconds`, `connect_timeout_seconds` | `90`, `15` |
| `transport_client` and version | recorded exactly |
| `runtime_version` | recorded exactly |
| `tls_verification` | recorded exactly, with the existing user-approved endpoint-scoped exception restated |
| `client_side_retries` | `0` -- hidden SDK/client retries disabled and asserted |
| `pricing` | the verified tariff of section 9.4, with its provenance and caveat |
| `inherits_from` | `experiments/authzgym_semantic_contract_v1_3/MODEL_TRANSPORT_CONFIG.json` plus that file's raw-file SHA-256 |

`experiments/authzgym_semantic_contract_v1_3/MODEL_TRANSPORT_CONFIG.json` is a
protected file and stays byte-unchanged, including its
`"model_identifier": "unassigned_until_separate_inference_authorization"`.
Proposed ADR-0023 is the separate authorization; the identifier is assigned in
`MODEL_CONDITION.json`, never by editing the protected file.

### 2.2 Prohibited within the condition

No second model, no automatic or manual escalation after any failure, no prompt
search or prompt variation, no system-instruction edit, no self-critique, no
voting, no sampling of multiple completions, no few-shot examples of any origin
and in particular none drawn from confirmation, no chain-of-thought elicitation,
no tool use, no semantic-response repair, and no post-hoc change to any request
field. The frozen prompt is
`experiments/authzgym_semantic_contract_v1_3/prompts/semantic_observation_v1_3.txt`,
used byte-unchanged.

### 2.3 Request construction

Requests are built only by `ser.authzgym.v1_3_public_input.build_normal_request`
and serialized only by `normal_request_bytes` (sorted keys, `,`/`:` separators,
`ensure_ascii=True`, UTF-8). The normal entry point rejects oracle arguments.
The normal initial state is empty and stays empty; `accept_normal_response`
raises otherwise. Nothing from the restricted bundle, the transformation maps,
the annotations, the canonical ordinals, or the usefulness vectors may enter a
request. This is asserted, not assumed (section 8.3, gate S-2).

---

## 3. The semantic interface -- unchanged

`authzgym_semantic_observation_v1_3` exactly as frozen: three top-level response
objects `facts` (f0--f16), `candidate_effects` (c0--c3 over
`support|contradict|neutral|unknown`), `unresolved_targets` (one `tN` per legal
uninspected slot, each with `r0`--`r4`). No extra properties. JSON booleans.
Exact enum members.

**The legal action set is the case's public, frozen
`legal_uninspected_target_slots`.** Model semantics do not alter target
legality. A response whose `unresolved_targets` key set differs from that set is
structurally invalid, is not repaired, and is handled by section 11.

---

## 4. The decision component and the primary endpoint

### 4.1 The component, and how it is fed

`est-repair-v1.3.1-B-1`, unchanged. It is invoked exactly as the frozen harness
invokes it: `build_sealed_input(case, parsed_response, contract)` produces the
section-2.4 sealed input exposing only the seven allowlisted items, and the
component returns a value per legal target slot. The only change from the sealed
oracle confirmation is **which response** is parsed: the model's, instead of the
independently certified gold annotation.

**B-1 receives the model's actual submitted effect values** -- never the
truth-table result computed from the model's facts, never a corrected vector,
never gold. This holds whatever the response's effect self-consistency turns out
to be (section 8.6, consequence 8), and it is asserted in the scoring path, not
merely intended.

The component reads no identifier, no ordinal, no `line_count`, no inventory
order, and no restricted field. The section-9 firewall of the repair
preregistration already validated this for the component; section 8.3 gate S-2
re-validates it for this condition on this condition's populations.

### 4.2 Choice sets

For canonical source `i`, with `L_i` the legal uninspected target slots:

```
V_i^gold  = B1component.values(sealed(case_i, gold_response_i))
V_i^model = B1component.values(sealed(case_i, measured_response_i))

G_i = { s in L_i : V_i^gold[s]  == max_{t in L_i} V_i^gold[t]  }
M_i = { s in L_i : V_i^model[s] == max_{t in L_i} V_i^model[t] }
```

Maximum and equality are taken after rounding each value to 12 decimal places,
the tolerance the frozen harness already uses for the degeneracy census. Both
sets are computed **without** the evaluator canonical ordinal; the ordinal
cannot influence either set.

### 4.3 The primary endpoint

```
preserved(i)  <=>  M_i != {}  AND  M_i is a subset of G_i
```

This permits a model-produced semantic state to refine a legitimate gold tie
without penalty, and rejects a model state that introduces a target B-1 did not
consider maximally valuable under gold semantics.

If no structurally valid response exists for source `i` after the permitted
retries, `M_i` is undefined and `preserved(i)` is **false**. The denominator
stays 8. A missing response is never imputed as a fact value, and is never
imputed as a preserved decision.

### 4.4 The primary gate

- **Confirmation (primary result):** `preserved(i)` on at least **7 of 8**
  canonical confirmation sources (`>= 0.875`).
- **Development (advancement screen):** `preserved(i)` on at least 7 of 8
  canonical development sources, computed **separately on each repeat**.
  Both repeats must independently reach `>= 7/8`. Repeat agreement -- the count
  of sources whose `preserved(i)` is identical across repeats, and the paired
  disagreement list -- is reported separately. The two Boolean outcomes are
  never averaged into a single eligibility number.

`7/8` is a **prospective engineering advancement screen over eight source
instances**. It is not an estimated population success rate, it carries no
confidence interval, and it must never be reported as one. No new statistical
null threshold is introduced for choice-set preservation (section 8.5).

### 4.5 Reported separately, never primary

- exact argmax-set equality, `M_i == G_i`;
- evaluator-canonical selected-target agreement (the target the frozen
  `(-value, canonical ordinal ascending)` rule returns under model semantics
  versus under gold semantics);
- top-two-set agreement;
- tie dependence: whether removing the evaluator's ordinal tie-break would
  change whether the case passes top-1 or top-2.

The frozen canonical ordinal remains evaluator-only. It is used only where the
existing usefulness scorer requires it -- to compute absolute top-1, top-2 and
regret. It never becomes model or controller input and is never part of the
scientific definition of primary decision preservation.

### 4.6 Unit of evidence

The unit is the **source instance**, 8 per split, one canonical `base_entry`
case each, equal weight `1/8`. The five equivalence variants are invariance
observations, not samples. `longest_artifact` is a different source-local
question and is retained only as a separately reported diagnostic: it never
selects, never gates, and never contributes to advancement. Non-canonical
variants are robustness and equivariance observations and cannot improve or
rescue the primary result.

### 4.7 Exactly where `longest_artifact` sits

`longest_artifact` is a different source-local question: a different current
artifact, different facts, a different relation matrix, and a target set that
includes the entry artifact. It is therefore:

- **excluded** from the primary endpoint, from every advancement decision, and
  from every selection of any kind -- those use only the 8 canonical
  `base_entry` source instances (section 4.6);
- **excluded** from the section-8.3 equivalence and continuity measurements,
  which are defined over the five semantic-equivalence variants only;
- **retained inside** the frozen v1.3 section-13 semantic-layer aggregates
  (facts, effects, relations), because those aggregates are defined over all 56
  equal-weight cases and narrowing them would change frozen scoring, which this
  condition may not do;
- **additionally reported** as its own separate downstream read-out --
  model-conditioned choice-set preservation, top-1, top-2 and regret over the 8
  `longest_artifact` cases -- clearly labelled a diagnostic, never a gate, and
  never combined with the primary.

No assumption of `longest_artifact` adequacy is made anywhere (section 17).

---

## 5. One exact hashing convention

Repository authority currently circulates three digests under the single name
"population hash" (`REPOSITORY_CONTRADICTIONS.md` section 4). This condition
fixes one convention and one vocabulary, and applies both to every artifact it
creates.

### 5.1 The convention

- **`file_sha256(p)` -- SHA-256 over the exact bytes on disk of `p` -- is the
  authoritative frozen-artifact byte hash for every new artifact this condition
  creates.** It is what every manifest, freeze record, access-ledger record,
  integrity check and seal in this condition records, and it is the only digest
  any gate, blocker or authorization refers to.
- `canonical_json_sha256(v)` -- SHA-256 over `ser.core.types.canonical_json(v)`
  encoded UTF-8: sorted keys, no insignificant whitespace, finite primitives.
  It is **optional, secondary and never authoritative**. Where it is useful --
  for value-identity across differing serializations -- it is recorded in its
  own explicitly named field, alongside and never instead of `file_sha256`.
- Every JSON file this condition writes is serialized with
  `json.dumps(value, indent=2, sort_keys=True) + "\n"`, so `file_sha256` is
  reproducible from the value.
- Every JSONL file is one canonical object per line,
  `json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"`.
- Every Markdown file is hashed as exact UTF-8 bytes with LF endings.
- A manifest's own `manifest_sha256` is computed with that field omitted, then
  stored.

### 5.2 Vocabulary, mandatory in every artifact this condition writes

| Field name | Meaning |
| --- | --- |
| `*_file_sha256` | authoritative: `file_sha256` of a named path |
| `*_canonical_json_sha256` | secondary, optional: `canonical_json_sha256` of a named value; never used where a file is meant, never used by a gate |
| `*_embedded_population_hash` | the value of a population file's own internal `population_hash` field, quoted verbatim |

**Multiple digest types are never called simply `population_hash`.** The bare
name `population_hash` is not used by this condition except when quoting a
historical record verbatim, and every such quotation is annotated with the
convention that produced it. A field that would otherwise be ambiguous carries
one of the three names above and no other.

### 5.3 Inherited digests are restated, never recomputed

`RESTATED_HASHES.json` records, for every inherited artifact this condition
depends on, the digest as recorded, the convention it was actually produced
under, and the re-derivation status. Verified at the time of writing:

| Recorded digest | Recorded as | Actually | Re-derives |
| --- | --- | --- | --- |
| `dda4e0c0...` | "development population hash" | `file_sha256` of `DEVELOPMENT_PUBLIC_POPULATION.json` | yes |
| `1615b87e...` | (not recorded anywhere) | `canonical_json_sha256` of the same file's parsed value; secondary only | n/a |
| `471c233d...` | the file's own `population_hash` field | inherited source-population hash from `authzgym_static_v1_1` | n/a |
| `1321bcd1...` | "population hash" and "public population file SHA-256" | `file_sha256` of `confirmation_v1_3_1/CONFIRMATION_PUBLIC_POPULATION.json` | yes |
| `0e20284b...` | "spent confirmation public" | `file_sha256`, restated from `CONFIRMATION_V1_3_1_FREEZE_RECORD.json` **without opening the spent population** | not re-derived, by design |
| `092a7a87...`, `f9c92317...`, `88b77c5f...`, `f0629d3b...`, `03bfe556...`, `ac4b8d47...`, `60b1cb5d...` | component/protected-file hashes | `file_sha256` (`88b77c5f...` is SHA-256 of the component class source text) | yes, all |

No historical seal, manifest, report or ADR is rewritten to match this
convention. Sealed artifacts stay byte-unchanged.

---

## 6. Access ledger at file-open granularity

`REPAIR_STUDY_PREREGISTRATION.md` section 8.5 required one record per **open**;
the delivered ledger is stage-granular
(`REPOSITORY_CONTRADICTIONS.md` section 5). This condition instruments the open.

### 6.1 Mechanism

Every read of a protected or confirmation path in this condition goes through a
single audited reader, `AuditedReader`, in the condition's harness module. No
stage may use `open()`, `Path.read_text`, `Path.read_bytes`, `json.load` on a
path, or any third-party loader on a protected or confirmation path. A static
check over the condition's own modules and tools enforces this and fails closed.

### 6.2 Record schema

One JSONL record per open, appended, never rewritten:

```json
{"schema_version": 1, "timestamp_utc": "...", "actor": "...", "process_id": 0,
 "stage": "...", "path": "...", "class": "protected|confirmation|public|condition",
 "operation": "read|write|hash|generate|validate|evaluate|seal",
 "bytes": 0, "file_sha256": "...", "tool_path": "...", "tool_sha256": "...",
 "authorization": "ADR-0023 section ...", "detail": ""}
```

### 6.3 Blocking rules

- Any open of a `confirmation_v1_3` path: blocking violation, stop.
- Any open of a `confirmation_v1_3_1` path by this condition: blocking
  violation, stop.
- Any open of a `confirmation_model_v1_3_1` path recorded **before** the
  section-13.4 freeze record is written: blocking violation; the population is
  spent immediately.
- Any protected-file open whose recorded `file_sha256` differs from the frozen
  value: blocking violation, stop.
- A ledger record missing `tool_sha256`, `process_id`, `file_sha256` or
  `authorization`: blocking validation failure.
- The development ledger and the confirmation ledger are separate files and are
  never merged.

Historical ledgers are not edited or backfilled.

---

## 7. Development schedule

- Population: the existing v1.3 development population, unchanged, raw-file
  SHA-256 `dda4e0c0...`. 8 source instances, 7 variants each, 56 cases.
- Schedule: the existing frozen `DEVELOPMENT_SCHEDULE.json`, unchanged. Each
  case is called **twice with identical request bytes**, `repeat=1` then
  `repeat=2`. Order is source-manifest order, then the seven variant orders,
  then repeat 1 then repeat 2.
- **112 logical calls.** No case is added, removed, reordered, resampled or
  re-weighted.
- No prompt or model tuning after any output is observed. The condition is
  frozen before call 1 and is byte-identical at call 112.
- There is no semantic-performance futility stop. All 112 calls complete unless
  an integrity, transport, mechanical-validity, access or spend stop fires
  (section 11.5). The retired v1.2 16/32 optimistic futility rule is not copied
  or adapted.
- Development determines **eligibility for confirmation** and nothing else. It
  produces no confirmed claim, and section 12 states its exact boundary.

---

## 8. Gates

Validity precedence is the frozen v1.3 order and is not reordered:

```
frozen-manifest integrity -> access/accounting -> answerability -> firewall
-> gold-adequacy (B-1 paired) -> mechanical response -> semantic/interface
-> downstream decision
```

A failure at an earlier layer blocks claims at every later layer. Transport and
raw mechanical observations may still be reported as scoped implementation
facts.

**S-7, effect self-consistency, sits outside this precedence chain.** Its
adjudicated disposition is `diagnostic_only` (section 8.6): it is a mandatory
measured and reported semantic/interface diagnostic with **no independent
advancement threshold and no veto power** over development eligibility or
untouched-confirmation success. An S-7 violation is a semantic error and is
preserved as one, but it never constitutes the "semantic/interface" failure that
this precedence blocks later layers behind. Every gate that participates in the
precedence chain is enumerated in sections 8.2 and 8.3; S-7 is not among
them.

### 8.1 Primary gate

`P-1` choice-set preservation, section 4.4. Confirmation `>= 7/8`; development
`>= 7/8` separately on each repeat.

### 8.2 Mandatory supporting gates with thresholds already frozen in repository authority

Reused unchanged; no value is re-derived, weakened or reinterpreted.

| ID | Gate | Requirement | Denominator |
| --- | --- | --- | --- |
| S-1 | Integrity / access / accounting | frozen manifest matches; zero access violations; every attempt recorded; spend within ceiling | per section 11 |
| S-2 | Answerability and firewall | answerability `pass`, firewall `pass`, zero failures, on every population used | per population |
| S-3 | Paired gold-semantic B-1 adequacy | on each population used: B-1 on gold meets top-1 `>= 0.60`, top-2 `>= 0.80`, regret `<= 0.35`, zero illegal, section-14 equivalence `40/40`, own-selection `40/40`; **and** ND-1 holds per canonical source, i.e. `G_i != L_i` for all 8 | 8 canonical sources |
| S-4 | First-attempt schema validity | `>= 0.99` | scheduled logical calls |
| S-5 | Post-permitted-retry validity | `= 1.00` | scheduled logical calls |
| S-6 | Zero illegal values / targets | `= 0` | all responses |
| S-7 | Effect self-consistency | **`diagnostic_only`** (section 8.6). Mandatory to measure, report and enumerate; **no advancement threshold, no veto**. Never gates, never blocks a later layer, never excludes a response | all structurally valid measured responses |
| S-8 | Fact precision / recall | `>= 0.65` / `>= 0.50` | frozen v1.3 section-13 micro counts |
| S-9 | Directional effect precision / recall | `>= 0.60` / `>= 0.50` | `(candidate, support)` and `(candidate, contradict)` items only |
| S-10 | Relation precision / recall | `>= 0.60` / `>= 0.50` | frozen v1.3 section-13 micro counts |
| S-11 | Absolute model-conditioned B-1 top-1 / top-2 / regret | `>= 0.60` / `>= 0.80` / `<= 0.35` | 8 canonical sources, frozen scorer |
| S-12 | Inherited non-degeneracy | ND-1, ND-2, ND-3 computed and recorded for the model-conditioned value vectors; ND-1 failure is a `structurally_catastrophic` classification (section 10) | 8 canonical sources |

Denominator rules, frozen and unchanged: precision is `TP/(TP+FP)`, recall is
`TP/(TP+FN)`; a zero denominator is `NA`, never `0` and never `1`; `NA` cannot
clear a threshold; a case with no positive gold labels reports recall `NA`, its
false-positive count, specificity over its negative slots, and exact-vector
correctness, and still contributes false positives to aggregate precision; a
layer with zero aggregate gold positives makes the population invalid before
inference; missing responses produce `missing`, never zeros. Development counts
are computed per repeat, averaged across the two repeats for each case, then
summed across the 56 equal-weight cases; confirmation has one record per case.
This is exactly `ser.evaluation.authz_v1_3.score_cases`, used unchanged.

### 8.3 Mandatory supporting gates resolved by the accepted Astra design

Each threshold below is supplied by the accepted research design. Each is a
**prospective engineering advancement screen over a fixed, small number of
source instances. None is a population estimate, none carries a confidence
interval, and none may be reported as one.**

#### S-13 -- paired degradation bound

Computed per split, paired per canonical source, gold-conditioned versus
model-conditioned, using the frozen scorer on the 8 canonical `base_entry`
sources:

```
top1_decline            = top1_gold            - top1_model
top2_decline            = top2_gold            - top2_model
excess_regret(i)        = regret_model(i) - regret_gold(i)
mean_positive_excess    = ( sum over i of max(0, excess_regret(i)) ) / 8
```

| Statistic | Requirement |
| --- | --- |
| `top1_decline` | `<= 0.125` |
| `top2_decline` | `<= 0.125` |
| `mean_positive_excess` regret | `<= 0.05` |

Denominator for both declines is the 8 canonical sources (`0.125` is exactly one
source of eight). `mean_positive_excess` clamps each source's excess at zero
before averaging, so a source where the model happens to beat gold cannot offset
a source where it degrades. A source whose model response is
`malformed_or_missing` contributes `top1_model = top2_model = 0` and
`regret_model = 1.0` for this gate; it is never dropped from the denominator.
On development the gate is evaluated **separately on each repeat**, on the same
repeat-matched basis as the primary endpoint (section 4.4).

#### S-14 -- model-conditioned own-selection equivariance

The component's own selection decision under **model** semantics must be
equivariant under the five semantic-equivalence transformations, compared after
mapping through `canonical_ordinal_by_variant_public_id`, exactly as the frozen
own-selection-decision reading of `CORRIGENDUM.md` section 2.3 defines it. A
declared top tie delegated to the frozen canonical-ordinal rule is admissible; an
identifier-dependent internal tie-break is not.

| Split | Comparisons | Requirement |
| --- | --- | --- |
| development | 8 sources x 5 equivalence variants x 2 repeats, **repeat-matched** | **80/80** |
| confirmation | 8 sources x 5 equivalence variants x 1 call | **40/40** |

"Repeat-matched" is normative: the comparison for variant `v` of source `s` at
repeat `r` is made against the `base_entry` response of source `s` **at the same
repeat `r`**. A cross-repeat comparison is never substituted for a missing
same-repeat one. A comparison whose variant response or whose repeat-matched
`base_entry` response is `malformed_or_missing` **fails**; it is never excluded
from the denominator, which is fixed at 80 and 40 respectively.

Reported alongside, non-gating: model-conditioned B-1 value-vector equivalence
within `1e-12` over the same comparisons, and model response semantic
equivalence (facts identical; effects identical after candidate-slot remapping;
relations identical after target remapping).

#### S-15 -- directional-effect continuity

Continuity is measured **within the model's own outputs**, not against gold. The
directional item set of a response is
`{ (effect_family, value) : value in {support, contradict} }`, keyed by
`effect_family` because families are invariant under every transformation while
candidate slots are not.

For each continuity comparison, `R` is the reference response's directional item
set and `P` the compared response's:

```
TP = |P intersect R|,   precision = TP / |P|,   recall = TP / |R|
```

The comparison set is the union of both continuity axes:

- **cross-variant**: for each source `s`, each equivalence variant `v`, each
  repeat `r` -- reference `base_entry(s, r)`, compared `v(s, r)`, repeat-matched;
- **cross-repeat** (development only): for each case -- reference `repeat 1`,
  compared `repeat 2`.

Counts are micro-aggregated over the whole comparison set into one precision and
one recall.

| Statistic | Requirement |
| --- | --- |
| continuity precision | `>= 0.60` |
| continuity recall | `>= 0.50` |

The frozen `NA` rules of section 8.2 apply unchanged: a zero denominator is `NA`,
never `0` and never `1`, and `NA` cannot clear a threshold. A comparison
involving a `malformed_or_missing` response contributes `P = {}`, which
contributes zero true positives and its reference items as false negatives.
Cross-variant and cross-repeat precision and recall are **also** reported
separately, as non-gating diagnostics.

These floors are numerically the same pair as the gold-referenced directional
gate S-9, but S-15 is a **separate gate against a different reference set**
(the model's own base response rather than gold). Neither substitutes for the
other, and passing one is never reported as passing the other.

### 8.4 Candidate effects are never a second capability signal

Candidate effects are a deterministic public local-cue classification of the
submitted fact vector. Gold effects are the same function applied to the gold
fact vector. Directional effect metrics (S-9) and effect self-consistency (S-7)
are derived interface diagnostics from fact semantics. They are never
double-counted as independent semantic-capability evidence, and every report
that renders them must carry that sentence.

### 8.5 The null, and what it is for

The existing all-equal-value null (baseline `B1`: identical value for every
legal target, selection by the frozen ordinal tie-break alone; recorded
development figures top-1 `0.375`, top-2 `0.5`, regret `0.558333`) is
recomputed on every population used and **reported**. It is retained for
usefulness and non-degeneracy interpretation only. It is **not** converted into
a gate on choice-set preservation, and no new statistical null threshold for
choice-set preservation is introduced.

### 8.6 Effect self-consistency (S-7) -- adjudicated `diagnostic_only`

**Disposition: `diagnostic_only`.** Adjudicated by Astra and normative here.

> Effect self-consistency remains a mandatory measured and reported
> semantic/interface diagnostic, but has no independent advancement threshold
> and no veto power over development eligibility or untouched-confirmation
> success.

#### 8.6.1 Normative consequences

1. Effect self-consistency is computed **exactly** from the model's submitted
   facts and submitted effects, using the frozen public v1.3 effect truth table
   and the public candidate family. No other input is used.
2. Both **response-level** and **field-level** consistency are reported.
3. **Every violation is enumerated.**
4. Invalid and missing responses are kept **separate** and are **never imputed
   consistent**.
5. **No response repair.**
6. **No semantic retry.** (Unchanged from section 11.2; restated because it is
   what makes an inconsistency unrecoverable and therefore what made the gating
   question material.)
7. **No exclusion because of inconsistency.** An inconsistent response stays in
   every population, every denominator and every other metric.
8. **B-1 receives the model's actual submitted effect values.** Never the
   truth-table result, never a corrected vector, never gold.
9. **Diagnostic substitutions never satisfy a gate** (section 10.3, enforced).
10. The existing `D0`/`D3` diagnostic analysis is retained for localizing the
    contribution of inconsistencies.
11. All existing directional-effect-versus-gold (S-9) and directional-effect
    continuity (S-15) gates are **unchanged**.
12. An S-7 violation remains a semantic error, but **by itself** it cannot
    produce `semantic_screen_below_threshold`, suppress the primary or
    downstream result, block `development_eligible`, or block
    `bounded_model_semantic_compatibility_confirmed`.
13. Historical specifications and results remain unchanged.

#### 8.6.2 The exact metric

For every structurally valid measured response `r` and candidate slot `c`:

```
I_rc = 1[ E_rc = T_c(F_r) ]
```

where `F_r` is the submitted fact vector, `E_rc` is the submitted effect, and
`T_c(F_r)` is the frozen public v1.3 truth-table result for that candidate's
public family.

Report both:

```
C_response = ( sum over r of ( product over c of I_rc ) ) / N
C_field    = ( sum over r of sum over c of I_rc ) / ( 4 N )
```

`N` is the number of structurally valid measured responses in the reporting
scope. Invalid and missing responses are excluded from `N` and are reported
separately with their own counts; they are never counted as consistent and never
counted as inconsistent.

`T_c` is `ser.authzgym.v1_3_contract.effect_from_facts` applied to the public
contract, the case's public `candidate_hypotheses`, and the response's own
submitted facts -- the same frozen function the scorer already uses. The
candidate's **public family** is the key; the opaque public label and the slot
index are addressing data only.

#### 8.6.3 Reporting scopes

`C_response` and `C_field` are reported for **development and confirmation
separately**, and **for each development repeat separately**, each with the
case, source, variant and family breakdowns already specified in section 13 of
the v1.3 preregistration. The violation enumeration carries, per violating
response: case id, split, repeat, attempt ordinal, candidate slot, public family,
the submitted fact vector, the submitted effect value, and `T_c(F_r)`.

#### 8.6.4 What S-7 may never do

It may not gate. It may not veto. It may not block a later layer in the
section-8 precedence. It may not exclude a response from any population,
denominator or metric. It may not cause a retry, a repair or a substitution. It
may not alter what B-1 receives. And no implementation agent may give it a
threshold.

---

## 9. Model-condition verification procedure -- zero inference

All of section 9 completes **before** `MODEL_CONDITION.json` is frozen and
before any billable call. No step in section 9 submits a chat/completions
request. A connectivity or catalog probe is not a paid inference and is recorded
as such.

### 9.1 Route availability

1. Establish the supervised egress hop exactly as
   `ser.authzgym.tunnel_supervisor` already does, with the recorded policy, the
   stripped SSH environment, and per-attempt liveness records.
2. Issue the catalog probe `GET {OPENAI_BASE_URL}/models` through the hop.
   Record HTTP status, latency, `curl` return code, and the raw catalog bytes.
3. Record `paid_inference: false` for the probe, as
   `transport_config.json.connectivity_probe.paid_inference` already does.
4. Save the catalog as `MODEL_CATALOG_SNAPSHOT.json` and record its
   `file_sha256`.

Blocker: probe failure, non-200, or an unreachable hop. Record and stop. Do not
substitute a different route, a different hop, or a different model.

### 9.2 Actual / provider model identity

5. Assert `patchersniper_praneeth/gpt-5.4-nano` is present in the catalog, by
   exact `id` equality. Record its `id`, `owned_by`, `created` and every other
   field the catalog exposes for that entry, verbatim.
6. Record the total catalog size and the full list of `id` values, so the
   selection is auditable and so a later reader can see that no comparison or
   escalation was performed.
7. Record explicitly that no other model is selected, evaluated, probed or
   compared, and that the selection rule is "the route previously exercised by
   `authzgym_static_realmodel_v1`, `authzgym_semantic_contract_v1_2` and
   `authzgym_transport_envelope_v1`", fixed by proposed ADR-0023 before
   verification began.

Blocker: the identifier is absent, or appears under a different `owned_by`, or
appears more than once. Record and stop; do not select a near neighbour.

### 9.3 Supported settings

8. From official vendor documentation for the underlying official model id,
   record: Chat Completions support; structured-output / JSON-schema
   `response_format` support; `reasoning_effort: none` support; the maximum
   output-token limit; and the documentation URL and retrieval date.
9. Assert that every field of `MODEL_CONDITION.json` section 2.1 is within
   documented support. Any field that is not documented as supported is not
   sent.
10. Record the caveat verbatim: the institutional endpoint's actual behaviour
    and billing are **not** established by its model catalog or by vendor
    documentation.

Blocker: a required capability is not documented as supported. Record and stop.

### 9.4 Immutable revision / fingerprint

11. If the catalog entry exposes an immutable revision, version, digest or
    fingerprint without inference, record it as `immutable_revision`.
12. If it does not, record `immutable_revision: "unavailable_without_inference"`
    together with `MODEL_CATALOG_SNAPSHOT.json`'s `file_sha256` as the
    strongest zero-inference identity evidence available.
13. In either case, the `system_fingerprint` (or equivalent) returned by the
    **first** response of the run is recorded as `observed_fingerprint_first`.
    Every later response's value is compared against it. **Any change of
    observed fingerprint mid-condition is a blocking integrity violation**: the
    run stops, the attempts already made are kept, and the condition is recorded
    as `invalid` for identity drift. Recording an observed fingerprint is not
    permission to change the frozen configuration.

### 9.5 Tariff

14. Record the official published list price per million tokens for input,
    cached input and output for the underlying official model id, with the
    documentation URL and retrieval date. The repository's previously recorded
    Nano list pricing is `input 0.20`, `cached_input 0.02`, `output 1.25` USD
    per million tokens; it is **re-verified**, not assumed, and the verified
    value is what enters `MODEL_CONDITION.json`.
15. Record the accounting basis verbatim: "official list pricing applied to
    provider-reported usage; not an institutional billing statement".
16. Compute and write `COST_GATE.json` before any call:

```
max_submissions            = 2 * (112 + 56) = 336
projected_uncached_input   = 336 * maximum_input_tokens
projected_output           = 336 * maximum_output_tokens
projected_worst_case_usd   = projected_uncached_input  * input_per_million/1e6
                           + projected_output          * output_per_million/1e6
proceed                    = projected_worst_case_usd <= 2.50
```

    Caching is never assumed: the projection uses the uncached input rate for
    every submission. Under the repository's recorded Nano list pricing and the
    frozen `4000`/`1024` ceilings this is
    `336*4000*0.20/1e6 + 336*1024*1.25/1e6 = 0.2688 + 0.4301 = 0.6989` USD, well
    inside the ceiling -- but the number that governs is the one computed from
    the **verified** tariff at verification time.

17. **If `proceed` is false, stop before inference.** Do not reduce the
    schedule, do not drop repeats, do not drop the confirmation split, do not
    lower the output ceiling, and do not switch model. Record the blocker and
    request new authority.

### 9.6 Verification artifacts

`MODEL_CONDITION_VERIFICATION.json` records steps 1--16 with every observed
value, every blocker check and its result, `paid_inference: false` throughout,
and the `file_sha256` of `MODEL_CATALOG_SNAPSHOT.json`. Then, and only then,
`MODEL_CONDITION.json` is written and hash-frozen.

---

## 10. Error-propagation specification

The frozen analysis chain is operationalized exactly as:

```
model semantic error  (facts / candidate_effects / unresolved_targets)
  -> effect consequence          (published truth table over the submitted facts)
  -> B-1 salient relation/category state   (salient tag set)
  -> target values / tie groups  (per-target value, rounded to 12 dp)
  -> choice set                  (argmax set M_i)
  -> usefulness / regret         (frozen scorer, evaluator channel)
```

### 10.1 Localization

For every case with a structurally valid measured response, record against the
certified gold annotation:

- per-fact-slot confusion over f0--f16;
- per-candidate effect confusion over the four-way enum, plus the directional
  subset;
- per-target-per-category relation confusion over `tN x r0..r4`;
- the model's salient tag set versus gold's;
- the per-target value vector, the tie-group partition, and `M_i` versus `G_i`;
- `selected`, `top1`, `top2`, `mean_normalized_regret` under the frozen scorer,
  model-conditioned and gold-conditioned, paired.

### 10.2 The five classes -- exhaustive, mutually exclusive, precedence-ordered

Applied in this order; the first match wins.

1. **`malformed_or_missing`** -- no structurally valid response after the
   permitted transport replay and structural retry, or a transport loss with no
   response. No B-1 evaluation is possible. `preserved(i)` is false.
2. **`structurally_catastrophic`** -- structurally valid, but the derived state
   collapses the decision: `M_i == L_i` while `G_i` is a proper subset of `L_i`.
   This is the ND-1 failure signature and the exact mode that spent the earlier
   confirmation population. `preserved(i)` is false.
3. **`decision_changing`** -- `M_i` is non-empty and is **not** a subset of
   `G_i`, and class 2 did not apply. The model state introduced a target B-1 did
   not consider maximally valuable under gold semantics. `preserved(i)` is
   false.
4. **`value_harmless`** -- the model-conditioned and gold-conditioned value
   vectors are equal for every legal target within `1e-12`. Semantic errors, if
   any, did not reach the value layer. `preserved(i)` is true.
5. **`decision_harmless`** -- value vectors differ somewhere, `M_i` is non-empty
   and is a subset of `G_i`. The decision survives a value-layer error, possibly
   as a strict refinement of a legitimate gold tie. `preserved(i)` is true.

Every case in every split carries exactly one class. Class counts are reported
per split, per repeat, per family, per variant and per source.

### 10.3 Evaluator-only diagnostic substitutions

B-1 reads only `candidate_effects` and `unresolved_targets`; facts reach it only
through the published effect truth table. Four counterfactual reconstructions
are therefore computed, **in the evaluator channel only**:

| ID | Effects used | Relations used | Isolates |
| --- | --- | --- | --- |
| `D0` | model | model | the measured result (not a substitution) |
| `D1` | gold | model | the decision cost of the model's effect errors |
| `D2` | model | gold | the decision cost of the model's relation errors |
| `D3` | `effect_from_facts(model facts)` | model | whether the model's effect errors are downstream of its fact errors or are violations of the published effect rule itself -- this is the **S-7 localization**: the gap between `D0` and `D3` is exactly the decision-level contribution of the response's effect self-consistency violations |
| `D4` | gold | gold | the gold reference (already computed as `G_i`) |

For each of `D1`--`D3` record the resulting value vector, choice set, and
`preserved`-equivalent Boolean, plus the frozen scorer's top-1/top-2/regret.

**These substitutions never touch the measured response.** The measured response
bytes, its hash, its attempt record and its classification are unchanged by
them; no substituted state is written back; **no substituted result may satisfy
any gate, primary or supporting**; and every table rendering them must be
labelled `evaluator_only_diagnostic_substitution`. Substituted results are
reported in a section separate from every gated number.

The `D0`/`D3` pair is retained specifically to localize the contribution of
effect self-consistency violations (section 8.6, consequence 10). It is a
localization, not a repair: `D3` never becomes the measured result, never
replaces what B-1 received, and never enters a gate.

---

## 11. Response, retry and accounting policy

### 11.1 Structural validity

A response is structurally valid when, and only when, all hold: the transport
returned a body; the body parses as JSON; `finish_reason` is not a length
termination; the object has exactly the three frozen top-level keys and no extra
properties; `facts` is exactly f0--f16 with JSON booleans; `candidate_effects`
is exactly c0--c3 with exact enum members; `unresolved_targets` keys equal
exactly the case's `legal_uninspected_target_slots` rendered `tN`, each with
exactly `r0`--`r4` as JSON booleans; and
`ser.authzgym.v1_3_contract.parse_response` accepts it. Nothing else is
considered, and in particular semantic correctness is not considered.

### 11.2 Retries

Per logical call, at most:

- **one identical-byte transport replay** -- a transport-layer failure (no body,
  connect failure, timeout, proxy handshake error) permits exactly one
  resubmission of byte-identical request bytes;
- **one structural-response retry** -- a returned but structurally invalid
  response permits exactly one resubmission of byte-identical request bytes.

Request bytes are identical across every attempt of a logical call; this is
asserted by hash before each submission. Hidden SDK or client retries are
disabled and asserted to be zero. There is **no retry for a structurally valid
but semantically wrong response**, at any point, for any reason.

### 11.3 Which response is measured

**The measured response is the first structurally valid response, in attempt
order, under this frozen retry-selection rule.** Attempt order is the order of
submission and is recorded. Later attempts, if any exist, are kept but are never
measured, never substituted, and never compared for selection.

### 11.4 Everything is kept

Every attempt is preserved: attempt ordinal, request bytes hash, raw response
bytes, raw response hash, HTTP status, `curl` return code, latency,
`finish_reason`, `system_fingerprint`, provider-reported usage, transport
outcome, structural-validity verdict and failure reason. Failed submissions,
ambiguous transport submissions and discarded later attempts are all retained
and all counted against spend. No attempt is deleted, edited, repaired or
regenerated.

### 11.5 Stop conditions before the schedule completes

Integrity (frozen manifest mismatch, protected-file drift); access (any section
6.3 violation); identity drift (section 9.4 step 13); spend (accumulated cost
would exceed `$2.50`); transport exhaustion under the frozen replay bound; or an
unrecoverable egress failure. Each records a blocker, preserves everything
collected, and stops. None of them is permission to tune, escalate, reduce the
schedule, or retry semantics.

### 11.6 Accounting

Accumulated cost is computed after **every** submission from provider-reported
usage at the verified tariff and is written to an append-only ledger. The
`$2.50` hard ceiling covers the entire model condition: development,
confirmation, all permitted retries, failed submissions and ambiguous transport
submissions. A submission that would carry the accumulated total past the
ceiling is not made.

---

## 12. Development pass/fail and confirmation-eligibility checklist

Every item is blocking and is evaluated in this order. `ELIGIBILITY.json`
records each item's observed value and verdict.

| # | Item | Requirement |
| --- | --- | --- |
| 1 | Frozen-manifest integrity | every protected and condition file matches its frozen `file_sha256` |
| 2 | Access ledger | file-open granular, schema-complete, zero section-6.3 violations |
| 3 | Accounting | every attempt recorded; accumulated cost `<= $2.50`; no unrecorded submission |
| 4 | Schedule completeness | 112 logical calls attempted; no case skipped, added or reordered |
| 5 | Answerability | development `pass`, zero unsupported or ambiguous forms |
| 6 | Firewall | development `pass`, zero failures |
| 7 | Gold-adequacy (S-3) | B-1 on gold meets the frozen gate on the development population, and `G_i != L_i` for all 8 canonical sources |
| 8 | First-attempt schema validity (S-4) | `>= 0.99` |
| 9 | Post-retry validity (S-5) | `= 1.00` |
| 10 | Zero illegal values/targets (S-6) | `= 0` |
| 11 | Effect self-consistency (S-7) | **`diagnostic_only`** -- `C_response` and `C_field` computed and reported per repeat, every violation enumerated, invalid/missing kept separate; **not a gate, and not an input to any other item** (section 8.6) |
| 12 | Fact precision/recall (S-8) | `>= 0.65` / `>= 0.50` |
| 13 | Directional effect precision/recall (S-9) | `>= 0.60` / `>= 0.50` |
| 14 | Relation precision/recall (S-10) | `>= 0.60` / `>= 0.50` |
| 15 | Absolute model-conditioned B-1 (S-11) | top-1 `>= 0.60`, top-2 `>= 0.80`, regret `<= 0.35` |
| 16 | Non-degeneracy (S-12) | ND-1/ND-2/ND-3 computed and recorded; ND-1 failures enumerated |
| 17 | Paired degradation (S-13) | top-1 decline `<= 0.125`, top-2 decline `<= 0.125`, mean positive excess regret `<= 0.05`; **separately on each repeat** |
| 18 | Model-conditioned own-selection equivariance (S-14) | **80/80** repeat-matched development comparisons |
| 19 | Directional-effect continuity (S-15) | continuity precision `>= 0.60` and recall `>= 0.50`, micro-aggregated over both continuity axes |
| 20 | **Primary, repeat 1** | choice-set preservation `>= 7/8` canonical sources on repeat 1 alone |
| 21 | **Primary, repeat 2** | choice-set preservation `>= 7/8` canonical sources on repeat 2 alone |
| 22 | Repeat agreement | computed and reported separately; **never** averaged into items 20 or 21 |
| 23 | `longest_artifact` | computed and reported as a separate diagnostic; contributes to no item above |

Development **passes** if and only if items 1--10 and 12--21 all hold. The gated
item set is exactly `{1..10} union {12..21}`; it is written that way in the
harness, as an explicit literal set, so that no later edit can widen it by
accident. **Item 11 is not a member of it**, and items 22 and 23 are not members
of it. Item 11 is recorded with its measured values and its violation
enumeration and contributes nothing to the verdict; an eligibility computation
that reads item 11's verdict field raises (section 12.1).

Every threshold in items 12--21 is a prospective engineering advancement screen
over eight source instances. None is a population estimate.

### 12.1 Structural guarantee that S-7 cannot gate

Three machine-enforced properties, all unit-tested before any call:

1. `GATED_DEVELOPMENT_ITEMS` is a frozen literal set containing `1..10` and
   `12..21`, asserted not to contain `11`.
2. The eligibility function receives the S-7 record as a `DiagnosticOnly`
   wrapper whose `verdict` attribute raises `DiagnosticOnlyMisuse` on access. A
   test constructs an eligibility computation that tries to read it and asserts
   the raise.
3. A test sets S-7 to total failure -- `C_response = 0.0`, every response
   enumerated as violating -- holds every other item at pass, and asserts that
   the development verdict is still `pass`, that the outcome label is still
   `development_eligible`, and that the enumerated violations are present in the
   report.

A development pass makes the condition **eligible** for confirmation. It is not
a result, is not a confirmed claim, and does not establish that confirmation
will pass: 8 canonical sources against a `>= 7/8` screen cannot support that
inference.

---

## 13. Prospective confirmation construction, access and freeze protocol

Not generated during development. Not accessed until section 14.2 is satisfied.

### 13.1 Population

- Split label: `confirmation_model_v1_3_1`.
- Generator `src/ser/authzgym/generation.py` (`03bfe556...`) and converter
  `src/ser/authzgym/v1_3_population.py` (`ac4b8d47...`), byte-unchanged. No
  generator parameter, seed, template or production is altered.
- Four mechanism families per layout, two layouts, **eight independent source
  instances**, the same seven variants, **56 cases**, **one call each**.

### 13.2 Layout selection -- content-blind, prospective

- Proposed layouts **44/45**, admitted only if content-blind provenance
  establishes they were never generated or inspected. The permitted evidence is
  exactly: directory listing, file names, manifest metadata fields already
  permitted before freeze, and textual search of specifications for layout
  literals. Opening generated case content to decide is forbidden.
- Prospective collision-only fallback, in order: **46/47**, then **48/49**.
- A collision is resolved by advancing to the next listed pair and **never** by
  inspecting content.
- **If all prospectively listed pairs fail the preregistered content-blind
  eligibility and collision conditions, stop and request new authority. The
  sequence is never extended automatically.**

### 13.3 Duplicate and equivalence checks -- all blocking

Against the development population and, **by construction and without opening
them**, against `confirmation_v1_3` and `confirmation_v1_3_1`:

1. population `file_sha256` differs from `dda4e0c0...`, `0e20284b...` and
   `1321bcd1...`;
2. case-id sets pairwise disjoint;
3. `public_input_sha256` sets pairwise disjoint;
4. no source-episode-id collision;
5. no byte-identical public input against any prior v1.3 population;
6. layout digests differ between the two layouts.

Disjointness from the spent and sealed populations is verified by construction
-- distinct split label, distinct layout indices, and the split-and-layout
embedding in every source episode id -- exactly as
`CONFIRMATION_V1_3_1_DUPLICATION_CHECKS.json` records it, and never by opening
them.

### 13.4 Freeze timing -- strict order, each step's hashes recorded before the next

1. development schedule complete; development report written and hashed;
   `MODEL_CONDITION.json` frozen and hashed; the condition's implementation
   frozen and hashed;
2. the separate post-development authorization (section 14.2) exists and names
   those hashes;
3. `CONFIRMATION_MODEL_FREEZE_RECORD.json` restating this section's parameters
   and naming those hashes;
4. generation, conversion, independent certification, answerability validation,
   firewall validation, and the section-8.2 S-3 gold-adequacy check, in that
   order, in an isolated process emitting only aggregate pass/fail counts and
   hashes;
5. the 56 model calls;
6. scoring, the primary endpoint, the supporting gates, the error-propagation
   classification;
7. seal.

Any deviation from this order spends the population.

### 13.5 Isolation and custodian

Generation and validation run in an isolated process whose working directory
contains no development response, no development score, and no development
report. The custodian who seals is distinct from whoever ran development where
staffing permits; where it does not, the requirement is satisfied by the freeze
ordering in 13.4, which freezes and publishes the condition's hashes before
generation begins. That ordering is required in either case.

### 13.6 One call per case, and no case replacement

One call per case. A failing case is not replaced, repaired, regenerated,
excluded or reweighted. A failed confirmation spends the population for this
condition and every derivative of it. A later condition requires a further new
population under this same protocol at the next listed layout pair, and its own
decision.

### 13.7 Gold-adequacy is a blocker, not a fallback trigger

If the generated confirmation population fails S-3 -- in particular if any
canonical gold choice set `G_i` equals the entire legal target set `L_i` -- that
is an **instrument-validity blocker**, not an automatic preservation success and
not a trigger to advance to the next layout pair. Advancing on a content-derived
property would be selecting a population by inspecting its content, which
sections 13.2 and 13.3 forbid. Execution stops, the blocker is recorded, the
population is spent, and new authority is requested. The mechanical default for
the implementation agent is therefore **stop and record**; it requires no
choice. (Flagged in `OPEN_RESEARCH_DECISIONS.md` item O-4 for Astra's explicit
confirmation.)

### 13.8 The confirmation gate set

Evaluated in the section-8 validity precedence, on the sealed
`confirmation_model_v1_3_1` population, one call per case, once.

| # | Item | Requirement |
| --- | --- | --- |
| 1 | Frozen-manifest integrity, access ledger, accounting, spend | as section 12 items 1--3, against the confirmation freeze record |
| 2 | Schedule completeness | 56 logical calls attempted; no case skipped, added, reordered or replaced |
| 3 | Answerability, firewall | `pass`, zero failures |
| 4 | Gold-adequacy (S-3) | frozen gate met on gold, and `G_i != L_i` for all 8 canonical sources; failure is a blocker, section 13.7 |
| 5 | Mechanical validity (S-4, S-5, S-6) | `>= 0.99`, `= 1.00`, `= 0` |
| 6 | Effect self-consistency (S-7) | **`diagnostic_only`** -- measured, reported, violations enumerated; **not a gate**, and excluded from the confirmation gated item set by the same structural guarantee as section 12.1 |
| 7 | Semantic layers (S-8, S-9, S-10) | `>= 0.65`/`>= 0.50`, `>= 0.60`/`>= 0.50`, `>= 0.60`/`>= 0.50` |
| 8 | Absolute model-conditioned B-1 (S-11) | top-1 `>= 0.60`, top-2 `>= 0.80`, regret `<= 0.35` |
| 9 | Non-degeneracy (S-12) | ND-1/ND-2/ND-3 computed and recorded |
| 10 | Paired degradation (S-13) | top-1 decline `<= 0.125`, top-2 decline `<= 0.125`, mean positive excess regret `<= 0.05` |
| 11 | Own-selection equivariance (S-14) | **40/40** |
| 12 | Directional-effect continuity (S-15) | precision `>= 0.60`, recall `>= 0.50`, cross-variant axis only (confirmation has one repeat, so the cross-repeat axis is empty and is recorded `NA`, which cannot clear a threshold and is therefore excluded from the micro aggregate rather than counted as a pass) |
| 13 | **Primary** | choice-set preservation `>= 7/8` canonical sources |
| 14 | Reported, never gating | argmax-set equality, evaluator-canonical selected-target agreement, top-two-set agreement, tie dependence, the `B1` null, the `longest_artifact` read-out, the error-propagation classes, the `D1`--`D3` substitutions |

Every threshold here is a prospective engineering advancement screen over eight
source instances. None is a population estimate, and none acquires that status
by being applied to a confirmation split rather than a development split.

---

## 14. Inference-authorization boundary

### 14.1 What acceptance of this document authorizes

If -- and only if -- a Sol/Astra decision accepts this document and appends
proposed ADR-0023, it authorizes:

- the section-9 zero-inference model-condition verification;
- freezing `MODEL_CONDITION.json`, `COST_GATE.json`,
  `FROZEN_INPUTS_MODEL_V1_3_1.json` and `FREEZE_CHECKLIST.md`;
- building the condition's runner, audited reader, scorer wiring, and tests;
- **development inference only**: the 112 logical calls of section 7 against the
  existing v1.3 development population, within the section-11 retry, accounting
  and spend policy;
- scoring, the section-12 eligibility checklist, the error-propagation analysis,
  and the development report, whatever the outcome;
- writing blocker records.

### 14.2 What requires a separate later authorization

Generation of, access to, and inference on the confirmation population each
require a **separate post-development authorization** that names, by hash:

1. the frozen implementation (the condition's runner/harness module set);
2. the frozen development report;
3. the frozen `MODEL_CONDITION.json`;
4. the frozen `FROZEN_INPUTS_MODEL_V1_3_1.json` manifest.

No confirmation path may be created, listed for content, opened or called before
that authorization exists and is recorded in the confirmation access ledger.

### 14.3 What is never authorized by this document, under any outcome

Model comparison; automatic or manual escalation after failure; prompt search or
any prompt change; self-critique, voting, multi-sample selection, or few-shot
examples; semantic-response repair or any retry of a valid-but-wrong response;
reuse, reopening, resampling, counting or characterization of `confirmation_v1_3`
or `confirmation_v1_3_1`; generating a second confirmation population for this
condition after a failure; replacing, repairing, excluding or reweighting a
confirmation case; any change to B-1, the fixed adapter, the historical
estimator, any v1.3 semantic rule, prompt, schema, population, threshold,
usefulness target, tie rule or transformation; reducing the frozen schedule to
fit the spend ceiling; inventing a statistical null threshold for choice-set
preservation; editing any artifact under
`experiments/authzgym_semantic_contract_v1_3/`,
`experiments/authzgym_estimator_repair_v1_3_1/` or
`experiments/authzgym_confirmation_v1_3_1/`; reinterpreting the historical
estimator's preserved fresh-confirmation failure; rewriting a historical seal to
match section 5's convention; closed-loop routing, Jev, representation
intervention, graph policies, coupling operators, architecture comparison, IDS
import, or real GitLab integration; promotion of any concept; creation of any
`E-*` record; or any edit to `state/STATUS.yaml`, `plan/ROADMAP.md`,
`CHARTER.md`, `MAP.md`, `DECISIONS.md` or `theory/` other than the prospective
corrections proposed ADR-0023 item D10 explicitly authorizes.

### 14.4 Stop rather than choose

If any step would require choosing a new label meaning, syntax rule,
transformation, threshold, population rule, access condition, retry semantics,
denominator, or interpretation that this document does not already fix, the
implementation **stops and records the contradiction**. It does not choose, does
not pick the reading that improves a number, and does not ask a later step to
decide. This mirrors the AGENTS.md AuthzGym workflow gate and is not waivable.

---

## 15. Interpretation table -- fixed in advance

The outcome label is chosen by this table, not by narrative after the fact. The
first row whose condition holds, in order, is the outcome.

| # | Condition | Outcome label | Meaning |
| --- | --- | --- | --- |
| 1 | Frozen-manifest integrity, access, accounting or spend violation | `invalid` | The schedule is not a measurement. No semantic or downstream number may be reported as a result; raw transport observations may be reported as scoped implementation facts. |
| 2 | Identity drift (section 9.4 step 13) | `invalid_identity_drift` | The frozen condition was not the condition that answered. Same reporting restriction. |
| 3 | Answerability, firewall, or S-3 gold-adequacy failure on a population used | `instrument_blocked` | The instrument, not the model, is unmeasurable on that population. No model attribution of any kind is permitted. Record and stop. |
| 4 | S-4 or S-5 mechanical floor missed on an integrity-valid schedule | `contract_unstable` | The wire/response contract did not hold for this configuration. Semantic numbers are descriptive partial diagnostics only and cannot satisfy any screen. |
| 5 | Mechanical floors met; one or more of S-6, S-8, S-9, S-10, S-11, S-12, S-13, S-14, S-15 fails. **S-7 is excluded from this row by its `diagnostic_only` disposition and can never trigger it** | `semantic_screen_below_threshold` | The model did not produce enough valid v1.3 semantic information under the frozen screens. The primary endpoint is reported but carries no downstream claim, because the frozen precedence blocks a downstream claim behind a semantic-layer failure. |
| 6 | All supporting gates met; primary `< 7/8` | `decision_preservation_below_screen` | Valid semantics, insufficient decision preservation. A clean negative result about this configuration on this population. |
| 7 | All supporting gates met; primary `>= 7/8`; development split | `development_eligible` | Eligible for confirmation under section 14.2. Not a result. |
| 8 | All supporting gates met; primary `>= 7/8`; confirmation split | `bounded_model_semantic_compatibility_confirmed` | The claim of section 16.1, and nothing more. |

Artifact classifier for any outcome: `model_semantic_compatibility_diagnostic`.
It is not an `E-*` evidence record.

**S-7 violations are preserved in every label.** Whichever row matches, the
outcome record carries `effect_self_consistency` with `C_response`, `C_field`,
the per-split and per-repeat breakdowns, and the full violation enumeration, and
the label is rendered with the suffix `(S-7 violations: <count>)` whenever the
count is non-zero. A `development_eligible` or
`bounded_model_semantic_compatibility_confirmed` outcome reached with S-7
violations present is reported with those violations visible in the same record
and in the report's summary paragraph. They qualify how the result is read; they
do not change which row matched, and they never suppress the primary or
downstream result.

---

## 16. Prior-result and claim boundary

### 16.1 What a pass establishes -- quote in this form

> Under the fixed, frozen AuthzGym v1.3 instrument and the frozen
> `est-repair-v1.3.1-B-1` decision component, one frozen inexpensive model
> configuration reading the current source artifact produced, on an untouched
> confirmation population of eight canonical source instances in this controlled
> generator, enough valid v1.3 semantic information for the component's choice
> set to remain a non-empty subset of the gold choice set on at least seven of
> eight sources, while meeting every preregistered supporting gate.

That is bounded compatibility of
`source artifact -> this model/configuration -> v1.3 semantics -> frozen B-1`
inside this controlled generator.

### 16.2 What a pass must never be described as

Authorization competence; general code understanding; closed-loop routing;
adaptive-routing advantage; SER architecture superiority or any comparison
against ReAct, fixed-order, monolithic or ordinary-agent baselines; GitLab
transfer or transfer to any real repository; real-world action value; validation
of the usefulness target, the instrument or the benchmark; a diagnosis of the
historical estimator's preserved confirmation failure; evidence about any model
other than this exact configuration; evidence about any fixture family other
than this generator; or grounds to promote any hypothesis or change any concept
maturity.

### 16.3 Prior results this condition does not touch

V1.2 artifacts and their corrigendum; `authzgym_transport_envelope_v1`'s
transport facts; `authzgym_stronger_model_v1`'s futility stop;
`authzgym_semantic_bottleneck_v1`'s answerability localization; the historical
estimator's development pass and fresh-confirmation failure; the
`est-repair-v1.3.1` development report and its `estimator-only-change-sufficient`
label, which continues to read as sufficiency **with the adapter arm untested**;
and the sealed B-1 successor confirmation. None is rescored, re-aggregated,
reinterpreted or averaged with anything produced here.

### 16.4 Effects, again

Candidate effects are deterministic consequences of facts. They are never
counted as a second, independent semantic-capability signal, in any table, in
any summary, in any abstract.

---

## 17. Closed-loop boundary

A clean untouched-confirmation pass makes closed-loop **experimental design**
the next research task. It does **not** authorize closed-loop execution.

A later closed-loop study requires its own decision and preregistration and must
separately establish, before it may claim anything:

- public accumulation and update of multiple observations;
- useful-action validity at later decision states, not only at the first;
- public-information-only handling of B-1 ties;
- budgets and stopping rules;
- matched open-loop controls;
- evidence that observations actually alter the preferred next inspection.

**Do not assume `longest_artifact` adequacy.** The recorded read-outs warn
against it explicitly: the historical estimator's development `longest_artifact`
read-out is top-1 `0.125` / top-2 `0.375` / regret `0.658333`, and B-1's on the
sealed confirmation is top-1 `0.25` / top-2 `0.25` / regret `0.600000`. A second
decision state reached by inspecting the longest artifact is not established to
be informative, and this condition produces no evidence that it is.

---

## 18. Required artifacts before any model call

All present, hash-frozen under section 5's convention, and listed in
`FROZEN_INPUTS_MODEL_V1_3_1.json` with the repository commit and dirty status:

- this preregistration and the appended ADR-0023;
- `OPEN_RESEARCH_DECISIONS.md` with every item resolved, item O-6 recording the `diagnostic_only` adjudication now written into sections 8, 8.2, 8.6, 12, 12.1, 13.8 and 15;
- `MODEL_CONDITION_VERIFICATION.json`, `MODEL_CATALOG_SNAPSHOT.json`,
  `MODEL_CONDITION.json`, `COST_GATE.json`;
- `RESTATED_HASHES.json`;
- by-hash references to every inherited v1.3 input: `PUBLIC_CONTRACT.json`, the
  prompt, the vocabulary and response schemas, the fixture generator and
  converter, the development public and restricted populations, the
  transformation maps, the schedule, the independent annotations and
  certificates, `ANSWERABILITY_VALIDATION.json`, `FIREWALL_VALIDATION.json`, and
  the development block of `ORACLE_VALIDATION.json`;
- by-hash references to `policies_v1_3_1.py`, `DEVELOPMENT_REPORT.md`, and
  `experiments/authzgym_confirmation_v1_3_1/CONFIRMATION_V1_3_1_ORACLE_VALIDATION.json`
  and `CONFIRMATION_V1_3_1_SEAL.json`;
- the condition's own runner, audited reader, harness wiring and tests, hashed;
- `GOLD_ADEQUACY_DEVELOPMENT.json` (S-3 on the development population);
- `FREEZE_CHECKLIST.md`, every item checked, with reviewer and date fields.

Until every item is present and matched, the only authorized work is offline
implementation, test, validation, documentation and freezing.
