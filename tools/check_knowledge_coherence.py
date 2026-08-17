#!/usr/bin/env python3
"""Lightweight, read-only coherence checks for SER's knowledge architecture."""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True

import emit_context


ROOT = Path(__file__).resolve().parents[1]
VALID_STATUSES = {
    "seed",
    "working",
    "accepted",
    "experimentally_supported",
    "rejected",
    "deprecated",
}
KIND_PREFIX = {
    "foundation": "F",
    "primitive": "P",
    "hypothesis": "H",
    "mechanism": "M",
    "empirical_finding": "E",
    "open_question": "Q",
}
REQUIRED_IDEA_FIELDS = {
    "id",
    "kind",
    "title",
    "status",
    "statement",
    "why_it_matters",
    "depends_on",
    "related_to",
    "would_support",
    "would_falsify",
    "implementation_refs",
    "evidence_refs",
    "origin",
    "last_reviewed",
    "notes",
}
VALID_LEGACY_CLASSIFICATIONS = {
    "reuse_unchanged",
    "generalize",
    "empirical_evidence_only",
    "inspiration_only",
    "discard",
}
REQUIRED_LEGACY_FIELDS = {
    "id",
    "source_path",
    "component",
    "classification",
    "ser_relevance",
    "related_idea_ids",
    "what_it_does",
    "why_it_might_transfer",
    "why_it_might_not",
    "dependencies",
    "ids_specific_assumptions",
    "tests_or_evidence",
    "recommended_action",
    "confidence",
    "notes",
}
REQUIRED_FILES = {
    "README.md",
    "AGENTS.md",
    "MAP.md",
    "CHARTER.md",
    "DECISIONS.md",
    "theory/PRIMITIVES.md",
    "theory/IDEA_MAP.yaml",
    "theory/IDEA_MAP.md",
    "theory/HYPOTHESES.md",
    "theory/QUESTIONS.md",
    "plan/ROADMAP.md",
    "state/STATUS.yaml",
    "state/CONTEXT_PACKET.md",
    "reference/IDS_LEGACY.md",
    "reference/IDS_LESSONS.md",
    "reference/LEGACY_INVENTORY.yaml",
    "reference/LEGACY_INVENTORY.md",
    "reference/TERMINOLOGY.md",
    "experiments/README.md",
    "tools/emit_context.py",
    "tools/check_knowledge_coherence.py",
}


def result(name: str, ok: bool, detail: str) -> dict[str, object]:
    return {"name": name, "ok": ok, "detail": detail}


def check_required_files() -> dict[str, object]:
    missing = sorted(path for path in REQUIRED_FILES if not (ROOT / path).exists())
    return result(
        "required_files",
        not missing,
        f"missing: {', '.join(missing)}" if missing else f"all {len(REQUIRED_FILES)} canonical files exist",
    )


def load_sources() -> tuple[dict, dict]:
    return emit_context.registry(), emit_context.status()


def check_idea_schema() -> dict[str, object]:
    data, _ = load_sources()
    missing: list[str] = []
    wrong_types: list[str] = []
    for item in data.get("ideas", []):
        idea_id = item.get("id", "<missing-id>")
        absent = sorted(REQUIRED_IDEA_FIELDS - set(item))
        if absent:
            missing.append(f"{idea_id}: {','.join(absent)}")
        for field in ("depends_on", "related_to", "would_support", "would_falsify", "implementation_refs", "evidence_refs"):
            if field in item and not isinstance(item[field], list):
                wrong_types.append(f"{idea_id}.{field}")
    vocabulary_ok = set(data.get("status_vocabulary", [])) == VALID_STATUSES
    ok = not missing and not wrong_types and vocabulary_ok
    details = []
    if missing:
        details.append("missing fields: " + "; ".join(missing[:8]))
    if wrong_types:
        details.append("non-list fields: " + ", ".join(wrong_types[:8]))
    if not vocabulary_ok:
        details.append("canonical status vocabulary differs from checker")
    return result("idea_schema", ok, "; ".join(details) if details else "all entries have the canonical fields and types")


def check_stable_ids() -> dict[str, object]:
    data, _ = load_sources()
    ids = [item.get("id", "") for item in data["ideas"]]
    duplicates = sorted(idea_id for idea_id, count in Counter(ids).items() if count > 1)
    malformed = []
    for item in data["ideas"]:
        idea_id = item.get("id", "")
        kind = item.get("kind", "")
        if not re.fullmatch(r"[FPHMEQ]-\d{3}", idea_id):
            malformed.append(idea_id or "<empty>")
        elif KIND_PREFIX.get(kind) != idea_id[0]:
            malformed.append(f"{idea_id}(kind={kind})")
    ok = not duplicates and not malformed
    detail = []
    if duplicates:
        detail.append("duplicates: " + ", ".join(duplicates))
    if malformed:
        detail.append("malformed/mismatched: " + ", ".join(malformed))
    return result("stable_ids", ok, "; ".join(detail) if detail else f"{len(ids)} unique, well-formed IDs")


def check_id_references() -> dict[str, object]:
    data, _ = load_sources()
    ids = {item["id"] for item in data["ideas"]}
    missing = []
    self_refs = []
    for item in data["ideas"]:
        for field in ("depends_on", "related_to"):
            for target in item[field]:
                if target not in ids:
                    missing.append(f"{item['id']}.{field}->{target}")
                if target == item["id"]:
                    self_refs.append(f"{item['id']}.{field}")
    ok = not missing and not self_refs
    detail = []
    if missing:
        detail.append("missing: " + ", ".join(missing[:12]))
    if self_refs:
        detail.append("self refs: " + ", ".join(self_refs))
    return result("idea_references", ok, "; ".join(detail) if detail else "all relationship IDs exist and no entry self-references")


def check_file_references() -> dict[str, object]:
    data, _ = load_sources()
    missing = []
    for item in data["ideas"]:
        for field in ("implementation_refs", "evidence_refs"):
            for raw in item[field]:
                path = Path(raw)
                resolved = path if path.is_absolute() else ROOT / path
                if not resolved.exists():
                    missing.append(f"{item['id']}.{field}->{raw}")
    return result(
        "file_references",
        not missing,
        "missing: " + ", ".join(missing[:12]) if missing else "all populated implementation/evidence paths exist",
    )


def check_statuses() -> dict[str, object]:
    data, _ = load_sources()
    invalid = [f"{item['id']}={item.get('status')}" for item in data["ideas"] if item.get("status") not in VALID_STATUSES]
    conflicts = [
        item["id"]
        for item in data["ideas"]
        if item.get("status") in {"rejected", "deprecated"} and item.get("accepted") is True
    ]
    ok = not invalid and not conflicts
    detail = []
    if invalid:
        detail.append("invalid: " + ", ".join(invalid))
    if conflicts:
        detail.append("rejected/deprecated also accepted: " + ", ".join(conflicts))
    if not detail:
        detail.append("all statuses valid; single-valued status prevents accepted/rejected overlap")
    return result("maturity_status", ok, "; ".join(detail))


def check_legacy_inventory() -> dict[str, object]:
    data = emit_context.legacy_inventory()
    components = data.get("components", [])
    idea_ids = set(emit_context.idea_index())
    ids = [item.get("id", "") for item in components]
    duplicate_ids = sorted(item for item, count in Counter(ids).items() if count > 1)
    malformed_ids = [item or "<empty>" for item in ids if not re.fullmatch(r"L-\d{3}", item)]
    missing_fields = []
    wrong_types = []
    invalid_classifications = []
    missing_idea_refs = []
    invalid_confidence = []
    for item in components:
        component_id = item.get("id", "<missing-id>")
        absent = sorted(REQUIRED_LEGACY_FIELDS - set(item))
        if absent:
            missing_fields.append(f"{component_id}: {','.join(absent)}")
        for field in ("related_idea_ids", "dependencies", "ids_specific_assumptions", "tests_or_evidence"):
            if field in item and not isinstance(item[field], list):
                wrong_types.append(f"{component_id}.{field}")
        if item.get("classification") not in VALID_LEGACY_CLASSIFICATIONS:
            invalid_classifications.append(f"{component_id}={item.get('classification')}")
        for idea_id in item.get("related_idea_ids", []):
            if idea_id not in idea_ids:
                missing_idea_refs.append(f"{component_id}->{idea_id}")
        if item.get("confidence") not in {"high", "medium", "low"}:
            invalid_confidence.append(f"{component_id}={item.get('confidence')}")

    declared = set(data.get("classification_vocabulary", []))
    counts = Counter(item.get("classification") for item in components)
    conclusion_count = data.get("phase_1_conclusion", {}).get("reuse_unchanged_count")
    reuse_count_ok = conclusion_count == counts["reuse_unchanged"]
    risk_ids = [item.get("id", "") for item in data.get("architectural_contamination_risks", [])]
    risk_ids_ok = (
        bool(risk_ids)
        and len(risk_ids) == len(set(risk_ids))
        and all(re.fullmatch(r"R-\d{3}", item) for item in risk_ids)
    )
    contract_dispositions = {
        "design_from_scratch",
        "define_interface_defer_implementations",
        "generalize_patterns",
        "reuse_legacy_implementation_later",
        "intentionally_defer",
    }
    contract_errors = []
    for index, item in enumerate(data.get("phase_2_contract_recommendations", []), start=1):
        missing = {
            "contract",
            "phase_2_disposition",
            "recommendation",
            "legacy_influence",
            "must_not_assume",
            "related_idea_ids",
        } - set(item)
        if missing:
            contract_errors.append(f"contract {index} missing {','.join(sorted(missing))}")
            continue
        if item["phase_2_disposition"] not in contract_dispositions:
            contract_errors.append(f"{item['contract']} disposition={item['phase_2_disposition']}")
        for idea_id in item["related_idea_ids"]:
            if idea_id not in idea_ids:
                contract_errors.append(f"{item['contract']}->{idea_id}")
    ok = (
        bool(components)
        and declared == VALID_LEGACY_CLASSIFICATIONS
        and not duplicate_ids
        and not malformed_ids
        and not missing_fields
        and not wrong_types
        and not invalid_classifications
        and not missing_idea_refs
        and not invalid_confidence
        and reuse_count_ok
        and risk_ids_ok
        and bool(data.get("symbol_findings"))
        and bool(data.get("phase_2_contract_recommendations"))
        and not contract_errors
    )
    details = []
    if declared != VALID_LEGACY_CLASSIFICATIONS:
        details.append("classification vocabulary differs from checker")
    if duplicate_ids:
        details.append("duplicate IDs: " + ", ".join(duplicate_ids))
    if malformed_ids:
        details.append("malformed IDs: " + ", ".join(malformed_ids))
    if missing_fields:
        details.append("missing fields: " + "; ".join(missing_fields[:8]))
    if wrong_types:
        details.append("wrong types: " + ", ".join(wrong_types[:8]))
    if invalid_classifications:
        details.append("invalid classifications: " + ", ".join(invalid_classifications))
    if missing_idea_refs:
        details.append("missing idea refs: " + ", ".join(missing_idea_refs[:12]))
    if invalid_confidence:
        details.append("invalid confidence: " + ", ".join(invalid_confidence))
    if not reuse_count_ok:
        details.append("conclusion reuse count does not match components")
    if not risk_ids_ok:
        details.append("contamination-risk IDs are missing, duplicate, or malformed")
    if not data.get("symbol_findings"):
        details.append("symbol findings missing")
    if not data.get("phase_2_contract_recommendations"):
        details.append("Phase 2 recommendations missing")
    if contract_errors:
        details.append("Phase 2 contract errors: " + ", ".join(contract_errors[:12]))
    if not details:
        details.append(
            f"{len(components)} unique component IDs; classifications, idea refs, risks, findings, and conclusion are coherent"
        )
    return result("legacy_inventory", ok, "; ".join(details))


def check_legacy_source_references() -> dict[str, object]:
    data = emit_context.legacy_inventory()
    archive = Path(data["archive"]["path"])
    missing = []
    fields = ("source_path", "dependencies", "tests_or_evidence")
    for item in data["components"]:
        for field in fields:
            values = item[field] if isinstance(item[field], list) else [item[field]]
            for raw in values:
                if not (archive / raw).exists():
                    missing.append(f"{item['id']}.{field}->{raw}")
    for item in data["architectural_contamination_risks"]:
        for raw in item["source_refs"]:
            if not (archive / raw).exists():
                missing.append(f"{item['id']}.source_refs->{raw}")
    return result(
        "legacy_source_references",
        not missing,
        "missing: " + ", ".join(missing[:12])
        if missing
        else f"all inventory paths resolve inside read-only archive `{archive}`",
    )


def check_adrs() -> dict[str, object]:
    text = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    heading_ids = re.findall(r"^## (ADR-\d{4}) -- ", text, re.MULTILINE)
    duplicates = sorted(item for item, count in Counter(heading_ids).items() if count > 1)
    decisions = emit_context.parse_decisions()
    incomplete = [
        item["id"]
        for item in decisions
        if not all(item.get(field) for field in ("status", "date", "decision", "why", "alternatives_rejected"))
    ]
    invalid_status = [item["id"] for item in decisions if item["status"] != "accepted"]
    ok = bool(decisions) and not duplicates and not incomplete and not invalid_status
    detail = []
    if not decisions:
        detail.append("no ADRs parsed")
    if duplicates:
        detail.append("duplicates: " + ", ".join(duplicates))
    if incomplete:
        detail.append("incomplete: " + ", ".join(incomplete))
    if invalid_status:
        detail.append("non-accepted ledger entries: " + ", ".join(invalid_status))
    return result("adr_ledger", ok, "; ".join(detail) if detail else f"{len(decisions)} unique accepted ADRs")


def check_roadmap() -> dict[str, object]:
    phases = emit_context.parse_roadmap()
    allowed = {"planned", "active", "done"}
    active = [phase for phase in phases if phase["status"] == "active"]
    invalid = [f"{phase['id']}={phase['status']}" for phase in phases if phase["status"] not in allowed]
    ids = [phase["id"] for phase in phases]
    duplicates = sorted(item for item, count in Counter(ids).items() if count > 1)
    active_index = ids.index(active[0]["id"]) if len(active) == 1 else -1
    order_errors = []
    if active_index >= 0:
        order_errors.extend(
            f"phase {phase['id']} before cursor is {phase['status']}"
            for phase in phases[:active_index]
            if phase["status"] != "done"
        )
        order_errors.extend(
            f"phase {phase['id']} after cursor is {phase['status']}"
            for phase in phases[active_index + 1 :]
            if phase["status"] != "planned"
        )
    ok = bool(phases) and len(active) == 1 and not invalid and not duplicates and not order_errors
    detail = []
    if not phases:
        detail.append("no phases parsed")
    if len(active) != 1:
        detail.append(f"active phases={len(active)}")
    if invalid:
        detail.append("invalid status: " + ", ".join(invalid))
    if duplicates:
        detail.append("duplicate IDs: " + ", ".join(map(str, duplicates)))
    if order_errors:
        detail.append("; ".join(order_errors))
    if not detail:
        detail.append(f"exactly one active phase: {active[0]['id']} -- {active[0]['title']}")
    return result("roadmap_cursor", ok, "; ".join(detail))


def check_status_cursor() -> dict[str, object]:
    _, current = load_sources()
    active = [phase for phase in emit_context.parse_roadmap() if phase["status"] == "active"]
    if len(active) != 1:
        return result("status_cursor", False, "roadmap does not have exactly one active phase")
    phase = active[0]
    status_cursor = current.get("roadmap", {})
    ok = (
        status_cursor.get("active_phase_id") == phase["id"]
        and status_cursor.get("active_phase_title") == phase["title"]
        and bool(status_cursor.get("immediate_next_task"))
    )
    return result(
        "status_cursor",
        ok,
        "STATUS cursor and immediate task match ROADMAP" if ok else f"STATUS={status_cursor!r}, ROADMAP={phase!r}",
    )


def check_generated_markers() -> dict[str, object]:
    bad = []
    for path in (emit_context.IDEA_OUTPUT, emit_context.CONTEXT_OUTPUT, emit_context.LEGACY_OUTPUT):
        if not path.exists() or not path.read_text(encoding="utf-8").startswith(emit_context.GENERATED_WARNING):
            bad.append(str(path.relative_to(ROOT)))
    return result(
        "generated_markers",
        not bad,
        "missing marker: " + ", ".join(bad) if bad else "all generated views identify themselves",
    )


def check_generated_freshness() -> dict[str, object]:
    stale = []
    try:
        expected = emit_context.generated_outputs()
    except Exception as exc:  # provide a coherent failure instead of a traceback
        return result("generated_freshness", False, f"renderer failed: {exc}")
    for path, content in expected.items():
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            stale.append(str(path.relative_to(ROOT)))
    return result(
        "generated_freshness",
        not stale,
        "stale: " + ", ".join(stale) if stale else "generated views exactly match current canonical sources",
    )


def check_context_size() -> dict[str, object]:
    path = emit_context.CONTEXT_OUTPUT
    if not path.exists():
        return result("context_size", False, "context packet missing")
    words = len(re.findall(r"\b[\w'-]+\b", path.read_text(encoding="utf-8")))
    ok = 1200 <= words <= 4000
    return result(
        "context_size",
        ok,
        f"{words} words (required guardrail 1,200-4,000; target approximately 2,000-4,000)",
    )


CHECKS = [
    check_required_files,
    check_idea_schema,
    check_stable_ids,
    check_id_references,
    check_file_references,
    check_statuses,
    check_legacy_inventory,
    check_legacy_source_references,
    check_adrs,
    check_roadmap,
    check_status_cursor,
    check_generated_markers,
    check_generated_freshness,
    check_context_size,
]


def main() -> int:
    results = []
    for check in CHECKS:
        try:
            results.append(check())
        except Exception as exc:
            results.append(result(check.__name__.removeprefix("check_"), False, f"checker error: {exc}"))
    failures = [item for item in results if not item["ok"]]
    print("SER knowledge coherence check")
    print(f"Status: {'FAIL' if failures else 'PASS'} ({len(results)} checks, {len(failures)} failing)")
    print()
    for item in results:
        print(f"[{'PASS' if item['ok'] else 'FAIL'}] {item['name']}: {item['detail']}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
