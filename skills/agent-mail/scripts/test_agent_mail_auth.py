from __future__ import annotations

import importlib.util
import json
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


if __name__ == "__main__":
    unittest.main()
