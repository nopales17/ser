<!-- GENERATED FILE: DO NOT EDIT. Run `python3 tools/emit_context.py`. -->

# SER context packet

Canonical sources reviewed through `2026-08-17`. This is a portable projection, not a source of truth.

## 1. What SER is trying to investigate

SER investigates how an intelligent system might allocate limited epistemic
resources among observation, retrieval, experimentation, hypothesis generation,
hypothesis refinement, comparison, internal reasoning, abandonment, and stopping
to obtain useful decision-relevant uncertainty reduction under constraints.

The starting loop is:

`state -> choose epistemic action -> obtain observation/result -> update state -> choose again`

This loop and the provisional objective
`expected decision-relevant information gain - cost - latency - risk` are working
research formulations, not validated laws or settled implementations. The exact
objective, state representation, action set, update rule, and stopping rule remain
open.

The research target is substrate-independent. Candidate resources include model
tokens, cheap- or frontier-model computation, retrieval, source inspection,
program execution, tests, active experimentation, sensor observations,
wall-clock time, and money.

The central empirical question is `H-001`: whether allocation organization contributes value beyond total computation. `F-004` makes the burden explicit: fixed, random, exhaustive, token/cost-matched frontier reasoning, and ordinary-agent baselines must be used where relevant.

## 2. Current maturity / what has actually been built

Project maturity is `phase_2_minimal_control_formalization_ready`. The durable knowledge architecture exists: canonical idea data, generated readable/context views, an ADR ledger, a single roadmap cursor, and a lightweight coherence checker. Runtime built: **false**. Controllers: **0**. Environments: **0**. Model integrations: **0**.

No SER experiment has run and no SER scientific hypothesis has experimental support.

Legacy inventory: **31** component groups classified at archive commit `38b661324725c094ffcc820371a836573f4aadc5`: 0 reuse unchanged, 11 generalize, 14 empirical evidence only, 4 inspiration only, and 2 discard. No component is authorized for unchanged reuse.

Phase 1 found no legacy code suitable for unchanged reuse. Trace/provenance envelopes, completeness and access-policy checks, hash manifests, evaluator separation, paired controls, blinding, replay, and failed-run preservation survive only as patterns to rebuild behind SER-owned contracts. IDS data and labels are deferred environment/evaluator assets; prompts, rankers, comparators, product neighborhoods, domain schemas, and normalizers remain excluded prior solution logic. No generic Scope, Interval, epistemic-memory, flag, signal, or SER coupling-operator implementation was found in the current archive or reachable history.

Do not infer runtime progress from the conceptual inventory. Mechanism entries preserve ideas; they are not code.

## 3. Settled architectural decisions

- `ADR-0001` **Layered knowledge architecture**: Separate cold conceptual authority, warm planning, hot-ish current state, reference material, and evidence artifacts. Keep the canonical document set small and assign each source one ownership role in `MAP.md`.
- `ADR-0002` **Canonical stable-ID idea registry**: `theory/IDEA_MAP.yaml` is the canonical registry for important concepts. Stable category-prefixed IDs are never reused. The file uses the JSON-compatible subset of YAML so all tooling remains Python-standard-library only.
- `ADR-0003` **Authority and maturity are independent**: Location determines authority and a single explicit status determines maturity. Allowed statuses are `seed`, `working`, `accepted`, `experimentally_supported`, `rejected`, and `deprecated`. Implementation never promotes theory automatically.
- `ADR-0004` **Deterministic generated context**: `tools/emit_context.py` deterministically renders `theory/IDEA_MAP.md` and `state/CONTEXT_PACKET.md` from canonical sources. Generated files carry a warning and are checked byte-for-byte for freshness.
- `ADR-0005` **Explicit single phase cursor**: `plan/ROADMAP.md` contains exactly one phase with status `active`. `state/STATUS.yaml` repeats the cursor only as a coherence-checked current-state fact. Phase detail remains coarse until it approaches execution.
- `ADR-0006` **IDS archive isolation**: Treat `/Users/paolo/proj/ids-rule-to-cve-inference-archive` as read-only historical input. Phase 1 may classify reuse candidates, but copying code, importing data, building an adapter, or claiming transfer requires later explicit decisions and relevant evidence.
- `ADR-0007` **Canonical legacy inventory and no-transfer default**: `reference/LEGACY_INVENTORY.yaml` is the canonical registry for Phase 1 legacy-component judgments, and `reference/LEGACY_INVENTORY.md` is its generated readable view. Classifications record research recommendations, not import authorization. The default remains no code or data transfer; any future reuse or environment ingestion requires a separate explicit decision.

## 4. Current high-value primitives

- `P-001` **Explicit epistemic state** (`working`): A controller may require explicit state containing observations, hypotheses, claims, unknowns, contradictions, uncertainty, provenance, scope, available actions, and costs.
- `P-002` **Epistemic unit** (`seed`): Knowledge and evidence may need a substrate-independent unit carrying content, type, scope, provenance, confidence, time, acquisition cost, and relations.
- `P-003` **Scope** (`working`): Evidence and hypotheses may need explicit semantic, structural, temporal, spatial, and observational applicability boundaries.
- `P-004` **Epistemic action** (`working`): Candidate actions include observe, retrieve, transform, hypothesize, compare, test, deepen, broaden, revise, abandon, and stop.
- `P-005` **Epistemic resource** (`working`): Epistemic resources may include tokens, model tiers, compute, retrieval, inspection, execution, tests, observations, time, and money.
- `P-006` **Cost, latency, and risk** (`working`): An epistemic action can consume multiple costs and may introduce latency or risk in addition to monetary or compute expense.
- `P-007` **Provenance** (`working`): Structured state and compressed summaries should retain links to recoverable source observations and transformation history.
- `P-008` **Uncertainty and confidence** (`seed`): Epistemic state may need explicit uncertainty or confidence attached to claims, observations, and alternatives.

These are candidate theoretical primitives. No Python class, graph schema, or universal resource conversion is accepted. `P-003` Scope, `H-003` scope-aware allocation, `M-006` SCOPE_FILTER, a future implementation, and experiment evidence are separate objects.

## 5. Working hypotheses

- `H-001` **Allocation organization contributes to inference-time intelligence** (`working`): Inference-time performance may depend partly on how computation and evidence acquisition are organized, not only on their total amount.
- `H-006` **Epistemic exploration-exploitation tradeoff** (`working`): Choosing among deepening a hypothesis, gathering more evidence, generating alternatives, and abandoning a branch may be an exploration-exploitation problem.
- `H-009` **Active observation can manufacture discriminating evidence** (`working`): When a system can choose an action or input before observing the world, active experiments may yield more decision-relevant evidence than passive observation at comparable cost.

`working` means specified enough for refinement or test design, not experimentally supported. `H-016` is the eventual resource-normalized advantage claim but remains a `seed`.

## 6. Important speculative/cold ideas worth remembering

- `P-002` **Epistemic unit** (`seed`): Knowledge and evidence may need a substrate-independent unit carrying content, type, scope, provenance, confidence, time, acquisition cost, and relations.
- `P-008` **Uncertainty and confidence** (`seed`): Epistemic state may need explicit uncertainty or confidence attached to claims, observations, and alternatives.
- `H-002` **Decision-relevant information utility objective** (`seed`): A useful action objective may resemble expected decision-relevant information gain minus cost, latency, and risk.
- `H-003` **Scope-aware allocation improves efficiency** (`seed`): Representing applicability scope and using it in gating may improve resource efficiency when evidence has local relevance.
- `H-004` **Sparse selective propagation** (`seed`): Selective local propagation of evidence may allocate resources more effectively than broadcasting every item to every hypothesis.
- `H-005` **Decision-sufficient epistemic compression** (`seed`): Raw interaction history may be compressible into smaller decision-relevant structured state while retaining provenance links needed for recovery and audit.
- `H-007` **Observation-reasoning oscillation** (`seed`): Trajectory quality may relate to oscillation rate, the frequency of switching between external acquisition and internal inference, and oscillation depth, the resources spent within a mode before switching.
- `H-008` **Environmental coherence timescale constrains reasoning depth** (`seed`): In changing environments, useful reasoning depth may depend on how long observations remain coherent with the underlying system.
- `H-010` **Hierarchical boundary selection** (`seed`): Selecting epistemic scope across nested boundaries may be substrate-independent, such as function to runtime or pixel to larger physical system.
- `H-011` **IDS-to-CVE as a future controlled environment** (`seed`): The completed IDS-to-CVE benchmark may be adaptable into an early real SER environment with partial evidence and known ground truth.
- `H-012` **Software and fuzzing environment** (`seed`): A later software environment could test SER where the controller actively generates evidence through execution, tests, or fuzzing.
- `H-013` **Remote-sensing generalization environment** (`seed`): A later observation environment with spatial and temporal resolution, modality, latency, and measurement uncertainty could test cross-domain generality.
- `H-014` **SERT learned routing policy** (`seed`): A future learned policy or training regime might learn to route epistemic resources from trajectories and outcomes.
- `H-015` **Temporal graph policy or TGNN** (`seed`): If epistemic state becomes a temporal relational graph, a learned graph policy might predict where computation or evidence acquisition should go next.
- `H-016` **Resource-normalized SER advantage** (`seed`): A SER controller may achieve better outcome per constrained resource than fixed, random, exhaustive, frontier-reasoning, or ordinary-agent strategies.
- `M-010` **Epistemic compressor** (`seed`): An epistemic compressor would transform raw history into decision-relevant structured state while preserving links to recoverable evidence.
- `M-012` **SER controller/runtime** (`seed`): SER provisionally denotes a control architecture that maintains structured epistemic state and routes resources among epistemic actions.
- `M-011` **MicroGym synthetic environment family** (`working`): MicroGym should provide zero-LLM synthetic environments with known hidden state, explicit observation costs, actions with different information value, and computable optimal or near-optimal behavior.
- Preserved coupling-operator family (`seed`): `M-001` RES, `M-002` GATE, `M-003` AMP, `M-004` DAMP, `M-005` INHIBIT, `M-006` SCOPE_FILTER, `M-007` TOPK, `M-008` DEFEAT, `M-009` PROMOTE. Their semantics are unresolved under `Q-006`; names must not be converted into code or theory by guesswork.

Cold preservation is deliberate: it prevents intellectual loss without promoting these ideas. Observation/reasoning oscillation rate and depth are trajectory measurements, not fixed constants. Remote sensing, SERT, and TGNN work are late-stage generalization possibilities, not roadmap commitments.

### Unresolved questions that constrain later work

- `Q-001` **What objective should the controller optimize?** (`working`): How should decision relevance, information gain, cost, latency, risk, and multi-resource constraints be represented and combined?
- `Q-002` **What is the minimal explicit epistemic state?** (`working`): Which observations, hypotheses, claims, unknowns, contradictions, uncertainties, provenance, scope, actions, and costs must be represented for useful control?
- `Q-003` **What schema should an epistemic unit use?** (`working`): Which metadata and relations are truly substrate-independent, and which should remain environment-specific?
- `Q-004` **What, if anything, should transfer from IDS?** (`working`): Which IDS archive components should be reused unchanged, generalized, treated only as evidence or inspiration, or discarded, including any interval/scope work?
- `Q-005` **What can an epistemic compressor discard safely?** (`working`): What information can be removed from raw history without harming future epistemic decisions, correction, or audit?
- `Q-006` **What are the coupling operators' semantics?** (`seed`): What precise inputs, outputs, algebra, conflict behavior, scope rules, and costs should RES, GATE, AMP, DAMP, INHIBIT, SCOPE_FILTER, TOPK, DEFEAT, and PROMOTE have?
- `Q-007` **When should epistemic work stop?** (`working`): What stopping rule balances remaining decision-relevant uncertainty against expected information value, latency, cost, and risk?
- `Q-008` **Are SER and SERT the right names?** (`seed`): The project name, the expansion of SER, and the future SERT policy/training name remain provisional.
- `Q-009` **What evidence warrants scientific promotion?** (`working`): Which environments, baselines, ablations, uncertainty analyses, and independent confirmations are required before a SER hypothesis becomes experimentally supported or accepted?

These questions are part of the durable conceptual state. Future work should update their canonical entries with decisions or evidence instead of resolving them only in conversation.

## 7. Rejected/deprecated ideas

None. The absence of rejected entries reflects project age, not confirmation of the seeded ideas.

## 8. Current experimental evidence

SER evidence records: **0**.
- `E-001` **Historical IDS archive provides scoped benchmark artifacts** (`experimentally_supported`): The read-only IDS archive documents a completed, deterministic benchmark separating closed-book vulnerability-shape reconstruction from closed-corpus exact-CVE attribution over frozen artifacts, with explicit negative results and claim limits.
  Limitation: Evidence is historical and IDS-scoped. Phase 1 confirmed reproducible assets and important negative results, but also product/lexical confounds, population corrections, invalid or unrun evaluations, and no holdout. It is not experimental support for any SER hypothesis.
The IDS finding is historical environment evidence only. It does not support the SER controller, scope-aware gating, sparse propagation, compression, learned policy, or substrate-independence hypotheses.

## 9. Current roadmap cursor

Active: **Phase 2 -- Formalize the minimal control problem**. Status: `active`.

Goal: define the smallest useful state, action, observation, transition, cost, outcome, stopping, and metric formulation.

Exit: a falsifiable specification names baseline policies, resource accounting, and the questions that MicroGym must distinguish.

## 10. Immediate next task

Specify, without implementation, the minimal domain-neutral contracts for state, observation, epistemic unit or hypothesis, signal, scope, action, action result, transition, environment, policy interface, typed cost, outcome, and experiment/evaluator behavior; name baselines and unresolved choices before MicroGym.

The IDS archive remains read-only. Phase 2 authorizes conceptual specification only: no code/data copy, adapter, MicroGym, controller, or model integration.

## 11. Important non-goals

- No SER runtime or controller until Phase 2's conceptual exit criteria are met.
- No LLM/model integration, TGNN, graph neural network, learned policy, or training infrastructure.
- No coupling-law implementation, fuzzer, remote-sensing integration, or IDS adapter.
- No IDS code or data import and no claim that IDS results validate SER.

Also avoid scientific overclaiming: a cold location is not acceptance, implementation is not evidence, a failed mechanism does not erase its conceptual history, and additional model calls are not architectural success.

## 12. Canonical documents for deeper context

- `CHARTER.md`: research boundary, invariants, category distinctions, promotion/demotion, and non-goals.
- `MAP.md`: document ownership and precedence.
- `DECISIONS.md`: append-only accepted ADR history.
- `theory/IDEA_MAP.yaml`: canonical concept identities, statuses, relations, provenance, falsifiers, and references.
- `theory/PRIMITIVES.md`, `theory/HYPOTHESES.md`, and `theory/QUESTIONS.md`: concise conceptual reading aids.
- `plan/ROADMAP.md`: the only authoritative phase cursor.
- `state/STATUS.yaml`: current implementation and evidence facts.
- `reference/IDS_LEGACY.md`: disciplined boundary around historical IDS input.
- `reference/LEGACY_INVENTORY.yaml`: canonical Phase 1 component classifications, contamination risks, and Phase 2 recommendations.
- `reference/LEGACY_INVENTORY.md`: generated readable inventory view; never edit directly.
- `reference/IDS_LESSONS.md`: concise evidence and design lessons from the archive.
- `experiments/README.md`: evidence admission rules and current no-experiment state.
