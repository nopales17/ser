# Architectural decision record ledger

This cold ledger is append-only. Accepted architectural and governance decisions
are recorded here before dependent charter changes. Supersede an earlier ADR with
a new entry; do not rewrite it.

## ADR-0001 -- Layered knowledge architecture

- Status: accepted
- Date: 2026-08-17
- Decision: Separate cold conceptual authority, warm planning, hot-ish current
  state, reference material, and evidence artifacts. Keep the canonical document
  set small and assign each source one ownership role in `MAP.md`.
- Why: Future sessions need reconstructable state without one enormous README or
  dependence on conversation history.
- Alternatives rejected: a monolithic project document; raw transcripts as the
  primary memory; per-document authority labels without a central map.

## ADR-0002 -- Canonical stable-ID idea registry

- Status: accepted
- Date: 2026-08-17
- Decision: `theory/IDEA_MAP.yaml` is the canonical registry for important
  concepts. Stable category-prefixed IDs are never reused. The file uses the
  JSON-compatible subset of YAML so all tooling remains Python-standard-library
  only.
- Why: Stable identity prevents terminology drift, while structured data permits
  automatic rendering and validation without introducing a package dependency.
- Alternatives rejected: prose-only concept lists; generated IDs; a database or
  documentation framework at this stage.

## ADR-0003 -- Authority and maturity are independent

- Status: accepted
- Date: 2026-08-17
- Decision: Location determines authority and a single explicit status determines
  maturity. Allowed statuses are `seed`, `working`, `accepted`,
  `experimentally_supported`, `rejected`, and `deprecated`. Implementation never
  promotes theory automatically.
- Why: Speculative ideas must be preserved durably without becoming doctrine.
- Alternatives rejected: moving concepts between folders to indicate confidence;
  deleting rejected ideas; treating implementation as acceptance.

## ADR-0004 -- Deterministic generated context

- Status: accepted
- Date: 2026-08-17
- Decision: `tools/emit_context.py` deterministically renders
  `theory/IDEA_MAP.md` and `state/CONTEXT_PACKET.md` from canonical sources.
  Generated files carry a warning and are checked byte-for-byte for freshness.
- Why: A concise, portable briefing lets a new agent recover state while keeping
  the sources of truth explicit.
- Alternatives rejected: hand-maintained summaries; embedding a large context
  dump in README; using chat transcripts as a build input.

## ADR-0005 -- Explicit single phase cursor

- Status: accepted
- Date: 2026-08-17
- Decision: `plan/ROADMAP.md` contains exactly one phase with status `active`.
  `state/STATUS.yaml` repeats the cursor only as a coherence-checked current-state
  fact. Phase detail remains coarse until it approaches execution.
- Why: A fresh session needs one unambiguous next direction without a sprawling
  speculative implementation plan.
- Alternatives rejected: implicit next steps scattered through prose; multiple
  concurrent active research phases; a detailed long-range build schedule.

## ADR-0006 -- IDS archive isolation

- Status: accepted
- Date: 2026-08-17
- Decision: Treat `/Users/paolo/proj/ids-rule-to-cve-inference-archive` as
  read-only historical input. Phase 1 may classify reuse candidates, but copying
  code, importing data, building an adapter, or claiming transfer requires later
  explicit decisions and relevant evidence.
- Why: The completed IDS project offers disciplined benchmark artifacts but is a
  domain-specific study, not evidence for SER's general architecture.
- Alternatives rejected: forking the historical repository as SER; assuming its
  abstractions transfer; importing it during Phase 0.

