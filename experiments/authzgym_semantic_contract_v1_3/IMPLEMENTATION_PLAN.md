# AuthzGym v1.3 mechanical implementation handoff

Status: `ready_for_offline_implementation_no_inference`

Research semantics are frozen by ADR-0019 and `PREREGISTRATION.md`. The ordered
steps below may be executed by DeepSeek without making a research-semantic
choice. If a named rule cannot be implemented literally, stop and record the
contradiction; do not substitute a new rule.

Historical directories `authzgym_static_v1/`, `authzgym_static_v1_1/`,
`authzgym_static_realmodel_v1/`, `authzgym_semantic_contract_v1_2/`,
`authzgym_transport_envelope_v1/`, `authzgym_stronger_model_v1/`, and
`authzgym_semantic_bottleneck_v1/` are read-only inputs. No model/provider call
is authorized by any step in this plan.

## Repository placement and edit policy

| Concern | Authoritative placement | Edit policy |
| --- | --- | --- |
| Accepted v1.3 semantic/governance decision | ADR-0019 in `DECISIONS.md` | Append-only new ADR; do not revise ADR-0015--0018. |
| Exact v1.3 instrument contract | This directory's `PREREGISTRATION.md` | Accepted specification; implementation freeze adds separately hashed artifacts and an append-only freeze record, not result-driven semantic edits. |
| V1.2 interpretation correction | `PRIOR_RESULT_CORRIGENDUM.md`, summarized in `experiments/README.md` | Append-only correction in living documentation; never edit historical experiment reports, responses, or classifiers. |
| Research boundary/non-goals | `CHARTER.md` | Current-state correction after ADR-0019; no change to the general control semantics. |
| Phase cursor and implementation facts | `plan/ROADMAP.md` and `state/STATUS.yaml` | Current-state edits followed by context regeneration. |
| Repository landing-page cursor | `README.md` | Replace stale next-task language with the accepted v1.3 gate. |
| Agent/contributor workflow | `AGENTS.md` | Add the no-inference, independent-validator, firewall, history, and confirmation-access rules. |
| Source authority index | `MAP.md` | Add the v1.3 specification, handoff, and corrigendum roles. |
| Existing concept state | M-013 and H-018 entries in `theory/IDEA_MAP.yaml` | Update references/review notes without changing identity or maturity; regenerate the readable view. |
| Core control semantics/firewall | `theory/CONTROL_PROBLEM.md`, `theory/CONTRACTS.yaml`, `theory/INFORMATION_BOUNDARIES.md` | No edit: ADR-0019 applies existing entitlement and evaluator-separation semantics rather than changing them. |
| Historical evidence | All pre-v1.3 experiment directories | Immutable. |

## Step 1 -- Materialize the frozen public contract

Files/modules:

- create `src/ser/authzgym/v1_3_contract.py`;
- create `experiments/authzgym_semantic_contract_v1_3/PUBLIC_CONTRACT.json`;
- create `experiments/authzgym_semantic_contract_v1_3/prompts/semantic_observation_v1_3.txt`;
- create `experiments/authzgym_semantic_contract_v1_3/schemas/semantic_vocabulary_v1_3.json`;
- add `tests/test_authzgym_v1_3_contract.py`.

Behavior:

- Transcribe sections 2--7 of the preregistration exactly.
- Generate a strict per-case response schema containing only f0--f16, c0--c3,
  r0--r4, and the legal `tN` target properties.
- Parse responses without prose recovery, aliasing, inferred identifiers, or
  manual repair.
- Make public contract JSON the data input; Python code validates/uses it rather
  than defining a second mutable vocabulary.

Tests:

- exact key/type/enum tests; extra/missing keys fail;
- illegal targets fail; legal target set and schema hash are deterministic;
- f17--f24, r5--r8, summaries, roles, usefulness, and conclusions are absent;
- candidate order/label changes do not change family identity.

Acceptance: all tests pass and repeated contract/schema generation is
byte-identical.

Artifacts: public contract, prompt, vocabulary, schema fixtures, hashes.

Untouched: all v1.2 code and artifacts; estimator; core theory contracts.

## Step 2 -- Implement public fixture conversion and transformations

Files/modules:

- create `src/ser/authzgym/v1_3_population.py`;
- create `tools/prepare_authzgym_v1_3.py` with an explicit offline-only guard;
- add `tests/test_authzgym_v1_3_population.py`.

Behavior:

- Read the eight v1.1 development source episodes but ignore
  `expected_fact_keys`, logical roles, usefulness, and conclusions when building
  public cases.
- Emit the seven variants and exact mappings/order from preregistration section
  8, 56 cases, and the 112-call schedule.
- Emit no summary field and no prior artifact slots.
- Derive transformation tokens by the frozen SHA-256 rule and reject collision.
- Store mapping tables only in the restricted validation bundle.

Tests:

- exact counts, source/family balance, schedule order, repeat identity;
- base-to-transform byte differences are limited to authorized mapped fields;
- inverse maps reconstruct base public semantics;
- longest artifact is unique; current/uninspected status is exhaustive;
- public bundle contains no restricted fields or old expected tags.

Acceptance: 56 unique cases, 112 exact schedule entries, all population tests
pass, and two preparations are byte-identical.

Artifacts: `DEVELOPMENT_SOURCE_MANIFEST.json`,
`DEVELOPMENT_PUBLIC_POPULATION.json`, restricted transformation maps, schedule,
and population hash.

Untouched: v1.1 source population bytes; all earlier generated populations.

## Step 3 -- Create independent source annotations and certificates

Files/modules:

- create a data-only
  `experiments/authzgym_semantic_contract_v1_3/annotations/development_annotations.jsonl`;
- create `src/ser/authzgym/v1_3_annotation_schema.py` for structural validation
  only;
- add certificate fixtures and tests in
  `tests/test_authzgym_v1_3_certificates.py`.

Behavior:

- Apply the published rules to public source, recording positive/negative
  certificates for every fact, effect, target, and relation.
- Record line/column spans, normalized AST production, complete negative scope,
  source/public-input hash, and rule ID.
- Do not import generation roles, old expected tags, the production scorer, or
  the independent checker.

Tests:

- every label has exactly one complete certificate record;
- positive spans resolve to the asserted public AST production;
- negative coverage enumerates all relevant nodes/calls;
- certificate/public-input hashes match; no evaluator role/mechanism field is
  present.

Acceptance: complete schema-valid certificates for 56 development cases, with
zero unresolved source spans.

Artifacts: development annotations and certificate manifest.

Untouched: public contract; source cases; old gold arrays.

## Step 4 -- Implement the independent answerability validator

Files/modules:

- create standalone `tools/validate_authzgym_v1_3_answerability.py`;
- do not place its label derivation in `src/ser/evaluation/` or import
  `v1_3_contract.py` label helpers;
- add `tests/test_authzgym_v1_3_answerability.py`.

Behavior:

- Load only the public contract JSON, public cases, and independent certificates.
- Independently parse AST and derive f0--f16, effects, and r0--r4.
- Compare only after both annotations and checker results are complete.
- Run hidden-data mutation, transformation, complete-negative, unsupported-form,
  and deterministic-replay checks from section 9.
- Refuse a filesystem bundle containing restricted population/gold files during
  public derivation.

Tests:

- one mutation test per fact production, effect truth-table row, cue precedence,
  target binding, negative certificate, and unsupported/ambiguous form;
- injected old role/expected tags cannot change output;
- deliberate disagreement fails closed.

Acceptance: every section-9 criterion equals its required value; no skipped or
warning status is accepted.

Artifacts: `ANSWERABILITY_VALIDATION.json`, checker output labels, logs, hashes.

Untouched: production evaluator/scorer; estimator; old validator code.

## Step 5 -- Implement public input assembly and the firewall suite

Files/modules:

- create `src/ser/authzgym/v1_3_public_input.py` with no evaluator imports;
- create `tools/validate_authzgym_v1_3_firewall.py`;
- add `tests/test_authzgym_v1_3_firewall.py`.

Behavior:

- Build normal requests exclusively from the public bundle.
- Start normal state empty and accept only actual response-derived updates.
- Implement every restricted mutation, provenance trace, public-only replay,
  oracle-spy, cache/channel separation, and metadata side-channel test in
  preregistration section 10.
- Normal execution must fail to import/mount restricted data; oracle execution
  uses a separate entry point and output namespace.

Tests:

- byte equality under every individual/all-at-once evaluator mutation;
- normal replay succeeds after restricted bundle and evaluator modules are
  removed from the process path;
- attempted oracle argument/reference/cache access fails;
- no field lacks public/controller provenance.

Acceptance: zero blocking failures and byte-identical replay for all 56 cases.

Artifacts: `FIREWALL_VALIDATION.json`, provenance graph, public replay manifest.

Untouched: `theory/INFORMATION_BOUNDARIES.md`; old summary implementation and
historical traces.

## Step 6 -- Implement the v1.3 evaluator and scoring diagnostics

Files/modules:

- create `src/ser/evaluation/authz_v1_3.py`;
- create `tests/test_authzgym_v1_3_scoring.py`.

Behavior:

- Load independent restricted annotations only after normal output exists.
- Compute all metrics, weights, missingness, NA behavior, tie handling,
  threshold labels, and validity precedence exactly as section 13 specifies.
- Derive gold effects from gold facts in the evaluator implementation; check
  response self-consistency separately.
- Use the fixed public adapter and unchanged estimator hash for downstream
  diagnostics. Never reconstruct prior state from gold.

Tests:

- hand-calculated TP/FP/FN and four-way effect fixtures;
- all zero-denominator/empty-positive/missing/invalid cases;
- equal-usefulness and score-tie fixtures;
- repeated-case averaging and family/source/variant aggregation;
- earlier validity failures prevent later pass classifications;
- effect metrics are labeled non-independent in every rendered report.

Acceptance: exact agreement with all hand-calculated fixtures and no import from
the answerability checker.

Artifacts: scorer hash and offline synthetic metric fixtures only; no model
results.

Untouched: `src/ser/authzgym/policies.py` estimator behavior and all historical
analysis reports.

## Step 7 -- Revalidate the unchanged oracle/estimator

Files/modules:

- create `tools/validate_authzgym_v1_3_oracle.py`;
- add `tests/test_authzgym_v1_3_oracle.py`.

Behavior:

- Hash and call the unchanged estimator through only the section-13 adapter.
- Use independently validated gold, empty initial state, canonical development
  entries, and all mapped equivalence variants.
- Compute exact development gates and `1e-12` transformation equality.
- Do not change estimator weights, ranking inputs, source cases, or gold.

Tests:

- adapter mapping exactness; no prior state; target legality;
- mapped action-value equality for all five equivalence variants;
- deliberate estimator/hash/ranking failures create a blocker.

Acceptance: development canonical top-1/top-2/regret gates pass, all equivalent
values map exactly, and estimator hash matches. Confirmation portion remains
pending until Step 9.

Artifacts: preliminary `ORACLE_VALIDATION.json`; on failure also
`ORACLE_BLOCKER.md` and stop.

Untouched: estimator source and old oracle results.

## Step 8 -- Decide confirmation reuse without inspecting content

Files/modules/artifacts:

- create `CONFIRMATION_ELIGIBILITY.json` and a content-blind access transcript;
- add validation for its schema to `tests/test_authzgym_v1_3_population.py`.

Behavior:

- Gather only the metadata permitted by preregistration section 11.
- Record access history, prior zero-provider-call evidence, decision-source
  provenance, implementation freeze hashes, and declarations.
- Select exactly `reuse_with_new_v1_3_freeze` if every proof item passes;
  otherwise select `fresh_confirmation_v1_3_layouts_40_41`.

Tests:

- omission or prohibited metadata forces the fresh fallback;
- a reuse decision cannot be emitted before code/gate hashes are fixed.

Acceptance: one auditable outcome, with no case content emitted during this
step.

Artifacts: eligibility record, transcript hash, declarations.

Untouched: existing confirmation source bytes and manifests.

## Step 9 -- Convert, validate, and seal confirmation

Files/modules:

- extend only the already frozen parameterized paths in the population,
  answerability, firewall, scoring, and oracle tools; semantic code changes are
  prohibited after Step 8;
- add confirmation artifacts under this v1.3 directory.

Behavior:

- In an isolated run, either convert the allowed old sources or generate split
  `confirmation_v1_3` layouts 40/41 using the unchanged authoring method.
- Produce 8 sources x 7 variants = 56 cases and one scheduled call per case.
- Generate independent certificates, run answerability and firewall validation,
  and finish oracle validation. Reveal only aggregate pass/fail counts and hashes
  until sealed.
- On any failure, preserve it and stop. Do not patch a case or switch policy
  after viewing it.

Tests: same parameterized tests as development; explicit one-call schedule and
development/confirmation disjointness checks.

Acceptance: all confirmation answerability/firewall checks pass, oracle gates
pass, and sealed public/restricted manifests match.

Artifacts: confirmation source/public/restricted manifests, population,
certificates, validations, and hashes.

Untouched: development frozen bytes; existing confirmation artifacts.

## Step 10 -- Freeze the complete no-inference instrument

Files/modules:

- create `tools/verify_authzgym_v1_3.py` as a read-only verifier;
- create `FROZEN_INPUTS.json` and `FREEZE_CHECKLIST.md`;
- add read-only verification tests.

Behavior:

- Hash every item required by preregistration sections 12 and 16.
- Verify clean/matched source state, public/restricted separation, complete
  schedules, validator outcomes, estimator hash, and no provider-response files.
- Verification must not contact a network or import a provider client.

Tests: byte mutation of every manifest class fails; absent validation fails;
unexpected provider response/run file fails.

Acceptance: the verifier returns pass twice from a clean checkout and every
freeze item below is checked by named reviewer/date. This freezes the instrument
but still does not itself authorize a provider run; a later inference protocol
must name the frozen manifest.

Artifacts: final manifest, checklist, verifier report.

Untouched: all research semantics, estimator, and history.

## Step 11 -- Update current-state documentation after successful freeze

Files:

- update `state/STATUS.yaml`, `plan/ROADMAP.md`, `README.md`, and the M-013/H-018
  current notes/evidence references in `theory/IDEA_MAP.yaml`;
- regenerate generated views; append a new ADR only if an accepted constraint
  changed.

Behavior: record implementation/validation facts only. Do not promote a
hypothesis, add E-* evidence, or describe the instrument freeze as model
capability.

Tests: context regeneration and knowledge-coherence checker.

Acceptance: generated files are current, coherence passes, and the next cursor
names a separately authorized inference protocol rather than implying that
freeze itself ran a model.

Artifacts: updated living state and generated packet.

Untouched: historical ADRs/reports and concept maturity.

## Blocking semantic contradictions

Stop rather than delegate a choice if any of these occurs:

- two normative rules in the preregistration assign different answers to the
  same supported AST;
- the seven transformations cannot preserve the stated mapped semantics;
- a retained source cannot be certified without hidden role data;
- public-only derivation cannot reproduce a scored label;
- firewall separation is impossible without changing the accepted core access
  model;
- the unchanged estimator cannot consume the exact fixed adapter; or
- confirmation eligibility cannot be established under either the reuse or
  fresh fallback rule.

Implementation inconvenience, model expectations, historical score changes, or
oracle underperformance are not permission to choose new semantics.

## Freeze checklist -- all required before any model/provider inference

- [ ] ADR-0019 and this preregistration are included in the frozen manifest.
- [ ] V1.2 and every prior experiment artifact are byte-unchanged.
- [ ] Public contract, prompt, vocabulary, and strict schemas are frozen.
- [ ] Only f0--f16 exist; f17--f24 are absent and crosswalk is recorded.
- [ ] Four public effect families and the deterministic cue table are exact.
- [ ] Five unresolved-call categories and precedence are exact.
- [ ] `maximal_public_summary` and all normal prior semantic state are absent.
- [ ] Seven variants, 56 development cases, and 112-call repeat schedule match.
- [ ] Development public/restricted manifests and transformation maps match.
- [ ] Every scored development label has positive/negative evidence certificate.
- [ ] Independent public-only checker has 100% coverage/agreement and no shared
      label-producing helper with scorer/gold code.
- [ ] Hidden-data invariance and transformation consistency are 100%.
- [ ] Unsupported/ambiguous syntax count is zero.
- [ ] Firewall restricted-field mutations produce byte-identical normal state.
- [ ] Public-only replay passes with restricted files/modules unavailable.
- [ ] Normal state has no oracle-derived prior and oracle/normal channels are
      isolated, with no shared writable cache.
- [ ] Scoring fixtures pass, including empty-positive, NA, missingness, ties,
      weighting, validity precedence, and effect non-independence wording.
- [ ] Unchanged estimator hash matches and development oracle gates pass.
- [ ] Confirmation eligibility record proves reuse or selects fresh layouts
      40/41 without case-specific repair influence.
- [ ] Confirmation has 8 sources, 56 cases, one call per case, and separate new
      v1.3 manifests.
- [ ] Confirmation answerability and firewall checks pass with zero failures.
- [ ] Confirmation unchanged-estimator oracle gates pass.
- [ ] Public and restricted bundles are separately hash-frozen.
- [ ] Model/transport/retry/token/resource/spend configuration is frozen.
- [ ] No provider-response, run, or paid-call artifact exists for v1.3.
- [ ] `FROZEN_INPUTS.json` covers every required code/data/document path and
      verifies twice from a clean checkout.
- [ ] Final preregistration status is changed only to `frozen_no_inference_yet`
      by an append-only freeze record; research-semantic text is unchanged.
- [ ] Named reviewer and freeze date are recorded.
- [ ] A separate inference authorization names the exact final manifest.
- [ ] Jev, new architectures, and representation interventions remain deferred.
