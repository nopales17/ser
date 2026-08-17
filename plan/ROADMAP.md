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

- status: active
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

## Phase 4 -- First controlled real environment

- status: planned
- goal: select and adapt a real environment only after MicroGym exposes a
  measurable routing question; the IDS archive is one candidate, not the default
  by inheritance.
- exit: intentionally coarse until Phase 3 evidence exists.

## Phase 5 -- Active evidence generation

- status: planned
- goal: investigate intervention selection in a software/testing environment if
  earlier phases justify it.
- exit: intentionally coarse.

## Phase 6 -- Generalization and learned policies

- status: planned
- goal: consider cross-domain observation environments, SERT, or learned graph
  policies only after simpler controllers demonstrate resource-normalized value.
- exit: intentionally coarse; no implementation commitment.
