# Static Semantic AuthzGym real-model v1 report

Validation: **fail**
Preregistered classification: **invalid**

This is a 24-episode frozen finite-population pilot. Results are descriptive, not a population-level superiority claim.

## Development and cost gate

- Development inference calls: 1
- Development input/output tokens: 1586/287
- Development accounted spend: $0.000675950
- Projected complete worst-policy spend before evaluation: $1.536676

## Frozen evaluation

| Architecture | Correct | Precision | Recall | Useful acquisition | Routing regret | Input tokens | Output tokens | Calls | Cost (USD) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `fixed_order_semantic` | 1/24 | 0.386 | 0.344 | 1.000 | 0.436 | 130489 | 21612 | 74 | 0.046154720 |
| `react_like_semantic` | 1/24 | 0.612 | 0.423 | 1.000 | 0.469 | 142433 | 23452 | 80 | 0.046650240 |
| `ser_explicit_value` | 1/24 | 0.642 | 0.493 | 1.000 | 0.764 | 143750 | 23232 | 82 | 0.048113200 |
| `monolithic_semantic` | 0/24 | 0.603 | 0.417 | 0.000 | 0.000 | 89081 | 13045 | 42 | 0.027809490 |

## SER action value and conditional routing

- Useful-action top-1: 0.179
- Useful-action top-2: 0.321
- Mean normalized routing regret: 0.764
- Eligible-group branch rate: 1.000
- Oracle-consistent first branch rate: 0.000
- Zero-value spurious branch rate: 0.250

## Paired architecture comparisons

- `ser_vs_react`: SER wins 1, react wins 1, ties 22, mean accuracy difference 0.000.
- `ser_vs_fixed`: SER wins 1, fixed wins 1, ties 22, mean accuracy difference 0.000.

## Perturbation stability

- `fixed_order_semantic`: joint 0.125, correctness 0.833, logical route 0.125, semantic fact set 0.167.
- `monolithic_semantic`: joint 0.292, correctness 1.000, logical route 0.292, semantic fact set 0.292.
- `react_like_semantic`: joint 0.083, correctness 0.917, logical route 0.125, semantic fact set 0.250.
- `ser_explicit_value`: joint 0.208, correctness 0.917, logical route 0.208, semantic fact set 0.375.

## Interpretation boundary

The provider outputs are frozen empirical observations. Deterministic reanalysis consumes those local outputs; replay does not claim the provider will emit identical text again.
