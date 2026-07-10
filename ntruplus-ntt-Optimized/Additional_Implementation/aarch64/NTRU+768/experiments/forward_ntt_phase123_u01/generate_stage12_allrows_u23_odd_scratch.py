#!/usr/bin/env python3
"""Generate the all-row shared-prefix odd U23 -> stage12 scratch prototype."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "phase123_u23_odd_stage12_allrows_scratch_stripe67.sym.s"

ODD_ITERS = ((1, "b"), (3, "a"), (5, "c"), (7, "b"))
ROW_SCRATCH_BASE = {"row0": 0, "row1": 128, "row2": 256}
ROW_DST = {"row0": "x4", "row1": "x5", "row2": "x6"}
SCRATCH_SLOT = {6: 0, 7: 16, 14: 32, 15: 48, 22: 64, 23: 80, 30: 96, 31: 112}

Z = {
    "Z1e": "v24",
    "Z1o": "v25",
    "Z3e": "v28",
    "Z3o": "v29",
    "Z5e": "v30",
    "Z5o": "v31",
}

TYPE_SLOTS = {
    "a": (("Z5e", "Z3e", "Z1e"), ("Z1o", "Z5o", "Z3o")),
    "b": (("Z1e", "Z5e", "Z3e"), ("Z3o", "Z1o", "Z5o")),
    "c": (("Z3e", "Z1e", "Z5e"), ("Z5o", "Z3o", "Z1o")),
}


def scratch_offset(row: str, q_index: int) -> int:
    return ROW_SCRATCH_BASE[row] + SCRATCH_SLOT[q_index]


def emit_common_prefix(lines: list[str], iteration: int) -> None:
    x1_off = iteration * 32
    x3_off = iteration * 384
    lines.extend(
        [
            f"    // U23 odd iter{iteration}: shared P1/P3/P5 prefix.",
            f"    add x7, x3, #{x3_off}",
            f"    ldr q10, [x1, #{x1_off + 784}]",
            f"    ldr q12, [x1, #{x1_off + 1040}]",
            f"    ldr q14, [x1, #{x1_off + 1296}]",
            "    mul v16.8h, v10.8h, v0.h[4]",
            "    mul v18.8h, v12.8h, v0.h[4]",
            "    mul v20.8h, v14.8h, v0.h[4]",
            "    sqrdmulh v1.8h, v10.8h, v0.h[5]",
            "    sqrdmulh v3.8h, v12.8h, v0.h[5]",
            "    sqrdmulh v7.8h, v14.8h, v0.h[5]",
            "    mls v16.8h, v1.8h, v0.h[0]",
            "    mls v18.8h, v3.8h, v0.h[0]",
            "    mls v20.8h, v7.8h, v0.h[0]",
            "    sub v10.8h, v10.8h, v16.8h",
            "    sub v12.8h, v12.8h, v18.8h",
            "    sub v14.8h, v14.8h, v20.8h",
            f"    ldr q4, [x1, #{x1_off + 16}]",
            f"    ldr q6, [x1, #{x1_off + 272}]",
            f"    ldr q8, [x1, #{x1_off + 528}]",
            "    add v10.8h, v10.8h, v4.8h",
            "    add v12.8h, v12.8h, v6.8h",
            "    add v14.8h, v14.8h, v8.8h",
            "    add v4.8h, v4.8h, v16.8h",
            "    add v6.8h, v6.8h, v18.8h",
            "    add v8.8h, v8.8h, v20.8h",
            "    ldp q1, q2, [x7, #32]",
            "    sqrdmulh v3.8h, v10.8h, v2.8h",
            "    mul v10.8h, v10.8h, v1.8h",
            "    mls v10.8h, v3.8h, v0.h[0]",
            "    ldp q1, q2, [x7, #96]",
            "    sqrdmulh v3.8h, v12.8h, v2.8h",
            "    mul v12.8h, v12.8h, v1.8h",
            "    mls v12.8h, v3.8h, v0.h[0]",
            "    ldp q1, q2, [x7, #160]",
            "    sqrdmulh v3.8h, v14.8h, v2.8h",
            "    mul v14.8h, v14.8h, v1.8h",
            "    mls v14.8h, v3.8h, v0.h[0]",
            "    ldp q1, q2, [x7, #224]",
            "    sqrdmulh v3.8h, v4.8h, v2.8h",
            "    mul v4.8h, v4.8h, v1.8h",
            "    mls v4.8h, v3.8h, v0.h[0]",
            "    ldp q1, q2, [x7, #288]",
            "    sqrdmulh v3.8h, v6.8h, v2.8h",
            "    mul v6.8h, v6.8h, v1.8h",
            "    mls v6.8h, v3.8h, v0.h[0]",
            "    ldp q1, q2, [x7, #352]",
            "    sqrdmulh v3.8h, v8.8h, v2.8h",
            "    mul v8.8h, v8.8h, v1.8h",
            "    mls v8.8h, v3.8h, v0.h[0]",
            "    zip1 v24.2d, v4.2d, v10.2d",
            "    zip2 v25.2d, v4.2d, v10.2d",
            "    zip1 v28.2d, v6.2d, v12.2d",
            "    zip2 v29.2d, v6.2d, v12.2d",
            "    zip1 v30.2d, v8.2d, v14.2d",
            "    zip2 v31.2d, v8.2d, v14.2d",
            "",
        ]
    )


def emit_slot(lines: list[str], typ: str, slot: int, q_index: int) -> None:
    a_name, b_name, c_name = TYPE_SLOTS[typ][slot]
    a, b, c = Z[a_name], Z[b_name], Z[c_name]
    lines.extend(
        [
            f"    // Type {typ.upper()} U23 odd slot{slot + 2}: a={a_name}, b={b_name}, c={c_name} -> Q{q_index}.",
            f"    sub v6.8h, {b}.8h, {c}.8h",
            "    sqrdmulh v7.8h, v6.8h, v0.h[3]",
            "    mul v8.8h, v6.8h, v0.h[2]",
            "    mls v8.8h, v7.8h, v0.h[0]",
            f"    add v9.8h, {a}.8h, {b}.8h",
            f"    add v9.8h, v9.8h, {c}.8h",
            f"    sub v10.8h, {a}.8h, {c}.8h",
            "    add v10.8h, v10.8h, v8.8h",
            f"    sub v11.8h, {a}.8h, {b}.8h",
            "    sub v11.8h, v11.8h, v8.8h",
            f"    str q9, [x13, #{scratch_offset('row0', q_index)}]",
            f"    str q10, [x13, #{scratch_offset('row1', q_index)}]",
            f"    str q11, [x13, #{scratch_offset('row2', q_index)}]",
            "",
        ]
    )


def emit_stage12_stripe(lines: list[str], row: str, stripe: int) -> None:
    dst = ROW_DST[row]
    base = ROW_SCRATCH_BASE[row]
    q0, q8, q16, q24 = stripe, stripe + 8, stripe + 16, stripe + 24
    lines.extend(
        [
            f"    // Stage12 {row} stripe{stripe}.",
            f"    ldr q24, [x13, #{base + SCRATCH_SLOT[q0]}]",
            f"    ldr q28, [x13, #{base + SCRATCH_SLOT[q8]}]",
            f"    ldr q5, [x13, #{base + SCRATCH_SLOT[q16]}]",
            f"    ldr q13, [x13, #{base + SCRATCH_SLOT[q24]}]",
            "    add v16.8h, v28.8h, v13.8h",
            "    sqrdmulh v17.8h, v16.8h, v2.h[0]",
            "    mls v16.8h, v17.8h, v0.h[0]",
            "    sub v18.8h, v28.8h, v13.8h",
            "    sqrdmulh v19.8h, v18.8h, v4.h[0]",
            "    mul v18.8h, v18.8h, v3.h[0]",
            "    mls v18.8h, v19.8h, v0.h[0]",
            "    add v20.8h, v24.8h, v5.8h",
            "    sub v21.8h, v24.8h, v5.8h",
            "    add v22.8h, v20.8h, v16.8h",
            "    sub v23.8h, v20.8h, v16.8h",
            "    add v26.8h, v21.8h, v18.8h",
            "    sub v27.8h, v21.8h, v18.8h",
            f"    str q22, [{dst}, #{16 * q0}]",
            f"    str q23, [{dst}, #{16 * q8}]",
            f"    str q26, [{dst}, #{16 * q16}]",
            f"    str q27, [{dst}, #{16 * q24}]",
            "",
        ]
    )


def main() -> int:
    lines: list[str] = [
        "// Generated source-order prototype for odd all-row shared-prefix U23 -> NTT32 stage12.",
        "// Do not edit the generated body by hand; edit generate_stage12_allrows_u23_odd_scratch.py.",
        ".text",
        "",
        "slothy_start_phase123_u23_odd_stage12_allrows_scratch_stripe67:",
    ]
    for iteration, typ in ODD_ITERS:
        emit_common_prefix(lines, iteration)
        emit_slot(lines, typ, 0, 4 * iteration + 2)
        emit_slot(lines, typ, 1, 4 * iteration + 3)
    lines.extend(
        [
            "    ldr q2, [x12, #16]",
            "    ldr q3, [x12, #32]",
            "    ldr q4, [x12, #48]",
            "",
        ]
    )
    for row in ("row0", "row1", "row2"):
        for stripe in (6, 7):
            emit_stage12_stripe(lines, row, stripe)
    lines.append("slothy_end_phase123_u23_odd_stage12_allrows_scratch_stripe67:")
    lines.append("")
    OUT.write_text("\n".join(lines))
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
