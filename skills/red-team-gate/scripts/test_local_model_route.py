#!/usr/bin/env python3
"""Regression tests for the Red-Team Gate's canonical local model route."""

from __future__ import annotations

import importlib.util
from importlib.machinery import SourceFileLoader
import os
from pathlib import Path
import subprocess
import sys


SKILL_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = SKILL_ROOT / "runtime" / "primus-local-v1"
BIN = RUNTIME_ROOT / "bin"
LIB = RUNTIME_ROOT / "lib"
CANONICAL_MODEL = "local-inference-11888"


def load_checker_module():
    sys.path.insert(0, str(LIB))
    loader = SourceFileLoader(
        "primus_adversarial_code_checker_for_route_test",
        str(BIN / "primus-adversarial-code-checker"),
    )
    spec = importlib.util.spec_from_loader(loader.name, loader)
    if spec is None:
        raise AssertionError("could not load checker module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assert_rejects_model_override(executable: Path, arguments: list[str], variable: str) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(LIB)
    env[variable] = "Qwen3.8-4B-Empero-AI-FullStack.i1-Q6_K.gguf"
    result = subprocess.run(
        [sys.executable, str(executable), *arguments, "--local"],
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert result.returncode != 0, f"{executable.name} accepted a 4B local model override"
    combined = result.stdout + result.stderr
    assert "local Red-Team Gate inference must use 'local-inference-11888'" in combined


def main() -> int:
    checker = load_checker_module()
    good = {
        "router_url": "http://127.0.0.1:11888/v1",
        "model_alias": CANONICAL_MODEL,
        "route_header_consistent": True,
        "adapter_identity_verified": True,
        "request_id": "request-1",
        "cloud_used": False,
        "truncated": False,
    }
    assert checker.local_router_route_evidence_is_valid(good)
    bad = dict(good, model_alias="Qwen3.8-4B-Empero-AI-FullStack.i1-Q6_K.gguf")
    assert not checker.local_router_route_evidence_is_valid(bad)

    # A live prompt-processing slot may hold its counters steady for several
    # polls.  It is slow work, not a transport failure, and must not be killed
    # by the evidence watcher.
    slow_processing = {
        "active_global": 1,
        "active_user": 1,
        "queued_global": 0,
        "queued_user": 0,
        "worker_busy": 1,
        "slot_busy": 1,
        "requests_processing": 1,
    }
    assert not checker._transport_ambiguity_confirmed(
        slow_processing,
        activity_seen=True,
        idle_observations=checker.EVIDENCE_IDLE_PROBES_REQUIRED,
        request_thread_alive=True,
    )
    released_without_response = {
        "active_global": 0,
        "active_user": 0,
        "queued_global": 0,
        "queued_user": 0,
        "worker_busy": 0,
        "slot_busy": 0,
        "requests_processing": 0,
        "requests_deferred": 0,
    }
    assert checker._transport_ambiguity_confirmed(
        released_without_response,
        activity_seen=True,
        idle_observations=checker.EVIDENCE_IDLE_PROBES_REQUIRED,
        request_thread_alive=True,
    )
    assert not checker._transport_ambiguity_confirmed(
        released_without_response,
        activity_seen=False,
        idle_observations=checker.EVIDENCE_IDLE_PROBES_REQUIRED,
        request_thread_alive=True,
    )

    assert_rejects_model_override(
        BIN / "primus-adversarial-code-checker",
        ["--input", "/dev/null"],
        "PRIMUS_CHECKER_MODEL",
    )
    assert_rejects_model_override(
        BIN / "primus-general-code-review",
        [
            "--config",
            "/dev/null",
            "--input",
            "/dev/null",
            "--output",
            "/dev/null",
            "--raw-dir",
            "/tmp",
        ],
        "PRIMUS_GRUMPY_MODEL",
    )
    assert_rejects_model_override(
        BIN / "primus-grumpy-reviewer",
        ["--input", "/dev/null"],
        "PRIMUS_GRUMPY_MODEL",
    )
    assert_rejects_model_override(
        BIN / "primus-grumpy-fast-checker",
        ["--input", "/dev/null"],
        "PRIMUS_GRUMPY_MODEL",
    )
    print("local-model-route: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
