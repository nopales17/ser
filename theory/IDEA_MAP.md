<!-- GENERATED FILE: DO NOT EDIT. Run `python3 tools/emit_context.py`. -->

# SER idea map

Readable rendering of canonical `theory/IDEA_MAP.yaml`. Status records maturity; this cold location records authority and preservation, not truth.

Schema version: `1`. Total entries: **51**.

ID families: `F-*` foundation or methodological constraint; `P-*` candidate primitive; `H-*` hypothesis; `M-*` proposed mechanism; `E-*` empirical finding; `Q-*` open question.

Status vocabulary: `seed`, `working`, `accepted`, `experimentally_supported`, `rejected`, `deprecated`

## Foundations (5)

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

- **Status:** `working`
- **Statement:** A useful starting abstraction is state -> choose epistemic action -> obtain result -> update state -> choose again.
- **Why it matters:** It identifies the object to formalize while leaving the state, policy, transition, and stopping rule open.
- **Depends on:** `F-001`
- **Related to:** `P-001`, `P-004`, `H-001`
- **Would support:** A formal control problem that covers multiple environments without domain-specific exceptions.
- **Would falsify:** A target environment whose useful epistemic behavior cannot be represented as iterative state/action/update decisions.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Working abstraction, not a validated architecture.

### `F-003` -- Substrate-independent formulation

- **Status:** `working`
- **Statement:** The intended theory should describe epistemic allocation across model computation, retrieval, execution, testing, sensing, time, and money rather than being tied to LLM tokens.
- **Why it matters:** A substrate-independent formulation is necessary for meaningful cross-domain generalization claims.
- **Depends on:** `F-001`, `P-005`
- **Related to:** `H-010`, `H-012`, `H-013`
- **Would support:** One minimal control formulation predicts useful policies in structurally different environments.
- **Would falsify:** Required concepts or metrics remain inseparable from one substrate after attempted formalization.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** An aspiration under investigation, not demonstrated generality.

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
- **Notes:** Accepted methodological constraint; no comparison has run.

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

## Candidate primitives (8)

### `P-001` -- Explicit epistemic state

- **Status:** `working`
- **Statement:** A controller may require explicit state containing observations, hypotheses, claims, unknowns, contradictions, uncertainty, provenance, scope, available actions, and costs.
- **Why it matters:** Allocation decisions require a representation of what is known, unknown, conflicting, and possible next.
- **Depends on:** `F-002`
- **Related to:** `P-002`, `P-003`, `P-007`, `P-008`, `M-010`
- **Would support:** A smaller explicit state is sufficient for near-optimal choices in MicroGym.
- **Would falsify:** Explicit state provides no benefit over history-only baselines when resources are matched.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** The listed fields are candidates, not a frozen schema.

### `P-002` -- Epistemic unit

- **Status:** `seed`
- **Statement:** Knowledge and evidence may need a substrate-independent unit carrying content, type, scope, provenance, confidence, time, acquisition cost, and relations.
- **Why it matters:** A common unit could make heterogeneous evidence comparable and routable.
- **Depends on:** `F-003`
- **Related to:** `P-001`, `P-003`, `P-006`, `P-007`, `Q-003`
- **Would support:** One minimal unit represents observations and claims across multiple environments without lossy special cases.
- **Would falsify:** Cross-domain representations require incompatible semantics hidden behind a superficial common schema.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Do not freeze the schema before Phase 2.

### `P-003` -- Scope

- **Status:** `working`
- **Statement:** Evidence and hypotheses may need explicit semantic, structural, temporal, spatial, and observational applicability boundaries.
- **Why it matters:** Unscoped evidence can be propagated or trusted outside the conditions where it is informative.
- **Depends on:** `P-002`
- **Related to:** `H-003`, `H-010`, `Q-004`, `M-006`
- **Would support:** Scope-aware controllers outperform matched scope-blind controls on environments with local relevance.
- **Would falsify:** Scope annotations add cost without improving decisions in environments designed to require local applicability.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Candidate primitive. Reuse of any IDS interval/scope work is unresolved.

### `P-004` -- Epistemic action

- **Status:** `working`
- **Statement:** Candidate actions include observe, retrieve, transform, hypothesize, compare, test, deepen, broaden, revise, abandon, and stop.
- **Why it matters:** The controller's choice space must distinguish ways of acquiring evidence from ways of transforming belief.
- **Depends on:** `F-002`
- **Related to:** `P-005`, `H-006`, `H-009`, `Q-002`
- **Would support:** A compact action taxonomy covers optimal or near-optimal policies in early environments.
- **Would falsify:** The taxonomy systematically aliases actions with different transition or cost behavior.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Action boundaries and granularity remain open.

### `P-005` -- Epistemic resource

- **Status:** `working`
- **Statement:** Epistemic resources may include tokens, model tiers, compute, retrieval, inspection, execution, tests, observations, time, and money.
- **Why it matters:** The research concerns allocation across heterogeneous constraints, not merely reasoning length.
- **Depends on:** `F-001`
- **Related to:** `P-006`, `F-003`, `F-004`, `H-016`
- **Would support:** Resource accounting predicts tradeoffs and permits matched comparisons.
- **Would falsify:** Purported resource types cannot be made comparable enough to define constraints or baselines.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** No universal scalar conversion is assumed.

### `P-006` -- Cost, latency, and risk

- **Status:** `working`
- **Statement:** An epistemic action can consume multiple costs and may introduce latency or risk in addition to monetary or compute expense.
- **Why it matters:** Information gain that arrives too late, costs too much, or creates excessive risk may not be useful.
- **Depends on:** `P-004`, `P-005`
- **Related to:** `H-002`, `Q-001`
- **Would support:** Multi-cost policies improve task utility under explicit constraints.
- **Would falsify:** The added dimensions never affect optimal decisions in relevant environments.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** The combination rule is unresolved.

### `P-007` -- Provenance

- **Status:** `working`
- **Statement:** Structured state and compressed summaries should retain links to recoverable source observations and transformation history.
- **Why it matters:** Future decisions and audits may need to recover why a claim exists and which evidence it depends on.
- **Depends on:** `P-001`, `P-002`
- **Related to:** `M-010`, `H-005`
- **Would support:** Provenance links allow compact state while preserving correction and audit behavior.
- **Would falsify:** Maintaining sufficient provenance costs more than any decision benefit it enables in target settings.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Raw chat transcript accumulation is not the intended provenance system.

### `P-008` -- Uncertainty and confidence

- **Status:** `seed`
- **Statement:** Epistemic state may need explicit uncertainty or confidence attached to claims, observations, and alternatives.
- **Why it matters:** Choosing where to investigate next depends on unresolved uncertainty, not only accumulated content.
- **Depends on:** `P-001`
- **Related to:** `H-002`, `Q-002`
- **Would support:** Calibrated uncertainty improves action choice and stopping under matched resources.
- **Would falsify:** Explicit confidence fails to improve routing and introduces systematic miscalibration.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** No probabilistic semantics are fixed.

## Hypotheses (16)

### `H-001` -- Allocation organization contributes to inference-time intelligence

- **Status:** `working`
- **Statement:** Inference-time performance may depend partly on how computation and evidence acquisition are organized, not only on their total amount.
- **Why it matters:** This is the central reason to investigate a controller rather than only scaling raw computation.
- **Depends on:** `F-001`, `F-002`
- **Related to:** `H-002`, `H-016`, `M-012`
- **Would support:** A routing controller beats matched-total-compute baselines across preregistered environments.
- **Would falsify:** Matched simpler strategies consistently equal or beat controlled routing.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Central hypothesis; currently unsupported by SER experiments.

### `H-002` -- Decision-relevant information utility objective

- **Status:** `seed`
- **Statement:** A useful action objective may resemble expected decision-relevant information gain minus cost, latency, and risk.
- **Why it matters:** It offers a candidate rule for answering where the next unit of resource should go.
- **Depends on:** `P-006`, `P-008`
- **Related to:** `Q-001`, `Q-007`
- **Would support:** The objective predicts near-optimal actions in environments with known hidden state and costs.
- **Would falsify:** Policies optimizing it reduce nominal uncertainty while worsening relevant decisions or violating constraints.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Exact terms, scaling, and estimators are unresolved.

### `H-003` -- Scope-aware allocation improves efficiency

- **Status:** `seed`
- **Statement:** Representing applicability scope and using it in gating may improve resource efficiency when evidence has local relevance.
- **Why it matters:** It connects the Scope primitive to a measurable allocation benefit.
- **Depends on:** `P-003`
- **Related to:** `H-004`, `M-002`, `M-006`
- **Would support:** A scope-aware ablation improves matched-cost outcomes over scope-blind routing.
- **Would falsify:** Scope-aware gating fails in environments constructed with explicit local relevance or costs more than it saves.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Do not confuse with implementing a Scope class.

### `H-004` -- Sparse selective propagation

- **Status:** `seed`
- **Statement:** Selective local propagation of evidence may allocate resources more effectively than broadcasting every item to every hypothesis.
- **Why it matters:** Dense propagation can spend compute on irrelevant or weakly coupled branches.
- **Depends on:** `P-001`, `P-003`
- **Related to:** `M-001`, `M-002`, `M-003`, `M-004`, `M-005`, `M-006`, `M-007`, `M-008`, `M-009`
- **Would support:** Sparse policies retain or improve task outcomes at lower matched cost.
- **Would falsify:** Broadcast baselines are consistently more accurate and no less resource efficient.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** No coupling operator has defined semantics or implementation.

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
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** May be an analogy rather than the final formalism.

### `H-007` -- Observation-reasoning oscillation

- **Status:** `seed`
- **Statement:** Trajectory quality may relate to oscillation rate, the frequency of switching between external acquisition and internal inference, and oscillation depth, the resources spent within a mode before switching.
- **Why it matters:** These measurements may reveal under-observation, over-deliberation, or wasteful mode switching.
- **Depends on:** `P-004`, `P-005`
- **Related to:** `H-008`
- **Would support:** Rate and depth predict outcomes after controlling for total resources and task difficulty.
- **Would falsify:** They add no explanatory or policy value beyond total action counts and costs.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Initially measured trajectory properties, never fixed architectural constants.

### `H-008` -- Environmental coherence timescale constrains reasoning depth

- **Status:** `seed`
- **Statement:** In changing environments, useful reasoning depth may depend on how long observations remain coherent with the underlying system.
- **Why it matters:** Long internal reasoning can lose value when the world changes faster than the reasoning loop.
- **Depends on:** `H-007`, `P-006`
- **Related to:** `H-013`
- **Would support:** Optimal reasoning depth changes predictably as controlled environment dynamics change.
- **Would falsify:** Coherence timescale fails to explain or predict allocation after matched controls.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Hypothesis, not a law.

### `H-009` -- Active observation can manufacture discriminating evidence

- **Status:** `working`
- **Statement:** When a system can choose an action or input before observing the world, active experiments may yield more decision-relevant evidence than passive observation at comparable cost.
- **Why it matters:** Fuzzing and tests change evidence acquisition from selection among sources to intervention design.
- **Depends on:** `P-004`, `P-006`
- **Related to:** `H-012`
- **Would support:** Selected interventions distinguish hypotheses more efficiently than passive or random observations.
- **Would falsify:** Intervention selection provides no gain over cost-matched passive sampling in target environments.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Passive: world -> observation. Active: choose input -> world/system -> observation.

### `H-010` -- Hierarchical boundary selection

- **Status:** `seed`
- **Statement:** Selecting epistemic scope across nested boundaries may be substrate-independent, such as function to runtime or pixel to larger physical system.
- **Why it matters:** The relevant boundary of investigation can move as evidence changes.
- **Depends on:** `P-003`, `F-003`
- **Related to:** `H-003`
- **Would support:** A shared hierarchical selection mechanism improves routing in software and observation domains.
- **Would falsify:** Boundary choice requires unrelated domain-specific machinery with no transferable abstraction.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Candidate generalization hypothesis.

### `H-011` -- IDS-to-CVE as a future controlled environment

- **Status:** `seed`
- **Statement:** The completed IDS-to-CVE benchmark may be adaptable into an early real SER environment with partial evidence and known ground truth.
- **Why it matters:** It could provide a real task after synthetic control experiments while preserving evaluation discipline.
- **Depends on:** `E-001`, `F-004`
- **Related to:** `Q-004`
- **Would support:** A Phase 1 inventory finds reusable, separable environment interfaces without importing IDS-specific theory.
- **Would falsify:** The benchmark's task and artifacts cannot expose meaningful sequential epistemic allocation choices.
- **Implementation refs:** None recorded.
- **Evidence refs:** `reference/IDS_LEGACY.md`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Candidate environment/adaptor only; not SER and not yet imported.

### `H-012` -- Software and fuzzing environment

- **Status:** `seed`
- **Statement:** A later software environment could test SER where the controller actively generates evidence through execution, tests, or fuzzing.
- **Why it matters:** It exercises intervention choice rather than retrieval-only evidence acquisition.
- **Depends on:** `H-009`
- **Related to:** `F-003`
- **Would support:** A controller chooses discriminating executions more efficiently than random or exhaustive strategies.
- **Would falsify:** The environment measures software search skill without isolating epistemic allocation.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** No fuzzer or software adapter should be implemented in current phases.

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
- **Notes:** Generalization test, not a near-term target.

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
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** No SER evidence exists.

## Proposed mechanisms (12)

### `M-001` -- RES coupling operator

- **Status:** `seed`
- **Statement:** RES is a preserved candidate operator name for an unresolved form of epistemic coupling or propagation.
- **Why it matters:** Preserving the name prevents loss of an earlier design possibility while withholding invented semantics.
- **Depends on:** `H-004`
- **Related to:** `Q-006`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis inventory, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Exact semantics unresolved; do not implement.

### `M-002` -- GATE coupling operator

- **Status:** `seed`
- **Statement:** GATE is a candidate operator for conditionally allowing propagation or resource allocation.
- **Why it matters:** Conditional selection is central to sparse routing.
- **Depends on:** `H-004`
- **Related to:** `H-003`, `Q-006`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis inventory, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Exact semantics unresolved; do not implement.

### `M-003` -- AMP coupling operator

- **Status:** `seed`
- **Statement:** AMP is a candidate operator for increasing the influence or priority of selected epistemic content.
- **Why it matters:** Some evidence may justify concentrating resources on a branch.
- **Depends on:** `H-004`
- **Related to:** `Q-006`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis inventory, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Exact semantics unresolved; do not implement.

### `M-004` -- DAMP coupling operator

- **Status:** `seed`
- **Statement:** DAMP is a candidate operator for reducing the influence or priority of selected epistemic content.
- **Why it matters:** Weak or redundant evidence may deserve less downstream resource.
- **Depends on:** `H-004`
- **Related to:** `Q-006`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis inventory, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Exact semantics unresolved; do not implement.

### `M-005` -- INHIBIT coupling operator

- **Status:** `seed`
- **Statement:** INHIBIT is a candidate operator for suppressing an action, claim, branch, or propagation path.
- **Why it matters:** Contradiction or risk may make some routes inappropriate even if locally salient.
- **Depends on:** `H-004`
- **Related to:** `Q-006`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis inventory, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Exact semantics unresolved; do not implement.

### `M-006` -- SCOPE_FILTER coupling operator

- **Status:** `seed`
- **Statement:** SCOPE_FILTER is a candidate operator for limiting propagation or action eligibility by applicability scope.
- **Why it matters:** It is a possible mechanism connecting scope representation to local routing.
- **Depends on:** `P-003`, `H-004`
- **Related to:** `H-003`, `Q-006`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis inventory, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Exact semantics unresolved; do not implement.

### `M-007` -- TOPK coupling operator

- **Status:** `seed`
- **Statement:** TOPK is a candidate operator for retaining only the highest-priority items, branches, or actions under a selection rule.
- **Why it matters:** Hard sparsification may constrain breadth and cost.
- **Depends on:** `H-004`
- **Related to:** `Q-006`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis inventory, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Exact semantics and selection score unresolved; do not implement.

### `M-008` -- DEFEAT coupling operator

- **Status:** `seed`
- **Statement:** DEFEAT is a candidate operator for recording that evidence or an argument undercuts a competing claim or branch.
- **Why it matters:** Contradictory evidence may need structured effects beyond scalar confidence reduction.
- **Depends on:** `H-004`
- **Related to:** `Q-006`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis inventory, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Exact semantics unresolved; do not implement.

### `M-009` -- PROMOTE coupling operator

- **Status:** `seed`
- **Statement:** PROMOTE is a candidate operator for raising a claim, branch, or action to a more active decision role.
- **Why it matters:** A controller may need an explicit transition from background candidate to resource target.
- **Depends on:** `H-004`
- **Related to:** `Q-006`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis inventory, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Not the same as maturity promotion; exact runtime semantics unresolved.

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
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Phase 3 target; no environment implemented.

### `M-012` -- SER controller/runtime

- **Status:** `seed`
- **Statement:** SER provisionally denotes a control architecture that maintains structured epistemic state and routes resources among epistemic actions.
- **Why it matters:** It names the possible runtime object whose value the project may eventually test.
- **Depends on:** `F-002`, `P-001`, `P-004`, `P-005`, `H-001`
- **Related to:** `H-014`, `Q-008`
- **Would support:** A minimal controller can be specified and evaluated without embedding the result in its design.
- **Would falsify:** The proposed architecture adds no separable behavior beyond an ordinary agent loop.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Name and expansion provisional. Do not implement in current phases.

## Empirical findings (1)

### `E-001` -- Historical IDS archive provides scoped benchmark artifacts

- **Status:** `experimentally_supported`
- **Statement:** The read-only IDS archive documents a completed, deterministic benchmark separating closed-book vulnerability-shape reconstruction from closed-corpus exact-CVE attribution over frozen artifacts, with explicit negative results and claim limits.
- **Why it matters:** Those properties may make it useful as a future environment, but they do not validate SER or prove sequential routing value.
- **Depends on:** None recorded.
- **Related to:** `H-011`, `Q-004`
- **Would support:** Read-only inventory confirms separable interfaces and reproducible artifacts relevant to an environment adapter.
- **Would falsify:** Deeper inventory shows that usable behavior depends inseparably on IDS-specific assumptions or unavailable artifacts.
- **Implementation refs:** None recorded.
- **Evidence refs:** `reference/IDS_LEGACY.md`, `/Users/paolo/proj/ids-rule-to-cve-inference-archive/README.md`
- **Origin:** read-only IDS archive inspection, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Evidence is historical and IDS-scoped. It is not experimental support for any SER hypothesis.

## Open questions (9)

### `Q-001` -- What objective should the controller optimize?

- **Status:** `working`
- **Statement:** How should decision relevance, information gain, cost, latency, risk, and multi-resource constraints be represented and combined?
- **Why it matters:** Different objectives can choose different actions and create different stopping behavior.
- **Depends on:** `H-002`, `P-006`
- **Related to:** `Q-007`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Intentionally unresolved.

### `Q-002` -- What is the minimal explicit epistemic state?

- **Status:** `working`
- **Statement:** Which observations, hypotheses, claims, unknowns, contradictions, uncertainties, provenance, scope, actions, and costs must be represented for useful control?
- **Why it matters:** Too little state loses decision information; too much recreates unbounded history.
- **Depends on:** `P-001`
- **Related to:** `P-008`, `Q-003`, `Q-005`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Phase 2 formalization question.

### `Q-003` -- What schema should an epistemic unit use?

- **Status:** `working`
- **Statement:** Which metadata and relations are truly substrate-independent, and which should remain environment-specific?
- **Why it matters:** Premature schema commitment could encode a single domain as universal theory.
- **Depends on:** `P-002`
- **Related to:** `Q-002`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Intentionally unresolved until minimal control formalization.

### `Q-004` -- What, if anything, should transfer from IDS?

- **Status:** `working`
- **Statement:** Which IDS archive components should be reused unchanged, generalized, treated only as evidence or inspiration, or discarded, including any interval/scope work?
- **Why it matters:** Unreviewed transfer could contaminate SER with domain-specific assumptions or mistaken validation claims.
- **Depends on:** `E-001`, `H-011`
- **Related to:** `P-003`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** `reference/IDS_LEGACY.md`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Phase 1 owns the inventory; no transfer decision exists.

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
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Intentionally cold and unresolved; do not invent semantics to fill the gap.

### `Q-007` -- When should epistemic work stop?

- **Status:** `working`
- **Statement:** What stopping rule balances remaining decision-relevant uncertainty against expected information value, latency, cost, and risk?
- **Why it matters:** Stopping is an epistemic action and central to resource efficiency.
- **Depends on:** `H-002`, `P-004`
- **Related to:** `H-006`, `Q-001`
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** None recorded.
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** No threshold or rule is fixed.

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
- **Statement:** Which environments, baselines, ablations, uncertainty analyses, and independent confirmations are required before a SER hypothesis becomes experimentally supported or accepted?
- **Why it matters:** Promotion thresholds must resist development-set overfitting and broad claims from narrow evidence.
- **Depends on:** `F-004`, `F-005`, `H-016`
- **Related to:** None recorded.
- **Would support:** Not yet specified.
- **Would falsify:** Not yet specified.
- **Implementation refs:** None recorded.
- **Evidence refs:** `CHARTER.md`
- **Origin:** design synthesis discussion, 2026-08-17
- **Last reviewed:** `2026-08-17`
- **Notes:** Governance path is accepted; scientific thresholds remain open.
