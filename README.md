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
boundary. A later zero-call audit found that v1.2's scorer did not match its
public source-direct task and that one Nano summary condition exposed
oracle-derived prior state. ADR-0019 therefore preserves v1.2 but withdraws a
clean fact/effect capability-floor interpretation. AuthzGym v1.3 is now the
accepted new instrument specification: it uses source-grounded f0--f16 labels,
public deterministic local-cue effects, five visible-call categories, no hidden
roles, and no summary condition. It has not been implemented or run. Semantic
action-value estimation and advantage over ReAct or an ordinary agent remain
unproved.

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

Active Phase 5 permits only offline implementation and validation of the exact
AuthzGym v1.3 preregistration under ADR-0019. The instrument, independent
answerability certificates/checker, firewall suite, unchanged-estimator oracle
validation, development and confirmation populations, manifests, and freeze
record must all pass before any new model/provider inference. The old v1.2
confirmation protocol is not resumed; underlying unqueried source instances are
reusable only under the recorded no-influence proof, otherwise the preregistered
fresh fallback is mandatory. Phase 5 does not authorize real GitLab integration,
broad vulnerability discovery, general LLM agents, graph policies, coupling
operators, production fuzzers, IDS adapters, remote-sensing integrations, or
training infrastructure, and it does not authorize Jev, model escalation,
representation intervention, or architecture comparison. GitLab authorization is the practical research trunk,
not current evidence; the completed IDS-to-CVE project remains read-only
historical input and only a conditional semantic bridge.
