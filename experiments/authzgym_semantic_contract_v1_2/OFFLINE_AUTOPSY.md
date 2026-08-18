# AuthzGym real-model v1 offline response autopsy

This is a read-only reanalysis of the 609 preserved provider attempts. It does not repair, reinterpret, or rerun the invalid experiment.

## Exact accounting

- Attempts: **609**.
- Full-contract valid: **336**.
- Full-contract invalid: **273**.
- Run-level provider-token ceiling violations: **1**.

## Dominant root cause for each invalid attempt

| Root cause | Attempts |
| --- | ---: |
| `duplicate_reference` | 3 |
| `finish_reason_length` | 134 |
| `illegal_artifact_reference` | 62 |
| `illegal_reference_identifier` | 74 |

## Causally useful overlaps

| Cause | Invalid attempts |
| --- | ---: |
| `duplicate_reference` | 3 |
| `finish_reason_length` | 134 |
| `illegal_artifact_reference` | 64 |
| `illegal_reference_identifier` | 77 |
| `illegal_relation_identifier` | 3 |
| `incomplete_or_truncated_json` | 132 |

## Field visible at length termination

| Last top-level field begun | Invalid attempts |
| --- | ---: |
| `hypothesis_effects` | 4 |
| `recommended_next_artifact_id` | 6 |
| `uncertainty_flags` | 13 |
| `unresolved_references` | 111 |

## Conclusions

1. The 320-token per-artifact ceiling was mechanically insufficient: length termination dominated the invalid attempts and incomplete JSON was its principal overlap.
2. The 1,280-token monolithic ceiling was not mechanically insufficient: none of its 86 attempts ended for length, and observed outputs remained far below the ceiling. Its 68 invalid attempts were dominated by illegal public-symbol references, which more output would not repair.
3. The fields reached at length termination are listed above. The count is derived from the last top-level key begun in each preserved partial response.
4. Valid JSON still failed on model-generated artifact recommendations, public-symbol references, relation tags, and duplicate references. No illegal hypothesis ID was observed. A larger ceiling cannot fix these legality failures.
5. One completed SER run separately exceeded its frozen aggregate provider-token ceiling. A larger per-call ceiling requires a correspondingly explicit run-level resource rule; it is not a parser repair.

The accompanying JSON retains per-attempt architecture, split, provider-token counts, configured maximum, retry status, artifact size, summary size, finish reason, root cause, overlaps, and response hash without copying response contents.
