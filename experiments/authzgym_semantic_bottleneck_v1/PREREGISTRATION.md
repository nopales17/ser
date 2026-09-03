# AuthzGym semantic bottleneck v1 preregistration

Date frozen before any new model inference: 2026-09-03

## Question and boundary

This Phase 5A diagnostic asks which upstream component best explains the valid
`gpt-5.4-mini` development failure under semantic contract v1.2: model semantic
weakness, elicitation/interface burden, representational insufficiency, or
benchmark/task ambiguity. It is not another population capability benchmark,
does not compare routing architectures, does not alter v1.2, and cannot promote
H-001, H-016, H-017, or H-018.

The prior oracle result is retained: perfect evaluator v1.2 content gives
top-1/top-2/regret `1.0/1.0/0.0` through the unchanged deterministic estimator.
This study is therefore restricted to `artifact -> semantic state`.

## Ordered gates

1. Audit every incorrect result in the 16 already exposed, executed development
   cases. No confirmation case, prompt, or raw content may be loaded.
2. Independently check whether each evaluator label is recoverable from the
   exact model-visible source, prompt, candidate descriptions, and inventory.
3. Freeze four to eight challenge cases from the audit, including complete
   equivalent pairs and a relative successful control where possible.
4. Stop before new inference if any selected case has unavailable or
   prompt-inconsistent evaluator truth. Preserve the frozen selection and null
   paid conditions.
5. Only if the answerability gate passes, freeze a decomposed Mini prompt and
   one genuinely stronger-model v1.2 condition, prove their worst-case spend is
   below $0.25, and then call them without tuning.

The answerability stop has precedence over model availability, model selection,
prompt construction, and paid execution. Discovering it is a valid diagnostic
outcome rather than a reason to repair labels in place.

## Offline audit taxonomy

Each evaluator/model disagreement is classified, where possible, as:

- false-positive or false-negative fact;
- incorrect or missed candidate effect;
- false-positive or missed unresolved relation;
- transformation instability;
- artifact insufficiency;
- evaluator-label mismatch;
- task ambiguity; or
- other.

The audit also tests, without assuming, the overcommit hypothesis that the model
asserts candidate effects while failing to expose uncertainty through the
unresolved-relation channel. Only observable outputs may support this; hidden
reasoning is never inferred.

For fact answerability, the audit applies the frozen slot definitions literally
to current visible source without using `ArtifactSpec.expected_fact_keys`, since
those keys are the labels under audit. Relation answerability is independently
reconstructed from visible calls and public exported symbols. A slot that needs
an evaluator-only logical role is marked unavailable.

## Frozen challenge-selection rule

If possible, select two complete base/order-equivalent pairs from the executed
development prefix: one dominated by overcommit and unresolved omissions, and
one containing a relative control that recovers all authored-positive fact
labels. Selection is based only on the offline taxonomy. The exact case IDs,
rationales, and answerability findings are frozen in
`FROZEN_CASE_SELECTION.json`.

## Conditional model conditions

- **A — stored baseline:** reuse the existing v1.2 Mini outputs; never rerun.
- **B — decomposed Mini:** independently ask bounded fact, effect, and relation
  questions with ternary or frozen-enum answers and concise evidence pointers,
  without chain-of-thought. Freeze exact prompts and schema before calls.
- **C — stronger unchanged v1.2:** run one genuinely stronger usable model on
  the same selected cases under the exact v1.2 prompt and schema, with no tuning.

Conditions B and C are null if the answerability gate fails. A null condition is
not evidence that the condition would have succeeded or failed.

## Cost and transport

The incremental hard ceiling is **$0.25**, with expected cost at or below
**$0.10**. Worst-case retries must be priced before any call, and the runner must
fail closed if the projection is not strictly below the ceiling. Transport,
provider responses, schema failures, and semantic retries remain separate.

If calls become authorized, the configured endpoint may use only the previously
approved endpoint-scoped insecure/no-TLS-verification path through the supervised
SSH/SOCKS envelope. Credentials must remain in the anonymous curl configuration
pipe and outside artifacts and command arguments.

## Classification

The narrow terminal labels are:

- `model_capability_bottleneck_supported`;
- `semantic_elicitation_bottleneck_supported`;
- `representation_insufficiency_candidate`;
- `benchmark_ambiguity_detected`;
- `mixed_semantic_bottleneck`;
- `diagnostic_inconclusive`; or
- `invalid`.

An answerability failure has precedence and yields
`benchmark_ambiguity_detected` when independently reproducible. Its only next
empirical decision is benchmark/task-definition repair. No E-* item, ADR,
stable concept, hypothesis promotion, v1.3 contract, or architecture experiment
is authorized here.
