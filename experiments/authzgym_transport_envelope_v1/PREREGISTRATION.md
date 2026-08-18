# AuthzGym transport-envelope v1 preregistration

Date frozen before real transport stress calls: 2026-08-17

## Question and scope

This development-only protocol asks only whether the local Mac to supervised SSH
SOCKS to wiseau to configured model-API transport can complete the already
frozen semantic-contract v1.2 workload. Transport is the only manipulated
layer. The previous semantic-contract v1.2 experiment remains immutable.

The protocol reuses exactly:

- model `patchersniper_praneeth/gpt-5.4-nano`;
- the v1.2 prompt, strict per-call JSON Schemas, vocabulary, and parser;
- reasoning effort `none`, no temperature, and the 1,024-token output ceiling;
- the v1.2 maximum of two semantic/model-response attempts;
- population hash
  `2d9eb6a25d17486bb442492d36ca2ea1c988d2d1a66539d8b5dc05542abdbaf7`;
- all 128 logical calls over only the eight development source episodes.

No old evaluation episode, architecture comparison, stronger model, prompt
tuning, semantic-schema change, estimator change, or higher-layer work occurs.

## Offline failure diagnosis

The immutable Phase 5A.4 records show eight successful provider responses in
48.047 seconds, followed by 37 curl code 28 failures lasting approximately the
15-second connect timeout, one curl code 97 proxy-handshake failure, and 202
immediate curl code 7 connection failures. All 240 failed attempts had empty
response bodies. Each API attempt used a new curl process, so a shared curl
connection pool or cross-call HTTP keep-alive session did not exist.

The strongest supported cause is failure of the long-lived SSH/SOCKS forwarding
path, which stopped completing new connections and later stopped accepting local
proxy connections. The old logs do not retain curl stderr or per-attempt SSH and
listener state, so they cannot distinguish remote SOCKS DNS, wiseau egress, or
endpoint reachability during the first timeout interval and cannot establish the
exact SSH exit instant.

## Frozen tunnel supervision

The runner selects an unused localhost port, launches only:

```text
ssh -N -T -D 127.0.0.1:PORT
    -o ExitOnForwardFailure=yes
    -o ServerAliveInterval=15
    -o ServerAliveCountMax=2
    -o ConnectTimeout=15
    -o TCPKeepAlive=yes
    -o BatchMode=yes
    -o ControlMaster=no
    nopales17@wiseau.seclab.cs.ucsb.edu
```

There is no remote command. The SSH child environment explicitly removes
`OPENAI_API_KEY` and `OPENAI_BASE_URL`. Startup requires a live SSH process, a
listening local SOCKS socket, and a local curl GET of the configured `/models`
endpoint through the tunnel. The probe uses no model inference and accepts an
HTTP response below 500 as connectivity evidence. TLS verification is disabled
only in that dedicated curl invocation.

Before every logical call, the supervisor checks the SSH process and local
listener. A failed check replaces the tunnel and repeats the free connectivity
probe before any API submission.

## Frozen recovery and HTTP policy

Each logical request has one transport reconnection/replay allowance shared
across both semantic attempts. A transport failure is a curl submission that
does not yield a complete JSON provider HTTP response. On such a failure the
runner records curl stderr, HTTP timing metadata, process/listener events, and
tunnel generation locally; terminates stale local tunnel state; establishes and
probes a fresh tunnel; and submits the exact same request bytes once.

Transport replay does not increment the semantic attempt. If the recovered
provider response violates the frozen semantic contract, the existing single
semantic/model-response retry remains available. At most three API submissions
may occur for one logical call: two semantic attempts plus one transport replay.
No infinite retry exists.

Every API submission uses a new local curl process; there is no shared HTTP
connection pool, curl session, or cross-call proxy session. A fresh process has
no prior connection cache to reuse, so no additional curl connection-reuse flag
is required.
Hostname resolution remains remote through `socks5h`. The bearer credential is
supplied only through an anonymous local curl configuration pipe, never in an
argument, file, SSH environment, or experiment artifact. Endpoint-specific TLS
verification remains disabled only in the dedicated curl clients.

### Preserved zero-inference preflight correction

The initially frozen preflight included curl's optional `fresh-connect` flag.
This Mac's system curl 8.7.1 rejected that flag as unknown with return code 26.
Two supervised tunnels and local SOCKS listeners became live, but their free
`/models` probes stopped at local curl option parsing; no benchmark request or
paid inference was submitted, and cleanup confirmed both process exit and
listener closure. The original manifest, cost gate, and nine tunnel events are
preserved under `preflight_attempt_1/`, and `PREFLIGHT_FAILURE.md` records their
hashes. Before any paid call, the redundant unsupported flag was removed and
the full protocol was frozen again. No semantic input, retry, population,
model, schema, estimator, endpoint, proxy, DNS, TLS, or credential behavior
changed.

## Frozen transport classifier

Integrity failure, a changed frozen semantic input, an incomplete logical
schedule, security/boundary failure, inconsistent accounting, or spend at or
above $1 is `invalid`.

Given valid integrity:

- `transport_stable` requires provider responses for 128/128 logical calls,
  zero permanent transport losses, zero failed tunnel-start attempts, every
  requested reconnection to complete, successful final process/listener cleanup,
  local-only credentials/artifacts, and consistent accounting;
- `transport_recoverable_but_unstable` requires 128/128 provider responses and
  zero permanent losses, but at least one allowed tunnel-start attempt failed
  before later recovery or recovery bookkeeping was not one-for-one;
- `transport_unstable` applies when any logical call is permanently lost to
  transport after the frozen allowance;
- `invalid` takes precedence over all three.

Raw transport failures do not by themselves prevent `transport_stable` if the
first permitted recovery succeeds, every logical call receives a provider
response, and all other requirements pass.

## Separate frozen semantic diagnostics

Provider responses are passed through the unchanged v1.2 parser and thresholds.
The protocol separately reports schema-valid rate, length termination,
incomplete JSON, illegal references, semantic precision/recall, action-value
compatibility, repeat exactness, and transformation equivalence. No result may
change the prompt, schema, vocabulary, parser, model, or estimator in this task.

The oracle-conditioned diagnostic remains the unchanged eight-entry computation
from v1.2. It must reproduce top-1 1.0, top-2 1.0, and normalized regret 0.0.

## Cost gate

The hard ceiling is $1. The conservative projection treats every one of the
maximum 384 API submissions as potentially billed at 4,000 uncached input tokens
and the full 1,024 output tokens, for $0.798720 at the frozen rates. Connectivity
probes make no model inference. The runner also enforces the 384-submission and
$1 ceilings at runtime.

## Mechanical next-experiment rule

1. If transport is not stable, stay at the transport layer and identify the
   remaining networking blocker.
2. If transport is stable but the semantic contract is not mechanically stable,
   return only to separately versioned semantic-contract engineering.
3. If transport and contract are stable but semantic signal is weak or absent,
   retain v1.2 and test the next stronger inexpensive model in a separate study.
4. If transport, contract, and nano semantic signal are sufficient, preregister
   an architecture experiment using a fresh untouched confirmatory population.

No architecture experiment or stronger-model call occurs here.
