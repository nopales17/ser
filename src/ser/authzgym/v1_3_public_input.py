"""Public-only request assembly and normal state for AuthzGym v1.3.

This module is deliberately outside the evaluator package and has no oracle,
gold, usefulness, role, mechanism, or scoring access.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from ser.core.types import content_hash

from .v1_3_contract import parse_response


class PublicInputV13Error(ValueError):
    pass


FORBIDDEN_PUBLIC_NAMES = {
    "DEVELOPMENT_RESTRICTED_POPULATION.json",
    "CONFIRMATION_RESTRICTED_POPULATION.json",
    "DEVELOPMENT_TRANSFORMATION_MAPS.json",
    "CONFIRMATION_TRANSFORMATION_MAPS.json",
    "ORACLE_VALIDATION.json",
    "provider_responses.jsonl",
}


@dataclass(frozen=True)
class NormalState:
    """Empty initial state and actual-response-derived updates only."""

    facts: tuple[tuple[str, bool], ...]
    candidate_effects: tuple[tuple[str, str], ...]
    unresolved_targets: tuple[tuple[str, tuple[tuple[str, bool], ...]], ...]
    response_sha256: str

    @classmethod
    def empty(cls) -> "NormalState":
        return cls((), (), (), "")

    def to_dict(self) -> dict:
        return {
            "facts": dict(self.facts),
            "candidate_effects": dict(self.candidate_effects),
            "unresolved_targets": {
                target: dict(values) for target, values in self.unresolved_targets
            },
            "response_sha256": self.response_sha256,
            "oracle_derived_prior": False,
        }


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _refuse_restricted(public_dir: Path) -> None:
    for path in public_dir.rglob("*"):
        if path.name in FORBIDDEN_PUBLIC_NAMES:
            raise PublicInputV13Error(
                f"restricted field is present in public input directory: {path}"
            )


def load_public_bundle(public_dir: Path) -> tuple[dict, dict, str]:
    _refuse_restricted(public_dir)
    contract = _read_json(public_dir / "PUBLIC_CONTRACT.json")
    prompt = (public_dir / "prompts/semantic_observation_v1_3.txt").read_text(
        encoding="utf-8"
    )
    return contract, prompt, content_hash(contract)


def build_normal_request(
    case: Mapping[str, object],
    prompt: str,
    *,
    oracle_view: object | None = None,
) -> dict:
    if oracle_view is not None:
        raise PublicInputV13Error("normal entry point rejects oracle arguments")
    visible = case["model_visible_input"]
    return {
        "system_instruction": prompt,
        "user_payload": {
            "semantic_interface": visible["semantic_interface"],
            "instruction_scope": visible["instruction_scope"],
            "current_artifact": {
                "slot": visible["current_artifact"]["slot"],
                "public_id": visible["current_artifact"]["public_id"],
                "path": visible["current_artifact"]["path"],
                "source": visible["current_artifact"]["source"],
            },
            "candidate_hypotheses": [
                {
                    "slot": item["slot"],
                    "public_label": item["public_label"],
                    "effect_family": item["effect_family"],
                    "description": item["description"],
                }
                for item in visible["candidate_hypotheses"]
            ],
            "public_artifact_inventory": [
                {
                    "slot": item["slot"],
                    "public_id": item["public_id"],
                    "path": item["path"],
                    "exported_symbols": list(item["exported_symbols"]),
                    "line_count": item["line_count"],
                    "inspection_status": item["inspection_status"],
                }
                for item in visible["public_artifact_inventory"]
            ],
            "legal_uninspected_target_slots": list(
                visible["legal_uninspected_target_slots"]
            ),
        },
        "response_schema": case["response_schema"],
    }


def normal_request_bytes(
    case: Mapping[str, object],
    prompt: str,
    *,
    oracle_view: object | None = None,
) -> bytes:
    request = build_normal_request(case, prompt, oracle_view=oracle_view)
    return json.dumps(
        request, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def start_normal_state() -> NormalState:
    return NormalState.empty()


def accept_normal_response(
    state: NormalState,
    case: Mapping[str, object],
    contract: Mapping[str, object],
    response: object,
) -> NormalState:
    if state != NormalState.empty():
        raise PublicInputV13Error("v1.3 normal initial state must be empty")
    legal = tuple(int(item) for item in case["runner_control"]["legal_target_slots"])
    parsed = parse_response(response, contract, legal)
    return NormalState(
        tuple(sorted(parsed["facts"].items())),
        tuple(sorted(parsed["candidate_effects"].items())),
        tuple(
            (target, tuple(sorted(values.items())))
            for target, values in sorted(parsed["unresolved_targets"].items())
        ),
        content_hash(response),
    )


def replay_public_requests(
    cases: list[Mapping[str, object]],
    prompt: str,
) -> list[str]:
    return [
        content_hash(json.loads(normal_request_bytes(case, prompt).decode("utf-8")))
        for case in cases
    ]
