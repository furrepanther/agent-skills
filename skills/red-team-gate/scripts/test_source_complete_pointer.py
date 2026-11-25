#!/usr/bin/env python3
"""Regression proof for large source-complete pointer-backed review packets."""

from __future__ import annotations

import importlib.machinery
import importlib.util
import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime" / "primus-local-v1"
LIB = RUNTIME / "lib"
ENTRYPOINT = RUNTIME / "bin" / "primus-general-code-review"
sys.path.insert(0, str(LIB))
loader = importlib.machinery.SourceFileLoader("primus_general_code_review_test", str(ENTRYPOINT))
spec = importlib.util.spec_from_loader(loader.name, loader)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[loader.name] = module
spec.loader.exec_module(module)


def main() -> int:
    client_type = module._load_common_mcp_client()
    client_origin = Path(sys.modules[client_type.__module__].__file__).resolve()
    assert client_origin.name == "common_mcp_client.py"

    captured = {}
    module._common_mcp_memory_call = lambda tool, payload: (
        captured.update({"tool": tool, "payload": payload})
        or {"status": "complete", "memory_id": "entry-1", "entry_id": "entry-1"}
    )
    module._write_temporary_evidence_via_async_mcp(
        content="evidence",
        metadata={},
        idempotency_key="idempotency-1",
    )
    assert captured["tool"] == "memory_store"
    assert "idempotency_key" not in captured["payload"]
    assert captured["payload"]["metadata"]["idempotency_key"] == "idempotency-1"

    captured.clear()
    module._memory_async_status("job-1")
    assert captured == {
        "tool": "memory_write_async_status",
        "payload": {"job_id": "job-1"},
    }

    delete_capture = {}
    module._memory_api_json = lambda path, payload: (
        delete_capture.update({"path": path, "payload": payload})
        or {"deleted": True, "found": True}
    )
    module._memory_delete_exact(memory_id="mem-1", entry_id="entry-1")
    assert delete_capture == {
        "path": "/memory/delete",
        "payload": {
            "memory_id": "mem-1",
            "entry_id": "entry-1",
            "user_id": "global",
            "reason": "temporary review evidence no longer needed",
            "origin_tool": "primus-general-code-review",
        },
    }

    # Compact lane transport may retain the exact proof fields while omitting
    # the redundant record_kind/canonical fields. The exact record metadata is
    # the authoritative proof and must still validate without widening scope.
    saved_exact_result = module._memory_exact_result
    try:
        module._memory_exact_result = lambda memory_id, lookup_query="": {
            "memory_id": memory_id,
            "entry_id": memory_id,
            "metadata": {
                "temporary": True,
                "canonical": False,
                "retention_verified": True,
                "content_sha256": "c" * 64,
                "packet_sha256": "p" * 64,
                "purge_after_utc": "2099-01-01T00:00:00Z",
            },
        }
        module.verify_temporary_evidence_pointer(
            {
                "memory_id": "mem-compact",
                "verified": True,
                "retention_verified": True,
                "content_sha256": "c" * 64,
                "packet_sha256": "p" * 64,
                "purge_after_utc": "2099-01-01T00:00:00Z",
            }
        )
    finally:
        module._memory_exact_result = saved_exact_result

    saved = {
        name: os.environ.get(name)
        for name in ("PRIMUS_MEMORY_API_URL", "ANTIGRAVITY_MEMORY_API_URL", "MEMORY_API_URL")
    }
    try:
        for name in saved:
            os.environ.pop(name, None)
        assert module.resolve_memory_api_url() == "http://127.0.0.1:8001"
        os.environ["PRIMUS_MEMORY_API_URL"] = "http://127.0.0.1:9123/"
        assert module.resolve_memory_api_url() == "http://127.0.0.1:9123"
        os.environ["PRIMUS_MEMORY_API_URL"] = "https://example.invalid:9123"
        try:
            module.resolve_memory_api_url()
        except ValueError:
            pass
        else:
            raise AssertionError("remote Memory Fabric endpoint was accepted")
    finally:
        for name, value in saved.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value

    chunks = module._split_temporary_evidence_content(
        "y" * (module.TEMP_EVIDENCE_CHUNK_PAYLOAD_MAX_CHARS * 17)
    )
    assert len(chunks) == 17
    assert len(chunks) <= module.MAX_TEMP_EVIDENCE_CHUNKS

    content = "source-bytes\n" + ("x" * 20_000)
    digest = module._source_content_sha256(content, "repo/example.py")
    artifact = {
        "path": "repo/example.py",
        "content": content,
        "file_sha256_full": digest,
        "size_bytes": len(content.encode("utf-8")),
    }
    packet = {
        "TASK": "large source packet",
        "ACCEPTANCE_CRITERIA": ["pointer transport is reachable"],
        "DIFF_OR_FILES": ["repo/example.py"],
        "TESTS": ["pointer regression"],
        "KNOWN_CONSTRAINTS": ["local-only"],
        "OUT_OF_SCOPE": ["deployment"],
        "PROVENANCE": {
            "require_temporary_evidence_pointer": True,
            "artifact_refs": [artifact["path"]],
        },
        "FULL_ARTIFACTS": [artifact],
        "SOURCE_ARTIFACTS": [artifact],
    }
    source_artifacts, source_delivery = module._source_artifacts_from_full_artifacts(packet)
    assert source_artifacts is not None and source_delivery is not None
    packet["PROVENANCE"]["source_delivery"] = source_delivery
    pointer = {
        "memory_id": "temporary-review-regression",
        "record_kind": "temporary_review_evidence",
        "verified": True,
        "retention_verified": True,
        "content_sha256": "a" * 64,
        "packet_sha256": "b" * 64,
    }
    module.write_temporary_evidence_record = lambda _packet: dict(pointer)
    module.verify_temporary_evidence_pointer = lambda _pointer: None

    result = module.ensure_temporary_evidence_pointer(packet, 12_000)
    provenance = result["PROVENANCE"]
    assert "SOURCE_ARTIFACTS" not in result
    assert provenance["full_artifacts_transport"]["transport"] == "pointer_backed_complete_bytes"
    assert provenance["temporary_evidence_pointer"]["memory_id"] == pointer["memory_id"]

    compact_pointer = module.compact_packet_section_for_key(
        "PROVENANCE",
        {
            **provenance,
            "temporary_evidence_pointer": {
                **provenance["temporary_evidence_pointer"],
                "record_kind": "temporary_review_evidence",
                "canonical": False,
                "storage_format": module.TEMP_EVIDENCE_CHUNK_MANIFEST_SCHEMA,
                "chunk_count": 3,
                "manifest_content_sha256": "m" * 64,
                "packet_sha256": "b" * 64,
                "source_packet_sha256_scope": "temporary_memory_record",
                "packet_sha256_scope": "temporary_memory_record",
                "purge_after_utc": "2099-01-01T00:00:00Z",
            },
        },
        850,
    )
    compact_pointer_fields = compact_pointer["temporary_evidence_pointer"]
    assert compact_pointer_fields["storage_format"] == module.TEMP_EVIDENCE_CHUNK_MANIFEST_SCHEMA
    assert compact_pointer_fields["chunk_count"] == 3
    assert compact_pointer_fields["manifest_content_sha256"] == "m" * 64

    pages = module._source_review_pages_from_artifacts(result["FULL_ARTIFACTS"])
    assert len(pages) > 1
    samples, samples_sha256 = module._source_file_samples_from_artifacts(result["FULL_ARTIFACTS"])
    page_packet = module._attach_source_review_page(
        result,
        pointer=provenance["temporary_evidence_pointer"],
        source_page=pages[0],
        source_samples=samples,
        source_samples_sha256=samples_sha256,
        lane_id="source-page-regression",
    )
    module.validate_source_review_page_delivery(page_packet)
    module.validate_source_file_sample_delivery(page_packet)
    assert page_packet["SOURCE_FILE_SAMPLES"].startswith("0\t")
    assert page_packet["SOURCE_DELIVERY"]["file_sample_bytes_per_file"] == 32
    assert page_packet["SOURCE_DELIVERY"]["file_sample_total_bytes"] == len(
        samples[0]["sample"].encode("utf-8")
    )
    assert page_packet["SOURCE_DELIVERY"]["file_sha256_full_order"] == "SOURCE_FILE_SAMPLES.path_order"
    assert len(page_packet["SOURCE_DELIVERY"]["file_sha256_full"][0]) == 64

    multi_page_packet = module._attach_source_review_page(
        result,
        pointer=provenance["temporary_evidence_pointer"],
        source_page=pages[0],
        source_pages=pages[:2],
        source_samples=samples,
        source_samples_sha256=samples_sha256,
        lane_id="multi-source-page-regression",
    )
    module.validate_source_review_page_delivery(multi_page_packet)
    assert len(multi_page_packet["SOURCE_PAGES"]) == 2
    assert len(multi_page_packet["SOURCE_DELIVERY"]["page_receipts"]) == 2
    compacted_multi = module.compact_single_lane_packet(
        result,
        12_000,
        source_page=pages[0],
        source_pages=pages[:2],
        source_samples=samples,
        source_samples_sha256=samples_sha256,
        lane_id="multi-source-page-regression",
    )
    module.validate_source_review_page_delivery(compacted_multi)
    assert "page_index" not in compacted_multi["SOURCE_DELIVERY"]
    assert len(compacted_multi["SOURCE_DELIVERY"]["page_receipts"]) == 2
    tampered = module.deep_copy_json(page_packet)
    tampered["SOURCE_FILE_SAMPLES"] = '{"path":"repo/wrong.py","sample":"source-by"}'
    try:
        module.validate_source_file_sample_delivery(tampered)
    except ValueError:
        pass
    else:
        raise AssertionError("source sample path tampering was accepted")
    normalized, _, _ = module.checker_normalized_packet(page_packet)
    assert normalized["SOURCE_PAGES"][0]["content"] == pages[0]["content"]
    assert normalized["SOURCE_DELIVERY"]["reviewer_receipt"] is True
    assert module.checker_user_content_chars(page_packet) < 12_000

    indexed = module.compact_complete_evidence_packet(
        [
            {"path": "mcp-agent-mail/src/a.py", "diff": "return durable_failure"},
            {"path": "SimpleMem/MCP/server/http_server.py", "diff": "raise explicit_conflict"},
        ],
        2_000,
    )
    assert "prefix_table=m:mcp-agent-mail/|a:agent-mail-link/|s:SimpleMem/" in indexed
    assert "path=m:src/a.py" in indexed
    assert "path=s:MCP/server/http_server.py" in indexed
    assert "evidence=return durable_failure" in indexed

    scoped_gate = module._scope_lane_acceptance_criteria(
        {
            "ACCEPTANCE_CRITERIA": [
                {"criterion_id": "AC-001", "text": "source"},
                {"criterion_id": "AC-006", "text": "local router and Grumpy lane"},
            ],
            "EVIDENCE": [
                {"id": "EV-1", "criterion_id": "AC-001", "status": "pass"},
                {"id": "EV-6", "criterion_id": "AC-006", "status": "pass"},
            ],
            "TESTS": [
                "T-001 criterion=AC-001 assertion=source pass",
                "T-006 criterion=AC-006 assertion=router pass",
            ],
        }
    )
    assert [row["criterion_id"] for row in scoped_gate["ACCEPTANCE_CRITERIA"]] == ["AC-001"]
    assert [row["id"] for row in scoped_gate["EVIDENCE"]] == ["EV-1"]
    assert scoped_gate["TESTS"] == ["T-001 criterion=AC-001 assertion=source pass"]

    complete_tests = [
        "T-001 criterion=AC-001 assertion=builder rejects incomplete or mismatched artifact bytes; source-complete-pointer verifies exact pointer, page, sample, and digest receipts; observed=pass",
        "T-002 criterion=AC-002 assertion=identity, peer-token, routing, contact, and notification negative tests reject stale or ambiguous state without replacement identity creation; observed=pass",
    ]
    retained_tests = module.compact_tests_evidence(complete_tests, 1_600)
    assert retained_tests == complete_tests
    assert "..." not in json.dumps(retained_tests)
    compacted_tests = module.compact_tests_evidence(complete_tests * 4, 500)
    assert all(
        isinstance(row, str)
        and row.startswith("T")
        and " assertion=" in row
        and "; observed=" in row
        for row in compacted_tests
    )

    path_index = module.compact_complete_evidence_packet(
        ["mcp-agent-mail/src/a.py", "SimpleMem/MCP/server/http_server.py"],
        2_000,
    )
    rebound_path_index = module.compact_packet_section_for_key(
        "DIFF_OR_FILES", path_index, 1_200
    )
    assert rebound_path_index.startswith("complete_path_index=yes;")
    assert module._source_paths_from_diff(rebound_path_index) == [
        "mcp-agent-mail/src/a.py",
        "SimpleMem/MCP/server/http_server.py",
    ]

    absolute_path = "/mnt/linuxdata/Github/.worktrees/example/src/bridge.py"
    absolute_index = module.compact_complete_evidence_packet([absolute_path], 2_000)
    assert "prefix_table=" in absolute_index and "x:" in absolute_index
    assert module._source_paths_from_diff(absolute_index) == [absolute_path]

    scoped = module.deep_copy_json(page_packet)
    scoped["DIFF_OR_FILES"] = ["repo/example.py"]
    scoped_page = module._attach_source_review_page(
        scoped,
        pointer=provenance["temporary_evidence_pointer"],
        source_page=pages[0],
        source_samples=samples,
        source_samples_sha256=samples_sha256,
        lane_id="scoped-source-regression",
    )
    assert scoped_page["SOURCE_DELIVERY"]["file_sample_count"] == 1
    module.validate_source_file_sample_delivery(scoped_page)

    # A lane can select a non-prefix subset of the complete changed-file
    # index. The serialized row must retain its authoritative full-index
    # position instead of being renumbered and rebound to the first entry.
    non_prefix_samples = [{"path": "repo/third.py", "sample": "third-bytes"}]
    non_prefix_wire = module._serialize_source_file_samples(
        non_prefix_samples,
        artifact_paths=["repo/first.py", "repo/second.py", "repo/third.py"],
    )
    assert non_prefix_wire.startswith("2\t")
    assert module._parse_source_file_samples(
        non_prefix_wire,
        artifact_paths=["repo/first.py", "repo/second.py", "repo/third.py"],
    ) == non_prefix_samples

    grumpy_with_page = module.build_grumpy_packet(
        page_packet,
        [],
        1_800,
        500,
        120,
    )
    assert isinstance(grumpy_with_page["DIFF_OR_FILES"], str)
    assert grumpy_with_page["SOURCE_DELIVERY"]["reviewer_receipt"] is True

    near_ceiling_lanes = [
        {
            "lane_id": f"lane-{index}",
            "status": "evidence_failure",
            "decision": "block",
            "blocking_findings": 1,
            "parse_error": "bounded local review evidence unavailable",
            "route_evidence": {"router_url": "http://127.0.0.1:11888/v1"},
        }
        for index in range(6)
    ]
    near_ceiling = module.build_grumpy_packet(
        page_packet,
        near_ceiling_lanes,
        12_000,
        12_000,
        1_200,
    )
    fitted = module.fit_grumpy_packet_to_budget(near_ceiling, 12_000)
    assert module.checker_user_content_chars(fitted) <= 12_000

    # A transport complaint may coexist with an independent substantive
    # blocker. Only the transport finding is cleared; the real blocker stays.
    mixed_result = {
        "merge_decision": {"decision": "block"},
        "findings": [
            {
                "id": "transport",
                "blocking": True,
                "location": "SOURCE_PAGES",
                "observed_evidence": "only one source page is visible",
                "required_fix": "provide verified pointer hydration for complete source bytes",
            },
            {
                "id": "real",
                "blocking": True,
                "location": "runtime behavior",
                "observed_evidence": "replay can duplicate a delivery",
                "required_fix": "add an idempotency assertion",
            },
        ],
    }
    assert not module.pointer_only_evidence_block(mixed_result, page_packet)
    assert module.resolve_verified_pointer_transport_block(mixed_result, page_packet)
    assert mixed_result["findings"][0]["blocking"] is False
    assert mixed_result["findings"][1]["blocking"] is True
    assert mixed_result["merge_decision"]["decision"] == "block"

    sample_transport_result = {
        "merge_decision": {"decision": "insufficient_evidence"},
        "findings": [
            {
                "blocking": False,
                "location": "review_packet.SOURCE_FILE_SAMPLES",
                "observed_evidence": "Samples are truncated to 32 bytes per file.",
                "required_fix": "Cross-reference the full source bytes in the temporary Memory Fabric pointer.",
            }
        ],
    }
    assert module.pointer_only_evidence_block(sample_transport_result, page_packet)
    assert module.resolve_verified_pointer_transport_block(sample_transport_result, page_packet)
    assert sample_transport_result["merge_decision"]["decision"] == "no_blocking_defect_found"

    rows = module.compact_tests_evidence(
        [
            "T-001 AC-001 complete source receipt PASS",
            "T-002 AC-002 stale identity rejected PASS",
        ],
        500,
    )
    assert isinstance(rows, list)
    assert rows[0].startswith("T-001")
    assert rows[1].startswith("T-002")

    evidence_rows = module.compact_evidence_ledger(
        [
            {
                "id": "EV-1",
                "criterion_id": "AC-1",
                "status": "pass",
                "artifact_ref": "mcp-agent-mail/src/mcp_agent_mail/app.py",
                "test_or_locus": "identity regression",
                "observed_outcome": "exact receipt",
            }
        ],
        260,
    )
    assert len(module.json.dumps(evidence_rows, separators=(",", ":"))) <= 260
    assert evidence_rows[0]["artifact_ref"] == "mcp-agent-mail/src/mcp_agent_mail/app.py"
    assert "..." not in evidence_rows[0]["artifact_ref"]

    route_packet = module._attach_gate_execution_evidence(
        {"TASK": "route-growth-regression"},
        lane_id="lane-2",
        prior_route_receipts=[{"route": "x" * 5000} for _ in range(20)],
    )
    assert route_packet["GATE_EXECUTION_EVIDENCE"]["prior_lane_count"] == 20
    assert "prior_lane_route_receipts" not in route_packet["GATE_EXECUTION_EVIDENCE"]

    snapshot = module.snapshot_authoritative_grumpy_packet(result)
    assert "SOURCE_ARTIFACTS" not in snapshot
    grumpy = module.build_grumpy_packet(result, [], 1_800, 500, 120)
    assert "SOURCE_ARTIFACTS" not in grumpy
    print("source-complete-pointer: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
