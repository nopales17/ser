# AuthzGym transport-envelope v1 report

This development-only study manipulates only local transport supervision. The semantic-contract v1.2 prompt, schema, model, population, parser, and estimator remain frozen.

Validation: **pass**
Transport classifier: **`transport_stable`**
Semantic-contract diagnostic: **`contract_stable`**
Semantic-signal diagnostic: **`semantic_signal_weak`**

## Prior failure evidence

The immutable Phase 5A.4 sequence retained 8 successful prefix attempts followed by 37 timeouts, 1 proxy-handshake failure, and 202 immediate connection failures. The strongest supported cause is the long-lived SSH/SOCKS forwarding path; the old logs cannot isolate remote DNS, wiseau egress, or endpoint health during the initial timeouts.

## Transport completion

- Provider responses received: **128/128**.
- Raw transport failures: **0**.
- Successful recoveries: **0** of **0** requested.
- Permanent logical-call losses: **0**.
- Tunnel generations: **1**; failed starts: **0**.
- Longest successful logical-call sequence: **128**.
- Final process/listener cleanup: **true**.
- Provider-response latency is grouped by tunnel generation in `summary.json`; **0** before/after generation transition pairs were observed.

## Frozen semantic-contract diagnostics

- First-attempt schema-valid: **128/128** (`1.000000`).
- Valid after frozen semantic retry: **128/128** (`1.000000`).
- Length/incomplete JSON: **0/0**.
- Illegal artifact/hypothesis/relation references: **0/0/0**.
- Fact precision/recall: **0.166667/0.095588**.
- Hypothesis-effect precision/recall: **0.310606/0.320312**.
- Unresolved-relation precision/recall: **0.017241/0.001894**.
- Repeat exactness: **0.296875**; transformation semantic equivalence: **0.087500**.

## Oracle and resources

Oracle-conditioned top-1/top-2/regret: **1.000000/1.000000/0.000000**.
Provider-reported input/output tokens: **309002/50988**.
Accounted spend: **$0.086505640** under the $1 ceiling.
Decision-rule result: **`case_c_same_contract_next_stronger_inexpensive_model`**.

No H-001, H-016, H-017, H-018, or new E-* finding is promoted by this transport/development result.
