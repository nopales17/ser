"""Deterministic AuthzGym v1.3 population conversion and transformations."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable, Mapping

from ser.core.types import content_hash

from .v1_3_contract import (
    SEMANTIC_INTERFACE,
    effect_from_facts,
    load_public_contract,
    response_schema,
)


VARIANTS = (
    "base_entry",
    "longest_artifact",
    "artifact_reordering",
    "symbol_renaming",
    "candidate_label_renaming",
    "artifact_identifier_variation",
    "combined_permutation",
)
SEMANTIC_EQUIVALENCE_VARIANTS = VARIANTS[2:]
FAMILIES = ("ownership", "membership", "role", "context")


class PopulationV13Error(ValueError):
    """A source cannot be converted under the frozen v1.3 rules."""


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _bijection_token(
    source_episode_id: str,
    variant_id: str,
    namespace: str,
    original_token: str,
) -> str:
    payload = content_hash(
        {
            "source_episode_id": source_episode_id,
            "variant_id": variant_id,
            "namespace": namespace,
            "original_token": original_token,
        }
    )
    return payload[:12]


class _Bijection:
    def __init__(self, source_episode_id: str, variant_id: str, namespace: str, prefix: str):
        self.source_episode_id = source_episode_id
        self.variant_id = variant_id
        self.namespace = namespace
        self.prefix = prefix
        self.forward: dict[str, str] = {}
        self.inverse: dict[str, str] = {}

    def apply(self, token: str) -> str:
        if token not in self.forward:
            transformed = f"{self.prefix}{_bijection_token(self.source_episode_id, self.variant_id, self.namespace, token)}"
            if transformed in self.inverse:
                raise PopulationV13Error(
                    f"bijection collision in {self.namespace}: {transformed}"
                )
            self.forward[token] = transformed
            self.inverse[transformed] = token
        return self.forward[token]


def _source_payload(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    digest = payload.get("population_hash")
    body = dict(payload)
    body.pop("population_hash", None)
    if not isinstance(digest, str) or content_hash(body) != digest:
        raise PopulationV13Error("source development population hash mismatch")
    if payload.get("benchmark") != "authzgym-static-v1":
        raise PopulationV13Error("unexpected source benchmark identifier")
    return payload


def _source_family(episode: Mapping[str, object]) -> str:
    mechanism = str(episode["restricted_truth"]["mechanism_id"])
    mapping = {"h1": "ownership", "h2": "membership", "h3": "role", "h4": "context"}
    if mechanism not in mapping:
        raise PopulationV13Error(f"unsupported source mechanism: {mechanism}")
    return mapping[mechanism]


def _base_candidates(source_episode_id: str, contract: Mapping[str, object]) -> list[dict]:
    candidates = []
    for index, family in enumerate(contract["effect_families"]):
        label = f"label-{_bijection_token(source_episode_id, 'base_entry', 'candidate_label', family)}"
        candidates.append(
            {
                "slot": f"c{index}",
                "public_label": label,
                "effect_family": family,
                "description": contract["candidate_descriptions"][family],
            }
        )
    return candidates


def _base_inventory(episode: Mapping[str, object]) -> list[dict]:
    by_id = {
        str(item["descriptor"]["artifact_id"]): item for item in episode["artifacts"]
    }
    inventory = []
    for slot, artifact_id in enumerate(episode["public"]["artifact_inventory"]):
        artifact = by_id[str(artifact_id["artifact_id"])]
        descriptor = artifact["descriptor"]
        inventory.append(
            {
                "slot": slot,
                "public_id": str(descriptor["artifact_id"]),
                "path": str(descriptor["path"]),
                "exported_symbols": [str(item) for item in descriptor["exported_symbols"]],
                "line_count": int(descriptor["line_count"]),
                "source": str(artifact["source"]),
                "canonical_ordinal": slot,
                "usefulness": float(
                    artifact["restricted_truth"]["evaluator_usefulness"]
                ),
            }
        )
    return inventory


def _rename_source(source: str, symbol_map: Mapping[str, str]) -> str:
    placeholders: dict[str, str] = {}
    result = source
    for index, old in enumerate(sorted(symbol_map, key=lambda item: (-len(item), item))):
        if old not in result:
            continue
        placeholder = f"__SER_V13_SYMBOL_{index}__"
        result = result.replace(old, placeholder)
        placeholders[placeholder] = symbol_map[old]
    for placeholder, value in placeholders.items():
        result = result.replace(placeholder, value)
    return result


def _variant_inventory(
    source_episode_id: str,
    variant: str,
    base_inventory: list[dict],
    *,
    current_id: str,
) -> tuple[list[dict], dict]:
    artifact_id_map = _Bijection(
        source_episode_id, variant, "artifact_id", "aid-"
    )
    path_map = _Bijection(source_episode_id, variant, "artifact_path", "path-")
    symbol_map = _Bijection(
        source_episode_id, variant, "artifact_symbol", "sym_"
    )

    use_identifiers = variant in ("artifact_identifier_variation", "combined_permutation")
    use_symbols = variant in ("symbol_renaming", "combined_permutation")
    reverse_other = variant in ("artifact_reordering", "combined_permutation")

    if use_symbols:
        for item in base_inventory:
            for symbol in item["exported_symbols"]:
                symbol_map.apply(symbol)
    if use_identifiers:
        for item in base_inventory:
            artifact_id_map.apply(item["public_id"])
            path_map.apply(item["path"])

    working = []
    for item in base_inventory:
        value = dict(item)
        if use_identifiers:
            value["public_id"] = artifact_id_map.apply(item["public_id"])
            value["path"] = path_map.apply(item["path"])
        if use_symbols:
            value["exported_symbols"] = [
                symbol_map.apply(symbol) for symbol in item["exported_symbols"]
            ]
            value["source"] = _rename_source(item["source"], symbol_map.forward)
        working.append(value)

    if reverse_other:
        current_ordinal = next(
            item["canonical_ordinal"]
            for item in base_inventory
            if item["public_id"] == current_id
        )
        entry = next(
            item for item in working if item["canonical_ordinal"] == current_ordinal
        )
        others = [item for item in working if item is not entry]
        working = [entry, *reversed(others)]

    for slot, item in enumerate(working):
        item["slot"] = slot
    maps = {
        "artifact_id_forward": dict(artifact_id_map.forward),
        "artifact_id_inverse": dict(artifact_id_map.inverse),
        "path_forward": dict(path_map.forward),
        "path_inverse": dict(path_map.inverse),
        "symbol_forward": dict(symbol_map.forward),
        "symbol_inverse": dict(symbol_map.inverse),
    }
    return working, maps


def _variant_candidates(
    source_episode_id: str,
    variant: str,
    base_candidates: list[dict],
) -> tuple[list[dict], dict]:
    rename = variant in ("candidate_label_renaming", "combined_permutation")
    reverse = variant == "combined_permutation"
    label_map = _Bijection(
        source_episode_id, variant, "candidate_public_label", "label-"
    )
    ordered = list(reversed(base_candidates)) if reverse else list(base_candidates)
    result = []
    for slot, candidate in enumerate(ordered):
        item = dict(candidate)
        item["slot"] = f"c{slot}"
        if rename:
            item["public_label"] = label_map.apply(candidate["public_label"])
        result.append(item)
    maps = {
        "candidate_label_forward": dict(label_map.forward),
        "candidate_label_inverse": dict(label_map.inverse),
        "candidate_family_by_slot": {
            f"c{index}": item["effect_family"] for index, item in enumerate(result)
        },
        "canonical_base_slot_by_variant_slot": {
            f"c{index}": candidate["slot"]
            for index, candidate in enumerate(ordered)
        },
    }
    return result, maps


def build_variant_cases(
    source_episode: Mapping[str, object],
    contract: Mapping[str, object],
    *,
    split: str,
    repeat_count: int,
) -> tuple[list[dict], list[dict]]:
    source_episode_id = str(source_episode["public"]["episode_id"])
    source_family = _source_family(source_episode)
    base_inventory = _base_inventory(source_episode)
    base_candidates = _base_candidates(source_episode_id, contract)
    entry_id = str(source_episode["public"]["entry_artifact_id"])

    public_cases: list[dict] = []
    restricted_cases: list[dict] = []
    for variant_index, variant in enumerate(VARIANTS):
        if variant == "longest_artifact":
            counts = [item["line_count"] for item in base_inventory]
            maximum = max(counts)
            if counts.count(maximum) != 1:
                raise PopulationV13Error(
                    f"longest artifact tie for source {source_episode_id}"
                )
            current_id = next(
                item["public_id"]
                for item in base_inventory
                if item["line_count"] == maximum
            )
        else:
            current_id = entry_id

        inventory, artifact_maps = _variant_inventory(
            source_episode_id,
            variant,
            base_inventory,
            current_id=current_id,
        )
        candidates, candidate_maps = _variant_candidates(
            source_episode_id,
            variant,
            base_candidates,
        )
        current_ordinal = next(
            item["canonical_ordinal"]
            for item in base_inventory
            if item["public_id"] == current_id
        )
        current_slot = next(
            item["slot"]
            for item in inventory
            if item["canonical_ordinal"] == current_ordinal
        )
        for item in inventory:
            item["inspection_status"] = (
                "current" if item["slot"] == current_slot else "uninspected"
            )
        legal_target_slots = tuple(
            item["slot"] for item in inventory if item["slot"] != current_slot
        )
        for item in inventory:
            if item["inspection_status"] == "uninspected" and len(item["exported_symbols"]) != 1:
                raise PopulationV13Error(
                    f"uninspected target does not export exactly one symbol: {item['public_id']}"
                )
        visible = {
            "semantic_interface": SEMANTIC_INTERFACE,
            "instruction_scope": "current_artifact_only",
            "current_artifact": {
                "slot": current_slot,
                "public_id": next(
                    item["public_id"]
                    for item in inventory
                    if item["slot"] == current_slot
                ),
                "path": next(
                    item["path"] for item in inventory if item["slot"] == current_slot
                ),
                "source": next(
                    item["source"] for item in inventory if item["slot"] == current_slot
                ),
            },
            "candidate_hypotheses": [
                {
                    "slot": item["slot"],
                    "public_label": item["public_label"],
                    "effect_family": item["effect_family"],
                    "description": item["description"],
                }
                for item in candidates
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
                for item in inventory
            ],
            "legal_uninspected_target_slots": list(legal_target_slots),
        }
        schema = response_schema(contract, legal_target_slots)
        public_input_sha256 = content_hash(
            {"model_visible_input": visible, "response_schema": schema}
        )
        case_id = (
            f"{source_episode_id}--{variant}--"
            f"{public_input_sha256[:10]}"
        )
        public_cases.append(
            {
                "schema_version": 1,
                "case_id": case_id,
                "split": split,
                "source_episode_id": source_episode_id,
                "variant": variant,
                "variant_index": variant_index,
                "model_visible_input": visible,
                "response_schema": schema,
                "runner_control": {
                    "repeat_count": repeat_count,
                    "current_artifact_slot": current_slot,
                    "legal_target_slots": list(legal_target_slots),
                    "schema_sha256": content_hash(schema),
                    "public_input_sha256": public_input_sha256,
                },
            }
        )

        base_by_id = {item["public_id"]: item for item in base_inventory}
        variant_by_base_id = {
            base_id: next(
                item["public_id"]
                for item in inventory
                if item["canonical_ordinal"]
                == base_by_id[base_id]["canonical_ordinal"]
            )
            for base_id in base_by_id
        }
        candidate_by_family = {
            item["effect_family"]: item for item in candidates
        }
        restricted_cases.append(
            {
                "schema_version": 1,
                "case_id": case_id,
                "source_episode_id": source_episode_id,
                "source_family": source_family,
                "variant": variant,
                "public_input_sha256": public_input_sha256,
                "canonical_current_artifact_id": current_id,
                "canonical_source_ordinal_by_variant_slot": {
                    f"t{item['slot']}": item["canonical_ordinal"]
                    for item in inventory
                    if item["slot"] != current_slot
                },
                "usefulness_by_variant_target_slot": {
                    f"t{item['slot']}": item["usefulness"]
                    for item in inventory
                    if item["slot"] != current_slot
                },
                "public_id_by_canonical_artifact_id": {
                    base_id: variant_by_base_id[base_id] for base_id in base_by_id
                },
                "candidate_slot_by_effect_family": {
                    family: candidate_by_family[family]["slot"] for family in FAMILIES
                },
                "candidate_family_by_slot": candidate_maps[
                    "candidate_family_by_slot"
                ],
                "transformation_maps": {
                    **artifact_maps,
                    **candidate_maps,
                    "base_artifact_order": [
                        item["public_id"] for item in base_inventory
                    ],
                    "variant_artifact_order": [
                        item["public_id"] for item in inventory
                    ],
                    "canonical_ordinal_by_variant_public_id": {
                        item["public_id"]: item["canonical_ordinal"]
                        for item in inventory
                    },
                    "variant_target_slot_by_canonical_artifact_id": {
                        base_id: next(
                            f"t{item['slot']}"
                            for item in inventory
                            if item["public_id"] == variant_by_base_id[base_id]
                            and item["slot"] != current_slot
                        )
                        for base_id in base_by_id
                        if variant_by_base_id[base_id]
                        != next(
                            item["public_id"]
                            for item in inventory
                            if item["slot"] == current_slot
                        )
                    },
                },
            }
        )
    return public_cases, restricted_cases


def build_source_cases(
    sources: Iterable[Mapping[str, object]],
    contract: Mapping[str, object],
    *,
    split: str,
    repeat_count: int,
) -> tuple[list[dict], list[dict]]:
    public_cases: list[dict] = []
    restricted_cases: list[dict] = []
    for source in sources:
        public, restricted = build_variant_cases(
            source, contract, split=split, repeat_count=repeat_count
        )
        public_cases.extend(public)
        restricted_cases.extend(restricted)
    if len({item["case_id"] for item in public_cases}) != len(public_cases):
        raise PopulationV13Error("variant/case identifiers are not unique")
    return public_cases, restricted_cases


def schedule_payload(public_cases: list[dict], *, repeats: int) -> list[dict]:
    return [
        {"case_id": case["case_id"], "repeat": repeat}
        for case in public_cases
        for repeat in range(1, repeats + 1)
    ]


def public_population_payload(
    public_cases: list[dict],
    *,
    experiment: str,
    split: str,
    repeat_count: int,
) -> dict:
    payload = {
        "schema_version": 1,
        "experiment": experiment,
        "split": split,
        "variant_count_per_source": len(VARIANTS),
        "source_count": len(public_cases) // len(VARIANTS),
        "repeat_count": repeat_count,
        "cases": public_cases,
        "schedule": schedule_payload(public_cases, repeats=repeat_count),
    }
    payload["population_hash"] = content_hash(payload)
    return payload


def load_development_contract() -> dict:
    return load_public_contract()


def build_development_population(source_path: Path) -> tuple[dict, dict]:
    contract = load_development_contract()
    source = _source_payload(source_path)
    public_cases, restricted_cases = build_source_cases(
        source["episodes"], contract, split="development", repeat_count=2
    )
    if len(public_cases) != 56:
        raise PopulationV13Error("development population must contain 56 cases")
    public = public_population_payload(
        public_cases,
        experiment="authzgym-semantic-contract-v1.3-development",
        split="development",
        repeat_count=2,
    )
    restricted = {
        "schema_version": 1,
        "experiment": "authzgym-semantic-contract-v1.3-development",
        "split": "development",
        "cases": restricted_cases,
        "source_population_hash": source["population_hash"],
        "source_path": str(source_path.as_posix()),
    }
    restricted["restricted_hash"] = content_hash(restricted)
    return public, restricted


def build_fresh_confirmation_population() -> tuple[dict, dict]:
    """Build the fixed fresh fallback before inspecting confirmation content."""

    from .generation import MECHANISMS, _episode

    contract = load_development_contract()
    sources = []
    for layout_index in (40, 41):
        for mechanism in MECHANISMS:
            sources.append(
                _episode(
                    "confirmation_v1_3",
                    layout_index,
                    mechanism,
                    decision_group=f"confirmation-v1-3-{layout_index}",
                    control_type="eligible_branch",
                ).to_dict()
            )
    public_cases, restricted_cases = build_source_cases(
        sources, contract, split="confirmation_v1_3", repeat_count=1
    )
    if len(public_cases) != 56:
        raise PopulationV13Error("confirmation population must contain 56 cases")
    public = public_population_payload(
        public_cases,
        experiment="authzgym-semantic-contract-v1.3-confirmation",
        split="confirmation_v1_3",
        repeat_count=1,
    )
    restricted = {
        "schema_version": 1,
        "experiment": "authzgym-semantic-contract-v1.3-confirmation",
        "split": "confirmation_v1_3",
        "layout_indices": [40, 41],
        "cases": restricted_cases,
        "source_population_hash": content_hash(
            {"split": "confirmation_v1_3", "layout_indices": [40, 41]}
        ),
    }
    restricted["restricted_hash"] = content_hash(restricted)
    return public, restricted
