# MicroGym routing-v1 evidence interpretation

The preregistered mechanical classification is **`routing_supported`** for population `0dc7d82cfcb8ffb1ce186ef90aa040378e62d920b4f9cf4b2af7bf4ba82f3aea`.

## What the result establishes

The frozen benchmark contained 6 positive-VOA and 3 zero-VOA regimes. Oracle VOA ranged from `0.000000` to `0.202500`.

The unchanged myopic candidate branched at 6/6 eligible nodes, matched the exact closed-loop routing pattern at 6/6, and made 0/3 spurious zero-VOA branches. Its exact mean advantage over open-loop on positive-VOA regimes was `0.140083` and its VOA-weighted Adaptivity Capture was `1.000000`.

> In the frozen one-step MicroGym routing benchmark, a public-model belief-conditioned policy used a legitimately released cue to select different acquisitions and captured exact decision value unavailable to the best same-model open-loop plan.

The primary condition used one equal-cost acquisition and no STOP. Thus stopping, thrift, unequal budget, model access, identifiers, action order, or hidden truth cannot explain the exact routing gap.

## What remains unresolved

The setting supplies clean likelihood tables, a one-step horizon, four discrete hidden states, and two tiny actions. The candidate is myopic and is mathematically aligned with this horizon. This does not establish semantic action-value estimation, multi-stage rerouting, robustness to model misspecification, real software investigation, IDS transfer, GitLab value, general SER advantage, learned routing, Scope, graphs, or coupling laws.

Realized noisy episodes in which the candidate lost to open-loop remain in `runs.jsonl` and the report's failure taxonomy. Exact expected advantage does not imply every conditional choice wins ex post.

## Next unresolved question

> Can a controller estimate decision-relevant epistemic-action values from imperfect authorization/software evidence when clean likelihood tables are not supplied?

Under ADR-0013, the smallest controlled authorization-oriented software environment is preferred because it can test that question while advancing the practical GitLab authorization trunk. A full GitLab integration is not yet justified, and an IDS bridge is unnecessary unless it becomes a materially cleaner way to isolate semantic action-value estimation.
