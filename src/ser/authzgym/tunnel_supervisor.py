"""Local-only supervision for an ephemeral SSH SOCKS transport hop."""

from __future__ import annotations

import os
import socket
import subprocess
import time
from dataclasses import dataclass
from typing import Callable, Mapping

from ser.core.types import content_hash


class TunnelError(RuntimeError):
    """The supervised SOCKS tunnel could not be established or recovered."""


@dataclass(frozen=True)
class TunnelPolicy:
    protocol_id: str
    ssh_binary: str
    remote_host: str
    local_bind_host: str
    preferred_local_port: int
    exit_on_forward_failure: bool
    server_alive_interval_seconds: int
    server_alive_count_max: int
    ssh_connect_timeout_seconds: int
    startup_timeout_seconds: int
    listener_poll_interval_seconds: float
    listener_connect_timeout_seconds: float
    startup_attempts: int
    reconnect_backoff_seconds: float
    maximum_transport_reconnections_per_logical_call: int
    maximum_api_submissions: int
    api_probe_path: str
    api_probe_connect_timeout_seconds: int
    api_probe_timeout_seconds: int
    http_connection_strategy: str
    proxy_dns_mode: str
    tls_verification: bool
    stripped_ssh_environment_names: tuple[str, ...]

    @classmethod
    def from_dict(cls, value: Mapping[str, object]) -> "TunnelPolicy":
        keepalive = value["keepalive"]
        startup = value["startup"]
        recovery = value["recovery"]
        probe = value["connectivity_probe"]
        if not all(
            isinstance(item, Mapping)
            for item in (keepalive, startup, recovery, probe)
        ):
            raise ValueError("transport policy sections must be mappings")
        policy = cls(
            protocol_id=str(value["protocol_id"]),
            ssh_binary=str(value["ssh_binary"]),
            remote_host=str(value["remote_host"]),
            local_bind_host=str(value["local_bind_host"]),
            preferred_local_port=int(value["preferred_local_port"]),
            exit_on_forward_failure=bool(value["exit_on_forward_failure"]),
            server_alive_interval_seconds=int(
                keepalive["server_alive_interval_seconds"]
            ),
            server_alive_count_max=int(keepalive["server_alive_count_max"]),
            ssh_connect_timeout_seconds=int(
                keepalive["ssh_connect_timeout_seconds"]
            ),
            startup_timeout_seconds=int(startup["timeout_seconds"]),
            listener_poll_interval_seconds=float(
                startup["listener_poll_interval_seconds"]
            ),
            listener_connect_timeout_seconds=float(
                startup["listener_connect_timeout_seconds"]
            ),
            startup_attempts=int(startup["attempts"]),
            reconnect_backoff_seconds=float(recovery["backoff_seconds"]),
            maximum_transport_reconnections_per_logical_call=int(
                recovery["maximum_reconnections_per_logical_call"]
            ),
            maximum_api_submissions=int(recovery["maximum_api_submissions"]),
            api_probe_path=str(probe["path"]),
            api_probe_connect_timeout_seconds=int(
                probe["connect_timeout_seconds"]
            ),
            api_probe_timeout_seconds=int(probe["timeout_seconds"]),
            http_connection_strategy=str(value["http_connection_strategy"]),
            proxy_dns_mode=str(value["proxy_dns_mode"]),
            tls_verification=bool(value["tls_verification"]),
            stripped_ssh_environment_names=tuple(
                str(item) for item in value["stripped_ssh_environment_names"]
            ),
        )
        if policy.remote_host != "nopales17@wiseau.seclab.cs.ucsb.edu":
            raise ValueError("transport policy must retain the approved wiseau hop")
        if policy.local_bind_host != "127.0.0.1":
            raise ValueError("SOCKS listener must bind only to localhost")
        if policy.proxy_dns_mode != "socks5h_remote_resolution":
            raise ValueError("transport policy must retain SOCKS hostname resolution")
        if policy.tls_verification:
            raise ValueError("the approved endpoint requires the scoped TLS exception")
        if not policy.exit_on_forward_failure:
            raise ValueError("ExitOnForwardFailure must remain enabled")
        if policy.maximum_transport_reconnections_per_logical_call != 1:
            raise ValueError("the frozen policy permits one request replay after recovery")
        if policy.startup_attempts != 2:
            raise ValueError("the frozen policy permits two tunnel startup attempts")
        if policy.maximum_api_submissions != 384:
            raise ValueError("the frozen cost gate permits at most 384 API submissions")
        return policy

    def public_dict(self) -> dict:
        return {
            "protocol_id": self.protocol_id,
            "ssh_binary": self.ssh_binary,
            "remote_host": self.remote_host,
            "local_bind_host": self.local_bind_host,
            "preferred_local_port": self.preferred_local_port,
            "exit_on_forward_failure": self.exit_on_forward_failure,
            "keepalive": {
                "server_alive_interval_seconds": self.server_alive_interval_seconds,
                "server_alive_count_max": self.server_alive_count_max,
                "ssh_connect_timeout_seconds": self.ssh_connect_timeout_seconds,
            },
            "startup": {
                "timeout_seconds": self.startup_timeout_seconds,
                "listener_poll_interval_seconds": self.listener_poll_interval_seconds,
                "listener_connect_timeout_seconds": self.listener_connect_timeout_seconds,
                "attempts": self.startup_attempts,
            },
            "recovery": {
                "backoff_seconds": self.reconnect_backoff_seconds,
                "maximum_reconnections_per_logical_call": self.maximum_transport_reconnections_per_logical_call,
                "maximum_api_submissions": self.maximum_api_submissions,
            },
            "connectivity_probe": {
                "path": self.api_probe_path,
                "connect_timeout_seconds": self.api_probe_connect_timeout_seconds,
                "timeout_seconds": self.api_probe_timeout_seconds,
                "paid_inference": False,
            },
            "http_connection_strategy": self.http_connection_strategy,
            "proxy_dns_mode": self.proxy_dns_mode,
            "tls_verification": self.tls_verification,
            "stripped_ssh_environment_names": list(
                self.stripped_ssh_environment_names
            ),
        }


def load_tunnel_policy(path) -> TunnelPolicy:
    import json

    value = json.loads(path.read_text(encoding="utf-8"))
    policy = TunnelPolicy.from_dict(value)
    if value != policy.public_dict():
        raise ValueError("transport policy does not round-trip")
    return policy


class TunnelSupervisor:
    """Own one local SSH process and replace it when its SOCKS path fails."""

    def __init__(
        self,
        policy: TunnelPolicy,
        event_sink: Callable[[dict], None],
        *,
        environment: Mapping[str, str] | None = None,
        process_factory: Callable[..., object] = subprocess.Popen,
        port_selector: Callable[[], int] | None = None,
        listener_checker: Callable[[str, int, float], bool] | None = None,
        clock: Callable[[], float] = time.monotonic,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self.policy = policy
        self.event_sink = event_sink
        self.environment = dict(os.environ if environment is None else environment)
        self.process_factory = process_factory
        self.port_selector = port_selector or self._select_port
        self.listener_checker = listener_checker or self._listener_available
        self.clock = clock
        self.sleeper = sleeper
        self.process = None
        self.port: int | None = None
        self.generation = 0
        self.reconnect_requests = 0
        self.successful_reconnects = 0
        self._event_index = 0
        self._started_at = self.clock()

    @property
    def proxy_url(self) -> str:
        if self.port is None:
            raise TunnelError("tunnel has no assigned local port")
        return f"socks5h://{self.policy.local_bind_host}:{self.port}"

    def _emit(self, event: str, **details) -> dict:
        self._event_index += 1
        value = {
            "schema_version": 1,
            "event_index": self._event_index,
            "event": event,
            "generation": self.generation,
            "elapsed_ms": (self.clock() - self._started_at) * 1000.0,
            **details,
        }
        value["record_hash"] = content_hash(value)
        self.event_sink(value)
        return value

    def _select_port(self) -> int:
        preferred = self.policy.preferred_local_port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as candidate:
            try:
                candidate.bind((self.policy.local_bind_host, preferred))
                return preferred
            except OSError:
                candidate.bind((self.policy.local_bind_host, 0))
                return int(candidate.getsockname()[1])

    @staticmethod
    def _listener_available(host: str, port: int, timeout: float) -> bool:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except OSError:
            return False

    def _ssh_args(self, port: int) -> list[str]:
        return [
            self.policy.ssh_binary,
            "-N",
            "-T",
            "-D",
            f"{self.policy.local_bind_host}:{port}",
            "-o",
            "ExitOnForwardFailure=yes",
            "-o",
            f"ServerAliveInterval={self.policy.server_alive_interval_seconds}",
            "-o",
            f"ServerAliveCountMax={self.policy.server_alive_count_max}",
            "-o",
            f"ConnectTimeout={self.policy.ssh_connect_timeout_seconds}",
            "-o",
            "TCPKeepAlive=yes",
            "-o",
            "BatchMode=yes",
            "-o",
            "ControlMaster=no",
            self.policy.remote_host,
        ]

    def _safe_ssh_environment(self) -> dict[str, str]:
        result = dict(self.environment)
        for name in self.policy.stripped_ssh_environment_names:
            result.pop(name, None)
        return result

    def process_alive(self) -> bool:
        return self.process is not None and self.process.poll() is None

    def listener_alive(self) -> bool:
        return self.port is not None and self.listener_checker(
            self.policy.local_bind_host,
            self.port,
            self.policy.listener_connect_timeout_seconds,
        )

    def liveness(self) -> dict:
        return {
            "process_alive": self.process_alive(),
            "listener_alive": self.listener_alive(),
            "generation": self.generation,
            "local_port": self.port,
        }

    def _collect_stderr(self) -> str:
        if self.process is None or not hasattr(self.process, "communicate"):
            return ""
        try:
            _, stderr = self.process.communicate(timeout=0.2)
        except (subprocess.TimeoutExpired, TypeError):
            return ""
        if isinstance(stderr, bytes):
            return stderr.decode("utf-8", errors="replace")
        return str(stderr or "")

    def _terminate_current(self, reason: str) -> dict:
        process = self.process
        port = self.port
        was_alive = self.process_alive()
        if process is not None and was_alive:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        stderr = self._collect_stderr()
        process_exited = process is None or process.poll() is not None
        listener_closed = port is None or not self.listener_checker(
            self.policy.local_bind_host,
            port,
            self.policy.listener_connect_timeout_seconds,
        )
        self.process = None
        self.port = None
        return self._emit(
            "tunnel_stopped",
            reason=reason,
            was_alive=was_alive,
            process_exited=process_exited,
            listener_closed=listener_closed,
            local_port=port,
            ssh_stderr=stderr,
        )

    def establish(self, probe: Callable[[str], dict], *, reason: str) -> dict:
        last_error = "tunnel startup did not run"
        for startup_attempt in range(1, self.policy.startup_attempts + 1):
            if self.process is not None:
                self._terminate_current("replace_before_start")
            if startup_attempt > 1 and self.policy.reconnect_backoff_seconds > 0:
                self.sleeper(self.policy.reconnect_backoff_seconds)
            port = self.port_selector()
            args = self._ssh_args(port)
            safe_environment = self._safe_ssh_environment()
            self.generation += 1
            self.port = port
            started = self.clock()
            self.process = self.process_factory(
                args,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                env=safe_environment,
                start_new_session=True,
            )
            self._emit(
                "tunnel_start",
                reason=reason,
                startup_attempt=startup_attempt,
                local_port=port,
                ssh_args=args,
                remote_command=False,
                stripped_environment_names=list(
                    self.policy.stripped_ssh_environment_names
                ),
            )
            deadline = self.clock() + self.policy.startup_timeout_seconds
            while self.clock() < deadline:
                if not self.process_alive():
                    last_error = "SSH process exited before SOCKS listener became live"
                    break
                if self.listener_alive():
                    probe_result = probe(self.proxy_url)
                    self._emit(
                        "api_connectivity_probe",
                        local_port=port,
                        probe=probe_result,
                    )
                    if probe_result.get("ok"):
                        result = self._emit(
                            "tunnel_ready",
                            reason=reason,
                            startup_attempt=startup_attempt,
                            local_port=port,
                            connection_ms=(self.clock() - started) * 1000.0,
                        )
                        return result
                    last_error = (
                        "SOCKS listener was live but API connectivity probe failed"
                    )
                    break
                self.sleeper(self.policy.listener_poll_interval_seconds)
            else:
                last_error = "SOCKS listener startup timed out"
            self._emit(
                "tunnel_start_failed",
                reason=reason,
                startup_attempt=startup_attempt,
                local_port=port,
                error=last_error,
            )
            self._terminate_current("failed_startup")
        raise TunnelError(last_error)

    def ensure_live(self, probe: Callable[[str], dict]) -> bool:
        state = self.liveness()
        self._emit("precall_liveness", **state)
        if state["process_alive"] and state["listener_alive"]:
            return False
        self.establish(probe, reason="precall_liveness_failure")
        return True

    def reconnect(self, probe: Callable[[str], dict], *, reason: str) -> dict:
        self.reconnect_requests += 1
        self._emit("reconnect_requested", reason=reason)
        if self.process is not None:
            self._terminate_current("transport_recovery")
        result = self.establish(probe, reason="transport_recovery")
        self.successful_reconnects += 1
        self._emit("reconnect_complete", reason=reason)
        return result

    def stop(self, *, reason: str = "runner_cleanup") -> dict:
        if self.process is None:
            return self._emit(
                "cleanup_complete",
                reason=reason,
                process_exited=True,
                listener_closed=True,
                local_port=None,
            )
        stopped = self._terminate_current(reason)
        return self._emit(
            "cleanup_complete",
            reason=reason,
            process_exited=stopped["process_exited"],
            listener_closed=stopped["listener_closed"],
            local_port=stopped["local_port"],
        )
