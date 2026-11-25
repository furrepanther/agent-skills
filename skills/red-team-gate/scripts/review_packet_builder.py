#!/usr/bin/env python3
"""Build and validate a Red-Team-Gate packet before reviewer dispatch.

This is a dependency-free local fallback for review packages that do not ship
their own typed packet builder. It treats the input as an unattested draft and
emits one canonical, attested JSON packet only after schema, semantic,
provenance, artifact, and serialized-size checks pass.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


BUILDER_VERSION = "red-team-gate-packet-builder-v1"
DEFAULT_WIRE_LIMIT = 16384
DEFAULT_STORAGE_LIMIT = 120000
REQUIRED_FIELDS = (
    "TASK",
    "ACCEPTANCE_CRITERIA",
    "DIFF_OR_FILES",
    "TESTS",
    "EVIDENCE",
    "KNOWN_CONSTRAINTS",
    "OUT_OF_SCOPE",
    "PROVENANCE",
)
OPTIONAL_FIELDS = {"FULL_ARTIFACTS", "findings"}
BUILDER_FIELDS = {
    "provenance_verified",
    "complete_packet",
    "pointer_verified",
    "cleanup_verified",
    "empty_boat",
    "source_packet_sha256",
    "packet_sha256",
    "wire_sha256",
    "pointer_required",
    "wire_size_policy",
    "wire_size_status",
    "builder_version",
    "gate_state",
}
ALIASES = {
    "implementation_files",
    "implementation_scope",
    "tests",
    "provenance",
}
EVIDENCE_FIELDS = {
    "id",
    "criterion_id",
    "test_or_locus",
    "input_boundary",
    "observed_outcome",
    "status",
    "artifact_ref",
}
OPTIONAL_EVIDENCE_FIELDS = {"blocker", "no_claim"}
CLEANUP_PROOF_FIELDS = {
    "status",
    "receipt_ref",
    "receipt_sha256_full",
    "target",
    "observed_absence",
    "record_cap",
    "byte_cap",
    "active_pointer_check",
    "post_delete_check",
    "recursive_tree_check",
    "recursive_tree_entry_count",
}
STATUSES = {"pass", "fail", "unknown"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class PacketError(ValueError):
    """A draft cannot safely cross the reviewer dispatch boundary."""


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def nonempty(value: Any, field: str) -> None:
    if value in (None, "", [], {}):
        raise PacketError(f"{field} is empty")


def text_value(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PacketError(f"{field} must be a non-empty string")
    return value.strip()


def text_list(value: Any, field: str) -> list[str]:
    nonempty(value, field)
    if isinstance(value, str):
        values = [value]
    elif isinstance(value, list):
        values = value
    else:
        raise PacketError(f"{field} must be a string or list")
    if not values or any(not isinstance(item, str) or not item.strip() for item in values):
        raise PacketError(f"{field} contains an empty or non-string item")
    return [item.strip() for item in values]


def criterion_ids(value: Any) -> list[str]:
    nonempty(value, "ACCEPTANCE_CRITERIA")
    if not isinstance(value, list):
        raise PacketError("ACCEPTANCE_CRITERIA must be a list")
    result: list[str] = []
    for index, item in enumerate(value, start=1):
        if isinstance(item, str):
            if not item.strip():
                raise PacketError(f"ACCEPTANCE_CRITERIA[{index - 1}] is empty")
            result.append(f"AC-{index:03d}")
            continue
        if not isinstance(item, dict):
            raise PacketError(f"ACCEPTANCE_CRITERIA[{index - 1}] must be a string or object")
        criterion_id = str(item.get("criterion_id") or item.get("id") or "").strip()
        description = item.get("text", item.get("description"))
        if not criterion_id or not isinstance(description, str) or not description.strip():
            raise PacketError(f"ACCEPTANCE_CRITERIA[{index - 1}] lacks stable id/text")
        result.append(criterion_id)
    if len(result) != len(set(result)):
        raise PacketError("ACCEPTANCE_CRITERIA contains duplicate criterion IDs")
    return result


def path_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if not isinstance(value, list):
        raise PacketError("DIFF_OR_FILES must be a string or list")
    paths: list[str] = []
    for index, item in enumerate(value):
        if isinstance(item, str):
            path = item.strip()
        elif isinstance(item, dict):
            path = str(item.get("path") or "").strip()
        else:
            raise PacketError(f"DIFF_OR_FILES[{index}] must be a string or object")
        if not path:
            raise PacketError(f"DIFF_OR_FILES[{index}] has no path")
        paths.append(path)
    return paths


def validate_inline_diff_payloads(draft: dict[str, Any]) -> None:
    """Require reviewable bytes when the packet does not carry full artifacts."""
    if draft.get("FULL_ARTIFACTS") is not None:
        return
    raw = draft["DIFF_OR_FILES"]
    if isinstance(raw, str):
        raise PacketError(
            "DIFF_OR_FILES path-only input requires FULL_ARTIFACTS or an inline diff/content payload"
        )
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise PacketError(
                f"DIFF_OR_FILES[{index}] requires an inline diff/content payload"
            )
        payloads = []
        for field in ("diff", "content"):
            if field not in item:
                continue
            value = item[field]
            if not isinstance(value, str) or not value.strip():
                raise PacketError(f"DIFF_OR_FILES[{index}].{field} is empty or not text")
            payloads.append(value)
        if not payloads:
            raise PacketError(
                f"DIFF_OR_FILES[{index}] requires an inline diff/content payload"
            )


def validate_artifacts(draft: dict[str, Any], provenance: dict[str, Any]) -> None:
    artifacts = draft.get("FULL_ARTIFACTS")
    if artifacts is None:
        return
    if not isinstance(artifacts, list) or not artifacts:
        raise PacketError("FULL_ARTIFACTS must be a non-empty list when present")
    refs = provenance.get("artifact_refs")
    if not isinstance(refs, list) or not refs:
        raise PacketError("PROVENANCE.artifact_refs must cover FULL_ARTIFACTS")
    paths: list[str] = []
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict):
            raise PacketError(f"FULL_ARTIFACTS[{index}] must be an object")
        path = str(artifact.get("path") or "").strip()
        digest = str(artifact.get("file_sha256_full") or "").strip().lower()
        if not path or not SHA256_RE.fullmatch(digest):
            raise PacketError(f"FULL_ARTIFACTS[{index}] requires path and full SHA-256")
        paths.append(path)
        if "content" not in artifact or not isinstance(artifact["content"], str):
            raise PacketError(
                f"FULL_ARTIFACTS[{index}] requires complete UTF-8 content bytes"
            )
        content = artifact["content"]
        actual = hashlib.sha256(content.encode("utf-8")).hexdigest()
        if actual != digest:
            raise PacketError(f"FULL_ARTIFACTS[{index}] digest does not match content")
        declared_size = artifact.get("size_bytes")
        if declared_size is not None and declared_size != len(content.encode("utf-8")):
            raise PacketError(f"FULL_ARTIFACTS[{index}] size does not match content")
    if len(paths) != len(set(paths)):
        raise PacketError("FULL_ARTIFACTS contains duplicate paths")
    if set(paths) != {str(ref).strip() for ref in refs}:
        raise PacketError("PROVENANCE.artifact_refs does not exactly cover FULL_ARTIFACTS")


def validate_cleanup_proof(provenance: dict[str, Any]) -> bool:
    """Validate an optional draft-only proof for bounded temporary cleanup.

    The builder owns the resulting attestation flag.  The proof is only a
    typed claim tied to a reviewable receipt; the reviewer still verifies the
    referenced receipt and its exact target/absence evidence.
    """
    proof = provenance.get("cleanup_proof")
    if proof is None:
        return False
    if not isinstance(proof, dict):
        raise PacketError("PROVENANCE.cleanup_proof must be an object")
    unknown = set(proof) - CLEANUP_PROOF_FIELDS
    if unknown:
        raise PacketError(
            "PROVENANCE.cleanup_proof has unknown fields: "
            + ", ".join(sorted(unknown))
        )
    required = {
        "status",
        "receipt_ref",
        "receipt_sha256_full",
        "target",
        "observed_absence",
        "record_cap",
        "byte_cap",
        "active_pointer_check",
        "post_delete_check",
        "recursive_tree_check",
        "recursive_tree_entry_count",
    }
    missing = sorted(required - set(proof))
    if missing:
        raise PacketError(
            "PROVENANCE.cleanup_proof missing: " + ", ".join(missing)
        )
    if proof["status"] != "pass":
        raise PacketError("PROVENANCE.cleanup_proof.status must be pass")
    receipt_ref = proof["receipt_ref"]
    if not isinstance(receipt_ref, str) or not receipt_ref.strip():
        raise PacketError("PROVENANCE.cleanup_proof.receipt_ref is empty or not text")
    refs = {str(ref).strip() for ref in provenance.get("artifact_refs", [])}
    if not receipt_ref.startswith("inline:") and receipt_ref.strip() not in refs:
        raise PacketError(
            "PROVENANCE.cleanup_proof.receipt_ref is not inline or listed in artifact_refs"
        )
    digest = proof["receipt_sha256_full"]
    if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest.lower()):
        raise PacketError(
            "PROVENANCE.cleanup_proof.receipt_sha256_full must be a full SHA-256"
        )
    text_value(proof["target"], "PROVENANCE.cleanup_proof.target")
    absence = proof["observed_absence"]
    if (
        not isinstance(absence, list)
        or not absence
        or any(not isinstance(item, str) or not item.strip() for item in absence)
        or len({item.strip() for item in absence}) != len(absence)
    ):
        raise PacketError(
            "PROVENANCE.cleanup_proof.observed_absence must be unique non-empty paths"
        )
    for field in ("record_cap", "byte_cap"):
        value = proof[field]
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise PacketError(
                f"PROVENANCE.cleanup_proof.{field} must be a positive integer"
            )
    for field in ("active_pointer_check", "post_delete_check"):
        if proof[field] != "pass":
            raise PacketError(
                f"PROVENANCE.cleanup_proof.{field} must be pass"
            )
    if proof["recursive_tree_check"] != "pass":
        raise PacketError(
            "PROVENANCE.cleanup_proof.recursive_tree_check must be pass"
        )
    tree_count = proof["recursive_tree_entry_count"]
    if isinstance(tree_count, bool) or not isinstance(tree_count, int) or tree_count != 0:
        raise PacketError(
            "PROVENANCE.cleanup_proof.recursive_tree_entry_count must be zero"
        )
    return True


def validate_draft(draft: dict[str, Any]) -> tuple[list[str], list[str]]:
    if not isinstance(draft, dict):
        raise PacketError("packet draft must be an object")
    unknown = set(draft) - set(REQUIRED_FIELDS) - OPTIONAL_FIELDS
    if unknown:
        raise PacketError(f"unknown top-level fields: {', '.join(sorted(unknown))}")
    aliases = sorted(ALIASES.intersection(draft))
    if aliases:
        raise PacketError(f"aliases must be mapped before build: {', '.join(aliases)}")
    for field in REQUIRED_FIELDS:
        nonempty(draft.get(field), field)
    text_value(draft["TASK"], "TASK")
    for field in ("TESTS", "KNOWN_CONSTRAINTS", "OUT_OF_SCOPE"):
        text_list(draft[field], field)
    criteria = criterion_ids(draft["ACCEPTANCE_CRITERIA"])
    paths = path_values(draft["DIFF_OR_FILES"])
    validate_inline_diff_payloads(draft)
    if len(paths) != len(set(paths)):
        raise PacketError("DIFF_OR_FILES contains duplicate paths")
    provenance = draft["PROVENANCE"]
    if not isinstance(provenance, dict):
        raise PacketError("PROVENANCE must be an object")
    forbidden = sorted(BUILDER_FIELDS.intersection(provenance))
    if forbidden:
        raise PacketError(f"builder-owned provenance fields supplied: {', '.join(forbidden)}")
    for field in ("repo_or_scope", "base_revision", "source_identity", "observed_at_utc"):
        value = text_value(provenance.get(field), f"PROVENANCE.{field}")
        if value.lower() == "unknown":
            raise PacketError(f"PROVENANCE.{field} is missing or unknown")
    refs = provenance.get("artifact_refs", [])
    if not isinstance(refs, list) or any(not isinstance(ref, str) for ref in refs):
        raise PacketError("PROVENANCE.artifact_refs must be a list of string paths")
    normalized_refs = {ref.strip() for ref in refs if ref.strip()}
    if len(refs) != len(normalized_refs):
        raise PacketError("PROVENANCE.artifact_refs must be a list of unique paths")
    if len(normalized_refs) != len(refs):
        raise PacketError("PROVENANCE.artifact_refs cannot contain empty paths")
    missing_diff_refs = sorted(set(paths) - normalized_refs)
    if missing_diff_refs:
        raise PacketError(
            "PROVENANCE.artifact_refs must declare every DIFF_OR_FILES path: "
            + ", ".join(missing_diff_refs)
        )
    validate_cleanup_proof(provenance)
    evidence = draft["EVIDENCE"]
    if not isinstance(evidence, list) or not evidence:
        raise PacketError("EVIDENCE must be a non-empty list")
    seen_evidence: set[str] = set()
    covered: set[str] = set()
    for index, record in enumerate(evidence):
        if not isinstance(record, dict):
            raise PacketError(f"EVIDENCE[{index}] must be an object")
        unknown_fields = set(record) - EVIDENCE_FIELDS - OPTIONAL_EVIDENCE_FIELDS
        if unknown_fields:
            raise PacketError(
                f"EVIDENCE[{index}] has unknown fields: {', '.join(sorted(unknown_fields))}"
            )
        missing = EVIDENCE_FIELDS - set(record)
        if missing:
            raise PacketError(f"EVIDENCE[{index}] missing: {', '.join(sorted(missing))}")
        record_id = str(record["id"]).strip()
        if not record_id or record_id in seen_evidence:
            raise PacketError(f"EVIDENCE[{index}] has a duplicate/empty id")
        seen_evidence.add(record_id)
        criterion_id = str(record["criterion_id"]).strip()
        if criterion_id not in criteria:
            raise PacketError(f"EVIDENCE[{index}] references unknown criterion {criterion_id!r}")
        for field in ("test_or_locus", "input_boundary", "observed_outcome", "artifact_ref"):
            if not isinstance(record[field], str) or not record[field].strip():
                raise PacketError(f"EVIDENCE[{index}].{field} is empty or not text")
        if record["status"] not in STATUSES:
            raise PacketError(f"EVIDENCE[{index}].status is invalid")
        artifact_ref = record["artifact_ref"].strip()
        if not artifact_ref.startswith("inline:") and artifact_ref not in {
            str(ref).strip() for ref in provenance.get("artifact_refs", [])
        }:
            raise PacketError(
                f"EVIDENCE[{index}].artifact_ref is not inline or listed in PROVENANCE.artifact_refs"
            )
        if record["status"] == "unknown":
            blocker = record.get("blocker")
            if not isinstance(blocker, str) or not blocker.strip():
                raise PacketError(
                    f"EVIDENCE[{index}] unknown status requires an explicit blocker"
                )
            if record.get("no_claim") is not True:
                raise PacketError(
                    f"EVIDENCE[{index}] unknown status requires no_claim=true"
                )
        covered.add(criterion_id)
    missing_coverage = sorted(set(criteria) - covered)
    if missing_coverage:
        raise PacketError(f"criteria lack evidence: {', '.join(missing_coverage)}")
    validate_artifacts(draft, provenance)
    return criteria, paths


def build_packet(
    draft: dict[str, Any],
    wire_limit: int = DEFAULT_WIRE_LIMIT,
    storage_limit: int = DEFAULT_STORAGE_LIMIT,
) -> dict[str, Any]:
    criteria, _ = validate_draft(draft)
    packet = copy.deepcopy(draft)
    provenance = packet["PROVENANCE"]
    source_digest = sha256_json(packet)
    unknown_present = any(record["status"] == "unknown" for record in packet["EVIDENCE"])
    no_claim_requested = str(provenance.get("promotion_intent") or "").strip().lower() == "no_claim"
    cleanup_verified = validate_cleanup_proof(provenance)
    pointer_required = (
        isinstance(packet.get("FULL_ARTIFACTS"), list)
        or provenance.get("require_temporary_evidence_pointer") is True
    )
    provenance.update(
        {
            "builder_version": BUILDER_VERSION,
            "source_packet_sha256": source_digest,
            "provenance_verified": True,
            "complete_packet": True,
            "pointer_verified": False,
            "cleanup_verified": cleanup_verified,
            "empty_boat": False,
            "pointer_required": pointer_required,
            "wire_size_policy": "pointer_backed_storage" if pointer_required else "inline_only",
            "wire_size_status": "pointer_required" if pointer_required else "inline_bounded",
            "gate_state": {
                "structural_result": "validated",
                "functional_proof_state": "unknown_evidence_present" if unknown_present else "evidence_present",
                "promotion_decision": "no_claim" if unknown_present or no_claim_requested else "pending_review",
                "no_claim": unknown_present or no_claim_requested,
                "pointer_cleanup_applicability": (
                    "not_applicable_to_skill_only_change"
                    if no_claim_requested
                    else "required_before_promotion"
                ),
                "criterion_ids": criteria,
            },
        }
    )
    packet_digest_input = copy.deepcopy(packet)
    packet["PROVENANCE"]["packet_sha256"] = sha256_json(packet_digest_input)
    wire_digest_input = copy.deepcopy(packet)
    packet["PROVENANCE"]["wire_sha256"] = sha256_json(wire_digest_input)
    wire_chars = len(canonical_bytes(packet))
    if wire_chars > storage_limit:
        raise PacketError(f"serialized storage packet is {wire_chars} chars; limit is {storage_limit}")
    if wire_chars > wire_limit and not pointer_required:
        raise PacketError(f"serialized wire packet is {wire_chars} chars; limit is {wire_limit}")
    return packet


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--wire-limit", type=int, default=DEFAULT_WIRE_LIMIT)
    parser.add_argument("--storage-limit", type=int, default=DEFAULT_STORAGE_LIMIT)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        return run_self_test()
    if not args.input or not args.output:
        raise SystemExit("--input and --output are required unless --self-test is used")
    try:
        draft = json.loads(args.input.read_text(encoding="utf-8"))
        packet = build_packet(draft, args.wire_limit, args.storage_limit)
    except (OSError, json.JSONDecodeError, PacketError) as exc:
        print(f"packet-preflight: FAIL: {exc}", file=sys.stderr)
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_bytes(packet) + b"\n")
    print(json.dumps({"status": "pass", "wire_chars": len(canonical_bytes(packet)), "output": str(args.output)}))
    return 0


def sample_draft() -> dict[str, Any]:
    return {
        "TASK": "test packet builder",
        "ACCEPTANCE_CRITERIA": ["valid packet reaches dispatch", "invalid packet is blocked"],
        "DIFF_OR_FILES": [{"path": "skill.md", "diff": "test"}],
        "TESTS": ["python3 test_review_packet_builder.py"],
        "EVIDENCE": [
            {
                "id": "ev-1",
                "criterion_id": "AC-001",
                "test_or_locus": "builder",
                "input_boundary": "valid draft",
                "observed_outcome": "attested packet emitted",
                "status": "pass",
                "artifact_ref": "inline:test",
            },
            {
                "id": "ev-2",
                "criterion_id": "AC-002",
                "test_or_locus": "builder",
                "input_boundary": "invalid draft",
                "observed_outcome": "dispatch is blocked",
                "status": "pass",
                "artifact_ref": "inline:test",
            },
        ],
        "KNOWN_CONSTRAINTS": ["local-only"],
        "OUT_OF_SCOPE": ["production deployment"],
        "PROVENANCE": {
            "repo_or_scope": "skill",
            "base_revision": "abc123",
            "source_identity": "local-test",
            "observed_at_utc": "2026-01-01T00:00:00Z",
            "artifact_refs": ["skill.md"],
        },
    }


def run_self_test() -> int:
    valid = sample_draft()
    packet = build_packet(valid)
    assert packet["PROVENANCE"]["provenance_verified"] is True
    assert packet["PROVENANCE"]["complete_packet"] is True
    assert packet["PROVENANCE"]["gate_state"]["criterion_ids"] == ["AC-001", "AC-002"]
    invalid_cases = []
    forged = copy.deepcopy(valid)
    forged["PROVENANCE"]["complete_packet"] = True
    invalid_cases.append(forged)
    missing = copy.deepcopy(valid)
    missing["EVIDENCE"] = missing["EVIDENCE"][:1]
    invalid_cases.append(missing)
    unknown_without_blocker = copy.deepcopy(valid)
    unknown_without_blocker["EVIDENCE"][0]["status"] = "unknown"
    invalid_cases.append(unknown_without_blocker)
    duplicate = copy.deepcopy(valid)
    duplicate["EVIDENCE"][1]["id"] = duplicate["EVIDENCE"][0]["id"]
    invalid_cases.append(duplicate)
    overflow = copy.deepcopy(valid)
    overflow["TASK"] = "x" * 20000
    invalid_cases.append(overflow)
    path_only = copy.deepcopy(valid)
    path_only["DIFF_OR_FILES"] = ["skill.md"]
    invalid_cases.append(path_only)
    for case in invalid_cases:
        try:
            build_packet(case)
        except PacketError:
            continue
        raise AssertionError("invalid packet was accepted")
    print(json.dumps({"status": "pass", "invalid_cases": len(invalid_cases), "valid_cases": 1}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
