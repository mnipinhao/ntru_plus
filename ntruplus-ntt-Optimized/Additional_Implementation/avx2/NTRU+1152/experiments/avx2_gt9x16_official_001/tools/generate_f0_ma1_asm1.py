#!/usr/bin/env python3
"""Generate caller-shaped F0-MA1 ASM1 C0/C1 assembly and proof data."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

Q = 3457
QINV = 12929
R = 65536 % Q


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def signed16(value: int) -> int:
    value &= 0xffff
    return value - 65536 if value >= 32768 else value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, content: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text() != content:
            raise SystemExit(f"generated file is stale: {path}")
    else:
        path.write_text(content)


def vec16(label: str, values: list[int]) -> str:
    if len(values) != 16:
        raise SystemExit(f"{label}: vector length is not 16")
    return f"{label}:\n  .short " + ", ".join(map(str, values)) + "\n"


def bytes32(label: str, values: list[int]) -> str:
    if len(values) != 32:
        raise SystemExit(f"{label}: byte mask length is not 32")
    return f"{label}:\n  .byte " + ", ".join(map(str, values)) + "\n"


@dataclass(frozen=True)
class HProjection:
    source_offsets_bytes: tuple[int, int]
    permute_imm: int
    shuffle: tuple[int, ...]
    blend_imm: int


@dataclass(frozen=True)
class OutputRoute:
    permute_immediates: tuple[int, int]
    masks: tuple[tuple[int, ...], tuple[int, ...]]


def byte_shuffle(word_indices: list[int | None]) -> tuple[int, ...]:
    result: list[int] = []
    for word in word_indices:
        if word is None:
            result.extend((128, 128))
        else:
            result.extend((2 * word, 2 * word + 1))
    return tuple(result)


def h_projection(tile: dict, coefficient: int) -> HProjection:
    plane = tile["planes"][coefficient]
    vectors = plane["resident_h_source_vectors"]
    positions = plane["resident_h_official_positions_i16"]
    by_vector = {vector: index for index, vector in enumerate(vectors)}
    halves = []
    word_indices = []
    source_indices = []
    for position in positions:
        vector, lane = divmod(position, 16)
        source_indices.append(by_vector[vector])
        halves.append(lane // 8)
        word_indices.append(lane % 8)
    for destination_half in range(2):
        part = halves[8 * destination_half:8 * destination_half + 8]
        if len(set(part)) != 1:
            raise SystemExit("resident-h projection mixes source halves")
    if word_indices[:8] != word_indices[8:]:
        raise SystemExit("resident-h projection needs distinct half shuffles")
    expected_source = [0] * 8 + [1] * 8
    cross = [actual != expected for actual, expected in
             zip(source_indices, expected_source)]
    if cross[:8] != cross[8:]:
        raise SystemExit("resident-h cross-vector exchange is not symmetric")
    low_select = halves[0]
    high_select = 2 + halves[8]
    return HProjection(
        tuple(32 * vector for vector in vectors),
        low_select | (high_select << 4),
        byte_shuffle(word_indices[:8] + word_indices[:8]),
        sum((1 << lane) for lane, enabled in enumerate(cross[:8]) if enabled),
    )


def output_route(tiles: list[dict], chunk: int, coefficient: int,
                 official_vector: int) -> OutputRoute:
    owners = {}
    for tile_index, tile in enumerate(tiles):
        plane = tile["planes"][coefficient]
        for semantic_lane, position in enumerate(
                plane["resident_h_official_positions_i16"]):
            owners[position] = (tile_index, semantic_lane)
    selections: list[list[int]] = [[], []]
    word_masks: list[list[int | None]] = [[], []]
    for destination_lane in range(16):
        position = official_vector * 16 + destination_lane
        if position not in owners:
            raise SystemExit(f"missing output owner for position {position}")
        tile_index, semantic_lane = owners[position]
        selections[semantic_lane // 8].append(tile_index)
    immediates = []
    masks = []
    for source_half in range(2):
        per_half_select = []
        mask_words: list[int | None] = []
        for destination_half in range(2):
            half_owners = [owners[official_vector * 16 + 8 * destination_half + lane]
                           for lane in range(8)]
            tile_ids = {owner[0] for owner in half_owners}
            if len(tile_ids) != 1:
                raise SystemExit("official output half mixes semantic tiles")
            tile_index = tile_ids.pop()
            per_half_select.append(2 * tile_index + source_half)
            for owner_tile, semantic_lane in half_owners:
                if owner_tile != tile_index:
                    raise SystemExit("output half owner changed")
                mask_words.append(semantic_lane % 8
                                  if semantic_lane // 8 == source_half else None)
        immediates.append(per_half_select[0] | (per_half_select[1] << 4))
        masks.append(byte_shuffle(mask_words))
    return OutputRoute(tuple(immediates), tuple(masks))


def label_tile(tile: dict) -> str:
    data = tile["tile"]
    return f"b{data['branch']}p{data['p']}"


def emit_common_macros() -> str:
    return r'''
.macro MA1_CENTER x,tmp
  vpmulhrsw ymm\tmp, ymm\x, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm\tmp, ymm\tmp, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm\x, ymm\x, ymm\tmp
  vpcmpgtw ymm\tmp, ymm\x, YMMWORD PTR [rip + .Lma1_half_q]
  vpand ymm\tmp, ymm\tmp, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm\x, ymm\x, ymm\tmp
  vmovdqa ymm\tmp, YMMWORD PTR [rip + .Lma1_negative_half_q]
  vpcmpgtw ymm\tmp, ymm\tmp, ymm\x
  vpand ymm\tmp, ymm\tmp, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm\x, ymm\x, ymm\tmp
.endm

.macro MA1_CENTER2 a,b,ta,tb
  vpmulhrsw ymm\ta, ymm\a, YMMWORD PTR [rip + .Lma1_barrett]
  vpmulhrsw ymm\tb, ymm\b, YMMWORD PTR [rip + .Lma1_barrett]
  vpmullw ymm\ta, ymm\ta, YMMWORD PTR [rip + .Lma1_q]
  vpmullw ymm\tb, ymm\tb, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm\a, ymm\a, ymm\ta
  vpsubw ymm\b, ymm\b, ymm\tb
  vpcmpgtw ymm\ta, ymm\a, YMMWORD PTR [rip + .Lma1_half_q]
  vpcmpgtw ymm\tb, ymm\b, YMMWORD PTR [rip + .Lma1_half_q]
  vpand ymm\ta, ymm\ta, YMMWORD PTR [rip + .Lma1_q]
  vpand ymm\tb, ymm\tb, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm\a, ymm\a, ymm\ta
  vpsubw ymm\b, ymm\b, ymm\tb
  vmovdqa ymm\ta, YMMWORD PTR [rip + .Lma1_negative_half_q]
  vmovdqa ymm\tb, YMMWORD PTR [rip + .Lma1_negative_half_q]
  vpcmpgtw ymm\ta, ymm\ta, ymm\a
  vpcmpgtw ymm\tb, ymm\tb, ymm\b
  vpand ymm\ta, ymm\ta, YMMWORD PTR [rip + .Lma1_q]
  vpand ymm\tb, ymm\tb, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm\a, ymm\a, ymm\ta
  vpaddw ymm\b, ymm\b, ymm\tb
.endm

.macro MA1_MONT_CONST dst,a,factor,factor_qinv,tmp
  vpmullw ymm\tmp, ymm\a, YMMWORD PTR [rip + \factor_qinv]
  vpmulhw ymm\dst, ymm\a, YMMWORD PTR [rip + \factor]
  vpmulhw ymm\tmp, ymm\tmp, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm\dst, ymm\dst, ymm\tmp
.endm

.macro MA1_MONT_CONST2 da,db,a,b,factor,factor_qinv,ta,tb
  vpmullw ymm\ta, ymm\a, YMMWORD PTR [rip + \factor_qinv]
  vpmullw ymm\tb, ymm\b, YMMWORD PTR [rip + \factor_qinv]
  vpmulhw ymm\da, ymm\a, YMMWORD PTR [rip + \factor]
  vpmulhw ymm\db, ymm\b, YMMWORD PTR [rip + \factor]
  vpmulhw ymm\ta, ymm\ta, YMMWORD PTR [rip + .Lma1_q]
  vpmulhw ymm\tb, ymm\tb, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm\da, ymm\da, ymm\ta
  vpsubw ymm\db, ymm\db, ymm\tb
.endm

.macro MA1_MONT_REG dst,a,b,tmp
  vpmullw ymm\tmp, ymm\a, YMMWORD PTR [rip + .Lma1_qinv]
  vpmullw ymm\tmp, ymm\tmp, ymm\b
  vpmulhw ymm\dst, ymm\a, ymm\b
  vpmulhw ymm\tmp, ymm\tmp, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm\dst, ymm\dst, ymm\tmp
.endm

.macro MA1_MONT_REG2 da,db,a,b,ra,rb,ta,tb
  vpmullw ymm\ta, ymm\a, YMMWORD PTR [rip + .Lma1_qinv]
  vpmullw ymm\tb, ymm\b, YMMWORD PTR [rip + .Lma1_qinv]
  vpmullw ymm\ta, ymm\ta, ymm\ra
  vpmullw ymm\tb, ymm\tb, ymm\rb
  vpmulhw ymm\da, ymm\a, ymm\ra
  vpmulhw ymm\db, ymm\b, ymm\rb
  vpmulhw ymm\ta, ymm\ta, YMMWORD PTR [rip + .Lma1_q]
  vpmulhw ymm\tb, ymm\tb, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm\da, ymm\da, ymm\ta
  vpsubw ymm\db, ymm\db, ymm\tb
.endm

.macro MA1_PROJECT_H dst,tmp,aoff,boff,imm,mask,blend
  vmovdqa ymm\dst, YMMWORD PTR [rcx + \aoff]
  vmovdqa ymm\tmp, YMMWORD PTR [rcx + \boff]
  vperm2i128 ymm\dst, ymm\dst, ymm\tmp, \imm
  vpshufb ymm\dst, ymm\dst, YMMWORD PTR [rip + \mask]
  vperm2i128 ymm\tmp, ymm\dst, ymm\dst, 0x01
  vpblendw ymm\dst, ymm\dst, ymm\tmp, \blend
.endm

.macro MA1_PRODUCT hbase,himm,rbase0,rbase1,rimm,mode
  vperm2i128 ymm6, ymm\hbase, ymm\hbase, \himm
  .if \rimm < 0
    MA1_MONT_REG 8,6,\rbase0,9
  .else
    vperm2i128 ymm7, ymm\rbase0, ymm\rbase1, \rimm
    MA1_MONT_REG 8,6,7,9
  .endif
  .if \mode == 0
    vpaddw ymm4, ymm4, ymm8
  .elseif \mode == 1
    vpand ymm10, ymm8, YMMWORD PTR [rip + .Lma1_low_half]
    vpaddw ymm5, ymm5, ymm10
    vpxor ymm10, ymm10, ymm8
    vpaddw ymm4, ymm4, ymm10
  .else
    vpaddw ymm5, ymm5, ymm8
  .endif
.endm

.macro MA1_PAIR01 mbase,moff,lambda,lambda_qinv,outoff
  vmovdqa ymm4, YMMWORD PTR [rdx + \mbase + \moff]
  MA1_CENTER 4,9
  vpxor ymm5, ymm5, ymm5
  MA1_PRODUCT 0,0x00,2,2,-1,0
  MA1_PRODUCT 0,0x11,3,2,0x21,1
  MA1_PRODUCT 1,0x00,3,3,-1,2
  MA1_PRODUCT 1,0x11,2,3,0x21,2
  MA1_MONT_CONST 8,5,\lambda,\lambda_qinv,9
  vpaddw ymm4, ymm4, ymm8
  MA1_MONT_CONST 4,4,.Lma1_inv4,.Lma1_inv4_qinv,9
  MA1_CENTER 4,9
  vmovdqa YMMWORD PTR [r8 + \outoff], ymm4
.endm

.macro MA1_PAIR23 mbase,moff,lambda,lambda_qinv,outoff
  vmovdqa ymm4, YMMWORD PTR [rdx + \mbase + \moff]
  MA1_CENTER 4,9
  vpxor ymm5, ymm5, ymm5
  MA1_PRODUCT 0,0x00,3,3,-1,0
  MA1_PRODUCT 0,0x11,2,3,0x21,0
  MA1_PRODUCT 1,0x00,2,2,-1,0
  MA1_PRODUCT 1,0x11,3,2,0x21,1
  MA1_MONT_CONST 8,5,\lambda,\lambda_qinv,9
  vpaddw ymm4, ymm4, ymm8
  MA1_MONT_CONST 4,4,.Lma1_inv4,.Lma1_inv4_qinv,9
  MA1_CENTER 4,9
  vmovdqa YMMWORD PTR [r8 + \outoff], ymm4
.endm

.macro MA1_STREAM_C0 rbase,mbase,roff0,roff1,moff0,moff1,lambda,lambda_qinv,h0,h1,out0,out1
  vmovdqa ymm0, YMMWORD PTR [r8 + \h0]
  vmovdqa ymm1, YMMWORD PTR [r8 + \h1]
  MA1_CENTER 0,9
  MA1_CENTER 1,9
  MA1_MONT_CONST 0,0,.Lma1_r2,.Lma1_r2_qinv,9
  MA1_MONT_CONST 1,1,.Lma1_r2,.Lma1_r2_qinv,9
  vmovdqa ymm2, YMMWORD PTR [rsi + \rbase + \roff0]
  vmovdqa ymm3, YMMWORD PTR [rsi + \rbase + \roff1]
  MA1_CENTER 2,9
  MA1_CENTER 3,9
  MA1_PAIR01 \mbase,\moff0,\lambda,\lambda_qinv,\out0
  MA1_PAIR23 \mbase,\moff1,\lambda,\lambda_qinv,\out1
.endm

.macro MA1_PACK_CHUNK ctoff
  vmovdqa ymm0, YMMWORD PTR [r8 + 256]
  vmovdqa ymm1, YMMWORD PTR [r8 + 288]
  vmovdqa ymm2, YMMWORD PTR [r8 + 320]
  vmovdqa ymm3, YMMWORD PTR [r8 + 352]
  vmovdqa ymm4, YMMWORD PTR [r8 + 384]
  vmovdqa ymm5, YMMWORD PTR [r8 + 416]
  vmovdqa ymm6, YMMWORD PTR [r8 + 448]
  vmovdqa ymm7, YMMWORD PTR [r8 + 480]
  vpmulhrsw ymm10, ymm0, YMMWORD PTR [rip + .Lma1_pack_barrett]
  vpmulhrsw ymm11, ymm1, YMMWORD PTR [rip + .Lma1_pack_barrett]
  vpmulhrsw ymm12, ymm2, YMMWORD PTR [rip + .Lma1_pack_barrett]
  vpmulhrsw ymm13, ymm3, YMMWORD PTR [rip + .Lma1_pack_barrett]
  vpmullw ymm10, ymm10, YMMWORD PTR [rip + .Lma1_q]
  vpmullw ymm11, ymm11, YMMWORD PTR [rip + .Lma1_q]
  vpmullw ymm12, ymm12, YMMWORD PTR [rip + .Lma1_q]
  vpmullw ymm13, ymm13, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm0, ymm0, ymm10
  vpsubw ymm1, ymm1, ymm11
  vpsubw ymm2, ymm2, ymm12
  vpsubw ymm3, ymm3, ymm13
  vpmulhrsw ymm10, ymm4, YMMWORD PTR [rip + .Lma1_pack_barrett]
  vpmulhrsw ymm11, ymm5, YMMWORD PTR [rip + .Lma1_pack_barrett]
  vpmulhrsw ymm12, ymm6, YMMWORD PTR [rip + .Lma1_pack_barrett]
  vpmulhrsw ymm13, ymm7, YMMWORD PTR [rip + .Lma1_pack_barrett]
  vpmullw ymm10, ymm10, YMMWORD PTR [rip + .Lma1_q]
  vpmullw ymm11, ymm11, YMMWORD PTR [rip + .Lma1_q]
  vpmullw ymm12, ymm12, YMMWORD PTR [rip + .Lma1_q]
  vpmullw ymm13, ymm13, YMMWORD PTR [rip + .Lma1_q]
  vpsubw ymm4, ymm4, ymm10
  vpsubw ymm5, ymm5, ymm11
  vpsubw ymm6, ymm6, ymm12
  vpsubw ymm7, ymm7, ymm13
  vpsraw ymm10, ymm0, 15
  vpsraw ymm11, ymm1, 15
  vpsraw ymm12, ymm2, 15
  vpsraw ymm13, ymm3, 15
  vpand ymm10, ymm10, YMMWORD PTR [rip + .Lma1_q]
  vpand ymm11, ymm11, YMMWORD PTR [rip + .Lma1_q]
  vpand ymm12, ymm12, YMMWORD PTR [rip + .Lma1_q]
  vpand ymm13, ymm13, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm0, ymm0, ymm10
  vpaddw ymm1, ymm1, ymm11
  vpaddw ymm2, ymm2, ymm12
  vpaddw ymm3, ymm3, ymm13
  vpsraw ymm10, ymm4, 15
  vpsraw ymm11, ymm5, 15
  vpsraw ymm12, ymm6, 15
  vpsraw ymm13, ymm7, 15
  vpand ymm10, ymm10, YMMWORD PTR [rip + .Lma1_q]
  vpand ymm11, ymm11, YMMWORD PTR [rip + .Lma1_q]
  vpand ymm12, ymm12, YMMWORD PTR [rip + .Lma1_q]
  vpand ymm13, ymm13, YMMWORD PTR [rip + .Lma1_q]
  vpaddw ymm4, ymm4, ymm10
  vpaddw ymm5, ymm5, ymm11
  vpaddw ymm6, ymm6, ymm12
  vpaddw ymm7, ymm7, ymm13
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
  vmovdqu YMMWORD PTR [rdi + \ctoff], ymm0
  vmovdqu YMMWORD PTR [rdi + \ctoff + 32], ymm1
  vmovdqu YMMWORD PTR [rdi + \ctoff + 64], ymm2
  vmovdqu YMMWORD PTR [rdi + \ctoff + 96], ymm3
  vmovdqu YMMWORD PTR [rdi + \ctoff + 128], ymm4
  vmovdqu YMMWORD PTR [rdi + \ctoff + 160], ymm5
.endm
'''


def emit_tile_c0(tile: dict, scratch_base: int, h_specs: dict,
                 mask_labels: dict) -> list[str]:
    name = label_tile(tile)
    base_words = min(position for plane in tile["planes"]
                     for position in plane["f0_positions_i16"])
    base = 2 * base_words
    out = [f"  /* C0 tile {name}. */"]
    for coefficient in range(4):
        spec = h_specs[(name, coefficient)]
        mask = mask_labels[spec.shuffle]
        out.append(f"  MA1_PROJECT_H {coefficient},8,{spec.source_offsets_bytes[0]},"
                   f"{spec.source_offsets_bytes[1]},0x{spec.permute_imm:02x},{mask},"
                   f"0x{spec.blend_imm:02x}")
    out += [
        "  vperm2i128 ymm8, ymm0, ymm1, 0x20",
        "  vperm2i128 ymm9, ymm0, ymm1, 0x31",
        f"  vmovdqa YMMWORD PTR [r8 + {scratch_base}], ymm8",
        f"  vmovdqa YMMWORD PTR [r8 + {scratch_base + 32}], ymm9",
        "  vperm2i128 ymm8, ymm2, ymm3, 0x20",
        "  vperm2i128 ymm9, ymm2, ymm3, 0x31",
        f"  vmovdqa YMMWORD PTR [r8 + {scratch_base + 64}], ymm8",
        f"  vmovdqa YMMWORD PTR [r8 + {scratch_base + 96}], ymm9",
        f"  MA1_STREAM_C0 {base},{base},0,64,0,64,.Llambda_{name}_s0,.Llambda_{name}_s0_qinv,{scratch_base},{scratch_base + 64},{scratch_base},{scratch_base + 64}",
        f"  MA1_STREAM_C0 {base},{base},32,96,32,96,.Llambda_{name}_s1,.Llambda_{name}_s1_qinv,{scratch_base + 32},{scratch_base + 96},{scratch_base + 32},{scratch_base + 96}",
        f"  vmovdqa ymm0, YMMWORD PTR [r8 + {scratch_base}]",
        f"  vmovdqa ymm1, YMMWORD PTR [r8 + {scratch_base + 32}]",
        "  vperm2i128 ymm2, ymm0, ymm1, 0x20",
        "  vperm2i128 ymm3, ymm0, ymm1, 0x31",
        f"  vmovdqa YMMWORD PTR [r8 + {scratch_base}], ymm2",
        f"  vmovdqa YMMWORD PTR [r8 + {scratch_base + 32}], ymm3",
        f"  vmovdqa ymm0, YMMWORD PTR [r8 + {scratch_base + 64}]",
        f"  vmovdqa ymm1, YMMWORD PTR [r8 + {scratch_base + 96}]",
        "  vperm2i128 ymm2, ymm0, ymm1, 0x20",
        "  vperm2i128 ymm3, ymm0, ymm1, 0x31",
        f"  vmovdqa YMMWORD PTR [r8 + {scratch_base + 64}], ymm2",
        f"  vmovdqa YMMWORD PTR [r8 + {scratch_base + 96}], ymm3",
    ]
    return out


def emit_output_routes(chunk: int, tiles: list[dict], output_specs: dict,
                       mask_labels: dict) -> list[str]:
    out = [f"  /* Chunk {chunk}: semantic planes to eight Official vectors. */"]
    for coefficient in range(4):
        out += [
            f"  vmovdqa ymm0, YMMWORD PTR [r8 + {32 * coefficient}]",
            f"  vmovdqa ymm1, YMMWORD PTR [r8 + {128 + 32 * coefficient}]",
        ]
        for group in range(2):
            spec = output_specs[(chunk, coefficient, group)]
            mask0 = mask_labels[spec.masks[0]]
            mask1 = mask_labels[spec.masks[1]]
            out += [
                f"  vperm2i128 ymm2, ymm0, ymm1, 0x{spec.permute_immediates[0]:02x}",
                f"  vpshufb ymm2, ymm2, YMMWORD PTR [rip + {mask0}]",
                f"  vperm2i128 ymm3, ymm0, ymm1, 0x{spec.permute_immediates[1]:02x}",
                f"  vpshufb ymm3, ymm3, YMMWORD PTR [rip + {mask1}]",
                "  vpor ymm2, ymm2, ymm3",
                f"  vmovdqa YMMWORD PTR [r8 + {256 + 32 * (4 * group + coefficient)}], ymm2",
            ]
    return out


def emit_c1_project_pair(tile_a: dict, tile_b: dict, coefficients: tuple[int, int],
                         h_specs: dict, mask_labels: dict) -> list[str]:
    out = []
    pair_vectors = []
    for tile_index, tile in enumerate((tile_a, tile_b)):
        name = label_tile(tile)
        regs = (0, 1) if tile_index == 0 else (4, 5)
        for coefficient, register in zip(coefficients, regs):
            spec = h_specs[(name, coefficient)]
            out.append(f"  MA1_PROJECT_H {register},8,{spec.source_offsets_bytes[0]},"
                       f"{spec.source_offsets_bytes[1]},0x{spec.permute_imm:02x},"
                       f"{mask_labels[spec.shuffle]},0x{spec.blend_imm:02x}")
        low, high = (2, 3) if tile_index == 0 else (6, 7)
        out += [f"  vperm2i128 ymm{low}, ymm{regs[0]}, ymm{regs[1]}, 0x20",
                f"  vperm2i128 ymm{high}, ymm{regs[0]}, ymm{regs[1]}, 0x31"]
        pair_vectors.append((low, high))
    pair_base = 0 if coefficients[0] == 0 else 64
    out += [
        f"  MA1_CENTER2 2,6,14,15",
        f"  MA1_MONT_CONST2 2,6,2,6,.Lma1_r2,.Lma1_r2_qinv,14,15",
        f"  vmovdqa YMMWORD PTR [r8 + {pair_base}], ymm2",
        f"  vmovdqa YMMWORD PTR [r8 + {128 + pair_base}], ymm6",
        f"  MA1_CENTER2 3,7,14,15",
        f"  MA1_MONT_CONST2 3,7,3,7,.Lma1_r2,.Lma1_r2_qinv,14,15",
        f"  vmovdqa YMMWORD PTR [r8 + {pair_base + 32}], ymm3",
        f"  vmovdqa YMMWORD PTR [r8 + {128 + pair_base + 32}], ymm7",
    ]
    return out


PAIR_TERMS = {
    "01": [(0, 0x00, "r0", 0), (0, 0x11, "mix", 1),
           (1, 0x00, "r1", 2), (1, 0x11, "mixrev", 2)],
    "23": [(0, 0x00, "r1", 0), (0, 0x11, "mixrev", 0),
           (1, 0x00, "r0", 0), (1, 0x11, "mix", 1)],
}


def emit_pair2(kind: str, stream: int, tile_a: dict, tile_b: dict,
               output_offsets: tuple[int, int]) -> list[str]:
    name_a, name_b = label_tile(tile_a), label_tile(tile_b)
    base_a = 2 * min(position for plane in tile_a["planes"]
                     for position in plane["f0_positions_i16"])
    base_b = 2 * min(position for plane in tile_b["planes"]
                     for position in plane["f0_positions_i16"])
    r0off, r1off = (0, 64) if stream == 0 else (32, 96)
    moff = r0off if kind == "01" else r1off
    out = []
    if kind == "01":
        out += [
            f"  vmovdqa ymm0, YMMWORD PTR [rsi + {base_a + r0off}]",
            f"  vmovdqa ymm1, YMMWORD PTR [rsi + {base_a + r1off}]",
            f"  vmovdqa ymm2, YMMWORD PTR [rsi + {base_b + r0off}]",
            f"  vmovdqa ymm3, YMMWORD PTR [rsi + {base_b + r1off}]",
            "  MA1_CENTER2 0,2,14,15", "  MA1_CENTER2 1,3,14,15",
        ]
    out += [
        f"  vmovdqa ymm4, YMMWORD PTR [rdx + {base_a + moff}]",
        f"  vmovdqa ymm6, YMMWORD PTR [rdx + {base_b + moff}]",
        "  MA1_CENTER2 4,6,14,15",
        "  vpxor ymm5, ymm5, ymm5", "  vpxor ymm7, ymm7, ymm7",
    ]
    hpair_base = 0 if stream == 0 else 32
    for hbase, himm, rkind, mode in PAIR_TERMS[kind]:
        hvec = hpair_base + 64 * hbase
        out += [
            f"  vmovdqa ymm8, YMMWORD PTR [r8 + {hvec}]",
            f"  vmovdqa ymm9, YMMWORD PTR [r8 + {128 + hvec}]",
            f"  vperm2i128 ymm8, ymm8, ymm8, 0x{himm:02x}",
            f"  vperm2i128 ymm9, ymm9, ymm9, 0x{himm:02x}",
        ]
        if rkind == "r0":
            ra, rb = 0, 2
        elif rkind == "r1":
            ra, rb = 1, 3
        elif rkind == "mix":
            out += ["  vperm2i128 ymm10, ymm1, ymm0, 0x21",
                    "  vperm2i128 ymm11, ymm3, ymm2, 0x21"]
            ra, rb = 10, 11
        else:
            out += ["  vperm2i128 ymm10, ymm0, ymm1, 0x21",
                    "  vperm2i128 ymm11, ymm2, ymm3, 0x21"]
            ra, rb = 10, 11
        out.append(f"  MA1_MONT_REG2 12,13,8,9,{ra},{rb},14,15")
        if mode == 0:
            out += ["  vpaddw ymm4, ymm4, ymm12", "  vpaddw ymm6, ymm6, ymm13"]
        elif mode == 2:
            out += ["  vpaddw ymm5, ymm5, ymm12", "  vpaddw ymm7, ymm7, ymm13"]
        else:
            out += [
                "  vpand ymm8, ymm12, YMMWORD PTR [rip + .Lma1_low_half]",
                "  vpand ymm9, ymm13, YMMWORD PTR [rip + .Lma1_low_half]",
                "  vpaddw ymm5, ymm5, ymm8", "  vpaddw ymm7, ymm7, ymm9",
                "  vpxor ymm8, ymm8, ymm12",
                "  vpxor ymm9, ymm9, ymm13",
                "  vpaddw ymm4, ymm4, ymm8", "  vpaddw ymm6, ymm6, ymm9",
            ]
    out += [
        f"  MA1_MONT_CONST2 12,13,5,7,.Llambda_{name_a}_s{stream},.Llambda_{name_a}_s{stream}_qinv,14,15",
    ]
    # Both tiles in one chunk can have different lambda vectors.
    if name_a != name_b:
        out[-1] = f"  MA1_MONT_CONST 12,5,.Llambda_{name_a}_s{stream},.Llambda_{name_a}_s{stream}_qinv,14"
        out.append(f"  MA1_MONT_CONST 13,7,.Llambda_{name_b}_s{stream},.Llambda_{name_b}_s{stream}_qinv,15")
    out += [
        "  vpaddw ymm4, ymm4, ymm12", "  vpaddw ymm6, ymm6, ymm13",
        "  MA1_MONT_CONST2 4,6,4,6,.Lma1_inv4,.Lma1_inv4_qinv,14,15",
        "  MA1_CENTER2 4,6,14,15",
        f"  vmovdqa YMMWORD PTR [r8 + {output_offsets[0]}], ymm4",
        f"  vmovdqa YMMWORD PTR [r8 + {output_offsets[1]}], ymm6",
    ]
    return out


def emit_c1_chunk(chunk: int, tiles: list[dict], h_specs: dict,
                  mask_labels: dict) -> list[str]:
    out = [f"  /* C1 chunk {chunk}: two-tile interleaved schedule. */"]
    out += emit_c1_project_pair(tiles[0], tiles[1], (0, 1), h_specs, mask_labels)
    out += emit_c1_project_pair(tiles[0], tiles[1], (2, 3), h_specs, mask_labels)
    for stream in range(2):
        out += emit_pair2("01", stream, tiles[0], tiles[1],
                          (256 + 32 * stream, 384 + 32 * stream))
        out += emit_pair2("23", stream, tiles[0], tiles[1],
                          (320 + 32 * stream, 448 + 32 * stream))
    # Pair-packed to coefficient planes for both tiles.
    for source, destination in ((256, 0), (384, 128)):
        out += [
            f"  vmovdqa ymm0, YMMWORD PTR [r8 + {source}]",
            f"  vmovdqa ymm1, YMMWORD PTR [r8 + {source + 32}]",
            "  vperm2i128 ymm2, ymm0, ymm1, 0x20",
            "  vperm2i128 ymm3, ymm0, ymm1, 0x31",
            f"  vmovdqa YMMWORD PTR [r8 + {destination}], ymm2",
            f"  vmovdqa YMMWORD PTR [r8 + {destination + 32}], ymm3",
            f"  vmovdqa ymm0, YMMWORD PTR [r8 + {source + 64}]",
            f"  vmovdqa ymm1, YMMWORD PTR [r8 + {source + 96}]",
            "  vperm2i128 ymm2, ymm0, ymm1, 0x20",
            "  vperm2i128 ymm3, ymm0, ymm1, 0x31",
            f"  vmovdqa YMMWORD PTR [r8 + {destination + 64}], ymm2",
            f"  vmovdqa YMMWORD PTR [r8 + {destination + 96}], ymm3",
        ]
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schedule", type=Path, required=True)
    parser.add_argument("--asm", type=Path, required=True)
    parser.add_argument("--constants", type=Path, required=True)
    parser.add_argument("--header", type=Path, required=True)
    parser.add_argument("--oracle-header", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    schedule = json.loads(args.schedule.read_text())
    if schedule["schema"] != "gt-f0-ma-schedule/v1":
        raise SystemExit("wrong F0-MA schedule")
    tiles_by_key = {(tile["tile"]["branch"], tile["tile"]["p"]): tile
                    for tile in schedule["semantic_tiles"]}
    chunks = []
    for chunk_data in schedule["official_chunk_pairing"]:
        tiles = [tiles_by_key[(item["branch"], item["p"])]
                 for item in chunk_data["semantic_tiles"]]
        chunks.append(tiles)

    h_specs = {}
    output_specs = {}
    masks: dict[tuple[int, ...], str] = {}

    def mask_label(mask: tuple[int, ...]) -> str:
        if mask not in masks:
            masks[mask] = f".Lma1_mask_{len(masks)}"
        return masks[mask]

    for tile in schedule["semantic_tiles"]:
        for coefficient in range(4):
            spec = h_projection(tile, coefficient)
            h_specs[(label_tile(tile), coefficient)] = spec
            mask_label(spec.shuffle)
    for chunk, tiles in enumerate(chunks):
        for coefficient in range(4):
            for group in range(2):
                official_vector = chunk * 8 + group * 4 + coefficient
                spec = output_route(tiles, chunk, coefficient, official_vector)
                output_specs[(chunk, coefficient, group)] = spec
                mask_label(spec.masks[0])
                mask_label(spec.masks[1])

    constants = "/* Generated F0-MA1-ASM1 constants. */\n.p2align 5\n"
    for label, value in ((".Lma1_q", Q), (".Lma1_qinv", QINV),
                         (".Lma1_barrett", 9), (".Lma1_pack_barrett", 9),
                         (".Lma1_half_q", 1728),
                         (".Lma1_negative_half_q", -1728),
                         (".Lma1_r2", 867), (".Lma1_r2_qinv", 2787)):
        constants += vec16(label, [value] * 16)
    inv4 = pow(4, -1, Q)
    inv4_r = centered(inv4 * R)
    constants += vec16(".Lma1_inv4", [inv4_r] * 16)
    constants += vec16(".Lma1_inv4_qinv", [signed16(inv4_r * QINV)] * 16)
    constants += vec16(".Lma1_low_half", [-1] * 8 + [0] * 8)
    for tile in schedule["semantic_tiles"]:
        name = label_tile(tile)
        lambdas = tile["planes"][0]["lambda_mod_q"]
        if any(plane["lambda_mod_q"] != lambdas for plane in tile["planes"]):
            raise SystemExit("lambda depends on terminal coefficient")
        factors = [centered(value * R) for value in lambdas]
        qinvs = [signed16(value * QINV) for value in factors]
        for stream in range(2):
            values = factors[8 * stream:8 * stream + 8] * 2
            values_qinv = qinvs[8 * stream:8 * stream + 8] * 2
            constants += vec16(f".Llambda_{name}_s{stream}", values)
            constants += vec16(f".Llambda_{name}_s{stream}_qinv", values_qinv)
    for mask, label in masks.items():
        constants += bytes32(label, list(mask))

    asm = ".intel_syntax noprefix\n.text\n" + emit_common_macros()
    for variant in ("c0", "c1"):
        symbol = f"ntruplus1152_exp001_f0_ma1_asm1_{variant}"
        asm += f"\n.globl {symbol}\n.type {symbol},@function\n.p2align 5\n{symbol}:\n"
        for chunk, tiles in enumerate(chunks):
            if variant == "c0":
                asm += "\n".join(emit_tile_c0(tiles[0], 0, h_specs, masks)) + "\n"
                asm += "\n".join(emit_tile_c0(tiles[1], 128, h_specs, masks)) + "\n"
            else:
                asm += "\n".join(emit_c1_chunk(chunk, tiles, h_specs, masks)) + "\n"
            asm += "\n".join(emit_output_routes(chunk, tiles, output_specs, masks)) + "\n"
            asm += f"  MA1_PACK_CHUNK {192 * chunk}\n"
        asm += f"  ret\n.size {symbol}, .-{symbol}\n"
    asm += '\n.section .rodata\n#include "generated/f0-ma1-asm1-constants.inc"\n'
    asm += '\n.section .note.GNU-stack,"",@progbits\n'

    header = """#ifndef NTRUPLUS1152_EXP001_F0_MA1_ASM1_H
#define NTRUPLUS1152_EXP001_F0_MA1_ASM1_H
#include <stdint.h>
void ntruplus1152_exp001_f0_ma1_asm1_c0(
    uint8_t output[1728], const int16_t r_f0[1152],
    const int16_t m_f0[1152], const int16_t h_official[1152],
    int16_t chunk_scratch[256]);
void ntruplus1152_exp001_f0_ma1_asm1_c1(
    uint8_t output[1728], const int16_t r_f0[1152],
    const int16_t m_f0[1152], const int16_t h_official[1152],
    int16_t chunk_scratch[256]);
#endif
"""

    oracle = """#ifndef NTRUPLUS1152_EXP001_F0_MA1_ASM1_ORACLE_H
#define NTRUPLUS1152_EXP001_F0_MA1_ASM1_ORACLE_H
struct f0_ma1_tile_oracle {
  int branch, p, chunk;
  int f0[4][16];
  int h[4][16];
  int lambda[16];
};
static const struct f0_ma1_tile_oracle f0_ma1_tiles[18] = {
"""
    for tile in schedule["semantic_tiles"]:
        oracle += "  {" + f"{tile['tile']['branch']}, {tile['tile']['p']}, {tile['official_serializer_chunk']},\n"
        oracle += "   {\n" + "\n".join(
            "    {" + ",".join(map(str, plane["f0_positions_i16"])) + "},"
            for plane in tile["planes"]) + "\n   },\n"
        oracle += "   {\n" + "\n".join(
            "    {" + ",".join(map(str, plane["resident_h_official_positions_i16"])) + "},"
            for plane in tile["planes"]) + "\n   },\n"
        oracle += "   {" + ",".join(map(str, tile["planes"][0]["lambda_mod_q"])) + "}},\n"
    oracle += "};\n#endif\n"

    contract = {
        "schema": "gt-f0-ma1-asm1/v1",
        "checkpoint": "F0-MA1-ASM1",
        "boundary": "nine serializer chunks; two semantic tiles per chunk; no full normalized polynomial ABI",
        "abi": {
            "symbols": ["ntruplus1152_exp001_f0_ma1_asm1_c0",
                        "ntruplus1152_exp001_f0_ma1_asm1_c1"],
            "output": "1728 unconstrained-alignment ciphertext bytes",
            "inputs": "three non-aliasing 32-byte-aligned 1152xi16 arrays",
            "scratch": "256xi16 (512-byte) 32-byte-aligned per-chunk workspace",
        },
        "schedules": {
            "C0": "tile A complete; tile B complete; inverse project and serialize",
            "C1": "A/B h lifts and every corresponding Montgomery product chain interleaved; inverse project and serialize",
        },
        "montgomery_ledger": {
            "tiles": 18,
            "core_product_chains_per_tile": 20,
            "h_projection_lift_chains_per_tile": 4,
            "output_scale_chains_per_tile": 4,
            "total_chains_per_tile": 28,
            "core_product_chains_full": 360,
            "h_projection_lift_chains_full": 72,
            "output_scale_chains_full": 72,
            "total_chains_full": 504,
            "output_r_exponent": 0,
            "output_transform_scale": 1,
        },
        "liveness": {
            "C0_peak_ymm": 13,
            "C1_peak_ymm": 16,
            "C1_critical_phase": {
                "ymm0_3": "A/B resident r pair vectors",
                "ymm4_7": "A/B plain and wrapped accumulators",
                "ymm8_9": "A/B h operands or split temporaries",
                "ymm10_11": "A/B formed r operands",
                "ymm12_13": "A/B Montgomery results",
                "ymm14_15": "A/B Montgomery temporaries",
            },
            "spills_allowed": False,
        },
        "range_proof": {
            "source": "generated/f0-ma-schedule.json closed interval proof",
            "h_is_centered_before_every_r2_lift": True,
            "r_and_m_are_centered_on_consumption": True,
            "all_preoperations_signed_i16": True,
            "schedule_reassociation": False,
        },
        "routing": {
            "classification": "machine counts supplied by linked-object audit",
            "old_792": "semantic route slots only",
            "shared_projection_pack_between_C0_C1": True,
        },
        "alignment": {
            "entry_and_constants": 32,
            "poly_and_scratch": 32,
            "ciphertext": "unaligned vmovdqu stores",
        },
        "benchmark_authorized_after_correctness": True,
        "source_sha256": {"schedule": digest(args.schedule)},
    }

    write(args.asm, asm, args.check)
    write(args.constants, constants, args.check)
    write(args.header, header, args.check)
    write(args.oracle_header, oracle, args.check)
    write(args.contract, json.dumps(contract, indent=2, sort_keys=True) + "\n",
          args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
