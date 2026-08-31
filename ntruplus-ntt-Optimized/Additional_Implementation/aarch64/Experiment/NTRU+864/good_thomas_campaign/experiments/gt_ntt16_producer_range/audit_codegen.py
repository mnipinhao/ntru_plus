#!/usr/bin/env python3
"""Record compiler realization facts without turning them into the range gate."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


def main() -> None:
    binary = Path(sys.argv[1])
    source = Path(sys.argv[2]).read_text()
    disassembly = subprocess.check_output(
        ["otool", "-tvV", str(binary)], text=True)
    match = re.search(
        r"_gt864_ntt16_p8_neon:\n(?P<body>.*?)(?=\n_[A-Za-z0-9_]+:|\Z)",
        disassembly, re.S)
    assert match
    body = match.group("body")
    stack_match = re.search(r"sub\s+sp, sp, #0x([0-9a-f]+)", body)
    stack_bytes = int(stack_match.group(1), 16) if stack_match else 0

    assert "barrett" not in source.lower()
    assert "length = 2" in source and "stage < 4" in source
    print(json.dumps({
        "gate": "gt864_ntt16_codegen_inventory",
        "status": "recorded_not_a_promotion_gate",
        "compiled_stack_bytes": stack_bytes,
        "compiler_spills_vector_array": stack_bytes != 0,
        "explicit_barrett_reductions": 0,
        "memory_schedule_claim": False,
        "meaning": "intrinsics freeze arithmetic/range only; handwritten assembly is still required for the two-load/two-store schedule",
        "production_linked": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
