#!/usr/bin/env python3
"""Generate P32 symbolic producer and sixteen bounded terminal regions."""
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


def producer():
    body = p13.body_prefix("inverse16_lazy")
    body += [f"str Q<{r}>, [x0, #{16*t}]" for t, r in enumerate(REGS)]
    header = [
        "#ifdef __APPLE__", "#define p32_i16_prefix _p32_i16_prefix", "#endif",
        ".text", ".global p32_i16_prefix", "p32_i16_prefix:",
        "// live-in: x0 output scratch, x1 input scratch, x3 stage table",
        "// live-out: sixteen preterminal Q records at x0",
        "// coefficient range: input abs<=2617, preterminal abs<=21397",
        "// reserved physical registers: x18-x30, sp, xzr",
        "// x0 == x1: consumed 256-byte input block is overwritten in place",
        "p32_i16_prefix_slothy_start:",
    ]
    return "\n".join(header + ["    " + x for x in body] + [
        "p32_i16_prefix_slothy_end:", "    ret", ""
    ])


def stores(lines, name, t, group, high):
    component, half = divmod(group, 2)
    base = 2 * component + 24 * half + 54 * t + (864 if high else 0)
    for lane in range(4):
        lines += [
            f"umov w9, V<{name}>.h[{lane}]",
            f"strh w9, [x0, #{base + 6*lane}]",
        ]


def terminal_region(t):
    off = 64 * t
    tag = f"t{t}"
    lines = [
        f"ldr q26, [x4, #{off}]",
        f"ldr q27, [x4, #{off+16}]",
        f"ldr q28, [x4, #{off+32}]",
        f"ldr q29, [x4, #{off+48}]",
    ]
    for g in range(6):
        s = f"{tag}_g{g}"
        lines += [f"p32_terminal_{t}_g{g}_start:",
            f"ldr Q<{s}_x>, [x1, #{256*g + 16*t}]",
            f"sqrdmulh V<{s}_lq>.8h, V<{s}_x>.8h, v27.8h",
            f"sqrdmulh V<{s}_hq>.8h, V<{s}_x>.8h, v29.8h",
            f"mul V<{s}_low>.8h, V<{s}_x>.8h, v26.8h",
            f"mul V<{s}_high>.8h, V<{s}_x>.8h, v28.8h",
            f"mls V<{s}_low>.8h, V<{s}_lq>.8h, v30.8h",
            f"mls V<{s}_high>.8h, V<{s}_hq>.8h, v30.8h",
            f"ext V<{s}_lr>.16b, V<{s}_low>.16b, V<{s}_low>.16b, #8",
            f"ext V<{s}_hr>.16b, V<{s}_high>.16b, V<{s}_high>.16b, #8",
            f"add V<{s}_low>.8h, V<{s}_low>.8h, V<{s}_lr>.8h",
            f"add V<{s}_high>.8h, V<{s}_high>.8h, V<{s}_hr>.8h",
        ]
        if t in RESET_LOW:
            lines += [
                f"sqrdmulh V<{s}_rl>.8h, V<{s}_low>.8h, v31.8h",
                f"mls V<{s}_low>.8h, V<{s}_rl>.8h, v30.8h",
            ]
        if t in RESET_HIGH:
            lines += [
                f"sqrdmulh V<{s}_rh>.8h, V<{s}_high>.8h, v31.8h",
                f"mls V<{s}_high>.8h, V<{s}_rh>.8h, v30.8h",
            ]
        stores(lines, f"{s}_high", t, g, True)
        stores(lines, f"{s}_low", t, g, False)
        lines += [f"p32_terminal_{t}_g{g}_end:"]
    return lines


def consumer():
    lines = [
        "#ifdef __APPLE__", "#define p32_i16_terminal6 _p32_i16_terminal6", "#endif",
        ".text", ".global p32_i16_terminal6", "p32_i16_terminal6:",
        "// live-in: x0 natural output, x1 six preterminal blocks, x4 composite table",
        "// live-out: exact 768 main natural raw int16 coefficient stores",
        "// coefficient range: preterminal abs<=21397, output abs<=4454",
        "// reserved physical registers: x18-x30, sp, xzr; fixed v26-v31",
        "p32_i16_terminal6_slothy_start:",
        "mov w8, #3457", "dup v30.8h, w8", "mov w8, #9", "dup v31.8h, w8",
    ]
    for t in range(16):
        lines += [f"p32_terminal_{t}_start:"]
        lines += ["    " + x for x in terminal_region(t)]
        lines += [f"p32_terminal_{t}_end:"]
    lines += ["p32_i16_terminal6_slothy_end:", "    ret", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    (HERE / "candidate-prefix.sym.S").write_text(producer())
    (HERE / "candidate-terminal.sym.S").write_text(consumer())
    print({"prefix_states": 16, "terminal_columns": 16, "banks": 6})
