#!/usr/bin/env python3
"""Replace Wave24 Dec's Basemul/InvNTT island with the Wave31 R^-1 pair."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    text = args.source.read_text(encoding="utf-8")
    text = text.replace(
        '#include "wave24.h"\n',
        '#include "wave24.h"\n#include "wave25.h"\n',
        1,
    )
    old = """\
\tgt_basemul_native_asm_avx2(m.coeffs, c.coeffs, f.coeffs);
\twave20_invntt_native_three_child_avx2(m.coeffs, m.coeffs);"""
    new = f"""\
\twave25_basemul_native_l3pair_rminus1_asm_avx2(
\t    m.coeffs, c.coeffs, f.coeffs);
\t{args.endpoint}(m.coeffs, m.coeffs);"""
    if text.count(old) != 1:
        raise RuntimeError(f"Dec island audit changed: count={text.count(old)}")
    text = text.replace(old, new, 1)
    declaration = (
        f"void {args.endpoint}(int16_t out[NTRUPLUS_N], "
        "const int16_t native[NTRUPLUS_N]);\n\n"
    )
    marker = "static inline void wave20_forward_centered("
    if marker not in text:
        raise RuntimeError("declaration marker changed")
    text = text.replace(marker, declaration + marker, 1)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
