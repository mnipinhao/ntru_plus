#!/usr/bin/env python3
"""Exact interval replay for the fused FR-ISO2 inverse consumer."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from generate_tables import make_tables

Q = 3457
NEG_QINV = -12929
INPUT_BOUND = 2168
S16_MIN = -(1 << 15)
S16_MAX = (1 << 15) - 1

Interval = tuple[int, int]
maximum_halfword_abs = INPUT_BOUND
maximum_product_abs = 0


def s16(value: int) -> int:
    value &= 0xffff
    return value - 0x10000 if value >= 0x8000 else value


def montgomery(value: int, constant: int) -> int:
    product = value * constant
    quotient = s16(s16(product) * NEG_QINV)
    numerator = product + quotient * Q
    assert numerator % (1 << 16) == 0
    return numerator // (1 << 16)


def barrett(value: int, constant: int, reciprocal: int) -> int:
    product = s16(value * constant)
    doubled = 2 * value * reciprocal
    quotient = (doubled + (1 << 15)) // (1 << 16)
    result = s16(product - s16(quotient * Q))
    assert (result - value * constant) % Q == 0
    return result


def mul_interval(interval: Interval, constant: int) -> Interval:
    global maximum_halfword_abs, maximum_product_abs
    lo, hi = interval
    maximum_product_abs = max(maximum_product_abs,
                              abs(lo * constant), abs(hi * constant))
    values = [montgomery(value, constant) for value in range(lo, hi + 1)]
    result = (min(values), max(values))
    maximum_halfword_abs = max(maximum_halfword_abs,
                               abs(result[0]), abs(result[1]))
    assert S16_MIN <= result[0] <= result[1] <= S16_MAX
    return result


def barrett_interval(interval: Interval, pair: list[int]) -> Interval:
    global maximum_halfword_abs, maximum_product_abs
    lo, hi = interval
    constant, reciprocal = pair
    maximum_product_abs = max(maximum_product_abs,
                              abs(lo * constant), abs(hi * constant))
    values = [barrett(value, constant, reciprocal)
              for value in range(lo, hi + 1)]
    result = (min(values), max(values))
    maximum_halfword_abs = max(maximum_halfword_abs,
                               abs(result[0]), abs(result[1]))
    assert S16_MIN <= result[0] <= result[1] <= S16_MAX
    return result


def add(left: Interval, right: Interval) -> Interval:
    global maximum_halfword_abs
    result = (left[0] + right[0], left[1] + right[1])
    assert S16_MIN <= result[0] <= result[1] <= S16_MAX
    maximum_halfword_abs = max(maximum_halfword_abs,
                               abs(result[0]), abs(result[1]))
    return result


def sub(left: Interval, right: Interval) -> Interval:
    return add(left, (-right[1], -right[0]))


def b3_inverse(x0: Interval, x1: Interval,
               x2: Interval) -> list[Interval]:
    return [
        add(add(x0, x1), x2),
        add(x0, add(mul_interval(x1, 1033), mul_interval(x2, -886))),
        add(x0, add(mul_interval(x1, -886), mul_interval(x2, 1033))),
    ]


def inverse9(source: list[Interval], constants: list[int]) -> list[Interval]:
    g0 = b3_inverse(source[0], source[3], source[6])
    g1 = b3_inverse(source[1], source[4], source[7])
    g2 = b3_inverse(source[8], source[2], source[5])
    a = b3_inverse(g0[0], g1[0], g2[0])
    b = b3_inverse(g0[1], mul_interval(g1[1], 1510),
                   mul_interval(g2[1], 708))
    c = b3_inverse(g0[2], mul_interval(g1[2], 708),
                   mul_interval(g2[2], 1510))
    unscaled = [a[0], b[0], c[1], a[1], b[1], c[2], a[2], b[2], c[0]]
    return [mul_interval(unscaled[s], constants[s]) for s in range(9)]


def inverse16(values: list[Interval], stage: list[list[int]],
              final: list[int]) -> list[Interval]:
    reverse = [0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15]
    state = [(0, 0)] * 16
    for column in range(16):
        state[reverse[column]] = values[column]
    for stage_index, length in enumerate((2, 4, 8, 16)):
        half = length // 2
        for start in range(0, 16, length):
            for j in range(half):
                left = start + j
                right = left + half
                u = state[left]
                v = mul_interval(state[right], stage[stage_index][j])
                state[left] = add(u, v)
                state[right] = sub(u, v)
    return [mul_interval(state[t], final[t]) for t in range(16)]


def load_fr0_tables() -> dict[str, object]:
    script = Path(__file__).resolve().parent.parent / (
        "gt_fr0_inverse_consumer/generate_tables.py")
    spec = importlib.util.spec_from_file_location("fr0_inverse_tables", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    reference = Path(__file__).resolve().parents[8] / (
        "ntruplus-ntt-Optimized/Reference_Implementation/NTRU+864/ntt.c")
    return module.make_tables(reference)


def main() -> None:
    row_table, twist = make_tables()
    fr0 = load_fr0_tables()
    p8 = [[[(0, 0) for _ in range(16)] for _ in range(9)]
          for _ in range(2)]
    maximum_nontrivial_corrected_input_abs = 0

    for top in range(2):
        for component in range(3):
            for block in range(2):
                for lane in range(8):
                    column = 8 * block + lane
                    source = [(-INPUT_BOUND, INPUT_BOUND)] * 9
                    if component != 0:
                        for r in range(1, 9):
                            source[r] = barrett_interval(
                                source[r], row_table[component][r])
                            maximum_nontrivial_corrected_input_abs = max(
                                maximum_nontrivial_corrected_input_abs,
                                abs(source[r][0]), abs(source[r][1]))
                    constants = [twist[top][component][block][s][lane]
                                 for s in range(9)]
                    values = inverse9(source, constants)
                    for s in range(9):
                        old = p8[top][s][column]
                        p8[top][s][column] = (
                            min(old[0], values[s][0]),
                            max(old[1], values[s][1]))

    pass1_max = max(abs(x) for top in p8 for row in top
                    for interval in row for x in interval)
    transformed = [[[None for _ in range(16)] for _ in range(9)]
                   for _ in range(2)]
    for top in range(2):
        final = [fr0["inverse16_main_scale"][t][0 if top == 0 else 4]
                 for t in range(16)]
        for s in range(9):
            transformed[top][s] = inverse16(
                p8[top][s], fr0["inverse16_stage"], final)
    inverse16_max = max(abs(x) for top in transformed for row in top
                        for interval in row for x in interval)
    outputs = []
    for s in range(9):
        for t in range(16):
            a = transformed[0][s][t]
            b = transformed[1][s][t]
            high = mul_interval(sub(b, a), fr0["delta_inv_mont"])
            low = sub(a, mul_interval(high, fr0["alpha_mont"]))
            outputs.extend((low, high))
    output_max = max(abs(x) for interval in outputs for x in interval)

    print(json.dumps({
        "gate": "gt864_friso2_direct_inverse_range",
        "status": "pass",
        "input_contract": [-INPUT_BOUND, INPUT_BOUND],
        "maximum_nontrivial_corrected_input_abs":
            maximum_nontrivial_corrected_input_abs,
        "inverse9_p8_max_abs": pass1_max,
        "inverse16_scaled_top_max_abs": inverse16_max,
        "final_output_max_abs": output_max,
        "maximum_halfword_abs_any_stage": maximum_halfword_abs,
        "maximum_widened_known_product_abs": maximum_product_abs,
        "all_halfword_add_sub_fit_int16": True,
        "all_widened_products_fit_int32": maximum_product_abs < (1 << 31),
        "coefficient_conversion_passes": 0,
        "production_linked": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
