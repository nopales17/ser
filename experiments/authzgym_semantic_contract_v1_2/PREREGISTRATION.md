# AuthzGym semantic contract v1.2 preregistration

Date frozen before real stress calls: 2026-08-17

## Question and boundary

This development-only protocol asks whether the already selected inexpensive
model can emit a mechanically reliable, bounded, decision-relevant semantic
observation. It is not an SER-vs-ReAct comparison, does not reuse the 24 primary
or 24 perturbation evaluation episodes, and cannot admit a general SER finding.

The immutable real-model v1 run remains `invalid`. Its 609 stored attempts are
reanalyzed offline before this interface is changed. No preserved response or
historical protocol is repaired in place.

## Frozen semantic interface

The model receives exactly one purchased development artifact, the four public
candidate descriptions in positional slots, a compact public epistemic summary,
and public inventory metadata. It never receives evaluator truth, mechanism
labels, expected facts, logical roles, usefulness values, correct conclusions,
unseen source, or action recommendations.

The output has only three fixed objects:

1. twenty-five fixed boolean fact slots covering the existing fact vocabulary
   plus public, non-H-ID aliases for the four test-expectation facts;
2. four fixed candidate-effect slots with enum values `support`, `contradict`,
   `neutral`, or `unknown`;
3. one property for each currently legal uninspected artifact slot, containing
   nine fixed boolean public-relation slots so multiple relations remain
   representable without arrays or generated names.

The model emits no prose, model-generated identifier, symbol, hypothesis ID,
artifact ID, uncertainty string, or routing recommendation. Runtime translation
maps slots back to the already frozen AuthzGym representation. This changes only
the semantic I/O contract and transport envelope; it does not change mechanism
families, H1-H4, ground truth, four-artifact ceilings, usefulness labels, the
SER estimator, or any historical evaluation record.

## Model, transport, retry, and output ceiling

The exact retained model is `patchersniper_praneeth/gpt-5.4-nano`, with Chat
Completions strict JSON Schema, reasoning effort `none`, no temperature, a 1,024
maximum completion-token safety ceiling, 90-second request timeout, 15-second
connect timeout, and at most one identical automatic retry. Any second invalid
attempt makes that stress call invalid. Length termination is invalid even if a
partial payload happens to parse. Manual repair is prohibited.

All execution and persistence remain local on the Mac. The only network path is
an ephemeral local SOCKS5h tunnel through
`nopales17@wiseau.seclab.cs.ucsb.edu`. No remote command, file, prompt, response,
credential, repository, or temporary artifact is created. TLS verification is
disabled only by the dedicated curl client for this approved endpoint. The API
key is supplied through an anonymous inherited configuration pipe and never an
argument or file.

## Development stress population

The source population is exactly the eight frozen v1.1 development episodes,
covering the four authorization mechanism families twice. Each episode produces
eight development-only cases:

- canonical entry artifact;
- longest legitimate artifact;
- public inventory reordering;
- public symbol renaming;
- candidate-label permutation;
- legal artifact-identifier variation;
- the largest legitimate summary after three purchased artifacts;
- combined identifier, symbol, candidate, and order permutation.

Each of the 64 cases is called twice, for exactly 128 scheduled semantic calls.
The transformations are contract stressors, not a new evaluation corpus. No
prompt or schema change follows observation of these calls.

## Cost gate

The hard ceiling for this task is $1.00. Projection assumes every one of the 128
calls uses both allowed attempts, 4,000 uncached input tokens per attempt, and
the complete 1,024-token output ceiling at frozen rates of $0.20/M input,
$0.02/M cached input, and $1.25/M output. Evaluation proceeds only if that
worst-case projection is below $1. Runtime reserves the same per-attempt maximum
and fails closed before a call that could cross the cap. Cost is provider-usage
accounting, not an invoice.

## Preregistered contract classifier

`contract_stable` requires all of:

- first-attempt schema-valid rate >= 0.99;
- valid after the allowed retry = 1.00;
- zero `finish_reason=length` attempts;
- zero incomplete JSON attempts;
- zero illegal artifact, hypothesis, or relation references;
- zero manual repairs;
- zero secret or information-boundary violations;
- complete schedule, valid response/run hashes, frozen inputs, single model, and
  total spend below $1.

An integrity, access, hash, population, or spend failure is `invalid`. A complete
integrity-valid run missing any mechanical threshold is `contract_unstable`.

## Separate semantic diagnostic

Only contract-valid responses enter these development diagnostics:

- fact precision >= 0.65 and recall >= 0.50 is "reasonable fact signal";
- hypothesis-effect precision >= 0.60 and recall >= 0.50;
- unresolved-relation precision >= 0.60 and recall >= 0.50;
- downstream top-1 >= 0.60, top-2 >= 0.80, and mean normalized regret <= 0.35.

`semantic_signal_promising` requires every semantic and downstream threshold.
`semantic_signal_absent` requires zero true positives across all three semantic
layers. Every other result is `semantic_signal_weak`. This semantic label does
not determine mechanical contract stability and does not promote H-018.

Perturbation-equivalent outputs are normalized to fact slots, semantic candidate
relations, and logical target roles only after execution. Exact pair stability
and repeat stability are diagnostics, not contract-validity gates.

## Oracle-conditioned action-value diagnostic

Evaluator-only analysis supplies the correct structured observation for each of
the eight canonical development entries to the unchanged updater and explicit
value estimator. The estimator is called adequate under this diagnostic only if
it clears the same top-1, top-2, and normalized-regret thresholds above. Oracle
content never enters a model prompt or normal controller state.

## Mechanical next-experiment rule

1. If the contract is not stable, create another contract version and do not run
   an architecture evaluation.
2. If stable but fact signal is below threshold, keep v1.2 frozen and test the
   next stronger inexpensive model; do not redesign the benchmark.
3. If facts are reasonable but effects or unresolved relations are weak, isolate
   `fact -> decision-relevant implication` in a separate preregistration,
   potentially comparing deterministic and model derivation.
4. If perfect observations fail the oracle-conditioned threshold, repair the
   deterministic value estimator only in a separate experiment.
5. If contract, all semantic layers, model-conditioned action values, and the
   oracle diagnostic pass, the next study is a separately preregistered
   architecture comparison on a fresh confirmatory population. The observed
   original 24 may be used only as recovery/diagnostic replication.

No stronger model, old evaluation rerun, fresh confirmatory population,
executable AuthzGym, GitLab, IDS, fuzzing, runtime requests, graph state,
coupling mechanism, learned routing, or hypothesis promotion occurs here.
