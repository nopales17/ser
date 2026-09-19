"""Retry-state-machine tests for `model-semantic-v1.3.1-N1`.

Handoff step 4: the eight frozen behaviours, all against recorded fixtures with
no network. Test 4 of the handoff's list -- "structurally valid but semantically
wrong -> exactly one submission" -- is the one that encodes the frozen rule and
is asserted here again independently of the client test module.
"""

from __future__ import annotations

import unittest

from ser.authzgym.semantic_contract_v1_3 import request_sha256
from ser.authzgym.v1_3_contract import parse_response
from ser.core.types import canonical_json
from tests.test_model_semantic_v1_3_1_client import (
    build_client,
    fixture_outcome,
    fixtures_case,
    fixtures_contract,
    fixtures_envelope,
    fixtures_invalid_response,
    fixtures_valid_response,
)


def _call(outcomes, *, case=None, contract=None):
    case = case or fixtures_case()
    contract = contract or fixtures_contract()
    client, submitter, attempts, transports = build_client(outcomes)
    result = client.invoke_logical_call(
        case, contract, call_context={"case_id": case["case_id"], "repeat": 1}
    )
    return result, submitter, attempts, transports, client


class RetryStateMachineTests(unittest.TestCase):
    def test_transport_failure_then_valid_uses_two_submissions(self) -> None:
        case, contract = fixtures_case(), fixtures_contract()
        response = fixtures_valid_response(case, contract)
        call, submitter, attempts, _, client = _call(
            [
                fixture_outcome(None, returncode=28),
                fixture_outcome(fixtures_envelope(canonical_json(response))),
            ]
        )
        self.assertEqual(call["submission_count"], 2)
        self.assertEqual(call["transport_replays_used"], 1)
        self.assertEqual(call["structural_retries_used"], 0)
        self.assertEqual(call["measured_attempt_ordinal"], 2)
        self.assertEqual(call["measured_response"], response)
        self.assertEqual(call["case_classification"], "measured")
        self.assertEqual(call["attempts"][0]["transport_failure_class"], "timeout")
        self.assertEqual(call["attempts"][0]["discarded_reason"], "transport_replay_used")
        self.assertEqual(client.accounting_snapshot()["transport_failures"], 1)
        self.assertEqual(len(submitter.bodies), 2)

    def test_structurally_invalid_then_valid_uses_two_submissions(self) -> None:
        case, contract = fixtures_case(), fixtures_contract()
        response = fixtures_valid_response(case, contract)
        invalid = fixtures_invalid_response(case, contract, mode="extra_key")
        call, submitter, _, _, _ = _call(
            [
                fixture_outcome(fixtures_envelope(canonical_json(invalid))),
                fixture_outcome(fixtures_envelope(canonical_json(response))),
            ]
        )
        self.assertEqual(call["submission_count"], 2)
        self.assertEqual(call["structural_retries_used"], 1)
        self.assertEqual(call["transport_replays_used"], 0)
        self.assertEqual(call["measured_attempt_ordinal"], 2)
        self.assertEqual(call["attempts"][0]["structural_failure"], "top_level_shape")
        self.assertEqual(len(submitter.bodies), 2)

    def test_structurally_valid_but_wrong_never_retries(self) -> None:
        case, contract = fixtures_case(), fixtures_contract()
        wrong = fixtures_valid_response(case, contract)
        wrong["facts"]["f0"] = True
        call, submitter, attempts, _, client = _call(
            [
                fixture_outcome(fixtures_envelope(canonical_json(wrong))),
                fixture_outcome(fixtures_envelope(canonical_json(wrong))),
            ]
        )
        self.assertEqual(call["submission_count"], 1)
        self.assertEqual(call["semantic_retries_used"], 0)
        self.assertEqual(call["measured_attempt_ordinal"], 1)
        self.assertEqual(call["measured_response"], wrong)
        self.assertEqual(len(submitter.bodies), 1)
        self.assertEqual(len(attempts), 1)
        self.assertEqual(client.accounting_snapshot()["submissions"], 1)

    def test_invalid_then_invalid_stops_at_two_and_records_malformed(self) -> None:
        case, contract = fixtures_case(), fixtures_contract()
        invalid = fixtures_invalid_response(case, contract, mode="wrong_targets")
        call, submitter, attempts, _, _ = _call(
            [
                fixture_outcome(fixtures_envelope(canonical_json(invalid))),
                fixture_outcome(fixtures_envelope(canonical_json(invalid))),
            ]
        )
        self.assertEqual(call["submission_count"], 2)
        self.assertEqual(call["measured_attempt_ordinal"], None)
        self.assertEqual(call["measured_response"], None)
        self.assertEqual(call["case_classification"], "malformed_or_missing")
        self.assertEqual(len(submitter.bodies), 2)
        self.assertEqual(len(attempts), 2)
        self.assertEqual(
            call["attempts"][1]["discarded_reason"], "structural_retry_exhausted"
        )

    def test_transport_failure_then_transport_failure_stops_at_two(self) -> None:
        call, submitter, _, _, _ = _call(
            [
                fixture_outcome(None, returncode=7),
                fixture_outcome(None, returncode=7),
            ]
        )
        self.assertEqual(call["submission_count"], 2)
        self.assertEqual(call["case_classification"], "malformed_or_missing")
        self.assertEqual(
            call["attempts"][1]["discarded_reason"], "transport_replay_exhausted"
        )
        self.assertEqual(len(submitter.bodies), 2)

    def test_request_bytes_identical_across_attempts(self) -> None:
        case, contract = fixtures_case(), fixtures_contract()
        response = fixtures_valid_response(case, contract)
        invalid = fixtures_invalid_response(case, contract, mode="extra_key")
        call, submitter, _, _, _ = _call(
            [
                fixture_outcome(fixtures_envelope(canonical_json(invalid))),
                fixture_outcome(fixtures_envelope(canonical_json(response))),
            ]
        )
        hashes = {request_sha256(_as_body(item)) for item in submitter.bodies}
        self.assertEqual(len(hashes), 1)
        self.assertEqual(hashes, {call["request_sha256"]})

    def test_later_attempt_after_measured_is_never_requested(self) -> None:
        case, contract = fixtures_case(), fixtures_contract()
        response = fixtures_valid_response(case, contract)
        call, submitter, _, _, _ = _call(
            [fixture_outcome(fixtures_envelope(canonical_json(response)))]
        )
        self.assertEqual(call["submission_count"], 1)
        self.assertEqual(len(submitter.bodies), 1)
        self.assertTrue(call["attempts"][0]["measured"])

    def test_measured_response_parses_under_the_frozen_contract(self) -> None:
        case, contract = fixtures_case(), fixtures_contract()
        response = fixtures_valid_response(case, contract)
        call, _, _, _, _ = _call(
            [fixture_outcome(fixtures_envelope(canonical_json(response)))]
        )
        parsed = parse_response(
            call["measured_response"],
            contract,
            tuple(case["runner_control"]["legal_target_slots"]),
        )
        self.assertEqual(set(parsed), {"facts", "candidate_effects", "unresolved_targets"})


def _as_body(payload: bytes) -> dict:
    import json

    return json.loads(payload.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
