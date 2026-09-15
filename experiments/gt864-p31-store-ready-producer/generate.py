#!/usr/bin/env python3
"""Generate P31 store-ready inverse producer kernels.

P31 keeps P29's exact arithmetic and natural output ABI, but moves the main
route into the pair2 and pair1 producers.  Pair2 consumes bank0 and emits
rows 0..3; pair1 consumes the retained bank2 high half and emits rows 4..7.
"""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P28_GENERATOR = ROOT / "experiments/gt864-p28-paired-i16/generate.py"

spec = importlib.util.spec_from_file_location("p28_generate", P28_GENERATOR)
p28 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p28)

# The public inverse wrapper has already saved x19-x28.  At this point x20,
# x21 and x26-x28 are dead; x18 is caller-saved.  Using those six registers
# lets us park nine Q values and retain the four normalization constants
# without a memory spill.  x19/x22-x25 remain wrapper state and are reserved.
PARK_FROM = 7
DIRECT_A = 5
PARK_GPRS = list(range(5, 17)) + [18, 20, 21, 26, 27, 28]


def park(lines):
    gprs = iter(PARK_GPRS)
    parked = {}
    for t in range(PARK_FROM, 16):
        reg = f"a_{p28.REGS[t]}"
        lo, hi = next(gprs), next(gprs)
        parked[t] = (lo, hi)
        lines.append(f"umov x{lo}, V<{reg}>.d[0]")
        lines.append(f"umov x{hi}, V<{reg}>.d[1]")
    return parked


def restore(lines, t, parked):
    lo, hi = parked[t]
    name = f"a_restore{t}"
    lines.append(f"dup V<{name}>.2d, x{lo}")
    lines.append(f"ins V<{name}>.d[1], x{hi}")
    return name


def constants(lines):
    # x5-x28 contain parked transform state here; in particular x8 holds the
    # high half of t=8.  x3 is a dead duplicate of the I16-table pointer (the
    # canonical copy remains in x25), so w3 is the safe scalar construction
    # register for all four vector constants.
    lines += [
        "mov w3, #1728", "dup V<tern_hi>.8h, w3",
        "mov w3, #-1728", "dup V<tern_lo>.8h, w3",
        "mov w3, #10923", "dup V<tern_recip>.8h, w3",
        "movi V<tern_three>.8h, #3",
    ]


def normalization(lines, value, tag):
    lines += [
        f"cmgt V<{tag}_above>.8h, V<{value}>.8h, V<tern_hi>.8h",
        f"cmgt V<{tag}_below>.8h, V<tern_lo>.8h, V<{value}>.8h",
        f"add V<{value}>.8h, V<{value}>.8h, V<{tag}_above>.8h",
        f"sub V<{value}>.8h, V<{value}>.8h, V<{tag}_below>.8h",
        f"sqrdmulh V<{tag}_quot>.8h, V<{value}>.8h, V<tern_recip>.8h",
        f"mls V<{value}>.8h, V<{tag}_quot>.8h, V<tern_three>.8h",
    ]


def paired_value(lines, parked, t, side):
    off = t * 64
    base = off if side == "low" else off + 32
    short = "l" if side == "low" else "h"
    astate = f"a_{p28.REGS[t]}" if t < DIRECT_A else restore(lines, t, parked)
    lines += [
        f"ldr Q<c{t}_{short}b>, [x4, #{base}]",
        f"ldr Q<c{t}_{short}h>, [x4, #{base + 16}]",
    ]
    aout = p28.group_terminal_side(lines, "a", astate, t, side)
    bout = p28.group_terminal_side(lines, "b", f"b_{p28.REGS[t]}", t, side)
    lines.append(f"mov V<{aout}>.d[1], V<{bout}>.d[0]")
    reset = t in (p28.RESET_LOW if side == "low" else p28.RESET_HIGH)
    if reset:
        lines += [
            f"movi V<c{t}_{side}_nine>.8h, #9",
            f"sqrdmulh V<c{t}_{side}_reset>.8h, V<{aout}>.8h, V<c{t}_{side}_nine>.8h",
            f"mls V<{aout}>.8h, V<c{t}_{side}_reset>.8h, V<q>.8h",
        ]
    return aout


def prefix():
    lines = p28.transform("a", "x0", True)
    parked = park(lines)
    lines += p28.transform("b", "x1", False)
    # x3/x4 duplicate wrapper-held table pointers.  After both transforms,
    # x19/x22 and x23/x24 can park t5/t6.  x22/x23 are restored from x3/x4;
    # x24 (tail-table state) is explicitly reloaded by the P31 wrapper.
    parked[DIRECT_A] = (19, 22)
    parked[DIRECT_A + 1] = (23, 24)
    lines += [
        f"umov x19, V<a_{p28.REGS[DIRECT_A]}>.d[0]",
        f"umov x22, V<a_{p28.REGS[DIRECT_A]}>.d[1]",
        f"umov x23, V<a_{p28.REGS[DIRECT_A + 1]}>.d[0]",
        f"umov x24, V<a_{p28.REGS[DIRECT_A + 1]}>.d[1]",
    ]
    return lines, parked


def emit_pair2():
    lines, parked = prefix()
    lines.append("p31_pair2_terminal_start:")
    constants(lines)
    # pair2 inputs are scratch+1024 and scratch+1280.  All input loads are
    # complete now, so reuse x0/x1 as bank0 and retained-B2-high pointers.
    lines += ["sub x0, x0, #1024", "sub x1, x1, #768", "mov x3, x0"]
    for t in range(16):
        for side, pointer, output in (("low", "x0", "x2"), ("high", "x1", "x17")):
            lines.append(f"p31_pair2_{t}_{side}_compute_start:")
            b2 = paired_value(lines, parked, t, side)
            normalization(lines, b2, f"p31_b2n_{t}_{side}")
            lines.append(f"p31_pair2_{t}_{side}_compute_end:")
            # The compute allocator may return B2 in v0.  B0 normalization is
            # deliberately fixed to v0 for the consecutive ST3 triple, so
            # transfer B2 to its final v2 slot before v0 is reused.
            b2ready = f"p31_b2ready_{t}_{side}"
            lines.append(f"p31_pair2_{t}_{side}_bridge_start:")
            lines.append(f"orr V<{b2ready}>.16b, V<{b2}>.16b, V<{b2}>.16b")
            lines.append(f"p31_pair2_{t}_{side}_bridge_end:")
            lines.append(f"p31_pair2_{t}_{side}_b0_start:")
            b0 = f"p31_b0_{t}_{side}"
            lines.append(f"ldr Q<{b0}>, [{pointer}, #{16 * t}]")
            normalization(lines, b0, f"p31_b0n_{t}_{side}")
            lines.append(f"p31_pair2_{t}_{side}_b0_end:")
            lines.append(f"p31_pair2_{t}_{side}_store_start:")
            b0hi = f"p31_b0hi_{t}_{side}"
            b2hi = f"p31_b2hi_{t}_{side}"
            lines += [
                f"ext V<{b0hi}>.16b, V<{b0}>.16b, V<{b0}>.16b, #8",
                f"st3 {{V<{b0}>.4h, V<{b0hi}>.4h, V<{b2ready}>.4h}}, [{output}], #24",
                f"add {output}, {output}, #30",
                f"ext V<{b2hi}>.16b, V<{b2ready}>.16b, V<{b2ready}>.16b, #8",
                f"str D<{b2hi}>, [x3, #0]",
                "add x3, x3, #8",
            ]
            lines.append(f"p31_pair2_{t}_{side}_store_end:")
    lines += [
        "sub x19, x2, #864", "mov x22, x25", "mov x23, x4", "mov x25, x0",
    ]
    write("pair2", "p31_pair2_low_store", lines, parked,
          "pair2 input blocks -> rows 0..3 plus retained normalized B2 high D")


def emit_pair1():
    lines, parked = prefix()
    lines.append("p31_pair1_terminal_start:")
    constants(lines)
    # pair1 inputs are scratch+256 and scratch+768; subtracting 256 selects
    # the B0 slots overwritten by pair2 with normalized B2 high halves.
    lines += ["sub x0, x0, #256", "sub x1, x1, #256", "mov x3, x0"]
    for t in range(16):
        for side, pointer, output in (("low", "x0", "x2"), ("high", "x1", "x17")):
            lines.append(f"p31_pair1_{t}_{side}_compute_start:")
            b1 = paired_value(lines, parked, t, side)
            normalization(lines, b1, f"p31_b1n_{t}_{side}")
            lines.append(f"p31_pair1_{t}_{side}_compute_end:")
            lines.append(f"p31_pair1_{t}_{side}_route_start:")
            b1store = f"p31_b1store_{t}_{side}"
            b1hi = f"p31_b1hi_{t}_{side}"
            b2hi = f"p31_saved_b2hi_{t}_{side}"
            lines += [
                f"orr V<{b1store}>.16b, V<{b1}>.16b, V<{b1}>.16b",
                f"ext V<{b1hi}>.16b, V<{b1store}>.16b, V<{b1store}>.16b, #8",
                f"ldr D<{b2hi}>, [x3], #8",
                f"st3 {{V<{b1store}>.4h, V<{b1hi}>.4h, V<{b2hi}>.4h}}, [{output}], #24",
                f"add {output}, {output}, #30",
            ]
            lines.append(f"p31_pair1_{t}_{side}_route_end:")
    lines += [
        "sub x19, x2, #888", "mov x22, x25", "mov x23, x4", "mov x25, x0",
    ]
    write("pair1", "p31_pair1_high_store", lines, parked,
          "pair1 input blocks plus retained B2 high D -> rows 4..7")


def write(stem, function, lines, parked, result):
    header = [
        "#ifdef __APPLE__", f"#define {function} _{function}", "#endif",
        ".text", ".p2align 4", f".global {function}", f"{function}:",
        "// live-in: x0/x1 paired P8 blocks; x2/x17 natural output cursors; x3/x4 tables",
        f"// live-out: {result}",
        "// range: P8 abs<=2617, I16 abs<=21397, raw abs<=4577, ternary abs<=1",
        "// x20/x21/x26-x28 are dead wrapper state, already saved by the public wrapper",
        "    mov x25, x3  // preserve I16 table; scratch base is recoverable from x0",
        f"p31_{stem}_slothy_start:",
    ]
    footer = [f"p31_{stem}_slothy_end:", "    ret", ""]
    (HERE / f"candidate-{stem}.sym.S").write_text(
        "\n".join(header + ["    " + line for line in lines] + footer)
    )


if __name__ == "__main__":
    emit_pair2()
    emit_pair1()
    print({"parked_q": 16 - PARK_FROM, "park_gprs": PARK_GPRS})
