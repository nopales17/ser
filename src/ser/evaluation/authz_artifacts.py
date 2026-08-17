"""Fail-closed manifests and artifacts for Static Semantic AuthzGym v1."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable, Mapping

from ser.authzgym.generation import AUTHZ_AUTHORING_SEED
from ser.authzgym.model import AUTHZ_RESOURCE_SCHEMA, AuthzEpisode
from ser.core.types import content_hash

from .artifacts import verify_record_hash, write_new_json, write_new_jsonl


BENCHMARK_NAME = "authzgym-static-v1"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def population_payload(
    split: str,
    episodes: Iterable[AuthzEpisode],
    preregistration_path: Path,
    prompt_paths: tuple[Path, ...],
    model_config_path: Path,
) -> dict:
    episodes = tuple(episodes)
    return {
        "schema_version": 1,
        "benchmark": BENCHMARK_NAME,
        "split": split,
        "visibility": "evaluator_only_experiment_definition",
        "frozen_before_aggregate_evaluation": True,
        "real_model_calls_authorized": False,
        "benchmark_construction_is_empirical_support": False,
        "authoring_seed": AUTHZ_AUTHORING_SEED,
        "preregistration_sha256": file_sha256(preregistration_path),
        "prompt_hashes": {path.name: file_sha256(path) for path in prompt_paths},
        "model_config_sha256": file_sha256(model_config_path),
        "resource_schema": [
            {"name": item.name, "unit": item.unit}
            for item in AUTHZ_RESOURCE_SCHEMA.dimensions
        ],
        "episodes": [item.to_dict() for item in episodes],
    }


def freeze_population(
    path: Path,
    split: str,
    episodes: Iterable[AuthzEpisode],
    preregistration_path: Path,
    prompt_paths: tuple[Path, ...],
    model_config_path: Path,
) -> str:
    payload = population_payload(
        split,
        episodes,
        preregistration_path,
        prompt_paths,
        model_config_path,
    )
    digest = content_hash(payload)
    write_new_json(path, {**payload, "population_hash": digest})
    return digest


def load_population(path: Path) -> tuple[tuple[AuthzEpisode, ...], str, dict]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    digest = str(raw.pop("population_hash"))
    if content_hash(raw) != digest:
        raise ValueError(f"AuthzGym population hash mismatch: {path.name}")
    return (
        tuple(AuthzEpisode.from_dict(item) for item in raw["episodes"]),
        digest,
        raw,
    )


def write_run_records(path: Path, records: Iterable[dict]) -> None:
    write_new_jsonl(path, records)


def verify_record_hashes(records: Iterable[Mapping[str, object]]) -> bool:
    return all(verify_record_hash(item) for item in records)
