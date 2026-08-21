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
NEW_HEAD = r''' \inputb
 \inputa
.ifc \name,ntruplus768_basemul_scale_m_avx2
.if {scale}
 vmovdqa .Ltile4_bm_qinv(%rip), %ymm13
 vpmullw %ymm13, %ymm1, %ymm5
 vpmullw %ymm13, %ymm2, %ymm6
 vpmullw %ymm13, %ymm3, %ymm7
 vpmullw %ymm13, %ymm4, %ymm8
.else
 vpmullw .Ltile4_bm_qinv(%rip), %ymm1, %ymm5
 vpmullw .Ltile4_bm_qinv(%rip), %ymm2, %ymm6
 vpmullw .Ltile4_bm_qinv(%rip), %ymm3, %ymm7
 vpmullw .Ltile4_bm_qinv(%rip), %ymm4, %ymm8
.endif
.else
.if {general}
 vmovdqa .Ltile4_bm_qinv(%rip), %ymm13
 vpmullw %ymm13, %ymm1, %ymm5
 vpmullw %ymm13, %ymm2, %ymm6
 vpmullw %ymm13, %ymm3, %ymm7
 vpmullw %ymm13, %ymm4, %ymm8
.else
 vpmullw .Ltile4_bm_qinv(%rip), %ymm1, %ymm5
 vpmullw .Ltile4_bm_qinv(%rip), %ymm2, %ymm6
 vpmullw .Ltile4_bm_qinv(%rip), %ymm3, %ymm7
 vpmullw .Ltile4_bm_qinv(%rip), %ymm4, %ymm8
.endif
.endif'''

OLD_END = r''' vzeroupper
 ret
 .size \name,.-\name
 .endm
 .p2align 5
 .macro TILE4_BASEMUL_FUNCTION'''
NEW_END = r''' vzeroupper
 ret
.ifc \name,ntruplus768_basemul_scale_m_avx2
.if {scale}
 .fill 4,1,0x90
.endif
.else
.if {general}
 .fill 4,1,0x90
.endif
.endif
 .size \name,.-\name
 .endm
 .p2align 5
 .macro TILE4_BASEMUL_FUNCTION'''


def basemul_variant(source: str, scale: bool, general: bool) -> str:
    if source.count(OLD_HEAD) != 1 or source.count(OLD_END) != 1:
        raise SystemExit("basemul source anchors changed")
    values = {"scale": int(scale), "general": int(general)}
    return source.replace(OLD_HEAD, NEW_HEAD.format(**values)).replace(
        OLD_END, NEW_END.format(**values))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, required=True)
    p.add_argument("--decode-candidate", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=True)
    (a.output / "pack-A.s").write_text((a.root / "pack.s").read_text())
    (a.output / "pack-D.s").write_text(a.decode_candidate.read_text())
    source = (a.root / "basemul.s").read_text()
    for tag, scale, general in (("A", 0, 0), ("S", 1, 0),
                                ("G", 0, 1), ("SG", 1, 1)):
        (a.output / f"basemul-{tag}.s").write_text(
            basemul_variant(source, bool(scale), bool(general)))


if __name__ == "__main__":
    main()

