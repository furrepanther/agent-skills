#!/usr/bin/env python3
"""Regression tests for typed acceptance/test binding in the local checker."""

from __future__ import annotations

import importlib.util
from importlib.machinery import SourceFileLoader
import hashlib
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime" / "primus-local-v1"
LIB = RUNTIME / "lib"
ENTRYPOINT = RUNTIME / "bin" / "primus-adversarial-code-checker"
sys.path.insert(0, str(LIB))
loader = SourceFileLoader("primus_adversarial_code_checker_contract_test", str(ENTRYPOINT))
spec = importlib.util.spec_from_loader(loader.name, loader)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
sys.modules[loader.name] = module
spec.loader.exec_module(module)


def main() -> int:
    packet = {
        "ACCEPTANCE_CRITERIA": [
            {"criterion_id": "AC-001", "text": "source bytes are verified"},
            {"criterion_id": "AC-002", "text": "routing fails closed"},
        ],
        "TESTS": [
            "T-001 criterion=AC-001 assertion=source receipt is exact; observed=pass",
            "T-002 criterion=AC-002 assertion=stale peer is rejected; observed=pass",
            "T-007 scope=adversarial assertion=all hostile paths are reviewed; observed=pass",
        ],
    }
    requirements = module.packet_requirements(packet)
    assert [row["id"] for row in requirements] == ["R1", "R2"]
    assert requirements[0]["requirement"] == "source bytes are verified"

    tests = module.scaffold_tests(packet, requirements)
    assert [row["id"] for row in tests] == ["T1", "T2", "T7"]
    assert tests[0]["covers_requirements"] == ["R1"]
    assert tests[1]["covers_requirements"] == ["R2"]
    assert tests[2]["covers_requirements"] == []

    coverage = module.normalize_coverage(
        [
            {
                "requirement_id": "AC-001",
                "covered_by_tests": ["T1"],
                "coverage": "covered",
                "implementation_evidence": "receipt is verified",
                "test_evidence": "T1 passes",
                "gap": "",
                "no_block_justification": "evidence is explicit",
            }
        ],
        requirements,
        tests,
    )
    assert coverage[0]["requirement_id"] == "R1"
    assert coverage[0]["covered_by_tests"] == ["T1"]

    pages = []
    receipts = []
    for index, (path, content) in enumerate((("src/a.py", "return 1"), ("src/b.py", "raise ValueError"))):
        page_digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        page = {
            "schema": module.SOURCE_REVIEW_PAGE_SCHEMA,
            "path": path,
            "file_sha256_full": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            "page_sha256_full": page_digest,
            "page_index": index,
            "page_count": 2,
            "byte_start": 0,
            "byte_end": len(content.encode("utf-8")),
            "size_bytes": len(content.encode("utf-8")),
            "content": content,
        }
        pages.append(page)
        receipts.append({key: page[key] for key in (
            "page_index", "page_count", "page_sha256_full", "path", "byte_start", "byte_end"
        )})
    delivery = {
        "transport": "pointer_hydrated_source_page",
        "reviewer_receipt": True,
        "complete_source_bytes_verified": True,
        "parent_memory_id": "temporary-review-1",
        "source_packet_sha256": "a" * 64,
        "page_receipts": receipts,
    }
    assert module._source_review_page_delivery_defects({
        "SOURCE_PAGES": pages,
        "SOURCE_DELIVERY": delivery,
    }) == []
    malformed = dict(delivery)
    malformed.pop("page_receipts")
    assert module._source_review_page_delivery_defects({
        "SOURCE_PAGES": pages,
        "SOURCE_DELIVERY": malformed,
    }) == ["multi-page SOURCE_PAGES requires page_receipts"]

    absolute_index = (
        "complete_path_index=yes; entries=1; all_items_listed=yes; prefix_table=x:\n"
        "[1/1] path=x:/mnt/linuxdata/Github/example.py"
    )
    assert module._source_paths_from_diff(absolute_index) == [
        "/mnt/linuxdata/Github/example.py"
    ]
    print("checker-packet-contract: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
