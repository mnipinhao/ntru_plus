#!/usr/bin/env python3
"""Generate P29 symbolic direct-tail and full-ST3 main-route kernels."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P28_GENERATOR = ROOT / "experiments/gt864-p28-paired-i16/generate.py"

spec = importlib.util.spec_from_file_location("p28_generate", P28_GENERATOR)
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
        for side, base, reset, pointer in (
            ("low", offset, t in p28.RESET_LOW, "x5"),
            ("high", offset + 32, t in p28.RESET_HIGH, "x6"),
        ):
            lines.append(f"p29_tail_{t}_{side}_start:")
            short = "l" if side == "low" else "h"
            lines += [
                f"ldr Q<t{t}_{short}b>, [x4, #{base}]",
                f"ldr Q<t{t}_{short}h>, [x4, #{base + 16}]",
            ]
            value = p28.group_terminal_side(
                lines, "tail", f"t_{state}", t, side,
                shift=6, constant_prefix="t",
            )
            if reset:
                lines += [
                    "mov w2, #9",
                    f"dup V<t{t}_{side}_nine>.8h, w2",
                    f"sqrdmulh V<t{t}_{side}_reset>.8h, V<{value}>.8h, V<t{t}_{side}_nine>.8h",
                    f"mls V<{value}>.8h, V<t{t}_{side}_reset>.8h, V<q>.8h",
                ]
            normalization(lines, value, f"tail_{t}_{side}")
            lines += [
                f"umov x9, V<{value}>.d[0]",
                f"str w9, [{pointer}, #0]",
                "lsr x9, x9, #32",
                f"strh w9, [{pointer}, #4]",
                f"add {pointer}, {pointer}, #54",
                f"p29_tail_{t}_{side}_end:",
            ]
    header = [
        "#ifdef __APPLE__", "#define p29_tail_direct _p29_tail_direct", "#endif",
        ".text", ".p2align 4", ".global p29_tail_direct", "p29_tail_direct:",
        "// live-in: x0 natural output, x1 padded tail P8, x3 I16 table, x4 tail composite table",
        "// live-out: exact 3-coefficient ternary tail at every public top/t natural address",
        "// range: P8 abs<=2617, I16 abs<=21397, raw abs<=4577, ternary abs<=1",
        "// no lane ST3; one STR W plus one STRH stores exactly six bytes per top/t",
        "// reserved physical registers: x18-x30, sp and xzr",
        "p29_tail_slothy_start:",
    ]
    footer = ["p29_tail_slothy_end:", "    ret", ""]
    (HERE / "candidate-tail.sym.S").write_text(
        "\n".join(header + ["    " + line for line in lines] + footer)
    )


def generate_main_route():
    lines = [
        "mov w3, #1728", "dup V<tern_hi>.8h, w3",
        "mov w3, #-1728", "dup V<tern_lo>.8h, w3",
        "mov w3, #10923", "dup V<tern_recip>.8h, w3",
        "movi V<tern_three>.8h, #3",
        "mov x2, x0",
    ]
    bases = ((0, 16, 64), (32, 48, 80))
    for top in range(2):
        for t in range(16):
            lines.append(f"p29_main_route_q{top * 16 + t}_start:")
            values = []
            for bank, base in enumerate(bases[top]):
                value = f"q{top}_{t}_b{bank}"
                lines.append(f"ldr Q<{value}>, [x1, #{16 * (base + t)}]")
                normalization(lines, value, f"main_{top}_{t}_b{bank}")
                values.append(value)
            comp1_low = f"q{top}_{t}_c1lo"
            comp1_high = f"q{top}_{t}_c1hi"
            comp2_high = f"q{top}_{t}_c2hi"
            lines += [
                f"ext V<{comp1_low}>.16b, V<{values[0]}>.16b, V<{values[0]}>.16b, #8",
                f"ext V<{comp1_high}>.16b, V<{values[1]}>.16b, V<{values[1]}>.16b, #8",
                f"ext V<{comp2_high}>.16b, V<{values[2]}>.16b, V<{values[2]}>.16b, #8",
                f"st3 {{V<{values[0]}>.4h, V<{comp1_low}>.4h, V<{values[2]}>.4h}}, [x2], #24",
                f"st3 {{V<{values[1]}>.4h, V<{comp1_high}>.4h, V<{comp2_high}>.4h}}, [x2], #24",
                "add x2, x2, #6",
                f"p29_main_route_q{top * 16 + t}_end:",
            ]
    header = [
        "#ifdef __APPLE__", "#define p29_main_route _p29_main_route", "#endif",
        ".text", ".p2align 4", ".global p29_main_route", "p29_main_route:",
        "// live-in: x0 natural output, x1 P29 equal-half paired main scratch",
        "// live-out: rows 0..7 of every top/t in natural component-interleaved order",
        "// full-vector ST3.4h only; six-byte tail holes are skipped with public ADD",
        "// range: raw abs<=4577, adjusted abs<=4576, ternary abs<=1",
        "// reserved physical registers: x18-x30, sp and xzr",
        "p29_main_route_slothy_start:",
    ]
    footer = ["p29_main_route_slothy_end:", "    ret", ""]
    (HERE / "candidate-main-route.sym.S").write_text(
        "\n".join(header + ["    " + line for line in lines] + footer)
    )


generate_tail()
generate_main_route()
print({
    "tail_source": "candidate-tail.sym.S",
    "main_route_source": "candidate-main-route.sym.S",
    "main_route_windows": 32,
})
