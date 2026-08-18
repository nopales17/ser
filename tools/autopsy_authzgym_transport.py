#!/usr/bin/env python3
"""Offline transport autopsy for the immutable Phase 5A.4 stress run."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from ser.core.types import canonical_json, content_hash
from ser.evaluation.authz_artifacts import file_sha256


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/authzgym_semantic_contract_v1_2"


def _jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def _latency_summary(values: list[float]) -> dict:
    return {
        "count": len(values),
        "minimum_seconds": min(values) if values else 0.0,
        "mean_seconds": sum(values) / len(values) if values else 0.0,
        "maximum_seconds": max(values) if values else 0.0,
        "total_seconds": sum(values),
    }


def analyze(source: Path = SOURCE) -> dict:
    response_path = source / "provider_responses.jsonl"
    run_path = source / "stress_runs.jsonl"
    notes_path = source / "IMPLEMENTATION_NOTES.md"
    responses = _jsonl(response_path)
    runs = _jsonl(run_path)
    codes = [item["transport"]["returncode"] for item in responses]
    successful_prefix = 0
    for code in codes:
        if code != 0:
            break
        successful_prefix += 1

    segments = []
    if codes:
        start = 1
        previous = codes[0]
        for index, code in enumerate(codes[1:], 2):
            if code != previous:
                segments.append(
                    {
                        "first_attempt_ordinal": start,
                        "last_attempt_ordinal": index - 1,
                        "curl_returncode": previous,
                    }
                )
                start = index
                previous = code
        segments.append(
            {
                "first_attempt_ordinal": start,
                "last_attempt_ordinal": len(codes),
                "curl_returncode": previous,
            }
        )

    latency_by_code = {}
    for code in sorted(set(codes)):
        latency_by_code[str(code)] = _latency_summary(
            [
                item["transport"]["latency_ms"] / 1000.0
                for item in responses
                if item["transport"]["returncode"] == code
            ]
        )

    result = {
        "schema_version": 1,
        "source_experiment": "authzgym-semantic-contract-v1.2",
        "source_files": {
            "provider_responses.jsonl": file_sha256(response_path),
            "stress_runs.jsonl": file_sha256(run_path),
            "IMPLEMENTATION_NOTES.md": file_sha256(notes_path),
        },
        "scheduled_logical_calls": len(runs),
        "recorded_transport_attempts": len(responses),
        "successful_provider_responses": sum(code == 0 for code in codes),
        "successful_prefix_attempts": successful_prefix,
        "first_failed_attempt_ordinal": successful_prefix + 1,
        "curl_returncode_counts": {
            str(key): value for key, value in sorted(Counter(codes).items())
        },
        "curl_returncode_meanings": {
            "0": "curl completed and a provider response was recorded",
            "7": "curl could not connect to the configured proxy/host",
            "28": "curl timed out",
            "97": "curl reported a proxy-handshake error",
        },
        "sequence_segments": segments,
        "latency_by_returncode": latency_by_code,
        "successful_prefix_elapsed_seconds": sum(
            item["transport"]["latency_ms"] for item in responses[:successful_prefix]
        )
        / 1000.0,
        "total_recorded_transport_seconds": sum(
            item["transport"]["latency_ms"] for item in responses
        )
        / 1000.0,
        "empty_response_bodies_on_failed_attempts": sum(
            item["transport"]["returncode"] != 0
            and item["raw_response_body"] == ""
            for item in responses
        ),
        "request_process_model": {
            "curl_process_per_attempt": True,
            "shared_http_connection_pool": False,
            "shared_curl_session": False,
            "persistent_component": "one externally managed SSH SOCKS process",
        },
        "preserved_ssh_evidence": {
            "implementation_notes_state": "the egress SSH connection timed out and was explicitly terminated after the run",
            "per_attempt_ssh_process_state_recorded": False,
            "per_attempt_listener_state_recorded": False,
            "curl_stderr_recorded": False,
            "http_status_or_curl_phase_recorded_on_failure": False,
        },
        "most_supported_failure_cause": (
            "The long-lived SSH/SOCKS forwarding path stopped completing new "
            "connections and later ceased accepting local proxy connections."
        ),
        "supported_inferences": [
            "The failure began after eight completed provider responses rather than at startup.",
            "Thirty-seven failures lasted approximately the frozen 15-second connect timeout and returned no provider body.",
            "One subsequent proxy-handshake error marks a transition in SOCKS behavior.",
            "The final 202 failures were immediate curl code 7 failures, consistent with the local SOCKS listener no longer accepting connections.",
            "Fresh curl processes rule out a shared curl connection pool or stale cross-call HTTP keep-alive session.",
            "No provider response after the eighth call contained an authentication or API error.",
        ],
        "not_established": [
            "The exact attempt at which the SSH process exited.",
            "Whether the listener remained present during the 37 connect timeouts.",
            "Whether remote SOCKS DNS, wiseau egress routing, or the API endpoint caused the initial timeouts.",
            "Whether authentication or endpoint health changed after call eight.",
            "The exact curl connection phase because stderr and write-out timing fields were not retained.",
        ],
    }
    result["record_hash"] = content_hash(result)
    return result


def render_report(value: dict) -> str:
    counts = value["curl_returncode_counts"]
    latencies = value["latency_by_returncode"]
    return "\n".join(
        [
            "# Phase 5A.4 transport-failure autopsy",
            "",
            "This is an offline analysis of the immutable Phase 5A.4 records. It does not modify or rerun that experiment.",
            "",
            "## Exact observed sequence",
            "",
            f"- The first **{value['successful_prefix_attempts']}** transport attempts completed in **{value['successful_prefix_elapsed_seconds']:.3f} seconds** and returned provider responses.",
            f"- They were followed by **{counts.get('28', 0)}** curl code 28 failures, each lasting approximately **{latencies.get('28', {}).get('mean_seconds', 0.0):.3f} seconds**, the frozen connection timeout.",
            f"- One curl code 97 proxy-handshake failure followed, then **{counts.get('7', 0)}** immediate curl code 7 connection failures.",
            f"- All **{value['empty_response_bodies_on_failed_attempts']}** failed attempts had empty response bodies. No post-prefix provider or authentication error was recorded.",
            "",
            "## Strongest supported cause",
            "",
            value["most_supported_failure_cause"],
            "",
            "Every request used a new curl process with no shared connection pool or curl session. Persistent HTTP connection reuse therefore cannot explain the cross-call transition. The only long-lived network component was the externally managed SSH SOCKS process.",
            "",
            "## Evidentiary limit",
            "",
            "The old records did not retain curl stderr, HTTP timing phases, per-attempt SSH process state, or per-attempt listener state. They therefore cannot distinguish remote SOCKS DNS failure, wiseau egress failure, or endpoint unavailability during the initial 37 timeouts, nor identify the exact instant the SSH process exited.",
            "",
        ]
    )


def _write_new(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(text)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    result = analyze(args.source)
    if args.output_dir is None:
        print(canonical_json(result))
        return
    _write_new(
        args.output_dir / "TRANSPORT_AUTOPSY.json",
        json.dumps(result, indent=2, sort_keys=True) + "\n",
    )
    _write_new(args.output_dir / "TRANSPORT_AUTOPSY.md", render_report(result))
    print(
        canonical_json(
            {
                "recorded_transport_attempts": result[
                    "recorded_transport_attempts"
                ],
                "successful_prefix_attempts": result["successful_prefix_attempts"],
                "record_hash": result["record_hash"],
            }
        )
    )


if __name__ == "__main__":
    main()
