#!/usr/bin/env python3
"""Executable regression coverage for the Red-Team-Gate packet builder."""

from __future__ import annotations

import copy
import hashlib
import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent))
from review_packet_builder import PacketError, build_packet, sample_draft  # noqa: E402


class PacketBuilderTests(unittest.TestCase):
    def test_valid_packet_is_attested_and_wire_bounded(self) -> None:
        draft = sample_draft()
        draft["PROVENANCE"]["promotion_intent"] = "no_claim"
        packet = build_packet(draft)
        provenance = packet["PROVENANCE"]
        self.assertTrue(provenance["provenance_verified"])
        self.assertTrue(provenance["complete_packet"])
        self.assertIn("wire_sha256", provenance)
        self.assertTrue(provenance["gate_state"]["no_claim"])
        self.assertEqual(
            provenance["gate_state"]["pointer_cleanup_applicability"],
            "not_applicable_to_skill_only_change",
        )
        self.assertFalse(provenance["cleanup_verified"])

    def test_valid_cleanup_proof_sets_builder_attestation(self) -> None:
        draft = sample_draft()
        draft["PROVENANCE"]["cleanup_proof"] = {
            "status": "pass",
            "receipt_ref": "inline:cleanup-receipt",
            "receipt_sha256_full": hashlib.sha256(b"cleanup-receipt").hexdigest(),
            "target": "/tmp/primus-review/exact-temporary-record",
            "observed_absence": [
                "/tmp/primus-review/exact-temporary-record",
                "/tmp/primus-review/exact-temporary-record.pointer",
            ],
            "record_cap": 1,
            "byte_cap": 65536,
            "active_pointer_check": "pass",
            "post_delete_check": "pass",
            "recursive_tree_check": "pass",
            "recursive_tree_entry_count": 0,
        }
        packet = build_packet(draft)
        self.assertTrue(packet["PROVENANCE"]["cleanup_verified"])

    def test_cleanup_proof_requires_reviewable_receipt_and_guards(self) -> None:
        draft = sample_draft()
        proof = {
            "status": "pass",
            "receipt_ref": "missing-receipt.json",
            "receipt_sha256_full": hashlib.sha256(b"receipt").hexdigest(),
            "target": "/tmp/primus-review/exact-temporary-record",
            "observed_absence": ["/tmp/primus-review/exact-temporary-record"],
            "record_cap": 1,
            "byte_cap": 1024,
            "active_pointer_check": "pass",
            "post_delete_check": "pass",
            "recursive_tree_check": "pass",
            "recursive_tree_entry_count": 0,
        }
        draft["PROVENANCE"]["cleanup_proof"] = proof
        with self.assertRaises(PacketError):
            build_packet(draft)

        proof["receipt_ref"] = "inline:receipt"
        proof["active_pointer_check"] = "fail"
        with self.assertRaises(PacketError):
            build_packet(draft)

    def test_unknown_evidence_forces_no_claim(self) -> None:
        draft = sample_draft()
        draft["EVIDENCE"][0]["status"] = "unknown"
        draft["EVIDENCE"][0]["blocker"] = "independent runtime evidence is pending"
        draft["EVIDENCE"][0]["no_claim"] = True
        packet = build_packet(draft)
        self.assertTrue(packet["PROVENANCE"]["gate_state"]["no_claim"])
        self.assertEqual(packet["PROVENANCE"]["gate_state"]["promotion_decision"], "no_claim")

    def test_unknown_evidence_without_blocker_or_no_claim_is_rejected(self) -> None:
        draft = sample_draft()
        draft["EVIDENCE"][0]["status"] = "unknown"
        with self.assertRaises(PacketError):
            build_packet(draft)
        draft["EVIDENCE"][0]["blocker"] = "independent runtime evidence is pending"
        with self.assertRaises(PacketError):
            build_packet(draft)

    def test_evidence_artifact_reference_must_be_exact_or_inline(self) -> None:
        draft = sample_draft()
        draft["EVIDENCE"][0]["artifact_ref"] = "missing-artifact.json"
        with self.assertRaises(PacketError):
            build_packet(draft)

    def test_unknown_evidence_fields_are_rejected(self) -> None:
        draft = sample_draft()
        draft["EVIDENCE"][0]["typo_field"] = "not accepted"
        with self.assertRaises(PacketError):
            build_packet(draft)

    def test_required_text_fields_reject_wrong_types(self) -> None:
        for field in ("TASK", "TESTS", "KNOWN_CONSTRAINTS", "OUT_OF_SCOPE"):
            draft = sample_draft()
            draft[field] = {"unexpected": "object"}
            with self.subTest(field=field):
                with self.assertRaises(PacketError):
                    build_packet(draft)

        draft = sample_draft()
        draft["TESTS"] = ["valid", 7]
        with self.assertRaises(PacketError):
            build_packet(draft)

    def test_provenance_identity_and_artifact_refs_reject_coercion(self) -> None:
        draft = sample_draft()
        draft["PROVENANCE"]["base_revision"] = 123
        with self.assertRaises(PacketError):
            build_packet(draft)

        draft = sample_draft()
        draft["PROVENANCE"]["artifact_refs"] = [123]
        with self.assertRaises(PacketError):
            build_packet(draft)

    def test_forced_attestation_is_rejected(self) -> None:
        draft = sample_draft()
        draft["PROVENANCE"]["complete_packet"] = True
        with self.assertRaises(PacketError):
            build_packet(draft)

    def test_missing_criterion_coverage_is_rejected(self) -> None:
        draft = sample_draft()
        draft["EVIDENCE"] = draft["EVIDENCE"][:1]
        with self.assertRaises(PacketError):
            build_packet(draft)

    def test_duplicate_ids_and_paths_are_rejected(self) -> None:
        duplicate_id = sample_draft()
        duplicate_id["EVIDENCE"][1]["id"] = duplicate_id["EVIDENCE"][0]["id"]
        with self.assertRaises(PacketError):
            build_packet(duplicate_id)
        duplicate_path = sample_draft()
        duplicate_path["DIFF_OR_FILES"].append(copy.deepcopy(duplicate_path["DIFF_OR_FILES"][0]))
        with self.assertRaises(PacketError):
            build_packet(duplicate_path)

    def test_diff_paths_must_be_declared_in_provenance(self) -> None:
        draft = sample_draft()
        draft["PROVENANCE"]["artifact_refs"] = []
        with self.assertRaises(PacketError):
            build_packet(draft)

    def test_inline_diff_requires_reviewable_payload(self) -> None:
        draft = sample_draft()
        draft["DIFF_OR_FILES"] = ["skill.md"]
        with self.assertRaises(PacketError):
            build_packet(draft)
        draft["DIFF_OR_FILES"] = [{"path": "skill.md"}]
        with self.assertRaises(PacketError):
            build_packet(draft)

    def test_full_artifacts_allow_path_only_diff_index(self) -> None:
        draft = sample_draft()
        draft["DIFF_OR_FILES"] = ["skill.md"]
        content = "actual"
        draft["FULL_ARTIFACTS"] = [{
            "path": "skill.md",
            "content": content,
            "file_sha256_full": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            "size_bytes": len(content.encode("utf-8")),
        }]
        packet = build_packet(draft)
        self.assertEqual(packet["DIFF_OR_FILES"], ["skill.md"])
        self.assertTrue(packet["PROVENANCE"]["pointer_required"])

    def test_full_artifacts_require_complete_content(self) -> None:
        draft = sample_draft()
        draft["FULL_ARTIFACTS"] = [{
            "path": "skill.md",
            "file_sha256_full": hashlib.sha256(b"actual").hexdigest(),
            "size_bytes": 6,
        }]
        draft["PROVENANCE"]["artifact_refs"] = ["skill.md"]
        with self.assertRaises(PacketError):
            build_packet(draft)

    def test_empty_artifact_reference_is_rejected(self) -> None:
        draft = sample_draft()
        draft["PROVENANCE"]["artifact_refs"] = ["skill.md", ""]
        with self.assertRaises(PacketError):
            build_packet(draft)

    def test_alias_only_input_is_rejected(self) -> None:
        draft = sample_draft()
        draft["implementation_scope"] = draft.pop("DIFF_OR_FILES")
        with self.assertRaises(PacketError):
            build_packet(draft)

    def test_digest_and_size_mismatch_are_rejected(self) -> None:
        draft = sample_draft()
        draft["FULL_ARTIFACTS"] = [{
            "path": "skill.md",
            "content": "actual",
            "file_sha256_full": "0" * 64,
            "size_bytes": 6,
        }]
        draft["PROVENANCE"]["artifact_refs"] = ["skill.md"]
        with self.assertRaises(PacketError):
            build_packet(draft)

    def test_wire_overflow_is_rejected_before_dispatch(self) -> None:
        draft = sample_draft()
        draft["TASK"] = "x" * 5000
        with self.assertRaises(PacketError):
            build_packet(draft, wire_limit=1000)

    def test_full_artifacts_require_pointer_backed_transport(self) -> None:
        draft = sample_draft()
        content = "x" * 3000
        draft["FULL_ARTIFACTS"] = [{
            "path": "skill.md",
            "content": content,
            "file_sha256_full": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            "size_bytes": len(content.encode("utf-8")),
        }]
        draft["PROVENANCE"]["artifact_refs"] = ["skill.md"]
        packet = build_packet(draft, wire_limit=1000, storage_limit=12000)
        self.assertTrue(packet["PROVENANCE"]["pointer_required"])
        self.assertEqual(packet["PROVENANCE"]["wire_size_status"], "pointer_required")

    def test_invalid_drafts_make_zero_downstream_calls(self) -> None:
        downstream_calls = []

        def dispatch(draft):
            packet = build_packet(draft)
            downstream_calls.append(packet)
            return packet

        invalid = sample_draft()
        invalid["PROVENANCE"]["complete_packet"] = True
        with self.assertRaises(PacketError):
            dispatch(invalid)
        invalid = sample_draft()
        invalid["EVIDENCE"] = invalid["EVIDENCE"][:1]
        with self.assertRaises(PacketError):
            dispatch(invalid)
        invalid = sample_draft()
        invalid["TASK"] = "x" * 20000
        with self.assertRaises(PacketError):
            dispatch(invalid)
        invalid = sample_draft()
        invalid["TESTS"] = {"not": "a list"}
        with self.assertRaises(PacketError):
            dispatch(invalid)
        self.assertEqual(downstream_calls, [])


if __name__ == "__main__":
    unittest.main()
