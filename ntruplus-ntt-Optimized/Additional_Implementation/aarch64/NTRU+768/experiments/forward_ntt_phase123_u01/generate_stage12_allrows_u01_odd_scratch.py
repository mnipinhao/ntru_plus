#!/usr/bin/env python3
"""Generate the all-row shared-prefix odd U01 -> stage12 scratch prototype."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "phase123_u01_odd_stage12_allrows_scratch_stripe45.sym.s"

ODD_ITERS = ((1, "b"), (3, "a"), (5, "c"), (7, "b"))
ROW_SCRATCH_BASE = {"row0": 0, "row1": 128, "row2": 256}
ROW_DST = {"row0": "x4", "row1": "x5", "row2": "x6"}
SCRATCH_SLOT = {4: 0, 5: 16, 12: 32, 13: 48, 20: 64, 21: 80, 28: 96, 29: 112}

Z = {
    "Z0e": "v22",
    "Z0o": "v23",
    "Z2e": "v26",
    "Z2o": "v27",
    "Z4e": "v30",
    "Z4o": "v31",
}

TYPE_SLOTS = {
    "a": (("Z0e", "Z4e", "Z2e"), ("Z2o", "Z0o", "Z4o")),
    "b": (("Z2e", "Z0e", "Z4e"), ("Z4o", "Z2o", "Z0o")),
    "c": (("Z4e", "Z2e", "Z0e"), ("Z0o", "Z4o", "Z2o")),
}


def scratch_offset(row: str, q_index: int) -> int:
    return ROW_SCRATCH_BASE[row] + SCRATCH_SLOT[q_index]


def emit_common_prefix(lines: list[str], iteration: int) -> None:
    x1_off = iteration * 32
    x3_off = iteration * 384
    lines.extend(
        [
            f"    // U01 odd iter{iteration}: shared P0/P2/P4 prefix.",
            f"    add x7, x3, #{x3_off}",
            f"    ldr q10, [x1, #{x1_off + 768}]",
            f"    ldr q12, [x1, #{x1_off + 1024}]",
            f"    ldr q14, [x1, #{x1_off + 1280}]",
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
            f"    ldr q4, [x1, #{x1_off}]",
            f"    ldr q6, [x1, #{x1_off + 256}]",
            f"    ldr q8, [x1, #{x1_off + 512}]",
            "    add v10.8h, v10.8h, v4.8h",
            "    add v12.8h, v12.8h, v6.8h",
            "    add v14.8h, v14.8h, v8.8h",
            "    add v4.8h, v4.8h, v16.8h",
            "    add v6.8h, v6.8h, v18.8h",
            "    add v8.8h, v8.8h, v20.8h",
            "    ldp q1, q2, [x7, #0]",
            "    sqrdmulh v3.8h, v10.8h, v2.8h",
            "    mul v10.8h, v10.8h, v1.8h",
            "    mls v10.8h, v3.8h, v0.h[0]",
            "    ldp q1, q2, [x7, #64]",
            "    sqrdmulh v3.8h, v12.8h, v2.8h",
            "    mul v12.8h, v12.8h, v1.8h",
            "    mls v12.8h, v3.8h, v0.h[0]",
            "    ldp q1, q2, [x7, #128]",
            "    sqrdmulh v3.8h, v14.8h, v2.8h",
            "    mul v14.8h, v14.8h, v1.8h",
            "    mls v14.8h, v3.8h, v0.h[0]",
            "    ldp q1, q2, [x7, #192]",
            "    sqrdmulh v3.8h, v4.8h, v2.8h",
            "    mul v4.8h, v4.8h, v1.8h",
            "    mls v4.8h, v3.8h, v0.h[0]",
            "    ldp q1, q2, [x7, #256]",
            "    sqrdmulh v3.8h, v6.8h, v2.8h",
            "    mul v6.8h, v6.8h, v1.8h",
            "    mls v6.8h, v3.8h, v0.h[0]",
            "    ldp q1, q2, [x7, #320]",
            "    sqrdmulh v3.8h, v8.8h, v2.8h",
            "    mul v8.8h, v8.8h, v1.8h",
            "    mls v8.8h, v3.8h, v0.h[0]",
            "    zip1 v22.2d, v4.2d, v10.2d",
            "    zip2 v23.2d, v4.2d, v10.2d",
            "    zip1 v26.2d, v6.2d, v12.2d",
            "    zip2 v27.2d, v6.2d, v12.2d",
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
            f"    // Type {typ.upper()} U01 odd slot{slot}: a={a_name}, b={b_name}, c={c_name} -> Q{q_index}.",
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
        "// Generated source-order prototype for odd all-row shared-prefix U01 -> NTT32 stage12.",
        "// Do not edit the generated body by hand; edit generate_stage12_allrows_u01_odd_scratch.py.",
        ".text",
        "",
        "slothy_start_phase123_u01_odd_stage12_allrows_scratch_stripe45:",
    ]
    for iteration, typ in ODD_ITERS:
        emit_common_prefix(lines, iteration)
        emit_slot(lines, typ, 0, 4 * iteration)
        emit_slot(lines, typ, 1, 4 * iteration + 1)
    lines.extend(
        [
            "    ldr q2, [x12, #16]",
            "    ldr q3, [x12, #32]",
            "    ldr q4, [x12, #48]",
            "",
        ]
    )
    for row in ("row0", "row1", "row2"):
        for stripe in (4, 5):
            emit_stage12_stripe(lines, row, stripe)
    lines.append("slothy_end_phase123_u01_odd_stage12_allrows_scratch_stripe45:")
    lines.append("")
    OUT.write_text("\n".join(lines))
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
