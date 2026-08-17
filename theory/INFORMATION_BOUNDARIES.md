# Information boundaries

## Purpose

This document is the authoritative Phase 2 disclosure design for the minimal
epistemic control problem. It defines who may know what and which flows are
prohibited. It specifies semantics for future enforcement; no runtime firewall is
implemented.

The controlling rule is:

> Information may affect a normal policy only after the experiment specification
> authorizes a channel and the environment or executor releases a provenance-
> bearing observation or public action result through that channel.

Possession by the environment, evaluator, experiment runner, filesystem, or
trace system is not policy authorization.

## Information classes

Every episode artifact or field belongs to one of these access classes:

| Class | Meaning | Normal policy access |
| --- | --- | --- |
| `public_episode` | initial observations, public metadata, action interface, submitted actions, public action results, remaining budget | direct |
| `controller_private` | epistemic state, policy memory, controller-authored hypotheses, private internal-computation products | only the owning controller/update package |
| `environment_private` | latent state, unreleased observations, hidden dynamics, secret legality constraints, environment seeds/snapshots | never direct |
| `evaluator_only` | gold labels, oracle actions/values, counterfactual outcomes, scoring keys, restricted trace annotations | never |
| `runner_control` | manifests, access policy, budgets, seeds, truncation/safety rules, component routing configuration | only fields explicitly projected into the public episode view |
| `restricted_trace` | hidden snapshots, gold attachments, evaluator diagnostics, secret replay material | never during normal policy execution |

Classification is field-level when a record mixes public and restricted data.
Marking a container public does not make every nested field public.

## Role visibility matrix

`yes` means the role may access the class to perform its declared function. It
does not authorize forwarding it.

| Information | Environment | Controller / policy | StateUpdater | Evaluator | Runner | Trace / replay |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| latent `W_t` | yes | no | no | as required | reference/control only | restricted only |
| initial/public observations | emits | yes | yes | yes | routes | public trace |
| current action interface `D_t` | emits | yes | yes if updater needs public context | yes | routes | public trace |
| remaining raw budget `b_t` | may validate | yes | yes if declared | yes | owns/enforces | public trace |
| controller epistemic state `B_t` | no | yes | yes | reference/snapshot only if protocol permits | opaque reference only | public hash or restricted snapshot |
| policy-private memory | no | yes | only if same declared package | only if protocol explicitly audits it | opaque reference only | restricted or hashed |
| submitted action | yes | yes | yes | yes | routes | public trace |
| public `ActionResult` | emits | yes | yes | yes | routes | public trace |
| environment-private result fields | yes | no | no | as required | routes without projecting | restricted trace |
| gold labels / oracle values | possibly encoded in world | no | no | yes | only to route evaluation | restricted trace |
| vector outcome | no normal need | no during episode | no | creates | records after episode | outcome record |
| seeds/manifests | environment seed as needed | only declared public subset | only declared public subset | as required | yes | restricted plus releasable manifest |

The environment must not receive `B_t`. An action payload may deliberately cite
controller-visible observations or hypotheses, but that is a selected request,
not wholesale disclosure of controller state.

## Authorized flows

The normal episode data path is:

```text
runner configuration
  -> environment reset
  -> public initial interface
  -> controller/updater
  -> submitted action
  -> authorized executor/environment
  -> visibility-split ActionResult
  -> controller/updater and trace
  -> evaluator after/during evaluation through a separate restricted view
```

Internal epistemic actions use controller-visible inputs and a declared executor.
They may return derived observations or private state products with derivation
provenance. They do not gain environment-private or evaluator-only access merely
because they are called "reasoning."

An evaluator may operate online for safety or termination, but its decisions
must travel only through a declared runner-control channel such as `truncate`.
They may not add semantic hints to observations, action descriptors, error text,
cost estimates, or ordering.

## Prohibited leakage paths

The following invalidate an ordinary policy run unless the experiment explicitly
defines and labels a different access condition:

1. Passing `W_t`, a world-state object, hidden-state identifier, or a reversible
   reference to the controller or updater.
2. Adding gold labels, answers, oracle values, evaluator scores, counterfactual
   outcomes, or target-derived features to `B_t`, `D_t`, observations, action
   results, prompts, tool responses, filenames, or logs visible during choice.
3. Letting the evaluator reorder, filter, name, or describe actions according to
   hidden utility while presenting the result as environment legality.
4. Letting the environment inspect private hypotheses or confidence in order to
   expose actions tailored to what is epistemically best.
5. Reusing runner, evaluator, or trace objects in policy code when their type or
   reference permits restricted-field access.
6. Returning secret values in exception messages, debug output, timing channels,
   cache keys, counts, schemas, or metadata.
7. Computing a controller-visible cost estimate or scope label from hidden ground
   truth unless that computation is part of the declared environment observation
   model.
8. Giving a normal policy oracle-policy caches, optimal actions, regret values,
   or seeds that reveal the latent state.
9. Treating prior solution artifacts as neutral observations without an explicit
   access-condition decision and leakage audit.
10. Joining public and restricted trace tables on identifiers available to the
    policy during an episode.

A harmless-looking identifier can leak as much as a payload. Visibility review
therefore covers names, ordering, cardinalities, hashes, paths, timestamps, and
error behavior.

## Role-specific obligations

### Environment

The environment owns `W_t`, releases initial observations, describes legal
actions/capabilities, executes domain transitions, and reports public results. It
may use latent state to decide physical legality or produce observations, but the
public descriptor must expose only intended information. It does not know which
legal action is epistemically best and never consumes SER-specific belief state.

### Controller / policy

The controller sees only the public decision context plus its own private state
and declared priors. A policy may ignore any part of this context. It must submit
actions through the declared interface; filesystem or service access outside an
action capability is undeclared information access.

### StateUpdater (state updater)

The updater has the same information entitlement as its controller package. It
may transform public history and controller-private state, but it cannot query
the environment, evaluator, or trace-restricted view unless that query is itself
a legal action whose result is released publicly.

### Evaluator

The evaluator may inspect hidden state, gold labels, complete traces,
counterfactuals, oracle policies, and domain scoring material as declared. It
produces `Outcome`; it does not coach the policy. If evaluator feedback becomes
part of a continuing task, the environment must issue it as a new observation
under a separately named access condition.

### Runner (experiment runner)

The runner instantiates versions, access policies, seeds, budgets, and safety
rules; routes already authorized views; records events; truncates when required;
and invokes evaluation. It does not select actions, repair policy decisions,
silently retry failures, enrich observations, or pass a shared privileged object
to policy code.

### Trace / replay system

The trace system records public and restricted fields in visibility-separated
views. Replay may use restricted state internally while presenting exactly the
original public view. Export, debugging, and training-data preparation require
their own projection rules. Sanitization cannot be assumed merely because a
trace is labeled public.

## Oracle policies

An oracle policy is an evaluator/reference instrument, not a normal policy with
better implementation. It receives a separately declared oracle view, runs in a
separate access class, and produces a labeled upper bound, optimal action, or
regret reference. Its state, caches, traces, and outputs cannot be reused by
normal policies within the same evaluation condition.

For MicroGym, the evaluator may compute an optimal policy directly from the
known model. The normal random, fixed, greedy, or SER policy still receives only
public observations, legal capabilities, and budget.

## Domain leakage examples

### MicroGym

- Hidden cause/hypothesis IDs cannot appear in observation IDs, test order,
  action costs, RNG seeds, filenames, or failure patterns unless deliberately
  part of the observation model.
- An oracle's next action and sufficient-evidence stopping point are evaluator-
  only. They may be used to score regret after the normal policy acts.
- A precomputed observation table must expose only the row selected by an
  executed action, not the hidden-state index or unused rows.

### IDS to CVE

- Target CVE, qrels, gold mappings, evaluator-only candidate membership, and
  target-aware construction fields are never controller-visible.
- Rule names, file paths, identifiers, ordering, corpus cardinality, descriptions,
  and structured fields must be audited for answer leakage.
- Prior rankers, prompts, predicted-product outputs, comparators, APF/AQB/CDA
  artifacts, and solution-derived neighborhoods are not observations by default.
- The candidate universe and eligibility corrections belong to the environment
  and evaluator specification. The controller receives only the explicitly
  frozen public view for its named access condition.
- Evaluation scores, ranks, and gold-hit diagnostics become available only after
  the policy has stopped or been truncated.

### Active software investigation

- Oracle vulnerability labels, seeded bug locations, hidden tests, exploit
  checks, and reference patches remain evaluator-only.
- Source and runtime evidence become visible only through declared actions such
  as file inspection, tracing, execution, or testing. A repository existing on
  the runner machine does not grant the controller ambient read access.
- Crash, HTTP 500, timeout, sanitizer report, or test failure is an observation,
  not automatically a validated vulnerability outcome.
- Error messages and coverage reports must not include hidden-test names or bug
  annotations unless the environment deliberately exposes them.

### Remote-sensing pressure test

- The true physical state, withheld labels, future frames, and evaluator fusion
  products remain hidden.
- Sensor observations carry acquisition/release time and domain reliability
  metadata when required; future observations cannot leak through cache names or
  action availability before their release time.
- Weather context or another modality is visible only after a declared retrieval
  or sensor action. Spatial/temporal Scope metadata is not a hidden-truth label.

## Information-boundary invariants

1. Policy visibility is determined by explicit projection, never by co-location
   in memory, a process, a file, or a record.
2. `B_t` and updater inputs are subsets or transforms of entitled information;
   they cannot expand entitlement.
3. Evaluator-only data has no path into policy-visible observations, action
   descriptors, results, errors, ordering, timing, or metadata.
4. Environment legality may use hidden constraints but cannot encode hidden
   epistemic utility as action recommendation.
5. Oracle and normal policy access classes are non-interchangeable.
6. Public traces are projections, not unrestricted copies with fields removed by
   convention.
7. Every release identifies its access condition and provenance.
8. A run with an undeclared or ambiguous privileged flow is invalid, even if the
   result appears unfavorable to the policy.

## Audit questions for future implementations

- Can the policy reach a privileged object through references, helpers, caches,
  exception objects, serialization, or ambient filesystem/network access?
- Can identifiers, order, length, timing, or missingness reveal hidden truth?
- Does action generation reflect legality/capability or evaluator judgment?
- Are controller and evaluator imports, processes, stores, and trace projections
  separable enough to test the claimed boundary?
- Can replay reconstruct exactly the public view without revealing the
  restricted view?
- Are oracle results and development diagnostics erased from normal-policy
  caches before evaluation?
- Does every transformed observation retain lineage to authorized inputs?

Passing these questions is engineering evidence about a firewall implementation,
not evidence that a SER policy improves reasoning.
