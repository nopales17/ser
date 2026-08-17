#!/usr/bin/env python3
"""Write the fail-closed MicroGym counterfactual adaptivity audit."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "src"))

from ser.evaluation.adaptivity import audit_suite
from ser.evaluation.artifacts import load_population, write_new_json
from ser.policies import AdaptiveBeliefPolicy, NoAdaptationPolicy, NoAdaptiveStopPolicy


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--population", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    problems, _, population_hash = load_population(args.population)
    audit = audit_suite(
        problems,
        (AdaptiveBeliefPolicy(), NoAdaptationPolicy(), NoAdaptiveStopPolicy()),
    )
    audit["population_hash"] = population_hash
    write_new_json(args.output, audit)
    for name, item in audit["policies"].items():
        print(
            f"{name}: {item['observation_conditioned_branching_nodes']}/"
            f"{item['counterfactual_decision_nodes']} branching nodes"
        )


if __name__ == "__main__":
    main()
