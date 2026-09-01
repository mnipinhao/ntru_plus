#!/usr/bin/env python3
"""Compose the reviewed M5J handoff with a second renamed M5I consumer."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
M5J = ROOT.parent / "gt_forward_ntt16_ntt9_handoff_slothy/gt864_forward_ntt16_ntt9_handoff.sym.S"
M5I = ROOT.parent / "gt_forward_ntt9_core_slothy/gt864_forward_ntt9_core.sym.S"
OUTPUT = ROOT / "gt864_forward_two_ntt9_blocks.sym.S"


def region(path: Path, start: str, end: str) -> str:
    text = path.read_text(encoding="utf-8")
    body = text[text.index(start + ":") + len(start) + 1:text.index(end + ":")]
    return body.strip("\n")


def rename_second_core(text: str) -> str:
    inputs = {"f0": "hold0", **{f"f{i}": f"h{i}" for i in range(1, 9)}}
    outputs = {f"out{i}": f"out{i + 9}" for i in range(9)}

    def replace(match: re.Match[str]) -> str:
        kind, name = match.groups()
        if name in inputs:
            renamed = inputs[name]
        elif name in outputs:
            renamed = outputs[name]
        elif name in ("roots", "modq"):
            renamed = name
        else:
            renamed = "second_" + name
        return f"{kind}<{renamed}>"

    return re.sub(r"\b([VQ])<([A-Za-z_][A-Za-z0-9_]*)>", replace, text)


first = region(
    M5J,
    "gt864_forward_ntt16_ntt9_handoff_slothy_start",
    "gt864_forward_ntt16_ntt9_handoff_slothy_end",
)
core = rename_second_core(region(
    M5I,
    "gt864_forward_ntt9_core_slothy_start",
    "gt864_forward_ntt9_core_slothy_end",
))

twists = [
    "    // Capture the fixed tail only when the second consumer becomes active.",
    "    orr V<hold8>.16b, v16.16b, v16.16b",
    "",
    "    // Twist held rows 1..8; x3 already points past the first block table.",
]
for s in range(1, 9):
    source = f"hold{s}"
    twists.extend([
        f"    ldr Q<h_tw{s}>, [x3], #16",
        f"    ldr Q<h_tw{s}p>, [x3], #16",
        f"    sqrdmulh V<h_tw{s}q>.8h, V<{source}>.8h, V<h_tw{s}p>.8h",
        f"    mul V<h{s}>.8h, V<{source}>.8h, V<h_tw{s}>.8h",
        f"    mls V<h{s}>.8h, V<h_tw{s}q>.8h, V<modq>.8h",
    ])

header = """/* M5K: complete two-block NTT16-column to oriented-NTT9 region. */
// symbolic live-in: c0,c1,c2,c3,c4,c5,c6,c7,c8,c9,c10,c11,c12,c13,c14,c15,tail0,roots,modq
// fixed live-in: v16 is held s8; x3 is the public table pointer
// symbolic live-out: out0,out1,out2,out3,out4,out5,out6,out7,out8,out9,out10,out11,out12,out13,out14,out15,out16,out17
// concrete live-out: x3 advances by 512 bytes
// v16 remains live through the first complete NTT9 and is captured before block two
// reserved physical registers: v8-v15 and every GPR except public x3
// range: NTT16 max 9342; twists max 3436; each complete NTT9 max 28568
// memory: thirty-two public twist-table loads, zero coefficient loads or stores

gt864_forward_two_ntt9_blocks_slothy_start:
"""
footer = "\ngt864_forward_two_ntt9_blocks_slothy_end:\n"
text = header + first + "\n\n" + "\n".join(twists) + "\n\n" + core + footer
OUTPUT.write_text(text, encoding="utf-8")
