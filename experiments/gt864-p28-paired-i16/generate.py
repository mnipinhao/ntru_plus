#!/usr/bin/env python3
"""Generate the P28 paired-main symbolic I16 candidate.

The arithmetic is cloned from the machine-checked P13-B main kernel.  P28
executes two independent 16-point transforms, parks six completed vectors
from the first transform in caller-saved GPRs, shares each terminal constant
load between the two transforms, and writes two dense 8-lane banks.
"""

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P13B = ROOT / "experiments/gt864-p13b-inverse16-arithmetic/candidate.sym.S"
P13B_TAIL = ROOT / "experiments/gt864-p13b-inverse16-arithmetic/candidate-tail.sym.S"

REGS = [
    "r24", "r1", "r2", "r3", "r4", "r5", "r6", "r7",
    "r16", "r17", "r18", "r19", "r20", "r21", "r22", "r23",
]
RESET_LOW = {0, 12}
RESET_HIGH = {0, 2, 8, 10}
PARK_FROM = 10
PARK_GPRS = list(range(5, 17))


def p13b_prefix(tail=False):
    path = P13B_TAIL if tail else P13B
    label = "p13b_itail_slothy_start:" if tail else "p13b_i16_slothy_start:"
    lines = [line.strip() for line in path.read_text().splitlines()]
    start = lines.index(label) + 1
    end = next(i for i in range(start, len(lines)) if lines[i] == "mov w8, #9")
    return [line for line in lines[start:end] if line and not line.startswith("//")]


def rename(line, tag):
    def repl(match):
        name = match.group(1)
        return f"<{name if name == 'q' else tag + '_' + name}>"
    return re.sub(r"<([^>]+)>", repl, line)


def transform(tag, pointer, keep_q_setup, tail=False):
    src = p13b_prefix(tail)
    if not keep_q_setup:
        src = src[2:]
    out = []
    for line in src:
        line = rename(line, tag)
        if pointer == "x0":
            line = line.replace("[x1,", "[x0,")
        out.append(line)
    return out


def park(lines):
    gprs = iter(PARK_GPRS)
    parked = {}
    for t in range(PARK_FROM, 16):
        reg = f"a_{REGS[t]}"
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


def group_terminal_side(lines, tag, state, t, side, shift=8, constant_prefix="c"):
    p = f"{tag}_c{t}_{side}"
    short = "l" if side == "low" else "h"
    lines += [
        f"sqrdmulh V<{p}_q>.8h, V<{state}>.8h, V<{constant_prefix}{t}_{short}h>.8h",
        f"mul V<{p}_out>.8h, V<{state}>.8h, V<{constant_prefix}{t}_{short}b>.8h",
        f"mls V<{p}_out>.8h, V<{p}_q>.8h, V<q>.8h",
        f"ext V<{p}_rot>.16b, V<{p}_out>.16b, V<{p}_out>.16b, #{shift}",
        f"add V<{p}_out>.8h, V<{p}_out>.8h, V<{p}_rot>.8h",
    ]
    return f"{p}_out"


def terminal(lines, parked):
    for t in range(16):
        off = t * 64
        astate = f"a_{REGS[t]}" if t < PARK_FROM else restore(lines, t, parked)
        for side, base, reset, pointer in (
            ("low", off, t in RESET_LOW, "x0"),
            ("high", off + 32, t in RESET_HIGH, "x1"),
        ):
            short = "l" if side == "low" else "h"
            lines += [
                f"ldr Q<c{t}_{short}b>, [x4, #{base}]",
                f"ldr Q<c{t}_{short}h>, [x4, #{base + 16}]",
            ]
            aout = group_terminal_side(lines, "a", astate, t, side)
            bout = group_terminal_side(lines, "b", f"b_{REGS[t]}", t, side)
            lines.append(f"mov V<{aout}>.d[1], V<{bout}>.d[0]")
            if reset:
                lines += [
                    "mov w2, #9",
                    f"dup V<c{t}_{side}_nine>.8h, w2",
                    f"sqrdmulh V<c{t}_{side}_reset>.8h, V<{aout}>.8h, V<c{t}_{side}_nine>.8h",
                    f"mls V<{aout}>.8h, V<c{t}_{side}_reset>.8h, V<q>.8h",
                ]
            lines.append(f"str Q<{aout}>, [{pointer}, #{16 * t}]")


def main():
    lines = transform("a", "x0", True)
    parked = park(lines)
    lines += transform("b", "x1", False)
    lines.append("p28_main_terminal_start:")
    terminal(lines, parked)
    header = [
        "#ifdef __APPLE__",
        "#define p28_paired_i16 _p28_paired_i16",
        "#endif",
        ".text",
        ".global p28_paired_i16",
        "p28_paired_i16:",
        "// live-in: x0/x1 two P8 blocks; x3 I16 table; x4 composite table",
        "// live-out: x0=16 top0 Q, x1=16 top1 Q in P27 eight-channel lane order",
        "// coefficient range: input abs<=2617, I16 abs<=21397, output abs<=4577",
        "// reserved physical registers: x18-x30 and sp; x5-x16 park six Q",
        "p28_main_slothy_start:",
    ]
    footer = ["p28_main_slothy_end:", "    ret", ""]
    (HERE / "candidate-main.sym.S").write_text(
        "\n".join(header + ["    " + line for line in lines] + footer)
    )
    print({"main_instructions": len(lines), "parked_q": len(parked), "gprs": PARK_GPRS})


def tail():
    lines = transform("t", "x0", True, tail=True)
    lines.append("p28_tail_terminal_start:")
    initialized = set()
    for t, state in enumerate(REGS):
        off = t * 64
        for side, base, reset, record_base in (
            ("low", off, t in RESET_LOW, 0),
            ("high", off + 32, t in RESET_HIGH, 6),
        ):
            short = "l" if side == "low" else "h"
            lines += [
                f"ldr Q<t{t}_{short}b>, [x4, #{base}]",
                f"ldr Q<t{t}_{short}h>, [x4, #{base + 16}]",
            ]
            src = group_terminal_side(lines, "tail", f"t_{state}", t, side,
                                      shift=6, constant_prefix="t")
            if reset:
                lines += [
                    "mov w2, #9",
                    f"dup V<t{t}_{side}_nine>.8h, w2",
                    f"sqrdmulh V<t{t}_{side}_reset>.8h, V<{src}>.8h, V<t{t}_{side}_nine>.8h",
                    f"mls V<{src}>.8h, V<t{t}_{side}_reset>.8h, V<q>.8h",
                ]
            for lane in range(3):
                linear = 3 * t + lane
                record, dst_lane = divmod(linear, 8)
                acc = f"tail_{side}_q{record}"
                if acc not in initialized:
                    lines.append(f"movi V<{acc}>.8h, #0")
                    initialized.add(acc)
                lines.append(f"ins V<{acc}>.h[{dst_lane}], V<{src}>.h[{lane}]")
                if dst_lane == 7:
                    lines.append(f"str Q<{acc}>, [x0, #{16 * (record_base + record)}]")
    header = [
        "#ifdef __APPLE__",
        "#define p28_dense_tail _p28_dense_tail",
        "#endif",
        ".text",
        ".global p28_dense_tail",
        "p28_dense_tail:",
        "// live-in: x0 consumed 16-Q tail block; x3 I16 table; x4 tail composite table",
        "// live-out: x0 records 0..5 top0 and 6..11 top1, all densely packed",
        "// coefficient range: input abs<=2617, I16 abs<=21397, output abs<=4577",
        "// reserved physical registers: x18-x30 and sp; no stack spill",
        "p28_tail_slothy_start:",
    ]
    footer = ["p28_tail_slothy_end:", "    ret", ""]
    (HERE / "candidate-tail.sym.S").write_text(
        "\n".join(header + ["    " + line for line in lines] + footer)
    )
    print({"tail_instructions": len(lines), "dense_q": 12, "lane_ins": 96})


if __name__ == "__main__":
    main()
    tail()
