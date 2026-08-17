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
| `theory/PRIMITIVES.md` | cold explanation | distinctions and current candidate primitive vocabulary | maturity or identity independent of the idea map |
| `theory/HYPOTHESES.md` | cold explanation | hypothesis families and evaluation discipline | hypothesis status independent of the idea map |
| `theory/QUESTIONS.md` | cold explanation | unresolved research questions and their concept IDs | roadmap priority |
| `plan/ROADMAP.md` | warm | ordered phases, exactly one active phase, exit criteria | whether a hypothesis is true |
| `state/STATUS.yaml` | hot-ish, canonical data | what exists now, current evidence inventory, active cursor summary, immediate task | theory or accepted architectural decisions |
| `state/CONTEXT_PACKET.md` | generated view | nothing independently; portable synthesis of canonical sources | direct edits |
| `reference/TERMINOLOGY.md` | reference | preferred vocabulary and usage boundaries | scientific maturity |
| `reference/IDS_LEGACY.md` | reference | scoped historical interpretation of the read-only IDS archive | SER evidence or automatic reuse decisions |
| `experiments/README.md` | evidence index | experiment admission, evidence-record rules, and current absence of SER results | unrun claims |
| `tools/` | artifact | executable knowledge-generation and checking behavior | validation of SER theory |

## Precedence

When sources disagree, first compare their ownership above. Canonical data beats
its generated view. An experimental artifact beats a prose summary of the same
measurement, but it does not automatically outrank the charter's claim boundary.
Resolve a genuine accepted-design conflict with a new ADR; do not silently edit
history.

