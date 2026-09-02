#!/usr/bin/env python3
"""Audit M5R-D returned Slothy artifacts and arithmetic instruction gate."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gt864_forward_one_bank_all_one_mul_b3.sym.S"
OPT = ROOT / "slothy-output/gt864_forward_one_bank_all_one_mul_b3.n1.opt.S"
RA = ROOT / "slothy-output/gt864_forward_one_bank_all_one_mul_b3.ra.log"
SCHEDULE = ROOT / "slothy-output/gt864_forward_one_bank_all_one_mul_b3.schedule.log"
START = "gt864_forward_one_bank_all_one_mul_b3_slothy_start:"
END = "gt864_forward_one_bank_all_one_mul_b3_slothy_end:"


def instructions(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    body = text[text.index(START) + len(START):text.index(END)]
    result = []
    for raw in body.splitlines():
        line = raw.split("//", 1)[0].strip()
        if line and not line.endswith(":"):
            result.append(line)
    return result


def counts(lines: list[str]) -> dict[str, int]:
    return {op: sum(line.startswith(op + " ") for line in lines)
            for op in ("ldr", "ld1", "mul", "sqrdmulh", "mls", "orr", "str", "st1", "stp")}


def main() -> None:
    symbolic, optimized = instructions(SOURCE), instructions(OPT)
    assert len(symbolic) == len(optimized) == 569
    expected = {"ldr": 69, "ld1": 16, "mul": 90, "sqrdmulh": 90,
                "mls": 90, "orr": 0, "str": 0, "st1": 0, "stp": 0}
    assert counts(symbolic) == counts(optimized) == expected
    assert sum("[x3], #16" in line for line in optimized if line.startswith("ldr ")) == 32
    assert not any(line.startswith("ldp ") and "[x3]" in line for line in optimized)
    assert "<" not in "\n".join(optimized) and ">" not in "\n".join(optimized)
    ra, schedule = RA.read_text(encoding="utf-8"), SCHEDULE.read_text(encoding="utf-8")
    assert "Instructions in body: 569" in ra
    assert "OPTIMAL" in ra and ".selfcheck:OK!" in ra
    assert "split.split_heuristic_full:OK!" in schedule
    assert "allocated_liveouts=" in schedule
    assert "spill" not in (ra + schedule).lower()
    print(json.dumps({
        "status": "pass",
        "one_bank_instructions": 569,
        "M5R-C_one_bank_instructions": 593,
        "M5R-B_one_bank_instructions": 617,
        "algorithm10_mulmods_per_bank": 90,
        "additional_mulmods_deleted_per_ntt9_block": 3,
        "total_mulmods_deleted_per_ntt9_block_vs_M5R-B": 6,
        "independent_twist_ldrs_per_bank": 32,
        "spills": 0,
        "new_memory_boundaries": 0,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
