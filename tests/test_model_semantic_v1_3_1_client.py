"""Request-body and response-extraction tests for `model-semantic-v1.3.1-N1`.

Handoff step 4. Every test runs against recorded fixtures with **no network**:
the transport is replaced by an injected ``submitter``.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from types import SimpleNamespace

from ser.authzgym.semantic_contract_v1_3 import (
    SEMANTIC_RETRY_LIMIT,
    STRUCTURAL_RETRY_LIMIT,
    TRANSPORT_REPLAY_LIMIT,
    build_request_body,
    request_bytes,
    request_sha256,
    structural_classification,
)
from ser.authzgym.supervised_transport_v1_3 import (
    CLIENT_SIDE_RETRIES,
    MAX_SUBMISSIONS_PER_LOGICAL_CALL,
    SupervisedSemanticContractClientV13,
)
from ser.authzgym.v1_3_contract import load_public_contract
from ser.core.types import canonical_json


ROOT = Path(__file__).resolve().parents[1]
V13_DIR = ROOT / "experiments" / "authzgym_semantic_contract_v1_3"
DEV_POPULATION = V13_DIR / "DEVELOPMENT_PUBLIC_POPULATION.json"


def fixtures_contract() -> dict:
    return load_public_contract(V13_DIR / "PUBLIC_CONTRACT.json")


def fixtures_case(index: int = 0) -> dict:
    population = json.loads(DEV_POPULATION.read_text(encoding="utf-8"))
    return population["cases"][index]


def fixtures_prompt() -> str:
    return (V13_DIR / "prompts" / "semantic_observation_v1_3.txt").read_text(
        encoding="utf-8"
    )


def fixtures_condition() -> dict:
    return {
        "route_model_identifier": "patchersniper_praneeth/gpt-5.4-nano",
        "reasoning_effort": "none",
        "temperature": None,
        "maximum_output_tokens": 1024,
        "maximum_input_tokens": 4000,
        "request_timeout_seconds": 90,
        "connect_timeout_seconds": 15,
        "hard_spend_ceiling_usd": 2.50,
        "pricing": {
            "input_per_million_tokens_usd": 0.20,
            "cached_input_per_million_tokens_usd": 0.02,
            "output_per_million_tokens_usd": 1.25,
        },
    }


def fixtures_policy() -> SimpleNamespace:
    return SimpleNamespace(
        maximum_api_submissions=384,
        api_probe_path="/models",
        api_probe_connect_timeout_seconds=15,
        api_probe_timeout_seconds=30,
        proxy_dns_mode="socks5h_remote_resolution",
        tls_verification=False,
    )


def fixtures_supervisor() -> SimpleNamespace:
    return SimpleNamespace(proxy_url="socks5h://127.0.0.1:47819", generation=1, port=47819)


def fixtures_valid_response(case: dict, contract: dict) -> dict:
    """A structurally valid response built without any evaluator information."""

    legal = [int(item) for item in case["runner_control"]["legal_target_slots"]]
    return {
        "facts": {slot: False for slot in contract["fact_slots"]},
        "candidate_effects": {slot: "unknown" for slot in contract["candidate_slots"]},
        "unresolved_targets": {
            f"t{slot}": {slot_name: False for slot_name in contract["relation_slots"]}
            for slot in legal
        },
    }


def fixtures_invalid_response(case: dict, contract: dict, *, mode: str) -> dict:
    response = fixtures_valid_response(case, contract)
    if mode == "extra_key":
        response = {**response, "unexpected": True}
    elif mode == "wrong_targets":
        response["unresolved_targets"] = {
            "t99": {slot_name: False for slot_name in contract["relation_slots"]}
        }
    elif mode == "open_value":
        response["candidate_effects"] = {
            slot: ("support" if slot == "c0" else "malformed")
            for slot in contract["candidate_slots"]
        }
    else:  # pragma: no cover - guard
        raise ValueError(mode)
    return response


def fixtures_envelope(
    content: str,
    *,
    finish_reason: str = "stop",
    fingerprint: str = "fp-fixture-1",
    input_tokens: int = 1200,
    output_tokens: int = 200,
) -> dict:
    return {
        "id": "chatcmpl-fixture",
        "object": "chat.completion",
        "model": "patchersniper_praneeth/gpt-5.4-nano",
        "choices": [
            {
                "index": 0,
                "finish_reason": finish_reason,
                "message": {"role": "assistant", "content": content},
            }
        ],
        "system_fingerprint": fingerprint,
        "usage": {
            "prompt_tokens": input_tokens,
            "completion_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "prompt_tokens_details": {"cached_tokens": 0},
            "completion_tokens_details": {"reasoning_tokens": 0},
        },
    }


def fixture_outcome(envelope: dict | None, *, returncode: int = 0) -> dict:
    body = b"" if envelope is None else canonical_json(envelope).encode("utf-8")
    return {
        "http_status": 200 if envelope is not None else 0,
        "curl_returncode": returncode,
        "curl_metadata": {
            "http_status": 200 if envelope is not None else 0,
            "time_connect_seconds": 0.01,
            "time_starttransfer_seconds": 0.2,
            "time_total_seconds": 0.3,
        },
        "latency_ms": 300.0,
        "stderr": "",
        "credential_redacted": False,
        "raw_response_sha256": __import__("hashlib").sha256(body).hexdigest(),
        "raw_response_bytes": len(body),
        "raw_response_text": body.decode("utf-8"),
        "provider_response_received": envelope is not None,
        "transport_failure_class": None if envelope is not None else "timeout",
        "envelope": envelope,
        "provider_usage": {
            "input_tokens": 1200,
            "output_tokens": 200,
            "total_tokens": 1400,
            "cached_input_tokens": 0,
            "reasoning_output_tokens": 0,
            "cost_usd": 0.00049,
        },
    }


class ScriptedSubmitter:
    """A recorded-fixture transport: one outcome per submission."""

    def __init__(self, outcomes: list[dict]) -> None:
        self.outcomes = list(outcomes)
        self.bodies: list[bytes] = []

    def __call__(self, request_body: bytes, *, call_context: dict) -> dict:
        self.bodies.append(bytes(request_body))
        if not self.outcomes:
            raise AssertionError("unexpected extra submission")
        return dict(self.outcomes.pop(0))


def build_client(outcomes: list[dict]):
    attempts: list[dict] = []
    transports: list[dict] = []
    submitter = ScriptedSubmitter(outcomes)
    client = SupervisedSemanticContractClientV13(
        fixtures_condition(),
        fixtures_prompt(),
        fixtures_supervisor(),
        fixtures_policy(),
        attempts.append,
        transports.append,
        environment={
            "OPENAI_BASE_URL": "https://endpoint.invalid/v1",
            "OPENAI_API_KEY": "fixture-key",
        },
        submitter=submitter,
    )
    return client, submitter, attempts, transports


class RequestBodyTests(unittest.TestCase):
    def test_request_body_is_the_frozen_public_payload(self) -> None:
        case = fixtures_case()
        body = build_request_body(case, fixtures_prompt(), fixtures_condition())
        self.assertEqual(body["model"], "patchersniper_praneeth/gpt-5.4-nano")
        self.assertEqual(body["reasoning_effort"], "none")
        self.assertEqual(body["max_completion_tokens"], 1024)
        self.assertEqual(body["response_format"]["json_schema"]["schema"], case["response_schema"])
        self.assertTrue(body["response_format"]["json_schema"]["strict"])
        for forbidden in ("temperature", "top_p", "seed", "stop", "n", "tools"):
            self.assertNotIn(forbidden, body)
        payload = json.loads(body["messages"][1]["content"])
        self.assertEqual(
            sorted(payload),
            sorted(
                [
                    "semantic_interface",
                    "instruction_scope",
                    "current_artifact",
                    "candidate_hypotheses",
                    "public_artifact_inventory",
                    "legal_uninspected_target_slots",
                ]
            ),
        )
        self.assertNotIn("usefulness", body["messages"][1]["content"])
        self.assertNotIn("logical_role", body["messages"][1]["content"])

    def test_request_bytes_are_deterministic_across_attempts(self) -> None:
        case = fixtures_case()
        first = request_bytes(build_request_body(case, fixtures_prompt(), fixtures_condition()))
        second = request_bytes(build_request_body(case, fixtures_prompt(), fixtures_condition()))
        self.assertEqual(first, second)
        self.assertEqual(request_sha256(json.loads(first)), request_sha256(json.loads(second)))

    def test_temperature_override_is_refused(self) -> None:
        condition = fixtures_condition() | {"temperature": 0.0}
        with self.assertRaises(Exception):
            build_request_body(fixtures_case(), fixtures_prompt(), condition)


class ResponseExtractionTests(unittest.TestCase):
    def test_valid_response_is_extracted_with_full_record(self) -> None:
        case = fixtures_case()
        contract = fixtures_contract()
        response = fixtures_valid_response(case, contract)
        envelope = fixtures_envelope(canonical_json(response))
        classification = structural_classification(
            envelope,
            contract=contract,
            legal_target_slots=tuple(case["runner_control"]["legal_target_slots"]),
        )
        self.assertTrue(classification["structurally_valid"])
        self.assertEqual(classification["finish_reason"], "stop")
        self.assertEqual(classification["system_fingerprint"], "fp-fixture-1")
        self.assertEqual(classification["usage"]["input_tokens"], 1200)
        self.assertEqual(classification["response"], response)
        self.assertTrue(classification["response_sha256"])

    def test_length_termination_is_structurally_invalid(self) -> None:
        case = fixtures_case()
        contract = fixtures_contract()
        envelope = fixtures_envelope(
            canonical_json(fixtures_valid_response(case, contract)),
            finish_reason="length",
        )
        classification = structural_classification(
            envelope,
            contract=contract,
            legal_target_slots=tuple(case["runner_control"]["legal_target_slots"]),
        )
        self.assertFalse(classification["structurally_valid"])
        self.assertEqual(classification["failure"], "length_termination")

    def test_extra_key_and_wrong_targets_are_structurally_invalid(self) -> None:
        case = fixtures_case()
        contract = fixtures_contract()
        legal = tuple(case["runner_control"]["legal_target_slots"])
        for mode in ("extra_key", "wrong_targets", "open_value"):
            envelope = fixtures_envelope(
                canonical_json(fixtures_invalid_response(case, contract, mode=mode))
            )
            classification = structural_classification(
                envelope, contract=contract, legal_target_slots=legal
            )
            self.assertFalse(classification["structurally_valid"], mode)

    def test_missing_body_is_classified_without_a_response(self) -> None:
        case = fixtures_case()
        classification = structural_classification(
            None,
            contract=fixtures_contract(),
            legal_target_slots=tuple(case["runner_control"]["legal_target_slots"]),
        )
        self.assertFalse(classification["structurally_valid"])
        self.assertEqual(classification["failure"], "no_provider_response")


class MeasuredResponseTests(unittest.TestCase):
    def test_valid_first_attempt_uses_one_submission(self) -> None:
        case = fixtures_case()
        contract = fixtures_contract()
        response = fixtures_valid_response(case, contract)
        client, submitter, attempts, transports = build_client(
            [fixture_outcome(fixtures_envelope(canonical_json(response)))]
        )
        call = client.invoke_logical_call(case, contract, call_context={"case_id": case["case_id"]})
        self.assertEqual(call["submission_count"], 1)
        self.assertEqual(call["measured_attempt_ordinal"], 1)
        self.assertEqual(call["measured_response"], response)
        self.assertEqual(call["case_classification"], "measured")
        self.assertEqual(len(submitter.bodies), 1)
        self.assertEqual(len(attempts), 1)
        self.assertEqual(len(transports), 1)

    def test_structurally_valid_but_semantically_wrong_is_never_retried(self) -> None:
        case = fixtures_case()
        contract = fixtures_contract()
        wrong = fixtures_valid_response(case, contract)
        # Deliberately wrong: contradicts nothing but asserts an arbitrary
        # relation pattern. It is structurally valid, so it is measured as is.
        wrong["unresolved_targets"][
            f"t{int(case['runner_control']['legal_target_slots'][0])}"
        ] = {slot: True for slot in contract["relation_slots"]}
        client, submitter, attempts, _ = build_client(
            [
                fixture_outcome(fixtures_envelope(canonical_json(wrong))),
                fixture_outcome(fixtures_envelope(canonical_json(wrong))),
            ]
        )
        call = client.invoke_logical_call(case, contract, call_context={"case_id": case["case_id"]})
        self.assertEqual(call["submission_count"], 1)
        self.assertEqual(call["semantic_retries_used"], 0)
        self.assertEqual(call["measured_response"], wrong)
        self.assertEqual(len(submitter.bodies), 1)
        self.assertEqual(len(attempts), 1)
        self.assertEqual(client.client_side_retries, 0)

    def test_frozen_limits_are_the_section_11_2_and_9_5_values(self) -> None:
        self.assertEqual(TRANSPORT_REPLAY_LIMIT, 1)
        self.assertEqual(STRUCTURAL_RETRY_LIMIT, 1)
        self.assertEqual(SEMANTIC_RETRY_LIMIT, 0)
        self.assertEqual(MAX_SUBMISSIONS_PER_LOGICAL_CALL, 2)
        self.assertEqual(CLIENT_SIDE_RETRIES, 0)

    def test_hidden_client_retries_are_zero_and_asserted(self) -> None:
        case = fixtures_case()
        contract = fixtures_contract()
        response = fixtures_valid_response(case, contract)
        client, _, _, _ = build_client(
            [fixture_outcome(fixtures_envelope(canonical_json(response)))]
        )
        call = client.invoke_logical_call(case, contract, call_context={"case_id": case["case_id"]})
        self.assertEqual(call["client_side_retries"], 0)
        self.assertEqual(client.accounting_snapshot()["client_side_retries"], 0)

    def test_every_attempt_is_preserved_with_its_full_record(self) -> None:
        case = fixtures_case()
        contract = fixtures_contract()
        response = fixtures_valid_response(case, contract)
        invalid = fixtures_invalid_response(case, contract, mode="extra_key")
        client, _, attempts, _ = build_client(
            [
                fixture_outcome(fixtures_envelope(canonical_json(invalid))),
                fixture_outcome(fixtures_envelope(canonical_json(response))),
            ]
        )
        call = client.invoke_logical_call(case, contract, call_context={"case_id": case["case_id"]})
        self.assertEqual(len(call["attempts"]), 2)
        self.assertEqual(len(attempts), 2)
        first = call["attempts"][0]
        for field in (
            "attempt_ordinal",
            "request_sha256",
            "raw_response_sha256",
            "http_status",
            "curl_returncode",
            "latency_ms",
            "finish_reason",
            "system_fingerprint",
            "transport_failure_class",
            "structural_failure",
            "discarded_reason",
        ):
            self.assertIn(field, first)
        self.assertEqual(first["discarded_reason"], "structural_retry_used")
        self.assertFalse(first["measured"])


if __name__ == "__main__":
    unittest.main()
