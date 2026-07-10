#!/usr/bin/env python3
"""Differential oracle for all-row shared-prefix U23 -> stage12 scratch source."""

from __future__ import annotations

import argparse
from pathlib import Path

from verify_u01_symbolic import ROOT, NeonInterp, extract_region, make_input, parse_hwords
from verify_stage12_row0_symbolic import parse_ntt32_twiddle_mem
from verify_u01_stage12_stripe01 import (
    NTT32,
    parse_ntt32_stage12_twiddles,
    production_phase123_rows,
    stage12_stripe,
)


DEFAULT_SOURCE = (
    ROOT
    / "experiments/forward_ntt_phase123_u01/phase123_u23_stage12_allrows_scratch_stripe23.sym.s"
)


def expected_allrows(seed: int, zetas: list[int], twist: list[int]) -> dict[str, dict[int, list[int]]]:
    p00_pre, p08_norm, p08_pre = parse_ntt32_stage12_twiddles(NTT32)
    phase_rows = production_phase123_rows(seed, zetas, twist)
    out: dict[str, dict[int, list[int]]] = {}
    for row_base in ("x4", "x5", "x6"):
        row_out: dict[int, list[int]] = {}
        for stripe in (2, 3):
            row_out.update(stage12_stripe(phase_rows[row_base], stripe, zetas[0], p00_pre, p08_norm, p08_pre))
        out[row_base] = row_out
    return out


def fused_allrows(
    seed: int,
    zetas: list[int],
    twist: list[int],
    ntt32_twiddles: list[int],
    source: Path,
) -> dict[str, dict[int, list[int]]]:
    scratch = [0] * 256
    interp = NeonInterp(
        make_input(seed),
        twist,
        zetas,
        extra_mems={"x12": ntt32_twiddles, "x13": scratch},
    )
    for reg in ("x1", "x3", "x4", "x5", "x6", "x12", "x13"):
        interp.ptr[reg] = 0
    interp.run(
        extract_region(
            source,
            "slothy_start_phase123_u23_stage12_allrows_scratch_stripe23",
            "slothy_end_phase123_u23_stage12_allrows_scratch_stripe23",
        )
    )
    return {row: interp.rows[row] for row in ("x4", "x5", "x6")}


def compare_one(
    seed: int,
    zetas: list[int],
    twist: list[int],
    ntt32_twiddles: list[int],
    source: Path,
) -> list[str]:
    want = expected_allrows(seed, zetas, twist)
    got = fused_allrows(seed, zetas, twist, ntt32_twiddles, source)
    errors: list[str] = []
    for row in ("x4", "x5", "x6"):
        for off in sorted(want[row]):
            if got[row].get(off) != want[row][off]:
                errors.append(
                    f"seed={seed} row={row} off={off}: want={want[row][off]} got={got[row].get(off)}"
                )
                if len(errors) >= 16:
                    return errors
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=64)
    ap.add_argument("--source", default=str(DEFAULT_SOURCE))
    args = ap.parse_args()

    source = Path(args.source)
    if not source.is_absolute():
        source = ROOT / source

    zetas, twist = parse_hwords(ROOT / "asm/gt/ntt_gt_body.inc")
    ntt32_twiddles = parse_ntt32_twiddle_mem()
    for seed in range(args.seeds):
        errors = compare_one(seed, zetas, twist, ntt32_twiddles, source)
        if errors:
            print("phase123_u23_stage12_allrows_scratch_mismatches:")
            for err in errors:
                print(err)
            return 1

    print(f"phase123_u23_stage12_allrows_scratch_ok seeds={args.seeds} rows=3 outputs=24")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
