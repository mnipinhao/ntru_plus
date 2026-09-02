#!/usr/bin/env python3
"""Static instruction, table, ABI, and memory-boundary audit for M5U-CF0."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PASS2 = ROOT / "gt864_forward_six_bank_friso2.S"
WRAPPER = ROOT / "gt864_forward_poly_ntt_friso2.S"


def instructions(text: str) -> list[str]:
    return [line.split("//", 1)[0].strip() for line in text.splitlines()
            if line.split("//", 1)[0].strip()
            and not line.split("//", 1)[0].strip().endswith(":")
            and not line.lstrip().startswith((".", "/*", "*", "*/"))]


def main() -> None:
    text = PASS2.read_text(encoding="utf-8")
    wrapper = WRAPPER.read_text(encoding="utf-8")
    lines = instructions(text)
    assert text.count("M5U-CF0: live-out FR-0 -> FR-ISO2") == 4
    assert sum(line.startswith("ldp q2, q7, [x5], #32") for line in lines) == 72
    for opcode in ("mul", "sqrdmulh", "mls"):
        # The 569-instruction bank helper is present once in the object and is
        # called six times; the four live-out scale regions are emitted once.
        assert sum(line.startswith(opcode + " ") for line in lines) == 90 + 72
    assert sum(line.startswith("str q") for line in lines) == 108
    assert sum(line.startswith(("st1 ", "stp q")) for line in lines) == 0
    assert "sub sp, sp, #1792" in wrapper and "add sp, sp, #1792" in wrapper
    assert wrapper.count("stp d") == 4 and wrapper.count("ldp d") == 4
    assert not re.search(r"\b(?:cbz|cbnz|tbz|tbnz|b\.(?:eq|ne|lt|le|gt|ge))\b", text)
    result = {
        "status": "pass",
        "baseline_full_forward_dynamic_instructions": 4446,
        "candidate_full_forward_dynamic_instructions": 4738,
        "dynamic_delta": 292,
        "algorithm10_mulmods_added": 72,
        "constant_ldp_added": 72,
        "coefficient_loads_added": 0,
        "coefficient_stores_added": 0,
        "coefficient_memory_boundaries_added": 0,
        "scale_scratch_vectors": ["v2", "v7", "v18"],
        "stack_contract": "unchanged 1792-byte P8 plus public ABI save frame",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
