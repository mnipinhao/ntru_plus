#!/usr/bin/env python3
"""Generate the frozen PROD3 Natural-Q/T0-beta/H1 encapsulation overlay."""

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
    if not text.startswith("/* Generated experiment overlay:"):
        raise SystemExit("source is not the frozen PROD3 H1 KEM overlay")
    text = replace_once(
        text,
        '#include "gt9x16-prod3-ma2-hash-h1.h"',
        '#include "gt9x16-prod3-ma2-qorder-natural-asm.h"\n'
        '#include "gt9x16-prod3-cumulative-ma2.h"',
    )
    text = replace_once(
        text,
        "    _Alignas(32) int16_t ma2_scratch[128];",
        "    poly c_f0;",
    )
    if text.count("ntruplus1152_exp001_gt9x16_prod3_aos_full(") != 2:
        raise SystemExit("frozen caller no longer has exactly two PROD3 forwards")
    text = text.replace(
        "ntruplus1152_exp001_gt9x16_prod3_aos_full(",
        "ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta(",
    )
    text = replace_once(
        text,
        "ntruplus1152_exp001_prod3_ma2_hash_h1(ct, r_f0.coeffs);",
        "ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q(ct, r_f0.coeffs);",
    )
    text = replace_once(
        text,
        "    ntruplus1152_exp001_f0_ma2_native_full(\n"
        "        ct, r_f0.coeffs, m_f0.coeffs, h.coeffs, ma2_scratch);",
        "    ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4(\n"
        "        c_f0.coeffs, r_f0.coeffs, m_f0.coeffs, h.coeffs);\n"
        "    ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q(\n"
        "        ct, c_f0.coeffs);",
    )
    text = replace_once(
        text,
        "    secure_clear(ma2_scratch, sizeof ma2_scratch);",
        "    secure_clear(&c_f0, sizeof c_f0);",
    )
    lines = text.splitlines()
    lines[0] = (
        "/* Generated cumulative overlay: PROD3 persistent-AoS, Natural-Q, "
        "T0-beta, native MA2, and direct H1. */"
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
