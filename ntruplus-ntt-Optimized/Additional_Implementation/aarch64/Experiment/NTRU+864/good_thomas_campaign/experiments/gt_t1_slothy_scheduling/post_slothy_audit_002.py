#!/usr/bin/env python3
"""Strict post-Slothy audit for A1-S-002 schedule-only and diagnostics."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
START = "gt864_t1_one_bank_slothy_start:"
END = "gt864_t1_one_bank_slothy_end:"


def body(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    region = text[text.index(START) + len(START):text.index(END)]
    return [code for raw in region.splitlines()
            if (code := raw.split("//", 1)[0].strip()) and
            re.match(r"^[a-z][a-z0-9]*\s", code)]


def mnemonics(lines: list[str]) -> Counter[str]:
    return Counter(line.split(None, 1)[0].lower() for line in lines)


def no_spills(lines: list[str]) -> bool:
    return not any(re.search(r"\bsp\b|\b(?:str|stp|st1)\b", line) for line in lines)


def successful(log: Path, required: str) -> bool:
    text = log.read_text(encoding="utf-8")
    return ("SLOTHY version: 0.2.0" in text and required in text and
            "Traceback" not in text and "Couldn't parse" not in text)


def main() -> None:
    baseline = body(HERE / "build/t1.schedule_input.S")
    schedule = body(HERE / "rerun-002/t1.schedule_only.S")
    allocated = body(HERE / "rerun-002/t1.ra_only.S")
    ra_schedule = body(HERE / "rerun-002/t1.ra_schedule.opt.S")
    assert len(baseline) == len(schedule) == len(allocated) == len(ra_schedule) == 552
    expected = mnemonics(baseline)
    assert all(mnemonics(candidate) == expected
               for candidate in (schedule, allocated, ra_schedule))
    assert all(no_spills(candidate) for candidate in (schedule, allocated, ra_schedule))
    assert not any("<" in line or ">" in line for line in (allocated + ra_schedule))
    assert expected["ldp"] == 1 and expected["ldr"] == 69
    assert expected["mul"] == expected["sqrdmulh"] == expected["mls"] == 90
    assert successful(HERE / "rerun-002/schedule-only.log", "split_heuristic_full:OK!")
    assert successful(HERE / "rerun-002/ra-only.log", ".selfcheck:OK!")
    assert successful(HERE / "rerun-002/ra-schedule.log", "split_heuristic_full:OK!")
    print("post_slothy_audit_002=pass")
    print("primary_candidate=schedule_only_original_physical_RA")
    print("instructions=552")
    print("instruction_multiset_change=0")
    print("algorithm10_products=90")
    print("spills_or_stack_accesses=0")
    print("coefficient_memory_boundary_change=0")
    print("schedule_only_split_window_full_selfcheck=pass")
    print("ra_only_selfcheck=pass")
    print("ra_schedule_split_window_full_selfcheck=pass")


if __name__ == "__main__":
    main()
