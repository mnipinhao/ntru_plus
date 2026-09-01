#!/usr/bin/env python3
"""Prove FR-0 BaseMul/BaseMulAdd accumulator and scale bounds."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

Q = 3457
NEG_QINV = -12929
R = -147
RSQ = 867
ZETA_BOUND = 1728
INT32_MIN = -(1 << 31)
INT32_MAX = (1 << 31) - 1

Interval = tuple[int, int]


def wrap16(value: int) -> int:
    value &= 0xFFFF
    return value - 0x10000 if value >= 0x8000 else value


def add(*values: Interval) -> Interval:
    return (sum(value[0] for value in values),
            sum(value[1] for value in values))


def multiply(left: Interval, right: Interval) -> Interval:
    products = [x * y for x in left for y in right]
    return min(products), max(products)


def ceil_div(value: int, divisor: int) -> int:
    return -((-value) // divisor)


def montgomery_bound(value: Interval) -> Interval:
    # quotient=int16(low16(value)*-qinv), hence q in [-32768,32767].
    numerator = (value[0] - 32768 * Q, value[1] + 32767 * Q)
    return numerator[0] // 65536, ceil_div(numerator[1], 65536)


def load_fr0_bound() -> tuple[int, dict[str, object]]:
    path = (Path(__file__).resolve().parents[1] /
            "gt_fr0_kernel_realization/prove_ranges.py")
    spec = importlib.util.spec_from_file_location("m5a_range_contract", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    analyzer, outputs = module.analyze((-8874, 8874))
    bound = max(abs(endpoint) for interval in outputs for endpoint in interval)
    return bound, {
        "m5b_ntt16_input": [-8874, 8874],
        "m5a_maximum_any_step": module.maximum_abs(analyzer),
        "m5a_output_union": [min(x[0] for x in outputs),
                             max(x[1] for x in outputs)],
    }


def main() -> None:
    operand_bound, derivation = load_fr0_bound()
    assert operand_bound == 24438
    operand = (-operand_bound, operand_bound)
    product1 = multiply(operand, operand)
    product2 = add(product1, product1)
    product3 = add(product1, product1, product1)
    assert product3[0] >= INT32_MIN and product3[1] <= INT32_MAX

    first_cross = montgomery_bound(product2)
    first_square = montgomery_bound(product1)
    zeta = (-ZETA_BOUND, ZETA_BOUND)
    accum0 = add(multiply(first_cross, zeta), product1)
    accum1 = add(multiply(first_square, zeta), product1, product1)
    accum2 = product3
    for interval in (accum0, accum1, accum2):
        assert interval[0] >= INT32_MIN and interval[1] <= INT32_MAX
    reduced = [montgomery_bound(x) for x in (accum0, accum1, accum2)]

    product_outputs = []
    add_outputs = []
    final_accumulators = []
    for value in reduced:
        product_accum = multiply(value, (RSQ, RSQ))
        add_accum = add(product_accum, multiply(operand, (R, R)))
        final_accumulators.extend((product_accum, add_accum))
        product_outputs.append(montgomery_bound(product_accum))
        add_outputs.append(montgomery_bound(add_accum))
    assert all(interval[0] >= INT32_MIN and interval[1] <= INT32_MAX
               for interval in final_accumulators)
    assert max(abs(x) for interval in product_outputs for x in interval) == 2114
    assert max(abs(x) for interval in add_outputs for x in interval) == 2168

    # Exhaust every possible low half of the Neon -qinv/add reduction.
    low_half_checks = 0
    for low_unsigned in range(1 << 16):
        low = wrap16(low_unsigned)
        quotient = wrap16(low * NEG_QINV)
        assert (low_unsigned + quotient * Q) % (1 << 16) == 0
        low_half_checks += 1

    all_accumulators = [product1, product2, product3, accum0, accum1,
                        accum2, *final_accumulators]
    largest_accumulator = max(abs(x) for interval in all_accumulators
                              for x in interval)
    print(json.dumps({
        "gate": "gt864_fr0_basemul_range",
        "status": "pass",
        "operand_bound_derivation": derivation,
        "operand_bound": operand_bound,
        "scale_contract": {
            "inputs": "R0",
            "zeta": "R1",
            "cross_reduction": "R-1",
            "post_zeta_reduction": "R-1",
            "final_RSQ_reduction": "R0",
            "addend": "R0_times_R_inside_final_reduction",
        },
        "accumulator_bounds": {
            "one_product": list(product1),
            "two_products": list(product2),
            "three_products": list(product3),
            "coefficient_0_after_zeta": list(accum0),
            "coefficient_1_after_zeta": list(accum1),
            "coefficient_2": list(accum2),
            "largest_abs": largest_accumulator,
            "all_fit_signed_int32": True,
        },
        "intermediate_R_minus_1_bounds": [list(x) for x in reduced],
        "basemul_R0_output_bounds": [list(x) for x in product_outputs],
        "basemul_add_R0_output_bounds": [list(x) for x in add_outputs],
        "maximum_abs_basemul_output": 2114,
        "maximum_abs_basemul_add_output": 2168,
        "montgomery_low_half_checks": low_half_checks,
        "intentional_low_half_wrap": True,
        "production_linked": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
