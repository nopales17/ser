# Static Semantic AuthzGym v1 preregistration

Date frozen: 2026-08-17

## Scope and hypothesis

The benchmark is designed for the narrow future hypothesis:

> With the same inexpensive semantic model and evidence budget, an explicit
> routed architecture can use interpretations of purchased authorization-code
> artifacts to estimate which remaining inspection is decision-relevant better
> than matched fixed-order and ordinary tool-selection procedures.

This commit freezes the benchmark and runs deterministic mock calibration only.
Construction and mock behavior are not empirical support for that hypothesis.
No real model, GitLab source, IDS artifact, execution, mutation, request, test,
fuzzer, network, or deployment is authorized.

## Experimental decomposition

The trace separates:

```text
purchased raw code
  -> bounded semantic call
  -> parsed SemanticObservation
  -> explicit epistemic-state update
  -> optional action-value vector
  -> next inspection
  -> final hypothesis decision
  -> evaluator-only decomposition
```

Failures are assigned to semantic extraction, epistemic update, action-value
estimation, routing, final decision, or resource cost. Structured outputs are
recorded; no chain-of-thought is requested or stored.

## Population and holdout boundary

- Development: 8 episodes in two four-mechanism counterfactual groups.
- Primary evaluation: 24 episodes—16 in four eligible counterfactual groups and
  8 in four zero-value control pairs.
- Perturbation audit: 24 deterministic counterparts with renamed artifact,
  symbol, hidden, and candidate IDs plus reversed non-entry file order.
- Each episode has six small Python artifacts, 100–500 total lines, four frozen
  candidate hypotheses, one common required entry inspection, and a maximum of
  four inspected artifacts.

Development and evaluation manifests are separate. Evaluation episodes are not
used to tune prompts, parser rules, action-value weights, decision thresholds,
or classifier thresholds. A prompt, parser, policy, or threshold change after a
real-model evaluation requires a new benchmark/evaluation version.

The primary candidate hypotheses are:

1. ownership assumption discrepancy;
2. direct versus inherited membership discrepancy;
3. role propagation/transformation discrepancy;
4. token-scope or request-context discrepancy.

The correct hypothesis, mechanism ID, explanation, relevant files/functions,
evidence relationships, oracle usefulness, and correct conclusion are
evaluator-only.

## Authorization families and controls

Four families instantiate ownership/alternate-entry, inherited membership, role
propagation, and token/context propagation discrepancies. Within an eligible
group, layout, public inventory, symbol assignment, and presentation order are
held fixed while the purchased entry artifact changes which logical artifact is
most discriminating. The oracle-preferred second inspection differs across the
four family members.

Each zero-value pair holds the correct mechanism and oracle-best second artifact
fixed while a weak secondary semantic clue changes. A controller should not
change its selected logical artifact merely because that nondiagnostic evidence
changes its state.

Sources use opaque `unit_*.py` paths, opaque cross-file symbols, no mechanism
labels, no answer-bearing comments, and procedurally varied layout. Natural code
tokens such as owner, membership, role, token, and context are legitimate raw
semantic evidence, not evaluator annotations.

## Evidence actions and semantic interface

The only action is bounded static artifact inspection. A semantic call receives:

- exactly the selected artifact, or the monolithic baseline's explicitly bounded
  four-artifact batch;
- the four candidate hypotheses;
- current public epistemic summary;
- public artifact descriptors and exported symbols;
- the frozen prompt and model configuration.

It does not receive evaluator truth, hidden roles, unpurchased source, future
observations, oracle values, useful-action labels, environment seeds, or prior
solutions.

The structured result contains extracted facts, hypothesis support or
contradiction, unresolved symbol relationships, and uncertainty flags. The same
interface and prompt are used for every architecture and interpreter condition.

## Explicit action-value estimate

The SER-style policy maintains cumulative support for the supplied candidate
hypotheses. For every uninspected artifact it computes an inspectable score from:

1. unresolved symbol references extracted from already purchased artifacts;
2. the relation tag assigned to each reference by the semantic interpreter;
3. the candidate-hypothesis relation tags supplied equally to every architecture;
4. current nonnegative hypothesis support.

An unreferenced artifact receives only a small common prior. A referenced
artifact receives a base increment plus bounded support for hypotheses linked to
the extracted relation. Artifact contents, evaluator usefulness, mechanism ID,
and correct answer are not inputs. This is an experiment-specific heuristic, not
a universal information-value objective.

## Architecture baselines

Primary fixed-model comparisons are:

- `fixed_order_semantic`: required entry artifact, then frozen public order;
- `react_like_semantic`: required entry artifact, then the first unresolved tool
  reference in recent conversational state, with public-order fallback;
- `ser_explicit_value`: required entry artifact, then the maximum explicit
  policy-visible action-value estimate.

All three use exactly four single-artifact semantic calls and four inspections.
They share the model, prompt, candidate set, initial evidence, action inventory,
hard resource ceilings, final state updater, and final decision rule.

`monolithic_semantic` is secondary: one consolidated semantic call over the
first four public-order artifacts. It has the same artifact ceiling but not the
same call count, so it cannot by itself establish matched-call architectural
value.

## Resource ceilings and accounting

Primary architectures have hard ceilings of four artifact inspections, four
semantic calls, 6,000 deterministic input-token proxies, and 2,000 output-token
proxies. The secondary monolithic condition receives four artifacts in one call
under the same token ceilings. Every call records inspected artifacts, exact
visible input, output, parsed observation, lexical token proxies, declared/mock
latency, monetary cost, prompt hash, model/config hash, and action selected next.

Lexical proxies are not provider tokens. Deterministic mock latency is declared,
not observed provider wall-clock time. A real-model follow-up must record
provider-reported tokens when available, measured wall-clock latency, calls, and
monetary cost without silently equating those quantities.

## Mock calibration conditions

This benchmark-construction commit runs:

- `deterministic_structured_v1`, a narrow rule-based interface test double;
- `deterministic_degraded_v1`, the same interface with deterministic omissions.

They test manifests, parsing, state updates, ranking, routing, metrics, failures,
and replay. They are not cheap or strong language models and their results cannot
satisfy the real-model classifier.

## Evaluator metrics

Evaluator-only truth supports:

- micro fact precision and recall;
- first post-entry useful-action top-1 and top-2 recall;
- normalized routing regret;
- eligible-group conditional branch rate;
- oracle-consistent first-branch rate;
- zero-value spurious branch rate;
- final hypothesis accuracy and decision loss;
- per-layer failure counts;
- raw calls, inspections, token proxies, latency, and monetary cost.

## Frozen real-model classifier

The first real inexpensive-model follow-up may classify
`semantic_routing_supported` only if all validation checks pass and all of:

1. SER semantic fact precision is at least 0.65 and recall at least 0.50;
2. SER useful-action top-1 recall is at least 0.60 and top-2 recall at least 0.80;
3. SER mean normalized routing regret is at most 0.35;
4. SER branches in at least 50% of eligible counterfactual groups;
5. at least 60% of eligible first routes are oracle-consistent;
6. zero-value spurious branching is at most 25%;
7. SER accuracy exceeds fixed order by at least 2/24 (`0.083333`) and ReAct-like
   selection by at least 1/24 (`0.041667`);
8. SER's mean input-plus-output token use is no more than 1.10 times the better
   primary control;
9. model/prompt access, four-call/four-artifact ceilings, firewall, replay, and
   identifier/order perturbation checks pass.

Otherwise:

- `invalid`: any required integrity, access, budget, replay, or perturbation
  condition fails;
- `no_semantic_signal`: semantic precision or recall fails;
- `semantic_estimation_only`: semantic and action-ranking thresholds pass but
  matched decision value does not;
- `routing_without_value`: branch requirements pass but matched decision value
  does not;
- `negative`: SER accuracy is below both primary controls after integrity and
  semantic thresholds pass;
- `null`: remaining valid pattern without required estimation/routing/value.

Mock calibration is always labeled `benchmark_calibration_only`; diagnostic
"would-be" metrics or preview labels do not admit a finding.

## Interpretation boundary and readiness

A positive real-model result would support only bounded static semantic
inspection routing under the named model, prompt, corpus, and budgets. It would
not establish open-ended hypothesis generation, dynamic execution, fuzzing,
GitLab competence, IDS transfer, learned routing, graph/coupling machinery,
general SER advantage, or deployment economics.

Phase 5B is justified only after an actual inexpensive model extracts useful
facts, estimates action values beyond trivial heuristics, routes conditionally,
and improves decision quality or efficiency under matched budgets. Real GitLab
remains gated until Phase 5B establishes useful active evidence generation and
repeated evaluation is economically plausible or expected value dominates
model/tool cost.
