# Knowledge map

This is a thin authority index. Location determines a document's role; maturity
is an independent field on concepts and evidence.

| Source | Layer | Authoritative for | Not authoritative for |
| --- | --- | --- | --- |
| `CHARTER.md` | cold | research boundary, invariants, category distinctions, non-goals, promotion rules | proof that a scientific claim is true |
| `DECISIONS.md` | cold | append-only accepted architectural and governance decisions | hypotheses or experimental findings |
| `AGENTS.md` | cold | agent/contributor bootstrap and edit protocol | project theory |
| `MAP.md` | cold | source ownership and precedence | substantive theory |
| `theory/IDEA_MAP.yaml` | cold, canonical data | stable concept identities, maturity, relations, provenance, evidence links | current implementation state |
| `theory/IDEA_MAP.md` | generated view | nothing independently; readable rendering of the YAML registry | edits or new concepts |
| `theory/CONTROL_PROBLEM.md` | cold, canonical theory | accepted semantic formulation, invariants, contract interpretation, deferrals, and Phase 3 requirements | runtime API or evidence that a controller works |
| `theory/CONTRACTS.yaml` | cold, canonical data | stable Phase 2 contract identities, status, required/optional semantics, relations, and invariants | language-specific class definitions |
| `theory/INFORMATION_BOUNDARIES.md` | cold, canonical theory | role visibility, authorized flows, leakage prohibitions, and oracle separation | proof that a future implementation enforces the firewall |
| `theory/DOMAIN_INSTANTIATIONS.md` | cold explanation | manual application and adversarial pressure testing of the common contracts across four domains | implemented environments or empirical generality |
| `theory/PRIMITIVES.md` | cold explanation | distinctions and current candidate primitive vocabulary | maturity or identity independent of the idea map |
| `theory/HYPOTHESES.md` | cold explanation | hypothesis families and evaluation discipline | hypothesis status independent of the idea map |
| `theory/QUESTIONS.md` | cold explanation | unresolved research questions and their concept IDs | roadmap priority |
| `plan/ROADMAP.md` | warm | ordered phases, exactly one active phase, exit criteria | whether a hypothesis is true |
| `state/STATUS.yaml` | hot-ish, canonical data | what exists now, current evidence inventory, active cursor summary, immediate task | theory or accepted architectural decisions |
| `state/CONTEXT_PACKET.md` | generated view | nothing independently; portable synthesis of canonical sources | direct edits |
| `reference/TERMINOLOGY.md` | reference | preferred vocabulary and usage boundaries | scientific maturity |
| `reference/IDS_LEGACY.md` | reference | scoped historical interpretation of the read-only IDS archive | SER evidence or automatic reuse decisions |
| `reference/LEGACY_INVENTORY.yaml` | reference, canonical data | stable legacy component classifications, transfer rationale, contamination risks, and Phase 2 recommendations | permission to copy code/data or evidence for SER hypotheses |
| `reference/LEGACY_INVENTORY.md` | generated view | nothing independently; readable rendering of the canonical legacy inventory | edits or import authorization |
| `reference/IDS_LESSONS.md` | reference synthesis | concise evidence-backed lessons and explicit non-claims from the IDS archive | component identity, maturity, or SER validation |
| `experiments/README.md` | evidence index | experiment admission, evidence-record rules, and admitted result index | generalization beyond each frozen protocol |
| `experiments/microgym_v1/` | evidence artifacts | frozen MicroGym v1 population, traces, validation, numeric summary, adaptivity audit, and scoped interpretation | broad SER, semantic, or real-domain claims |
| `src/ser/` | implementation | minimal MicroGym runtime, public policies, evaluator-only oracle, trace/replay, and analysis behavior | theory maturity or empirical validity by itself |
| `tools/` | artifact | executable knowledge-generation and checking behavior | validation of SER theory |

## Precedence

When sources disagree, first compare their ownership above. Canonical data beats
its generated view. An experimental artifact beats a prose summary of the same
measurement, but it does not automatically outrank the charter's claim boundary.
Resolve a genuine accepted-design conflict with a new ADR; do not silently edit
history.
