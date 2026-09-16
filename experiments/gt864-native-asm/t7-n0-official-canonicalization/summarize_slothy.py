#!/usr/bin/env python3
"""Validate T7-N0 Slothy artifacts without misclassifying search probes."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
NAMES = ["pair_full", "pair_small", "pair_merge_full", "pair_merge_small"]


def body(path: Path) -> list[str]:
    return [line.split("//", 1)[0].strip().lower() for line in path.read_text().splitlines()
            if line.startswith("    ") and line.split("//", 1)[0].strip() and line.split("//", 1)[0].strip() != "ret"]


def main() -> None:
    reports = {}
    for name in NAMES:
        directory = HERE / "build/slothy" / name
        allocation = json.loads((directory / "allocation.json").read_text())
        timing = json.loads((directory / "timing.json").read_text())
        alloc_source = directory / "candidate.alloc.S"
        opt_source = directory / "candidate.opt.S"
        if allocation["allocation"] != "pass" or allocation["allow_spills"]:
            raise AssertionError(name)
        if Counter(body(alloc_source)) != Counter(body(opt_source)):
            raise AssertionError(f"{name}: timing changed operation multiset")
        if re.search(r"\[(?:sp|x29|x30)", opt_source.read_text(), re.I):
            raise AssertionError(f"{name}: stack/spill access")
        logs = (directory / "slothy-allocate.log").read_text() + (directory / "slothy-timing.log").read_text()
        if "Traceback" in logs or "Exception" in logs:
            raise AssertionError(f"{name}: Slothy exception")
        terminal = re.findall(r"\b(OPTIMAL|FEASIBLE), wall time:", (directory / "slothy-timing.log").read_text())
        if not terminal:
            raise AssertionError(f"{name}: no terminal timing solution")
        reports[name] = {
            "allocation": "pass", "allow_spills": False,
            "vector_liveness_peak": allocation["vector_liveness_peak"],
            "timing_operation_multiset_preserved": True,
            "timing_terminal_solutions": len(terminal),
            "timing_region_cycle_sum": sum(region["cycles"] for region in timing.get("regions", [])) or None,
        }
    result = {
        "status": "pass", "source_checkout": "/Users/chenpinhao/slothy", "target": "cortex_a76",
        "reports": reports,
        "generic_parser_note": "The generic parser flags configured timeout text and intentionally infeasible binary-search probes; artifact-aware terminal and multiset checks are used here.",
    }
    (HERE / "build/slothy-summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
