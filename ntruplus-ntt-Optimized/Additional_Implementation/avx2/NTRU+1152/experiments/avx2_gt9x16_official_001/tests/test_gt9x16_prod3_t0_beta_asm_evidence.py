#!/usr/bin/env python3
"""Regression checks for the linked Natural-Q T0-beta ASM audit."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "generated/gt9x16-prod3-natural-q-t0-beta-asm-audit.json"


def main() -> None:
    report = json.loads(AUDIT.read_text(encoding="utf-8"))
    assert report["schema"] == "gt9x16-prod3-natural-q-t0-beta-asm-audit/v1"

    machine = report["linked_machine"]
    control = machine["control"]
    candidate = machine["candidate"]
    delta = machine["candidate_minus_control"]

    assert control["instructions"] == 2819
    assert candidate["instructions"] == 2787
    assert control["vpmullw"] == 368 and candidate["vpmullw"] == 360
    assert control["vpmulhw"] == 592 and candidate["vpmulhw"] == 576
    assert control["constant_memory_operands"] == 594
    assert candidate["constant_memory_operands"] == 578
    assert delta["instructions"] == -32
    assert delta["constant_memory_operands"] == -16

    for key in ("routing_total", "data_loads", "data_stores", "barrett"):
        assert control[key] == candidate[key]
        assert delta[key] == 0
    for side in (control, candidate):
        assert side["vector_spills"] == 0
        assert side["stack_references"] == 0
        assert side["calls"] == 0
        assert side["branches"] == 0
        assert side["vzeroupper"] == 0

    footprint = report["object_footprint"]
    assert footprint["delta"] == {"text": -192, "rodata": 416}
    assert set(report["alignment"].values()) == {32, True}
    assert all(report["gates"].values())
    assert report["authorization"] == {
        "native_kem": False,
        "producer_caller_island_pricing_next": True,
        "promotion": False,
    }
    print("T0-beta ASM evidence passed: exact linked schedule and zero movement debt")


if __name__ == "__main__":
    main()
