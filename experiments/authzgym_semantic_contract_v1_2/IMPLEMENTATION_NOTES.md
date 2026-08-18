# AuthzGym semantic contract v1.2 implementation notes

## Provenance and scope

- Prior SER HEAD: `2c6577a04426230c5fc095bc82fdf1ca413545b6`.
- The pre-run SER worktree and the read-only IDS archive were clean. The IDS
  archive remained at `38b661324725c094ffcc820371a836573f4aadc5`.
- This was a development-only semantic-interface study. It did not call any of
  the 24 previously observed evaluation episodes, compare architectures, change
  H1--H4 or the benchmark truth, or modify the SER value estimator.
- All code, prompts, requests, responses, logs, and experiment state were
  created and retained locally on the Mac. `wiseau.seclab.cs.ucsb.edu` was used
  only as transient SOCKS network egress; no remote command, transfer, or file
  creation was used.
- TLS verification was disabled only for the dedicated local API transport.
  Neither the bearer token nor endpoint value is present in these artifacts.

## Offline autopsy before interface changes

The immutable 609-attempt real-model v1 record reproduced exactly: 336 full-
contract-valid responses and 273 invalid responses. The mutually exclusive
dominant causes of the 273 invalid attempts were 134 `finish_reason_length`, 62
illegal artifact recommendations/references, 74 illegal public-symbol reference
identifiers, and 3 duplicate references. Causally useful overlapping flags were
132 incomplete or truncated JSON contents, 134 length finishes, 64 illegal
artifact references, 77 illegal reference identifiers, 3 illegal relation
identifiers, and 3 duplicate references.

The 320-token per-artifact ceiling was mechanically insufficient. At length
termination, the last top-level field begun was `hypothesis_effects` 4 times,
`recommended_next_artifact_id` 6 times, `uncertainty_flags` 13 times, and
`unresolved_references` 111 times. In contrast, none of the 86 monolithic
attempts using the 1,280-token ceiling ended for length; 68 were invalid mostly
because of illegal public-symbol references. Larger output ceilings would not
repair those dynamic-reference failures. One completed v1 SER run also exceeded
its aggregate provider-token ceiling.

## Frozen v1.2 protocol

Semantic contract v1.2 uses a compact, prose-free object with 25 fixed boolean
fact slots, four fixed candidate-effect slots, and fixed boolean relation slots
inside only the legal target slots supplied for that call. It does not ask the
model to emit artifact identifiers, hypothesis identifiers, public-symbol
identifiers, explanations, or next-artifact recommendations. Runner-side maps
translate public aliases and positional slots back to internal entities, and
evaluator-only identifiers are excluded from every model-visible enum.

The per-artifact output safety ceiling is 1,024 tokens. A 4,096-token
monolithic ceiling remains recorded for configuration parity, but this protocol
made no monolithic calls. The exact model remained
`patchersniper_praneeth/gpt-5.4-nano`, with reasoning effort `none`, at most one
identical retry, and local transport timeouts of 90 seconds plus 15 seconds for
connection setup.

Eight development episodes were crossed with eight transformations: base
entry, longest legitimate artifact, artifact reordering, symbol renaming,
candidate-label permutation, artifact-identifier variation, maximal public
summary, and a combined permutation. Repeating all 64 cases twice produced a
128-call frozen schedule. The projected worst case was 256 provider attempts,
1,024,000 uncached input tokens, 262,144 output tokens, and $0.532480, below the
$1 hard ceiling.

The protocol was frozen before real stress calls. Its population hash is
`2d9eb6a25d17486bb442492d36ca2ea1c988d2d1a66539d8b5dc05542abdbaf7` and
its input-manifest hash is
`39bcb5d11b223add3cc81909ed45b059072e7691288a56e93737c2ff75595fca`.

## Preserved run result

The full 128-record schedule was preserved. It required 248 provider attempts.
The first eight calls were valid on their first attempt; the egress SSH
connection then timed out, and all remaining 120 calls exhausted the frozen
identical retry. The transport errors were 37 curl code 28 responses, 202 code
7 responses, and 1 code 97 response, for 240 transport failures in total.

The observed first-attempt and post-retry valid rates were both 8/128, or
0.0625. The eight successful prefix responses had zero length finishes, zero
incomplete JSON, and zero illegal artifact, hypothesis, or relation references.
No manual repair or information-boundary violation occurred. Provider-reported
usage was 19,884 input tokens, including 14,848 cached input tokens, and 3,336
output tokens. The largest successful response used 2,502 input and 420 output
tokens, within the frozen 4,000/1,024 per-call ceilings. Accounted spend was
$0.005474160.

The integrity verifier passed, but the preregistered mechanical classifier was
`contract_unstable`. The semantic classifier was `semantic_signal_weak` on the
eight non-random successful prefix calls; those semantic and perturbation
numbers are nonrepresentative diagnostics, not model-capability evidence.

With perfect evaluator observations, the unchanged downstream estimator
achieved top-1 1.0, top-2 1.0, and mean normalized regret 0.0 on the eight
canonical development entries. This isolates no estimator blocker under the
oracle condition, but is not evidence about the model or an SER architecture.
The preregistered decision rule selected `case_a_new_contract_version`.

The timed-out SSH process was explicitly terminated after the run, and the
local SOCKS port had no listener afterward.
