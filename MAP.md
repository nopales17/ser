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
| `experiments/microgym_routing_v1/` | evidence artifacts | frozen fixed-horizon routing population, exact open/closed-loop values, candidate traces, branch audit, validation, and scoped interpretation | multi-stage, semantic, software, GitLab, or general SER claims |
| `experiments/authzgym_static_v1/` | preserved benchmark-calibration artifacts | frozen population and the complete failed deterministic calibration history, including the identifier-dependent test-double defect | empirical semantic-model or SER evidence |
| `experiments/authzgym_static_v1_1/` | benchmark-calibration artifacts | corrected frozen Static Semantic AuthzGym population, semantic interface, budgets, baselines, classifier thresholds, deterministic mock traces, validation, and limitations | empirical semantic-model or SER evidence; permission to revise the frozen real-model protocol after observing outcomes |
| `experiments/authzgym_static_realmodel_v1/` | preserved invalid empirical artifacts | first complete inexpensive-model architecture schedule, raw local provider responses, cost accounting, invalid classifier, and failure diagnostics | an admitted semantic or architecture finding; permission to repair the run in place |
| `experiments/authzgym_semantic_contract_v1_2/` | preserved development stress artifacts | offline v1 response autopsy, frozen compact semantic schema, development-only stress population, raw local provider responses, transport-unstable classifier, oracle decomposition, and cost accounting | semantic capability, architecture leverage, evaluation-population performance, or permission to interpret the successful prefix as representative |
| `experiments/authzgym_transport_envelope_v1/` | development transport/capability diagnostic artifacts | preserved Phase 5A.4 transport autopsy, supervised-tunnel protocol, zero-inference preflight failure, frozen 128-call transport run, local provider responses, exact validation, transport/contract classifiers, nano semantic diagnostics, oracle decomposition, and cost accounting | architecture leverage, hypothesis promotion, untouched confirmation, old evaluation-population reuse, or semantic-contract tuning |
| `src/ser/` | implementation | minimal MicroGym and Static Semantic AuthzGym instruments, public policies, evaluator-only truth/oracles, semantic-call tracing, routing instrumentation, trace/replay, and analysis behavior | theory maturity or empirical validity by itself |
| `tools/` | artifact | executable knowledge-generation and checking behavior | validation of SER theory |

## Precedence

When sources disagree, first compare their ownership above. Canonical data beats
its generated view. An experimental artifact beats a prose summary of the same
measurement, but it does not automatically outrank the charter's claim boundary.
Resolve a genuine accepted-design conflict with a new ADR; do not silently edit
history.
