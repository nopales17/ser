# SER charter

## Authority and maturity

This cold document owns the project boundary, invariants, category distinctions,
non-goals, and promotion rules. It changes only after an accepted ADR is appended
to `DECISIONS.md`.

Authority and maturity are orthogonal:

- **Location** answers which source owns a statement.
- **Status** answers how much confidence the project places in a concept.

A `seed` concept may remain permanently in the cold canonical idea map. Cold
storage preserves intellectual history; it does not turn an idea into doctrine.

## Research boundary

SER investigates how an intelligent system might allocate limited epistemic
resources among observation, retrieval, experimentation, hypothesis generation,
hypothesis refinement, comparison, internal reasoning, abandonment, and stopping
to obtain useful decision-relevant uncertainty reduction under constraints.

The accepted problem-level loop is:

`state -> choose epistemic action -> obtain observation/result -> update state -> choose again`

The role separation and sequential control formulation are accepted architectural
framing under `F-002` and ADR-0008 through ADR-0012, not a validated controller.
The provisional policy objective `expected decision-relevant information gain -
cost - latency - risk` remains a working research hypothesis. Exact policy
objectives, state representations, domain action schemas, update algorithms, and
stopping rules remain open.

The research target is substrate-independent. Candidate resources include model
tokens, cheap- or frontier-model computation, retrieval, source inspection,
program execution, tests, active experimentation, sensor observations,
wall-clock time, and money.

`SER` provisionally names a control architecture that selects, targets, times,
and stops resource-consuming epistemic actions while maintaining
controller-entitled state. The name and expansion are not permanent decisions.

## Category invariants

These categories must not collapse:

- **Foundation:** a project framing, methodological constraint, or durable
  boundary used to organize the research.
- **Primitive:** a candidate irreducible concept needed to state a theory, such
  as typed scope or vector resource cost. Rejected candidates remain recorded.
- **Hypothesis:** a falsifiable or sharpenable claim about how primitives relate
  or what effect a mechanism will have.
- **Mechanism:** a proposed operation or architecture intended to realize a
  hypothesis.
- **Implementation:** executable code or a concrete schema. It may instantiate a
  mechanism without validating it.
- **Evidence:** an observation produced by a specified protocol, with scope,
  provenance, and limitations. Evidence can support or undermine a hypothesis
  without becoming the hypothesis.
- **Open question:** an unresolved choice or unknown that constrains later work.

Example: `P-003` Scope is a candidate primitive. `H-003` scope-aware allocation
is a hypothesis. A future Python `Scope` class would be an implementation. A
controlled ablation would produce evidence. None substitutes for the others.

## Concept maturity

Allowed statuses are:

- `seed`: preserved idea with little specification or evidence;
- `working`: sufficiently clear to reason about or design tests for, but not
  accepted as established;
- `accepted`: adopted project framing, method constraint, or architectural
  decision; for empirical claims this requires evidence appropriate to scope;
- `experimentally_supported`: supported by one or more scoped experiments but
  not elevated to an invariant or general law;
- `rejected`: tested or reviewed and found unsuitable in its stated scope;
- `deprecated`: retained for provenance but superseded or no longer recommended.

Status is a single-valued field. Rejected and deprecated entries remain in the
registry and keep links to the evidence or decision that changed their status.

## Promotion and demotion protocol

The normal path is:

```text
conversation or brainstorm
        -> seed idea
        -> working hypothesis with falsifiers
        -> specified experiment and baseline
        -> evidence with provenance and scope
        -> accepted, rejected, experimentally supported, or unresolved
```

Promotion requires an explicit edit to the canonical idea entry, a stated reason,
updated evidence references, and review of dependencies. Architectural or
governance promotion also requires an ADR. Scientific promotion must name the
protocol, scope, comparison, and result that justify it.

Demotion follows the same explicit path. Failed experiments do not erase a
concept. A rejection records what was rejected, in which scope, and why. A newer
decision supersedes rather than rewrites an older ADR.

The following are never sufficient by themselves:

- appearing in a conversation;
- being stored in a cold document;
- being implemented;
- receiving more model calls or a larger raw compute budget;
- looking plausible in one anecdote;
- inheriting a result from the IDS project or another domain.

## Methodological invariants

- **I-001 -- Conservative claims.** State proposed architecture as an object of
  investigation until evidence warrants a narrower scoped claim.
- **I-002 -- Stable identities.** Important concepts use stable IDs from
  `theory/IDEA_MAP.yaml`; renaming does not create a new concept.
- **I-003 -- Provenance and scope.** Evidence and promoted claims identify their
  origin, applicable scope, and important limitations.
- **I-004 -- Matched alternatives.** SER must be compared with simpler compute
  strategies under meaningful resource matching: fixed pipeline, random routing,
  exhaustive routing, token/cost-matched frontier reasoning, and an ordinary
  agent loop where applicable.
- **I-005 -- Resource-normalized evaluation.** More calls or longer reasoning is
  not success. Evaluation must report useful outcome relative to relevant costs.
- **I-006 -- Implementation is not validation.** Building a controller, schema,
  or operator does not promote its underlying theory.
- **I-007 -- Generated memory.** `state/CONTEXT_PACKET.md` and
  `theory/IDEA_MAP.md` are generated projections and are never hand-edited.
- **I-008 -- Historical isolation.** The IDS archive is read-only historical
  input. Its artifacts may later be inventoried, but its results do not validate
  SER and no code or data transfers automatically.
- **I-009 -- One roadmap cursor.** Exactly one roadmap phase is active.
- **I-010 -- Information-role separation.** Latent world state, legitimately
  released observations, controller epistemic state, and evaluator-only
  information remain distinct. A normal policy cannot access hidden state except
  through an authorized observation.
- **I-011 -- Policy-neutral environments.** Environments define dynamics,
  observations, and legal capabilities without consuming private controller
  belief state or recommending which legal action is epistemically best.
- **I-012 -- Raw vector resource accounting.** Resource dimensions and units are
  preserved before any experiment-specific scalarization; absent cross-domain
  dimensions are not silently treated as zero.
- **I-013 -- Explicit termination semantics.** Controller STOP, environment
  termination, and evaluator/runner truncation remain distinguishable.
- **I-014 -- Minimal ontology.** Baseline policies remain valid without explicit
  hypotheses, graph state, Signal, coupling operators, universal confidence, or
  a universal epistemic-unit schema.

The central falsification constraint is `F-004`: if a simpler frontier-model or
ordinary-agent strategy consistently matches or beats SER under the same relevant
resource budget, SER has not demonstrated architectural value in that scope.

## Current non-goals

Phase 3 implemented a minimal zero-LLM MicroGym validation runtime and produced
a narrow stopping finding. Phase 4 then supported observation-conditioned
routing only in a frozen explicit-likelihood, fixed-horizon, one-step benchmark.
Under ADR-0014 and ADR-0015, active Phase 5 froze Static Semantic AuthzGym
protocol 1.1 as the smallest controlled authorization-oriented benchmark needed
to test semantic epistemic-action value estimation without supplied likelihood
tables. Its deterministic mock calibration is implementation validation, not an
empirical result. Real-model v1 was invalid from response truncation and dynamic
references. Development-only semantic-contract v1.2 then removed those free-
form channels but was classified `contract_unstable` after its ephemeral egress
tunnel failed, leaving only 8/128 valid calls. Transport-envelope v1 then
retained the exact semantic contract and completed 128/128 provider calls with
zero transport failures; all 128 were first-attempt schema-valid, while the
nano semantic signal remained weak. Under ADR-0018, transport stability and
mechanical contract reliability are accepted only for that development
protocol. The weak nano measurements are capability-floor diagnostics, not SER
evidence. The next authorized empirical work is a separately versioned,
preregistered stronger-inexpensive-model semantic study retaining contract v1.2
and using a fresh confirmatory design before any architecture claim.

Architecture comparison, evaluation-population reruns, general LLM agents,
graph neural networks, TGNNs, learned policies, coupling
laws, semantic compressors, fuzzers, IDS adapters, GitLab integration, remote-
sensing integrations, epistemic graph runtimes, and training infrastructure
remain non-goals. Phase 5 authorizes only the next preregistered inexpensive
semantic capability study needed for Static Semantic AuthzGym, not a production
model runtime or an architecture comparison.
Do not import IDS code or datasets. GitLab authorization is the primary
practical trunk and IDS a possible semantic validation instrument under
ADR-0013; neither is current evidence. Phase 5 does not authorize real GitLab
integration, broad vulnerability discovery, or IDS import without a later
explicit decision.
