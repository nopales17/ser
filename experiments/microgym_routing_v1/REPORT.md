# MicroGym routing-v1 benchmark report

This report is generated from the frozen routing population and exact-model/run artifacts. It tests one-step observation-conditioned acquisition only; it does not test semantic reasoning or a real domain.

## Frozen primary condition

- Population hash: `0dc7d82cfcb8ffb1ce186ef90aa040378e62d920b4f9cf4b2af7bf4ba82f3aea`
- Regimes: **9**; episodes: **1152**.
- Runs: **3456** (3456 valid, 0 invalid).
- Horizon: one required equal-cost acquisition after a public reset cue; adaptive STOP is unavailable.
- Objective: terminal 0/1 decision loss. Raw `tests`, `synthetic_cost_units`, and `latency_steps` remain recorded separately.
- VOA convention: exact open-loop expected loss minus exact closed-loop expected loss; positive is value available only through conditioning.

## Decisive policies

- `exact_open_loop`: exact public-model acquisition committed before the cue; the cue and acquired result still inform its final answer.
- `adaptive_belief`: the unchanged Phase 3 Bayesian update and one-step acquisition score, invoked after the cue under runner-enforced fixed horizon.
- `exact_closed_loop_oracle`: evaluator-only exact cue-conditioned acquisition mapping.

All three receive the same prior, likelihoods, actions, costs, one-action budget, objective, identifiers, and presentation distribution. The candidate's only routing privilege over open-loop is using the released cue before selecting its acquisition.

## Exact VOA and Adaptivity Capture by regime

| Regime | Family | Band | Open loss | Candidate loss | Closed loss | VOA | Capture | Candidate mapping |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `ra-r0` | RA | high | 0.347500 | 0.145000 | 0.145000 | 0.202500 | 1.000000 | `v0->a0, v1->a1` |
| `ra-r1` | RA | high | 0.445000 | 0.265000 | 0.265000 | 0.180000 | 1.000000 | `v0->a0, v1->a1` |
| `rb-r0` | RB | zero | 0.220000 | 0.220000 | 0.220000 | 0.000000 | n/a | `v0->a1, v1->a1` |
| `rb-r1` | RB | zero | 0.180000 | 0.180000 | 0.180000 | 0.000000 | n/a | `v0->a0, v1->a0` |
| `rc-r0` | RC | zero | 0.550000 | 0.550000 | 0.550000 | 0.000000 | n/a | `v0->a1, v1->a1` |
| `rc-r1` | RC | low | 0.550000 | 0.532000 | 0.532000 | 0.018000 | 1.000000 | `v0->a0, v1->a1` |
| `rc-r2` | RC | moderate | 0.550000 | 0.460000 | 0.460000 | 0.090000 | 1.000000 | `v0->a0, v1->a1` |
| `rc-r3` | RC | high | 0.440000 | 0.280000 | 0.280000 | 0.160000 | 1.000000 | `v0->a0, v1->a1` |
| `rc-r4` | RC | high | 0.335000 | 0.145000 | 0.145000 | 0.190000 | 1.000000 | `v0->a0, v1->a1` |

## Results by VOA band

| VOA band | Regimes | Episodes | Mean VOA | Open expected loss | Candidate expected loss | Mean capture | Frozen-population candidate-open loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| zero | 3 | 384 | 0.000000 | 0.316667 | 0.316667 | n/a | 0.000000 |
| low | 1 | 128 | 0.018000 | 0.550000 | 0.532000 | 1.000000 | -0.101562 |
| moderate | 1 | 128 | 0.090000 | 0.550000 | 0.460000 | 1.000000 | -0.085938 |
| high | 4 | 512 | 0.183125 | 0.391875 | 0.208750 | 1.000000 | -0.199219 |

## Frozen-population outcomes and resources

| Policy | Correct | Decision loss | Tests | Cost units | Latency steps |
| --- | ---: | ---: | ---: | ---: | ---: |
| `exact_open_loop` | 0.598958 | 0.401042 | 1.000000 | 1.000000 | 1.000000 |
| `adaptive_belief` | 0.708333 | 0.291667 | 1.000000 | 1.000000 | 1.000000 |
| `exact_closed_loop_oracle` | 0.708333 | 0.291667 | 1.000000 | 1.000000 | 1.000000 |

On positive-VOA regimes, exact mean candidate advantage over open-loop was `0.140083` and VOA-weighted Adaptivity Capture was `1.000000`. On the frozen realized episodes, candidate-minus-open decision loss was `-0.164062` with 168 wins, 558 ties, and 42 losses.

## Behavioral branch audit

- Eligible conditional nodes: **6**.
- Candidate conditional branches: **6/6** (`1.000000`).
- Oracle-consistent branch mappings: **6/6** (`1.000000`).
- Beneficial branch mappings: **6/6** (`1.000000`).
- Zero-VOA spurious branches: **0/3** (`0.000000`).

The oracle artifacts separately record whether belief changed, action ranking changed, selected action changed, and exact value improved. A changed posterior alone is not counted as successful routing.

## Failure taxonomy

| Regime | Structural flags | Candidate better / tie / worse than open on realized episodes |
| --- | --- | ---: |
| `ra-r0` | none | 25 / 102 / 1 |
| `ra-r1` | none | 23 / 105 / 0 |
| `rb-r0` | belief_changed_without_action_ranking_change | 0 / 128 / 0 |
| `rb-r1` | belief_changed_without_action_ranking_change | 0 / 128 / 0 |
| `rc-r0` | none | 0 / 128 / 0 |
| `rc-r1` | none | 33 / 75 / 20 |
| `rc-r2` | none | 31 / 77 / 20 |
| `rc-r3` | none | 27 / 100 / 1 |
| `rc-r4` | none | 29 / 99 / 0 |

A candidate-worse episode is retained as a noise/wrong-reroute diagnostic even when the cue-conditioned mapping has lower exact expected loss. The benchmark does not tune these episodes away.

## Validation

- **population structure:** `pass` — 9 regimes, 1152 episodes, VOA bands ['high', 'high', 'zero', 'zero', 'zero', 'low', 'moderate', 'high', 'high']
- **oracle VOA bands:** `pass` — every declared zero/low/moderate/high band matches exact open-minus-closed loss
- **record hashes:** `pass` — verified 3465 content-addressed records
- **fixed horizon without STOP:** `pass` — all 3456 runs contain exactly one acquisition and no STOP
- **cost integrity:** `pass` — every policy receives and spends the same one-action raw resource vector
- **evaluator firewall and future-result blindness:** `pass` — public run projections contain no truth, environment seed, oracle hint, or future result
- **matched information and opportunity:** `pass` — open-loop and candidate share the public model, costs, budget, identifiers, and horizon
- **open-loop commitment invariance:** `pass` — the exact open-loop acquisition is unchanged across all realized cues
- **closed-loop release discipline:** `pass` — candidate action changes, when present, are reconstructed from the released cue only
- **action-order coverage:** `pass` — both presentation orders occur in every frozen regime
- **action-order permutation:** `pass` — value and branching signatures invariant in 9/9 regimes
- **identifier and action-label permutation:** `pass` — renamed action/outcome signatures invariant in 9/9 regimes
- **hidden-label permutation:** `pass` — permuted hidden-label signatures invariant in 9/9 regimes
- **seed isolation:** `pass` — policy seeds reproduce from public identity and are independent of restricted observation seeds
- **observation provenance:** `pass` — every cue and acquired observation carries release provenance
- **deterministic replay:** `pass` — exact replay reproduced 3456/3456 policy and oracle records

## Preregistered classification

Classification: **`routing_supported`**.

The classifier requires positive oracle VOA, verified conditional behavior, oracle-consistent routing, exact value over the matched open-loop plan, no STOP explanation, low zero-VOA spurious branching, and all invariance/leakage checks. Aggregate objective improvement alone cannot pass.

## Limitations

This is a deliberately favorable one-step explicit-likelihood setting. The candidate's one-step score is exactly suited to a one-action horizon; the result cannot establish multi-stage planning, action-value estimation without likelihood tables, semantics, software competence, IDS transfer, GitLab authorization value, learned routing, graph/coupling mechanisms, or substrate independence. The optional routing-by-STOP factorial was not run because the primary fixed-horizon experiment already isolates the intended question and Phase 3 separately measured stopping.
