#!/usr/bin/env python3
"""Emit the P10 symbolic candidate as an apply_patch payload."""

from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent


class DAG:
    def __init__(self, q: str, qi: str):
        self.q = q
        self.qi = qi
        self.lines: list[str] = []
        self.seq = 0

    def fresh(self, stem: str = "t") -> str:
        self.seq += 1
        return f"{stem}_{self.seq}"

    def emit(self, line: str) -> None:
        self.lines.append(line)

    def load(self, name: str, ptr: str, offset: int) -> str:
        self.emit(f"ldr Q<{name}>, [{ptr}, #{offset}]")
        return name

    def store(self, name: str, ptr: str, offset: int) -> None:
        self.emit(f"str Q<{name}>, [{ptr}, #{offset}]")

    def wide_product(self, a: str, b: str) -> tuple[str, str]:
        lo, hi = self.fresh("lo"), self.fresh("hi")
        self.emit(f"smull V<{lo}>.4s, V<{a}>.4h, V<{b}>.4h")
        self.emit(f"smull2 V<{hi}>.4s, V<{a}>.8h, V<{b}>.8h")
        return lo, hi

    def wide_accumulate(self, acc: tuple[str, str], op: str, a: str, b: str) -> None:
        lo, hi = acc
        self.emit(f"{op} V<{lo}>.4s, V<{a}>.4h, V<{b}>.4h")
        self.emit(f"{op}2 V<{hi}>.4s, V<{a}>.8h, V<{b}>.8h")

    def redc_wide(self, acc: tuple[str, str]) -> str:
        lo, hi = acc
        low = self.fresh("low")
        corr = self.fresh("corr")
        out = self.fresh("redc")
        self.emit(f"uzp1 V<{low}>.8h, V<{lo}>.8h, V<{hi}>.8h")
        self.emit(f"mul V<{corr}>.8h, V<{low}>.8h, V<{self.qi}>.8h")
        self.emit(f"smlal V<{lo}>.4s, V<{corr}>.4h, V<{self.q}>.4h")
        self.emit(f"smlal2 V<{hi}>.4s, V<{corr}>.8h, V<{self.q}>.8h")
        self.emit(f"uzp2 V<{out}>.8h, V<{lo}>.8h, V<{hi}>.8h")
        return out

    def mm_with_bqi(self, a: str, b: str, bqi: str) -> str:
        quotient = self.fresh("quot")
        self.emit(f"mul V<{quotient}>.8h, V<{a}>.8h, V<{bqi}>.8h")
        acc = self.wide_product(a, b)
        self.wide_accumulate(acc, "smlal", quotient, self.q)
        out = self.fresh("redc")
        self.emit(f"uzp2 V<{out}>.8h, V<{acc[0]}>.8h, V<{acc[1]}>.8h")
        return out

    def mm(self, a: str, b: str) -> str:
        bqi = self.fresh("bqi")
        self.emit(f"mul V<{bqi}>.8h, V<{b}>.8h, V<{self.qi}>.8h")
        return self.mm_with_bqi(a, b, bqi)


def direct_tile(d: DAG, suffix: str, input_offset: int, zeta_offset: int, output_offset: int, den_offset: int) -> None:
    a = d.load(f"a_{suffix}", "x1", input_offset)
    b = d.load(f"b_{suffix}", "x1", input_offset + 16)
    c = d.load(f"c_{suffix}", "x1", input_offset + 32)
    zr = d.load(f"zr_{suffix}", "x2", zeta_offset)

    # c*qi is shared by REDC(b*c) and REDC(c*c).
    cqi = d.fresh("cqi")
    d.emit(f"mul V<{cqi}>.8h, V<{c}>.8h, V<{d.qi}>.8h")
    u = d.mm_with_bqi(b, c, cqi)
    w = d.mm_with_bqi(c, c, cqi)

    n0_acc = d.wide_product(a, a)
    d.wide_accumulate(n0_acc, "smlsl", u, zr)
    n0 = d.redc_wide(n0_acc)

    n1_acc = d.wide_product(w, zr)
    d.wide_accumulate(n1_acc, "smlsl", a, b)
    n1 = d.redc_wide(n1_acc)

    n2_acc = d.wide_product(b, b)
    d.wide_accumulate(n2_acc, "smlsl", a, c)
    n2 = d.redc_wide(n2_acc)

    h_acc = d.wide_product(n2, b)
    d.wide_accumulate(h_acc, "smlal", n1, c)
    h = d.redc_wide(h_acc)

    den_acc = d.wide_product(h, zr)
    d.wide_accumulate(den_acc, "smlal", n0, a)
    den = d.redc_wide(den_acc)

    d.store(n0, "x0", output_offset)
    d.store(n1, "x0", output_offset + 16)
    d.store(n2, "x0", output_offset + 32)
    d.store(den, "x3", den_offset)


def numerator_pair() -> list[str]:
    d = DAG("q_num", "qi_num")
    direct_tile(d, "a", 0, 0, 0, 0)
    direct_tile(d, "b", 48, 16, 48, 48)
    assert len(d.lines) == 132
    return d.lines


def finish_tile() -> list[str]:
    d = DAG("q_finish", "qi_finish")
    a = [d.load(f"n{i}", "x0", 16 * i) for i in range(3)]
    den = d.load("inverse_den", "x1", 0)
    dqi = d.fresh("dqi")
    d.emit(f"mul V<{dqi}>.8h, V<{den}>.8h, V<{d.qi}>.8h")
    for i, value in enumerate(a):
        out = d.mm_with_bqi(value, den, dqi)
        d.store(out, "x0", 16 * i)
    assert len(d.lines) == 26
    return d.lines


def inverse3() -> list[str]:
    d = DAG("q_inv", "qi_inv")
    # This region owns its constants; unlike the repeated numerator/finish
    # leaves it executes only once per public BaseInv call.
    d.emit("mov w8, #3457")
    d.emit("dup V<q_inv>.8h, w8")
    d.emit("mov w8, #-12929")
    d.emit("dup V<qi_inv>.8h, w8")
    x, y, z = [d.load(f"chain{i}", "x1", 16 * i) for i in range(3)]
    xy = d.mm(x, y)
    a1 = d.mm(xy, z)
    a2 = d.mm(a1, a1)
    a4 = d.mm(a2, a2)
    a8 = d.mm(a4, a4)
    a16 = d.mm(a8, a8)
    a17 = d.mm(a16, a1)
    a32 = d.mm(a16, a16)
    a64 = d.mm(a32, a32)
    a128 = d.mm(a64, a64)
    a145 = d.mm(a128, a17)
    a273 = d.mm(a145, a128)
    a546 = d.mm(a273, a273)
    a691 = d.mm(a546, a145)
    a1382 = d.mm(a691, a691)
    a2764 = d.mm(a1382, a1382)
    inverse = d.mm(a2764, a691)

    d.emit("mov w8, #-1571")
    d.emit("dup V<scale>.8h, w8")
    d.emit("mov w8, #-14891")
    d.emit("dup V<scale_hat>.8h, w8")
    corrected = d.fresh("corrected")
    corr = d.fresh("scale_corr")
    d.emit(f"mul V<{corrected}>.8h, V<{inverse}>.8h, V<scale>.8h")
    d.emit(f"sqrdmulh V<{corr}>.8h, V<{inverse}>.8h, V<scale_hat>.8h")
    d.emit(f"mls V<{corrected}>.8h, V<{corr}>.8h, V<q_inv>.8h")

    invxy = d.mm(corrected, z)
    outputs = [d.mm(invxy, y), d.mm(invxy, x), d.mm(corrected, xy)]
    for i, value in enumerate(outputs):
        d.store(value, "x0", 16 * i)
    assert len(d.lines) == 164
    return d.lines


def region(name: str, live: str, range_note: str, lines: list[str]) -> list[str]:
    return [
        ".p2align 4",
        f".global {name}",
        f"{name}:",
        f"// live-in: {live}",
        "// live-out: x0-x3 unchanged where present; contracted stores updated.",
        f"// coefficient range: {range_note}",
        "// reserved physical registers: x18-x30, sp, xzr; no physical vector registers.",
        f"{name}_slothy_start:",
        *["    " + line for line in lines],
        f"{name}_slothy_end:",
        "    ret",
        "",
    ]


source = [".text"]
source += region(
    "p10_num_pair",
    "x0-x3 pointers and Q<q_num>/Q<qi_num> fixed vectors",
    "K1 R0 inputs abs <=28765; cofactor abs <=26980; determinant abs <=8724",
    numerator_pair(),
)
source += region(
    "p10_finish_tile",
    "x0-x1 pointers and Q<q_finish>/Q<qi_finish> fixed vectors",
    "cofactor abs <=26980 and recovered inverse abs <=1994; FR0 output abs <=2550",
    finish_tile(),
)
source += region(
    "p10_inverse3",
    "x0 output pointer and x1 final-prefix pointer",
    "R1 prefix inputs abs <=1995 and nonzero; corrected inverse abs <=1741",
    inverse3(),
)

print("*** Begin Patch")
print("*** Add File: experiments/gt864-p10-baseinv/candidate.sym.S")
for line in source:
    print("+" + line)
print("*** End Patch")
