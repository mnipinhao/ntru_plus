#!/usr/bin/env python3
"""Generate a lane-native CT inverse from the frozen Official GS network."""

import argparse
from pathlib import Path

from derive_lane_native_ct import (
    Q, derive, effective_twiddle, parse_array, qinv_word, stored_twiddle,
)


CT_LEVEL6 = """#ct-level6-unity-twiddle
vpaddw %ymm7,  %ymm3, %ymm11
vpaddw %ymm8,  %ymm4, %ymm12
vpaddw %ymm9,  %ymm5, %ymm13
vpaddw %ymm10, %ymm6, %ymm14
vpsubw %ymm7,  %ymm3, %ymm7
vpsubw %ymm8,  %ymm4, %ymm8
vpsubw %ymm9,  %ymm5, %ymm9
vpsubw %ymm10, %ymm6, %ymm10

#range checkpoint: only the four unreduced CT sum paths
vpmulhrsw %ymm1, %ymm13, %ymm5
vpmulhrsw %ymm1, %ymm14, %ymm6
vpmullw %ymm0, %ymm5, %ymm5
vpmullw %ymm0, %ymm6, %ymm6
vpsubw %ymm5, %ymm13, %ymm13
vpsubw %ymm6, %ymm14, %ymm14
vpmulhrsw %ymm1, %ymm9, %ymm5
vpmulhrsw %ymm1, %ymm10, %ymm6
vpmullw %ymm0, %ymm5, %ymm5
vpmullw %ymm0, %ymm6, %ymm6
vpsubw %ymm5, %ymm9, %ymm9
vpsubw %ymm6, %ymm10, %ymm10

"""


def ct_level(table_offset: int, unity_registers: tuple[int, ...] = ()) -> str:
    lines = ["#ct-mul-high-first"]
    for index, (bottom, low) in enumerate(zip(range(7, 11), range(11, 15))):
        if index in unity_registers:
            lines.append(f"# ymm{bottom} twiddle is one; retain lazy representative")
            continue
        offset = table_offset + 64 * index
        lines.extend([
            f"vmovdqa {offset}(%rdx), %ymm15",
            f"vpmullw %ymm15, %ymm{bottom}, %ymm{low}",
            f"vmovdqa {offset + 32}(%rdx), %ymm2",
            f"vpmulhw %ymm2, %ymm{bottom}, %ymm{bottom}",
        ])
    for bottom, low in zip(range(7, 11), range(11, 15)):
        index = bottom - 7
        if index in unity_registers:
            continue
        lines.extend([
            f"vpmulhw %ymm0, %ymm{low}, %ymm{low}",
            f"vpsubw %ymm{low}, %ymm{bottom}, %ymm{bottom}",
        ])
    lines.extend(["", "#ct-additive-range"])
    for top, bottom, out in zip(range(3, 7), range(7, 11), range(11, 15)):
        lines.append(f"vpaddw %ymm{bottom}, %ymm{top}, %ymm{out}")
    for top, bottom in zip(range(3, 7), range(7, 11)):
        lines.append(f"vpsubw %ymm{bottom}, %ymm{top}, %ymm{bottom}")
    return "\n".join(lines) + "\n\n"


def replace_level(text: str, level: int, replacement: str, end_marker: str) -> str:
    start = text.index("#zetas\n", text.index(f"#level{level}\n"))
    end = text.index(end_marker, start)
    return text[:start] + replacement + text[end:]


def radix3_one(data_offset: int, table_offset: int) -> str:
    x = data_offset
    y = data_offset + 256
    z = data_offset + 512
    return f"""# fused radix-3 group at data offset {data_offset}
vmovdqa {x}(%rdi), %ymm7
vmovdqa {y}(%rdi), %ymm8
vmovdqa {z}(%rdi), %ymm9
vpmullw %ymm1, %ymm8, %ymm10
vpmulhw %ymm2, %ymm8, %ymm8
vpmulhw %ymm0, %ymm10, %ymm10
vpsubw %ymm10, %ymm8, %ymm8
vpmullw %ymm3, %ymm9, %ymm11
vpmulhw %ymm4, %ymm9, %ymm9
vpmulhw %ymm0, %ymm11, %ymm11
vpsubw %ymm11, %ymm9, %ymm9
vpsubw %ymm9, %ymm8, %ymm10
vpmullw %ymm5, %ymm10, %ymm12
vpmulhw %ymm6, %ymm10, %ymm10
vpmulhw %ymm0, %ymm12, %ymm12
vpsubw %ymm12, %ymm10, %ymm10
vpaddw %ymm8, %ymm7, %ymm12
vpaddw %ymm9, %ymm12, %ymm12
vpsubw %ymm8, %ymm7, %ymm13
vpsubw %ymm10, %ymm13, %ymm13
vpsubw %ymm9, %ymm7, %ymm14
vpaddw %ymm10, %ymm14, %ymm14
vpmullw {table_offset}(%rax), %ymm12, %ymm15
vpmulhw {table_offset + 32}(%rax), %ymm12, %ymm12
vpmulhw %ymm0, %ymm15, %ymm15
vpsubw %ymm15, %ymm12, %ymm12
vpmullw {table_offset + 64}(%rax), %ymm13, %ymm7
vpmulhw {table_offset + 96}(%rax), %ymm13, %ymm13
vpmulhw %ymm0, %ymm7, %ymm7
vpsubw %ymm7, %ymm13, %ymm13
vpmullw {table_offset + 128}(%rax), %ymm14, %ymm8
vpmulhw {table_offset + 160}(%rax), %ymm14, %ymm14
vpmulhw %ymm0, %ymm8, %ymm8
vpsubw %ymm8, %ymm14, %ymm14
vmovdqa %ymm12, {x}(%rdi)
vmovdqa %ymm13, {y}(%rdi)
vmovdqa %ymm14, {z}(%rdi)
"""


def fused_radix3() -> str:
    return """#level1: paired fused root restoration and radix-3 CT
vmovdqa _16xwqinv(%rip), %ymm5
vmovdqa _16xw(%rip), %ymm6
lea official_ct_radix3_fused(%rip), %rax
lea 256(%rdi), %r8

.p2align 5
.Lofficial_ct_looptop_j_1:
vmovdqa   0(%rax), %ymm1 # c qinv
vmovdqa  32(%rax), %ymm2 # c
vmovdqa  64(%rax), %ymm3 # c^2 qinv
vmovdqa  96(%rax), %ymm4 # c^2
""" + radix3_one(0, 128) + radix3_one(768, 320) + """
add $512, %rax
add $32, %rdi
cmp %r8, %rdi
jb .Lofficial_ct_looptop_j_1

sub $256, %rdi
lea zetas_inv+464(%rip), %rdx

"""


def render(source: Path) -> str:
    text = source.read_text()
    text = text.replace(
        ".global poly_invntt_scale\npoly_invntt_scale:",
        ".global official_invntt_ct_lane_native_asm\n"
        ".type official_invntt_ct_lane_native_asm,@function\n"
        "official_invntt_ct_lane_native_asm:",
    )
    text = text.replace("_looptop", ".Lofficial_ct_looptop")
    text = text.replace("lea     zetas_inv(%rip), %rdx",
                        "lea     official_ct_twiddles(%rip), %rdx")
    text = replace_level(text, 6, CT_LEVEL6, "#shuffle\n")
    for level, offset in ((5, 0), (4, 1536), (3, 3072)):
        text = replace_level(text, level, ct_level(offset), "#shuffle\n")
    loop_end = text.index("sub $1536, %rdi")
    add = text.rfind("add $64,  %rdx", 0, loop_end)
    if add < 0:
        raise ValueError("cannot find radix-2 block table increment")
    text = text[:add] + "add $256, %rdx" + text[add + len("add $64,  %rdx"):]

    level2 = text.index("#level2\n")
    text = text[:level2] + "lea official_ct_level2(%rip), %rdx\n\n" + text[level2:]
    level2 = text.index("#level2\n")
    text = replace_level(text, 2, ct_level(0), "#store\n")
    level2_end = text.index("sub $1536, %rdi", level2)
    add = text.rfind("add $8,   %rdx", level2, level2_end)
    if add < 0:
        raise ValueError("cannot find level-2 table increment")
    text = text[:add] + "add $256, %rdx" + text[add + len("add $8,   %rdx"):]

    level1 = text.index("#level1\n")
    level0 = text.index("#level 0\n", level1)
    text = (text[:level1] + "lea zetas_inv+432(%rip), %rdx\n\n" +
            fused_radix3() + text[level0:])

    needle = "\nret\n\n.ifndef no_gnu_stack"
    text = text.replace(
        needle,
        "\nret\n.size official_invntt_ct_lane_native_asm,."
        "-official_invntt_ct_lane_native_asm\n\n.ifndef no_gnu_stack",
    )
    return "/* Generated by generate_lane_native_ct.py; do not edit. */\n" + text


def vector_pair(values: list[int]) -> list[int]:
    stored = [stored_twiddle(value) for value in values]
    return [qinv_word(value) for value in stored] + stored


def format_table(label: str, values: list[int]) -> str:
    rows = [
        ".short " + ", ".join(str(value) for value in values[offset:offset + 16])
        for offset in range(0, len(values), 16)
    ]
    return ("\n.section .rodata\n.p2align 5\n" + label + ":\n" +
            "\n".join(rows) + "\n.text\n")


def generated_tables(consts: Path) -> str:
    old = parse_array(consts, "zetas_inv")
    twiddles, scales = derive(old)
    main = []
    for level in (5, 4, 3):
        for block in range(6):
            for register in range(4):
                main.extend(vector_pair(twiddles[level][block][register]))
    level2 = []
    for block in range(6):
        for register in range(4):
            level2.extend(vector_pair(twiddles[2][block][register]))
    radix3 = []
    # Each vector has sY=sX*c and sZ=sX*c^2.  The three output
    # multipliers restore sX while absorbing the two Official alpha factors.
    for vector in range(8):
        shared_c = None
        shared_c2 = None
        outputs = []
        for group in range(2):
            alpha1 = effective_twiddle(old[794 + 8 * group])
            alpha2 = effective_twiddle(old[798 + 8 * group])
            sx = scales[group * 24 + vector]
            sy = scales[group * 24 + 8 + vector]
            sz = scales[group * 24 + 16 + vector]
            c = [sy[lane] * pow(sx[lane], Q - 2, Q) % Q for lane in range(16)]
            c2 = [sz[lane] * pow(sx[lane], Q - 2, Q) % Q for lane in range(16)]
            if any(c2[lane] != c[lane] * c[lane] % Q for lane in range(16)):
                raise ValueError("radix-3 child scales are not sX*(1,c,c^2)")
            if shared_c is not None and (c != shared_c or c2 != shared_c2):
                raise ValueError("paired radix-3 groups do not share c,c^2")
            shared_c, shared_c2 = c, c2
            out1 = [value * alpha1 % Q for value in sx]
            out2 = [value * alpha2 % Q for value in sx]
            outputs.extend((sx, out1, out2))
        for values in (shared_c, shared_c2, *outputs):
            radix3.extend(vector_pair(values))
    return (format_table("official_ct_twiddles", main) +
            format_table("official_ct_level2", level2) +
            format_table("official_ct_radix3_fused", radix3))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--consts", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    generated = render(args.source) + generated_tables(args.consts)
    if args.output:
        args.output.write_text(generated)
    elif args.check:
        if args.check.read_text() != generated:
            raise SystemExit(f"stale: {args.check}")
        print(f"lane-native-ct-check=passed file={args.check}")
    else:
        print(generated, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
