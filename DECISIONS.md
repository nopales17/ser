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
