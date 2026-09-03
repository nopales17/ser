# AuthzGym stronger-model semantic capability v1 report

This staged study changes only the model under semantic contract v1.2. It is not an architecture comparison.

Validation: **pass**
Classification: **`semantic_capability_below_threshold`**
Selected model: **`patchersniper_praneeth/gpt-5.4-mini`**

The preserved initial smoke preflight made 4 valid non-semantic calls, cost $0.012318, and was superseded only because its offline base-only analyzer was incompatible with the smoke population. That cost remains included below.

## Smoke

Population hash: `9c64104b4257319debc7762db5e7d53b20b297c4ec0a5ccb5fd6d4e43b257549`.
Transport/contract: **`transport_stable`** / **`contract_stable`**.
Logical calls/provider attempts/provider responses: **4 / 4 / 4**.
Raw/permanent transport failures: **0 / 0**.
First-attempt/post-retry valid rates: **1.000000 / 1.000000**.

## Development

Population hash: `070d083ef23906f95a348fcb7f359a17593cc08225ec4ae074e2380ad80bef71`.
Transport/contract: **`transport_stable`** / **`contract_stable`**.
Logical calls/provider attempts/provider responses: **16 / 16 / 16**.
Raw/permanent transport failures: **0 / 0**.
First-attempt/post-retry valid rates: **1.000000 / 1.000000**.

| Metric | Observed | Threshold | Result |
| --- | ---: | ---: | --- |
| Fact precision | 0.322034 | >= 0.65 | fail |
| Fact recall | 0.542857 | >= 0.50 | pass |
| Effect precision | 0.300000 | >= 0.60 | fail |
| Effect recall | 0.562500 | >= 0.50 | pass |
| Unresolved precision | 1.000000 | >= 0.60 | pass |
| Unresolved recall | 0.014493 | >= 0.50 | fail |
| Useful-action top-1 | 0.000000 | >= 0.60 | fail |
| Useful-action top-2 | 0.187500 | >= 0.80 | fail |
| Mean normalized regret | 0.795833 | <= 0.35 | fail |

Semantic classifier: **`semantic_signal_weak`**.
Transformation-equivalence exact rate: **0.0** across 8 scheduled pairs.
Repeat exactness: **not scheduled under the $2.50 ceiling**.

## Confirmation

Not executed under the frozen gate.

## Fresh oracle diagnostic

Top-1/top-2/mean normalized regret: **1.000000 / 1.000000 / 0.000000** across 8 canonical fresh episodes.
Oracle gate: **pass**.

## Failure taxonomy and resources

Failure taxonomy: `{"benchmark_failure":false,"downstream_estimator_failure":false,"permanent_transport_failures":0,"response_contract_failures":0,"semantic_failure":true,"transport_failures":0}`.
Provider-reported input/cached/output tokens: **59297 / 34560 / 9984**.
Logical calls/provider attempts/provider responses: **24 / 24 / 24**.
Accounted spend: **$0.066072750** under the **$2.50** hard ceiling.

## Interpretation

The frozen semantic channel did not establish confirmatory semantic capability.

This result does not establish SER architecture advantage, any listed hypothesis, real-software competence, or bug-finding capability. No E-* item is admitted.

Next empirical decision: **`investigate_semantic_representation_failure`**.
