#!/usr/bin/env python3
"""Exact interval proof for the M5D two-pass inverse schedule."""

from __future__ import annotations

import functools
import json
from pathlib import Path

from generate_tables import make_tables

Q = 3457
NEG_QINV = -12929
INPUT_BOUND = 2205
S16_MIN = -(1 << 15)
S16_MAX = (1 << 15) - 1

Interval = tuple[int, int]
maximum_pre_reduction_abs = 0
maximum_halfword_abs = INPUT_BOUND


def s16(value: int) -> int:
    value &= 0xFFFF
    return value - 0x10000 if value >= 0x8000 else value


def montgomery(value: int, constant: int) -> int:
    product = value * constant
    quotient = s16(s16(product) * NEG_QINV)
    numerator = product + quotient * Q
    assert numerator % (1 << 16) == 0
    result = numerator // (1 << 16)
    assert S16_MIN <= result <= S16_MAX
    return result


@functools.lru_cache(maxsize=None)
def mul_interval(interval: Interval, constant: int) -> Interval:
    global maximum_pre_reduction_abs, maximum_halfword_abs
    lo, hi = interval
    maximum_pre_reduction_abs = max(
        maximum_pre_reduction_abs, abs(lo * constant), abs(hi * constant))
    values = [montgomery(value, constant) for value in range(lo, hi + 1)]
    out = (min(values), max(values))
    maximum_halfword_abs = max(maximum_halfword_abs, abs(out[0]), abs(out[1]))
    return out


def add(left: Interval, right: Interval) -> Interval:
    global maximum_halfword_abs
    out = (left[0] + right[0], left[1] + right[1])
    assert S16_MIN <= out[0] <= out[1] <= S16_MAX
    maximum_halfword_abs = max(maximum_halfword_abs, abs(out[0]), abs(out[1]))
    return out


def sub(left: Interval, right: Interval) -> Interval:
    return add(left, (-right[1], -right[0]))


def b3_inverse(x0: Interval, x1: Interval, x2: Interval) -> list[Interval]:
    rho = -886
    rho2 = 1033
    o0 = add(add(x0, x1), x2)
    o1 = add(x0, add(mul_interval(x1, rho2), mul_interval(x2, rho)))
    o2 = add(x0, add(mul_interval(x1, rho), mul_interval(x2, rho2)))
    return [o0, o1, o2]


def inverse9_lane(constants: list[int]) -> list[Interval]:
    source = [(-INPUT_BOUND, INPUT_BOUND)] * 9
    g0 = b3_inverse(source[0], source[3], source[6])
    g1 = b3_inverse(source[1], source[4], source[7])
    g2 = b3_inverse(source[8], source[2], source[5])
    a = [g0[0], g1[0], g2[0]]
    b = [g0[1], mul_interval(g1[1], 1510),
         mul_interval(g2[1], 708)]
    c = [g0[2], mul_interval(g1[2], 708),
         mul_interval(g2[2], 1510)]
    a = b3_inverse(*a)
    b = b3_inverse(*b)
    c = b3_inverse(*c)
    unscaled = [a[0], b[0], c[1], a[1], b[1], c[2], a[2], b[2], c[0]]
    return [mul_interval(unscaled[s], constants[s]) for s in range(9)]


def inverse16(values: list[Interval], stage_table: list[list[int]],
              final_constants: list[int]) -> list[Interval]:
    reverse = [0,8,4,12,2,10,6,14,1,9,5,13,3,11,7,15]
    state: list[Interval] = [(0, 0)] * 16
    for column in range(16):
        state[reverse[column]] = values[column]
    for stage, length in enumerate((2, 4, 8, 16)):
        half = length // 2
        for start in range(0, 16, length):
            for j in range(half):
                left = start + j
                right = left + half
                u = state[left]
                v = mul_interval(state[right], stage_table[stage][j])
                state[left] = add(u, v)
                state[right] = sub(u, v)
    return [mul_interval(state[t], final_constants[t]) for t in range(16)]


def main() -> None:
    reference = Path(__file__).resolve().parents[8] / (
        "ntruplus-ntt-Optimized/Reference_Implementation/NTRU+864/ntt.c")
    tables = make_tables(reference)
    inverse9 = tables["inverse9"]
    p8: list[list[list[Interval]]] = [
        [[(0, 0) for _ in range(16)] for _ in range(9)] for _ in range(2)]

    for top in range(2):
        for block in range(2):
            for lane in range(8):
                column = 8 * block + lane
                constants = [inverse9[top][block][s][lane] for s in range(9)]
                outputs = inverse9_lane(constants)
                for s in range(9):
                    p8[top][s][column] = outputs[s]

    pass1_max = max(abs(value) for top in p8 for s in top for interval in s
                    for value in interval)
    top_values: list[list[list[Interval]]] = [
        [[(0, 0) for _ in range(16)] for _ in range(9)] for _ in range(2)]
    main_scale = tables["inverse16_main_scale"]
    for top in range(2):
        final = [main_scale[t][0 if top == 0 else 4] for t in range(16)]
        for s in range(9):
            top_values[top][s] = inverse16(
                p8[top][s], tables["inverse16_stage"], final)

    scaled_top_max = max(abs(value) for top in top_values for s in top
                         for interval in s for value in interval)
    output: list[Interval] = []
    delta = tables["delta_inv_mont"]
    alpha = tables["alpha_mont"]
    for s in range(9):
        for t in range(16):
            a = top_values[0][s][t]
            b = top_values[1][s][t]
            high = mul_interval(sub(b, a), delta)
            low = sub(a, mul_interval(high, alpha))
            output.extend((low, high))
    output_bound = max(abs(value) for interval in output for value in interval)

    assert pass1_max <= S16_MAX
    assert scaled_top_max <= S16_MAX
    assert output_bound <= S16_MAX
    print(json.dumps({
        "gate": "gt864_fr0_inverse_range",
        "status": "pass",
        "input_contract": [-INPUT_BOUND, INPUT_BOUND],
        "input_source": "M5C BaseMulAdd symmetric bound",
        "inverse9_p8_max_abs": pass1_max,
        "inverse16_scaled_top_max_abs": scaled_top_max,
        "final_output_max_abs": output_bound,
        "all_halfword_add_sub_fit_int16": True,
        "maximum_halfword_abs_any_stage": maximum_halfword_abs,
        "maximum_widened_known_product_abs": maximum_pre_reduction_abs,
        "all_widened_products_fit_int32": maximum_pre_reduction_abs < (1 << 31),
        "montgomery_convention": "-qinv/add",
        "algorithmic_full_buffer_load_passes": 2,
        "algorithmic_full_buffer_store_passes": 2,
        "production_linked": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
