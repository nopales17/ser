"""Compact semantic contract and development-only stress population for v1.2."""

from __future__ import annotations

import re
from dataclasses import replace
from typing import Mapping

from ser.core.types import content_hash

from .generation import permuted_episode
from .interpreters import _relation_tag
from .model import (
    ArtifactDescriptor,
    ArtifactSpec,
    AuthzEpisode,
    CandidateHypothesis,
    SemanticObservation,
    SemanticReference,
)


SEMANTIC_INTERFACE = "authzgym_semantic_observation_v1_2"
FACT_KEYS = (
    "alternate-entry",
    "direct-only-membership",
    "inherited-membership-included",
    "role-fallback",
    "role-map-transform",
    "role-preserved",
    "missing-token-scope",
    "missing-feature-context",
    "token-scope-forwarded",
    "feature-context-forwarded",
    "sensitive-without-owner-check",
    "ownership-compared",
    "weak-ownership-audit",
    "weak-membership-audit",
    "weak-role-audit",
    "weak-context-audit",
    "cross-layer-relationship",
    "alternate-entry-bypass",
    "inherited-membership-omitted",
    "guard-context-loss",
    "test-implementation-relationship",
    "ownership-behavioral-expectation",
    "membership-behavioral-expectation",
    "role-behavioral-expectation",
    "context-behavioral-expectation",
)
FACT_SLOTS = tuple(f"f{index}" for index in range(len(FACT_KEYS)))
FACT_BY_SLOT = dict(zip(FACT_SLOTS, FACT_KEYS))
SLOT_BY_FACT = {value: key for key, value in FACT_BY_SLOT.items()}
EFFECT_VALUES = ("support", "contradict", "neutral", "unknown")
RELATION_VALUES = (
    "ownership_path",
    "alternate_entry",
    "membership_path",
    "membership_inheritance",
    "role_path",
    "role_propagation",
    "context_path",
    "token_scope",
    "general_dependency",
)
RELATION_SLOTS = tuple(f"r{index}" for index in range(len(RELATION_VALUES)))
RELATION_BY_SLOT = dict(zip(RELATION_SLOTS, RELATION_VALUES))
VARIANTS = (
    "base_entry",
    "longest_artifact",
    "artifact_reordering",
    "symbol_renaming",
    "candidate_label_permutation",
    "artifact_identifier_variation",
    "maximal_public_summary",
    "combined_permutation",
)
SEMANTIC_EQUIVALENCE_VARIANTS = (
    "artifact_reordering",
    "symbol_renaming",
    "candidate_label_permutation",
    "artifact_identifier_variation",
    "combined_permutation",
)

# Evaluator-only mapping used after calls. It is not emitted in a model-visible
# schema or prompt as a correct-answer key.
FACT_RELATION_DIRECTIONS = {
    "alternate-entry": ("ownership_path", 1),
    "direct-only-membership": ("membership_path", 1),
    "inherited-membership-included": ("membership_path", -1),
    "role-fallback": ("role_path", 1),
    "role-map-transform": ("role_path", 1),
    "role-preserved": ("role_path", -1),
    "missing-token-scope": ("context_path", 1),
    "missing-feature-context": ("context_path", 1),
    "token-scope-forwarded": ("context_path", -1),
    "feature-context-forwarded": ("context_path", -1),
    "sensitive-without-owner-check": ("ownership_path", 1),
    "ownership-compared": ("ownership_path", -1),
    "weak-ownership-audit": ("ownership_path", 1),
    "weak-membership-audit": ("membership_path", 1),
    "weak-role-audit": ("role_path", 1),
    "weak-context-audit": ("context_path", 1),
    "alternate-entry-bypass": ("ownership_path", 1),
    "inherited-membership-omitted": ("membership_path", 1),
    "guard-context-loss": ("context_path", 1),
    "ownership-behavioral-expectation": ("ownership_path", 1),
    "membership-behavioral-expectation": ("membership_path", 1),
    "role-behavioral-expectation": ("role_path", 1),
    "context-behavioral-expectation": ("context_path", 1),
}
PUBLIC_FACT_BY_EXPECTED = {
    **{key: key for key in FACT_KEYS},
    "h1-behavioral-expectation": "ownership-behavioral-expectation",
    "h2-behavioral-expectation": "membership-behavioral-expectation",
    "h3-behavioral-expectation": "role-behavioral-expectation",
    "h4-behavioral-expectation": "context-behavioral-expectation",
}


class ContractV12Error(ValueError):
    """A response that violates the compact v1.2 contract."""


def vocabulary_payload() -> dict:
    return {
        "schema_version": 1,
        "semantic_interface": SEMANTIC_INTERFACE,
        "fact_slots": FACT_BY_SLOT,
        "candidate_slots": [f"c{index}" for index in range(4)],
        "effect_values": list(EFFECT_VALUES),
        "relation_slots": RELATION_BY_SLOT,
        "artifact_target_slots": "dynamic t{public_inventory_slot}; only legal uninspected targets are properties and each contains fixed relation booleans",
    }


def response_schema(legal_target_slots: tuple[int, ...]) -> dict:
    """Build the exact per-call schema; illegal dynamic references have no key."""

    fact_properties = {slot: {"type": "boolean"} for slot in FACT_SLOTS}
    effect_properties = {
        f"c{index}": {"type": "string", "enum": list(EFFECT_VALUES)}
        for index in range(4)
    }
    relation_properties = {
        slot: {"type": "boolean"} for slot in RELATION_SLOTS
    }
    target_properties = {
        f"t{slot}": {
            "type": "object",
            "additionalProperties": False,
            "required": list(RELATION_SLOTS),
            "properties": relation_properties,
        }
        for slot in legal_target_slots
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["facts", "hypothesis_effects", "unresolved_targets"],
        "properties": {
            "facts": {
                "type": "object",
                "additionalProperties": False,
                "required": list(FACT_SLOTS),
                "properties": fact_properties,
            },
            "hypothesis_effects": {
                "type": "object",
                "additionalProperties": False,
                "required": list(effect_properties),
                "properties": effect_properties,
            },
            "unresolved_targets": {
                "type": "object",
                "additionalProperties": False,
                "required": list(target_properties),
                "properties": target_properties,
            },
        },
    }


def _relation_to_candidate_slots(
    candidates: tuple[CandidateHypothesis, ...],
) -> dict[str, int]:
    return {
        relation: index
        for index, candidate in enumerate(candidates)
        for relation in candidate.relation_tags
    }


def _expected_effects(
    fact_keys: tuple[str, ...], candidates: tuple[CandidateHypothesis, ...]
) -> dict[str, dict[str, bool]]:
    relation_to_slot = _relation_to_candidate_slots(candidates)
    totals = {f"c{index}": 0 for index in range(4)}
    addressed = set()
    for fact_key in fact_keys:
        if fact_key not in FACT_RELATION_DIRECTIONS:
            continue
        relation, direction = FACT_RELATION_DIRECTIONS[fact_key]
        candidate_slot = relation_to_slot.get(relation)
        if candidate_slot is None:
            continue
        key = f"c{candidate_slot}"
        totals[key] += direction
        addressed.add(key)
    result = {}
    for key, total in totals.items():
        if key not in addressed:
            result[key] = "unknown"
        elif total > 0:
            result[key] = "support"
        elif total < 0:
            result[key] = "contradict"
        else:
            result[key] = "neutral"
    return result


def _expected_unresolved_targets(
    episode: AuthzEpisode,
    artifact: ArtifactSpec,
    legal_target_slots: tuple[int, ...],
) -> dict[str, str]:
    slot_by_artifact = {
        artifact_id: index for index, artifact_id in enumerate(episode.artifact_order)
    }
    symbol_index = {
        symbol: item.descriptor.artifact_id
        for item in episode.artifacts
        for symbol in item.descriptor.exported_symbols
    }
    result = {
        f"t{slot}": {relation_slot: False for relation_slot in RELATION_SLOTS}
        for slot in legal_target_slots
    }
    for line in artifact.source.splitlines():
        for symbol, target_id in symbol_index.items():
            target_slot = slot_by_artifact[target_id]
            if target_slot not in legal_target_slots:
                continue
            if re.search(rf"\b{re.escape(symbol)}\s*\(", line):
                relation = _relation_tag(line)
                key = f"t{target_slot}"
                relation_slot = next(
                    slot for slot, value in RELATION_BY_SLOT.items() if value == relation
                )
                result[key][relation_slot] = True
    return result


def oracle_content(
    episode: AuthzEpisode,
    artifact_slot: int,
    legal_target_slots: tuple[int, ...],
) -> dict:
    artifact = episode.artifact(episode.artifact_order[artifact_slot])
    expected = {
        PUBLIC_FACT_BY_EXPECTED[item] for item in artifact.expected_fact_keys
    }
    return {
        "facts": {slot: fact in expected for slot, fact in FACT_BY_SLOT.items()},
        "hypothesis_effects": _expected_effects(
            tuple(expected), episode.candidates
        ),
        "unresolved_targets": _expected_unresolved_targets(
            episode, artifact, legal_target_slots
        ),
    }


def parse_content(
    value: object,
    episode: AuthzEpisode,
    legal_target_slots: tuple[int, ...],
) -> tuple[SemanticObservation, dict]:
    if not isinstance(value, dict) or set(value) != {
        "facts",
        "hypothesis_effects",
        "unresolved_targets",
    }:
        raise ContractV12Error("top-level fields do not match v1.2")
    facts = value["facts"]
    effects = value["hypothesis_effects"]
    targets = value["unresolved_targets"]
    if not isinstance(facts, dict) or set(facts) != set(FACT_SLOTS):
        raise ContractV12Error("fact slots do not match v1.2")
    if any(type(item) is not bool for item in facts.values()):
        raise ContractV12Error("fact values must be booleans")
    expected_effect_slots = {f"c{index}" for index in range(4)}
    if not isinstance(effects, dict) or set(effects) != expected_effect_slots:
        raise ContractV12Error("candidate effect slots do not match v1.2")
    if any(item not in EFFECT_VALUES for item in effects.values()):
        raise ContractV12Error("candidate effect value is outside the enum")
    expected_target_slots = {f"t{slot}" for slot in legal_target_slots}
    if not isinstance(targets, dict) or set(targets) != expected_target_slots:
        raise ContractV12Error("artifact target slots do not match the legal set")
    for target in targets.values():
        if not isinstance(target, dict) or set(target) != set(RELATION_SLOTS):
            raise ContractV12Error("unresolved relation slots do not match v1.2")
        if any(type(item) is not bool for item in target.values()):
            raise ContractV12Error("unresolved relation values must be booleans")

    fact_keys = tuple(FACT_BY_SLOT[key] for key in FACT_SLOTS if facts[key])
    numeric = {"support": 1.0, "contradict": -1.0, "neutral": 0.0, "unknown": 0.0}
    hypothesis_effects = tuple(
        (episode.candidates[index].hypothesis_id, numeric[effects[f"c{index}"]])
        for index in range(4)
    )
    references = []
    for slot in legal_target_slots:
        artifact = episode.artifact(episode.artifact_order[slot])
        if len(artifact.descriptor.exported_symbols) != 1:
            raise ContractV12Error("target slot does not have one public exported symbol")
        for relation_slot, present in targets[f"t{slot}"].items():
            if present:
                references.append(
                    SemanticReference(
                        artifact.descriptor.exported_symbols[0],
                        RELATION_BY_SLOT[relation_slot],
                    )
                )
    observation = SemanticObservation(
        fact_keys,
        (),
        hypothesis_effects,
        tuple(references),
        (),
    )
    return observation, {
        "fact_keys": list(fact_keys),
        "hypothesis_effects": dict(hypothesis_effects),
        "unresolved_targets": {
            key: dict(value) for key, value in targets.items()
        },
    }


def _rename_episode(
    episode: AuthzEpisode,
    *,
    rename_symbols: bool = False,
    rename_artifacts: bool = False,
    permute_candidate_labels: bool = False,
) -> AuthzEpisode:
    id_map = {
        item.descriptor.artifact_id: (
            f"z-{content_hash({'episode': episode.episode_id, 'artifact': item.descriptor.artifact_id})[:10]}"
            if rename_artifacts
            else item.descriptor.artifact_id
        )
        for item in episode.artifacts
    }
    symbol_map = {
        symbol: (
            f"sx_{content_hash({'episode': episode.episode_id, 'symbol': symbol})[:10]}"
            if rename_symbols
            else symbol
        )
        for item in episode.artifacts
        for symbol in item.descriptor.exported_symbols
    }

    def remap_source(source: str) -> str:
        placeholders = {}
        for index, (old, new) in enumerate(symbol_map.items()):
            placeholder = f"__SER_V12_SYMBOL_{index}__"
            source = source.replace(old, placeholder)
            placeholders[placeholder] = new
        for placeholder, new in placeholders.items():
            source = source.replace(placeholder, new)
        return source

    artifacts = tuple(
        ArtifactSpec(
            ArtifactDescriptor(
                id_map[item.descriptor.artifact_id],
                (
                    f"unit_{content_hash({'episode': episode.episode_id, 'path': item.descriptor.path})[:8]}.py"
                    if rename_artifacts
                    else item.descriptor.path
                ),
                tuple(symbol_map[symbol] for symbol in item.descriptor.exported_symbols),
                item.descriptor.line_count,
            ),
            remap_source(item.source),
            item.logical_role,
            item.expected_fact_keys,
            item.evaluator_usefulness,
        )
        for item in episode.artifacts
    )
    candidate_map = {
        item.hypothesis_id: f"label-{index + 17}"
        for index, item in enumerate(episode.candidates)
    }
    candidates = tuple(
        replace(item, hypothesis_id=candidate_map[item.hypothesis_id])
        if permute_candidate_labels
        else item
        for item in episode.candidates
    )
    truth = replace(
        episode.truth,
        correct_conclusion=candidate_map[episode.truth.correct_conclusion],
    ) if permute_candidate_labels else episode.truth
    return replace(
        episode,
        candidates=candidates,
        artifacts=artifacts,
        artifact_order=tuple(id_map[item] for item in episode.artifact_order),
        entry_artifact_id=id_map[episode.entry_artifact_id],
        truth=truth,
    )


def _variant_episode(episode: AuthzEpisode, variant: str) -> AuthzEpisode:
    if variant == "artifact_reordering":
        remaining = tuple(
            reversed(
                [item for item in episode.artifact_order if item != episode.entry_artifact_id]
            )
        )
        return replace(
            episode,
            artifact_order=(episode.entry_artifact_id, *remaining),
        )
    if variant == "symbol_renaming":
        return _rename_episode(episode, rename_symbols=True)
    if variant == "candidate_label_permutation":
        return _rename_episode(episode, permute_candidate_labels=True)
    if variant == "artifact_identifier_variation":
        return _rename_episode(episode, rename_artifacts=True)
    if variant == "combined_permutation":
        return replace(permuted_episode(episode), split="development")
    return episode


def _compact_summary(
    episode: AuthzEpisode, prior_slots: tuple[int, ...], current_slot: int
) -> dict:
    remaining = tuple(
        slot
        for slot in range(len(episode.artifact_order))
        if slot not in set(prior_slots) | {current_slot}
    )
    seen_facts = set()
    support = {f"c{index}": 0.0 for index in range(4)}
    unresolved = {
        f"t{slot}": {relation_slot: False for relation_slot in RELATION_SLOTS}
        for slot in remaining
    }
    for prior_slot in prior_slots:
        legal_at_step = tuple(
            slot
            for slot in range(len(episode.artifact_order))
            if slot not in set(prior_slots[: prior_slots.index(prior_slot) + 1])
        )
        value = oracle_content(episode, prior_slot, legal_at_step)
        for fact_slot, present in value["facts"].items():
            if present:
                seen_facts.add(fact_slot)
        for candidate_slot, effect in value["hypothesis_effects"].items():
            support[candidate_slot] += {"support": 1.0, "contradict": -1.0}.get(
                effect, 0.0
            )
        for target_slot, relations in value["unresolved_targets"].items():
            if target_slot in unresolved:
                for relation_slot, present in relations.items():
                    unresolved[target_slot][relation_slot] |= present
    return {
        "inspected_artifact_slots": list(prior_slots),
        "facts_seen": {slot: slot in seen_facts for slot in FACT_SLOTS},
        "candidate_support": support,
        "unresolved_targets": unresolved,
    }


def build_stress_cases(episodes: tuple[AuthzEpisode, ...]) -> list[dict]:
    cases = []
    for source_episode in episodes:
        for variant in VARIANTS:
            episode = _variant_episode(source_episode, variant)
            if variant == "longest_artifact":
                artifact = max(
                    episode.artifacts,
                    key=lambda item: (
                        item.descriptor.line_count,
                        item.descriptor.artifact_id,
                    ),
                )
                current_slot = episode.artifact_order.index(
                    artifact.descriptor.artifact_id
                )
                prior_slots = ()
            elif variant == "maximal_public_summary":
                prior_slots = (0, 1, 2)
                current_slot = 3
            else:
                current_slot = episode.artifact_order.index(episode.entry_artifact_id)
                prior_slots = ()
            legal_targets = tuple(
                slot
                for slot in range(len(episode.artifact_order))
                if slot not in set(prior_slots) | {current_slot}
            )
            current_artifact = episode.artifact(episode.artifact_order[current_slot])
            summary = _compact_summary(episode, prior_slots, current_slot)
            visible = {
                "semantic_interface": SEMANTIC_INTERFACE,
                "instruction_scope": "current_artifact_only",
                "current_artifact": {
                    "slot": current_slot,
                    "public_id": current_artifact.descriptor.artifact_id,
                    "path": current_artifact.descriptor.path,
                    "source": current_artifact.source,
                },
                "candidate_hypotheses": [
                    {
                        "slot": f"c{index}",
                        "public_label": candidate.hypothesis_id,
                        "description": candidate.description,
                        "relation_tags": list(candidate.relation_tags),
                    }
                    for index, candidate in enumerate(episode.candidates)
                ],
                "current_epistemic_summary": summary,
                "public_artifact_inventory": [
                    {
                        "slot": slot,
                        "public_id": episode.artifact(artifact_id).descriptor.artifact_id,
                        "path": episode.artifact(artifact_id).descriptor.path,
                        "exported_symbols": list(
                            episode.artifact(artifact_id).descriptor.exported_symbols
                        ),
                        "line_count": episode.artifact(artifact_id).descriptor.line_count,
                    }
                    for slot, artifact_id in enumerate(episode.artifact_order)
                ],
            }
            schema = response_schema(legal_targets)
            expected = oracle_content(episode, current_slot, legal_targets)
            case_id = (
                f"{source_episode.episode_id}--{variant}--"
                f"{content_hash({'visible': visible, 'schema': schema})[:10]}"
            )
            cases.append(
                {
                    "schema_version": 1,
                    "case_id": case_id,
                    "source_episode_id": source_episode.episode_id,
                    "variant": variant,
                    "model_visible_input": visible,
                    "response_schema": schema,
                    "runner_control": {
                        "current_artifact_slot": current_slot,
                        "prior_artifact_slots": list(prior_slots),
                        "legal_target_slots": list(legal_targets),
                        "schema_sha256": content_hash(schema),
                    },
                    "evaluator_only": {
                        "visibility": "evaluator_only",
                        "mechanism_family": source_episode.truth.mechanism_id,
                        "expected_content": expected,
                        "logical_roles_by_slot": {
                            f"t{slot}": episode.artifact(artifact_id).logical_role
                            for slot, artifact_id in enumerate(episode.artifact_order)
                        },
                        "usefulness_by_slot": {
                            f"t{slot}": episode.artifact(
                                artifact_id
                            ).evaluator_usefulness
                            for slot, artifact_id in enumerate(episode.artifact_order)
                        },
                    },
                    "episode": episode.to_dict(),
                }
            )
    if len(cases) != 64:
        raise ValueError("stress population must contain 64 unique cases")
    return cases


def stress_population_payload(episodes: tuple[AuthzEpisode, ...]) -> dict:
    cases = build_stress_cases(episodes)
    schedule = [
        {"case_id": case["case_id"], "repeat": repeat}
        for case in cases
        for repeat in (1, 2)
    ]
    payload = {
        "schema_version": 1,
        "experiment": "authzgym-semantic-contract-v1.2",
        "development_only": True,
        "source_episode_count": len(episodes),
        "variant_count_per_episode": len(VARIANTS),
        "repeats_per_case": 2,
        "cases": cases,
        "schedule": schedule,
    }
    payload["population_hash"] = content_hash(payload)
    return payload


def episode_from_case(case: Mapping[str, object]) -> AuthzEpisode:
    return AuthzEpisode.from_dict(dict(case["episode"]))
