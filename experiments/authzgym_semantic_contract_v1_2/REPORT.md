# AuthzGym semantic contract v1.2 report

This development-only experiment tests the semantic wire contract and the cheap model's capability floor. It is not an SER-vs-ReAct comparison and admits no general SER finding.

Validation: **pass**
Contract classifier: **`contract_unstable`**
Semantic diagnostic: **`semantic_signal_weak`**

## Preserved v1 autopsy

The immutable 609-attempt run reproduced 336 valid and 273 invalid responses. Dominant invalid roots were {'duplicate_reference': 3, 'finish_reason_length': 134, 'illegal_artifact_reference': 62, 'illegal_reference_identifier': 74}. The 320-token ceiling caused 134 invalid length-finished attempts; the 1,280-token monolithic condition had zero length terminations and failed mainly on unconstrained public-symbol references.

## Contract reliability

- Scheduled semantic calls: **128**; provider attempts: **248**.
- First-attempt schema-valid: **8/128** (`0.062500`).
- Valid after frozen retry: **8/128** (`0.062500`).
- Length terminations: **0**; incomplete JSON: **0**.
- Illegal artifact/hypothesis/relation references: **0/0/0**.
- Manual repairs: **0**.

## Semantic layers

| Layer | Precision | Recall |
| --- | ---: | ---: |
| Fact extraction | 0.269 | 0.438 |
| Hypothesis effect | 0.364 | 1.000 |
| Remaining unresolved relation | 0.000 | 0.000 |

Unknown hypothesis-effect rate: `0.281`.

## Downstream action-value decomposition

Model-conditioned top-1/top-2 and normalized regret: `0.000` / `0.000` / `1.000`.
Oracle-conditioned top-1/top-2 and normalized regret on the eight canonical development entries: `1.000` / `1.000` / `0.000`.
Existing estimator adequate under the preregistered oracle rule: **true**.

## Protocol stability

- Semantic-equivalence exact pairs: `0.000` across 80 pairs.
- Repeated-call exact semantic stability: `0.000` across 64 pairs.

## Resources and next experiment

Provider-reported input/output tokens: **19884 / 3336**.
Accounted spend: **$0.005474160** under the $1 hard ceiling.
Decision-rule result: **`case_a_new_contract_version`**.

No H-001, H-016, H-017, H-018, or new E-* finding is promoted from this development-only result.
