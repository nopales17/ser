# AuthzGym transport-envelope v1 implementation notes

## Scope

Execution remained local on the Mac. `wiseau` was used only as an SSH dynamic
forwarding hop (`-N -T`); no remote command ran and no SER prompt, response,
credential, benchmark file, temporary artifact, or workspace was created
there. The SSH child environment omitted `OPENAI_API_KEY` and
`OPENAI_BASE_URL`. Each API request used a new local curl process, remote
hostname resolution through `socks5h`, and the endpoint-scoped TLS-verification
exception. The bearer header was supplied through an inherited anonymous pipe.

## Preserved preflight correction

The first frozen free connectivity preflight found that this Mac's system curl
8.7.1 does not implement the optional `fresh-connect` flag. Both SSH processes
and SOCKS listeners were live, but curl returned code 26 during local config
parsing. No benchmark request or paid inference occurred. The initial manifest,
cost gate, and nine event records are preserved under `preflight_attempt_1/`;
their hashes and cleanup state are recorded in `PREFLIGHT_FAILURE.md`.

Because every request already launches a new curl process with no connection
pool or reusable session, the unsupported flag was redundant. It was removed,
the corrected protocol was tested and refrozen before paid execution, and no
semantic input or model setting changed.

## Frozen execution

- Corrected frozen manifest:
  `e3dbeec53f6e082bd1a970e9e67acf4af91c0988167305ee84a3a476aab586f8`.
- Population:
  `2d9eb6a25d17486bb442492d36ca2ea1c988d2d1a66539d8b5dc05542abdbaf7`.
- Logical calls: 128/128 completed with a provider response.
- API submissions: 128; semantic retries: 0; raw transport failures: 0.
- Tunnel generations: 1; requested/completed recoveries: 0/0.
- Longest provider-response sequence: 128.
- Accounted provider spend: $0.086505640 under the $1 ceiling.
- Provider-reported input/output tokens: 309,002/50,988, including 216,832
  cached input tokens and zero reasoning-output tokens.
- Final cleanup recorded process exit and closure of the localhost listener.

The transport classifier is `transport_stable`. All 128 responses were valid
on the first frozen semantic attempt, producing `contract_stable`. The
development-only semantic diagnostic is `semantic_signal_weak`: fact
precision/recall was 0.166667/0.095588, hypothesis-effect precision/recall was
0.310606/0.320312, and unresolved-relation precision/recall was
0.017241/0.001894. Repeat semantic exactness was 0.296875 and transformation
equivalence exactness was 0.0875. The unchanged oracle-conditioned estimator
reproduced top-1 1.0, top-2 1.0, and normalized regret 0.0.

These are development-only capability-floor diagnostics, not architecture
evidence. No `E-*` finding is created and H-001, H-016, H-017, and H-018 are
not promoted. The preregistered mechanical next case is C: retain semantic
contract v1.2 and separately preregister the next stronger inexpensive model.
