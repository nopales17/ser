#!/usr/bin/env python3
"""Reproduce the offline response-failure autopsy for AuthzGym real-model v1."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import fmean

from ser.authzgym.model import ArtifactDescriptor, SemanticObservation
from ser.authzgym.policies import (
    AuthzEpistemicState,
    select_next_artifact,
    update_state,
)
from ser.authzgym.realmodel import (
    FACT_KEYS,
    MalformedSemanticResponse,
    ProviderError,
    _extract_content,
    parse_semantic_content,
)
from ser.core.types import canonical_json
from ser.evaluation.authz_artifacts import load_population


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/authzgym_static_v1_1"
DEFAULT_INPUT = ROOT / "experiments/authzgym_static_realmodel_v1"
DEFAULT_OUTPUT = ROOT / "experiments/authzgym_semantic_contract_v1_2"

RELATION_TAGS = {
    "ownership_path",
    "alternate_entry",
    "membership_path",
    "membership_inheritance",
    "role_path",
    "role_propagation",
    "context_path",
    "token_scope",
    "general_dependency",
}
TOP_LEVEL_FIELDS = (
    "fact_keys",
    "facts",
    "hypothesis_effects",
    "unresolved_references",
    "uncertainty_flags",
    "recommended_next_artifact_id",
)


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _load_runs(experiment: Path) -> dict[tuple[str, str, str], dict]:
    result = {}
    for name in ("evaluation_runs.jsonl", "perturbation_runs.jsonl"):
        for record in _jsonl(experiment / name):
            public = record["public"]
            result[(public["split"], public["episode_id"], public["architecture"])] = record
    return result


def _load_episodes() -> dict[tuple[str, str], object]:
    result = {}
    for name in ("evaluation_population.json", "perturbation_population.json"):
        episodes, _, _ = load_population(SOURCE / name)
        for episode in episodes:
            result[(episode.split, episode.episode_id)] = episode
    return result


def _selected_ids(step: dict) -> tuple[str, ...]:
    action = step["action"]
    if "artifact_id" in action:
        return (action["artifact_id"],)
    return tuple(action["artifact_ids"])


def _call_inputs(episode, run: dict, step_number: int) -> dict:
    architecture = run["public"]["architecture"]
    inventory = tuple(
        ArtifactDescriptor.from_dict(item)
        for item in episode.public_view()["artifact_inventory"]
    )
    public_inventory = tuple(item.to_dict() for item in inventory)
    state = AuthzEpistemicState.initial(episode.candidates)
    prior_steps = [
        item for item in run["public"]["steps"] if item["step"] < step_number
    ]
    for prior in prior_steps:
        observation = SemanticObservation.from_dict(
            prior["semantic_call"]["parsed_semantic_observation"]
        )
        state = update_state(state, _selected_ids(prior), observation)

    if architecture == "monolithic_semantic":
        selected_ids = tuple(episode.artifact_order[: episode.max_inspections])
        permitted = ()
        recommendation_required = False
        max_output_tokens = 1280
    else:
        available = tuple(
            item.artifact_id
            for item in inventory
            if item.artifact_id not in state.inspected_artifacts
        )
        recorded = next(
            (item for item in run["public"]["steps"] if item["step"] == step_number),
            None,
        )
        if recorded is not None:
            selected_ids = _selected_ids(recorded)
        elif step_number == 1:
            selected_ids = (episode.entry_artifact_id,)
        elif architecture == "react_like_semantic":
            recommendation = prior_steps[-1]["semantic_call"][
                "recommended_next_artifact_id"
            ]
            selected_ids = (recommendation,)
        else:
            target, _, _ = select_next_artifact(
                architecture, state, inventory, episode.candidates
            )
            selected_ids = (target,)
        permitted = tuple(item for item in available if item not in selected_ids)
        recommendation_required = step_number < episode.max_inspections
        max_output_tokens = 320

    artifacts = tuple(episode.artifact(item) for item in selected_ids)
    summary_text = canonical_json(state.to_dict())
    return {
        "candidates": episode.candidates,
        "public_inventory": public_inventory,
        "permitted": permitted,
        "recommendation_required": recommendation_required,
        "max_output_tokens": max_output_tokens,
        "artifact_count": len(artifacts),
        "artifact_line_count": sum(item.descriptor.line_count for item in artifacts),
        "artifact_character_count": sum(len(item.source) for item in artifacts),
        "epistemic_summary_character_count": len(summary_text),
        "epistemic_summary_observation_count": len(state.observations),
    }


def _envelope(record: dict) -> tuple[dict | None, str | None, str | None, dict]:
    transport = record["transport"]
    if transport["returncode"] != 0:
        return None, None, None, {}
    try:
        response = json.loads(record["raw_response_body"])
    except json.JSONDecodeError:
        return None, None, None, {}
    choices = response.get("choices") or []
    first = choices[0] if choices and isinstance(choices[0], dict) else {}
    finish_reason = first.get("finish_reason")
    try:
        content = _extract_content(response)
    except ProviderError:
        content = None
    usage = response.get("usage") if isinstance(response.get("usage"), dict) else {}
    return response, content, finish_reason, usage


def _truncation_field(content: str | None) -> str:
    if not content:
        return "before_content"
    positions = [
        (content.rfind(json.dumps(field)), field) for field in TOP_LEVEL_FIELDS
    ]
    positions = [item for item in positions if item[0] >= 0]
    return max(positions)[1] if positions else "before_first_field"


def _static_overlaps(value: object) -> list[str]:
    if not isinstance(value, dict):
        return ["schema_invalid_json"]
    overlaps = []
    if set(value) != set(TOP_LEVEL_FIELDS):
        overlaps.append("schema_invalid_json")
        return overlaps
    cardinalities = {
        "fact_keys": len(FACT_KEYS),
        "facts": len(FACT_KEYS),
        "hypothesis_effects": 4,
        "unresolved_references": 16,
        "uncertainty_flags": 8,
    }
    for field, maximum in cardinalities.items():
        if isinstance(value[field], list) and len(value[field]) > maximum:
            overlaps.append("excessive_list_cardinality")
    if not isinstance(value["fact_keys"], list) or any(
        not isinstance(item, str) or item not in FACT_KEYS for item in value["fact_keys"]
    ):
        overlaps.append("malformed_enum_or_value")
    if not isinstance(value["facts"], list) or any(
        not isinstance(item, str) for item in value["facts"]
    ):
        overlaps.append("schema_invalid_json")
    if not isinstance(value["uncertainty_flags"], list) or any(
        not isinstance(item, str) for item in value["uncertainty_flags"]
    ):
        overlaps.append("schema_invalid_json")
    return overlaps


def _dynamic_overlaps(value: object, call: dict) -> list[str]:
    if not isinstance(value, dict):
        return []
    overlaps = []
    candidate_ids = {item.hypothesis_id for item in call["candidates"]}
    effects = value.get("hypothesis_effects")
    if isinstance(effects, list):
        seen = set()
        for item in effects:
            if not isinstance(item, dict):
                continue
            hypothesis_id = item.get("hypothesis_id")
            effect = item.get("effect")
            if hypothesis_id not in candidate_ids:
                overlaps.append("illegal_hypothesis_reference")
            if hypothesis_id in seen:
                overlaps.append("duplicate_hypothesis_reference")
            seen.add(hypothesis_id)
            if (
                isinstance(effect, bool)
                or not isinstance(effect, (int, float))
                or not -2.0 <= float(effect) <= 2.0
            ):
                overlaps.append("malformed_enum_or_value")
    public_symbols = {
        symbol
        for item in call["public_inventory"]
        for symbol in item["exported_symbols"]
    }
    references = value.get("unresolved_references")
    if isinstance(references, list):
        seen = set()
        for item in references:
            if not isinstance(item, dict):
                continue
            symbol = item.get("symbol")
            relation = item.get("relation_tag")
            if symbol not in public_symbols:
                overlaps.append("illegal_reference_identifier")
            if relation not in RELATION_TAGS:
                overlaps.append("illegal_relation_identifier")
            pair = (symbol, relation)
            if pair in seen:
                overlaps.append("duplicate_reference")
            seen.add(pair)
    recommendation = value.get("recommended_next_artifact_id")
    if recommendation is not None and recommendation not in call["permitted"]:
        overlaps.append("illegal_artifact_reference")
    if call["recommendation_required"] and recommendation is None:
        overlaps.append("missing_required_artifact_reference")
    return overlaps


def _mean_or_zero(values: list[float]) -> float:
    return fmean(values) if values else 0.0


def _dimension(rows: list[dict], field: str) -> dict:
    grouped = defaultdict(list)
    for row in rows:
        grouped[str(row[field])].append(row)
    return {
        key: {
            "attempts": len(items),
            "invalid_attempts": sum(not item["contract_valid"] for item in items),
            "invalid_rate": _mean_or_zero(
                [float(not item["contract_valid"]) for item in items]
            ),
            "finish_reason_length": sum(
                item["finish_reason"] == "length" for item in items
            ),
            "mean_input_tokens": _mean_or_zero(
                [item["input_tokens"] for item in items]
            ),
            "mean_output_tokens": _mean_or_zero(
                [item["output_tokens"] for item in items]
            ),
            "dominant_root_causes": dict(
                sorted(
                    Counter(
                        item["dominant_root_cause"]
                        for item in items
                        if not item["contract_valid"]
                    ).items()
                )
            ),
        }
        for key, items in sorted(grouped.items())
    }


def analyze(experiment: Path) -> dict:
    episodes = _load_episodes()
    runs = _load_runs(experiment)
    responses = _jsonl(experiment / "provider_responses.jsonl")
    detailed = []
    for record in responses:
        context = record["call_context"]
        key = (context["split"], context["episode_id"], context["architecture"])
        episode = episodes[(context["split"], context["episode_id"])]
        run = runs[key]
        call = _call_inputs(episode, run, int(context["step"]))
        response, content, finish_reason, usage = _envelope(record)
        overlaps = []
        value = None
        parse_error = None
        if record["transport"]["returncode"] != 0:
            overlaps.append("transport_failure")
        elif response is None:
            overlaps.append("provider_envelope_parser_failure")
        elif content is None:
            overlaps.append("provider_envelope_parser_failure")
        else:
            try:
                value = json.loads(content)
            except json.JSONDecodeError:
                overlaps.append("incomplete_or_truncated_json")
            overlaps.extend(_static_overlaps(value) if value is not None else [])
            overlaps.extend(_dynamic_overlaps(value, call))
            try:
                parse_semantic_content(
                    content,
                    call["candidates"],
                    call["public_inventory"],
                    call["permitted"],
                    call["recommendation_required"],
                )
                contract_valid = True
            except (MalformedSemanticResponse, ProviderError) as exc:
                contract_valid = False
                parse_error = f"{type(exc).__name__}:{exc}"
        if content is None:
            contract_valid = False
        if finish_reason == "length":
            overlaps.append("finish_reason_length")
        overlaps = list(dict.fromkeys(overlaps))
        if contract_valid:
            dominant = "valid"
        elif "finish_reason_length" in overlaps:
            dominant = "finish_reason_length"
        elif "incomplete_or_truncated_json" in overlaps:
            dominant = "incomplete_or_truncated_json"
        else:
            priority = (
                "illegal_artifact_reference",
                "illegal_hypothesis_reference",
                "illegal_reference_identifier",
                "illegal_relation_identifier",
                "duplicate_reference",
                "duplicate_hypothesis_reference",
                "missing_required_artifact_reference",
                "excessive_list_cardinality",
                "malformed_enum_or_value",
                "schema_invalid_json",
                "provider_envelope_parser_failure",
                "transport_failure",
            )
            dominant = next((item for item in priority if item in overlaps), "other")
        detailed.append(
            {
                "split": context["split"],
                "architecture": context["architecture"],
                "episode_id": context["episode_id"],
                "step": int(context["step"]),
                "attempt": int(record["attempt"]),
                "retry_status": "retry" if int(record["attempt"]) > 1 else "first_attempt",
                "contract_valid": contract_valid,
                "dominant_root_cause": dominant,
                "overlapping_causes": overlaps,
                "finish_reason": finish_reason,
                "input_tokens": int(usage.get("prompt_tokens", 0) or 0),
                "output_tokens": int(usage.get("completion_tokens", 0) or 0),
                "configured_max_output_tokens": call["max_output_tokens"],
                "artifact_count": call["artifact_count"],
                "artifact_line_count": call["artifact_line_count"],
                "artifact_character_count": call["artifact_character_count"],
                "epistemic_summary_character_count": call[
                    "epistemic_summary_character_count"
                ],
                "epistemic_summary_observation_count": call[
                    "epistemic_summary_observation_count"
                ],
                "truncation_field": _truncation_field(content)
                if not contract_valid
                else None,
                "parse_error": parse_error,
                "raw_response_sha256": record["raw_response_sha256"],
            }
        )

    invalid = [item for item in detailed if not item["contract_valid"]]
    valid = [item for item in detailed if item["contract_valid"]]
    run_records = list(runs.values())
    resource_invalid = [
        item
        for item in run_records
        if item["public"]["invalid_reason"] == "resource_ceiling_or_completeness_failure"
        and "cost_failure" in item["restricted"]["outcome"]["failure_layers"]
    ]
    result = {
        "schema_version": 1,
        "source_experiment": "authzgym-static-realmodel-v1",
        "source_response_attempts": len(detailed),
        "contract_valid_attempts": len(valid),
        "contract_invalid_attempts": len(invalid),
        "dominant_root_causes": dict(
            sorted(Counter(item["dominant_root_cause"] for item in invalid).items())
        ),
        "overlapping_causes": dict(
            sorted(Counter(cause for item in invalid for cause in item["overlapping_causes"]).items())
        ),
        "finish_reason_counts": dict(
            sorted(Counter(str(item["finish_reason"]) for item in detailed).items())
        ),
        "length_finished_but_contract_valid": sum(
            item["finish_reason"] == "length" and item["contract_valid"]
            for item in detailed
        ),
        "truncation_fields": dict(
            sorted(Counter(item["truncation_field"] for item in invalid if item["truncation_field"]).items())
        ),
        "length_truncation_fields": dict(
            sorted(
                Counter(
                    item["truncation_field"]
                    for item in invalid
                    if item["finish_reason"] == "length" and item["truncation_field"]
                ).items()
            )
        ),
        "by_architecture": _dimension(detailed, "architecture"),
        "by_split": _dimension(detailed, "split"),
        "by_retry_status": _dimension(detailed, "retry_status"),
        "by_configured_max_output_tokens": _dimension(
            detailed, "configured_max_output_tokens"
        ),
        "resource_ceiling_violations": {
            "runs": len(resource_invalid),
            "run_ids": [item["public"]["run_id"] for item in resource_invalid],
        },
        "prompt_schema_path": {
            "prompt": "experiments/authzgym_static_realmodel_v1/prompts/semantic_interpretation_v1.txt",
            "schema": "experiments/authzgym_static_realmodel_v1/schemas/semantic_observation_v1.json",
            "distinct_prompt_hashes": sorted(
                {item["public"]["prompt_sha256"] for item in run_records}
            ),
            "distinct_schema_hashes": sorted(
                {item["public"]["schema_sha256"] for item in run_records}
            ),
        },
        "invalid_attempt_ranges": {
            field: {
                "minimum": min(item[field] for item in invalid),
                "maximum": max(item[field] for item in invalid),
                "mean": _mean_or_zero([item[field] for item in invalid]),
            }
            for field in (
                "input_tokens",
                "output_tokens",
                "artifact_line_count",
                "artifact_character_count",
                "epistemic_summary_character_count",
                "epistemic_summary_observation_count",
            )
        },
        "attempts": detailed,
    }
    if len(valid) != 336 or len(invalid) != 273:
        raise ValueError(
            f"autopsy does not reproduce recorded validity: {len(valid)} valid, {len(invalid)} invalid"
        )
    return result


def render_report(value: dict) -> str:
    roots = value["dominant_root_causes"]
    overlaps = value["overlapping_causes"]
    truncation = value["length_truncation_fields"]
    lines = [
        "# AuthzGym real-model v1 offline response autopsy",
        "",
        "This is a read-only reanalysis of the 609 preserved provider attempts. It does not repair, reinterpret, or rerun the invalid experiment.",
        "",
        "## Exact accounting",
        "",
        f"- Attempts: **{value['source_response_attempts']}**.",
        f"- Full-contract valid: **{value['contract_valid_attempts']}**.",
        f"- Full-contract invalid: **{value['contract_invalid_attempts']}**.",
        f"- Run-level provider-token ceiling violations: **{value['resource_ceiling_violations']['runs']}**.",
        "",
        "## Dominant root cause for each invalid attempt",
        "",
        "| Root cause | Attempts |",
        "| --- | ---: |",
    ]
    lines.extend(f"| `{key}` | {count} |" for key, count in roots.items())
    lines += [
        "",
        "## Causally useful overlaps",
        "",
        "| Cause | Invalid attempts |",
        "| --- | ---: |",
    ]
    lines.extend(f"| `{key}` | {count} |" for key, count in overlaps.items())
    lines += [
        "",
        "## Field visible at length termination",
        "",
        "| Last top-level field begun | Invalid attempts |",
        "| --- | ---: |",
    ]
    lines.extend(f"| `{key}` | {count} |" for key, count in truncation.items())
    lines += [
        "",
        "## Conclusions",
        "",
        "1. The 320-token per-artifact ceiling was mechanically insufficient: length termination dominated the invalid attempts and incomplete JSON was its principal overlap.",
        "2. The 1,280-token monolithic ceiling was not mechanically insufficient: none of its 86 attempts ended for length, and observed outputs remained far below the ceiling. Its 68 invalid attempts were dominated by illegal public-symbol references, which more output would not repair.",
        "3. The fields reached at length termination are listed above. The count is derived from the last top-level key begun in each preserved partial response.",
        "4. Valid JSON still failed on model-generated artifact recommendations, public-symbol references, relation tags, and duplicate references. No illegal hypothesis ID was observed. A larger ceiling cannot fix these legality failures.",
        "5. One completed SER run separately exceeded its frozen aggregate provider-token ceiling. A larger per-call ceiling requires a correspondingly explicit run-level resource rule; it is not a parser repair.",
        "",
        "The accompanying JSON retains per-attempt architecture, split, provider-token counts, configured maximum, retry status, artifact size, summary size, finish reason, root cause, overlaps, and response hash without copying response contents.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = analyze(args.input)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "OFFLINE_AUTOPSY.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (args.output / "OFFLINE_AUTOPSY.md").write_text(
        render_report(result), encoding="utf-8"
    )
    print(
        canonical_json(
            {
                "attempts": result["source_response_attempts"],
                "valid": result["contract_valid_attempts"],
                "invalid": result["contract_invalid_attempts"],
                "dominant_root_causes": result["dominant_root_causes"],
            }
        )
    )


if __name__ == "__main__":
    main()
