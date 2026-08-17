# SER

SER is an early-stage research project about allocating limited epistemic
resources. Its starting question is:

> How can an intelligent system choose among observation, retrieval,
> experimentation, hypothesis generation or refinement, internal reasoning,
> and stopping so that it produces the greatest useful reduction in uncertainty
> under resource constraints?

The proposed control loop is only an object of investigation:

`state -> choose epistemic action -> obtain result -> update state -> choose again`

No SER runtime, controller, agent, learned policy, or experimental result exists
yet. This repository currently contains only the durable knowledge architecture
needed to investigate those possibilities without confusing ideas, decisions,
implementations, and evidence.

## Start here

For a fresh, portable briefing, read `state/CONTEXT_PACKET.md`. Then read:

1. `CHARTER.md` for the research boundary and invariants.
2. `MAP.md` for document authority.
3. `theory/IDEA_MAP.md` for the readable conceptual inventory.
4. `plan/ROADMAP.md` for the active phase and immediate next task.

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
- **Evidence:** `experiments/` will eventually index protocols and results. It
  currently records that no SER experiments have run.

Concept maturity is recorded independently as `seed`, `working`, `accepted`,
`experimentally_supported`, `rejected`, or `deprecated`. Neither placement in a
cold document nor implementation in code promotes a concept.

## Regenerate and check

From the repository root:

```bash
python3 tools/emit_context.py
python3 tools/check_knowledge_coherence.py
```

The generator deterministically renders both `theory/IDEA_MAP.md` and
`state/CONTEXT_PACKET.md`. Do not edit either generated file directly.

## Current non-goals

This phase does not build LLM agents, model integrations, graph policies,
coupling operators, fuzzers, IDS adapters, remote-sensing integrations, or
training infrastructure. The completed IDS-to-CVE project is read-only
historical input and a possible future environment; none of its results validate
SER.

