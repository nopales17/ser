<!-- GENERATED FILE: DO NOT EDIT. Run `python3 tools/emit_context.py`. -->

# SER idea map

Readable rendering of canonical `theory/IDEA_MAP.yaml`. Status records maturity; this cold location records authority and preservation, not truth.

Schema version: `1`. Total entries: **60**.

ID families: `F-*` foundation or methodological constraint; `P-*` candidate primitive; `H-*` hypothesis; `M-*` proposed mechanism; `E-*` empirical finding; `Q-*` open question.

Status vocabulary: `seed`, `working`, `accepted`, `experimentally_supported`, `rejected`, `deprecated`

## Foundations (8)

### `F-001` -- Epistemic resource allocation research boundary

- **Status:** `accepted`
- **Statement:** SER investigates how a system might allocate constrained epistemic resources among information acquisition, reasoning, hypothesis work, experimentation, and stopping to improve decision-relevant uncertainty reduction.
- **Why it matters:** This is the accepted project boundary, not a claim that a successful controller already exists.
- **Depends on:** None recorded.
- **Related to:** `F-002`, `F-003`, `F-004`, `P-004`, `P-005`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** `CHARTER.md`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Accepted as project framing only; it carries no empirical success claim.

### `F-002` -- Iterative epistemic control loop

- **Status:** `accepted`
- **Statement:** The accepted problem abstraction separates latent world state, released observations/history, controller epistemic state, legal action capabilities, vector budgets, action results, controller-side state update, first-class stopping, and evaluator-owned outcomes across sequential steps.
- **Why it matters:** It defines the object of study without prescribing a SER solution, state representation, policy objective, or domain pipeline.
- **Depends on:** `F-001`
- **Related to:** `F-006`, `F-007`, `P-001`, `P-004`, `H-001`
- **Would support:** The same semantic contracts instantiate MicroGym, IDS attribution, active software investigation, and a dynamic remote-sensing pressure test without core exceptions.
- **Would falsify:** A target environment whose useful epistemic behavior cannot be represented as iterative state/action/update decisions.
- **Implementation refs:** None recorded.
- **Evidence refs:** `DECISIONS.md`, `theory/CONTROL_PROBLEM.md`, `theory/CONTRACTS.yaml`, `theory/DOMAIN_INSTANTIATIONS.md`
- **Origin:** design synthesis discussion and Phase 2 formalization, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Accepted as a problem-formulation and architectural boundary under ADR-0008 through ADR-0012. It carries no empirical claim that a SER controller is useful.

### `F-003` -- Substrate-independent formulation

- **Status:** `working`
- **Statement:** The intended theory should describe epistemic allocation across model computation, retrieval, execution, testing, sensing, time, and money rather than being tied to LLM tokens.
- **Why it matters:** A substrate-independent formulation is necessary for meaningful cross-domain generalization claims.
- **Depends on:** `F-001`, `P-005`
- **Related to:** `H-010`, `H-012`, `H-013`
- **Would support:** One minimal control formulation predicts useful policies in structurally different environments.
- **Would falsify:** Required concepts or metrics remain inseparable from one substrate after attempted formalization.
- **Implementation refs:** None recorded.
- **Evidence refs:** `theory/CONTROL_PROBLEM.md`, `theory/DOMAIN_INSTANTIATIONS.md`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** The common contracts survive four manual pressure tests, but manual instantiation is not evidence of implemented or empirical generality.

### `F-004` -- Matched-baseline falsification constraint

- **Status:** `accepted`
- **Statement:** SER demonstrates value only if it improves relevant outcomes against simpler strategies under meaningful token, cost, latency, or other resource matching; more calls alone do not count.
- **Why it matters:** It blocks complexity and extra computation from masquerading as architectural intelligence.
- **Depends on:** `F-001`, `P-005`, `P-006`
- **Related to:** `H-016`, `Q-009`
- **Would support:** Matched comparisons against fixed, random, exhaustive, frontier-reasoning, and ordinary-agent baselines.
- **Would falsify:** Simpler matched-budget strategies consistently match or outperform the SER controller.
- **Implementation refs:** None recorded.
- **Evidence refs:** `CHARTER.md`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Accepted methodological constraint. MicroGym comparisons and one exact-likelihood routing comparison have run. Static AuthzGym real-model v1 also ran matched architectures, but its response-contract validation failed, so it supplies no valid architecture comparison or promotion evidence.

### `F-005` -- Authority-maturity separation

- **Status:** `accepted`
- **Statement:** A concept's repository location determines authority while its explicit status determines maturity.
- **Why it matters:** Important speculative ideas can remain durable without silently becoming accepted theory.
- **Depends on:** None recorded.
- **Related to:** `Q-009`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** `tools/check_knowledge_coherence.py`
- **Evidence refs:** `DECISIONS.md`
- **Origin:** ADR-0003, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Governance invariant, not a scientific proposition.

### `F-006` -- Latent-world and evaluator firewall

- **Status:** `accepted`
- **Statement:** Latent world state, legitimately released observations, controller epistemic state, and evaluator-only information are distinct roles; a normal policy can use hidden facts only after authorized observational release.
- **Why it matters:** Partial observability, oracle comparison, and policy evaluation are uninterpretable when hidden truth or evaluator knowledge can leak into decisions.
- **Depends on:** `F-001`, `F-002`
- **Related to:** `P-001`, `P-007`, `F-004`
- **Would support:** Future implementations can enforce and audit role-specific projections across MicroGym and real environments.
- **Would falsify:** A required target environment cannot represent legitimate feedback without collapsing evaluator truth into normal policy access.
- **Implementation refs:** None recorded.
- **Evidence refs:** `DECISIONS.md`, `theory/CONTROL_PROBLEM.md`, `theory/INFORMATION_BOUNDARIES.md`, `theory/CONTRACTS.yaml`
- **Origin:** ADR-0008 and Phase 2 formalization, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Accepted architectural boundary, not a claim that a runtime firewall exists or has been validated.

### `F-007` -- Policy-neutral environment contract

- **Status:** `accepted`
- **Statement:** An environment owns latent dynamics, observation release, legal actions or capabilities, domain execution, and environment termination without consuming controller-private belief state or choosing the epistemically preferred legal action.
- **Why it matters:** Different policies and state representations need to share an environment without the environment silently implementing part of the controller.
- **Depends on:** `F-002`, `F-006`
- **Related to:** `P-004`, `P-005`, `H-001`, `M-011`
- **Would support:** Random, fixed, exhaustive, oracle-reference, and candidate controllers can use the same environment contract under declared access classes.
- **Would falsify:** Useful legal capability generation necessarily requires access to controller-private epistemic state in a target domain.
- **Implementation refs:** None recorded.
- **Evidence refs:** `DECISIONS.md`, `theory/CONTROL_PROBLEM.md`, `theory/CONTRACTS.yaml`, `theory/DOMAIN_INSTANTIATIONS.md`
- **Origin:** ADR-0009 and Phase 2 formalization, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Accepted architectural boundary. Legality may depend on hidden safety constraints but must not encode hidden epistemic recommendations.

### `F-008` -- Evidence-directed environment selection and software research trunk

- **Status:** `accepted`
- **Statement:** GitLab authorization investigation is SER's primary practical research trunk, while MicroGym is a control-mechanism validation instrument, IDS is only a possible semantic bridge, controlled software experimentation is a trunk-aligned intervention instrument, and remote sensing remains a dormant substrate-independence falsification candidate.
- **Why it matters:** It prevents archive convenience or broad generalization ambitions from choosing environments before a concrete unresolved architectural question does.
- **Depends on:** `F-001`, `F-004`
- **Related to:** `H-009`, `H-011`, `H-012`, `H-013`, `M-011`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** `plan/ROADMAP.md`
- **Evidence refs:** `DECISIONS.md`
- **Origin:** Phase 3 steering decision and ADR-0013, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Accepted roadmap governance, not evidence for SER, GitLab, IDS, fuzzing, or cross-domain generalization. A new environment is scheduled only when it can resolve a named uncertainty that current experiments cannot.

## Candidate primitives (9)

### `P-001` -- Explicit epistemic state

- **Status:** `working`
- **Statement:** A policy acts on controller-entitled epistemic state that may be raw public history, a summary, or a structured representation, but is never latent world state or evaluator-only information.
- **Why it matters:** The semantic boundary permits different state and update strategies while keeping policy information entitlement auditable.
- **Depends on:** `F-002`, `F-006`
- **Related to:** `P-002`, `P-003`, `P-007`, `P-008`, `M-010`
- **Would support:** A smaller explicit state is sufficient for near-optimal choices in MicroGym.
- **Would falsify:** Explicit state provides no benefit over history-only baselines when resources are matched.
- **Implementation refs:** None recorded.
- **Evidence refs:** `reference/LEGACY_INVENTORY.yaml`, `reference/IDS_LESSONS.md`, `theory/CONTROL_PROBLEM.md`, `theory/CONTRACTS.yaml`, `DECISIONS.md`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Working candidate primitive. Phase 2 accepts the entitlement and representation-independence contract, not a particular structured schema. Baselines may use history only and maintain no hypotheses, graph, uncertainty calculus, or Scope.

### `P-002` -- Epistemic unit

- **Status:** `rejected`
- **Statement:** A universal semantic supertype unifying observations, hypotheses, and other epistemic content was considered for the minimal core and is not required.
- **Why it matters:** Rejecting the premature ontology keeps observation release, optional controller claims, provenance, and scope semantics distinct until repeated implementations demonstrate a true common invariant.
- **Depends on:** `F-003`
- **Related to:** `P-001`, `P-003`, `P-006`, `P-007`, `Q-003`
- **Would support:** One minimal unit represents observations and claims across multiple environments without lossy special cases.
- **Would falsify:** Cross-domain representations require incompatible semantics hidden behind a superficial common schema.
- **Implementation refs:** None recorded.
- **Evidence refs:** `reference/LEGACY_INVENTORY.yaml`, `theory/CONTROL_PROBLEM.md`, `theory/CONTRACTS.yaml`, `theory/DOMAIN_INSTANTIATIONS.md`, `DECISIONS.md`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Rejected only as a required Phase 2/Phase 3 primitive under ADR-0012. Observation and optional Hypothesis remain separate. A future infrastructure envelope may be reconsidered after multiple domains expose repeated semantics; the stable ID is preserved.

### `P-003` -- Scope

- **Status:** `working`
- **Statement:** Scope is optional domain-typed metadata describing the claimed applicability or support domain of an observation, hypothesis, action, or relation, with any algebra owned by that scope type.
- **Why it matters:** Explicit local applicability may support later gating tests without imposing one universal coordinate system or making scope mandatory for every policy.
- **Depends on:** `F-003`
- **Related to:** `H-003`, `H-010`, `Q-004`, `M-006`
- **Would support:** Scope-aware controllers outperform matched scope-blind controls on environments with local relevance.
- **Would falsify:** Scope annotations add cost without improving decisions in environments designed to require local applicability.
- **Implementation refs:** None recorded.
- **Evidence refs:** `reference/LEGACY_INVENTORY.yaml`, `reference/IDS_LESSONS.md`, `theory/CONTROL_PROBLEM.md`, `theory/CONTRACTS.yaml`, `theory/DOMAIN_INSTANTIATIONS.md`, `DECISIONS.md`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Working optional capability, not required in the first MicroGym. No universal compatible/intersection/contains operation is accepted. Deep archive inspection found no generic implementation, and product neighborhoods remain unrelated environment logic.

### `P-004` -- Epistemic action

- **Status:** `working`
- **Statement:** An epistemic action is a controller choice using a domain-owned schema and payload that can affect available information, transform entitled state, intervene on the world, or explicitly stop; descriptive categories are not a universal enum.
- **Why it matters:** A minimal envelope must represent finite and generative domain actions, internal computation, active tests, failures, and STOP without making their parameters identical.
- **Depends on:** `F-002`
- **Related to:** `P-005`, `H-006`, `H-009`, `Q-002`
- **Would support:** A compact action taxonomy covers optimal or near-optimal policies in early environments.
- **Would falsify:** The taxonomy systematically aliases actions with different transition or cost behavior.
- **Implementation refs:** None recorded.
- **Evidence refs:** `theory/CONTROL_PROBLEM.md`, `theory/CONTRACTS.yaml`, `theory/DOMAIN_INSTANTIATIONS.md`, `DECISIONS.md`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Action identity, schema/kind, and declared payload are universal; target, typed scope, and analytic external/internal/mixed mode are optional. STOP is first-class under ADR-0011.

### `P-005` -- Epistemic resource

- **Status:** `working`
- **Statement:** Episodes declare named epistemic resource dimensions and units; actions incur nonnegative raw resource vectors that aggregate componentwise and may be constrained by partial vector budgets.
- **Why it matters:** The research concerns allocation across heterogeneous constraints, not merely reasoning length.
- **Depends on:** `F-001`
- **Related to:** `P-006`, `F-003`, `F-004`, `H-016`
- **Would support:** Resource accounting predicts tradeoffs and permits matched comparisons.
- **Would falsify:** Purported resource types cannot be made comparable enough to define constraints or baselines.
- **Implementation refs:** None recorded.
- **Evidence refs:** `theory/CONTROL_PROBLEM.md`, `theory/CONTRACTS.yaml`, `DECISIONS.md`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** ADR-0010 accepts vector accounting as architecture. A dimension absent from an episode schema is unmeasured or inapplicable, not zero; experiment-specific scalarization remains optional.

### `P-006` -- Cost, latency, and risk

- **Status:** `working`
- **Statement:** An epistemic action can consume multiple costs and may introduce latency or risk in addition to monetary or compute expense.
- **Why it matters:** Information gain that arrives too late, costs too much, or creates excessive risk may not be useful.
- **Depends on:** `P-004`, `P-005`
- **Related to:** `H-002`, `Q-001`
- **Would support:** Multi-cost policies improve task utility under explicit constraints.
- **Would falsify:** The added dimensions never affect optimal decisions in relevant environments.
- **Implementation refs:** None recorded.
- **Evidence refs:** `theory/CONTROL_PROBLEM.md`, `theory/CONTRACTS.yaml`, `DECISIONS.md`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Raw measurable costs use declared vector dimensions. Latency may also advance a dynamic world; risk and multi-objective outcome semantics remain experiment-specific. No universal combination rule is accepted.

### `P-007` -- Provenance

- **Status:** `working`
- **Statement:** Structured state and compressed summaries should retain links to recoverable source observations and transformation history.
- **Why it matters:** Future decisions and audits may need to recover why a claim exists and which evidence it depends on.
- **Depends on:** `P-001`
- **Related to:** `M-010`, `H-005`
- **Would support:** Provenance links allow compact state while preserving correction and audit behavior.
- **Would falsify:** Maintaining sufficient provenance costs more than any decision benefit it enables in target settings.
- **Implementation refs:** None recorded.
- **Evidence refs:** `reference/LEGACY_INVENTORY.yaml`, `reference/IDS_LESSONS.md`, `theory/CONTROL_PROBLEM.md`, `theory/INFORMATION_BOUNDARIES.md`, `theory/CONTRACTS.yaml`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Every externally acquired observation requires release provenance. Transition state references may be snapshots, hashes, or reconstruction recipes; full universal state serialization is not required.

### `P-008` -- Uncertainty and confidence

- **Status:** `seed`
- **Statement:** Epistemic state may need explicit uncertainty or confidence attached to claims, observations, and alternatives.
- **Why it matters:** Choosing where to investigate next depends on unresolved uncertainty, not only accumulated content.
- **Depends on:** `P-001`
- **Related to:** `H-002`, `Q-002`
- **Would support:** Calibrated uncertainty improves action choice and stopping under matched resources.
- **Would falsify:** Explicit confidence fails to improve routing and introduces systematic miscalibration.
- **Implementation refs:** None recorded.
- **Evidence refs:** `theory/CONTROL_PROBLEM.md`, `theory/CONTRACTS.yaml`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Optional controller/evidence metadata only. No baseline, observation, hypothesis, STOP, or outcome contract requires probabilistic confidence or a universal uncertainty calculus.

### `P-009` -- Signal

- **Status:** `seed`
- **Statement:** Signal is a reserved candidate name for a future epistemic role that would need semantics irreducible to Observation, ActionResult, EpistemicState, relations, or reliability metadata.
- **Why it matters:** Giving Signal stable identity preserves the earlier design question while preventing an undefined second evidence carrier from entering the minimal ontology.
- **Depends on:** `F-002`
- **Related to:** `P-001`, `P-002`, `P-008`, `Q-003`
- **Would support:** A required behavior in multiple environments cannot be represented cleanly by accepted contracts without a distinct Signal role.
- **Would falsify:** Proposed Signal use cases remain ordinary observations, action results, derived state, relations, or reliability annotations.
- **Implementation refs:** None recorded.
- **Evidence refs:** `theory/CONTROL_PROBLEM.md`, `theory/CONTRACTS.yaml`, `reference/LEGACY_INVENTORY.yaml`
- **Origin:** Phase 1 contract recommendation and Phase 2 ontology review, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Explicitly deferred. No irreducible role was found, no legacy implementation exists, and Signal is not required for Phase 3. Do not implement it merely because the name is preserved.

## Hypotheses (18)

### `H-001` -- Allocation organization contributes to inference-time intelligence

- **Status:** `working`
- **Statement:** Inference-time performance may depend partly on how computation and evidence acquisition are organized, not only on their total amount.
- **Why it matters:** This is the central reason to investigate a controller rather than only scaling raw computation.
- **Depends on:** `F-001`, `F-002`
- **Related to:** `H-002`, `H-016`, `M-012`
- **Would support:** A routing controller beats matched-total-compute baselines across preregistered environments.
- **Would falsify:** Matched simpler strategies consistently equal or beat controlled routing.
- **Implementation refs:** `src/ser/policies/adaptive.py`, `src/ser/evaluation/routing.py`
- **Evidence refs:** `experiments/microgym_v1/INTERPRETATION.md`, `experiments/microgym_routing_v1/INTERPRETATION.md`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** MicroGym v1 did not support observation-conditioned routing. Routing-v1 subsequently supported a narrow one-step explicit-likelihood instance: the unchanged candidate captured exact VOA against a same-model open-loop plan. That favorable synthetic instance is insufficient to promote the broad inference-time intelligence claim, which still lacks multi-stage, semantic, matched-compute, and real-domain evidence.

### `H-002` -- Decision-relevant information utility objective

- **Status:** `seed`
- **Statement:** A useful action objective may resemble expected decision-relevant information gain minus cost, latency, and risk.
- **Why it matters:** It offers a candidate rule for answering where the next unit of resource should go.
- **Depends on:** `P-006`, `P-008`
- **Related to:** `Q-001`, `Q-007`
- **Would support:** The objective predicts near-optimal actions in environments with known hidden state and costs.
- **Would falsify:** Policies optimizing it reduce nominal uncertainty while worsening relevant decisions or violating constraints.
- **Implementation refs:** `src/ser/policies/adaptive.py`
- **Evidence refs:** `theory/CONTROL_PROBLEM.md`, `theory/CONTRACTS.yaml`, `experiments/microgym_v1/summary.json`, `experiments/microgym_v1/INTERPRETATION.md`, `experiments/microgym_routing_v1/summary.json`, `experiments/microgym_routing_v1/INTERPRETATION.md`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** MicroGym v1 operationalized one experiment-specific myopic Bayes-risk-minus-cost rule and exposed a stopping/routing interaction. Under routing-v1's fixed one-step equal-cost horizon, the same score matched the exact closed-loop action and captured all available VOA. The objective remains a policy instance, not a universal information utility, and action-value estimation without likelihood tables remains untested.

### `H-003` -- Scope-aware allocation improves efficiency

- **Status:** `seed`
- **Statement:** Representing applicability scope and using it in gating may improve resource efficiency when evidence has local relevance.
- **Why it matters:** It connects the Scope primitive to a measurable allocation benefit.
- **Depends on:** `P-003`
- **Related to:** `H-004`, `M-002`, `M-006`
- **Would support:** A scope-aware policy improves matched-cost vector outcomes over scope-blind, fixed-order, random, cheap-first, and exhaustive controls in a preregistered environment with explicit local relevance.
- **Would falsify:** The apparent benefit disappears after controlling for order, cost, identifiers, formatting, or brute-force compute, or scope overhead costs more than it saves.
- **Implementation refs:** None recorded.
- **Evidence refs:** `theory/CONTROL_PROBLEM.md`, `theory/CONTRACTS.yaml`, `theory/DOMAIN_INSTANTIATIONS.md`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Scope is an optional typed capability. The first MicroGym need not implement it; a separate locality variant and shortcut controls are required before testing this hypothesis.

### `H-004` -- Sparse selective propagation

- **Status:** `seed`
- **Statement:** Selective local propagation of evidence may allocate resources more effectively than broadcasting every item to every hypothesis.
- **Why it matters:** Dense propagation can spend compute on irrelevant or weakly coupled branches.
- **Depends on:** `P-001`, `P-003`
- **Related to:** `M-001`, `M-002`, `M-003`, `M-004`, `M-005`, `M-006`, `M-007`, `M-008`, `M-009`
- **Would support:** Sparse policies retain or improve task outcomes at lower matched cost.
- **Would falsify:** Broadcast baselines are consistently more accurate and no less resource efficient.
- **Implementation refs:** None recorded.
- **Evidence refs:** `reference/LEGACY_INVENTORY.yaml`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** No coupling operator is required by the formal problem or initial MicroGym. Selective propagation remains a hypothesis that could later be implemented as ordinary policy or updater logic; all nine names remain deferred seeds.

### `H-005` -- Decision-sufficient epistemic compression

- **Status:** `seed`
- **Statement:** Raw interaction history may be compressible into smaller decision-relevant structured state while retaining provenance links needed for recovery and audit.
- **Why it matters:** Unbounded history consumes resources and obscures which information actually affects the next decision.
- **Depends on:** `P-001`, `P-007`, `M-010`
- **Related to:** `Q-005`
- **Would support:** Compressed state matches full-history decisions across held-out trajectories with lower resource use.
- **Would falsify:** Discarded history repeatedly changes optimal later actions in ways provenance recovery cannot repair.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** The safe discard boundary is a central open question.

### `H-006` -- Epistemic exploration-exploitation tradeoff

- **Status:** `working`
- **Statement:** Choosing among deepening a hypothesis, gathering more evidence, generating alternatives, and abandoning a branch may be an exploration-exploitation problem.
- **Why it matters:** A controller must balance refining promising branches against avoiding premature convergence.
- **Depends on:** `P-004`
- **Related to:** `H-001`, `Q-007`
- **Would support:** Bandit- or search-like analysis predicts useful branch allocation in MicroGym.
- **Would falsify:** The analogy hides state transitions or information structure essential to performance.
- **Implementation refs:** `src/ser/microgym/families.py`, `src/ser/microgym/routing.py`, `src/ser/policies/adaptive.py`
- **Evidence refs:** `experiments/microgym_v1/adaptivity.json`, `experiments/microgym_v1/INTERPRETATION.md`, `experiments/microgym_routing_v1/summary.json`, `experiments/microgym_routing_v1/INTERPRETATION.md`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** MicroGym v1 included budgeted branch and repeated-evidence families, but the candidate produced zero observation-conditioned branches. Routing-v1 later showed exact one-step branch selection when STOP was removed, but it had no multi-stage depth/breadth tradeoff. The exploration-exploitation analogy remains unvalidated.

### `H-007` -- Observation-reasoning oscillation

- **Status:** `seed`
- **Statement:** Trajectory quality may relate to oscillation rate, the frequency of switching between external acquisition and internal inference, and oscillation depth, the resources spent within a mode before switching.
- **Why it matters:** These measurements may reveal under-observation, over-deliberation, or wasteful mode switching.
- **Depends on:** `P-004`, `P-005`
- **Related to:** `H-008`
- **Would support:** Rate and depth predict outcomes after controlling for total resources and task difficulty.
- **Would falsify:** They add no explanatory or policy value beyond total action counts and costs.
- **Implementation refs:** None recorded.
- **Evidence refs:** `theory/CONTROL_PROBLEM.md`, `theory/CONTRACTS.yaml`, `theory/DOMAIN_INSTANTIATIONS.md`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Optional external_acquisition/internal_computation/mixed action metadata permits trace-derived measurement without prescribing oscillation; mixed actions are not forced into a false binary.

### `H-008` -- Environmental coherence timescale constrains reasoning depth

- **Status:** `seed`
- **Statement:** In changing environments, useful reasoning depth may depend on how long observations remain coherent with the underlying system.
- **Why it matters:** Long internal reasoning can lose value when the world changes faster than the reasoning loop.
- **Depends on:** `H-007`, `P-006`
- **Related to:** `H-013`
- **Would support:** Optimal reasoning depth changes predictably as controlled environment dynamics change.
- **Would falsify:** Coherence timescale fails to explain or predict allocation after matched controls.
- **Implementation refs:** None recorded.
- **Evidence refs:** `theory/CONTROL_PROBLEM.md`, `theory/DOMAIN_INSTANTIATIONS.md`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Dynamic-world transitions, acquisition/release times, and action latency make this testable later. No coherence timescale is part of the core contract.

### `H-009` -- Active observation can manufacture discriminating evidence

- **Status:** `working`
- **Statement:** When a system can choose an action or input before observing the world, active experiments may yield more decision-relevant evidence than passive observation at comparable cost.
- **Why it matters:** Fuzzing and tests change evidence acquisition from selection among sources to intervention design.
- **Depends on:** `P-004`, `P-006`
- **Related to:** `H-012`
- **Would support:** Selected interventions distinguish hypotheses more efficiently than passive or random observations.
- **Would falsify:** Intervention selection provides no gain over cost-matched passive sampling in target environments.
- **Implementation refs:** None recorded.
- **Evidence refs:** `theory/CONTROL_PROBLEM.md`, `theory/DOMAIN_INSTANTIATIONS.md`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** The software pressure test shows the contracts can represent choose input -> world transition -> observation, including mixed world-changing and informative actions. This is formal coverage, not empirical support.

### `H-010` -- Hierarchical boundary selection

- **Status:** `seed`
- **Statement:** Selecting epistemic scope across nested boundaries may be substrate-independent, such as function to runtime or pixel to larger physical system.
- **Why it matters:** The relevant boundary of investigation can move as evidence changes.
- **Depends on:** `P-003`, `F-003`
- **Related to:** `H-003`
- **Would support:** A shared hierarchical selection mechanism improves routing in software and observation domains.
- **Would falsify:** Boundary choice requires unrelated domain-specific machinery with no transferable abstraction.
- **Implementation refs:** None recorded.
- **Evidence refs:** `theory/CONTROL_PROBLEM.md`, `theory/DOMAIN_INSTANTIATIONS.md`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Core contracts permit domain actions with hierarchical targets and optional typed Scope, but require no hierarchy machinery. Cross-domain benefit remains untested.

### `H-011` -- IDS-to-CVE as a possible semantic bridge

- **Status:** `seed`
- **Statement:** A small IDS-to-CVE experiment may serve as a semantic validation bridge only if MicroGym supports adaptive routing yet leaves unresolved whether the advantage survives imperfect semantic evidence.
- **Why it matters:** It could isolate semantic-evidence interpretation without reopening IDS as the main SER research program.
- **Depends on:** `E-001`, `F-004`, `F-008`
- **Related to:** `Q-004`, `H-012`
- **Would support:** A narrow sequential IDS task distinguishes adaptive routing from matched model-aware controls under imperfect semantic evidence.
- **Would falsify:** The archive cannot expose meaningful sequential allocation or a controlled-software environment answers the same question more directly.
- **Implementation refs:** None recorded.
- **Evidence refs:** `reference/IDS_LEGACY.md`, `reference/LEGACY_INVENTORY.yaml`, `reference/IDS_LESSONS.md`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Optional validation instrument, not the primary trunk, not SER, and not imported. It is justified only by a concrete unresolved semantic-transfer question after MicroGym; all archived prompts, rankers, comparators, and construction heuristics remain prior solution logic.

### `H-012` -- Controlled software investigation toward GitLab authorization

- **Status:** `seed`
- **Statement:** The primary practical trunk should progress through minimal controlled software investigation toward GitLab authorization research, testing whether a controller chooses inspections, executions, tests, or fuzzing interventions that manufacture discriminating evidence efficiently.
- **Why it matters:** It tests active evidence generation while advancing the intended authorization-vulnerability research target rather than adding an unrelated validation domain.
- **Depends on:** `H-009`, `F-008`
- **Related to:** `F-003`, `H-011`
- **Would support:** A controller chooses discriminating software interventions more efficiently than matched fixed, random, exhaustive, and non-adaptive strategies in a controlled authorization setting.
- **Would falsify:** The environment measures generic software search skill without isolating epistemic allocation, or matched simple controls erase the claimed advantage.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Primary practical target and roadmap priority only; GitLab is not evidence for SER. After routing-v1 supported a narrow exact-model routing claim, ADR-0014 selected a minimal controlled authorization environment to test semantic action-value estimation. Static Semantic AuthzGym now supplies a static-inspection benchmark calibration, but it does not test active evidence generation and does not support this hypothesis. Real GitLab integration, production fuzzing, and broad vulnerability discovery remain unauthorized.

### `H-013` -- Remote-sensing generalization environment

- **Status:** `seed`
- **Statement:** A later observation environment with spatial and temporal resolution, modality, latency, and measurement uncertainty could test cross-domain generality.
- **Why it matters:** It stresses scope and cost primitives outside software and language-model settings.
- **Depends on:** `F-003`, `P-003`, `P-006`, `P-008`
- **Related to:** `H-008`, `H-010`
- **Would support:** The same formal control primitives transfer with limited domain-specific adaptation.
- **Would falsify:** SER's useful abstractions collapse when observations are physical, delayed, and uncertain.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Dormant substrate-independence falsification candidate, not a planned implementation phase. Introduce it only if a later named architectural uncertainty cannot be resolved within software.

### `H-014` -- SERT learned routing policy

- **Status:** `seed`
- **Statement:** A future learned policy or training regime might learn to route epistemic resources from trajectories and outcomes.
- **Why it matters:** Hand-designed control may eventually be replaced or complemented by learned allocation.
- **Depends on:** `M-012`, `H-001`
- **Related to:** `H-015`
- **Would support:** A learned policy generalizes beyond training environments and beats matched hand-designed baselines.
- **Would falsify:** Learned routing overfits environment artifacts or gains only from extra compute.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** SERT name is provisional. Late-stage only; do not implement.

### `H-015` -- Temporal graph policy or TGNN

- **Status:** `seed`
- **Statement:** If epistemic state becomes a temporal relational graph, a learned graph policy might predict where computation or evidence acquisition should go next.
- **Why it matters:** Relational state could make local coupling and temporal changes explicit to a policy.
- **Depends on:** `P-001`, `H-014`
- **Related to:** `H-004`
- **Would support:** Graph structure yields matched-budget gains over non-graph policies after simpler controllers are established.
- **Would falsify:** Equivalent non-graph policies match performance or the graph representation adds unjustified complexity.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Late-stage speculation; must not drive the first implementation.

### `H-016` -- Resource-normalized SER advantage

- **Status:** `seed`
- **Statement:** A SER controller may achieve better outcome per constrained resource than fixed, random, exhaustive, frontier-reasoning, or ordinary-agent strategies.
- **Why it matters:** This is the eventual performance claim the project would need to demonstrate in explicit scopes.
- **Depends on:** `H-001`, `F-004`
- **Related to:** `Q-009`
- **Would support:** Preregistered resource-matched evaluations with ablations and independent confirmation.
- **Would falsify:** Simpler matched strategies consistently match or beat SER across intended environments.
- **Implementation refs:** `src/ser/policies/adaptive.py`, `src/ser/evaluation/analysis.py`, `src/ser/evaluation/routing.py`, `src/ser/evaluation/routing_analysis.py`, `src/ser/authzgym/policies.py`, `src/ser/authzgym/real_runner.py`, `src/ser/evaluation/authz_analysis.py`, `src/ser/evaluation/authz_real_analysis.py`
- **Evidence refs:** `experiments/microgym_v1/summary.json`, `experiments/microgym_v1/INTERPRETATION.md`, `experiments/microgym_routing_v1/summary.json`, `experiments/microgym_routing_v1/INTERPRETATION.md`, `experiments/authzgym_static_realmodel_v1/summary.json`, `experiments/authzgym_static_realmodel_v1/validation.json`, `experiments/authzgym_static_realmodel_v1/INTERPRETATION.md`, `experiments/authzgym_semantic_contract_v1_2/summary.json`, `experiments/authzgym_semantic_contract_v1_2/validation.json`, `experiments/authzgym_semantic_contract_v1_2/INTERPRETATION.md`, `experiments/authzgym_transport_envelope_v1/summary.json`, `experiments/authzgym_transport_envelope_v1/validation.json`, `experiments/authzgym_transport_envelope_v1/INTERPRETATION.md`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** MicroGym v1 was insufficient for promotion because its matched open-loop gap was small, cost-driven, and non-routing. Routing-v1 adds a favorable one-step exact-model routing result under identical fixed resources, but still lacks semantic evidence, multiple domains, and independent confirmation. Static AuthzGym real-model v1 completed its matched schedule but was classified invalid after 104/192 runs failed the response/resource contract; its 1-1-22 SER/ReAct paired diagnostic cannot support an architecture claim. Development-only transport-envelope v1 established stable transport and a stable semantic wire contract for 128/128 nano calls, but made no architecture comparison and found weak semantic quality. The broad resource-normalized claim remains a seed.

### `H-017` -- Decision-value-conditioned epistemic routing

- **Status:** `working`
- **Statement:** Newly released information should change epistemic resource allocation when it changes the expected value landscape of available actions, rather than merely because posterior belief changed.
- **Why it matters:** It distinguishes decision-relevant adaptation from arbitrary behavioral responsiveness and directs attention to action-value estimation rather than uncertainty alone.
- **Depends on:** `P-001`, `P-004`, `H-002`
- **Related to:** `H-001`, `H-006`, `H-012`, `H-018`, `Q-001`
- **Would support:** Across preregistered positive- and zero-VOA controls, a matched closed-loop policy branches when action values change, avoids spurious branches when they do not, and improves the relevant outcome over the best open-loop plan.
- **Would falsify:** The policy branches on belief changes without value, fails to branch when exact action values change, or loses its advantage when action values must be estimated rather than supplied.
- **Implementation refs:** `src/ser/policies/adaptive.py`, `src/ser/evaluation/routing.py`, `src/ser/evaluation/routing_analysis.py`, `src/ser/authzgym/policies.py`, `src/ser/evaluation/authz_analysis.py`
- **Evidence refs:** `experiments/microgym_routing_v1/PREREGISTRATION.md`, `experiments/microgym_routing_v1/summary.json`, `experiments/microgym_routing_v1/INTERPRETATION.md`, `experiments/authzgym_static_realmodel_v1/summary.json`, `experiments/authzgym_static_realmodel_v1/validation.json`, `experiments/authzgym_static_realmodel_v1/INTERPRETATION.md`, `experiments/authzgym_semantic_contract_v1_2/summary.json`, `experiments/authzgym_semantic_contract_v1_2/validation.json`, `experiments/authzgym_semantic_contract_v1_2/INTERPRETATION.md`, `experiments/authzgym_transport_envelope_v1/summary.json`, `experiments/authzgym_transport_envelope_v1/validation.json`, `experiments/authzgym_transport_envelope_v1/INTERPRETATION.md`
- **Origin:** Phase 4 conceptual synthesis and frozen routing-v1 experiment, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Working hypothesis with one narrowly supportive explicit-likelihood, one-step experiment. Static AuthzGym real-model v1 was not a valid semantic test. Development-only transport-envelope v1 tested no routing architecture, but it removed transport and schema reliability as confounders for the exact 128-call nano schedule. Nano's semantic signal and model-conditioned action compatibility were weak, while the oracle-only perfect-observation diagnostic routed correctly on eight development entries. None of these development diagnostics are architecture evidence. Valid semantic action-value estimation with a capable model, model misspecification, multi-stage routing, and real-domain generality remain untested.

### `H-018` -- Bounded semantic action-value estimation

- **Status:** `working`
- **Statement:** Interpretations of only the authorization-code artifacts already purchased by a controller may contain enough decision-relevant structure to estimate which remaining bounded inspection is most useful without supplied likelihood tables or evaluator labels.
- **Why it matters:** It isolates the estimation step that clean exact-model MicroGym routing assumed and that must work before static semantic routing can claim architectural value.
- **Depends on:** `P-001`, `P-004`, `P-005`, `H-017`, `F-004`
- **Related to:** `H-001`, `H-012`, `H-016`, `Q-001`, `Q-009`
- **Would support:** Under a frozen static authorization benchmark, an actual inexpensive semantic model achieves preregistered fact quality and useful-action ranking, the explicit-value policy routes conditionally, respects zero-value controls, and improves matched decisions or efficiency over fixed and ReAct-like controls.
- **Would falsify:** Purchased-artifact interpretations do not recover the required authorization relations, useful inspection rankings are no better than simple controls, routing is label-sensitive or oracle-dependent, or any apparent advantage disappears under matched evidence and model budgets.
- **Implementation refs:** `src/ser/authzgym`, `src/ser/authzgym/realmodel.py`, `src/ser/authzgym/real_runner.py`, `src/ser/authzgym/semantic_contract.py`, `src/ser/authzgym/semantic_transport.py`, `src/ser/authzgym/tunnel_supervisor.py`, `src/ser/authzgym/supervised_transport.py`, `src/ser/evaluation/authz_artifacts.py`, `src/ser/evaluation/authz_analysis.py`, `src/ser/evaluation/authz_real_analysis.py`, `src/ser/evaluation/authz_contract_analysis.py`, `src/ser/evaluation/authz_transport_analysis.py`, `tools/run_authzgym_static.py`, `tools/verify_authzgym_static.py`, `tools/run_authzgym_realmodel.py`, `tools/verify_authzgym_realmodel.py`, `tools/run_authzgym_semantic_contract.py`, `tools/verify_authzgym_semantic_contract.py`, `tools/run_authzgym_transport_envelope.py`, `tools/verify_authzgym_transport_envelope.py`
- **Evidence refs:** `experiments/authzgym_static_v1_1/PREREGISTRATION.md`, `experiments/authzgym_static_realmodel_v1/PREREGISTRATION.md`, `experiments/authzgym_static_realmodel_v1/summary.json`, `experiments/authzgym_static_realmodel_v1/validation.json`, `experiments/authzgym_static_realmodel_v1/INTERPRETATION.md`, `experiments/authzgym_static_realmodel_v1/IMPLEMENTATION_NOTES.md`, `experiments/authzgym_semantic_contract_v1_2/PREREGISTRATION.md`, `experiments/authzgym_semantic_contract_v1_2/summary.json`, `experiments/authzgym_semantic_contract_v1_2/validation.json`, `experiments/authzgym_semantic_contract_v1_2/INTERPRETATION.md`, `experiments/authzgym_semantic_contract_v1_2/IMPLEMENTATION_NOTES.md`, `experiments/authzgym_transport_envelope_v1/PREREGISTRATION.md`, `experiments/authzgym_transport_envelope_v1/summary.json`, `experiments/authzgym_transport_envelope_v1/validation.json`, `experiments/authzgym_transport_envelope_v1/INTERPRETATION.md`, `experiments/authzgym_transport_envelope_v1/IMPLEMENTATION_NOTES.md`
- **Origin:** Phase 5A Static Semantic AuthzGym design, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** The hypothesis is formalized and its benchmark is implemented. The first actual-model experiment was invalid and semantic-contract v1.2 was transport-unstable. Transport-envelope v1 then completed 128/128 provider calls with transport_stable and contract_stable, making nano's development semantic capability measurable without those confounders. Nano produced semantic_signal_weak: fact precision/recall 0.166667/0.095588, hypothesis-effect precision/recall 0.310606/0.320312, unresolved-relation precision/recall 0.017241/0.001894, and model-conditioned top-1/top-2 0.21875/0.382812 with regret 0.595833. Perfect evaluator observations still allowed the unchanged estimator to achieve top-1/top-2 1.0 and zero regret. This neither promotes nor rejects H-018 because no matched routing architecture was tested and the semantic channel was below threshold; the next smallest test retains contract v1.2 with a stronger inexpensive model.

## Proposed mechanisms (13)

### `M-001` -- RES coupling operator

- **Status:** `seed`
- **Statement:** RES is a preserved candidate operator name for an unresolved form of epistemic coupling or propagation.
- **Why it matters:** Preserving the name prevents loss of an earlier design possibility while withholding invented semantics.
- **Depends on:** `H-004`
- **Related to:** `Q-006`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** `theory/CONTROL_PROBLEM.md`, `theory/CONTRACTS.yaml`
- **Origin:** design synthesis inventory, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Deferred. RES could name state-updater propagation, but no irreducible semantics have been shown beyond an ordinary updater transformation. It is not required for Phase 3; do not implement from the name alone.

### `M-002` -- GATE coupling operator

- **Status:** `seed`
- **Statement:** GATE is a candidate operator for conditionally allowing propagation or resource allocation.
- **Why it matters:** Conditional selection is central to sparse routing.
- **Depends on:** `H-004`
- **Related to:** `H-003`, `Q-006`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** `theory/CONTROL_PROBLEM.md`, `theory/CONTRACTS.yaml`
- **Origin:** design synthesis inventory, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Deferred. Policy routing may gate which legal action is chosen, but environment legality is separately defined by ActionInterface and must not encode a preferred policy. GATE is not required for Phase 3.

### `M-003` -- AMP coupling operator

- **Status:** `seed`
- **Statement:** AMP is a candidate operator for increasing the influence or priority of selected epistemic content.
- **Why it matters:** Some evidence may justify concentrating resources on a branch.
- **Depends on:** `H-004`
- **Related to:** `Q-006`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** `theory/CONTROL_PROBLEM.md`, `theory/CONTRACTS.yaml`
- **Origin:** design synthesis inventory, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Deferred. Increasing influence may be ordinary updater or policy scoring logic; no separate universal operator has been justified. AMP is not required for Phase 3.

### `M-004` -- DAMP coupling operator

- **Status:** `seed`
- **Statement:** DAMP is a candidate operator for reducing the influence or priority of selected epistemic content.
- **Why it matters:** Weak or redundant evidence may deserve less downstream resource.
- **Depends on:** `H-004`
- **Related to:** `Q-006`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** `theory/CONTROL_PROBLEM.md`, `theory/CONTRACTS.yaml`
- **Origin:** design synthesis inventory, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Deferred. Reducing influence may be ordinary updater or policy scoring logic; no separate universal operator has been justified. DAMP is not required for Phase 3.

### `M-005` -- INHIBIT coupling operator

- **Status:** `seed`
- **Statement:** INHIBIT is a candidate operator for suppressing an action, claim, branch, or propagation path.
- **Why it matters:** Contradiction or risk may make some routes inappropriate even if locally salient.
- **Depends on:** `H-004`
- **Related to:** `Q-006`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** `theory/CONTROL_PROBLEM.md`, `theory/CONTRACTS.yaml`
- **Origin:** design synthesis inventory, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Deferred. Suppression could occur in an updater or policy, while hard legality remains an environment responsibility. INHIBIT is not required for Phase 3.

### `M-006` -- SCOPE_FILTER coupling operator

- **Status:** `seed`
- **Statement:** SCOPE_FILTER is a candidate operator for limiting propagation or action eligibility by applicability scope.
- **Why it matters:** It is a possible mechanism connecting scope representation to local routing.
- **Depends on:** `P-003`, `H-004`
- **Related to:** `H-003`, `Q-006`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** `theory/CONTROL_PROBLEM.md`, `theory/CONTRACTS.yaml`
- **Origin:** design synthesis inventory, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Deferred. Scope-aware policy gating is representable with the optional typed Scope capability, but it is not synonymous with environment legality and is not required for the first MicroGym.

### `M-007` -- TOPK coupling operator

- **Status:** `seed`
- **Statement:** TOPK is a candidate operator for retaining only the highest-priority items, branches, or actions under a selection rule.
- **Why it matters:** Hard sparsification may constrain breadth and cost.
- **Depends on:** `H-004`
- **Related to:** `Q-006`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** `theory/CONTROL_PROBLEM.md`, `theory/CONTRACTS.yaml`
- **Origin:** design synthesis inventory, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Deferred. Top-k behavior is presently ordinary policy selection or state compression, not a primitive coupling law. Its score and tie behavior remain unspecified, and it is not required for Phase 3.

### `M-008` -- DEFEAT coupling operator

- **Status:** `seed`
- **Statement:** DEFEAT is a candidate operator for recording that evidence or an argument undercuts a competing claim or branch.
- **Why it matters:** Contradictory evidence may need structured effects beyond scalar confidence reduction.
- **Depends on:** `H-004`
- **Related to:** `Q-006`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** `theory/CONTROL_PROBLEM.md`, `theory/CONTRACTS.yaml`
- **Origin:** design synthesis inventory, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Deferred. A defeat relation may be useful only when an environment exposes optional structured hypotheses or arguments. Hypotheses are not core-required and DEFEAT is not required for Phase 3.

### `M-009` -- PROMOTE coupling operator

- **Status:** `seed`
- **Statement:** PROMOTE is a candidate operator for raising a claim, branch, or action to a more active decision role.
- **Why it matters:** A controller may need an explicit transition from background candidate to resource target.
- **Depends on:** `H-004`
- **Related to:** `Q-006`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** `theory/CONTROL_PROBLEM.md`, `theory/CONTRACTS.yaml`
- **Origin:** design synthesis inventory, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Deferred. Runtime activation or routing priority could be ordinary policy/updater state. This is not concept-maturity promotion, its exact semantics remain unresolved, and it is not required for Phase 3.

### `M-010` -- Epistemic compressor

- **Status:** `seed`
- **Statement:** An epistemic compressor would transform raw history into decision-relevant structured state while preserving links to recoverable evidence.
- **Why it matters:** It could bound context growth without severing auditability or future recovery.
- **Depends on:** `P-001`, `P-007`, `H-005`
- **Related to:** `Q-005`
- **Would support:** A specified compressor preserves future action quality under held-out trajectories.
- **Would falsify:** Compression causes material decision loss that recovery links cannot correct.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** The repository's context generator is project-memory infrastructure, not this runtime mechanism.

### `M-011` -- MicroGym synthetic environment family

- **Status:** `working`
- **Statement:** MicroGym should provide zero-LLM synthetic environments with known hidden state, explicit observation costs, actions with different information value, and computable optimal or near-optimal behavior.
- **Why it matters:** It can isolate whether routing and gating work independently of model capability.
- **Depends on:** `F-002`, `F-004`
- **Related to:** `H-001`, `H-002`, `H-006`
- **Would support:** Controllers recover known allocation structure and beat trivial matched baselines.
- **Would falsify:** The environments cannot distinguish routing quality from task-solving capacity or have no useful baseline oracle.
- **Implementation refs:** `src/ser/microgym`, `src/ser/evaluation`, `tools/run_microgym.py`, `tools/run_microgym_routing.py`, `tools/verify_microgym_routing.py`
- **Evidence refs:** `theory/CONTROL_PROBLEM.md`, `theory/CONTRACTS.yaml`, `theory/DOMAIN_INSTANTIATIONS.md`, `experiments/microgym_v1/population.json`, `experiments/microgym_v1/validation.json`, `experiments/microgym_v1/REPORT.md`, `experiments/microgym_v1/INTERPRETATION.md`, `experiments/microgym_routing_v1/population.json`, `experiments/microgym_routing_v1/validation.json`, `experiments/microgym_routing_v1/REPORT.md`, `experiments/microgym_routing_v1/INTERPRETATION.md`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Implemented as a control-mechanism validation instrument, not the practical research trunk. MicroGym v1 covered stopping, failure, resources, replay, baselines, and exact oracle but showed no conditional routing. The separate immutable routing-v1 benchmark used nine regimes, fixed horizon, exact open/closed values, and zero-VOA controls; it supported only one-step explicit-likelihood routing.

### `M-012` -- SER controller/runtime

- **Status:** `seed`
- **Statement:** SER provisionally denotes a control architecture that selects, targets, times, and stops resource-consuming epistemic actions while maintaining controller-entitled epistemic state.
- **Why it matters:** It names the possible runtime object whose value the project may eventually test.
- **Depends on:** `F-002`, `P-001`, `P-004`, `P-005`, `H-001`
- **Related to:** `H-014`, `Q-008`
- **Would support:** A minimal controller can be specified and evaluated without embedding the result in its design.
- **Would falsify:** The proposed architecture adds no separable behavior beyond an ordinary agent loop.
- **Implementation refs:** None recorded.
- **Evidence refs:** `theory/CONTROL_PROBLEM.md`, `theory/CONTRACTS.yaml`, `theory/INFORMATION_BOUNDARIES.md`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** The semantic role is formalized, but the name and expansion remain provisional. MicroGym v1 implemented an experimental candidate, not a validated or production SER runtime; no broad mechanism claim was promoted.

### `M-013` -- Static Semantic AuthzGym benchmark

- **Status:** `working`
- **Statement:** Static Semantic AuthzGym is an authored, static authorization-code benchmark that exposes bounded artifact inspection, purchased-artifact semantic interpretation, epistemic update, explicit inspection-value estimation, routing, final diagnosis, evaluator truth, and raw resource accounting as separately traceable stages.
- **Why it matters:** It provides the smallest current instrument for testing the semantic estimation gap left by exact-likelihood MicroGym while preserving evaluator and information boundaries.
- **Depends on:** `F-002`, `F-004`, `F-006`, `H-018`
- **Related to:** `H-012`, `H-017`, `Q-009`
- **Would support:** Frozen populations, exact replay, matched budgets, evaluator firewall, purchased-artifact scope, failure decomposition, and identifier/label/order perturbations reproduce before any empirical interpretation.
- **Would falsify:** The benchmark leaks evaluator truth, confounds artifact identity with usefulness, cannot reproduce traces and budgets, or fails to distinguish semantic extraction from routing and decision failures.
- **Implementation refs:** `src/ser/authzgym`, `src/ser/authzgym/realmodel.py`, `src/ser/authzgym/real_runner.py`, `src/ser/authzgym/semantic_contract.py`, `src/ser/authzgym/semantic_transport.py`, `src/ser/authzgym/tunnel_supervisor.py`, `src/ser/authzgym/supervised_transport.py`, `src/ser/evaluation/authz_artifacts.py`, `src/ser/evaluation/authz_analysis.py`, `src/ser/evaluation/authz_real_analysis.py`, `src/ser/evaluation/authz_contract_analysis.py`, `src/ser/evaluation/authz_transport_analysis.py`, `tools/run_authzgym_static.py`, `tools/verify_authzgym_static.py`, `tools/run_authzgym_realmodel.py`, `tools/verify_authzgym_realmodel.py`, `tools/run_authzgym_semantic_contract.py`, `tools/verify_authzgym_semantic_contract.py`, `tools/run_authzgym_transport_envelope.py`, `tools/verify_authzgym_transport_envelope.py`
- **Evidence refs:** `experiments/authzgym_static_v1/FIRST_RUN_FAILURE.json`, `experiments/authzgym_static_v1/IMPLEMENTATION_NOTES.md`, `experiments/authzgym_static_v1_1/PREREGISTRATION.md`, `experiments/authzgym_static_v1_1/validation.json`, `experiments/authzgym_static_v1_1/INTERPRETATION.md`, `experiments/authzgym_static_realmodel_v1/PREREGISTRATION.md`, `experiments/authzgym_static_realmodel_v1/validation.json`, `experiments/authzgym_static_realmodel_v1/summary.json`, `experiments/authzgym_static_realmodel_v1/INTERPRETATION.md`, `experiments/authzgym_semantic_contract_v1_2/PREREGISTRATION.md`, `experiments/authzgym_semantic_contract_v1_2/summary.json`, `experiments/authzgym_semantic_contract_v1_2/validation.json`, `experiments/authzgym_semantic_contract_v1_2/INTERPRETATION.md`, `experiments/authzgym_semantic_contract_v1_2/IMPLEMENTATION_NOTES.md`, `experiments/authzgym_transport_envelope_v1/PREREGISTRATION.md`, `experiments/authzgym_transport_envelope_v1/validation.json`, `experiments/authzgym_transport_envelope_v1/summary.json`, `experiments/authzgym_transport_envelope_v1/INTERPRETATION.md`, `experiments/authzgym_transport_envelope_v1/IMPLEMENTATION_NOTES.md`
- **Origin:** Phase 5A benchmark construction and calibration, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Protocol v1 is preserved as an invalid mock calibration and protocol 1.1 corrects its identifier-dependent test-double defect. Real-model v1 remains an invalid empirical run and semantic-contract v1.2 remains transport-unstable. The separate transport-envelope protocol completed 128/128 nano responses with stable transport and contract mechanics, establishing that the benchmark's v1.2 response channel is measurable on the exact development schedule. Nano semantic_signal_weak and low repeat/transformation exactness are development diagnostics, not architecture evidence. The benchmark remains working; no AuthzGym E-* entry follows and the next run retains v1.2 with a separately preregistered stronger inexpensive model.

## Empirical findings (3)

### `E-001` -- Historical IDS archive provides scoped benchmark artifacts

- **Status:** `experimentally_supported`
- **Statement:** The read-only IDS archive documents a completed, deterministic benchmark separating closed-book vulnerability-shape reconstruction from closed-corpus exact-CVE attribution over frozen artifacts, with explicit negative results and claim limits.
- **Why it matters:** Those properties may make it useful as a future environment, but they do not validate SER or prove sequential routing value.
- **Depends on:** None recorded.
- **Related to:** `H-011`, `Q-004`
- **Would support:** Read-only inventory confirms separable interfaces and reproducible artifacts relevant to an environment adapter.
- **Would falsify:** Deeper inventory shows that usable behavior depends inseparably on IDS-specific assumptions or unavailable artifacts.
- **Implementation refs:** None recorded.
- **Evidence refs:** `reference/IDS_LEGACY.md`, `reference/LEGACY_INVENTORY.yaml`, `reference/IDS_LESSONS.md`, `/Users/paolo/proj/ids-rule-to-cve-inference-archive/README.md`
- **Origin:** read-only IDS archive inspection, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Evidence is historical and IDS-scoped. Phase 1 confirmed reproducible assets and important negative results, but also product/lexical confounds, population corrections, invalid or unrun evaluations, and no holdout. It is not experimental support for any SER hypothesis.

### `E-002` -- MicroGym v1 stopping efficiency without conditional routing

- **Status:** `experimentally_supported`
- **Statement:** On the frozen 728-episode MicroGym v1 population, the public-model myopic candidate lowered mean experiment-specific combined objective to 0.303159 versus 0.465220-0.481049 for five simple controls and 0.311429 for a matched model-aware open-loop control, but it had worse decision loss than every simple control, gained only 0.008269 against open-loop through lower expenditure, and exhibited zero observation-conditioned branches across 20 eligible counterfactual decision nodes.
- **Why it matters:** It separates a valid cost-sensitive stopping result from the stronger adaptive-routing claim that Phase 3 intended to test.
- **Depends on:** `F-004`, `F-006`, `M-011`
- **Related to:** `H-001`, `H-002`, `H-006`, `H-016`, `Q-007`, `Q-009`
- **Would support:** Exact replay, artifact hashes, seed isolation, evaluator firewall, matched open-loop comparison, and the counterfactual branch audit remain valid for the frozen population.
- **Would falsify:** A replay/hash failure, hidden-information leak, seed coupling, population change, or incorrect branch enumeration invalidates the scoped finding.
- **Implementation refs:** `src/ser`, `tools/run_microgym.py`, `tools/audit_microgym_adaptivity.py`
- **Evidence refs:** `experiments/microgym_v1/PREREGISTRATION.md`, `experiments/microgym_v1/population.json`, `experiments/microgym_v1/runs.jsonl`, `experiments/microgym_v1/oracle.jsonl`, `experiments/microgym_v1/summary.json`, `experiments/microgym_v1/validation.json`, `experiments/microgym_v1/adaptivity.json`, `experiments/microgym_v1/REPORT.md`, `experiments/microgym_v1/INTERPRETATION.md`
- **Origin:** frozen MicroGym v1 experiment, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Narrow synthetic finding only. The preregistered mechanical classifier said strong_enough_to_continue because it lacked a positive-adaptivity admission requirement; scientific interpretation is narrow. It does not promote H-001, H-016, semantic reasoning, scope, coupling, IDS transfer, software investigation, or GitLab research.

### `E-003` -- MicroGym routing-v1 captures one-step explicit-model adaptivity

- **Status:** `experimentally_supported`
- **Statement:** On the frozen nine-regime, 1,152-episode MicroGym routing-v1 population, the unchanged public-model candidate branched at all 6 eligible conditional nodes, matched the exact closed-loop route at all 6, made 0 spurious branches across 3 zero-VOA controls, and achieved VOA-weighted Adaptivity Capture 1.0 under a fixed one-acquisition horizon with no STOP.
- **Why it matters:** It cleanly demonstrates that the existing belief-conditioned action score can use a realized observation to recover exact one-step decision value unavailable to the best same-model open-loop plan when likelihood tables are supplied.
- **Depends on:** `F-004`, `F-006`, `M-011`
- **Related to:** `H-001`, `H-002`, `H-006`, `H-017`, `Q-009`
- **Would support:** The population, exact open/closed calculations, fixed-horizon traces, branch audit, seed/access checks, and invariance tests reproduce from the frozen manifest.
- **Would falsify:** A replay/hash failure, hidden-information leak, incorrect open-loop commitment, adaptive STOP path, oracle error, or failed label/order invariance invalidates the scoped finding.
- **Implementation refs:** `src/ser/microgym/routing.py`, `src/ser/evaluation/routing.py`, `src/ser/evaluation/routing_analysis.py`, `tools/run_microgym_routing.py`, `tools/verify_microgym_routing.py`
- **Evidence refs:** `experiments/microgym_routing_v1/PREREGISTRATION.md`, `experiments/microgym_routing_v1/population.json`, `experiments/microgym_routing_v1/oracle.jsonl`, `experiments/microgym_routing_v1/runs.jsonl`, `experiments/microgym_routing_v1/summary.json`, `experiments/microgym_routing_v1/validation.json`, `experiments/microgym_routing_v1/REPORT.md`, `experiments/microgym_routing_v1/INTERPRETATION.md`, `experiments/microgym_routing_v1/IMPLEMENTATION_NOTES.md`
- **Origin:** frozen MicroGym routing-v1 experiment, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Narrow synthetic finding only. Exact VOA ranged from 0 to 0.2025; candidate expected advantage averaged 0.140083 on positive regimes, and all policies spent the same raw resource vector. The one-step score is aligned with the one-step horizon. The finding does not promote H-001 or H-016 and does not establish semantic value estimation, multi-stage planning, IDS or GitLab transfer, or general SER value.

## Open questions (9)

### `Q-001` -- What objective should the controller optimize?

- **Status:** `working`
- **Statement:** How should a controller value decision quality and information under vector cost, latency, risk, and partially ordered resource constraints without assuming one universal scalarization?
- **Why it matters:** Different objectives can choose different actions and create different stopping behavior.
- **Depends on:** `H-002`, `P-006`
- **Related to:** `Q-007`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** `theory/CONTROL_PROBLEM.md`, `theory/CONTRACTS.yaml`, `experiments/microgym_v1/INTERPRETATION.md`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Phase 2 settled raw nonnegative vector accounting and preregistration of any scalarization or Pareto rule. MicroGym v1 showed that a scalar combined-objective win can coincide with worse decision loss and no adaptive routing, so the policy objective and admission rule remain unresolved.

### `Q-002` -- What is the minimal explicit epistemic state?

- **Status:** `working`
- **Statement:** Beyond the accepted minimum entitlement, update, identity, and provenance invariants, which observations, hypotheses, contradictions, uncertainties, scopes, and summaries are useful to represent for control?
- **Why it matters:** Too little state loses decision information; too much recreates unbounded history.
- **Depends on:** `P-001`
- **Related to:** `P-008`, `Q-003`, `Q-005`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** `src/ser/policies/adaptive.py`, `src/ser/evaluation/runner.py`
- **Evidence refs:** `theory/CONTROL_PROBLEM.md`, `theory/CONTRACTS.yaml`, `experiments/microgym_v1/summary.json`, `experiments/microgym_v1/adaptivity.json`, `experiments/microgym_v1/INTERPRETATION.md`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Phase 2 accepted the minimum semantics of controller-entitled epistemic state without requiring hypotheses, confidence, graphs, or a single representation. Useful additional structure remains empirical and domain-sensitive.

### `Q-003` -- Should epistemic content share a common schema?

- **Status:** `working`
- **Statement:** Is a future common envelope for observations, hypotheses, results, and other epistemic content useful, and which metadata or relations—if any—are truly substrate-independent?
- **Why it matters:** Premature schema commitment could encode a single domain as universal theory.
- **Depends on:** `P-002`
- **Related to:** `Q-002`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** `theory/CONTROL_PROBLEM.md`, `theory/CONTRACTS.yaml`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Phase 2 rejected a universal EpistemicUnit from the minimal core and kept Observation plus optional Hypothesis as distinct roles. A later common envelope remains open if implementation evidence warrants it.

### `Q-004` -- What, if anything, should transfer from IDS?

- **Status:** `working`
- **Statement:** Which IDS archive components should be reused unchanged, generalized, treated only as evidence or inspiration, or discarded, including any interval/scope work?
- **Why it matters:** Unreviewed transfer could contaminate SER with domain-specific assumptions or mistaken validation claims.
- **Depends on:** `E-001`, `H-011`
- **Related to:** `P-003`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** `reference/IDS_LEGACY.md`, `reference/LEGACY_INVENTORY.yaml`, `reference/IDS_LESSONS.md`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Phase 1 found zero components fit for unchanged reuse. Eleven patterns merit clean SER-owned reimplementation after contracts exist; IDS assets remain deferred environment/evaluator material; prior solution logic and domain schemas stay excluded. Future import still requires an explicit decision.

### `Q-005` -- What can an epistemic compressor discard safely?

- **Status:** `working`
- **Statement:** What information can be removed from raw history without harming future epistemic decisions, correction, or audit?
- **Why it matters:** This determines whether compression can remain both useful and recoverable.
- **Depends on:** `H-005`, `M-010`
- **Related to:** `P-007`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** No discard policy is accepted.

### `Q-006` -- What are the coupling operators' semantics?

- **Status:** `seed`
- **Statement:** What precise inputs, outputs, algebra, conflict behavior, scope rules, and costs should RES, GATE, AMP, DAMP, INHIBIT, SCOPE_FILTER, TOPK, DEFEAT, and PROMOTE have?
- **Why it matters:** Operator names without semantics cannot support implementation or falsifiable comparison.
- **Depends on:** `M-001`, `M-002`, `M-003`, `M-004`, `M-005`, `M-006`, `M-007`, `M-008`, `M-009`
- **Related to:** `H-004`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** `reference/LEGACY_INVENTORY.yaml`, `theory/CONTROL_PROBLEM.md`, `theory/CONTRACTS.yaml`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** All nine names remain cold, deferred, and unnecessary for the first MicroGym. Phase 2 classified possible future roles but found no irreducible semantics; exact archive search likewise found no executable or documented SER operator definitions. APF/APF2 filters must not fill the gap by analogy.

### `Q-007` -- When should epistemic work stop?

- **Status:** `working`
- **Statement:** Which policy stopping rule best balances submission or abstention quality against expected remaining value, latency, vector cost, and risk, and how should stopping regret be measured?
- **Why it matters:** Stopping is an epistemic action and central to resource efficiency.
- **Depends on:** `H-002`, `P-004`
- **Related to:** `H-006`, `Q-001`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** `theory/CONTROL_PROBLEM.md`, `theory/CONTRACTS.yaml`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** MicroGym v1 made exact stopping regret computable. Its myopic rule eliminated post-sufficiency acquisitions but stopped prematurely in 30/728 episodes and suppressed all observation-conditioned routing; stopping remains an open policy question.

### `Q-008` -- Are SER and SERT the right names?

- **Status:** `seed`
- **Statement:** The project name, the expansion of SER, and the future SERT policy/training name remain provisional.
- **Why it matters:** Terminology should follow conceptual clarity rather than constrain it.
- **Depends on:** `M-012`, `H-014`
- **Related to:** None recorded.
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Renaming should preserve these stable IDs.

### `Q-009` -- What evidence warrants scientific promotion?

- **Status:** `working`
- **Statement:** Which cross-environment evidence, matched baselines, ablations, holdouts, uncertainty analyses, and independent confirmations warrant promoting a SER hypothesis?
- **Why it matters:** Promotion thresholds must resist development-set overfitting and broad claims from narrow evidence.
- **Depends on:** `F-004`, `F-005`, `H-016`
- **Related to:** None recorded.
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** `CHARTER.md`, `theory/CONTROL_PROBLEM.md`, `theory/DOMAIN_INSTANTIATIONS.md`, `experiments/microgym_v1/INTERPRETATION.md`, `experiments/microgym_routing_v1/PREREGISTRATION.md`, `experiments/microgym_routing_v1/INTERPRETATION.md`, `experiments/authzgym_static_v1_1/PREREGISTRATION.md`, `experiments/authzgym_static_v1_1/validation.json`, `experiments/authzgym_static_v1_1/INTERPRETATION.md`, `experiments/authzgym_static_realmodel_v1/PREREGISTRATION.md`, `experiments/authzgym_static_realmodel_v1/validation.json`, `experiments/authzgym_static_realmodel_v1/INTERPRETATION.md`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** MicroGym v1 exposed an admission-rule defect; routing-v1 corrected it prospectively. Static AuthzGym v1 then exposed identifier-sensitive mock degradation, which protocol 1.1 corrected before any actual-model result. Real-model v1 subsequently completed every scheduled condition but its frozen classifier returned invalid because response/run validity failed. Preserving all three failures prevents partial diagnostics from becoming promotion evidence. Broader promotion still requires a valid semantic, multi-stage, resource-accounted, and independently confirmed result.
