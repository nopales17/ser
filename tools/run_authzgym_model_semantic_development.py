#!/usr/bin/env python3
"""Development runner for condition `model-semantic-v1.3.1-N1` (handoff step 7).

**Not executed by the step-6 freeze pass.** This module exists at the freeze
boundary because preregistration section 18 requires the condition's own runner
to be present and hash-frozen before any model call.

Contract:

* the frozen ``FROZEN_INPUTS_MODEL_V1_3_1.json`` manifest is verified before the
  first call and after the final call, and a mismatch is a blocking stop;
* the schedule is exactly ``DEVELOPMENT_SCHEDULE.json``: source-manifest order,
  then the seven variants, then repeat 1 then repeat 2 -- 112 logical calls;
* after every submission the attempt record is appended, the accumulated cost is
  recomputed from provider-reported usage at the verified tariff, and the spend
  ledger is appended; a submission that would carry the total past ``$2.50`` is
  refused;
* ``system_fingerprint`` is compared against ``observed_fingerprint_first``; a
  change stops the run and preserves everything;
* there is no futility stop and no semantic retry.

``--dry-run`` (default) verifies the freeze, resolves the schedule and prints
the plan without making any call. ``--execute`` performs the 112 calls and is
only appropriate after a separate Step-7 inference authorization.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from ser.authzgym.supervised_transport_v1_3 import (  # noqa: E402
    SupervisedSemanticContractClientV13,
)
from ser.authzgym.tunnel_supervisor import TunnelSupervisor  # noqa: E402
from ser.authzgym.v1_3_contract import load_public_contract  # noqa: E402
from ser.core.types import canonical_json  # noqa: E402
from ser.evaluation.authz_model_semantic_v1_3_1 import (  # noqa: E402
    CONDITION_DIR,
    V13_DIR,
    AuditedReader,
    relative_path,
)


CONDITION_ID = "model-semantic-v1.3.1-N1"
AUTHORIZING_ADR = "ADR-0023"
TOOL_PATH = Path(__file__).resolve()
MANIFEST_PATH = CONDITION_DIR / "FROZEN_INPUTS_MODEL_V1_3_1.json"
MODEL_CONDITION_PATH = CONDITION_DIR / "MODEL_CONDITION.json"
FREEZE_CHECKLIST_PATH = CONDITION_DIR / "FREEZE_CHECKLIST.md"
DEVELOPMENT_DIR = CONDITION_DIR / "development"
ACCESS_LEDGER_PATH = CONDITION_DIR / "DEVELOPMENT_ACCESS_LEDGER.jsonl"
ATTEMPTS_PATH = DEVELOPMENT_DIR / "attempts.jsonl"
RESPONSES_PATH = DEVELOPMENT_DIR / "responses.jsonl"
SPEND_LEDGER_PATH = DEVELOPMENT_DIR / "spend_ledger.jsonl"
TRANSPORT_EVENTS_PATH = DEVELOPMENT_DIR / "transport_events.jsonl"
STOP_PATH = CONDITION_DIR / "DEVELOPMENT_STOP.json"
SCHEDULE_PATH = V13_DIR / "DEVELOPMENT_SCHEDULE.json"
POPULATION_PATH = V13_DIR / "DEVELOPMENT_PUBLIC_POPULATION.json"
TRANSPORT_CONFIG_PATH = (
    ROOT / "experiments" / "authzgym_transport_envelope_v1" / "transport_config.json"
)
EXPECTED_LOGICAL_CALLS = 112
DEVELOPMENT_AUTHORIZATION = (
    "ADR-0023 sections 14.1 and D5/D9; PREREGISTRATION.md sections 7, 11 and 12; "
    "IMPLEMENTATION_HANDOFF.md step 7"
)


class DevelopmentRunError(RuntimeError):
    """A preregistration section-11.5 stop condition fired."""


def _append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def _file_sha256(path: Path) -> str:
    from ser.evaluation.authz_model_semantic_v1_3_1 import file_sha256

    return file_sha256(path)


def manifest_verification() -> dict:
    """Re-verify every hashed file the freeze manifest lists."""

    if not MANIFEST_PATH.is_file():
        raise DevelopmentRunError("frozen inputs manifest is absent")
    reader = AuditedReader(
        actor="implementation_agent",
        stage="development_manifest_verification",
        tool_path=TOOL_PATH,
        authorization=DEVELOPMENT_AUTHORIZATION,
        ledger_path=ACCESS_LEDGER_PATH,
    )
    manifest = reader.read_json(
        MANIFEST_PATH, detail="frozen inputs manifest verification"
    )
    mismatches = []
    missing = []
    checked = 0
    for name, expected in manifest.get("files", {}).items():
        path = ROOT / name
        if not path.is_file():
            missing.append(name)
            continue
        checked += 1
        if _file_sha256(path) != expected:
            mismatches.append(name)
    recorded_manifest_sha256 = manifest.get("manifest_sha256", "")
    without = {
        key: value for key, value in manifest.items() if key != "manifest_sha256"
    }
    recomputed = hashlib.sha256(
        json.dumps(without, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "manifest_path": relative_path(MANIFEST_PATH),
        "manifest_file_sha256": _file_sha256(MANIFEST_PATH),
        "manifest_sha256_recorded": recorded_manifest_sha256,
        "manifest_sha256_recomputed": recomputed,
        "manifest_sha256_matches": recorded_manifest_sha256 == recomputed,
        "checked_file_count": checked,
        "mismatches": mismatches,
        "missing": missing,
        "matches": not mismatches
        and not missing
        and recorded_manifest_sha256 == recomputed,
    }


def development_plan() -> dict:
    reader = AuditedReader(
        actor="implementation_agent",
        stage="development_plan",
        tool_path=TOOL_PATH,
        authorization=DEVELOPMENT_AUTHORIZATION,
        ledger_path=ACCESS_LEDGER_PATH,
    )
    schedule = reader.read_json(SCHEDULE_PATH, detail="frozen development schedule")
    population = reader.read_json(POPULATION_PATH, detail="frozen development population")
    reader.read_json(MODEL_CONDITION_PATH, detail="frozen model condition")
    if not FREEZE_CHECKLIST_PATH.is_file():
        raise DevelopmentRunError("freeze checklist is absent")
    entries = schedule["schedule"]
    if len(entries) != EXPECTED_LOGICAL_CALLS:
        raise DevelopmentRunError(
            f"schedule has {len(entries)} logical calls, not {EXPECTED_LOGICAL_CALLS}"
        )
    order = [str(item["case_id"]) for item in entries]
    cases = {str(case["case_id"]): case for case in population["cases"]}
    if set(order) != set(cases):
        raise DevelopmentRunError("schedule and population disagree")
    repeats = [int(item["repeat"]) for item in entries]
    return {
        "logical_calls": len(entries),
        "population_case_count": len(cases),
        "repeat_1_calls": repeats.count(1),
        "repeat_2_calls": repeats.count(2),
        "first_entry": entries[0],
        "last_entry": entries[-1],
        "cases": cases,
        "entries": entries,
    }


def _write_stop(name: str, detail: dict) -> dict:
    record = {
        "schema_version": 1,
        "condition_id": CONDITION_ID,
        "authorizing_adr": AUTHORIZING_ADR,
        "stage": "development_inference",
        "blocker": name,
        "detail": detail,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "preserved": True,
    }
    STOP_PATH.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return record


def execute() -> dict:
    """The 112-call development schedule. Requires the step-7 authorization."""

    plan = development_plan()
    verification_before = manifest_verification()
    if not verification_before["matches"]:
        raise DevelopmentRunError("frozen manifest mismatch before call 1")

    reader = AuditedReader(
        actor="implementation_agent",
        stage="development_inference",
        tool_path=TOOL_PATH,
        authorization=DEVELOPMENT_AUTHORIZATION,
        ledger_path=ACCESS_LEDGER_PATH,
    )
    model_condition = reader.read_json(
        MODEL_CONDITION_PATH, detail="frozen model condition"
    )
    transport_config = reader.read_json(
        TRANSPORT_CONFIG_PATH, detail="supervised egress hop policy"
    )
    from ser.authzgym.tunnel_supervisor import TunnelPolicy

    policy = TunnelPolicy.from_dict(transport_config)
    contract = load_public_contract(V13_DIR / "PUBLIC_CONTRACT.json")
    prompt = reader.read_text(
        V13_DIR / "prompts" / "semantic_observation_v1_3.txt",
        detail="frozen prompt (byte-unchanged)",
    )

    state = {
        "submissions": 0,
        "accumulated_cost_usd": 0.0,
        "observed_fingerprint_first": "",
        "measured_calls": 0,
        "malformed_or_missing_calls": 0,
    }

    def attempt_sink(record: dict) -> None:
        _append_jsonl(ATTEMPTS_PATH, record)

    def transport_sink(record: dict) -> None:
        _append_jsonl(TRANSPORT_EVENTS_PATH, record)
        usage = record.get("provider_usage") or {}
        state["submissions"] += 1
        state["accumulated_cost_usd"] += float(usage.get("cost_usd", 0.0))
        _append_jsonl(
            SPEND_LEDGER_PATH,
            {
                "schema_version": 1,
                "condition_id": CONDITION_ID,
                "api_submission_ordinal": record.get("api_submission_ordinal"),
                "attempt_ordinal": record.get("attempt_ordinal"),
                "case_id": (record.get("call_context") or {}).get("case_id"),
                "repeat": (record.get("call_context") or {}).get("repeat"),
                "usage": usage,
                "accumulated_cost_usd": round(state["accumulated_cost_usd"], 12),
                "hard_spend_ceiling_usd": float(
                    model_condition["hard_spend_ceiling_usd"]
                ),
                "within_ceiling": state["accumulated_cost_usd"]
                <= float(model_condition["hard_spend_ceiling_usd"]),
            },
        )
        if state["accumulated_cost_usd"] > float(
            model_condition["hard_spend_ceiling_usd"]
        ):
            raise DevelopmentRunError("accumulated spend passed the hard ceiling")

    supervisor = TunnelSupervisor(
        policy, lambda item: _append_jsonl(TRANSPORT_EVENTS_PATH, item)
    )
    client = SupervisedSemanticContractClientV13(
        model_condition,
        prompt,
        supervisor,
        policy,
        attempt_sink,
        transport_sink,
    )
    supervisor.establish(client.connectivity_probe, reason="development_startup")
    try:
        for ordinal, entry in enumerate(plan["entries"], start=1):
            case = plan["cases"][str(entry["case_id"])]
            context = {
                "condition_id": CONDITION_ID,
                "schedule_ordinal": ordinal,
                "case_id": str(entry["case_id"]),
                "repeat": int(entry["repeat"]),
                "variant": str(case["variant"]),
                "source_episode_id": str(case["source_episode_id"]),
            }
            supervisor.ensure_live(client.connectivity_probe)
            call = client.invoke_logical_call(case, contract, call_context=context)
            _append_jsonl(
                RESPONSES_PATH,
                {
                    "schema_version": 1,
                    "condition_id": CONDITION_ID,
                    "schedule_ordinal": ordinal,
                    "case_id": call["case_id"],
                    "repeat": int(entry["repeat"]),
                    "request_sha256": call["request_sha256"],
                    "submission_count": call["submission_count"],
                    "measured_attempt_ordinal": call["measured_attempt_ordinal"],
                    "measured_response_sha256": call["measured_response_sha256"],
                    "case_classification": call["case_classification"],
                    "measured_response": call["measured_response"],
                    "system_fingerprint": next(
                        (
                            item["system_fingerprint"]
                            for item in call["attempts"]
                            if item["system_fingerprint"]
                        ),
                        "",
                    ),
                },
            )
            if call["measured_response"] is None:
                state["malformed_or_missing_calls"] += 1
            else:
                state["measured_calls"] += 1
            fingerprint = next(
                (
                    item["system_fingerprint"]
                    for item in call["attempts"]
                    if item["system_fingerprint"]
                ),
                "",
            )
            if fingerprint:
                if not state["observed_fingerprint_first"]:
                    state["observed_fingerprint_first"] = fingerprint
                elif fingerprint != state["observed_fingerprint_first"]:
                    _write_stop(
                        "identity_drift",
                        {
                            "observed_fingerprint_first": state[
                                "observed_fingerprint_first"
                            ],
                            "observed_fingerprint_current": fingerprint,
                            "schedule_ordinal": ordinal,
                            "attempts_preserved": True,
                        },
                    )
                    raise DevelopmentRunError("observed fingerprint changed mid-condition")
    finally:
        supervisor.stop(reason="development_complete")

    verification_after = manifest_verification()
    if not verification_after["matches"]:
        _write_stop("frozen_manifest_drift", verification_after)
        raise DevelopmentRunError("frozen manifest mismatch after the final call")
    return {
        "logical_calls": len(plan["entries"]),
        "submissions": state["submissions"],
        "measured_calls": state["measured_calls"],
        "malformed_or_missing_calls": state["malformed_or_missing_calls"],
        "accumulated_cost_usd": round(state["accumulated_cost_usd"], 12),
        "observed_fingerprint_first": state["observed_fingerprint_first"],
        "manifest_before": verification_before,
        "manifest_after": verification_after,
        "client_accounting": client.accounting_snapshot(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    verification = manifest_verification()
    if not args.execute:
        plan = development_plan()
        print(
            canonical_json(
                {
                    "mode": "dry_run",
                    "manifest_verification": verification,
                    "logical_calls": plan["logical_calls"],
                    "repeat_1_calls": plan["repeat_1_calls"],
                    "repeat_2_calls": plan["repeat_2_calls"],
                    "first_entry": plan["first_entry"],
                    "last_entry": plan["last_entry"],
                    "model_calls": 0,
                }
            )
        )
        return 0
    print(canonical_json(execute()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
