# Static Semantic AuthzGym v1 implementation notes

## First frozen mock-run compatibility failure

The first frozen mock aggregate stopped before writing any run or summary
artifact. The consolidated baseline combined four purchased artifacts into one
structured result, but the runner applied the mock condition's per-artifact
output allowance only once. The result exceeded that cap and raised the failure
preserved in `FIRST_RUN_FAILURE.json`. No aggregate candidate metric was emitted
or inspected.

The compatibility correction multiplies the per-artifact allowance by four for
that explicitly bounded four-artifact call. This gives the consolidated baseline
the same total output allowance available to four single-artifact calls while
retaining its one-call accounting. The global frozen 2,000-output-token ceiling
still applies.

The frozen populations, prompts, model condition file, parser rules, policy
behavior, decision rule, and classifier thresholds were not changed. This note
does not convert mock calibration into empirical evidence.

## Preserved invalid invariance result

The completed v1 mock calibration then failed the identifier/order invariance
check: 32 of 96 routed/ReAct paired runs differed in first-route role or final
correctness under opaque renaming. The degraded mock condition selected its
deterministic omissions using artifact IDs. The frozen validation detail says
"preserved in 96/96" because it reported the number compared rather than the
number passing; its `fail` status is correct. Both the leakage defect and that
reporting defect are preserved here instead of rewriting v1 artifacts.

The corrected omission schedule is evaluated only in the separately frozen
`authzgym_static_v1_1` calibration. The original v1 manifests, runs, validation,
summary, and report remain immutable and exactly replayable.
