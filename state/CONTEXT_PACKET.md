<!-- GENERATED FILE: DO NOT EDIT. Run `python3 tools/emit_context.py`. -->

# SER context packet

Canonical sources reviewed through `2026-09-03`. This is a portable projection, not a source of truth.

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

Project maturity is `phase_5a_stronger_model_below_semantic_capability_threshold`. The durable knowledge architecture exists: canonical idea data, generated readable/context views, an ADR ledger, a single roadmap cursor, and a lightweight coherence checker. Runtime built: **true**. Controllers: **17**. Environments: **13**. Model integrations: **1**.

MicroGym v1 admitted a narrow stopping/cost finding without conditional routing. Routing-v1 then supported a narrow one-step routing result under clean supplied likelihoods. Static Semantic AuthzGym protocol 1.1 remains a validated benchmark calibration. Real-model v1 is preserved as invalid and semantic-contract v1.2 as transport-unstable. The separate transport-envelope v1 run established transport_stable and contract_stable for the exact nano development protocol. The subsequent stronger-model study retained v1.2, passed transport/schema smoke, and stopped at the frozen 16/32 development futility boundary because multiple semantic and downstream thresholds were mathematically unreachable even under perfect remaining calls. Confirmation was not run. No AuthzGym E-* finding or architecture claim was admitted, and no general SER hypothesis was promoted.

Static Semantic AuthzGym protocol 1.1 is frozen with 8 development, 24 primary evaluation, and 24 paired perturbation episodes. Its 384 records use deterministic test doubles; all 11 construction safeguards pass, but the status is `benchmark_calibration_only`, the real-model classifier is `not_run`, and no `E-*` finding was added. The preserved v1 calibration remains invalid because it exposed identifier-dependent mock degradation.

Legacy inventory: **31** component groups classified at archive commit `38b661324725c094ffcc820371a836573f4aadc5`: 0 reuse unchanged, 11 generalize, 14 empirical evidence only, 4 inspiration only, and 2 discard. No component is authorized for unchanged reuse.

Phase 1 found no legacy code suitable for unchanged reuse. Trace/provenance envelopes, completeness and access-policy checks, hash manifests, evaluator separation, paired controls, blinding, replay, and failed-run preservation survive only as patterns to rebuild behind SER-owned contracts. IDS data and labels are deferred environment/evaluator assets; prompts, rankers, comparators, product neighborhoods, domain schemas, and normalizers remain excluded prior solution logic. No generic Scope, Interval, epistemic-memory, flag, signal, or SER coupling-operator implementation was found in the current archive or reachable history.

Phase 2 formalization: **22** semantic contracts, **12** required invariants, and **4** domain pressure tests. Phase 2 separates latent world, released observation history, controller epistemic state, policy-neutral legal actions, raw vector resources, first-class stopping, and evaluator-owned outcomes. MicroGym v1 and routing-v1 implemented these semantics without a contract correction, but synthetic implementations do not validate their generality. Observation and optional Hypothesis remain distinct; Scope is optional; Signal and all nine coupling mechanisms remain deferred.

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
- `ADR-0014` **Route from synthetic control to controlled authorization evidence**: Complete Phase 4 with a narrowly scoped routing finding and make a minimal controlled authorization-oriented software environment the next validation phase. Its unresolved question is whether a controller can estimate decision-relevant epistemic-action values from imperfect software and authorization evidence when clean likelihood tables are not supplied. Do not begin with real GitLab integration. Do not add an IDS bridge unless a later explicit comparison shows that it is materially cleaner or cheaper for isolating that same question.
- `ADR-0015` **Separate authorization benchmark calibration from model evidence**: Preserve the failed v1 calibration without rewriting it and freeze protocol 1.1 as a benchmark-integrity correction. Protocol 1.1 changes only the deterministic mock omission key from opaque artifact identity to semantic fact/relation role. Treat both protocols as construction and calibration, not empirical SER evidence. Any actual inexpensive-model evaluation must be a separate frozen experiment using the already frozen population, semantic interface, budgets, baselines, and classifier thresholds, or must declare a new protocol version before observing evaluation outcomes.
- `ADR-0016` **Preserve the first real-model AuthzGym run as invalid**: Preserve the complete responses, traces, reports, and failure classification without repairing or re-running them. Admit no semantic or architecture-leverage finding and promote no hypothesis from diagnostic metrics. Keep Phase 5 active and Phase 5B blocked. The next admissible work is a separately versioned, preregistered static follow-up that establishes response-contract reliability and sufficient output budget on development episodes before repeating a complete frozen evaluation. Do not move to a larger population, stronger model, executable AuthzGym, historical cases, GitLab, or IDS to escape the invalid result.
- `ADR-0017` **Preserve semantic-contract v1.2 as transport-unstable**: Preserve the complete v1.2 responses, stress records, hashes, accounting, report, and classifier without rerunning or repairing them in place. Admit no semantic-capability or SER finding and promote no hypothesis. Keep Phase 5 active and Phase 5B blocked. The next admissible work is a new separately versioned development-only transport-envelope stability protocol that retains the v1.2 semantic schema, prompt, model, and development source population while preregistering tunnel-liveness handling and transport failure accounting. Do not proceed to architecture comparison or a stronger model until the complete semantic channel clears its mechanical contract.
- `ADR-0018` **Admit transport stability and preserve weak nano semantics as a development diagnostic**: Treat the local-Mac to supervised SSH SOCKS to wiseau to API transport envelope as stable for this exact development protocol and treat semantic contract v1.2 as mechanically reliable with this model and schedule. Preserve the weak nano semantic result as a development-only capability-floor diagnostic. Create no `E-*` finding, promote no hypothesis, and make no architecture comparison. Keep Phase 5 active and Phase 5B blocked. Under the preregistered Case C rule, the next admissible experiment retains the frozen v1.2 semantic contract and uses the next stronger inexpensive model in a separately versioned, preregistered development/confirmatory design. The 24 previously observed evaluation episodes remain recovery/diagnostic material and cannot serve as untouched confirmation.

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
- `H-017` **Decision-value-conditioned epistemic routing** (`working`): Newly released information should change epistemic resource allocation when it changes the expected value landscape of available actions, rather than merely because posterior belief changed.
- `H-018` **Bounded semantic action-value estimation** (`working`): Interpretations of only the authorization-code artifacts already purchased by a controller may contain enough decision-relevant structure to estimate which remaining bounded inspection is most useful without supplied likelihood tables or evaluator labels.

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
- `M-013` **Static Semantic AuthzGym benchmark** (`working`): Static Semantic AuthzGym is an authored, static authorization-code benchmark that exposes bounded artifact inspection, purchased-artifact semantic interpretation, epistemic update, explicit inspection-value estimation, routing, final diagnosis, evaluator truth, and raw resource accounting as separately traceable stages.
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

Empirical-finding records: **3**.
- `E-001` **Historical IDS archive provides scoped benchmark artifacts** (`experimentally_supported`): The read-only IDS archive documents a completed, deterministic benchmark separating closed-book vulnerability-shape reconstruction from closed-corpus exact-CVE attribution over frozen artifacts, with explicit negative results and claim limits.
  Limitation: Evidence is historical and IDS-scoped. Phase 1 confirmed reproducible assets and important negative results, but also product/lexical confounds, population corrections, invalid or unrun evaluations, and no holdout. It is not experimental support for any SER hypothesis.
- `E-002` **MicroGym v1 stopping efficiency without conditional routing** (`experimentally_supported`): On the frozen 728-episode MicroGym v1 population, the public-model myopic candidate lowered mean experiment-specific combined objective to 0.303159 versus 0.465220-0.481049 for five simple controls and 0.311429 for a matched model-aware open-loop control, but it had worse decision loss than every simple control, gained only 0.008269 against open-loop through lower expenditure, and exhibited zero observation-conditioned branches across 20 eligible counterfactual decision nodes.
  Limitation: Narrow synthetic finding only. The preregistered mechanical classifier said strong_enough_to_continue because it lacked a positive-adaptivity admission requirement; scientific interpretation is narrow. It does not promote H-001, H-016, semantic reasoning, scope, coupling, IDS transfer, software investigation, or GitLab research.
- `E-003` **MicroGym routing-v1 captures one-step explicit-model adaptivity** (`experimentally_supported`): On the frozen nine-regime, 1,152-episode MicroGym routing-v1 population, the unchanged public-model candidate branched at all 6 eligible conditional nodes, matched the exact closed-loop route at all 6, made 0 spurious branches across 3 zero-VOA controls, and achieved VOA-weighted Adaptivity Capture 1.0 under a fixed one-acquisition horizon with no STOP.
  Limitation: Narrow synthetic finding only. Exact VOA ranged from 0 to 0.2025; candidate expected advantage averaged 0.140083 on positive regimes, and all policies spent the same raw resource vector. The one-step score is aligned with the one-step horizon. The finding does not promote H-001 or H-016 and does not establish semantic value estimation, multi-stage planning, IDS or GitLab transfer, or general SER value.
The IDS finding is historical environment evidence only. MicroGym v1 supports a narrow stopping/cost finding without routing; routing-v1 supports only one-step observation-conditioned routing with supplied likelihoods. Static Semantic AuthzGym is absent from this finding list because deterministic benchmark calibration is not empirical evidence. None establishes semantic action-value estimation, scope-aware gating, sparse propagation, compression, learned policy, real-domain transfer, or substrate independence.

## 9. Current roadmap cursor

Active: **Phase 5 -- Controlled authorization action-value estimation**. Status: `active`.

Goal: determine whether a controller can estimate decision-relevant epistemic-action values from imperfect software and authorization evidence when clean likelihood tables are not supplied. - selection rule: use the smallest controlled authorization-oriented software environment that separates action-value estimation from generic software task skill while advancing the GitLab authorization research trunk.

Exit: a frozen matched-control experiment determines whether useful action values can be estimated without supplied likelihood tables, or records the smallest specific estimation/representation failure before any move to real GitLab research.

## 10. Immediate next task

Preregister a bounded semantic-representation diagnosis that uses the valid stronger-model development failures and evaluator-oracle intervention to distinguish model inability, systematic interface omission, and task ambiguity without changing v1.2 in place or beginning an architecture comparison.

The IDS archive remains read-only. Active Phase 5 now authorizes only a separately preregistered bounded diagnosis of the valid stronger-model development failure, distinguishing model inability, systematic v1.2 interface omission, and task ambiguity without changing v1.2 in place. It does not authorize architecture comparison, use of the untouched confirmation population for tuning, IDS code/data copy, real GitLab integration, an adapter, a production runtime or general model integration, graph runtime, production fuzzing, or coupling-law implementation.

## 11. Important non-goals

- No production SER runtime; the implemented code consists of MicroGym and Static Semantic AuthzGym benchmark instruments plus small exact, reference, and deterministic mock controllers.
- Four bounded real semantic-model protocols are preserved: architecture v1 is invalid, development contract v1.2 is transport-unstable, transport-envelope v1 is a transport-stable weak-nano development diagnostic, and stronger-model v1 is a valid development capability-floor failure with confirmation not run; none is a general LLM agent or an admitted architecture finding.
- No coupling-law implementation, universal epistemic graph, production fuzzer, remote-sensing integration, or IDS adapter.
- No IDS code or data import, real GitLab integration, or claim that IDS/GitLab validates SER.

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
