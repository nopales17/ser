"""Narrow semantic-interpreter interface and deterministic mock conditions."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Iterable

from ser.core.types import canonical_json, content_hash

from .model import (
    ArtifactSpec,
    CandidateHypothesis,
    SemanticObservation,
    SemanticReference,
)


TOKEN_PATTERN = re.compile(r"\w+|[^\s\w]", re.UNICODE)


@dataclass(frozen=True)
class InterpreterCondition:
    condition_id: str
    kind: str
    drop_modulus: int
    declared_latency_ms_per_call: float
    monetary_cost_usd_per_call: float
    max_output_tokens: int

    def to_dict(self) -> dict:
        return {
            "condition_id": self.condition_id,
            "kind": self.kind,
            "drop_modulus": self.drop_modulus,
            "declared_latency_ms_per_call": self.declared_latency_ms_per_call,
            "monetary_cost_usd_per_call": self.monetary_cost_usd_per_call,
            "max_output_tokens": self.max_output_tokens,
        }


INTERPRETER_CONDITIONS = (
    InterpreterCondition(
        "deterministic_structured_v1",
        "mock_rule_interpreter",
        0,
        1.0,
        0.0,
        320,
    ),
    InterpreterCondition(
        "deterministic_degraded_v1",
        "mock_rule_interpreter_with_deterministic_omissions",
        4,
        1.0,
        0.0,
        320,
    ),
)


def conditions_from_config(value: dict) -> tuple[InterpreterCondition, ...]:
    if value.get("real_model_calls_authorized"):
        raise ValueError("mock-calibration runner cannot authorize real model calls")
    conditions = tuple(
        InterpreterCondition(
            str(item["condition_id"]),
            str(item["kind"]),
            int(item["drop_modulus"]),
            float(item["declared_latency_ms_per_call"]),
            float(item["monetary_cost_usd_per_call"]),
            int(item["max_output_tokens"]),
        )
        for item in value["conditions"]
    )
    if not conditions or any(not item.kind.startswith("mock_rule_interpreter") for item in conditions):
        raise ValueError("only explicit mock-rule conditions are supported here")
    return conditions


def token_proxy(text: str) -> int:
    """Deterministic lexical proxy; never represented as provider token usage."""

    return len(TOKEN_PATTERN.findall(text))


def _relation_tag(line: str) -> str:
    lower = line.lower()
    if "owner" in lower or "alternate" in lower:
        return "ownership_path"
    if "member" in lower or "group" in lower or "inherited" in lower:
        return "membership_path"
    if "role" in lower:
        return "role_path"
    if "token" in lower or "context" in lower or "flags" in lower:
        return "context_path"
    return "general_dependency"


def _rules(source: str) -> list[tuple[str, str, tuple[tuple[str, float], ...]]]:
    rules: list[tuple[str, str, tuple[tuple[str, float], ...]]] = []

    def add(key: str, fact: str, effects: tuple[tuple[str, float], ...]) -> None:
        rules.append((key, fact, effects))

    if 'channel == "alternate"' in source:
        add(
            "alternate-entry",
            "An alternate request path is handled separately from the standard path.",
            (("ownership_path", 0.8),),
        )
    if "direct_only=True" in source:
        add(
            "direct-only-membership",
            "Membership lookup is explicitly limited to direct records.",
            (("membership_path", 0.8),),
        )
    if "include_inherited=True" in source:
        add(
            "inherited-membership-included",
            "Membership lookup explicitly includes inherited records.",
            (("membership_path", -0.4),),
        )
    if 'fallback_role="reader"' in source or "role_map.get" in source:
        add(
            "role-fallback",
            "Role evaluation supplies or applies a fallback role.",
            (("role_path", 0.8),),
        )
    if "role_map.get" in source:
        add(
            "role-map-transform",
            "A role mapping transforms the source role before authorization.",
            (("role_path", 1.1),),
        )
    if "propagated_role = source_role" in source:
        add(
            "role-preserved",
            "The policy preserves the supplied role without transformation.",
            (("role_path", -0.4),),
        )
    if "token_scope=None" in source:
        add(
            "missing-token-scope",
            "An authorization call omits token scope.",
            (("context_path", 0.6),),
        )
    if "feature_context={}" in source:
        add(
            "missing-feature-context",
            "An authorization call replaces request context with an empty value.",
            (("context_path", 0.6),),
        )
    if "token_scope=token_scope" in source or "token_scope=request.token.scope" in source:
        add(
            "token-scope-forwarded",
            "Token scope is forwarded into authorization.",
            (("context_path", -0.3),),
        )
    if "feature_context=feature_context" in source or "feature_context=request.flags" in source:
        add(
            "feature-context-forwarded",
            "Request feature context is forwarded into authorization.",
            (("context_path", -0.3),),
        )
    if "apply_change(actor, item)" in source and "actor.owner_id == item.owner_id" not in source:
        add(
            "sensitive-without-owner-check",
            "A sensitive change is invoked without a local ownership comparison.",
            (("ownership_path", 1.8),),
        )
    if "actor.owner_id == item.owner_id" in source:
        add(
            "ownership-compared",
            "The service compares actor and resource ownership before the change.",
            (("ownership_path", -0.5),),
        )
    weak_patterns = {
        'audit_record = ("owner"': ("weak-ownership-audit", "ownership_path"),
        'audit_record = ("membership"': ("weak-membership-audit", "membership_path"),
        'audit_record = ("role"': ("weak-role-audit", "role_path"),
        'audit_record = ("context"': ("weak-context-audit", "context_path"),
    }
    for pattern, (key, relation_tag) in weak_patterns.items():
        if pattern in source:
            add(
                key,
                "An audit record mentions one authorization relationship without resolving it.",
                ((relation_tag, 0.2),),
            )
    return rules


def _keep(condition: InterpreterCondition, artifact_id: str, key: str) -> bool:
    if condition.drop_modulus <= 0:
        return True
    if condition.condition_id.endswith("_v1_1"):
        stable_key = key.rsplit("|", 1)[-1] if key.startswith("reference|") else key
        payload = f"{condition.condition_id}|semantic-role|{stable_key}"
    else:
        # Preserved for exact replay of the first invalid v1 calibration.  Its
        # artifact-ID dependence is the leakage defect corrected by v1.1.
        payload = f"{condition.condition_id}|{artifact_id}|{key}"
    digest = hashlib.sha256(payload.encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") % condition.drop_modulus != 0


def _parse_one(
    artifact: ArtifactSpec,
    condition: InterpreterCondition,
    symbol_index: dict[str, str],
    candidates: tuple[CandidateHypothesis, ...],
) -> SemanticObservation:
    selected = [
        item for item in _rules(artifact.source) if _keep(condition, artifact.descriptor.artifact_id, item[0])
    ]
    fact_keys = tuple(dict.fromkeys(item[0] for item in selected))
    facts = tuple(dict.fromkeys(item[1] for item in selected))
    effects: dict[str, float] = {}
    relation_to_hypotheses = {
        tag: candidate.hypothesis_id
        for candidate in candidates
        for tag in candidate.relation_tags
    }
    for _, _, updates in selected:
        for relation_tag, score in updates:
            hypothesis_id = relation_to_hypotheses.get(relation_tag)
            if hypothesis_id is not None:
                effects[hypothesis_id] = effects.get(hypothesis_id, 0.0) + score

    references = []
    for line in artifact.source.splitlines():
        for symbol, target_id in symbol_index.items():
            if target_id == artifact.descriptor.artifact_id:
                continue
            if re.search(rf"\b{re.escape(symbol)}\s*\(", line):
                key = f"reference|{symbol}|{_relation_tag(line)}"
                if _keep(condition, artifact.descriptor.artifact_id, key):
                    references.append(SemanticReference(symbol, _relation_tag(line)))
    references = list(
        dict.fromkeys((item.symbol, item.relation_tag) for item in references)
    )
    unresolved = tuple(SemanticReference(symbol, tag) for symbol, tag in references)
    uncertainty = []
    if not fact_keys:
        uncertainty.append("no_authorization_fact_extracted")
    if unresolved:
        uncertainty.append("cross_artifact_relationship_unresolved")
    return SemanticObservation(
        fact_keys,
        facts,
        tuple(sorted(effects.items())),
        unresolved,
        tuple(uncertainty),
    )


def _aggregate(observations: Iterable[SemanticObservation]) -> SemanticObservation:
    observations = tuple(observations)
    effects: dict[str, float] = {}
    for observation in observations:
        for hypothesis_id, score in observation.hypothesis_effects:
            effects[hypothesis_id] = effects.get(hypothesis_id, 0.0) + score
    return SemanticObservation(
        tuple(dict.fromkeys(key for item in observations for key in item.fact_keys)),
        tuple(dict.fromkeys(fact for item in observations for fact in item.facts)),
        tuple(sorted(effects.items())),
        tuple(
            SemanticReference(symbol, tag)
            for symbol, tag in dict.fromkeys(
                (reference.symbol, reference.relation_tag)
                for item in observations
                for reference in item.unresolved_references
            )
        ),
        tuple(
            dict.fromkeys(flag for item in observations for flag in item.uncertainty_flags)
        ),
    )


def interpret_artifacts(
    artifacts: tuple[ArtifactSpec, ...],
    candidates: tuple[CandidateHypothesis, ...],
    current_summary: dict,
    public_inventory: tuple[dict, ...],
    prompt_text: str,
    prompt_version: str,
    condition: InterpreterCondition,
    *,
    consolidated: bool = False,
) -> dict:
    """Interpret only the explicitly purchased artifacts and return a traceable call."""

    symbol_index = {
        symbol: item["artifact_id"]
        for item in public_inventory
        for symbol in item["exported_symbols"]
    }
    visible_input = {
        "prompt_version": prompt_version,
        "prompt": prompt_text,
        "artifacts": [
            {
                "artifact_id": item.descriptor.artifact_id,
                "path": item.descriptor.path,
                "source": item.source,
            }
            for item in artifacts
        ],
        "candidate_hypotheses": [item.to_dict() for item in candidates],
        "current_epistemic_summary": current_summary,
        "public_artifact_inventory": list(public_inventory),
    }
    parsed_parts = tuple(
        _parse_one(item, condition, symbol_index, candidates) for item in artifacts
    )
    parsed = _aggregate(parsed_parts)
    raw_output = parsed.to_dict()
    input_text = canonical_json(visible_input)
    output_text = canonical_json(raw_output)
    input_tokens = token_proxy(input_text)
    output_tokens = token_proxy(output_text)
    effective_output_ceiling = condition.max_output_tokens * (
        len(artifacts) if consolidated else 1
    )
    if output_tokens > effective_output_ceiling:
        raise ValueError("mock semantic output exceeds frozen output-token ceiling")
    return {
        "call_id": content_hash(
            {
                "condition": condition.condition_id,
                "visible_input": visible_input,
                "consolidated": consolidated,
            }
        )[:20],
        "interface": "interpret_artifact_v1" if not consolidated else "interpret_batch_v1",
        "model_identifier": condition.condition_id,
        "model_configuration": condition.to_dict(),
        "visible_input": visible_input,
        "raw_output": raw_output,
        "parsed_semantic_observation": raw_output,
        "resource_use": {
            "artifact_inspections": float(len(artifacts)),
            "semantic_calls": 1.0,
            "input_tokens_proxy": float(input_tokens),
            "output_tokens_proxy": float(output_tokens),
            "declared_latency_ms": condition.declared_latency_ms_per_call,
            "monetary_cost_usd": condition.monetary_cost_usd_per_call,
        },
        "effective_output_token_ceiling": effective_output_ceiling,
        "accounting_note": (
            "Tokens are a deterministic lexical proxy, not provider-reported usage; "
            "latency and monetary cost are declared mock-condition values."
        ),
    }
