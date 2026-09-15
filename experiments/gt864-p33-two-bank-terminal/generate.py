#!/usr/bin/env python3
"""Generate the P33 materialized-prefix and live-prefix pair kernels."""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P13 = ROOT / "experiments/gt864-p13b-inverse16-arithmetic/generate.py"
spec = importlib.util.spec_from_file_location("p13_generate", P13)
p13 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p13)

REGS = p13.REGS
RESET_LOW = p13.RESET_LOW
RESET_HIGH = p13.RESET_HIGH


def materialized_prefix():
    body = p13.body_prefix("inverse16_lazy")
    body += [f"str Q<{r}>, [x0, #{16*t}]" for t, r in enumerate(REGS)]
    header = [
        "#ifdef __APPLE__", "#define p33_i16_prefix _p33_i16_prefix", "#endif",
        ".text", ".global p33_i16_prefix", "p33_i16_prefix:",
        "// live-in: x0 == x1 consumed half-zero block; x3 inverse16 table",
        "// live-out: sixteen preterminal Q records at x0",
        "// coefficient range: input abs<=2617; preterminal abs<=21397",
        "// reserved physical registers: all GPRs are concrete; vectors allocated by Slothy",
        "p33_i16_prefix_slothy_start:",
    ]
    return "\n".join(header + ["    " + x for x in body] + [
        "p33_i16_prefix_slothy_end:", "    ret", ""
    ])


def scatter(lines, name, t, half, high):
    base = 24 * half + 54 * t + (864 if high else 0)
    for lane in range(4):
        lines += [
            f"umov w9, V<{name}>.h[{lane}]",
            f"strh w9, [x0, #{base + 6*lane}]",
        ]


def terminal(lines, name, source, t, half):
    lines += [
        f"sqrdmulh V<{name}_lq>.8h, V<{source}>.8h, V<c{t}_lh>.8h",
        f"sqrdmulh V<{name}_hq>.8h, V<{source}>.8h, V<c{t}_hh>.8h",
        f"mul V<{name}_low>.8h, V<{source}>.8h, V<c{t}_lb>.8h",
        f"mul V<{name}_high>.8h, V<{source}>.8h, V<c{t}_hb>.8h",
        f"mls V<{name}_low>.8h, V<{name}_lq>.8h, V<q>.8h",
        f"mls V<{name}_high>.8h, V<{name}_hq>.8h, V<q>.8h",
        f"ext V<{name}_lr>.16b, V<{name}_low>.16b, V<{name}_low>.16b, #8",
        f"ext V<{name}_hr>.16b, V<{name}_high>.16b, V<{name}_high>.16b, #8",
        f"add V<{name}_low>.8h, V<{name}_low>.8h, V<{name}_lr>.8h",
        f"add V<{name}_high>.8h, V<{name}_high>.8h, V<{name}_hr>.8h",
    ]
    if t in RESET_LOW:
        lines += [
            f"sqrdmulh V<{name}_rl>.8h, V<{name}_low>.8h, V<nine>.8h",
            f"mls V<{name}_low>.8h, V<{name}_rl>.8h, V<q>.8h",
        ]
    if t in RESET_HIGH:
        lines += [
            f"sqrdmulh V<{name}_rh>.8h, V<{name}_high>.8h, V<nine>.8h",
            f"mls V<{name}_high>.8h, V<{name}_rh>.8h, V<q>.8h",
        ]
    scatter(lines, f"{name}_high", t, half, True)
    scatter(lines, f"{name}_low", t, half, False)


def pair():
    # The exact production prefix is reused for B.  Only its input pointer is
    # changed from x1 to x2; its sixteen results remain symbolic live-outs.
    body = [x.replace("[x1,", "[x2,") for x in p13.body_prefix("inverse16_lazy")]
    lines = [
        "#ifdef __APPLE__", "#define p33_i16_pair _p33_i16_pair", "#endif",
        ".text", ".global p33_i16_pair", "p33_i16_pair:",
        "// x0 component output base; x1 materialized A; x2 post-I9 B",
        "// x3 inverse16 table; x4 composite terminal table",
        "// live-in: x0, x1, x2, x3, x4 and sixteen secret B input Q records",
        "// live-out: 256 exact raw int16 natural coefficient stores",
        "// coefficient range: input abs<=2617; preterminal abs<=21397; output abs<=4454",
        "// reserved physical registers: all GPRs are concrete; vectors allocated by Slothy",
        "// live B states: sixteen Q vectors; q and nine stay resident",
        "p33_i16_pair_slothy_start:",
    ]
    lines += ["    " + x for x in body]
    lines += [
        "p33_i16_pair_terminal_start:",
        "    mov w8, #9",
        "    dup V<nine>.8h, w8",
        "p33_i16_pair_t0_start:",
    ]
    for t, breg in enumerate(REGS):
        if t:
            lines += [f"p33_i16_pair_t{t}_start:"]
        off = 64 * t
        lines += [
            f"    ldr Q<c{t}_lb>, [x4, #{off}]",
            f"    ldr Q<c{t}_lh>, [x4, #{off+16}]",
            f"    ldr Q<c{t}_hb>, [x4, #{off+32}]",
            f"    ldr Q<c{t}_hh>, [x4, #{off+48}]",
            f"    ldr Q<a{t}>, [x1, #{16*t}]",
        ]
        a_block = []
        terminal(a_block, f"a{t}", f"a{t}", t, 0)
        lines += ["    " + x for x in a_block]
        lines += [f"p33_i16_pair_t{t}_a_end:", f"p33_i16_pair_t{t}_b_start:"]
        b_block = []
        terminal(b_block, f"b{t}", breg, t, 1)
        lines += ["    " + x for x in b_block]
        lines += [f"p33_i16_pair_t{t}_b_end:"]
        lines += [f"p33_i16_pair_t{t}_end:"]
    lines += ["p33_i16_pair_slothy_end:", "    ret", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    (HERE / "candidate-prefix.sym.S").write_text(materialized_prefix())
    (HERE / "candidate-pair.sym.S").write_text(pair())
    print({"live_b_states": len(REGS), "pair_terminal_windows": 16})
