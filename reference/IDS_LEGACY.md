# IDS-to-CVE historical project

## Boundary and provenance

Historical repository:
`/Users/paolo/proj/ids-rule-to-cve-inference-archive`

It was inspected read-only on 2026-08-17. It remains a separate, completed
internship repository. This document is a scoped reference summary, not an import
manifest and not SER evidence.

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

## Why it may be useful later

As `H-011` states, the archive may offer a future real environment because it has
partial evidence, known labels, several possible information-acquisition paths,
frozen artifacts, and explicit controls. Whether it exposes a meaningful
*sequential allocation* problem is not yet established.

Potential inventory candidates for Phase 1 include:

- the documentation governance pattern: authority by location, ADRs, generated
  state, and coherence checking;
- deterministic construction, hashing, provenance manifests, and trace
  contracts;
- separation between construction, method-under-test, controls, evidence, and
  claim limits;
- staged knowledge-access conditions and matched-baseline discipline;
- environment-facing data interfaces, scoring functions, and frozen artifacts;
- scope-aware reporting practices such as explicit populations, task labels, and
  applicability limits.

This list means "inspect," not "reuse." The initial Phase 0 inspection did not
establish a general interval/scope implementation suitable for `P-003`; any such
candidate must be found, understood, and classified during Phase 1.

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

## Phase 1 classification rule

Every inspected candidate must receive one classification with rationale:

1. reuse unchanged;
2. generalize behind a domain-independent interface;
3. empirical evidence only;
4. inspiration only; or
5. discard.

No classification itself authorizes code or data transfer. A later roadmap step
and, where architectural, an ADR must authorize implementation.

