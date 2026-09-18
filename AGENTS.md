# Agent protocol

Scope: these instructions apply to the SER repository rooted at this file.

## Bootstrap before changing anything

Read in this order:

1. `state/CONTEXT_PACKET.md` -- generated portable project state.
2. `CHARTER.md` -- research boundary, invariants, and non-goals.
3. `MAP.md` -- which source is authoritative for each kind of knowledge.
4. Relevant entries in `theory/IDEA_MAP.yaml` or its generated readable view.
5. `theory/CONTROL_PROBLEM.md` and relevant entries in
   `theory/CONTRACTS.yaml` -- accepted semantic contracts and deferrals.
6. `theory/INFORMATION_BOUNDARIES.md` -- access roles and prohibited flows.
7. `plan/ROADMAP.md` -- the single active phase and its exit criteria.
8. Implementation files, only after the conceptual context is understood.

If the generated packet is absent or stale, run `python3 tools/emit_context.py`
before continuing.

## Required distinctions

- State facts as facts and hypotheses as hypotheses.
- Use existing stable concept IDs; do not create a synonym for an existing
  concept merely to avoid reading its entry.
- Keep foundation, primitive, hypothesis, mechanism, implementation, and
  empirical evidence distinct. A Python class is not validation of a primitive.
- A concept's location determines authority; its `status` determines maturity.
  Cold storage does not mean accepted truth.
- When a genuinely new architectural idea appears, add a stable entry to
  `theory/IDEA_MAP.yaml` with conservative status and provenance.
- Record accepted architectural or governance decisions by appending an ADR to
  `DECISIONS.md`. Never revise old ADR history silently.
- Never promote a concept because it was discussed, documented, or implemented.
  Promotion requires the evidence described in `CHARTER.md`.
- Preserve rejected and deprecated concepts with their evidence and rationale.
- Report any implementation behavior that contradicts canonical documentation;
  do not silently make one conform to the other.

## Edit routing

- Research boundary or invariant: append an ADR, then amend `CHARTER.md`.
- Concept identity, relationship, maturity, or evidence link: edit
  `theory/IDEA_MAP.yaml`, then regenerate.
- Formal control semantics, invariants, deferrals, or Phase 3 requirements: edit
  `theory/CONTROL_PROBLEM.md`; append an ADR first when changing an accepted
  architectural constraint.
- Contract identity, status, or semantic fields: edit `theory/CONTRACTS.yaml`
  and keep the control-problem prose aligned.
- Role visibility or leakage rules: edit `theory/INFORMATION_BOUNDARIES.md`;
  append an ADR first when changing the evaluator/controller firewall.
- Domain pressure-test mappings: edit `theory/DOMAIN_INSTANTIATIONS.md` without
  treating a manual instantiation as empirical evidence.
- Plan or phase cursor: edit `plan/ROADMAP.md` and current facts in
  `state/STATUS.yaml`, then regenerate.
- Present implementation/evidence fact: edit `state/STATUS.yaml`, then
  regenerate.
- Vocabulary: edit `reference/TERMINOLOGY.md`.
- Historical IDS interpretation: edit `reference/IDS_LEGACY.md`, supported by
  read-only inspection of the archive.
- Legacy component identity, classification, transfer rationale, or
  contamination risk: edit `reference/LEGACY_INVENTORY.yaml`, then regenerate.

Never hand-edit `theory/IDEA_MAP.md`, `state/CONTEXT_PACKET.md`, or
`reference/LEGACY_INVENTORY.md`; each begins with a generated-file warning.

## Boundaries

- Do not build the SER runtime until the roadmap authorizes implementation.
- Treat `/Users/paolo/proj/ids-rule-to-cve-inference-archive` as read-only. Do
  not copy code or data from it without an accepted future decision.
- Do not treat IDS measurements as SER evidence.
- Do not commit, create a remote, or push unless explicitly requested.

## AuthzGym v1.3 workflow gate

- Read ADR-0019 and
  `experiments/authzgym_semantic_contract_v1_3/PREREGISTRATION.md` before any
  AuthzGym semantic-contract work. Treat its label, population, scoring,
  confirmation, and validity rules as frozen research semantics.
- Follow
  `experiments/authzgym_semantic_contract_v1_3/IMPLEMENTATION_PLAN.md` in order.
  If implementation would require choosing a new label meaning, syntax rule,
  transformation, threshold, population rule, or access condition, stop and
  surface the contradiction. Do not assign the choice to an implementation
  agent.
- Never edit a historical AuthzGym experiment artifact or old ADR to apply the
  v1.3 correction. Current interpretation belongs in the v1.3 corrigendum and
  living state documents.
- The independent answerability checker must consume a public-only bundle and
  must not import or reuse label-producing code, gold arrays, expected tags,
  scorer helpers, oracle helpers, logical roles, usefulness, or conclusions.
- Normal input/state code must not import evaluator/oracle modules. Run
  restricted-field mutation and public-only replay tests; field-name scanning
  alone is insufficient firewall evidence.
- Before the confirmation eligibility decision, inspect only the content-blind
  metadata explicitly allowed by the preregistration. If no-case-specific-
  influence cannot be demonstrated, use the fixed fresh confirmation fallback.
- Do not run a model/provider call for v1.3 until every freeze-checklist item is
  complete, the final manifest verifies from a clean checkout, and a separate
  inference authorization names that manifest. Oracle failure is a blocker, not
  permission to tune the estimator.
- Jev remains deferred and must not influence v1.3 semantics, code paths,
  populations, or acceptance tests.

## Before finishing a change

1. Run `python3 tools/emit_context.py`.
2. Run `python3 tools/check_knowledge_coherence.py`.
3. Read the resulting context packet for misleading promotions or stale state.
4. Report changed files, phase/cursor changes, checks run, unresolved questions,
   and `git status`.
