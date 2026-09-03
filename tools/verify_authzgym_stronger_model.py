#!/usr/bin/env python3
"""Verify stored stronger-model capability artifacts by exact reproduction."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from run_authzgym_stronger_model import EXPERIMENT, _paths, build_results
from ser.core.types import canonical_json


def verify(experiment: Path) -> dict:
    paths = _paths(experiment)
    validation, summary, report, interpretation, notes = build_results(experiment)
    checks = {
        "validation_reproduces": validation
        == json.loads(paths["validation"].read_text(encoding="utf-8")),
        "summary_reproduces": summary
        == json.loads(paths["summary"].read_text(encoding="utf-8")),
        "report_reproduces": report == paths["report"].read_text(encoding="utf-8"),
        "interpretation_reproduces": interpretation
        == paths["interpretation"].read_text(encoding="utf-8"),
        "implementation_notes_reproduce": notes
        == paths["implementation_notes"].read_text(encoding="utf-8"),
    }
    return {
        "status": "pass" if all(checks.values()) else "fail",
        "checks": checks,
        "classification": summary["classification"],
        "accounted_spend_usd": summary["resources"]["total_cost_usd"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment-dir", type=Path, default=EXPERIMENT)
    args = parser.parse_args()
    result = verify(args.experiment_dir)
    print(canonical_json(result))
    if result["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
