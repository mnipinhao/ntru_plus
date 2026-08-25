#!/usr/bin/env python3
"""Generate the experiment KEM overlay with real MA2 encapsulation."""
from __future__ import annotations
import argparse
from pathlib import Path

def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument("--upstream", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True); p.add_argument("--check", action="store_true")
    a = p.parse_args(); text = a.upstream.read_text()
    text = text.replace('#include "randombytes.h"', '#include "randombytes.h"\n#include "f0-ma2-asm.h"\n#include "f0-official-to-f0.h"')
    text = text.replace('    poly c, h, r, m;', '    poly h, r, m, r_f0, m_f0;\n    _Alignas(32) int16_t ma2_scratch[128];')
    old = '''    poly_basemul(&c, &h, &r);
    poly_add(&c, &c, &m);
    poly_tobytes(ct, &c);'''
    new = '''    ntruplus1152_exp001_official_to_f0(r_f0.coeffs, r.coeffs);
    ntruplus1152_exp001_official_to_f0(m_f0.coeffs, m.coeffs);
    ntruplus1152_exp001_f0_ma2_full(ct, r_f0.coeffs, m_f0.coeffs,
                                    h.coeffs, ma2_scratch);'''
    if text.count(old) != 1: raise SystemExit("upstream encapsulation block changed")
    text = text.replace(old, new)
    text = text.replace('    secure_clear(&m, sizeof m);', '''    secure_clear(&m, sizeof m);
    secure_clear(&r_f0, sizeof r_f0);
    secure_clear(&m_f0, sizeof m_f0);
    secure_clear(ma2_scratch, sizeof ma2_scratch);''', 1)
    banner = "/* Generated experiment overlay: real encapsulation caller with F0-MA2. */\n"
    rendered = banner + "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
    if a.check:
        if not a.output.is_file() or a.output.read_text() != rendered:
            raise SystemExit(f"generated file is stale: {a.output}")
    else: a.output.write_text(rendered)
    return 0
if __name__ == "__main__": raise SystemExit(main())
