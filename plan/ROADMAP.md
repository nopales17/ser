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
- current cursor: Phase 5A.1 construction and Phase 5A.2 freezing are complete;
  Phase 5A overall is not complete. Static Semantic AuthzGym protocol 1.1
  freezes 8 development, 24 primary evaluation, and 24
  paired perturbation episodes; constrained H1-H4 diagnoses; purchased-artifact
  semantic traces; fixed, ReAct-like, explicit-value, and secondary monolithic
  architectures; matched budgets; evaluator truth; failure decomposition; and
  a real-model classifier. Deterministic mock calibration passes all benchmark
  safeguards but is not empirical evidence. The next step is a separately
  frozen run with one selected inexpensive semantic model and no post-evaluation
  prompt, parser, policy, population, budget, or threshold tuning.
- readiness: Phase 5B is not ready. It requires an actual model to extract
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
