"""Scoped provider transport for the frozen AuthzGym semantic contract v1.2."""

from __future__ import annotations

import json
from typing import Callable, Mapping

from ser.core.types import canonical_json, content_hash

from .model import AuthzEpisode
from .realmodel import (
    CurlChatCompletionsClient,
    ProviderError,
    RealModelCondition,
    _extract_content,
    _sha256_bytes,
    _usage_from_response,
    usage_cost_usd,
)
from .semantic_contract import ContractV12Error, parse_content


def _finish_reason(response: Mapping[str, object]) -> str | None:
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], Mapping):
        return None
    value = choices[0].get("finish_reason")
    return str(value) if value is not None else None


class SemanticContractClientV12(CurlChatCompletionsClient):
    """Use the prior isolated curl path with a per-call dynamic strict schema."""

    def __init__(
        self,
        condition: RealModelCondition,
        prompt_text: str,
        proxy_url: str,
        response_sink: Callable[[dict], None],
        *,
        environment: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(
            condition,
            prompt_text,
            {},
            proxy_url,
            response_sink,
            environment=environment,
        )

    def _request_body_v12(
        self, visible_input: dict, schema: dict, max_output_tokens: int
    ) -> bytes:
        body = {
            "model": self.condition.model_identifier,
            "messages": [
                {"role": "system", "content": self.prompt_text},
                {"role": "user", "content": canonical_json(visible_input)},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "authzgym_semantic_observation_v1_2",
                    "strict": True,
                    "schema": schema,
                },
            },
            "reasoning_effort": self.condition.reasoning_effort,
            "max_completion_tokens": max_output_tokens,
        }
        if self.condition.temperature is not None:
            body["temperature"] = self.condition.temperature
        return canonical_json(body).encode("utf-8")

    def invoke_v12(
        self,
        visible_input: dict,
        schema: dict,
        episode: AuthzEpisode,
        legal_target_slots: tuple[int, ...],
        *,
        call_context: dict,
    ) -> dict:
        max_output_tokens = self.condition.max_output_tokens_per_artifact
        request_body = self._request_body_v12(
            visible_input, schema, max_output_tokens
        )
        request_sha256 = _sha256_bytes(request_body)
        errors = []
        _, api_key = self._configuration()
        for attempt in range(1, self.condition.maximum_attempts_per_semantic_call + 1):
            conservative_next_cost = (
                self.condition.input_token_ceiling_per_sequential_run
                * self.condition.input_price_per_million_usd
                + max_output_tokens * self.condition.output_price_per_million_usd
            ) / 1_000_000.0
            if (
                self.total_cost_usd + conservative_next_cost
                > self.condition.hard_spend_ceiling_usd + 1e-12
            ):
                raise ProviderError(
                    "hard provider-spend ceiling reserve would be exceeded by request"
                )

            returncode, stdout, _, latency_ms = self._curl(request_body)
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
                "response_schema_sha256": content_hash(schema),
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
            response = None
            usage = None
            parsed = None
            validation_error = None
            try:
                if credential_redacted:
                    raise ProviderError("provider echoed credential")
                if returncode != 0:
                    raise ProviderError(f"provider transport returned code {returncode}")
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
                if _finish_reason(response) == "length":
                    raise ContractV12Error("finish_reason=length")
                content = _extract_content(response)
                try:
                    value = json.loads(content)
                except json.JSONDecodeError as exc:
                    raise ContractV12Error("message content is not complete JSON") from exc
                observation, normalized = parse_content(
                    value, episode, legal_target_slots
                )
                parsed = {
                    "provider_content": value,
                    "normalized": normalized,
                    "semantic_observation": observation.to_dict(),
                }
            except (ProviderError, ContractV12Error, json.JSONDecodeError) as exc:
                validation_error = f"{type(exc).__name__}:{exc}"

            response_record["contract_validation"] = {
                "valid": validation_error is None,
                "error": validation_error,
                "finish_reason": _finish_reason(response) if response else None,
            }
            response_record["record_hash"] = content_hash(response_record)
            self.response_sink(response_record)
            if validation_error is not None:
                errors.append(f"attempt {attempt}: {validation_error}")
                continue

            assert response is not None and usage is not None and parsed is not None
            return {
                "call_id": str(response.get("id") or raw_hash[:24]),
                "request_sha256": request_sha256,
                "raw_response_sha256": raw_hash,
                "provider_model": str(response.get("model") or "unreported"),
                "system_fingerprint": response.get("system_fingerprint"),
                "attempts": attempt,
                "parsed": parsed,
                "usage": usage,
                "latency_ms": latency_ms,
                "monetary_cost_usd": usage_cost_usd(usage, self.condition),
                "max_output_tokens": max_output_tokens,
                "finish_reason": _finish_reason(response),
            }
        raise ContractV12Error("; ".join(errors))
