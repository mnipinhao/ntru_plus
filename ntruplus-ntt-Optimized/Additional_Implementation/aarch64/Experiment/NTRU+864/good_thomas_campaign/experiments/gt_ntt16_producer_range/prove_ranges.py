#!/usr/bin/env python3
"""Machine-check top split -> twisted radix-2 NTT16 -> M5A range closure."""

from __future__ import annotations

import json
import re
from pathlib import Path

Q = 3457
QINV = 12929
R = (1 << 16) % Q
THETA = 9
ALPHA = -722
ALPHA_RECIP = -6844
INPUT = (-3456, 3456)
CONSUMER_BOUND = 15752


def i16(value: int) -> int:
    value &= 0xFFFF
    return value - 0x10000 if value >= 0x8000 else value


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def sqrdmulh(left: int, right: int) -> int:
    numerator = 2 * left * right + 32768
    if numerator >= 0:
        return numerator // 65536
    return -((-numerator + 65535) // 65536)


def fixed_alpha(value: int) -> int:
    low = i16(value * ALPHA)
    quotient = sqrdmulh(value, ALPHA_RECIP)
    return i16(low - i16(quotient * Q))


def montgomery_reduce(product: int) -> int:
    quotient = i16(i16(product) * QINV)
    numerator = product - quotient * Q
    assert numerator % (1 << 16) == 0
    return numerator >> 16


def mul_interval(interval: tuple[int, int], constant: int,
                 audit: dict[str, int]) -> tuple[int, int]:
    values = []
    for value in range(interval[0], interval[1] + 1):
        product = value * constant
        output = montgomery_reduce(product)
        assert (output * R - value * constant) % Q == 0
        quotient = i16(i16(product) * QINV)
        numerator = product - quotient * Q
        audit["checks"] += 1
        audit["largest_product"] = max(audit["largest_product"], abs(product))
        audit["largest_numerator"] = max(audit["largest_numerator"],
                                         abs(numerator))
        values.append(output)
    return min(values), max(values)


def parse_tables() -> tuple[list[list[int]], list[list[int]], list[list[int]]]:
    text = Path("gt864_ntt16_tables.h").read_text()
    twist_match = re.search(
        r"gt864_ntt16_twist_mont\s*\[2\]\[16\]\s*=\s*\{(.*?)\};",
        text, re.S)
    stage_match = re.search(
        r"gt864_ntt16_stage_twiddle_mont\s*\[4\]\[8\]\s*=\s*\{(.*?)\};",
        text, re.S)
    tail_match = re.search(
        r"gt864_ntt16_tail_twist_mont\s*\[16\]\[8\]\s*=\s*\{(.*?)\};",
        text, re.S)
    assert twist_match and stage_match and tail_match
    twist_values = [int(x) for x in re.findall(r"-?\d+", twist_match.group(1))]
    stage_values = [int(x) for x in re.findall(r"-?\d+", stage_match.group(1))]
    tail_values = [int(x) for x in re.findall(r"-?\d+", tail_match.group(1))]
    assert (len(twist_values) == 32 and len(stage_values) == 32
            and len(tail_values) == 128)
    return ([twist_values[:16], twist_values[16:]],
            [stage_values[i:i + 8] for i in range(0, 32, 8)],
            [tail_values[i:i + 8] for i in range(0, 128, 8)])


def bit_reverse4(value: int) -> int:
    return int(f"{value:04b}"[::-1], 2)


def main() -> None:
    twists, stages, tail_twists = parse_tables()
    omega = pow(THETA, 54, Q)

    expected_twists = []
    for residue in (1, 5):
        zeta = pow(THETA, 9 * residue, Q)
        expected_twists.append([
            centered(pow(zeta, degree, Q) * R) for degree in range(16)
        ])
        assert pow(zeta, 16, Q) == pow(THETA, 144 * residue, Q)
    expected_stages = [[0] * 8 for _ in range(4)]
    for stage, length in enumerate((2, 4, 8, 16)):
        for j in range(length // 2):
            expected_stages[stage][j] = centered(
                pow(omega, j * 16 // length, Q) * R)
    assert twists == expected_twists
    assert tail_twists == [
        [twists[0][degree]] * 3 + [twists[1][degree]] * 3 + [0, 0]
        for degree in range(16)
    ]
    assert stages == expected_stages
    assert pow(omega, 16, Q) == 1 and pow(omega, 8, Q) != 1
    assert sorted(bit_reverse4(i) for i in range(16)) == list(range(16))

    # Exact dependency-aware top-split bounds: low is independent, while
    # high-fixed_alpha(high) must not be separated into unrelated intervals.
    high_values = range(INPUT[0], INPUT[1] + 1)
    alpha_products = [fixed_alpha(value) for value in high_values]
    beta_high_terms = [value - fixed_alpha(value) for value in high_values]
    top_bounds = [
        (INPUT[0] + min(alpha_products), INPUT[1] + max(alpha_products)),
        (INPUT[0] + min(beta_high_terms), INPUT[1] + max(beta_high_terms)),
    ]
    assert top_bounds == [(-5292, 5292), (-8450, 8450)]
    assert max(abs(x) for bound in top_bounds for x in bound) < 32768

    audit = {"checks": 0, "largest_product": 0, "largest_numerator": 0}
    top_reports = []
    global_max = 0
    for top in range(2):
        value: list[tuple[int, int] | None] = [None] * 16
        for degree in range(16):
            value[bit_reverse4(degree)] = mul_interval(
                top_bounds[top], twists[top][degree], audit)
        assert all(item is not None for item in value)
        state = [item for item in value if item is not None]
        stage_maxima = [{
            "stage": "branch_twist",
            "maximum_abs": max(abs(x) for pair in state for x in pair),
        }]
        global_max = max(global_max, stage_maxima[-1]["maximum_abs"])

        for stage, length in enumerate((2, 4, 8, 16)):
            half = length // 2
            for start in range(0, 16, length):
                for j in range(half):
                    left = start + j
                    right = left + half
                    product = mul_interval(state[right], stages[stage][j], audit)
                    u = state[left]
                    state[left] = (u[0] + product[0], u[1] + product[1])
                    state[right] = (u[0] - product[1], u[1] - product[0])
                    assert all(-32768 <= x <= 32767
                               for pair in (state[left], state[right])
                               for x in pair)
            maximum = max(abs(x) for pair in state for x in pair)
            stage_maxima.append({
                "stage": f"radix2_length_{length}",
                "maximum_abs": maximum,
            })
            global_max = max(global_max, maximum)
        top_reports.append({
            "top": top,
            "top_split_bound": list(top_bounds[top]),
            "stages": stage_maxima,
            "output_union": [min(x for pair in state for x in pair),
                             max(x for pair in state for x in pair)],
        })

    assert global_max == 8874
    assert global_max <= CONSUMER_BOUND
    assert audit["largest_product"] < (1 << 31)
    assert audit["largest_numerator"] < (1 << 31)

    print(json.dumps({
        "gate": "gt864_ntt16_producer_range",
        "status": "pass",
        "input_contract": list(INPUT),
        "input_contract_covers": ["centered_mod_q", "canonical_mod_q"],
        "top_split_semantics": "exact_mul_sqrdmulh_mls_signed_int16",
        "ntt16": {
            "root": "omega16=theta^54",
            "branch_twist": "zeta_top^t, zeta_top=theta^(9*residue)",
            "load_order": "bit_reverse_4_public_register_placement",
            "layers": [2, 4, 8, 16],
            "explicit_barrett_reductions": 0,
            "reports": top_reports,
        },
        "montgomery": {
            "congruence_checks": audit["checks"],
            "largest_abs_product": audit["largest_product"],
            "largest_abs_reduction_numerator": audit["largest_numerator"],
            "all_widened_intermediates_fit_int32": True,
        },
        "maximum_abs_any_ntt16_step": global_max,
        "m5a_consumer_bound": CONSUMER_BOUND,
        "consumer_margin": CONSUMER_BOUND - global_max,
        "all_ntt16_butterfly_add_sub_steps_no_wrap": True,
        "intentional_low_half_wrap": [
            "top_split_mul_and_mls_fixed_constant_reduction",
            "Montgomery_low_half_quotient",
        ],
        "production_linked": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
