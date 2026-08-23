#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIN = ROOT / "build/bench"
SYMBOLS = (
    "producer062_p0_tile4_post_s1_asm",
    "producer062_p1_hwa_explicit_post_s1_asm",
    "producer062_p2_hwa_fused_post_s1_asm",
)
FAMILIES = ("vmov", "vperm2i128", "vpshufb", "vshufps", "vpunpck",
            "vpblend", "vpmullw", "vpmulhw", "vpaddw", "vpsubw")
dis = subprocess.check_output(["objdump", "-d", "--no-show-raw-insn", BIN],
                              text=True)
nm = subprocess.check_output(["nm", "-S", "--size-sort", BIN], text=True)
sizes = {}
for line in nm.splitlines():
    fields = line.split()
    if len(fields) >= 4 and fields[3] in SYMBOLS:
        sizes[fields[3]] = int(fields[1], 16)
result = {}
for symbol in SYMBOLS:
    match = re.search(rf"^[0-9a-f]+ <{symbol}>:\n(.*?)(?=^[0-9a-f]+ <|\Z)",
                      dis, re.M | re.S)
    if not match:
        raise SystemExit(f"missing {symbol}")
    instructions = []
    for line in match.group(1).splitlines():
        m = re.match(r"\s*[0-9a-f]+:\s+([a-z0-9]+)\s*(.*)", line)
        if m:
            instructions.append((m.group(1), m.group(2)))
    memory_loads = sum("(" in operands and not operands.strip().startswith("%ymm")
                       for mnemonic, operands in instructions
                       if mnemonic.startswith("v"))
    memory_stores = sum("(" in operands and operands.strip().startswith("%ymm")
                        for mnemonic, operands in instructions
                        if mnemonic.startswith("v"))
    result[symbol] = {
        "code_bytes": sizes[symbol],
        "instructions": len(instructions),
        "families": {family: sum(m.startswith(family) for m, _ in instructions)
                     for family in FAMILIES},
        "stack_references": sum("%rsp" in operands or "%rbp" in operands
                                for _, operands in instructions),
        "vector_memory_loads_static": memory_loads,
        "vector_memory_stores_static": memory_stores,
    }
(ROOT / "results").mkdir(exist_ok=True)
(ROOT / "results/static.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
