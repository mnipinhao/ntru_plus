#!/usr/bin/env python3
"""Inventory compiler stack realization; not a performance/promotion gate."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


def frame(disassembly: str, symbol: str) -> int:
    match = re.search(
        rf"_{symbol}:\n(?P<body>.*?)(?=\n_[A-Za-z0-9_]+:|\Z)",
        disassembly, re.S)
    assert match, symbol
    stack = re.search(r"sub\s+sp, sp, #0x([0-9a-f]+)", match.group("body"))
    return int(stack.group(1), 16) if stack else 0


def main() -> None:
    binary = Path(sys.argv[1])
    disassembly = subprocess.check_output(
        ["otool", "-tvV", str(binary)], text=True)
    ntt9 = frame(disassembly, "gt864_fr0_inverse_ntt9_neon")
    finish = frame(disassembly, "gt864_fr0_inverse_finish_neon")
    print(json.dumps({
        "gate": "gt864_fr0_inverse_codegen_inventory",
        "status": "recorded_not_a_promotion_gate",
        "inverse_ntt9_compiled_stack_bytes": ntt9,
        "inverse_finish_compiled_stack_bytes": finish,
        "compiler_spills_intrinsic_arrays": ntt9 != 0 or finish != 0,
        "algorithmic_memory_pass_contract": "FR0_to_P8; P8_to_natural",
        "handwritten_assembly_still_required": True,
        "production_linked": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
