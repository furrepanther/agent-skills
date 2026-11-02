from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).with_name("agent_mail_auth.py")
SPEC = importlib.util.spec_from_file_location("agent_mail_auth", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class FakeResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._payload

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None


class AgentMailAuthTests(unittest.TestCase):
    def test_identity_loads_without_emitting_token(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            identity_path = Path(directory) / "identity.env"
            identity_path.write_text(
                "\n".join(
                    (
                        'export AGENT_MAIL_PROJECT="/tmp/project"',
                        'export AGENT_MAIL_AGENT="BlueLake"',
                        'export AGENT_MAIL_REGISTRATION_TOKEN="secret-token"',
                        'export AGENT_MAIL_URL="http://127.0.0.1:8766/api/"',
                    )
                ),
                encoding="utf-8",
            )
            identity_path.chmod(0o660)
            identity = MODULE._load_identity(identity_path)
        self.assertEqual(identity["AGENT_MAIL_AGENT"], "BlueLake")
        self.assertEqual(identity["_token"], "secret-token")

    def test_non_loopback_endpoint_is_rejected(self) -> None:
        with self.assertRaises(MODULE.AgentMailAuthError):
            MODULE._require_loopback_api("https://example.invalid/api/")

    def test_inbox_accepts_an_incremental_timestamp(self) -> None:
        args = MODULE._parse_args(["inbox", "--since", "2026-11-02T16:00:00+00:00"])
        self.assertEqual(args.since_ts, "2026-11-02T16:00:00+00:00")

    def test_agents_uses_the_active_project_slug(self) -> None:
        self.assertEqual(MODULE._parse_args(["agents"]).operation, "agents")
        self.assertEqual(MODULE._project_slug("/home/Antigravity"), "home-antigravity")

    def test_send_parses_only_explicit_validated_recipients(self) -> None:
        args = MODULE._parse_args(
            [
                "send",
                "--to",
                "Primus",
                "--to",
                "Primus",
                "--subject",
                "Router residency check",
                "--body-file",
                "/tmp/request.md",
                "--importance",
                "high",
                "--ack-required",
                "--topic",
                "memory-fabric",
            ]
        )
        self.assertEqual(args.to, ["Primus", "Primus"])
        self.assertEqual(args.importance, "high")
        self.assertTrue(args.ack_required)
        self.assertEqual(args.topic, "memory-fabric")

    def test_send_rejects_whitespace_recipient_and_multiline_subject(self) -> None:
        with mock.patch("sys.stderr", new_callable=io.StringIO):
            with self.assertRaises(SystemExit):
                MODULE._parse_args(
                    ["send", "--to", "not a name", "--subject", "valid", "--body-file", "/tmp/request.md"]
                )
            with self.assertRaises(SystemExit):
                MODULE._parse_args(
                    ["send", "--to", "Primus", "--subject", "invalid\nsubject", "--body-file", "/tmp/request.md"]
                )

    @mock.patch.object(MODULE.request, "urlopen")
    def test_inbox_request_keeps_token_in_body_and_redacts_output(self, mocked_urlopen: mock.Mock) -> None:
        mocked_urlopen.return_value = FakeResponse(
            {"jsonrpc": "2.0", "result": {"structuredContent": {"token": "server-token", "count": 1}}}
        )
        identity = {
            "AGENT_MAIL_URL": "http://127.0.0.1:8766/api/",
            "_token": "secret-token",
        }
        result = MODULE._call_tool(identity, "fetch_inbox", {"registration_token": identity["_token"]})
        request_body = mocked_urlopen.call_args.args[0].data.decode("utf-8")
        self.assertIn("secret-token", request_body)
        self.assertEqual(MODULE._redact(result)["token"], "[redacted]")
        self.assertEqual(MODULE._redact("reply secret-token", ("secret-token",)), "reply [redacted]")

    def test_tool_error_exposes_only_sanitized_detail(self) -> None:
        payload = {
            "result": {
                "isError": True,
                "content": [
                    {
                        "type": "text",
                        "text": "recipient Primus rejected token=secret-token",
                    }
                ],
            }
        }
        with self.assertRaisesRegex(MODULE.AgentMailAuthError, "recipient Primus rejected token=\\[redacted\\]"):
            MODULE._tool_result(payload, secrets=("secret-token",))

    @mock.patch.object(MODULE.request, "urlopen")
    def test_each_request_uses_a_fresh_json_rpc_id(self, mocked_urlopen: mock.Mock) -> None:
        mocked_urlopen.return_value = FakeResponse(
            {"jsonrpc": "2.0", "result": {"structuredContent": {"count": 0}}}
        )
        identity = {
            "AGENT_MAIL_URL": "http://127.0.0.1:8766/api/",
            "_token": "secret-token",
        }
        MODULE._call_tool(identity, "fetch_inbox", {"registration_token": identity["_token"]})
        MODULE._call_tool(identity, "fetch_inbox", {"registration_token": identity["_token"]})
        first_payload = json.loads(mocked_urlopen.call_args_list[0].args[0].data.decode("utf-8"))
        second_payload = json.loads(mocked_urlopen.call_args_list[1].args[0].data.decode("utf-8"))
        self.assertNotEqual(first_payload["id"], second_payload["id"])
        self.assertTrue(first_payload["id"].startswith("agent-mail-managed-cli-"))

    @mock.patch.object(MODULE.request, "urlopen")
    def test_agents_resource_request_uses_a_local_resource_uri(self, mocked_urlopen: mock.Mock) -> None:
        mocked_urlopen.return_value = FakeResponse(
            {
                "jsonrpc": "2.0",
                "result": {
                    "contents": [
                        {
                            "uri": "resource://agents/home-antigravity",
                            "mimeType": "application/json",
                            "text": '{"agents":[{"name":"PrimusRunner"}]}',
                        }
                    ]
                },
            }
        )
        identity = {
            "AGENT_MAIL_URL": "http://127.0.0.1:8766/api/",
            "_token": "secret-token",
        }
        result = MODULE._call_resource(identity, "resource://agents/home-antigravity")
        request_payload = json.loads(mocked_urlopen.call_args.args[0].data.decode("utf-8"))
        self.assertEqual(request_payload["method"], "resources/read")
        self.assertEqual(request_payload["params"]["uri"], "resource://agents/home-antigravity")
        self.assertEqual(result["agents"], [{"name": "PrimusRunner"}])

    @mock.patch.object(MODULE, "_call_tool")
    @mock.patch.object(MODULE, "_load_identity")
    @mock.patch.object(MODULE, "_identity_path")
    def test_send_uses_managed_identity_and_disables_auto_contact(
        self,
        _identity_path: mock.Mock,
        load_identity: mock.Mock,
        call_tool: mock.Mock,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            body_path = Path(directory) / "request.md"
            body_path.write_text("Please inspect the router.\n", encoding="utf-8")
            load_identity.return_value = {
                "AGENT_MAIL_PROJECT": "/tmp/project",
                "AGENT_MAIL_AGENT": "Datacube",
                "AGENT_MAIL_URL": "http://127.0.0.1:8766/api/",
                "_token": "secret-token",
            }
            call_tool.return_value = {"count": 1}
            with mock.patch("sys.stdout", new_callable=io.StringIO):
                with mock.patch.object(
                    sys,
                    "argv",
                    [
                        "agent_mail_auth.py",
                        "send",
                        "--to",
                        "Primus",
                        "--to",
                        "Primus",
                        "--subject",
                        "Router residency check",
                        "--body-file",
                        str(body_path),
                        "--importance",
                        "high",
                        "--ack-required",
                    ],
                ):
                    self.assertEqual(MODULE.main(), 0)

        tool_name, arguments = call_tool.call_args.args[1:]
        self.assertEqual(tool_name, "send_message")
        self.assertEqual(arguments["sender_token"], "secret-token")
        self.assertEqual(arguments["to"], ["Primus"])
        self.assertEqual(arguments["importance"], "high")
        self.assertTrue(arguments["ack_required"])
        self.assertFalse(arguments["auto_contact_if_blocked"])


if __name__ == "__main__":
    unittest.main()
