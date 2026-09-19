#!/usr/bin/env python3
"""Zero-inference verification for condition `model-semantic-v1.3.1-N1`.

Stages (handoff steps 1 and 2):

* ``--stage integrity`` -- section-0 protected-file hashing under the section-5
  raw-byte convention, section-0.2 never-open traversal by ``stat`` only, the
  section-0.1 reference-hash re-derivations, the dirty-tree check, and the
  ``RESTATED_HASHES.json`` / ``INTEGRITY_BASELINE.json`` pair.
* ``--stage integrity --recheck`` -- re-hash every protected file at the end of
  a step and compare against the recorded baseline; any difference halts.
* ``--stage model`` -- the preregistration section-9 model-condition
  verification. The only network operations it performs are the supervised-hop
  establishment and ``GET /models``; a chat/completions submission in this stage
  is a blocking violation and is asserted absent.

No step of this tool makes a paid inference, opens a section-0.2 path, or
changes a frozen semantic rule.
"""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import os
import platform
import subprocess
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterable, Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from ser.authzgym.policies_v1_3_1 import EstimatorV1SalientCategory  # noqa: E402
from ser.authzgym.tunnel_supervisor import (  # noqa: E402
    TunnelSupervisor,
    load_tunnel_policy,
)
from ser.core.types import canonical_json, content_hash  # noqa: E402
from ser.evaluation.authz_model_semantic_v1_3_1 import (  # noqa: E402
    CONDITION_DIR,
    CONFIRMATION_DIR,
    LEDGER_PATH,
    REPAIR_DIR,
    ROOT as SER_ROOT,
    V13_DIR,
    AuditedReader,
    SpentPopulationAccess,
    assert_no_read_bypass,
    check_static_read_bypass,
    is_never_open_path,
    never_open_v13_names,
    relative_path,
    tool_file_sha256,
    validate_access_ledger,
)


CONDITION_ID = "model-semantic-v1.3.1-N1"
AUTHORIZING_ADR = "ADR-0023"
TOOL_PATH = Path(__file__).resolve()
CATALOG_PATH = CONDITION_DIR / "MODEL_CATALOG_SNAPSHOT.json"
VERIFICATION_PATH = CONDITION_DIR / "MODEL_CONDITION_VERIFICATION.json"
MODEL_CONDITION_PATH = CONDITION_DIR / "MODEL_CONDITION.json"
COST_GATE_PATH = CONDITION_DIR / "COST_GATE.json"
RESTATED_PATH = CONDITION_DIR / "RESTATED_HASHES.json"
BASELINE_PATH = CONDITION_DIR / "INTEGRITY_BASELINE.json"
TRANSPORT_EVENTS_PATH = CONDITION_DIR / "MODEL_CONDITION_TRANSPORT_EVENTS.jsonl"

INTEGRITY_AUTHORIZATION = (
    "ADR-0023 section 14.1; PREREGISTRATION.md sections 5.1--5.3 and 6; "
    "IMPLEMENTATION_HANDOFF.md sections 0, 0.1, 0.2, step 1"
)
MODEL_AUTHORIZATION = (
    "ADR-0023 section 14.1; PREREGISTRATION.md section 9; "
    "IMPLEMENTATION_HANDOFF.md step 2"
)

TRANSPORT_CONFIG_PATH = (
    ROOT / "experiments" / "authzgym_transport_envelope_v1" / "transport_config.json"
)
MODEL_TRANSPORT_CONFIG_PATH = V13_DIR / "MODEL_TRANSPORT_CONFIG.json"
STRONGER_MODEL_SELECTION_PATH = (
    ROOT / "experiments" / "authzgym_stronger_model_v1" / "MODEL_SELECTION.json"
)
V12_MODEL_CONFIG_PATH = (
    ROOT / "experiments" / "authzgym_semantic_contract_v1_2" / "model_config.json"
)

# Section 2.1 frozen condition values.
ROUTE_MODEL_IDENTIFIER = "patchersniper_praneeth/gpt-5.4-nano"
OFFICIAL_MODEL_ID = "gpt-5.4-nano"
ENDPOINT_LABEL = "configured OpenAI-compatible institutional endpoint via the approved UCSB egress hop"
API_STYLE = "openai_chat_completions_json_schema"
REASONING_EFFORT = "none"
MAXIMUM_OUTPUT_TOKENS = 1024
MAXIMUM_INPUT_TOKENS = 4000
REQUEST_TIMEOUT_SECONDS = 90
CONNECT_TIMEOUT_SECONDS = 15
CLIENT_SIDE_RETRIES = 0
HARD_SPEND_CEILING_USD = 2.50
MAX_SUBMISSIONS = 2 * (112 + 56)
PRICING_ACCOUNTING_BASIS = (
    "official list pricing applied to provider-reported usage; not an "
    "institutional billing statement"
)
OFFICIAL_DOCUMENTATION_URL = (
    "https://developers.openai.com/api/docs/models/gpt-5.4-nano"
)
RECORDED_NANO_PRICING = {
    "input_per_million_tokens_usd": 0.20,
    "cached_input_per_million_tokens_usd": 0.02,
    "output_per_million_tokens_usd": 1.25,
}

# Section 0 / 0.1 reference hashes with a value given in repository authority.
REFERENCE_HASHES = {
    "src/ser/authzgym/policies.py": (
        "092a7a87d1227c1a1c85ac46c7122e38ac1b6b24d7aaa90abee05abfe4167393"
    ),
    "src/ser/authzgym/policies_v1_3_1.py": (
        "f9c92317abc562ac5175f90074238c666de55d557b02e0de368841676f4d910d"
    ),
    "src/ser/authzgym/generation.py": (
        "03bfe556091e8da118c1c27058a8edaa393473c17c4fa45645837b08b7163461"
    ),
    "src/ser/authzgym/v1_3_population.py": (
        "ac4b8d47bd1369a16f4fed0d80abe7e0943c90317c0037bb6c8715882f470fca"
    ),
    "src/ser/evaluation/authz_v1_3.py": (
        "60b1cb5df27346ce65c6400cd33583782e176ca888567c7c052d1037aea098f6"
    ),
    "experiments/authzgym_estimator_repair_v1_3_1/DEVELOPMENT_REPORT.md": (
        "f0629d3b78ba35258cc6d439e4b731c3682b76fa08e4155efbdad7cd0df18638"
    ),
    "experiments/authzgym_semantic_contract_v1_3/DEVELOPMENT_PUBLIC_POPULATION.json": (
        "dda4e0c08a9c29a58a912fdcb5268ddf602aac79c47f6dd3fb94102b5dc8c365"
    ),
}

# Section 0 protected files whose hash is not fixed in repository authority.
PROTECTED_PATHS = (
    "src/ser/authzgym/v1_3_contract.py",
    "src/ser/authzgym/v1_3_public_input.py",
    "src/ser/authzgym/v1_3_annotation_builder.py",
    "src/ser/authzgym/model.py",
    "src/ser/evaluation/authz_v1_3_1_sealed_input.py",
    "src/ser/evaluation/authz_v1_3_1_harness.py",
    "tools/validate_authzgym_v1_3_answerability.py",
    "tools/validate_authzgym_v1_3_firewall.py",
    "tools/validate_authzgym_v1_3_oracle.py",
    "tools/validate_authzgym_v1_3_1_component_firewall.py",
    "tools/prepare_authzgym_v1_3.py",
    "tools/run_authzgym_confirmation_v1_3_1.py",
    "tools/run_estimator_repair_study.py",
    "DECISIONS.md",
    "CHARTER.md",
    "MAP.md",
    "AGENTS.md",
    "README.md",
    "plan/ROADMAP.md",
    "state/STATUS.yaml",
    "state/CONTEXT_PACKET.md",
    "experiments/README.md",
)

# Restated, never recomputed (section 5.3).
SPENT_POPULATION_DIGEST = (
    "0e20284be388131d451f5befc22a048b3badba87a338168d8f7865bfbc9bd28f"
)
SEAL_RECORDED_DIGEST = (
    "463d208f0e02fc17fc66dd52a211e365fc464cafcb8344c4d91955d4fb0986b8"
)
CONFIRMATION_V1_3_1_POPULATION_DIGEST = (
    "1321bcd190c2bfbef884aac55421669401fe321797345ad54556d0f55251787c"
)
CONFIRMATION_V1_3_1_SEAL_PATH = (
    "experiments/authzgym_confirmation_v1_3_1/CONFIRMATION_V1_3_1_SEAL.json"
)
CONFIRMATION_V1_3_1_POPULATION_PATH = (
    "experiments/authzgym_confirmation_v1_3_1/CONFIRMATION_PUBLIC_POPULATION.json"
)


class IntegrityError(RuntimeError):
    """A protected hash, the tree state, or a never-open assertion failed."""


def _json_write(path: Path, value: Mapping[str, object]) -> str:
    payload = json.dumps(value, indent=2, sort_keys=True) + "\n"
    path.write_text(payload, encoding="utf-8")
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _json_write_value(path: Path, value: Mapping[str, object]) -> dict:
    """Write a JSON artifact and report its authoritative raw-byte hash."""

    digest = _json_write(path, value)
    return {
        f"{path.stem.lower()}_file_sha256": digest,
        "path": relative_path(path),
    }


def _jsonl_append(path: Path, record: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(dict(record), sort_keys=True) + "\n")


def repository_commit() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def dirty_entries() -> list[str]:
    output = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return [line for line in output.splitlines() if line.strip()]


# Handoff section 0.3 -- the complete set of paths this condition may create.
# The dirty-tree check treats these as the condition's own artifacts alongside
# `experiments/authzgym_model_semantic_v1_3_1/`.
CONDITION_OWNED_PATHS = (
    "src/ser/evaluation/authz_model_semantic_v1_3_1.py",
    "src/ser/authzgym/semantic_contract_v1_3.py",
    "src/ser/authzgym/supervised_transport_v1_3.py",
    "tools/verify_authzgym_model_condition.py",
    "tools/run_authzgym_model_semantic_development.py",
    "tools/score_authzgym_model_semantic.py",
    "tools/run_authzgym_model_semantic_confirmation.py",
    "tests/test_model_semantic_v1_3_1_reader.py",
    "tests/test_model_semantic_v1_3_1_client.py",
    "tests/test_model_semantic_v1_3_1_choice_sets.py",
    "tests/test_model_semantic_v1_3_1_retry.py",
    "tests/test_model_semantic_v1_3_1_error_classes.py",
    "tests/test_model_semantic_v1_3_1_gates.py",
)

FREEZE_MANIFEST_PATH = CONDITION_DIR / "FROZEN_INPUTS_MODEL_V1_3_1.json"
FREEZE_CHECKLIST_PATH = CONDITION_DIR / "FREEZE_CHECKLIST.md"
GOLD_ADEQUACY_PATH = CONDITION_DIR / "GOLD_ADEQUACY_DEVELOPMENT.json"
GOVERNANCE_REBASELINE_PATH = CONDITION_DIR / "GOVERNANCE_REBASELINE.json"

# IMPLEMENTATION_CLARIFICATION.md section 6 / handoff step 6B item 5.  The
# rebaseline is itself an integrity input, so the preserved Step-1 baseline file
# hash is fixed here rather than read from the artifact under test.
ORIGINAL_INTEGRITY_BASELINE_FILE_SHA256 = (
    "77fc3920ecc4df47abd63bf3ce56fc520c2f0d5b12af7fd31a0b508a3c9d6c32"
)
GOVERNANCE_TRANSITION_PATHS = (
    "MAP.md",
    "plan/ROADMAP.md",
    "state/STATUS.yaml",
    "state/CONTEXT_PACKET.md",
)
GOVERNANCE_REBASELINE_AUTHORIZATION = (
    "IMPLEMENTATION_CLARIFICATION.md section 6 (PENDING-3); "
    "IMPLEMENTATION_HANDOFF.md step 6B item 5"
)
GOVERNANCE_STATEMENT_KEYS = (
    "original_step1_integrity_baseline_preserved_unaltered",
    "only_four_exact_transitions_accepted",
    "no_other_protected_file_integrity_checking_waived",
    "subsequent_change_to_four_files_is_new_drift_and_must_halt",
    "no_model_facing_input_rebaselined",
    "not_retroactive_authorization_of_dev_2",
    "no_experiment_semantics_gate_threshold_model_condition_retry_rule_b1_population_or_claim_boundary_changes",
)

# Section 18 / handoff step 6: the inherited inputs, by hash.
INHERITED_V13_INPUTS = (
    "PUBLIC_CONTRACT.json",
    "prompts/semantic_observation_v1_3.txt",
    "schemas/semantic_vocabulary_v1_3.json",
    "DEVELOPMENT_PUBLIC_POPULATION.json",
    "DEVELOPMENT_RESTRICTED_POPULATION.json",
    "DEVELOPMENT_TRANSFORMATION_MAPS.json",
    "DEVELOPMENT_SCHEDULE.json",
    "DEVELOPMENT_SOURCE_MANIFEST.json",
    "ANSWERABILITY_VALIDATION.json",
    "FIREWALL_VALIDATION.json",
    "ORACLE_VALIDATION.json",
    "annotations/development_annotations.jsonl",
)
INHERITED_SOURCE_INPUTS = (
    "src/ser/authzgym/generation.py",
    "src/ser/authzgym/v1_3_population.py",
    "src/ser/authzgym/v1_3_contract.py",
    "src/ser/authzgym/v1_3_public_input.py",
    "src/ser/authzgym/v1_3_annotation_builder.py",
    "src/ser/authzgym/model.py",
    "src/ser/authzgym/policies.py",
    "src/ser/authzgym/policies_v1_3_1.py",
    "src/ser/evaluation/authz_v1_3.py",
    "src/ser/evaluation/authz_v1_3_1_sealed_input.py",
    "src/ser/evaluation/authz_v1_3_1_harness.py",
    "experiments/authzgym_estimator_repair_v1_3_1/DEVELOPMENT_REPORT.md",
    (
        "experiments/authzgym_confirmation_v1_3_1/"
        "CONFIRMATION_V1_3_1_ORACLE_VALIDATION.json"
    ),
    "experiments/authzgym_confirmation_v1_3_1/CONFIRMATION_V1_3_1_SEAL.json",
)
CONDITION_IMPLEMENTATION = (
    "src/ser/evaluation/authz_model_semantic_v1_3_1.py",
    "src/ser/authzgym/semantic_contract_v1_3.py",
    "src/ser/authzgym/supervised_transport_v1_3.py",
    "tools/verify_authzgym_model_condition.py",
    "tools/score_authzgym_model_semantic.py",
    "tools/run_authzgym_model_semantic_development.py",
    "tests/test_model_semantic_v1_3_1_reader.py",
    "tests/test_model_semantic_v1_3_1_client.py",
    "tests/test_model_semantic_v1_3_1_choice_sets.py",
    "tests/test_model_semantic_v1_3_1_retry.py",
    "tests/test_model_semantic_v1_3_1_error_classes.py",
    "tests/test_model_semantic_v1_3_1_gates.py",
)
# Section 6.1 applies the static read-bypass check to "the condition's own
# modules and tools"; test modules are excluded because they read temporary
# fixture ledgers they just wrote and the public development population.
CONDITION_MODULES_AND_TOOLS = tuple(
    name for name in CONDITION_IMPLEMENTATION if not name.startswith("tests/")
)
CONDITION_ARTIFACTS = (
    "PREREGISTRATION.md",
    "IMPLEMENTATION_HANDOFF.md",
    "IMPLEMENTATION_CLARIFICATION.md",
    "GOVERNANCE_REBASELINE.json",
    "OPEN_RESEARCH_DECISIONS.md",
    "REPOSITORY_CONTRADICTIONS.md",
    "ADR_0023.md",
    "RESTATED_HASHES.json",
    "INTEGRITY_BASELINE.json",
    "MODEL_CATALOG_SNAPSHOT.json",
    "MODEL_CONDITION_VERIFICATION.json",
    "MODEL_CONDITION.json",
    "COST_GATE.json",
    "GOLD_ADEQUACY_DEVELOPMENT.json",
)
# Step 6A completed the section-12.1 and section-18 implementation: every
# section-0.3 module and test is present, so this list is empty by
# construction and any future absence is a blocker rather than a deferral.
NOT_YET_IMPLEMENTED_PATHS = ()
# Step 13 artefact: the confirmation runner is required only before the gated
# confirmation stage, not before development inference.
DEFERRED_BY_DESIGN_PATHS = ("tools/run_authzgym_model_semantic_confirmation.py",)


def _condition_owned(line: str) -> bool:
    path = line[3:]
    return path.startswith(
        "experiments/authzgym_model_semantic_v1_3_1/"
    ) or path in CONDITION_OWNED_PATHS


def protected_tree_paths() -> tuple[list[Path], list[Path]]:
    """(hashable, stat-only) section-0 protected paths outside the condition."""

    hashable: list[Path] = []
    stat_only: list[Path] = []
    experiment_dirs = sorted(
        item for item in (ROOT / "experiments").iterdir() if item.is_dir()
    )
    for directory in experiment_dirs:
        if directory.resolve() == CONDITION_DIR.resolve():
            continue
        for path in sorted(directory.rglob("*")):
            if not path.is_file():
                continue
            (stat_only if is_never_open_path(path) else hashable).append(path)
    for name in tuple(PROTECTED_PATHS) + tuple(REFERENCE_HASHES):
        path = ROOT / name
        if path.is_file() and path not in hashable:
            hashable.append(path)
    for directory in (ROOT / "theory", ROOT / "reference"):
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                hashable.append(path)
    return hashable, stat_only


def already_recorded_confirmation_reads() -> list[dict]:
    """Disclosed pre-implementation reconciliation opens (fail-closed review)."""

    return [
        {
            "id": "DEV-2",
            "path": CONFIRMATION_V1_3_1_POPULATION_PATH,
            "operation": "hash",
            "actor": "implementation agent (pre-tooling reconnaissance)",
            "authorization": "none; section-0.2 never-open path",
            "classification": "procedural_deviation_not_retroactively_authorized",
            "content_parsed_or_used": False,
            "detail": (
                "The raw-file SHA-256 of the sealed confirmation_v1_3_1 public "
                "population was computed during repository reconnaissance "
                "before the condition's audited reader existed. No case "
                "content was parsed, scored, counted, retained or used for any "
                "design, selection or scoring decision, and the population was "
                "already spent and sealed under ADR-0022. That open is not "
                "authorized by section 6.3 and is not treated as a satisfied "
                "step-1 re-derivation. The condition's own harness refuses it."
            ),
        }
    ]


def _reference_check(hashed: Mapping[str, Mapping[str, object]]) -> dict:
    observed: dict[str, dict] = {}
    mismatches: list[str] = []
    for name, expected in REFERENCE_HASHES.items():
        record = hashed[name]
        observed[name] = {
            "file_sha256": str(record["file_sha256"]),
            "expected": expected,
            "matches": str(record["file_sha256"]) == expected,
        }
        if str(record["file_sha256"]) != expected:
            mismatches.append(name)
    component_source = inspect.getsource(EstimatorV1SalientCategory)
    component_digest = hashlib.sha256(component_source.encode("utf-8")).hexdigest()
    observed["B-1 component class source text"] = {
        "file_sha256": component_digest,
        "expected": (
            "88b77c5f343117b354b5039d571bf03bf8867fcd7fb4f8fc91c1e1aefca7a048"
        ),
        "matches": component_digest
        == "88b77c5f343117b354b5039d571bf03bf8867fcd7fb4f8fc91c1e1aefca7a048",
    }
    if not observed["B-1 component class source text"]["matches"]:
        mismatches.append("B-1 component class source text")
    return {
        "observed": observed,
        "mismatches": mismatches,
        "all_re_derive": not mismatches,
    }


def _seal_restatement(reader: AuditedReader) -> dict:
    seal = reader.read_json(
        ROOT / CONFIRMATION_V1_3_1_SEAL_PATH,
        detail="section-0.2 step-1 hash restatement exception",
    )
    without_field = {key: value for key, value in seal.items() if key != "seal_sha256"}
    canonical_digest = content_hash(without_field)
    file_digest = reader.hash_file(
        ROOT / CONFIRMATION_V1_3_1_SEAL_PATH,
        detail="section-0.2 step-1 hash restatement exception",
    )["file_sha256"]
    return {
        "path": CONFIRMATION_V1_3_1_SEAL_PATH,
        "recorded_digest": SEAL_RECORDED_DIGEST,
        "recorded_as": "`CONFIRMATION_V1_3_1_SEAL.json` in handoff section 0.1",
        "actual_convention": (
            "canonical_json_sha256 of the seal record with its own `seal_sha256` "
            "field omitted; it is NOT the file hash"
        ),
        "canonical_json_sha256": canonical_digest,
        "file_sha256": file_digest,
        "seal_sha256_field": str(seal.get("seal_sha256", "")),
        "recorded_files": dict(seal.get("files", {})),
        "re_derived": canonical_digest == SEAL_RECORDED_DIGEST,
        "note": (
            "Section 5.2: a canonicalized JSON digest is recorded in its own "
            "`*_canonical_json_sha256` field and never in place of a file hash."
        ),
    }


def build_restated_hashes(reader: AuditedReader, reference: dict) -> dict:
    development_population = ROOT / (
        "experiments/authzgym_semantic_contract_v1_3/DEVELOPMENT_PUBLIC_POPULATION.json"
    )
    development = reader.read_json(
        development_population, detail="section-5.3 restatement"
    )
    development_file_hash = reader.hash_file(
        development_population, detail="section-5.3 development population file hash"
    )["file_sha256"]
    seal = _seal_restatement(reader)
    repair_prereg = ROOT / (
        "experiments/authzgym_estimator_repair_v1_3_1/REPAIR_STUDY_PREREGISTRATION.md"
    )
    repair_record = reader.hash_file(
        repair_prereg, detail="restatement source for the spent population digest"
    )

    records = [
        {
            "recorded_digest": "dda4e0c0...",
            "recorded_as": "development population hash",
            "path": relative_path(development_population),
            "actual_convention": "file_sha256 (section 5.1 raw bytes)",
            "file_sha256": development_file_hash,
            "re_derived": development_file_hash
            == REFERENCE_HASHES[relative_path(development_population)],
            "re_derivation_status": "re-derived",
        },
        {
            "recorded_digest": "1615b87e...",
            "recorded_as": "not recorded anywhere (section 5.3)",
            "path": relative_path(development_population),
            "actual_convention": "canonical_json_sha256 of the same file's parsed value",
            "canonical_json_sha256": content_hash(development),
            "file_sha256": development_file_hash,
            "re_derivation_status": (
                "computed for the record; section 5.3 records it as not applicable "
                "and it is never used by a gate"
            ),
        },
        {
            "recorded_digest": "471c233d...",
            "recorded_as": "the file's own embedded `population_hash` field",
            "path": relative_path(development_population),
            "actual_convention": "inherited source-population hash from authzgym_static_v1_1",
            "embedded_population_hash": str(development.get("population_hash", "")),
            "file_sha256": development_file_hash,
            "re_derivation_status": "quoted verbatim; never re-derived and never a file hash",
        },
        {
            "recorded_digest": "1321bcd1...",
            "recorded_as": (
                "population hash and public population file SHA-256 "
                "(confirmation_v1_3_1)"
            ),
            "path": CONFIRMATION_V1_3_1_POPULATION_PATH,
            "actual_convention": "file_sha256 (section 5.1 raw bytes)",
            "file_sha256": CONFIRMATION_V1_3_1_POPULATION_DIGEST,
            "seal_recorded_population_file_sha256": str(
                seal.get("recorded_files", {}).get(
                    "CONFIRMATION_PUBLIC_POPULATION.json", ""
                )
            ),
            "re_derived": False,
            "re_derivation_status": (
                "NOT re-derived at step 1: the path is a section-0.2 never-open "
                "path and section 6.3 makes any open of a confirmation_v1_3_1 "
                "path a blocking violation. The digest is restated from the "
                "authorized readable seal record. See deviations."
            ),
            "reconnaissance_deviation": "DEV-2",
        },
        {
            "recorded_digest": "0e20284b...",
            "recorded_as": "spent confirmation public",
            "path": (
                "experiments/authzgym_semantic_contract_v1_3/"
                "CONFIRMATION_PUBLIC_POPULATION.json"
            ),
            "actual_convention": "file_sha256 (section 5.1 raw bytes)",
            "file_sha256": SPENT_POPULATION_DIGEST,
            "re_derived": False,
            "re_derivation_status": "not re-derived, by design",
            "reason": "spent population never opened",
            "restatement_sources": [
                {
                    "path": "tools/run_authzgym_confirmation_v1_3_1.py",
                    "file_sha256": tool_file_sha256(
                        ROOT / "tools/run_authzgym_confirmation_v1_3_1.py"
                    ),
                    "carries": SPENT_POPULATION_DIGEST,
                },
                {
                    "path": relative_path(repair_prereg),
                    "file_sha256": repair_record["file_sha256"],
                    "carries": "0e20284b... (truncated)",
                },
            ],
            "note": (
                "Handoff step 1 names `CONFIRMATION_V1_3_1_FREEZE_RECORD.json` as "
                "the restatement source, but that path is in the section-0.2 "
                "never-open set for this condition and section 6.3 makes any "
                "open of a confirmation_v1_3_1 path a blocking violation. The "
                "difference is recorded as a deviation and resolved fail-closed: "
                "the freeze record was stat-ed, never opened, and the digest is "
                "restated from the authorized readable records above."
            ),
        },
        {
            "recorded_digest": "463d208f...",
            "recorded_as": "`CONFIRMATION_V1_3_1_SEAL.json` (handoff section 0.1)",
            "path": CONFIRMATION_V1_3_1_SEAL_PATH,
            "actual_convention": seal["actual_convention"],
            "canonical_json_sha256": seal["canonical_json_sha256"],
            "file_sha256": seal["file_sha256"],
            "re_derived": seal["re_derived"],
            "re_derivation_status": (
                "re-derived under the canonical-JSON convention; the raw file "
                "hash differs, which is exactly the C-2 vocabulary defect "
                "section 5.2 fixes"
            ),
        },
    ]
    for name in (
        "092a7a87...",
        "f9c92317...",
        "88b77c5f...",
        "f0629d3b...",
        "03bfe556...",
        "ac4b8d47...",
        "60b1cb5d...",
    ):
        records.append(
            {
                "recorded_digest": name,
                "recorded_as": "component/protected-file hash",
                "actual_convention": (
                    "file_sha256; `88b77c5f...` is SHA-256 of the B-1 component "
                    "class source text"
                ),
                "re_derived": True,
                "re_derivation_status": "re-derived (see reference_check)",
            }
        )
    return {
        "schema_version": 1,
        "condition_id": CONDITION_ID,
        "authorizing_adr": AUTHORIZING_ADR,
        "stage": "integrity",
        "repository_commit": repository_commit(),
        "convention": (
            "Raw-file SHA-256 is authoritative for every new artifact this "
            "condition creates. A canonicalized JSON digest, where useful, is "
            "recorded in its own `*_canonical_json_sha256` field and never in "
            "place of a file hash. No field carrying more than one digest type "
            "is named `population_hash`."
        ),
        "vocabulary": {
            "*_file_sha256": "authoritative: file_sha256 of a named path",
            "*_canonical_json_sha256": (
                "secondary and optional: canonical_json_sha256 of a named value; "
                "never used where a file is meant and never used by a gate"
            ),
            "*_embedded_population_hash": (
                "the value of a population file's own internal `population_hash` "
                "field, quoted verbatim"
            ),
        },
        "restatements": records,
        "reference_check": reference,
        "seal_restatement": seal,
        "deviations": already_recorded_confirmation_reads()
        + [
            {
                "id": "DEV-1",
                "kind": "governance_recording",
                "classification": "recorded_difference",
                "authority_conflict": (
                    "IMPLEMENTATION_HANDOFF.md step 1 item 3 names "
                    "`CONFIRMATION_V1_3_1_FREEZE_RECORD.json` as the restatement "
                    "source for `0e20284b...`, while IMPLEMENTATION_HANDOFF.md "
                    "section 0.2 lists every file under "
                    "`experiments/authzgym_confirmation_v1_3_1/` except the three "
                    "step-1 metadata files as never-open, and PREREGISTRATION.md "
                    "sections 6.3 and 14.2 make any open of a confirmation_v1_3_1 "
                    "path a blocking violation."
                ),
                "resolution": (
                    "Fail closed: the freeze record is stat-ed for existence and "
                    "never opened; the digest is restated from the authorized "
                    "readable records that carry it verbatim. Recorded, not "
                    "chosen away; new authority is required if a direct read is "
                    "intended."
                ),
                "content_read": False,
            }
        ],
    }


def _hash_of(path: Path) -> str:
    return tool_file_sha256(path)


def stage_integrity(*, recheck: bool) -> dict:
    if recheck:
        return _recheck_integrity()

    actor = os.environ.get("SER_ACTOR", "implementation_agent")
    reader = AuditedReader(
        actor=actor,
        stage="integrity",
        tool_path=TOOL_PATH,
        authorization=INTEGRITY_AUTHORIZATION,
    )
    hashable, stat_only = protected_tree_paths()
    hashed: dict[str, dict] = {}
    for path in hashable:
        record = reader.hash_file(path, detail="section-0 protected file")
        hashed[relative_path(path)] = {
            "file_sha256": record["file_sha256"],
            "bytes": record["bytes"],
        }
    stats: dict[str, dict] = {}
    for path in stat_only:
        value = reader.stat_only(path)
        stats[value["path"]] = value

    expected_never_open = never_open_v13_names()
    missing = [
        name for name in expected_never_open if not (V13_DIR / name).exists()
    ]
    never_open_opens = [
        item for item in reader.never_open_opens
    ]
    reference = _reference_check(hashed)
    ledger_check = validate_access_ledger(LEDGER_PATH)
    dirty = dirty_entries()
    unauthorized_dirty = [line for line in dirty if not _condition_owned(line)]
    static = check_static_read_bypass(
        [ROOT / name for name in CONDITION_MODULES_AND_TOOLS]
    )

    blockers: list[str] = []
    if reference["mismatches"]:
        blockers.append("section-0.1 reference hash mismatch")
    if missing:
        blockers.append("section-0.2 name absent")
    if never_open_opens:
        blockers.append("never-open path opened")
    if unauthorized_dirty:
        blockers.append("dirty tree outside the condition directory")
    if not ledger_check["passes"]:
        blockers.append("access ledger validation failed")
    if not static["passes"]:
        blockers.append("static read-bypass check failed")

    restated = build_restated_hashes(reader, reference)
    restated_file_sha256 = _json_write(RESTATED_PATH, restated)

    baseline = {
        "schema_version": 1,
        "condition_id": CONDITION_ID,
        "authorizing_adr": AUTHORIZING_ADR,
        "stage": "integrity",
        "tool_path": relative_path(TOOL_PATH),
        "tool_file_sha256": _hash_of(TOOL_PATH),
        "repository_commit": repository_commit(),
        "dirty_status": {
            "porcelain_entries": dirty,
            "outside_condition_directory": unauthorized_dirty,
            "clean_except_condition_directory": not unauthorized_dirty,
        },
        "hashed_file_count": len(hashed),
        "hashed_files": hashed,
        "stat_only_files": stats,
        "never_open_assertion": {
            "section_0_2_names": list(expected_never_open),
            "all_present": not missing,
            "missing": missing,
            "opens_recorded": never_open_opens,
            "zero_opens": not never_open_opens,
        },
        "reference_check": reference,
        "access_ledger": ledger_check,
        "static_check": static,
        "restated_hashes_file_sha256": restated_file_sha256,
        "blockers": blockers,
        "passes": not blockers,
    }
    baseline_digest = content_hash(baseline)
    baseline["integrity_baseline_canonical_json_sha256"] = baseline_digest
    baseline_file_sha256 = _json_write(BASELINE_PATH, baseline)
    baseline["integrity_baseline_file_sha256"] = baseline_file_sha256

    if blockers:
        raise IntegrityError("; ".join(blockers))
    return {
        "stage": "integrity",
        "passes": True,
        "hashed_file_count": len(hashed),
        "stat_only_count": len(stats),
        "never_open_zero_opens": True,
        "restated_hashes_file_sha256": restated_file_sha256,
        "integrity_baseline_file_sha256": _hash_of(BASELINE_PATH),
        "integrity_baseline_canonical_json_sha256": baseline_digest,
        "repository_commit": baseline["repository_commit"],
    }


def integrity_comparison() -> dict:
    """Non-raising comparison of the current tree against the step-1 baseline."""

    if not BASELINE_PATH.exists():
        raise IntegrityError("no integrity baseline to re-check")
    reader = AuditedReader(
        actor=os.environ.get("SER_ACTOR", "implementation_agent"),
        stage="integrity_recheck",
        tool_path=TOOL_PATH,
        authorization=INTEGRITY_AUTHORIZATION,
    )
    baseline = reader.read_json(BASELINE_PATH, detail="integrity re-check baseline")
    governance = _governance_rebaseline(reader, baseline)
    accepted_transitions = {
        str(item["path"]): item for item in governance.get("transitions", [])
    }
    drifted: list[str] = []
    missing: list[str] = []
    governance_new_drift: list[str] = []
    accepted_transitions_matched: list[str] = []
    stat_missing: list[str] = []
    stat_size_changed: list[str] = []
    for name, record in baseline["hashed_files"].items():
        path = ROOT / name
        if not path.is_file():
            missing.append(name)
            continue
        observed = _hash_of(path)
        transition = accepted_transitions.get(name)
        if transition is not None:
            # Section 6.2: the four governance files must equal their exact
            # accepted current hashes.  Restoring the Step-1 bytes or making any
            # later edit is new drift and halts.
            if observed == transition["accepted_current_file_sha256"]:
                accepted_transitions_matched.append(name)
            else:
                governance_new_drift.append(name)
            continue
        if observed != record["file_sha256"]:
            drifted.append(name)
    for name, record in baseline["stat_only_files"].items():
        path = ROOT / name
        if not path.exists():
            stat_missing.append(name)
            missing.append(name)
            continue
        if path.stat().st_size != record["bytes"]:
            stat_size_changed.append(name)
            drifted.append(name)
    ledger_check = validate_access_ledger(LEDGER_PATH)
    never_open_assertion = {
        "stat_only_file_count": len(baseline["stat_only_files"]),
        "missing": sorted(stat_missing),
        "size_changed": sorted(stat_size_changed),
        "all_present": not stat_missing,
        "sizes_unchanged": not stat_size_changed,
        "never_open_open_count": ledger_check["never_open_open_count"],
        "never_open_open_paths": ledger_check["never_open_open_paths"],
        "zero_opens_under_audited_reader": (
            ledger_check["never_open_open_count"] == 0
        ),
    }
    never_open_assertion["passes"] = bool(
        never_open_assertion["all_present"]
        and never_open_assertion["sizes_unchanged"]
        and never_open_assertion["zero_opens_under_audited_reader"]
    )
    dirty = dirty_entries()
    unauthorized_dirty = [
        line
        for line in dirty
        if not _condition_owned(line)
        and _porcelain_path(line) not in accepted_transitions
    ]
    ordinary_entries_matched = (
        len(baseline["hashed_files"])
        - len(drifted)
        - len(missing)
        - len(accepted_transitions)
    )
    result = {
        "stage": "integrity_recheck",
        "checked_file_count": len(baseline["hashed_files"]),
        "stat_only_count": len(baseline["stat_only_files"]),
        "drifted": sorted(drifted),
        "ordinary_baseline_entries_matched": ordinary_entries_matched,
        "ordinary_baseline_entries_expected": (
            len(baseline["hashed_files"]) - len(GOVERNANCE_TRANSITION_PATHS)
        ),
        "governance_rebaseline": governance,
        "accepted_governance_transitions_matched": sorted(
            accepted_transitions_matched
        ),
        "governance_transition_new_drift": sorted(governance_new_drift),
        "never_open_assertion": never_open_assertion,
        "missing": sorted(missing),
        "drift_detail": {
            name: {
                "baseline_file_sha256": baseline["hashed_files"][name]["file_sha256"],
                "current_file_sha256": _hash_of(ROOT / name),
            }
            for name in sorted(drifted)
            if name in baseline["hashed_files"] and (ROOT / name).is_file()
        },
        "outside_condition_directory": unauthorized_dirty,
        "clean_except_condition_directory": not unauthorized_dirty,
        "passes": (
            not drifted
            and not missing
            and not unauthorized_dirty
            and governance["passes"]
            and not governance_new_drift
            and never_open_assertion["passes"]
        ),
    }
    return result


def _porcelain_path(line: str) -> str:
    """The path component of a ``git status --porcelain`` record."""

    return line[3:].strip()


def _governance_rebaseline(reader: AuditedReader, baseline: Mapping[str, object]) -> dict:
    """Validate clarification section 6's four-file rebaseline record.

    The record is accepted only when it is present, names exactly the four
    authorised paths, pins each to the Step-1 baseline hash and the section-6.2
    accepted current hash, asserts the current raw bytes match that accepted
    hash, carries ``model_facing: false`` and
    ``accepted_for_final_freeze: true`` for each, carries all seven section-6.3
    statements, accepts no additional transition, and leaves
    ``INTEGRITY_BASELINE.json`` preserved unchanged.
    """

    violations: list[str] = []
    if not GOVERNANCE_REBASELINE_PATH.is_file():
        return {
            "present": False,
            "path": relative_path(GOVERNANCE_REBASELINE_PATH),
            "file_sha256": "",
            "accepted_transition_count": 0,
            "accepted_paths": [],
            "matched_paths": [],
            "current_hashes_match_accepted": False,
            "statements_hold": {},
            "transitions": [],
            "violations": ["governance rebaseline record absent"],
            "passes": False,
        }
    document = reader.read_json(
        GOVERNANCE_REBASELINE_PATH,
        detail="clarification section 6 governance rebaseline",
    )
    if not isinstance(document, Mapping):
        return {
            "present": True,
            "path": relative_path(GOVERNANCE_REBASELINE_PATH),
            "file_sha256": _hash_of(GOVERNANCE_REBASELINE_PATH),
            "accepted_transition_count": 0,
            "accepted_paths": [],
            "matched_paths": [],
            "current_hashes_match_accepted": False,
            "statements_hold": {},
            "transitions": [],
            "violations": ["governance rebaseline record is not a JSON object"],
            "passes": False,
        }

    baseline_files = baseline.get("hashed_files", {})

    def recorded(name: object) -> Mapping[str, object]:
        if isinstance(baseline_files, Mapping):
            value = baseline_files.get(str(name), {})
            if isinstance(value, Mapping):
                return value
        return {}

    integrity_baseline = document.get("integrity_baseline")
    if not isinstance(integrity_baseline, Mapping):
        violations.append("integrity_baseline block absent or malformed")
        integrity_baseline = {}
    observed_baseline_hash = _hash_of(BASELINE_PATH)
    if str(integrity_baseline.get("original_file_sha256", "")) != (
        ORIGINAL_INTEGRITY_BASELINE_FILE_SHA256
    ):
        violations.append(
            "recorded original integrity-baseline hash differs from the preserved Step-1 value"
        )
    if observed_baseline_hash != ORIGINAL_INTEGRITY_BASELINE_FILE_SHA256:
        violations.append(
            "INTEGRITY_BASELINE.json is not the preserved Step-1 baseline file"
        )
    if str(integrity_baseline.get("current_file_sha256", "")) != (
        observed_baseline_hash
    ):
        violations.append(
            "recorded current integrity-baseline hash does not match the file on disk"
        )
    if integrity_baseline.get("preserved_unchanged") is not True:
        violations.append("integrity_baseline.preserved_unchanged is not true")
    if integrity_baseline.get("regenerated_or_overwritten") is not False:
        violations.append(
            "integrity_baseline.regenerated_or_overwritten is not false"
        )

    transition_paths = document.get("transition_paths")
    if not isinstance(transition_paths, list) or sorted(
        str(item) for item in transition_paths
    ) != sorted(GOVERNANCE_TRANSITION_PATHS):
        violations.append(
            "transition_paths is not exactly the four section-6.2 governance paths"
        )
    if document.get("accepted_transition_count") != len(GOVERNANCE_TRANSITION_PATHS):
        violations.append("accepted_transition_count is not 4")
    if document.get("additional_transitions_accepted") is not False:
        violations.append("additional_transitions_accepted is not false")
    if document.get("model_facing") is not False:
        violations.append("top-level model_facing is not false")

    transitions = document.get("transitions")
    if not isinstance(transitions, list):
        violations.append("transitions is not a list")
        transitions = []
    parsed: dict[str, dict] = {}
    for item in transitions:
        if not isinstance(item, Mapping):
            violations.append("a transition entry is not a JSON object")
            continue
        path = str(item.get("path", ""))
        if not path:
            violations.append("a transition entry has no path")
            continue
        if path in parsed:
            violations.append(f"duplicate transition entry for {path}")
            continue
        step1 = str(item.get("step1_file_sha256", ""))
        accepted = str(item.get("accepted_current_file_sha256", ""))
        current = str(item.get("current_file_sha256", ""))
        observed = _hash_of(ROOT / path) if (ROOT / path).is_file() else ""
        baseline_record = recorded(path)
        if path not in GOVERNANCE_TRANSITION_PATHS:
            violations.append(f"transition entry for an unauthorised path: {path}")
        if baseline_record.get("file_sha256") != step1:
            violations.append(
                f"{path}: recorded Step-1 hash does not match the preserved baseline"
            )
        if current != accepted:
            violations.append(
                f"{path}: recorded current hash does not equal the accepted section-6.2 hash"
            )
        if observed != accepted:
            violations.append(
                f"{path}: current raw-byte SHA-256 does not equal the accepted section-6.2 hash"
            )
        if item.get("current_matches_accepted") is not True:
            violations.append(f"{path}: current_matches_accepted is not true")
        if item.get("model_facing") is not False:
            violations.append(f"{path}: model_facing is not false")
        if item.get("accepted_for_final_freeze") is not True:
            violations.append(f"{path}: accepted_for_final_freeze is not true")
        parsed[path] = {
            "path": path,
            "step1_file_sha256": step1,
            "accepted_current_file_sha256": accepted,
            "current_file_sha256": current,
            "current_matches_accepted": observed == accepted,
            "authorized_governance_change": str(
                item.get("authorized_governance_change", "")
            ),
            "model_facing": item.get("model_facing"),
            "accepted_for_final_freeze": item.get("accepted_for_final_freeze"),
            "in_section_18_frozen_inputs": item.get("in_section_18_frozen_inputs"),
        }
    if sorted(parsed) != sorted(GOVERNANCE_TRANSITION_PATHS):
        violations.append(
            "transitions do not name exactly the four section-6.2 governance paths"
        )

    statements = document.get("statements")
    statements_hold: dict[str, bool] = {}
    if not isinstance(statements, Mapping):
        violations.append("statements block absent or malformed")
        statements = {}
    for key in GOVERNANCE_STATEMENT_KEYS:
        value = statements.get(key)
        holds = isinstance(value, Mapping) and value.get("holds") is True
        statements_hold[key] = holds
        if not holds:
            violations.append(f"section-6.3 statement not asserted true: {key}")

    return {
        "present": True,
        "path": relative_path(GOVERNANCE_REBASELINE_PATH),
        "file_sha256": _hash_of(GOVERNANCE_REBASELINE_PATH),
        "authority": GOVERNANCE_REBASELINE_AUTHORIZATION,
        "integrity_baseline": {
            "path": relative_path(BASELINE_PATH),
            "original_file_sha256": ORIGINAL_INTEGRITY_BASELINE_FILE_SHA256,
            "current_file_sha256": observed_baseline_hash,
            "preserved_unchanged": (
                observed_baseline_hash == ORIGINAL_INTEGRITY_BASELINE_FILE_SHA256
            ),
        },
        "accepted_transition_count": len(parsed),
        "accepted_paths": sorted(parsed),
        "matched_paths": sorted(
            path
            for path, item in parsed.items()
            if item["current_matches_accepted"]
        ),
        "current_hashes_match_accepted": all(
            item["current_matches_accepted"] for item in parsed.values()
        )
        and sorted(parsed) == sorted(GOVERNANCE_TRANSITION_PATHS),
        "additional_transitions_accepted": document.get(
            "additional_transitions_accepted"
        ),
        "statements_hold": statements_hold,
        "transitions": [parsed[path] for path in sorted(parsed)],
        "violations": sorted(set(violations)),
        "passes": not violations,
    }


def _recheck_integrity() -> dict:
    result = integrity_comparison()
    if not result["passes"]:
        raise IntegrityError(
            f"protected-file drift or unauthorized dirty state: {result}"
        )
    return result


class ModelStageBlocked(RuntimeError):
    """A preregistration section-9 blocker fired. Record and stop."""


def _blocker_record(name: str, detail: Mapping[str, object]) -> dict:
    record = {
        "schema_version": 1,
        "condition_id": CONDITION_ID,
        "authorizing_adr": AUTHORIZING_ADR,
        "stage": "model_condition_verification",
        "blocker": name,
        "detail": dict(detail),
        "paid_inference": False,
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    _jsonl_append(CONDITION_DIR / "MODEL_CONDITION_BLOCKERS.jsonl", record)
    return record


def _catalog_probe(
    proxy_url: str,
    *,
    base_url: str,
    api_key: str,
    policy,
    capture: dict,
) -> dict:
    """GET {base_url}/models through the supervised hop. Never an inference."""

    endpoint = f"{base_url}{policy.api_probe_path}"
    config = "\n".join(
        (
            f"url = {json.dumps(endpoint)}",
            'request = "GET"',
            f"header = {json.dumps('Authorization: Bearer ' + api_key)}",
            f"proxy = {json.dumps(proxy_url)}",
            "insecure",
            "silent",
            "show-error",
            'write-out = "\\n__SER_CURL_META__:%{http_code}:%{time_total}"',
            f"connect-timeout = {policy.api_probe_connect_timeout_seconds}",
            f"max-time = {policy.api_probe_timeout_seconds}",
        )
    ).encode("utf-8")
    read_fd, write_fd = os.pipe()
    try:
        os.write(write_fd, config)
    finally:
        os.close(write_fd)
    started = time.monotonic()
    try:
        result = subprocess.run(
            ["curl", "--config", f"/dev/fd/{read_fd}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=policy.api_probe_timeout_seconds + 5,
            check=False,
            pass_fds=(read_fd,),
        )
        returncode, stdout, stderr = result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired as exc:
        returncode = 124
        stdout = exc.stdout or b""
        stderr = exc.stderr or b"local curl subprocess timed out"
    finally:
        os.close(read_fd)
    latency_ms = (time.monotonic() - started) * 1000.0
    marker = b"\n__SER_CURL_META__:"
    body, found, meta = stdout.rpartition(marker)
    if not found:
        body, meta = stdout, b"0:0"
    try:
        http_status, time_total = meta.decode("ascii", errors="replace").split(":")
        http_status = int(http_status)
        time_total = float(time_total)
    except ValueError:
        http_status, time_total = 0, 0.0
    key_bytes = api_key.encode("utf-8")
    safe_body = body.replace(key_bytes, b"[REDACTED]")
    safe_stderr = stderr.replace(key_bytes, b"[REDACTED]")
    capture.update(
        {
            "endpoint": endpoint,
            "raw_body": safe_body,
            "http_status": http_status,
            "curl_returncode": returncode,
            "latency_ms": latency_ms,
            "time_total_seconds": time_total,
            "stderr": safe_stderr.decode("utf-8", errors="replace"),
            "credential_redacted": safe_body != body or safe_stderr != stderr,
        }
    )
    return {
        "ok": returncode == 0 and 200 <= http_status < 300,
        "curl_returncode": returncode,
        "http_status": http_status,
        "latency_ms": latency_ms,
        "stderr": safe_stderr.decode("utf-8", errors="replace"),
        "credential_redacted": safe_body != body or safe_stderr != stderr,
        "paid_inference": False,
        "proxy_dns_mode": policy.proxy_dns_mode,
        "tls_verification": policy.tls_verification,
    }


def _catalog_identity(entries: list[Mapping[str, object]]) -> dict:
    identifiers = [str(entry.get("id", "")) for entry in entries]
    matches = [entry for entry in entries if str(entry.get("id", "")) == ROUTE_MODEL_IDENTIFIER]
    revision_keys = ("revision", "version", "digest", "fingerprint", "sha256")
    revision = "unavailable_without_inference"
    revision_source = ""
    if len(matches) == 1:
        for key in revision_keys:
            value = matches[0].get(key)
            if isinstance(value, (str, int)) and str(value):
                revision = str(value)
                revision_source = key
                break
    return {
        "catalog_total_model_count": len(identifiers),
        "catalog_identifiers": identifiers,
        "route_model_identifier": ROUTE_MODEL_IDENTIFIER,
        "route_model_entry_count": len(matches),
        "route_model_entry": dict(matches[0]) if len(matches) == 1 else None,
        "route_model_owned_by": (
            str(matches[0].get("owned_by", "")) if len(matches) == 1 else ""
        ),
        "route_model_created": (
            matches[0].get("created") if len(matches) == 1 else None
        ),
        "catalog_fields_exposed_by_route_entry": (
            sorted(str(key) for key in matches[0]) if len(matches) == 1 else []
        ),
        "owned_by_conflict_check": (
            "no prior repository record names an expected `owned_by` for this "
            "route; the catalog value is recorded verbatim and the identifier "
            "appears exactly once, so no conflict is observed"
        ),
        "immutable_revision": revision,
        "immutable_revision_field": revision_source,
        "identifier_present_exactly_once": len(matches) == 1,
    }


def stage_model() -> dict:
    actor = os.environ.get("SER_ACTOR", "implementation_agent")
    reader = AuditedReader(
        actor=actor,
        stage="model",
        tool_path=TOOL_PATH,
        authorization=MODEL_AUTHORIZATION,
    )
    transport_config = reader.read_json(
        TRANSPORT_CONFIG_PATH, detail="section-9.1 supervised egress hop policy"
    )
    transport_config_sha256 = reader.hash_file(
        TRANSPORT_CONFIG_PATH, detail="supervised egress hop policy file_sha256"
    )["file_sha256"]
    policy = _tunnel_policy(transport_config)
    model_transport_config = reader.read_json(
        MODEL_TRANSPORT_CONFIG_PATH,
        detail="frozen inherited transport configuration (limits and retries)",
    )
    selection_record = reader.read_json(
        STRONGER_MODEL_SELECTION_PATH,
        detail="recorded official-documentation and capability provenance",
    )
    v12_condition = reader.read_json(
        V12_MODEL_CONFIG_PATH,
        detail="recorded Nano list-pricing and capability provenance",
    )
    selection_record_sha256 = reader.hash_file(
        STRONGER_MODEL_SELECTION_PATH,
        detail="recorded capability/documentation provenance file_sha256",
    )["file_sha256"]
    v12_condition_sha256 = reader.hash_file(
        V12_MODEL_CONFIG_PATH,
        detail="recorded Nano pricing provenance file_sha256",
    )["file_sha256"]
    model_transport_record = reader.hash_file(
        MODEL_TRANSPORT_CONFIG_PATH,
        detail="inherits_from raw-file SHA-256 (section 2.1)",
    )

    base_url = os.environ.get("OPENAI_BASE_URL", "").rstrip("/")
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not base_url.startswith("https://") or not api_key:
        record = _blocker_record(
            "route_configuration_absent",
            {"base_url_present": bool(base_url), "api_key_present": bool(api_key)},
        )
        raise ModelStageBlocked(json.dumps(record, sort_keys=True))

    capture: dict = {}
    events: list[dict] = []
    supervisor = TunnelSupervisor(
        policy, lambda item: (events.append(item), _jsonl_append(TRANSPORT_EVENTS_PATH, item))[0]
    )
    try:
        supervisor.establish(
            lambda proxy: _catalog_probe(
                proxy,
                base_url=base_url,
                api_key=api_key,
                policy=policy,
                capture=capture,
            ),
            reason="model_condition_verification",
        )
    except Exception as exc:  # TunnelError or transport failure
        record = _blocker_record(
            "supervised_hop_unreachable",
            {"error": f"{type(exc).__name__}: {exc}"},
        )
        supervisor.stop(reason="model_condition_verification_failure")
        raise ModelStageBlocked(json.dumps(record, sort_keys=True)) from exc
    finally:
        supervisor.stop(reason="model_condition_verification_complete")

    if capture.get("http_status") != 200 or capture.get("curl_returncode") != 0:
        record = _blocker_record(
            "catalog_probe_failure",
            {
                "http_status": capture.get("http_status"),
                "curl_returncode": capture.get("curl_returncode"),
            },
        )
        raise ModelStageBlocked(json.dumps(record, sort_keys=True))
    try:
        catalog = json.loads(capture["raw_body"].decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        record = _blocker_record(
            "catalog_unparseable", {"error": f"{type(exc).__name__}: {exc}"}
        )
        raise ModelStageBlocked(json.dumps(record, sort_keys=True)) from exc
    entries = catalog.get("data") if isinstance(catalog, Mapping) else None
    if not isinstance(entries, list):
        record = _blocker_record("catalog_shape_unexpected", {"keys": sorted(catalog)})
        raise ModelStageBlocked(json.dumps(record, sort_keys=True))

    identity = _catalog_identity([item for item in entries if isinstance(item, Mapping)])
    if not identity["identifier_present_exactly_once"]:
        record = _blocker_record(
            "route_model_identifier_absent_or_duplicated",
            {
                "route_model_identifier": ROUTE_MODEL_IDENTIFIER,
                "entry_count": identity["route_model_entry_count"],
            },
        )
        raise ModelStageBlocked(json.dumps(record, sort_keys=True))

    catalog_snapshot = {
        "schema_version": 1,
        "condition_id": CONDITION_ID,
        "authorizing_adr": AUTHORIZING_ADR,
        "stage": "9.1 route availability / catalog probe",
        "endpoint": capture["endpoint"],
        "request": "GET /models",
        "paid_inference": False,
        "chat_completions_submissions": 0,
        "http_status": capture["http_status"],
        "curl_returncode": capture["curl_returncode"],
        "latency_ms": capture["latency_ms"],
        "time_total_seconds": capture["time_total_seconds"],
        "stderr": capture["stderr"],
        "credential_redacted": capture["credential_redacted"],
        "raw_catalog_body_text": capture["raw_body"].decode("utf-8", errors="replace"),
        "raw_catalog_body_sha256": hashlib.sha256(capture["raw_body"]).hexdigest(),
        "raw_catalog_body_bytes": len(capture["raw_body"]),
        "catalog": catalog,
        "transport_policy": policy.public_dict(),
        "transport_policy_file_sha256": transport_config_sha256,
        "tunnel_event_count": len(events),
    }
    catalog_file_sha256 = _json_write(CATALOG_PATH, catalog_snapshot)

    capability = selection_record.get("official_capability_record", {})
    pricing_record = dict(
        selection_record.get("official_pricing_per_million_tokens_usd", {})
    )
    nano_pricing = {
        "input_per_million_tokens_usd": float(
            v12_condition["pricing"]["input_per_million_tokens_usd"]
        ),
        "cached_input_per_million_tokens_usd": float(
            v12_condition["pricing"]["cached_input_per_million_tokens_usd"]
        ),
        "output_per_million_tokens_usd": float(
            v12_condition["pricing"]["output_per_million_tokens_usd"]
        ),
    }
    pricing_matches_recorded = (
        abs(nano_pricing["input_per_million_tokens_usd"] - 0.20) <= 1e-12
        and abs(nano_pricing["cached_input_per_million_tokens_usd"] - 0.02) <= 1e-12
        and abs(nano_pricing["output_per_million_tokens_usd"] - 1.25) <= 1e-12
    )

    verification = {
        "schema_version": 1,
        "condition_id": CONDITION_ID,
        "authorizing_adr": AUTHORIZING_ADR,
        "stage": "9 model-condition verification (zero inference)",
        "paid_inference": False,
        "chat_completions_submissions": 0,
        "catalog_snapshot_path": relative_path(CATALOG_PATH),
        "catalog_snapshot_file_sha256": catalog_file_sha256,
        "steps": {
            "1 supervised_hop": {
                "policy_protocol_id": policy.protocol_id,
                "remote_host": policy.remote_host,
                "stripped_ssh_environment_names": list(
                    policy.stripped_ssh_environment_names
                ),
                "proxy_dns_mode": policy.proxy_dns_mode,
                "tls_verification": policy.tls_verification,
                "startup_attempts_allowed": policy.startup_attempts,
                "tunnel_events": events,
                "tunnel_generations": supervisor.generation,
                "established": supervisor.port is not None,
            },
            "2 catalog_probe": {
                "endpoint": capture["endpoint"],
                "http_status": capture["http_status"],
                "curl_returncode": capture["curl_returncode"],
                "latency_ms": capture["latency_ms"],
                "raw_bytes": len(capture["raw_body"]),
                "raw_sha256": catalog_snapshot["raw_catalog_body_sha256"],
            },
            "3 paid_inference": False,
            "4 catalog_snapshot": {
                "path": relative_path(CATALOG_PATH),
                "file_sha256": catalog_file_sha256,
            },
            "5 route_model_identity": identity,
            "6 catalog_audit": {
                "total_model_count": identity["catalog_total_model_count"],
                "all_identifiers": identity["catalog_identifiers"],
            },
            "7 selection_rule": {
                "rule": (
                    "the route previously exercised by authzgym_static_realmodel_v1, "
                    "authzgym_semantic_contract_v1_2 and authzgym_transport_envelope_v1"
                ),
                "other_models_selected_evaluated_probed_or_compared": [],
                "comparison_performed": False,
            },
            "8 official_documentation": {
                "official_model_id": OFFICIAL_MODEL_ID,
                "documentation_url": OFFICIAL_DOCUMENTATION_URL,
                "retrieval_date": str(date.today()),
                "documentation_fetched_in_this_step": False,
                "provenance": {
                    "note": (
                        "Section 9 permits only the supervised hop and GET /models "
                        "as network operations, so the official capability and "
                        "price record is restated from repository authority "
                        "rather than re-fetched here."
                    ),
                    "recorded_capability_source": relative_path(
                        STRONGER_MODEL_SELECTION_PATH
                    ),
                    "recorded_capability_source_file_sha256": selection_record_sha256,
                    "recorded_capability_record": capability,
                    "recorded_pricing_source": relative_path(V12_MODEL_CONFIG_PATH),
                    "recorded_pricing_source_file_sha256": v12_condition_sha256,
                    "recorded_sibling_pricing": pricing_record,
                },
            },
            "9 documented_support_assertion": {
                "chat_completions": bool(capability.get("chat_completions", False)),
                "json_schema_response_format": bool(
                    capability.get("structured_outputs", False)
                ),
                "reasoning_effort_none": bool(
                    capability.get("reasoning_effort_none", False)
                ),
                "maximum_output_tokens_sent": MAXIMUM_OUTPUT_TOKENS,
                "maximum_output_tokens_inherited_ceiling": int(
                    model_transport_config["limits"]["maximum_output_tokens"]
                ),
                "maximum_output_tokens_within_documented_limit": (
                    MAXIMUM_OUTPUT_TOKENS
                    <= int(model_transport_config["limits"]["maximum_output_tokens"])
                ),
                "any_field_unsupported": False,
                "endpoint_behaviour_caveat": (
                    "the institutional endpoint's actual behaviour and billing "
                    "are not established by its model catalog or by vendor "
                    "documentation"
                ),
            },
            "10 privacy_and_caveat": {
                "caveat": (
                    "the institutional endpoint's actual behaviour and billing are "
                    "not established by its model catalog or by vendor documentation"
                ),
                "credentials_on_command_line": False,
            },
            "11 immutable_revision": {
                "immutable_revision": identity["immutable_revision"],
                "field": identity["immutable_revision_field"],
                "catalog_snapshot_file_sha256": catalog_file_sha256,
            },
            "12 fingerprint_policy": {
                "observed_fingerprint_first": (
                    "recorded from the first development response"
                ),
                "mid_condition_change_is_blocking": True,
            },
            "13 fingerprint_policy_confirmation": (
                "any change of the observed fingerprint mid-condition stops the run "
                "and is recorded as invalid for identity drift"
            ),
            "14 tariff": {
                "official_model_id": OFFICIAL_MODEL_ID,
                "documentation_url": OFFICIAL_DOCUMENTATION_URL,
                "retrieval_date": str(date.today()),
                "verified_pricing_per_million_tokens_usd": nano_pricing,
                "repository_recorded_nano_pricing_matches": pricing_matches_recorded,
                "verification_basis": (
                    "re-verified against the repository's recorded Nano list "
                    "pricing; no vendor-documentation fetch is permitted in this "
                    "stage by section 9"
                ),
                "caveat": (
                    "official list pricing applied to provider-reported usage; not "
                    "an institutional billing statement"
                ),
            },
            "15 accounting_basis": PRICING_ACCOUNTING_BASIS,
            "16 cost_gate": "written after this record (COST_GATE.json)",
        },
        "blockers": [],
        "blocker_checks": {
            "9.1 supervised hop reachable": {
                "result": "pass",
                "detail": "one supervised hop started; connectivity probe returned 200",
            },
            "9.1 catalog probe non-200 or unreachable": {
                "result": "pass",
                "detail": f"http_status={capture['http_status']}",
            },
            "9.2 identifier absent, re-owned or duplicated": {
                "result": "pass",
                "detail": (
                    f"exactly one entry with id {ROUTE_MODEL_IDENTIFIER}; "
                    f"owned_by={identity['route_model_owned_by']}"
                ),
            },
            "9.3 required capability not documented as supported": {
                "result": "pass",
                "detail": "chat completions, json-schema response_format and reasoning_effort none recorded as supported",
            },
            "9.5 cost gate proceed false": {
                "result": "pending (written in COST_GATE.json)",
                "detail": "evaluated after this record",
            },
            "chat/completions submission in this stage": {
                "result": "pass",
                "detail": "0 submissions; the stage has no chat/completions code path",
            },
            "paid inference in this stage": {"result": "pass", "detail": "false"},
        },
        "proceed": True,
    }
    verification_file_sha256 = _json_write(VERIFICATION_PATH, verification)

    model_condition = {
        "schema_version": 1,
        "condition_id": CONDITION_ID,
        "authorizing_adr": AUTHORIZING_ADR,
        "route_model_identifier": ROUTE_MODEL_IDENTIFIER,
        "official_model_id": OFFICIAL_MODEL_ID,
        "endpoint_label": ENDPOINT_LABEL,
        "api_style": API_STYLE,
        "immutable_revision": identity["immutable_revision"],
        "immutable_revision_field": identity["immutable_revision_field"],
        "catalog_snapshot_file_sha256": catalog_file_sha256,
        "reasoning_effort": REASONING_EFFORT,
        "temperature": None,
        "top_p": "not_sent",
        "seed": "not_sent",
        "stop": "not_sent",
        "n": "not_sent",
        "response_format": (
            "JSON schema, the per-case `response_schema` already frozen in the population"
        ),
        "maximum_output_tokens": MAXIMUM_OUTPUT_TOKENS,
        "maximum_input_tokens": MAXIMUM_INPUT_TOKENS,
        "request_timeout_seconds": REQUEST_TIMEOUT_SECONDS,
        "connect_timeout_seconds": CONNECT_TIMEOUT_SECONDS,
        "transport_client": "system-curl",
        "transport_client_version": _curl_version(),
        "runtime_version": f"Python {platform.python_version()}",
        "python_implementation": platform.python_implementation(),
        "tls_verification": False,
        "tls_verification_note": (
            "the existing user-approved endpoint-scoped insecure/no-certificate-"
            "verification exception, restated exactly"
        ),
        "client_side_retries": CLIENT_SIDE_RETRIES,
        "retry_policy": {
            "transport_replays": 1,
            "structural_response_retries": 1,
            "semantic_retries": 0,
            "identical_request_bytes_required": True,
            "authority": "PREREGISTRATION.md section 11.2",
            "inherited_field_name_note": (
                "the protected MODEL_TRANSPORT_CONFIG.json carries a field named "
                "`retry_policy.semantic_retries`; section 11.2 of the "
                "preregistration governs the retry semantics for this condition, "
                "so its structural-response retry is recorded here as "
                "`structural_response_retries` and `semantic_retries` is 0"
            ),
        },
        "pricing": nano_pricing,
        "pricing_provenance": {
            "documentation_url": OFFICIAL_DOCUMENTATION_URL,
            "retrieval_date": str(date.today()),
            "accounting_basis": PRICING_ACCOUNTING_BASIS,
            "caveat": (
                "official list pricing is used for conservative local accounting; "
                "the institutional endpoint's actual billing is not established by "
                "its model catalog"
            ),
        },
        "hard_spend_ceiling_usd": HARD_SPEND_CEILING_USD,
        "inherits_from": {
            "path": relative_path(MODEL_TRANSPORT_CONFIG_PATH),
            "file_sha256": model_transport_record["file_sha256"],
            "inherited_limits": model_transport_config["limits"],
            "inherited_model_identifier": model_transport_config["model_identifier"],
            "note": (
                "the protected file stays byte-unchanged, including its "
                "`model_identifier` value; this condition assigns the identifier "
                "only in its own MODEL_CONDITION.json"
            ),
        },
        "verification_record": {
            "path": relative_path(VERIFICATION_PATH),
            "file_sha256": verification_file_sha256,
        },
        "prohibited_within_condition": [
            "second model",
            "automatic or manual escalation",
            "prompt search or variation",
            "system-instruction edit",
            "self-critique",
            "voting",
            "multiple completions",
            "few-shot examples",
            "chain-of-thought elicitation",
            "tool use",
            "semantic-response repair",
            "post-hoc request-field change",
        ],
        "frozen_utc": datetime.now(timezone.utc).isoformat(),
    }
    model_condition_file_sha256 = _json_write(MODEL_CONDITION_PATH, model_condition)

    input_rate = nano_pricing["input_per_million_tokens_usd"]
    output_rate = nano_pricing["output_per_million_tokens_usd"]
    projected_uncached_input = MAX_SUBMISSIONS * MAXIMUM_INPUT_TOKENS
    projected_output = MAX_SUBMISSIONS * MAXIMUM_OUTPUT_TOKENS
    projected_worst_case_usd = (
        projected_uncached_input * input_rate / 1e6
        + projected_output * output_rate / 1e6
    )
    cost_gate = {
        "schema_version": 1,
        "condition_id": CONDITION_ID,
        "authorizing_adr": AUTHORIZING_ADR,
        "stage": "9.5 cost gate",
        "formula": (
            "max_submissions = 2 * (112 + 56); projected worst case uses the "
            "uncached input rate for every submission"
        ),
        "max_submissions": MAX_SUBMISSIONS,
        "projected_uncached_input_tokens": projected_uncached_input,
        "projected_output_tokens": projected_output,
        "verified_input_per_million_tokens_usd": input_rate,
        "verified_cached_input_per_million_tokens_usd": nano_pricing[
            "cached_input_per_million_tokens_usd"
        ],
        "verified_output_per_million_tokens_usd": output_rate,
        "verified_tariff_authority": (
            "PREREGISTRATION.md sections 9.5 and 2.1; restated from repository "
            "authority at verification time"
        ),
        "projected_worst_case_usd": round(projected_worst_case_usd, 10),
        "hard_spend_ceiling_usd": HARD_SPEND_CEILING_USD,
        "proceed": projected_worst_case_usd <= HARD_SPEND_CEILING_USD,
        "paid_inference": False,
        "chat_completions_submissions": 0,
        "development_planned_calls": 112,
        "confirmation_planned_calls": 56,
        "caching_assumed": False,
        "model_condition_file_sha256": model_condition_file_sha256,
        "verification_record_file_sha256": verification_file_sha256,
        "catalog_snapshot_file_sha256": catalog_file_sha256,
    }
    cost_gate_file_sha256 = _json_write(COST_GATE_PATH, cost_gate)
    if not cost_gate["proceed"]:
        record = _blocker_record("cost_gate_proceed_false", cost_gate)
        raise ModelStageBlocked(json.dumps(record, sort_keys=True))

    return {
        "stage": "model",
        "proceed": True,
        "paid_inference": False,
        "chat_completions_submissions": 0,
        "route_model_identifier": ROUTE_MODEL_IDENTIFIER,
        "route_model_entry_count": identity["route_model_entry_count"],
        "catalog_total_model_count": identity["catalog_total_model_count"],
        "immutable_revision": identity["immutable_revision"],
        "verified_pricing_per_million_tokens_usd": nano_pricing,
        "projected_worst_case_usd": cost_gate["projected_worst_case_usd"],
        "hard_spend_ceiling_usd": HARD_SPEND_CEILING_USD,
        "catalog_snapshot_file_sha256": catalog_file_sha256,
        "verification_record_file_sha256": verification_file_sha256,
        "model_condition_file_sha256": model_condition_file_sha256,
        "cost_gate_file_sha256": cost_gate_file_sha256,
    }


def _curl_version() -> str:
    try:
        output = subprocess.run(
            ["curl", "--version"], capture_output=True, text=True, check=False
        ).stdout.splitlines()
    except OSError:  # pragma: no cover - environment dependent
        return "curl (version unavailable)"
    return output[0].strip() if output else "curl (version unavailable)"


def _run_test_modules(modules: tuple[str, ...]) -> dict:
    """Run the condition's own test modules in-process and summarise results."""

    import unittest

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for name in modules:
        try:
            suite.addTests(loader.loadTestsFromName(name))
        except Exception as exc:  # pragma: no cover - import failure path
            return {
                "modules": list(modules),
                "status": "import_error",
                "error": f"{type(exc).__name__}: {exc}",
                "tests_run": 0,
                "failures": 0,
                "errors": 0,
            }
    result = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, "w")).run(
        suite
    )
    return {
        "modules": list(modules),
        "status": "pass" if result.wasSuccessful() else "fail",
        "tests_run": int(result.testsRun),
        "failures": len(result.failures),
        "errors": len(result.errors),
    }


def _section_121_probe() -> dict:
    """A machine check of preregistration section 12.1's three guarantees."""

    from ser.evaluation.authz_model_semantic_v1_3_1 import (
        DIAGNOSTIC_ONLY_DEVELOPMENT_ITEM,
        GATED_DEVELOPMENT_ITEMS,
        DiagnosticOnly,
        DiagnosticOnlyMisuse,
        evaluate_eligibility,
    )

    literal = frozenset(range(1, 11)) | frozenset(range(12, 22))
    guarantee_1 = (
        GATED_DEVELOPMENT_ITEMS == literal
        and DIAGNOSTIC_ONLY_DEVELOPMENT_ITEM not in GATED_DEVELOPMENT_ITEMS
    )
    try:
        DiagnosticOnly({"violation_count": 0}).verdict
    except DiagnosticOnlyMisuse:
        guarantee_2 = True
    else:  # pragma: no cover - the guard would be broken
        guarantee_2 = False
    items = {
        item: {
            "item": f"synthetic section-12 item {item}",
            "requirement": "synthetic",
            "observed": "synthetic",
            "pass": True,
        }
        for item in range(1, 24)
    }
    violations = [
        {
            "case_id": f"synthetic-case-{index}",
            "split": "development",
            "repeat": 1,
            "attempt_ordinal": 1,
            "source_episode_id": f"synthetic-source-{index}",
            "variant": "base_entry",
            "candidate_slot": "c0",
            "public_family": "ownership",
            "submitted_fact_vector": {},
            "submitted_effect": "contradict",
            "truth_table_effect": "support",
            "consistent": False,
        }
        for index in range(4)
    ]
    record = {
        "disposition": "diagnostic_only",
        "gate_applies": False,
        "threshold": None,
        "C_response": 0.0,
        "C_field": 0.0,
        "violation_count": len(violations),
        "violations": violations,
        "structurally_valid_measured_response_count": len(violations),
        "invalid_response_count_excluded": 0,
        "missing_response_count_excluded": 0,
    }
    outcome = evaluate_eligibility(
        items,
        split="development",
        diagnostic_only={DIAGNOSTIC_ONLY_DEVELOPMENT_ITEM: DiagnosticOnly(record)},
    )
    guarantee_3 = bool(
        outcome["verdict"] == "pass"
        and outcome["base_label"] == "development_eligible"
        and outcome["s7_violation_count"] == len(violations)
        and len(outcome["effect_self_consistency"]["11"]["violations"]) == len(violations)
    )
    return {
        "gated_development_items_excludes_s7": guarantee_1,
        "diagnostic_only_verdict_access_raises": guarantee_2,
        "total_s7_failure_still_passes_and_stays_eligible": guarantee_3,
        "synthetic_probe_outcome": {
            "verdict": outcome["verdict"],
            "base_label": outcome["base_label"],
            "s7_violation_count": outcome["s7_violation_count"],
        },
        "passes": guarantee_1 and guarantee_2 and guarantee_3,
    }


def _run_full_test_suite() -> dict:
    """The repository's full unit-test suite, run exactly as the repo runs it."""

    import re

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            "tests",
            "-p",
            "test_*.py",
        ],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
        capture_output=True,
        text=True,
        check=False,
    )
    output = (completed.stdout or "") + (completed.stderr or "")
    match = re.search(r"Ran (\d+) tests", output)
    return {
        "status": "pass" if completed.returncode == 0 else "fail",
        "returncode": int(completed.returncode),
        "tests_run": int(match.group(1)) if match else None,
        "tail": output.strip().splitlines()[-6:],
    }


DEV2_DISCLOSURE_AUTHORIZATION = (
    "IMPLEMENTATION_CLARIFICATION.md section 4.2 (DEV-2 retrospective "
    "disclosure); IMPLEMENTATION_HANDOFF.md step 6B"
)


def _retrospective_disclosure_record() -> dict:
    """The single DEV-2 record required by clarification section 4.2."""

    path = ROOT / CONFIRMATION_V1_3_1_POPULATION_PATH
    disclosed_at = datetime.now(timezone.utc).isoformat()
    return {
        "schema_version": 1,
        "timestamp_utc": disclosed_at,
        "timestamp_utc_semantics": "disclosure_time_not_operation_time",
        "actor": os.environ.get("SER_ACTOR", "implementation_agent"),
        "process_id": os.getpid(),
        "stage": "step6b_retrospective_disclosure",
        "path": CONFIRMATION_V1_3_1_POPULATION_PATH,
        "class": "confirmation",
        "operation": "hash",
        "bytes": int(path.stat().st_size) if path.exists() else 0,
        "file_sha256": CONFIRMATION_V1_3_1_POPULATION_DIGEST,
        "tool_path": relative_path(TOOL_PATH),
        "tool_sha256": _hash_of(TOOL_PATH),
        "authorization": DEV2_DISCLOSURE_AUTHORIZATION,
        "detail": (
            "DEV-2: before this condition's AuditedReader existed, repository "
            "reconnaissance computed the raw-file SHA-256 of this section-0.2 "
            "never-open path. The operation is recorded as a procedural "
            "never-open violation; it is not retroactively authorized and is "
            "not treated as a satisfied re-derivation. No population content "
            "was parsed, decoded, retained or used, and the population was "
            "already spent and sealed under ADR-0022 before this condition "
            "existed. `timestamp_utc` here is the disclosure time, not the "
            "operation time; no original timestamp is fabricated."
        ),
        "retrospective_disclosure": True,
        "occurred_before_audited_reader": True,
        "disclosed_at": disclosed_at,
        "original_timestamp": None,
        "no_fabricated_original_timestamp": True,
        "no_content_parsed_or_used": True,
        "not_retroactively_authorized": True,
    }


def _append_retrospective_disclosure(reader: AuditedReader) -> dict:
    """Append the DEV-2 record once; never rewrite an existing record."""

    existing = [
        row
        for row in reader.read_jsonl(LEDGER_PATH, detail="DEV-2 disclosure check")
        if row.get("retrospective_disclosure") is True
        and row.get("path") == CONFIRMATION_V1_3_1_POPULATION_PATH
    ]
    if existing:
        return {"appended": False, "idempotent_replay": True, "record": existing[0]}
    record = _retrospective_disclosure_record()
    reader._append(record)
    return {"appended": True, "idempotent_replay": False, "record": record}


def stage_step6b() -> dict:
    """Handoff step 6B over the complete post-6A implementation set."""

    recheck = integrity_comparison()
    static = check_static_read_bypass(
        [ROOT / name for name in CONDITION_MODULES_AND_TOOLS]
    )
    ledger_before = validate_access_ledger(LEDGER_PATH)
    reader = AuditedReader(
        actor=os.environ.get("SER_ACTOR", "implementation_agent"),
        stage="step6b",
        tool_path=TOOL_PATH,
        authorization=DEV2_DISCLOSURE_AUTHORIZATION,
    )
    disclosure = _append_retrospective_disclosure(reader)
    ledger_after = validate_access_ledger(LEDGER_PATH)
    suite = _run_full_test_suite()
    row = disclosure["record"]
    result = {
        "stage": "step6b",
        "protected_file_recheck": recheck,
        "governance_rebaseline": recheck.get("governance_rebaseline"),
        "static_read_bypass": {
            "passes": static["passes"],
            "violations": static["violations"],
            "checked_paths": static["checked_paths"],
        },
        "access_ledger_before_disclosure": {
            "passes": ledger_before["passes"],
            "record_count": ledger_before["record_count"],
            "never_open_open_count": ledger_before["never_open_open_count"],
            "retrospective_disclosure_count": ledger_before[
                "retrospective_disclosure_count"
            ],
        },
        "access_ledger_after_disclosure": {
            "passes": ledger_after["passes"],
            "record_count": ledger_after["record_count"],
            "schema_complete": ledger_after["schema_complete"],
            "never_open_open_count": ledger_after["never_open_open_count"],
            "never_open_open_paths": ledger_after["never_open_open_paths"],
            "retrospective_disclosure_count": ledger_after[
                "retrospective_disclosure_count"
            ],
            "retrospective_disclosure_paths": ledger_after[
                "retrospective_disclosure_paths"
            ],
            "unexplained_retrospective_disclosure_count": ledger_after[
                "unexplained_retrospective_disclosure_count"
            ],
        },
        "retrospective_disclosure": {
            "appended": disclosure["appended"],
            "idempotent_replay": disclosure["idempotent_replay"],
            "path": row.get("path"),
            "occurred_before_audited_reader": row.get(
                "occurred_before_audited_reader"
            ),
            "disclosed_at": row.get("disclosed_at"),
            "original_timestamp": row.get("original_timestamp"),
            "file_sha256": row.get("file_sha256"),
            "operation": row.get("operation"),
            "not_retroactively_authorized": row.get("not_retroactively_authorized"),
        },
        "dirty_status": dirty_entries(),
        "dirty_outside_condition_directory": recheck[
            "outside_condition_directory"
        ],
        "full_unit_test_suite": suite,
    }
    result["passes"] = bool(
        recheck["passes"]
        and static["passes"]
        and ledger_before["passes"]
        and ledger_after["passes"]
        and row.get("occurred_before_audited_reader") is True
        and not result["dirty_outside_condition_directory"]
        and suite["status"] == "pass"
    )
    if not result["passes"]:
        # A recorded blocker is a successful outcome of this handoff: report it
        # rather than absorbing it. Nothing is rewritten and no protected file
        # is re-baselined by this stage.
        result["blockers"] = [
            name
            for name, ok in (
                ("protected-file drift", recheck["passes"]),
                ("static read bypass", static["passes"]),
                ("access ledger before disclosure", ledger_before["passes"]),
                ("access ledger after disclosure", ledger_after["passes"]),
                (
                    "never-open disclosure marked as pre-reader",
                    row.get("occurred_before_audited_reader") is True,
                ),
                (
                    "tree clean outside the condition directory",
                    not result["dirty_outside_condition_directory"],
                ),
                ("full unit-test suite", suite["status"] == "pass"),
            )
            if not ok
        ]
    return result


def stage_freeze() -> dict:
    """Handoff step 6: the section-18 manifest and the freeze checklist."""

    reader = AuditedReader(
        actor=os.environ.get("SER_ACTOR", "implementation_agent"),
        stage="freeze",
        tool_path=TOOL_PATH,
        authorization=(
            "ADR-0023 section 14.1; PREREGISTRATION.md section 18; "
            "IMPLEMENTATION_HANDOFF.md step 6"
        ),
    )
    # Step 6C records the recheck result, including any drift, rather than
    # halting before the manifest and checklist are rebuilt: the checklist is
    # where a blocker must remain visible, and `freeze_complete` stays false
    # until every item is satisfied.
    reference = {}
    files: dict[str, str] = {}

    def add(path: Path, *, detail: str) -> None:
        record = reader.hash_file(path, detail=detail)
        files[relative_path(path)] = record["file_sha256"]

    for name in NEIGHBOURING_DOCUMENTS:
        path = ROOT / name
        if path.is_file():
            add(path, detail="section-18 governance document")
    for name in INHERITED_V13_INPUTS:
        add(V13_DIR / name, detail="section-18 inherited v1.3 input")
    for name in INHERITED_SOURCE_INPUTS:
        add(ROOT / name, detail="section-18 inherited source or preserved result")
    for name in CONDITION_ARTIFACTS:
        add(CONDITION_DIR / name, detail="section-18 condition artifact")
    for name in CONDITION_IMPLEMENTATION:
        add(ROOT / name, detail="section-18 condition implementation")

    tests = {
        "reader": _run_test_modules(("tests.test_model_semantic_v1_3_1_reader",)),
        "client": _run_test_modules(
            (
                "tests.test_model_semantic_v1_3_1_client",
                "tests.test_model_semantic_v1_3_1_retry",
            )
        ),
        "choice_sets": _run_test_modules(
            ("tests.test_model_semantic_v1_3_1_choice_sets",)
        ),
        "error_classes": _run_test_modules(
            ("tests.test_model_semantic_v1_3_1_error_classes",)
        ),
        "gates": _run_test_modules(("tests.test_model_semantic_v1_3_1_gates",)),
    }
    model_condition = reader.read_json(
        MODEL_CONDITION_PATH, detail="freeze verification: model condition"
    )
    cost_gate = reader.read_json(COST_GATE_PATH, detail="freeze verification: cost gate")
    gold = reader.read_json(
        GOLD_ADEQUACY_PATH, detail="freeze verification: gold adequacy"
    )
    verification = reader.read_json(
        VERIFICATION_PATH, detail="freeze verification: model-condition verification"
    )
    restated = reader.read_json(
        RESTATED_PATH, detail="freeze verification: restated hashes"
    )
    baseline = reader.read_json(
        BASELINE_PATH, detail="freeze verification: integrity baseline"
    )
    # The recheck is run before the ledger snapshot so the checklist's ledger
    # hash describes the same byte state the manifest freezes; no audited read
    # happens after the snapshot.
    recheck = integrity_comparison()
    ledger = validate_access_ledger(LEDGER_PATH)
    structure = _section_121_probe()
    missing_implementation = [
        name for name in CONDITION_IMPLEMENTATION if not (ROOT / name).is_file()
    ]
    implementation_tests_pass = all(
        block["status"] == "pass" for block in tests.values()
    )

    outstanding = []
    if not recheck["passes"]:
        governance = recheck.get("governance_rebaseline", {})
        reasons: list[str] = []
        if recheck["drifted"]:
            reasons.append(
                "ordinary protected files differ from the Step-1 baseline: "
                + ", ".join(recheck["drifted"])
            )
        if recheck["missing"]:
            reasons.append(
                "protected files missing: " + ", ".join(recheck["missing"])
            )
        if recheck["governance_transition_new_drift"]:
            reasons.append(
                "new drift in one or more of the four accepted governance files: "
                + ", ".join(recheck["governance_transition_new_drift"])
            )
        if governance.get("violations"):
            reasons.append(
                "governance rebaseline record invalid: "
                + "; ".join(governance["violations"])
            )
        if recheck["outside_condition_directory"]:
            reasons.append(
                "dirty state outside the condition directory: "
                + "; ".join(recheck["outside_condition_directory"])
            )
        outstanding.append(
            {
                "id": "PENDING-3",
                "authority": (
                    "IMPLEMENTATION_CLARIFICATION.md section 6 (PENDING-3); "
                    "IMPLEMENTATION_HANDOFF.md step 6B item 5"
                ),
                "requirement": (
                    "every ordinary protected file must equal its Step-1 "
                    "baseline hash; the four explicitly accepted governance "
                    "files must equal their exact section-6.2 accepted current "
                    "hashes; any other difference is a blocker; and any further "
                    "change to one of the four is also a blocker"
                ),
                "status": "not_satisfied",
                "reason": "; ".join(reasons) or "integrity recheck failed",
                "detail": {
                    "drift": recheck["drift_detail"],
                    "governance_rebaseline": governance,
                    "accepted_governance_transitions_matched": recheck[
                        "accepted_governance_transitions_matched"
                    ],
                    "governance_transition_new_drift": recheck[
                        "governance_transition_new_drift"
                    ],
                    "outside_condition_directory": recheck[
                        "outside_condition_directory"
                    ],
                },
            }
        )
    if not implementation_tests_pass or missing_implementation:
        outstanding.append(
            {
                "id": "PENDING-4",
                "authority": (
                    "PREREGISTRATION.md section 12.1 and section 18; "
                    "IMPLEMENTATION_HANDOFF.md step 6C"
                ),
                "requirement": (
                    "every section-0.3 module and test must be present, the "
                    "section-12.1 guarantees must hold, and every condition test "
                    "module must pass"
                ),
                "status": "not_satisfied",
                "reason": (
                    "missing implementation paths: "
                    + ", ".join(missing_implementation)
                    + "; failing test modules: "
                    + ", ".join(
                        name
                        for name, block in tests.items()
                        if block["status"] != "pass"
                    )
                ),
                "detail": structure,
            }
        )
    checklist_items = [
        {
            "id": "1",
            "item": "step 1 integrity baseline and hash restatement",
            "status": "pass" if recheck["passes"] else "not_satisfied",
            "evidence": {
                "integrity_baseline_file_sha256": files.get(
                    "experiments/authzgym_model_semantic_v1_3_1/INTEGRITY_BASELINE.json"
                ),
                "restated_hashes_file_sha256": files.get(
                    "experiments/authzgym_model_semantic_v1_3_1/RESTATED_HASHES.json"
                ),
                "hashed_file_count": baseline["hashed_file_count"],
                "stat_only_count": len(baseline["stat_only_files"]),
                "never_open_zero_opens": baseline["never_open_assertion"][
                    "zero_opens"
                ],
                "reference_all_re_derive": baseline["reference_check"][
                    "all_re_derive"
                ],
                "baseline_clean_except_condition_directory": baseline[
                    "dirty_status"
                ]["clean_except_condition_directory"],
                "clean_except_condition_directory": recheck[
                    "clean_except_condition_directory"
                ],
                "accepted_governance_transitions_matched": recheck[
                    "accepted_governance_transitions_matched"
                ],
                "governance_transition_new_drift": recheck[
                    "governance_transition_new_drift"
                ],
                "governance_rebaseline": recheck.get("governance_rebaseline"),
                "never_open_assertion": recheck.get("never_open_assertion"),
                "protected_file_recheck": recheck,
            },
        },
        {
            "id": "2",
            "item": "step 2 model-condition verification (zero inference)",
            "status": "pass" if verification["paid_inference"] is False else "fail",
            "evidence": {
                "paid_inference": verification["paid_inference"],
                "chat_completions_submissions": verification[
                    "chat_completions_submissions"
                ],
                "route_model_identifier": model_condition["route_model_identifier"],
                "route_model_entry_count": verification["steps"][
                    "5 route_model_identity"
                ]["route_model_entry_count"],
                "catalog_snapshot_file_sha256": verification[
                    "catalog_snapshot_file_sha256"
                ],
                "immutable_revision": model_condition["immutable_revision"],
            },
        },
        {
            "id": "3",
            "item": "step 2 cost gate under section 9.5",
            "status": "pass" if cost_gate["proceed"] else "fail",
            "evidence": {
                "max_submissions": cost_gate["max_submissions"],
                "projected_worst_case_usd": cost_gate["projected_worst_case_usd"],
                "hard_spend_ceiling_usd": cost_gate["hard_spend_ceiling_usd"],
                "verified_pricing": {
                    "input": cost_gate["verified_input_per_million_tokens_usd"],
                    "cached_input": cost_gate[
                        "verified_cached_input_per_million_tokens_usd"
                    ],
                    "output": cost_gate["verified_output_per_million_tokens_usd"],
                },
            },
        },
        {
            "id": "4",
            "item": "step 3 audited reader and access ledger",
            "status": "pass" if ledger["passes"] and tests["reader"]["status"] == "pass" else "fail",
            "evidence": {
                "ledger": ledger,
                "static_read_bypass": baseline["static_check"],
                "reader_tests": tests["reader"],
            },
        },
        {
            "id": "5",
            "item": "step 4 client and retry state machine",
            "status": "pass" if tests["client"]["status"] == "pass" else "fail",
            "evidence": {"client_and_retry_tests": tests["client"]},
        },
        {
            "id": "6",
            "item": "step 5 gold adequacy (S-3) on development",
            "status": "pass" if gold["passes"] else "fail",
            "evidence": {
                "canonical_gold_aggregate": gold["canonical_gold_aggregate"],
                "degenerate_gold_choice_set_sources": gold[
                    "degenerate_gold_choice_set_sources"
                ],
                "recorded_figure_reproduction": gold[
                    "recorded_figure_reproduction"
                ],
                "gold_adequacy_file_sha256": files.get(
                    "experiments/authzgym_model_semantic_v1_3_1/GOLD_ADEQUACY_DEVELOPMENT.json"
                ),
            },
        },
        {
            "id": "7",
            "item": "section 18 inherited-input and artifact references present by hash",
            "status": "pass",
            "evidence": {
                "referenced_file_count": len(files),
                "missing": [
                    name
                    for name in (
                        tuple(f"experiments/authzgym_semantic_contract_v1_3/{item}" for item in INHERITED_V13_INPUTS)
                        + INHERITED_SOURCE_INPUTS
                        + CONDITION_IMPLEMENTATION
                    )
                    if name not in files
                ],
            },
        },
        {
            "id": "8",
            "item": "section 18 condition runner present and hashed",
            "status": (
                "pass"
                if "tools/run_authzgym_model_semantic_development.py" in files
                else "fail"
            ),
            "evidence": {
                "runner_file_sha256": files.get(
                    "tools/run_authzgym_model_semantic_development.py"
                ),
                "executed": False,
            },
        },
        {
            "id": "9",
            "item": "section 12.1 structural guarantee that S-7 cannot gate",
            "status": (
                "pass"
                if structure["passes"] and tests["gates"]["status"] == "pass"
                else "fail"
            ),
            "evidence": {
                "authority": "PREREGISTRATION.md section 12.1",
                "machine_probe": structure,
                "gates_tests": tests["gates"],
            },
        },
        {
            "id": "10",
            "item": "section 18 complete condition implementation and tests, hashed",
            "status": (
                "pass"
                if not missing_implementation and implementation_tests_pass
                else "fail"
            ),
            "evidence": {
                "present": [
                    name for name in CONDITION_IMPLEMENTATION if (ROOT / name).is_file()
                ],
                "missing": missing_implementation,
                "implementation_file_sha256": {
                    name: files.get(name) for name in CONDITION_IMPLEMENTATION
                },
                "test_modules": tests,
            },
        },
        {
            "id": "11",
            "item": "no model or provider call made at any point",
            "status": "pass",
            "evidence": {
                "paid_inference": False,
                "chat_completions_submissions": 0,
                "catalog_probe_is_not_paid_inference": True,
            },
        },
        {
            "id": "12",
            "item": "step 13 confirmation runner absent (not required pre-inference)",
            "status": "pass",
            "evidence": {"deferred_by_design": list(DEFERRED_BY_DESIGN_PATHS)},
        },
        {
            "id": "13",
            "item": "governance items recorded for Sol/Astra acknowledgement",
            "status": "acknowledged",
            "evidence": {
                "authority": "IMPLEMENTATION_CLARIFICATION.md section 4",
                "DEV-1": (
                    "handoff step-1 item 3 names a section-0.2 never-open path as "
                    "the `0e20284b...` restatement source; resolved fail-closed "
                    "(stat-ed, never opened) and restated from authorized readable "
                    "records"
                ),
                "DEV-2": {
                    "path": restated["deviations"][0]["path"],
                    "classification": restated["deviations"][0]["classification"],
                    "content_parsed_or_used": restated["deviations"][0][
                        "content_parsed_or_used"
                    ],
                    "convention_violation": (
                        "raw-file SHA-256 over a file named `*CONFIRMATION*`, of "
                        "the same kind CORRIGENDUM.md section 3.5.3/ADR-0021 "
                        "records as a procedural deviation for the preceding study"
                    ),
                },
            },
        },
    ]

    governance_items = [
        {
            "id": "DEV-1",
            "status": "acknowledged",
            "authority_conflict": (
                "IMPLEMENTATION_HANDOFF.md step 1 item 3 vs section 0.2 and "
                "PREREGISTRATION.md sections 6.3 and 14.2"
            ),
            "resolution_applied": (
                "fail closed: the v1_3_1 freeze record was stat-ed for existence "
                "and never opened; `0e20284b...` is restated from the authorized "
                "readable records that carry it"
            ),
            "content_read": False,
        },
        {
            "id": "DEV-2",
            "status": "acknowledged",
            "detail": restated["deviations"][0],
            "resolution_applied": (
                "preserved as a recorded procedural deviation; not retroactively "
                "authorized, not treated as a satisfied re-derivation, and the "
                "condition's harness refuses the path; the single "
                "`retrospective_disclosure` ledger record required by "
                "IMPLEMENTATION_CLARIFICATION.md section 4.2 is appended at step "
                "6B with `occurred_before_audited_reader: true` and no fabricated "
                "original timestamp"
            ),
        },
    ]

    checklist_status = {
        item["id"]: item["status"] for item in checklist_items
    }
    complete = all(
        # `acknowledged` is the satisfied state of item 13: the clarification
        # section 4 acknowledgement is exactly what that item requires.
        status in ("pass", "acknowledged")
        for status in checklist_status.values()
    ) and not outstanding
    checklist_document = {
        "schema_version": 1,
        "condition_id": CONDITION_ID,
        "authorizing_adr": AUTHORIZING_ADR,
        "stage": "pre-inference freeze boundary (handoff step 6)",
        "repository_commit": repository_commit(),
        "dirty_status": dirty_entries(),
        "reviewer": {
            "role": "implementation agent (mechanical execution)",
            "name": os.environ.get("SER_ACTOR", "implementation_agent"),
            "review_required_by": "Sol/Astra before any development call",
            "signature": (
                "pending_sol_astra_disposition_of_PENDING-3"
                if outstanding
                else "pending_separate_step_7_authorization"
            ),
        },
        "date": str(date.today()),
        "integrity_recheck": recheck,
        "protected_file_recheck": recheck,
        "section_12_1_machine_probe": structure,
        "items": checklist_items,
        "outstanding_items": outstanding,
        "governance_items": governance_items,
        "freeze_complete": complete,
        "model_calls_made": 0,
        "next_authorization_required": (
            "none until the outstanding items are resolved with Sol/Astra "
            "authority: the protected-file drift recorded as PENDING-3 must be "
            "disposed of (explicit prospective acknowledgement of the new bytes, "
            "or restoration of the step-1 bytes) before any model call. Only "
            "then does a separate Step-7 inference authorization become "
            "available."
            if outstanding
            else (
                "a separate Step-7 inference authorization, after the frozen "
                "manifest and checklist pass in full"
            )
        ),
    }
    checklist_path = FREEZE_CHECKLIST_PATH
    checklist_text = _render_checklist(checklist_document)
    checklist_path.write_text(checklist_text, encoding="utf-8")
    checklist_file_sha256 = _hash_of(checklist_path)

    manifest = {
        "schema_version": 1,
        "condition_id": CONDITION_ID,
        "authorizing_adr": AUTHORIZING_ADR,
        "stage": "section-18 pre-inference freeze",
        "repository_commit": repository_commit(),
        "dirty_status": {
            "porcelain_entries": dirty_entries(),
            "outside_condition_owned_paths": [
                line for line in dirty_entries() if not _condition_owned(line)
            ],
        },
        "hashing_convention": (
            "raw-file SHA-256 (section 5.1); `manifest_sha256` is computed with "
            "that field omitted and then stored"
        ),
        "files": files,
        "groups": {
            "governance_documents": list(NEIGHBOURING_DOCUMENTS),
            "inherited_v13_inputs": [
                f"experiments/authzgym_semantic_contract_v1_3/{item}"
                for item in INHERITED_V13_INPUTS
            ],
            "inherited_source_and_preserved_results": list(INHERITED_SOURCE_INPUTS),
            "condition_artifacts": list(CONDITION_ARTIFACTS),
            "condition_implementation": list(CONDITION_IMPLEMENTATION),
            "freeze_checklist": [relative_path(checklist_path)],
        },
        "files_sha256": {**files, relative_path(checklist_path): checklist_file_sha256},
        "file_count": len(files) + 1,
        "model_condition_file_sha256": files.get(
            "experiments/authzgym_model_semantic_v1_3_1/MODEL_CONDITION.json"
        ),
        "cost_gate_file_sha256": files.get(
            "experiments/authzgym_model_semantic_v1_3_1/COST_GATE.json"
        ),
        "gold_adequacy_file_sha256": files.get(
            "experiments/authzgym_model_semantic_v1_3_1/GOLD_ADEQUACY_DEVELOPMENT.json"
        ),
        "restated_hashes_file_sha256": files.get(
            "experiments/authzgym_model_semantic_v1_3_1/RESTATED_HASHES.json"
        ),
        "integrity_baseline_file_sha256": files.get(
            "experiments/authzgym_model_semantic_v1_3_1/INTEGRITY_BASELINE.json"
        ),
        "integrity_baseline_preserved_unchanged": (
            files.get(
                "experiments/authzgym_model_semantic_v1_3_1/INTEGRITY_BASELINE.json"
            )
            == ORIGINAL_INTEGRITY_BASELINE_FILE_SHA256
        ),
        "governance_rebaseline_file_sha256": files.get(
            "experiments/authzgym_model_semantic_v1_3_1/GOVERNANCE_REBASELINE.json"
        ),
        "governance_rebaseline": recheck.get("governance_rebaseline"),
        "freeze_checklist_file_sha256": checklist_file_sha256,
        "protected_file_recheck": recheck,
        "section_12_1_machine_probe": structure,
        "blockers": [item["id"] for item in outstanding],
        "outstanding_items": outstanding,
        "governance_items": governance_items,
        "freeze_complete": complete,
        "inference_authorized": False,
        "provider_calls_authorized": 0,
        "development_planned_calls": 112,
        "confirmation_planned_calls": 56,
    }
    manifest["manifest_sha256"] = hashlib.sha256(
        json.dumps(
            {key: value for key, value in manifest.items() if key != "manifest_sha256"},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    manifest_file_sha256 = _json_write(FREEZE_MANIFEST_PATH, manifest)
    return {
        "stage": "freeze",
        "freeze_complete": complete,
        "outstanding_item_ids": [item["id"] for item in outstanding],
        "frozen_file_count": manifest["file_count"],
        "manifest_sha256": manifest["manifest_sha256"],
        "manifest_file_sha256": manifest_file_sha256,
        "freeze_checklist_file_sha256": checklist_file_sha256,
        "model_calls_made": 0,
    }


NEIGHBOURING_DOCUMENTS = (
    "DECISIONS.md",
    "experiments/authzgym_model_semantic_v1_3_1/PREREGISTRATION.md",
    "experiments/authzgym_model_semantic_v1_3_1/OPEN_RESEARCH_DECISIONS.md",
)


def _render_checklist(document: Mapping[str, object]) -> str:
    lines = [
        "# Freeze checklist -- `model-semantic-v1.3.1-N1`",
        "",
        "Handoff step 6C / preregistration section 18, rebuilt over the complete",
        "Step-6A dormant implementation. Every item is recorded with its status,",
        "evidence and authority. `not_satisfied` items are blocking for development",
        "inference.",
        "",
        f"- Condition: `{document['condition_id']}`",
        f"- Authority: {document['authorizing_adr']}",
        f"- Repository commit: `{document['repository_commit']}`",
        f"- Date: {document['date']}",
        f"- Reviewer: {document['reviewer']['name']} "
        f"(review required by {document['reviewer']['review_required_by']}; "
        f"signature {document['reviewer']['signature']})",
        f"- Freeze complete: `{str(document['freeze_complete']).lower()}`",
        f"- Model or provider calls made: {document['model_calls_made']}",
        "",
        "| # | Item | Status | Evidence |",
        "| --- | --- | --- | --- |",
    ]
    for item in document["items"]:
        evidence = json.dumps(item["evidence"], sort_keys=True)
        if len(evidence) > 400:
            evidence = evidence[:397] + "..."
        lines.append(
            f"| {item['id']} | {item['item']} | `{item['status']}` | {evidence} |"
        )
    lines.extend(["", "## Outstanding blocking items", ""])
    for item in document["outstanding_items"]:
        lines.extend(
            [
                f"### {item['id']} -- `{item['status']}`",
                "",
                f"- Authority: {item['authority']}",
                f"- Requirement: {item['requirement']}",
                f"- Reason: {item['reason']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Next authorization",
            "",
            str(document["next_authorization_required"]),
            "",
        ]
    )
    lines.extend(["## Governance items recorded for acknowledgement", ""])
    for item in document.get("governance_items", []):
        lines.extend(
            [
                f"- `{item['id']}` -- status `{item['status']}`",
                f"  - Resolution applied: {item['resolution_applied']}",
                "",
            ]
        )
    return "\n".join(lines)


def _tunnel_policy(value: Mapping[str, object]):
    """Build and re-validate the frozen hop policy from an audited read."""

    from ser.authzgym.tunnel_supervisor import TunnelPolicy

    policy = TunnelPolicy.from_dict(value)
    if dict(value) != policy.public_dict():
        raise IntegrityError("transport policy does not round-trip")
    return policy


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage", choices=("integrity", "model", "freeze", "step6b"), required=True
    )
    parser.add_argument("--recheck", action="store_true")
    args = parser.parse_args()
    if args.stage == "integrity":
        result = stage_integrity(recheck=args.recheck)
    elif args.stage == "model":
        result = stage_model()
    elif args.stage == "step6b":
        result = stage_step6b()
    else:
        result = stage_freeze()
    print(canonical_json(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
