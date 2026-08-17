# MicroGym routing-v1 implementation notes

## Post-run causal-order review

After the first frozen run, source review found that `exact_open_loop` computed
its mathematically cue-independent plan after the environment reset had released
the cue, even though the plan function did not consume that cue and validation
confirmed the same action for every possible realization.

The runner was corrected to compute and store the exact open-loop action from
the frozen public problem view before calling environment reset. This was a
causal-ordering bug fix required by the preregistered comparison, not a policy or
strategy change.

The population, candidate, likelihoods, thresholds, actions, seeds, run records,
metrics, classification, and report were not changed. Exact artifact
verification after the correction reproduced every first-run artifact byte for
byte. `AdaptiveBeliefPolicy` remained unchanged.

## Frozen validation-detail wording

The frozen deterministic-replay detail says "3456/3456 policy and oracle
records." The count is the 3,456 policy run records; the nine oracle records are
separately rebuilt by the exact artifact verifier, and all 3,465 run-plus-oracle
content hashes are checked by validation. The imprecise frozen wording is
preserved rather than rewriting the first-run artifacts.
