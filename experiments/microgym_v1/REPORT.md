# MicroGym v1 benchmark report

This report is generated from the frozen population and run artifacts. It evaluates a synthetic, explicit-likelihood control problem; it does not test semantic reasoning or real-domain generalization.

## Frozen experiment definition

- Population hash: `a9234fa60b40d3628f6317284a964c95917bcd7442796d8961f18b14b9958b3d`
- Problem regimes: **24** across **6** families.
- Episodes: **728**; the population was frozen before aggregation.
- Normal policy runs: **7280** (7280 valid, 0 invalid).
- Raw resources: `tests` (count), `synthetic_cost_units` (unit), and `latency_steps` (step).
- MicroGym-only objective: decision loss + the regime's preregistered cost weight × synthetic cost units.
- Sufficient evidence: the exact evaluator oracle selects STOP at the current public belief/budget state; hidden-state hindsight is not used.
- Randomness domains: population generation `31415926`, environment realization master `27182818`, and policy randomness master `16180339`. Normal policies never receive the environment seed.

## Policy definitions

- `ablation_cost_blind`: uses only the declared public prior, likelihoods, costs, and released observations; uses Bayes-optimal answer-or-abstain submission under declared decision loss; uses adaptive expected Bayes-risk reduction but ignores resource cost
- `ablation_information_blind`: uses only the declared public prior, likelihoods, costs, and released observations; uses Bayes-optimal answer-or-abstain submission under declared decision loss; selects minimum immediate primary-resource cost with opaque-ID tie-breaking; fixed stop after three acquisitions or when none remain legal; registered as the cost-only adaptive-policy ablation
- `ablation_no_adaptation`: uses only the declared public prior, likelihoods, costs, and released observations; uses Bayes-optimal answer-or-abstain submission under declared decision loss; receives the same public generative model, objective, costs, and budget as the adaptive candidate; commits an open-loop acquisition plan from the prior before inspecting the episode's initial observation; neither action ranking nor stopping length can change in response to realized observations; released observations still inform the final answer so only acquisition control is ablated
- `ablation_no_adaptive_stop`: uses only the declared public prior, likelihoods, costs, and released observations; uses Bayes-optimal answer-or-abstain submission under declared decision loss; uses observation-conditioned adaptive routing; cannot compare acquisition against STOP and instead stops after three acquisitions or exhaustion
- `adaptive_belief`: uses only the declared public prior, likelihoods, costs, and released observations; uses Bayes-optimal answer-or-abstain submission under declared decision loss; maintains a posterior with the declared public observation model; chooses the legal action with greatest one-step Bayes-risk reduction minus experiment-specific primary cost; chooses STOP when no acquisition has positive myopic net value; is a candidate experimental policy, not a canonical SER objective
- `cheap_first`: uses only the declared public prior, likelihoods, costs, and released observations; uses Bayes-optimal answer-or-abstain submission under declared decision loss; selects minimum immediate primary-resource cost with opaque-ID tie-breaking; fixed stop after three acquisitions or when none remain legal
- `exhaustive`: uses only the declared public prior, likelihoods, costs, and released observations; uses Bayes-optimal answer-or-abstain submission under declared decision loss; precommits to presentation order and acquires every action affordable under that order; repeated tests are exhausted only after every test has been attempted once
- `fixed_order`: uses only the declared public prior, likelihoods, costs, and released observations; uses Bayes-optimal answer-or-abstain submission under declared decision loss; follows the episode's frozen presentation order independently of observations; fixed stop after three acquisitions or when none remain legal
- `greedy`: uses only the declared public prior, likelihoods, costs, and released observations; uses Bayes-optimal answer-or-abstain submission under declared decision loss; uses a fixed public pairwise-separation-per-cost score; does not recompute utility from observations; fixed stop after three acquisitions or when none remain legal
- `random`: uses only the declared public prior, likelihoods, costs, and released observations; uses Bayes-optimal answer-or-abstain submission under declared decision loss; uniform seeded choice among legal acquisition actions; fixed stop after three acquisitions or when none remain legal

## Overall results

| Policy | Correct | Abstain | Decision loss | Cost units | Tests | Combined objective | Combined regret | Actions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `ablation_cost_blind` | 0.7349 | 0.2143 | 0.1258 | 2.3544 | 0.7912 | 0.3649 | 0.0651 | 0.7912 |
| `ablation_information_blind` | 0.5330 | 0.3846 | 0.2170 | 2.5874 | 1.9258 | 0.4720 | 0.1721 | 1.9258 |
| `ablation_no_adaptation` | 0.4560 | 0.5082 | 0.2136 | 1.2074 | 0.5673 | 0.3114 | 0.0116 | 0.5673 |
| `ablation_no_adaptive_stop` | 0.6786 | 0.2569 | 0.1545 | 2.9093 | 1.8022 | 0.4339 | 0.1341 | 1.8022 |
| `adaptive_belief` | 0.4382 | 0.5082 | 0.2315 | 0.9066 | 0.4121 | 0.3032 | 0.0033 | 0.4121 |
| `cheap_first` | 0.5330 | 0.3846 | 0.2170 | 2.5874 | 1.9258 | 0.4720 | 0.1721 | 1.9258 |
| `exhaustive` | 0.6126 | 0.3255 | 0.1758 | 3.0665 | 1.8214 | 0.4810 | 0.1812 | 1.8214 |
| `fixed_order` | 0.6154 | 0.3214 | 0.1757 | 3.0500 | 1.8049 | 0.4793 | 0.1794 | 1.8049 |
| `greedy` | 0.5632 | 0.3599 | 0.2029 | 2.7110 | 1.9258 | 0.4652 | 0.1654 | 1.9258 |
| `random` | 0.6538 | 0.2802 | 0.1640 | 3.1360 | 1.8393 | 0.4770 | 0.1772 | 1.8393 |

### Raw resource distributions

Cells show mean [p10, p50, p90]; all dimensions remain separate.

| Policy | Tests | Synthetic cost units | Latency steps |
| --- | ---: | ---: | ---: |
| `ablation_cost_blind` | 0.7912 [0.0000, 1.0000, 1.0000] | 2.3544 [0.0000, 3.0000, 3.0000] | 2.3544 [0.0000, 3.0000, 3.0000] |
| `ablation_information_blind` | 1.9258 [1.0000, 2.0000, 3.0000] | 2.5874 [1.5000, 2.5000, 4.0000] | 2.5874 [1.5000, 2.5000, 4.0000] |
| `ablation_no_adaptation` | 0.5673 [0.0000, 0.0000, 2.0000] | 1.2074 [0.0000, 0.0000, 4.0000] | 1.2074 [0.0000, 0.0000, 4.0000] |
| `ablation_no_adaptive_stop` | 1.8022 [1.0000, 2.0000, 3.0000] | 2.9093 [1.5000, 2.5000, 4.0000] | 2.9093 [1.5000, 2.5000, 4.0000] |
| `adaptive_belief` | 0.4121 [0.0000, 0.0000, 1.0000] | 0.9066 [0.0000, 0.0000, 3.0000] | 0.9066 [0.0000, 0.0000, 3.0000] |
| `cheap_first` | 1.9258 [1.0000, 2.0000, 3.0000] | 2.5874 [1.5000, 2.5000, 4.0000] | 2.5874 [1.5000, 2.5000, 4.0000] |
| `exhaustive` | 1.8214 [1.0000, 2.0000, 2.0000] | 3.0665 [2.0000, 3.0000, 4.0000] | 3.0665 [2.0000, 3.0000, 4.0000] |
| `fixed_order` | 1.8049 [1.0000, 2.0000, 2.0000] | 3.0500 [2.0000, 3.0000, 4.0000] | 3.0500 [2.0000, 3.0000, 4.0000] |
| `greedy` | 1.9258 [1.0000, 2.0000, 3.0000] | 2.7110 [1.5000, 2.5000, 4.0000] | 2.7110 [1.5000, 2.5000, 4.0000] |
| `random` | 1.8393 [1.0000, 2.0000, 3.0000] | 3.1360 [2.0000, 3.0000, 4.0000] | 3.1360 [2.0000, 3.0000, 4.0000] |

## Results by family

### Family A

| Policy | Correct | Decision loss | Cost | Objective | Regret |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ablation_cost_blind` | 0.2417 | 0.2708 | 1.2500 | 0.3458 | 0.0000 |
| `ablation_information_blind` | 0.3333 | 0.3146 | 3.0000 | 0.5696 | 0.2238 |
| `ablation_no_adaptation` | 0.2417 | 0.2708 | 1.2500 | 0.3458 | 0.0000 |
| `ablation_no_adaptive_stop` | 0.5250 | 0.2312 | 3.7500 | 0.5312 | 0.1854 |
| `adaptive_belief` | 0.2417 | 0.2708 | 1.2500 | 0.3458 | 0.0000 |
| `cheap_first` | 0.3333 | 0.3146 | 3.0000 | 0.5696 | 0.2238 |
| `exhaustive` | 0.4250 | 0.2662 | 3.3000 | 0.5393 | 0.1934 |
| `fixed_order` | 0.4250 | 0.2662 | 3.3000 | 0.5393 | 0.1934 |
| `greedy` | 0.5250 | 0.2312 | 3.7500 | 0.5312 | 0.1854 |
| `random` | 0.4750 | 0.2487 | 3.5750 | 0.5383 | 0.1924 |

### Family B

| Policy | Correct | Decision loss | Cost | Objective | Regret |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ablation_cost_blind` | 0.9667 | 0.0333 | 2.9500 | 0.3248 | 0.0582 |
| `ablation_information_blind` | 0.5333 | 0.2012 | 2.2000 | 0.4213 | 0.1546 |
| `ablation_no_adaptation` | 0.7333 | 0.1042 | 1.7500 | 0.2667 | 0.0000 |
| `ablation_no_adaptive_stop` | 0.8667 | 0.0575 | 2.6000 | 0.3110 | 0.0443 |
| `adaptive_belief` | 0.7333 | 0.1042 | 1.7500 | 0.2667 | 0.0000 |
| `cheap_first` | 0.5333 | 0.2012 | 2.2000 | 0.4213 | 0.1546 |
| `exhaustive` | 0.7083 | 0.1183 | 2.8500 | 0.4061 | 0.1395 |
| `fixed_order` | 0.7083 | 0.1183 | 2.8500 | 0.4061 | 0.1395 |
| `greedy` | 0.5333 | 0.2012 | 2.2000 | 0.4213 | 0.1546 |
| `random` | 0.7250 | 0.1450 | 2.9158 | 0.4404 | 0.1738 |

### Family C

| Policy | Correct | Decision loss | Cost | Objective | Regret |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ablation_cost_blind` | 0.9500 | 0.0392 | 3.0167 | 0.4167 | 0.2742 |
| `ablation_information_blind` | 0.8833 | 0.0571 | 3.2500 | 0.4071 | 0.2646 |
| `ablation_no_adaptation` | 0.9500 | 0.0500 | 2.0000 | 0.2000 | 0.0575 |
| `ablation_no_adaptive_stop` | 0.8833 | 0.0571 | 3.2500 | 0.4071 | 0.2646 |
| `adaptive_belief` | 0.8750 | 0.1250 | 0.7500 | 0.1625 | 0.0200 |
| `cheap_first` | 0.8833 | 0.0571 | 3.2500 | 0.4071 | 0.2646 |
| `exhaustive` | 0.9167 | 0.0454 | 3.4667 | 0.4388 | 0.2963 |
| `fixed_order` | 0.9167 | 0.0454 | 3.4667 | 0.4388 | 0.2963 |
| `greedy` | 0.8833 | 0.0571 | 3.2500 | 0.4071 | 0.2646 |
| `random` | 0.9417 | 0.0421 | 3.6167 | 0.4654 | 0.3229 |

### Family D

| Policy | Correct | Decision loss | Cost | Objective | Regret |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ablation_cost_blind` | 0.8917 | 0.1083 | 3.0000 | 0.4083 | 0.0525 |
| `ablation_information_blind` | 0.7083 | 0.2213 | 3.0000 | 0.5212 | 0.1654 |
| `ablation_no_adaptation` | 0.2167 | 0.2958 | 0.7500 | 0.3558 | 0.0000 |
| `ablation_no_adaptive_stop` | 0.8500 | 0.1175 | 3.7500 | 0.4825 | 0.1267 |
| `adaptive_belief` | 0.2167 | 0.2958 | 0.7500 | 0.3558 | 0.0000 |
| `cheap_first` | 0.7083 | 0.2213 | 3.0000 | 0.5212 | 0.1654 |
| `exhaustive` | 0.7917 | 0.1704 | 4.0042 | 0.5703 | 0.2144 |
| `fixed_order` | 0.8083 | 0.1700 | 3.9042 | 0.5595 | 0.2037 |
| `greedy` | 0.7083 | 0.2213 | 3.0000 | 0.5212 | 0.1654 |
| `random` | 0.8417 | 0.1258 | 3.8225 | 0.5069 | 0.1511 |

### Family E

| Policy | Correct | Decision loss | Cost | Objective | Regret |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ablation_cost_blind` | 0.3984 | 0.2766 | 1.0000 | 0.3766 | 0.0266 |
| `ablation_information_blind` | 0.1953 | 0.3223 | 1.8250 | 0.5023 | 0.1523 |
| `ablation_no_adaptation` | 0.0000 | 0.3500 | 0.0000 | 0.3500 | 0.0000 |
| `ablation_no_adaptive_stop` | 0.3984 | 0.2766 | 1.8750 | 0.4616 | 0.1116 |
| `adaptive_belief` | 0.0000 | 0.3500 | 0.0000 | 0.3500 | 0.0000 |
| `cheap_first` | 0.1953 | 0.3223 | 1.8250 | 0.5023 | 0.1523 |
| `exhaustive` | 0.1953 | 0.3070 | 1.9875 | 0.5055 | 0.1555 |
| `fixed_order` | 0.1953 | 0.3070 | 1.9875 | 0.5055 | 0.1555 |
| `greedy` | 0.1875 | 0.3199 | 1.8250 | 0.4999 | 0.1499 |
| `random` | 0.2500 | 0.2980 | 2.0109 | 0.4996 | 0.1496 |

### Family F

| Policy | Correct | Decision loss | Cost | Objective | Regret |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ablation_cost_blind` | 0.9833 | 0.0167 | 3.0000 | 0.3167 | -0.0183 |
| `ablation_information_blind` | 0.5667 | 0.1787 | 2.3000 | 0.4083 | 0.0732 |
| `ablation_no_adaptation` | 0.6250 | 0.2017 | 1.5750 | 0.3477 | 0.0127 |
| `ablation_no_adaptive_stop` | 0.5667 | 0.1787 | 2.3000 | 0.4083 | 0.0732 |
| `adaptive_belief` | 0.5917 | 0.2350 | 1.0000 | 0.3350 | 0.0000 |
| `cheap_first` | 0.5667 | 0.1787 | 2.3000 | 0.4083 | 0.0732 |
| `exhaustive` | 0.6667 | 0.1383 | 2.8625 | 0.4248 | 0.0898 |
| `fixed_order` | 0.6667 | 0.1383 | 2.8625 | 0.4248 | 0.0898 |
| `greedy` | 0.5667 | 0.1787 | 2.3000 | 0.4083 | 0.0732 |
| `random` | 0.7167 | 0.1154 | 2.9500 | 0.4102 | 0.0752 |

## Paired adaptive comparisons

Negative adaptive-minus-control objective/cost differences favor the adaptive candidate. Intervals are deterministic paired bootstrap descriptions of this frozen population, not p-values.

| Control | Objective Δ | 95% descriptive interval | Wins / ties / losses | Decision-loss Δ | Cost Δ |
| --- | ---: | --- | ---: | ---: | ---: |
| `fixed_order` | -0.1761 | [-0.1982, -0.1531] | 564 / 29 / 135 | 0.0558 | -2.1434 |
| `random` | -0.1739 | [-0.1964, -0.1515] | 554 / 25 / 149 | 0.0674 | -2.2294 |
| `cheap_first` | -0.1688 | [-0.1912, -0.1463] | 522 / 35 / 171 | 0.0144 | -1.6808 |
| `exhaustive` | -0.1779 | [-0.1995, -0.1544] | 564 / 29 / 135 | 0.0557 | -2.1599 |
| `greedy` | -0.1621 | [-0.1861, -0.1386] | 529 / 35 / 164 | 0.0286 | -1.8044 |
| `ablation_no_adaptation` | -0.0083 | [-0.0166, -0.0002] | 70 / 645 / 13 | 0.0179 | -0.3008 |
| `ablation_cost_blind` | -0.0618 | [-0.0837, -0.0409] | 227 / 304 / 197 | 0.1056 | -1.4478 |
| `ablation_information_blind` | -0.1688 | [-0.1919, -0.1454] | 522 / 35 / 171 | 0.0144 | -1.6808 |
| `ablation_no_adaptive_stop` | -0.1308 | [-0.1514, -0.1108] | 502 / 76 / 150 | 0.0770 | -2.0027 |

The `ablation_no_adaptation` comparison is the causal model-access control: it receives the same public generative model, costs, budget, and scoring objective, but commits its acquisition sequence and stopping length from the prior before inspecting the episode's initial observation.

## Stopping and adaptivity

| Policy | Premature stop rate | Stopping regret | Unnecessary actions | Avoidable cost | Conditional routing rate |
| --- | ---: | ---: | ---: | ---: | ---: |
| `ablation_cost_blind` | 0.0000 | 0.0000 | 0.3379 | 0.9203 | 0.0690 |
| `ablation_information_blind` | 0.0000 | 0.0000 | 1.3049 | 1.8456 | 0.0000 |
| `ablation_no_adaptation` | 0.0000 | 0.0000 | 0.0934 | 0.1978 | 0.0000 |
| `ablation_no_adaptive_stop` | 0.0000 | 0.0000 | 1.3063 | 1.8777 | 0.0370 |
| `adaptive_belief` | 0.0412 | 0.0002 | 0.0000 | 0.0000 | 0.0000 |
| `cheap_first` | 0.0000 | 0.0000 | 1.3049 | 1.8456 | 0.0000 |
| `exhaustive` | 0.0000 | 0.0000 | 1.2266 | 1.9158 | 0.0763 |
| `fixed_order` | 0.0000 | 0.0000 | 1.2102 | 1.8993 | 0.0763 |
| `greedy` | 0.0000 | 0.0000 | 1.3049 | 1.8456 | 0.0000 |
| `random` | 0.0000 | 0.0000 | 1.2500 | 1.9718 | 0.0541 |

## Leakage, replay, and invariance checks

- **action-order coverage:** `pass` — all 24 regimes contain multiple frozen action presentation orders
- **action-order permutation:** `pass` — adaptive outcome/resource signatures invariant in 6/6 family representatives after reversing presentation order
- **cost integrity:** `pass` — trace costs, componentwise budgets, and evaluator totals agree across 7280 runs
- **deterministic replay:** `pass` — exact public replay passed for 8008/8008 oracle and policy traces
- **evaluator firewall:** `pass` — public projections omit truth/realization fields; a hidden-state probe fails; evaluator policies and invalid truth tokens are rejected
- **failed-run preservation:** `pass` — artifacts retain 265 failed actions and 144 environment terminations; validity remains explicit
- **future-result blindness:** `pass` — normal policies receive separate policy-only randomness plus distributions, never the environment seed, RNG slot, or sampled future result
- **hidden-state permutation:** `pass` — adaptive outcome/resource signatures invariant in 6/6 family representatives after permuting hypothesis rows and labels
- **identifier scrambling:** `pass` — adaptive outcome/resource signatures invariant in 6/6 family representatives after renaming hypotheses, actions, and outcomes
- **matched public model access:** `pass` — all normal policies received the same public prior, declared likelihoods, costs, legal actions, released history, and budget projection
- **observation release:** `pass` — all released observations carry step and result provenance across 7280 runs
- **opaque identifiers:** `pass` — action IDs are opaque and contain no hypothesis-target labels
- **population scale:** `pass` — 24 regimes, 728 episodes, family counts {'A': 120, 'B': 120, 'C': 120, 'D': 120, 'E': 128, 'F': 120}
- **record hashes:** `pass` — verified 8008/8008 content-addressed records
- **seed isolation:** `pass` — population, hidden environment realization, and policy randomness use named domains; evaluator seeds are restricted, policy seeds are public, and perturbing the environment seed leaves random-policy routing unchanged

## Failure analysis

- **Family A:** failed_action_loss=0, loses_to_best_simple=27, loses_to_cheap_first=27, loses_to_fixed_order=26, matches_simple_trajectory=0, misled_on_noisy_episode=35, spends_after_sufficiency=0, spends_more=6, stops_incorrectly=0
  - `mgv1-a-r3-e003` lost to `fixed_order` by 1.1200: higher_combined_objective, wrong_when_simple_correct, spends_more.
  - `mgv1-a-r3-e002` lost to `fixed_order` by 0.1200: higher_combined_objective, spends_more.
  - `mgv1-a-r3-e007` lost to `fixed_order` by 0.1200: higher_combined_objective, spends_more.
- **Family B:** failed_action_loss=0, loses_to_best_simple=38, loses_to_cheap_first=36, loses_to_fixed_order=19, matches_simple_trajectory=38, misled_on_noisy_episode=30, spends_after_sufficiency=0, spends_more=36, stops_incorrectly=0
  - `mgv1-b-r2-e016` lost to `fixed_order` by 0.6640: higher_combined_objective, wrong_when_simple_correct.
  - `mgv1-b-r2-e020` lost to `fixed_order` by 0.6400: higher_combined_objective, wrong_when_simple_correct.
  - `mgv1-b-r1-e002` lost to `fixed_order` by 0.1300: higher_combined_objective, wrong_when_simple_correct.
- **Family C:** failed_action_loss=0, loses_to_best_simple=12, loses_to_cheap_first=12, loses_to_fixed_order=12, matches_simple_trajectory=0, misled_on_noisy_episode=12, spends_after_sufficiency=0, spends_more=0, stops_incorrectly=30
  - `mgv1-c-r1-e006` lost to `fixed_order` by 0.6000: higher_combined_objective, wrong_when_simple_correct, premature_stop.
  - `mgv1-c-r1-e011` lost to `fixed_order` by 0.6000: higher_combined_objective, wrong_when_simple_correct, premature_stop.
  - `mgv1-c-r1-e012` lost to `fixed_order` by 0.6000: higher_combined_objective, wrong_when_simple_correct, premature_stop.
- **Family D:** failed_action_loss=0, loses_to_best_simple=52, loses_to_cheap_first=43, loses_to_fixed_order=24, matches_simple_trajectory=0, misled_on_noisy_episode=90, spends_after_sufficiency=0, spends_more=0, stops_incorrectly=0
  - `mgv1-d-r2-e008` lost to `cheap_first` by 1.0000: higher_combined_objective, wrong_when_simple_correct.
  - `mgv1-d-r2-e029` lost to `cheap_first` by 1.0000: higher_combined_objective, wrong_when_simple_correct.
  - `mgv1-d-r2-e017` lost to `cheap_first` by 0.6500: higher_combined_objective.
- **Family E:** failed_action_loss=0, loses_to_best_simple=49, loses_to_cheap_first=25, loses_to_fixed_order=25, matches_simple_trajectory=0, misled_on_noisy_episode=49, spends_after_sufficiency=0, spends_more=0, stops_incorrectly=0
  - `mgv1-e-r1-e000` lost to `random` by 0.1700: higher_combined_objective, wrong_when_simple_correct.
  - `mgv1-e-r1-e002` lost to `fixed_order` by 0.1700: higher_combined_objective, wrong_when_simple_correct.
  - `mgv1-e-r1-e003` lost to `fixed_order` by 0.1700: higher_combined_objective, wrong_when_simple_correct.
- **Family F:** failed_action_loss=15, loses_to_best_simple=32, loses_to_cheap_first=28, loses_to_fixed_order=29, matches_simple_trajectory=16, misled_on_noisy_episode=27, spends_after_sufficiency=0, spends_more=0, stops_incorrectly=0
  - `mgv1-f-r0-e014` lost to `fixed_order` by 0.8000: higher_combined_objective, wrong_when_simple_correct.
  - `mgv1-f-r0-e021` lost to `fixed_order` by 0.8000: higher_combined_objective, wrong_when_simple_correct.
  - `mgv1-f-r1-e014` lost to `random` by 0.8000: higher_combined_objective, wrong_when_simple_correct.

## Evidence classification and limitations

Classification: **`strong_enough_to_continue`**.

The candidate is myopic and knows the declared likelihood model. MicroGym labels and observations are opaque but mathematically clean. The result cannot establish semantic reasoning, real-domain transfer, Scope-aware gating, graph value, coupling laws, learned routing, LLM value, IDS performance, or software-investigation performance. Failed actions and adaptive losses remain in the run artifacts.
