from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from ser.authzgym.realmodel import load_real_model_condition
from ser.authzgym.semantic_contract import episode_from_case
from ser.authzgym.supervised_transport import (
    SupervisedSemanticContractClientV12,
    TransportUnavailable,
    _split_curl_output,
)
from ser.authzgym.tunnel_supervisor import TunnelSupervisor, load_tunnel_policy
from ser.evaluation.authz_transport_analysis import classify_transport


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "experiments/authzgym_transport_envelope_v1"
SEMANTIC_SOURCE = ROOT / "experiments/authzgym_semantic_contract_v1_2"


class FakeProcess:
    def __init__(self):
        self.alive = True
        self.returncode = None
        self.terminated = False
        self.killed = False

    def poll(self):
        return None if self.alive else self.returncode

    def terminate(self):
        self.terminated = True
        self.alive = False
        self.returncode = -15

    def kill(self):
        self.killed = True
        self.alive = False
        self.returncode = -9

    def wait(self, timeout=None):
        self.alive = False
        if self.returncode is None:
            self.returncode = 0
        return self.returncode

    def communicate(self, timeout=None):
        return b"", b""


class DummySupervisor:
    def __init__(self):
        self.generation = 1
        self.port = 47819
        self.reconnects = 0

    @property
    def proxy_url(self):
        return f"socks5h://127.0.0.1:{self.port}"

    def reconnect(self, probe, *, reason):
        self.reconnects += 1
        self.generation += 1
        return {"reason": reason}


def provider_envelope(content: dict) -> dict:
    return {
        "id": "transport-test-response",
        "model": "patchersniper_praneeth/gpt-5.4-nano",
        "choices": [
            {
                "finish_reason": "stop",
                "message": {"role": "assistant", "content": json.dumps(content)},
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 10,
            "total_tokens": 20,
            "prompt_tokens_details": {"cached_tokens": 0},
            "completion_tokens_details": {"reasoning_tokens": 0},
        },
    }


def transport_outcome(envelope: dict | None, *, received: bool, generation: int = 1):
    body = b"" if envelope is None else json.dumps(envelope).encode("utf-8")
    return {
        "returncode": 0 if received else 7,
        "body": body,
        "envelope": envelope,
        "credential_redacted": False,
        "provider_response_received": received,
        "transport_failure_class": None if received else "connection_failure",
        "transport_record_hash": f"transport-record-{generation}",
        "curl_metadata": {
            "http_status": 200 if received else 0,
            "time_connect_seconds": 0.1 if received else 0.0,
            "time_starttransfer_seconds": 0.2 if received else 0.0,
            "time_total_seconds": 0.3 if received else 0.01,
        },
        "latency_ms": 300.0 if received else 10.0,
        "tunnel_generation": generation,
    }


class TunnelSupervisorTests(unittest.TestCase):
    def setUp(self):
        self.policy = load_tunnel_policy(EXPERIMENT / "transport_config.json")

    def test_policy_is_bounded_and_retains_required_transport(self):
        self.assertEqual(self.policy.server_alive_interval_seconds, 15)
        self.assertEqual(self.policy.server_alive_count_max, 2)
        self.assertEqual(
            self.policy.maximum_transport_reconnections_per_logical_call, 1
        )
        self.assertEqual(self.policy.maximum_api_submissions, 384)
        self.assertEqual(self.policy.proxy_dns_mode, "socks5h_remote_resolution")
        self.assertFalse(self.policy.tls_verification)

    def test_startup_uses_no_remote_command_and_strips_credentials(self):
        processes = []
        launches = []
        events = []

        def factory(args, **kwargs):
            process = FakeProcess()
            processes.append(process)
            launches.append((args, kwargs))
            return process

        supervisor = TunnelSupervisor(
            self.policy,
            events.append,
            environment={
                "OPENAI_API_KEY": "SECRET",
                "OPENAI_BASE_URL": "https://example.invalid/v1",
                "PATH": "/usr/bin",
            },
            process_factory=factory,
            port_selector=lambda: 49001,
            listener_checker=lambda host, port, timeout: processes[-1].alive,
            sleeper=lambda value: None,
        )
        supervisor.establish(
            lambda proxy: {"ok": True, "paid_inference": False},
            reason="test_startup",
        )
        args, kwargs = launches[0]
        self.assertIn("-N", args)
        self.assertIn("-T", args)
        self.assertIn("ExitOnForwardFailure=yes", args)
        self.assertIn("ServerAliveInterval=15", args)
        self.assertIn("ServerAliveCountMax=2", args)
        self.assertEqual(args[-1], "nopales17@wiseau.seclab.cs.ucsb.edu")
        self.assertNotIn("SECRET", json.dumps(args))
        self.assertNotIn("OPENAI_API_KEY", kwargs["env"])
        self.assertNotIn("OPENAI_BASE_URL", kwargs["env"])
        self.assertTrue(
            all(
                event.get("remote_command") is not True
                for event in events
            )
        )
        cleanup = supervisor.stop()
        self.assertTrue(cleanup["process_exited"])
        self.assertTrue(cleanup["listener_closed"])

    def test_precall_death_replaces_tunnel(self):
        processes = []
        events = []

        def factory(args, **kwargs):
            process = FakeProcess()
            processes.append(process)
            return process

        supervisor = TunnelSupervisor(
            self.policy,
            events.append,
            process_factory=factory,
            port_selector=lambda: 49002,
            listener_checker=lambda host, port, timeout: processes[-1].alive,
            sleeper=lambda value: None,
        )
        probe = lambda proxy: {"ok": True, "paid_inference": False}
        supervisor.establish(probe, reason="initial")
        processes[-1].alive = False
        processes[-1].returncode = 255
        replaced = supervisor.ensure_live(probe)
        self.assertTrue(replaced)
        self.assertEqual(supervisor.generation, 2)
        self.assertTrue(supervisor.process_alive())
        supervisor.stop()


class TransportClassifierTests(unittest.TestCase):
    def classify(self, **overrides):
        values = {
            "validation_status": "pass",
            "provider_completed": 128,
            "permanently_failed": 0,
            "failed_tunnel_starts": 0,
            "reconnect_requests": 1,
            "successful_reconnects": 1,
            "cleanup_ok": True,
        }
        values.update(overrides)
        return classify_transport(**values)

    def test_exact_transport_classifier_precedence(self):
        self.assertEqual(self.classify(), "transport_stable")
        self.assertEqual(
            self.classify(failed_tunnel_starts=1),
            "transport_recoverable_but_unstable",
        )
        self.assertEqual(
            self.classify(successful_reconnects=0),
            "transport_recoverable_but_unstable",
        )
        self.assertEqual(
            self.classify(provider_completed=127, permanently_failed=1),
            "transport_unstable",
        )
        self.assertEqual(
            self.classify(validation_status="fail"),
            "invalid",
        )


class SupervisedTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = load_tunnel_policy(EXPERIMENT / "transport_config.json")
        cls.condition = load_real_model_condition(
            SEMANTIC_SOURCE / "model_config.json"
        )
        cls.prompt = (
            SEMANTIC_SOURCE / "prompts/semantic_observation_v1_2.txt"
        ).read_text(encoding="utf-8")
        population = json.loads(
            (SEMANTIC_SOURCE / "STRESS_POPULATION.json").read_text(
                encoding="utf-8"
            )
        )
        cls.case = population["cases"][0]
        cls.episode = episode_from_case(cls.case)
        cls.expected = cls.case["evaluator_only"]["expected_content"]

    def client(self):
        supervisor = DummySupervisor()
        responses = []
        transports = []
        client = SupervisedSemanticContractClientV12(
            self.condition,
            self.prompt,
            supervisor,
            self.policy,
            responses.append,
            transports.append,
            environment={
                "OPENAI_BASE_URL": "https://example.invalid/v1",
                "OPENAI_API_KEY": "FAKE_TEST_SECRET",
            },
        )
        return client, supervisor, responses, transports

    def invoke(self, client):
        return client.invoke_v12(
            self.case["model_visible_input"],
            self.case["response_schema"],
            self.episode,
            tuple(self.case["runner_control"]["legal_target_slots"]),
            call_context={"logical_request_index": 1, "test": True},
        )

    def test_transport_recovery_replays_same_request_without_semantic_retry(self):
        client, supervisor, responses, _ = self.client()
        outcomes = [
            transport_outcome(None, received=False, generation=1),
            transport_outcome(
                provider_envelope(self.expected), received=True, generation=2
            ),
        ]
        with patch.object(client, "_curl_request", side_effect=outcomes) as mocked:
            result = self.invoke(client)
        self.assertEqual(supervisor.reconnects, 1)
        self.assertEqual(result["attempts"], 1)
        self.assertEqual(result["transport_attempts"], 2)
        self.assertEqual(len(responses), 1)
        self.assertEqual(mocked.call_args_list[0].args[1], mocked.call_args_list[1].args[1])
        self.assertEqual(mocked.call_args_list[0].args[4], 1)
        self.assertEqual(mocked.call_args_list[1].args[4], 1)

    def test_schema_retry_does_not_reconnect_tunnel(self):
        client, supervisor, responses, _ = self.client()
        outcomes = [
            transport_outcome(
                provider_envelope({"invalid": True}), received=True, generation=1
            ),
            transport_outcome(
                provider_envelope(self.expected), received=True, generation=1
            ),
        ]
        with patch.object(client, "_curl_request", side_effect=outcomes) as mocked:
            result = self.invoke(client)
        self.assertEqual(supervisor.reconnects, 0)
        self.assertEqual(result["attempts"], 2)
        self.assertEqual(len(responses), 2)
        self.assertEqual(mocked.call_args_list[0].args[4], 1)
        self.assertEqual(mocked.call_args_list[1].args[4], 2)

    def test_second_transport_failure_exhausts_bounded_recovery(self):
        client, supervisor, _, _ = self.client()
        outcomes = [
            transport_outcome(None, received=False, generation=1),
            transport_outcome(None, received=False, generation=2),
        ]
        with patch.object(client, "_curl_request", side_effect=outcomes):
            with self.assertRaises(TransportUnavailable):
                self.invoke(client)
        self.assertEqual(supervisor.reconnects, 1)

    def test_curl_writeout_metadata_is_removed_from_response_body(self):
        body = b'{"ok":true}'
        raw = body + b"\n__SER_CURL_META__:200:0.1:0.2:0.3"
        observed, metadata = _split_curl_output(raw)
        self.assertEqual(observed, body)
        self.assertEqual(metadata["http_status"], 200)
        self.assertEqual(metadata["time_total_seconds"], 0.3)

    def test_probe_uses_fresh_process_without_unsupported_curl_flag(self):
        client, supervisor, _, _ = self.client()
        with patch.object(
            client,
            "_anonymous_curl",
            return_value=(7, b"000", b"connection failed", 1.0),
        ) as mocked:
            client.connectivity_probe(supervisor.proxy_url)
        config = mocked.call_args.args[0].decode("utf-8")
        self.assertNotIn("fresh-connect", config)
        self.assertIn('proxy = "socks5h://127.0.0.1:47819"', config)
        self.assertIn("insecure", config)

        with patch.object(
            client,
            "_anonymous_curl",
            return_value=(7, b"", b"connection failed", 1.0),
        ) as request_mock:
            client._curl_request(b"{}", "request-hash", {}, {}, 1, 1)
        request_config = request_mock.call_args.args[0].decode("utf-8")
        self.assertNotIn("fresh-connect", request_config)
        self.assertIn('proxy = "socks5h://127.0.0.1:47819"', request_config)
        self.assertIn("insecure", request_config)


if __name__ == "__main__":
    unittest.main()
