# Preserved stronger-model smoke preflight failure

The first frozen smoke attempt used manifest
`525b2377d3ac71bb05c6ded88977a8d08a51a1f4577a685e57396a87b1b59ac6`.
All four exposed smoke calls returned contract-valid provider responses without a
retry or transport failure, accounting for $0.012318. Smoke semantic accuracy
was not inspected or admitted as evidence.

The post-run integration check failed before any development call because the
inherited v1.2 summary routine assumes all eight transformation variants are
present. The deliberately four-case smoke population contains only `base_entry`,
so the routine raised `KeyError: artifact_reordering`. This is an offline
analysis integration defect, not a transport, response-contract, semantic, or
model failure.

The original manifest, cost gate, and complete smoke transport/response/run/event
artifacts are preserved under `preflight_attempt_1/`. The exact pre-correction
runner hash recorded by that manifest is
`d90706df5e864511ac57d91cf347edbbfe21080b1d977c9e96f2609168e0133c`.
The preserved file hashes are:

| File | SHA-256 |
| --- | --- |
| `FROZEN_INPUTS.json` | `4e78c257840daee32bdab93a769995a518e887535139d84ac50bd0050b2cfa1e` |
| `COST_GATE.json` | `2cf50dd3a940579681b38b36d6565f6a7921645c1f0ba8abd5bfeea83e68cf91` |
| `smoke/execution.json` | `4798b9e510285f1a112515d8aeefb6f99cf5f70ff45687ef34b56933e9855906` |
| `smoke/provider_responses.jsonl` | `8e3a47731a3c2d3ad48a76f2bab3eb2e17ca6eab388c415b6d3e0063d641b27f` |
| `smoke/runs.jsonl` | `7ad6708053c76fd0d7a0b667ff4bcfded772108a06b7e642dadad52439a320a4` |
| `smoke/transport_attempts.jsonl` | `d2233a5f8cb69e4b70d142138cf363b25ac3e03953bea6755a3d094cfe534c6f` |
| `smoke/tunnel_events.jsonl` | `9d20a14d7faac6427423cf6f3635c890930f58ed5f6b8cba4650f468cf9a721b` |

The only correction is a smoke-specific contract/accounting summary that does
not request absent transformation peers. No prompt, schema, model, semantic
parser, population, estimator, retry, transport, or threshold changes. The
$0.012318 spent here remains charged to the user-set $2.50 global ceiling before
the corrected protocol is frozen and smoke is repeated.
