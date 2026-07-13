#!/usr/bin/env python3
"""Check the U01 -> NTT32 stage12 stripes0+1 handoff.

This oracle composes:

  U01(iter0), U01(iter2), U01(iter4), U01(iter6)

with the NTT32 stage12 stripe0/stripe1 arithmetic, then compares those
post-stage12 values against production Phase123 followed by the same stage12
formula.  It proves the dataflow shape before any fused assembly is written.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from verify_u01_symbolic import (
    PHASE123,
    ROOT,
    U01,
    NeonInterp,
    add_vec,
    extract_region,
    make_input,
    mul_vec,
    parse_hwords,
    s16,
    sqrdmulh_vec,
    sub_vec,
    vec,
)


NTT32 = ROOT / "asm/gt/ntt/ntt32_batch8_to_blockmajor.n1.opt.S"


def parse_gt_ntt32_batch8_ct_stage12_twiddles(path: Path) -> tuple[list[int], list[int], list[int]]:
    vals: list[int] = []
    inside = False
    for raw in path.read_text().splitlines():
        line = raw.split("//", 1)[0].strip()
        if line == "gt_ntt32_batch8_twiddle_vecs:":
            inside = True
            continue
        if inside and line.startswith(".unreq"):
            break
        if inside and ".hword" in line:
            vals.extend(s16(int(x, 0)) for x in re.findall(r"0x[0-9a-fA-F]+|-?\d+", line))

    if len(vals) < 32:
        raise ValueError(f"failed to parse NTT32 stage12 twiddles: {len(vals)} hwords")

    p00_pre = vals[8:16]
    p08_norm = vals[16:24]
    p08_pre = vals[24:32]
    return p00_pre, p08_norm, p08_pre


def reduce_identity(a: list[int], pre: int, q: int) -> list[int]:
    t = sqrdmulh_vec(a, vec([pre] * 8))
    return sub_vec(a, mul_vec(t, vec([q] * 8)))


def fqmul_lane(a: list[int], norm: int, pre: int, q: int) -> list[int]:
    t = sqrdmulh_vec(a, vec([pre] * 8))
    y = mul_vec(a, vec([norm] * 8))
    return sub_vec(y, mul_vec(t, vec([q] * 8)))


def stage12_stripe(
    row: dict[int, list[int]],
    stripe: int,
    q: int,
    p00_pre: list[int],
    p08_norm: list[int],
    p08_pre: list[int],
) -> dict[int, list[int]]:
    off0 = 16 * stripe
    off8 = 16 * (stripe + 8)
    off16 = 16 * (stripe + 16)
    off24 = 16 * (stripe + 24)

    q0 = row[off0]
    q8 = row[off8]
    q16 = row[off16]
    q24 = row[off24]

    # Production resets gt_ntt32_batch8_twiddle_vecs before every stage12 stripe and uses
    # lane 0 of the loaded twiddle vectors. The stripe number changes memory
    # offsets, not the twiddle lane.
    high_sum = reduce_identity(add_vec(q8, q24), p00_pre[0], q)
    high_diff = fqmul_lane(sub_vec(q8, q24), p08_norm[0], p08_pre[0], q)
    low_sum = add_vec(q0, q16)
    low_diff = sub_vec(q0, q16)

    return {
        off0: add_vec(low_sum, high_sum),
        off8: sub_vec(low_sum, high_sum),
        off16: add_vec(low_diff, high_diff),
        off24: sub_vec(low_diff, high_diff),
    }


def production_phase123_rows(seed: int, zetas: list[int], twist: list[int]) -> dict[str, dict[int, list[int]]]:
    input_mem = make_input(seed)
    rows = {"x4": {}, "x5": {}, "x6": {}}
    for iteration in range(8):
        prod = NeonInterp(input_mem, twist, zetas)
        prod.set_iteration(iteration)
        prod.run(extract_region(
            PHASE123,
            f"slothy_start_ntt_phase123_iter{iteration}",
            f"slothy_end_ntt_phase123_iter{iteration}",
        ))
        for row_base in rows:
            rows[row_base].update(prod.rows[row_base])
    return rows


def u01_even_phase123_rows(seed: int, zetas: list[int], twist: list[int]) -> dict[str, dict[int, list[int]]]:
    input_mem = make_input(seed)
    rows = {"x4": {}, "x5": {}, "x6": {}}
    type_for_iter = {0: "a", 2: "c", 4: "b", 6: "a"}
    for iteration, utype in type_for_iter.items():
        cand = NeonInterp(input_mem, twist, zetas)
        cand.set_iteration(iteration)
        cand.run(extract_region(
            U01,
            f"slothy_start_ntt_phase123_u01_type_{utype}",
            f"slothy_end_ntt_phase123_u01_type_{utype}",
        ))
        for row_base in rows:
            rows[row_base].update(cand.rows[row_base])
    return rows


def compare_one(seed: int, zetas: list[int], twist: list[int], p00_pre: list[int], p08_norm: list[int], p08_pre: list[int]) -> list[str]:
    errors: list[str] = []
    q = zetas[0]
    prod_rows = production_phase123_rows(seed, zetas, twist)
    cand_rows = u01_even_phase123_rows(seed, zetas, twist)

    for row_base in ("x4", "x5", "x6"):
        prod_out: dict[int, list[int]] = {}
        cand_out: dict[int, list[int]] = {}
        for stripe in (0, 1):
            prod_out.update(stage12_stripe(prod_rows[row_base], stripe, q, p00_pre, p08_norm, p08_pre))
            cand_out.update(stage12_stripe(cand_rows[row_base], stripe, q, p00_pre, p08_norm, p08_pre))

        for off in sorted(prod_out):
            got = cand_out.get(off)
            want = prod_out[off]
            if got != want:
                errors.append(
                    f"seed={seed} row={row_base} off={off}: want={want} got={got}"
                )
                if len(errors) >= 16:
                    return errors
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=64)
    args = ap.parse_args()

    zetas, twist = parse_hwords(ROOT / "asm/gt/ntt/poly_ntt_body.inc")
    p00_pre, p08_norm, p08_pre = parse_gt_ntt32_batch8_ct_stage12_twiddles(NTT32)

    for seed in range(args.seeds):
        errors = compare_one(seed, zetas, twist, p00_pre, p08_norm, p08_pre)
        if errors:
            print("phase123_u01_stage12_stripe01_mismatches:")
            for err in errors:
                print(err)
            return 1

    print(f"phase123_u01_stage12_stripe01_ok seeds={args.seeds} rows=3 stripes=2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
