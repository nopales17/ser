"""Public contract and strict response parsing for AuthzGym v1.3.

This module is intentionally vocabulary-only.  It does not derive benchmark
labels, inspect source, or import evaluator/scoring helpers.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Mapping


SEMANTIC_INTERFACE = "authzgym_semantic_observation_v1_3"
DEFAULT_PUBLIC_CONTRACT_PATH = (
    Path(__file__).resolve().parents[3]
    / "experiments"
    / "authzgym_semantic_contract_v1_3"
    / "PUBLIC_CONTRACT.json"
)


class ContractV13Error(ValueError):
    """A request or response violates the frozen v1.3 contract."""


def load_public_contract(path: Path | str | None = None) -> dict:
    contract_path = Path(path) if path is not None else DEFAULT_PUBLIC_CONTRACT_PATH
    value = json.loads(contract_path.read_text(encoding="utf-8"))
    validate_public_contract(value)
    return value


def validate_public_contract(contract: Mapping[str, object]) -> None:
    if not isinstance(contract, Mapping):
        raise ContractV13Error("public contract must be an object")
    if contract.get("schema_version") != 1:
        raise ContractV13Error("public contract schema_version must be 1")
    if contract.get("semantic_interface") != SEMANTIC_INTERFACE:
        raise ContractV13Error("public contract semantic_interface mismatch")
    if contract.get("instruction_scope") != "current_artifact_only":
        raise ContractV13Error("public contract instruction scope mismatch")

    fact_slots = contract.get("fact_slots")
    if not isinstance(fact_slots, Mapping) or tuple(fact_slots) != tuple(
        f"f{index}" for index in range(17)
    ):
        raise ContractV13Error("public contract must contain exactly f0--f16")
    if len(set(fact_slots.values())) != 17:
        raise ContractV13Error("public fact meanings must be unique")

    candidate_slots = contract.get("candidate_slots")
    if candidate_slots != ["c0", "c1", "c2", "c3"]:
        raise ContractV13Error("public contract candidate slots must be c0--c3")
    families = contract.get("effect_families")
    if families != ["ownership", "membership", "role", "context"]:
        raise ContractV13Error("public contract effect family order mismatch")
    descriptions = contract.get("candidate_descriptions")
    if not isinstance(descriptions, Mapping) or set(descriptions) != set(families):
        raise ContractV13Error("public contract candidate descriptions mismatch")
    if contract.get("effect_values") != [
        "support",
        "contradict",
        "neutral",
        "unknown",
    ]:
        raise ContractV13Error("public contract effect value order mismatch")

    relation_slots = contract.get("relation_slots")
    if not isinstance(relation_slots, Mapping) or tuple(relation_slots) != tuple(
        f"r{index}" for index in range(5)
    ):
        raise ContractV13Error("public contract must contain exactly r0--r4")
    if list(relation_slots.values()) != [
        "ownership",
        "membership",
        "role",
        "context",
        "general_dependency",
    ]:
        raise ContractV13Error("public contract relation categories mismatch")

    if contract.get("response_top_level_keys") != [
        "facts",
        "candidate_effects",
        "unresolved_targets",
    ]:
        raise ContractV13Error("public response top-level keys mismatch")
    retired = set(contract.get("retired_fact_slots", ()))
    if retired != {f"f{index}" for index in range(17, 25)}:
        raise ContractV13Error("retired fact slots must be f17--f24")
    if contract.get("normal_summary_fields") != []:
        raise ContractV13Error("v1.3 normal input must not contain a summary")


def response_schema(contract: Mapping[str, object], legal_target_slots: Iterable[int]) -> dict:
    validate_public_contract(contract)
    slots = tuple(int(item) for item in legal_target_slots)
    if len(slots) != len(set(slots)) or any(slot < 0 for slot in slots):
        raise ContractV13Error("legal target slots must be unique nonnegative integers")
    fact_slots = tuple(contract["fact_slots"])
    candidate_slots = tuple(contract["candidate_slots"])
    relation_slots = tuple(contract["relation_slots"])
    target_properties = {
        f"t{slot}": {
            "type": "object",
            "additionalProperties": False,
            "required": list(relation_slots),
            "properties": {
                relation_slot: {"type": "boolean"} for relation_slot in relation_slots
            },
        }
        for slot in slots
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "required": list(contract["response_top_level_keys"]),
        "properties": {
            "facts": {
                "type": "object",
                "additionalProperties": False,
                "required": list(fact_slots),
                "properties": {
                    fact_slot: {"type": "boolean"} for fact_slot in fact_slots
                },
            },
            "candidate_effects": {
                "type": "object",
                "additionalProperties": False,
                "required": list(candidate_slots),
                "properties": {
                    candidate_slot: {
                        "type": "string",
                        "enum": list(contract["effect_values"]),
                    }
                    for candidate_slot in candidate_slots
                },
            },
            "unresolved_targets": {
                "type": "object",
                "additionalProperties": False,
                "required": list(target_properties),
                "properties": target_properties,
            },
        },
    }


def parse_response(
    value: object,
    contract: Mapping[str, object],
    legal_target_slots: Iterable[int],
) -> dict:
    """Parse a response without prose recovery, aliases, or manual repair."""

    validate_public_contract(contract)
    if not isinstance(value, dict) or set(value) != set(contract["response_top_level_keys"]):
        raise ContractV13Error("top-level response shape mismatch")

    facts = value["facts"]
    fact_slots = tuple(contract["fact_slots"])
    if not isinstance(facts, dict) or set(facts) != set(fact_slots):
        raise ContractV13Error("fact response shape mismatch")
    if any(type(item) is not bool for item in facts.values()):
        raise ContractV13Error("fact response values must be JSON booleans")

    effects = value["candidate_effects"]
    candidate_slots = tuple(contract["candidate_slots"])
    if not isinstance(effects, dict) or set(effects) != set(candidate_slots):
        raise ContractV13Error("candidate-effect response shape mismatch")
    if any(item not in contract["effect_values"] for item in effects.values()):
        raise ContractV13Error("candidate-effect value is outside the frozen enum")

    targets = value["unresolved_targets"]
    expected_targets = {f"t{slot}" for slot in legal_target_slots}
    if not isinstance(targets, dict) or set(targets) != expected_targets:
        raise ContractV13Error("unresolved-target response shape mismatch")
    relation_slots = tuple(contract["relation_slots"])
    for target in targets.values():
        if not isinstance(target, dict) or set(target) != set(relation_slots):
            raise ContractV13Error("relation response shape mismatch")
        if any(type(item) is not bool for item in target.values()):
            raise ContractV13Error("relation response values must be JSON booleans")

    return {
        "facts": {slot: bool(facts[slot]) for slot in fact_slots},
        "candidate_effects": {
            slot: str(effects[slot]) for slot in candidate_slots
        },
        "unresolved_targets": {
            target: {slot: bool(targets[target][slot]) for slot in relation_slots}
            for target in sorted(targets, key=lambda item: int(item[1:]))
        },
    }


def effect_from_facts(
    contract: Mapping[str, object],
    candidates: list[dict],
    facts: Mapping[str, bool],
) -> dict[str, str]:
    """Apply the frozen public local-cue table to a submitted fact vector."""

    validate_public_contract(contract)
    support_by_family = contract["effect_support_cues"]
    counter_by_family = contract["effect_counter_cues"]
    result = {}
    for index, candidate in enumerate(candidates):
        family = str(candidate["effect_family"])
        support = any(bool(facts[slot]) for slot in support_by_family[family])
        counter = any(bool(facts[slot]) for slot in counter_by_family[family])
        if support and not counter:
            value = "support"
        elif counter and not support:
            value = "contradict"
        elif support and counter:
            value = "neutral"
        else:
            value = "unknown"
        result[f"c{index}"] = value
    return result
