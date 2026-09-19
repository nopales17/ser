# Roadmap

This warm document owns sequence and the project cursor. Exactly one phase has
status `active`. A phase advances only when its exit criteria are satisfied; far
phases remain deliberately coarse.

Allowed statuses: `planned`, `active`, `done`.

## Phase 0 -- Knowledge architecture

- status: done
- goal: establish durable conceptual identity, authority, provenance, project
  memory generation, and lightweight coherence checks without building SER.
- exit: the canonical idea map exists; generated views reproduce
  deterministically; the coherence checker passes; a new agent can identify
  current maturity, unresolved ideas, and the next task from the context packet.

## Phase 1 -- Legacy component inventory

- status: done
- goal: inspect the read-only IDS archive and classify candidates as reuse
  unchanged, generalize, empirical evidence only, inspiration only, or discard.
- boundary: no SER runtime, IDS adapter, code copy, or data import.
- exit: a reviewed inventory records each candidate's provenance, domain
  assumptions, proposed classification, and unresolved transfer risk.

## Phase 2 -- Formalize the minimal control problem

- status: done
- goal: define the smallest useful state, action, observation, transition, cost,
  outcome, stopping, and metric formulation.
- boundary: do not freeze epistemic-unit or coupling-operator schemas merely to
  make implementation convenient.
- exit: a falsifiable specification names baseline policies, resource accounting,
  and the questions that MicroGym must distinguish.
- result: the accepted specification separates latent world, released history,
  controller epistemic state, legal action capabilities, raw vector resources,
  stopping, and evaluator outcomes; it defines 22 semantic contracts, 12
  required invariants, baseline families, and four domain pressure tests. This
  result is architectural, not experimental evidence.

## Phase 3 -- MicroGym

- status: done
- goal: implement zero-LLM synthetic environments and trivial baseline
  controllers with known hidden state and computable optimal or near-optimal
  behavior.
- boundary: implement only the accepted Phase 2 contracts needed for the
  smallest falsifiable experiment. Do not add an LLM, graph runtime, learned
  policy, coupling laws, universal confidence calculus, IDS adapter, or
  production SER framework.
- exit: matched-cost fixed, random, exhaustive, and candidate routing policies
  can be compared reproducibly; noisy, failed, and abstaining trajectories are
  represented; raw vector costs and stopping regret are computable; hidden and
  evaluator-only information are demonstrably firewalled from normal policies.
- result: MicroGym v1 froze 24 regimes and 728 episodes, produced 7,280 valid
  normal-policy runs plus 728 exact-oracle traces, and passed replay, firewall,
  cost, seed, and invariance checks. The candidate lowered the preregistered
  scalar objective mainly through lower expenditure, but worsened decision loss,
  produced zero observation-conditioned branches, and failed the intended
  adaptive-routing test. The admitted finding is narrow; no broad hypothesis was
  promoted.

## Phase 4 -- Adaptive-routing falsification follow-up

- status: done
- goal: determine whether a preregistered public-model policy can exhibit and
  benefit from genuinely observation-conditioned routing once STOP calibration
  no longer suppresses the branch choice.
- boundary: preserve MicroGym v1 unchanged. Make the smallest synthetic
  policy/admission-rule correction; require positive counterfactual branching
  and retain the same-model open-loop control. Do not add IDS, GitLab, fuzzing,
  LLMs, graphs, or a new domain.
- exit: a frozen follow-up either demonstrates a paired advantage attributable
  to realized-observation routing, or records a clean null/negative result and
  narrows or rejects that mechanism before any semantic/software expansion.
- result: MicroGym routing-v1 froze nine regimes and 1,152 episodes under a
  one-acquisition horizon with no adaptive STOP. Six regimes had positive exact
  value of adaptivity and three were zero-VOA controls. The unchanged myopic
  candidate branched at 6/6 eligible nodes, matched the exact closed-loop route
  at 6/6, captured all oracle-available one-step adaptivity, and made 0/3
  spurious zero-VOA branches. This supports only a narrow explicit-likelihood,
  one-step routing claim; it does not establish semantic action-value estimation
  or general SER value.

## Phase 5 -- Controlled authorization action-value estimation

- status: active
- goal: determine whether a controller can estimate decision-relevant
  epistemic-action values from imperfect software and authorization evidence
  when clean likelihood tables are not supplied.
- selection rule: use the smallest controlled authorization-oriented software
  environment that separates action-value estimation from generic software
  task skill while advancing the GitLab authorization research trunk.
- boundary: do not begin with real GitLab integration, a production fuzzer, or
  broad vulnerability discovery. IDS remains read-only and is used only after a
  new explicit decision showing it is a materially cleaner bridge for this
  exact question. Do not add graphs, coupling laws, learned policies, or
  cross-substrate environments.
- current cursor: Phase 5A.1 through Phase 5A.7 are complete; Phase 5A overall
  is not complete. Real-model v1 remains `invalid`, semantic-contract v1.2
  remains preserved as transport-unstable, and transport-envelope v1 remains
  the transport/contract-stable Nano wire diagnostic; ADR-0019 withdraws its
  clean semantic capability-floor interpretation. Phase 5A.6 changed only
  the model to `patchersniper_praneeth/gpt-5.4-mini` under unchanged v1.2. Its
  smoke and 16 executed development calls were all first-attempt schema-valid
  with zero transport failures or retries, but the frozen early-stop rule fired
  at 16/32 because even perfect remaining calls could not repair fact precision,
  effect precision, unresolved-relation recall, action top-1/top-2, or regret.
  The untouched 64-call confirmatory population was not run. Evaluator-oracle
  v1.2 content retained top-1 1.0, top-2 1.0, and regret 0.0 on both development
  and fresh canonical entries, so the deterministic estimator and population
  remain adequate under that diagnostic. The valid classification is
  `semantic_capability_below_threshold`; it admits no architecture or E-* finding.
  Phase 5A.7 then audited all 16 exposed development cases offline. The audit
  found that the v1.2 evaluator omits source-direct facts required by the public
  prompt and that test-specific labels require evaluator-only logical roles.
  All four frozen diagnostic cases failed the preregistered answerability gate,
  so decomposed Mini and stronger-model probes were not run; incremental cost
  was zero and confirmation remained untouched. The valid localization is
  `benchmark_ambiguity_detected`. The next step is separately versioned
  benchmark/task-definition repair that preserves v1.2 and the prior result,
  re-establishes answerability and the evaluator firewall, and precedes any
  model escalation, representation intervention, or architecture comparison.
- accepted repair specification: ADR-0019 freezes AuthzGym v1.3 as a new
  measurement instrument rather than a v1.2 rewrite. The accepted public task
  retains f0--f16, four mechanism families, seven non-summary variants, public
  deterministic local-cue effects, and five visible-call categories; it retires
  f17--f24, excludes hidden logical roles and `maximal_public_summary`, and
  prohibits evaluator-derived normal state. The exact preregistration and
  mechanical implementation handoff live in
  `experiments/authzgym_semantic_contract_v1_3/`. Historical v1.2 artifacts and
  results remain immutable and are qualified only through the separate living
  corrigendum.
- current cursor: v1.3 offline implementation is complete through the
  development and fresh-confirmation populations, independent certificates,
  public-only answerability checker, restricted-field firewall suite, scoring
  fixtures, and the fixed estimator adapter. The unchanged historical estimator
  passes the development canonical oracle gate but the sealed fresh-confirmation
  canonical top-2 gate fails at 0.75 versus the frozen `>= 0.80` requirement.
  `ORACLE_BLOCKER.md` records the blocker. Population freeze and all inference
  remain unauthorized; the next admissible step is a separate Sol/Astra decision
  on a versioned estimator/adapter change or a new accepted oracle/confirmation
  interpretation. An oracle or validator failure is not permission to tune
  semantics or the estimator.
- accepted repair authorization: ADR-0020 accepts
  `experiments/authzgym_estimator_repair_v1_3_1/REPAIR_STUDY_PREREGISTRATION.md`
  as the governing preregistration for `est-repair-v1.3.1` and authorizes
  bounded offline development under the fixed A then B then C order, with a
  total budget of at most 10 attempts (`<= 10`). The Tier-1
  authorized-information ceiling is computed before any candidate; B0, B1, B2,
  B3 and the B2-derived ND-3 floor are frozen before any candidate evaluation;
  ND-1, ND-2, ND-3, own-ranking invariance, the section-2 input allowlist, and
  the expanded section-9 component firewall are enforced exactly as specified.
  The study is an existence/sufficiency study: it stops the whole development
  study at the first admissible passing candidate, never evaluates a second one,
  and preserves every refused or failing attempt in `CANDIDATE_LEDGER.jsonl`.
  Section-8 successor confirmation generation and execution are not authorized;
  a later decision must name the frozen component hash and the frozen
  development-report hash first. The historical estimator, the fixed adapter,
  all v1.3 semantics, populations, thresholds, usefulness targets, prior
  results, and protected artifacts stay byte-unchanged, and model/provider
  inference remains unauthorized.
- accepted correction: ADR-0021 accepts
  `experiments/authzgym_estimator_repair_v1_3_1/CORRIGENDUM.md` after the study
  stopped at handoff step 1. The recorded `longest_artifact` regret `0.783` was a
  transcription of the confirmation split; step-1 reproduction is authorized
  against the development value `0.6583333333333333`, with no gating metric or
  threshold changed and `longest_artifact` still reported-only and
  non-selecting. The own-ranking obligation is resolved prospectively as
  own-selection-decision equivariance: mapped value-vector equivalence still
  required, B0 still 36/40, a candidate must reach 40/40, no arbitrary order
  among tied or equivalent targets is required, and full-order invariance is
  descriptive only. ND-1, ND-2, and ND-3 are unchanged. The step-0 hashing of
  confirmation-named files is a procedural deviation that is not retroactively
  authorized; on the verified facts that no candidate existed, no budget was
  consumed, no confirmation content was parsed or used, the population was
  already spent, and no successor population existed, it does not invalidate the
  study, and the integrity procedure is amended so the development harness opens
  or hashes no confirmation path.
- development result: the ADR-0020/0021 study terminated prospectively at its
  first admissible pass. `est-repair-v1.3.1-B-1` (arm B, estimator-only) passes
  all nine gate checks -- canonical top-1 `0.75`, top-2 `1.0`, regret
  `0.116667`, zero illegal targets, ND-1/ND-2/ND-3 with strict-unique-maximum
  `6` against the frozen floor `4`, own-selection equivariance `40/40`, frozen
  section-14 equivalence `40/40`, complexity `3` of `4` -- with the expanded
  action-value firewall passing and zero failing leave-one-source-out folds.
  Three of ten attempts were used; A-1 and A-2 met the frozen thresholds but
  failed ND-1/ND-2 on the two degenerate ownership cases, and Arm A was closed
  after 2 of 4 attempts on a written impossibility argument, recorded as a
  deviation. The label `estimator-only-change-sufficient` is sufficiency with the
  adapter arm untested, not adapter adequacy and not attribution of the preserved
  fresh-confirmation failure. The result confirms nothing and is a
  `development_component_compatibility_diagnostic`.
- current cursor: ADR-0022 authorizes only the already-preregistered section-8
  successor confirmation for the exact frozen B-1 component named by hash:
  generate and freeze `confirmation_v1_3_1` at layouts 42/43, certify and
  validate in the isolation order, run one and only one oracle evaluation under
  unchanged gates, and preserve the outcome either way. A construction,
  duplication, answerability, firewall, or freeze failure stops execution and is
  recorded rather than repaired; a failing one-shot result is final for this
  component and no second population is generated. Changes to B-1, further
  candidate development, spent-confirmation reuse, case replacement, threshold or
  benchmark changes, inference, Jev, adaptive-routing experiments, and
  architecture comparison all remain unauthorized.
- successor confirmation result: the ADR-0022 one-shot successor confirmation
  executed and passed. `confirmation_v1_3_1` was generated and frozen at layouts
  42/43, certified and validated in the section-8.7 isolation order
  (answerability pass, firewall pass), and evaluated exactly once: canonical
  top-1 `0.875`, top-2 `1.0`, mean normalized regret `0.058333`, zero illegal
  targets, own-selection equivariance `40/40`, section-14 equivalence `40/40`,
  ND-1/ND-2/ND-3 true as reported-only diagnostics, zero failing
  leave-one-source-out folds, and **zero provider calls**. The population is
  sealed at `463d208f...` and is spent. This confirms compatibility of the
  frozen `est-repair-v1.3.1-B-1` component with the fixed v1.3 instrument under
  the preregistered controlled condition. It is not authorization reasoning,
  adaptive routing, architecture, transfer, model capability, instrument
  validation, a diagnosis of the preserved historical-estimator confirmation
  failure, or a pass of AuthzGym v1.3 preregistration section 16, which was
  never satisfied and is not claimed to have been.
- accepted next condition: ADR-0023 accepts
  `experiments/authzgym_model_semantic_v1_3_1/PREREGISTRATION.md` as repository
  authority for `model-semantic-v1.3.1-N1` and authorizes **only zero-inference
  mechanical implementation** of that package and its development harness,
  stopping at the preregistered pre-inference freeze boundary. The experiment
  changes exactly one link, `gold semantic response -> actual model semantic
  response`, leaving v1.3 semantics, `est-repair-v1.3.1-B-1`, thresholds,
  endpoints, populations, retry policy and the closed-loop boundary frozen. The
  primary endpoint is choice-set preservation -- `M_i` non-empty and a subset of
  `G_i` -- at `>= 7/8` canonical sources, separately on each development repeat,
  computed without the evaluator canonical ordinal. Effect self-consistency is
  adjudicated `diagnostic_only`: mandatory to compute, enumerate and report,
  outside validity precedence, with no advancement threshold and no veto over
  development eligibility or untouched-confirmation success. No unresolved
  research-semantic decision remains in the package. Model or provider
  inference, the 112 development calls, confirmation generation or access,
  model substitution or escalation, prompt tuning, retry-policy changes, Jev,
  and closed-loop execution or architecture work all remain unauthorized; each
  requires its own later decision.
- current cursor: model-semantic study accepted; zero-inference implementation
  in progress, freeze incomplete. Handoff steps 1--6 are complete with zero
  provider calls: integrity baseline, zero-inference model-condition
  verification and cost gate (`patchersniper_praneeth/gpt-5.4-nano`, projected
  worst case `$0.69888` against the `$2.50` ceiling), audited reader and access
  ledger, client and retry state machine, and the S-3 gold-adequacy check
  reproducing the recorded B-1 development figures with no degenerate gold
  choice set. `freeze_complete` is `false` on two recorded items: the section
  12.1 S-7 structural non-gating guarantees and the section-18 complete
  scoring/gate/error-propagation implementation and tests.
  `IMPLEMENTATION_CLARIFICATION.md` records that this machinery is already
  inside ADR-0023's authorized scope -- its `Authorized scope` bullet names
  "scorer wiring, error-propagation classification and tests" -- and that the
  defect was only the handoff's mechanical step order, which placed that
  machinery after the development-inference stage that the freeze itself gates.
  No ADR is appended for it: `MAP.md` assigns step order to the warm handoff and
  explicitly not authorization scope, and nothing research-semantic changes.
  Steps 6A--6D now carry the dormant implementation, the final
  integrity/static/access checks, the manifest and checklist finalization, and
  the stop. Steps 6A--6C are complete; the sole remaining blocker is PENDING-3.
  Four living-governance documents -- `MAP.md`, `plan/ROADMAP.md`,
  `state/STATUS.yaml`, `state/CONTEXT_PACKET.md` -- differ from their Step-1
  integrity baseline because ADR-0023 item D10 and the accepted ordering
  clarification required exactly those edits. Independent recomputation confirms
  4 differing files of 233 baselined, none missing; all 52 section-18 frozen
  inputs and every model-facing input -- populations, prompt, schemas, v1.3
  contract, B-1, thresholds, model condition and retry machinery -- are
  byte-identical to their Step-1 hashes.
  `IMPLEMENTATION_CLARIFICATION.md` section 6 prospectively accepts those four
  exact old-to-new transitions by hash for the final freeze, preserves the
  Step-1 baseline unaltered as historical evidence, waives integrity checking
  for nothing else, and makes any later change to those four files new drift
  that halts again. Two disclosed deviations are acknowledged prospectively without
  retroactive authorization: DEV-1, the handoff naming a never-open path as a
  restatement source, resolved fail-closed; and DEV-2, a procedural never-open
  violation in pre-`AuditedReader` reconnaissance that reproduced an
  already-published digest, recorded with its evidentiary scope stated precisely
  rather than overclaimed. Step 7 development inference remains unauthorized and
  requires its own later decision.
- readiness: Phase 5B is not ready. It requires a valid actual-model run to extract
  useful facts, rank inspections beyond trivial heuristics, route conditionally,
  and improve matched decision quality or efficiency under the frozen rule.
- exit: a frozen matched-control experiment determines whether useful action
  values can be estimated without supplied likelihood tables, or records the
  smallest specific estimation/representation failure before any move to real
  GitLab research.

## Phase 6 -- Controlled active software and GitLab authorization research

- status: planned
- goal: test chosen inspections, executions, tests, or fuzzing interventions in
  controlled authorization software, then progress toward real GitLab
  authorization-vulnerability investigation if evidence justifies it.
- boundary: cross-substrate environments, SERT, and learned graph policies remain
  dormant until a concrete uncertainty requires them; remote sensing is not a
  scheduled phase.
- exit: intentionally coarse; no implementation commitment.
