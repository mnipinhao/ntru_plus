#!/usr/bin/env python3
"""Lower the frozen H1 direct-hash schedule to straight-line AVX2."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


SYMBOL = "ntruplus1152_exp001_prod3_ma2_hash_h1"
Q = 3457
INV4 = -901
INV4_QINV = 16379


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, data: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text() != data:
            raise SystemExit(f"generated file is stale: {path}")
    else:
        path.write_text(data)


def write_json(path: Path, data: dict, check: bool) -> None:
    write(path, json.dumps(data, indent=2, sort_keys=True) + "\n", check)


def mask_label(index: int) -> str:
    return f".Lprod3_hash_h1_mask_{index}"


PACK = """\
  vpsllw ymm10, ymm1, 12
  vpsllw ymm11, ymm5, 12
  vpxor ymm0, ymm0, ymm10
  vpxor ymm4, ymm4, ymm11
  vpsllw ymm10, ymm2, 8
  vpsllw ymm11, ymm6, 8
  vpsrlw ymm12, ymm1, 4
  vpsrlw ymm13, ymm5, 4
  vpxor ymm1, ymm12, ymm10
  vpxor ymm5, ymm13, ymm11
  vpsllw ymm10, ymm3, 4
  vpsllw ymm11, ymm7, 4
  vpsrlw ymm12, ymm2, 8
  vpsrlw ymm13, ymm6, 8
  vpxor ymm2, ymm12, ymm10
  vpxor ymm6, ymm13, ymm11
  vpslld ymm7, ymm1, 16
  vpslld ymm8, ymm4, 16
  vpslld ymm9, ymm6, 16
  vpblendw ymm7, ymm0, ymm7, 0xaa
  vpblendw ymm8, ymm2, ymm8, 0xaa
  vpblendw ymm9, ymm5, ymm9, 0xaa
  vpsrlq ymm10, ymm0, 16
  vpsrlq ymm11, ymm2, 16
  vpsrlq ymm12, ymm5, 16
  vpblendw ymm10, ymm10, ymm1, 0xaa
  vpblendw ymm11, ymm11, ymm4, 0xaa
  vpblendw ymm12, ymm12, ymm6, 0xaa
  vpsllq ymm0, ymm8, 32
  vpsllq ymm1, ymm10, 32
  vpsllq ymm2, ymm12, 32
  vpblendd ymm0, ymm7, ymm0, 0xaa
  vpblendd ymm1, ymm9, ymm1, 0xaa
  vpblendd ymm2, ymm11, ymm2, 0xaa
  vpsrlq ymm3, ymm7, 32
  vpsrlq ymm4, ymm9, 32
  vpsrlq ymm5, ymm11, 32
  vpblendd ymm3, ymm3, ymm8, 0xaa
  vpblendd ymm4, ymm4, ymm10, 0xaa
  vpblendd ymm5, ymm5, ymm12, 0xaa
  vpunpcklqdq ymm6, ymm0, ymm1
  vpunpcklqdq ymm7, ymm2, ymm3
  vpunpcklqdq ymm8, ymm4, ymm5
  vpunpckhqdq ymm9, ymm0, ymm1
  vpunpckhqdq ymm10, ymm2, ymm3
  vpunpckhqdq ymm11, ymm4, ymm5
  vperm2i128 ymm0, ymm6, ymm7, 0x20
  vperm2i128 ymm1, ymm8, ymm9, 0x20
  vperm2i128 ymm2, ymm10, ymm11, 0x20
  vperm2i128 ymm3, ymm6, ymm7, 0x31
  vperm2i128 ymm4, ymm8, ymm9, 0x31
  vperm2i128 ymm5, ymm10, ymm11, 0x31
"""


def emit_store(offset: int) -> list[str]:
    return [f"  vmovdqu YMMWORD PTR [rdi + {offset + 32 * i}], ymm{i}"
            for i in range(6)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schedule", type=Path, required=True)
    parser.add_argument("--direct-map", type=Path, required=True)
    parser.add_argument("--asm", type=Path, required=True)
    parser.add_argument("--constants", type=Path, required=True)
    parser.add_argument("--header", type=Path, required=True)
    parser.add_argument("--map-header", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    schedule = json.loads(args.schedule.read_text())
    direct = json.loads(args.direct_map.read_text())
    if schedule["schema"] != "gt9x16-prod3-ma2-hash-direct-schedule/v1":
        raise SystemExit("wrong schedule schema")
    if direct["schema"] != "gt9x16-prod3-ma2-hash-direct-map/v1":
        raise SystemExit("wrong direct-map schema")
    if not schedule["decision"]["H1_asm0_authorized"]:
        raise SystemExit("H1 ASM0 is not authorized")
    ledger = schedule["H1"]["ledger"]
    if ledger["peak_ymm"] != 16 or not schedule["H1"]["spill_free_register_plan"]:
        raise SystemExit("frozen spill-free H1 register plan changed")

    masks: list[tuple[int, ...]] = []
    mask_ids: dict[tuple[int, ...], int] = {}
    for block in schedule["H1"]["blocks"]:
        for construction in block["construction"]:
            for group in construction["groups"]:
                mask = tuple(group["vpshufb_mask"])
                if mask not in mask_ids:
                    mask_ids[mask] = len(masks)
                    masks.append(mask)

    lines = [
        "/* Generated H1 ASM0: materialized scale-4 MA2 planes -> exact hash bytes. */",
        ".intel_syntax noprefix",
        ".text",
        f".globl {SYMBOL}",
        f".type {SYMBOL},@function",
        ".p2align 5",
        f"{SYMBOL}:",
    ]
    for block in schedule["H1"]["blocks"]:
        lines.append(f"  /* H1 block {block['block']}: exact Official vectors. */")
        for construction in block["construction"]:
            destination = int(construction["destination_register"][3:])
            for group_index, group in enumerate(construction["groups"]):
                low = group["low_source"]
                high = group["high_source"]
                lines += [
                    f"  vmovdqu ymm8, YMMWORD PTR [rsi + {32 * low['vector']}]",
                    f"  vmovdqu ymm9, YMMWORD PTR [rsi + {32 * high['vector']}]",
                    f"  vperm2i128 ymm10, ymm8, ymm9, {group['vperm2i128_immediate']}",
                ]
                label = mask_label(mask_ids[tuple(group["vpshufb_mask"])])
                if group_index == 0:
                    lines.append(
                        f"  vpshufb ymm{destination}, ymm10, YMMWORD PTR [rip + {label}]")
                else:
                    lines += [
                        f"  vpshufb ymm10, ymm10, YMMWORD PTR [rip + {label}]",
                        f"  vpor ymm{destination}, ymm{destination}, ymm10",
                    ]
        lines += [
            "  vmovdqa ymm13, YMMWORD PTR [rip + .Lprod3_hash_h1_qinv]",
            "  vmovdqa ymm14, YMMWORD PTR [rip + .Lprod3_hash_h1_inv4]",
            "  vmovdqa ymm15, YMMWORD PTR [rip + .Lprod3_hash_h1_q]",
        ]
        for register in range(8):
            lines += [
                f"  vpmullw ymm11, ymm{register}, ymm13",
                f"  vpmulhw ymm{register}, ymm{register}, ymm14",
                "  vpmulhw ymm11, ymm11, ymm15",
                f"  vpsubw ymm{register}, ymm{register}, ymm11",
                f"  vpsraw ymm11, ymm{register}, 15",
                "  vpand ymm11, ymm11, ymm15",
                f"  vpaddw ymm{register}, ymm{register}, ymm11",
            ]
        lines.extend(PACK.rstrip().splitlines())
        lines.extend(emit_store(block["output_byte_offset"]))
    lines += ["  ret", f".size {SYMBOL}, .-{SYMBOL}", ""]
    lines += [
        '.section .rodata,"a",@progbits',
        ".p2align 5",
        ".Lprod3_hash_h1_qinv:",
        "  .short " + ", ".join([str(INV4_QINV)] * 16),
        ".p2align 5",
        ".Lprod3_hash_h1_inv4:",
        "  .short " + ", ".join([str(INV4)] * 16),
        ".p2align 5",
        ".Lprod3_hash_h1_q:",
        "  .short " + ", ".join([str(Q)] * 16),
    ]
    constants = []
    for index, mask in enumerate(masks):
        lines += [".p2align 5", f"{mask_label(index)}:",
                  "  .byte " + ", ".join(map(str, mask))]
        constants.append({"label": mask_label(index), "bytes": list(mask)})
    lines += ["", '.section .note.GNU-stack,"",@progbits', ""]
    asm = "\n".join(lines)

    constant_document = {
        "schema": "gt9x16-prod3-ma2-hash-h1-constants/v1",
        "alignment_bytes": 32,
        "vectors": {"q": Q, "inv4": INV4, "inv4_qinv": INV4_QINV},
        "shuffle_masks": constants,
    }
    header = f"""\
#ifndef NTRUPLUS1152_EXP001_PROD3_MA2_HASH_H1_H
#define NTRUPLUS1152_EXP001_PROD3_MA2_HASH_H1_H

#include <stdint.h>

void {SYMBOL}(uint8_t output[1728], const int16_t input_planes[1152]);

#endif
"""
    source_for_official = [None] * 1152
    for cell in direct["coefficient_map"]:
        source_for_official[cell["official_coefficient"]] = (
            16 * cell["ma2"]["vector"] + cell["ma2"]["lane"])
    if any(value is None for value in source_for_official):
        raise SystemExit("direct map cannot produce scalar oracle table")
    contributions: list[tuple[int, int, int, int, int]] = []
    contribution_offsets = [0]
    by_official = {cell["official_coefficient"]: cell
                   for cell in direct["coefficient_map"]}
    for official in range(1152):
        for item in by_official[official]["serializer"]["byte_contributions"]:
            coefficient_low, coefficient_high = item["coefficient_bits"]
            byte_low, byte_high = item["byte_bits"]
            width = coefficient_high - coefficient_low + 1
            if width != byte_high - byte_low + 1:
                raise SystemExit("serializer bit-width mismatch")
            contributions.append((item["byte_index"], coefficient_low,
                                  byte_low, width, official))
        contribution_offsets.append(len(contributions))
    if len(contributions) != 2304:
        raise SystemExit("serializer contribution count changed")
    map_header = """\
#ifndef NTRUPLUS1152_EXP001_PROD3_MA2_HASH_H1_MAP_H
#define NTRUPLUS1152_EXP001_PROD3_MA2_HASH_H1_MAP_H

#include <stdint.h>

typedef struct {
  uint16_t byte_index;
  uint8_t coefficient_low_bit;
  uint8_t byte_low_bit;
  uint8_t width;
} ntruplus1152_exp001_h1_contribution;

static const uint16_t ntruplus1152_exp001_h1_source_for_official[1152] = {
""" + "\n".join(
        "  " + ", ".join(str(x) for x in source_for_official[i:i + 16]) + ","
        for i in range(0, 1152, 16)) + "\n};\n\n" + \
        "static const uint16_t ntruplus1152_exp001_h1_contribution_offset[1153] = {\n" + \
        "\n".join("  " + ", ".join(str(x) for x in contribution_offsets[i:i + 16]) + ","
                  for i in range(0, 1153, 16)) + "\n};\n\n" + \
        "static const ntruplus1152_exp001_h1_contribution " \
        "ntruplus1152_exp001_h1_contribution_table[2304] = {\n" + \
        "\n".join(f"  {{{byte}, {coefficient_low}, {byte_low}, {width}}},"
                  for byte, coefficient_low, byte_low, width, _ in contributions) + \
        "\n};\n\n#endif\n"
    contract = {
        "schema": "gt9x16-prod3-ma2-hash-h1-asm/v1",
        "symbol": SYMBOL,
        "input": {"bytes": 2304, "alignment": 2,
                  "range": [-20751, 20753], "immutable": True,
                  "may_overlap_output": False,
                  "representation": "materialized scale-4 MA2 coefficient planes"},
        "output": {"bytes": 1728, "alignment": 1,
                   "representation": "exact pinned-Official poly_tobytes bytes"},
        "arithmetic": {"inv4_montgomery": [INV4, INV4_QINV], "q": Q,
                       "post_inv4": [-1998, 1998], "canonical": [0, 3456],
                       "barrett": False},
        "scheduled_ledger": ledger,
        "lowering": {"straight_line": True, "entry_alignment": 32,
                     "constant_alignment": 32, "pointer_loads_unaligned": True,
                     "stack_bytes": 0, "vector_spills": 0,
                     "intermediate_polynomial_bytes": 0,
                     "distinct_shuffle_masks": len(masks)},
        "source_sha256": {"schedule": sha256(args.schedule),
                          "direct_map": sha256(args.direct_map)},
        "authorization": {"H1_ASM0": True, "H2": False,
                          "benchmark": False, "KEM": False},
    }
    write(args.asm, asm, args.check)
    write_json(args.constants, constant_document, args.check)
    write(args.header, header, args.check)
    write(args.map_header, map_header, args.check)
    write_json(args.contract, contract, args.check)
    print(f"H1 ASM0: {len(masks)} masks; full 2304 -> 1728 lowering emitted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
