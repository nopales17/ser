# Minimal epistemic control problem

## Status and purpose

This document is the authoritative Phase 2 specification of the problem SER is
intended to study. It specifies semantic roles and information boundaries, not a
runtime API, controller design, state representation, reward function, or claim
of empirical value. Machine-readable contract summaries live in
`theory/CONTRACTS.yaml`; disclosure rules live in
`theory/INFORMATION_BOUNDARIES.md`; four pressure-test instantiations live in
`theory/DOMAIN_INSTANTIATIONS.md`.

The problem is:

> Given partial, legitimately acquired information about an environment and a
> constrained vector of epistemic resources, choose a sequence of information-
> relevant actions and a stopping point so as to produce useful decisions under
> evaluator-defined criteria.

The formulation is deliberately policy-neutral. It must admit random, fixed,
exhaustive, greedy, oracle-reference, learned, LLM-based, and future SER policies
without requiring any of them to use explicit hypotheses, a graph, coupling
operators, expected information gain, or a common evidence ontology.

## Formal episode

An episode has a latent world state `W_t`, a public interaction history `H_t`, a
controller-owned epistemic state `B_t`, a current action interface `D_t`, a
remaining resource budget `b_t`, and evaluator-owned outcome state `Y_t`.

- `W_t` is owned by the environment and is never a normal policy input.
- `H_t` contains only information legitimately released to the controller:
  initial observations and prior submitted actions and public action results.
- `B_t` is the policy-visible decision state derived from entitled information.
  It may equal `H_t`, summarize it, or use a completely different private
  representation.
- `D_t` describes legal concrete actions and/or legal action-generating
  capabilities. It describes possibility, not epistemic merit.
- `b_t` is the remaining raw resource budget under the episode's declared
  resource schema.
- `Y_t` denotes evaluator-only truth, labels, metrics, or oracle information. It
  may overlap with facts encoded in `W_t`, but it is a separate access role.

A normal policy acts only on a decision context to which it is entitled:

```text
a_t ~ pi(B_t, D_t, b_t; m_t)
```

where `m_t` is declared policy-private memory, if any. Logically, policy-private
memory is part of the controller's epistemic state even when an implementation
stores it separately.

An authorized executor validates and attempts the action. For an environment
action, the transition may be written:

```text
(W_{t+1}, r_t, D_{t+1}) ~ E(W_t, a_t, H_t, b_t, xi_t)
```

where `r_t` is an `ActionResult`, `xi_t` represents declared stochasticity or
exogenous evolution, and `D_{t+1}` is the next public action interface. Static
worlds are the special case in which the latent state does not change. Internal
epistemic computation is representable as an action whose authorized executor
consumes controller-visible inputs. It has no deliberate world effect; in a
static environment its world transition is the identity, while exogenous time-
dependent evolution may still occur. The environment does not receive `B_t`
merely to support internal reasoning.

The controller-side updater then integrates the public result:

```text
B_{t+1} = U(B_t, a_t, r_t)
```

`U` may append raw history, apply a deterministic transform, invoke a declared
stochastic inference procedure, or be absorbed inside a policy implementation.
Its semantic separation from `pi` allows later comparisons of state/update
methods independently of action-selection methods. It is never part of the
environment contract.

The evaluator computes an `Outcome` from an evaluation view that may include
hidden state and restricted trace fields:

```text
Outcome = V(W_{0:T}, Y_{0:T}, Trace_{0:T}, experiment_spec)
```

An outcome is not returned by ordinary action execution and is not made policy-
visible unless a continuing environment deliberately converts some feedback
into a new, provenance-bearing observation.

## World state

`WorldState` means whatever can be true in the environment independently of what
the controller has observed or believes. It may include hidden causes, ground
truth, objects, programs, mutable services, unobserved evidence, clocks, or
exogenous processes.

Required semantics are intentionally small:

1. The environment can distinguish the world states needed to execute its own
   transitions and evaluation hooks.
2. The world may be static, action-dependent, exogenously dynamic, stochastic,
   or some combination.
3. A normal policy cannot inspect or receive `W_t` directly.
4. The core does not require a universal serializable world schema. Replay may
   use seeds, event logs, snapshots, environment-specific state references, or
   checksums according to the environment's declared reproducibility contract.

Hidden target CVEs, hidden MicroGym causes, actual program behavior, and actual
physical conditions are examples of world facts. Their commonality is access
semantics, not data representation.

## Observations and public history

An `Observation` is information legitimately released to the controller by the
episode's initial interface or by an authorized action result. Payloads may be
textual, numeric, structured, binary, multimodal, delayed, noisy, contradictory,
partial, or derived. An action may successfully execute and release no useful
observation; an observation may report that an attempted measurement failed.

Every externally acquired observation requires:

- a stable identity within the episode;
- a domain-typed or opaque payload;
- release provenance identifying the initial interface or source action result;
- the episode step or event at which it became policy-visible.

Optional, environment-owned semantics include acquisition time distinct from
release time, measurement/reliability metadata, derivation lineage, and typed
scope. Absence of reliability metadata means "not supplied," not "perfectly
reliable." Scope is not required on every observation.

`H_t` is an ordered record of policy-visible episode events, not a claim that a
policy must retain raw history. Failed actions and empty/noisy observations stay
in public history because their occurrence and cost can affect later decisions.
Evaluator-only attachments are not part of `H_t`.

## Epistemic state

`EpistemicState` (`B_t`) is the information a controller implementation is
entitled to use when selecting its next action. It is not the world state and is
not required to be a calibrated belief distribution. It may be as small as a
step counter, as direct as the complete public history, or as structured as a
set of observations, hypotheses, unknowns, summaries, and relations.

Every implementation of `B_t` must satisfy these invariants:

1. **Entitlement:** it is derived only from public episode inputs, policy-
   declared priors/configuration, and the controller's own authorized internal
   computation.
2. **No hidden-state alias:** it cannot contain a reference or decoding path to
   `W_t` or evaluator-only data unless that information was deliberately released
   as an observation under the experiment specification.
3. **Update accountability:** the update rule or policy package is identified;
   stochastic updates declare their randomness source.
4. **Auditability:** a trace can associate a decision with a state version,
   snapshot reference, checksum, or sufficient public history. Full state
   serialization is not universally required.
5. **Representation independence:** the environment does not interpret, mutate,
   or require the internal representation.
6. **Baseline compatibility:** a policy can operate with no explicit hypothesis,
   uncertainty model, graph, scope algebra, or semantic coupling machinery.

Epistemic state is a semantic contract; graph state is one possible future
implementation.

## Observation, hypothesis, and the rejected universal unit

Phase 2 chooses the smallest of the three considered ontology alternatives:

- **Alternative A — chosen:** `Observation` and optional `Hypothesis` remain
  separate concepts with no required semantic supertype.
- **Alternative B — deferred:** a common `EpistemicObject` envelope might later
  reduce duplicated infrastructure fields, but identity, provenance, visibility,
  and scope do not currently have identical semantics for observations and
  controller-authored claims.
- **Alternative C — rejected from the minimal core:** making everything an
  `EpistemicUnit` adds an ontology without enabling any required Phase 3 action,
  transition, baseline, or measurement.

Infrastructure records may use common identifiers and reference conventions.
That implementation convenience is not a universal epistemic ontology.

A `Hypothesis`, when a controller chooses to maintain one, is a controller-
authored proposition that could affect future action or stopping choices. A
trace-visible hypothesis minimally needs a stable identity, a proposition in a
controller-defined representation, and creation/derivation provenance. Scope,
lifecycle status, qualitative or quantitative confidence, and evidence links are
optional. Confidence is not required to be probabilistic. The environment never
requires hypotheses, and a random or fixed policy remains valid without them.

## Action and action interface

An `Action` is a controller choice submitted to a declared executor. The common
envelope requires:

- an episode-unique action identity;
- an environment- or capability-defined action schema/kind identifier;
- a payload containing the schema-specific declared parameters.

Optional metadata includes target references, typed scope, and an analytic mode
such as `external_acquisition`, `internal_computation`, or `mixed`. The analytic
mode exists only to support later trajectory analysis; it neither prescribes a
policy nor forces every action into a perfectly clean binary. Retrieval, tool-
assisted reasoning, and active tests may be mixed.

Names such as observe, retrieve, transform, hypothesize, compare, test, deepen,
broaden, revise, and abandon are descriptive categories, not a universal enum.
Domain actions such as `run_input(x)`, `inspect_file(path)`, `purchase_test(B)`,
or `inspect_band(region, band)` retain their own payload schemas.

An action is epistemic in this problem when its selection is relevant to what
information becomes available, how entitled information is transformed for a
decision, or when the controller commits, abstains, or stops. It need not reveal
useful evidence, and it may also change the world.

`ActionInterface` (`D_t`) communicates legal possibility without choosing on the
controller's behalf. It may contain a finite set of concrete action descriptors,
generative action schemas/capabilities plus validators, or both. This permits
unbounded query strings, fuzz inputs, paths, spatial regions, and other actions
that cannot be enumerated.

Legality may depend on latent safety constraints, public episode history,
remaining budget, earlier actions, environment state, and declared capabilities.
The descriptor exposed to the controller must reveal only intended information.
Legality must not depend on the controller's private `B_t`, and the environment
must not rank actions by which is epistemically best. Policy utility and
environment legality are separate.

## Action result

`ActionResult` records what happened when an action was validated or attempted.
It minimally contains:

- the source action identity;
- execution status, including rejection, failure, partial completion, or
  completion;
- the actual `ResourceVector` charged, including cost incurred by failure;
- zero or more released observations;
- public termination or continuation information produced by the executor.

Optional fields include timing, executor/version references, domain metadata,
error details safe for policy visibility, and restricted evaluator attachments.
The result may reflect a world change without revealing the hidden new state.

An HTTP 500 after `run_input(x)` and twenty records returned by a retrieval are
action results. Neither is automatically a vulnerability discovery or a correct
CVE identification. Those are evaluator judgments represented in `Outcome`.

## Transition and trace

A `Transition` is an immutable semantic record of one decision step. It links:

```text
state-reference B_t
  -> action a_t
  -> action result r_t
  -> state-reference B_{t+1}
```

and records step identity, budget before/after, actual resource vector, relevant
component versions, randomness references, and any termination event. State
references may be full snapshots, content hashes, opaque trace references, or a
reconstruction recipe; the core does not require full before/after state copies.

An episode `Trace` is an append-only ordered collection of initial-interface and
transition records with visibility labels. It must preserve rejected, failed,
partial, invalid, truncated, and successful events. The trace semantics must
support evaluation, resource accounting, debugging, ablation, and, when the
environment declares sufficient replay support, deterministic or statistically
equivalent replay. A trace is not automatically suitable SERT training data.

Manifests identify the versions and content hashes of the environment,
experiment specification, policy/update package, action schemas, evaluator,
resource schema, seeds, and referenced artifacts. Replay claims must state which
parts are exact, seeded, externally unavailable, or nondeterministic.

## Resource vectors and budgets

An episode declares a `ResourceSchema`: named resource dimensions, units, and
aggregation rules. A `ResourceVector` maps applicable dimensions to nonnegative
quantities. Examples include model input/output tokens, compute, money,
wall-clock latency, tool calls, retrievals, environment interactions, program
executions, and sensor acquisitions.

Semantics are:

1. Within a declared schema, an omitted dimension in a particular action cost is
   zero for that action.
2. A dimension absent from the episode schema is **unmeasured or inapplicable**,
   not zero, and must not be used in cross-episode equality claims.
3. Quantities with different units are not added or converted by the core.
4. Cumulative episode cost is componentwise addition under the declared schema.
5. A `Budget` gives upper bounds for a subset of dimensions. Unbounded or merely
   measured dimensions need no bound.
6. The experiment/environment declares a feasibility rule for actions whose
   actual cost is uncertain. Estimates, reservations, or maximum costs may be
   exposed, but actual costs are always recorded. Overrun, if possible, becomes
   a recorded violation or evaluator truncation rather than disappearing.

Experiments may preregister a scalarization such as `w^T C`, lexicographic
constraints, or Pareto analysis. Raw dimensions remain in the trace and outcome.
There is no universal scalar cost, reward, latency conversion, or risk calculus.

## Stopping and termination

`STOP` is a first-class controller action and is legal whenever the episode
specification permits controller termination. Its domain-defined submission may
contain an answer/decision or an explicit abstention. Confidence, rationale, and
remaining-uncertainty reports are optional and must not be fabricated by policies
that do not maintain them.

Three termination causes are distinct:

- **Controller stop:** a policy selected `STOP`; the trace contains its optional
  submission and actual cost.
- **Environment termination:** continuation became impossible or meaningless
  because of world/environment semantics, such as a crashed service or expired
  observation window.
- **Evaluator/runner truncation:** an experiment rule, budget, safety limit, or
  time limit ended the episode without treating the event as a controller stop.

An episode may record multiple contributing conditions, but one primary cause is
required for analysis. This permits measurement of premature stopping, wasteful
continuation, abstention quality, and stopping regret without conflation.

## Outcome and evaluator

`Outcome` is an evaluator-owned, vector-valued assessment of a completed or
truncated episode. It may report correctness, rank, task utility, validation
status, abstention quality, regret, safety violations, constraint violations,
coverage, termination classification, and raw cumulative resources. Each metric
declares its direction, units or scale, validity conditions, and required
evaluator information.

No universal scalar reward is required. An experiment may preregister a summary
or comparison rule while retaining component metrics. Outcome computation may
inspect hidden state, oracle policies, gold answers, and restricted trace data;
these remain outside the normal policy channel.

## Environment, policy, updater, and runner roles

The conceptual `Environment` owns latent state, initial observation release,
legal action/capability descriptions, action validation/execution for its domain,
world evolution, environment termination, and replay declarations. It does not
receive or interpret `B_t`, optimize epistemic utility, or require SER-specific
state machinery.

The `Policy` receives `B_t`, `D_t`, `b_t`, and declared public episode metadata.
It returns a legal action or `STOP`. A policy may maintain declared private
memory, but that memory receives no additional information entitlement. A
special oracle-reference policy may receive hidden state only in a separately
declared evaluator channel; its access class and results must never be confused
with an admissible normal policy.

The `StateUpdater` is a separable controller-side role. Phase 3 may implement a
trivial append-history updater so policies can be compared. Rich update or
inference mechanisms are optional and deferred. The environment never depends on
them.

The `ExperimentRunner` freezes versions, creates episodes, routes only authorized
views, enforces budgets/truncation and access classes, records manifests and
traces, and invokes evaluation. It must not choose actions, add evaluator-derived
hints, or silently repair invalid policy outputs.

Detailed role visibility and prohibited flows are canonical in
`theory/INFORMATION_BOUNDARIES.md`.

## Scope decision

Scope is an **optional typed capability**, not a mandatory universal coordinate
system. Its minimal meaning is:

> Scope metadata describes the claimed applicability or support domain of an
> observation, hypothesis, action, or relation under a domain-owned scope type.

An environment or controller that uses scope declares the scope type, payload
semantics, and any operations it supports. `compatible`, `intersection`, or
`contains` are not core operations; a domain algebra may provide them when its
experiment requires those questions. Code, temporal, spatial, candidate, and
experimental scopes need not share coordinates or algebra.

The minimum core permits opaque scope attachments and scope-bearing action
parameters. It does not require Scope for the first MicroGym, but Phase 3 needs a
separate locality/gating environment before `H-003` can be tested. Hierarchical
boundary movement can be represented by domain actions whose targets or scopes
move across a declared hierarchy; no hierarchy machinery belongs in the core.

## Signal decision

`Signal` is deferred and is not an accepted Phase 2 semantic role. Its deferred
record is `C-021`, linked to `P-009`. Every proposed role is already covered by
an observation, an action result, derived controller state, a hypothesis/evidence
relation, or reliability metadata. Introducing Signal now would create a second
evidence carrier without a distinct invariant or Phase 3 requirement. A future
proposal may revive it only by identifying behavior that cannot be expressed
cleanly by those existing contracts.

## Coupling-operator classification

No coupling operator is required for Phase 3 or for the formal problem.

| Operator | Possible future role | Phase 2 decision |
| --- | --- | --- |
| `RES` | ambiguous resolution or resonance state update | defer; semantics and necessity unknown |
| `GATE` | policy routing/eligibility heuristic | defer; environment legality and policy preference must remain distinct |
| `AMP` | state-update or scoring transform | defer; potentially redundant with controller-specific update logic |
| `DAMP` | state-update or scoring transform | defer; potentially redundant with controller-specific update logic |
| `INHIBIT` | state-update or policy suppression | defer; potentially redundant and no algebra exists |
| `SCOPE_FILTER` | policy-side scope gating | defer; must not be confused with environment legality or typed scope algebra |
| `TOPK` | policy selection or state compression heuristic | defer; ordinary policy logic, not a core operation |
| `DEFEAT` | optional hypothesis relation/update | defer; hypotheses themselves are optional |
| `PROMOTE` | controller-specific lifecycle or routing change | defer; ambiguous and unrelated to concept maturity |

## Dynamics, action modes, and boundary movement

Exogenous world change is represented by the environment transition and its
time/event inputs even when the controller takes no externally informative
action. A `WAIT`-like domain action may advance time, and environments may also
advance time during internal computation or latency. Observation acquisition
and world time are therefore distinct fields when a domain needs them.

Optional action-mode metadata makes later measurement of external-acquisition
versus internal-computation switching possible. Oscillation rate and depth are
trace-derived measurements, not architectural schedules. Mixed actions remain
mixed instead of being forced into a false binary.

Likewise, boundary selection is permitted through typed action targets and
optional Scope capabilities. Function-to-module or pixel-to-region movement is
domain structure. The core neither assumes a hierarchy nor prevents one.

## Formal invariants

The following are accepted Phase 2 architectural invariants:

1. A normal policy cannot access hidden world state except through a legitimate
   observation deliberately released under the episode specification.
2. Evaluator-only information cannot affect policy-visible state, action
   interfaces, action results, or updater inputs.
3. Every externally acquired observation has release provenance.
4. Every attempted or rejected action records actual cost under the declared
   resource schema, including a zero vector when execution truly costs nothing.
5. Episode traces preserve failures, invalid actions, partial results,
   truncations, and successes.
6. Controller `STOP`, environment termination, and evaluator/runner truncation
   remain distinguishable.
7. `Outcome` is not `ActionResult`.
8. Environment contracts do not depend on SER-specific policy or epistemic-state
   internals.
9. Raw resource dimensions are preserved before optional experiment-specific
   scalarization.
10. Baseline policies can operate without explicit hypotheses, graphs, scope,
    confidence, Signal, or coupling operators.
11. Action legality describes what may be attempted, never which legal action is
    epistemically best.
12. Oracle access is a separately labeled evaluation access class and cannot be
    inherited by normal policies.

These constraints are necessary to interpret comparisons. They do not claim
that structured state, scope-aware gating, or any future SER policy is useful.

## Evaluation questions and falsifiable comparisons

Phase 3 and later experiments must preserve vector outcomes and resource use.
Efficiency is therefore a comparison relation or Pareto surface until an
experiment preregisters a scalarization. A controller cannot claim efficiency by
improving an uncosted dimension or silently omitting a resource dimension.

Where a synthetic environment supplies an optimal policy, report decision
regret, componentwise excess resource use, and terminal-quality difference.
Stopping analysis should distinguish stopping before additional evidence would
change the optimal terminal decision from spending after the evaluator can show
that sufficient evidence was already available. The latter requires evaluator-
only counterfactual knowledge and must not become a policy hint.

Semantic gating must be compared with fixed order, random, cheap-first,
exhaustive, matched-budget greedy, and any relevant oracle policy. Experiments
must remove or counterbalance action order, cost, identifier, and formatting
cues so a policy cannot look semantic by following shortcuts.

Cross-environment generality requires preregistered success under the same core
contracts in structurally different environments, with environment-specific
adapters and metrics stated openly. A shared API or successful IDS result is not
evidence of transfer.

## Phase 3 requirements

MicroGym may be implemented only after this specification. Its first version
must provide:

- at least one finite hidden-state environment with known observation models;
- initial observations, legal test actions, generative capability support where
  useful, explicit `STOP`, and all three termination categories;
- declared resource dimensions/units, per-action actual cost, componentwise
  budgets, and vector outcomes;
- deterministic seeded execution and immutable, complete transition traces;
- a trivial history-based state updater so no hypothesis ontology is required;
- fixed, random, exhaustive, cheap-first/greedy, and oracle-reference policies
  with explicit access classes and meaningful budget matching;
- evaluator-computable decision regret and stopping/waste analyses where the
  environment permits them;
- failure, noisy-observation, abstention, and budget-truncation cases;
- a separate locality/scope variant before testing `H-003`, including shortcut
  controls that distinguish semantic relevance from order and cost heuristics.

MicroGym must not initially require an LLM, graph, learned policy, coupling
operator, universal confidence calculus, compressor, or IDS artifact.

## Adversarial pressure test

| Challenge | Representation in this specification | Remaining limitation |
| --- | --- | --- |
| No explicit hypotheses | `B_t` may be raw public history or any opaque state | whether hypotheses help is empirical |
| Random policy | `pi` may ignore `B_t` and sample from `D_t` | sampling over generative actions is environment-specific |
| Oracle policy without leakage | separately labeled oracle access class | only suitable when evaluator can define an oracle |
| Failed action | failure/rejection is an `ActionResult` with cost and trace | error payload visibility remains domain-owned |
| Noisy or contradictory observation | observation payload plus optional measurement metadata | no universal noise model |
| Independent world change | exogenous `xi_t`, time, and environment transitions | replay strength varies by environment |
| Infinite/generative actions | action schemas/capabilities with validators | policy search over payloads is not solved by the contract |
| World-changing but uninformative action | transition can change `W` and release zero observations | evaluator must define safety/utility consequences |
| Costly internal reasoning | authorized internal executor with no deliberate world effect; exogenous dynamics may still advance | exact compute accounting is substrate-specific |
| Action changes world and reveals evidence | one result may record both transition effects and observations | hidden effects remain evaluator/environment-side |
| Abstention | domain-defined `STOP` submission | abstention quality is evaluator-specific |
| Multi-objective evaluation | vector `Outcome` and raw resource vector | experiment comparison rule remains open |
| Different policy states | environment never consumes `B_t` | adapters must avoid incidental serialization coupling |
| Same policy across environments | common decision-context semantics | action payload compatibility still requires adapters |
| Remote-sensing dynamics | time, latency, typed scope, noise, exogenous change | sensor geometry and uncertainty remain domain-specific |

The formalism survives these cases without a domain-specific change to the core.
It deliberately leaves policy construction and domain semantics unsolved.

## Explicitly Deferred

- universal epistemic-unit or epistemic-object ontology;
- first-class `Signal`;
- mandatory explicit hypotheses;
- graph representation and epistemic graph runtime;
- coupling-law implementation and all nine named operators;
- universal confidence or uncertainty calculus;
- universal information-gain or Shannon-entropy objective;
- universal scalar cost or reward;
- universal scope coordinate system or algebra;
- semantic compressor and long-term memory architecture;
- learned routing, SERT, TGNN, and cross-domain learned policy;
- LLM integrations, prompts, and model clients;
- production SER/controller frameworks and any implementation beyond the
  roadmap-authorized minimal zero-LLM MicroGym;
- IDS adapters, prior IDS solution logic, and data import;
- fuzzing engines and active software tooling;
- remote-sensing adapters and sensor integrations;
- SERT dataset/training-record design.

## Exit-criteria answers

1. Hidden world facts live in `W_t`; normal policies never receive it.
2. A legitimate observation is an initial or action-result release with identity,
   payload, provenance, and release step.
3. `B_t` is entitled controller-side decision state, not hidden truth.
4. Hypotheses are optional.
5. A controller chooses typed domain actions or `STOP`.
6. The environment declares legality/capabilities; the controller chooses among
   legal possibilities.
7. Action interfaces may be generative rather than enumerated.
8. `ActionResult` reports execution status, actual costs, observations, and
   public execution metadata.
9. `Outcome` is a restricted evaluator judgment; it is not an action result.
10. Immutable transitions link state references, action, result, costs, budgets,
    versions, and termination.
11. Costs are raw typed vectors under an episode resource schema.
12. Budgets constrain declared dimensions through an episode feasibility rule;
    actual costs and overruns remain recorded.
13. Scope is optional typed applicability/support metadata with domain-owned
    semantics.
14. Signal is not required and is deferred.
15. No coupling operator is required.
16. `STOP` is a controller action carrying a domain submission or abstention.
17. STOP, environment termination, and runner/evaluator truncation are distinct.
18. The environment and evaluator may know ground truth under separate roles.
19. The information firewall and visibility-labeled traces isolate evaluator
    data.
20. Environment transitions include action-driven and exogenous change.
21. Active actions may change the world and release new observations.
22. Internal actions may consume declared resources under identity world
    transitions.
23. The four domain cases use the same contracts; see
    `theory/DOMAIN_INSTANTIATIONS.md`.
24. Baselines may use raw history and no SER-specific state machinery.
25. Deferred concepts are listed above and in `theory/CONTRACTS.yaml`.

## What is SER controlling?

SER would control the **selection, targeting, timing, and stopping of
resource-consuming epistemic actions over a partially observed episode**. The
controlled process is allocation across possible ways of acquiring or
transforming decision-relevant information, not tokens, an LLM, a graph,
hypotheses, or CVE retrieval.

What makes an action epistemic is its role in changing the information available
for a decision, transforming entitled information, or deciding that further
information work should stop. The controller chooses using `B_t`, legal action
capabilities, remaining raw budgets, its declared priors/models, and past public
results—not the hidden world state.

If LLMs are removed, the problem remains a resource-constrained, partially
observed sequential decision problem with actions, observations, state updates,
budgets, stopping, traces, and evaluator-owned vector outcomes.
