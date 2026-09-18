#!/usr/bin/env python3
"""Custodian runner for the ADR-0022 successor confirmation (preregistration section 8).

Stages run in the section-8.7 order and each stage refuses to run out of order:

  freeze-record  step 2  restate the section-8 parameters and name the frozen hashes
  generate       step 3a generation, conversion, independent annotations, 8.3 checks
  validate       step 3b independent answerability and firewall validation
  oracle         step 4  exactly one oracle evaluation of the frozen component
  seal           step 5  seal the manifest

The frozen authoring method, converter, contract, annotations, scoring, and the
component are used unchanged; this tool only calls them. It never opens the spent
``confirmation_v1_3`` population and never runs a model or provider call.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import inspect
import json
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from ser.authzgym.v1_3_annotation_builder import derive_case_annotations
from ser.authzgym.v1_3_contract import load_public_contract
from ser.authzgym.v1_3_population import (
    VARIANTS,
    build_source_cases,
    public_population_payload,
)
from ser.core.types import content_hash
from ser.evaluation.authz_v1_3_1_harness import (
    DevelopmentBundle,
    gate_record,
    guarded_sha256,
    integrity_files_v13,
)


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
OUT = ROOT / "experiments/authzgym_confirmation_v1_3_1"
V13 = ROOT / "experiments/authzgym_semantic_contract_v1_3"
REPAIR = ROOT / "experiments/authzgym_estimator_repair_v1_3_1"

SPLIT = "confirmation_v1_3_1"
LAYOUT_INDICES = (42, 43)
RESERVED_FALLBACK_PAIRS = ((44, 45), (46, 47))

COMPONENT = "est-repair-v1.3.1-B-1"
COMPONENT_CLASS_SHA256 = (
    "88b77c5f343117b354b5039d571bf03bf8867fcd7fb4f8fc91c1e1aefca7a048"
)
COMPONENT_MODULE_SHA256 = (
    "f9c92317abc562ac5175f90074238c666de55d557b02e0de368841676f4d910d"
)
DEVELOPMENT_REPORT_SHA256 = (
    "f0629d3b78ba35258cc6d439e4b731c3682b76fa08e4155efbdad7cd0df18638"
)
DEVELOPMENT_POPULATION_SHA256 = (
    "dda4e0c08a9c29a58a912fdcb5268ddf602aac79c47f6dd3fb94102b5dc8c365"
)
SPENT_CONFIRMATION_POPULATION_SHA256 = (
    "0e20284be388131d451f5befc22a048b3badba87a338168d8f7865bfbc9bd28f"
)
DEVELOPMENT_FROZEN_INPUTS = (
    "src/ser/authzgym/generation.py",
    "src/ser/authzgym/v1_3_population.py",
    "src/ser/authzgym/v1_3_contract.py",
    "src/ser/authzgym/v1_3_annotation_builder.py",
    "tools/validate_authzgym_v1_3_answerability.py",
    "tools/validate_authzgym_v1_3_firewall.py",
    "src/ser/evaluation/authz_v1_3.py",
    "src/ser/authzgym/policies.py",
)
CONFIRMATION_GATE = (
    "canonical_top1",
    "canonical_top2",
    "mean_normalized_regret",
    "illegal_target_count",
    "section_14_equivalence",
    "own_selection_equivalence",
)


class CustodianError(RuntimeError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(
            json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n"
            for row in rows
        ),
        encoding="utf-8",
    )


def _read_json(path: Path) -> dict:
    return json.loads(guard(path).read_text(encoding="utf-8"))


def guard(path: Path) -> Path:
    """Refuse to touch the spent confirmation_v1_3 population."""

    candidate = Path(path)
    name = candidate.name
    if (
        name.startswith("CONFIRMATION_")
        and "V1_3_1" not in name
        and candidate.parent == V13
    ):
        raise CustodianError(f"refusing to open spent confirmation path: {name}")
    return candidate


def ledger(event: str, *, path: str, operation: str, detail: str = "") -> None:
    record = {
        "schema_version": 1,
        "event": event,
        "timestamp_utc": _now(),
        "actor": "custodian",
        "condition_id": COMPONENT,
        "path": path,
        "operation": operation,
        "detail": detail,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "CONFIRMATION_V1_3_1_ACCESS_LEDGER.jsonl").open(
        "a", encoding="utf-8"
    ) as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def _manifest(files: dict[str, Path]) -> dict:
    document = {
        "schema_version": 1,
        "files": {
            name: hashlib.sha256(path.read_bytes()).hexdigest()
            for name, path in sorted(files.items())
        },
    }
    document["manifest_sha256"] = content_hash(document)
    return document


def step_freeze_record() -> dict:
    """Section 8.7 step 2: restate the parameters and name the frozen hashes."""

    if (OUT / "CONFIRMATION_V1_3_1_FREEZE_RECORD.json").exists():
        raise CustodianError("freeze record already exists; refusing to rewrite it")
    development_report = REPAIR / "DEVELOPMENT_REPORT.md"
    observed_report = hashlib.sha256(development_report.read_bytes()).hexdigest()
    if observed_report != DEVELOPMENT_REPORT_SHA256:
        raise CustodianError(
            f"frozen development report hash mismatch: {observed_report}"
        )
    component_module = ROOT / "src/ser/authzgym/policies_v1_3_1.py"
    observed_module = hashlib.sha256(component_module.read_bytes()).hexdigest()
    if observed_module != COMPONENT_MODULE_SHA256:
        raise CustodianError(f"component module hash mismatch: {observed_module}")
    component_class = importlib.import_module("ser.authzgym.policies_v1_3_1")
    observed_class = hashlib.sha256(
        inspect.getsource(component_class.EstimatorV1SalientCategory).encode("utf-8")
    ).hexdigest()
    if observed_class != COMPONENT_CLASS_SHA256:
        raise CustodianError(f"component class hash mismatch: {observed_class}")

    record = {
        "schema_version": 1,
        "condition_id": COMPONENT,
        "authorizing_adr": "ADR-0022",
        "governing_preregistration": (
            "experiments/authzgym_estimator_repair_v1_3_1/"
            "REPAIR_STUDY_PREREGISTRATION.md section 8"
        ),
        "step": "8.7.2 freeze record",
        "selected_component": {
            "candidate_id": COMPONENT,
            "class_sha256": COMPONENT_CLASS_SHA256,
            "module_sha256": COMPONENT_MODULE_SHA256,
            "fragile_label": None,
        },
        "development_report_sha256": DEVELOPMENT_REPORT_SHA256,
        "population": {
            "split": SPLIT,
            "layout_indices": list(LAYOUT_INDICES),
            "reserved_fallback_pairs": [list(pair) for pair in RESERVED_FALLBACK_PAIRS],
            "selection_rule": (
                "next unused layout indices in ascending order, fixed before "
                "generation; a collision advances to the next reserved pair and is "
                "never resolved by inspecting content"
            ),
            "variants": list(VARIANTS),
            "source_instances": 8,
            "expected_cases": 56,
            "expected_scheduled_calls": 56,
            "repeats_per_case": 1,
            "generator": "src/ser/authzgym/generation.py (byte-unchanged)",
            "converter": "src/ser/authzgym/v1_3_population.py (byte-unchanged)",
            "no_model_or_provider_call": True,
        },
        "duplicate_reference_hashes": {
            "development_public_population_file_sha256": DEVELOPMENT_POPULATION_SHA256,
            "spent_confirmation_public_population_file_sha256": (
                SPENT_CONFIRMATION_POPULATION_SHA256
            ),
            "spent_population_opened": False,
        },
    }
    ledger(
        "freeze_record_written",
        path="CONFIRMATION_V1_3_1_FREEZE_RECORD.json",
        operation="write",
        detail="section 8.7 step 2; component and report hashes verified",
    )
    _write_json(OUT / "CONFIRMATION_V1_3_1_FREEZE_RECORD.json", record)
    return record


def _build_population() -> tuple[dict, dict, list[dict], dict[int, list[str]]]:
    from ser.authzgym.generation import MECHANISMS, _episode

    contract = load_public_contract(V13 / "PUBLIC_CONTRACT.json")
    layout_source_ids: dict[int, list[str]] = {}
    sources = []
    for layout_index in LAYOUT_INDICES:
        for mechanism in MECHANISMS:
            episode = _episode(
                SPLIT,
                layout_index,
                mechanism,
                decision_group=f"confirmation-v1-3-1-{layout_index}",
                control_type="eligible_branch",
            ).to_dict()
            layout_source_ids.setdefault(layout_index, []).append(
                str(episode["public"]["episode_id"])
            )
            sources.append(episode)
    public_cases, restricted_cases = build_source_cases(
        sources, contract, split=SPLIT, repeat_count=1
    )
    if len(public_cases) != 56:
        raise CustodianError("successor confirmation population must contain 56 cases")
    public = public_population_payload(
        public_cases,
        experiment="authzgym-semantic-contract-v1.3.1-confirmation",
        split=SPLIT,
        repeat_count=1,
    )
    restricted = {
        "schema_version": 1,
        "experiment": "authzgym-semantic-contract-v1.3.1-confirmation",
        "split": SPLIT,
        "layout_indices": list(LAYOUT_INDICES),
        "cases": restricted_cases,
        "source_population_hash": content_hash(
            {"split": SPLIT, "layout_indices": list(LAYOUT_INDICES)}
        ),
    }
    restricted["restricted_hash"] = content_hash(restricted)
    annotations = [derive_case_annotations(case, contract) for case in public_cases]
    return public, restricted, annotations, layout_source_ids


def step_generate() -> dict:
    """Section 8.7 step 3a, plus the section-8.3 duplicate and equivalence checks."""

    if not (OUT / "CONFIRMATION_V1_3_1_FREEZE_RECORD.json").exists():
        raise CustodianError("the section-8.7 step-2 freeze record must be written first")
    for name in (
        "CONFIRMATION_PUBLIC_POPULATION.json",
        "CONFIRMATION_RESTRICTED_POPULATION.json",
    ):
        if (OUT / name).exists():
            raise CustodianError(f"{name} already exists; refusing to regenerate")

    ledger("generation_start", path=SPLIT, operation="generate")
    public, restricted, annotations, layout_source_ids = _build_population()

    public_path = OUT / "CONFIRMATION_PUBLIC_POPULATION.json"
    restricted_path = OUT / "CONFIRMATION_RESTRICTED_POPULATION.json"
    schedule_path = OUT / "CONFIRMATION_SCHEDULE.json"
    annotations_path = OUT / "annotations/confirmation_v1_3_1_annotations.jsonl"
    maps_path = OUT / "CONFIRMATION_TRANSFORMATION_MAPS.json"
    _write_json(public_path, public)
    _write_json(restricted_path, restricted)
    _write_json(
        schedule_path,
        {
            "schema_version": 1,
            "split": SPLIT,
            "repeats_per_case": 1,
            "schedule": public["schedule"],
            "schedule_hash": content_hash(public["schedule"]),
        },
    )
    _write_jsonl(annotations_path, annotations)
    _write_json(
        maps_path,
        {
            "schema_version": 1,
            "visibility": "restricted",
            "split": SPLIT,
            "cases": {
                item["case_id"]: item["transformation_maps"]
                for item in restricted["cases"]
            },
        },
    )
    for name, path in (
        ("CONFIRMATION_PUBLIC_POPULATION.json", public_path),
        ("CONFIRMATION_RESTRICTED_POPULATION.json", restricted_path),
        ("CONFIRMATION_SCHEDULE.json", schedule_path),
        ("annotations/confirmation_v1_3_1_annotations.jsonl", annotations_path),
        ("CONFIRMATION_TRANSFORMATION_MAPS.json", maps_path),
    ):
        ledger("write", path=name, operation="write")

    checks = _duplication_checks(public, public_path, layout_source_ids)
    _write_json(OUT / "CONFIRMATION_V1_3_1_DUPLICATION_CHECKS.json", checks)
    source_manifest = _manifest(
        {
            "CONFIRMATION_PUBLIC_POPULATION.json": public_path,
            "CONFIRMATION_RESTRICTED_POPULATION.json": restricted_path,
            "CONFIRMATION_SCHEDULE.json": schedule_path,
            "annotations/confirmation_v1_3_1_annotations.jsonl": annotations_path,
            "CONFIRMATION_TRANSFORMATION_MAPS.json": maps_path,
        }
    )
    source_manifest.update(
        {
            "split": SPLIT,
            "layout_indices": list(LAYOUT_INDICES),
            "generation": "unchanged_frozen_authoring_method_and_converter",
            "generator_sha256": hashlib.sha256(
                (ROOT / "src/ser/authzgym/generation.py").read_bytes()
            ).hexdigest(),
            "converter_sha256": hashlib.sha256(
                (ROOT / "src/ser/authzgym/v1_3_population.py").read_bytes()
            ).hexdigest(),
            "source_instances": 8,
            "variants_per_source": len(VARIANTS),
            "cases": len(public["cases"]),
            "scheduled_calls": len(public["schedule"]),
            "repeats_per_case": 1,
            "provider_calls_authorized": 0,
        }
    )
    source_manifest["manifest_sha256"] = content_hash(
        {k: v for k, v in source_manifest.items() if k != "manifest_sha256"}
    )
    _write_json(OUT / "CONFIRMATION_V1_3_1_SOURCE_MANIFEST.json", source_manifest)
    _write_json(
        OUT / "CONFIRMATION_V1_3_1_PUBLIC_MANIFEST.json",
        _manifest(
            {
                "PUBLIC_CONTRACT.json": V13 / "PUBLIC_CONTRACT.json",
                "CONFIRMATION_PUBLIC_POPULATION.json": public_path,
                "CONFIRMATION_SCHEDULE.json": schedule_path,
            }
        ),
    )
    _write_json(
        OUT / "CONFIRMATION_V1_3_1_RESTRICTED_MANIFEST.json",
        _manifest(
            {
                "CONFIRMATION_RESTRICTED_POPULATION.json": restricted_path,
                "CONFIRMATION_TRANSFORMATION_MAPS.json": maps_path,
                "annotations/confirmation_v1_3_1_annotations.jsonl": annotations_path,
            }
        ),
    )
    frozen_inputs = {
        "schema_version": 1,
        "split": SPLIT,
        "git_commit": _git_commit(),
        "files": {
            **{
                name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                for name in DEVELOPMENT_FROZEN_INPUTS
            },
            **{
                f"experiments/authzgym_confirmation_v1_3_1/{name}": hashlib.sha256(
                    path.read_bytes()
                ).hexdigest()
                for name, path in (
                    ("CONFIRMATION_PUBLIC_POPULATION.json", public_path),
                    ("CONFIRMATION_RESTRICTED_POPULATION.json", restricted_path),
                    ("CONFIRMATION_SCHEDULE.json", schedule_path),
                    ("CONFIRMATION_TRANSFORMATION_MAPS.json", maps_path),
                    (
                        "annotations/confirmation_v1_3_1_annotations.jsonl",
                        annotations_path,
                    ),
                    (
                        "CONFIRMATION_V1_3_1_SOURCE_MANIFEST.json",
                        OUT / "CONFIRMATION_V1_3_1_SOURCE_MANIFEST.json",
                    ),
                )
            },
        },
        "frozen_component": {
            "candidate_id": COMPONENT,
            "class_sha256": COMPONENT_CLASS_SHA256,
            "module_sha256": COMPONENT_MODULE_SHA256,
        },
        "development_report_sha256": DEVELOPMENT_REPORT_SHA256,
        "provider_calls_authorized": 0,
        "inference_authorized": False,
    }
    frozen_inputs["manifest_sha256"] = content_hash(frozen_inputs)
    _write_json(OUT / "FROZEN_INPUTS_V1_3_1.json", frozen_inputs)
    ledger("generation_complete", path=SPLIT, operation="generate")
    return {
        "cases": len(public["cases"]),
        "scheduled_calls": len(public["schedule"]),
        "source_manifest_sha256": source_manifest["manifest_sha256"],
        "duplication_checks_passed": checks["all_passed"],
    }


def _git_commit() -> str:
    import subprocess

    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _duplication_checks(
    public: dict, public_path: Path, layout_source_ids: dict[int, list[str]]
) -> dict:
    """Section 8.3. The spent population is compared by construction, not opened."""

    development = json.loads(
        (V13 / "DEVELOPMENT_PUBLIC_POPULATION.json").read_text(encoding="utf-8")
    )
    new_hash = hashlib.sha256(public_path.read_bytes()).hexdigest()
    new_case_ids = {str(case["case_id"]) for case in public["cases"]}
    new_inputs = {
        str(case["runner_control"]["public_input_sha256"]) for case in public["cases"]
    }
    new_sources = {str(case["source_episode_id"]) for case in public["cases"]}
    development_case_ids = {str(case["case_id"]) for case in development["cases"]}
    development_inputs = {
        str(case["runner_control"]["public_input_sha256"])
        for case in development["cases"]
    }
    development_sources = {
        str(case["source_episode_id"]) for case in development["cases"]
    }
    layout_digests = {
        str(layout): content_hash(sorted(identifiers))
        for layout, identifiers in sorted(layout_source_ids.items())
    }
    checks = {
        "schema_version": 1,
        "split": SPLIT,
        "population_file_sha256": new_hash,
        "population_hash_differs_from_development": (
            new_hash != DEVELOPMENT_POPULATION_SHA256
        ),
        "population_hash_differs_from_spent_confirmation": (
            new_hash != SPENT_CONFIRMATION_POPULATION_SHA256
        ),
        "case_ids_disjoint_from_development": not (new_case_ids & development_case_ids),
        "public_input_hashes_disjoint_from_development": not (
            new_inputs & development_inputs
        ),
        "source_episode_ids_disjoint_from_development": not (
            new_sources & development_sources
        ),
        "layout_digests_differ": layout_digests[str(LAYOUT_INDICES[0])]
        != layout_digests[str(LAYOUT_INDICES[1])],
        "layout_digests": layout_digests,
        "spent_population_method": (
            "verified_by_construction: the split label "
            f"{SPLIT!r} differs from 'confirmation_v1_3', the layout indices "
            f"{list(LAYOUT_INDICES)} are disjoint from the spent layouts 40/41, and the "
            "frozen converter derives every public identifier from a bijection over "
            "(source_episode_id, variant_id, namespace, original_token) where "
            "source_episode_id embeds the split label and layout index. The spent "
            "population content was not opened, per section 12.2."
        ),
        "spent_population_opened": False,
        "checks_verified_directly": [
            "population_hash_differs_from_development",
            "case_ids_disjoint_from_development",
            "public_input_hashes_disjoint_from_development",
            "source_episode_ids_disjoint_from_development",
            "layout_digests_differ",
        ],
        "checks_verified_by_construction": [
            "population_hash_differs_from_spent_confirmation",
            "case_ids_disjoint_from_spent_confirmation",
            "public_input_hashes_disjoint_from_spent_confirmation",
            "source_episode_ids_disjoint_from_spent_confirmation",
            "no_byte_identical_public_input_against_spent_confirmation",
        ],
    }
    checks["all_passed"] = all(
        value
        for key, value in checks.items()
        if key.startswith(
            (
                "population_hash_differs",
                "case_ids_disjoint",
                "public_input_hashes_disjoint",
                "source_episode_ids_disjoint",
                "layout_digests_differ",
            )
        )
    )
    return checks


def _load_confirmation_bundle() -> tuple[DevelopmentBundle, dict]:
    contract = load_public_contract(V13 / "PUBLIC_CONTRACT.json")
    public = _read_json(OUT / "CONFIRMATION_PUBLIC_POPULATION.json")
    restricted = {
        item["case_id"]: item
        for item in _read_json(OUT / "CONFIRMATION_RESTRICTED_POPULATION.json")["cases"]
    }
    annotations = {
        item["case_id"]: item
        for item in (
            json.loads(line)
            for line in (
                OUT / "annotations/confirmation_v1_3_1_annotations.jsonl"
            ).read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }
    transformation_maps = _read_json(OUT / "CONFIRMATION_TRANSFORMATION_MAPS.json")
    bundle = DevelopmentBundle(
        contract=contract,
        cases=tuple(public["cases"]),
        restricted=restricted,
        annotations=annotations,
        transformation_maps=transformation_maps,
    )
    return bundle, public


def step_validate() -> dict:
    """Section 8.7 step 3b: independent answerability and firewall validation."""

    checks = _read_json(OUT / "CONFIRMATION_V1_3_1_DUPLICATION_CHECKS.json")
    if not checks["all_passed"]:
        raise CustodianError("section-8.3 duplication checks failed; refusing to validate")
    for name in (
        "CONFIRMATION_V1_3_1_ANSWERABILITY_VALIDATION.json",
        "CONFIRMATION_V1_3_1_FIREWALL_VALIDATION.json",
    ):
        if (OUT / name).exists():
            raise CustodianError(f"{name} already exists; refusing to re-validate")

    from tools import validate_authzgym_v1_3_answerability as answerability
    from tools import validate_authzgym_v1_3_firewall as firewall

    with tempfile.TemporaryDirectory() as temporary:
        stage = Path(temporary)
        shutil.copy2(V13 / "PUBLIC_CONTRACT.json", stage / "PUBLIC_CONTRACT.json")
        # The frozen checkers are pointed at the successor population by staging the
        # successor public bundle under the file names they already read. Neither
        # checker is modified.
        shutil.copy2(
            OUT / "CONFIRMATION_PUBLIC_POPULATION.json",
            stage / "CONFIRMATION_PUBLIC_POPULATION.json",
        )
        shutil.copy2(
            OUT / "CONFIRMATION_PUBLIC_POPULATION.json",
            stage / "DEVELOPMENT_PUBLIC_POPULATION.json",
        )
        (stage / "prompts").mkdir()
        shutil.copy2(
            V13 / "prompts/semantic_observation_v1_3.txt",
            stage / "prompts/semantic_observation_v1_3.txt",
        )
        (stage / "schemas").mkdir()
        shutil.copy2(
            V13 / "schemas/semantic_vocabulary_v1_3.json",
            stage / "schemas/semantic_vocabulary_v1_3.json",
        )
        certificates = (
            OUT / "annotations/confirmation_v1_3_1_annotations.jsonl"
        )
        ledger("read", path="PUBLIC_CONTRACT.json", operation="validate")
        answerability_result = answerability.validate(
            stage, certificates, split=SPLIT
        )
        firewall_result = firewall.validate(stage)
    answerability_result["reviewed_population"] = SPLIT
    answerability_result["staged_file_names"] = [
        "PUBLIC_CONTRACT.json",
        "CONFIRMATION_PUBLIC_POPULATION.json",
    ]
    firewall_result["reviewed_population"] = SPLIT

    _write_json(OUT / "CONFIRMATION_V1_3_1_ANSWERABILITY_VALIDATION.json", answerability_result)
    _write_json(OUT / "CONFIRMATION_V1_3_1_FIREWALL_VALIDATION.json", firewall_result)
    outcome = {
        "answerability_status": answerability_result["status"],
        "firewall_status": firewall_result["status"],
        "all_passed": (
            answerability_result["status"] == "pass"
            and firewall_result["status"] == "pass"
        ),
    }
    ledger(
        "validation_complete",
        path=SPLIT,
        operation="validate",
        detail=json.dumps(outcome, sort_keys=True),
    )
    return outcome


def step_oracle() -> dict:
    """Section 8.7 step 4 and 8.8: exactly one oracle evaluation."""

    for name in (
        "CONFIRMATION_V1_3_1_ANSWERABILITY_VALIDATION.json",
        "CONFIRMATION_V1_3_1_FIREWALL_VALIDATION.json",
    ):
        if not (OUT / name).exists():
            raise CustodianError("answerability and firewall validation must pass first")
        if _read_json(OUT / name)["status"] != "pass":
            raise CustodianError(f"{name} did not pass; a failure is a blocker")
    if (OUT / "CONFIRMATION_V1_3_1_ORACLE_VALIDATION.json").exists():
        raise CustodianError(
            "the one-shot oracle evaluation has already run; refusing to repeat it"
        )

    component_module = ROOT / "src/ser/authzgym/policies_v1_3_1.py"
    if hashlib.sha256(component_module.read_bytes()).hexdigest() != COMPONENT_MODULE_SHA256:
        raise CustodianError("frozen component module changed; refusing to evaluate")
    component_class = importlib.import_module("ser.authzgym.policies_v1_3_1")
    if (
        hashlib.sha256(
            inspect.getsource(component_class.EstimatorV1SalientCategory).encode("utf-8")
        ).hexdigest()
        != COMPONENT_CLASS_SHA256
    ):
        raise CustodianError("frozen component class changed; refusing to evaluate")

    bundle, public = _load_confirmation_bundle()
    development = _read_json(REPAIR / "BASELINES.json")
    nd3_floor = development["frozen_nd3_floor_from_b2"]
    component = component_class.EstimatorV1SalientCategory()
    ledger("oracle_evaluation_start", path="CONFIRMATION_PUBLIC_POPULATION.json", operation="evaluate")
    record = gate_record(bundle, component, nd3_floor=nd3_floor)

    checks = {
        "canonical_top1": record["canonical_aggregate"]["top1"] >= 0.60,
        "canonical_top2": record["canonical_aggregate"]["top2"] >= 0.80,
        "mean_normalized_regret": (
            record["canonical_aggregate"]["mean_normalized_regret"] <= 0.35
        ),
        "illegal_target_count": (
            record["canonical_aggregate"]["illegal_target_count"] == 0
        ),
        "section_14_equivalence": (
            record["section_14_equivalence"]["pair_count"] == 40
            and not record["section_14_equivalence"]["failures"]
        ),
        "own_selection_equivalence": (
            record["own_ranking_invariance"]["selection_total"] == 40
            and record["own_ranking_invariance"]["selection_pass"] == 40
        ),
    }
    passed = all(checks.values())
    document = {
        "schema_version": 1,
        "condition_id": COMPONENT,
        "authorizing_adr": "ADR-0022",
        "stage": "8.7.4 one-shot oracle evaluation",
        "population_split": SPLIT,
        "population_file_sha256": hashlib.sha256(
            (OUT / "CONFIRMATION_PUBLIC_POPULATION.json").read_bytes()
        ).hexdigest(),
        "canonical_case_count": record["canonical_aggregate"]["case_count"],
        "component": {
            "candidate_id": COMPONENT,
            "class_sha256": COMPONENT_CLASS_SHA256,
            "module_sha256": COMPONENT_MODULE_SHA256,
        },
        "gate_definition": {
            "canonical_top1": ">= 0.60",
            "canonical_top2": ">= 0.80",
            "mean_normalized_regret": "<= 0.35",
            "illegal_target_count": "= 0",
            "section_14_equivalence": "40/40 within 1e-12",
            "own_selection_equivalence": "40/40 after ordinal mapping",
        },
        "gate_checks": checks,
        "canonical_aggregate": record["canonical_aggregate"],
        "section_14_equivalence": record["section_14_equivalence"],
        "own_selection_equivalence": record["own_ranking_invariance"],
        "non_degeneracy_descriptive_only": record["non_degeneracy"],
        "longest_artifact_descriptive_only": record["longest_artifact_aggregate"],
        "leave_one_source_out_descriptive_only": record["leave_one_source_out"],
        "status": "pass" if passed else "fail",
        "one_shot": True,
        "evaluations_run": 1,
        "model_or_provider_calls": 0,
    }
    _write_json(OUT / "CONFIRMATION_V1_3_1_ORACLE_VALIDATION.json", document)
    ledger(
        "oracle_evaluation_complete",
        path="CONFIRMATION_V1_3_1_ORACLE_VALIDATION.json",
        operation="write",
        detail=f"status={document['status']}",
    )
    return {
        "status": document["status"],
        "canonical_top1": record["canonical_aggregate"]["top1"],
        "canonical_top2": record["canonical_aggregate"]["top2"],
        "mean_normalized_regret": record["canonical_aggregate"]["mean_normalized_regret"],
        "failing_gates": [key for key, value in checks.items() if not value],
    }


def step_seal() -> dict:
    """Section 8.7 step 5: seal the population after the one-shot evaluation."""

    if not (OUT / "CONFIRMATION_V1_3_1_ORACLE_VALIDATION.json").exists():
        raise CustodianError("the one-shot oracle evaluation must run before the seal")
    if (OUT / "CONFIRMATION_V1_3_1_SEAL.json").exists():
        raise CustodianError("the population is already sealed; refusing to reseal")
    files = {}
    for path in sorted(OUT.rglob("*")):
        if not path.is_file():
            continue
        if path.name in (
            "CONFIRMATION_V1_3_1_SEAL.json",
            "CONFIRMATION_V1_3_1_ACCESS_LEDGER.jsonl",
            "REPORT.md",
        ):
            continue
        files[str(path.relative_to(OUT))] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
    seal = {
        "schema_version": 1,
        "split": SPLIT,
        "sealed": True,
        "sealed_after_oracle": True,
        "files": files,
        "population_hash": files["CONFIRMATION_PUBLIC_POPULATION.json"],
        "oracle_status": _read_json(
            OUT / "CONFIRMATION_V1_3_1_ORACLE_VALIDATION.json"
        )["status"],
        "provider_calls": 0,
    }
    seal["seal_sha256"] = content_hash(seal)
    _write_json(OUT / "CONFIRMATION_V1_3_1_SEAL.json", seal)
    ledger("sealed", path="CONFIRMATION_V1_3_1_SEAL.json", operation="write")
    return {
        "sealed": True,
        "population_hash": seal["population_hash"],
        "oracle_status": seal["oracle_status"],
        "seal_sha256": seal["seal_sha256"],
    }


STAGES = {
    "freeze-record": step_freeze_record,
    "generate": step_generate,
    "validate": step_validate,
    "oracle": step_oracle,
    "seal": step_seal,
    "report": lambda: step_report(),
}


def step_report() -> dict:
    """Render the confirmation report from the sealed artifacts."""

    freeze = _read_json(OUT / "CONFIRMATION_V1_3_1_FREEZE_RECORD.json")
    source = _read_json(OUT / "CONFIRMATION_V1_3_1_SOURCE_MANIFEST.json")
    duplication = _read_json(OUT / "CONFIRMATION_V1_3_1_DUPLICATION_CHECKS.json")
    answerability = _read_json(OUT / "CONFIRMATION_V1_3_1_ANSWERABILITY_VALIDATION.json")
    firewall = _read_json(OUT / "CONFIRMATION_V1_3_1_FIREWALL_VALIDATION.json")
    oracle = _read_json(OUT / "CONFIRMATION_V1_3_1_ORACLE_VALIDATION.json")
    seal = _read_json(OUT / "CONFIRMATION_V1_3_1_SEAL.json")

    gate_rows = "\n".join(
        f"| {name} | {requirement} | {oracle['gate_checks'][name]} |".replace(
            "True", "pass"
        ).replace("False", "fail")
        for name, requirement in oracle["gate_definition"].items()
    )
    lines = [
        "# AuthzGym successor confirmation report -- `est-repair-v1.3.1-B-1`",
        "",
        f"Condition: `{COMPONENT}`. Authorized by ADR-0022 under preregistration",
        "section 8. Status: **sealed**, one-shot evaluation complete.",
        "",
        "This is a confirmation of component/instrument compatibility. It is not an",
        "architecture, capability, transfer, or model finding, and no model or",
        "provider call was made at any point.",
        "",
        "## 1. Frozen inputs",
        "",
        f"- component class SHA-256: `{freeze['selected_component']['class_sha256']}`",
        f"- component module SHA-256: `{freeze['selected_component']['module_sha256']}`",
        f"- development report SHA-256: `{freeze['development_report_sha256']}`",
        "- fragile label: none (zero failing leave-one-source-out folds)",
        "",
        "## 2. Population",
        "",
        f"- split: `{source['split']}`, layouts `{source['layout_indices']}`, selected",
        "  before generation and never by inspecting content",
        f"- sources: {source['source_instances']} ({source['variants_per_source']} variants each),",
        f"  cases: {source['cases']}, scheduled calls: {source['scheduled_calls']},",
        f"  repeats per case: {source['repeats_per_case']}",
        "- generator and converter: byte-unchanged frozen code",
        f"- generator SHA-256: `{source['generator_sha256']}`",
        f"- converter SHA-256: `{source['converter_sha256']}`",
        f"- source manifest SHA-256: `{source['manifest_sha256']}`",
        f"- public population file SHA-256: `{duplication['population_file_sha256']}`",
        f"- provider calls authorized and made: **0**",
        "",
        "## 3. Section-8.3 duplicate and equivalence checks",
        "",
        f"- population hash differs from development: {duplication['population_hash_differs_from_development']}",
        f"- population hash differs from the spent confirmation: {duplication['population_hash_differs_from_spent_confirmation']}",
        f"- case-id sets disjoint from development: {duplication['case_ids_disjoint_from_development']}",
        f"- public-input-hash sets disjoint from development: {duplication['public_input_hashes_disjoint_from_development']}",
        f"- source-episode-id sets disjoint from development: {duplication['source_episode_ids_disjoint_from_development']}",
        f"- layout digests differ: {duplication['layout_digests_differ']}",
        "",
        "Checks against the spent `confirmation_v1_3` population were verified by",
        "construction, not by opening it: the split label, the layout indices, and the",
        "identifier bijection are all disjoint by design, and the spent population was",
        "never opened, read, counted, or characterized.",
        "",
        "## 4. Validation gates",
        "",
        f"- independent public-only answerability: **{answerability['status']}** "
        f"({answerability['case_count']} cases, {answerability['label_count']} labels,",
        f"  label agreement {answerability['label_agreement']}, "
        f"{answerability['transformation_checks']} transformation checks,",
        f"  hidden-data invariance {answerability['hidden_data_invariance']}, "
        f"deterministic replay {answerability['deterministic_replay']})",
        f"- public-only firewall audit: **{firewall['status']}**",
    ]
    lines += [f"  - {name}: {item['status']}" for name, item in firewall["checks"].items()]
    lines += [
        "",
        "## 5. One-shot oracle evaluation",
        "",
        "Exactly one evaluation was run, after both validation gates passed, on the",
        "eight canonical confirmation entries.",
        "",
        "| gate | requirement | result |",
        "| --- | --- | --- |",
        gate_rows,
        "",
        f"- canonical cases: {oracle['canonical_case_count']}",
        f"- top-1: **{oracle['canonical_aggregate']['top1']}**",
        f"- top-2: **{oracle['canonical_aggregate']['top2']}**",
        f"- mean normalized regret: **{oracle['canonical_aggregate']['mean_normalized_regret']:.6f}**",
        f"- illegal target/value count: {oracle['canonical_aggregate']['illegal_target_count']}",
        f"- section-14 equivalence: {oracle['section_14_equivalence']['pair_count']} pairs, "
        f"{len(oracle['section_14_equivalence']['failures'])} failures",
        f"- own-selection equivariance: "
        f"{oracle['own_selection_equivalence']['selection_pass']}/"
        f"{oracle['own_selection_equivalence']['selection_total']}",
        f"- **outcome: `{oracle['status']}`**",
        "",
        "Reported-only diagnostics (not gates at confirmation): non-degeneracy "
        f"ND-1 {oracle['non_degeneracy_descriptive_only']['nd1_pass']}, ND-2 "
        f"{oracle['non_degeneracy_descriptive_only']['nd2_pass']}, ND-3 "
        f"{oracle['non_degeneracy_descriptive_only']['nd3_pass']}; "
        f"`longest_artifact` top-1 {oracle['longest_artifact_descriptive_only']['top1']}, "
        f"top-2 {oracle['longest_artifact_descriptive_only']['top2']}, regret "
        f"{oracle['longest_artifact_descriptive_only']['mean_normalized_regret']:.6f}; "
        f"leave-one-source-out failing folds "
        f"{oracle['leave_one_source_out_descriptive_only']['failing_fold_count']}.",
        "",
        "## 6. Claim boundary",
        "",
        "The confirmed claim is the compatibility claim of preregistration section",
        "10.1 on a newly frozen untouched confirmation population: under the fixed",
        "instrument, the named component meets the existing engineering gate on those",
        "instances using only authorized public semantic outputs. It remains a claim",
        "about a component and an instrument. It is not general authorization",
        "reasoning, adaptive routing, SER architecture superiority, GitLab or",
        "real-world transfer, model capability, validation of the instrument, a",
        "diagnosis of the earlier confirmation failure, or promotion of any concept.",
        "",
        "## 7. Seal",
        "",
        f"- sealed: {seal['sealed']} (after the one-shot evaluation: {seal['sealed_after_oracle']})",
        f"- population hash: `{seal['population_hash']}`",
        f"- seal SHA-256: `{seal['seal_sha256']}`",
        f"- oracle status recorded at seal: `{seal['oracle_status']}`",
        "",
        "Not authorized and not performed: any further evaluation of this population,",
        "any replacement population, any threshold or semantic change, any model or",
        "provider inference, Jev, and adaptive-routing experiments.",
        "",
    ]
    (OUT / "REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    return {"report": "experiments/authzgym_confirmation_v1_3_1/REPORT.md",
            "oracle_status": oracle["status"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=tuple(STAGES), required=True)
    args = parser.parse_args()
    result = STAGES[args.stage]()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not isinstance(result, dict) or result.get("status", "pass") != "fail" else 1


if __name__ == "__main__":
    raise SystemExit(main())
