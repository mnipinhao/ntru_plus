#!/usr/bin/env python3
"""B1-K0 and B1-D0 feasibility gates from the closed G0 leaf intervals."""

from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
G0 = HERE.parent / "gt_m5rd_fr0_range_chain_closure/build/range-chain.json"
INT16 = 32767
INT32 = (1 << 31) - 1
R = -147
Q = 3457
SQRD_SHIFT = 1 << 31
SQRD_ROUND = 1 << 30
D1_RECIP = 621199


def magnitude(interval: tuple[int, int]) -> int:
    return max(abs(interval[0]), abs(interval[1]))


def add(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    return left[0] + right[0], left[1] + right[1]


def sub(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    return left[0] - right[1], left[1] - right[0]


def mul(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    values = [x * y for x in left for y in right]
    return min(values), max(values)


def sqrdmulh_s32(value: int, constant: int) -> int:
    """Exact non-saturating case of signed 32-bit SQRDMULH."""
    return (value * constant + SQRD_ROUND) // SQRD_SHIFT


def exact_barrett_residual_range(low: int, high: int,
                                 reciprocal: int) -> dict[str, int]:
    """Exact extrema by checking every quotient-transition boundary."""
    q_low = sqrdmulh_s32(low, reciprocal)
    q_high = sqrdmulh_s32(high, reciprocal)
    minimum = 1 << 63
    maximum = -(1 << 63)
    minimum_at = maximum_at = 0

    def observe(value: int) -> None:
        nonlocal minimum, maximum, minimum_at, maximum_at
        residual = value - sqrdmulh_s32(value, reciprocal) * Q
        if residual < minimum:
            minimum, minimum_at = residual, value
        if residual > maximum:
            maximum, maximum_at = residual, value

    observe(low); observe(high)
    for quotient in range(q_low + 1, q_high + 1):
        transition = (quotient * SQRD_SHIFT - SQRD_ROUND + reciprocal - 1) // reciprocal
        if low <= transition - 1 <= high:
            observe(transition - 1)
        if low <= transition <= high:
            observe(transition)
    return {"input_low": low, "input_high": high,
            "quotient_low": q_low, "quotient_high": q_high,
            "residual_low": minimum, "residual_high": maximum,
            "minimum_at": minimum_at, "maximum_at": maximum_at}


def main() -> None:
    data = json.loads(G0.read_text(encoding="utf-8"))
    reports = data["basemul"]["reports"]
    k0 = []
    d0 = []
    for report in reports:
        operand = tuple(report["operand_interval"])
        plus = add(operand, operand)
        minus = sub(operand, operand)
        best_preadd = min(magnitude(plus), magnitude(minus))
        k0.append({"top": report["top"], "row": report["row"],
                   "column": report["column"], "operand": list(operand),
                   "plus": list(plus), "minus": list(minus),
                   "best_preadd_abs": best_preadd,
                   "int16_safe": best_preadd <= INT16})

        square = mul(operand, operand)
        cross = add(square, square)
        zeta = (int(report["zeta_mont"]), int(report["zeta_mont"]))
        # Removing the first cross reduction while retaining one final
        # Montgomery reduction requires a scale-matched direct accumulator:
        # cross*zeta_R + (a0*b0)*R.
        direct0 = add(mul(cross, zeta), mul(square, (R, R)))
        direct1 = add(mul(square, zeta), mul(add(square, square), (R, R)))
        d0.append({"top": report["top"], "row": report["row"],
                   "column": report["column"], "direct_c0": list(direct0),
                   "direct_c1": list(direct1),
                   "maximum_abs": max(magnitude(direct0), magnitude(direct1)),
                   "int32_safe": (magnitude(direct0) <= INT32 and
                                  magnitude(direct1) <= INT32)})

    groups: dict[tuple[int, int, int], list[dict[str, object]]] = defaultdict(list)
    for item in k0:
        groups[(int(item["top"]), int(item["row"]),
                int(item["column"]) // 8)].append(item)
    k1_reports = []
    for (top, row, block), lanes in sorted(groups.items()):
        assert len(lanes) == 8
        safe_lanes = sum(bool(lane["int16_safe"]) for lane in lanes)
        k1_reports.append({"top": top, "row": row, "column_block": block,
                           "safe_lanes": safe_lanes,
                           "full_vector_safe": safe_lanes == 8})

    # D1 starts after the current, required cross-term Montgomery reductions.
    # At this point each cubic component is an exact R0 int32 accumulator.
    cubic_intervals = [tuple(interval) for report in reports
                       for interval in report["accumulators"]]
    add_intervals = [add(tuple(interval), tuple(report["operand_interval"]))
                     for report in reports for interval in report["accumulators"]]
    d1_low = min(interval[0] for interval in cubic_intervals + add_intervals)
    d1_high = max(interval[1] for interval in cubic_intervals + add_intervals)
    d1_exact = exact_barrett_residual_range(d1_low, d1_high, D1_RECIP)
    quotient_product = (d1_exact["quotient_low"] * Q,
                        d1_exact["quotient_high"] * Q)
    d1_bound = max(abs(d1_exact["residual_low"]),
                   abs(d1_exact["residual_high"]))
    inverse_fixed = 3444
    inverse_bounds = {
        "input": d1_bound,
        "first_radix3_sum": 3 * d1_bound,
        "first_radix3_weighted": d1_bound + 2 * inverse_fixed,
        "second_radix3_lazy": max(3 * d1_bound + 2 * inverse_fixed,
                                  d1_bound + 4 * inverse_fixed),
        "inverse16_layers": [inverse_fixed * layer for layer in range(1, 6)],
    }
    inverse_bounds["maximum_halfword_abs"] = max(
        inverse_bounds["first_radix3_sum"],
        inverse_bounds["first_radix3_weighted"],
        inverse_bounds["second_radix3_lazy"],
        *inverse_bounds["inverse16_layers"])

    result = {
        "gate": "B1_K0_K1_D0_D1_static_feasibility",
        "source": str(G0),
        "leaf_count": len(reports),
        "K0": {
            "question": "six_product_pair_preadds_fit_signed_int16",
            "safe_leaves": sum(item["int16_safe"] for item in k0),
            "unsafe_leaves": sum(not item["int16_safe"] for item in k0),
            "maximum_best_preadd_abs": max(item["best_preadd_abs"] for item in k0),
            "status": "pass" if all(item["int16_safe"] for item in k0) else "reject_global_six_product_int16_path",
            "reports": k0,
        },
        "K1": {
            "question": "K0_safe_leaves_form_complete_eight_lane_groups",
            "full_vector_groups": sum(item["full_vector_safe"] for item in k1_reports),
            "maximum_safe_lanes_in_any_group": max(item["safe_lanes"] for item in k1_reports),
            "status": ("candidate" if any(item["full_vector_safe"] for item in k1_reports)
                       else "reject_no_complete_vector_group"),
            "reports": k1_reports,
        },
        "D0": {
            "question": "remove_initial_cross_reductions_with_int32_direct_accumulators",
            "safe_leaves": sum(item["int32_safe"] for item in d0),
            "unsafe_leaves": sum(not item["int32_safe"] for item in d0),
            "maximum_abs": max(item["maximum_abs"] for item in d0),
            "status": "pass" if all(item["int32_safe"] for item in d0) else "reject_global_int32_direct_wide_path",
            "reports": d0,
        },
        "D1": {
            "question": "final_R0_int32_accumulator_to_R0_int16_with_one_SQRDMULH_MLS",
            "reciprocal": D1_RECIP,
            "reciprocal_identity": f"{D1_RECIP}*{Q}-2^31={D1_RECIP * Q - SQRD_SHIFT}",
            "input_interval_covering_BaseMul_and_BaseMulAdd": [d1_low, d1_high],
            "exact_quotient_transition_proof": d1_exact,
            "quotient_times_q_interval": list(quotient_product),
            "mls_int32_safe": (-INT32 - 1 <= quotient_product[0] <=
                               quotient_product[1] <= INT32),
            "residual_bound": d1_bound,
            "residual_fits_int16": d1_bound <= INT16,
            "residual_within_old_G0_2205": d1_bound <= 2205,
            "exact_mod_q": True,
            "inverse_reclosure": inverse_bounds,
            "inverse_int16_safe": inverse_bounds["maximum_halfword_abs"] <= INT16,
            "status": ("pass_new_bound_requires_G0_update" if
                       d1_bound <= INT16 and
                       inverse_bounds["maximum_halfword_abs"] <= INT16
                       else "reject"),
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
