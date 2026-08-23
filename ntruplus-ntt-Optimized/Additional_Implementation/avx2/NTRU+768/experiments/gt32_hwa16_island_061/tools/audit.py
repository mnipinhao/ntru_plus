#!/usr/bin/env python3
"""Static instruction/movement/stack/code-size audit for the measured symbols."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGETS = {
    "v1_v2": (ROOT / "build" / "bench", [
        "ctl_tile4_forward_asm", "hwa16_forward_v1_asm", "hwa16_forward_v2_asm",
        "ctl_tile4_basemul_asm", "hwa16_basemul_asm",
        "ctl_tile4_inverse_asm", "hwa16_inverse_v1_asm", "hwa16_inverse_v2_asm",
    ]),
    "v3": (ROOT / "build" / "bench_v3", [
        "ctl_tile4_forward_asm", "ctl_tile4_basemul_asm",
        "ctl_tile4_inverse_asm",
        "hwa16_v3_forward_m40a_asm", "hwa16_v3_inverse_m40a_asm",
        "hwa16_v3_forward_m40b_asm", "hwa16_v3_inverse_m40b_asm",
        "hwa16_v3_forward_m40c_asm", "hwa16_v3_inverse_m40c_asm",
        "hwa16_v3_basemul_m40a_asm", "hwa16_v3_basemul_m40b_asm",
        "hwa16_v3_basemul_m40c_asm", "hwa16_v3_basemul_common_asm",
    ]),
}
FAMILIES = ("vperm2i128", "vpermq", "vpshufb", "vpshufd", "vshufps",
            "vpunpck", "vpblend", "vmov")

result = {}
for group, (binary, symbols) in TARGETS.items():
    dis = subprocess.check_output(
        ["objdump", "-d", "--no-show-raw-insn", str(binary)], text=True)
    nm = subprocess.check_output(
        ["nm", "-a", "-S", "--size-sort", str(binary)], text=True)
    sizes = {}
    for line in nm.splitlines():
        fields = line.split()
        if len(fields) >= 4 and fields[3] in symbols:
            sizes[fields[3]] = int(fields[1], 16)

    result[group] = {}
    for symbol in symbols:
        match = re.search(
            rf"^[0-9a-f]+ <{re.escape(symbol)}>:\n(.*?)(?=^[0-9a-f]+ <|\Z)",
            dis, re.M | re.S)
        if not match:
            raise SystemExit(f"missing disassembly for {symbol} in {binary}")
        instructions = []
        for line in match.group(1).splitlines():
            m = re.match(r"\s*[0-9a-f]+:\s+([a-z0-9]+)\s*(.*)", line)
            if m:
                instructions.append((m.group(1), m.group(2)))
        counts = {family: sum(mn.startswith(family) for mn, _ in instructions)
                  for family in FAMILIES}
        stack = sum("%rsp" in operands or "%rbp" in operands
                    for _, operands in instructions)
        result[group][symbol] = {
            "code_bytes": sizes.get(symbol),
            "instructions": len(instructions),
            "movement": counts,
            "stack_references": stack,
        }

print(json.dumps(result, indent=2, sort_keys=True))
