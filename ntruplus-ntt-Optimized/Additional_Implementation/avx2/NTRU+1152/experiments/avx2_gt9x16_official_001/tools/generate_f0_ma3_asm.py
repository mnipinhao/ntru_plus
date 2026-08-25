#!/usr/bin/env python3
"""Generate one-tile and caller-shaped streaming MA3 AVX2 assembly."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import generate_f0_ma1_asm1 as ma1

Q, QINV, R = ma1.Q, ma1.QINV, ma1.R


def write(path: Path, value: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text() != value:
            raise SystemExit(f"generated file is stale: {path}")
    else:
        path.write_text(value)


def tile_base(tile: dict) -> int:
    return 2 * min(position for plane in tile["planes"]
                   for position in plane["f0_positions_i16"])


def ma3_macros() -> str:
    return r'''
.macro MA3_QM1 h0,h1,r0,r1,lambda,lambda_qinv
  vmovdqa ymm0, YMMWORD PTR [r8 + \h0]
  vmovdqa ymm1, YMMWORD PTR [r8 + \h1]
  vmovdqa ymm2, YMMWORD PTR [r8 + \r0]
  vmovdqa ymm3, YMMWORD PTR [r8 + \r1]
  MA1_MONT_REG 4,0,2,6
  MA1_MONT_REG 5,1,3,7
  vpaddw ymm0, ymm0, ymm1
  vpaddw ymm2, ymm2, ymm3
  MA1_CENTER 0,6
  MA1_CENTER 2,7
  MA1_MONT_REG 8,0,2,6
  vpsubw ymm9, ymm8, ymm4
  vpsubw ymm9, ymm9, ymm5
  MA1_CENTER 9,6
  MA1_MONT_CONST 8,5,\lambda,\lambda_qinv,6
  vpaddw ymm4, ymm4, ymm8
  MA1_CENTER 4,6
  /* first in ymm4, second in ymm9 */
.endm

.macro MA3_QM2 ah0,bh0,ah1,bh1,ar0,br0,ar1,br1,alambda,alambda_qinv,blambda,blambda_qinv
  vmovdqa ymm0, YMMWORD PTR [r8 + \ah0]
  vmovdqa ymm1, YMMWORD PTR [r8 + \bh0]
  vmovdqa ymm2, YMMWORD PTR [r8 + \ah1]
  vmovdqa ymm3, YMMWORD PTR [r8 + \bh1]
  vmovdqa ymm4, YMMWORD PTR [r8 + \ar0]
  vmovdqa ymm5, YMMWORD PTR [r8 + \br0]
  vmovdqa ymm6, YMMWORD PTR [r8 + \ar1]
  vmovdqa ymm7, YMMWORD PTR [r8 + \br1]
  MA1_MONT_REG2 8,9,0,1,4,5,12,13
  MA1_MONT_REG2 10,11,2,3,6,7,12,13
  vpaddw ymm0, ymm0, ymm2
  vpaddw ymm1, ymm1, ymm3
  vpaddw ymm4, ymm4, ymm6
  vpaddw ymm5, ymm5, ymm7
  MA1_CENTER2 0,1,12,13
  MA1_CENTER2 4,5,12,13
  MA1_MONT_REG2 14,15,0,1,4,5,12,13
  vpsubw ymm14, ymm14, ymm8
  vpsubw ymm15, ymm15, ymm9
  vpsubw ymm14, ymm14, ymm10
  vpsubw ymm15, ymm15, ymm11
  MA1_CENTER2 14,15,12,13
  MA1_MONT_CONST 12,10,\alambda,\alambda_qinv,2
  MA1_MONT_CONST 13,11,\blambda,\blambda_qinv,3
  vpaddw ymm8, ymm8, ymm12
  vpaddw ymm9, ymm9, ymm13
  MA1_CENTER2 8,9,12,13
  /* first A/B in ymm8/9, second A/B in ymm14/15 */
.endm
'''


def emit_h_pair(tile_a: dict, tile_b: dict, h_specs: dict,
                labels: dict) -> list[str]:
    out = []
    for coefficient in range(4):
        for tile, reg, temp in ((tile_a, 0, 8), (tile_b, 1, 9)):
            spec = h_specs[(ma1.label_tile(tile), coefficient)]
            out.append(
                f"  MA1_PROJECT_H {reg},{temp},{spec.source_offsets_bytes[0]},"
                f"{spec.source_offsets_bytes[1]},0x{spec.permute_imm:02x},"
                f"{labels[spec.shuffle]},0x{spec.blend_imm:02x}")
        out += ["  MA1_CENTER2 0,1,12,13",
                "  MA1_MONT_CONST2 0,1,0,1,.Lma1_r2,.Lma1_r2_qinv,12,13",
                f"  vmovdqa YMMWORD PTR [r8 + {256 + 32 * coefficient}], ymm0",
                f"  vmovdqa YMMWORD PTR [r8 + {384 + 32 * coefficient}], ymm1"]
    return out


def emit_h_one(tile: dict, h_specs: dict, labels: dict) -> list[str]:
    out = []
    for coefficient in range(4):
        spec = h_specs[(ma1.label_tile(tile), coefficient)]
        out += [
            f"  MA1_PROJECT_H 0,8,{spec.source_offsets_bytes[0]},"
            f"{spec.source_offsets_bytes[1]},0x{spec.permute_imm:02x},"
            f"{labels[spec.shuffle]},0x{spec.blend_imm:02x}",
            "  MA1_CENTER 0,12",
            "  MA1_MONT_CONST 0,0,.Lma1_r2,.Lma1_r2_qinv,12",
            f"  vmovdqa YMMWORD PTR [r8 + {256 + 32 * coefficient}], ymm0",
        ]
    return out


def emit_f0_pair(pointer: str, tile_a: dict, tile_b: dict,
                 destination_a: int, destination_b: int) -> list[str]:
    out = []
    bases = (tile_base(tile_a), tile_base(tile_b))
    for coefficient in range(4):
        source_pair = 0 if coefficient < 2 else 64
        immediate = 0x20 if coefficient % 2 == 0 else 0x31
        out += [
            f"  vmovdqa ymm0, YMMWORD PTR [{pointer} + {bases[0] + source_pair}]",
            f"  vmovdqa ymm2, YMMWORD PTR [{pointer} + {bases[0] + source_pair + 32}]",
            f"  vperm2i128 ymm0, ymm0, ymm2, 0x{immediate:02x}",
            f"  vmovdqa ymm1, YMMWORD PTR [{pointer} + {bases[1] + source_pair}]",
            f"  vmovdqa ymm3, YMMWORD PTR [{pointer} + {bases[1] + source_pair + 32}]",
            f"  vperm2i128 ymm1, ymm1, ymm3, 0x{immediate:02x}",
            "  MA1_CENTER2 0,1,12,13",
            f"  vmovdqa YMMWORD PTR [r8 + {destination_a + 32 * coefficient}], ymm0",
            f"  vmovdqa YMMWORD PTR [r8 + {destination_b + 32 * coefficient}], ymm1",
        ]
    return out


def emit_f0_one(pointer: str, destination: int) -> list[str]:
    out = []
    for coefficient in range(4):
        source_pair = 0 if coefficient < 2 else 64
        immediate = 0x20 if coefficient % 2 == 0 else 0x31
        out += [
            f"  vmovdqa ymm0, YMMWORD PTR [{pointer} + {source_pair}]",
            f"  vmovdqa ymm2, YMMWORD PTR [{pointer} + {source_pair + 32}]",
            f"  vperm2i128 ymm0, ymm0, ymm2, 0x{immediate:02x}",
            "  MA1_CENTER 0,12",
            f"  vmovdqa YMMWORD PTR [r8 + {destination + 32 * coefficient}], ymm0",
        ]
    return out


def emit_tt_inputs() -> list[str]:
    out = []
    # A/B h sums, then A/B r sums.
    for source_a, source_b, destination_a, destination_b in (
            (256, 384, 1024, 1152), (512, 640, 1088, 1216)):
        for pair in range(2):
            c0, c1 = 2 * pair, 2 * pair + 1
            out += [
                f"  vmovdqa ymm0, YMMWORD PTR [r8 + {source_a + 32 * c0}]",
                f"  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + {source_a + 32 * c1}]",
                f"  vmovdqa ymm1, YMMWORD PTR [r8 + {source_b + 32 * c0}]",
                f"  vpaddw ymm1, ymm1, YMMWORD PTR [r8 + {source_b + 32 * c1}]",
                "  MA1_CENTER2 0,1,12,13",
                f"  vmovdqa YMMWORD PTR [r8 + {destination_a + 32 * pair}], ymm0",
                f"  vmovdqa YMMWORD PTR [r8 + {destination_b + 32 * pair}], ymm1",
            ]
    return out


def emit_tt_inputs_one() -> list[str]:
    out = []
    for source, destination in ((256, 1024), (512, 1088)):
        for pair in range(2):
            c0, c1 = 2 * pair, 2 * pair + 1
            out += [
                f"  vmovdqa ymm0, YMMWORD PTR [r8 + {source + 32 * c0}]",
                f"  vpaddw ymm0, ymm0, YMMWORD PTR [r8 + {source + 32 * c1}]",
                "  MA1_CENTER 0,12",
                f"  vmovdqa YMMWORD PTR [r8 + {destination + 32 * pair}], ymm0",
            ]
    return out


def add_pair(reg_a: int, reg_b: int, offset_a: int, offset_b: int) -> list[str]:
    return [f"  vpaddw ymm{reg_a}, ymm{reg_a}, YMMWORD PTR [r8 + {offset_a}]",
            f"  vpaddw ymm{reg_b}, ymm{reg_b}, YMMWORD PTR [r8 + {offset_b}]",
            f"  vmovdqa YMMWORD PTR [r8 + {offset_a}], ymm{reg_a}",
            f"  vmovdqa YMMWORD PTR [r8 + {offset_b}], ymm{reg_b}"]


def emit_core_pair(tile_a: dict, tile_b: dict,
                   final_center: bool = True) -> list[str]:
    a, b = ma1.label_tile(tile_a), ma1.label_tile(tile_b)
    q = lambda h0, h1, r0, r1: (
        f"  MA3_QM2 {256+32*h0},{384+32*h0},{256+32*h1},{384+32*h1},"
        f"{512+32*r0},{640+32*r0},{512+32*r1},{640+32*r1},"
        f".Llambda_{a},.Llambda_{a}_qinv,.Llambda_{b},.Llambda_{b}_qinv")
    out = [q(0, 2, 0, 2)]
    out += ["  vmovdqa YMMWORD PTR [r8 + 768], ymm8",
            "  vmovdqa YMMWORD PTR [r8 + 896], ymm9",
            "  vmovdqa YMMWORD PTR [r8 + 800], ymm14",
            "  vmovdqa YMMWORD PTR [r8 + 928], ymm15"]
    out += add_pair(8, 9, 0, 128) + add_pair(14, 15, 64, 192)
    out.append(q(1, 3, 1, 3))
    out += ["  vmovdqa YMMWORD PTR [r8 + 832], ymm8",
            "  vmovdqa YMMWORD PTR [r8 + 960], ymm9",
            "  vmovdqa YMMWORD PTR [r8 + 864], ymm14",
            "  vmovdqa YMMWORD PTR [r8 + 992], ymm15"]
    out += add_pair(8, 9, 64, 192)
    out += [f"  MA1_MONT_CONST 10,14,.Llambda_{a},.Llambda_{a}_qinv,12",
            f"  MA1_MONT_CONST 11,15,.Llambda_{b},.Llambda_{b}_qinv,13"]
    out += add_pair(10, 11, 0, 128)
    out.append(
        f"  MA3_QM2 1024,1152,1056,1184,1088,1216,1120,1248,"
        f".Llambda_{a},.Llambda_{a}_qinv,.Llambda_{b},.Llambda_{b}_qinv")
    # cross0 = TT0 - EE0 - OO0; cross1 likewise.
    out += ["  vpsubw ymm8, ymm8, YMMWORD PTR [r8 + 768]",
            "  vpsubw ymm9, ymm9, YMMWORD PTR [r8 + 896]",
            "  vpsubw ymm8, ymm8, YMMWORD PTR [r8 + 832]",
            "  vpsubw ymm9, ymm9, YMMWORD PTR [r8 + 960]",
            "  vpsubw ymm14, ymm14, YMMWORD PTR [r8 + 800]",
            "  vpsubw ymm15, ymm15, YMMWORD PTR [r8 + 928]",
            "  vpsubw ymm14, ymm14, YMMWORD PTR [r8 + 864]",
            "  vpsubw ymm15, ymm15, YMMWORD PTR [r8 + 992]",
            "  MA1_CENTER2 8,9,12,13", "  MA1_CENTER2 14,15,12,13"]
    out += add_pair(8, 9, 32, 160) + add_pair(14, 15, 96, 224)
    # Common S0 finalizer.
    for coefficient in range(4):
        out += [f"  vmovdqa ymm0, YMMWORD PTR [r8 + {32*coefficient}]",
                f"  vmovdqa ymm1, YMMWORD PTR [r8 + {128+32*coefficient}]",
                "  MA1_MONT_CONST2 0,1,0,1,.Lma1_inv4,.Lma1_inv4_qinv,12,13"]
        if final_center:
            out.append("  MA1_CENTER2 0,1,12,13")
        out += [
                f"  vmovdqa YMMWORD PTR [r8 + {32*coefficient}], ymm0",
                f"  vmovdqa YMMWORD PTR [r8 + {128+32*coefficient}], ymm1"]
    return out


def emit_core_one(tile: dict) -> list[str]:
    name = ma1.label_tile(tile)
    q = lambda h0, h1, r0, r1: (
        f"  MA3_QM1 {256+32*h0},{256+32*h1},{512+32*r0},{512+32*r1},"
        f".Llambda_{name},.Llambda_{name}_qinv")
    out = [q(0, 2, 0, 2)]
    out += [
        "  vmovdqa YMMWORD PTR [r8 + 768], ymm4",
        "  vmovdqa YMMWORD PTR [r8 + 800], ymm9",
        "  vpaddw ymm4, ymm4, YMMWORD PTR [r8 + 0]",
        "  vmovdqa YMMWORD PTR [r8 + 0], ymm4",
        "  vpaddw ymm9, ymm9, YMMWORD PTR [r8 + 64]",
        "  vmovdqa YMMWORD PTR [r8 + 64], ymm9",
        q(1, 3, 1, 3),
        "  vmovdqa YMMWORD PTR [r8 + 832], ymm4",
        "  vmovdqa YMMWORD PTR [r8 + 864], ymm9",
        "  vpaddw ymm4, ymm4, YMMWORD PTR [r8 + 64]",
        "  vmovdqa YMMWORD PTR [r8 + 64], ymm4",
        f"  MA1_MONT_CONST 10,9,.Llambda_{name},.Llambda_{name}_qinv,12",
        "  vpaddw ymm10, ymm10, YMMWORD PTR [r8 + 0]",
        "  vmovdqa YMMWORD PTR [r8 + 0], ymm10",
        q(0, 1, 0, 1).replace("256,288,512,544", "1024,1056,1088,1120"),
        "  vpsubw ymm4, ymm4, YMMWORD PTR [r8 + 768]",
        "  vpsubw ymm4, ymm4, YMMWORD PTR [r8 + 832]",
        "  vpsubw ymm9, ymm9, YMMWORD PTR [r8 + 800]",
        "  vpsubw ymm9, ymm9, YMMWORD PTR [r8 + 864]",
        "  MA1_CENTER 4,12",
        "  MA1_CENTER 9,12",
        "  vpaddw ymm4, ymm4, YMMWORD PTR [r8 + 32]",
        "  vmovdqa YMMWORD PTR [r8 + 32], ymm4",
        "  vpaddw ymm9, ymm9, YMMWORD PTR [r8 + 96]",
        "  vmovdqa YMMWORD PTR [r8 + 96], ymm9",
    ]
    for coefficient in range(4):
        out += [
            f"  vmovdqa ymm0, YMMWORD PTR [r8 + {32*coefficient}]",
            "  MA1_MONT_CONST 0,0,.Lma1_inv4,.Lma1_inv4_qinv,12",
            "  MA1_CENTER 0,12",
            f"  vmovdqa YMMWORD PTR [r8 + {32*coefficient}], ymm0",
        ]
    return out


def emit_asm0(tile: dict, h_specs: dict, labels: dict) -> list[str]:
    out = ["  /* Exact B0/P0 single-tile EE -> OO -> TT streaming DAG. */"]
    out += emit_h_one(tile, h_specs, labels)
    out += emit_f0_one("rsi", 512)
    out += emit_f0_one("rdx", 0)
    out += emit_tt_inputs_one() + emit_core_one(tile)
    for coefficient in range(4):
        out += [f"  vmovdqa ymm0, YMMWORD PTR [r8 + {32*coefficient}]",
                f"  vmovdqa YMMWORD PTR [rdi + {32*coefficient}], ymm0"]
    out.append("  ret")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schedule", type=Path, required=True)
    parser.add_argument("--asm", type=Path, required=True)
    parser.add_argument("--constants", type=Path, required=True)
    parser.add_argument("--header", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    schedule = json.loads(args.schedule.read_text())
    tiles_by_key = {(t["tile"]["branch"], t["tile"]["p"]): t
                    for t in schedule["semantic_tiles"]}
    chunks = [[tiles_by_key[(x["branch"], x["p"])]
               for x in chunk["semantic_tiles"]]
              for chunk in schedule["official_chunk_pairing"]]
    h_specs, output_specs, masks = {}, {}, {}
    def label(mask):
        if mask not in masks:
            masks[mask] = f".Lma3_mask_{len(masks)}"
        return masks[mask]
    for tile in schedule["semantic_tiles"]:
        for coefficient in range(4):
            spec = ma1.h_projection(tile, coefficient)
            h_specs[(ma1.label_tile(tile), coefficient)] = spec
            label(spec.shuffle)
    for chunk, tiles in enumerate(chunks):
        for coefficient in range(4):
            for group in range(2):
                spec = ma1.output_route(tiles, chunk, coefficient,
                                        8 * chunk + 4 * group + coefficient)
                output_specs[(chunk, coefficient, group)] = spec
                label(spec.masks[0]); label(spec.masks[1])

    constants = "/* Generated F0-MA3 constants. */\n.p2align 5\n"
    for name, value in ((".Lma1_q", Q), (".Lma1_qinv", QINV),
                        (".Lma1_barrett", 9), (".Lma1_pack_barrett", 9),
                        (".Lma1_half_q", 1728), (".Lma1_negative_half_q", -1728),
                        (".Lma1_r2", 867), (".Lma1_r2_qinv", 2787)):
        constants += ma1.vec16(name, [value] * 16)
    inv4_r = ma1.centered(pow(4, -1, Q) * R)
    constants += ma1.vec16(".Lma1_inv4", [inv4_r] * 16)
    constants += ma1.vec16(".Lma1_inv4_qinv", [ma1.signed16(inv4_r*QINV)] * 16)
    constants += ma1.vec16(".Lma1_low_half", [-1] * 8 + [0] * 8)
    for tile in schedule["semantic_tiles"]:
        name = ma1.label_tile(tile)
        factors = [ma1.centered(x * R) for x in tile["planes"][0]["lambda_mod_q"]]
        constants += ma1.vec16(f".Llambda_{name}", factors)
        constants += ma1.vec16(f".Llambda_{name}_qinv",
                               [ma1.signed16(x * QINV) for x in factors])
    for mask, name in masks.items():
        constants += ma1.bytes32(name, list(mask))

    asm = ".intel_syntax noprefix\n.text\n" + ma1.emit_common_macros() + ma3_macros()
    asm0 = "ntruplus1152_exp001_f0_ma3_asm0_b0p0"
    asm += f"\n.globl {asm0}\n.type {asm0},@function\n.p2align 5\n{asm0}:\n"
    asm += "\n".join(emit_asm0(tiles_by_key[(0, 0)], h_specs, masks))
    asm += f"\n.size {asm0}, .-{asm0}\n"
    asm1 = "ntruplus1152_exp001_f0_ma3_asm1_c1"
    asm += f"\n.globl {asm1}\n.type {asm1},@function\n.p2align 5\n{asm1}:\n"
    for chunk, tiles in enumerate(chunks):
        asm += f"  /* MA3 two-tile chunk {chunk}. */\n"
        asm += "\n".join(emit_h_pair(tiles[0], tiles[1], h_specs, masks)) + "\n"
        asm += "\n".join(emit_f0_pair("rsi", tiles[0], tiles[1], 512, 640)) + "\n"
        asm += "\n".join(emit_f0_pair("rdx", tiles[0], tiles[1], 0, 128)) + "\n"
        asm += "\n".join(emit_tt_inputs()) + "\n"
        asm += "\n".join(emit_core_pair(tiles[0], tiles[1],
                                         final_center=False)) + "\n"
        asm += "\n".join(ma1.emit_output_routes(chunk, tiles, output_specs, masks)) + "\n"
        asm += f"  MA1_PACK_CHUNK {192*chunk}\n"
    asm += f"  ret\n.size {asm1}, .-{asm1}\n"
    asm += '\n.section .rodata\n#include "generated/f0-ma3-constants.inc"\n'
    asm += '\n.section .note.GNU-stack,"",@progbits\n'
    header = """#ifndef NTRUPLUS1152_EXP001_F0_MA3_ASM_H
#define NTRUPLUS1152_EXP001_F0_MA3_ASM_H
#include <stdint.h>
void ntruplus1152_exp001_f0_ma3_asm0_b0p0(
    int16_t out[64], const int16_t r[64], const int16_t m[64],
    const int16_t h[1152], int16_t scratch[640]);
void ntruplus1152_exp001_f0_ma3_asm1_c1(
    uint8_t out[1728], const int16_t r[1152], const int16_t m[1152],
    const int16_t h[1152], int16_t scratch[640]);
#endif
"""
    contract = {
        "schema": "gt-f0-ma3-asm/v1", "checkpoint": "F0-MA3-ASM0/ASM1",
        "dag": ["EE", "OO", "TT", "CROSS", "inv4", "serializer"],
        "ledger": {"core_per_tile": 13, "h_lift_per_tile": 4,
                   "inv4_per_tile": 4, "total_per_tile": 21,
                   "full_total": 378},
        "asm0": {"scope": "exact B0/P0 single-tile proof kernel",
                 "montgomery_chains": 21, "scratch_i16": 640},
        "asm1": {"tiles": 18, "chunks": 9, "scratch_i16": 640,
                 "two_tile_ilp": True, "intermediate_canonical_abi": False,
                 "post_inv4_center": False,
                 "final_range_proof": "generated/f0-ma3-final-range.json",
                 "peak_ymm": 16, "spills_allowed": False},
        "range_source": "generated/f0-ma-schedule.json",
        "alignment": {"entries": 32, "constants": 32,
                      "inputs_and_scratch": 32, "ciphertext": "unaligned"},
        "schedule_sha256": hashlib.sha256(args.schedule.read_bytes()).hexdigest(),
    }
    write(args.asm, asm, args.check); write(args.constants, constants, args.check)
    write(args.header, header, args.check)
    write(args.contract, json.dumps(contract, indent=2, sort_keys=True) + "\n",
          args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
