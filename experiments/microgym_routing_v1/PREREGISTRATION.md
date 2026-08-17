# MicroGym routing-v1 preregistration

Date frozen: 2026-08-17

## Narrow hypothesis

> In environments with positive exact value of closed-loop adaptation, a
> model-aware closed-loop policy can condition its single later acquisition on
> a legitimately released cue and recover decision value unavailable to the
> best matched model-aware acquisition plan committed before that cue.

This is a synthetic fixed-horizon control hypothesis. It is not a claim that
SER, semantic reasoning, learned routing, IDS transfer, GitLab investigation,
or general resource allocation works.

## Primary causal comparison

Every episode supplies the same public prior, likelihood model, action
descriptors, equal action costs, one-action budget, terminal decision loss, and
opaque identifiers.

- `exact_open_loop` computes the exact best acquisition from the public model
  before the reset cue is observed. It cannot change that committed action in
  response to the cue. The cue and acquired result still inform its final
  answer.
- `adaptive_belief` uses the unchanged Phase 3 `AdaptiveBeliefPolicy` posterior
  update and one-step action scoring. The routing runner calls its existing
  acquisition-selection method after releasing the cue.
- `exact_closed_loop_oracle` computes the exact best acquisition separately for
  every possible released cue. It is evaluator-only and is never an input to
  the candidate.

The primary runner requires exactly one acquisition after the reset cue. STOP
is not presented, all policies receive one equivalent acquisition opportunity,
and the runner ends the episode immediately afterward. No routing-by-STOP or
resource-thrift explanation is possible in this condition.

## Frozen regimes

The population contains nine regimes and 1,152 episodes: 128 per regime with
balanced hidden states and counterbalanced action presentation order.

| Family | Regime | Cue reliability | Acquisition structure | Declared VOA band |
| --- | --- | ---: | --- | --- |
| RA | 0 | 0.90 | complementary specialists, accuracy 0.95 | high |
| RA | 1 | 0.75 | complementary specialists, accuracy 0.98 | high |
| RB | 0 | 0.90 | two identical general tests, accuracy 0.78 | zero |
| RB | 1 | 0.85 | dominant general test 0.82 versus 0.68 | zero |
| RC | 0 | 0.50 | complementary specialists, accuracy 0.90 | zero |
| RC | 1 | 0.52 | complementary specialists, accuracy 0.90 | low |
| RC | 2 | 0.60 | complementary specialists, accuracy 0.90 | moderate |
| RC | 3 | 0.80 | complementary specialists, accuracy 0.90 | high |
| RC | 4 | 0.95 | complementary specialists, accuracy 0.90 | high |

RA is the diagnostic-branch family. RB is the zero-value adaptation control:
the cue changes belief but should not change the best next action. RC grades the
available value of conditioning by changing cue reliability. These parameters
are frozen from the structural design and exact open/closed-loop calculation,
not selected from candidate aggregate performance.

## Objective, oracle values, and VOA

The primary objective is expected terminal 0/1 decision loss after the required
acquisition. All acquisitions cost exactly one `tests` count, one
`synthetic_cost_units`, and one `latency_steps`; raw dimensions remain recorded
but do not enter the primary objective because they are fixed and equal.

For every regime, exact public-model enumeration computes:

- `L_open`: minimum expected terminal loss over acquisition actions committed
  before the cue;
- `L_closed`: expected minimum terminal loss when the acquisition may depend on
  the released cue;
- `VOA = L_open - L_closed`.

Positive VOA therefore means lower loss is available only through conditional
routing. Bands are frozen as: zero `<= 1e-12`, low `(0, 0.05)`, moderate
`[0.05, 0.15)`, and high `>= 0.15`.

For positive-VOA regimes:

`AdaptivityCapture = (L_open - L_candidate) / (L_open - L_closed)`.

Zero captures none of the exact opportunity, one matches the closed-loop
oracle, a negative value is worse than open-loop, and a value above one requires
an oracle or analysis audit.

## Behavioral audit

The primary analysis distinguishes:

1. whether the cue changed the posterior;
2. whether candidate action ranking changed;
3. whether candidate action choice changed across possible cues;
4. whether that change lowered exact expected loss.

An eligible conditional node is a regime in which VOA is positive and different
possible cue values have different exact closed-loop optimal acquisitions. The
report records candidate branch rate, oracle-consistent branch rate, beneficial
branch rate, and spurious branch rate in zero-VOA controls. Candidate-side
beliefs, action scores, rankings, and selected actions are recorded from public
information only.

## Frozen classifier

`routing_supported` requires all of:

1. at least four positive-VOA regimes across at least two families and at least
   two zero-VOA controls;
2. candidate branching on at least 80% of eligible conditional nodes;
3. oracle-consistent candidate mappings on at least 90% of eligible nodes;
4. lower exact candidate loss than exact open-loop on every positive-VOA regime
   and mean positive-regime advantage greater than 0.005;
5. VOA-weighted Adaptivity Capture of at least 0.75;
6. exactly one acquisition and no STOP in every primary run;
7. spurious branching in no more than 5% of zero-VOA regimes;
8. all replay, cost, access-matching, seed, firewall, label/order, and future-
   result blindness checks pass.

Otherwise the mechanical result is:

- `invalid` if required regime structure or validation fails;
- `negative` if the candidate is worse than open-loop on positive-VOA regimes;
- `behavior_without_value` if it branches but does not clear the value rule;
- `value_without_verified_routing` if value improves but branching or oracle
  consistency misses its rule;
- `null` if it neither branches nor improves;
- `negative` for any remaining failed pattern.

The classifier, population, families, thresholds, and candidate implementation
will not be altered after the final population is frozen. A changed policy or
strategy requires a new benchmark identity, preregistration, and manifest. The
first frozen candidate result is preserved whether favorable or unfavorable.

## Randomness, traces, and interpretation

Population layout, evaluator-only observation/noise realization, and policy
randomness use separately named seed domains. A normal policy never receives an
environment seed or future sampled result. Every run records the cue, selected
action, acquired result, public action-value landscape, fixed termination,
raw costs, restricted truth/outcome, and content hash. Exact replay must recover
all public and restricted run records.

The frozen finite-population paired differences and exact model expectations are
primary. Any interval is descriptive only; no sampling-based significance claim
will be made. Identifier, action-label, hidden-label, and action-order
permutations must preserve value and branching conclusions.
