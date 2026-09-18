# AuthzGym semantic contract v1.3 preregistration

Status: `accepted_semantics_implementation_and_freeze_pending`

Decision authority: ADR-0019

Date accepted: 2026-09-18

This document freezes the research semantics and the implementation acceptance
rules for AuthzGym v1.3. It does **not** authorize model/provider inference.
Implementation-generated populations and hashes must be appended through the
artifacts named below; this document must not be edited in response to their
outcomes. If an implementation reveals a direct contradiction, stop and record
the blocker. Do not choose a new meaning in code.

## 1. Scope and non-claims

V1.3 is a new measurement instrument, not a repaired-in-place v1.2. It measures
bounded extraction of published source-local authorization facts, deterministic
classification of their local candidate cues, and visible unresolved calls to
uninspected public inventory definitions. It also supplies a downstream
compatibility diagnostic to the unchanged deterministic action-value estimator.

It does not measure complete vulnerability diagnosis, execution behavior,
causality, posterior belief, general Python understanding, semantic memory,
architecture advantage, or broad authorization competence. It does not test
Jev, a representation intervention, a new routing architecture, a graph,
coupling operators, GitLab, IDS, or active testing.

V1.2 artifacts remain immutable. V1.3 scores are not directly numerically
comparable with v1.2 model scores.

## 2. Versioned public request and response

The semantic interface identifier is
`authzgym_semantic_observation_v1_3`. A request consists of the frozen system
instruction plus exactly this user-payload shape:

```json
{
  "semantic_interface": "authzgym_semantic_observation_v1_3",
  "instruction_scope": "current_artifact_only",
  "current_artifact": {
    "slot": 0,
    "public_id": "opaque string",
    "path": "opaque string",
    "source": "complete fixture module source"
  },
  "candidate_hypotheses": [
    {
      "slot": "c0",
      "public_label": "opaque string",
      "effect_family": "ownership|membership|role|context",
      "description": "public candidate description"
    }
  ],
  "public_artifact_inventory": [
    {
      "slot": 0,
      "public_id": "opaque string",
      "path": "opaque string",
      "exported_symbols": ["public symbol"],
      "line_count": 1,
      "inspection_status": "current|uninspected"
    }
  ],
  "legal_uninspected_target_slots": [1, 2, 3, 4, 5]
}
```

Required input invariants:

- There are exactly four candidates and exactly one of each `effect_family`.
- Candidate slots are exactly `c0` through `c3`, in array order. Public labels
  are addressing data only. The family and description are semantic.
- The current artifact is present exactly once in the inventory and has
  `inspection_status=current`; every other inventory item is `uninspected`.
- `legal_uninspected_target_slots` equals the set of all and only uninspected
  inventory slots. Each such artifact exports exactly one symbol.
- The current source is complete for the fixture module. There is no prior
  semantic history and no `current_epistemic_summary`, `facts_seen`,
  `candidate_support`, prior observation, or oracle-derived state.
- `public_id`, `path`, opaque candidate label, and inventory order have no
  semantic meaning except addressing. Exported symbols are semantic only for
  binding a visible call to a public target; their spelling is excluded from
  relation-category classification.

The four candidate descriptions remain:

| Family | Description |
| --- | --- |
| ownership | An ownership assumption differs between authorization layers or entry paths. |
| membership | Direct and inherited membership are treated inconsistently. |
| role | A propagated or transformed role differs between layers. |
| context | Token scope or request context is lost or checked inconsistently. |

The strict response has exactly three top-level objects and no prose or extra
properties:

```json
{
  "facts": {
    "f0": false, "f1": false, "f2": false, "f3": false,
    "f4": false, "f5": false, "f6": false, "f7": false,
    "f8": false, "f9": false, "f10": false, "f11": false,
    "f12": false, "f13": false, "f14": false, "f15": false,
    "f16": false
  },
  "candidate_effects": {
    "c0": "support|contradict|neutral|unknown",
    "c1": "support|contradict|neutral|unknown",
    "c2": "support|contradict|neutral|unknown",
    "c3": "support|contradict|neutral|unknown"
  },
  "unresolved_targets": {
    "t1": {"r0": false, "r1": false, "r2": false, "r3": false, "r4": false}
  }
}
```

`facts` contains exactly f0--f16. `candidate_effects` contains the four
candidate slots. `unresolved_targets` contains exactly one `tN` property for
each legal uninspected target slot and each target contains exactly r0--r4.
Booleans must be JSON booleans. Effect strings must be exact enum members.

## 3. Public fixture/API legend

The fixture language is the frozen authored Python subset produced by the v1.3
fixture generator. It is inspected statically; calls are not executed. The
following names and forms have published meanings:

- `membership_store.lookup(...)` is the membership lookup API.
- A call to a public inventory export with membership keywords is also a
  membership-relevant call at the current source boundary.
- `role_map.get(source_role, fallback_role)` is the role transformation API.
- `authorize(...)` is the local authorization API. Calls to public inventory
  exports may also carry authorization arguments.
- `apply_change(actor, item)` is the designated sensitive-change API.
- `actor.owner_id == item.owner_id` is the only ownership-guard form.
- `request.channel == "alternate"` is the only alternate-channel predicate.
- `audit_record = (<category literal>, <value>)` is the only audit-record form.
- The fixed `normalize_*`, `combine_*`, and `stable_*` helper productions are
  neutral padding. They never establish a fact or relation.
- An inventory export is defined by `public_artifact_inventory`. A visible call
  binds only by exact exported-symbol equality after parsing, never by substring.

Comments, filenames, public IDs, candidate labels, callee spelling, helper-name
suffixes, ordering, and hidden logical roles do not establish facts. A string or
identifier outside the productions below does not establish a fact merely
because it contains a keyword.

The independent checker must parse the source with Python's AST and match these
productions. Raw unrestricted substring matching is non-conforming.

## 4. Normative fact semantics

All facts are source-local. A fact is true if at least one matching production
occurs in the complete current source and false only after exhaustive inspection
of that source under the published grammar.

| Slot | Stable name | Exact public rule |
| --- | --- | --- |
| f0 | `alternate-entry` | An `if` test is exactly `request.channel == "alternate"`. The branch need not be executed. |
| f1 | `direct-only-membership` | A membership API call or public-export call has keyword `direct_only=True`. |
| f2 | `inherited-membership-included` | A membership API call or public-export call has keyword `include_inherited=True`. |
| f3 | `role-fallback` | At least one of: a function declares `fallback_role` with a non-`None` default; a call supplies keyword `fallback_role`; or `role_map.get` uses `fallback_role` as its default argument. |
| f4 | `role-map-transform` | The source contains the exact assignment `propagated_role = role_map.get(source_role, fallback_role)`. |
| f5 | `role-preserved` | The source contains the direct assignment `propagated_role = source_role`. |
| f6 | `missing-token-scope` | `authorize` or a public-export call supplies keyword `token_scope=None`. |
| f7 | `missing-feature-context` | `authorize` or a public-export call supplies keyword `feature_context={}` with an empty literal dictionary. |
| f8 | `token-scope-forwarded` | `authorize` or a public-export call supplies keyword `token_scope` with exactly `token_scope` or `request.token.scope`. |
| f9 | `feature-context-forwarded` | `authorize` or a public-export call supplies keyword `feature_context` with exactly `feature_context` or `request.flags`. |
| f10 | `sensitive-without-owner-check` | A call to `apply_change(actor, item)` is not syntactically control-dependent on an enclosing `if actor.owner_id == item.owner_id` in the same function. |
| f11 | `ownership-compared` | A call to `apply_change(actor, item)` is syntactically inside the body of an enclosing `if actor.owner_id == item.owner_id` in the same function. |
| f12 | `weak-ownership-audit` | The value assigned to `audit_record` contains the exact string literal `"owner"` or `"ownership"`. |
| f13 | `weak-membership-audit` | The value assigned to `audit_record` contains the exact string literal `"membership"`. |
| f14 | `weak-role-audit` | The value assigned to `audit_record` contains the exact string literal `"role"`. |
| f15 | `weak-context-audit` | The value assigned to `audit_record` contains the exact string literal `"context"`. |
| f16 | `cross-artifact-call` | The current source contains a call whose simple callee name exactly equals an exported symbol of another public-inventory artifact. This establishes only the call, not callee behavior. |

F10 and f11 are independently evaluated and may both be true if separate
sensitive calls satisfy their respective rules. F12--f15 describe audit text,
not enforcement. F16 does not inherit any property of the unseen target.

### Retired-slot crosswalk

Retired slots do not appear in the v1.3 schema and are not reassigned.

| V1.2 slot | Former meaning | V1.3 disposition |
| --- | --- | --- |
| f17 | alternate entry bypasses the standard ownership guard | Retired as a cross-artifact/role-dependent conclusion. F0 and f10 remain separate local observations; they are not automatically combined. |
| f18 | inherited membership is omitted | Retired. F1 records an explicit direct-only request and f2 records explicit inclusion; absence of f2 is not scored as omission. |
| f19 | guard loses token scope or request context | Retired as a cross-layer conclusion. F6 and f7 record only explicit local arguments. |
| f20 | test code relates an expectation to implementation behavior | Retired because test role is hidden and the source does not identify a privileged implementation target. |
| f21 | ownership behavior expected by a test | Retired; no role-dependent replacement. |
| f22 | membership behavior expected by a test | Retired; no role-dependent replacement. |
| f23 | role propagation behavior expected by a test | Retired; no role-dependent replacement. |
| f24 | token/context behavior expected by a test | Retired; no role-dependent replacement. |

No hidden logical role is added to normal input to preserve a retired label.

## 5. Candidate-effect rule

Candidate effects are a deterministic public local-cue classification, not a
posterior, causal conclusion, proof of the complete candidate, or independent
capability target.

| Candidate family | Support cues | Counter-cues |
| --- | --- | --- |
| ownership | f10 | f11 |
| membership | f1 | f2 |
| role | f3 or f4 | f5 |
| context | f6 or f7 | f8 or f9 |

For each candidate, let `S` mean that at least one support cue is true and `C`
mean that at least one counter-cue is true. Duplicate cues do not vote.

- `S` and not `C` -> `support`.
- `C` and not `S` -> `contradict`.
- `S` and `C` -> `neutral`, meaning mixed local cues.
- neither -> `unknown`, meaning no directional cue under this rubric.

F0 and f12--f16 have no effect polarity. Gold effects are computed from the
gold retained-fact vector. A response's effects must also equal the same
function applied to its submitted fact vector. Gold-effect agreement and
self-consistency are reported separately. Effects never count as evidence
independent of facts.

## 6. Unresolved-target rule

Relation slots are:

| Slot | Category |
| --- | --- |
| r0 | ownership |
| r1 | membership |
| r2 | role |
| r3 | context |
| r4 | general dependency |

A target is eligible only when its slot is listed in
`legal_uninspected_target_slots`. For every AST call whose simple callee exactly
matches that target's sole exported symbol, classify the call once as follows:

1. Remove the callee node. Collect lower-case identifier components from
   positional arguments, keyword names, and keyword values. Attribute chains are
   split into their identifier components. String literals in arguments are
   collected as lower-case whole tokens. Other literal values contribute no cue.
2. Apply the first matching category in this exact precedence:
   - ownership: a collected token contains `owner` or `alternate`;
   - membership: a token contains `member`, `group`, or `inherited`, or equals
     `direct_only` or `include_inherited`;
   - role: a token contains `role`;
   - context: a token contains `token`, `context`, `flags`, or `request`;
   - general dependency: no preceding cue matched.
3. Set the corresponding target/category Boolean true. All others remain false.

The opaque callee name, public ID, path, inventory position, and hidden role are
never category cues. One call receives exactly one category. Multiple calls to
the same target may therefore make multiple target categories true. The output
states only that the current source visibly calls an uninspected definition in
that public call context; it does not assert the target's behavior.

## 7. Unsupported or ambiguous source

The population converter and answerability checker fail closed. A case is
ineligible if parsing fails; a target does not have exactly one exported symbol;
binding is ambiguous; a relevant production uses an unlisted equivalent form;
the current source is incomplete; source-span certification is impossible; or
two conforming independent derivations disagree. Ineligible cases are not sent
to a model and are not repaired case by case inside the frozen version.

An unsupported form is not labeled false. It blocks the case. A population with
any blocked scheduled case fails the pre-inference answerability gate.

## 8. Transformations and development population

The development source population is exactly the eight frozen v1.1 development
source instances: two source layouts for each of the four existing mechanism
families. Conversion reads source and public descriptors, discards v1.2
`expected_fact_keys` and summaries, and derives v1.3 gold only through the
independent process in section 9.

Each source produces exactly seven cases in this order:

1. `base_entry`: current artifact is the entry artifact; original inventory,
   identifiers, symbols, candidate order, and labels.
2. `longest_artifact`: current artifact is the unique artifact with greatest
   declared line count. A tie blocks conversion.
3. `artifact_reordering`: same current entry and source; keep the current entry
   first and reverse every other inventory item. Remap target slots only.
4. `symbol_renaming`: same order and current artifact; apply a deterministic
   bijection to every exported symbol and every exact source reference to it.
   Local non-export identifiers are unchanged.
5. `candidate_label_renaming`: same order and current artifact; replace only
   opaque public candidate labels through a deterministic bijection. Candidate
   slots, order, family, and description are unchanged. This does not test
   candidate-order sensitivity.
6. `artifact_identifier_variation`: same order, source semantics, and symbols;
   apply deterministic bijections to public artifact IDs and paths.
7. `combined_permutation`: compose identifier/path and symbol renaming, keep the
   current entry first while reversing other inventory items, reverse candidate
   order, assign new opaque candidate labels, and remap all slots and gold by the
   recorded bijections. It is the only retained variant that changes candidate
   order.

The five cases 3--7 are semantic-equivalence transformations of `base_entry`.
`longest_artifact` is a different source-local question and is not an
equivalence pair. All bijections are derived by SHA-256 from the source episode
ID, variant ID, and original public token; collision is a blocking conversion
failure. The conversion manifest records forward and inverse maps in the
restricted validation channel, not in normal input.

The result is 8 sources x 7 cases = 56 development cases. Each case is called
twice with an identical byte request, `repeat=1` then `repeat=2`, producing 112
scheduled calls. Schedule order is source-manifest order, then the seven variant
orders above, then repeat 1 and repeat 2. Each case has weight 1/56 after its two
repeats are averaged; each repeat has weight 1/2 within case. Source-, variant-,
and family-level reports are mandatory. Transformations and repeats are
dependent stress observations, not independent research samples.

There is no semantic-performance futility stop in v1.3 development. All 112
calls complete unless a preregistered integrity, transport, mechanical-validity,
or spend stop fires. The v1.2 16/32 optimistic futility rule is retired because
the label universe and denominators changed. It must not be copied or adapted
after observing v1.3 responses.

## 9. Independent answerability validator

### Inputs and isolation

The validator may read only:

- the frozen v1.3 public contract and fixture grammar;
- the public request bundle and response schema;
- an independently authored source-span annotation/certificate file;
- Python standard-library parsing, JSON, and hashing facilities; and
- generic, semantics-free canonical serialization code.

It must not import or call v1.2 or v1.3 scorer/gold/oracle helpers,
`oracle_content`, `expected_fact_keys`, logical roles, mechanism IDs,
usefulness, correct conclusions, action rankings, or any evaluator annotation
other than the independent certificates being checked. It must not import the
production label generator. The public-only checker and production scorer must
be separately implemented and must not share a label-producing function,
constant mapping module, generated label table, or fixture-role dispatch.

Run the public checker in a process whose input directory contains no restricted
case data. Its complete output becomes the independently derived label vector;
the production evaluator's source-grounded annotation is compared only after
both are complete.

### Evidence certificates

Every fact Boolean and target/category Boolean has a certificate containing:

- case ID, public-input SHA-256, label path, Boolean value, public rule ID;
- for a positive label, exact 1-based source line/column span(s) and normalized
  AST production(s) witnessing it;
- for a negative label, the complete inspected scope, source hash, enumerated
  relevant AST node kinds/call sites, and a statement that no witness matched;
- checker version/hash and annotation version/hash.

Every effect certificate lists the candidate slot/family, the retained fact
vector hash, support/counter cue Booleans, and the deterministic truth table row.
Negative absence is valid only because the complete fixture module is present
and the checker exhausts the declared bounded grammar.

### Required checks

1. Public-input-only derivation reproduces every fact, effect, and relation.
2. Independent annotations and checker outputs agree exactly for every label.
3. Mutating hidden roles, mechanisms, usefulness, correct conclusions, old
   expected tags, oracle values, or restricted metadata while public bytes stay
   fixed cannot change any derived target.
4. Each authorized transformation preserves the mapped base answer exactly;
   longest-artifact answers are independently certified.
5. Every scheduled case has complete positive and negative certificates and no
   unsupported or ambiguous syntax.
6. Repeated validator execution is byte-identical.

Acceptance requires 100% case coverage, 100% label agreement, 100%
transformation consistency for cases 3--7, zero hidden-data dependencies, zero
unsupported forms, and byte-identical replay. Any failure blocks population
freeze and all inference. It is never resolved by choosing the scorer's answer
or the answer that improves model performance.

## 10. Firewall validation

For fixed authorized public input, fixed controller/model output, fixed public
configuration, and fixed controller randomness, changing evaluator-only data
must not change normal input, response schema, controller-visible state, action
interface, action-value input, public trace, or any normal-channel metadata.

The test suite must include:

- individual and all-at-once mutations of hidden roles, mechanism family,
  source annotations, fact/effect/relation gold, usefulness, conclusion, oracle
  ranks/values, certificates, and old v1.2 expected tags;
- static import/dependency checks plus runtime provenance/taint records for every
  normal-visible field;
- byte-identical public-only replay from a bundle containing no restricted
  files or evaluator modules;
- a spy assertion that normal initial state is empty and no oracle/gold helper
  is called to construct prior state or model-conditioned diagnostics;
- separate normal and oracle entry points, stores, trace namespaces, and output
  types; the normal entry point must reject oracle arguments and the oracle
  diagnostic must be incapable of writing a normal trace;
- mutation of oracle diagnostic output with proof that normal replay remains
  byte-identical; and
- checks of identifiers, ordering, counts, schemas, errors, hashes, timestamps,
  and missingness, not only field names.

A blocking firewall failure is any normal-byte change under restricted-field
mutation, any normal field without public/controller provenance, any import or
reachable reference that permits restricted access, any oracle-derived initial
or prior state, any inability to run public-only replay, any shared writable
normal/oracle cache, or any undeclared information-dependent error/ordering
channel. Zero failures are required before population freeze and inference.

## 11. Confirmation construction and access

Development code, certificates, validators, thresholds, transformations,
scoring, and the unchanged-estimator adapter are frozen before confirmation
conversion. Confirmation contains eight source instances, two per existing
family, and the same seven variants, for 56 cases. Confirmation uses one call
per case and has no repeat-based tuning. It is a new v1.3 freeze even if its
underlying source instances are reused.

### Conditional reuse of existing source instances

Reuse is allowed only when `CONFIRMATION_ELIGIBILITY.json` records all of:

1. the prior source-population hash and evidence that provider/model calls equal
   zero for every source instance;
2. a chronological access ledger from the start of v1.3 repair through semantic,
   code, test, and threshold freeze;
3. signed human/agent declarations that no case-specific source, ordering,
   identifiers, candidates, gold, usefulness, certificate, or oracle output was
   inspected or used to choose or revise v1.3 rules;
4. proof that all repair decisions cite only repository authority, common
   generator templates, v1.2 public semantics, and exposed development data;
5. hashes showing conversion code and all gates were frozen before a tool first
   opened confirmation case content; and
6. a content-blind pre-freeze metadata transcript containing only permitted
   fields.

Before freeze, permitted confirmation metadata is limited to path, byte size,
file SHA-256, schema version, declared split, record/case/schedule counts,
population hash, freeze timestamp, generator commit/hash, aggregate planned
family counts, provider-call count, and the already published aggregate
v1.2 oracle top-1/top-2/regret result with its pre-repair artifact hash. That
aggregate may be recorded but not recomputed, expanded, or inspected per case.
Source text, ASTs, artifact/candidate order or identifiers, case IDs, gold,
usefulness, conclusions, certificates, and case-level oracle outputs are
prohibited.

After freeze, an isolated converter may read the sources, construct v1.3 cases,
run answerability/firewall/oracle checks, and reveal only pass/fail counts and
hashes until the confirmation manifest is sealed. A failure is recorded; it
does not authorize case-specific repair.

If any required record is absent, any prohibited field was exposed, or
case-specific confirmation content influenced repair, reuse is forbidden. The
mandatory fallback is a fresh population made by the unchanged frozen authoring
method with split `confirmation_v1_3` and layout indices 40 and 41, four
families per layout, before inspecting generated content. The same isolated
conversion and validation rules apply. Changing only opaque identifiers is not
freshness.

## 12. Hashes and manifests

All JSON is hashed as UTF-8 canonical JSON with sorted keys, no insignificant
whitespace, and finite JSON primitives. Text files are hashed as exact UTF-8
bytes with LF endings. SHA-256 is used throughout.

`FROZEN_INPUTS.json` must map logical paths to file hashes and include hashes for
this preregistration, ADR-0019, the public contract/vocabulary, prompt, schema
generator and generated schemas, fixture generator/converter, transformation
maps, public populations, restricted annotations/gold, certificates,
answerability validator, firewall validator, scorer, unchanged estimator and
adapter, schedules, model/transport configuration, confirmation-eligibility
record, and every validation result. It also records the Git commit and dirty
status. The manifest hash is computed with its own `manifest_sha256` field
omitted, then stored in that field. Any later byte change requires a new version;
no model call may use a mismatched manifest.

Public and restricted bundles have separate manifests. Normal execution mounts
only the public bundle. The evaluator opens the restricted bundle only through
the separate scoring/oracle channel.

## 13. Scoring and reporting

Only structurally valid responses enter semantic diagnostics. Missing or invalid
calls are never imputed as false labels. If the full schedule is incomplete or
post-retry validity is below 1.00, semantic numbers may be reported only as
descriptive partial diagnostics and cannot satisfy the capability screen.

### Semantic layers

- Facts: micro TP/FP/FN, precision, recall, F1, exact 17-bit vector accuracy,
  per-slot confusion, per-case, per-variant, per-source, and per-family results.
- Effects: four-way accuracy/confusion, deterministic self-consistency against
  the submitted fact vector, and historical directional precision/recall over
  only `(candidate, support)` and `(candidate, contradict)` items. Effects are
  explicitly non-independent interface diagnostics derived from fact semantics.
- Relations: micro TP/FP/FN, precision, recall, F1, exact target/category-vector
  accuracy, and per-category/target/family reports.

Counts are computed per repeat, averaged across the two repeats for each
development case, then summed across the 56 equal-weight cases. Confirmation
has one record per case. Also report family-macro and source-clustered summaries;
do not treat variants or repeats as independent samples.

For precision `TP/(TP+FP)` and recall `TP/(TP+FN)`, a zero denominator is `NA`,
never 0 or 1. `NA` cannot clear a threshold. A case with no positive gold labels
reports recall `NA`, false-positive count, specificity over its negative slots,
and exact-vector correctness; it still contributes false positives to aggregate
precision. A layer with zero aggregate gold positives makes the population
invalid before inference. Missing responses produce `missing`, not zeros.

### Downstream diagnostic

Map v1.3 ownership/membership/role/context/general relations to the existing
internal tags `ownership_path`, `membership_path`, `role_path`, `context_path`,
and `general_dependency`; map support/contradict/neutral/unknown to
`+1/-1/0/0`. Start from the normal empty epistemic state, add only the current
response, and call the unchanged historical estimator whose source hash is
frozen. No oracle prior state is permitted.

Report top-1, top-2, and normalized regret against evaluator usefulness. Score
ties after mapping artifacts to their canonical source-instance ordinals stored
only in the restricted transformation map; ascending canonical ordinal is the
fixed tie-break and is invariant to public renaming/reordering. With usefulness
`u`, `regret=(max(u)-u(selected))/(max(u)-min(u))`. If all legal targets have
equal usefulness, top-1 and top-2 are true, regret is 0, and the case is marked
`nondiscriminating`; it is reported but excluded from threshold denominators.

### Prospective engineering screens

- fact precision >= 0.65 and recall >= 0.50;
- directional effect precision >= 0.60 and recall >= 0.50;
- relation precision >= 0.60 and recall >= 0.50;
- effect self-consistency = 1.00;
- downstream top-1 >= 0.60, top-2 >= 0.80, and mean normalized regret <= 0.35;
- all mechanical response requirements pass; and
- answerability and firewall failures = 0.

These historical numbers are retained only as prospective engineering
continuity floors. They do not validate broad competence and do not make v1.3
comparable with v1.2. Report all values even when a gate fails.

### Mechanical response validity

The exact schema, no-extra-properties rule, Boolean and enum types, legal target
set, output-token ceiling, finish reason, raw-response hash, retry identity,
attempt count, model identifier, transport outcome, and absence of manual repair
are checked per call. First-attempt schema validity must be at least 0.99;
post-identical-retry validity must equal 1.00; length terminations, incomplete
JSON, illegal references, manual repairs, secret leaks, and schedule/hash/spend
violations must be zero. A population/hash/access/spend violation is `invalid`;
an integrity-valid schedule missing a mechanical floor is `contract_unstable`.

Validity precedence is: frozen-manifest integrity -> answerability -> firewall ->
oracle -> mechanical response -> semantic/interface -> downstream. A failure at
an earlier layer blocks claims at later layers. Transport and raw mechanical
observations may still be reported as scoped implementation facts.

## 14. Oracle validation

Before model inference, feed independently validated v1.3 gold observations for
all canonical development cases and sealed canonical confirmation cases through
the public adapter to the unchanged estimator. Use an empty initial state and no
prior summary. Validate exact adapter mapping, target legality, identity/order
invariance, and action-value/ranking equivalence across cases 3--7 after applying
the recorded transformation maps.

Acceptance requires, separately for development and confirmation canonical
entries, aggregate top-1 >= 0.60, top-2 >= 0.80, and mean normalized regret <=
0.35; zero illegal target/value; and exact transformed action-value equivalence
within absolute tolerance `1e-12`. Per-family values are reported but are not an
additional gate. The estimator source hash must equal the historical frozen
hash; only the mapping stated in section 13 may be new.

If the oracle fails, write `ORACLE_BLOCKER.md` and `ORACLE_VALIDATION.json`, stop,
and leave inference unauthorized. Do not alter weights, scoring, source cases,
gold, or estimator. Any proposed estimator change requires a separate decision,
version, and preregistration.

## 15. Prior-result boundary

The exact v1.2 correction is in `PRIOR_RESULT_CORRIGENDUM.md`. In summary,
transport, response-byte/schema, accounting, cleanup, and observed stopping
events remain valid within their recorded scope. V1.2 semantic aggregates,
futility bounds, and oracle action diagnostics are descriptive/conditional on
the defective scorer. Clean fact/effect capability-floor interpretations are
withdrawn. `contract_stable` continues to describe wire reliability only and no
longer implies a firewall-valid or semantically answerable ordinary condition.

## 16. Required freeze artifacts

Before any model/provider call, the v1.3 directory must contain hash-frozen:

- `PUBLIC_CONTRACT.json`, prompt, vocabulary, and all exact response schemas;
- development and confirmation source/public/restricted manifests;
- transformation maps and schedules;
- independent annotations and evidence certificates;
- `ANSWERABILITY_VALIDATION.json` with full pass;
- `FIREWALL_VALIDATION.json` with full pass;
- `ORACLE_VALIDATION.json` with full pass and unchanged estimator hash;
- `CONFIRMATION_ELIGIBILITY.json` selecting reuse or fresh fallback;
- scorer tests and metric denominator fixtures;
- model, transport, retry, resource, and spend configuration;
- `FROZEN_INPUTS.json` with clean/matched hashes; and
- a copied freeze checklist with every item checked and reviewer/date fields.

Until then, the only authorized work is offline implementation, test,
validation, documentation, and freezing of this instrument.
