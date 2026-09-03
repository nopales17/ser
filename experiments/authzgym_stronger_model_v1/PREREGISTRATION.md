# AuthzGym stronger-model semantic capability v1 preregistration

Date frozen before AuthzGym inference: 2026-09-03

## Question and boundary

This staged Phase 5A experiment asks whether one stronger but still inexpensive
model can clear the already accepted semantic-capability floor under semantic
contract v1.2. It does not compare SER with another architecture, exercise live
software, alter the action-value estimator, or admit a general SER finding.

The intervention is only the model identifier. The prompt, strict response
schema, vocabulary, positional identifiers, parser, 1,024-token output ceiling,
and deterministic downstream estimator are the immutable v1.2 versions. There
is no post-result prompt, schema, vocabulary, retry, or estimator tuning.

## Frozen model selection

A credentialed but zero-inference `/models` catalog request was made before any
AuthzGym call. `MODEL_SELECTION.json` records the plausible catalog-listed
options and the mechanical selection rule. The selected model is exactly
`patchersniper_praneeth/gpt-5.4-mini`: the immediate tier above the prior
`patchersniper_praneeth/gpt-5.4-nano` on the same provider route and in the same
model family. Official documentation lists Chat Completions, structured outputs,
and reasoning effort `none` for the nominal model.

The exact API configuration is Chat Completions strict JSON Schema, reasoning
effort `none`, no temperature parameter, 1,024 maximum completion tokens,
90-second request timeout, 15-second connect timeout, and at most one identical
semantic retry. One independent transport reconnection/replay remains available
under the frozen transport-envelope policy, so a logical call can make at most
three byte-identical or schema-identical API submissions in the failure case.
Manual repair is prohibited.

The endpoint remains reachable only through the local supervised SSH/SOCKS hop.
The user explicitly approved its scoped insecure/no-TLS-certificate-verification
flag on 2026-09-03. The bearer credential is supplied through an anonymous local
curl configuration pipe, is removed from the SSH child environment, and is never
written to an experiment artifact or command argument.

### Preserved smoke-analysis correction

An initial four-call smoke attempt completed its provider and transport work but
exposed an offline analysis integration defect before development: the inherited
summary routine requested transformation peers that a base-only smoke population
does not contain. `PREFLIGHT_FAILURE.md` and `preflight_attempt_1/` preserve the
original manifest and complete attempt. The correction adds only a base-only
smoke contract/accounting summary; all semantic inputs and execution behavior
remain unchanged. Its $0.012318 cost is charged to the same $2.50 ceiling.

## Frozen populations and stages

All population identities and file hashes are bound by `FROZEN_INPUTS.json`
before the first smoke inference.

1. **Smoke:** four already exposed `base_entry` cases, one per mechanism family.
   These calls test only endpoint, strict-schema, parser, transport, and accounting
   compatibility. They are excluded from semantic evidence.
2. **Development:** 32 already exposed cases. Four source episodes are chosen
   before inference by the fixed alternating-layout rule `(h1 layout 0, h2 layout
   1, h3 layout 0, h4 layout 1)`, and each is crossed with all eight frozen v1.2
   transformations. The schedule is interleaved by transformation then mechanism.
   Each case is called once.
3. **Confirmation:** 64 fresh cases generated before inference with the existing
   AuthzGym authoring method, previously unused split/layout inputs 30 and 31,
   all four existing mechanism families, and all eight frozen v1.2 transformations.
   Each case is called exactly once. Source IDs, public input hashes, generated
   paths, non-invariant exported symbols, and case IDs must be disjoint from
   every exposed development, evaluation, and perturbation source. The authoring
   method's common public entry-point name `handle_request` is intentionally
   invariant and is not an episode identity. Evaluator truth remains outside
   every model-visible input.

Confirmation is run only if smoke and development both satisfy their gates and
the fresh oracle diagnostic is adequate. Confirmation is never used for tuning,
and its evaluator truth is not scored until every scheduled response is frozen.
The old 24 evaluation and 24 perturbation episodes remain exposed diagnostic
material and are never used as confirmation.

Repeated-call exactness is not scheduled under the user-set cost ceiling. It was
a diagnostic rather than a v1.2 gate. Transformation equivalence remains a
diagnostic on every development and confirmation source episode.

## Frozen thresholds

Metrics retain their historical micro-aggregation and direction. Only
contract-valid responses enter semantic metrics.

| Metric | Exact definition | Population | Threshold | Direction | Role | Source |
| --- | --- | --- | ---: | --- | --- | --- |
| Provider-response completion | logical calls receiving a provider response after the one allowed transport replay / scheduled calls | each stage | 1.00 | >= | primary prerequisite | transport-envelope v1 preregistration |
| First-attempt schema validity | first provider responses satisfying finish, complete JSON, strict schema, and v1.2 parser / first attempts | development; confirmation | 0.99 | >= | primary prerequisite | semantic-contract v1.2 preregistration |
| Post-retry validity | valid logical responses after at most one identical semantic retry / completed logical calls | development; confirmation | 1.00 | >= | primary prerequisite | semantic-contract v1.2 preregistration |
| Length/incomplete/illegal/manual/boundary failures | count of length finishes, incomplete JSON, illegal artifact/candidate/relation references, manual repairs, or information-boundary violations | development; confirmation | 0 each | <= | primary prerequisite | semantic-contract v1.2 preregistration |
| Fact precision | micro true-positive fixed fact booleans / all asserted fixed fact booleans | development; confirmation | 0.65 | >= | primary | semantic-contract v1.2 `SEMANTIC_THRESHOLDS` |
| Fact recall | micro true-positive fixed fact booleans / evaluator-expected fixed fact booleans | development; confirmation | 0.50 | >= | primary | semantic-contract v1.2 `SEMANTIC_THRESHOLDS` |
| Candidate-effect precision | micro correct `(candidate slot, support-or-contradict)` pairs / all asserted non-neutral pairs | development; confirmation | 0.60 | >= | primary | semantic-contract v1.2 `SEMANTIC_THRESHOLDS` |
| Candidate-effect recall | micro correct non-neutral candidate-effect pairs / evaluator-expected non-neutral pairs | development; confirmation | 0.50 | >= | primary | semantic-contract v1.2 `SEMANTIC_THRESHOLDS` |
| Unresolved-relation precision | micro correct `(target slot, relation slot)` booleans / all asserted relation booleans | development; confirmation | 0.60 | >= | primary | semantic-contract v1.2 `SEMANTIC_THRESHOLDS` |
| Unresolved-relation recall | micro correct relation booleans / evaluator-expected relation booleans | development; confirmation | 0.50 | >= | primary | semantic-contract v1.2 `SEMANTIC_THRESHOLDS` |
| Useful-action top-1 | fraction of model-conditioned deterministic rankings whose first action has maximum evaluator usefulness among remaining actions | development; confirmation | 0.60 | >= | primary | semantic-contract v1.2 `SEMANTIC_THRESHOLDS` |
| Useful-action top-2 | fraction whose first two ranked actions contain a maximum-usefulness remaining action | development; confirmation | 0.80 | >= | primary | semantic-contract v1.2 `SEMANTIC_THRESHOLDS` |
| Normalized action regret | mean `(best usefulness - selected usefulness) / (best - lowest usefulness)` | development; confirmation | 0.35 | <= | primary | semantic-contract v1.2 `SEMANTIC_THRESHOLDS` |
| Oracle top-1/top-2/regret | same three action metrics after evaluator-only perfect v1.2 observations enter the unchanged estimator | development; fresh confirmation | 0.60 / 0.80 / 0.35 | >= / >= / <= | prerequisite diagnostic | semantic-contract v1.2 preregistration |
| Transformation equivalence | exact normalized facts, effects-by-relation, and unresolved-relations-by-logical-role for base versus each semantic-equivalence transformation | development; confirmation | none | descriptive | diagnostic | semantic-contract v1.2 preregistration |
| Repeat exactness | exact normalized semantic equality for repeated identical calls | not scheduled | none | descriptive | diagnostic | semantic-contract v1.2 preregistration |

`semantic_signal_promising` retains its exact v1.2 meaning: all six semantic and
all three model-conditioned downstream thresholds pass. No average or partial
credit can substitute for a failed primary threshold.

## Oracle and benchmark-validity gate

The evaluator-only oracle observation is passed to the unchanged updater and
action-value estimator after population freeze. It must clear top-1 0.60, top-2
0.80, and mean normalized regret 0.35 on both development and fresh canonical
entries. If the fresh oracle fails, confirmation inference is prohibited and the
result is `benchmark_invalid`; no model-capability attribution is allowed.

## Development early stop

Development is checked only after balanced 8-call blocks. Stop at calls 8, 16,
or 24 if either (a) any contract failure makes the 0.99 first-attempt or 1.00
post-retry thresholds mathematically unreachable, or (b) even assigning every
remaining expected semantic item and action outcome perfectly cannot bring any
primary metric across its frozen threshold. The optimistic precision bound adds
only true-positive predictions for all remaining evaluator-expected items; the
recall bound makes all remaining expected items true positives; top-1/top-2 make
all remaining calls successful; regret assigns zero to all remaining calls.

If no futility boundary fires, all 32 development calls run. Confirmation is
permitted only when transport is stable, the response contract is stable, every
semantic and downstream threshold passes, and the development and fresh oracle
diagnostics pass. A development failure ends the paid protocol without changing
the model, prompt, schema, representation, estimator, or benchmark.

## Cost gate

The user-set hard ceiling is **$2.50**. Official list rates used for conservative
accounting are $0.75/M uncached input, $0.075/M cached input, and $4.50/M output;
this is not an institutional billing statement. The maximum schedule is 4 smoke
+ 32 development + 64 confirmation = 100 logical calls. Treating all three
possible submissions per call as billable at 4,000 uncached input and 1,024
output tokens gives 1,200,000 input tokens, 307,200 output tokens, and a worst
case of **$2.282400**. The runner reserves against the global $2.50 ceiling before
every submission and also caps the experiment at 300 submissions.

## Classification and next decision

Precedence is: integrity/information/population/oracle failure ->
`benchmark_invalid` or `experiment_invalid`; permanent transport loss ->
`transport_unstable`; mechanical response failure ->
`response_contract_unstable`; development below any capability threshold ->
`semantic_capability_below_threshold`; development pass followed by confirmation
failure -> `semantic_capability_development_only`; both pass ->
`semantic_capability_confirmed`.

No outcome promotes H-001, H-016, H-017, H-018, creates an E-* finding, or
establishes SER advantage. A confirmed result permits only a new, separately
preregistered matched architecture comparison. A below-threshold result permits
only one separately chosen next empirical investigation under the failure
taxonomy.
