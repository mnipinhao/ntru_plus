#!/usr/bin/env python3
"""P107: pack the tail's ternary normalisation two sides at a time.

P29's tail calls a six-instruction normalisation once per (t, side) -- 32 times,
192 instructions, for 96 values, because j = 8 gives one (t, side) only its
three components.  Three of eight lanes.

The three values sit in lanes 0..2 and leave through `umov x9, V.d[0]`, so the
high side's three fit in lanes 4..6 with a single `mov V<low>.d[1],
V<high>.d[0]` and one normalisation then covers six values.  The store path is
unchanged: `.d[0]` for the low side, `.d[1]` for the high.

Twelve instructions and one pack replace twenty-four: -80 over the sixteen t.
"""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P28 = ROOT / "experiments/gt864-p28-paired-i16/generate.py"
spec = importlib.util.spec_from_file_location("p28_generate", P28)
p28 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p28)


def normalization(lines, value, tag):
    lines += [
        f"cmgt V<{tag}_above>.8h, V<{value}>.8h, V<tern_hi>.8h",
        f"cmgt V<{tag}_below>.8h, V<tern_lo>.8h, V<{value}>.8h",
        f"add V<{value}>.8h, V<{value}>.8h, V<{tag}_above>.8h",
        f"sub V<{value}>.8h, V<{value}>.8h, V<{tag}_below>.8h",
        f"sqrdmulh V<{tag}_quot>.8h, V<{value}>.8h, V<tern_recip>.8h",
        f"mls V<{value}>.8h, V<{tag}_quot>.8h, V<tern_three>.8h",
    ]


def generate_tail():
    lines = p28.transform("t", "x0", True, tail=True)
    lines = [line.replace("[x0,", "[x1,") for line in lines]
    lines += [
        "p29_tail_terminal_start:",
        "mov w8, #1728", "dup V<tern_hi>.8h, w8",
        "mov w8, #-1728", "dup V<tern_lo>.8h, w8",
        "mov w8, #10923", "dup V<tern_recip>.8h, w8",
        "mov w8, #3", "dup V<tern_three>.8h, w8",
        "add x5, x0, #48",
        "add x6, x0, #912",
    ]
    for t, state in enumerate(p28.REGS):
        offset = t * 64
        lines.append(f"p29_tail_{t}_start:")
        value = {}
        for side, base, reset in (
            ("low", offset, t in p28.RESET_LOW),
            ("high", offset + 32, t in p28.RESET_HIGH),
        ):
            short = "l" if side == "low" else "h"
            lines += [
                f"ldr Q<t{t}_{short}b>, [x4, #{base}]",
                f"ldr Q<t{t}_{short}h>, [x4, #{base + 16}]",
            ]
            v = p28.group_terminal_side(
                lines, "tail", f"t_{state}", t, side, shift=6, constant_prefix="t",
            )
            if reset:
                lines += [
                    "mov w2, #9",
                    f"dup V<t{t}_{side}_nine>.8h, w2",
                    f"sqrdmulh V<t{t}_{side}_reset>.8h, V<{v}>.8h, V<t{t}_{side}_nine>.8h",
                    f"mls V<{v}>.8h, V<t{t}_{side}_reset>.8h, V<q>.8h",
                ]
            value[side] = v
        # six values in one vector: low in lanes 0..2, high in lanes 4..6
        lines.append(f"mov V<{value['low']}>.d[1], V<{value['high']}>.d[0]")
        normalization(lines, value["low"], f"tail_{t}")
        for half, pointer in ((0, "x5"), (1, "x6")):
            lines += [
                f"umov x9, V<{value['low']}>.d[{half}]",
                f"str w9, [{pointer}, #0]",
                "lsr x9, x9, #32",
                f"strh w9, [{pointer}, #4]",
                f"add {pointer}, {pointer}, #54",
            ]
        lines.append(f"p29_tail_{t}_end:")
    header = [
        "#ifdef __APPLE__", "#define p29_tail_direct _p29_tail_direct", "#endif",
        ".text", ".p2align 4", ".global p29_tail_direct", "p29_tail_direct:",
        "// live-in: x0 natural output, x1 padded tail P8, x3 I16 table, x4 tail composite table",
        "// live-out: exact 3-coefficient ternary tail at every public top/t natural address",
        "// one normalisation a t, six values a vector, not three",
        "// reserved physical registers: x18-x30, sp and xzr",
        "p29_tail_slothy_start:",
    ]
    footer = ["p29_tail_slothy_end:", "    ret", ""]
    (HERE / "candidate-tail.sym.S").write_text(
        "\n".join(header + ["    " + l for l in lines] + footer))


generate_tail()
import re
t = (HERE / "candidate-tail.sym.S").read_text()
n = len([l for l in t.splitlines() if re.match(r"^\s{4}[a-z]", l)])
print(f"  candidate-tail.sym.S: {n} 條符號指令")
