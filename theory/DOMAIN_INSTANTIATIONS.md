# Domain instantiations and pressure tests

## Purpose

These conceptual examples instantiate the same contracts from
`theory/CONTROL_PROBLEM.md` and `theory/CONTRACTS.yaml`. They are not runtime
designs, datasets, experiments, or evidence. Domain payloads and evaluators vary;
the information roles, action/result distinction, resource vectors, stopping,
and trace semantics do not.

## Case 1 — Minimal MicroGym

### Episode definition

The latent world contains one hidden cause `H*` in `{H1, H2, H3}`. The controller
receives a neutral initial observation stating the admissible answers and a
budget of `4 test_units`. The environment exposes tests:

| Action | Actual cost | Observation behavior |
| --- | ---: | --- |
| `purchase_test(A)` | `{test_units: 1}` | separates `H1` from `{H2,H3}` but cannot distinguish `H2` from `H3` |
| `purchase_test(B)` | `{test_units: 2}` | strongly separates `H3` from `{H1,H2}` with declared 10% noise |
| `purchase_test(C)` | `{test_units: 8}` | nearly reveals the cause but is illegal under this budget |
| `STOP(submission)` | `{test_units: 0}` | controller answer or abstention; no observation |

The evaluator knows `H*`, the observation model, and an optimal policy. Normal
policies know the test descriptions, costs, public observations, and remaining
budget but not `H*` or the oracle's next action.

### Complete hypothetical trajectory

Assume `W_0.hidden_cause = H3`.

1. `reset` releases observation `o-000`: the three admissible answers, test
   capability schemas, resource schema `{test_units}`, and budget `4`.
   `B_0` for a simple baseline is just this public history.
2. The policy chooses `a-001 = purchase_test(A)`. The environment validates it.
   Result `r-001` is `completed`, costs `{test_units: 1}`, and releases `o-001 =
   not_H1`. The world remains static. Remaining budget is `3`.
3. The updater appends `a-001/r-001/o-001`, producing `B_1`. No explicit
   hypothesis object is required.
4. The policy chooses `a-002 = purchase_test(B)`. Result `r-002` is `completed`,
   costs `{test_units: 2}`, and releases noisy observation `o-002 = supports_H3`
   with the test's declared reliability metadata. Remaining budget is `1`.
5. The updater produces `B_2`. The policy chooses
   `STOP({answer: H3})`. Result `r-003` records controller termination and zero
   test cost. Total cost is `{test_units: 3}`.
6. Only after termination, the evaluator compares the answer to hidden `H3`,
   computes correctness, total raw cost, decision regret against its oracle, and
   whether the policy continued beyond the oracle's sufficient-evidence point.

The trace stores state references, actions, results, costs, observations, budget
changes, seed/model versions, and controller-stop cause. It does not place the
hidden cause or oracle action in the public trace view.

### What this case tests

The contracts represent finite hidden state, noisy tests, budget-constrained
legality, a history-only policy, first-class STOP, an illegal expensive action,
oracle-reference regret, and vector outcome without an LLM or graph. A separate
MicroGym variant with local relevance and misleading order/cost cues is required
before testing scope-aware semantic gating.

## Case 2 — IDS to CVE partial-evidence attribution

### Episode mapping

| Contract | IDS instantiation |
| --- | --- |
| `WorldState` | hidden target CVE, complete rule/evidence record, frozen corpus state, and environment-private mappings |
| initial `Observation` | one deliberately selected sanitized rule view plus public task/access metadata |
| `EpistemicState` | controller-chosen history or representation; it need not reproduce vulnerability-shape or candidate-ledger schemas |
| `ActionInterface` | declared retrieval, field inspection, source acquisition, transformation, internal comparison, and STOP capabilities for the named condition |
| `Action` | e.g. `retrieve(query)`, `inspect_record(public_id, field)`, `transform(observation_refs, method)`, or `STOP(answer/abstain)` |
| `ActionResult` | records returned, released field values, failures, actual retrieval/tool/model/latency costs, and provenance |
| `Scope` | optional corpus, record, field, or evidence-support metadata owned by this environment—not product equality by default |
| `Outcome` | evaluator-only correctness/rank/abstention/validity plus resource vector and leakage flags |

The environment may be static even though policy-visible information grows.
In this static case internal reasoning actions have identity world transitions
and declared compute costs. Retrieval and inspection expose only fields
authorized for that action.

### Information separation

The controller never receives target CVE, qrels, hidden mappings, eligibility
labels, target-aware construction fields, evaluator ranks, or oracle actions.
Prior IDS prompts, predicted-product outputs, rankers, comparators, APF/AQB/CDA
artifacts, and solution-derived neighborhoods are not environment observations.
Identifiers, descriptions, ordering, file paths, and corpus cardinalities require
leakage review before release.

The evaluator can use the frozen target mapping and complete trace after STOP.
A retrieval result containing twenty public records is an `ActionResult`; it is
not a correct attribution. `STOP({answer: CVE-X})` is a controller submission;
the match to gold is an `Outcome`.

### Example trajectory sketch

The policy receives a sanitized rule observation, retrieves by a query derived
from entitled content, observes a result set, inspects two allowed fields on one
record, performs a declared internal comparison, and stops with an answer or
abstention. Each step charges its own dimensions. Nothing in the core requires
the historical representation-then-retrieval pipeline, candidate list, product
gate, or vulnerability-shape ontology.

### Pressure-test conclusion

The same contracts cover a closed static environment, but Phase 1 showed that
this archive does not yet establish a meaningful sequential allocation problem
or valid holdout. IDS therefore remains a possible later environment, not the
Phase 3 implementation target and not evidence for the formalism.

## Case 3 — Active software investigation

### Episode definition

Suppose a service intermittently returns an authorization error. Hidden world
state includes the actual implementation, runtime state, configuration, cache
contents, and any real vulnerability. The evaluator seeds or otherwise knows a
reference fault for the conceptual case. The controller initially receives a
bug report and a public repository/service interface, not the hidden label.

The controller may privately entertain hypotheses such as:

- parser inconsistency;
- authorization-state error;
- caching/state discrepancy.

Those hypotheses are optional controller state. The environment never consumes
them.

Available capability schemas may include:

- `inspect_source(path, region)`;
- `trace_call(entrypoint, input)`;
- `run_input(input, session_setup)`;
- `construct_and_run(template, mutation_constraints)`;
- `run_test(test_id)`;
- `retrieve_documentation(query)`;
- `internal_compare(observation_refs)`;
- `STOP({diagnosis|patch_reference|abstain})`.

Paths and input spaces may be generative rather than pre-enumerated. The
environment validates existence, permissions, safety limits, and budgets without
ranking actions by which private hypothesis they would discriminate.

### Evidence-manufacturing trajectory

1. The initial report says two semantically similar requests sometimes receive
   different authorization responses.
2. The controller chooses `inspect_source` for the parser/authorization boundary.
   The result releases a permitted source excerpt and charges one file
   inspection.
3. It chooses an internal comparison action over the report and excerpt. The
   world does not change; the result is a derived observation with lineage and a
   compute charge.
4. It chooses `construct_and_run` with two inputs differing only in normalized
   path encoding. Execution changes runtime/cache state and returns one `200`
   and one `403`, plus latency and execution costs. The controller actively
   manufactured a discriminating observation.
5. It traces the caller under one input. The result may fail or time out; that
   failure and its cost remain in the trace.
6. It stops with a diagnosis or abstains. The evaluator separately validates
   whether the diagnosis identifies the reference fault, whether a proposed
   patch passes hidden tests, whether unsafe actions occurred, and the resources
   consumed.

An HTTP 500, crash, sanitizer message, or coverage increase is evidence, not an
evaluator-owned conclusion that a vulnerability exists.

### Pressure-test conclusion

This case demonstrates active intervention, mixed world-changing/informative
actions, effectively infinite action parameters, failures, costly internal
reasoning, safety constraints, and dynamic runtime state. It uses no change to
the core contracts. A fuzzing engine, source adapter, executor, and vulnerability
oracle remain domain-specific Phase 5 work.

## Case 4 — Remote-sensing generality pressure test

### Conceptual episode

The latent world is a changing physical region with weather, objects, land
state, and sensor conditions. The controller initially receives one delayed,
noisy image-derived observation and public acquisition capabilities. It may:

- inspect another timestamp already available;
- inspect a different spatial region;
- request a different modality or spectral band;
- retrieve weather/context data;
- request greater spatial detail;
- wait for a future acquisition window;
- perform internal comparison/fusion over already released observations;
- stop with a decision or abstention.

World evolution may occur during action latency or internal computation. An
observation may have distinct acquisition and release times. Spatial/temporal
support, resolution, sensor lineage, and uncertainty are domain-specific
observation metadata and optional typed Scope payloads. The core does not need a
universal geometry, sensor model, or scope intersection operation.

### Pressure-test questions and answers

- **Latency:** represented by action cost/result timing while the environment
  transition may advance world time.
- **Changing world:** represented by exogenous transition state `xi_t`; old
  observations remain facts about their acquisition time, not necessarily the
  current world.
- **Spatial/temporal support:** represented by an optional domain Scope type.
- **Sensor uncertainty:** represented by domain measurement metadata, not a
  universal confidence calculus.
- **Future availability:** represented by time-dependent action capability and
  release rules, without leaking future observations.
- **Multimodality:** observation payloads are not assumed to be strings.
- **Waiting:** a legal action can consume time and change the world while
  releasing no immediate observation.

### Pressure-test conclusion

The core model does not break under latency, spatial/temporal support, sensor
uncertainty, or exogenous change. What remains domain-specific is substantial:
geometry, sensor calibration, weather models, acquisition scheduling, fusion,
and outcome labels. This case therefore supports the contract's permissiveness,
not a claim of demonstrated cross-domain generality and not an implementation
target.

## Cross-domain comparison

| Property | MicroGym | IDS to CVE | Software | Remote-sensing pressure test |
| --- | --- | --- | --- | --- |
| hidden world | cause | target/evidence/corpus truth | implementation/runtime/fault | changing physical state |
| active world change | usually no | usually no | yes | wait/acquisition timing may coincide with change |
| generative actions | optional | queries may be open | inputs/paths are open | regions/times may be large |
| noisy observations | configurable | model/retrieval uncertainty | runtime nondeterminism | central |
| optional typed Scope | test/locality variant | corpus/record/evidence | code/runtime boundary | spatial/temporal/modality |
| evaluator-only truth | hidden cause/oracle | qrels/gold | fault/hidden tests | withheld truth/labels |
| STOP | answer/abstain | CVE/abstain | diagnosis/patch/abstain | decision/abstain |
| resource dimensions | tests/time | retrieval/model/tool/time | files/tests/executions/time | acquisitions/latency/money |

The shared object is not an evidence format or solution pipeline. It is the
partially observed, resource-constrained sequence of legal action choices,
results, controller-side updates, and stopping under an evaluator firewall.
