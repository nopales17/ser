#!/usr/bin/env python3
"""Deterministically render SER's readable idea map and portable context packet.

The .yaml sources deliberately use JSON-compatible YAML, so this repository's
knowledge infrastructure requires only the Python standard library.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IDEA_SOURCE = ROOT / "theory" / "IDEA_MAP.yaml"
STATUS_SOURCE = ROOT / "state" / "STATUS.yaml"
IDEA_OUTPUT = ROOT / "theory" / "IDEA_MAP.md"
CONTEXT_OUTPUT = ROOT / "state" / "CONTEXT_PACKET.md"
GENERATED_WARNING = "<!-- GENERATED FILE: DO NOT EDIT. Run `python3 tools/emit_context.py`. -->"

KIND_ORDER = [
    "foundation",
    "primitive",
    "hypothesis",
    "mechanism",
    "empirical_finding",
    "open_question",
]

KIND_LABELS = {
    "foundation": "Foundations",
    "primitive": "Candidate primitives",
    "hypothesis": "Hypotheses",
    "mechanism": "Proposed mechanisms",
    "empirical_finding": "Empirical findings",
    "open_question": "Open questions",
}


def load_json_yaml(path: Path) -> dict:
    """Load the JSON-compatible subset of YAML used by canonical data files."""
    return json.loads(path.read_text(encoding="utf-8"))


def registry() -> dict:
    return load_json_yaml(IDEA_SOURCE)


def status() -> dict:
    return load_json_yaml(STATUS_SOURCE)


def idea_index(data: dict | None = None) -> dict[str, dict]:
    data = data or registry()
    return {item["id"]: item for item in data["ideas"]}


def clean_prose(value: str) -> str:
    return " ".join(value.split())


def display_list(values: list[str]) -> str:
    return ", ".join(f"`{value}`" for value in values) if values else "None recorded."


def markdown_section(path: Path, heading: str) -> str:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL
    )
    match = pattern.search(text)
    if not match:
        raise ValueError(f"missing section {heading!r} in {path.relative_to(ROOT)}")
    return match.group(1).strip()


def parse_decisions() -> list[dict[str, str]]:
    text = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    matches = list(re.finditer(r"^## (ADR-\d{4}) -- (.+)$", text, re.MULTILINE))
    decisions: list[dict[str, str]] = []
    for pos, match in enumerate(matches):
        end = matches[pos + 1].start() if pos + 1 < len(matches) else len(text)
        block = text[match.end() : end]
        fields: dict[str, str] = {
            "id": match.group(1),
            "title": match.group(2).strip(),
        }
        for field in ("Status", "Date", "Decision", "Why", "Alternatives rejected"):
            value_match = re.search(
                rf"^- {re.escape(field)}:\s*(.*?)(?=\n- [A-Z][^:\n]*:|\n## |\Z)",
                block,
                re.MULTILINE | re.DOTALL,
            )
            fields[field.lower().replace(" ", "_")] = (
                clean_prose(value_match.group(1)) if value_match else ""
            )
        decisions.append(fields)
    return decisions


def parse_roadmap() -> list[dict[str, str | int]]:
    text = (ROOT / "plan" / "ROADMAP.md").read_text(encoding="utf-8")
    matches = list(re.finditer(r"^## Phase (\d+) -- (.+)$", text, re.MULTILINE))
    phases: list[dict[str, str | int]] = []
    for pos, match in enumerate(matches):
        end = matches[pos + 1].start() if pos + 1 < len(matches) else len(text)
        block = text[match.end() : end]
        status_match = re.search(r"^- status:\s*(\w+)\s*$", block, re.MULTILINE)
        goal_match = re.search(
            r"^- goal:\s*(.*?)(?=\n- [a-z_]+:|\n## |\Z)",
            block,
            re.MULTILINE | re.DOTALL,
        )
        exit_match = re.search(
            r"^- exit:\s*(.*?)(?=\n- [a-z_]+:|\n## |\Z)",
            block,
            re.MULTILINE | re.DOTALL,
        )
        phases.append(
            {
                "id": int(match.group(1)),
                "title": match.group(2).strip(),
                "status": status_match.group(1) if status_match else "",
                "goal": clean_prose(goal_match.group(1)) if goal_match else "",
                "exit": clean_prose(exit_match.group(1)) if exit_match else "",
            }
        )
    return phases


def render_idea_map(data: dict | None = None) -> str:
    data = data or registry()
    ideas = data["ideas"]
    counts = Counter(item["kind"] for item in ideas)
    lines = [
        GENERATED_WARNING,
        "",
        "# SER idea map",
        "",
        "Readable rendering of canonical `theory/IDEA_MAP.yaml`. Status records maturity; this cold location records authority and preservation, not truth.",
        "",
        f"Schema version: `{data['schema_version']}`. Total entries: **{len(ideas)}**.",
        "",
        "ID families: "
        + "; ".join(f"`{prefix}-*` {meaning}" for prefix, meaning in data["id_convention"].items())
        + ".",
        "",
        "Status vocabulary: " + display_list(data["status_vocabulary"]),
        "",
    ]

    for kind in KIND_ORDER:
        group = [item for item in ideas if item["kind"] == kind]
        lines.extend([f"## {KIND_LABELS[kind]} ({counts[kind]})", ""])
        for item in group:
            lines.extend(
                [
                    f"### `{item['id']}` -- {item['title']}",
                    "",
                    f"- **Status:** `{item['status']}`",
                    f"- **Statement:** {item['statement']}",
                    f"- **Why it matters:** {item['why_it_matters']}",
                    f"- **Depends on:** {display_list(item['depends_on'])}",
                    f"- **Related to:** {display_list(item['related_to'])}",
                    f"- **Would support:** {'; '.join(item['would_support']) if item['would_support'] else 'Not yet specified.'}",
                    f"- **Would falsify:** {'; '.join(item['would_falsify']) if item['would_falsify'] else 'Not yet specified.'}",
                    f"- **Implementation refs:** {display_list(item['implementation_refs'])}",
                    f"- **Evidence refs:** {display_list(item['evidence_refs'])}",
                    f"- **Origin:** {item['origin']}",
                    f"- **Last reviewed:** `{item['last_reviewed']}`",
                    f"- **Notes:** {item['notes'] or 'None.'}",
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"


def context_bullet(item: dict, include_status: bool = True) -> str:
    status_text = f" (`{item['status']}`)" if include_status else ""
    return f"- `{item['id']}` **{item['title']}**{status_text}: {item['statement']}"


def render_context_packet(
    data: dict | None = None, current: dict | None = None
) -> str:
    data = data or registry()
    current = current or status()
    ideas = data["ideas"]
    accepted_decisions = [item for item in parse_decisions() if item["status"] == "accepted"]
    phases = parse_roadmap()
    active = [phase for phase in phases if phase["status"] == "active"]
    if len(active) != 1:
        raise ValueError(f"expected exactly one active roadmap phase, found {len(active)}")
    active_phase = active[0]

    primitives = [item for item in ideas if item["kind"] == "primitive"]
    working_hypotheses = [
        item for item in ideas if item["kind"] == "hypothesis" and item["status"] == "working"
    ]
    speculative = [
        item
        for item in ideas
        if item["status"] == "seed" and item["kind"] in {"primitive", "hypothesis", "mechanism"}
    ]
    working_mechanisms = [
        item for item in ideas if item["kind"] == "mechanism" and item["status"] == "working"
    ]
    open_questions = [item for item in ideas if item["kind"] == "open_question"]
    coupling_ids = {f"M-{number:03d}" for number in range(1, 10)}
    coupling = [item for item in speculative if item["id"] in coupling_ids]
    speculative = [item for item in speculative if item["id"] not in coupling_ids]
    rejected = [item for item in ideas if item["status"] in {"rejected", "deprecated"}]
    findings = [item for item in ideas if item["kind"] == "empirical_finding"]

    investigation = markdown_section(ROOT / "CHARTER.md", "Research boundary")
    # The provisional naming paragraph is useful elsewhere but distracts here.
    investigation = investigation.split("\n\n`SER` provisionally", 1)[0]

    lines = [
        GENERATED_WARNING,
        "",
        "# SER context packet",
        "",
        f"Canonical sources reviewed through `{current['as_of']}`. This is a portable projection, not a source of truth.",
        "",
        "## 1. What SER is trying to investigate",
        "",
        investigation,
        "",
        "The central empirical question is `H-001`: whether allocation organization contributes value beyond total computation. `F-004` makes the burden explicit: fixed, random, exhaustive, token/cost-matched frontier reasoning, and ordinary-agent baselines must be used where relevant.",
        "",
        "## 2. Current maturity / what has actually been built",
        "",
        f"Project maturity is `{current['project_maturity']}`. The durable knowledge architecture exists: canonical idea data, generated readable/context views, an ADR ledger, a single roadmap cursor, and a lightweight coherence checker. Runtime built: **{str(current['runtime']['built']).lower()}**. Controllers: **{current['runtime']['controllers']}**. Environments: **{current['runtime']['environments']}**. Model integrations: **{current['runtime']['model_integrations']}**.",
        "",
        current["evidence"]["summary"],
        "",
        "Do not infer runtime progress from the conceptual inventory. Mechanism entries preserve ideas; they are not code.",
        "",
        "## 3. Settled architectural decisions",
        "",
    ]
    for decision in accepted_decisions:
        lines.append(f"- `{decision['id']}` **{decision['title']}**: {decision['decision']}")

    lines.extend(["", "## 4. Current high-value primitives", ""])
    lines.extend(context_bullet(item) for item in primitives)
    lines.extend(
        [
            "",
            "These are candidate theoretical primitives. No Python class, graph schema, or universal resource conversion is accepted. `P-003` Scope, `H-003` scope-aware allocation, `M-006` SCOPE_FILTER, a future implementation, and experiment evidence are separate objects.",
            "",
            "## 5. Working hypotheses",
            "",
        ]
    )
    lines.extend(context_bullet(item) for item in working_hypotheses)
    lines.extend(
        [
            "",
            "`working` means specified enough for refinement or test design, not experimentally supported. `H-016` is the eventual resource-normalized advantage claim but remains a `seed`.",
            "",
            "## 6. Important speculative/cold ideas worth remembering",
            "",
        ]
    )
    lines.extend(context_bullet(item) for item in speculative)
    lines.extend(context_bullet(item) for item in working_mechanisms)
    if coupling:
        names = ", ".join(f"`{item['id']}` {item['title'].split()[0]}" for item in coupling)
        lines.append(
            f"- Preserved coupling-operator family (`seed`): {names}. Their semantics are unresolved under `Q-006`; names must not be converted into code or theory by guesswork."
        )
    lines.extend(
        [
            "",
            "Cold preservation is deliberate: it prevents intellectual loss without promoting these ideas. Observation/reasoning oscillation rate and depth are trajectory measurements, not fixed constants. Remote sensing, SERT, and TGNN work are late-stage generalization possibilities, not roadmap commitments.",
            "",
            "### Unresolved questions that constrain later work",
            "",
        ]
    )
    lines.extend(context_bullet(item) for item in open_questions)
    lines.extend(
        [
            "",
            "These questions are part of the durable conceptual state. Future work should update their canonical entries with decisions or evidence instead of resolving them only in conversation.",
            "",
            "## 7. Rejected/deprecated ideas",
            "",
        ]
    )
    if rejected:
        lines.extend(context_bullet(item) for item in rejected)
    else:
        lines.append("None. The absence of rejected entries reflects project age, not confirmation of the seeded ideas.")

    lines.extend(["", "## 8. Current experimental evidence", ""])
    lines.append(f"SER evidence records: **{len(current['evidence']['ser_experiments'])}**.")
    for finding in findings:
        lines.append(context_bullet(finding))
        if finding["notes"]:
            lines.append(f"  Limitation: {finding['notes']}")
    lines.append(
        "The IDS finding is historical environment evidence only. It does not support the SER controller, scope-aware gating, sparse propagation, compression, learned policy, or substrate-independence hypotheses."
    )

    lines.extend(
        [
            "",
            "## 9. Current roadmap cursor",
            "",
            f"Active: **Phase {active_phase['id']} -- {active_phase['title']}**. Status: `active`.",
            "",
            f"Goal: {active_phase['goal']}",
            "",
            f"Exit: {active_phase['exit']}",
            "",
            "## 10. Immediate next task",
            "",
            current["roadmap"]["immediate_next_task"],
            "",
            "Keep the work read-only with respect to the IDS archive. The next task does not authorize copying code/data or implementing an adapter or controller.",
            "",
            "## 11. Important non-goals",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in current["non_goals"])
    lines.extend(
        [
            "",
            "Also avoid scientific overclaiming: a cold location is not acceptance, implementation is not evidence, a failed mechanism does not erase its conceptual history, and additional model calls are not architectural success.",
            "",
            "## 12. Canonical documents for deeper context",
            "",
            "- `CHARTER.md`: research boundary, invariants, category distinctions, promotion/demotion, and non-goals.",
            "- `MAP.md`: document ownership and precedence.",
            "- `DECISIONS.md`: append-only accepted ADR history.",
            "- `theory/IDEA_MAP.yaml`: canonical concept identities, statuses, relations, provenance, falsifiers, and references.",
            "- `theory/PRIMITIVES.md`, `theory/HYPOTHESES.md`, and `theory/QUESTIONS.md`: concise conceptual reading aids.",
            "- `plan/ROADMAP.md`: the only authoritative phase cursor.",
            "- `state/STATUS.yaml`: current implementation and evidence facts.",
            "- `reference/IDS_LEGACY.md`: disciplined boundary around historical IDS input.",
            "- `experiments/README.md`: evidence admission rules and current no-experiment state.",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def generated_outputs() -> dict[Path, str]:
    data = registry()
    current = status()
    return {
        IDEA_OUTPUT: render_idea_map(data),
        CONTEXT_OUTPUT: render_context_packet(data, current),
    }


def main() -> int:
    for path, content in generated_outputs().items():
        path.write_text(content, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
