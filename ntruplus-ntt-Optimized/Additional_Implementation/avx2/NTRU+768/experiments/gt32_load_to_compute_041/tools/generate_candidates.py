#!/usr/bin/env python3
"""Generate bounded load-to-compute probes from the GT Clean sources."""

from __future__ import annotations

import argparse
from pathlib import Path


def make_pack(source: str) -> str:
    old_prologue = """ntruplus768_pack_m_lazy10788_avx2:
.Lq24_lazy_cage_begin:
 vmovdqa .Lq24_q(%rip), %ymm15
 vmovdqa .Lq24_v(%rip), %ymm13
 Q24_ENCODE_SOA_BODY"""
    new_prologue = """ntruplus768_pack_m_lazy10788_avx2:
.Lq24_lazy_cage_begin:
 vmovdqa .Lq24_q(%rip), %ymm15
 vmovdqa .Lq24_v(%rip), %ymm13
 vmovdqa .Lq24_pack_mask(%rip), %ymm12
 Q24_ENCODE_SOA_BODY"""
    if source.count(old_prologue) != 1:
        raise ValueError("Q24 production prologue anchor changed")
    source = source.replace(old_prologue, new_prologue)

    macro_begin = source.index(".macro Q24_ENCODE_CANONICAL_REG_PACKET ")
    macro_end = source.index(".endm", macro_begin)
    body = source[macro_begin:macro_end]
    if body.count("vpshufb .Lq24_pack_mask(%rip),") != 1:
        raise ValueError("Q24 canonical pack-mask anchor changed")
    body = body.replace("vpshufb .Lq24_pack_mask(%rip),", "vpshufb %ymm12,")
    source = source[:macro_begin] + body + source[macro_end:]
    return source


def make_pack_factor(source: str) -> str:
    old_prologue = """ntruplus768_pack_m_lazy10788_avx2:
.Lq24_lazy_cage_begin:
 vmovdqa .Lq24_q(%rip), %ymm15
 vmovdqa .Lq24_v(%rip), %ymm13
 Q24_ENCODE_SOA_BODY"""
    new_prologue = """ntruplus768_pack_m_lazy10788_avx2:
.Lq24_lazy_cage_begin:
 vmovdqa .Lq24_q(%rip), %ymm15
 vmovdqa .Lq24_v(%rip), %ymm13
 vmovdqa .Lq24_pair_factor(%rip), %ymm12
 Q24_ENCODE_SOA_BODY"""
    if source.count(old_prologue) != 1:
        raise ValueError("Q24 production prologue anchor changed")
    source = source.replace(old_prologue, new_prologue)
    macro_begin = source.index(".macro Q24_ENCODE_CANONICAL_REG_PACKET ")
    macro_end = source.index(".endm", macro_begin)
    body = source[macro_begin:macro_end]
    if body.count("vpmaddwd .Lq24_pair_factor(%rip),") != 1:
        raise ValueError("Q24 canonical pair-factor anchor changed")
    body = body.replace("vpmaddwd .Lq24_pair_factor(%rip),", "vpmaddwd %ymm12,")
    return source[:macro_begin] + body + source[macro_end:]


def make_decode(source: str) -> str:
    macro_begin = source.index(".macro Q24_DECODE_REG ")
    macro_end = source.index(".endm", macro_begin)
    body = source[macro_begin:macro_end]
    old = " vpshufb \\mask(%rip), \\dst, \\dst"
    new = """.ifc \\mask,.Lq24_decode_mask_0123
 vpshufb %ymm13, \\dst, \\dst
.else
 vpshufb \\mask(%rip), \\dst, \\dst
.endif"""
    if body.count(old) != 1:
        raise ValueError("Q24 decode mask anchor changed")
    source = source[:macro_begin] + body.replace(old, new) + source[macro_end:]
    old_body = """ntruplus768_unpack_m_body_avx2:
 Q24_DECODE_ZERO
 Q24_DECODE_SOA_BODY"""
    new_body = """ntruplus768_unpack_m_body_avx2:
 Q24_DECODE_ZERO
 vmovdqa .Lq24_decode_mask_0123(%rip), %ymm13
 Q24_DECODE_SOA_BODY"""
    if source.count(old_body) != 1:
        raise ValueError("Q24 decode body anchor changed")
    source = source.replace(old_body, new_body)
    old_end = """ Q24_DECODE_FINISH
 ret
 .size ntruplus768_unpack_m_body_avx2,.-ntruplus768_unpack_m_body_avx2"""
    new_end = """ Q24_DECODE_FINISH
 ret
 .fill 48,1,0x90
 .size ntruplus768_unpack_m_body_avx2,.-ntruplus768_unpack_m_body_avx2"""
    if source.count(old_end) != 1:
        raise ValueError("Q24 decode body end anchor changed")
    return source.replace(old_end, new_end)


def make_basemul(source: str) -> str:
    old = """ \\inputb
 \\inputa
 vpmullw .Ltile4_bm_qinv(%rip), %ymm1, %ymm5
 vpmullw .Ltile4_bm_qinv(%rip), %ymm2, %ymm6
 vpmullw .Ltile4_bm_qinv(%rip), %ymm3, %ymm7
 vpmullw .Ltile4_bm_qinv(%rip), %ymm4, %ymm8"""
    new = """ \\inputb
 \\inputa
 vmovdqa .Ltile4_bm_qinv(%rip), %ymm13
 vpmullw %ymm13, %ymm1, %ymm5
 vpmullw %ymm13, %ymm2, %ymm6
 vpmullw %ymm13, %ymm3, %ymm7
 vpmullw %ymm13, %ymm4, %ymm8"""
    if source.count(old) != 1:
        raise ValueError("B3 initial qinv anchor changed")
    source = source.replace(old, new)
    old_end = """ vzeroupper
 ret
 .size \\name,.-\\name
 .endm
 .p2align 5
 .macro TILE4_BASEMUL_FUNCTION"""
    new_end = """ vzeroupper
 ret
 .fill 4,1,0x90
 .size \\name,.-\\name
 .endm
 .p2align 5
 .macro TILE4_BASEMUL_FUNCTION"""
    if source.count(old_end) != 1:
        raise ValueError("B3 function end anchor changed")
    return source.replace(old_end, new_end)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack", type=Path, required=True)
    parser.add_argument("--basemul", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "pack_ltc.s").write_text(make_pack(args.pack.read_text()))
    (args.out_dir / "pack_factor_ltc.s").write_text(
        make_pack_factor(args.pack.read_text()))
    (args.out_dir / "pack_decode_ltc.s").write_text(
        make_decode(args.pack.read_text()))
    (args.out_dir / "basemul_ltc.s").write_text(make_basemul(args.basemul.read_text()))


if __name__ == "__main__":
    main()
