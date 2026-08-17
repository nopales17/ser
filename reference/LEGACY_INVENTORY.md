<!-- GENERATED FILE: DO NOT EDIT. Run `python3 tools/emit_context.py`. -->

# IDS legacy component inventory

Canonical source: `reference/LEGACY_INVENTORY.yaml`. Read-only archive: `/Users/paolo/proj/ids-rule-to-cve-inference-archive` at `38b661324725c094ffcc820371a836573f4aadc5`. Inspection date: `2026-08-17`.

The inventory records transfer recommendations, not permission to copy code or data. Historical IDS measurements are not SER evidence.

## Classification summary

| Classification | Count | Meaning |
| --- | ---: | --- |
| `reuse_unchanged` | 0 | An artifact can enter SER without semantic or domain changes after an explicit import decision. |
| `generalize` | 11 | A pattern is worth re-implementing behind SER-owned contracts; the IDS code is not copied. |
| `empirical_evidence_only` | 14 | The artifact is historical evidence or a possible future environment asset, never controller architecture or SER validation. |
| `inspiration_only` | 4 | The design may inform a fresh specification but carries assumptions that make code or schema reuse unsafe. |
| `discard` | 2 | Exclude the artifact from SER architecture and implementation; preserve it only in the read-only archive. |

## Missing purported legacy implementations

### Scope and Interval definitions

No class, function, dataclass, schema, or model named Scope or Interval was found in the current tracked tree or any reachable git revision. SameProductNeighborhood and several claim-scope labels are IDS-specific constructs, not implementations of P-003.

- **Search scope:** ripgrep over the current archive plus git log -S and git grep over every revision returned by git rev-list --all
- **Recommendation:** Specify P-003 from first principles in Phase 2; do not retrofit a product neighborhood into the primitive.

### EpistemicMemoryUnit, Signal, and FlagAttachment definitions

No definition or reference to EpistemicMemoryUnit or FlagAttachment, and no relevant class or schema named Signal, was found in the current tracked tree or reachable history.

- **Search scope:** ripgrep over the current archive plus git log -S and git grep over every revision returned by git rev-list --all
- **Recommendation:** Treat the memory-unit and signal concepts as new SER design work, not legacy recovery.

### RES, GATE, AMP, DAMP, INHIBIT, SCOPE_FILTER, TOPK, DEFEAT, and PROMOTE

No exact SER coupling-operator implementation or semantics was found in the current tracked tree or reachable history. APF/APF2 filter operators are candidate-field predicates and are not evidence for M-001 through M-009.

- **Search scope:** exact-token ripgrep over the current archive plus git log -S and git grep over every revision returned by git rev-list --all
- **Recommendation:** Leave M-001 through M-009 speculative and define any Phase 2 coupling contract without inheriting APF vocabulary or behavior.

## Compact decision table

| Legacy component | Classification | Why | Phase 2 implication |
| --- | --- | --- | --- |
| `L-001` Tiered documentation, ADR ledger, and explicit authority boundaries | `inspiration_only` | The archive's document graph is project-specific and its status generator later omitted active post-poster work. | Keep the governance lesson; retain SER's independently designed knowledge architecture. |
| `L-002` Documentation coherence checker and generated status emitter | `inspiration_only` | The selected source set did not cover later active work, so a passing generator could still emit a misleading old substrate summary. | Use the failure as a design test: every generated SER view must declare and validate its full canonical source set. |
| `L-003` Run trace, sanitization, and secret-guard pattern | `generalize` | Fields and guards assume C1/C2 rule-to-CVE stages; resource accounting is optional and incomplete for SER allocation experiments. | Write a new SER trace contract with mandatory resource, observation, action, scope, budget, and outcome fields; borrow only the pattern. |
| `L-004` Completeness and run-audit gates | `generalize` | Expected counts, prediction schemas, and leakage tests are tied to IDS rule and candidate tasks. | Re-implement generic completeness and policy-conformance interfaces after Phase 2 contracts exist. |
| `L-005` Hash manifests, freeze records, and provenance bundles | `generalize` | The manifests encode CVE corpora, CPE resolution, and fixed candidate-universe construction. | Define a generic SER artifact manifest and hash every environment, controller, policy, seed, and trace schema version. |
| `L-006` Knowledge-access declarations and stage isolation | `generalize` | The C1/C2/C3 decomposition is a fixed two-stage attribution workflow, not a general reasoning environment. | Make an environment-owned access policy a required Phase 2 experiment contract. |
| `L-007` Versioned same-product candidate neighborhood | `empirical_evidence_only` | It is a static product partition over a 323-item corpus, not a dynamic scope carrying availability, locality, temporal, causal, or tool constraints. | Keep only as historical evidence; never implement P-003 by adapting this class or its product relation. |
| `L-008` Claim-scope and population-scope labels | `inspiration_only` | They are prose qualifiers, not a computational primitive or controller-visible object. | Use the lesson when specifying claims and evaluator reports, but define computational scope independently. |
| `L-009` Candidate-blind evidence ledger schema | `inspiration_only` | The schema is a draft for a candidate-list comparator, hard-codes IDS fields and caps, and has no completed model run. | Use as a falsification checklist while designing new epistemic-unit and signal contracts; do not adapt the schema. |
| `L-010` APF2 declarative three-valued filter protocol | `empirical_evidence_only` | The operator set is a CVE candidate filter, not SER coupling semantics; the completed development run eliminated no candidates. | Retain the safety outcome as historical evidence; do not import its predicates, flow, or operator names into Phase 2. |
| `L-011` APF1 model-generated Python filters | `empirical_evidence_only` | Executing generated filter code is unsafe, candidate-specific, and lost the gold answer in observed development cases. | Exclude executable model-authored policy code; preserve the failed result as a guardrail. |
| `L-012` Agentic Query Bridge | `empirical_evidence_only` | Product terms dominated; it did not beat the predicted-product baseline, and later variants introduced deviations and confirmation gaps. | Keep results as IDS evidence only; do not expose AQB queries, rankers, or comparators to a SER controller. |
| `L-013` Constraint-Directed Attribution scaffold | `empirical_evidence_only` | No model calls or adopted evaluation results exist; the scaffold is bound to candidate ranking and CVE descriptions. | Treat only as a source of test questions; build no Phase 2 contract around the CDA pipeline. |
| `L-014` Curated IDS rules and sanitized rule views | `empirical_evidence_only` | These are domain data, not reasoning primitives; the sequential sanitization ladder is not a general resource axis. | Leave in the archive; consider only through a future, explicitly accepted IDS environment adapter. |
| `L-015` CVE candidate corpus records | `empirical_evidence_only` | Descriptions expose answer-correlated fields; the closed universe encodes a static retrieval task rather than a general world. | Keep evaluator/environment-owned and unavailable to SER core unless an experiment contract explicitly exposes a view. |
| `L-016` Qrels, mappings, and eligibility labels | `empirical_evidence_only` | The archive contains corrected universe definitions and incomplete mappings; controller exposure would leak the task. | Keep strictly evaluator-side; if used later, freeze an explicit population and audit all corrections before any SER experiment. |
| `L-017` Corpus construction manifests and source provenance | `empirical_evidence_only` | The construction logic carries domain choices and prior target knowledge; it is not a neutral SER dataset abstraction. | Retain as archive provenance; future ingestion must be a separately reviewed environment decision. |
| `L-018` Deterministic observation-view construction pattern | `generalize` | The functions parse Suricata syntax and remove CVE/vendor/product cues according to an IDS-specific ladder. | Define a generic environment view interface; re-implement any IDS adapter later without copying this parser. |
| `L-019` Outcome scorer and evaluator separation pattern | `generalize` | Exact-match, partial semantic recovery, and eligibility logic are specific to vulnerability-shape labels. | Specify a generic scorer interface with environment-owned metrics, then implement environment-specific scorers independently. |
| `L-020` Lexical ranker and corpus004 retrieval runner | `empirical_evidence_only` | It embeds prior solution logic, hard-coded data paths, target task structure, and product/string shortcuts. | Exclude from SER core and controller-visible tools; preserve only to reproduce named historical baselines. |
| `L-021` Predicted-shape model prompts and runners | `empirical_evidence_only` | Prompts, output ontology, model IDs, parsing, and two-stage pipeline all pre-solve the IDS task structure. | Do not import prompts, outputs, or runners; use only as historical evidence with model/version caveats. |
| `L-022` Candidate comparators, product gates, and attribution object schemas | `empirical_evidence_only` | The comparator is bound to candidate lists and a single hidden answer; it is fragile and order-sensitive. | Exclude from any SER environment action set; retain only as evidence about confounding and evaluation design. |
| `L-023` Candidate construction, CPE resolver, and neighborhood selection | `empirical_evidence_only` | Normalization and selection encode CVE/vendor/product ontology and prior knowledge of the attribution problem. | Keep outside SER core; future use requires an environment-specific ADR and a new leakage audit. |
| `L-024` Paired statistical controls and deterministic resampling | `generalize` | Metrics, strata, and input schemas are tied to rule-to-CVE top-k retrieval. | Reuse the statistical ideas, not the code; choose tests only after Phase 2 outcome units and estimands are explicit. |
| `L-025` Blind benchmark splits and opaque identifiers | `generalize` | The freeze is for one IDS benchmark, and no evaluation case was ever run against either archived version. | Adopt blinding and split-freeze requirements at experiment design time, using new SER-owned schemas. |
| `L-026` Offline replay and portable benchmark bundle pattern | `generalize` | The bundle is a candidate freeze for a specific IDS pipeline and was not used for a completed benchmark evaluation. | Require portable replay as a later implementation criterion; do not copy the archived bundle. |
| `L-027` Isolation, secret, determinism, and outcome-blindness tests | `generalize` | Fixtures and forbidden fields are specific to rules, CVEs, and archived stage protocols. | Translate each property into environment-neutral contract tests after the relevant interfaces are specified. |
| `L-028` Preservation of failed runs and append-only experiment history | `generalize` | The directory organization and run semantics are inconsistent across the long IDS project. | Define a new append-only SER experiment record with explicit valid, invalid, aborted, and negative outcomes. |
| `L-029` Frozen benchmark attempts and failed Dev2 holdout acquisition | `empirical_evidence_only` | No benchmark evaluation was run, and the acquisition result concerns availability of IDS/CVE cases only. | Treat as a warning: define SER evaluation populations before controller iteration and never call the inspected IDS set a SER holdout. |
| `L-030` CVE, CPE, CWE, vendor, and product normalization maps | `discard` | Embedding these maps in SER would make general primitives depend on cybersecurity taxonomies and exact-string shortcuts. | Discard from SER architecture and implementation; leave in the archive unless a future IDS adapter explicitly owns it. |
| `L-031` IDS poster, figure, and Sankey plotting utilities | `discard` | The charts encode APF/AQB/CDA stages and could make a frozen sequential pipeline appear architecturally necessary. | Discard from SER; design visualizations only after SER experiment outputs exist. |

## Component records

### `L-001` -- Tiered documentation, ADR ledger, and explicit authority boundaries

- **Source path:** `README.md`
- **Classification:** `inspiration_only`
- **SER relevance:** Knowledge governance
- **Related idea IDs:** `F-005`, `P-007`
- **What it does:** Separates canonical documents, generated status, experiment records, and historical material while preserving decision history.
- **Why it might transfer:** The authority-versus-maturity distinction and append-only decisions are useful for a long-lived research program.
- **Why it might not:** The archive's document graph is project-specific and its status generator later omitted active post-poster work.
- **Dependencies:** `plan/ROADMAP.md`, `DECISIONS.md`, `state/STATUS.md`
- **IDS-specific assumptions:** IDS stage names; poster and internship milestones
- **Tests or evidence:** `tools/check_doc_coherence.py`, `tools/emit_status.py`
- **Recommended action:** Keep the governance lesson; retain SER's independently designed knowledge architecture.
- **Confidence:** `high`
- **Notes:** No file reuse is needed because SER Phase 0 already established its own smaller authority map.

### `L-002` -- Documentation coherence checker and generated status emitter

- **Source path:** `tools/check_doc_coherence.py`
- **Classification:** `inspiration_only`
- **SER relevance:** Generated-state validation
- **Related idea IDs:** `F-005`, `P-007`
- **What it does:** Checks a selected set of IDS documents and emits a synthesized project status page.
- **Why it might transfer:** Deterministic generation and explicit checks reduce silent documentation drift.
- **Why it might not:** The selected source set did not cover later active work, so a passing generator could still emit a misleading old substrate summary.
- **Dependencies:** `tools/emit_status.py`, `state/STATUS.md`
- **IDS-specific assumptions:** fixed IDS document headings; 50/150-rule substrate vocabulary
- **Tests or evidence:** `state/STATUS.md`, `plan/ROADMAP.md`
- **Recommended action:** Use the failure as a design test: every generated SER view must declare and validate its full canonical source set.
- **Confidence:** `high`
- **Notes:** Generic filenames do not imply generic behavior.

### `L-003` -- Run trace, sanitization, and secret-guard pattern

- **Source path:** `tools/run_trace.py`
- **Classification:** `generalize`
- **SER relevance:** P-007 provenance and replay
- **Related idea IDs:** `P-007`, `H-010`
- **What it does:** Writes structured JSONL traces and manifests with input hashes, access declarations, model metadata, candidates, raw and normalized outputs, then provides redaction and secret checks.
- **Why it might transfer:** A versioned, fail-closed trace envelope is necessary for replay, audit, and cost-matched evaluation.
- **Why it might not:** Fields and guards assume C1/C2 rule-to-CVE stages; resource accounting is optional and incomplete for SER allocation experiments.
- **Dependencies:** `tools/sanitize_trace.py`, `tools/test_secret_guard.py`
- **IDS-specific assumptions:** rule IDs and views; candidate CVE lists; C1/C2 access policy
- **Tests or evidence:** `tools/test_secret_guard.py`, `results/traces/pilot_shape_100_l3f_004/manifest.sanitized.json`
- **Recommended action:** Write a new SER trace contract with mandatory resource, observation, action, scope, budget, and outcome fields; borrow only the pattern.
- **Confidence:** `high`
- **Notes:** Do not copy trace rows or prompt text into SER.

### `L-004` -- Completeness and run-audit gates

- **Source path:** `tools/check_run_completeness.py`
- **Classification:** `generalize`
- **SER relevance:** Evidence admission
- **Related idea IDs:** `F-004`, `P-007`, `H-010`
- **What it does:** Fails on missing, duplicate, error, hash-mismatched, or trace-misaligned records and audits declared versus observed source access.
- **Why it might transfer:** SER results need machine-checkable admission gates and explicit limits on what a harness can establish.
- **Why it might not:** Expected counts, prediction schemas, and leakage tests are tied to IDS rule and candidate tasks.
- **Dependencies:** `tools/audit_shape_run.py`, `tools/run_trace.py`
- **IDS-specific assumptions:** one prediction per rule; shape-output leakage vocabulary
- **Tests or evidence:** `tools/audit_shape_run.py`
- **Recommended action:** Re-implement generic completeness and policy-conformance interfaces after Phase 2 contracts exist.
- **Confidence:** `high`
- **Notes:** The archive correctly notes that harness evidence cannot exclude gateway tools or model memorization.

### `L-005` -- Hash manifests, freeze records, and provenance bundles

- **Source path:** `data/s100_attribution_corpus_004/corpus_manifest.json`
- **Classification:** `generalize`
- **SER relevance:** P-007 provenance and immutable experimental inputs
- **Related idea IDs:** `P-007`, `H-010`
- **What it does:** Records source versions, file hashes, population construction, exclusions, and frozen artifact identities.
- **Why it might transfer:** Content-addressed inputs make results reproducible and prevent accidental benchmark mutation.
- **Why it might not:** The manifests encode CVE corpora, CPE resolution, and fixed candidate-universe construction.
- **Dependencies:** `data/benchmarks/ids_cve_attribution_v2/FREEZE_MANIFEST.json`
- **IDS-specific assumptions:** CVE/CPE sources; single frozen candidate corpus
- **Tests or evidence:** `data/s100_attribution_corpus_004/corpus_manifest.json`, `data/benchmarks/ids_cve_attribution_v2/VALIDATION_REPORT.md`
- **Recommended action:** Define a generic SER artifact manifest and hash every environment, controller, policy, seed, and trace schema version.
- **Confidence:** `high`
- **Notes:** Manifest structure transfers; archived contents do not.

### `L-006` -- Knowledge-access declarations and stage isolation

- **Source path:** `reference/KNOWLEDGE_ACCESS_POLICY.md`
- **Classification:** `generalize`
- **SER relevance:** Experimental controls and information boundaries
- **Related idea IDs:** `F-004`, `F-005`, `H-010`
- **What it does:** Defines what information, candidates, tools, and external sources each IDS stage may access.
- **Why it might transfer:** Controller and baseline comparisons are uninterpretable unless information access is declared and enforced.
- **Why it might not:** The C1/C2/C3 decomposition is a fixed two-stage attribution workflow, not a general reasoning environment.
- **Dependencies:** `reference/BENCHMARK_SPEC.md`, `tools/audit_shape_run.py`
- **IDS-specific assumptions:** closed-book rule-to-shape; closed-corpus shape-to-CVE
- **Tests or evidence:** `tools/test_aqb_isolation.py`, `tools/test_cda_isolation.py`
- **Recommended action:** Make an environment-owned access policy a required Phase 2 experiment contract.
- **Confidence:** `high`
- **Notes:** Preserve the distinction between declared access, harness-observed access, and unobservable provider behavior.

### `L-007` -- Versioned same-product candidate neighborhood

- **Source path:** `tools/same_product_neighborhood_v2.py`
- **Classification:** `empirical_evidence_only`
- **SER relevance:** Negative boundary evidence for P-003 Scope
- **Related idea IDs:** `P-003`, `H-003`, `M-006`
- **What it does:** Constructs a deterministic, outcome-blind CVE candidate set sharing an exact normalized product with a rule's mapped product.
- **Why it might transfer:** Its versioned correction tests illustrate how a restricted comparison set can be made explicit and reproducible.
- **Why it might not:** It is a static product partition over a 323-item corpus, not a dynamic scope carrying availability, locality, temporal, causal, or tool constraints.
- **Dependencies:** `tools/cpe_resolver_v1.py`, `data/s100_attribution_corpus_004/candidate_cves.jsonl`
- **IDS-specific assumptions:** CPE product identity; one hidden CVE target; fixed closed candidate universe
- **Tests or evidence:** `tools/test_cda_neighborhoods.py`, `state/STATUS.md`
- **Recommended action:** Keep only as historical evidence; never implement P-003 by adapting this class or its product relation.
- **Confidence:** `high`
- **Notes:** The archive contains no generic Scope or Interval definition.

### `L-008` -- Claim-scope and population-scope labels

- **Source path:** `state/STATUS.md`
- **Classification:** `inspiration_only`
- **SER relevance:** P-003 boundary vocabulary
- **Related idea IDs:** `P-003`, `F-003`, `Q-005`
- **What it does:** Qualifies IDS conclusions by population, corpus, stage, and comparison set.
- **Why it might transfer:** Explicit scope labels help prevent local observations from becoming universal claims.
- **Why it might not:** They are prose qualifiers, not a computational primitive or controller-visible object.
- **Dependencies:** `reference/DATASET_CARD.md`, `reference/BENCHMARK_SPEC.md`
- **IDS-specific assumptions:** eligible31 population; within-product and global candidate tasks
- **Tests or evidence:** `state/STATUS.md`, `archive/`
- **Recommended action:** Use the lesson when specifying claims and evaluator reports, but define computational scope independently.
- **Confidence:** `high`
- **Notes:** Population scope, claim scope, and controller action scope must remain distinct.

### `L-009` -- Candidate-blind evidence ledger schema

- **Source path:** `tools/cda_schema.py`
- **Classification:** `inspiration_only`
- **SER relevance:** P-001, P-002, and P-007 conceptual structure
- **Related idea IDs:** `P-001`, `P-002`, `P-007`, `Q-002`, `Q-003`
- **What it does:** Separates observations, inferable propositions, alternative interpretations, and unknowns with stable local IDs and source-basis references before candidate comparison.
- **Why it might transfer:** The separation discourages conclusions from being smuggled into evidence and makes later references auditable.
- **Why it might not:** The schema is a draft for a candidate-list comparator, hard-codes IDS fields and caps, and has no completed model run.
- **Dependencies:** `tools/cda_harness.py`, `tools/cda_evaluate.py`
- **IDS-specific assumptions:** rule observations; candidate CVE excerpts; two-stage candidate comparison
- **Tests or evidence:** `tools/test_cda_schema.py`, `tools/test_cda_protocol.py`
- **Recommended action:** Use as a falsification checklist while designing new epistemic-unit and signal contracts; do not adapt the schema.
- **Confidence:** `medium`
- **Notes:** No EpistemicMemoryUnit, Signal, or FlagAttachment type exists in this code.

### `L-010` -- APF2 declarative three-valued filter protocol

- **Source path:** `tools/apf2_schema.py`
- **Classification:** `empirical_evidence_only`
- **SER relevance:** Negative evidence about safe declarative filtering
- **Related idea IDs:** `M-002`, `M-006`, `M-008`, `H-007`
- **What it does:** Restricts model output to declarative candidate-field predicates evaluated as support, contradiction, or unknown with fail-retain behavior.
- **Why it might transfer:** Typed declarative actions and explicit unknown handling are safer than executing generated code.
- **Why it might not:** The operator set is a CVE candidate filter, not SER coupling semantics; the completed development run eliminated no candidates.
- **Dependencies:** `tools/apf2_filter_runtime.py`, `tools/apf2_harness.py`, `tools/apf2_evaluate.py`
- **IDS-specific assumptions:** candidate records; monotonic elimination; hidden gold must be retained
- **Tests or evidence:** `tools/test_apf2_declarative.py`, `results/runs/agentic_progressive_filter_dev_002/manifest.json`
- **Recommended action:** Retain the safety outcome as historical evidence; do not import its predicates, flow, or operator names into Phase 2.
- **Confidence:** `high`
- **Notes:** Safe-but-inert is an important negative result, not validation of a SER mechanism.

### `L-011` -- APF1 model-generated Python filters

- **Source path:** `tools/apf_schema.py`
- **Classification:** `empirical_evidence_only`
- **SER relevance:** Negative safety evidence
- **Related idea IDs:** `F-005`, `M-002`, `M-006`
- **What it does:** Asks a model to propose executable filtering logic over CVE candidates and replays its effects.
- **Why it might transfer:** Its failure demonstrates why learned or model-proposed control actions need typed validation and sandbox boundaries.
- **Why it might not:** Executing generated filter code is unsafe, candidate-specific, and lost the gold answer in observed development cases.
- **Dependencies:** `tools/apf_filter_runtime.py`, `tools/apf_harness.py`, `tools/apf_replay_helper.py`
- **IDS-specific assumptions:** Python candidate filters; CVE metadata fields; gold-preserving elimination
- **Tests or evidence:** `results/runs/agentic_progressive_filter_dev_001/manifest.json`, `tools/test_apf_runtime.py`
- **Recommended action:** Exclude executable model-authored policy code; preserve the failed result as a guardrail.
- **Confidence:** `high`
- **Notes:** This is evidence against a technique, not a reusable component.

### `L-012` -- Agentic Query Bridge

- **Source path:** `tools/aqb_schema.py`
- **Classification:** `empirical_evidence_only`
- **SER relevance:** Historical retrieval experiment
- **Related idea IDs:** `H-004`, `H-005`, `H-011`
- **What it does:** Turns a candidate-blind rule representation into structured retrieval queries, executes lexical search, and optionally invokes a candidate comparator.
- **Why it might transfer:** It illustrates an auditable separation between representation, retrieval execution, and scoring.
- **Why it might not:** Product terms dominated; it did not beat the predicted-product baseline, and later variants introduced deviations and confirmation gaps.
- **Dependencies:** `tools/aqb_executor.py`, `tools/aqb_harness.py`, `tools/aqb_metrics.py`
- **IDS-specific assumptions:** CVE corpus retrieval; product/vendor terms; fixed candidate ranking
- **Tests or evidence:** `results/runs/agentic_query_bridge_dev_001/manifest.json`, `tools/test_aqb_isolation.py`
- **Recommended action:** Keep results as IDS evidence only; do not expose AQB queries, rankers, or comparators to a SER controller.
- **Confidence:** `high`
- **Notes:** Engaging a corpus is not evidence of useful adaptive allocation.

### `L-013` -- Constraint-Directed Attribution scaffold

- **Source path:** `tools/cda_harness.py`
- **Classification:** `empirical_evidence_only`
- **SER relevance:** Unexecuted candidate-comparison design exploration
- **Related idea IDs:** `P-001`, `P-002`, `H-006`, `H-007`
- **What it does:** Builds two-stage candidate-blind ledgers and candidate comparison prompts with deterministic neighborhood and triviality diagnostics.
- **Why it might transfer:** Its evidence-first discipline and explicit alternatives may inform future epistemic-state tests.
- **Why it might not:** No model calls or adopted evaluation results exist; the scaffold is bound to candidate ranking and CVE descriptions.
- **Dependencies:** `tools/cda_schema.py`, `tools/cda_neighborhoods.py`, `tools/cda_triviality.py`, `tools/cda_evaluate.py`
- **IDS-specific assumptions:** one target CVE; candidate description excerpts; within-product ranking
- **Tests or evidence:** `tools/test_cda_protocol.py`, `tools/test_cda_safety.py`, `tools/test_cda_discovery.py`
- **Recommended action:** Treat only as a source of test questions; build no Phase 2 contract around the CDA pipeline.
- **Confidence:** `high`
- **Notes:** Deterministic diagnostics are engineering evidence, not experimental validation.

### `L-014` -- Curated IDS rules and sanitized rule views

- **Source path:** `data/pilot_shape_100/curated_rules_100.jsonl`
- **Classification:** `empirical_evidence_only`
- **SER relevance:** Possible future IDS environment observations
- **Related idea IDs:** `E-001`, `H-011`
- **What it does:** Provides 100 curated Suricata rules plus progressively sanitized and L3F-style observation views.
- **Why it might transfer:** A future IDS environment could expose frozen views as observations under a declared access policy.
- **Why it might not:** These are domain data, not reasoning primitives; the sequential sanitization ladder is not a general resource axis.
- **Dependencies:** `data/pilot_shape_100_l3f/curated_rules_100_l3f.jsonl`, `tools/build_l3f_view.py`
- **IDS-specific assumptions:** Suricata rule syntax; hand-designed sanitization levels; known rule population
- **Tests or evidence:** `reference/DATASET_CARD.md`, `data/pilot_shape_100/curated_rules_100_with_l4.jsonl`
- **Recommended action:** Leave in the archive; consider only through a future, explicitly accepted IDS environment adapter.
- **Confidence:** `high`
- **Notes:** No data was copied during Phase 1.

### `L-015` -- CVE candidate corpus records

- **Source path:** `data/s100_attribution_corpus_004/candidate_cves.jsonl`
- **Classification:** `empirical_evidence_only`
- **SER relevance:** Possible future IDS environment assets
- **Related idea IDs:** `E-001`, `H-011`
- **What it does:** Provides a frozen 323-record candidate universe with CVE descriptions and structured vulnerability metadata.
- **Why it might transfer:** It can support replay of the historical attribution environment and controlled observation-cost studies.
- **Why it might not:** Descriptions expose answer-correlated fields; the closed universe encodes a static retrieval task rather than a general world.
- **Dependencies:** `data/s100_attribution_corpus_004/corpus_manifest.json`
- **IDS-specific assumptions:** CVE JSON schema; candidate-list framing; closed corpus
- **Tests or evidence:** `reference/BENCHMARK_SPEC.md`, `data/s100_attribution_corpus_004/corpus_manifest.json`
- **Recommended action:** Keep evaluator/environment-owned and unavailable to SER core unless an experiment contract explicitly exposes a view.
- **Confidence:** `high`
- **Notes:** Candidate descriptions and structured fields must be costed and access-controlled separately.

### `L-016` -- Qrels, mappings, and eligibility labels

- **Source path:** `data/s100_attribution_corpus_004/qrels_all100.jsonl`
- **Classification:** `empirical_evidence_only`
- **SER relevance:** Future IDS evaluator-only labels
- **Related idea IDs:** `E-001`, `F-004`, `H-011`
- **What it does:** Records hidden ground truth, primary mappings, resolution outcomes, exclusions, and evaluation eligibility.
- **Why it might transfer:** Evaluator-only labels are necessary for reproducible scoring and stratified analysis.
- **Why it might not:** The archive contains corrected universe definitions and incomplete mappings; controller exposure would leak the task.
- **Dependencies:** `data/s100_attribution_corpus_004/qrels_primary58.jsonl`, `data/s100_attribution_corpus_004/cpe_resolution_resolverv1.jsonl`
- **IDS-specific assumptions:** single CVE answer; CPE resolution; eligible31 subset
- **Tests or evidence:** `data/s100_attribution_corpus_004/rejected_candidates_resolverv1.jsonl`, `state/STATUS.md`
- **Recommended action:** Keep strictly evaluator-side; if used later, freeze an explicit population and audit all corrections before any SER experiment.
- **Confidence:** `high`
- **Notes:** The U2 omission and U3 correction show why universe validity must precede scores.

### `L-017` -- Corpus construction manifests and source provenance

- **Source path:** `data/s100_attribution_corpus_004/corpus_manifest.json`
- **Classification:** `empirical_evidence_only`
- **SER relevance:** Future environment provenance
- **Related idea IDs:** `P-007`, `E-001`, `H-011`
- **What it does:** Documents the rule population, candidate acquisition, CPE resolution, exclusions, source snapshots, and file hashes.
- **Why it might transfer:** A future IDS environment needs this provenance to identify exactly what world is being replayed.
- **Why it might not:** The construction logic carries domain choices and prior target knowledge; it is not a neutral SER dataset abstraction.
- **Dependencies:** `tools/build_s100_attribution_corpus_002.py`, `tools/cpe_resolver_v1.py`
- **IDS-specific assumptions:** NVD/CVE data; CPE lookup; target-aware corpus construction
- **Tests or evidence:** `tools/validate_corpus_002.py`, `tools/phase1_final_lock_validate.py`
- **Recommended action:** Retain as archive provenance; future ingestion must be a separately reviewed environment decision.
- **Confidence:** `high`
- **Notes:** Provenance is reusable evidence; construction heuristics are prior solution logic.

### `L-018` -- Deterministic observation-view construction pattern

- **Source path:** `tools/sanitization.py`
- **Classification:** `generalize`
- **SER relevance:** Environment-owned observation contracts
- **Related idea IDs:** `P-002`, `P-003`, `H-011`
- **What it does:** Builds reproducible redacted or reduced rule representations from a richer source record.
- **Why it might transfer:** SER environments should own deterministic observation projections and make information loss explicit.
- **Why it might not:** The functions parse Suricata syntax and remove CVE/vendor/product cues according to an IDS-specific ladder.
- **Dependencies:** `tools/build_l3f_view.py`
- **IDS-specific assumptions:** Suricata fields; CVE leakage patterns; linear L0-L4 view order
- **Tests or evidence:** `data/pilot_shape_100_l3f/curated_rules_100_l3f.jsonl`
- **Recommended action:** Define a generic environment view interface; re-implement any IDS adapter later without copying this parser.
- **Confidence:** `high`
- **Notes:** Observation views are environment assets, not Scope itself.

### `L-019` -- Outcome scorer and evaluator separation pattern

- **Source path:** `tools/evaluate_semantic_recovery.py`
- **Classification:** `generalize`
- **SER relevance:** Experiment/evaluator contracts
- **Related idea IDs:** `F-004`, `P-007`, `H-010`
- **What it does:** Scores deterministic domain outcomes separately from generation and fails on malformed or error-bearing records.
- **Why it might transfer:** SER needs evaluator-owned outcomes and explicit coverage rather than self-reported controller success.
- **Why it might not:** Exact-match, partial semantic recovery, and eligibility logic are specific to vulnerability-shape labels.
- **Dependencies:** `data/shape_maps/`, `reference/BENCHMARK_SPEC.md`
- **IDS-specific assumptions:** vulnerability shape ontology; one rule-level label record
- **Tests or evidence:** `tools/evaluate_semantic_recovery.py`
- **Recommended action:** Specify a generic scorer interface with environment-owned metrics, then implement environment-specific scorers independently.
- **Confidence:** `high`
- **Notes:** Scoring code is not a controller component.

### `L-020` -- Lexical ranker and corpus004 retrieval runner

- **Source path:** `tools/run_b2_corpus004.py`
- **Classification:** `empirical_evidence_only`
- **SER relevance:** Historical baseline and contamination risk
- **Related idea IDs:** `F-004`, `E-001`, `H-011`
- **What it does:** Ranks a fixed CVE corpus using hand-designed lexical fields, query variants, product gates, and candidate comparators.
- **Why it might transfer:** Its measurements define historical IDS baselines that a future environment might reproduce.
- **Why it might not:** It embeds prior solution logic, hard-coded data paths, target task structure, and product/string shortcuts.
- **Dependencies:** `data/s100_attribution_corpus_004/`, `tools/run_b2e3_controls.py`
- **IDS-specific assumptions:** lexical CVE retrieval; fixed corpus; known product fields
- **Tests or evidence:** `state/STATUS.md`, `archive/`
- **Recommended action:** Exclude from SER core and controller-visible tools; preserve only to reproduce named historical baselines.
- **Confidence:** `high`
- **Notes:** Product-set retrieval usually narrowed but rarely decided the answer.

### `L-021` -- Predicted-shape model prompts and runners

- **Source path:** `tools/predict_shape_llm.py`
- **Classification:** `empirical_evidence_only`
- **SER relevance:** Historical inference pipeline
- **Related idea IDs:** `E-001`, `H-011`
- **What it does:** Prompts a model for an IDS vulnerability-shape representation and feeds normalized output into downstream ranking experiments.
- **Why it might transfer:** Traces may support reproduction of historical measurements.
- **Why it might not:** Prompts, output ontology, model IDs, parsing, and two-stage pipeline all pre-solve the IDS task structure.
- **Dependencies:** `tools/run_b2c0_predicted_shape.py`, `data/shape_maps/`
- **IDS-specific assumptions:** vulnerability-shape ontology; fixed stage ordering; historical model behavior
- **Tests or evidence:** `results/traces/pilot_shape_100_l3f_004/manifest.sanitized.json`
- **Recommended action:** Do not import prompts, outputs, or runners; use only as historical evidence with model/version caveats.
- **Confidence:** `high`
- **Notes:** The 13/31 product-match result falls to 3/31 under a term-frequency clamp.

### `L-022` -- Candidate comparators, product gates, and attribution object schemas

- **Source path:** `tools/run_aqb_v2_rank_hidden_comparator.py`
- **Classification:** `empirical_evidence_only`
- **SER relevance:** Historical solution logic and leakage risk
- **Related idea IDs:** `F-004`, `H-011`, `Q-005`
- **What it does:** Compares candidate CVE descriptions and structured fields, often after product-based narrowing, to select a single target.
- **Why it might transfer:** It exposes useful failure modes such as order sensitivity and information-access leakage.
- **Why it might not:** The comparator is bound to candidate lists and a single hidden answer; it is fragile and order-sensitive.
- **Dependencies:** `tools/aqb_schema.py`, `tools/cda_schema.py`
- **IDS-specific assumptions:** one correct CVE; candidate descriptions; exact normalized product
- **Tests or evidence:** `tools/score_aqb_v2_eval.py`, `state/STATUS.md`
- **Recommended action:** Exclude from any SER environment action set; retain only as evidence about confounding and evaluation design.
- **Confidence:** `high`
- **Notes:** The reported 25/31 Phase 2G score is invalid as one corrected aggregate because prompts were incomplete and order-sensitive.

### `L-023` -- Candidate construction, CPE resolver, and neighborhood selection

- **Source path:** `tools/cpe_resolver_v1.py`
- **Classification:** `empirical_evidence_only`
- **SER relevance:** Future IDS environment construction only
- **Related idea IDs:** `E-001`, `H-011`, `P-003`
- **What it does:** Normalizes CPE identities, acquires candidate CVEs, and constructs product-related comparison sets.
- **Why it might transfer:** A future IDS environment may need a frozen reconstruction of candidate provenance.
- **Why it might not:** Normalization and selection encode CVE/vendor/product ontology and prior knowledge of the attribution problem.
- **Dependencies:** `data/shape_maps/cpe_vendor_aliases-v1.json`, `tools/same_product_neighborhood_v2.py`
- **IDS-specific assumptions:** CPE syntax; vendor aliases; product equality; CVE publication corpus
- **Tests or evidence:** `data/s100_attribution_corpus_004/cpe_resolution_resolverv1.jsonl`, `tools/test_candidate_validity_001.py`
- **Recommended action:** Keep outside SER core; future use requires an environment-specific ADR and a new leakage audit.
- **Confidence:** `high`
- **Notes:** Candidate construction is not a neutral implementation of scope.

### `L-024` -- Paired statistical controls and deterministic resampling

- **Source path:** `tools/run_b2e3_controls.py`
- **Classification:** `generalize`
- **SER relevance:** Baseline and uncertainty analysis
- **Related idea IDs:** `F-004`, `H-010`
- **What it does:** Computes paired comparisons, Wilson intervals, exact McNemar tests, and seeded bootstrap summaries for named retrieval conditions.
- **Why it might transfer:** SER experiments need paired designs, deterministic resampling, and uncertainty rather than headline accuracy alone.
- **Why it might not:** Metrics, strata, and input schemas are tied to rule-to-CVE top-k retrieval.
- **Dependencies:** `tools/run_b2_corpus004.py`
- **IDS-specific assumptions:** binary per-rule correctness; top-k retrieval outcomes; eligible31 strata
- **Tests or evidence:** `state/STATUS.md`
- **Recommended action:** Reuse the statistical ideas, not the code; choose tests only after Phase 2 outcome units and estimands are explicit.
- **Confidence:** `high`
- **Notes:** A statistical helper cannot repair an invalid population or incomplete run.

### `L-025` -- Blind benchmark splits and opaque identifiers

- **Source path:** `data/benchmarks/ids_cve_attribution_v2/FREEZE_MANIFEST.json`
- **Classification:** `generalize`
- **SER relevance:** Holdout and leakage control
- **Related idea IDs:** `F-004`, `H-010`
- **What it does:** Freezes dev/eval/backup splits, hashes files, separates evaluator mappings, and replaces public identifiers with HMAC-derived opaque IDs.
- **Why it might transfer:** Blinding and evaluator/controller separation are important wherever outcome identifiers can leak.
- **Why it might not:** The freeze is for one IDS benchmark, and no evaluation case was ever run against either archived version.
- **Dependencies:** `data/benchmarks/ids_cve_attribution_v2/opaque_id_config_evaluator.json`, `reference/BENCHMARK_SPEC.md`
- **IDS-specific assumptions:** rule/CVE mappings; static supervised split; single target labels
- **Tests or evidence:** `data/benchmarks/ids_cve_attribution_v2/VALIDATION_REPORT.md`, `data/benchmarks/ids_cve_attribution_v2/EXPANSION_SELECTION_REPORT.md`
- **Recommended action:** Adopt blinding and split-freeze requirements at experiment design time, using new SER-owned schemas.
- **Confidence:** `high`
- **Notes:** A frozen benchmark is infrastructure, not evidence until it is run.

### `L-026` -- Offline replay and portable benchmark bundle pattern

- **Source path:** `benchmark/freeze_candidate_v0/docker/README.md`
- **Classification:** `generalize`
- **SER relevance:** Reproducible evaluation packaging
- **Related idea IDs:** `P-007`, `H-010`
- **What it does:** Packages frozen inputs, an offline evaluation path, and a container-oriented reproduction boundary.
- **Why it might transfer:** SER claims should be replayable without relying on mutable services or hidden local state.
- **Why it might not:** The bundle is a candidate freeze for a specific IDS pipeline and was not used for a completed benchmark evaluation.
- **Dependencies:** `benchmark/freeze_candidate_v0/`, `data/benchmarks/ids_cve_attribution_v2/`
- **IDS-specific assumptions:** IDS attribution file layout; static input/output evaluation
- **Tests or evidence:** `data/benchmarks/ids_cve_attribution_v2/FREEZE_MANIFEST.json`
- **Recommended action:** Require portable replay as a later implementation criterion; do not copy the archived bundle.
- **Confidence:** `medium`
- **Notes:** Phase 2 should specify contracts, not packaging.

### `L-027` -- Isolation, secret, determinism, and outcome-blindness tests

- **Source path:** `tools/test_secret_guard.py`
- **Classification:** `generalize`
- **SER relevance:** Safety and evidence-quality test patterns
- **Related idea IDs:** `F-005`, `P-007`, `H-010`
- **What it does:** Tests field-aware secret rejection, deterministic transformations, protocol isolation, corrected-neighborhood behavior, and absence of outcome access.
- **Why it might transfer:** These are cross-cutting properties that future SER adapters and experiment harnesses should prove mechanically.
- **Why it might not:** Fixtures and forbidden fields are specific to rules, CVEs, and archived stage protocols.
- **Dependencies:** `tools/test_aqb_isolation.py`, `tools/test_cda_isolation.py`, `tools/test_cda_neighborhoods.py`
- **IDS-specific assumptions:** IDS secret patterns; candidate-list protocols; CVE gold fields
- **Tests or evidence:** `tools/test_apf2_protocol.py`, `tools/test_cda_safety.py`
- **Recommended action:** Translate each property into environment-neutral contract tests after the relevant interfaces are specified.
- **Confidence:** `high`
- **Notes:** Property names transfer more reliably than test bodies.

### `L-028` -- Preservation of failed runs and append-only experiment history

- **Source path:** `results/runs/`
- **Classification:** `generalize`
- **SER relevance:** Negative evidence and audit history
- **Related idea IDs:** `F-004`, `F-005`, `P-007`
- **What it does:** Retains manifests and artifacts for aborted, invalid, negative, and corrected experimental branches alongside successful runs.
- **Why it might transfer:** SER needs failed and invalidated attempts to remain inspectable so later claims cannot silently select favorable histories.
- **Why it might not:** The directory organization and run semantics are inconsistent across the long IDS project.
- **Dependencies:** `DECISIONS.md`, `state/STATUS.md`
- **IDS-specific assumptions:** IDS phase labels; historical run-directory conventions
- **Tests or evidence:** `results/runs/agentic_progressive_filter_dev_001/manifest.json`, `results/runs/agentic_progressive_filter_dev_002/manifest.json`
- **Recommended action:** Define a new append-only SER experiment record with explicit valid, invalid, aborted, and negative outcomes.
- **Confidence:** `high`
- **Notes:** Preservation does not make a result valid; it makes the validity judgment auditable.

### `L-029` -- Frozen benchmark attempts and failed Dev2 holdout acquisition

- **Source path:** `data/benchmarks/ids_cve_attribution_v2/VALIDATION_REPORT.md`
- **Classification:** `empirical_evidence_only`
- **SER relevance:** Historical evidence about evaluation readiness
- **Related idea IDs:** `F-004`, `H-010`, `E-001`
- **What it does:** Records two frozen benchmark packages and attempts to acquire a separate development population that failed minimum population floors.
- **Why it might transfer:** It demonstrates that a valid holdout is a population property, not a label that can be attached after repeated development inspection.
- **Why it might not:** No benchmark evaluation was run, and the acquisition result concerns availability of IDS/CVE cases only.
- **Dependencies:** `data/dev2_acquisition_pool/`, `data/benchmarks/ids_cve_attribution_v1/`
- **IDS-specific assumptions:** CVE publication population; rule eligibility floors; static supervised holdout
- **Tests or evidence:** `data/benchmarks/ids_cve_attribution_v2/EXPANSION_SELECTION_REPORT.md`, `state/STATUS.md`
- **Recommended action:** Treat as a warning: define SER evaluation populations before controller iteration and never call the inspected IDS set a SER holdout.
- **Confidence:** `high`
- **Notes:** The development population was repeatedly inspected and has no valid holdout role.

### `L-030` -- CVE, CPE, CWE, vendor, and product normalization maps

- **Source path:** `data/shape_maps/cpe_vendor_aliases-v1.json`
- **Classification:** `discard`
- **SER relevance:** None in SER core
- **Related idea IDs:** `F-005`, `P-003`
- **What it does:** Collapses domain strings and taxonomy values to support product identity, label equivalence, retrieval, and scoring.
- **Why it might transfer:** Only a future IDS environment may need frozen copies or equivalent normalization behavior.
- **Why it might not:** Embedding these maps in SER would make general primitives depend on cybersecurity taxonomies and exact-string shortcuts.
- **Dependencies:** `tools/cpe_resolver_v1.py`, `data/shape_maps/`
- **IDS-specific assumptions:** CVE/CPE/CWE ontology; vendor aliases; product equivalence
- **Tests or evidence:** `data/s100_attribution_corpus_004/cpe_resolution_resolverv1.jsonl`
- **Recommended action:** Discard from SER architecture and implementation; leave in the archive unless a future IDS adapter explicitly owns it.
- **Confidence:** `high`
- **Notes:** Do not let normalizer convenience define Scope or resource locality.

### `L-031` -- IDS poster, figure, and Sankey plotting utilities

- **Source path:** `tools/plot_apf_sankey.py`
- **Classification:** `discard`
- **SER relevance:** No architectural relevance
- **Related idea IDs:** `F-005`
- **What it does:** Renders IDS-specific figures, rank transitions, and candidate-flow Sankey diagrams for archived presentations.
- **Why it might transfer:** Visual communication remains useful, but no specific implementation is needed now.
- **Why it might not:** The charts encode APF/AQB/CDA stages and could make a frozen sequential pipeline appear architecturally necessary.
- **Dependencies:** `tools/plot_aqb_rank_transitions.py`, `tools/plot_cda_sankey.py`
- **IDS-specific assumptions:** candidate elimination stages; poster-specific labels and colors
- **Tests or evidence:** `tools/test_apf_figures.py`, `tools/test_cda_figures.py`
- **Recommended action:** Discard from SER; design visualizations only after SER experiment outputs exist.
- **Confidence:** `high`
- **Notes:** Presentation structure must not become controller structure.

## Architectural Contamination Risks

### `R-001`

- **Risk:** Treating a fixed candidate list or closed corpus as the natural shape of every reasoning environment.
- **Guardrail:** Phase 2 contracts must allow environments without candidates, retrieval, or a single hidden answer.
- **Archive sources:** `tools/run_b2_corpus004.py`, `reference/BENCHMARK_SPEC.md`
- **Related idea IDs:** `P-003`, `H-004`, `H-011`

### `R-002`

- **Risk:** Freezing the IDS representation-then-retrieval sequence into SER controller architecture.
- **Guardrail:** Represent observation, action, resource, and outcome interfaces without prescribing a pipeline order.
- **Archive sources:** `tools/predict_shape_llm.py`, `tools/aqb_harness.py`
- **Related idea IDs:** `P-001`, `P-002`, `H-004`

### `R-003`

- **Risk:** Equating product neighborhoods or claim qualifiers with P-003 Scope.
- **Guardrail:** Specify scope dimensions and invariants from first principles; keep environment population and controller scope separate.
- **Archive sources:** `tools/same_product_neighborhood_v2.py`, `state/STATUS.md`
- **Related idea IDs:** `P-003`, `H-003`, `M-006`

### `R-004`

- **Risk:** Importing CVE, CPE, CWE, vendor, product, or exact-string schemas into domain-neutral primitives.
- **Guardrail:** All domain data remains behind environment-owned observation and evaluator adapters.
- **Archive sources:** `tools/cpe_resolver_v1.py`, `data/shape_maps/`
- **Related idea IDs:** `F-005`, `P-001`, `P-003`

### `R-005`

- **Risk:** Confusing lexical retrieval, term frequency, or product gates with adaptive reasoning allocation.
- **Guardrail:** Always compare against fixed and token/cost-matched non-adaptive baselines and report shortcut controls.
- **Archive sources:** `tools/run_b2_corpus004.py`, `tools/run_b2e3_controls.py`
- **Related idea IDs:** `F-004`, `H-001`, `H-005`

### `R-006`

- **Risk:** Reading APF/APF2 predicates as implementations of SER coupling operators.
- **Guardrail:** Keep M-001 through M-009 speculative until their semantics, state transitions, and falsification tests are independently specified.
- **Archive sources:** `tools/apf2_schema.py`, `tools/apf2_filter_runtime.py`
- **Related idea IDs:** `M-001`, `M-002`, `M-006`, `M-008`

### `R-007`

- **Risk:** Letting prior prompts, outputs, rankers, or candidate comparators leak a historical solution into a future environment.
- **Guardrail:** Exclude prior solution logic from controller-visible assets and identify any reproduction baseline by name and version.
- **Archive sources:** `tools/predict_shape_llm.py`, `tools/run_aqb_v2_rank_hidden_comparator.py`
- **Related idea IDs:** `F-004`, `F-005`, `H-011`

### `R-008`

- **Risk:** Calling the repeatedly inspected eligible31 development set or an unrun benchmark a holdout.
- **Guardrail:** Pre-register a new evaluation population and its access history before SER controller iteration.
- **Archive sources:** `state/STATUS.md`, `data/benchmarks/ids_cve_attribution_v2/VALIDATION_REPORT.md`
- **Related idea IDs:** `F-004`, `H-010`

### `R-009`

- **Risk:** Assuming one ordered sanitization ladder is the universal resource or visibility axis.
- **Guardrail:** Model observation transformations as environment-defined and allow incomparable or multidimensional resource types.
- **Archive sources:** `tools/sanitization.py`, `tools/build_l3f_view.py`
- **Related idea IDs:** `P-002`, `P-003`, `Q-005`

### `R-010`

- **Risk:** Mistaking generic filenames, classes, or schemas for domain-independent semantics.
- **Guardrail:** Judge transfer by dependencies and invariants, not names; every generalized pattern receives a new SER specification and implementation.
- **Archive sources:** `tools/run_trace.py`, `tools/check_doc_coherence.py`
- **Related idea IDs:** `F-005`, `P-007`

### `R-011`

- **Risk:** Allowing generated status to pass checks while omitting a newly active body of work.
- **Guardrail:** Declare generator inputs, validate freshness, and review the rendered context for misleading omissions before every phase transition.
- **Archive sources:** `tools/emit_status.py`, `state/STATUS.md`
- **Related idea IDs:** `F-005`, `P-007`

### `R-012`

- **Risk:** Using candidate descriptions, qrels, or target-aware construction artifacts as controller observations.
- **Guardrail:** Separate public observations, controller state, environment internals, and evaluator-only labels in the Phase 2 contract.
- **Archive sources:** `data/s100_attribution_corpus_004/qrels_all100.jsonl`, `data/s100_attribution_corpus_004/candidate_cves.jsonl`
- **Related idea IDs:** `F-004`, `P-002`, `P-007`

## Phase 2 conceptual contract recommendation

| Contract | Phase 2 disposition | Recommendation | Legacy influence | Must not assume |
| --- | --- | --- | --- | --- |
| State | `design_from_scratch` | Specify only the controller-visible decision state required to choose and audit the next allocation; distinguish it from hidden environment state and evaluator state. | CDA's evidence ledger is a test case for separation, not a state schema to adapt. | candidate lists; graph storage; CVE fields; the CDA two-stage ledger |
| Observation | `design_from_scratch` | Define an environment-issued, provenance-bearing view made available after reset or action, with visibility and information-access boundaries explicit. | Deterministic sanitized views motivate environment ownership, but the IDS L0-L4 ladder is not adapted. | Suricata text; linear sanitization levels; lexical features; candidate descriptions |
| Epistemic unit / hypothesis | `design_from_scratch` | Specify a minimal immutable unit with stable identity, typed content or reference, provenance, creation step, visibility, confidence as an annotation rather than truth, and explicit derivation or supersession links. | CDA's separation of observations, propositions, alternatives, and unknowns is a useful test case only. | candidate lists; CVE fields; a single hidden answer; the CDA two-stage ledger |
| Signal | `design_from_scratch` | Specify a typed, provenance-bearing observation about state or change whose interpretation is separate from its payload and whose reliability can be calibrated by the environment or evaluator. | Trace envelopes and CDA basis references motivate provenance; the archive contains no generic Signal type. | lexical match score; candidate rank; binary support; CVE attribution |
| Scope | `design_from_scratch` | Specify an explicit environment-interpreted constraint over which actions, observations, tools, epistemic units, regions, or times are available, leaving composition and geometry minimal until an environment requires them. | Population qualifiers and versioned neighborhoods show why scope must be explicit, but no legacy implementation survives. | product equality; fixed corpus membership; linear sanitization levels; interval geometry |
| Action | `design_from_scratch` | Specify a typed request that allocates a declared resource to a target under a scope and budget, with validation, rejection, and accounting owned by the environment; do not yet prescribe a policy or coupling operator set. | APF2 demonstrates the safety value of declarative actions and fail-closed validation, while its filter flow is rejected as a general architecture. | candidate elimination; retrieval-first ordering; generated Python; RES/GATE/AMP operator semantics |
| ActionResult | `design_from_scratch` | Define the environment's accepted, rejected, failed, or completed response with observations produced, actual resources charged, termination information, and trace references. | Fail-closed run records and completeness checks motivate explicit rejection and failure states. | one prediction record; success-only traces; one model call; binary correctness |
| Transition | `design_from_scratch` | Specify how hidden environment state and controller-visible state change after an action, including deterministic or seeded stochastic behavior and termination conditions. | Seeded utilities and replay checks generalize as requirements; the IDS batch pipeline has no reusable transition model. | fixed pipeline stages; stateless ranking; monotonic candidate elimination; batch-only execution |
| Environment | `design_from_scratch` | Define reset, valid actions, transition execution, observation production, scope enforcement, resource accounting, stopping, and evaluator hooks without choosing an IDS adapter. | Access policies, frozen views, and evaluator separation supply requirements; IDS assets are intentionally deferred to a later environment decision. | retrieval; candidate sets; single hidden answers; IDS data availability |
| Policy | `define_interface_defer_implementations` | Define only the mapping from visible state and remaining budget to an action or stop decision; defer coupling laws, learned policies, graphs, and controller implementations. | Prior IDS rankers and prompts are baselines or contamination risks, not policies to adapt. | LLM calls; graph state; retrieval-first behavior; coupling operator semantics |
| Cost | `design_from_scratch` | Represent a typed resource vector and budget with environment-owned charging; do not force tokens, latency, tool calls, and dollars into one scalar before the comparison requires it. | Optional trace token/latency/cost fields expose the need for mandatory accounting but are not sufficient to adapt. | tokens as the universal unit; one scalar conversion; zero-cost observations; one provider |
| Outcome | `design_from_scratch` | Define environment- or evaluator-owned terminal and trajectory measures separately from controller belief, with invalidity and coverage reported alongside performance. | Separated deterministic scorers and corrected population definitions generalize as requirements, not implementations. | accuracy only; a single correct label; static qrels; controller access to outcome |
| Experiment and evaluator | `generalize_patterns` | Specify frozen environment/controller versions, access policy, seeds, resource accounting, trace completeness, outcome ownership, paired baselines, invalid-run rules, and holdout provenance before implementing an experiment. | Trace manifests, access declarations, blinding, completeness gates, and paired controls generalize as patterns. | accuracy as the only outcome; static supervised splits; one model call per item; IDS data availability |

## Phase 1 conclusion

No component is classified `reuse_unchanged` (0 total). The patterns worth independently rebuilding are:

- versioned trace and provenance envelopes
- fail-closed completeness and access-policy checks
- hash manifests and frozen inputs
- evaluator/controller information separation
- paired controls, uncertainty, blinding, and deterministic replay
- append-only preservation of failed and invalid runs

Rejected as architecture:

- fixed candidate-list and representation-to-retrieval pipelines
- product neighborhoods as Scope
- APF/APF2 predicates as coupling operators
- CVE/CPE/CWE schemas and normalizers in SER core
- prior prompts, rankers, comparators, and target-aware construction logic

Deferred environment assets:

- curated rules and sanitized views
- candidate corpus records and manifests
- qrels, mappings, populations, and benchmark splits

**Phase 2 starting point:** Specify the minimal, domain-neutral contracts for state, observation, epistemic unit or hypothesis, signal, scope, action, action result, transition, environment, policy interface, typed cost, outcome, and experiment/evaluator behavior. Legacy patterns may supply tests and provenance requirements, but no legacy code is authorized for import.

See `reference/IDS_LESSONS.md` for the concise scientific synthesis.
