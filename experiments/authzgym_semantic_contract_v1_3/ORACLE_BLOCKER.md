# AuthzGym v1.3 oracle blocker

Status: blocking. No estimator, gold, source, adapter, scoring, or population
change is authorized by this failure. Inference remains unauthorized.

The unchanged historical estimator passed the development canonical oracle
gate:

- canonical development cases: 8
- top-1: 0.625 (required >= 0.60)
- top-2: 0.875 (required >= 0.80)
- mean normalized regret: 0.175 (required <= 0.35)
- illegal target/value count: 0
- transformed action-value equivalence: 40/40 checks within `1e-12`

The same unchanged estimator failed the sealed fresh-confirmation canonical
oracle gate:

- canonical confirmation cases: 8
- top-1: 0.625 (required >= 0.60)
- top-2: 0.750 (required >= 0.80)
- mean normalized regret: 0.242 (required <= 0.35)
- illegal target/value count: 0
- transformed action-value equivalence: 40/40 checks within `1e-12`

The blocking question is not an implementation choice delegated to this worker.
Under section 13's fixed five-category adapter, several canonical confirmation
gold responses contain only non-positive candidate effects. The unchanged
estimator then assigns the same `1.05` score to every referenced legal target
and falls back to canonical ordinal order, which can rank a less useful target
first or second. The estimator hash matched the frozen historical source hash
`092a7a87d1227c1a1c85ac46c7122e38ac1b6b24d7aaa90abee05abfe4167393`.

The smallest decision needed to unblock implementation is a separate Sol/Astra
decision that either:

1. accepts a prospective, separately versioned estimator/adapter change with
   its own preregistration and evidence boundary; or
2. revises the confirmation eligibility or oracle-gate interpretation in a new
   accepted ADR and preregistration version without editing this frozen v1.3
   semantics.

Changing the estimator to make this gate pass, reinterpreting the gate after
seeing confirmation results, replacing seeded confirmation cases, or weakening
the mapping would violate ADR-0019 and the normative preregistration.
