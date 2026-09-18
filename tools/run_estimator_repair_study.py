#!/usr/bin/env python3
"""Run the ADR-0020 authorized ``est-repair-v1.3.1`` development harness.

Step 1 of ``IMPLEMENTATION_HANDOFF.md``: reproduce the preserved B0 baseline
through the component interface and record it in ``BASELINES.json``.
No candidate is created, no inference is run, and no confirmation path is
opened.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from ser.evaluation.authz_v1_3_1_harness import (
    REPAIR_DIR,
    V13_DIR,
    access_ledger_record,
    append_access_ledger,
    baseline_b0,
    load_development_bundle,
)


MOTIVATION = (
    "motivated by the observed fresh-confirmation top-2 failure recorded in "
    "experiments/authzgym_semantic_contract_v1_3/ORACLE_BLOCKER.md"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=REPAIR_DIR)
    parser.add_argument("--actor", default="root")
    parser.add_argument("--no-ledger", action="store_true")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    bundle = load_development_bundle()
    baseline = baseline_b0(bundle)
    document = {
        "schema_version": 1,
        "condition_id": "est-repair-v1.3.1",
        "authorizing_adr": "ADR-0020",
        "stage": "step1_baseline_reproduction",
        "development_population_file_sha256": _sha256(
            V13_DIR / "DEVELOPMENT_PUBLIC_POPULATION.json"
        ),
        "development_population_content_hash": bundle.population_hash(),
        "recorded_expectation": baseline["recorded_expectation"],
        "acceptance_figures": baseline["acceptance_figures"],
        "baselines": {baseline["identifier"]: baseline},
        "frozen_nd3_floor_from_b2": None,
        "inference_authorized": False,
        "confirmation_authorized": False,
    }
    (output_dir / "BASELINES.json").write_text(
        json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    if not args.no_ledger:
        append_access_ledger(
            output_dir / "ACCESS_LEDGER.jsonl",
            access_ledger_record(actor=args.actor, motivation=MOTIVATION),
        )

    observed = baseline["observed"]
    print("est-repair-v1.3.1 development harness (step 1, B0 reproduction)")
    print(f"  canonical top-1 / top-2 / regret : {observed['canonical_top1']} / "
          f"{observed['canonical_top2']} / {observed['canonical_regret']}")
    print(f"  illegal targets                  : {observed['illegal_target_count']}")
    print(f"  section-14 equivalence pairs     : {observed['equivalence_pairs']} "
          f"(failures: {len(observed['equivalence_failures'])})")
    print(f"  own-ranking invariance           : {observed['own_ranking_invariance']}")
    print(f"  longest_artifact top-1 / top-2 / regret : "
          f"{observed['longest_artifact_top1']} / {observed['longest_artifact_top2']} / "
          f"{observed['longest_artifact_regret']}")
    if baseline["mismatches"]:
        print("  recorded-figure mismatches:")
        for key, item in sorted(baseline["mismatches"].items()):
            print(f"    {key}: recorded={item['recorded']} observed={item['observed']}")
    else:
        print("  all recorded B0 figures reproduce exactly")
    return 0 if baseline["reproduces_recorded_figures"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
