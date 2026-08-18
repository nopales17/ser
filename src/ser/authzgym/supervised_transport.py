"""Transport-supervised client for the frozen AuthzGym semantic contract v1.2."""

from __future__ import annotations

import json
import os
import subprocess
import time
from typing import Callable, Mapping

from ser.core.types import content_hash

from .model import AuthzEpisode
from .realmodel import (
    ProviderError,
    RealModelCondition,
    _curl_config_quote,
    _extract_content,
    _sha256_bytes,
    _usage_from_response,
    usage_cost_usd,
)
from .semantic_contract import ContractV12Error, parse_content
from .semantic_transport import SemanticContractClientV12, _finish_reason
from .tunnel_supervisor import TunnelError, TunnelPolicy, TunnelSupervisor


class TransportUnavailable(ProviderError):
    """A logical request exhausted its frozen transport recovery allowance."""


_CURL_META_MARKER = b"\n__SER_CURL_META__:"


def _transport_failure_class(returncode: int) -> str:
    return {
        5: "proxy_resolution_failure",
        6: "target_resolution_failure",
        7: "connection_failure",
        18: "partial_transfer",
        28: "timeout",
        35: "tls_handshake_failure",
        52: "empty_reply",
        55: "send_failure",
        56: "receive_failure",
        92: "http2_stream_failure",
        97: "proxy_handshake_failure",
        124: "local_subprocess_timeout",
    }.get(returncode, "other_transport_failure")


def _split_curl_output(stdout: bytes) -> tuple[bytes, dict]:
    body, marker, metadata = stdout.rpartition(_CURL_META_MARKER)
    if not marker:
        return stdout, {
            "http_status": 0,
            "time_connect_seconds": 0.0,
            "time_starttransfer_seconds": 0.0,
            "time_total_seconds": 0.0,
        }
    parts = metadata.decode("ascii", errors="replace").strip().split(":")
    if len(parts) != 4:
        return body, {
            "http_status": 0,
            "time_connect_seconds": 0.0,
            "time_starttransfer_seconds": 0.0,
            "time_total_seconds": 0.0,
        }
    try:
        return body, {
            "http_status": int(parts[0]),
            "time_connect_seconds": float(parts[1]),
            "time_starttransfer_seconds": float(parts[2]),
            "time_total_seconds": float(parts[3]),
        }
    except ValueError:
        return body, {
            "http_status": 0,
            "time_connect_seconds": 0.0,
            "time_starttransfer_seconds": 0.0,
            "time_total_seconds": 0.0,
        }


class SupervisedSemanticContractClientV12(SemanticContractClientV12):
    """Keep tunnel recovery separate from the frozen semantic retry loop."""

    def __init__(
        self,
        condition: RealModelCondition,
        prompt_text: str,
        supervisor: TunnelSupervisor,
        tunnel_policy: TunnelPolicy,
        response_sink: Callable[[dict], None],
        transport_sink: Callable[[dict], None],
        *,
        environment: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(
            condition,
            prompt_text,
            "socks5h://127.0.0.1:0",
            response_sink,
            environment=environment,
        )
        self.supervisor = supervisor
        self.tunnel_policy = tunnel_policy
        self.transport_sink = transport_sink
        self.total_provider_responses = 0
        self.total_transport_failures = 0
        self.total_transport_recoveries = 0

    def accounting_snapshot(self) -> dict:
        value = super().accounting_snapshot()
        value.update(
            {
                "provider_responses": self.total_provider_responses,
                "transport_failures": self.total_transport_failures,
                "transport_recoveries": self.total_transport_recoveries,
            }
        )
        return value

    def _anonymous_curl(
        self, config: bytes, *, request_body: bytes | None, timeout_seconds: int
    ) -> tuple[int, bytes, bytes, float]:
        read_fd, write_fd = os.pipe()
        try:
            os.write(write_fd, config)
        finally:
            os.close(write_fd)
        started = time.monotonic()
        args = ["curl", "--config", f"/dev/fd/{read_fd}"]
        if request_body is not None:
            args.extend(("--data-binary", "@-"))
        try:
            result = subprocess.run(
                args,
                input=request_body,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout_seconds,
                check=False,
                pass_fds=(read_fd,),
            )
            returncode = result.returncode
            stdout = result.stdout
            stderr = result.stderr
        except subprocess.TimeoutExpired as exc:
            returncode = 124
            stdout = exc.stdout or b""
            stderr = exc.stderr or b"local curl subprocess timed out"
        finally:
            os.close(read_fd)
        latency_ms = (time.monotonic() - started) * 1000.0
        return returncode, stdout, stderr, latency_ms

    def connectivity_probe(self, proxy_url: str) -> dict:
        """Reach the API over SOCKS without making a model inference."""

        base_url, api_key = self._configuration()
        endpoint = f"{base_url}{self.tunnel_policy.api_probe_path}"
        config = "\n".join(
            (
                f"url = {_curl_config_quote(endpoint)}",
                'request = "GET"',
                f"header = {_curl_config_quote('Authorization: Bearer ' + api_key)}",
                f"proxy = {_curl_config_quote(proxy_url)}",
                "insecure",
                "silent",
                "show-error",
                'output = "/dev/null"',
                'write-out = "%{http_code}"',
                f"connect-timeout = {self.tunnel_policy.api_probe_connect_timeout_seconds}",
                f"max-time = {self.tunnel_policy.api_probe_timeout_seconds}",
            )
        ).encode("utf-8")
        returncode, stdout, stderr, latency_ms = self._anonymous_curl(
            config,
            request_body=None,
            timeout_seconds=self.tunnel_policy.api_probe_timeout_seconds + 5,
        )
        safe_stdout = stdout.replace(api_key.encode("utf-8"), b"[REDACTED]")
        safe_stderr = stderr.replace(api_key.encode("utf-8"), b"[REDACTED]")
        try:
            http_status = int(safe_stdout.decode("ascii", errors="replace")[-3:])
        except ValueError:
            http_status = 0
        return {
            "ok": returncode == 0 and 100 <= http_status < 500,
            "curl_returncode": returncode,
            "http_status": http_status,
            "latency_ms": latency_ms,
            "stderr": safe_stderr.decode("utf-8", errors="replace"),
            "credential_redacted": safe_stdout != stdout or safe_stderr != stderr,
            "paid_inference": False,
            "proxy_dns_mode": self.tunnel_policy.proxy_dns_mode,
            "tls_verification": False,
        }

    def _reserve_api_submission(self, max_output_tokens: int) -> None:
        if self.total_provider_calls >= self.tunnel_policy.maximum_api_submissions:
            raise ProviderError("frozen API-submission ceiling would be exceeded")
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

    def _curl_request(
        self,
        request_body: bytes,
        request_sha256: str,
        schema: dict,
        call_context: dict,
        semantic_attempt: int,
        transport_attempt: int,
    ) -> dict:
        max_output_tokens = self.condition.max_output_tokens_per_artifact
        self._reserve_api_submission(max_output_tokens)
        base_url, api_key = self._configuration()
        endpoint = f"{base_url}/chat/completions"
        proxy_url = self.supervisor.proxy_url
        config = "\n".join(
            (
                f"url = {_curl_config_quote(endpoint)}",
                'request = "POST"',
                'header = "Content-Type: application/json"',
                f"header = {_curl_config_quote('Authorization: Bearer ' + api_key)}",
                f"proxy = {_curl_config_quote(proxy_url)}",
                "insecure",
                "silent",
                "show-error",
                "fail-with-body",
                f"connect-timeout = {self.condition.connect_timeout_seconds}",
                f"max-time = {self.condition.request_timeout_seconds}",
                'write-out = "\\n__SER_CURL_META__:%{http_code}:%{time_connect}:%{time_starttransfer}:%{time_total}"',
            )
        ).encode("utf-8")
        returncode, raw_stdout, stderr, latency_ms = self._anonymous_curl(
            config,
            request_body=request_body,
            timeout_seconds=self.condition.request_timeout_seconds + 5,
        )
        self.total_provider_calls += 1
        self.total_latency_ms += latency_ms
        body, curl_metadata = _split_curl_output(raw_stdout)
        safe_body = body.replace(api_key.encode("utf-8"), b"[REDACTED]")
        safe_stderr = stderr.replace(api_key.encode("utf-8"), b"[REDACTED]")
        credential_redacted = safe_body != body or safe_stderr != stderr
        parsed_envelope = None
        try:
            candidate = json.loads(safe_body)
            if isinstance(candidate, dict):
                parsed_envelope = candidate
        except json.JSONDecodeError:
            pass
        provider_response_received = (
            returncode in (0, 22)
            and curl_metadata["http_status"] > 0
            and parsed_envelope is not None
        )
        failure_class = (
            None
            if provider_response_received
            else _transport_failure_class(returncode)
        )
        transport_record = {
            "schema_version": 1,
            "experiment": "authzgym-transport-envelope-v1",
            "call_context": call_context,
            "semantic_attempt": semantic_attempt,
            "transport_attempt": transport_attempt,
            "api_submission_ordinal": self.total_provider_calls,
            "request_sha256": request_sha256,
            "response_schema_sha256": content_hash(schema),
            "tunnel_generation": self.supervisor.generation,
            "local_proxy_port": self.supervisor.port,
            "proxy_kind": "ephemeral_local_socks5h",
            "proxy_dns_mode": self.tunnel_policy.proxy_dns_mode,
            "tls_verification": False,
            "credential_delivery": "anonymous_pipe_curl_config",
            "http_connection_strategy": self.tunnel_policy.http_connection_strategy,
            "curl_returncode": returncode,
            "curl_metadata": curl_metadata,
            "latency_ms": latency_ms,
            "stderr": safe_stderr.decode("utf-8", errors="replace"),
            "credential_redacted": credential_redacted,
            "response_body_sha256": _sha256_bytes(safe_body),
            "response_body_bytes": len(safe_body),
            "provider_response_received": provider_response_received,
            "transport_failure_class": failure_class,
        }
        transport_record["record_hash"] = content_hash(transport_record)
        self.transport_sink(transport_record)
        if not provider_response_received:
            self.total_transport_failures += 1
        return {
            "returncode": returncode,
            "body": safe_body,
            "envelope": parsed_envelope,
            "credential_redacted": credential_redacted,
            "provider_response_received": provider_response_received,
            "transport_failure_class": failure_class,
            "transport_record_hash": transport_record["record_hash"],
            "curl_metadata": curl_metadata,
            "latency_ms": latency_ms,
            "tunnel_generation": self.supervisor.generation,
        }

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
        reconnections_used = 0
        transport_attempt = 0
        for semantic_attempt in range(
            1, self.condition.maximum_attempts_per_semantic_call + 1
        ):
            while True:
                transport_attempt += 1
                outcome = self._curl_request(
                    request_body,
                    request_sha256,
                    schema,
                    call_context,
                    semantic_attempt,
                    transport_attempt,
                )
                if outcome["provider_response_received"]:
                    break
                if (
                    reconnections_used
                    >= self.tunnel_policy.maximum_transport_reconnections_per_logical_call
                ):
                    raise TransportUnavailable(
                        "logical request exhausted its frozen transport recovery allowance: "
                        + str(outcome["transport_failure_class"])
                    )
                reconnections_used += 1
                try:
                    self.supervisor.reconnect(
                        self.connectivity_probe,
                        reason=str(outcome["transport_failure_class"]),
                    )
                except TunnelError as exc:
                    raise TransportUnavailable(
                        "tunnel recovery failed after transport error: " + str(exc)
                    ) from exc
                self.total_transport_recoveries += 1

            self.total_provider_responses += 1
            response = outcome["envelope"]
            assert isinstance(response, dict)
            usage = None
            parsed = None
            validation_error = None
            try:
                if outcome["credential_redacted"]:
                    raise ProviderError("provider echoed credential")
                if outcome["curl_metadata"]["http_status"] >= 400:
                    raise ProviderError(
                        "provider returned HTTP status "
                        + str(outcome["curl_metadata"]["http_status"])
                    )
                usage = _usage_from_response(response)
                if usage["input_tokens"] <= 0 or usage["output_tokens"] <= 0:
                    raise ProviderError("provider usage metadata is absent or zero")
                cost = usage_cost_usd(usage, self.condition)
                self.total_cost_usd += cost
                self.total_input_tokens += usage["input_tokens"]
                self.total_output_tokens += usage["output_tokens"]
                self.total_cached_input_tokens += usage["cached_input_tokens"]
                self.total_reasoning_output_tokens += usage[
                    "reasoning_output_tokens"
                ]
                if (
                    self.total_cost_usd
                    > self.condition.hard_spend_ceiling_usd + 1e-12
                ):
                    raise ProviderError("hard provider-spend ceiling exceeded")
                if _finish_reason(response) == "length":
                    raise ContractV12Error("finish_reason=length")
                content = _extract_content(response)
                try:
                    value = json.loads(content)
                except json.JSONDecodeError as exc:
                    raise ContractV12Error(
                        "message content is not complete JSON"
                    ) from exc
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

            body = outcome["body"]
            raw_hash = _sha256_bytes(body)
            response_record = {
                "schema_version": 1,
                "experiment": "authzgym-transport-envelope-v1",
                "call_context": call_context,
                "attempt": semantic_attempt,
                "request_sha256": request_sha256,
                "response_schema_sha256": content_hash(schema),
                "raw_response_sha256": raw_hash,
                "raw_response_body": body.decode("utf-8", errors="replace"),
                "transport_attempt_record_hash": outcome[
                    "transport_record_hash"
                ],
                "transport": {
                    "client": "system-curl-fresh-process",
                    "proxy_kind": "ephemeral_local_socks5h",
                    "proxy_dns_mode": self.tunnel_policy.proxy_dns_mode,
                    "tls_verification": False,
                    "credential_delivery": "anonymous_pipe_curl_config",
                    "returncode": outcome["returncode"],
                    "http_status": outcome["curl_metadata"]["http_status"],
                    "latency_ms": outcome["latency_ms"],
                    "tunnel_generation": outcome["tunnel_generation"],
                    "credential_redacted": outcome["credential_redacted"],
                },
                "contract_validation": {
                    "valid": validation_error is None,
                    "error": validation_error,
                    "finish_reason": _finish_reason(response),
                },
            }
            response_record["record_hash"] = content_hash(response_record)
            self.response_sink(response_record)
            if validation_error is not None:
                errors.append(f"attempt {semantic_attempt}: {validation_error}")
                continue

            assert usage is not None and parsed is not None
            return {
                "call_id": str(response.get("id") or raw_hash[:24]),
                "request_sha256": request_sha256,
                "raw_response_sha256": raw_hash,
                "provider_model": str(response.get("model") or "unreported"),
                "system_fingerprint": response.get("system_fingerprint"),
                "attempts": semantic_attempt,
                "transport_attempts": transport_attempt,
                "transport_reconnections": reconnections_used,
                "parsed": parsed,
                "usage": usage,
                "latency_ms": outcome["latency_ms"],
                "monetary_cost_usd": usage_cost_usd(usage, self.condition),
                "max_output_tokens": max_output_tokens,
                "finish_reason": _finish_reason(response),
            }
        raise ContractV12Error("; ".join(errors))
