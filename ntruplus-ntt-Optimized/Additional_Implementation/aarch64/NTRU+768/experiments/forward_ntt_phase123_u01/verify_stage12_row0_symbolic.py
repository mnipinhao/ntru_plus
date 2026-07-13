#!/usr/bin/env python3
"""Differential oracle for the row0 U01 -> stage12 stripe01 fused source."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from verify_u01_symbolic import (
    ROOT,
    NeonInterp,
    extract_region,
    make_input,
    parse_hwords,
    s16,
)
from verify_u01_stage12_stripe01 import (
    NTT32,
    parse_gt_ntt32_batch8_ct_stage12_twiddles,
    production_phase123_rows,
    stage12_stripe,
)


DEFAULT_FUSED = ROOT / "experiments/forward_ntt_phase123_u01/phase123_u01_stage12_row0_stripe01.sym.s"


def parse_gt_ntt32_batch8_twiddle_mem() -> list[int]:
    vals: list[int] = []
    inside = False
    for raw in NTT32.read_text().splitlines():
        line = raw.split("//", 1)[0].strip()
        if line == "gt_ntt32_batch8_twiddle_vecs:":
            inside = True
            continue
        if inside and line.startswith(".unreq"):
            break
        if inside and ".hword" in line:
            vals.extend(s16(int(x, 0)) for x in re.findall(r"0x[0-9a-fA-F]+|-?\d+", line))
    if len(vals) < 32:
        raise ValueError(f"failed to parse gt_ntt32_batch8_twiddle_vecs: {len(vals)} hwords")
    return vals


def expected_row0(seed: int, zetas: list[int], twist: list[int]) -> dict[int, list[int]]:
    p00_pre, p08_norm, p08_pre = parse_gt_ntt32_batch8_ct_stage12_twiddles(NTT32)
    rows = production_phase123_rows(seed, zetas, twist)
    out: dict[int, list[int]] = {}
    for stripe in (0, 1):
        out.update(stage12_stripe(rows["x4"], stripe, zetas[0], p00_pre, p08_norm, p08_pre))
    return out


def fused_row0(seed: int, zetas: list[int], twist: list[int], ntt32_twiddles: list[int], source) -> dict[int, list[int]]:
    interp = NeonInterp(
        make_input(seed),
        twist,
        zetas,
        extra_mems={"x12": ntt32_twiddles},
    )
    interp.ptr["x1"] = 0
    interp.ptr["x3"] = 0
    interp.ptr["x4"] = 0
    interp.ptr["x12"] = 0
    interp.run(extract_region(
        source,
        "slothy_start_phase123_u01_stage12_row0_stripe01",
        "slothy_end_phase123_u01_stage12_row0_stripe01",
    ))
    return interp.rows["x4"]


def compare_one(seed: int, zetas: list[int], twist: list[int], ntt32_twiddles: list[int], source) -> list[str]:
    want = expected_row0(seed, zetas, twist)
    got = fused_row0(seed, zetas, twist, ntt32_twiddles, source)
    errors: list[str] = []
    for off in sorted(want):
        if got.get(off) != want[off]:
            errors.append(f"seed={seed} off={off}: want={want[off]} got={got.get(off)}")
            if len(errors) >= 16:
                return errors
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=64)
    ap.add_argument("--source", default=str(DEFAULT_FUSED))
    args = ap.parse_args()

    zetas, twist = parse_hwords(ROOT / "asm/gt/ntt/poly_ntt_body.inc")
    ntt32_twiddles = parse_gt_ntt32_batch8_twiddle_mem()
    source = Path(args.source)
    if not source.is_absolute():
        source = ROOT / source

    for seed in range(args.seeds):
        errors = compare_one(seed, zetas, twist, ntt32_twiddles, source)
        if errors:
            print("phase123_u01_stage12_row0_symbolic_mismatches:")
            for err in errors:
                print(err)
            return 1

    print(f"phase123_u01_stage12_row0_symbolic_ok seeds={args.seeds} outputs=8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
