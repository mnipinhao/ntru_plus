#!/usr/bin/env python3
"""Generate the complete wire-monotone scale-1 encapsulation overlay."""

from __future__ import annotations

import argparse
from pathlib import Path


def replace_once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"expected exactly one occurrence of: {old!r}")
    return text.replace(old, new, 1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    text = args.source.read_text(encoding="utf-8")
    if not text.startswith("/* Generated cumulative overlay:"):
        raise SystemExit("source is not the frozen cumulative KEM overlay")
    text = replace_once(
        text,
        '#include "gt9x16-prod3-ma2-qorder-natural-asm.h"\n'
        '#include "gt9x16-prod3-cumulative-ma2.h"',
        '#include "wire-monotone-kem.h"',
    )
    text = replace_once(
        text,
        "    poly h, r, m, r_f0, m_f0;\n    poly c_f0;",
        "    poly r, m, r_f0, m_f0;\n    poly c_f0;\n    int result;",
    )
    invalid_prefix = """    if(poly_frombytes(&h, pk))
    {
        for (size_t i = 0; i < NTRUPLUS_CIPHERTEXTBYTES; i++)
            ct[i] = 0;
        secure_clear(ss, NTRUPLUS_SSBYTES);

        return 1;
    }

"""
    text = replace_once(text, invalid_prefix, "")
    if text.count(
        "ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta("
    ) != 2:
        raise SystemExit("cumulative caller no longer has exactly two forwards")
    text = text.replace(
        "ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta(",
        "ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(",
    )
    text = replace_once(
        text,
        "ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q(ct, r_f0.coeffs);",
        "ntruplus1152_exp001_direct_serializer_wire(ct, r_f0.coeffs);",
    )
    text = replace_once(
        text,
        "    /* r has two consumers: H1 serializes the MA2-native planes directly. */",
        "    /* r has two consumers: serialize the wire-native planes directly. */",
    )
    old_tail = """    ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4(
        c_f0.coeffs, r_f0.coeffs, m_f0.coeffs, h.coeffs);
    ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q(
        ct, c_f0.coeffs);

    for (size_t i = 0; i < NTRUPLUS_SSBYTES; i++)
        ss[i] = buf[i];
"""
    new_tail = """    result = ntruplus1152_exp001_encap_h4_m3b_exact_egress_wire(
        ct, pk, r_f0.coeffs, m_f0.coeffs, c_f0.coeffs);
    if (result) {
        for (size_t i = 0; i < NTRUPLUS_CIPHERTEXTBYTES; i++)
            ct[i] = 0;
        secure_clear(ss, NTRUPLUS_SSBYTES);
    } else {
        for (size_t i = 0; i < NTRUPLUS_SSBYTES; i++)
            ss[i] = buf[i];
    }
"""
    text = replace_once(text, old_tail, new_tail)
    text = replace_once(
        text,
        "    secure_clear(&c_f0, sizeof c_f0);\n\n    return 0;",
        "    secure_clear(&c_f0, sizeof c_f0);\n\n    return result;",
    )
    lines = text.splitlines()
    lines[0] = (
        "/* Generated cumulative overlay: wire-monotone scale-1 lazy PROD3, "
        "direct r serializer, streaming H3/MA2, and exact H4 egress. */"
    )
    rendered = "\n".join(line.rstrip() for line in lines) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"generated file is stale: {args.output}")
    else:
        args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
