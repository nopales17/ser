#!/usr/bin/env python3
"""Prepare the offline-only AuthzGym v1.3 public and restricted bundles."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from ser.authzgym.v1_3_annotation_builder import derive_case_annotations
from ser.authzgym.v1_3_contract import load_public_contract
from ser.authzgym.v1_3_population import (
    build_development_population,
    build_fresh_confirmation_population,
)
from ser.core.types import content_hash


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "experiments/authzgym_semantic_contract_v1_3"
SOURCE_DEVELOPMENT = (
    ROOT / "experiments/authzgym_static_v1_1/development_population.json"
)


def _write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _write_jsonl(path: Path, values: list[dict]) -> None:
    path.write_text(
        "".join(
            json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
            for value in values
        ),
        encoding="utf-8",
    )


def _reset_bundle(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def _annotation_rows(public_population: dict, contract: dict) -> list[dict]:
    return [
        derive_case_annotations(case, contract)
        for case in public_population["cases"]
    ]


def prepare() -> dict:
    contract = load_public_contract(EXPERIMENT / "PUBLIC_CONTRACT.json")
    public_development, restricted_development = build_development_population(
        SOURCE_DEVELOPMENT
    )
    development_annotations = _annotation_rows(public_development, contract)

    # Step 8 is intentionally executed before the fresh generator is called.
    eligibility = {
        "schema_version": 1,
        "decision": "fresh_confirmation_v1_3_layouts_40_41",
        "reuse_allowed": False,
        "reason": (
            "The required chronological repair ledger, signed declarations, and "
            "complete pre-freeze proof are absent. The fixed fresh fallback is mandatory."
        ),
        "prior_confirmation_case_content_inspected": False,
        "permitted_metadata_only": True,
        "prohibited_fields_exposed": [],
        "fallback_split": "confirmation_v1_3",
        "fallback_layout_indices": [40, 41],
        "selected_before_generated_content_inspection": True,
        "implementation_freeze_hashes": {
            "population_code_sha256": _sha256_file(
                ROOT / "src/ser/authzgym/v1_3_population.py"
            ),
            "contract_code_sha256": _sha256_file(
                ROOT / "src/ser/authzgym/v1_3_contract.py"
            ),
            "annotation_code_sha256": _sha256_file(
                ROOT / "src/ser/authzgym/v1_3_annotation_builder.py"
            ),
            "answerability_checker_sha256": _sha256_file(
                ROOT / "tools/validate_authzgym_v1_3_answerability.py"
            ),
        },
    }
    _write_json(EXPERIMENT / "CONFIRMATION_ELIGIBILITY.json", eligibility)

    public_confirmation, restricted_confirmation = build_fresh_confirmation_population()
    confirmation_annotations = _annotation_rows(public_confirmation, contract)

    _write_json(EXPERIMENT / "DEVELOPMENT_PUBLIC_POPULATION.json", public_development)
    _write_json(
        EXPERIMENT / "DEVELOPMENT_RESTRICTED_POPULATION.json", restricted_development
    )
    _write_json(
        EXPERIMENT / "DEVELOPMENT_SCHEDULE.json",
        {
            "schema_version": 1,
            "split": "development",
            "repeats_per_case": 2,
            "schedule": public_development["schedule"],
            "schedule_hash": content_hash(public_development["schedule"]),
        },
    )
    _write_jsonl(
        EXPERIMENT / "annotations/development_annotations.jsonl",
        development_annotations,
    )
    _write_json(
        EXPERIMENT / "DEVELOPMENT_SOURCE_MANIFEST.json",
        {
            "schema_version": 1,
            "source": "experiments/authzgym_static_v1_1/development_population.json",
            "source_sha256": _sha256_file(SOURCE_DEVELOPMENT),
            "source_population_hash": public_development["population_hash"],
            "source_episodes": 8,
            "variants_per_source": 7,
            "cases": 56,
            "scheduled_calls": 112,
        },
    )

    _write_json(
        EXPERIMENT / "CONFIRMATION_PUBLIC_POPULATION.json", public_confirmation
    )
    _write_json(
        EXPERIMENT / "CONFIRMATION_RESTRICTED_POPULATION.json",
        restricted_confirmation,
    )
    _write_json(
        EXPERIMENT / "CONFIRMATION_SCHEDULE.json",
        {
            "schema_version": 1,
            "split": "confirmation_v1_3",
            "repeats_per_case": 1,
            "schedule": public_confirmation["schedule"],
            "schedule_hash": content_hash(public_confirmation["schedule"]),
        },
    )
    _write_jsonl(
        EXPERIMENT / "annotations/confirmation_annotations.jsonl",
        confirmation_annotations,
    )
    _write_json(
        EXPERIMENT / "CONFIRMATION_SOURCE_MANIFEST.json",
        {
            "schema_version": 1,
            "generation": "unchanged_frozen_authoring_method",
            "split": "confirmation_v1_3",
            "layout_indices": [40, 41],
            "source_episodes": 8,
            "variants_per_source": 7,
            "cases": 56,
            "scheduled_calls": 56,
            "population_hash": public_confirmation["population_hash"],
        },
    )

    _write_json(
        EXPERIMENT / "DEVELOPMENT_TRANSFORMATION_MAPS.json",
        {
            "schema_version": 1,
            "visibility": "restricted",
            "cases": {
                item["case_id"]: item["transformation_maps"]
                for item in restricted_development["cases"]
            },
        },
    )
    _write_json(
        EXPERIMENT / "CONFIRMATION_TRANSFORMATION_MAPS.json",
        {
            "schema_version": 1,
            "visibility": "restricted",
            "cases": {
                item["case_id"]: item["transformation_maps"]
                for item in restricted_confirmation["cases"]
            },
        },
    )

    _write_json(
        EXPERIMENT / "MODEL_TRANSPORT_CONFIG.json",
        {
            "schema_version": 1,
            "inference_authorized": False,
            "provider_calls_authorized": 0,
            "development_planned_calls": 112,
            "confirmation_planned_calls": 56,
            "model_identifier": "unassigned_until_separate_inference_authorization",
            "retry_policy": {
                "semantic_retries": 1,
                "transport_replays": 1,
                "identical_request_bytes_required": True,
            },
            "limits": {
                "maximum_output_tokens": 1024,
                "maximum_input_tokens": 4000,
                "hard_spend_ceiling_usd": 2.5,
            },
            "provider_response_artifacts": [],
        },
    )

    public_bundle = EXPERIMENT / "PUBLIC_BUNDLE"
    restricted_bundle = EXPERIMENT / "RESTRICTED_BUNDLE"
    _reset_bundle(public_bundle)
    _reset_bundle(restricted_bundle)
    for name in (
        "PUBLIC_CONTRACT.json",
        "DEVELOPMENT_PUBLIC_POPULATION.json",
        "CONFIRMATION_PUBLIC_POPULATION.json",
        "DEVELOPMENT_SCHEDULE.json",
        "CONFIRMATION_SCHEDULE.json",
    ):
        shutil.copy2(EXPERIMENT / name, public_bundle / name)
    (public_bundle / "prompts").mkdir()
    shutil.copy2(
        EXPERIMENT / "prompts/semantic_observation_v1_3.txt",
        public_bundle / "prompts/semantic_observation_v1_3.txt",
    )
    (public_bundle / "schemas").mkdir()
    shutil.copy2(
        EXPERIMENT / "schemas/semantic_vocabulary_v1_3.json",
        public_bundle / "schemas/semantic_vocabulary_v1_3.json",
    )
    for name in (
        "DEVELOPMENT_RESTRICTED_POPULATION.json",
        "CONFIRMATION_RESTRICTED_POPULATION.json",
        "DEVELOPMENT_TRANSFORMATION_MAPS.json",
        "CONFIRMATION_TRANSFORMATION_MAPS.json",
        "CONFIRMATION_ELIGIBILITY.json",
    ):
        shutil.copy2(EXPERIMENT / name, restricted_bundle / name)
    (restricted_bundle / "annotations").mkdir()
    shutil.copy2(
        EXPERIMENT / "annotations/development_annotations.jsonl",
        restricted_bundle / "annotations/development_annotations.jsonl",
    )
    shutil.copy2(
        EXPERIMENT / "annotations/confirmation_annotations.jsonl",
        restricted_bundle / "annotations/confirmation_annotations.jsonl",
    )

    public_manifest = {
        "schema_version": 1,
        "split": "both",
        "files": {
            path.name: _sha256_file(path)
            for path in sorted(public_bundle.rglob("*"))
            if path.is_file()
        },
    }
    restricted_manifest = {
        "schema_version": 1,
        "split": "both",
        "files": {
            path.name: _sha256_file(path)
            for path in sorted(restricted_bundle.rglob("*"))
            if path.is_file()
        },
    }
    public_manifest["manifest_hash"] = content_hash(public_manifest)
    restricted_manifest["manifest_hash"] = content_hash(restricted_manifest)
    _write_json(EXPERIMENT / "PUBLIC_BUNDLE_MANIFEST.json", public_manifest)
    _write_json(EXPERIMENT / "RESTRICTED_BUNDLE_MANIFEST.json", restricted_manifest)
    return {
        "development_cases": len(public_development["cases"]),
        "development_calls": len(public_development["schedule"]),
        "confirmation_cases": len(public_confirmation["cases"]),
        "confirmation_calls": len(public_confirmation["schedule"]),
        "public_bundle_manifest_hash": public_manifest["manifest_hash"],
        "restricted_bundle_manifest_hash": restricted_manifest["manifest_hash"],
    }


def _sha256_file(path: Path) -> str:
    return __import__("hashlib").sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--offline",
        action="store_true",
        help="required explicit assertion that no provider or network call is permitted",
    )
    args = parser.parse_args()
    if not args.offline:
        raise SystemExit("refusing to prepare without --offline")
    print(json.dumps(prepare(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
