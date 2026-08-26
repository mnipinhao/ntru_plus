#!/usr/bin/env python3
"""Generate the experiment KEM overlay with PROD3 and native MA2 encapsulation."""
from __future__ import annotations
import argparse
import re
from pathlib import Path

def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument("--upstream", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True); p.add_argument("--check", action="store_true")
    a = p.parse_args(); text = a.upstream.read_text()
    text = text.replace(
        '#include "randombytes.h"',
        '#include "randombytes.h"\n'
        '#include "f0-ma2-asm.h"\n'
        '#include "f0_prod3_hash_bridge.h"\n'
        '#include "gt9x16_forward.h"\n'
        '#include "gt9x16_prod3_aos_full.h"')
    text = text.replace('    poly c, h, r, m;', '    poly h, r, m, r_f0, m_f0;\n    _Alignas(32) int16_t ma2_scratch[128];')
    new = '''    poly_cbd1(&r, buf + NTRUPLUS_SYMBYTES);
    ntruplus1152_exp001_top_split_small(r_f0.coeffs, r.coeffs);
    ntruplus1152_exp001_gt9x16_prod3_aos_full(r_f0.coeffs);

    /* r has two consumers: preserve Official's exact serialized hash edge. */
    ntruplus1152_exp001_prod3_hash_bytes(ct, r_f0.coeffs, &r, &m);
    hash_g(ct, ct);
    poly_sotp_encode(&m, msg, ct);
    ntruplus1152_exp001_top_split_small(m_f0.coeffs, m.coeffs);
    ntruplus1152_exp001_gt9x16_prod3_aos_full(m_f0.coeffs);

    ntruplus1152_exp001_f0_ma2_native_full(
        ct, r_f0.coeffs, m_f0.coeffs, h.coeffs, ma2_scratch);'''
    pattern = re.compile(
        r"    poly_cbd1\(&r, buf \+ NTRUPLUS_SYMBYTES\);\s*"
        r"    poly_ntt\(&r\);\s*"
        r"    poly_tobytes\(ct, &r\);\s*"
        r"    hash_g\(ct, ct\);\s*"
        r"    poly_sotp_encode\(&m, msg, ct\);\s*"
        r"    poly_ntt\(&m\);\s*"
        r"    poly_basemul\(&c, &h, &r\);\s*"
        r"    poly_add\(&c, &c, &m\);\s*"
        r"    poly_tobytes\(ct, &c\);")
    text, replacements = pattern.subn(new, text)
    if replacements != 1:
        raise SystemExit("upstream encapsulation block changed")
    text = text.replace('    secure_clear(&m, sizeof m);', '''    secure_clear(&m, sizeof m);
    secure_clear(&r_f0, sizeof r_f0);
    secure_clear(&m_f0, sizeof m_f0);
    secure_clear(ma2_scratch, sizeof ma2_scratch);''', 1)
    banner = ("/* Generated experiment overlay: PROD3 persistent-AoS "
              "encapsulation with native MA2. */\n")
    rendered = banner + "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
    if a.check:
        if not a.output.is_file() or a.output.read_text() != rendered:
            raise SystemExit(f"generated file is stale: {a.output}")
    else: a.output.write_text(rendered)
    return 0
if __name__ == "__main__": raise SystemExit(main())
