<!-- GENERATED FILE: DO NOT EDIT. Run `python3 tools/emit_context.py`. -->

# SER context packet

Canonical sources reviewed through `2026-09-18`. This is a portable projection, not a source of truth.

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

Project maturity is `phase_5a_b1_successor_confirmation_sealed_model_semantic_condition_accepted_zero_inference_implementation_pending`. The durable knowledge architecture exists: canonical idea data, generated readable/context views, an ADR ledger, a single roadmap cursor, and a lightweight coherence checker. Runtime built: **true**. Controllers: **17**. Environments: **13**. Model integrations: **1**.

MicroGym v1 supports narrow stopping/cost results and routing-v1 one-step exact-likelihood routing. AuthzGym 1.1 stays calibration; real-model v1 invalid; v1.2 transport-unstable; Mini stopped futility after a zero-call audit found unanswerable labels. ADR-0019's v1.3 passes implementation, answerability, and firewall checks, but its oracle blocks freeze and inference. No E-* or architecture finding was admitted.

Static Semantic AuthzGym protocol 1.1 is frozen with 8 development, 24 primary evaluation, and 24 paired perturbation episodes. Its 384 records use deterministic test doubles; all 11 construction safeguards pass, but the status is `benchmark_calibration_only`, the real-model classifier is `not_run`, and no `E-*` finding was added. The preserved v1 calibration remains invalid because it exposed identifier-dependent mock degradation.

Legacy inventory: **31** component groups classified at archive commit `38b661324725c094ffcc820371a836573f4aadc5`: 0 reuse unchanged, 11 generalize, 14 empirical evidence only, 4 inspiration only, and 2 discard. No component is authorized for unchanged reuse.

Phase 1 found no legacy code suitable for unchanged reuse. Trace/provenance envelopes, completeness and access-policy checks, hash manifests, evaluator separation, paired controls, blinding, replay, and failed-run preservation survive as patterns to rebuild behind SER-owned contracts. IDS data and labels stay deferred evaluator assets; prompts, rankers, comparators, neighborhoods, schemas, and normalizers remain excluded. No generic Scope, Interval, memory, flag, signal, or coupling operator exists.

Phase 2 formalization: **22** semantic contracts, **12** required invariants, and **4** domain pressure tests. Phase 2 separates latent world, released observations, controller epistemic state, policy-neutral legal actions, vector resources, first-class stopping, and evaluator-owned outcomes. MicroGym v1 and routing-v1 instantiated these semantics without correction, but synthetic implementations do not validate generality. Observation and optional Hypothesis stay distinct, Scope is optional, and Signal with the nine coupling mechanisms remains deferred.

Do not infer runtime progress from the conceptual inventory. Mechanism entries preserve ideas; they are not code.

## 3. Settled architectural decisions

The newest 4 decisions are rendered in full, together with any older decision the current state or roadmap cites; every other decision is listed as an index entry only. `DECISIONS.md` is the full append-only history.
- `ADR-0001` — Layered knowledge architecture
- `ADR-0002` — Canonical stable-ID idea registry
- `ADR-0003` — Authority and maturity are independent
- `ADR-0004` — Deterministic generated context
- `ADR-0005` — Explicit single phase cursor
- `ADR-0006` — IDS archive isolation
- `ADR-0007` — Canonical legacy inventory and no-transfer default
- `ADR-0008` — Separate latent world, epistemic state, and evaluation
- `ADR-0009` — Policy-neutral environment and action-legality boundary
- `ADR-0010` — Preserve vector-valued resource accounting
- `ADR-0011` — First-class STOP and distinct termination causes
- `ADR-0012` — Minimal epistemic ontology and explicit deferral
- `ADR-0013` — Evidence-directed environment selection and software research trunk
- `ADR-0014` — Route from synthetic control to controlled authorization evidence
- `ADR-0015` — Separate authorization benchmark calibration from model evidence
- `ADR-0016` — Preserve the first real-model AuthzGym run as invalid
- `ADR-0017` — Preserve semantic-contract v1.2 as transport-unstable
- `ADR-0018` — Admit transport stability and preserve weak nano semantics as a development diagnostic
- `ADR-0019` **Replace AuthzGym v1.2 semantics with a separately versioned, answerable v1.3 instrument**: Create v1.3 as a new instrument under the exact normative preregistration; do not repair v1.2 in place. Retain four mechanism families, f0--f16, and seven non-summary variants; retire f17--f24. Derive gold from published source-local rules, keep roles hidden, make effects public deterministic fact-derived diagnostics, and restrict relations to five visible-call categories. Exclude `maximal_public_summary` and all evaluator-derived normal state. Independent public-only answerability, firewall, unchanged-estimator oracle, population, manifest, and freeze gates must pass before inference.
- `ADR-0020` **Authorize the bounded development-only estimator repair `est-repair-v1.3.1`**: Accept `experiments/authzgym_estimator_repair_v1_3_1/REPAIR_STUDY_PREREGISTRATION.md` as the governing preregistration for `est-repair-v1.3.1` and authorize its bounded offline development-only existence study in the fixed A then B then C order within a total budget of at most 10 attempts (`<= 10`), under every ceiling, baseline-freeze, non-degeneracy, own-ranking invariance, input allowlist, component firewall, and stopping rule that preregistration specifies. Section 8 successor confirmation generation, freezing, and execution are **not** authorized.
- `ADR-0021` **Correct the `est-repair-v1.3.1` step-1 specification defects and resume the authorized study**: Accept `experiments/authzgym_estimator_repair_v1_3_1/CORRIGENDUM.md` as an append-only correction governing `est-repair-v1.3.1` prospectively, with its three sections normative: the recorded `longest_artifact` regret is a transcription error and step-1 reproduction is authorized against the development value `0.6583333333333333`, with the confirmation-split read-out recorded as further already-exposed spent-confirmation information; the own-ranking obligation is resolved as own-selection-decision equivariance, B0 at 36/40, candidates at 40/40, full-order invariance descriptive only; and the step-0 confirmation-path hashing is a procedural deviation, not retroactively authorized, which on the verified facts does not invalidate the study, with the integrity procedure amended so the development harness opens or hashes no confirmation path. No gate, threshold, budget, arm order, stopping rule, non-degeneracy requirement, input allowlist, firewall requirement, or claim boundary changes; ADR-0020 resumes unchanged and the study resumes at handoff step 1.
- `ADR-0022` **Authorize the one-shot successor confirmation of the frozen `est-repair-v1.3.1-B-1` component**: Authorize execution of the already-preregistered section-8 successor confirmation protocol for exactly one component, `est-repair-v1.3.1-B-1` (component class SHA-256 `88b77c5f343117b354b5039d571bf03bf8867fcd7fb4f8fc91c1e1aefca7a048`, module SHA-256 `f9c92317abc562ac5175f90074238c666de55d557b02e0de368841676f4d910d`), against the frozen development report `DEVELOPMENT_REPORT.md` SHA-256 `f0629d3b78ba35258cc6d439e4b731c3682b76fa08e4155efbdad7cd0df18638`. Authorized: (1) generation and freezing of the `confirmation_v1_3_1` population at layouts 42/43 under the preregistered content-independent selection rule, with the preregistered collision rule advancing to the reserved pairs 44/45 then 46/47 and never by inspecting content; (2) independent certification, answerability validation, and firewall validation in the section-8.7 isolation order, with the section-8.5 access ledger and the section-8.3 duplication and equivalence checks; (3) exactly one oracle evaluation of the frozen B-1 component under the unchanged top-1 `>= 0.60`, top-2 `>= 0.80`, regret `<= 0.35`, zero-illegal, section-14 equivalence, and own-selection equivariance gates; and (4) preservation of the outcome, pass or failure, as this component's final result. Nothing beyond these four items is authorized.
- `ADR-0023` **Accept the AuthzGym model-semantic condition `model-semantic-v1.3.1-N1` and authorize zero-inference implementation only**: Accept the finalized model-semantic study package in `experiments/authzgym_model_semantic_v1_3_1/` as repository authority for condition `model-semantic-v1.3.1-N1`, and authorize **only zero-inference mechanical implementation** of that package and its development harness, up to and stopping at the preregistered pre-inference freeze boundary. The primary endpoint is choice-set preservation: for canonical source `i`, with `G_i` the legal targets tied for maximum B-1 value under certified gold semantics and `M_i` the same under the actual model response, the decision is preserved when `M_i` is non-empty and `M_i` is a subset of `G_i`, at `>= 7/8` canonical sources and, in development, separately on each repeat. The evaluator canonical ordinal stays evaluator-only and never enters the scientific definition of preservation. Effect self-consistency (S-7) is adjudicated `diagnostic_only`. No unresolved research-semantic decision remains in the package.

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

Model-semantic study accepted; zero-inference implementation in progress with the freeze incomplete. Handoff steps 1 through 6C are done and freeze_complete is false on one recorded item, PENDING-3. Four living-governance documents differ from their step-1 integrity baseline because ADR-0023 item D10 and the accepted ordering clarification required those edits; none is model-facing and none is a section-18 frozen input. IMPLEMENTATION_CLARIFICATION.md section 6 accepts those four exact old-to-new hash transitions for the final freeze without restoring the stale versions and without erasing the step-1 baseline. Next: write GOVERNANCE_REBASELINE.json recording path, step-1 hash, current hash, responsible governance change, model_facing false and accepted_for_final_freeze true for each of the four, plus the seven required statements; re-run the step 6B integrity, static and access checks against the original baseline plus exactly those four transitions; rebuild the step 6C manifest and checklist; set freeze_complete true only if every other requirement still passes; stop at 6D. Model or provider inference, the 112 development calls, scoring or analysis of actual model responses, confirmation generation or access, changes to v1.3 semantics, changes to est-repair-v1.3.1-B-1, changes to thresholds or endpoints, model substitution or escalation, prompt tuning, retry-policy changes, Jev, and closed-loop execution or architecture work all remain unauthorized; step 7 requires its own later decision.

The IDS archive remains read-only. Phase 5 authorizes offline v1.3 implementation, answerability/firewall/oracle validation, population freezing, the ADR-0020 est-repair-v1.3.1 study, and, under ADR-0023, zero-inference mechanical implementation of the accepted model-semantic condition through its pre-inference freeze boundary. It preserves v1.2 and forbids inference, development and confirmation calls, confirmation tuning, representation changes, Jev, IDS transfer, GitLab integration, and runtime work until the accepted gates pass and a further decision is recorded.

## 11. Important non-goals

- No production SER runtime; the implemented code consists of MicroGym and Static Semantic AuthzGym benchmark instruments plus small exact, reference, and deterministic mock controllers.
- Four bounded real semantic-model protocols are preserved: architecture v1 invalid, contract v1.2 transport-unstable, transport-envelope v1 a transport-stable wire/response diagnostic, and stronger-model v1 a mechanically valid development result below threshold with capability attribution blocked by benchmark answerability. None is a general LLM agent or an admitted architecture finding; the zero-call localization and v1.3 specification are offline work.
- No coupling-law implementation, universal epistemic graph, production fuzzer, remote-sensing integration, IDS adapter, Jev condition, representation intervention, or new routing architecture.
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
