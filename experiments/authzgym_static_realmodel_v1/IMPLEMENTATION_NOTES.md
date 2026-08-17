# Static Semantic AuthzGym real-model v1 implementation notes

## Provenance and topology

- Prior SER HEAD: `bcd0da1a87631414e9391999f15ff9d55c23a3bc`.
- All runner code, prompts, benchmark source, requests, responses, traces,
  accounting, and reports remained under the local SER repository on the Mac.
- `wiseau.seclab.cs.ucsb.edu` was used only by local `ssh -N -D` SOCKS
  forwarding on `127.0.0.1:47819`. No remote command, workspace, file transfer,
  remote environment forwarding, or remote temporary artifact was used.
- The scoped model client alone used `socks5h` and disabled TLS certificate-chain
  verification. SSH host verification and unrelated local TLS behavior were not
  changed.
- Local configuration names were `OPENAI_BASE_URL` and `OPENAI_API_KEY`. Values
  were never printed or persisted. The API key reached curl through an anonymous
  inherited configuration pipe rather than an argument or file.

This workflow cannot make a forensic claim about infrastructure-level SSH or
network logs on systems it did not administer. It did create no remote SER
research file or workspace.

## Selection, development, and freeze

One non-inference catalog request identified the endpoint's available models.
`patchersniper_praneeth/gpt-5.4-nano` was selected before benchmark inference for
cost, structured-output support, bounded context, and extraction suitability.

The single development inference succeeded without retry:

- input tokens: 1,586;
- output tokens: 287;
- accounted cost: $0.000675950;
- strict semantic parse: valid.

The conservative complete-run projection, including every allowed retry, was
$1.536675950. The frozen evaluation therefore passed the preregistered <$4
proceed gate with at least $1 margin below the $5 absolute ceiling.

The pre-evaluation manifest hash was
`733db20bb45ce143a3a421a4539f70e73373e38205b758736bb4330ad4ccd730`.
It binds the preregistration, prompt, schema, configuration, source v1.1
populations, run schedule, classifier thresholds, and execution/analysis code.

## Complete frozen run

All 192 scheduled runs completed: 96 primary evaluation runs and 96 paired
perturbation runs across fixed-order, ReAct-like, SER explicit-value, and
monolithic architectures. The complete task used 610 inference calls including
development and accounted $0.379060610 from provider-reported token usage at the
frozen listed rates. This is accounting, not a provider invoice.

The 609 frozen response attempts contained 1,128,619 input tokens, 176,798 output
tokens, 379,648 cached input tokens, and 2,308,412.882 ms aggregate request
latency. Exact offline reanalysis verifies every response and run hash.

## Fail-closed outcome

Validation failed because only 88/192 runs remained valid. Across the frozen
run, 336 model responses passed the full semantic contract and 273 attempts did
not. Envelope inspection found:

- 135 responses with `finish_reason=length`;
- 132 response contents that were not complete JSON;
- 477 syntactically valid JSON contents;
- additional dynamic-contract failures for unavailable next-artifact
  recommendations, references outside the public inventory, and one duplicate
  reference case;
- one otherwise completed SER run over its frozen provider-token ceiling.

The preregistered classifier is therefore `invalid`. Diagnostic primary metrics
must not be interpreted as an architecture comparison: SER, ReAct-like, and
fixed each produced 1/24 correct scheduled conclusions; monolithic produced
0/24. SER and ReAct each had eight valid primary runs. SER fact precision/recall
were 0.642/0.493, effect-direction precision/recall were 0.200/0.077,
useful-action top-1/top-2 were 0.179/0.321, and mean normalized routing regret was
0.764. SER versus ReAct had one paired win, one paired loss, and 22 ties, but the
invalid-run rate prevents an architecture-leverage inference.

No semantic-routing, semantic-signal, SER-leverage, authorization-competence, or
general model-capability finding is admitted. H-016, H-017, and H-018 are not
promoted. Phase 5B, executable AuthzGym, historical cases, GitLab, IDS, fuzzing,
and stronger-model testing remain gated.

## Follow-up boundary

The smallest justified follow-up is a new preregistered static protocol that
first establishes response-contract reliability under a sufficient output
ceiling and tighter dynamic-ID/reference constraints on development episodes,
then repeats the full frozen population without post-result tuning. It must not
reuse these evaluation outputs for accuracy optimization. A larger population,
stronger model, or executable environment is not yet justified.
