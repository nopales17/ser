# AuthzGym semantic bottleneck v1 report

## A. Repository state

The study began at `ed53f944c9b75a07247ebec9f8ce37e90b50fe2f` on
`main`, two commits ahead of `origin/main`, with a clean worktree. All 19
knowledge-coherence checks passed. The active cursor remained Phase 5.

The stronger-model confirmation population was not loaded by the diagnostic
tool, its execution directory remained absent, and it received zero model
calls. Only the already exposed 16-call development prefix and its stored raw
responses were audited.

## B. Previous-result localization

The prior result already established two narrow facts. First, the mechanically
valid Mini channel failed multiple development thresholds and all eight executed
equivalence checks. Second, perfect evaluator v1.2 content passed through the
unchanged deterministic action-value estimator at top-1 `1.0`, top-2 `1.0`, and
regret `0.0`, including the fresh oracle diagnostic. The measured bottleneck is
therefore upstream of action ranking, in `artifact -> semantic state`.

Those facts did not distinguish model inability, elicitation burden, or task
ambiguity. This diagnostic found that the aggregate fact/effect scorer itself is
not answerable under the frozen model-visible contract.

## C. Offline failure taxonomy

All 16 executed development cases and every evaluator/model disagreement were
audited before any new inference.

| Discrepancy category | Count |
| --- | ---: |
| Evaluator-label mismatch | 28 |
| Artifact insufficiency or label ambiguity | 24 |
| False-positive effect / model overcommit | 13 |
| False-negative fact / model omission | 10 |
| False-positive fact / model overcommit | 8 |
| Incorrect or missed effect | 7 |
| Missed unresolved relation | 68 |

The original evaluator comparison contained 40 false-positive and 16
false-negative facts. The independent prompt-grounded audit reclassified 28 of
those discrepancies as evaluator-label mismatches: the model asserted a fact
directly established by the visible source but the curated evaluator key marked
it false. Examples include `include_inherited=True`,
`token_scope=request.token.scope`, and
`feature_context=request.flags`, which directly satisfy f2, f8, and f9 but are
absent from the entry-artifact evaluator labels.

Three longest-artifact cases expose an independent answerability defect. The
evaluator expects f20 and a test-family fact, but the model-visible artifact has
an opaque filename and symbol and receives no logical-role label. Whether it is
“test code” is evaluator-only information. Across all slots, the audit found 74
fact-label and 42 effect-label answerability mismatches or unavailable labels;
every one of the 16 cases was affected.

Unresolved-relation labels were different: all 16 sets reproduced exactly from
visible calls and public inventory. The model nevertheless missed 68 of 69
positive relations. This is real evidence of weak extraction under the existing
one-shot task, although it does not identify model versus elicitation cause.

The overcommit hypothesis receives moderate descriptive support, with an
important contamination caveat. The model emitted 30 non-unknown candidate
effects while missing 68 answerable unresolved relations. Thirteen categorical
disagreements were unsupported positive effects even after the prompt-grounded
audit. No hidden reasoning is inferred.

## D. Frozen diagnostic cases

Four cases were frozen as two complete order-equivalent pairs:

| Mechanism | Variant | Case ID | Diagnostic role |
| --- | --- | --- | --- |
| h1 | base | `asv1-d-5e6417ce899f--base_entry--71eb766486` | fact/effect overcommit plus missed unresolved relations |
| h1 | reordered | `asv1-d-5e6417ce899f--artifact_reordering--0e8b205ac2` | order-sensitivity peer |
| h4 | base | `asv1-d-f5f54c9c8670--base_entry--0dd132fa21` | conservative omission of answerable context-loss facts |
| h4 | reordered | `asv1-d-f5f54c9c8670--artifact_reordering--fbd1de3a37` | relative control recovering all authored-positive facts but adding unsupported assertions |

Every selected case failed the preregistered answerability gate. The selection
was frozen, then new inference was prohibited as required by the stop rule.

## E. Conditions and configurations

- Condition A reused the exact stored Mini/v1.2 outputs and made no new calls.
- Condition B, decomposed Mini interrogation, was not frozen or executed after
  the answerability stop.
- Condition C, a stronger model under unchanged v1.2, was not selected or
  executed after the answerability stop.

These null conditions say nothing about how either intervention would perform.
No endpoint access occurred, so the approved insecure TLS flag was not used.

## F. Mini decomposed-query results

Not run. Running decomposition against labels known to be unavailable or
prompt-inconsistent would not distinguish semantic competence from scorer
misalignment and would violate the frozen stop rule.

## G. Transformation-equivalence results

All eight stored base-versus-equivalent comparisons failed exact normalized
semantic agreement:

- four artifact-order pairs changed semantics;
- four symbol-renaming pairs changed semantics;
- facts changed in six pairs;
- candidate effects changed in six pairs;
- unresolved relations changed in one pair.

Equivalence itself is evaluator-independent here, so this remains valid evidence
of transformation instability. Without the decomposed condition, it is only
weak evidence that one-shot elicitation contributes to the instability.

## H. Stronger-model v1.2 probe

Not run. A stronger model would still be judged by the same invalid fact/effect
targets, so the result could not cleanly localize a model capability floor.

## I. Diagnostic matrix

| Candidate bottleneck | Assessment | Concrete support |
| --- | --- | --- |
| Model weakness | moderate evidence | 10 answerable fact omissions, 68/69 unresolved relations missed, and 0/8 exact equivalent pairs |
| Elicitation/interface weakness | weak evidence | high one-shot decision burden and transformation instability; decomposition was not run |
| Representational insufficiency | no evidence | v1.2 can encode unknown effects and unresolved target relations; no correct but unencodable distinction was observed |
| Task ambiguity | strong evidence | all 16 cases have unavailable or prompt-inconsistent labels; 28 scored fact errors match source-direct prompt semantics |

## J. Cost

Incremental logical calls, provider submissions, responses, tokens, retries, and
transport failures were all **0**. Incremental cost was **$0.00** of the **$0.25**
maximum, or **0%** of the authorized budget.

## K. Classification

**`benchmark_ambiguity_detected`**

This does not erase genuine observed Mini omissions or instability. It means the
current benchmark cannot validly decide whether Mini or a stronger model clears
the full fact/effect semantic floor, because correct source-direct assertions
can be scored wrong and some required labels depend on hidden role information.

No E-* item, ADR, stable concept, hypothesis promotion, or v1.3 contract is
created.

## L. Exact next empirical decision

**3. Benchmark/task-definition repair.**

Repair answerability in a separately versioned benchmark protocol before model
escalation or a representation intervention. The repair must align fact/effect
gold with the public slot definitions or expose the minimum role information
needed to answer them, then revalidate the evaluator firewall and deterministic
oracle. It must not rewrite v1.2 or the preserved stronger-model result.
