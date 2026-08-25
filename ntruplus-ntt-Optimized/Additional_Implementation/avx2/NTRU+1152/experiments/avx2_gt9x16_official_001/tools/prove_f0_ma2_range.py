#!/usr/bin/env python3
"""Prove the raw-input streaming MA2 signed-i16 and direct-pack ranges."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

Q = 3457
QINV = 12929
R = 1 << 16
CORRECTION = [-1729, 1728]
TERMS = (
    (((0, 0),), ((1, 3), (2, 2), (3, 1))),
    (((0, 1), (1, 0)), ((2, 3), (3, 2))),
    (((0, 2), (1, 1), (2, 0)), ((3, 3),)),
    (((0, 3), (1, 2), (2, 1), (3, 0)), ()),
)


def signed16(value: int) -> int:
    value &= 0xffff
    return value - 0x10000 if value & 0x8000 else value


def signed_high(value: int) -> int:
    return value // R


def mul_interval(a: list[int], b: list[int]) -> list[int]:
    products = [x * y for x in a for y in b]
    return [signed_high(min(products)), signed_high(max(products))]


def mont_interval(a: list[int], b: list[int]) -> list[int]:
    high = mul_interval(a, b)
    return [high[0] - CORRECTION[1], high[1] - CORRECTION[0]]


def add(*ranges: list[int]) -> list[int]:
    return [sum(x[0] for x in ranges), sum(x[1] for x in ranges)]


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def mont_const_exact(value: int, factor: int) -> int:
    low = signed16(value * signed16(factor * QINV))
    return signed16(signed_high(value * factor) - signed_high(low * Q))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schedule", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    raw = args.schedule.read_bytes()
    schedule = json.loads(raw)

    r2 = centered(867)
    h_values = [mont_const_exact(x, r2) for x in range(Q)]
    h_range = [min(h_values), max(h_values)]
    if h_range != [-1719, 1765]:
        raise SystemExit(f"unexpected raw-h R2 range {h_range}")

    inv4 = centered(pow(4, -1, Q) * R)
    tiles = []
    global_pre = [0, 0]
    global_post = [0, 0]
    for tile in schedule["semantic_tiles"]:
        lane_proofs = []
        for lane in range(16):
            r_ranges = [plane["f0_exact_ranges_i16"][lane]
                        for plane in tile["planes"]]
            # F0(r) and F0(m) have the same exact producer envelope.
            m_ranges = r_ranges
            coefficient_proofs = []
            for coefficient, (plain_terms, wrapped_terms) in enumerate(TERMS):
                plain_products = [mont_interval(h_range, r_ranges[v])
                                  for _, v in plain_terms]
                wrapped_products = [mont_interval(h_range, r_ranges[v])
                                    for _, v in wrapped_terms]
                accumulator_steps = []
                accumulator = list(m_ranges[coefficient])
                accumulator_steps.append(list(accumulator))
                for product in plain_products:
                    accumulator = add(accumulator, product)
                    accumulator_steps.append(list(accumulator))
                wrapped_steps = []
                wrapped = [0, 0]
                for product in wrapped_products:
                    wrapped = add(wrapped, product)
                    wrapped_steps.append(list(wrapped))
                if wrapped_products:
                    factor = centered(
                        tile["planes"][coefficient]["lambda_mod_q"][lane] * R)
                    wrapped_scaled = mont_interval(wrapped, [factor, factor])
                    accumulator = add(accumulator, wrapped_scaled)
                    accumulator_steps.append(list(accumulator))
                else:
                    wrapped_scaled = [0, 0]
                all_steps = accumulator_steps + wrapped_steps
                if any(lo < -32768 or hi > 32767 for lo, hi in all_steps):
                    raise SystemExit("MA2 raw-input schedule exceeds signed i16")
                post_values = [mont_const_exact(x, inv4)
                               for x in range(accumulator[0], accumulator[1] + 1)]
                post = [min(post_values), max(post_values)]
                if not (-Q < post[0] <= post[1] < Q):
                    raise SystemExit("MA2 direct-pack range is not inside (-q,q)")
                global_pre = [min(global_pre[0], accumulator[0]),
                              max(global_pre[1], accumulator[1])]
                global_post = [min(global_post[0], post[0]),
                               max(global_post[1], post[1])]
                coefficient_proofs.append({
                    "coefficient": coefficient,
                    "plain_product_bounds": plain_products,
                    "wrapped_product_bounds": wrapped_products,
                    "wrapped_sum_steps": wrapped_steps,
                    "wrapped_after_lambda": wrapped_scaled,
                    "accumulator_steps": accumulator_steps,
                    "pre_inv4": accumulator,
                    "post_inv4": post,
                })
            lane_proofs.append({"lane": lane, "coefficients": coefficient_proofs})
        tiles.append({"tile": tile["tile"], "lanes": lane_proofs})

    report = {
        "schema": "gt-f0-ma2-range/v1", "checkpoint": "F0-MA2-RANGE",
        "method": "closed signed-integer intervals over every tile/lane with exact constant-Montgomery enumeration",
        "contracts": {
            "resident_h_input": [0, Q - 1], "resident_h_after_raw_r2": h_range,
            "f0_r": "per-lane exact ranges from f0-ma-schedule",
            "f0_m": "same per-lane exact producer ranges as f0_r",
            "montgomery_low_correction": CORRECTION,
        },
        "reduction_policy": {
            "resident_h_center_before_r2": "cosmetic; removed",
            "f0_r_center": "range-reset only; removed by this proof",
            "f0_m_center": "range-reset only; removed by this proof",
            "wrapped_sum_center": "range-reset only; removed by this proof",
            "post_inv4_barrett": "redundant because output is in (-q,q); removed",
            "post_inv4_sign_add_q": "mandatory for unsigned 12-bit serialization",
        },
        "global_pre_inv4": global_pre, "global_post_inv4": global_post,
        "all_preoperations_signed_i16": True,
        "direct_sign_pack_proved": True, "tiles": tiles,
        "schedule_sha256": hashlib.sha256(raw).hexdigest(),
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit(f"generated file is stale: {args.output}")
    else:
        args.output.write_text(rendered)
    print(f"F0-MA2 range: raw h/r/m safe, pre-inv4 {global_pre}, post-inv4 {global_post}, direct sign-pack proved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
