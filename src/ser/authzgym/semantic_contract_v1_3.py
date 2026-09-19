"""v1.3 request construction and response extraction for `model-semantic-v1.3.1-N1`.

Handoff step 4, first half. Requests are built only from the public entry point
``ser.authzgym.v1_3_public_input.build_normal_request`` plus the frozen
``MODEL_CONDITION.json`` fields, and the per-case ``response_schema`` is taken
from the population unmodified. Response extraction records ``finish_reason``,
``system_fingerprint``, provider usage and the raw response-bytes hash, and
classifies structural validity exactly as preregistration section 11.1 defines
it. Semantic correctness is never considered here: a structurally valid but
semantically wrong response is valid, is measured, and is never retried.
"""

from __future__ import annotations

import hashlib
import json
from typing import Mapping

from ser.authzgym.v1_3_contract import parse_response
from ser.authzgym.v1_3_public_input import build_normal_request
from ser.core.types import canonical_json


SEMANTIC_INTERFACE = "authzgym_semantic_observation_v1_3"
JSON_SCHEMA_NAME = "authzgym_semantic_observation_v1_3"
TOP_LEVEL_KEYS = ("facts", "candidate_effects", "unresolved_targets")
LENGTH_FINISH_REASONS = ("length", "max_tokens")

TRANSPORT_REPLAY_LIMIT = 1
STRUCTURAL_RETRY_LIMIT = 1
SEMANTIC_RETRY_LIMIT = 0

USER_PAYLOAD_KEYS = (
    "semantic_interface",
    "instruction_scope",
    "current_artifact",
    "candidate_hypotheses",
    "public_artifact_inventory",
    "legal_uninspected_target_slots",
)


class SemanticContractV13Error(ValueError):
    """A request or response violates the frozen v1.3 condition contract."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def build_request_body(
    case: Mapping[str, object],
    prompt: str,
    model_condition: Mapping[str, object],
    *,
    contract: Mapping[str, object] | None = None,
) -> dict:
    """The frozen request body: public payload plus frozen condition fields."""

    normal = build_normal_request(case, prompt)
    payload = normal["user_payload"]
    if tuple(payload) != USER_PAYLOAD_KEYS:
        raise SemanticContractV13Error("public payload keys are not the frozen set")
    schema = case["response_schema"]
    if dict(schema) != dict(normal["response_schema"]):
        raise SemanticContractV13Error("population response schema changed")
    body = {
        "model": str(model_condition["route_model_identifier"]),
        "messages": [
            {"role": "system", "content": str(normal["system_instruction"])},
            {"role": "user", "content": canonical_json(payload)},
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": JSON_SCHEMA_NAME,
                "strict": True,
                "schema": schema,
            },
        },
        "max_completion_tokens": int(model_condition["maximum_output_tokens"]),
        "reasoning_effort": str(model_condition["reasoning_effort"]),
    }
    if model_condition.get("temperature") is not None:
        raise SemanticContractV13Error("temperature must not be overridden")
    for forbidden in ("top_p", "seed", "stop", "n", "tools", "tool_choice"):
        if forbidden in body:
            raise SemanticContractV13Error(f"frozen request must not send {forbidden}")
    return body


def request_bytes(body: Mapping[str, object]) -> bytes:
    return json.dumps(
        dict(body), sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def request_sha256(body: Mapping[str, object]) -> str:
    return sha256_bytes(request_bytes(body))


def extract_content(envelope: Mapping[str, object]) -> str:
    choices = envelope.get("choices")
    if not isinstance(choices, list) or not choices:
        raise SemanticContractV13Error("provider envelope has no choices")
    first = choices[0]
    if not isinstance(first, Mapping):
        raise SemanticContractV13Error("provider choice is not an object")
    message = first.get("message")
    if not isinstance(message, Mapping):
        raise SemanticContractV13Error("provider choice has no message object")
    content = message.get("content")
    if not isinstance(content, str):
        raise SemanticContractV13Error("provider message content is not text")
    return content


def finish_reason(envelope: Mapping[str, object]) -> str:
    choices = envelope.get("choices")
    if not isinstance(choices, list) or not choices:
        return ""
    first = choices[0]
    if not isinstance(first, Mapping):
        return ""
    value = first.get("finish_reason")
    return "" if value is None else str(value)


def system_fingerprint(envelope: Mapping[str, object]) -> str:
    value = envelope.get("system_fingerprint")
    return "" if value is None else str(value)


def usage(envelope: Mapping[str, object]) -> dict:
    raw = envelope.get("usage")
    if not isinstance(raw, Mapping):
        raw = {}
    prompt_details = raw.get("prompt_tokens_details")
    completion_details = raw.get("completion_tokens_details")
    prompt_details = prompt_details if isinstance(prompt_details, Mapping) else {}
    completion_details = (
        completion_details if isinstance(completion_details, Mapping) else {}
    )
    return {
        "input_tokens": int(raw.get("prompt_tokens", 0) or 0),
        "output_tokens": int(raw.get("completion_tokens", 0) or 0),
        "total_tokens": int(raw.get("total_tokens", 0) or 0),
        "cached_input_tokens": int(prompt_details.get("cached_tokens", 0) or 0),
        "reasoning_output_tokens": int(
            completion_details.get("reasoning_tokens", 0) or 0
        ),
    }


def structural_classification(
    envelope: Mapping[str, object] | None,
    *,
    contract: Mapping[str, object],
    legal_target_slots: tuple[int, ...],
    transport_outcome: Mapping[str, object] | None = None,
) -> dict:
    """Classify one submission exactly as preregistration section 11.1 defines."""

    if envelope is None:
        return {
            "structurally_valid": False,
            "failure": "no_provider_response",
            "detail": "transport returned no usable body",
        }
    reason = finish_reason(envelope)
    if reason in LENGTH_FINISH_REASONS:
        return {
            "structurally_valid": False,
            "failure": "length_termination",
            "detail": f"finish_reason={reason}",
        }
    try:
        content = extract_content(envelope)
    except SemanticContractV13Error as exc:
        return {
            "structurally_valid": False,
            "failure": "missing_message_content",
            "detail": str(exc),
        }
    try:
        parsed_content = json.loads(content)
    except json.JSONDecodeError as exc:
        return {
            "structurally_valid": False,
            "failure": "content_not_json",
            "detail": str(exc),
        }
    if not isinstance(parsed_content, dict) or set(parsed_content) != set(TOP_LEVEL_KEYS):
        return {
            "structurally_valid": False,
            "failure": "top_level_shape",
            "detail": "response must have exactly the three frozen top-level keys",
        }
    try:
        parse_response(parsed_content, contract, tuple(legal_target_slots))
    except Exception as exc:  # ContractV13Error and any strict-shape failure
        return {
            "structurally_valid": False,
            "failure": "contract_parse_failure",
            "detail": f"{type(exc).__name__}: {exc}",
        }
    return {
        "structurally_valid": True,
        "failure": None,
        "detail": "section 11.1 structural validity holds",
        "response": parsed_content,
        "response_sha256": sha256_bytes(content.encode("utf-8")),
        "finish_reason": reason,
        "system_fingerprint": system_fingerprint(envelope),
        "usage": usage(envelope),
        "transport_outcome": dict(transport_outcome or {}),
    }
