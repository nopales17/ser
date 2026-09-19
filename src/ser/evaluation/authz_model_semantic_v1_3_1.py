"""Audited reader, access ledger and harness wiring for `model-semantic-v1.3.1-N1`.

Normative sources: `experiments/authzgym_model_semantic_v1_3_1/PREREGISTRATION.md`
sections 5 (hashing convention, vocabulary, restated digests), 6 (access ledger
at file-open granularity) and 14.2, and
`experiments/authzgym_model_semantic_v1_3_1/IMPLEMENTATION_HANDOFF.md` sections
0.2 (never-open set, fail closed), 0.3 and 3.

This module is the only component of the condition that opens a protected or
confirmation path. Every open emits exactly one section-6.2 record. The
never-open predicate of section 0.2 is applied inside the reader and raises
before any byte is read.
"""

from __future__ import annotations

import ast
import hashlib
import json
import math
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[3]
V13_DIR = ROOT / "experiments" / "authzgym_semantic_contract_v1_3"
REPAIR_DIR = ROOT / "experiments" / "authzgym_estimator_repair_v1_3_1"
CONFIRMATION_DIR = ROOT / "experiments" / "authzgym_confirmation_v1_3_1"
CONDITION_DIR = ROOT / "experiments" / "authzgym_model_semantic_v1_3_1"

LEDGER_PATH = CONDITION_DIR / "ACCESS_LEDGER.jsonl"

# The audited reader itself is the one module allowed to call `open(`/`read_bytes`
# on a protected path; the section-6.1 static check exempts it explicitly.
AUDITED_READER_PATH = Path(__file__).resolve()

# Handoff section 0.2: files under the confirmation directory that may be read,
# once, at step 1, for hash restatement only.
CONFIRMATION_READABLE_EXCEPTIONS = (
    "CONFIRMATION_V1_3_1_ORACLE_VALIDATION.json",
    "CONFIRMATION_V1_3_1_SEAL.json",
    "REPORT.md",
)

# Handoff section 0.2 lists these explicitly; the name predicate below covers
# them plus every remaining `CONFIRMATION_`-prefixed file, the confirmation
# annotation copies, and the PUBLIC_BUNDLE/RESTRICTED_BUNDLE copies.
NEVER_OPEN_V13_EXPLICIT = (
    "CONFIRMATION_PUBLIC_POPULATION.json",
    "CONFIRMATION_RESTRICTED_POPULATION.json",
    "CONFIRMATION_SCHEDULE.json",
    "CONFIRMATION_TRANSFORMATION_MAPS.json",
)
NEVER_OPEN_BLOCKS = {"ORACLE_VALIDATION.json": ("confirmation",)}

ACCESS_CLASSES = ("protected", "confirmation", "public", "condition")
ACCESS_OPERATIONS = (
    "read",
    "write",
    "hash",
    "stat",
    "generate",
    "validate",
    "evaluate",
    "seal",
)
REQUIRED_RECORD_FIELDS = (
    "schema_version",
    "timestamp_utc",
    "actor",
    "process_id",
    "stage",
    "path",
    "class",
    "operation",
    "bytes",
    "file_sha256",
    "tool_path",
    "tool_sha256",
    "authorization",
    "detail",
)

# Section 9 permits exactly two network operations in the model-verification
# stage; nothing in this module performs either of them.
PERMITTED_MODEL_STAGE_NETWORK_OPERATIONS = (
    "supervised_hop_establish",
    "GET /models catalog probe",
)


class SpentPopulationAccess(RuntimeError):
    """A never-open (section 0.2) path or block was reached. Fail closed."""


class AccessLedgerError(RuntimeError):
    """An access-ledger record or ledger file violates section 6.2 or 6.3."""


class ReadBypassError(RuntimeError):
    """A condition module reads a protected path without the audited reader."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def file_sha256(path: Path | str) -> str:
    """Raw-byte SHA-256, the authoritative frozen-artifact convention (5.1)."""

    return sha256_bytes(Path(path).read_bytes())


def relative_path(path: Path | str) -> str:
    candidate = Path(path)
    try:
        return str(candidate.resolve().relative_to(ROOT))
    except ValueError:
        return str(candidate)


def is_under(path: Path | str, directory: Path) -> bool:
    try:
        Path(path).resolve().relative_to(directory.resolve())
        return True
    except ValueError:
        return False


def is_never_open_path(path: Path | str) -> bool:
    """The handoff section 0.2 never-open predicate, applied by path only."""

    candidate = Path(path)
    if is_under(candidate, V13_DIR):
        tail = candidate.resolve().relative_to(V13_DIR.resolve()).parts
        return any(part.lower().startswith("confirmation") for part in tail)
    if is_under(candidate, CONFIRMATION_DIR):
        tail = candidate.resolve().relative_to(CONFIRMATION_DIR.resolve()).parts
        return not (len(tail) == 1 and tail[0] in CONFIRMATION_READABLE_EXCEPTIONS)
    return False


def access_class(path: Path | str) -> str:
    candidate = Path(path)
    if is_under(candidate, CONDITION_DIR):
        return "condition"
    if is_never_open_path(candidate):
        return "confirmation"
    if is_under(candidate, CONFIRMATION_DIR):
        return "confirmation"
    if is_under(candidate, V13_DIR) or is_under(candidate, REPAIR_DIR):
        name = candidate.name
        if name in (
            "PUBLIC_CONTRACT.json",
            "DEVELOPMENT_PUBLIC_POPULATION.json",
            "DEVELOPMENT_SCHEDULE.json",
            "DEVELOPMENT_SOURCE_MANIFEST.json",
            "PUBLIC_BUNDLE_MANIFEST.json",
        ) or "prompts" in candidate.parts or "schemas" in candidate.parts:
            return "public"
        return "protected"
    return "protected"


def never_open_v13_names() -> tuple[str, ...]:
    """Every section-0.2 name inside the v1.3 instrument directory."""

    names: list[str] = []
    for path in sorted(V13_DIR.rglob("*")):
        rel = path.relative_to(V13_DIR)
        if is_never_open_path(path):
            names.append(str(rel))
    return tuple(names)


class AuditedReader:
    """One record per open, appended and never rewritten (section 6.2)."""

    def __init__(
        self,
        *,
        actor: str,
        stage: str,
        tool_path: Path | str,
        authorization: str,
        ledger_path: Path | str = LEDGER_PATH,
    ) -> None:
        self.actor = str(actor)
        self.stage = str(stage)
        self.tool_path = relative_path(tool_path)
        self.tool_sha256 = file_sha256(tool_path)
        self.authorization = str(authorization)
        self.ledger_path = Path(ledger_path)
        self.opened_paths: list[str] = []
        self.stat_only_paths: list[str] = []
        self.never_open_opens: list[str] = []

    # -- ledger plumbing -------------------------------------------------
    def _append(self, record: Mapping[str, object]) -> dict:
        missing = [name for name in REQUIRED_RECORD_FIELDS if name not in record]
        if missing:
            raise AccessLedgerError(
                "access record is missing required fields: " + ", ".join(missing)
            )
        payload = dict(record)
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.ledger_path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")
        return payload

    def _record(
        self,
        path: Path | str,
        *,
        operation: str,
        size: int = 0,
        digest: str = "",
        detail: str = "",
    ) -> dict:
        candidate = Path(path)
        classification = access_class(candidate)
        if operation != "stat" and is_never_open_path(candidate):
            self.never_open_opens.append(relative_path(candidate))
        if operation != "stat":
            self.opened_paths.append(relative_path(candidate))
        return self._append(
            {
                "schema_version": 1,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "actor": self.actor,
                "process_id": os.getpid(),
                "stage": self.stage,
                "path": relative_path(candidate),
                "class": classification,
                "operation": operation,
                "bytes": int(size),
                "file_sha256": digest,
                "tool_path": self.tool_path,
                "tool_sha256": self.tool_sha256,
                "authorization": self.authorization,
                "detail": detail,
            }
        )

    def _guard(self, path: Path | str) -> Path:
        candidate = Path(path)
        if is_never_open_path(candidate):
            raise SpentPopulationAccess(
                f"section-0.2 never-open path reached: {relative_path(candidate)}"
            )
        return candidate

    # -- stat only (no open) --------------------------------------------
    def stat_only(self, path: Path | str) -> dict:
        candidate = Path(path)
        info = candidate.stat() if candidate.exists() else None
        present = info is not None
        value = {
            "path": relative_path(candidate),
            "present": present,
            "bytes": int(info.st_size) if info is not None else None,
            "mtime_ns": int(info.st_mtime_ns) if info is not None else None,
            "never_open": is_never_open_path(candidate),
        }
        self.stat_only_paths.append(value["path"])
        self._record(
            candidate,
            operation="stat",
            size=int(info.st_size) if info is not None else 0,
            digest="",
            detail=(
                "stat only; never opened"
                if value["never_open"]
                else "stat only; existence and metadata check"
            ),
        )
        return value

    # -- audited opens ---------------------------------------------------
    def read_bytes(
        self,
        path: Path | str,
        *,
        operation: str = "read",
        detail: str = "",
    ) -> bytes:
        candidate = self._guard(path)
        value = candidate.read_bytes()
        self._record(
            candidate,
            operation=operation,
            size=len(value),
            digest=sha256_bytes(value),
            detail=detail,
        )
        return value

    def read_text(
        self,
        path: Path | str,
        *,
        operation: str = "read",
        detail: str = "",
        encoding: str = "utf-8",
    ) -> str:
        return self.read_bytes(
            path, operation=operation, detail=detail
        ).decode(encoding)

    def hash_file(self, path: Path | str, *, detail: str = "") -> dict:
        candidate = self._guard(path)
        value = candidate.read_bytes()
        digest = sha256_bytes(value)
        self._record(
            candidate,
            operation="hash",
            size=len(value),
            digest=digest,
            detail=detail or "file_sha256 (section 5.1 raw-byte convention)",
        )
        return {"path": relative_path(candidate), "bytes": len(value), "file_sha256": digest}

    def read_json(
        self,
        path: Path | str,
        *,
        block: str | None = None,
        detail: str = "",
    ) -> object:
        candidate = self._guard(path)
        if block is not None and block in NEVER_OPEN_BLOCKS.get(candidate.name, ()):
            raise SpentPopulationAccess(
                f"section-0.2 never-open block {block!r} in {relative_path(candidate)}"
            )
        text = self.read_text(candidate, detail=detail or "read_json") 
        value = json.loads(text)
        if block is not None:
            if not isinstance(value, Mapping) or block not in value:
                raise AccessLedgerError(f"requested block {block!r} is absent")
        return value

    def read_jsonl(
        self, path: Path | str, *, detail: str = ""
    ) -> list[dict]:
        text = self.read_text(path, detail=detail or "read_jsonl")
        return [json.loads(line) for line in text.splitlines() if line.strip()]


def validate_access_ledger(path: Path | str) -> dict:
    """Schema completeness and section-6.3 blocking rules over one ledger."""

    ledger_path = Path(path)
    rows: list[dict] = []
    if ledger_path.exists():
        rows = [
            json.loads(line)
            for line in ledger_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    malformed = [
        index
        for index, row in enumerate(rows)
        if any(name not in row for name in REQUIRED_RECORD_FIELDS)
    ]
    missing_tool_hash = [
        index for index, row in enumerate(rows) if not str(row.get("tool_sha256", ""))
    ]
    # IMPLEMENTATION_CLARIFICATION.md section 4.2 / handoff step 6B: a
    # `retrospective_disclosure` record describes an operation that happened
    # before this condition's audited reader existed. It is a disclosed
    # deviation, not an open performed under the reader, and it may carry a
    # never-open path. Every such record must say so explicitly.
    disclosure_rows = [row for row in rows if row.get("retrospective_disclosure") is True]
    unexplained_disclosures = [
        row
        for row in disclosure_rows
        if row.get("occurred_before_audited_reader") is not True
    ]
    never_open_rows = [
        row
        for row in rows
        if row.get("retrospective_disclosure") is not True
        and row.get("operation") != "stat"
        and "path" in row
        and is_never_open_path(ROOT / str(row["path"]))
    ]
    unexplained_stat_rows = [
        row
        for row in rows
        if row.get("operation") == "stat" and not str(row.get("detail", "")).startswith("stat only")
    ]
    return {
        "schema_version": 1,
        "ledger_path": relative_path(ledger_path),
        "ledger_file_sha256": file_sha256(ledger_path) if ledger_path.exists() else "",
        "record_count": len(rows),
        "malformed_record_indices": malformed,
        "missing_tool_sha256_indices": missing_tool_hash,
        "retrospective_disclosure_count": len(disclosure_rows),
        "retrospective_disclosure_paths": sorted(
            {str(row.get("path", "")) for row in disclosure_rows}
        ),
        "unexplained_retrospective_disclosure_count": len(unexplained_disclosures),
        "never_open_open_count": len(never_open_rows),
        "never_open_open_paths": sorted({str(row["path"]) for row in never_open_rows}),
        "stat_records_without_stat_only_detail": len(unexplained_stat_rows),
        "stages": sorted({str(row.get("stage")) for row in rows}),
        "schema_complete": not malformed
        and not missing_tool_hash
        and not unexplained_disclosures,
        "passes": not malformed
        and not missing_tool_hash
        and not never_open_rows
        and not unexplained_disclosures,
    }


def check_static_read_bypass(
    paths: Iterable[Path | str],
    *,
    exempt: Sequence[Path | str] = (AUDITED_READER_PATH,),
) -> dict:
    """Section 6.1 static check over the condition's own modules and tools.

    Rejects a bare ``open(`` used for reading, ``Path.read_text``,
    ``Path.read_bytes``, ``json.load(`` on a path, and dynamic loaders, in any
    file that is not the audited reader itself.
    """

    exempt_paths = {Path(item).resolve() for item in exempt}
    violations: list[str] = []
    checked: list[str] = []
    for item in paths:
        candidate = Path(item)
        if not candidate.is_file():
            raise ReadBypassError(f"static check target is not a file: {candidate}")
        if candidate.resolve() in exempt_paths:
            continue
        checked.append(relative_path(candidate))
        tree = ast.parse(candidate.read_text(encoding="utf-8"), filename=str(candidate))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = _call_name(node.func)
                if name.endswith(".read_text") or name.endswith(".read_bytes"):
                    receiver = _receiver_name(node.func)
                    if receiver == "reader" or receiver.endswith("_reader"):
                        # ``AuditedReader.read_text``/``read_bytes`` are the
                        # instrumented path; the static check rejects every
                        # other reader-like open.
                        continue
                    violations.append(
                        f"{relative_path(candidate)}:{node.lineno}: {name}"
                    )
                elif name == "json.load":
                    violations.append(
                        f"{relative_path(candidate)}:{node.lineno}: json.load"
                    )
                elif name == "open" and not _is_write_mode(node):
                    violations.append(
                        f"{relative_path(candidate)}:{node.lineno}: bare open("
                    )
                elif name in (
                    "runpy.run_path",
                    "importlib.util.spec_from_file_location",
                ):
                    violations.append(f"{relative_path(candidate)}:{node.lineno}: {name}")
    return {
        "checked_paths": sorted(checked),
        "exempt_paths": sorted(relative_path(item) for item in exempt_paths),
        "violations": sorted(set(violations)),
        "passes": not violations,
    }


def assert_no_read_bypass(
    paths: Iterable[Path | str],
    *,
    exempt: Sequence[Path | str] = (AUDITED_READER_PATH,),
) -> dict:
    result = check_static_read_bypass(paths, exempt=exempt)
    if not result["passes"]:
        raise ReadBypassError("; ".join(result["violations"]))
    return result


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    if isinstance(node, ast.Call):
        return _call_name(node.func)
    return ""


def _receiver_name(node: ast.AST) -> str:
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        return node.value.id
    return ""


def _is_write_mode(node: ast.Call) -> bool:
    mode = None
    if len(node.args) > 1 and isinstance(node.args[1], ast.Constant):
        mode = node.args[1].value
    for keyword in node.keywords:
        if keyword.arg == "mode" and isinstance(keyword.value, ast.Constant):
            mode = keyword.value.value
    return isinstance(mode, str) and any(flag in mode for flag in ("w", "a", "x"))


def tool_file_sha256(path: Path | str) -> str:
    return file_sha256(path)


# ---------------------------------------------------------------------------
# Step 6A -- dormant scoring, choice-set, gate and error-propagation machinery
#
# Authority: ADR-0023 `Authorized scope` ("scorer wiring, error-propagation
# classification and tests"); PREREGISTRATION.md sections 4.2--4.4, 8.2--8.6,
# 10, 12, 12.1, 13.8, 15 and 18; IMPLEMENTATION_HANDOFF.md step 6A and steps
# 8--10 as relabelled by IMPLEMENTATION_CLARIFICATION.md section 2.
#
# Dormant, normatively: every function below is pure. None opens a path, none
# performs a network operation, and none may be executed against a model
# response before a separate Step-7 authorization exists. The unit tests
# exercise these functions against synthetic fixtures only (clarification
# section 2.1).
# ---------------------------------------------------------------------------

SCHEMA_VERSION = 1
ROUND_DIGITS = 12
VALUE_TOLERANCE = 1e-12

# PREREGISTRATION.md section 4.4: >= 7 of 8 canonical sources, per repeat.
PRIMARY_SOURCE_THRESHOLD = 7
PRIMARY_SOURCE_DENOMINATOR = 8

# PREREGISTRATION.md section 8.3, frozen Astra-supplied screens.
PAIRED_TOP1_DECLINE_MAX = 0.125
PAIRED_TOP2_DECLINE_MAX = 0.125
PAIRED_MEAN_POSITIVE_EXCESS_MAX = 0.05
OWN_SELECTION_DEVELOPMENT_COMPARISONS = 80
OWN_SELECTION_CONFIRMATION_COMPARISONS = 40
CONTINUITY_PRECISION_MIN = 0.60
CONTINUITY_RECALL_MIN = 0.50

# PREREGISTRATION.md section 8.2, absolute model-conditioned B-1 (S-11).
ABSOLUTE_TOP1_MIN = 0.60
ABSOLUTE_TOP2_MIN = 0.80
ABSOLUTE_REGRET_MAX = 0.35

# PREREGISTRATION.md section 12/12.1 guarantee 1: the gated development item
# set is exactly {1..10} union {12..21}, written as an explicit literal set so
# no later edit can widen it by accident. Item 11 (S-7) is not a member.
GATED_DEVELOPMENT_ITEMS: frozenset[int] = frozenset((*range(1, 11), *range(12, 22)))

# PREREGISTRATION.md section 13.8: items 1--13 with item 6 (S-7) diagnostic-only.
GATED_CONFIRMATION_ITEMS: frozenset[int] = frozenset(
    item for item in range(1, 14) if item != 6
)

DIAGNOSTIC_ONLY_DEVELOPMENT_ITEM = 11
DIAGNOSTIC_ONLY_CONFIRMATION_ITEM = 6
S7_DISPOSITION = "diagnostic_only"

_STRUCTURAL_GUARD_ERRORS = [
    error
    for error, violated in (
        ("section 12.1 guarantee 1: item 11 must not gate", 11 in GATED_DEVELOPMENT_ITEMS),
        ("section 13.8: item 6 must not gate", 6 in GATED_CONFIRMATION_ITEMS),
    )
    if violated
]
if _STRUCTURAL_GUARD_ERRORS:  # pragma: no cover - import-time structural guard
    raise RuntimeError("; ".join(_STRUCTURAL_GUARD_ERRORS))


class ScoringMachineryError(RuntimeError):
    """A frozen scoring, gate or error-propagation rule was violated."""


class DiagnosticOnlyMisuse(ScoringMachineryError):
    """A `diagnostic_only` record was read as if it carried a verdict."""


class SubstitutionMisuse(ScoringMachineryError):
    """An evaluator-only D1--D4 substitution was offered to a gate."""


class ChoiceSetError(ScoringMachineryError):
    """A choice-set input violated the section-4.2 definition."""


class DiagnosticOnly:
    """Section 8.6/12.1 wrapper: reportable measurement, never a verdict.

    The wrapped record is reachable only through :meth:`as_record`, which the
    report builder uses. Reading ``verdict``, ``passes``, ``failed``, ``status``
    or any other attribute raises :class:`DiagnosticOnlyMisuse`, so an
    eligibility computation cannot accidentally consume S-7 as a gate.
    """

    __slots__ = ("_record",)

    diagnostic_only = True
    disposition = S7_DISPOSITION

    def __init__(self, record: Mapping[str, object]) -> None:
        object.__setattr__(
            self, "_record", {str(key): value for key, value in dict(record).items()}
        )

    def __setattr__(self, name: str, value: object) -> None:
        raise DiagnosticOnlyMisuse("a diagnostic-only record is immutable")

    def as_record(self) -> dict:
        """The sanctioned reporting access. Never consulted for a verdict."""

        return {key: value for key, value in self._record.items()}

    def __getitem__(self, key: str) -> object:
        if str(key) in _VERDICT_KEYS:
            raise DiagnosticOnlyMisuse(
                f"section 12.1: the diagnostic-only record has no {key!r}"
            )
        return self._record[str(key)]

    def __contains__(self, key: object) -> bool:
        return str(key) in self._record and str(key) not in _VERDICT_KEYS

    @property
    def verdict(self) -> object:
        raise DiagnosticOnlyMisuse(
            "section 12.1 guarantee 2: the S-7 record has no verdict and may "
            "never be read as a gate"
        )

    @property
    def passes(self) -> object:
        raise DiagnosticOnlyMisuse(
            "section 8.6: S-7 may not gate; `passes` is not readable"
        )

    @property
    def failed(self) -> object:
        raise DiagnosticOnlyMisuse(
            "section 8.6: S-7 may not gate; `failed` is not readable"
        )

    @property
    def status(self) -> object:
        raise DiagnosticOnlyMisuse(
            "section 8.6: S-7 may not gate; `status` is not readable"
        )

    def __getattr__(self, name: str) -> object:
        raise DiagnosticOnlyMisuse(
            f"section 8.6: the diagnostic-only S-7 record may not be read as "
            f"a gate ({name!r})"
        )


_VERDICT_KEYS = ("verdict", "passes", "failed", "status", "pass")


class EvaluatorOnlySubstitution:
    """Section 10.3: a D1--D4 counterfactual reconstruction.

    It is reported in its own section, never written back, and never offered to
    a gate. Any attribute read that would look like a gate verdict raises
    :class:`SubstitutionMisuse`.
    """

    __slots__ = ("_record",)

    evaluator_only_diagnostic_substitution = True

    def __init__(self, record: Mapping[str, object]) -> None:
        object.__setattr__(
            self, "_record", {str(key): value for key, value in dict(record).items()}
        )

    def __setattr__(self, name: str, value: object) -> None:
        raise SubstitutionMisuse("an evaluator-only substitution is immutable")

    def as_record(self) -> dict:
        return {key: value for key, value in self._record.items()}

    def __getitem__(self, key: str) -> object:
        if str(key) in _VERDICT_KEYS:
            raise SubstitutionMisuse(
                f"section 10.3: a substituted row has no {key!r}"
            )
        return self._record[str(key)]

    @property
    def verdict(self) -> object:
        raise SubstitutionMisuse(
            "section 10.3: no substituted result may satisfy any gate"
        )

    @property
    def passes(self) -> object:
        raise SubstitutionMisuse(
            "section 10.3: no substituted result may satisfy any gate"
        )

    def __getattr__(self, name: str) -> object:
        raise SubstitutionMisuse(
            f"section 10.3: a substituted row may not be read as a gate ({name!r})"
        )


def assert_gate_input(value: object) -> object:
    """Section 10.3: only D0 (measured) rows may reach a gate."""

    if isinstance(value, EvaluatorOnlySubstitution):
        raise SubstitutionMisuse(
            "section 10.3: no substituted result may satisfy any gate"
        )
    if isinstance(value, DiagnosticOnly):
        raise DiagnosticOnlyMisuse(
            "section 8.6: a diagnostic-only record is not a gate input"
        )
    if isinstance(value, Mapping):
        if value.get("evaluator_only_diagnostic_substitution"):
            raise SubstitutionMisuse(
                "section 10.3: no substituted result may satisfy any gate"
            )
        if value.get("diagnostic_only"):
            raise DiagnosticOnlyMisuse(
                "section 8.6: a diagnostic-only record is not a gate input"
            )
    return value


# -- 4.2 choice sets ---------------------------------------------------------


def rounded_values(
    values: Mapping[int, float], *, digits: int = ROUND_DIGITS
) -> dict[int, float]:
    """Each value rounded to 12 decimal places, the frozen harness tolerance."""

    return {int(slot): round(float(value), digits) for slot, value in values.items()}


def choice_set(values: Mapping[int, float], legal_target_slots: Iterable[int]) -> tuple[int, ...]:
    """Section 4.2 ``G_i``/``M_i``: the legal argmax set after rounding."""

    legal = tuple(int(slot) for slot in legal_target_slots)
    if not legal:
        raise ChoiceSetError("the legal target set is empty")
    missing = [slot for slot in legal if slot not in values]
    if missing:
        raise ChoiceSetError(f"missing target values: {missing}")
    rounded = rounded_values({slot: values[slot] for slot in legal})
    maximum = max(rounded.values())
    return tuple(sorted(slot for slot in legal if rounded[slot] == maximum))


def decision_preserved(
    model_choice_set: Iterable[int], gold_choice_set: Iterable[int]
) -> bool:
    """Section 4.3: non-empty and a subset of the gold choice set."""

    model = {int(slot) for slot in model_choice_set}
    gold = {int(slot) for slot in gold_choice_set}
    return bool(model) and model <= gold


def choice_set_record(
    case_id: str,
    *,
    gold_values: Mapping[int, float],
    model_values: Mapping[int, float],
    legal_target_slots: Iterable[int],
    evaluator_ordinal_by_case: object | None = None,
) -> dict:
    """One section-4.2 ``G_i``/``M_i`` row.

    ``evaluator_ordinal_by_case`` exists only so callers can hand over the
    evaluator-channel ordinal structure. It is deliberately never read: the
    canonical ordinal cannot influence either choice set (sections 4.2 and
    4.5). Tests pass a poison object to prove that.
    """

    legal = tuple(int(slot) for slot in legal_target_slots)
    gold = choice_set(gold_values, legal)
    model = choice_set(model_values, legal)
    rounded_gold = rounded_values({slot: gold_values[slot] for slot in legal})
    rounded_model = rounded_values({slot: model_values[slot] for slot in legal})
    return {
        "schema_version": SCHEMA_VERSION,
        "case_id": str(case_id),
        "legal_target_slots": list(legal),
        "L_i": list(legal),
        "G_i": list(gold),
        "M_i": list(model),
        "G_i_size": len(gold),
        "M_i_size": len(model),
        "gold_choice_set_is_legal_set": set(gold) == set(legal),
        "M_i_equals_G_i": set(model) == set(gold),
        "M_i_is_subset_of_G_i": set(model) <= set(gold),
        "model_choice_set_is_empty": not model,
        "preserved": decision_preserved(model, gold),
        "gold_values_rounded": {str(slot): rounded_gold[slot] for slot in legal},
        "model_values_rounded": {str(slot): rounded_model[slot] for slot in legal},
        "evaluator_ordinal_used": False,
    }


# -- 4.4 primary endpoint ----------------------------------------------------


def _gate_flag(value: object) -> bool:
    assert_gate_input(value)
    if isinstance(value, Mapping):
        if "preserved" not in value:
            raise ScoringMachineryError("a gate row must carry `preserved`")
        return bool(value["preserved"])
    return bool(value)


def primary_endpoint(
    preserved_by_source: Mapping[str, object],
    *,
    denominator: int = PRIMARY_SOURCE_DENOMINATOR,
    threshold: int = PRIMARY_SOURCE_THRESHOLD,
) -> dict:
    """Section 4.4 primary gate over one repeat's canonical sources."""

    values = {str(source): _gate_flag(flag) for source, flag in preserved_by_source.items()}
    if len(values) != denominator:
        raise ScoringMachineryError(
            f"the section-4.4 denominator is {denominator}; received {len(values)} sources"
        )
    preserved = sorted(source for source, flag in values.items() if flag)
    failed = sorted(source for source, flag in values.items() if not flag)
    return {
        "schema_version": SCHEMA_VERSION,
        "denominator": denominator,
        "threshold": threshold,
        "preserved_count": len(preserved),
        "preservation_rate": len(preserved) / denominator,
        "preserved_sources": preserved,
        "failed_sources": failed,
        "passes": len(preserved) >= threshold,
        "gate": f"choice-set preservation >= {threshold}/{denominator}",
    }


def repeat_agreement(preserved_by_repeat: Mapping[int, Mapping[str, object]]) -> dict:
    """Section 4.4: report agreement and paired disagreement; never average."""

    repeats = sorted(int(repeat) for repeat in preserved_by_repeat)
    if len(repeats) != 2:
        raise ScoringMachineryError("development repeat agreement needs two repeats")
    first, second = preserved_by_repeat[repeats[0]], preserved_by_repeat[repeats[1]]
    sources = sorted(set(first) | set(second))
    agree, disagree = [], []
    for source in sources:
        left = bool(first.get(source, False))
        right = bool(second.get(source, False))
        (agree if left == right else disagree).append(source)
    return {
        "repeats": repeats,
        "source_count": len(sources),
        "agreement_count": len(agree),
        "agreement_rate": (len(agree) / len(sources)) if sources else None,
        "agreeing_sources": agree,
        "paired_disagreements": disagree,
        "is_averaged_into_primary": False,
    }


def development_primary(
    preserved_by_repeat: Mapping[int, Mapping[str, object]],
    *,
    denominator: int = PRIMARY_SOURCE_DENOMINATOR,
    threshold: int = PRIMARY_SOURCE_THRESHOLD,
) -> dict:
    """Section 4.4: the primary endpoint, separately on each development repeat."""

    repeats = {
        str(int(repeat)): primary_endpoint(
            rows, denominator=denominator, threshold=threshold
        )
        for repeat, rows in sorted(preserved_by_repeat.items())
    }
    agreement = repeat_agreement(preserved_by_repeat)
    return {
        "schema_version": SCHEMA_VERSION,
        "unit_of_evidence": "canonical source instance",
        "per_repeat": repeats,
        "repeat_agreement": agreement,
        "passes": all(item["passes"] for item in repeats.values()),
        "both_repeats_reach_threshold": all(
            item["passes"] for item in repeats.values()
        ),
    }


# -- 8.2 absolute usefulness and 8.3 S-13 paired degradation -----------------


def absolute_usefulness_gate(top1: float, top2: float, regret: float) -> dict:
    """Section 8.2 S-11 over the 8 canonical sources (frozen scorer output)."""

    assert_gate_input(top1)
    assert_gate_input(top2)
    assert_gate_input(regret)
    checks = {
        "top1": float(top1) >= ABSOLUTE_TOP1_MIN,
        "top2": float(top2) >= ABSOLUTE_TOP2_MIN,
        "mean_normalized_regret": float(regret) <= ABSOLUTE_REGRET_MAX + VALUE_TOLERANCE,
    }
    return {
        "observed": {
            "top1": float(top1),
            "top2": float(top2),
            "mean_normalized_regret": float(regret),
        },
        "thresholds": {
            "top1": f">= {ABSOLUTE_TOP1_MIN}",
            "top2": f">= {ABSOLUTE_TOP2_MIN}",
            "mean_normalized_regret": f"<= {ABSOLUTE_REGRET_MAX}",
        },
        "checks": checks,
        "passes": all(checks.values()),
    }


_MALFORMED_MODEL_ROW = {"top1": 0.0, "top2": 0.0, "mean_normalized_regret": 1.0}


def paired_degradation(
    gold_by_source: Mapping[str, Mapping[str, float] | None],
    model_by_source: Mapping[str, Mapping[str, float] | None],
    *,
    denominator: int = PRIMARY_SOURCE_DENOMINATOR,
) -> dict:
    """Section 8.3 S-13, on the fixed eight-source denominator.

    A source whose model response is ``malformed_or_missing`` contributes
    ``top1_model = top2_model = 0`` and ``regret_model = 1.0`` and is never
    dropped. Each source's excess regret is clamped at zero before averaging,
    so a source where the model beats gold cannot offset a degradation.
    """

    sources = sorted(set(gold_by_source) | set(model_by_source))
    for source in sources:
        assert_gate_input(gold_by_source.get(source))
        assert_gate_input(model_by_source.get(source))
    if len(sources) != denominator:
        raise ScoringMachineryError(
            f"the section-8.3 S-13 denominator is {denominator}; received {len(sources)}"
        )
    rows = {}
    for source in sources:
        gold = gold_by_source.get(source)
        if gold is None:
            raise ScoringMachineryError(f"gold row missing for source {source}")
        model = model_by_source.get(source) or _MALFORMED_MODEL_ROW
        excess = float(model["mean_normalized_regret"]) - float(
            gold["mean_normalized_regret"]
        )
        rows[source] = {
            "top1_gold": float(gold["top1"]),
            "top1_model": float(model["top1"]),
            "top2_gold": float(gold["top2"]),
            "top2_model": float(model["top2"]),
            "regret_gold": float(gold["mean_normalized_regret"]),
            "regret_model": float(model["mean_normalized_regret"]),
            "excess_regret": excess,
            "positive_excess_regret": max(0.0, excess),
            "model_response_malformed_or_missing": source not in model_by_source
            or model_by_source.get(source) is None,
        }
    top1_gold = sum(row["top1_gold"] for row in rows.values()) / denominator
    top1_model = sum(row["top1_model"] for row in rows.values()) / denominator
    top2_gold = sum(row["top2_gold"] for row in rows.values()) / denominator
    top2_model = sum(row["top2_model"] for row in rows.values()) / denominator
    mean_positive_excess = (
        sum(row["positive_excess_regret"] for row in rows.values()) / denominator
    )
    top1_decline = top1_gold - top1_model
    top2_decline = top2_gold - top2_model
    checks = {
        "top1_decline": top1_decline <= PAIRED_TOP1_DECLINE_MAX + VALUE_TOLERANCE,
        "top2_decline": top2_decline <= PAIRED_TOP2_DECLINE_MAX + VALUE_TOLERANCE,
        "mean_positive_excess": mean_positive_excess
        <= PAIRED_MEAN_POSITIVE_EXCESS_MAX + VALUE_TOLERANCE,
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "gate": "S-13 paired degradation",
        "denominator": denominator,
        "per_source": rows,
        "observed": {
            "top1_gold": top1_gold,
            "top1_model": top1_model,
            "top2_gold": top2_gold,
            "top2_model": top2_model,
            "top1_decline": top1_decline,
            "top2_decline": top2_decline,
            "mean_positive_excess_regret": mean_positive_excess,
        },
        "thresholds": {
            "top1_decline": f"<= {PAIRED_TOP1_DECLINE_MAX}",
            "top2_decline": f"<= {PAIRED_TOP2_DECLINE_MAX}",
            "mean_positive_excess_regret": f"<= {PAIRED_MEAN_POSITIVE_EXCESS_MAX}",
        },
        "checks": checks,
        "passes": all(checks.values()),
        "is_a_population_estimate": False,
    }


# -- 8.3 S-14 model-conditioned own-selection equivariance -------------------


def own_selection_equivariance(
    comparisons: Sequence[Mapping[str, object]],
    *,
    expected_total: int,
) -> dict:
    """Section 8.3 S-14, repeat-matched over the five equivalence variants.

    A comparison row carries ``source_episode_id``, ``variant``, ``repeat``,
    ``base_repeat``, ``variant_response_present``, ``base_response_present``,
    ``variant_selection`` (mapped canonical ordinals) and ``base_selection``.
    ``base_repeat`` must equal ``repeat``: a cross-repeat comparison is
    rejected, never substituted. A comparison involving a malformed or missing
    response fails; it is never excluded, and the denominator stays fixed.
    """

    failures: list[dict] = []
    value_vector_equal = 0
    value_vector_total = 0
    semantic_equal = 0
    semantic_total = 0
    for row in comparisons:
        assert_gate_input(row)
        if int(row["base_repeat"]) != int(row["repeat"]):
            raise ScoringMachineryError(
                "section 8.3: S-14 is repeat-matched; a comparison against "
                f"repeat {row['base_repeat']} was offered for repeat {row['repeat']}"
            )
        identity = {
            "source_episode_id": str(row["source_episode_id"]),
            "variant": str(row["variant"]),
            "repeat": int(row["repeat"]),
        }
        if not row["variant_response_present"]:
            failures.append({**identity, "reason": "variant_response_missing"})
            continue
        if not row["base_response_present"]:
            failures.append({**identity, "reason": "repeat_matched_base_response_missing"})
            continue
        variant_selection = {int(slot) for slot in row["variant_selection"]}
        base_selection = {int(slot) for slot in row["base_selection"]}
        if variant_selection != base_selection:
            failures.append(
                {
                    **identity,
                    "reason": "selection_mismatch",
                    "variant_selection": sorted(variant_selection),
                    "base_selection": sorted(base_selection),
                }
            )
        if row.get("value_vector_equal") is not None:
            value_vector_total += 1
            value_vector_equal += int(bool(row["value_vector_equal"]))
        if row.get("response_semantically_equal") is not None:
            semantic_total += 1
            semantic_equal += int(bool(row["response_semantically_equal"]))
    total = len(comparisons)
    return {
        "schema_version": SCHEMA_VERSION,
        "gate": "S-14 model-conditioned own-selection equivariance",
        "comparisons_total": total,
        "comparisons_required": expected_total,
        "comparisons_passed": total - len(failures),
        "failures": failures,
        "passes": total == expected_total and not failures,
        "denominator_is_fixed": True,
        "repeat_matched": True,
        "non_gating": {
            "value_vector_equivalence": (
                (value_vector_equal / value_vector_total)
                if value_vector_total
                else "NA"
            ),
            "value_vector_comparisons": value_vector_total,
            "response_semantic_equivalence": (
                (semantic_equal / semantic_total) if semantic_total else "NA"
            ),
            "response_semantic_comparisons": semantic_total,
        },
        "is_a_population_estimate": False,
    }


# -- 8.3 S-15 directional-effect continuity ----------------------------------


def directional_item_set(
    candidate_effects: Mapping[str, str],
    family_by_slot: Mapping[str, str],
) -> set[tuple[str, str]]:
    """Section 8.3: ``{(effect_family, value)}`` for support/contradict only."""

    items: set[tuple[str, str]] = set()
    for slot, value in candidate_effects.items():
        if str(value) in ("support", "contradict"):
            items.add((str(family_by_slot[str(slot)]), str(value)))
    return items


def _micro_rate(
    tp: int, positive_denominator: int
) -> float | str:
    return (tp / positive_denominator) if positive_denominator else "NA"


def directional_continuity(
    comparisons: Sequence[Mapping[str, object]],
    *,
    precision_min: float = CONTINUITY_PRECISION_MIN,
    recall_min: float = CONTINUITY_RECALL_MIN,
) -> dict:
    """Section 8.3 S-15, micro-aggregated over both continuity axes.

    Each comparison row carries ``axis`` (``cross_variant`` or ``cross_repeat``),
    ``reference_present``, ``compared_present`` and the directional item sets
    ``reference_items`` / ``compared_items``. A malformed or missing response
    contributes an empty item set, which contributes its reference items as
    false negatives and never as a passed comparison.
    """

    totals = defaultdict(lambda: {"tp": 0, "positive": 0, "reference": 0, "rows": 0})
    for row in comparisons:
        assert_gate_input(row)
        axis = str(row["axis"])
        bucket = totals[axis]
        bucket["rows"] += 1
        reference = (
            {tuple(item) for item in row.get("reference_items", ())}
            if row.get("reference_present")
            else set()
        )
        compared = (
            {tuple(item) for item in row.get("compared_items", ())}
            if row.get("compared_present")
            else set()
        )
        bucket["tp"] += len(compared & reference)
        bucket["positive"] += len(compared)
        bucket["reference"] += len(reference)
    per_axis = {}
    for axis, bucket in sorted(totals.items()):
        per_axis[axis] = {
            "comparison_count": bucket["rows"],
            "true_positives": bucket["tp"],
            "compared_item_count": bucket["positive"],
            "reference_item_count": bucket["reference"],
            "precision": _micro_rate(bucket["tp"], bucket["positive"]),
            "recall": _micro_rate(bucket["tp"], bucket["reference"]),
            "is_gate": False,
        }
    for axis in ("cross_variant", "cross_repeat"):
        per_axis.setdefault(
            axis,
            {
                "comparison_count": 0,
                "true_positives": 0,
                "compared_item_count": 0,
                "reference_item_count": 0,
                "precision": "NA",
                "recall": "NA",
                "is_gate": False,
            },
        )
    tp = sum(bucket["tp"] for bucket in totals.values())
    positive = sum(bucket["positive"] for bucket in totals.values())
    reference = sum(bucket["reference"] for bucket in totals.values())
    precision = _micro_rate(tp, positive)
    recall = _micro_rate(tp, reference)
    return {
        "schema_version": SCHEMA_VERSION,
        "gate": "S-15 directional-effect continuity",
        "axis_definition": {
            "cross_variant": "base_entry(s, r) reference, variant(s, r) compared",
            "cross_repeat": "development only: repeat 1 reference, repeat 2 compared",
        },
        "per_axis": per_axis,
        "micro_aggregate": {
            "true_positives": tp,
            "compared_item_count": positive,
            "reference_item_count": reference,
            "precision": precision,
            "recall": recall,
        },
        "thresholds": {"precision": f">= {precision_min}", "recall": f">= {recall_min}"},
        "checks": {
            "precision": (precision != "NA") and float(precision) >= precision_min,
            "recall": (recall != "NA") and float(recall) >= recall_min,
        },
        "na_cannot_clear_a_threshold": True,
        "passes": (precision != "NA")
        and (recall != "NA")
        and float(precision) >= precision_min
        and float(recall) >= recall_min,
        "is_a_population_estimate": False,
    }


# -- 8.6 S-7 effect self-consistency, diagnostic_only ------------------------


def expected_effects_from_facts(
    contract: Mapping[str, object],
    candidate_hypotheses: Sequence[Mapping[str, object]],
    facts: Mapping[str, bool],
) -> dict[str, str]:
    """``T_c(F_r)``, the frozen public truth table (section 8.6.2)."""

    from ser.authzgym.v1_3_contract import effect_from_facts

    return effect_from_facts(contract, [dict(item) for item in candidate_hypotheses], facts)


def effect_self_consistency(
    records: Sequence[Mapping[str, object]], *, contract: Mapping[str, object]
) -> dict:
    """Section 8.6: mandatory measurement, no threshold, no veto.

    Every record carries ``case_id``, ``split``, ``repeat``,
    ``attempt_ordinal``, ``source_episode_id``, ``variant`` and ``status``
    (``measured`` / ``invalid`` / ``missing``). A measured record also carries
    ``facts``, ``candidate_effects`` and ``candidate_hypotheses``.
    """

    n = 0
    consistent_responses = 0
    consistent_fields = 0
    violations: list[dict] = []
    invalid_count = 0
    missing_count = 0
    by_repeat: dict[str, dict] = defaultdict(
        lambda: {"responses": 0, "consistent_responses": 0, "consistent_fields": 0, "violation_count": 0}
    )
    by_case: dict[str, dict] = defaultdict(
        lambda: {"responses": 0, "consistent_responses": 0, "consistent_fields": 0, "violation_count": 0}
    )
    by_source: dict[str, dict] = defaultdict(
        lambda: {"responses": 0, "consistent_responses": 0, "consistent_fields": 0, "violation_count": 0}
    )
    by_variant: dict[str, dict] = defaultdict(
        lambda: {"responses": 0, "consistent_responses": 0, "consistent_fields": 0, "violation_count": 0}
    )
    by_family: dict[str, dict] = defaultdict(
        lambda: {"fields": 0, "consistent_fields": 0, "violation_count": 0}
    )
    for record in records:
        status = str(record.get("status", "missing"))
        if status == "invalid":
            invalid_count += 1
            continue
        if status != "measured":
            missing_count += 1
            continue
        candidates = list(record["candidate_hypotheses"])
        expected = expected_effects_from_facts(contract, candidates, record["facts"])
        family_by_slot = {str(item["slot"]): str(item["effect_family"]) for item in candidates}
        fields = sorted(expected)
        response_consistent = True
        buckets = [
            by_repeat[str(record["repeat"])],
            by_case[str(record["case_id"])],
            by_source[str(record["source_episode_id"])],
            by_variant[str(record["variant"])],
        ]
        for bucket in buckets:
            bucket["responses"] += 1
        n += 1
        submitted_fact_vector = {
            str(slot): bool(value) for slot, value in dict(record["facts"]).items()
        }
        for slot in fields:
            submitted = str(record["candidate_effects"][slot])
            family = family_by_slot[str(slot)]
            by_family[family]["fields"] += 1
            if submitted == expected[slot]:
                consistent_fields += 1
                for bucket in buckets:
                    bucket["consistent_fields"] += 1
                by_family[family]["consistent_fields"] += 1
                continue
            response_consistent = False
            by_family[family]["violation_count"] += 1
            for bucket in buckets:
                bucket["violation_count"] += 1
            violations.append(
                {
                    "case_id": str(record["case_id"]),
                    "split": str(record.get("split", "")),
                    "repeat": int(record["repeat"]),
                    "attempt_ordinal": record.get("attempt_ordinal"),
                    "source_episode_id": str(record["source_episode_id"]),
                    "variant": str(record["variant"]),
                    "candidate_slot": str(slot),
                    "public_family": family,
                    "submitted_fact_vector": submitted_fact_vector,
                    "submitted_effect": submitted,
                    "truth_table_effect": expected[slot],
                    "consistent": False,
                }
            )
        if response_consistent:
            consistent_responses += 1
            for bucket in buckets:
                bucket["consistent_responses"] += 1
    for bucket in list(by_repeat.values()) + list(by_case.values()) + list(
        by_source.values()
    ) + list(by_variant.values()):
        bucket["C_response"] = (
            bucket["consistent_responses"] / bucket["responses"]
            if bucket["responses"]
            else "NA"
        )
        bucket["C_field"] = (
            bucket["consistent_fields"] / (4 * bucket["responses"])
            if bucket["responses"]
            else "NA"
        )
    for bucket in by_family.values():
        bucket["C_field"] = (
            bucket["consistent_fields"] / bucket["fields"] if bucket["fields"] else "NA"
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "metric": "S-7 effect self-consistency",
        "disposition": S7_DISPOSITION,
        "gate_applies": False,
        "threshold": None,
        "formula": "I_rc = 1[E_rc = T_c(F_r)]",
        "C_response": (consistent_responses / n) if n else "NA",
        "C_field": (consistent_fields / (4 * n)) if n else "NA",
        "structurally_valid_measured_response_count": n,
        "consistent_response_count": consistent_responses,
        "inconsistent_response_count": n - consistent_responses,
        "consistent_field_count": consistent_fields,
        "field_count": 4 * n,
        "invalid_response_count_excluded": invalid_count,
        "missing_response_count_excluded": missing_count,
        "invalid_and_missing_never_imputed_consistent": True,
        "by_repeat": {key: dict(value) for key, value in sorted(by_repeat.items())},
        "by_case": {key: dict(value) for key, value in sorted(by_case.items())},
        "by_source": {key: dict(value) for key, value in sorted(by_source.items())},
        "by_variant": {key: dict(value) for key, value in sorted(by_variant.items())},
        "by_family": {key: dict(value) for key, value in sorted(by_family.items())},
        "violations": violations,
        "violation_count": len(violations),
    }


def diagnostic_only_s7(records: Sequence[Mapping[str, object]], *, contract: Mapping[str, object]) -> DiagnosticOnly:
    """The S-7 record wrapped so it can never be read as a gate."""

    return DiagnosticOnly(effect_self_consistency(records, contract=contract))


# -- 10.2 error-propagation classes ------------------------------------------

ERROR_CLASSES = (
    "malformed_or_missing",
    "structurally_catastrophic",
    "decision_changing",
    "value_harmless",
    "decision_harmless",
)


def _vectors_equal(
    left: Mapping[int, float],
    right: Mapping[int, float],
    legal: Sequence[int],
) -> bool:
    return all(
        abs(float(left[slot]) - float(right[slot])) <= VALUE_TOLERANCE for slot in legal
    )


def classify_error_propagation(
    *,
    measured_response_present: bool,
    model_choice_set: Iterable[int] | None,
    gold_choice_set: Iterable[int],
    legal_target_slots: Iterable[int],
    model_values: Mapping[int, float] | None = None,
    gold_values: Mapping[int, float] | None = None,
) -> dict:
    """Section 10.2, applied in precedence order; exactly one class per case."""

    legal = tuple(int(slot) for slot in legal_target_slots)
    gold = {int(slot) for slot in gold_choice_set}
    if not measured_response_present or model_choice_set is None:
        return {
            "error_class": "malformed_or_missing",
            "precedence_ordinal": 1,
            "preserved": False,
            "detail": "no structurally valid response; no B-1 evaluation is possible",
        }
    model = {int(slot) for slot in model_choice_set}
    legal_set = set(legal)
    if model == legal_set and gold < legal_set:
        return {
            "error_class": "structurally_catastrophic",
            "precedence_ordinal": 2,
            "preserved": False,
            "detail": "M_i == L_i while G_i is a proper subset of L_i (ND-1 signature)",
        }
    if model and not model <= gold:
        return {
            "error_class": "decision_changing",
            "precedence_ordinal": 3,
            "preserved": False,
            "detail": "M_i is non-empty and introduces a target outside G_i",
        }
    vectors_equal = (
        model_values is not None
        and gold_values is not None
        and _vectors_equal(model_values, gold_values, legal)
    )
    if vectors_equal:
        return {
            "error_class": "value_harmless",
            "precedence_ordinal": 4,
            "preserved": decision_preserved(model, gold),
            "detail": "model and gold value vectors agree within 1e-12",
        }
    return {
        "error_class": "decision_harmless",
        "precedence_ordinal": 5,
        "preserved": decision_preserved(model, gold),
        "detail": "value vectors differ; M_i is non-empty and a subset of G_i",
    }


def error_class_census(classes: Iterable[str]) -> dict:
    counts = {name: 0 for name in ERROR_CLASSES}
    for name in classes:
        counts[str(name)] = counts.get(str(name), 0) + 1
    return counts


# -- 10.1 localization -------------------------------------------------------


def localization_tables(rows: Sequence[Mapping[str, object]]) -> dict:
    """Section 10.1: per-fact, per-effect, per-relation and paired localization."""

    fact_slots = sorted(
        {
            str(slot)
            for row in rows
            for slot in dict(row.get("facts", {})).keys()
        }
    )
    facts = {
        slot: {"true_positive": 0, "false_positive": 0, "false_negative": 0, "true_negative": 0}
        for slot in fact_slots
    }
    effect_matrix: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    directional = {"true_positive": 0, "false_positive": 0, "false_negative": 0}
    relation_slots = sorted(
        {
            str(relation)
            for row in rows
            for target in dict(row.get("unresolved_targets", {})).values()
            for relation in dict(target).keys()
        }
    )
    target_slots = sorted(
        {
            str(target)
            for row in rows
            for target in dict(row.get("unresolved_targets", {})).keys()
        }
    )
    relations = {
        f"{target}:{relation}": {
            "agree_true": 0,
            "agree_false": 0,
            "model_only": 0,
            "gold_only": 0,
        }
        for target in target_slots
        for relation in relation_slots
    }
    paired = []
    for row in rows:
        case_id = str(row["case_id"])
        for slot in fact_slots:
            model = bool(dict(row.get("facts", {})).get(slot, False))
            gold = bool(dict(row.get("gold_facts", {})).get(slot, False))
            buckets = {
                (True, True): "true_positive",
                (True, False): "false_positive",
                (False, True): "false_negative",
                (False, False): "true_negative",
            }
            facts[slot][buckets[(model, gold)]] += 1
        for slot, value in dict(row.get("candidate_effects", {})).items():
            gold_value = dict(row.get("gold_candidate_effects", {})).get(slot, "missing")
            effect_matrix[str(slot)][f"{value}->{gold_value}"] += 1
            model_directional = str(value) in ("support", "contradict")
            gold_directional = str(gold_value) in ("support", "contradict")
            if model_directional and gold_directional and value == gold_value:
                directional["true_positive"] += 1
            elif model_directional and gold_directional:
                directional["false_positive"] += 1
                directional["false_negative"] += 1
            elif model_directional:
                directional["false_positive"] += 1
            elif gold_directional:
                directional["false_negative"] += 1
        for target, relations_value in dict(row.get("unresolved_targets", {})).items():
            gold_target = dict(row.get("gold_unresolved_targets", {})).get(target, {})
            for relation, value in dict(relations_value).items():
                key = f"{target}:{relation}"
                if key not in relations:
                    continue
                gold_flag = bool(dict(gold_target).get(relation, False))
                flag = bool(value)
                if flag and gold_flag:
                    relations[key]["agree_true"] += 1
                elif not flag and not gold_flag:
                    relations[key]["agree_false"] += 1
                elif flag:
                    relations[key]["model_only"] += 1
                else:
                    relations[key]["gold_only"] += 1
        paired.append(
            {
                "case_id": case_id,
                "model_salient_tags": sorted(str(item) for item in row.get("salient_tags_model", ())),
                "gold_salient_tags": sorted(str(item) for item in row.get("salient_tags_gold", ())),
                "value_vector_model": {
                    str(slot): float(value)
                    for slot, value in sorted(dict(row.get("model_values", {})).items())
                },
                "value_vector_gold": {
                    str(slot): float(value)
                    for slot, value in sorted(dict(row.get("gold_values", {})).items())
                },
                "M_i": sorted(int(slot) for slot in row.get("model_choice_set", ())),
                "G_i": sorted(int(slot) for slot in row.get("gold_choice_set", ())),
                "selected_model": row.get("selected_model"),
                "selected_gold": row.get("selected_gold"),
                "top1_model": row.get("top1_model"),
                "top1_gold": row.get("top1_gold"),
                "top2_model": row.get("top2_model"),
                "top2_gold": row.get("top2_gold"),
                "regret_model": row.get("regret_model"),
                "regret_gold": row.get("regret_gold"),
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "fact_slot_confusion": facts,
        "candidate_effect_confusion": {
            slot: dict(counts) for slot, counts in sorted(effect_matrix.items())
        },
        "directional_effect_subset": directional,
        "relation_confusion": relations,
        "per_case_paired_readout": paired,
    }


# -- 10.3 evaluator-only diagnostic substitutions ----------------------------


def diagnostic_substitution(
    *,
    identifier: str,
    case_id: str,
    values: Mapping[int, float],
    legal_target_slots: Iterable[int],
    gold_values: Mapping[int, float],
    gold_choice_set: Iterable[int],
    usefulness_by_slot: Mapping[int, float],
    evaluator_ordinal_by_slot: Mapping[int, int],
    effects_source: str,
    relations_source: str,
    isolates: str,
    measured: bool = False,
) -> EvaluatorOnlySubstitution:
    """One section-10.3 reconstruction, evaluated in the evaluator channel.

    ``D0`` is the measured result and is not a substitution. ``D1``--``D4`` are
    wrapped so a gate cannot read them. The frozen scorer's selection rule
    (``(-value, canonical ordinal ascending)``) supplies top-1/top-2/regret.
    """

    legal = tuple(int(slot) for slot in legal_target_slots)
    model = choice_set(values, legal)
    gold = {int(slot) for slot in gold_choice_set}
    ranked = sorted(
        legal,
        key=lambda slot: (-float(values[slot]), int(evaluator_ordinal_by_slot[slot])),
    )
    usefulness = {slot: float(usefulness_by_slot[slot]) for slot in legal}
    best = max(usefulness.values())
    lowest = min(usefulness.values())
    oracle_best = {slot for slot in legal if abs(usefulness[slot] - best) <= VALUE_TOLERANCE}
    nondiscriminating = abs(best - lowest) <= VALUE_TOLERANCE
    selected = ranked[0]
    regret = (
        0.0
        if nondiscriminating
        else (best - usefulness[selected]) / (best - lowest)
    )
    record = {
        "schema_version": SCHEMA_VERSION,
        "row_type": "evaluator_only_diagnostic_substitution",
        "identifier": str(identifier),
        "case_id": str(case_id),
        "effects_source": str(effects_source),
        "relations_source": str(relations_source),
        "isolates": str(isolates),
        "measured_result": bool(measured),
        "value_vector": {str(slot): float(values[slot]) for slot in legal},
        "choice_set": list(model),
        "preserved_equivalent": decision_preserved(model, gold),
        "M_i_is_subset_of_G_i": set(model) <= gold,
        "selected": selected,
        "top1": bool(nondiscriminating or selected in oracle_best),
        "top2": bool(nondiscriminating or set(ranked[:2]) & oracle_best),
        "mean_normalized_regret": regret,
        "nondiscriminating": nondiscriminating,
        "gold_values": {str(slot): float(gold_values[slot]) for slot in legal},
    }
    if measured:
        return record
    return EvaluatorOnlySubstitution(record)


def substitution_table(rows: Sequence[object]) -> dict:
    """Section 10.3 report section: D0 measured, D1--D4 evaluator-only."""

    table = {}
    for row in rows:
        if isinstance(row, EvaluatorOnlySubstitution):
            record = row.as_record()
        elif isinstance(row, Mapping) and row.get("row_type") == "evaluator_only_diagnostic_substitution":
            record = dict(row)
        else:
            record = dict(row)
        table[str(record["identifier"])] = record
    return {
        "schema_version": SCHEMA_VERSION,
        "row_label": "evaluator_only_diagnostic_substitution",
        "rows": table,
        "substituted_results_never_satisfy_a_gate": True,
        "measured_response_unchanged": True,
        "D0_D3_pair_localizes": "section 8.6 consequence 10",
    }


# -- 12 / 15 eligibility, validity precedence and the outcome label ----------


VALIDITY_LAYER_ORDER = (
    "frozen_manifest_integrity",
    "access_accounting",
    "answerability",
    "firewall",
    "gold_adequacy",
    "mechanical_response",
    "semantic_interface",
    "downstream_decision",
)

# Mechanical mapping of the section-12 items onto the section-8 precedence
# chain. The order is frozen; only the item-to-layer assignment is enumerated
# here so the report marks a later layer `blocked_by` an earlier failure.
ITEM_VALIDITY_LAYER: dict[int, str] = {
    1: "frozen_manifest_integrity",
    2: "access_accounting",
    3: "access_accounting",
    4: "access_accounting",
    5: "answerability",
    6: "firewall",
    7: "gold_adequacy",
    8: "mechanical_response",
    9: "mechanical_response",
    10: "mechanical_response",
    12: "semantic_interface",
    13: "semantic_interface",
    14: "semantic_interface",
    16: "semantic_interface",
    15: "downstream_decision",
    17: "downstream_decision",
    18: "downstream_decision",
    19: "downstream_decision",
    20: "downstream_decision",
    21: "downstream_decision",
}

OUTCOME_LABELS = (
    "invalid",
    "invalid_identity_drift",
    "instrument_blocked",
    "contract_unstable",
    "semantic_screen_below_threshold",
    "decision_preservation_below_screen",
    "development_eligible",
    "bounded_model_semantic_compatibility_confirmed",
)

SEMANTIC_SCREEN_ROW_ITEMS = (10, 12, 13, 14, 15, 16, 17, 18, 19)


def validity_precedence(
    items: Mapping[int, Mapping[str, object]], missing: Iterable[int]
) -> dict:
    """Section 8 preamble: a failure blocks claims at every later layer."""

    missing_set = {int(item) for item in missing}
    status: dict[str, dict] = {}
    first_failure: str | None = None
    for layer in VALIDITY_LAYER_ORDER:
        layer_items = sorted(
            item for item, assigned in ITEM_VALIDITY_LAYER.items() if assigned == layer
        )
        layer_missing = [item for item in layer_items if item in missing_set]
        layer_failed = [
            item
            for item in layer_items
            if item in items and not bool(items[item]["pass"])
        ]
        passes = not layer_missing and not layer_failed
        if not passes and first_failure is None:
            first_failure = layer
        if not passes:
            blocked_by = None if first_failure == layer else first_failure
        else:
            blocked_by = (
                first_failure
                if first_failure is not None and first_failure != layer
                else None
            )
        status[layer] = {
            "item_ids": layer_items,
            "missing_item_ids": layer_missing,
            "failed_item_ids": layer_failed,
            "passes": passes,
            "blocked_by": blocked_by,
        }
    return {
        "order": list(VALIDITY_LAYER_ORDER),
        "first_failure": first_failure,
        "layers": status,
        "s7_outside_precedence_chain": DIAGNOSTIC_ONLY_DEVELOPMENT_ITEM,
    }


def evaluate_eligibility(
    items: Mapping[int, Mapping[str, object]],
    *,
    split: str,
    diagnostic_only: Mapping[int, DiagnosticOnly] | None = None,
    primary_item_ids: Sequence[int] = (20, 21),
    gated_items: Iterable[int] | None = None,
    identity_drift: bool = False,
) -> dict:
    """Section 12/13.8/15: gate evaluation, precedence and the outcome label."""

    split = str(split)
    diagnostic_only = dict(diagnostic_only or {})
    provisional = (
        frozenset(gated_items)
        if gated_items is not None
        else (
            GATED_DEVELOPMENT_ITEMS
            if split == "development"
            else GATED_CONFIRMATION_ITEMS
        )
    )
    misused = sorted(set(diagnostic_only) & set(provisional))
    if misused:
        raise DiagnosticOnlyMisuse(
            f"section 8.6: diagnostic-only items cannot gate: {misused}"
        )
    if split == "development" and DIAGNOSTIC_ONLY_DEVELOPMENT_ITEM in provisional:
        raise DiagnosticOnlyMisuse("section 12.1 guarantee 1 violated")
    missing = sorted(item for item in provisional if item not in items)
    failed = sorted(
        item
        for item in provisional
        if item in items and not bool(items[item]["pass"])
    )
    verdict = "pass" if not missing and not failed else "fail"
    precedence = validity_precedence(items, missing)

    def layer_ok(name: str) -> bool:
        return bool(precedence["layers"][name]["passes"])

    def item_ok(item: int) -> bool:
        return item in items and not (item in missing) and bool(items[item]["pass"])

    primary_ok = all(item_ok(item) for item in primary_item_ids)
    support_items = tuple(item for item in provisional if item not in set(primary_item_ids))
    support_ok = all(item_ok(item) for item in support_items)
    semantic_ok = all(item_ok(item) for item in SEMANTIC_SCREEN_ROW_ITEMS)
    mechanical_ok = item_ok(8) and item_ok(9)

    if not layer_ok("frozen_manifest_integrity") or not layer_ok("access_accounting"):
        base_label = "invalid"
    elif identity_drift:
        base_label = "invalid_identity_drift"
    elif not (
        layer_ok("answerability") and layer_ok("firewall") and layer_ok("gold_adequacy")
    ):
        base_label = "instrument_blocked"
    elif not mechanical_ok:
        base_label = "contract_unstable"
    elif not semantic_ok:
        base_label = "semantic_screen_below_threshold"
    elif not primary_ok:
        base_label = "decision_preservation_below_screen"
    elif split == "development":
        base_label = "development_eligible"
    else:
        base_label = "bounded_model_semantic_compatibility_confirmed"
    if base_label not in OUTCOME_LABELS:  # pragma: no cover - defensive
        raise ScoringMachineryError(f"unknown outcome label {base_label!r}")

    s7_records = {str(item): record.as_record() for item, record in diagnostic_only.items()}
    s7_violation_count = sum(
        int(record.get("violation_count", 0)) for record in s7_records.values()
    )
    label = (
        f"{base_label} (S-7 violations: {s7_violation_count})"
        if s7_violation_count
        else base_label
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "split": split,
        "artifact_classifier": "model_semantic_compatibility_diagnostic",
        "gated_items": sorted(provisional),
        "gated_item_set_is_frozen_literal": sorted(provisional)
        == sorted(
            GATED_DEVELOPMENT_ITEMS
            if split == "development"
            else GATED_CONFIRMATION_ITEMS
        ),
        "diagnostic_only_items": sorted(diagnostic_only),
        "diagnostic_only_items_excluded_from_gates": True,
        "missing_item_ids": missing,
        "failed_item_ids": failed,
        "support_gates_all_met": support_ok,
        "primary_items_all_met": primary_ok,
        "verdict": verdict,
        "base_label": base_label,
        "outcome_label": label,
        "effect_self_consistency": s7_records,
        "s7_violation_count": s7_violation_count,
        "s7_violations_preserved_in_label": s7_violation_count > 0,
        "validity_precedence": precedence,
        "claims_blocked_by": [
            layer
            for layer, value in precedence["layers"].items()
            if value["blocked_by"] is not None
        ],
        "thresholds_are_population_estimates": False,
    }


def eligibility_report(
    items: Mapping[int, Mapping[str, object]],
    *,
    split: str,
    diagnostic_only: Mapping[int, DiagnosticOnly] | None = None,
    primary_item_ids: Sequence[int] = (20, 21),
    gated_items: Iterable[int] | None = None,
    identity_drift: bool = False,
) -> dict:
    """``ELIGIBILITY.json``: each item's observed value and verdict, in order."""

    outcome = evaluate_eligibility(
        items,
        split=split,
        diagnostic_only=diagnostic_only,
        primary_item_ids=primary_item_ids,
        gated_items=gated_items,
        identity_drift=identity_drift,
    )
    outcome["items"] = {
        str(item): dict(record) for item, record in sorted(items.items())
    }
    return outcome


# -- report structures -------------------------------------------------------

DEVELOPMENT_REPORT_SECTIONS = (
    "condition",
    "frozen_inheritance",
    "model_condition",
    "schedule",
    "accounting",
    "eligibility",
    "gates",
    "primary_endpoint",
    "per_source_choice_sets",
    "repeat_agreement",
    "non_primary_metrics",
    "effect_self_consistency",
    "error_propagation",
    "evaluator_only_diagnostic_substitution",
    "outcome",
    "claim_boundary",
)


def build_report(
    sections: Mapping[str, object], *, required: Sequence[str] = DEVELOPMENT_REPORT_SECTIONS
) -> dict:
    """Assemble a report document, refusing to omit a required section."""

    missing = [name for name in required if name not in sections]
    if missing:
        raise ScoringMachineryError(
            "required report sections missing: " + ", ".join(sorted(missing))
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "sections": {name: sections[name] for name in required},
        "claim_boundary": sections.get("claim_boundary"),
    }
