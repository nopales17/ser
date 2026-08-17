# Static Semantic AuthzGym v1 construction and mock-calibration report

This report validates a frozen benchmark and decomposition pipeline. It contains no real model call and is not empirical support for semantic routing or SER.

## Frozen scope

- Evaluation population hash: `cd8339fd3a0973da7135ca252244ce3b71e1ffc33674b5b8d03cad1fde46a2bb`.
- Primary evaluation: **24** episodes; mock runs: **192**.
- Each episode is a static six-file repository with four candidate hypotheses and a four-inspection ceiling.
- Primary matched architectures: fixed order, ReAct-like tool selection, and explicit SER-style action values, each with four calls and four artifacts.
- Secondary monolithic baseline: one consolidated call over four public-order artifacts.

## Mock-calibration metrics

| Interpreter | Architecture | Accuracy | Fact precision | Fact recall | First-route correct | Top-1 useful recall | Mean routing regret | Calls | Input-token proxy |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `deterministic_degraded_v1_1` | `fixed_order_semantic` | 0.791667 | 0.611111 | 0.496774 | 0.208333 | 0.000000 | 0.658333 | 4.000000 | 4353.458333 |
| `deterministic_degraded_v1_1` | `react_like_semantic` | 1.000000 | 0.563636 | 0.387500 | 0.000000 | 0.000000 | 0.466667 | 4.000000 | 4353.000000 |
| `deterministic_degraded_v1_1` | `ser_explicit_value` | 1.000000 | 0.652893 | 0.516340 | 1.000000 | 1.000000 | 0.000000 | 4.000000 | 4352.875000 |
| `deterministic_degraded_v1_1` | `monolithic_semantic` | 0.791667 | 0.611111 | 0.496774 | 0.000000 | 0.000000 | 0.000000 | 1.000000 | 1548.958333 |

For `deterministic_degraded_v1_1`, SER mock branch audit: 4/4 eligible groups branched; oracle-consistent first routes `1.000000`; zero-value spurious groups 0/4.

| `deterministic_structured_v1_1` | `fixed_order_semantic` | 0.791667 | 0.586207 | 0.548387 | 0.208333 | 0.000000 | 0.658333 | 4.000000 | 4400.791667 |
| `deterministic_structured_v1_1` | `react_like_semantic` | 1.000000 | 0.514706 | 0.437500 | 0.000000 | 0.000000 | 0.466667 | 4.000000 | 4428.250000 |
| `deterministic_structured_v1_1` | `ser_explicit_value` | 1.000000 | 0.609929 | 0.573333 | 1.000000 | 1.000000 | 0.000000 | 4.000000 | 4385.000000 |
| `deterministic_structured_v1_1` | `monolithic_semantic` | 0.791667 | 0.586207 | 0.548387 | 0.000000 | 0.000000 | 0.000000 | 1.000000 | 1548.958333 |

For `deterministic_structured_v1_1`, SER mock branch audit: 4/4 eligible groups branched; oracle-consistent first routes `1.000000`; zero-value spurious groups 0/4.

## Validation

- **development and evaluation separation:** `pass` — 8 development, 24 primary evaluation, and 24 paired perturbation-audit episodes have distinct manifests
- **bounded repository structure:** `pass` — six files and 100-500 lines per episode; evaluation family counts {'h1': 6, 'h2': 6, 'h3': 6, 'h4': 6}
- **branch and zero-value controls:** `pass` — evaluation control structure {'eligible_branch': 16, 'zero_value_control': 8}
- **opaque identifiers and source labels:** `pass` — opaque unit paths contain no mechanism labels, answers, or evaluator-field names
- **evaluator firewall:** `pass` — policy-visible runs contain no truth roles, useful-action labels, oracle ranks, or conclusions
- **purchased-artifact semantic scope:** `pass` — every semantic call contains exactly the artifact or bounded batch selected by its recorded action
- **matched evidence and declared budgets:** `pass` — fixed, ReAct-like, and SER use four calls/four artifacts; monolithic uses one bounded call over four artifacts
- **no real-model spending:** `pass` — all calibration records identify deterministic mock conditions and zero declared monetary cost
- **record hashes:** `pass` — verified 384 content-addressed run records
- **static-only action surface:** `pass` — only bounded artifact inspection exists; no execution, mutation, network, fuzzing, GitLab, or IDS action is present
- **identifier label and order perturbation:** `pass` — semantic first-route role and correctness preserved in 96/96 routed/ReAct paired runs

## Classifier status

Classification: **`benchmark_calibration_only`**.

The preregistered real-model classifier is frozen in the preregistration and summary, but it was not applied. Diagnostic preview labels from deterministic mocks cannot admit evidence.

## Limits

The rule interpreters are deterministic test doubles, token counts are lexical proxies, latency is declared rather than measured provider latency, and monetary cost is zero. The repositories are authored templates, not real GitLab. No conclusion about model semantics, architectural leverage, economic value, active experimentation, or deployment follows.
