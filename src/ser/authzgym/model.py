"""Data contracts for the static AuthzGym benchmark."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ser.core.types import ResourceDimension, ResourceSchema


AUTHZ_RESOURCE_SCHEMA = ResourceSchema(
    (
        ResourceDimension("artifact_inspections", "count"),
        ResourceDimension("semantic_calls", "count"),
        ResourceDimension("input_tokens_proxy", "deterministic_lexical_tokens"),
        ResourceDimension("output_tokens_proxy", "deterministic_lexical_tokens"),
        ResourceDimension("declared_latency_ms", "milliseconds"),
        ResourceDimension("monetary_cost_usd", "USD"),
    )
)


@dataclass(frozen=True)
class CandidateHypothesis:
    hypothesis_id: str
    description: str
    relation_tags: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "hypothesis_id": self.hypothesis_id,
            "description": self.description,
            "relation_tags": list(self.relation_tags),
        }

    @classmethod
    def from_dict(cls, value: dict) -> CandidateHypothesis:
        return cls(
            str(value["hypothesis_id"]),
            str(value["description"]),
            tuple(str(item) for item in value["relation_tags"]),
        )


CANDIDATE_HYPOTHESES = (
    CandidateHypothesis(
        "h1",
        "An ownership assumption differs between authorization layers or entry paths.",
        ("ownership_path", "alternate_entry"),
    ),
    CandidateHypothesis(
        "h2",
        "Direct and inherited membership are treated inconsistently.",
        ("membership_path", "membership_inheritance"),
    ),
    CandidateHypothesis(
        "h3",
        "A propagated or transformed role differs between layers.",
        ("role_path", "role_propagation"),
    ),
    CandidateHypothesis(
        "h4",
        "Token scope or request context is lost or checked inconsistently.",
        ("context_path", "token_scope"),
    ),
)


@dataclass(frozen=True)
class ArtifactDescriptor:
    artifact_id: str
    path: str
    exported_symbols: tuple[str, ...]
    line_count: int

    def to_dict(self) -> dict:
        return {
            "artifact_id": self.artifact_id,
            "path": self.path,
            "exported_symbols": list(self.exported_symbols),
            "line_count": self.line_count,
        }

    @classmethod
    def from_dict(cls, value: dict) -> ArtifactDescriptor:
        return cls(
            str(value["artifact_id"]),
            str(value["path"]),
            tuple(str(item) for item in value["exported_symbols"]),
            int(value["line_count"]),
        )


@dataclass(frozen=True)
class ArtifactSpec:
    descriptor: ArtifactDescriptor
    source: str
    logical_role: str
    expected_fact_keys: tuple[str, ...]
    evaluator_usefulness: float

    def public_descriptor(self) -> ArtifactDescriptor:
        return self.descriptor

    def to_dict(self) -> dict:
        return {
            "descriptor": self.descriptor.to_dict(),
            "source": self.source,
            "restricted_truth": {
                "visibility": "evaluator_only",
                "logical_role": self.logical_role,
                "expected_fact_keys": list(self.expected_fact_keys),
                "evaluator_usefulness": self.evaluator_usefulness,
            },
        }

    @classmethod
    def from_dict(cls, value: dict) -> ArtifactSpec:
        truth = value["restricted_truth"]
        return cls(
            ArtifactDescriptor.from_dict(value["descriptor"]),
            str(value["source"]),
            str(truth["logical_role"]),
            tuple(str(item) for item in truth["expected_fact_keys"]),
            float(truth["evaluator_usefulness"]),
        )


@dataclass(frozen=True)
class AuthorizationTruth:
    mechanism_id: str
    explanation: str
    relevant_artifact_roles: tuple[str, ...]
    relevant_functions: tuple[str, ...]
    evidence_relationships: tuple[str, ...]
    discriminating_artifact_role: str
    correct_conclusion: str
    decision_group: str
    control_type: str

    def to_dict(self) -> dict:
        return {
            "visibility": "evaluator_only",
            "mechanism_id": self.mechanism_id,
            "explanation": self.explanation,
            "relevant_artifact_roles": list(self.relevant_artifact_roles),
            "relevant_functions": list(self.relevant_functions),
            "evidence_relationships": list(self.evidence_relationships),
            "discriminating_artifact_role": self.discriminating_artifact_role,
            "correct_conclusion": self.correct_conclusion,
            "decision_group": self.decision_group,
            "control_type": self.control_type,
        }

    @classmethod
    def from_dict(cls, value: dict) -> AuthorizationTruth:
        return cls(
            str(value["mechanism_id"]),
            str(value["explanation"]),
            tuple(str(item) for item in value["relevant_artifact_roles"]),
            tuple(str(item) for item in value["relevant_functions"]),
            tuple(str(item) for item in value["evidence_relationships"]),
            str(value["discriminating_artifact_role"]),
            str(value["correct_conclusion"]),
            str(value["decision_group"]),
            str(value["control_type"]),
        )


@dataclass(frozen=True)
class AuthzEpisode:
    episode_id: str
    split: str
    task: str
    candidates: tuple[CandidateHypothesis, ...]
    artifacts: tuple[ArtifactSpec, ...]
    artifact_order: tuple[str, ...]
    entry_artifact_id: str
    max_inspections: int
    authoring_seed: int
    truth: AuthorizationTruth

    def artifact(self, artifact_id: str) -> ArtifactSpec:
        return next(
            item for item in self.artifacts if item.descriptor.artifact_id == artifact_id
        )

    def artifact_for_role(self, logical_role: str) -> ArtifactSpec:
        return next(item for item in self.artifacts if item.logical_role == logical_role)

    def public_view(self) -> dict:
        descriptors = {item.descriptor.artifact_id: item.descriptor for item in self.artifacts}
        return {
            "benchmark": "authzgym-static-v1",
            "episode_id": self.episode_id,
            "split": self.split,
            "task": self.task,
            "candidate_hypotheses": [item.to_dict() for item in self.candidates],
            "artifact_inventory": [descriptors[item].to_dict() for item in self.artifact_order],
            "entry_artifact_id": self.entry_artifact_id,
            "max_inspections": self.max_inspections,
            "resource_limits": {
                "artifact_inspections": float(self.max_inspections),
                "semantic_calls": float(self.max_inspections),
                "input_tokens_proxy": 6000.0,
                "output_tokens_proxy": 2000.0,
            },
        }

    def to_dict(self) -> dict:
        return {
            "public": self.public_view(),
            "artifacts": [item.to_dict() for item in self.artifacts],
            "runner_control": {
                "authoring_seed": self.authoring_seed,
            },
            "restricted_truth": self.truth.to_dict(),
        }

    @classmethod
    def from_dict(cls, value: dict) -> AuthzEpisode:
        public = value["public"]
        return cls(
            str(public["episode_id"]),
            str(public["split"]),
            str(public["task"]),
            tuple(
                CandidateHypothesis.from_dict(item)
                for item in public["candidate_hypotheses"]
            ),
            tuple(ArtifactSpec.from_dict(item) for item in value["artifacts"]),
            tuple(item["artifact_id"] for item in public["artifact_inventory"]),
            str(public["entry_artifact_id"]),
            int(public["max_inspections"]),
            int(value["runner_control"]["authoring_seed"]),
            AuthorizationTruth.from_dict(value["restricted_truth"]),
        )


@dataclass(frozen=True)
class SemanticReference:
    symbol: str
    relation_tag: str

    def to_dict(self) -> dict:
        return {"symbol": self.symbol, "relation_tag": self.relation_tag}


@dataclass(frozen=True)
class SemanticObservation:
    fact_keys: tuple[str, ...]
    facts: tuple[str, ...]
    hypothesis_effects: tuple[tuple[str, float], ...]
    unresolved_references: tuple[SemanticReference, ...]
    uncertainty_flags: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "fact_keys": list(self.fact_keys),
            "facts": list(self.facts),
            "hypothesis_effects": dict(self.hypothesis_effects),
            "unresolved_references": [item.to_dict() for item in self.unresolved_references],
            "uncertainty_flags": list(self.uncertainty_flags),
        }

    @classmethod
    def from_dict(cls, value: dict) -> SemanticObservation:
        return cls(
            tuple(str(item) for item in value["fact_keys"]),
            tuple(str(item) for item in value["facts"]),
            tuple(
                (str(key), float(score))
                for key, score in sorted(value["hypothesis_effects"].items())
            ),
            tuple(
                SemanticReference(str(item["symbol"]), str(item["relation_tag"]))
                for item in value["unresolved_references"]
            ),
            tuple(str(item) for item in value["uncertainty_flags"]),
        )


def public_symbol_index(episode: AuthzEpisode) -> dict[str, str]:
    return {
        symbol: artifact.descriptor.artifact_id
        for artifact in episode.artifacts
        for symbol in artifact.descriptor.exported_symbols
    }


def logical_role_index(episode: AuthzEpisode) -> dict[str, str]:
    return {
        artifact.descriptor.artifact_id: artifact.logical_role
        for artifact in episode.artifacts
    }


def line_count(source: str) -> int:
    return len(source.rstrip().splitlines())


def total_lines(artifacts: Iterable[ArtifactSpec]) -> int:
    return sum(item.descriptor.line_count for item in artifacts)
