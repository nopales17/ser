"""Supervised v1.3 transport with the frozen retry state machine.

Handoff step 4, second half. Mirrors ``ser.authzgym.supervised_transport`` for
v1.3 with:

* client-side retries set to zero and asserted (one fresh ``curl`` process per
  submission, no ``--retry``, no shared connection pool);
* a frozen bound of two submissions per logical call -- one identical-byte
  transport replay or one structural-response retry, never more, matching the
  section-9.5 cost-gate arithmetic ``max_submissions = 2 * (112 + 56)``;
* **no retry for a structurally valid but semantically wrong response**;
* the measured response being the first structurally valid response in attempt
  order, with every attempt preserved.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from typing import Callable, Mapping

from ser.authzgym.realmodel import (
    ProviderError,
    _curl_config_quote,
    _usage_from_response,
)
from ser.authzgym.semantic_contract_v1_3 import (
    SEMANTIC_RETRY_LIMIT,
    STRUCTURAL_RETRY_LIMIT,
    TRANSPORT_REPLAY_LIMIT,
    build_request_body,
    request_bytes,
    request_sha256 as body_sha256,
    sha256_bytes,
    structural_classification,
)


MAX_SUBMISSIONS_PER_LOGICAL_CALL = 2
CLIENT_SIDE_RETRIES = 0
TRANSPORT_FAILURE_CLASSES = {
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
}


class LogicalCallError(RuntimeError):
    """A logical call could not be completed under the frozen retry policy."""


def transport_failure_class(returncode: int) -> str:
    return TRANSPORT_FAILURE_CLASSES.get(returncode, "other_transport_failure")


def _empty_curl_metadata() -> dict:
    return {
        "http_status": 0,
        "time_connect_seconds": 0.0,
        "time_starttransfer_seconds": 0.0,
        "time_total_seconds": 0.0,
    }


def _split_curl_output(stdout: bytes) -> tuple[bytes, dict]:
    marker = b"\n__SER_CURL_META__:"
    body, found, metadata = stdout.rpartition(marker)
    if not found:
        return stdout, _empty_curl_metadata()
    parts = metadata.decode("ascii", errors="replace").strip().split(":")
    if len(parts) != 4:
        return body, _empty_curl_metadata()
    try:
        return body, {
            "http_status": int(parts[0]),
            "time_connect_seconds": float(parts[1]),
            "time_starttransfer_seconds": float(parts[2]),
            "time_total_seconds": float(parts[3]),
        }
    except ValueError:
        return body, _empty_curl_metadata()


class SupervisedSemanticContractClientV13:
    """One logical call at a time, over the supervised SOCKS hop."""

    def __init__(
        self,
        model_condition: Mapping[str, object],
        prompt_text: str,
        supervisor,
        tunnel_policy,
        attempt_sink: Callable[[dict], None],
        transport_sink: Callable[[dict], None],
        *,
        environment: Mapping[str, str] | None = None,
        submitter: Callable[..., dict] | None = None,
    ) -> None:
        self.condition = model_condition
        self.prompt_text = prompt_text
        self.supervisor = supervisor
        self.tunnel_policy = tunnel_policy
        self.attempt_sink = attempt_sink
        self.transport_sink = transport_sink
        self.environment = os.environ if environment is None else environment
        self.submitter = submitter
        self.client_side_retries = CLIENT_SIDE_RETRIES
        self.total_submissions = 0
        self.total_provider_responses = 0
        self.total_transport_failures = 0
        self.total_cost_usd = 0.0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cached_input_tokens = 0

    # -- configuration and accounting -----------------------------------
    def _configuration(self) -> tuple[str, str]:
        base_url = str(self.environment.get("OPENAI_BASE_URL", "")).rstrip("/")
        api_key = str(self.environment.get("OPENAI_API_KEY", ""))
        if not base_url.startswith("https://"):
            raise ProviderError("configured model base URL must use HTTPS")
        if not api_key:
            raise ProviderError("configured API key is empty")
        return base_url, api_key

    def accounting_snapshot(self) -> dict:
        return {
            "submissions": self.total_submissions,
            "provider_responses": self.total_provider_responses,
            "transport_failures": self.total_transport_failures,
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "cached_input_tokens": self.total_cached_input_tokens,
            "monetary_cost_usd": round(self.total_cost_usd, 10),
            "client_side_retries": self.client_side_retries,
        }

    def _reserve_submission(self) -> None:
        if self.client_side_retries != 0:
            raise ProviderError("hidden client retries must be zero")
        if self.total_submissions >= int(self.tunnel_policy.maximum_api_submissions):
            raise ProviderError("frozen API-submission ceiling would be exceeded")
        pricing = self.condition["pricing"]
        conservative_next_cost = (
            int(self.condition["maximum_input_tokens"])
            * float(pricing["input_per_million_tokens_usd"])
            + int(self.condition["maximum_output_tokens"])
            * float(pricing["output_per_million_tokens_usd"])
        ) / 1_000_000.0
        if (
            self.total_cost_usd + conservative_next_cost
            > float(self.condition["hard_spend_ceiling_usd"]) + 1e-12
        ):
            raise ProviderError("hard provider-spend ceiling would be exceeded")

    def _record_usage(self, envelope: Mapping[str, object]) -> dict:
        raw = _usage_from_response(envelope)
        pricing = self.condition["pricing"]
        cached = min(int(raw["cached_input_tokens"]), int(raw["input_tokens"]))
        uncached = int(raw["input_tokens"]) - cached
        cost = (
            uncached * float(pricing["input_per_million_tokens_usd"])
            + cached * float(pricing["cached_input_per_million_tokens_usd"])
            + int(raw["output_tokens"])
            * float(pricing["output_per_million_tokens_usd"])
        ) / 1_000_000.0
        self.total_input_tokens += int(raw["input_tokens"])
        self.total_output_tokens += int(raw["output_tokens"])
        self.total_cached_input_tokens += cached
        self.total_cost_usd += cost
        return {**raw, "cost_usd": round(cost, 12)}

    # -- transport -------------------------------------------------------
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
            returncode, stdout, stderr = (
                result.returncode,
                result.stdout,
                result.stderr,
            )
        except subprocess.TimeoutExpired as exc:
            returncode = 124
            stdout = exc.stdout or b""
            stderr = exc.stderr or b"local curl subprocess timed out"
        finally:
            os.close(read_fd)
        return returncode, stdout, stderr, (time.monotonic() - started) * 1000.0

    def connectivity_probe(self, proxy_url: str) -> dict:
        """Reach the catalog endpoint over SOCKS without making an inference."""

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
            "tls_verification": bool(self.tunnel_policy.tls_verification),
        }

    def submit(
        self,
        request_body: bytes,
        *,
        call_context: dict,
        attempt_ordinal: int,
    ) -> dict:
        """One submission. The ``submitter`` hook exists only for fixtures."""

        self._reserve_submission()
        self.total_submissions += 1
        if self.submitter is not None:
            outcome = dict(self.submitter(request_body, call_context=call_context))
        else:
            outcome = self._curl_submission(request_body)
        if outcome.get("provider_response_received"):
            self.total_provider_responses += 1
            outcome["provider_usage"] = self._record_usage(
                outcome.get("envelope") or {}
            )
        else:
            self.total_transport_failures += 1
            outcome["provider_usage"] = {
                **_usage_from_response({}),
                "cost_usd": 0.0,
            }
        record = {
            "schema_version": 1,
            "condition_id": "model-semantic-v1.3.1-N1",
            "call_context": dict(call_context),
            "attempt_ordinal": int(attempt_ordinal),
            "api_submission_ordinal": self.total_submissions,
            "request_sha256": sha256_bytes(request_body),
            "request_bytes": len(request_body),
            "client_side_retries": self.client_side_retries,
            **outcome,
        }
        self.transport_sink(dict(record))
        return record

    def _curl_submission(self, request_body: bytes) -> dict:
        base_url, api_key = self._configuration()
        endpoint = f"{base_url}/chat/completions"
        config = "\n".join(
            (
                f"url = {_curl_config_quote(endpoint)}",
                'request = "POST"',
                'header = "Content-Type: application/json"',
                f"header = {_curl_config_quote('Authorization: Bearer ' + api_key)}",
                f"proxy = {_curl_config_quote(self.supervisor.proxy_url)}",
                "insecure",
                "silent",
                "show-error",
                "fail-with-body",
                f"connect-timeout = {int(self.condition['connect_timeout_seconds'])}",
                f"max-time = {int(self.condition['request_timeout_seconds'])}",
                'write-out = "\\n__SER_CURL_META__:%{http_code}:%{time_connect}:%{time_starttransfer}:%{time_total}"',
            )
        ).encode("utf-8")
        returncode, raw_stdout, stderr, latency_ms = self._anonymous_curl(
            config,
            request_body=request_body,
            timeout_seconds=int(self.condition["request_timeout_seconds"]) + 5,
        )
        body, curl_metadata = _split_curl_output(raw_stdout)
        safe_body = body.replace(api_key.encode("utf-8"), b"[REDACTED]")
        safe_stderr = stderr.replace(api_key.encode("utf-8"), b"[REDACTED]")
        envelope = None
        try:
            candidate = json.loads(safe_body)
        except json.JSONDecodeError:
            candidate = None
        if isinstance(candidate, dict):
            envelope = candidate
        provider_response_received = (
            returncode in (0, 22)
            and int(curl_metadata["http_status"]) > 0
            and envelope is not None
        )
        return {
            "http_status": int(curl_metadata["http_status"]),
            "curl_returncode": returncode,
            "curl_metadata": curl_metadata,
            "latency_ms": latency_ms,
            "stderr": safe_stderr.decode("utf-8", errors="replace"),
            "credential_redacted": safe_body != body or safe_stderr != stderr,
            "raw_response_sha256": sha256_bytes(safe_body),
            "raw_response_bytes": len(safe_body),
            "raw_response_text": safe_body.decode("utf-8", errors="replace"),
            "provider_response_received": provider_response_received,
            "transport_failure_class": (
                None
                if provider_response_received
                else transport_failure_class(returncode)
            ),
            "envelope": envelope,
            "provider_usage": _usage_from_response(envelope or {}),
        }

    # -- the frozen retry state machine ---------------------------------
    def invoke_logical_call(
        self,
        case: Mapping[str, object],
        contract: Mapping[str, object],
        *,
        call_context: dict,
    ) -> dict:
        body = build_request_body(case, self.prompt_text, self.condition)
        payload = request_bytes(body)
        digest = body_sha256(body)
        legal = tuple(
            int(item) for item in case["runner_control"]["legal_target_slots"]
        )
        attempts: list[dict] = []
        transport_failures = 0
        structural_failures = 0
        measured_ordinal: int | None = None

        while len(attempts) < MAX_SUBMISSIONS_PER_LOGICAL_CALL:
            ordinal = len(attempts) + 1
            record = self.submit(
                payload, call_context=call_context, attempt_ordinal=ordinal
            )
            if record["request_sha256"] != digest:
                raise LogicalCallError(
                    "request bytes differ across attempts of one logical call"
                )
            classification = structural_classification(
                record["envelope"],
                contract=contract,
                legal_target_slots=legal,
                transport_outcome={
                    "http_status": record["http_status"],
                    "curl_returncode": record["curl_returncode"],
                    "transport_failure_class": record["transport_failure_class"],
                },
            )
            attempt = {
                **record,
                "logical_attempt": ordinal,
                "structurally_valid": bool(classification["structurally_valid"]),
                "structural_failure": classification["failure"],
                "structural_detail": classification["detail"],
                "finish_reason": classification.get("finish_reason", ""),
                "system_fingerprint": classification.get("system_fingerprint", ""),
                "measured": False,
                "discarded_reason": "",
            }
            if classification["structurally_valid"]:
                attempt["measured"] = True
                attempt["response"] = classification["response"]
                attempt["response_sha256"] = classification["response_sha256"]
                measured_ordinal = ordinal
                attempts.append(attempt)
                self.attempt_sink(dict(attempt))
                break
            if classification["failure"] == "no_provider_response":
                if transport_failures < TRANSPORT_REPLAY_LIMIT:
                    transport_failures += 1
                    attempt["discarded_reason"] = "transport_replay_used"
                else:
                    attempt["discarded_reason"] = "transport_replay_exhausted"
            else:
                if structural_failures < STRUCTURAL_RETRY_LIMIT:
                    structural_failures += 1
                    attempt["discarded_reason"] = "structural_retry_used"
                else:
                    attempt["discarded_reason"] = "structural_retry_exhausted"
            attempts.append(attempt)
            self.attempt_sink(dict(attempt))
            if attempt["discarded_reason"].endswith("exhausted"):
                break

        measured = (
            attempts[measured_ordinal - 1] if measured_ordinal is not None else None
        )
        for attempt in attempts:
            if measured is not None and attempt is not measured:
                if not attempt["discarded_reason"]:
                    attempt["discarded_reason"] = "later_attempt_never_measured"
        return {
            "schema_version": 1,
            "condition_id": "model-semantic-v1.3.1-N1",
            "case_id": str(case["case_id"]),
            "call_context": dict(call_context),
            "request_sha256": digest,
            "request_bytes": len(payload),
            "submission_count": len(attempts),
            "transport_replays_used": transport_failures,
            "structural_retries_used": structural_failures,
            "semantic_retry_limit": SEMANTIC_RETRY_LIMIT,
            "semantic_retries_used": 0,
            "attempts": attempts,
            "measured_attempt_ordinal": measured_ordinal,
            "measured_response": None if measured is None else measured["response"],
            "measured_response_sha256": (
                "" if measured is None else measured["response_sha256"]
            ),
            "case_classification": (
                "measured" if measured is not None else "malformed_or_missing"
            ),
            "client_side_retries": self.client_side_retries,
        }
