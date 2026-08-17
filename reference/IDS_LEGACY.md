# IDS-to-CVE historical project

## Boundary and provenance

Historical repository:
`/Users/paolo/proj/ids-rule-to-cve-inference-archive`

It was inspected read-only on 2026-08-17 at commit
`38b661324725c094ffcc820371a836573f4aadc5`. It remains a separate, completed
internship repository. This document is a scoped reference summary, not an import
manifest and not SER evidence. The canonical component judgments are in
`reference/LEGACY_INVENTORY.yaml`.

## What the project actually studied

The archive describes a measurement instrument for recovering the vulnerability
targeted by an IDS rule from progressively sanitized rule signal. It separated:

- closed-book reconstruction of vulnerability shape from a rule view; and
- closed-corpus attribution of that rule or frozen reconstruction to an exact
  CVE among candidate records.

Construction was deterministic and used labeled public rules to retain known
ground truth after removing answer-bearing metadata. The project built frozen
rule views, CVE-derived labels, candidate corpora, baseline and model-assisted
runs, trace/audit infrastructure, and matched analyses. Its own final
documentation records negative and corrected results as well as successes. In
particular, it does not claim to have solved exact-CVE sibling discrimination or
to have built a general inference architecture.

Those findings are scoped to the IDS benchmark, its frozen populations, access
conditions, models, and metrics. The archive explicitly distinguishes measured
reconstruction/attribution results from broader transfer or dual-use claims.

## Phase 1 finding

As `H-011` states, the archive may offer a future real environment because it has
partial evidence, known labels, frozen artifacts, and explicit controls. Phase 1
did not establish a meaningful *sequential allocation* problem: the archived task
is a static candidate-retrieval and attribution instrument.

The inventory classified 31 component groups: zero for unchanged reuse, 11 for
generalization as clean SER-owned patterns, 14 as empirical evidence only, four
as inspiration only, and two for discard. The strongest surviving patterns are:

- deterministic construction, hashing, provenance manifests, and trace
  contracts;
- fail-closed completeness, stage-access, isolation, and secret checks;
- evaluator/controller information separation, blinding, paired controls, and
  deterministic replay;
- append-only preservation of negative, invalid, aborted, and corrected runs.

These are patterns to reimplement after SER contracts exist, not code to copy.
Deep current-tree and reachable-history inspection found no generic `Scope` or
`Interval`, no `EpistemicMemoryUnit` or `FlagAttachment`, no relevant generic
`Signal`, and no executable semantics for the preserved SER coupling-operator
names. Same-product neighborhoods and APF/APF2 filters are not substitutes.

## What must not transfer automatically

- Suricata/IDS rule parsing, sanitization levels, CVE schemas, CWE/product
  normalization, same-product neighborhoods, cyber-specific vocabulary, and the
  particular retrieval/comparator stack are domain-specific by default.
- Frozen datasets and historical traces remain historical artifacts; do not copy
  or relabel them as SER data.
- Benchmark scores and ablations do not validate `H-001`, `H-003`, `H-004`, or
  any other SER hypothesis.
- Post-poster agentic or learned experiments in the archive are explicitly
  exploratory/incomplete and must not be presented as accepted results.
- Known archive documentation defects, including a stale roadmap and a generated
  status scope defect called out by its README, are cautions against mechanical
  reuse.

## Phase 1 classification result

Every inspected candidate received one of the required classifications with
source, assumptions, evidence, confidence, and recommended action recorded in
the canonical inventory:

1. reuse unchanged;
2. generalize behind a domain-independent interface;
3. empirical evidence only;
4. inspiration only; or
5. discard.

No classification authorizes code or data transfer. `generalize` means rebuild a
pattern behind new SER-owned contracts. Environment assets remain in the archive
unless a later roadmap step and explicit decision authorize ingestion.
