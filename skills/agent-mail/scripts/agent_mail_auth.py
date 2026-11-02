#!/usr/bin/env python3
"""Managed-identity, loopback-only Agent Mail operations.

This helper intentionally exposes only the routine operations used by the
shared Agent Mail skill.  It never accepts a credential as an argument, never
logs a request body, and rejects non-loopback endpoints.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import socket
import sys
import uuid
from pathlib import Path
from typing import Any
from urllib import error, request
from urllib.parse import urlsplit


_IDENTITY_FIELDS = {
    "AGENT_MAIL_AGENT",
    "AGENT_MAIL_PROJECT",
    "AGENT_MAIL_REGISTRATION_TOKEN",
    "AGENT_MAIL_TOKEN",
    "AGENT_MAIL_URL",
}
_SECRET_FIELD_MARKERS = ("token", "secret", "authorization", "password", "credential")
_LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}
_DEFAULT_DATACUBE_IDENTITY = Path(
    "/mnt/f/Production/antigravity/runtime/mcp_agent_mail.codex.identity.env"
)


class AgentMailAuthError(RuntimeError):
    """An identity or transport precondition was not met."""


def _identity_path() -> Path:
    configured = os.environ.get("ANTIGRAVITY_AGENT_MAIL_IDENTITY_ENV", "").strip()
    if configured:
        return Path(configured)
    host = socket.gethostname().split(".", 1)[0].lower()
    if host.startswith("datacube"):
        return _DEFAULT_DATACUBE_IDENTITY
    raise AgentMailAuthError("managed Agent Mail identity path is not configured for this host")


def _parse_identity_value(raw: str) -> str:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        try:
            parts = shlex.split(raw, posix=True)
        except ValueError as exc:
            raise AgentMailAuthError("managed Agent Mail identity is malformed") from exc
        if len(parts) != 1:
            raise AgentMailAuthError("managed Agent Mail identity is malformed")
        value = parts[0]
    if not isinstance(value, str):
        raise AgentMailAuthError("managed Agent Mail identity is malformed")
    return value


def _load_identity(path: Path) -> dict[str, str]:
    try:
        stat_result = path.stat()
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise AgentMailAuthError("managed Agent Mail identity is unavailable") from exc
    if not path.is_file() or stat_result.st_mode & 0o007:
        raise AgentMailAuthError("managed Agent Mail identity permissions are unsafe")

    identity: dict[str, str] = {}
    for raw_line in lines:
        line = raw_line.strip()
        if not line.startswith("export "):
            continue
        assignment = line[len("export ") :]
        if "=" not in assignment:
            continue
        key, raw_value = assignment.split("=", 1)
        key = key.strip()
        if key in _IDENTITY_FIELDS:
            identity[key] = _parse_identity_value(raw_value.strip())

    token = identity.get("AGENT_MAIL_REGISTRATION_TOKEN") or identity.get("AGENT_MAIL_TOKEN")
    if not identity.get("AGENT_MAIL_PROJECT") or not identity.get("AGENT_MAIL_AGENT") or not token:
        raise AgentMailAuthError("managed Agent Mail identity is incomplete")
    if not identity.get("AGENT_MAIL_URL"):
        raise AgentMailAuthError("managed Agent Mail endpoint is missing")
    identity["_token"] = token
    return identity


def _require_loopback_api(url: str) -> str:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or parsed.hostname not in _LOOPBACK_HOSTS:
        raise AgentMailAuthError("managed Agent Mail endpoint is not loopback")
    path = parsed.path.rstrip("/")
    if path not in {"/api", "/mcp"}:
        raise AgentMailAuthError("managed Agent Mail endpoint is not an MCP API path")
    return url


def _redact(value: Any, secrets: tuple[str, ...] = ()) -> Any:
    if isinstance(value, dict):
        return {
            str(key): "[redacted]"
            if any(marker in str(key).lower() for marker in _SECRET_FIELD_MARKERS)
            else _redact(item, secrets)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_redact(item, secrets) for item in value]
    if isinstance(value, str):
        redacted = value
        for secret in secrets:
            if secret:
                redacted = redacted.replace(secret, "[redacted]")
        return redacted
    return value


def _truncate_bodies(value: Any, max_chars: int) -> Any:
    if isinstance(value, dict):
        trimmed: dict[str, Any] = {}
        for key, item in value.items():
            if key in {"body", "body_md", "body_excerpt"} and isinstance(item, str) and len(item) > max_chars:
                trimmed[key] = item[:max_chars].rstrip() + "\n[truncated]"
            else:
                trimmed[key] = _truncate_bodies(item, max_chars)
        return trimmed
    if isinstance(value, list):
        return [_truncate_bodies(item, max_chars) for item in value]
    return value


def _tool_error_detail(result: dict[str, Any], secrets: tuple[str, ...]) -> str:
    for item in result.get("content") or []:
        if not isinstance(item, dict) or item.get("type") != "text":
            continue
        detail = _redact(str(item.get("text") or "").strip(), secrets)
        if detail:
            return " ".join(detail.split())[:500]
    structured = result.get("structuredContent")
    if isinstance(structured, dict):
        code = str(structured.get("code") or "").strip()
        message = str(structured.get("message") or "").strip()
        detail = _redact(" ".join(value for value in (code, message) if value), secrets)
        if detail:
            return " ".join(detail.split())[:500]
    return ""


def _tool_result(payload: dict[str, Any], *, secrets: tuple[str, ...] = ()) -> Any:
    result = payload.get("result")
    if not isinstance(result, dict):
        raise AgentMailAuthError("Agent Mail returned an invalid response")
    if result.get("isError"):
        detail = _tool_error_detail(result, secrets)
        suffix = f": {detail}" if detail else ""
        raise AgentMailAuthError(f"Agent Mail rejected the requested operation{suffix}")
    structured = result.get("structuredContent")
    if structured is not None:
        return structured
    for item in result.get("content") or []:
        if not isinstance(item, dict) or item.get("type") != "text":
            continue
        text = str(item.get("text") or "").strip()
        if not text:
            continue
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text
    return result


def _resource_result(payload: dict[str, Any], *, secrets: tuple[str, ...] = ()) -> Any:
    result = payload.get("result")
    if not isinstance(result, dict):
        raise AgentMailAuthError("Agent Mail returned an invalid resource response")
    if result.get("isError"):
        detail = _tool_error_detail(result, secrets)
        suffix = f": {detail}" if detail else ""
        raise AgentMailAuthError(f"Agent Mail rejected the resource request{suffix}")
    for item in result.get("contents") or []:
        if not isinstance(item, dict) or not isinstance(item.get("text"), str):
            continue
        try:
            return json.loads(item["text"])
        except json.JSONDecodeError:
            return item["text"]
    raise AgentMailAuthError("Agent Mail returned an empty resource response")


def _call_tool(identity: dict[str, str], tool_name: str, arguments: dict[str, Any]) -> Any:
    endpoint = _require_loopback_api(identity["AGENT_MAIL_URL"])
    payload = {
        "jsonrpc": "2.0",
        # A JSON-RPC id identifies a single request.  Reusing it can let an
        # intermediary replay a prior inbox response, which is unsafe for
        # coordination intake.
        "id": f"agent-mail-managed-cli-{uuid.uuid4().hex}",
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
    }
    encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        endpoint,
        data=encoded,
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=5) as response:
            raw = response.read().decode("utf-8")
    except (error.HTTPError, error.URLError, TimeoutError, OSError) as exc:
        raise AgentMailAuthError("managed Agent Mail request failed") from exc
    try:
        response_payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AgentMailAuthError("Agent Mail returned an invalid response") from exc
    return _tool_result(response_payload, secrets=(identity.get("_token", ""),))


def _call_resource(identity: dict[str, str], uri: str) -> Any:
    endpoint = _require_loopback_api(identity["AGENT_MAIL_URL"])
    payload = {
        "jsonrpc": "2.0",
        "id": f"agent-mail-managed-cli-{uuid.uuid4().hex}",
        "method": "resources/read",
        "params": {"uri": uri},
    }
    encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        endpoint,
        data=encoded,
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=5) as response:
            raw = response.read().decode("utf-8")
    except (error.HTTPError, error.URLError, TimeoutError, OSError) as exc:
        raise AgentMailAuthError("managed Agent Mail resource request failed") from exc
    try:
        response_payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AgentMailAuthError("Agent Mail returned an invalid resource response") from exc
    return _resource_result(response_payload, secrets=(identity.get("_token", ""),))


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("value must be positive")
    return parsed


def _body_from_file(path: Path) -> str:
    try:
        if not path.is_file():
            raise OSError("not a regular file")
        body = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise AgentMailAuthError("message body file is unavailable") from exc
    if not body.strip() or len(body) > 12000:
        raise AgentMailAuthError("message body must contain 1 to 12000 characters")
    return body


def _recipient_name(value: str) -> str:
    name = value.strip()
    if not name or len(name) > 128 or any(character.isspace() for character in name):
        raise argparse.ArgumentTypeError("recipient must be a nonempty Agent Mail name")
    return name


def _subject(value: str) -> str:
    subject = value.strip()
    if not subject or len(subject) > 160 or "\n" in subject or "\r" in subject:
        raise argparse.ArgumentTypeError("subject must contain 1 to 160 characters on one line")
    return subject


def _topic(value: str) -> str:
    topic = value.strip()
    if (
        not topic
        or len(topic) > 64
        or not all(character.isascii() and (character.isalnum() or character in "-_") for character in topic)
    ):
        raise argparse.ArgumentTypeError("topic must be 1 to 64 letters, digits, hyphens, or underscores")
    return topic


def _project_slug(project_key: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", project_key.strip().lower()).strip("-")
    return slug or "project"


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Managed-identity Agent Mail operations")
    subparsers = parser.add_subparsers(dest="operation", required=True)

    inbox = subparsers.add_parser("inbox", help="Read the authenticated inbox")
    inbox.add_argument("--limit", type=_positive_int, default=20)
    inbox.add_argument("--urgent-only", action="store_true")
    inbox.add_argument("--include-bodies", action="store_true")
    inbox.add_argument("--max-body-chars", type=_positive_int, default=2400)
    inbox.add_argument("--since", dest="since_ts", metavar="ISO_8601")

    subparsers.add_parser("agents", help="List agents registered in the active project")

    contact_request = subparsers.add_parser(
        "contact-request",
        help="Request another registered agent's approval for contact",
    )
    contact_request.add_argument("--to", type=_recipient_name, required=True)
    contact_request.add_argument("--reason-file", type=Path, required=True)
    contact_request.add_argument("--ttl-seconds", type=_positive_int, default=7 * 24 * 3600)

    reply = subparsers.add_parser("reply", help="Reply in an existing Agent Mail thread")
    reply.add_argument("--message-id", type=_positive_int, required=True)
    reply.add_argument("--body-file", type=Path, required=True)

    send = subparsers.add_parser("send", help="Send a new authoritative Agent Mail message")
    send.add_argument("--to", type=_recipient_name, action="append", required=True)
    send.add_argument("--subject", type=_subject, required=True)
    send.add_argument("--body-file", type=Path, required=True)
    send.add_argument("--importance", choices=("low", "normal", "high", "urgent"), default="normal")
    send.add_argument("--ack-required", action="store_true")
    send.add_argument("--topic", type=_topic)

    ack = subparsers.add_parser("ack", help="Acknowledge a handled Agent Mail message")
    ack.add_argument("--message-id", type=_positive_int, required=True)

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    try:
        identity = _load_identity(_identity_path())
        common = {
            "project_key": identity["AGENT_MAIL_PROJECT"],
            "agent_name": identity["AGENT_MAIL_AGENT"],
        }
        if args.operation == "inbox":
            result = _call_tool(
                identity,
                "fetch_inbox",
                {
                    **common,
                    "registration_token": identity["_token"],
                    "limit": min(args.limit, 100),
                    "urgent_only": bool(args.urgent_only),
                    "include_bodies": bool(args.include_bodies),
                    **({"since_ts": args.since_ts} if args.since_ts else {}),
                },
            )
            if args.include_bodies:
                result = _truncate_bodies(result, min(args.max_body_chars, 10000))
        elif args.operation == "agents":
            result = _call_resource(
                identity,
                f"resource://agents/{_project_slug(identity['AGENT_MAIL_PROJECT'])}",
            )
        elif args.operation == "contact-request":
            result = _call_tool(
                identity,
                "request_contact",
                {
                    "project_key": common["project_key"],
                    "from_agent": common["agent_name"],
                    "to_agent": args.to,
                    "reason": _body_from_file(args.reason_file),
                    "ttl_seconds": args.ttl_seconds,
                    "registration_token": identity["_token"],
                    "register_if_missing": False,
                },
            )
        elif args.operation == "reply":
            result = _call_tool(
                identity,
                "reply_message",
                {
                    "project_key": common["project_key"],
                    "message_id": args.message_id,
                    "sender_name": common["agent_name"],
                    "sender_token": identity["_token"],
                    "body_md": _body_from_file(args.body_file),
                },
            )
        elif args.operation == "send":
            recipients = list(dict.fromkeys(args.to))
            if len(recipients) > 5:
                raise AgentMailAuthError("send accepts at most five explicit recipients")
            result = _call_tool(
                identity,
                "send_message",
                {
                    "project_key": common["project_key"],
                    "sender_name": common["agent_name"],
                    "sender_token": identity["_token"],
                    "to": recipients,
                    "subject": args.subject,
                    "body_md": _body_from_file(args.body_file),
                    "importance": args.importance,
                    "ack_required": bool(args.ack_required),
                    "auto_contact_if_blocked": False,
                    **({"topic": args.topic} if args.topic else {}),
                },
            )
        else:
            result = _call_tool(
                identity,
                "acknowledge_message",
                {
                    **common,
                    "registration_token": identity["_token"],
                    "message_id": args.message_id,
                },
            )
    except AgentMailAuthError as exc:
        print(f"agent-mail: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(_redact(result, (identity["_token"],)), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
