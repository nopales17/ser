# Preserved zero-inference transport preflight failure

The first frozen transport preflight terminated before any benchmark request or
paid inference. Both supervised SSH processes reached a live local SOCKS
listener. Both free `/models` probes then failed locally with curl return code
26 and:

```text
curl: option --config: error encountered when reading a file
```

Offline reproduction isolated the rejected config entry: this Mac's system
curl 8.7.1 reports `--fresh-connect` as unknown. Because every submission
already launches a new curl process, no connection cache or HTTP session exists
to reuse; removing that redundant unsupported option does not alter request
bytes, semantic retry behavior, or any frozen semantic input.

The original records are retained in `preflight_attempt_1/`:

- initial manifest hash:
  `19033f0d4264448b5708edc213b0e647e18a56c8d38757c968b7e13d7d387936`;
- `FROZEN_INPUTS.json` SHA-256:
  `1f17598e747cc33e6652ccd7f8cebfe229dc5e0f27a823d8779407a1459b07b0`;
- `COST_GATE.json` SHA-256:
  `a11f8a2255773bfdf7da7d3977180e565d3d5d24f63c22d86239c6e534e92cf1`;
- `tunnel_events.jsonl` SHA-256:
  `78a6efe65c2793180a47079a7d1fd6c3e4e5ec46bf5e6a9a99c404c84eede10b`.

The event log contains two tunnel starts, two live-listener probe failures, zero
paid-inference probes, and one final cleanup record confirming process exit and
listener closure. The corrected transport protocol was refrozen before any
paid API submission.
