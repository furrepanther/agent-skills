#!/usr/bin/env python3
"""Regression test for Grumpy's near-ceiling packet headroom."""

from __future__ import annotations

import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path
import sys


SKILL_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = SKILL_ROOT / "runtime" / "primus-local-v1"
LIB = RUNTIME_ROOT / "lib"
GENERAL = RUNTIME_ROOT / "bin" / "primus-general-code-review"


def load_general_module():
    sys.path.insert(0, str(LIB))
    loader = SourceFileLoader("primus_general_code_review_for_budget_test", str(GENERAL))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load general reviewer module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    module = load_general_module()
    calls: list[int] = []

    def fake_fit(packet, budget):
        calls.append(budget)
        return {"fit_budget": budget}

    module.fit_grumpy_packet_to_budget = fake_fit
    result, selected = module.compatible_grumpy_packet_for_budget({}, 12000)
    assert selected == 11900
    assert calls == [11900]
    assert result == {"fit_budget": 11900}
    print("grumpy-budget-headroom: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
