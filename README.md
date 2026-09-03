# SER

SER is an early-stage research project about allocating limited epistemic
resources. Its starting question is:

> How can an intelligent system choose among observation, retrieval,
> experimentation, hypothesis generation or refinement, internal reasoning,
> and stopping so that it produces the greatest useful reduction in uncertainty
> under resource constraints?

The accepted problem-level loop is an architectural framing, not a validated
controller:

`state -> choose epistemic action -> obtain result -> update state -> choose again`

The durable knowledge architecture, accepted language-neutral control problem,
and minimal zero-LLM MicroGym validation runtime now exist. MicroGym v1 produced
a narrow stopping result without conditional routing. The separate frozen
routing-v1 benchmark then showed that the unchanged myopic candidate can use a
released cue to choose the exact one-step closed-loop acquisition when clean
likelihood tables are supplied. Static Semantic AuthzGym protocol 1.1 is now a
frozen authorization-code benchmark with a validated deterministic mock
calibration. Real-model integration has since been exercised, but the first
real-model architecture run was invalid because its response/semantic contract
was not mechanically reliable enough for architecture inference. Semantic
contract v1.2 repaired the response-schema design by removing free-form and
dynamic-reference output channels; its first development stress run was
transport-unstable, while the subsequent transport-envelope study completed
128/128 `gpt-5.4-nano` calls with `transport_stable` and `contract_stable` for
that exact development protocol. Nano's semantic signal was weak. A subsequent
preregistered `gpt-5.4-mini` study retained v1.2 and again found stable transport
and schema behavior, but stopped at its frozen 16/32 development futility
boundary because six semantic/downstream requirements were mathematically
unreachable. Its untouched confirmation population was not run; oracle semantic
state still repaired action ranking completely. These are capability-floor
diagnostics, not admitted SER architecture findings: semantic action-value
estimation and advantage over ReAct or an ordinary agent remain unproved.

## Start here

For a fresh, portable briefing, read `state/CONTEXT_PACKET.md`. Then read:

1. `CHARTER.md` for the research boundary and invariants.
2. `MAP.md` for document authority.
3. `theory/CONTROL_PROBLEM.md` and `theory/CONTRACTS.yaml` for the accepted
   Phase 2 semantics.
4. `theory/INFORMATION_BOUNDARIES.md` for access and leakage rules.
5. `theory/DOMAIN_INSTANTIATIONS.md` for cross-domain pressure tests.
6. `theory/IDEA_MAP.md` for the readable conceptual inventory.
7. `plan/ROADMAP.md` for the active phase and immediate next task.

`theory/IDEA_MAP.yaml` is canonical; `theory/IDEA_MAP.md` is generated. Stable
concept IDs let documents refer to one idea without repeatedly renaming or
reinterpreting it.

## Knowledge layers

The architecture separates where knowledge belongs from how mature it is:

- **Cold:** `CHARTER.md`, `DECISIONS.md`, `MAP.md`, `AGENTS.md`, and the canonical
  idea map. These preserve boundaries, accepted decisions, and conceptual
  history. A cold idea can still be speculative.
- **Warm:** `plan/ROADMAP.md`. This owns sequence, the current cursor, and exit
  criteria.
- **Hot-ish:** `state/STATUS.yaml` owns present implementation and evidence
  facts. `state/CONTEXT_PACKET.md` is a generated projection of canonical
  sources.
- **Reference:** `reference/` owns vocabulary and historical context, not SER
  claims.
- **Evidence:** `experiments/` indexes frozen protocols, traces, validation,
  results, limitations, and admitted findings. MicroGym v1 and routing-v1 are
  distinct immutable experiments. AuthzGym v1 and 1.1 are frozen construction-
  calibration records, explicitly not admitted empirical evidence.

Concept maturity is recorded independently as `seed`, `working`, `accepted`,
`experimentally_supported`, `rejected`, or `deprecated`. Neither placement in a
cold document nor implementation in code promotes a concept.

## Regenerate and check

From the repository root:

```bash
python3 tools/emit_context.py
python3 tools/check_knowledge_coherence.py
```

The generator deterministically renders `theory/IDEA_MAP.md`,
`state/CONTEXT_PACKET.md`, and `reference/LEGACY_INVENTORY.md`. Do not edit
generated files directly.

## Current non-goals

Active Phase 5 next permits only a separately preregistered, bounded diagnosis
of the valid stronger-model development failure under semantic contract v1.2.
That work must distinguish model inability, systematic interface omission, and
task ambiguity without changing v1.2 in place or beginning an architecture
comparison. The frozen untouched confirmation population remains unqueried.
Phase 5 does not authorize real GitLab integration,
broad vulnerability discovery, general LLM agents, graph policies, coupling
operators, production fuzzers, IDS adapters, remote-sensing integrations, or
training infrastructure. GitLab authorization is the practical research trunk,
not current evidence; the completed IDS-to-CVE project remains read-only
historical input and only a conditional semantic bridge.
