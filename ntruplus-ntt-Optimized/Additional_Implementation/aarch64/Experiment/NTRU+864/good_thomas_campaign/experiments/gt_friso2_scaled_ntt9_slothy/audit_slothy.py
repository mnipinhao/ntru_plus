#!/usr/bin/env python3
"""Audit returned CF2 allocation/scheduling artifacts under the block boundary."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gt864_friso2_scaled_ntt9_variants.sym.S"
OUT = ROOT / "slothy-output"
EXPECTED = {"t0c1": (154, 34, 38), "t0c2": (154, 34, 38),
            "t1c1": (138, 18, 34), "t1c2": (138, 18, 34)}
FORBIDDEN_VECTORS = {f"v{i}" for i in range(16, 25)}


def region(text: str, case: str) -> str:
    start = f"gt864_friso2_scaled_{case}_slothy_start:"
    end = f"gt864_friso2_scaled_{case}_slothy_end:"
    return text[text.index(start):text.index(end)]


def instructions(text: str, physical: bool) -> list[str]:
    result = []
    for raw in text.splitlines():
        code = raw.split("//", 1)[0].strip()
        if not re.match(r"^[a-z][a-z0-9]*\s", code):
            continue
        if physical and "<" in code:
            continue
        result.append(code)
    return result


def main() -> None:
    symbolic_all = SOURCE.read_text(encoding="utf-8")
    reports = []
    for case, (expected_count, expected_ldr, expected_cycles) in EXPECTED.items():
        alloc_path = OUT / f"{case}.n1.alloc.S"
        opt_path = OUT / f"{case}.n1.opt.S"
        ra_path = OUT / f"{case}.ra.log"
        schedule_path = OUT / f"{case}.schedule.log"
        alloc_text = alloc_path.read_text(encoding="utf-8")
        opt_text = opt_path.read_text(encoding="utf-8")
        ra_log = ra_path.read_text(encoding="utf-8")
        schedule_log = schedule_path.read_text(encoding="utf-8")
        symbolic = instructions(region(symbolic_all, case), physical=False)
        allocated = instructions(region(alloc_text, case), physical=True)
        optimized = instructions(region(opt_text, case), physical=True)
        assert len(symbolic) == len(allocated) == len(optimized) == expected_count
        assert [line.split()[0] for line in symbolic] == [
            line.split()[0] for line in allocated]
        counts = Counter(line.split()[0] for line in optimized)
        assert counts["ldr"] == expected_ldr
        assert counts["mul"] == counts["sqrdmulh"] == counts["mls"] == 26
        assert counts["add"] + counts["sub"] == 42
        assert all(re.fullmatch(r"ldr q(?:[0-9]|[12][0-9]|3[01]), \[x3\], #16",
                                line, flags=re.IGNORECASE)
                   for line in optimized if line.startswith("ldr "))
        assert not any(line.startswith(("str ", "stp ", "st1 ", "ld1 "))
                       for line in optimized)
        assert not any(re.match(r"^(?:b|bl|br|cbz|cbnz|tbz|tbnz|ret)\b", line)
                       for line in optimized)
        assert not any(re.search(r"\b(?:sp|x29|x30)\b", line)
                       for line in optimized)
        registers = {"v" + value for line in optimized
                     for value in re.findall(r"\b(?:v|q)([0-9]|[12][0-9]|3[01])\b",
                                             line, flags=re.IGNORECASE)}
        assert not registers.intersection(FORBIDDEN_VECTORS)
        assert "v31" in registers
        assert "OPTIMAL" in ra_log and ".selfcheck:OK!" in ra_log
        assert "split_heuristic_full:OK!" in schedule_log
        assert "Traceback" not in ra_log + schedule_log
        match = re.search(r"Expected cycles:\s*([0-9]+)", region(opt_text, case))
        assert match and int(match.group(1)) == expected_cycles
        liveout_line = next(line for line in schedule_log.splitlines()
                            if line.startswith("allocated_liveouts="))
        liveouts = [entry.split(":")[1]
                    for entry in liveout_line.split("=", 1)[1].split(",")]
        assert len(liveouts) == len(set(liveouts)) == 9
        assert not set(liveouts).intersection(FORBIDDEN_VECTORS | {"v31"})
        reports.append({
            "case": case,
            "instructions": expected_count,
            "expected_cycles_N1_proxy": expected_cycles,
            "used_vector_registers": sorted(registers,
                                             key=lambda name: int(name[1:])),
            "used_vector_register_count": len(registers),
            "reserved_sibling_vectors_untouched": True,
            "distinct_liveouts": liveouts,
            "RA": "OPTIMAL_selfcheck_OK",
            "schedule": "split_heuristic_full_OK",
            "spill_stack_store_branch": "none",
        })
    print(json.dumps({
        "status": "pass",
        "reports": reports,
        "boundary": "nine sibling vectors v16-v24 reserved; v31 fixed q",
        "allocatable_core_registers": "v0-v15 and v25-v30",
        "new_coefficient_memory_boundary": 0,
        "cycle_claim": "N1 scheduling proxy only; not Cortex-A76 measurement",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
