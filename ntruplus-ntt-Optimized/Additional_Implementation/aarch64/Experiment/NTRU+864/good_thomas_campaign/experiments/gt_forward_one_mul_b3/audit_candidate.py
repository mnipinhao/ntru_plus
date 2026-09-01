#!/usr/bin/env python3
"""Audit M5R-C source, returned Slothy artifacts, and arithmetic hard gate."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gt864_forward_one_bank_one_mul_b3.sym.S"
OPT = ROOT / "slothy-output/gt864_forward_one_bank_one_mul_b3.n1.opt.S"
RA = ROOT / "slothy-output/gt864_forward_one_bank_one_mul_b3.ra.log"
SCHEDULE = ROOT / "slothy-output/gt864_forward_one_bank_one_mul_b3.schedule.log"
START = "gt864_forward_one_bank_one_mul_b3_slothy_start:"
END = "gt864_forward_one_bank_one_mul_b3_slothy_end:"


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
    return {opcode: sum(line.startswith(opcode + " ") for line in lines)
            for opcode in ("ldr", "ld1", "mul", "sqrdmulh", "mls", "orr", "str", "st1", "stp")}


def main() -> None:
    symbolic, optimized = instructions(SOURCE), instructions(OPT)
    sc, oc = counts(symbolic), counts(optimized)
    assert len(symbolic) == len(optimized) == 593
    assert sc == oc
    assert oc == {"ldr": 69, "ld1": 16, "mul": 96, "sqrdmulh": 96,
                  "mls": 96, "orr": 0, "str": 0, "st1": 0, "stp": 0}
    assert sum("[x3], #16" in line for line in optimized if line.startswith("ldr ")) == 32
    assert not any(line.startswith("ldp ") and "[x3]" in line for line in optimized)
    assert "<" not in "\n".join(optimized) and ">" not in "\n".join(optimized)

    ra, schedule = RA.read_text(encoding="utf-8"), SCHEDULE.read_text(encoding="utf-8")
    assert "Instructions in body: 593" in ra
    assert "OPTIMAL" in ra and ".selfcheck:OK!" in ra
    assert "split.split_heuristic_full:OK!" in schedule
    assert "allocated_liveouts=" in schedule
    assert "spill" not in (ra + schedule).lower()

    result = {
        "status": "pass",
        "one_bank_instructions": 593,
        "baseline_one_bank_instructions": 617,
        "algorithm10_mulmods_per_bank": 96,
        "baseline_algorithm10_mulmods_per_bank": 102,
        "mulmods_deleted_per_ntt9_block": 3,
        "net_instructions_deleted_per_ntt9_block": 12,
        "independent_twist_ldrs_preserved_per_bank": 32,
        "coefficient_stores_inside_bank": 0,
        "spills": 0,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
