"""Provider-neutral semantic calls for the AuthzGym real-model experiment.

The transport is intentionally small and isolated.  It invokes the system curl
binary through an ephemeral local SOCKS proxy, supplies the API credential over
an anonymous inherited pipe, and applies insecure TLS only to that invocation.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Mapping

from ser.core.types import canonical_json, content_hash

from .model import CandidateHypothesis, SemanticObservation, SemanticReference


FACT_KEYS = (
    "alternate-entry",
    "direct-only-membership",
    "inherited-membership-included",
    "role-fallback",
    "role-map-transform",
    "role-preserved",
    "missing-token-scope",
    "missing-feature-context",
    "token-scope-forwarded",
    "feature-context-forwarded",
    "sensitive-without-owner-check",
    "ownership-compared",
    "weak-ownership-audit",
    "weak-membership-audit",
    "weak-role-audit",
    "weak-context-audit",
)


class ProviderError(RuntimeError):
    """A provider transport or response-envelope failure."""


class MalformedSemanticResponse(ValueError):
    """A response that does not satisfy the frozen semantic contract."""


@dataclass(frozen=True)
class RealModelCondition:
    condition_id: str
    model_identifier: str
    endpoint_label: str
    api_style: str
    base_url_env: str
    api_key_env: str
    transport_client: str
    transport_client_version: str
    runtime_version: str
    proxy_kind: str
    tls_verification: bool
    reasoning_effort: str
    temperature: float | None
    max_output_tokens_per_artifact: int
    request_timeout_seconds: int
    connect_timeout_seconds: int
    maximum_attempts_per_semantic_call: int
    input_price_per_million_usd: float
    cached_input_price_per_million_usd: float
    output_price_per_million_usd: float
    hard_spend_ceiling_usd: float
    input_token_ceiling_per_sequential_run: int
    output_token_ceiling_per_sequential_run: int
    input_token_ceiling_per_monolithic_run: int
    output_token_ceiling_per_monolithic_run: int

    @classmethod
    def from_dict(cls, value: Mapping[str, object]) -> "RealModelCondition":
        pricing = value["pricing"]
        ceilings = value["resource_ceilings"]
        if not isinstance(pricing, Mapping) or not isinstance(ceilings, Mapping):
            raise ValueError("pricing and resource_ceilings must be mappings")
        condition = cls(
            condition_id=str(value["condition_id"]),
            model_identifier=str(value["model_identifier"]),
            endpoint_label=str(value["endpoint_label"]),
            api_style=str(value["api_style"]),
            base_url_env=str(value["base_url_env"]),
            api_key_env=str(value["api_key_env"]),
            transport_client=str(value["transport_client"]),
            transport_client_version=str(value["transport_client_version"]),
            runtime_version=str(value["runtime_version"]),
            proxy_kind=str(value["proxy_kind"]),
            tls_verification=bool(value["tls_verification"]),
            reasoning_effort=str(value["reasoning_effort"]),
            temperature=None
            if value.get("temperature") is None
            else float(value["temperature"]),
            max_output_tokens_per_artifact=int(
                value["max_output_tokens_per_artifact"]
            ),
            request_timeout_seconds=int(value["request_timeout_seconds"]),
            connect_timeout_seconds=int(value["connect_timeout_seconds"]),
            maximum_attempts_per_semantic_call=int(
                value["maximum_attempts_per_semantic_call"]
            ),
            input_price_per_million_usd=float(
                pricing["input_per_million_tokens_usd"]
            ),
            cached_input_price_per_million_usd=float(
                pricing["cached_input_per_million_tokens_usd"]
            ),
            output_price_per_million_usd=float(
                pricing["output_per_million_tokens_usd"]
            ),
            hard_spend_ceiling_usd=float(value["hard_spend_ceiling_usd"]),
            input_token_ceiling_per_sequential_run=int(
                ceilings["input_tokens_per_sequential_run"]
            ),
            output_token_ceiling_per_sequential_run=int(
                ceilings["output_tokens_per_sequential_run"]
            ),
            input_token_ceiling_per_monolithic_run=int(
                ceilings["input_tokens_per_monolithic_run"]
            ),
            output_token_ceiling_per_monolithic_run=int(
                ceilings["output_tokens_per_monolithic_run"]
            ),
        )
        if condition.api_style != "openai_chat_completions_json_schema":
            raise ValueError("unsupported provider API style")
        if condition.tls_verification:
            raise ValueError("this frozen transport records the required scoped TLS exception")
        if condition.proxy_kind != "ephemeral_local_socks5h":
            raise ValueError("unsupported proxy kind")
        if condition.maximum_attempts_per_semantic_call not in (1, 2):
            raise ValueError("the frozen retry policy permits zero or one retry")
        if condition.hard_spend_ceiling_usd > 5.0:
            raise ValueError("provider ceiling exceeds the experiment hard cap")
        return condition

    def public_dict(self) -> dict:
        return {
            "condition_id": self.condition_id,
            "model_identifier": self.model_identifier,
            "endpoint_label": self.endpoint_label,
            "api_style": self.api_style,
            "base_url_env": self.base_url_env,
            "api_key_env": self.api_key_env,
            "transport_client": self.transport_client,
            "transport_client_version": self.transport_client_version,
            "runtime_version": self.runtime_version,
            "proxy_kind": self.proxy_kind,
            "tls_verification": self.tls_verification,
            "reasoning_effort": self.reasoning_effort,
            "temperature": self.temperature,
            "max_output_tokens_per_artifact": self.max_output_tokens_per_artifact,
            "request_timeout_seconds": self.request_timeout_seconds,
            "connect_timeout_seconds": self.connect_timeout_seconds,
            "maximum_attempts_per_semantic_call": self.maximum_attempts_per_semantic_call,
            "pricing": {
                "input_per_million_tokens_usd": self.input_price_per_million_usd,
                "cached_input_per_million_tokens_usd": self.cached_input_price_per_million_usd,
                "output_per_million_tokens_usd": self.output_price_per_million_usd,
            },
            "hard_spend_ceiling_usd": self.hard_spend_ceiling_usd,
            "resource_ceilings": {
                "input_tokens_per_sequential_run": self.input_token_ceiling_per_sequential_run,
                "output_tokens_per_sequential_run": self.output_token_ceiling_per_sequential_run,
                "input_tokens_per_monolithic_run": self.input_token_ceiling_per_monolithic_run,
                "output_tokens_per_monolithic_run": self.output_token_ceiling_per_monolithic_run,
            },
        }


def load_real_model_condition(path: Path) -> RealModelCondition:
    value = json.loads(path.read_text(encoding="utf-8"))
    condition = RealModelCondition.from_dict(value)
    if value != condition.public_dict():
        raise ValueError("real-model configuration does not round-trip")
    return condition


def semantic_response_schema() -> dict:
    """Return the JSON Schema sent to the provider and frozen on disk."""

    return {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "fact_keys",
            "facts",
            "hypothesis_effects",
            "unresolved_references",
            "uncertainty_flags",
            "recommended_next_artifact_id",
        ],
        "properties": {
            "fact_keys": {
                "type": "array",
                "items": {"type": "string", "enum": list(FACT_KEYS)},
                "maxItems": len(FACT_KEYS),
            },
            "facts": {
                "type": "array",
                "items": {"type": "string"},
                "maxItems": len(FACT_KEYS),
            },
            "hypothesis_effects": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["hypothesis_id", "effect"],
                    "properties": {
                        "hypothesis_id": {"type": "string"},
                        "effect": {
                            "type": "number",
                            "minimum": -2.0,
                            "maximum": 2.0,
                        },
                    },
                },
                "maxItems": 4,
            },
            "unresolved_references": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["symbol", "relation_tag"],
                    "properties": {
                        "symbol": {"type": "string"},
                        "relation_tag": {"type": "string"},
                    },
                },
                "maxItems": 16,
            },
            "uncertainty_flags": {
                "type": "array",
                "items": {"type": "string"},
                "maxItems": 8,
            },
            "recommended_next_artifact_id": {
                "type": ["string", "null"],
            },
        },
    }


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _curl_config_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _usage_from_response(response: Mapping[str, object]) -> dict:
    raw = response.get("usage", {})
    if not isinstance(raw, Mapping):
        raw = {}
    prompt_details = raw.get("prompt_tokens_details", {})
    completion_details = raw.get("completion_tokens_details", {})
    if not isinstance(prompt_details, Mapping):
        prompt_details = {}
    if not isinstance(completion_details, Mapping):
        completion_details = {}
    return {
        "input_tokens": int(raw.get("prompt_tokens", 0) or 0),
        "output_tokens": int(raw.get("completion_tokens", 0) or 0),
        "total_tokens": int(raw.get("total_tokens", 0) or 0),
        "cached_input_tokens": int(prompt_details.get("cached_tokens", 0) or 0),
        "reasoning_output_tokens": int(
            completion_details.get("reasoning_tokens", 0) or 0
        ),
    }


def usage_cost_usd(usage: Mapping[str, int], condition: RealModelCondition) -> float:
    cached = min(int(usage["cached_input_tokens"]), int(usage["input_tokens"]))
    uncached = int(usage["input_tokens"]) - cached
    return (
        uncached * condition.input_price_per_million_usd
        + cached * condition.cached_input_price_per_million_usd
        + int(usage["output_tokens"]) * condition.output_price_per_million_usd
    ) / 1_000_000.0


def _extract_content(response: Mapping[str, object]) -> str:
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ProviderError("provider response has no choices")
    first = choices[0]
    if not isinstance(first, Mapping):
        raise ProviderError("provider response choice is not an object")
    message = first.get("message")
    if not isinstance(message, Mapping):
        raise ProviderError("provider response has no message object")
    content = message.get("content")
    if not isinstance(content, str):
        raise ProviderError("provider response message content is not text")
    return content


def parse_semantic_content(
    content: str,
    candidates: tuple[CandidateHypothesis, ...],
    public_inventory: tuple[dict, ...],
    permitted_next_artifact_ids: tuple[str, ...],
    recommendation_required: bool,
) -> tuple[SemanticObservation, str | None, dict]:
    """Fail closed on any violation not expressible in the static JSON schema."""

    try:
        value = json.loads(content)
    except json.JSONDecodeError as exc:
        raise MalformedSemanticResponse("message content is not JSON") from exc
    if not isinstance(value, dict):
        raise MalformedSemanticResponse("semantic response is not an object")
    required = {
        "fact_keys",
        "facts",
        "hypothesis_effects",
        "unresolved_references",
        "uncertainty_flags",
        "recommended_next_artifact_id",
    }
    if set(value) != required:
        raise MalformedSemanticResponse("semantic response fields do not match schema")
    fact_keys = value["fact_keys"]
    facts = value["facts"]
    effects = value["hypothesis_effects"]
    references = value["unresolved_references"]
    flags = value["uncertainty_flags"]
    recommendation = value["recommended_next_artifact_id"]
    if (
        not isinstance(fact_keys, list)
        or not all(isinstance(item, str) and item in FACT_KEYS for item in fact_keys)
        or len(fact_keys) != len(set(fact_keys))
    ):
        raise MalformedSemanticResponse("fact_keys are invalid or duplicated")
    if not isinstance(facts, list) or not all(isinstance(item, str) for item in facts):
        raise MalformedSemanticResponse("facts must be strings")
    candidate_ids = {item.hypothesis_id for item in candidates}
    parsed_effects: dict[str, float] = {}
    if not isinstance(effects, list):
        raise MalformedSemanticResponse("hypothesis_effects must be a list")
    for item in effects:
        if not isinstance(item, dict) or set(item) != {"hypothesis_id", "effect"}:
            raise MalformedSemanticResponse("hypothesis effect has invalid fields")
        hypothesis_id = item["hypothesis_id"]
        effect = item["effect"]
        if (
            not isinstance(hypothesis_id, str)
            or hypothesis_id not in candidate_ids
            or hypothesis_id in parsed_effects
            or isinstance(effect, bool)
            or not isinstance(effect, (int, float))
            or not -2.0 <= float(effect) <= 2.0
        ):
            raise MalformedSemanticResponse("hypothesis effect is out of contract")
        parsed_effects[hypothesis_id] = float(effect)
    public_symbols = {
        symbol
        for item in public_inventory
        for symbol in item.get("exported_symbols", [])
    }
    relation_tags = {
        tag for candidate in candidates for tag in candidate.relation_tags
    } | {"general_dependency"}
    parsed_references: list[SemanticReference] = []
    if not isinstance(references, list):
        raise MalformedSemanticResponse("unresolved_references must be a list")
    for item in references:
        if not isinstance(item, dict) or set(item) != {"symbol", "relation_tag"}:
            raise MalformedSemanticResponse("unresolved reference has invalid fields")
        symbol = item["symbol"]
        tag = item["relation_tag"]
        if symbol not in public_symbols or tag not in relation_tags:
            raise MalformedSemanticResponse("unresolved reference is outside public inventory")
        parsed_references.append(SemanticReference(str(symbol), str(tag)))
    if len({(item.symbol, item.relation_tag) for item in parsed_references}) != len(
        parsed_references
    ):
        raise MalformedSemanticResponse("unresolved references are duplicated")
    if not isinstance(flags, list) or not all(isinstance(item, str) for item in flags):
        raise MalformedSemanticResponse("uncertainty_flags must be strings")
    permitted = set(permitted_next_artifact_ids)
    if recommendation is not None and recommendation not in permitted:
        raise MalformedSemanticResponse("recommended artifact is not legally available")
    if recommendation_required and recommendation is None:
        raise MalformedSemanticResponse("a legal next-artifact recommendation is required")
    observation = SemanticObservation(
        tuple(fact_keys),
        tuple(facts),
        tuple(sorted(parsed_effects.items())),
        tuple(parsed_references),
        tuple(flags),
    )
    return observation, recommendation, value


class CurlChatCompletionsClient:
    """A scoped curl transport; AuthzGym itself has no knowledge of wiseau."""

    def __init__(
        self,
        condition: RealModelCondition,
        prompt_text: str,
        schema: dict,
        proxy_url: str,
        response_sink: Callable[[dict], None],
        *,
        environment: Mapping[str, str] | None = None,
    ) -> None:
        self.condition = condition
        self.prompt_text = prompt_text
        self.schema = schema
        self.proxy_url = proxy_url
        self.response_sink = response_sink
        self.environment = os.environ if environment is None else environment
        self.total_cost_usd = 0.0
        self.total_provider_calls = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cached_input_tokens = 0
        self.total_reasoning_output_tokens = 0
        self.total_latency_ms = 0.0

    def accounting_snapshot(self) -> dict:
        return {
            "provider_calls": self.total_provider_calls,
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "cached_input_tokens": self.total_cached_input_tokens,
            "reasoning_output_tokens": self.total_reasoning_output_tokens,
            "latency_ms": self.total_latency_ms,
            "monetary_cost_usd": self.total_cost_usd,
        }

    def _configuration(self) -> tuple[str, str]:
        try:
            base_url = self.environment[self.condition.base_url_env].rstrip("/")
            api_key = self.environment[self.condition.api_key_env]
        except KeyError as exc:
            raise ProviderError(f"required environment variable is absent: {exc.args[0]}") from None
        if not base_url.startswith("https://"):
            raise ProviderError("configured model base URL must use HTTPS")
        if not api_key:
            raise ProviderError("configured API key is empty")
        return base_url, api_key

    def _request_body(self, visible_input: dict, max_output_tokens: int) -> bytes:
        body = {
            "model": self.condition.model_identifier,
            "messages": [
                {"role": "system", "content": self.prompt_text},
                {"role": "user", "content": canonical_json(visible_input)},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "authzgym_semantic_observation_v1",
                    "strict": True,
                    "schema": self.schema,
                },
            },
            "reasoning_effort": self.condition.reasoning_effort,
            "max_completion_tokens": max_output_tokens,
        }
        if self.condition.temperature is not None:
            body["temperature"] = self.condition.temperature
        return canonical_json(body).encode("utf-8")

    def _curl(self, request_body: bytes) -> tuple[int, bytes, bytes, float]:
        base_url, api_key = self._configuration()
        endpoint = f"{base_url}/chat/completions"
        config = "\n".join(
            (
                f"url = {_curl_config_quote(endpoint)}",
                'request = "POST"',
                'header = "Content-Type: application/json"',
                f"header = {_curl_config_quote('Authorization: Bearer ' + api_key)}",
                f"proxy = {_curl_config_quote(self.proxy_url)}",
                "insecure",
                "silent",
                "show-error",
                "fail-with-body",
                f"connect-timeout = {self.condition.connect_timeout_seconds}",
                f"max-time = {self.condition.request_timeout_seconds}",
            )
        ).encode("utf-8")
        read_fd, write_fd = os.pipe()
        try:
            os.write(write_fd, config)
        finally:
            os.close(write_fd)
        started = time.monotonic()
        try:
            result = subprocess.run(
                ["curl", "--config", f"/dev/fd/{read_fd}", "--data-binary", "@-"],
                input=request_body,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=self.condition.request_timeout_seconds + 5,
                check=False,
                pass_fds=(read_fd,),
            )
        except subprocess.TimeoutExpired as exc:
            raise ProviderError("local provider transport timed out") from exc
        finally:
            os.close(read_fd)
        latency_ms = (time.monotonic() - started) * 1000.0
        return result.returncode, result.stdout, result.stderr, latency_ms

    def invoke(
        self,
        visible_input: dict,
        candidates: tuple[CandidateHypothesis, ...],
        public_inventory: tuple[dict, ...],
        permitted_next_artifact_ids: tuple[str, ...],
        recommendation_required: bool,
        *,
        artifacts_in_call: int,
        call_context: dict,
    ) -> dict:
        max_output_tokens = (
            self.condition.max_output_tokens_per_artifact * artifacts_in_call
        )
        request_body = self._request_body(visible_input, max_output_tokens)
        request_sha256 = _sha256_bytes(request_body)
        errors: list[str] = []
        _, api_key = self._configuration()
        for attempt in range(1, self.condition.maximum_attempts_per_semantic_call + 1):
            conservative_next_cost = (
                len(request_body) * self.condition.input_price_per_million_usd
                + max_output_tokens * self.condition.output_price_per_million_usd
            ) / 1_000_000.0
            if (
                self.total_cost_usd + conservative_next_cost
                > self.condition.hard_spend_ceiling_usd
            ):
                raise ProviderError(
                    "hard provider-spend ceiling reserve would be exceeded by request"
                )
            returncode, stdout, stderr, latency_ms = self._curl(request_body)
            self.total_provider_calls += 1
            self.total_latency_ms += latency_ms
            safe_stdout = stdout.replace(api_key.encode("utf-8"), b"[REDACTED]")
            credential_redacted = safe_stdout != stdout
            raw_hash = _sha256_bytes(safe_stdout)
            response_record = {
                "schema_version": 1,
                "call_context": call_context,
                "attempt": attempt,
                "request_sha256": request_sha256,
                "raw_response_sha256": raw_hash,
                "raw_response_body": safe_stdout.decode("utf-8", errors="replace"),
                "transport": {
                    "client": "system-curl",
                    "proxy_kind": "ephemeral_local_socks5h",
                    "tls_verification": False,
                    "credential_delivery": "anonymous_pipe_curl_config",
                    "returncode": returncode,
                    "latency_ms": latency_ms,
                    "credential_redacted": credential_redacted,
                },
            }
            response_record["record_hash"] = content_hash(response_record)
            self.response_sink(response_record)
            if credential_redacted:
                errors.append(f"attempt {attempt}: provider echoed credential; response rejected")
                continue
            if returncode != 0:
                errors.append(
                    f"attempt {attempt}: provider transport returned code {returncode}"
                )
                continue
            try:
                response = json.loads(stdout)
                if not isinstance(response, dict):
                    raise ProviderError("provider response envelope is not an object")
                usage = _usage_from_response(response)
                if usage["input_tokens"] <= 0 or usage["output_tokens"] <= 0:
                    raise ProviderError("provider usage metadata is absent or zero")
                cost = usage_cost_usd(usage, self.condition)
                self.total_cost_usd += cost
                self.total_input_tokens += usage["input_tokens"]
                self.total_output_tokens += usage["output_tokens"]
                self.total_cached_input_tokens += usage["cached_input_tokens"]
                self.total_reasoning_output_tokens += usage["reasoning_output_tokens"]
                if self.total_cost_usd > self.condition.hard_spend_ceiling_usd + 1e-12:
                    raise ProviderError("hard provider-spend ceiling exceeded")
                content = _extract_content(response)
                observation, recommendation, parsed = parse_semantic_content(
                    content,
                    candidates,
                    public_inventory,
                    permitted_next_artifact_ids,
                    recommendation_required,
                )
                return {
                    "call_id": str(response.get("id") or raw_hash[:24]),
                    "request_sha256": request_sha256,
                    "raw_response_sha256": raw_hash,
                    "provider_model": str(response.get("model") or "unreported"),
                    "system_fingerprint": response.get("system_fingerprint"),
                    "attempts": attempt,
                    "parsed_semantic_observation": observation.to_dict(),
                    "recommended_next_artifact_id": recommendation,
                    "parsed_provider_content": parsed,
                    "usage": usage,
                    "latency_ms": latency_ms,
                    "monetary_cost_usd": cost,
                    "max_output_tokens": max_output_tokens,
                }
            except (json.JSONDecodeError, ProviderError, MalformedSemanticResponse) as exc:
                errors.append(f"attempt {attempt}: {type(exc).__name__}: {exc}")
        raise MalformedSemanticResponse("; ".join(errors))


def safe_environment_names(condition: RealModelCondition) -> tuple[str, str]:
    return condition.base_url_env, condition.api_key_env
