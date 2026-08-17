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
and minimal zero-LLM MicroGym v1 validation runtime now exist. MicroGym produced
a narrow result: cost-sensitive stopping lowered its experiment-specific
combined objective, but the candidate showed no observation-conditioned routing.
No production SER controller, learned policy, model integration, or real-domain
evidence exists.

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
  results, limitations, and admitted findings. MicroGym v1 is the first run.

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

Active Phase 4 permits only the smallest synthetic adaptive-routing falsification
follow-up while preserving MicroGym v1. It does not authorize LLM agents, model
integrations, graph policies, coupling operators, fuzzers, IDS adapters, GitLab
integration, remote-sensing integrations, or training infrastructure. GitLab
authorization is the practical research trunk, not current evidence; the
completed IDS-to-CVE project remains read-only historical input and only a
possible future semantic bridge.
