#!/usr/bin/env python3
"""Generate streaming coefficient-plane MA2 ASM0 and direct-pack CHUNK0."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import generate_f0_ma1_asm1 as ma1

Q, QINV, R = ma1.Q, ma1.QINV, ma1.R
TERMS = (
    (((0, 0),), ((1, 3), (2, 2), (3, 1))),
    (((0, 1), (1, 0)), ((2, 3), (3, 2))),
    (((0, 2), (1, 1), (2, 0)), ((3, 3),)),
    (((0, 3), (1, 2), (2, 1), (3, 0)), ()),
)


def write(path: Path, value: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text() != value:
            raise SystemExit(f"generated file is stale: {path}")
    else:
        path.write_text(value)


def tile_base(tile: dict) -> int:
    return 2 * min(position for plane in tile["planes"]
                   for position in plane["f0_positions_i16"])


def emit_plane(pointer: str, base: int, coefficient: int,
               destination: int, temporary: int = 12) -> list[str]:
    source_pair = 0 if coefficient < 2 else 64
    immediate = 0x20 if coefficient % 2 == 0 else 0x31
    return [
        f"  vmovdqa ymm{destination}, YMMWORD PTR [{pointer} + {base + source_pair}]",
        f"  vmovdqa ymm{temporary}, YMMWORD PTR [{pointer} + {base + source_pair + 32}]",
        f"  vperm2i128 ymm{destination}, ymm{destination}, ymm{temporary}, 0x{immediate:02x}",
    ]


def emit_native_plane(pointer: str, base: int, coefficient: int,
                      destination: int) -> list[str]:
    return [
        f"  vmovdqa ymm{destination}, YMMWORD PTR "
        f"[{pointer} + {base + 32 * coefficient}]",
    ]


def emit_tile(tile: dict, h_specs: dict, labels: dict, r_base: int,
              m_base: int, output_base: int, output_pointer: str,
              native_inputs: bool = False) -> list[str]:
    name = ma1.label_tile(tile)
    out = [f"  /* MA2 streaming tile {name}: retain h[0..3], r[0..3]. */"]
    for coefficient in range(4):
        spec = h_specs[(name, coefficient)]
        out += [
            f"  MA1_PROJECT_H {coefficient},12,{spec.source_offsets_bytes[0]},"
            f"{spec.source_offsets_bytes[1]},0x{spec.permute_imm:02x},"
            f"{labels[spec.shuffle]},0x{spec.blend_imm:02x}",
            f"  MA1_MONT_CONST {coefficient},{coefficient},.Lma1_r2,.Lma1_r2_qinv,11",
        ]
    for coefficient in range(4):
        if native_inputs:
            out += emit_native_plane("rsi", r_base, coefficient, 4 + coefficient)
        else:
            out += emit_plane("rsi", r_base, coefficient, 4 + coefficient)

    for coefficient, (plain, wrapped) in enumerate(TERMS):
        if native_inputs:
            out += emit_native_plane("rdx", m_base, coefficient, 8)
        else:
            out += emit_plane("rdx", m_base, coefficient, 8)
        for h_index, r_index in plain:
            out += [f"  MA1_MONT_REG 10,{h_index},{4+r_index},11",
                    "  vpaddw ymm8, ymm8, ymm10"]
        for term_index, (h_index, r_index) in enumerate(wrapped):
            out.append(f"  MA1_MONT_REG 10,{h_index},{4+r_index},11")
            out.append("  vmovdqa ymm9, ymm10" if term_index == 0
                       else "  vpaddw ymm9, ymm9, ymm10")
        if wrapped:
            out += [f"  MA1_MONT_CONST 10,9,.Llambda_{name},.Llambda_{name}_qinv,11",
                    "  vpaddw ymm8, ymm8, ymm10"]
        out += ["  MA1_MONT_CONST 8,8,.Lma1_inv4,.Lma1_inv4_qinv,11",
                f"  vmovdqa YMMWORD PTR [{output_pointer} + {output_base + 32*coefficient}], ymm8"]
    return out


def direct_pack_macro(common: str) -> str:
    lines = common.splitlines()
    start = next(i for i, line in enumerate(lines)
                 if line.strip() == "vpsllw ymm10, ymm1, 12")
    end = next(i for i in range(start, len(lines))
               if lines[i].strip() == ".endm")
    body = "\n".join(lines[start:end])
    return f"\n.macro MA2_PACK_DIRECT ctoff\n{body}\n.endm\n"


def emit_direct_route(chunk: int, tiles: list[dict], output_specs: dict,
                      labels: dict, output_offset: int = 0) -> list[str]:
    out = ["  /* Semantic planes -> registers -> bytes; no Official-vector scratch. */"]
    for coefficient in range(4):
        out += [f"  vmovdqa ymm8, YMMWORD PTR [r8 + {32*coefficient}]",
                f"  vmovdqa ymm9, YMMWORD PTR [r8 + {128+32*coefficient}]"]
        for group in range(2):
            spec = output_specs[(chunk, coefficient, group)]
            target = 4 * group + coefficient
            out += [
                f"  vperm2i128 ymm10, ymm8, ymm9, 0x{spec.permute_immediates[0]:02x}",
                f"  vpshufb ymm10, ymm10, YMMWORD PTR [rip + {labels[spec.masks[0]]}]",
                f"  vperm2i128 ymm11, ymm8, ymm9, 0x{spec.permute_immediates[1]:02x}",
                f"  vpshufb ymm11, ymm11, YMMWORD PTR [rip + {labels[spec.masks[1]]}]",
                f"  vpor ymm{target}, ymm10, ymm11",
            ]
    for register in range(8):
        out += [f"  vpsraw ymm12, ymm{register}, 15",
                "  vpand ymm12, ymm12, YMMWORD PTR [rip + .Lma1_q]",
                f"  vpaddw ymm{register}, ymm{register}, ymm12"]
    out.append(f"  MA2_PACK_DIRECT {output_offset}")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schedule", type=Path, required=True)
    parser.add_argument("--range-proof", type=Path, required=True)
    parser.add_argument("--asm", type=Path, required=True)
    parser.add_argument("--constants", type=Path, required=True)
    parser.add_argument("--header", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    schedule_raw = args.schedule.read_bytes()
    schedule = json.loads(schedule_raw)
    proof_raw = args.range_proof.read_bytes()
    proof = json.loads(proof_raw)
    if proof["schema"] != "gt-f0-ma2-range/v1" or not proof["direct_sign_pack_proved"]:
        raise SystemExit("MA2 direct-pack range is not proved")
    by_key = {(x["tile"]["branch"], x["tile"]["p"]): x
              for x in schedule["semantic_tiles"]}
    chunks = [[by_key[(x["branch"], x["p"])]
               for x in entry["semantic_tiles"]]
              for entry in schedule["official_chunk_pairing"]]
    chunk0 = chunks[0]

    masks = {}
    def label(mask):
        if mask not in masks:
            masks[mask] = f".Lma2_mask_{len(masks)}"
        return masks[mask]
    h_specs = {}
    for tile in schedule["semantic_tiles"]:
        for coefficient in range(4):
            spec = ma1.h_projection(tile, coefficient)
            h_specs[(ma1.label_tile(tile), coefficient)] = spec
            label(spec.shuffle)
    output_specs = {}
    for chunk_index, chunk_tiles in enumerate(chunks):
        for coefficient in range(4):
            for group in range(2):
                spec = ma1.output_route(chunk_tiles, chunk_index, coefficient,
                                        8 * chunk_index + 4 * group + coefficient)
                output_specs[(chunk_index, coefficient, group)] = spec
                label(spec.masks[0]); label(spec.masks[1])

    constants = "/* Generated F0-MA2 constants. */\n.p2align 5\n"
    for name, value in ((".Lma1_q", Q), (".Lma1_qinv", QINV),
                        (".Lma1_barrett", 9), (".Lma1_pack_barrett", 9),
                        (".Lma1_half_q", 1728), (".Lma1_negative_half_q", -1728),
                        (".Lma1_r2", 867), (".Lma1_r2_qinv", 2787)):
        constants += ma1.vec16(name, [value] * 16)
    inv4 = ma1.centered(pow(4, -1, Q) * R)
    constants += ma1.vec16(".Lma1_inv4", [inv4] * 16)
    constants += ma1.vec16(".Lma1_inv4_qinv",
                           [ma1.signed16(inv4 * QINV)] * 16)
    for tile in schedule["semantic_tiles"]:
        name = ma1.label_tile(tile)
        factors = [ma1.centered(x * R)
                   for x in tile["planes"][0]["lambda_mod_q"]]
        constants += ma1.vec16(f".Llambda_{name}", factors)
        constants += ma1.vec16(f".Llambda_{name}_qinv",
                               [ma1.signed16(x * QINV) for x in factors])
    for mask, name in masks.items():
        constants += ma1.bytes32(name, list(mask))

    common = ma1.emit_common_macros()
    asm = ".intel_syntax noprefix\n.text\n" + common + direct_pack_macro(common)
    asm0 = "ntruplus1152_exp001_f0_ma2_asm0_b0p0"
    asm += f"\n.globl {asm0}\n.type {asm0},@function\n.p2align 5\n{asm0}:\n"
    asm += "\n".join(emit_tile(by_key[(0, 0)], h_specs, masks, 0, 0, 0, "rdi"))
    asm += f"\n  ret\n.size {asm0}, .-{asm0}\n"

    chunk = "ntruplus1152_exp001_f0_ma2_chunk0"
    asm += f"\n.globl {chunk}\n.type {chunk},@function\n.p2align 5\n{chunk}:\n"
    asm += "\n".join(emit_tile(chunk0[0], h_specs, masks,
                                tile_base(chunk0[0]), tile_base(chunk0[0]),
                                0, "r8")) + "\n"
    asm += "\n".join(emit_tile(chunk0[1], h_specs, masks,
                                tile_base(chunk0[1]), tile_base(chunk0[1]),
                                128, "r8")) + "\n"
    asm += "\n".join(emit_direct_route(0, chunk0, output_specs, masks))
    asm += f"\n  ret\n.size {chunk}, .-{chunk}\n"

    full = "ntruplus1152_exp001_f0_ma2_full"
    asm += f"\n.globl {full}\n.type {full},@function\n.p2align 5\n{full}:\n"
    for chunk_index, chunk_tiles in enumerate(chunks):
        asm += f"  /* Complete MA2 serializer chunk {chunk_index}. */\n"
        asm += "\n".join(emit_tile(chunk_tiles[0], h_specs, masks,
                                    tile_base(chunk_tiles[0]),
                                    tile_base(chunk_tiles[0]), 0, "r8")) + "\n"
        asm += "\n".join(emit_tile(chunk_tiles[1], h_specs, masks,
                                    tile_base(chunk_tiles[1]),
                                    tile_base(chunk_tiles[1]), 128, "r8")) + "\n"
        asm += "\n".join(emit_direct_route(chunk_index, chunk_tiles,
                                             output_specs, masks,
                                             192 * chunk_index)) + "\n"
    asm += f"  ret\n.size {full}, .-{full}\n"

    native_full = "ntruplus1152_exp001_f0_ma2_native_full"
    asm += (f"\n.globl {native_full}\n.type {native_full},@function\n"
            f".p2align 5\n{native_full}:\n")
    for chunk_index, chunk_tiles in enumerate(chunks):
        asm += f"  /* Complete MA2 native-input serializer chunk {chunk_index}. */\n"
        asm += "\n".join(emit_tile(chunk_tiles[0], h_specs, masks,
                                    tile_base(chunk_tiles[0]),
                                    tile_base(chunk_tiles[0]), 0, "r8",
                                    native_inputs=True)) + "\n"
        asm += "\n".join(emit_tile(chunk_tiles[1], h_specs, masks,
                                    tile_base(chunk_tiles[1]),
                                    tile_base(chunk_tiles[1]), 128, "r8",
                                    native_inputs=True)) + "\n"
        asm += "\n".join(emit_direct_route(chunk_index, chunk_tiles,
                                             output_specs, masks,
                                             192 * chunk_index)) + "\n"
    asm += f"  ret\n.size {native_full}, .-{native_full}\n"
    asm += '\n.section .rodata\n#include "generated/f0-ma2-constants.inc"\n'
    asm += '\n.section .note.GNU-stack,"",@progbits\n'

    header = """#ifndef NTRUPLUS1152_EXP001_F0_MA2_ASM_H
#define NTRUPLUS1152_EXP001_F0_MA2_ASM_H
#include <stdint.h>
void ntruplus1152_exp001_f0_ma2_asm0_b0p0(
    int16_t out[64], const int16_t r[64], const int16_t m[64],
    const int16_t h[1152]);
void ntruplus1152_exp001_f0_ma2_chunk0(
    uint8_t out[192], const int16_t r[1152], const int16_t m[1152],
    const int16_t h[1152], int16_t plane_scratch[128]);
void ntruplus1152_exp001_f0_ma2_full(
    uint8_t out[1728], const int16_t r[1152], const int16_t m[1152],
    const int16_t h[1152], int16_t plane_scratch[128]);
void ntruplus1152_exp001_f0_ma2_native_full(
    uint8_t out[1728], const int16_t r_planes[1152],
    const int16_t m_planes[1152], const int16_t h[1152],
    int16_t plane_scratch[128]);
#endif
"""
    contract = {
        "schema": "gt-f0-ma2-asm/v1", "checkpoint": "F0-MA2-ASM0/CHUNK0",
        "arithmetic": {"core_chains_per_tile": 19, "h_lifts_per_tile": 4,
                       "inv4_per_tile": 4, "total_per_tile": 27,
                       "chunk0_total": 54},
        "representation": "fixed coefficient, 16 physical-q leaves per YMM",
        "schedule": "retain four h and four r planes; stream one m/output accumulator",
        "asm0": {"tile": "b0p0", "scratch_bytes": 0, "peak_ymm": 13},
        "chunk0": {"tiles": [ma1.label_tile(x) for x in chunk0],
                   "scratch_i16": 128, "scratch_role": "eight semantic output planes only",
                   "official_vector_intermediate": False,
                   "pack_barrett": False, "peak_ymm": 14},
        "full": {"chunks": 9, "tiles": 18, "scratch_i16": 128,
                 "scratch_role": "reused eight semantic output planes",
                 "official_vector_intermediate": False,
                 "pack_barrett": False, "peak_ymm": 14,
                 "total_montgomery_chains": 486},
        "native_full": {
            "symbol": native_full, "chunks": 9, "tiles": 18,
            "input_abi": "MA2 coefficient planes",
            "r_aligned_plane_loads": 72, "m_aligned_plane_loads": 72,
            "generic_f0_projection_permutations": 0,
            "arithmetic_and_serializer": "identical to full",
            "scratch_i16": 128, "peak_ymm": 14,
            "total_montgomery_chains": 486,
        },
        "alignment": {"entries": 32, "constants": 32,
                      "polys_and_scratch": 32, "bytes": "unaligned"},
        "range_proof_sha256": hashlib.sha256(proof_raw).hexdigest(),
        "schedule_sha256": hashlib.sha256(schedule_raw).hexdigest(),
    }
    write(args.asm, asm, args.check); write(args.constants, constants, args.check)
    write(args.header, header, args.check)
    write(args.contract, json.dumps(contract, indent=2, sort_keys=True) + "\n",
          args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
