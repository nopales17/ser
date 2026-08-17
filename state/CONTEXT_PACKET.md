<!-- GENERATED FILE: DO NOT EDIT. Run `python3 tools/emit_context.py`. -->

# SER context packet

Canonical sources reviewed through `2026-08-17`. This is a portable projection, not a source of truth.

## 1. What SER is trying to investigate

SER investigates how an intelligent system might allocate limited epistemic
resources among observation, retrieval, experimentation, hypothesis generation,
hypothesis refinement, comparison, internal reasoning, abandonment, and stopping
to obtain useful decision-relevant uncertainty reduction under constraints.

The accepted problem-level loop is:

`state -> choose epistemic action -> obtain observation/result -> update state -> choose again`

The role separation and sequential control formulation are accepted architectural
framing under `F-002` and ADR-0008 through ADR-0012, not a validated controller.
The provisional policy objective `expected decision-relevant information gain -
cost - latency - risk` remains a working research hypothesis. Exact policy
objectives, state representations, domain action schemas, update algorithms, and
stopping rules remain open.

The research target is substrate-independent. Candidate resources include model
tokens, cheap- or frontier-model computation, retrieval, source inspection,
program execution, tests, active experimentation, sensor observations,
wall-clock time, and money.

The central empirical question is `H-001`: whether allocation organization contributes value beyond total computation. `F-004` makes the burden explicit: fixed, random, exhaustive, token/cost-matched frontier reasoning, and ordinary-agent baselines must be used where relevant.

## 2. Current maturity / what has actually been built

Project maturity is `phase_3_microgym_complete_narrow_finding`. The durable knowledge architecture exists: canonical idea data, generated readable/context views, an ADR ledger, a single roadmap cursor, and a lightweight coherence checker. Runtime built: **true**. Controllers: **11**. Environments: **6**. Model integrations: **0**.

MicroGym v1 is complete and valid, but its admitted finding is narrow: the myopic public-model candidate lowered an experiment-specific combined objective through lower spending and stopping while worsening decision loss and exhibiting no observation-conditioned routing. No general SER hypothesis was promoted.

Legacy inventory: **31** component groups classified at archive commit `38b661324725c094ffcc820371a836573f4aadc5`: 0 reuse unchanged, 11 generalize, 14 empirical evidence only, 4 inspiration only, and 2 discard. No component is authorized for unchanged reuse.

Phase 1 found no legacy code suitable for unchanged reuse. Trace/provenance envelopes, completeness and access-policy checks, hash manifests, evaluator separation, paired controls, blinding, replay, and failed-run preservation survive only as patterns to rebuild behind SER-owned contracts. IDS data and labels are deferred environment/evaluator assets; prompts, rankers, comparators, product neighborhoods, domain schemas, and normalizers remain excluded prior solution logic. No generic Scope, Interval, epistemic-memory, flag, signal, or SER coupling-operator implementation was found in the current archive or reachable history.

Phase 2 formalization: **22** semantic contracts, **12** required invariants, and **4** domain pressure tests. Phase 2 separates latent world, released observation history, controller epistemic state, policy-neutral legal actions, raw vector resources, first-class stopping, and evaluator-owned outcomes. MicroGym v1 implemented these semantics without a contract correction, but one synthetic implementation does not validate their generality. Observation and optional Hypothesis remain distinct; Scope is optional; Signal and all nine coupling mechanisms remain deferred.

Do not infer runtime progress from the conceptual inventory. Mechanism entries preserve ideas; they are not code.

## 3. Settled architectural decisions

- `ADR-0001` **Layered knowledge architecture**: Separate cold conceptual authority, warm planning, hot-ish current state, reference material, and evidence artifacts. Keep the canonical document set small and assign each source one ownership role in `MAP.md`.
- `ADR-0002` **Canonical stable-ID idea registry**: `theory/IDEA_MAP.yaml` is the canonical registry for important concepts. Stable category-prefixed IDs are never reused. The file uses the JSON-compatible subset of YAML so all tooling remains Python-standard-library only.
- `ADR-0003` **Authority and maturity are independent**: Location determines authority and a single explicit status determines maturity. Allowed statuses are `seed`, `working`, `accepted`, `experimentally_supported`, `rejected`, and `deprecated`. Implementation never promotes theory automatically.
- `ADR-0004` **Deterministic generated context**: `tools/emit_context.py` deterministically renders `theory/IDEA_MAP.md` and `state/CONTEXT_PACKET.md` from canonical sources. Generated files carry a warning and are checked byte-for-byte for freshness.
- `ADR-0005` **Explicit single phase cursor**: `plan/ROADMAP.md` contains exactly one phase with status `active`. `state/STATUS.yaml` repeats the cursor only as a coherence-checked current-state fact. Phase detail remains coarse until it approaches execution.
- `ADR-0006` **IDS archive isolation**: Treat `/Users/paolo/proj/ids-rule-to-cve-inference-archive` as read-only historical input. Phase 1 may classify reuse candidates, but copying code, importing data, building an adapter, or claiming transfer requires later explicit decisions and relevant evidence.
- `ADR-0007` **Canonical legacy inventory and no-transfer default**: `reference/LEGACY_INVENTORY.yaml` is the canonical registry for Phase 1 legacy-component judgments, and `reference/LEGACY_INVENTORY.md` is its generated readable view. Classifications record research recommendations, not import authorization. The default remains no code or data transfer; any future reuse or environment ingestion requires a separate explicit decision.
- `ADR-0008` **Separate latent world, epistemic state, and evaluation**: Environments own latent `WorldState`; normal policies act only on legitimately released observations, their controller-owned `EpistemicState`, legal action capabilities, and remaining budget; evaluators use a separate restricted view. Evaluator-only information has no path into normal policy state or interfaces.
- `ADR-0009` **Policy-neutral environment and action-legality boundary**: The environment owns latent dynamics, initial observation release, legal concrete actions or generative capabilities, domain execution, and environment termination. It never consumes `EpistemicState`. Legality may depend on world constraints, public history, capabilities, and budget, but not private controller reasoning. Policy preference is a separate role.
- `ADR-0010` **Preserve vector-valued resource accounting**: Episodes declare named resource dimensions and units. Per-action and cumulative costs are nonnegative vectors; budgets constrain named dimensions. The core defines no conversion factors or universal scalar. Experiments may preregister scalarization, lexicographic comparison, or Pareto analysis while retaining raw dimensions.
- `ADR-0011` **First-class STOP and distinct termination causes**: `STOP` is a first-class controller action with a domain submission or abstention. Controller stop, environment termination, and runner/evaluator truncation remain distinct trace events and outcome dimensions.
- `ADR-0012` **Minimal epistemic ontology and explicit deferral**: Observations are first-class released information; hypotheses are an optional controller representation with no required common semantic supertype. A universal `EpistemicUnit` is rejected from the minimal core. Scope is an optional typed capability with domain-owned semantics. Signal, graph state, coupling operators, learned routing, confidence calculus, and universal information-gain objectives are deferred.
- `ADR-0013` **Evidence-directed environment selection and software research trunk**: GitLab authorization investigation is the primary practical research trunk. MicroGym is a control-mechanism validation instrument. IDS may be used only as a small semantic bridge if a positive MicroGym result leaves survival under messy semantic evidence unresolved. Controlled software investigation, including chosen tests or fuzzing, is preferred when it can directly and cleanly test the remaining question while advancing authorization research. Remote sensing and other substrates remain dormant falsification candidates, not scheduled phases. A new environment requires a concrete statement of the unresolved architectural claim it can distinguish.

## 4. Current high-value primitives

- `P-001` **Explicit epistemic state** (`working`): A policy acts on controller-entitled epistemic state that may be raw public history, a summary, or a structured representation, but is never latent world state or evaluator-only information.
- `P-003` **Scope** (`working`): Scope is optional domain-typed metadata describing the claimed applicability or support domain of an observation, hypothesis, action, or relation, with any algebra owned by that scope type.
- `P-004` **Epistemic action** (`working`): An epistemic action is a controller choice using a domain-owned schema and payload that can affect available information, transform entitled state, intervene on the world, or explicitly stop; descriptive categories are not a universal enum.
- `P-005` **Epistemic resource** (`working`): Episodes declare named epistemic resource dimensions and units; actions incur nonnegative raw resource vectors that aggregate componentwise and may be constrained by partial vector budgets.
- `P-006` **Cost, latency, and risk** (`working`): An epistemic action can consume multiple costs and may introduce latency or risk in addition to monetary or compute expense.
- `P-007` **Provenance** (`working`): Structured state and compressed summaries should retain links to recoverable source observations and transformation history.

These are active candidate theoretical primitives. `P-002` is listed separately as rejected from the minimal core. No Python class, graph schema, universal confidence calculus, or universal resource conversion is accepted. `P-003` Scope, `H-003` scope-aware allocation, `M-006` SCOPE_FILTER, a future implementation, and experiment evidence are separate objects.

## 5. Working hypotheses

- `H-001` **Allocation organization contributes to inference-time intelligence** (`working`): Inference-time performance may depend partly on how computation and evidence acquisition are organized, not only on their total amount.
- `H-006` **Epistemic exploration-exploitation tradeoff** (`working`): Choosing among deepening a hypothesis, gathering more evidence, generating alternatives, and abandoning a branch may be an exploration-exploitation problem.
- `H-009` **Active observation can manufacture discriminating evidence** (`working`): When a system can choose an action or input before observing the world, active experiments may yield more decision-relevant evidence than passive observation at comparable cost.

`working` means specified enough for refinement or test design, not experimentally supported. `H-016` is the eventual resource-normalized advantage claim but remains a `seed`.

## 6. Important speculative/cold ideas worth remembering

- `P-008` **Uncertainty and confidence** (`seed`): Epistemic state may need explicit uncertainty or confidence attached to claims, observations, and alternatives.
- `P-009` **Signal** (`seed`): Signal is a reserved candidate name for a future epistemic role that would need semantics irreducible to Observation, ActionResult, EpistemicState, relations, or reliability metadata.
- `H-002` **Decision-relevant information utility objective** (`seed`): A useful action objective may resemble expected decision-relevant information gain minus cost, latency, and risk.
- `H-003` **Scope-aware allocation improves efficiency** (`seed`): Representing applicability scope and using it in gating may improve resource efficiency when evidence has local relevance.
- `H-004` **Sparse selective propagation** (`seed`): Selective local propagation of evidence may allocate resources more effectively than broadcasting every item to every hypothesis.
- `H-005` **Decision-sufficient epistemic compression** (`seed`): Raw interaction history may be compressible into smaller decision-relevant structured state while retaining provenance links needed for recovery and audit.
- `H-007` **Observation-reasoning oscillation** (`seed`): Trajectory quality may relate to oscillation rate, the frequency of switching between external acquisition and internal inference, and oscillation depth, the resources spent within a mode before switching.
- `H-008` **Environmental coherence timescale constrains reasoning depth** (`seed`): In changing environments, useful reasoning depth may depend on how long observations remain coherent with the underlying system.
- `H-010` **Hierarchical boundary selection** (`seed`): Selecting epistemic scope across nested boundaries may be substrate-independent, such as function to runtime or pixel to larger physical system.
- `H-011` **IDS-to-CVE as a possible semantic bridge** (`seed`): A small IDS-to-CVE experiment may serve as a semantic validation bridge only if MicroGym supports adaptive routing yet leaves unresolved whether the advantage survives imperfect semantic evidence.
- `H-012` **Controlled software investigation toward GitLab authorization** (`seed`): The primary practical trunk should progress through minimal controlled software investigation toward GitLab authorization research, testing whether a controller chooses inspections, executions, tests, or fuzzing interventions that manufacture discriminating evidence efficiently.
- `H-013` **Remote-sensing generalization environment** (`seed`): A later observation environment with spatial and temporal resolution, modality, latency, and measurement uncertainty could test cross-domain generality.
- `H-014` **SERT learned routing policy** (`seed`): A future learned policy or training regime might learn to route epistemic resources from trajectories and outcomes.
- `H-015` **Temporal graph policy or TGNN** (`seed`): If epistemic state becomes a temporal relational graph, a learned graph policy might predict where computation or evidence acquisition should go next.
- `H-016` **Resource-normalized SER advantage** (`seed`): A SER controller may achieve better outcome per constrained resource than fixed, random, exhaustive, frontier-reasoning, or ordinary-agent strategies.
- `M-010` **Epistemic compressor** (`seed`): An epistemic compressor would transform raw history into decision-relevant structured state while preserving links to recoverable evidence.
- `M-012` **SER controller/runtime** (`seed`): SER provisionally denotes a control architecture that selects, targets, times, and stops resource-consuming epistemic actions while maintaining controller-entitled epistemic state.
- `M-011` **MicroGym synthetic environment family** (`working`): MicroGym should provide zero-LLM synthetic environments with known hidden state, explicit observation costs, actions with different information value, and computable optimal or near-optimal behavior.
- Preserved coupling-operator family (`seed`, deferred): `M-001` RES, `M-002` GATE, `M-003` AMP, `M-004` DAMP, `M-005` INHIBIT, `M-006` SCOPE_FILTER, `M-007` TOPK, `M-008` DEFEAT, `M-009` PROMOTE. None is required for the first MicroGym. Their semantics remain unresolved under `Q-006`; names must not be converted into code or theory by guesswork.

Cold preservation is deliberate: it prevents intellectual loss without promoting these ideas. Observation/reasoning oscillation rate and depth are trajectory measurements, not fixed constants. Remote sensing, SERT, and TGNN work are late-stage generalization possibilities, not roadmap commitments.

### Unresolved questions that constrain later work

- `Q-001` **What objective should the controller optimize?** (`working`): How should a controller value decision quality and information under vector cost, latency, risk, and partially ordered resource constraints without assuming one universal scalarization?
- `Q-002` **What is the minimal explicit epistemic state?** (`working`): Beyond the accepted minimum entitlement, update, identity, and provenance invariants, which observations, hypotheses, contradictions, uncertainties, scopes, and summaries are useful to represent for control?
- `Q-003` **Should epistemic content share a common schema?** (`working`): Is a future common envelope for observations, hypotheses, results, and other epistemic content useful, and which metadata or relations—if any—are truly substrate-independent?
- `Q-004` **What, if anything, should transfer from IDS?** (`working`): Which IDS archive components should be reused unchanged, generalized, treated only as evidence or inspiration, or discarded, including any interval/scope work?
- `Q-005` **What can an epistemic compressor discard safely?** (`working`): What information can be removed from raw history without harming future epistemic decisions, correction, or audit?
- `Q-006` **What are the coupling operators' semantics?** (`seed`): What precise inputs, outputs, algebra, conflict behavior, scope rules, and costs should RES, GATE, AMP, DAMP, INHIBIT, SCOPE_FILTER, TOPK, DEFEAT, and PROMOTE have?
- `Q-007` **When should epistemic work stop?** (`working`): Which policy stopping rule best balances submission or abstention quality against expected remaining value, latency, vector cost, and risk, and how should stopping regret be measured?
- `Q-008` **Are SER and SERT the right names?** (`seed`): The project name, the expansion of SER, and the future SERT policy/training name remain provisional.
- `Q-009` **What evidence warrants scientific promotion?** (`working`): Which cross-environment evidence, matched baselines, ablations, holdouts, uncertainty analyses, and independent confirmations warrant promoting a SER hypothesis?

These questions are part of the durable conceptual state. Future work should update their canonical entries with decisions or evidence instead of resolving them only in conversation.

## 7. Rejected/deprecated ideas

- `P-002` **Epistemic unit** (`rejected`): A universal semantic supertype unifying observations, hypotheses, and other epistemic content was considered for the minimal core and is not required.

## 8. Current experimental evidence

SER evidence records: **1**.
- `E-001` **Historical IDS archive provides scoped benchmark artifacts** (`experimentally_supported`): The read-only IDS archive documents a completed, deterministic benchmark separating closed-book vulnerability-shape reconstruction from closed-corpus exact-CVE attribution over frozen artifacts, with explicit negative results and claim limits.
  Limitation: Evidence is historical and IDS-scoped. Phase 1 confirmed reproducible assets and important negative results, but also product/lexical confounds, population corrections, invalid or unrun evaluations, and no holdout. It is not experimental support for any SER hypothesis.
- `E-002` **MicroGym v1 stopping efficiency without conditional routing** (`experimentally_supported`): On the frozen 728-episode MicroGym v1 population, the public-model myopic candidate lowered mean experiment-specific combined objective to 0.303159 versus 0.465220-0.481049 for five simple controls and 0.311429 for a matched model-aware open-loop control, but it had worse decision loss than every simple control, gained only 0.008269 against open-loop through lower expenditure, and exhibited zero observation-conditioned branches across 20 eligible counterfactual decision nodes.
  Limitation: Narrow synthetic finding only. The preregistered mechanical classifier said strong_enough_to_continue because it lacked a positive-adaptivity admission requirement; scientific interpretation is narrow. It does not promote H-001, H-016, semantic reasoning, scope, coupling, IDS transfer, software investigation, or GitLab research.
The IDS finding is historical environment evidence only. The MicroGym finding is narrow stopping/cost evidence and explicitly does not establish observation-conditioned routing. Neither supports scope-aware gating, sparse propagation, compression, learned policy, real-domain transfer, or substrate independence.

## 9. Current roadmap cursor

Active: **Phase 4 -- Adaptive-routing falsification follow-up**. Status: `active`.

Goal: determine whether a preregistered public-model policy can exhibit and benefit from genuinely observation-conditioned routing once STOP calibration no longer suppresses the branch choice.

Exit: a frozen follow-up either demonstrates a paired advantage attributable to realized-observation routing, or records a clean null/negative result and narrows or rejects that mechanism before any semantic/software expansion.

## 10. Immediate next task

Design the smallest frozen synthetic follow-up whose admission rule requires actual observation-conditioned branching and whose same-model open-loop control isolates routing from stopping, without altering MicroGym v1 or introducing a new domain.

The IDS archive remains read-only. Active Phase 4 authorizes only a synthetic adaptive-routing falsification follow-up: no IDS code/data copy, GitLab integration, adapter, production runtime, model integration, graph runtime, fuzzing, or coupling-law implementation.

## 11. Important non-goals

- No production SER runtime; the implemented code is a minimal zero-LLM MicroGym validation instrument and trivial experimental controllers.
- No LLM/model integration, TGNN, graph neural network, learned policy, or training infrastructure.
- No coupling-law implementation, universal epistemic graph, fuzzer, remote-sensing integration, or IDS adapter.
- No IDS code or data import and no claim that IDS results validate SER.

Also avoid scientific overclaiming: a cold location is not acceptance, implementation is not evidence, a failed mechanism does not erase its conceptual history, and additional model calls are not architectural success.

## 12. Canonical documents for deeper context

- `CHARTER.md`: research boundary, invariants, category distinctions, promotion/demotion, and non-goals.
- `MAP.md`: document ownership and precedence.
- `DECISIONS.md`: append-only accepted ADR history.
- `theory/CONTROL_PROBLEM.md`: authoritative language-neutral control problem and Phase 3 requirements.
- `theory/CONTRACTS.yaml`: machine-readable semantic contracts and invariants; not runtime classes.
- `theory/INFORMATION_BOUNDARIES.md`: role visibility, authorized flows, and prohibited leakage paths.
- `theory/DOMAIN_INSTANTIATIONS.md`: four domain instantiations used to pressure-test generality.
- `theory/IDEA_MAP.yaml`: canonical concept identities, statuses, relations, provenance, falsifiers, and references.
- `theory/PRIMITIVES.md`, `theory/HYPOTHESES.md`, and `theory/QUESTIONS.md`: concise conceptual reading aids.
- `plan/ROADMAP.md`: the only authoritative phase cursor.
- `state/STATUS.yaml`: current implementation and evidence facts.
- `reference/IDS_LEGACY.md`: disciplined boundary around historical IDS input.
- `reference/LEGACY_INVENTORY.yaml`: canonical Phase 1 component classifications, contamination risks, and Phase 2 recommendations.
- `reference/LEGACY_INVENTORY.md`: generated readable inventory view; never edit directly.
- `reference/IDS_LESSONS.md`: concise evidence and design lessons from the archive.
- `experiments/README.md`: evidence admission rules and admitted experiment index.
