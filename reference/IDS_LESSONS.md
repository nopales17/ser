# Lessons from the IDS archive

This is a research synthesis of the read-only IDS archive at commit
`38b661324725c094ffcc820371a836573f4aadc5`. It is not SER evidence and it does
not authorize code or data transfer. Component-level judgments live in
`reference/LEGACY_INVENTORY.yaml`.

## What the IDS work established

- The archived project built a reproducible measurement instrument for two
  bounded tasks: closed-book rule-to-shape prediction and closed-corpus
  rule/shape-to-CVE attribution. It did not solve general inference.
- On the repeatedly inspected `eligible31` development population, the apparent
  predicted-product result of 13/31 fell to 3/31 under a term-frequency clamp;
  96.77% of affected rankings tied. Product identity and lexical style were
  major confounds.
- Product-set retrieval usually narrowed the candidate pool but rarely decided
  the answer. Non-product evidence produced only a bounded development result.
- The U2 candidate universe omitted other benchmark ground truths. The corrected
  U3 universe changed the valid task population and exposed an identical-
  description pair. Population validity had to precede performance claims.
- APF1 model-generated Python filters were unsafe and could eliminate the gold
  answer. APF2's declarative three-valued replacement was safer but eliminated
  no candidates in its completed development run.
- The Agentic Query Bridge engaged the corpus, but product terms dominated and
  it did not beat the predicted-product baseline.
- The archived trace, manifest, access-policy, sanitization, completeness,
  blinding, and deterministic-replay machinery demonstrated useful engineering
  patterns. The archive also preserved negative, aborted, invalid, and corrected
  runs rather than silently erasing them.

## What it suggested but did not establish

- Separating observations, inferable propositions, alternatives, and unknowns
  may improve epistemic-state discipline. The CDA scaffold tested schemas and
  deterministic diagnostics, but made no model calls and produced no adopted
  experimental result.
- Declarative, validated controller actions may be safer than executable
  model-authored policy code. APF2 supports the safety motivation, not a general
  SER action or coupling design.
- Environment-owned information views, scopes, costs, and access policies are
  likely necessary for interpretable allocation experiments. The IDS
  sanitization ladder and product neighborhoods are only domain examples.
- Retrieval can be one resource-bearing action in an environment. IDS did not
  establish that retrieval-first or representation-then-retrieval is a general
  reasoning architecture.
- No archive evidence establishes adaptive reasoning allocation, graph-based
  state, coupling dynamics, or transfer across environments.

## What failed or proved fragile

- Headline improvements were vulnerable to product identity, term frequency,
  exact-string normalization, lexical overlap, and candidate-pool construction.
- The candidate-aware Phase 2G comparator was order-sensitive and incompletely
  prompted. Its reported 25/31 outcome is not a valid single corrected score.
- Effects concentrated on the easiest cases, while the development set was
  repeatedly inspected. Attempts to acquire a separate Dev2 population failed
  minimum floors; no valid holdout exists.
- Benchmark v1 and v2 were frozen but never used for an evaluation case. A
  validated package is infrastructure, not empirical evidence.
- Static candidate lists, single hidden answers, product gates, and fixed stage
  boundaries made apparently generic components depend on the IDS task.
- A generated status view continued to summarize an older 50/150-rule substrate
  while later post-poster work existed. Fresh output can still be misleading if
  its canonical input set is incomplete.

## What SER should test differently

- Pre-register the environment population, controller-visible information,
  evaluator-only labels, outcomes, resource units, and invalid-run rules before
  controller iteration.
- Compare adaptive policies with fixed, random, exhaustive, ordinary-agent, and
  token/cost-matched frontier-reasoning baselines where applicable.
- Use shortcut and leakage controls that remove identity, frequency, formatting,
  ordering, and candidate-pool cues one at a time.
- Separate controller actions from environment execution and outcome scoring;
  trace every request, rejection, observation, transition, resource charge, and
  result with frozen versions and seeds.
- Establish population and universe validity before reporting performance, and
  reserve an untouched holdout or state plainly that only development evidence
  exists.
- Test the same minimal contracts in environments that do not have candidate
  lists, retrieval, or a single hidden answer before calling them general.

## What SER must not claim from IDS

- IDS measurements are not SER experiments and do not support any SER
  hypothesis as `experimentally_supported`.
- A product neighborhood is not an implementation or validation of `P-003`
  Scope. The archive contains no generic `Scope` or `Interval` definition.
- The archive contains no `EpistemicMemoryUnit`, relevant generic `Signal`, or
  `FlagAttachment` model, and no executable semantics for SER operators `RES`,
  `GATE`, `AMP`, `DAMP`, `INHIBIT`, `SCOPE_FILTER`, `TOPK`, `DEFEAT`, or
  `PROMOTE`.
- IDS prompts, rankers, comparators, filters, schemas, and normalizers are prior
  solution logic, not reusable SER architecture.
- The archived benchmark, frozen manifests, and engineering tests do not prove
  that a controller improves reasoning, adapts online, or transfers.
