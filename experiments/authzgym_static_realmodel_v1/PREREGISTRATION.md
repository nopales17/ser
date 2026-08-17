# Static Semantic AuthzGym real-model v1 preregistration

Date frozen before evaluation: 2026-08-17

## Question and evidential boundary

This is the first actual-model layer over the already frozen AuthzGym protocol
1.1 population. It asks whether one inexpensive semantic model can recover
bounded authorization structure and whether explicit SER state/value organization
adds leverage over matched fixed-order and ordinary ReAct-like control.

The experiment does not redesign or regenerate any v1/v1.1 episode. It cannot
validate an SER runtime, executable authorization testing, historical transfer,
GitLab readiness, IDS reuse, bounty ROI, learned routing, or general coupling
claims. Twenty-four evaluation episodes are pilot evidence only.

## Frozen condition

Exactly one model is used: `patchersniper_praneeth/gpt-5.4-nano`, selected from a
credentialed model-catalog request before any benchmark inference because it was
the endpoint's inexpensive nano-class option, supports structured extraction, and
fits the bounded context. Selection did not use development or evaluation accuracy.

The provider-neutral semantic interface is implemented separately from the scoped
transport. The local transport is Python 3.14.6 plus system curl 8.7.1, routed via
an ephemeral local `socks5h` tunnel. TLS chain verification is disabled only for
this configured API client, as explicitly authorized. Credentials remain local
environment values and are supplied to curl over an anonymous pipe, never a file
or process argument.

The API uses Chat Completions strict JSON Schema, reasoning effort `none`, no
temperature parameter, 320 maximum completion tokens per purchased artifact,
90-second request timeout, 15-second connect timeout, and at most one automatic
retry under the identical frozen request. A second invalid response makes that
semantic decision and run invalid. No manual repair is allowed.

## Semantic contract and information boundary

Every call receives only purchased source; H1-H4 descriptions/relation tags under
their current opaque IDs; public inventory metadata; current policy-visible state;
legal remaining artifact IDs; and the frozen prompt. It never receives unpurchased
source, evaluator truth, mechanism IDs, expected facts, usefulness values,
discriminating roles, future observations, web/repository tools, or private
chain-of-thought requests.

The output is a constrained set of authorization fact keys, concise public facts,
bounded hypothesis effects, unresolved public-symbol relations, uncertainty flags,
and one legal next-artifact recommendation when another sequential action remains.
The recommendation is emitted for all sequential conditions: fixed ignores it;
ReAct-like follows it as its model/tool loop; SER ignores it and selects through
external structured epistemic state plus the already frozen explicit action-value
function. Thus underlying semantic capability and evidence entitlement are held
constant while controller organization differs.

## Architectures, population, and schedule

All four frozen architectures run:

1. `fixed_order_semantic`: required common entry then public order;
2. `react_like_semantic`: required common entry then the model's legal recommendation
   from accumulated tool-loop state;
3. `ser_explicit_value`: required common entry then maximum external explicit value
   from extracted unresolved relations and hypothesis support;
4. `monolithic_semantic`: secondary one-call baseline over exactly the first four
   public-order artifacts.

Fixed, ReAct-like, and SER use four purchased artifacts and four semantic decisions.
Monolithic uses four artifacts in one decision. Provider attempts include at most
one retry per decision. Sequential runs have frozen provider ceilings of 12,000
input and 2,000 output tokens; monolithic runs have 12,000 input and 1,280 output
tokens. These are provider-token ceilings chosen before evaluation as the closest
safe mapping of the older 6,000/2,000 deterministic lexical-proxy ceiling without
truncating legitimate accumulated state.

The primary 24 episodes run first, followed by all 24 paired perturbations. Within
each split, architecture order rotates by episode across the four architectures to
balance temporal position. The exact schedule is content-addressed in
`FROZEN_INPUTS.json` before evaluation.

## Development call and hard cost gate

One minimal call on the first development episode's common entry artifact checks
connectivity, proxy/TLS behavior, strict-schema parsing, usage metadata, retry
behavior, and cost accounting. It is not used for accuracy tuning.

Before evaluation, the complete-cost projection takes the larger of:

- measured development input cost scaled to at least 3,000 input tokens for each
  sequential attempt and 12,000 for each monolithic attempt, with every output at
  its configured maximum; and
- the same configured ceiling projection directly.

It includes both attempts for every semantic decision, all 24 evaluation episodes,
all 24 perturbations, three primary architectures, monolithic, and development
spend. Evaluation proceeds only if projected cost is below $4.00, leaving at least
$1.00 beneath the absolute $5.00 hard ceiling. Runtime accounting stops before any
call once the $5.00 ceiling has been reached. Cost uses the frozen listed rates of
$0.20/M uncached input, $0.02/M cached input, and $1.25/M output tokens; this is
accounted inference cost from provider-reported usage, not a provider invoice.

## Metrics and classifier

Fact precision/recall compare emitted keys with evaluator-only expected keys for
purchased artifacts. Relation quality measures exact unresolved symbol/relation
pairs. Hypothesis-effect quality measures direction agreement for supported
artifact/hypothesis pairs. Useful-action top-1/top-2, reciprocal rank, and normalized
routing regret use evaluator usefulness only after execution. Conditional routing
reports eligible decision-group branching, evaluator-consistent first routing, and
zero-value spurious branching. Architecture comparisons report exact paired wins,
losses, ties, accuracy, useful acquisition, regret, tokens, calls, latency, and cost.

Thresholds are frozen in code and the hash manifest. Semantic extraction requires
fact precision >= 0.65, fact recall >= 0.50, hypothesis-effect direction precision
>= 0.60, direction recall >= 0.50, and malformed response rate <= 0.05. Estimation
requires SER useful-action top-1 >= 0.60, top-2 >= 0.80, and mean normalized regret
<= 0.35. Conditional routing requires eligible-group branch rate >= 0.50,
evaluator-consistent first routing >= 0.60, and zero-value spurious branching <=
0.25. Perturbation joint stability must be >= 0.90 for every architecture.

`semantic_routing_supported` additionally requires a valid fixed comparison,
integrity checks, routing, and at least one material SER gain over ReAct-like:
accuracy >= 1/24, regret reduction >= 0.10, useful-acquisition gain >= 0.10, or cost
reduction >= 10%. Accuracy may not degrade by more than 1/24 and cost may not exceed
1.25x ReAct. Other frozen outcomes are
`semantic_estimation_supported_no_architecture_leverage`, `semantic_signal_only`,
`no_semantic_signal`, `routing_without_value`, `negative`, and `invalid`.

Any frozen-input mismatch, incomplete population/architecture, response-hash
failure, evidence leak, invalid run, or spend-cap failure makes the experiment
`invalid`. Provider responses are local frozen empirical observations; replay uses
stored outputs and does not claim the live model is byte-reproducible.
