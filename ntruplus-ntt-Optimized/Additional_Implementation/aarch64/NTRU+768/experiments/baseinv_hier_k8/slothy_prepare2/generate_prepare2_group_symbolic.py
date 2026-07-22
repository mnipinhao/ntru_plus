#!/usr/bin/env python3
"""Generate the explicit symbolic DAG for one GT HIERK8 prepare2 group."""

from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "prepare2_group.sym.S"


def emit(lines, instruction=""):
    lines.append(f"\t{instruction}" if instruction else "")


def reduce_sum(lines, prefix, output, terms):
    """Emit one widening sum of products and Montgomery reduction."""

    lo = f"{prefix}_lo"
    hi = f"{prefix}_hi"
    mraw = f"{prefix}_mraw"
    mred = f"{prefix}_mred"
    lhs, rhs = terms[0]
    emit(lines, f"smull V<{lo}>.4s, V<{lhs}>.4h, V<{rhs}>.4h")
    emit(lines, f"smull2 V<{hi}>.4s, V<{lhs}>.8h, V<{rhs}>.8h")
    for lhs, rhs in terms[1:]:
        emit(lines, f"smlal V<{lo}>.4s, V<{lhs}>.4h, V<{rhs}>.4h")
        emit(lines, f"smlal2 V<{hi}>.4s, V<{lhs}>.8h, V<{rhs}>.8h")
    emit(lines, f"uzp1 V<{mraw}>.8h, V<{lo}>.8h, V<{hi}>.8h")
    emit(lines, f"mul V<{mred}>.8h, V<{mraw}>.8h, v0.h[2]")
    emit(lines, f"smlal V<{lo}>.4s, V<{mred}>.4h, v0.h[0]")
    emit(lines, f"smlal2 V<{hi}>.4s, V<{mred}>.8h, v0.h[0]")
    emit(lines, f"uzp2 V<{output}>.8h, V<{lo}>.8h, V<{hi}>.8h")


def prepare_block(lines, block, zero="zero"):
    p = f"b{block}"
    a0, a1, a2, a3 = (f"{p}_a{i}" for i in range(4))
    zeta = f"{p}_zeta"
    neg_a2 = f"{p}_neg_a2"
    neg_a3 = f"{p}_neg_a3"
    neg2a2 = f"{p}_neg2a2"
    neg2a3 = f"{p}_neg2a3"
    t0a = f"{p}_t0a"
    t1a = f"{p}_t1a"
    t0 = f"{p}_t0"
    t1 = f"{p}_t1"
    t2 = f"{p}_t2"
    negt1 = f"{p}_negt1"
    den = f"{p}_den"

    emit(lines, f"// Block {block}: closed-form quartic prepare")
    emit(lines, f"sub V<{neg_a2}>.8h, V<{zero}>.8h, V<{a2}>.8h")
    emit(lines, f"sub V<{neg_a3}>.8h, V<{zero}>.8h, V<{a3}>.8h")
    emit(lines, f"add V<{neg2a2}>.8h, V<{neg_a2}>.8h, V<{neg_a2}>.8h")
    emit(lines, f"add V<{neg2a3}>.8h, V<{neg_a3}>.8h, V<{neg_a3}>.8h")

    reduce_sum(lines, f"{p}_r_t0a", t0a, [(a2, a2), (a1, neg2a3)])
    reduce_sum(lines, f"{p}_r_t1a", t1a, [(a3, a3)])
    reduce_sum(lines, f"{p}_r_t0", t0, [(t0a, zeta), (a0, a0)])
    reduce_sum(
        lines,
        f"{p}_r_t1",
        t1,
        [(t1a, zeta), (a1, a1), (a0, neg2a2)],
    )
    reduce_sum(lines, f"{p}_r_t2", t2, [(t1, zeta)])
    emit(lines, f"sub V<{negt1}>.8h, V<{zero}>.8h, V<{t1}>.8h")
    reduce_sum(lines, f"{p}_r_den", den, [(t0, t0), (negt1, t2)])

    reduce_sum(lines, f"{p}_r_n0", f"{p}_n0", [(a0, t0), (a2, t2)])
    reduce_sum(lines, f"{p}_r_n1", f"{p}_n1", [(a3, t2), (a1, t0)])
    reduce_sum(lines, f"{p}_r_n2", f"{p}_n2", [(a2, t0), (a0, t1)])
    reduce_sum(lines, f"{p}_r_n3", f"{p}_n3", [(a1, t1), (a3, t0)])
    emit(
        lines,
        f"st4 {{V<{p}_n0>.8h, V<{p}_n1>.8h, V<{p}_n2>.8h, "
        f"V<{p}_n3>.8h}}, [x0], #64",
    )
    emit(lines)


def build_source():
    lines = [
        "/*",
        " * Generated symbolic Slothy source for one benchmark-only HIERK8",
        " * prepare2 group. See kernel-contract.yml and instruction-dag.yml.",
        " *",
        " * Live-in/out: x0-x5 pointer streams and fixed v0 constants.",
        " * No spills and no secret-dependent control or memory addressing.",
        " */",
        "",
        ".text",
        ".align 2",
        "// Live-in: x0-x5 pointer streams and fixed v0 constants.",
        "// Live-out: exact stores, x0-x5 pointer advances, and v0 preserved.",
        "// Range: current GT baseinv signed-int16 inputs, int32 widened products, exact int16 outputs.",
        "// Reserved physical registers: x6-x30, sp, and fixed vector v0.",
        "// The loads define Q<b0_zeta> Q<b1_zeta> Q<b2_zeta> Q<b0_a0> Q<b0_a1> Q<b0_a2> Q<b0_a3>.",
        "// They also define Q<b1_a0> Q<b1_a1> Q<b1_a2> Q<b1_a3> Q<b2_a0> Q<b2_a1> Q<b2_a2> Q<b2_a3>.",
        "slothy_start_gt_baseinv_prepare2_group:",
        "// Live-in: x0 x1 x4 x5 and fixed v0; loaded values are defined below.",
        "// Live-out: x0 x1 x4 x5 advances and Q<c01> for phase 2.",
        "// Range: current GT baseinv int16 inputs, int32 products, exact int16 outputs.",
        "// Reserved physical registers: x6-x30, sp, and fixed vector v0.",
        "slothy_start_gt_baseinv_prepare2_phase01:",
        "\tld1 {V<b0_zeta>.8h, V<b1_zeta>.8h}, [x5], #32",
        "\tld4 {V<b0_a0>.8h, V<b0_a1>.8h, V<b0_a2>.8h, V<b0_a3>.8h}, [x4], #64",
        "\tmovi V<zero>.8h, #0",
        "",
    ]

    prepare_block(lines, 0)
    emit(
        lines,
        "ld4 {V<b1_a0>.8h, V<b1_a1>.8h, V<b1_a2>.8h, V<b1_a3>.8h}, [x4], #64",
    )
    prepare_block(lines, 1)
    reduce_sum(lines, "c01_r", "c01", [("b0_den", "b1_den")])
    emit(lines, "stp Q<b0_den>, Q<b1_den>, [x1], #32")
    lines.append("slothy_end_gt_baseinv_prepare2_phase01:")
    emit(lines)

    lines.extend(
        [
            "// Live-in: x0-x5, fixed v0, and Q<c01> from phase 01.",
            "// Live-out: exact final stores and x0-x5 group pointer advances.",
            "// Range: current GT baseinv int16 inputs, int32 products, exact int16 outputs.",
            "// Reserved physical registers: x6-x30, sp, and fixed vector v0.",
            "// The loads define Q<b2_zeta> Q<b2_a0> Q<b2_a1> Q<b2_a2> Q<b2_a3>.",
            "slothy_start_gt_baseinv_prepare2_phase2:",
        ]
    )
    emit(lines, "ldr Q<b2_zeta>, [x5], #16")
    emit(
        lines,
        "ld4 {V<b2_a0>.8h, V<b2_a1>.8h, V<b2_a2>.8h, V<b2_a3>.8h}, [x4], #64",
    )
    emit(lines, "movi V<zero2>.8h, #0")
    prepare_block(lines, 2, zero="zero2")
    reduce_sum(lines, "group_r", "group_product", [("c01", "b2_den")])
    emit(lines, "str Q<b2_den>, [x1], #16")
    emit(lines, "str Q<c01>, [x2], #16")
    emit(lines, "str Q<group_product>, [x3], #16")
    lines.append("slothy_end_gt_baseinv_prepare2_phase2:")
    lines.append("slothy_end_gt_baseinv_prepare2_group:")
    lines.append("")
    return "\n".join(lines)


def main():
    OUTPUT.write_text(build_source(), encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
