#!/usr/bin/env python3
"""Strict post-Slothy evidence audit for the fixed-T1 candidate."""

from __future__ import annotations

import re
import importlib.util
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
START = "gt864_t1_one_bank_slothy_start:"
END = "gt864_t1_one_bank_slothy_end:"


def real_body(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    region = text[text.index(START) + len(START):text.index(END)]
    result = []
    for raw in region.splitlines():
        code = raw.split("//", 1)[0].strip()
        if re.match(r"^[a-z][a-z0-9]*\s", code): result.append(code)
    return result


def counts(lines: list[str]) -> Counter[str]:
    return Counter(re.match(r"([a-z0-9]+)", line).group(1) for line in lines)


def main() -> None:
    symbolic = real_body(HERE / "gt864_t1_one_bank.sym.S")
    allocated = real_body(HERE / "slothy-output/t1.ra_only.local.S")
    scheduled = real_body(HERE / "slothy-output/t1.ra_schedule.local.opt.S")
    assert len(symbolic) == len(allocated) == len(scheduled) == 552
    assert counts(symbolic) == counts(allocated) == counts(scheduled)
    for body in (allocated, scheduled):
        assert not any("<" in line or ">" in line for line in body)
        assert not any(re.search(r"\b(?:sp|stp|str|st1)\b", line) for line in body)
    assert counts(scheduled)["ldp"] == 1 and counts(scheduled)["ldr"] == 69
    assert counts(scheduled)["mul"] == counts(scheduled)["sqrdmulh"] == counts(scheduled)["mls"] == 90

    ra = (HERE / "slothy-output/local-ra-only.log").read_text(encoding="utf-8")
    schedule = (HERE / "slothy-output/local-ra-schedule.log").read_text(encoding="utf-8")
    assert "SLOTHY version: 0.2.0" in ra and "OPTIMAL" in ra and ".selfcheck:OK!" in ra
    assert "split_heuristic_full:OK!" in schedule
    assert "Traceback" not in ra + schedule and "ERROR:" not in ra + schedule
    # The generic parse-slothy-log script treats the benign configuration line
    # "Setting timeout" as a timeout failure.  Exact success markers above are
    # therefore authoritative for these saved logs.
    spec = importlib.util.spec_from_file_location("a1s_optimize", HERE / "optimize.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    module.configure()
    mapping = module.driver.allocated_liveouts(HERE / "slothy-output/t1.ra_only.local.S")
    expected = ["v10", "v22", "v28", "v7", "v1", "v30", "v8", "v29", "v9",
                "v11", "v19", "v6", "v2", "v3", "v4", "v27", "v25", "v21"]
    assert mapping == expected
    print("post_slothy_audit=pass")
    print("instructions=552")
    print("symbolic_registers_remaining=0")
    print("spills_or_stack_accesses=0")
    print("instruction_multiset_change=0")
    print("coefficient_memory_boundary_change=0")
    print("split_window_full_selfcheck=pass")


if __name__ == "__main__": main()
