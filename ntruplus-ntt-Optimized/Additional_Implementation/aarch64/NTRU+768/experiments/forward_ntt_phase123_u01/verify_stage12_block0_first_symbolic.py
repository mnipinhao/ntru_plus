#!/usr/bin/env python3
"""Differential oracle for the block0-first stage12 scaffold."""

from __future__ import annotations

import argparse
from pathlib import Path

from verify_u01_symbolic import ROOT, NeonInterp, extract_region, make_input, parse_hwords
from verify_stage12_row0_symbolic import parse_gt_ntt32_batch8_twiddle_mem
from verify_u01_stage12_stripe01 import (
    NTT32,
    parse_gt_ntt32_batch8_ct_stage12_twiddles,
    production_phase123_rows,
    stage12_stripe,
)


DEFAULT_SOURCE = (
    ROOT
    / "experiments/forward_ntt_phase123_u01/phase123_stage12_block0_first_allrows.sym.s"
)

ROW_SCRATCH_BASE = {"x4": 0, "x5": 512, "x6": 1024}


def expected_allrows(seed: int, zetas: list[int], twist: list[int]) -> dict[int, list[int]]:
    p00_pre, p08_norm, p08_pre = parse_gt_ntt32_batch8_ct_stage12_twiddles(NTT32)
    phase_rows = production_phase123_rows(seed, zetas, twist)
    out: dict[int, list[int]] = {}
    for row_base in ("x4", "x5", "x6"):
        row_out: dict[int, list[int]] = {}
        for stripe in range(8):
            row_out.update(
                stage12_stripe(
                    phase_rows[row_base],
                    stripe,
                    zetas[0],
                    p00_pre,
                    p08_norm,
                    p08_pre,
                )
            )
        for off, value in row_out.items():
            out[ROW_SCRATCH_BASE[row_base] + off] = value
    return out


def fused_allrows(
    seed: int,
    zetas: list[int],
    twist: list[int],
    ntt32_twiddles: list[int],
    source: Path,
) -> list[int]:
    scratch = [0] * 768
    interp = NeonInterp(
        make_input(seed),
        twist,
        zetas,
        extra_mems={"x12": ntt32_twiddles, "x13": scratch},
    )
    for reg in ("x1", "x3", "x12", "x13"):
        interp.ptr[reg] = 0
    interp.run(
        extract_region(
            source,
            "slothy_start_phase123_stage12_block0_first_allrows",
            "slothy_end_phase123_stage12_block0_first_allrows",
        )
    )
    return scratch


def load_q(mem: list[int], byte_offset: int) -> list[int]:
    idx = byte_offset // 2
    return mem[idx : idx + 8]


def compare_one(
    seed: int,
    zetas: list[int],
    twist: list[int],
    ntt32_twiddles: list[int],
    source: Path,
) -> list[str]:
    want = expected_allrows(seed, zetas, twist)
    got_mem = fused_allrows(seed, zetas, twist, ntt32_twiddles, source)
    errors: list[str] = []
    for off in sorted(want):
        got = load_q(got_mem, off)
        if got != want[off]:
            errors.append(f"seed={seed} off={off}: want={want[off]} got={got}")
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

    zetas, twist = parse_hwords(ROOT / "asm/gt/ntt/poly_ntt_body.inc")
    ntt32_twiddles = parse_gt_ntt32_batch8_twiddle_mem()
    for seed in range(args.seeds):
        errors = compare_one(seed, zetas, twist, ntt32_twiddles, source)
        if errors:
            print("phase123_stage12_block0_first_mismatches:")
            for err in errors:
                print(err)
            return 1

    print(
        f"phase123_stage12_block0_first_ok seeds={args.seeds} "
        "rows=3 outputs=96 block0_outputs=24 later_outputs=72"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
