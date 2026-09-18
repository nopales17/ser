# Architectural decision record ledger

This cold ledger is append-only. Accepted architectural and governance decisions
are recorded here before dependent charter changes. Supersede an earlier ADR with
a new entry; do not rewrite it.

## ADR-0001 -- Layered knowledge architecture

- Status: accepted
- Date: 2026-08-17
- Decision: Separate cold conceptual authority, warm planning, hot-ish current
  state, reference material, and evidence artifacts. Keep the canonical document
  set small and assign each source one ownership role in `MAP.md`.
- Why: Future sessions need reconstructable state without one enormous README or
  dependence on conversation history.
- Alternatives rejected: a monolithic project document; raw transcripts as the
  primary memory; per-document authority labels without a central map.

## ADR-0002 -- Canonical stable-ID idea registry

- Status: accepted
- Date: 2026-08-17
- Decision: `theory/IDEA_MAP.yaml` is the canonical registry for important
  concepts. Stable category-prefixed IDs are never reused. The file uses the
  JSON-compatible subset of YAML so all tooling remains Python-standard-library
  only.
- Why: Stable identity prevents terminology drift, while structured data permits
  automatic rendering and validation without introducing a package dependency.
- Alternatives rejected: prose-only concept lists; generated IDs; a database or
  documentation framework at this stage.

## ADR-0003 -- Authority and maturity are independent

- Status: accepted
- Date: 2026-08-17
- Decision: Location determines authority and a single explicit status determines
  maturity. Allowed statuses are `seed`, `working`, `accepted`,
  `experimentally_supported`, `rejected`, and `deprecated`. Implementation never
  promotes theory automatically.
- Why: Speculative ideas must be preserved durably without becoming doctrine.
- Alternatives rejected: moving concepts between folders to indicate confidence;
  deleting rejected ideas; treating implementation as acceptance.

## ADR-0004 -- Deterministic generated context

- Status: accepted
- Date: 2026-08-17
- Decision: `tools/emit_context.py` deterministically renders
  `theory/IDEA_MAP.md` and `state/CONTEXT_PACKET.md` from canonical sources.
  Generated files carry a warning and are checked byte-for-byte for freshness.
- Why: A concise, portable briefing lets a new agent recover state while keeping
  the sources of truth explicit.
- Alternatives rejected: hand-maintained summaries; embedding a large context
  dump in README; using chat transcripts as a build input.

## ADR-0005 -- Explicit single phase cursor

- Status: accepted
- Date: 2026-08-17
- Decision: `plan/ROADMAP.md` contains exactly one phase with status `active`.
  `state/STATUS.yaml` repeats the cursor only as a coherence-checked current-state
  fact. Phase detail remains coarse until it approaches execution.
- Why: A fresh session needs one unambiguous next direction without a sprawling
  speculative implementation plan.
- Alternatives rejected: implicit next steps scattered through prose; multiple
  concurrent active research phases; a detailed long-range build schedule.

## ADR-0006 -- IDS archive isolation

- Status: accepted
- Date: 2026-08-17
- Decision: Treat `/Users/paolo/proj/ids-rule-to-cve-inference-archive` as
  read-only historical input. Phase 1 may classify reuse candidates, but copying
  code, importing data, building an adapter, or claiming transfer requires later
  explicit decisions and relevant evidence.
- Why: The completed IDS project offers disciplined benchmark artifacts but is a
  domain-specific study, not evidence for SER's general architecture.
- Alternatives rejected: forking the historical repository as SER; assuming its
  abstractions transfer; importing it during Phase 0.

## ADR-0007 -- Canonical legacy inventory and no-transfer default

- Status: accepted
- Date: 2026-08-17
- Decision: `reference/LEGACY_INVENTORY.yaml` is the canonical registry for
  Phase 1 legacy-component judgments, and `reference/LEGACY_INVENTORY.md` is its
  generated readable view. Classifications record research recommendations, not
  import authorization. The default remains no code or data transfer; any future
  reuse or environment ingestion requires a separate explicit decision.
- Why: Stable inventory IDs, domain-assumption records, and contamination
  guardrails make the archaeological result durable without allowing legacy
  convenience to dictate SER architecture.
- Alternatives rejected: prose-only notes; copying candidate artifacts while
  evaluating them; treating `generalize` or `empirical_evidence_only` as implicit
  permission to import.

## ADR-0008 -- Separate latent world, epistemic state, and evaluation

- Status: accepted
- Date: 2026-08-17
- Context: A sequential epistemic-control comparison is uninterpretable if
  hidden truth, controller-entitled information, private belief state, and
  evaluator knowledge share one undifferentiated state object.
- Decision: Environments own latent `WorldState`; normal policies act only on
  legitimately released observations, their controller-owned `EpistemicState`,
  legal action capabilities, and remaining budget; evaluators use a separate
  restricted view. Evaluator-only information has no path into normal policy
  state or interfaces.
- Why: The separation makes partial observability, leakage audits, oracle
  references, and fair baseline comparison explicit across all target domains.
- Alternatives rejected: one global episode state passed to all components;
  policy access to world handles with voluntary field discipline; treating
  evaluator labels as ordinary environment metadata.
- Consequences: Future implementations require explicit projections and access
  classes. Oracle policies must run as separately labeled evaluator instruments.
- Revisit when: A target domain cannot be represented without legitimate online
  feedback from evaluation; that feedback must first be modeled as a new
  provenance-bearing observation under a named access condition.

## ADR-0009 -- Policy-neutral environment and action-legality boundary

- Status: accepted
- Date: 2026-08-17
- Context: Environments must expose what can legally be attempted without
  encoding which attempt is epistemically best or depending on SER's private
  belief representation.
- Decision: The environment owns latent dynamics, initial observation release,
  legal concrete actions or generative capabilities, domain execution, and
  environment termination. It never consumes `EpistemicState`. Legality may
  depend on world constraints, public history, capabilities, and budget, but not
  private controller reasoning. Policy preference is a separate role.
- Why: This permits random, fixed, exhaustive, oracle-reference, learned, LLM,
  and future SER policies to share the same environment without silently giving
  the environment policy power.
- Alternatives rejected: environment-supplied ranked recommendations; passing
  controller belief into action generation; assuming every action set is a small
  materialized list.
- Consequences: Action interfaces may use schemas and validators for effectively
  infinite spaces. Internal computation uses declared controller-side executors,
  has no deliberate world effect, and does not expose controller state to the
  environment; independent world evolution may still continue.
- Revisit when: A domain demonstrates that legal capability genuinely depends on
  controller-private state; the dependency must then be made public or modeled
  as a controller-side validator.

## ADR-0010 -- Preserve vector-valued resource accounting

- Status: accepted
- Date: 2026-08-17
- Context: Tokens, compute, latency, money, tool calls, executions, and sensor
  acquisitions are not universally commensurate, while resource-normalized
  comparison requires their actual consumption to remain visible.
- Decision: Episodes declare named resource dimensions and units. Per-action and
  cumulative costs are nonnegative vectors; budgets constrain named dimensions.
  The core defines no conversion factors or universal scalar. Experiments may
  preregister scalarization, lexicographic comparison, or Pareto analysis while
  retaining raw dimensions.
- Why: Raw accounting prevents hidden conversions and permits the same contracts
  to support domains with different scarce resources.
- Alternatives rejected: one universal cost number; tokens as the default unit;
  treating absent cross-domain dimensions as zero.
- Consequences: A dimension absent from an episode schema is unmeasured or
  inapplicable, while an omitted per-action value within a declared schema is
  zero. Unknown action cost needs an explicit feasibility/overrun rule.
- Revisit when: Empirical work identifies a stable, justified conversion within
  a stated scope; any conversion remains experiment-specific unless separately
  accepted.

## ADR-0011 -- First-class STOP and distinct termination causes

- Status: accepted
- Date: 2026-08-17
- Context: Treating termination as only a loop condition prevents analysis of
  premature stopping, wasteful continuation, abstention, and budget truncation.
- Decision: `STOP` is a first-class controller action with a domain submission or
  abstention. Controller stop, environment termination, and runner/evaluator
  truncation remain distinct trace events and outcome dimensions.
- Why: Stopping is part of epistemic allocation and must be attributable to the
  policy rather than conflated with external limits.
- Alternatives rejected: implicit termination on answer production; treating
  budget exhaustion as STOP; requiring every stop to include confidence or a
  natural-language rationale.
- Consequences: Phase 3 traces and evaluators must preserve a primary termination
  cause. STOP correctness remains evaluator-owned rather than an action result.
- Revisit when: Continuing tasks require pause/resume semantics; those semantics
  may extend rather than collapse the three causes.

## ADR-0012 -- Minimal epistemic ontology and explicit deferral

- Status: accepted
- Date: 2026-08-17
- Context: A universal evidence ontology, graph, Signal type, scope algebra, or
  coupling language is not needed to state the control problem or implement the
  first MicroGym baselines.
- Decision: Observations are first-class released information; hypotheses are an
  optional controller representation with no required common semantic supertype.
  A universal `EpistemicUnit` is rejected from the minimal core. Scope is an
  optional typed capability with domain-owned semantics. Signal, graph state,
  coupling operators, learned routing, confidence calculus, and universal
  information-gain objectives are deferred.
- Why: The smaller ontology supports hypothesis-free baselines and all four
  pressure-test domains while keeping experimental questions out of the problem
  definition.
- Alternatives rejected: everything as `EpistemicUnit`; a mandatory
  `EpistemicObject` envelope; mandatory graph state; preserving Signal or named
  coupling operators solely because they already have names.
- Consequences: Phase 3 begins with history-based state and no coupling operator.
  Scope-aware gating requires a separate environment variant and controls before
  it can support `H-003`.
- Revisit when: Multiple implemented environments expose the same missing
  semantic behavior and accepted contracts cannot represent it without repeated
  incompatible workarounds.

## ADR-0013 -- Evidence-directed environment selection and software research trunk

- Status: accepted
- Date: 2026-08-17
- Context: A synthetic control result does not by itself determine which real
  environment best resolves the next uncertainty. Existing IDS artifacts are
  convenient, but convenience is not a scientific reason to make IDS the main
  SER development environment.
- Decision: GitLab authorization investigation is the primary practical research
  trunk. MicroGym is a control-mechanism validation instrument. IDS may be used
  only as a small semantic bridge if a positive MicroGym result leaves survival
  under messy semantic evidence unresolved. Controlled software investigation,
  including chosen tests or fuzzing, is preferred when it can directly and
  cleanly test the remaining question while advancing authorization research.
  Remote sensing and other substrates remain dormant falsification candidates,
  not scheduled phases. A new environment requires a concrete statement of the
  unresolved architectural claim it can distinguish.
- Why: This keeps domain expansion evidence-directed, separates validation
  instruments from the practical target, and avoids inheritance from the IDS
  archive determining the roadmap.
- Alternatives rejected: making IDS the automatic Phase 4; treating every
  pressure-test domain as a planned implementation; moving directly to GitLab
  after a null MicroGym result; treating GitLab prioritization as evidence that
  SER works.
- Consequences: Phase 3 remains unchanged in scope. Its evidence determines
  whether the next phase is correction/falsification, a narrow IDS semantic
  bridge, or a controlled software/authz environment. No IDS, GitLab, fuzzing,
  LLM, or remote-sensing implementation is authorized during Phase 3.
- Revisit when: Phase 3 or later controlled-software evidence identifies a
  different smallest environment needed to resolve a named uncertainty.

## ADR-0014 -- Route from synthetic control to controlled authorization evidence

- Status: accepted
- Date: 2026-08-17
- Context: MicroGym routing-v1 isolated a one-step fixed-horizon condition in
  which the unchanged public-model candidate used a released cue to select the
  exact closed-loop acquisition and captured value unavailable to the best
  same-model open-loop plan. The result depends on clean supplied likelihood
  tables and does not test semantic action-value estimation.
- Decision: Complete Phase 4 with a narrowly scoped routing finding and make a
  minimal controlled authorization-oriented software environment the next
  validation phase. Its unresolved question is whether a controller can
  estimate decision-relevant epistemic-action values from imperfect software
  and authorization evidence when clean likelihood tables are not supplied.
  Do not begin with real GitLab integration. Do not add an IDS bridge unless a
  later explicit comparison shows that it is materially cleaner or cheaper for
  isolating that same question.
- Why: The synthetic result resolves whether the current candidate can execute
  observation-conditioned routing in a favorable exact-model setting. A
  controlled authorization environment tests the newly exposed estimation gap
  while advancing the practical research trunk established by ADR-0013.
- Alternatives rejected: treating the one-step synthetic result as general SER
  validation; moving directly to real GitLab; choosing IDS because artifacts
  already exist; remaining synthetic without a named remaining routing defect;
  adding LLM, graph, Scope, coupling, or learned-policy machinery preemptively.
- Consequences: Phase 5 may design the smallest controlled authorization task
  that separates semantic action-value estimation from generic software skill.
  Phase 4 artifacts remain immutable, IDS remains read-only, and no evidence is
  claimed for GitLab, semantic competence, multi-stage planning, or real-domain
  value.
- Revisit when: A controlled-environment design cannot isolate action-value
  estimation without a smaller semantic bridge, or evidence shows that routing
  itself still fails outside the exact one-step condition.

## ADR-0015 -- Separate authorization benchmark calibration from model evidence

- Status: accepted
- Date: 2026-08-17
- Context: Phase 5A requires a benchmark that separates semantic extraction,
  epistemic update, action-value estimation, routing, and final authorization
  diagnosis before any paid or variable model result is observed. The first
  deterministic calibration of Static Semantic AuthzGym v1 exposed an
  identifier-dependent omission schedule in a degraded test double, so its
  perturbation validation correctly failed.
- Decision: Preserve the failed v1 calibration without rewriting it and freeze
  protocol 1.1 as a benchmark-integrity correction. Protocol 1.1 changes only
  the deterministic mock omission key from opaque artifact identity to semantic
  fact/relation role. Treat both protocols as construction and calibration, not
  empirical SER evidence. Any actual inexpensive-model evaluation must be a
  separate frozen experiment using the already frozen population, semantic
  interface, budgets, baselines, and classifier thresholds, or must declare a
  new protocol version before observing evaluation outcomes.
- Why: Failed-run preservation makes the benchmark's contamination history
  auditable. Versioning prevents an invariance repair from becoming invisible
  post-result tuning, while the separation between deterministic mocks and an
  actual semantic model prevents implementation success from promoting a
  hypothesis.
- Alternatives rejected: overwriting the invalid v1 artifacts; weakening the
  perturbation check; treating deterministic rule interpreters as semantic
  evidence; calling a model before the benchmark and classifier were frozen;
  advancing directly to active testing or real GitLab.
- Consequences: Static Semantic AuthzGym protocol 1.1 is ready for a separately
  recorded inexpensive-model evaluation. Phase 5 remains active, no new
  empirical finding is admitted, model integrations remain zero, Phase 5B is
  not ready, real GitLab remains gated, and IDS remains dormant and read-only.
- Revisit when: The separate model run is complete, or a preregistered integrity
  failure requires another explicitly versioned correction before interpreting
  model performance.

## ADR-0016 -- Preserve the first real-model AuthzGym run as invalid

- Status: accepted
- Date: 2026-08-17
- Context: The separately frozen real-model v1 experiment completed every
  scheduled primary and perturbation architecture-run with one inexpensive
  model and valid cost, access, hash, and evidence-scope controls. However,
  response/schema validity failed: only 88/192 runs were valid, 135 provider
  responses hit the output-length limit, and dynamic artifact/reference
  constraints rejected further syntactically valid outputs. The preregistered
  classifier therefore returned `invalid`.
- Decision: Preserve the complete responses, traces, reports, and failure
  classification without repairing or re-running them. Admit no semantic or
  architecture-leverage finding and promote no hypothesis from diagnostic
  metrics. Keep Phase 5 active and Phase 5B blocked. The next admissible work is
  a separately versioned, preregistered static follow-up that establishes
  response-contract reliability and sufficient output budget on development
  episodes before repeating a complete frozen evaluation. Do not move to a
  larger population, stronger model, executable AuthzGym, historical cases,
  GitLab, or IDS to escape the invalid result.
- Why: Treating partial valid outputs as a matched architecture result would
  violate the frozen classifier and confound semantic capability with interface
  truncation and dynamic-contract failures. Preserving the invalid run exposes
  the smallest current experimental defect without tuning on evaluation
  behavior.
- Alternatives rejected: parsing truncated JSON heuristically; manually
  repairing responses; weakening legality/reference checks; comparing only
  valid subsets as if randomized; increasing output tokens after evaluation;
  silently switching models; advancing to a richer environment.
- Consequences: Static AuthzGym remains the active validation instrument, but
  real-model protocol v1 supplies no E-* finding and no support for H-016,
  H-017, or H-018. Its transport/economic evidence is retained as implementation
  fact: 610 inference calls including development cost $0.379060610 under the
  frozen accounting rule, all research artifacts remained local, and the
  egress tunnel terminated.
- Revisit when: A new versioned static protocol passes its own full integrity,
  response-validity, perturbation, and matched architecture gates.

## ADR-0017 -- Preserve semantic-contract v1.2 as transport-unstable

- Status: accepted
- Date: 2026-08-17
- Context: The separately frozen development-only semantic-contract v1.2 study
  removed free-form outputs and model-generated identifiers, raised the
  per-artifact output safety ceiling to 1,024 tokens, and scheduled 128 calls
  over only the eight development episodes. The first eight responses were
  schema-valid with no length termination or illegal reference. The ephemeral
  wiseau SSH connection then timed out; the remaining 120 calls exhausted their
  identical retry on transport connection/proxy failures. The complete schedule
  is integrity-valid but only 8/128 calls are response-valid, so the
  preregistered classifier is `contract_unstable`.
- Decision: Preserve the complete v1.2 responses, stress records, hashes,
  accounting, report, and classifier without rerunning or repairing them in
  place. Admit no semantic-capability or SER finding and promote no hypothesis.
  Keep Phase 5 active and Phase 5B blocked. The next admissible work is a new
  separately versioned development-only transport-envelope stability protocol
  that retains the v1.2 semantic schema, prompt, model, and development source
  population while preregistering tunnel-liveness handling and transport
  failure accounting. Do not proceed to architecture comparison or a stronger
  model until the complete semantic channel clears its mechanical contract.
- Why: Interpreting the eight successful responses would confound model
  capability with temporal position before an exogenous tunnel failure. The
  zero observed truncations and illegal references are encouraging diagnostics,
  but eight non-random prefix calls cannot establish response reliability or a
  capability floor for the full stress population.
- Alternatives rejected: treating transport failures as missing observations;
  comparing only the successful prefix; reconnecting and resuming the frozen
  run under an unregistered transport rule; rewriting v1.2 in place; weakening
  its 100% post-retry requirement; switching models; rerunning the observed 24
  evaluation episodes; advancing to executable AuthzGym, GitLab, or IDS.
- Consequences: The v1.2 oracle-only diagnostic may identify the unchanged
  deterministic estimator as adequate given perfect development observations,
  but it is not model evidence. The actual spend of $0.005474160, 248 attempts,
  240 transport failures, local-only persistence, and terminated tunnel remain
  implementation facts rather than an empirical SER result.
- Revisit when: A separately frozen full development stress protocol completes
  with stable transport and satisfies its response-contract classifier.

## ADR-0018 -- Admit transport stability and preserve weak nano semantics as a development diagnostic

- Status: accepted
- Date: 2026-08-17
- Context: The separately frozen transport-envelope v1 study retained semantic
  contract v1.2, the nano model, and the exact 128-call development schedule.
  A zero-inference preflight first exposed an unsupported redundant curl option;
  that failed preflight, its initial manifest, and cleanup evidence are preserved
  before the corrected protocol was refrozen. The corrected workload then
  received provider responses for 128/128 logical calls through one supervised
  SSH/SOCKS tunnel, with zero raw transport failures, zero reconnects, no
  permanent losses, successful cleanup, and $0.086505640 accounted spend. All
  128 responses passed the frozen schema on their first semantic attempt, but
  semantic precision/recall, action compatibility, repeat exactness, and
  transformation equivalence remained below the preregistered capability
  thresholds. The transport and contract classifiers are `transport_stable`
  and `contract_stable`; the semantic diagnostic is `semantic_signal_weak`.
- Decision: Treat the local-Mac to supervised SSH SOCKS to wiseau to API
  transport envelope as stable for this exact development protocol and treat
  semantic contract v1.2 as mechanically reliable with this model and schedule.
  Preserve the weak nano semantic result as a development-only capability-floor
  diagnostic. Create no `E-*` finding, promote no hypothesis, and make no
  architecture comparison. Keep Phase 5 active and Phase 5B blocked. Under the
  preregistered Case C rule, the next admissible experiment retains the frozen
  v1.2 semantic contract and uses the next stronger inexpensive model in a
  separately versioned, preregistered development/confirmatory design. The 24
  previously observed evaluation episodes remain recovery/diagnostic material
  and cannot serve as untouched confirmation.
- Why: Complete transport and schema validity remove networking and wire-format
  reliability as confounders for this development schedule, so nano's weak
  semantic measurements are now interpretable at the declared capability-floor
  scope. They do not test SER-vs-ReAct, resource-normalized architecture value,
  or untouched generalization, and therefore cannot support H-001, H-016,
  H-017, or H-018.
- Alternatives rejected: tuning the v1.2 prompt or schema after observing the
  weak metrics; rerunning nano until quality improves; interpreting schema
  validity as semantic competence; returning to the old 24 evaluation episodes;
  running SER-vs-ReAct with a weak semantic channel; moving to executable
  AuthzGym, GitLab, IDS, fuzzing, graphs, coupling laws, or training; silently
  discarding the zero-inference preflight failure.
- Consequences: Transport supervision, same-byte replay, scoped insecure TLS,
  remote SOCKS DNS, local credential delivery, event/hash accounting, and final
  cleanup are retained as implementation behavior for subsequent static model
  studies. The unchanged deterministic estimator remains adequate only under
  perfect evaluator observations on eight development entries. The smallest
  justified next question is whether a stronger inexpensive model can clear the
  same frozen semantic thresholds before any architecture experiment is
  designed.
- Revisit when: A separately frozen stronger-model semantic study completes, or
  transport behavior changes enough that the envelope no longer satisfies the
  recorded stability conditions.

## ADR-0019 -- Replace AuthzGym v1.2 semantics with a separately versioned, answerable v1.3 instrument

- Status: accepted
- Date: 2026-09-18
- Context: The preserved v1.2 semantic studies established useful transport and
  wire-format facts, but the later zero-call audit found that their public task
  and evaluator did not define the same semantic target. Curated per-artifact
  tags omitted source-direct facts requested by the prompt, some test labels
  depended on hidden logical roles, candidate effects used an unpublished
  evaluator mapping, and the `maximal_public_summary` condition constructed
  normal model-visible prior state from oracle content. These defects prevent
  clean fact/effect capability attribution and violate the declared normal-input
  firewall for the affected summary cases. The accepted external
  research-validity adjudication selected the smallest repair and is translated
  normatively in
  `experiments/authzgym_semantic_contract_v1_3/PREREGISTRATION.md`.
- Decision: Create v1.3 as a new instrument under the exact normative
  preregistration; do not repair v1.2 in place. Retain four mechanism families,
  f0--f16, and seven non-summary variants; retire f17--f24. Derive gold from
  published source-local rules, keep roles hidden, make effects public
  deterministic fact-derived diagnostics, and restrict relations to five
  visible-call categories. Exclude `maximal_public_summary` and all
  evaluator-derived normal state. Independent public-only answerability,
  firewall, unchanged-estimator oracle, population, manifest, and freeze gates
  must pass before inference.
- Confirmation decision: The old Mini confirmation protocol is not resumed.
  Its underlying model-unqueried source instances may be converted
  deterministically into a new v1.3 confirmation freeze only if an auditable
  record demonstrates that no case-specific confirmation content influenced
  the repair. Content-blind metadata inspection alone is permitted before the
  semantic and implementation freeze. If the non-influence record is incomplete
  or any case-specific source, gold, ordering, identifier, usefulness, or
  certificate influenced repair choices, generate a fresh confirmation source
  population under the preregistered fallback instead.
- Interpretation: v1.3 model scores will not be directly numerically comparable
  with v1.2 scores. Historical thresholds may be reused only as prospective
  engineering screening floors. Effect metrics do not constitute a second
  semantic-capability signal. Stored v1.2 responses may be rescored only as an
  explicitly labeled offline diagnostic over propositions with demonstrably
  unchanged meanings; such results are not v1.3 performance.
- Why: A measurement instrument cannot distinguish model error from benchmark
  error unless every scored answer is uniquely determined by the authorized
  public input and published rules. Separating normal and evaluator channels is
  an already accepted project invariant, not an optional benchmark feature.
  The narrower repair removes unanswerable labels and privileged assistance
  without introducing a model, representation, routing architecture, or new
  mechanism family.
- Alternatives rejected: exposing hidden logical roles; preserving all 25 facts
  for dimensional continuity; independently authoring candidate-effect labels;
  relabeling oracle summaries as public; weakening answerability to agreement
  with the current scorer; modifying the estimator to rescue oracle performance;
  overwriting prior reports; treating an unqueried confirmation manifest as
  automatically reusable after task semantics change; adding Jev or another
  architecture to the repair.
- Consequences: Historical model responses, reports, hashes, and classifiers
  remain immutable. A separate corrigendum qualifies their interpretation.
  Phase 5 remains active and Phase 5B remains blocked. The next authorized work
  is offline implementation and validation of the exact v1.3 instrument. No
  model/provider inference is authorized until every item in the v1.3 freeze
  checklist passes. An oracle failure is a separately recorded blocker and does
  not authorize silent estimator tuning.
- Revisit when: The v1.3 public contract, independent answerability validator,
  firewall suite, source populations, manifests, unchanged-estimator oracle
  validation, and final preregistration have all been frozen, or an internal
  contradiction makes the accepted contract impossible to implement. A future
  Jev study requires its own decision after v1.3 validation and may not alter
  this instrument to facilitate that comparison.

## ADR-0020 -- Authorize the bounded development-only estimator repair `est-repair-v1.3.1`

- Status: accepted
- Date: 2026-09-18
- Context: The unchanged v1.3 estimator passed the development canonical oracle
  gate (top-1 0.625, top-2 0.875, mean normalized regret 0.175, zero illegal
  targets, 40/40 transformation equivalence) but failed the sealed
  fresh-confirmation canonical top-2 gate at 0.750 against the frozen `>= 0.80`
  requirement. `experiments/authzgym_semantic_contract_v1_3/ORACLE_BLOCKER.md`
  records the blocker, and an accepted external adjudication selected the
  smallest repair: a prospective, separately versioned estimator/adapter change
  with its own preregistration and evidence boundary. That repair is specified
  normatively in
  `experiments/authzgym_estimator_repair_v1_3_1/REPAIR_STUDY_PREREGISTRATION.md`
  with a mechanical implementation plan in the same directory.
- Decision: Accept
  `experiments/authzgym_estimator_repair_v1_3_1/REPAIR_STUDY_PREREGISTRATION.md`
  as the governing preregistration for `est-repair-v1.3.1` and authorize its
  bounded offline development-only existence study in the fixed A then B then C
  order within a total budget of at most 10 attempts (`<= 10`), under every
  ceiling, baseline-freeze, non-degeneracy, own-ranking invariance, input
  allowlist, component firewall, and stopping rule that preregistration
  specifies. Section 8 successor confirmation generation, freezing, and
  execution are **not** authorized.
- Why: A measurement instrument whose scored answers are already known to be
  misaligned with the unchanged downstream component cannot support a clean
  component finding. The accepted v1.3 semantics are sound and frozen; the open
  question is only whether some admissible, bounded-complexity,
  invariance-certified component of the authorized public state can meet the
  existing engineering gate, and whether the defect is confined to one
  component boundary. Bounding the work to a bounded offline existence study,
  with the ceiling and baselines frozen before any candidate exists and with a
  single admissible pass ending the search, prevents the repair from becoming a
  tuning exercise against a spent confirmation population.
- Alternatives rejected: editing or retuning `src/ser/authzgym/policies.py` in
  place to make the preserved confirmation gate pass; weakening, re-deriving, or
  reinterpreting the top-2 `>= 0.80`, top-1 `>= 0.60`, or regret `<= 0.35`
  thresholds; reusing, resampling, or characterizing the spent
  `confirmation_v1_3` population; reinterpreting the preserved
  fresh-confirmation failure; scoring candidates beyond the first admissible
  pass or ranking passing candidates; authorizing section-8 confirmation
  generation or execution at the same time as development; deriving gold from
  hidden logical roles or evaluator-only channels; adding Jev, a representation
  intervention, or an architecture comparison to the repair; and treating an
  oracle or validator failure as permission to tune the estimator.
- Consequences: Condition `est-repair-v1.3.1` becomes an authorized
  development-only study whose artifacts live under
  `experiments/authzgym_estimator_repair_v1_3_1/` and whose revised components,
  if any, are new modules rather than edits to preserved baselines. Historical
  v1.2 and v1.3 artifacts, responses, reports, hashes, classifiers, and blockers
  remain immutable. Phase 5 remains active and Phase 5B remains blocked. A
  passing development candidate yields at most a
  `development_component_compatibility_diagnostic`; it is not an `E-*` evidence
  record, promotes no hypothesis, and establishes no capability, architecture,
  transfer, or model claim. Model/provider inference remains unauthorized, and a
  later separate decision naming the frozen component hash and the frozen
  development-report hash is required before any new confirmation population is
  generated, frozen, or accessed.
- Preserved under this decision: `src/ser/authzgym/policies.py` (SHA-256
  `092a7a87...`), `src/ser/evaluation/authz_v1_3.py`, every AuthzGym v1.3
  semantic rule, prompt, schema, population, threshold, usefulness target, prior
  result, and protected artifact stay byte-unchanged, and the spent
  `confirmation_v1_3` population is not opened, counted, sampled, or
  characterized. Reusing it, weakening or reinterpreting any gate, Jev,
  architecture comparison, semantic change, and hypothesis promotion all remain
  unauthorized.
- Revisit when: The development study terminates with a preregistered outcome
  label and a frozen development report, or an implementation contradiction
  appears that the accepted preregistration does not resolve. If a passing
  component exists, the successor decision must name its source hash and the
  development-report hash before section-8 confirmation work begins.

## ADR-0021 -- Correct the `est-repair-v1.3.1` step-1 specification defects and resume the authorized study

- Status: accepted
- Date: 2026-09-18
- Context: Under ADR-0020 the `est-repair-v1.3.1` development study executed
  handoff step 1 and stopped at its specified stop condition. Five of the six
  recorded B0 figures reproduced exactly, but the recorded `longest_artifact`
  regret did not: the specification text records `0.7833333333333333`, while the
  authorized development split yields `0.6583333333333333`. The recorded value is
  the confirmation-split figure from the `confirmation` block of
  `experiments/authzgym_semantic_contract_v1_3/ORACLE_VALIDATION.json`, which the
  preregistration itself lists as forbidden exposure, so the recorded figure could
  not be reproduced without reading a prohibited channel. The same stop surfaced
  two further defects: preregistration section 2.6 and handoff step 5 state the
  own-ranking invariance obligation in two non-equivalent readings, only one of
  which reproduces the recorded B0 36/40 fixture; and handoff step 0's instruction
  to hash everything under the v1.3 directory contradicted the study's prohibition
  on opening the spent confirmation population, so the step-0 integrity pass
  hashed 16 confirmation-named files. The worker asserted the recorded figures
  verbatim, refused to substitute a value or to read the confirmation channel,
  disclosed the step-0 access, and stopped without creating a candidate or
  consuming budget.
- Decision: Accept
  `experiments/authzgym_estimator_repair_v1_3_1/CORRIGENDUM.md` as an
  append-only correction governing `est-repair-v1.3.1` prospectively, with its
  three sections normative: the recorded `longest_artifact` regret is a
  transcription error and step-1 reproduction is authorized against the
  development value `0.6583333333333333`, with the confirmation-split read-out
  recorded as further already-exposed spent-confirmation information; the
  own-ranking obligation is resolved as own-selection-decision equivariance,
  B0 at 36/40, candidates at 40/40, full-order invariance descriptive only; and
  the step-0 confirmation-path hashing is a procedural deviation, not
  retroactively authorized, which on the verified facts does not invalidate the
  study, with the integrity procedure amended so the development harness opens
  or hashes no confirmation path. No gate, threshold, budget, arm order,
  stopping rule, non-degeneracy requirement, input allowlist, firewall
  requirement, or claim boundary changes; ADR-0020 resumes unchanged and the
  study resumes at handoff step 1.
- Why: A measurement instrument and its downstream study are only as trustworthy
  as the provenance of every recorded figure. A specification figure taken from a
  split the study is forbidden to read is a defect in the specification, not a
  finding, and correcting it in an append-only record preserves both the accepted
  text and the correction. Resolving the invariance obligation toward the
  selection reading keeps the obligation aligned with the property that actually
  failed for the preserved baseline, while refusing to require an ordering the
  authorized public state does not support. Recording rather than excusing the
  hashing deviation keeps the access ledger honest, and amending the procedure
  prevents the same instruction conflict from reaching a successor population,
  where an equivalent access would be a blocking violation.
- Alternatives rejected: editing the accepted preregistration or the
  implementation handoff in place to match the observed figures; adjusting the
  harness until the recorded `0.783` reproduced; reading the confirmation split
  to satisfy a recorded figure; treating the discrepancy as an experimental
  result, a regression, or evidence about either split; discarding the step-1
  artifacts or forfeiting budget over the hashing deviation; retroactively
  authorizing that access or omitting it from the record; adopting the full-order
  reading of the invariance obligation, which contradicts the recorded 36/40
  fixture and would demand an ordering the public state does not support;
  adopting the argmax-set reading, which would make the recorded fixture
  unattainable as a failure; weakening ND-1, ND-2, or ND-3 to accommodate
  declared ties; and re-opening ADR-0020's scope, budget, arm order, stopping
  rule, or claim boundary.
- Consequences: `est-repair-v1.3.1` resumes at handoff step 1 under the
  corrigendum and proceeds in order, with the Tier-1 ceiling still a blocking
  gate preceding all candidate work. No gate, threshold, budget, arm order,
  stopping rule, non-degeneracy requirement, input allowlist, firewall
  requirement, or claim boundary changes. The accepted preregistration, the
  implementation handoff, ADR-0019, ADR-0020, every AuthzGym v1.3 artifact, the
  historical estimator at SHA-256 `092a7a87...`, and the fixed adapter remain
  byte-unchanged. Successor confirmation generation, freezing and execution,
  model/provider inference, spent-confirmation access including hashing, v1.3
  semantic changes, threshold changes, Jev, and architecture comparison all
  remain unauthorized. Phase 5 remains active and Phase 5B remains blocked.
- Revisit when: The development study terminates with a preregistered outcome
  label and a frozen development report, or a further implementation
  contradiction appears that neither the accepted preregistration nor this
  corrigendum resolves.

## ADR-0022 -- Authorize the one-shot successor confirmation of the frozen `est-repair-v1.3.1-B-1` component

- Status: accepted
- Date: 2026-09-18
- Context: The ADR-0020 study, corrected by ADR-0021, terminated prospectively at
  its first admissible pass. Verification against repository artifacts confirms
  every entry condition. The Tier-1 authorized-information ceiling was computed
  before any candidate and is sufficient (top-1 `0.75`, top-2 `1.0`). B0--B3 and
  the B2-derived `nd3_floor_from_b2 = 4` were frozen before any candidate
  evaluation. Three attempts of ten were used. `est-repair-v1.3.1-B-1` passes all
  nine section-4.2 gate checks: canonical top-1 `0.75`, top-2 `1.0`, mean
  normalized regret `0.116667`, zero illegal targets, ND-1/ND-2/ND-3 all true
  with strict-unique-maximum `6` against the frozen floor `4`, own-selection
  equivariance `40/40`, frozen section-14 action-value equivalence `40/40` with
  zero failures, complexity `3` against the bound `4`, and the expanded
  action-value firewall checks 1--8 passing with the section-9.9 scope statement
  recorded. Leave-one-source-out has zero failing folds and no `fragile` label.
  Candidates A-1 and A-2 met all four frozen thresholds but failed ND-1 and ND-2
  on the two degenerate ownership-family cases, so the non-degeneracy
  requirement, not the thresholds, was the binding constraint. The component
  class SHA-256, module SHA-256, and development-report markdown SHA-256 each
  re-derive exactly from the artifacts on disk; every AuthzGym v1.2/v1.3
  artifact, `src/ser/authzgym/policies.py` at `092a7a87...`, and
  `src/ser/evaluation/authz_v1_3.py` are byte-unchanged; no provider, response,
  or run artifact exists; and the access ledger records no confirmation access
  during the resumed study.
- Decision: Authorize execution of the already-preregistered section-8 successor
  confirmation protocol for exactly one component, `est-repair-v1.3.1-B-1`
  (component class SHA-256
  `88b77c5f343117b354b5039d571bf03bf8867fcd7fb4f8fc91c1e1aefca7a048`, module
  SHA-256
  `f9c92317abc562ac5175f90074238c666de55d557b02e0de368841676f4d910d`), against
  the frozen development report `DEVELOPMENT_REPORT.md` SHA-256
  `f0629d3b78ba35258cc6d439e4b731c3682b76fa08e4155efbdad7cd0df18638`. Authorized:
  (1) generation and freezing of the `confirmation_v1_3_1` population at layouts
  42/43 under the preregistered content-independent selection rule, with the
  preregistered collision rule advancing to the reserved pairs 44/45 then 46/47
  and never by inspecting content; (2) independent certification, answerability
  validation, and firewall validation in the section-8.7 isolation order, with
  the section-8.5 access ledger and the section-8.3 duplication and equivalence
  checks; (3) exactly one oracle evaluation of the frozen B-1 component under the
  unchanged top-1 `>= 0.60`, top-2 `>= 0.80`, regret `<= 0.35`, zero-illegal,
  section-14 equivalence, and own-selection equivariance gates; and (4)
  preservation of the outcome, pass or failure, as this component's final
  result. Nothing beyond these four items is authorized.
- Why: The preregistered condition for a successor authorization -- a frozen
  component and a frozen development report, both named by verified hash -- is
  met, and section 8 already specifies the population, the freeze ordering, and
  the one-shot rule in advance. Authorizing only execution of that fixed protocol
  keeps the confirmation prospective: no parameter of it is chosen after seeing
  the development result, and the component cannot change in response to what
  confirmation shows.
- Alternatives rejected: modifying B-1 or re-tuning it before or after
  confirmation; opening further candidate development, including the two unused
  Arm A attempts or Arm C; reusing, re-reading, or characterizing the spent
  `confirmation_v1_3` population; replacing, repairing, excluding, or reweighting
  a failing confirmation case; generating a second population for B-1 after a
  failure; altering any threshold, gate, tie rule, usefulness label, or v1.3
  semantic rule; running model or provider inference; and adding Jev,
  adaptive-routing experiments, or architecture comparison.
- Consequences: If the successor population fails any preregistered
  construction, duplication, answerability, firewall, or freeze condition,
  execution stops and the blocker is recorded; it is not repaired post hoc. The
  one-shot component evaluation runs once and its result stands: a failure is
  preserved as this component's final result and no further population is
  generated for B-1. A pass establishes only confirmed compatibility of this
  component with the fixed AuthzGym v1.3 instrument under the preregistered
  controlled condition, carrying the section-10.2 claim boundary unchanged; it is
  not general authorization reasoning, adaptive-routing success, SER architecture
  superiority, GitLab transfer, real-world action-value validity, model
  capability, or an `E-*` record, and it promotes no hypothesis. Phase 5 remains
  active and Phase 5B remains blocked.
- Preserved procedural history: three disclosures are preserved as history and
  are not reinterpreted as candidate tuning, because repository evidence supports
  the recorded facts. (1) The pre-ADR-0021 step-0 hashing of 16
  confirmation-named files, already recorded under ADR-0021. (2) The duplicate
  candidate evaluation round: component class hashes and gate numbers are
  byte-identical across both rounds, and the dispositions differ only because the
  study's own firewall check 7 misclassified module-level constant maps as
  mutable caches in the first round. (3) Newly recorded here: Arm A was closed
  after 2 of its 4 budgeted attempts on a written impossibility argument rather
  than by exhausting its budget, which deviates from the section-5.4 rule 3 and
  handoff step-8 precondition that Arm A be exhausted first. The argument is
  corroborated -- an adapter-only change cannot alter the frozen `1.0 + max(0,
  support)` term when every candidate effect is non-positive, and A-1 and A-2
  failed ND-1/ND-2 on exactly those two cases -- and the deviation reduced the
  search rather than relaxing any gate, so it does not affect B-1's measured
  result. It does mean Arm A is under-tested relative to plan, and the
  `estimator-only-change-sufficient` label must continue to be read as
  sufficiency with the adapter arm untested, never as adapter adequacy or as
  attribution of the preserved fresh-confirmation failure. Two bookkeeping
  defects are recorded without altering the frozen artifacts: the candidate
  ledger's `stale_outcome_record` note misdescribes which superseded line was
  stale and points its `authoritative_outcome_record_index` at itself rather than
  at the last `study_outcome` record, and `freeze.report_json_sha256`
  (`444c76c0...`) does not re-derive from `DEVELOPMENT_REPORT.json` under
  canonical re-serialization. The authoritative development outcome is
  `estimator-only-change-sufficient` with passing candidate
  `est-repair-v1.3.1-B-1`, and the identifying hashes for this authorization are
  the component class, component module, and report markdown hashes named in the
  decision, each verified against the artifacts on disk.
- Revisit when: The successor confirmation terminates with a recorded pass or
  failure, or its construction, answerability, firewall, duplication, or freeze
  gate fires a blocker. Any component other than the exact frozen B-1 requires
  its own development study, its own decision, and its own new untouched
  population.

## ADR-0023 -- Accept the AuthzGym model-semantic condition `model-semantic-v1.3.1-N1` and authorize zero-inference implementation only

- Status: accepted
- Date: 2026-09-18
- Context: The controlled chain now supports four things. V1.3 source-local
  semantics are answerable under the bounded fixture grammar. Perfect v1.3
  semantics can drive a frozen downstream component to useful inspection
  rankings. `est-repair-v1.3.1-B-1` passed one-shot untouched successor
  confirmation on the sealed `confirmation_v1_3_1` population (top-1 `0.875`,
  top-2 `1.0`, regret `0.058333`, zero provider calls, seal `463d208f...`).
  Actual model production of the v1.3 semantic state and closed-loop routing
  remain untested. The accepted external research design, the
  choice-set-primary clarification, the three supplied advancement thresholds,
  and Astra's S-7 adjudication are translated normatively in
  `experiments/authzgym_model_semantic_v1_3_1/PREREGISTRATION.md`, with the
  reconstructed cursor and four verified repository contradictions recorded in
  `REPOSITORY_CONTRADICTIONS.md` in the same directory.
- Decision: Accept the finalized model-semantic study package in
  `experiments/authzgym_model_semantic_v1_3_1/` as repository authority for
  condition `model-semantic-v1.3.1-N1`, and authorize **only zero-inference
  mechanical implementation** of that package and its development harness, up
  to and stopping at the preregistered pre-inference freeze boundary. The
  primary endpoint is choice-set preservation: for canonical source `i`, with
  `G_i` the legal targets tied for maximum B-1 value under certified gold
  semantics and `M_i` the same under the actual model response, the decision is
  preserved when `M_i` is non-empty and `M_i` is a subset of `G_i`, at `>= 7/8`
  canonical sources and, in development, separately on each repeat. The
  evaluator canonical ordinal stays evaluator-only and never enters the
  scientific definition of preservation. Effect self-consistency (S-7) is
  adjudicated `diagnostic_only`. No unresolved research-semantic decision
  remains in the package.
- S-7 adjudication: Effect self-consistency remains a mandatory measured and
  reported semantic/interface diagnostic, but has no independent advancement
  threshold and no veto power over development eligibility or
  untouched-confirmation success. It is computed exactly from the model's
  submitted facts and submitted effects using the frozen public v1.3 effect
  truth table and the public candidate family; `C_response` and `C_field` are
  both reported, development and confirmation separately and each development
  repeat separately; every violation is enumerated; invalid and missing
  responses are kept separate and never imputed consistent. It sits outside the
  validity-precedence chain and can never constitute the semantic/interface
  failure that blocks later layers. No response repair and no semantic retry are
  permitted. B-1 consumes the model's actual submitted effect values. Diagnostic
  substitutions never satisfy a gate, and the `D0`/`D3` pair is retained to
  localize the contribution of inconsistencies. An S-7 violation remains a
  semantic error and is preserved in every outcome label, but by itself cannot
  produce `semantic_screen_below_threshold`, suppress the primary or downstream
  result, block `development_eligible`, or block
  `bounded_model_semantic_compatibility_confirmed`. Every other semantic,
  decision, degradation, invariance, mechanical and firewall gate remains
  unchanged, including the directional-effect-versus-gold gate and the
  directional-effect continuity gate.
- Authorized scope: the zero-inference model-condition verification of
  preregistration section 9; construction of the condition's runner, audited
  reader, sealed-input wiring, scorer wiring, error-propagation classification
  and tests; the gold-adequacy computation on the existing development
  population; and the writing of `RESTATED_HASHES.json`,
  `INTEGRITY_BASELINE.json`, `MODEL_CATALOG_SNAPSHOT.json`,
  `MODEL_CONDITION_VERIFICATION.json`, `MODEL_CONDITION.json`,
  `COST_GATE.json`, `GOLD_ADEQUACY_DEVELOPMENT.json`,
  `FROZEN_INPUTS_MODEL_V1_3_1.json` and `FREEZE_CHECKLIST.md`. Implementation
  stops at the freeze boundary.
- Not authorized: model or provider inference of any kind; the 112 development
  calls; confirmation generation, access or inference; any change to AuthzGym
  v1.3 semantics, prompt, schemas, populations or scoring; any change to
  `est-repair-v1.3.1-B-1`; any change to a threshold, denominator or endpoint;
  model substitution or escalation; prompt tuning; retry-policy changes; Jev;
  and closed-loop execution or architecture work. Development inference requires
  a further decision after the freeze checklist passes; confirmation requires
  the separate post-development authorization of preregistration section 14.2
  naming the frozen implementation, development report, model configuration and
  manifest hashes.
- Why: Every link in the controlled chain except one has been exercised under a
  frozen protocol, and the unexercised link is the one the project's central
  question depends on. Changing exactly that link, against an instrument whose
  answerability and firewall pass and a component that has already passed an
  untouched confirmation, is the smallest experiment that can produce
  information about it. Making choice-set preservation primary removes the
  evaluator-only ordinal from the definition of success, so the endpoint
  measures what the model's semantic state does to the decision rather than what
  a private tie-break does to the measurement. Separating acceptance of the
  specification from authorization to call a model keeps the freeze prospective:
  every threshold, denominator and stopping rule is fixed before any response
  exists. Adjudicating S-7 as `diagnostic_only` resolves a real conflict in the
  accepted design, since a zero-tolerance gate on a channel the same design
  declares non-independent could terminate a condition whose primary endpoint
  passed, and the no-semantic-retry rule made such a failure unrecoverable by
  construction.
- Alternatives rejected: authorizing development calls in the same decision that
  accepts the specification; using evaluator-selected-target agreement as the
  primary endpoint; exposing the canonical ordinal to the model or the
  component; gating on effect self-consistency, or giving it a tolerance below
  `1.00`, or dropping its measurement entirely; excluding, repairing or
  retrying a response because it is effect-inconsistent; passing B-1 a
  truth-table-corrected effect vector; claiming or engineering a retroactive
  pass of AuthzGym v1.3 section 16; creating historical v1.3 freeze artifacts
  after the fact or modifying any historical report; reinterpreting,
  superseding or averaging away the historical estimator's preserved
  fresh-confirmation failure; reusing `confirmation_v1_3` or
  `confirmation_v1_3_1` as a model population; running more than one model
  configuration or escalating after failure; reducing the frozen schedule to fit
  the spend ceiling; inventing a statistical null threshold for choice-set
  preservation; reporting any advancement screen as a population estimate;
  rewriting historical seals or access ledgers to match the new hashing and
  logging conventions; and adding closed-loop routing, Jev, representation
  intervention or architecture comparison to this condition.
- Consequences: `experiments/authzgym_model_semantic_v1_3_1/` becomes accepted
  repository authority. The living cursor becomes "model-semantic study
  accepted; zero-inference implementation pending". The already-executed, sealed
  B-1 successor confirmation is recorded in living state as what it is -- a
  separately versioned component/instrument compatibility confirmation -- and
  never as a pass of AuthzGym v1.3 section 16, which was never satisfied and is
  not claimed to have been. For new artifacts, raw-file SHA-256 is the
  authoritative frozen-artifact byte hash; a canonicalized JSON digest, where
  useful, is recorded separately as `canonical_json_sha256`; and multiple digest
  types are never called simply `population_hash`. File-open-granularity access
  logging is required for this condition. Historical ledgers, seals, reports,
  responses, hashes and classifiers are not rewritten. A future pass would
  establish only bounded compatibility of `source artifact -> this
  model/configuration -> v1.3 semantics -> frozen B-1` inside this controlled
  generator; it would not establish authorization competence, general code
  understanding, closed-loop routing, adaptive-routing advantage, SER
  architecture superiority, GitLab transfer or real-world action value, and it
  promotes no concept and creates no `E-*` record. Phase 5 remains active and
  Phase 5B remains blocked.
- Preserved under this decision: `src/ser/authzgym/policies.py`
  (`092a7a87...`), `src/ser/evaluation/authz_v1_3.py` (`60b1cb5d...`),
  `src/ser/authzgym/policies_v1_3_1.py` (`f9c92317...`),
  `src/ser/authzgym/generation.py` (`03bfe556...`),
  `src/ser/authzgym/v1_3_population.py` (`ac4b8d47...`), every artifact under
  `experiments/authzgym_semantic_contract_v1_3/`,
  `experiments/authzgym_estimator_repair_v1_3_1/` and
  `experiments/authzgym_confirmation_v1_3_1/`, and every earlier experiment
  directory. The spent `confirmation_v1_3` population stays unopened. ADR-0019
  and the v1.3 preregistration remain the semantic authority, unchanged and
  unreinterpreted.
- Revisit when: The zero-inference implementation reaches the freeze boundary
  with a complete freeze checklist and a matched manifest, at which point a
  further decision is required before the 112 development calls; or the
  model-condition verification, the cost gate, the gold-adequacy gate, the
  integrity baseline or the access-logging validation fires a blocker; or an
  implementation contradiction appears that this decision and the accepted
  preregistration do not resolve.
