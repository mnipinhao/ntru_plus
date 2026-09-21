#!/usr/bin/env python3
"""Schedule Official level-6 constants ahead of its independent shuffle."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "upstream/supercop-avx2/ntt.s").read_text()
NAME = "ntruplus768_officialopt_ntt_early_const"


def generate() -> str:
    old = ("#level6\n#shuffle\n")
    new = ("#level6\n#zetas: loaded before independent lane routing\n"
           "vmovdqa 1168(%rdx), %ymm15 #zetaqinv\n"
           "vmovdqa 1200(%rdx), %ymm2  #zeta\n\n#shuffle\n")
    if SOURCE.count(old) != 1:
        raise ValueError("Official level-6 stage changed")
    body = SOURCE.replace(old, new)
    late = ("#zetas\nvmovdqa 1168(%rdx), %ymm15 #zetaqinv\n"
            "vmovdqa 1200(%rdx), %ymm2  #zeta\n\n#mul")
    if body.count(late) != 1:
        raise ValueError("Official level-6 constant load changed")
    body = body.replace(late, "#mul")
    body = body.replace(".global poly_ntt\npoly_ntt:",
                        f".text\n.p2align 5\n.global {NAME}\n.type {NAME},@function\n{NAME}:", 1)
    body = re.sub(r"\b(_looptop_[A-Za-z0-9_]+)\b", r"officialopt_\1", body)
    marker = ".ifndef no_gnu_stack"
    if marker not in body:
        raise ValueError("Official NTT terminal changed")
    return body.replace(marker, f".size {NAME},.-{NAME}\n\n{marker}", 1)


if __name__ == "__main__":
    (ROOT / "asm/ntruplus768_officialopt_ntt_early_const.s").write_text(generate())
    kem = (ROOT / "upstream/supercop-avx2/kem.c").read_text()
    if kem.count("poly_ntt(") < 5:
        raise ValueError("Official Forward call graph changed")
    kem = kem.replace("poly_ntt(", NAME + "(")
    kem = kem.replace("#ifdef SUPERCOP\n",
                      f"void {NAME}(poly *);\n\n#ifdef SUPERCOP\n", 1)
    (ROOT / "src/kem_forward.c").write_text(kem)
