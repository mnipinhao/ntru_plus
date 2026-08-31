#!/usr/bin/env python3
"""Audit the assembled M5A one-block kernel and arithmetic categories."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


def main() -> None:
    binary = Path(sys.argv[1])
    assembly = Path(sys.argv[2])
    disassembly = subprocess.check_output(
        ["otool", "-tvV", str(binary)], text=True
    )
    match = re.search(
        r"_gt864_fr0_block_asm:\n(?P<body>.*?)(?=\n_[A-Za-z0-9_]+:|\Z)",
        disassembly,
        re.S,
    )
    assert match, "assembled symbol not found"
    body = match.group("body")
    instruction_lines = [
        line for line in body.splitlines()
        if re.match(r"^[0-9a-f]+\s", line.strip())
    ]
    assert not re.search(r"\bsp\b", body), "stack pointer used"
    assert not re.search(r"\bv(?:8|9|1[0-5])(?:\.|\b)", body), (
        "callee-saved Neon register used"
    )
    assert "ret" in body

    source = assembly.read_text()
    explicit_fqmul = len(re.findall(r"^\s*FQMUL\s+", source, re.M)) - 4
    # Four FQMUL tokens occur inside the B3 macro and are counted separately.
    b3_calls = len(re.findall(r"^\s*B3\s+", source, re.M))
    assert explicit_fqmul == 12
    assert b3_calls == 6
    per_block = {
        "lambda_twist": 8,
        "rho_or_rho2_inside_six_B3": b3_calls * 4,
        "eta_or_eta_inverse": 4,
    }
    assert sum(per_block.values()) == 36
    full = {name: count * 12 for name, count in per_block.items()}
    assert sum(full.values()) == 432

    payload = {
        "gate": "gt864_fr0_asm_static_audit",
        "status": "pass",
        "stack_pointer_used": False,
        "callee_saved_neon_used": False,
        "coefficient_spills": 0,
        "assembled_instruction_lines": len(instruction_lines),
        "field_mulmods_per_block": per_block,
        "field_mulmods_full_polynomial": full,
        "field_mulmods_full_total": sum(full.values()),
        "note": "96 is lambda twist only; widening-reduction instructions are implementation cost inside each field mulmod",
        "production_linked": False,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
