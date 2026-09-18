"""Sealed component input and the preregistration section-2.4 input allowlist.

Handoff step 2. ``SealedComponentInput`` exposes exactly the seven allowlisted
items of preregistration section 2.4 and nothing else; any other attribute
access raises :class:`ForbiddenComponentInput`. It is constructed from the
public case and the response only, never from a restricted case, an annotation
record, a transformation map, or a file handle, and it holds no such reference.

The static checker walks a candidate module's AST and transitive import closure
and rejects the forbidden references of preregistration section 2.5.
"""

from __future__ import annotations

import ast
from pathlib import Path
from types import MappingProxyType
from typing import Iterable, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SOURCE_ROOT = PROJECT_ROOT / "src"

ALLOWLISTED_ITEMS = (
    "facts",
    "candidate_effects",
    "unresolved_targets",
    "candidate_hypotheses",
    "contract_constants",
    "legal_target_slots",
    "current_artifact_slot",
)

# Preregistration section 2.5 attribute surfaces that may never be reached.
FORBIDDEN_ATTRIBUTES = frozenset(
    {
        "public_id",
        "path",
        "exported_symbols",
        "line_count",
        "public_label",
        "artifact_id",
        "source_family",
        "usefulness_by_variant_target_slot",
        "canonical_source_ordinal_by_variant_slot",
        "canonical_ordinal_by_variant_public_id",
        "public_artifact_inventory",
        "model_visible_input",
        "runner_control",
        "restricted_population",
        "restricted_case",
        "logical_role_index",
    }
)

# Preregistration section 2.5 identifiers, retired labels, and hidden roles.
FORBIDDEN_NAMES = frozenset(
    {
        "LOGICAL_ROLES",
        "DISCRIMINATING_ROLE",
        "logical_role_index",
        "AuthorizationTruth",
        "ArtifactSpec",
        "canonical_source_ordinal_by_variant_slot",
        "canonical_ordinal_by_variant_public_id",
        "usefulness_by_variant_target_slot",
        "public_id_by_canonical_artifact_id",
        "source_family",
        "line_count",
        "f17",
        "f18",
        "f19",
        "f20",
        "f21",
        "f22",
        "f23",
        "f24",
        "h1",
        "h2",
        "h3",
        "h4",
    }
)

# Hidden logical-role tokens are forbidden as *authoring-role* names, not as
# arbitrary substrings, so only exact identifiers are rejected above.
FORBIDDEN_MODULE_PREFIXES = (
    "ser.authzgym.generation",
    "ser.authzgym.v1_3_annotation_builder",
    "ser.authzgym.v1_3_population",
    "ser.authzgym.runner",
    "ser.authzgym.real_runner",
    "ser.authzgym.realmodel",
    "ser.authzgym.semantic_contract",
    "ser.authzgym.interpreters",
    "ser.evaluation.authz_v1_3",
    "ser.evaluation.authz_v1_3_1_harness",
)


class ForbiddenComponentInput(AttributeError):
    """A component reached an item outside the section-2.4 allowlist."""


class ComponentAllowlistError(RuntimeError):
    """A candidate module referenced a forbidden input or module."""


def _freeze(value: object) -> object:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise ComponentAllowlistError(
        f"sealed input may not hold {type(value).__name__} values"
    )


class SealedComponentInput:
    """Exactly the seven allowlisted items of preregistration section 2.4."""

    __slots__ = (
        "_facts",
        "_candidate_effects",
        "_unresolved_targets",
        "_candidate_hypotheses",
        "_contract_constants",
        "_legal_target_slots",
        "_current_artifact_slot",
    )

    def __init__(
        self,
        *,
        facts: Mapping[str, bool],
        candidate_effects: Mapping[str, str],
        unresolved_targets: Mapping[int, Sequence[bool]],
        candidate_hypotheses: Iterable[Sequence[str]],
        contract_constants: Mapping[str, object],
        legal_target_slots: Iterable[int],
        current_artifact_slot: int,
    ) -> None:
        object.__setattr__(self, "_facts", _freeze(facts))
        object.__setattr__(self, "_candidate_effects", _freeze(candidate_effects))
        object.__setattr__(
            self,
            "_unresolved_targets",
            MappingProxyType(
                {
                    int(slot): tuple(bool(item) for item in vector)
                    for slot, vector in unresolved_targets.items()
                }
            ),
        )
        object.__setattr__(
            self,
            "_candidate_hypotheses",
            tuple((str(a), str(b), str(c)) for a, b, c in candidate_hypotheses),
        )
        object.__setattr__(self, "_contract_constants", _freeze(contract_constants))
        object.__setattr__(
            self,
            "_legal_target_slots",
            tuple(int(slot) for slot in legal_target_slots),
        )
        object.__setattr__(
            self, "_current_artifact_slot", int(current_artifact_slot)
        )

    def __setattr__(self, name: str, value: object) -> None:
        raise ForbiddenComponentInput("sealed component input is immutable")

    def __getattr__(self, name: str) -> object:
        raise ForbiddenComponentInput(
            f"{name!r} is not one of the seven allowlisted component inputs"
        )

    @property
    def facts(self) -> Mapping[str, bool]:
        return self._facts

    @property
    def candidate_effects(self) -> Mapping[str, str]:
        return self._candidate_effects

    @property
    def unresolved_targets(self) -> Mapping[int, tuple[bool, ...]]:
        return self._unresolved_targets

    @property
    def candidate_hypotheses(self) -> tuple[tuple[str, str, str], ...]:
        return self._candidate_hypotheses

    @property
    def contract_constants(self) -> Mapping[str, object]:
        return self._contract_constants

    @property
    def legal_target_slots(self) -> tuple[int, ...]:
        return self._legal_target_slots

    @property
    def current_artifact_slot(self) -> int:
        return self._current_artifact_slot

    # Section 2.4 item 7: the cardinality of the legal-target set.
    @property
    def legal_target_count(self) -> int:
        return len(self._legal_target_slots)

    def category_vector(self, slot: int) -> tuple[bool, ...]:
        """Derived from the allowlisted relation matrix; addressing only."""

        return self._unresolved_targets[int(slot)]

    def __repr__(self) -> str:  # pragma: no cover - representation only
        return (
            f"SealedComponentInput(items={len(ALLOWLISTED_ITEMS)}, "
            f"legal_targets={len(self._legal_target_slots)})"
        )


def build_sealed_input(
    case: Mapping[str, object],
    response: Mapping[str, object],
    contract: Mapping[str, object],
) -> SealedComponentInput:
    """Build the sealed input from the public case and the response only."""

    from ser.authzgym.v1_3_contract import parse_response

    legal = tuple(int(item) for item in case["runner_control"]["legal_target_slots"])
    parsed = parse_response(response, contract, legal)
    return SealedComponentInput(
        facts={slot: bool(value) for slot, value in parsed["facts"].items()},
        candidate_effects={
            slot: str(value) for slot, value in parsed["candidate_effects"].items()
        },
        unresolved_targets={
            slot: tuple(
                bool(parsed["unresolved_targets"][f"t{slot}"][f"r{index}"])
                for index in range(5)
            )
            for slot in legal
        },
        candidate_hypotheses=tuple(
            (str(item["slot"]), str(item["effect_family"]), str(item["description"]))
            for item in case["model_visible_input"]["candidate_hypotheses"]
        ),
        contract_constants={
            "fact_slots": contract["fact_slots"],
            "effect_support_cues": contract["effect_support_cues"],
            "effect_counter_cues": contract["effect_counter_cues"],
            "effect_values": contract["effect_values"],
            "relation_slots": contract["relation_slots"],
            "relation_precedence": contract["relation_precedence"],
            "candidate_slots": contract["candidate_slots"],
        },
        legal_target_slots=legal,
        current_artifact_slot=int(case["runner_control"]["current_artifact_slot"]),
    )


def module_path(module_name: str, *, source_root: Path = SOURCE_ROOT) -> Path | None:
    relative = Path(*module_name.split("."))
    for candidate in (
        source_root / relative.with_suffix(".py"),
        source_root / relative / "__init__.py",
    ):
        if candidate.is_file():
            return candidate
    return None


def _imported_modules(tree: ast.AST) -> set[str]:
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                continue
            if node.module:
                modules.add(node.module)
    return modules


def _scan_module(
    path: Path, tree: ast.AST, *, full: bool = True
) -> list[str]:
    """Reference scan. ``full`` scans names/attributes; otherwise only imports.

    The candidate's own module is scanned in full. Imported library modules are
    checked for forbidden *module reachability* only: a library that merely
    defines a forbidden name (for example the public data-contract module
    defining ``AuthorizationTruth`` for the unrelated legacy fixture generator)
    does not by itself mean the candidate reaches it.
    """

    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if _is_forbidden_module(alias.name):
                    violations.append(
                        f"{path.name}:{node.lineno}: forbidden import {alias.name}"
                    )
                elif full and alias.name.split(".")[-1] in FORBIDDEN_NAMES:
                    violations.append(
                        f"{path.name}:{node.lineno}: forbidden import {alias.name}"
                    )
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if _is_forbidden_module(module):
                violations.append(
                    f"{path.name}:{node.lineno}: forbidden import {module}"
                )
            if full:
                for alias in node.names:
                    if alias.name in FORBIDDEN_NAMES:
                        violations.append(
                            f"{path.name}:{node.lineno}: forbidden import {alias.name}"
                        )
        elif not full:
            continue
        elif isinstance(node, ast.Attribute) and node.attr in FORBIDDEN_ATTRIBUTES:
            violations.append(f"{path.name}:{node.lineno}: attribute .{node.attr}")
        elif isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            violations.append(f"{path.name}:{node.lineno}: name {node.id}")
        elif (
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
        ):
            if "confirmation" in node.value.lower():
                violations.append(f"{path.name}:{node.lineno}: confirmation literal")
            elif node.value in FORBIDDEN_NAMES:
                violations.append(
                    f"{path.name}:{node.lineno}: forbidden literal {node.value!r}"
                )
    return violations


def _is_forbidden_module(module: str) -> bool:
    return any(
        module == prefix or module.startswith(prefix + ".")
        for prefix in FORBIDDEN_MODULE_PREFIXES
    )


def check_component_module(
    path: Path | str,
    *,
    source_root: Path = SOURCE_ROOT,
    include_closure: bool = True,
) -> dict:
    """Static allowlist check over a module and its transitive import closure."""

    entry = Path(path)
    if not entry.is_file():
        raise ComponentAllowlistError(f"component module not found: {entry}")
    violations: list[str] = []
    visited: set[Path] = set()
    queue: list[Path] = [entry]
    while queue:
        current = queue.pop()
        if current in visited:
            continue
        visited.add(current)
        tree = ast.parse(current.read_text(encoding="utf-8"), filename=str(current))
        violations.extend(_scan_module(current, tree, full=current == entry))
        if not include_closure:
            continue
        for module in sorted(_imported_modules(tree)):
            if _is_forbidden_module(module):
                violations.append(f"{current.name}: forbidden import {module}")
                continue
            resolved = module_path(module, source_root=source_root)
            if resolved is not None and resolved not in visited:
                queue.append(resolved)
    if violations:
        raise ComponentAllowlistError("; ".join(sorted(set(violations))))

    def _relative(item: Path) -> str:
        try:
            return str(item.resolve().relative_to(PROJECT_ROOT))
        except ValueError:
            return item.name

    return {
        "module": _relative(entry),
        "checked_modules": sorted(_relative(item) for item in visited),
        "violations": [],
        "allowlisted_items": list(ALLOWLISTED_ITEMS),
    }
