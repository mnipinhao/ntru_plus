#!/usr/bin/env python3
"""Generate the H1 direct Natural-Q decoder and preprojected-h MA2 control."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

N = 1152
DECODER = "ntruplus1152_exp001_poly_frombytes_h_natural_q"
CONSUMER = "ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4_preprojected_h"
SOURCE_CONSUMER = "ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4"
SOURCE_REGS = (11, 12, 13, 14, 7, 8, 9, 10)


def write(path: Path, data: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text() != data:
            raise SystemExit(f"generated file is stale: {path}")
    else:
        path.write_text(data)


def decode_block(block: int) -> list[str]:
    base = 192 * block
    load = lambda off: f"[rsi + {base + off}]"
    out = [f"  /* Decode and validate PK block {block}. */"]
    out += [f"  vmovdqu ymm{i}, YMMWORD PTR {load(32 * i)}" for i in range(6)]
    out += [
        "  vperm2i128 ymm6, ymm0, ymm3, 0x20",
        "  vperm2i128 ymm7, ymm0, ymm3, 0x31",
        "  vperm2i128 ymm8, ymm1, ymm4, 0x20",
        "  vperm2i128 ymm9, ymm1, ymm4, 0x31",
        "  vperm2i128 ymm10, ymm2, ymm5, 0x20",
        "  vperm2i128 ymm11, ymm2, ymm5, 0x31",
        "  vpunpcklqdq ymm0, ymm6, ymm9",
        "  vpunpckhqdq ymm1, ymm6, ymm9",
        "  vpunpcklqdq ymm2, ymm7, ymm10",
        "  vpunpckhqdq ymm3, ymm7, ymm10",
        "  vpunpcklqdq ymm4, ymm8, ymm11",
        "  vpunpckhqdq ymm5, ymm8, ymm11",
        "  vpsllq ymm8, ymm3, 32",
        "  vpsrlq ymm9, ymm0, 32",
        "  vpsllq ymm10, ymm4, 32",
        "  vpsrlq ymm11, ymm1, 32",
        "  vpsllq ymm12, ymm5, 32",
        "  vpsrlq ymm13, ymm2, 32",
        "  vpblendd ymm8, ymm0, ymm8, 0xaa",
        "  vpblendd ymm9, ymm9, ymm3, 0xaa",
        "  vpblendd ymm10, ymm1, ymm10, 0xaa",
        "  vpblendd ymm11, ymm11, ymm4, 0xaa",
        "  vpblendd ymm12, ymm2, ymm12, 0xaa",
        "  vpblendd ymm13, ymm13, ymm5, 0xaa",
        "  vpsllq ymm0, ymm11, 16",
        "  vpsrlq ymm1, ymm8, 16",
        "  vpsllq ymm2, ymm12, 16",
        "  vpsrlq ymm3, ymm9, 16",
        "  vpsllq ymm4, ymm13, 16",
        "  vpsrlq ymm5, ymm10, 16",
        "  vpblendw ymm0, ymm8, ymm0, 0xaa",
        "  vpblendw ymm1, ymm1, ymm11, 0xaa",
        "  vpblendw ymm2, ymm9, ymm2, 0xaa",
        "  vpblendw ymm3, ymm3, ymm12, 0xaa",
        "  vpblendw ymm4, ymm10, ymm4, 0xaa",
        "  vpblendw ymm5, ymm5, ymm13, 0xaa",
        "  vpand ymm11, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]",
        "  vpand ymm7, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]",
        "  vpsrlw ymm0, ymm0, 12",
        "  vpsrlw ymm3, ymm3, 12",
        "  vpsllw ymm6, ymm1, 4",
        "  vpsllw ymm9, ymm4, 4",
        "  vpxor ymm0, ymm0, ymm6",
        "  vpxor ymm3, ymm3, ymm9",
        "  vpand ymm12, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]",
        "  vpand ymm8, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]",
        "  vpsrlw ymm0, ymm1, 8",
        "  vpsrlw ymm3, ymm4, 8",
        "  vpsllw ymm1, ymm2, 8",
        "  vpsllw ymm4, ymm5, 8",
        "  vpxor ymm0, ymm0, ymm1",
        "  vpxor ymm3, ymm3, ymm4",
        "  vpand ymm13, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]",
        "  vpand ymm9, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]",
        "  vpsrlw ymm0, ymm2, 4",
        "  vpsrlw ymm3, ymm5, 4",
        "  vpand ymm14, ymm0, YMMWORD PTR [rip + .Lhdec_low_mask]",
        "  vpand ymm10, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]",
        "  vpmaxuw ymm0, ymm11, ymm12",
        "  vpmaxuw ymm1, ymm13, ymm14",
        "  vpmaxuw ymm2, ymm7, ymm8",
        "  vpmaxuw ymm3, ymm9, ymm10",
        "  vpmaxuw ymm0, ymm0, ymm1",
        "  vpmaxuw ymm2, ymm2, ymm3",
        "  vpmaxuw ymm0, ymm0, ymm2",
        "  vpcmpgtw ymm0, ymm0, YMMWORD PTR [rip + .Lhdec_qm1]",
        "  vpmovmskb edx, ymm0",
        "  or eax, edx",
    ]
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", type=Path, required=True)
    parser.add_argument("--schedule", type=Path, required=True)
    parser.add_argument("--ma2-source", type=Path, required=True)
    parser.add_argument("--asm", type=Path, required=True)
    parser.add_argument("--header", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    mapping = json.loads(args.map.read_text())
    schedule = json.loads(args.schedule.read_text())
    if mapping["decode_geometry"]["block_local_natural_vectors"] != 72:
        raise SystemExit("Natural-Q decoder block locality changed")
    plans = schedule["resident_h"]["natural_plans"]
    by_block: dict[int, list[tuple[int, dict]]] = {block: [] for block in range(9)}
    masks: dict[tuple[int, ...], str] = {}
    for destination, plan in enumerate(plans):
        blocks = {source // 8 for source in plan["source_vectors"]}
        if len(blocks) != 1:
            raise SystemExit("cross-block Natural-Q vector")
        block = blocks.pop()
        by_block[block].append((destination, plan))
        for group in plan["groups"]:
            key = tuple(group["vpshufb_mask"])
            masks.setdefault(key, f".Lhdec_mask_{len(masks)}")
    if any(len(items) != 8 for items in by_block.values()):
        raise SystemExit("each decoder block must form eight Natural-Q vectors")

    lines = [
        "/* Generated H1 control: direct PK decode to exact Natural-Q h. */",
        ".intel_syntax noprefix", ".text", f".globl {DECODER}",
        f".type {DECODER},@function", ".p2align 5", f"{DECODER}:",
        "  xor eax, eax",
    ]
    for block in range(9):
        lines += decode_block(block)
        for destination, plan in by_block[block]:
            groups = plan["groups"]
            if len(groups) != 2:
                raise SystemExit("H1 control expects two-source projector")
            for temp, group in zip((1, 2), groups):
                source = group["low_source"]["vector"]
                if source // 8 != block:
                    raise SystemExit("projector source block mismatch")
                reg = SOURCE_REGS[source % 8]
                mask = masks[tuple(group["vpshufb_mask"])]
                lines += [
                    f"  vperm2i128 ymm{temp}, ymm{reg}, ymm{reg}, {group['vperm2i128_immediate']}",
                    f"  vpshufb ymm{temp}, ymm{temp}, YMMWORD PTR [rip + {mask}]",
                ]
            lines += ["  vpor ymm0, ymm1, ymm2",
                      f"  vmovdqa YMMWORD PTR [rdi + {32 * destination}], ymm0"]
    lines += ["  test eax, eax", "  setne al", "  movzx eax, al", "  ret",
              f".size {DECODER}, .-{DECODER}"]

    ma2 = args.ma2_source.read_text()
    macro_start = ma2.index(".macro MA1_CENTER")
    function_start = ma2.index(f".globl {SOURCE_CONSUMER}")
    end_marker = f".size {SOURCE_CONSUMER}, .-{SOURCE_CONSUMER}\n"
    function_end = ma2.index(end_marker, function_start) + len(end_marker)
    macros = ma2[macro_start:function_start]
    function = ma2[function_start:function_end]
    pattern = re.compile(
        r"  vmovdqa ymm8, YMMWORD PTR \[rcx \+ \d+\]\n"
        r"  vmovdqa ymm9, YMMWORD PTR \[rcx \+ \d+\]\n"
        r"  vperm2i128 ymm10, ymm8, ymm8, 0x(?:20|31)\n"
        r"  vpshufb ymm([0-3]), ymm10, YMMWORD PTR \[rip \+ \.Lqnat_h_mask_\d+\]\n"
        r"  vperm2i128 ymm10, ymm9, ymm9, 0x(?:20|31)\n"
        r"  vpshufb ymm10, ymm10, YMMWORD PTR \[rip \+ \.Lqnat_h_mask_\d+\]\n"
        r"  vpor ymm\1, ymm\1, ymm10\n")
    count = 0
    def replacement(match: re.Match[str]) -> str:
        nonlocal count
        reg = match.group(1)
        result = f"  vmovdqa ymm{reg}, YMMWORD PTR [rcx + {32 * count}]\n"
        count += 1
        return result
    function = pattern.sub(replacement, function)
    if count != 72:
        raise SystemExit(f"expected 72 h projection replacements, got {count}")
    function = function.replace(SOURCE_CONSUMER, CONSUMER)
    lines += ["", "/* H1 control consumer: h is already exact Natural-Q. */",
              macros.rstrip(), function.rstrip()]
    lines += ["", ".section .rodata,\"a\",@progbits", ".p2align 5",
              ".Lhdec_low_mask:", "  .short " + ",".join(["4095"] * 16),
              ".Lhdec_qm1:", "  .short " + ",".join(["3456"] * 16)]
    for key, name in masks.items():
        lines += [".p2align 5", f"{name}:", "  .byte " + ",".join(map(str, key))]
    lines += ['#include "generated/f0-ma2-constants.inc"',
              '#include "generated/gt9x16-prod3-ma2-qorder-natural-constants.inc"',
              "", ".section .note.GNU-stack,\"\",@progbits", ""]
    asm = "\n".join(lines)

    header = (
        "#ifndef NTRUPLUS1152_EXP001_H_DECODE_NATURAL_Q_ASM_H\n"
        "#define NTRUPLUS1152_EXP001_H_DECODE_NATURAL_Q_ASM_H\n"
        "#include <stdint.h>\n"
        f"int {DECODER}(int16_t out[1152], const uint8_t pk[1728]);\n"
        f"void {CONSUMER}(int16_t out[1152], const int16_t r[1152], "
        "const int16_t m[1152], const int16_t h_natural[1152]);\n"
        "#endif\n")
    contract = {
        "schema": "encap-h-decode-natural-q-asm/v1",
        "checkpoint": "ENCAP-H-DECODE-NATURAL-Q-ASM-H1",
        "role": "conservative H1 control, not the target ingress architecture",
        "symbols": {"decoder": DECODER, "consumer": CONSUMER},
        "decoder": {"blocks": 9, "pk_loads": 54, "natural_stores": 72,
                    "formation_routes": 360, "scratch_bytes": 0,
                    "accepted_set": "all 1152 decoded 12-bit values are <3457"},
        "consumer": {"h_loads": 72, "removed_h_projection_loads": 72,
                     "removed_h_projection_routes": 360,
                     "arithmetic": "identical Natural-Q scale-4 MA2"},
        "boundary": {"bytes": 2304, "raw_exact_natural_q": True,
                     "scale": 1, "montgomery_exponent": 0},
        "benchmark_authorized": False,
    }
    write(args.asm, asm, args.check)
    write(args.header, header, args.check)
    write(args.contract, json.dumps(contract, indent=2, sort_keys=True) + "\n", args.check)
    print("H1 Natural-Q decoder: 9 block-local decodes, 72 exact stores; preprojected MA2 generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
