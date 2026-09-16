#!/usr/bin/env python3
"""Generate the three unscheduled A1 tail-NTT16 architecture candidates."""

from __future__ import annotations

from pathlib import Path

Q = 3457
THETA = 9
RESIDUES = (1, 5)
REVERSE4 = (0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15)
PACKED_STAGE_EXPONENTS = (
    (0, 0, 0, 0, 0, 0, 0, 0),
    (0, 0, 0, 0, 4, 4, 4, 4),
    (0, 0, 4, 4, 2, 2, 6, 6),
    (0, 4, 2, 6, 1, 5, 3, 7),
)
HERE = Path(__file__).resolve().parent
M5L = HERE.parent / "gt_forward_tail_ntt16_slothy/slothy-output/gt864_forward_tail_ntt16.n1.opt.S"
M5RD = HERE.parent / "gt_forward_level2_one_mul_b3"
OUT = HERE / "build/tail_variants.S"


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def reciprocal(value: int) -> int:
    value = centered(value)
    rounded = (abs(value) * (1 << 15) + Q // 2) // Q
    return -rounded if value < 0 else rounded


def vector(values: list[int]) -> list[str]:
    assert len(values) == 8
    return ["    .short " + ", ".join(str(value) for value in values)]


def packed_table(top: int) -> list[str]:
    omega16 = pow(THETA, 54, Q)
    twist = [centered(pow(THETA, 9 * RESIDUES[top] * t, Q))
             for t in range(16)]
    lines: list[str] = []
    lines += vector(twist[:8])
    lines += vector([reciprocal(value) for value in twist[:8]])
    lines += vector(twist[8:])
    lines += vector([reciprocal(value) for value in twist[8:]])
    for exponents in PACKED_STAGE_EXPONENTS:
        lanes = [centered(pow(omega16, exponent, Q))
                 for exponent in exponents]
        lines += vector(lanes)
        lines += vector([reciprocal(value) for value in lanes])
    # Halfword order 0,4,2,6,1,5,3,7 as a byte TBL permutation.
    indexes = []
    for lane in (0, 4, 2, 6, 1, 5, 3, 7):
        indexes += [2 * lane, 2 * lane + 1]
    lines.append("    .byte " + ", ".join(str(value) for value in indexes))
    return lines


def extract_current_body() -> list[str]:
    text = M5L.read_text(encoding="utf-8")
    start = text.index("        movi v30.8H, #0")
    end = text.index("        gt864_forward_tail_ntt16_slothy_end:")
    body = []
    for line in text[start:end].splitlines():
        instruction = line.split("//", 1)[0].rstrip()
        if instruction.strip():
            body.append("    " + instruction.strip())
    assert len(body) == 65
    return body


def emit_wrappers(lines: list[str], body: list[str]) -> None:
    lines += [
        ".text", ".p2align 2",
        ".global gt864_tail_t0_current", ".global _gt864_tail_t0_current",
        "gt864_tail_t0_current:", "_gt864_tail_t0_current:",
        "    mov x9, x0", "    mov x10, x1", "    mov x12, x30",
        "    mov x4, #16", "    mov w3, #3457", "    dup v17.8h, w3",
    ]
    for bank in range(6):
        top = bank // 3
        lines += [
            f"    add x1, x10, #{2 * bank}",
            f"    adr x2, .La1_packed_top{top}",
            "    bl .La1_t0_one_bank",
            f"    stp q27, q7, [x9, #{32 * bank}]",
        ]
    lines += ["    mov x30, x12", "    ret", ".La1_t0_one_bank:"]
    lines += body
    lines += ["    ret", ""]

    # T1 changes only the physical input load: two contiguous q loads replace
    # two zeroing instructions plus sixteen lane loads. Arithmetic is identical.
    gather_prefixes = ("movi v30.8H", "movi v20.8H",
                       "ld1 { v30.H }", "ld1 { v20.H }")
    t1_body = ["    ldp q30, q20, [x1]"] + [
        line for line in body
        if not line.strip().startswith(gather_prefixes)
    ]
    assert len(t1_body) == 48
    lines += [
        ".global gt864_tail_t1_bank_major", ".global _gt864_tail_t1_bank_major",
        "gt864_tail_t1_bank_major:", "_gt864_tail_t1_bank_major:",
        "    mov x9, x0", "    mov x10, x1", "    mov x12, x30",
        "    mov w3, #3457", "    dup v17.8h, w3",
    ]
    for bank in range(6):
        top = bank // 3
        lines += [
            f"    add x1, x10, #{32 * bank}",
            f"    adr x2, .La1_packed_top{top}",
            "    bl .La1_t1_one_bank",
            f"    stp q27, q7, [x9, #{32 * bank}]",
        ]
    lines += ["    mov x30, x12", "    ret", ".La1_t1_one_bank:"]
    lines += t1_body
    lines += ["    ret", ""]


def emit_transpose(lines: list[str], source_base: int, out_offset: int) -> None:
    # 8 vectors whose lanes are banks -> 8 vectors whose lanes are columns.
    for pair in range(4):
        a = source_base + 2 * pair
        b = a + 1
        lines += [
            f"    trn1 v{2 * pair}.8h, v{a}.8h, v{b}.8h",
            f"    trn2 v{2 * pair + 1}.8h, v{a}.8h, v{b}.8h",
        ]
    for group in range(2):
        a, b = 4 * group, 4 * group + 2
        dst = source_base + 4 * group
        lines += [
            f"    trn1 v{dst}.4s, v{a}.4s, v{b}.4s",
            f"    trn2 v{dst + 1}.4s, v{a}.4s, v{b}.4s",
            f"    trn1 v{dst + 2}.4s, v{a + 1}.4s, v{b + 1}.4s",
            f"    trn2 v{dst + 3}.4s, v{a + 1}.4s, v{b + 1}.4s",
        ]
    lines += [
        f"    trn1 v0.2d, v{source_base}.2d, v{source_base + 4}.2d",
        f"    trn2 v1.2d, v{source_base}.2d, v{source_base + 4}.2d",
        f"    trn1 v2.2d, v{source_base + 1}.2d, v{source_base + 5}.2d",
        f"    trn2 v3.2d, v{source_base + 1}.2d, v{source_base + 5}.2d",
        f"    trn1 v4.2d, v{source_base + 2}.2d, v{source_base + 6}.2d",
        f"    trn2 v5.2d, v{source_base + 2}.2d, v{source_base + 6}.2d",
        f"    trn1 v6.2d, v{source_base + 3}.2d, v{source_base + 7}.2d",
        f"    trn2 v7.2d, v{source_base + 3}.2d, v{source_base + 7}.2d",
    ]
    transpose_register = (0, 4, 2, 6, 1, 5, 3, 7)
    for bank in range(6):
        lines.append(
            f"    str q{transpose_register[bank]}, "
            f"[x0, #{32 * bank + out_offset}]")


def emit_t2(lines: list[str]) -> None:
    lines += [
        ".global gt864_tail_t2_six_bank_simd", ".global _gt864_tail_t2_six_bank_simd",
        "gt864_tail_t2_six_bank_simd:", "_gt864_tail_t2_six_bank_simd:",
        "    mov w3, #3457", "    dup v7.8h, w3",
        "    adr x2, .La1_t2_twist",
    ]
    for t, position in enumerate(REVERSE4):
        state = 16 + position
        lines += [
            f"    ldr q{state}, [x1, #{16 * t}]",
            "    ldp q5, q6, [x2], #32",
            f"    sqrdmulh v2.8h, v{state}.8h, v6.8h",
            f"    mul v{state}.8h, v{state}.8h, v5.8h",
            f"    mls v{state}.8h, v2.8h, v7.8h",
        ]
    lines.append("    adr x2, .La1_t2_stage")
    for length in (2, 4, 8, 16):
        half = length // 2
        for start in range(0, 16, length):
            for j in range(half):
                left = 16 + start + j
                right = left + half
                lines += [
                    "    ldr q0, [x2], #16",
                    f"    sqrdmulh v2.8h, v{right}.8h, v0.h[1]",
                    f"    mul v1.8h, v{right}.8h, v0.h[0]",
                    "    mls v1.8h, v2.8h, v7.8h",
                    f"    sub v{right}.8h, v{left}.8h, v1.8h",
                    f"    add v{left}.8h, v{left}.8h, v1.8h",
                ]
    emit_transpose(lines, 16, 0)
    emit_transpose(lines, 24, 16)
    lines += ["    ret", ""]


def emit_layout_only(lines: list[str]) -> None:
    lines += [
        ".global gt864_tail_layout_bank_major_inplace",
        ".global _gt864_tail_layout_bank_major_inplace",
        "gt864_tail_layout_bank_major_inplace:",
        "_gt864_tail_layout_bank_major_inplace:",
    ]
    for t in range(16):
        lines.append(f"    ldr q{16 + t}, [x0, #{16 * t}]")
    emit_transpose(lines, 16, 0)
    emit_transpose(lines, 24, 16)
    lines += ["    ret", ""]


def helper_region(text: str) -> tuple[str, list[str], str]:
    marker = ".Lgt864_m5rd_one_bank:"
    start = text.index(marker) + len(marker)
    end_label = text.index(
        "\ngt864_forward_six_bank_pass2_all_one_mul_b3_end:", start)
    end = text.rindex("\n    ret", start, end_label)
    instructions = [line for line in text[start:end].splitlines() if line.strip()]
    assert len(instructions) == 569
    return text[:start], instructions, text[end:]


def bank_major_calls(text: str) -> str:
    for bank, old in enumerate((0, 2, 4, 6, 8, 10)):
        needle = f"    add x1, x1, #{old}\n"
        assert text.count(needle) == 1
        text = text.replace(needle, f"    add x1, x1, #{32 * bank}\n")
    return text


def append_one_bank(text: str, tag: str, tail_offset: int) -> str:
    local = f"gt864_a1{tag}"
    table = text.index(f"\n.L{local}_common:")
    stores = []
    outputs = (31, 1, 9, 26, 20, 24, 30, 29, 22,
               19, 21, 23, 8, 10, 12, 6, 27, 0)
    for index, register in enumerate(outputs):
        stores.append(f"    str q{register}, [x6, #{16 * index}]")
    wrapper = [
        "", ".p2align 2", f".global gt864_one_bank_a1_{tag}",
        f".global _gt864_one_bank_a1_{tag}",
        f"gt864_one_bank_a1_{tag}:", f"_gt864_one_bank_a1_{tag}:",
        "    mov x6, x0", "    mov x7, x1", "    mov x16, x30",
        "    mov x4, #16", f"    adr x5, .L{local}_common",
        "    ldp q14, q15, [x5], #32", "    ldr q13, [x5]",
        "    mov x0, x7", f"    add x1, x7, #{tail_offset}",
        f"    adr x2, .L{local}_ntt16_top0",
        f"    adr x3, .L{local}_ntt9_top0",
        f"    bl .L{local}_one_bank",
    ] + stores + ["    mov x30, x16", "    ret", ""]
    return text[:table] + "\n".join(wrapper) + text[table:]


def emit_full_candidates() -> None:
    source = (M5RD / "gt864_forward_six_bank_all_one_mul_b3.S").read_text(
        encoding="utf-8")
    prefix, helper, suffix = helper_region(source)

    t0 = source.replace("m5rd", "a1t0").replace(
        "gt864_forward_six_bank_pass2_all_one_mul_b3",
        "gt864_forward_six_bank_pass2_a1_t0")
    t0 = append_one_bank(t0, "t0", 1536)

    gather = {"    movi v8.8H, #0", "    movi v2.8H, #0"}
    gather.update(f"    ld1 {{ v8.H }}[{lane}], [x1], x4" for lane in range(8))
    gather.update(f"    ld1 {{ v2.H }}[{lane}], [x1], x4" for lane in range(8))
    assert sum(line in gather for line in helper) == 18
    t1_helper = ["    ldp q8, q2, [x1]"] + [line for line in helper if line not in gather]
    assert len(t1_helper) == 552
    t1 = bank_major_calls(prefix + "\n" + "\n".join(t1_helper) + suffix)
    t1 = t1.replace("m5rd", "a1t1").replace(
        "gt864_forward_six_bank_pass2_all_one_mul_b3",
        "gt864_forward_six_bank_pass2_a1_t1")
    t1 = append_one_bank(t1, "t1", 1536)

    first_main = helper.index("    ldr q12, [x2], #16")
    tail_only_after_main = {
        "    sqrdmulh v3.8H, v25.8H, v1.8H",
        "    mls v27.8H, v3.8H, v14.8H",
        "    add v2.8H, v28.8H, v27.8H",
        "    sub v1.8H, v28.8H, v27.8H",
        "    tbl v17.16B, {v2.16B}, v13.16B",
        "    tbl v16.16B, {v1.16B}, v13.16B",
    }
    assert all(line in helper[first_main:] for line in tail_only_after_main)
    t2_helper = [
        "    ldp q17, q16, [x1]",
        "    add x2, x2, #192",
    ] + [line for line in helper[first_main:] if line not in tail_only_after_main]
    t2 = bank_major_calls(prefix + "\n" + "\n".join(t2_helper) + suffix)
    t2 = t2.replace("m5rd", "a1t2").replace(
        "gt864_forward_six_bank_pass2_all_one_mul_b3",
        "gt864_forward_six_bank_pass2_a1_t2")
    t2 = append_one_bank(t2, "t2", 1536)

    wrapper = (M5RD / "gt864_forward_poly_ntt_all_one_mul_b3.S").read_text(
        encoding="utf-8")
    (HERE / "build/full_t0_wrapper.S").write_text(
        wrapper.replace("gt864_forward_six_bank_pass2_all_one_mul_b3",
                        "gt864_forward_six_bank_pass2_a1_t0"),
        encoding="utf-8")
    insertion = "    bl gt864_top_split_ld3\n"
    assert wrapper.count(insertion) == 1
    for name, prep, pass2 in (
        ("t1", "gt864_tail_layout_bank_major_inplace", "gt864_forward_six_bank_pass2_a1_t1"),
        ("t2", "gt864_tail_t2_six_bank_simd", "gt864_forward_six_bank_pass2_a1_t2"),
    ):
        candidate = wrapper.replace(
            insertion,
            insertion + "    add x0, sp, #1536\n    mov x1, x0\n" +
            f"    bl {prep}\n")
        candidate = candidate.replace(
            "gt864_forward_poly_ntt_all_one_mul_b3",
            f"gt864_forward_poly_ntt_a1_{name}")
        candidate = candidate.replace(
            "gt864_forward_six_bank_pass2_all_one_mul_b3", pass2)
        (HERE / f"build/full_{name}_wrapper.S").write_text(candidate, encoding="utf-8")
    (HERE / "build/pass2_t0.S").write_text(t0, encoding="utf-8")
    (HERE / "build/pass2_t1.S").write_text(t1, encoding="utf-8")
    (HERE / "build/pass2_t2.S").write_text(t2, encoding="utf-8")


def emit_tables(lines: list[str]) -> None:
    omega16 = pow(THETA, 54, Q)
    # Keep local constants in the text section so one `adr` form works in both
    # Mach-O local validation and the Pi 5 ELF benchmark build.
    lines += [".text", ".p2align 4", ".La1_packed_top0:"]
    lines += packed_table(0)
    lines += [".p2align 4", ".La1_packed_top1:"]
    lines += packed_table(1)
    lines += [".p2align 4", ".La1_t2_twist:"]
    for t in range(16):
        values = [centered(pow(THETA, 9 * RESIDUES[bank // 3] * t, Q))
                  if bank < 6 else 0 for bank in range(8)]
        lines += vector(values)
        lines += vector([reciprocal(value) for value in values])
    lines += [".p2align 4", ".La1_t2_stage:"]
    for length in (2, 4, 8, 16):
        half = length // 2
        for _start in range(0, 16, length):
            for j in range(half):
                value = centered(pow(omega16, j * 16 // length, Q))
                lines += vector([value, reciprocal(value), 0, 0, 0, 0, 0, 0])


def main() -> None:
    body = extract_current_body()
    lines = [
        "/* A1 generated unscheduled architecture shootout; do not promote. */",
    ]
    emit_wrappers(lines, body)
    emit_t2(lines)
    emit_layout_only(lines)
    emit_tables(lines)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    emit_full_candidates()
    print(f"generated={OUT}")
    print("T0_algorithm10=36")
    print("T1_algorithm10=36")
    print("T2_algorithm10=48")


if __name__ == "__main__":
    main()
