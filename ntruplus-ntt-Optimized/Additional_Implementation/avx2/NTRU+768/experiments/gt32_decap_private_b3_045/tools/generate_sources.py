#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path

OLD_HEAD = r''' \inputb
 \inputa
 vpmullw .Ltile4_bm_qinv(%rip), %ymm1, %ymm5
 vpmullw .Ltile4_bm_qinv(%rip), %ymm2, %ymm6
 vpmullw .Ltile4_bm_qinv(%rip), %ymm3, %ymm7
 vpmullw .Ltile4_bm_qinv(%rip), %ymm4, %ymm8'''
OLD_END = r''' vzeroupper
 ret
 .size \name,.-\name
 .endm
 .p2align 5
 .macro TILE4_BASEMUL_FUNCTION'''
PRIVATE = "ntruplus768_basemul_general_m_decap_avx2"

def basemul(source: str, preload: bool) -> str:
    candidate = r''' vmovdqa .Ltile4_bm_qinv(%rip), %ymm13
 vpmullw %ymm13, %ymm1, %ymm5
 vpmullw %ymm13, %ymm2, %ymm6
 vpmullw %ymm13, %ymm3, %ymm7
 vpmullw %ymm13, %ymm4, %ymm8'''
    original = OLD_HEAD.split(r" \inputa" + "\n", 1)[1]
    head = r''' \inputb
 \inputa
.ifc \name,'''+PRIVATE+r'''
'''+(candidate if preload else original)+r'''
.else
'''+original+r'''
.endif'''
    end = r''' vzeroupper
 ret
'''
    if preload:
        end += r'''.ifc \name,'''+PRIVATE+r'''
 .fill 4,1,0x90
.endif
'''
    end += r''' .size \name,.-\name
 .endm
 .p2align 5
 .macro TILE4_BASEMUL_FUNCTION'''
    if source.count(OLD_HEAD) != 1 or source.count(OLD_END) != 1:
        raise SystemExit("basemul anchors changed")
    source = source.replace(OLD_HEAD, head).replace(OLD_END, end)
    anchor = (" TILE4_BASEMUL_B3_FUNCTION ntruplus768_basemul_general_m_avx2, "
              "TILE4_OUTPUT_SOA_LATE_RSQ,TILE4_INPUT_A_SOA,TILE4_INPUT_B_SOA")
    private = (anchor + "\n TILE4_BASEMUL_B3_FUNCTION " + PRIVATE + ", "
               "TILE4_OUTPUT_SOA_LATE_RSQ,TILE4_INPUT_A_SOA,TILE4_INPUT_B_SOA")
    if source.count(anchor) != 1: raise SystemExit("general instantiation changed")
    return source.replace(anchor, private)

def decap(source: str) -> str:
    old = "ntruplus768_basemul_general_m_avx2(scratch->aux,"
    new = "ntruplus768_basemul_general_m_decap_avx2(scratch->aux,"
    if source.count(old) != 1: raise SystemExit("decap call anchor changed")
    return source.replace(old, new)

def internal(source: str) -> str:
    anchor = '''void ntruplus768_basemul_general_m_avx2(int16_t out[NTRUPLUS_N],
	const int16_t a[NTRUPLUS_N], const int16_t b[NTRUPLUS_N]);'''
    addition = anchor + '''
void ntruplus768_basemul_general_m_decap_avx2(int16_t out[NTRUPLUS_N],
	const int16_t a[NTRUPLUS_N], const int16_t b[NTRUPLUS_N]);'''
    if source.count(anchor) != 1: raise SystemExit("internal declaration changed")
    return source.replace(anchor, addition)

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args(); a.output.mkdir(parents=True, exist_ok=True)
    base = (a.root / "basemul.s").read_text()
    (a.output / "basemul-C.s").write_text(basemul(base, False))
    (a.output / "basemul-P.s").write_text(basemul(base, True))
    (a.output / "decap.c").write_text(decap((a.root / "decap.c").read_text()))
    (a.output / "internal.h").write_text(internal((a.root / "internal.h").read_text()))

if __name__ == "__main__": main()
