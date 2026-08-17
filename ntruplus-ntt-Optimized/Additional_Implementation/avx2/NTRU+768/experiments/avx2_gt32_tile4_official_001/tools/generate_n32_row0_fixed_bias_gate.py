#!/usr/bin/env python3
"""Test one-instruction, lane-wise fixed-kq repair of conjugated row 0."""

from __future__ import annotations

import functools
import json

import generate_n32_bm_inv_joint_range_gate as joint_range
import generate_tile4 as gt


OUT = gt.GENERATED / "tile4_n32_row0_fixed_bias_gate.json"
INT16_LIMIT = 32767


Interval = tuple[int, int]


def add(left: Interval, right: Interval) -> Interval:
    return left[0] + right[0], left[1] + right[1]


def sub(left: Interval, right: Interval) -> Interval:
    return left[0] - right[1], left[1] - right[0]


def peak(interval: Interval) -> int:
    return max(abs(interval[0]), abs(interval[1]))


@functools.lru_cache(maxsize=None)
def mont_interval(low: int, high: int, factor: int) -> Interval:
    values = [gt.montgomery_fixed(value, factor)
              for value in range(low, high + 1)]
    return min(values), max(values)


def raw_top_interval(branch: int) -> Interval:
    values = []
    for low in range(-3, 5):
        for high in range(-3, 5):
            raw = -722 * high
            values.append(low + raw if branch == 0 else low + high - raw)
    return min(values), max(values)


def branch_rows(branch: int) -> tuple[list[list[Interval]], list[int]]:
    scale = gt.BRANCH_SCALE[branch]
    residual = [
        [pow(scale, -((64 * row + 33 * q) % 96), gt.Q)
         for q in range(32)]
        for row in range(3)
    ]
    initial = raw_top_interval(branch)
    rows = [[[initial for _degree in range(4)] for _q in range(32)]
            for _row in range(3)]
    for stage in range(1, 6):
        distance = 32 >> stage
        next_residual = [row[:] for row in residual]
        next_rows = [[lane[:] for lane in row] for row in rows]
        for row in range(3):
            for group in range(0, 32, 2 * distance):
                zeta = pow(gt.OMEGA32, gt.forward_power(stage, group), gt.Q)
                for lane in range(distance):
                    low_q = group + lane
                    high_q = low_q + distance
                    normal = (zeta * residual[row][high_q] *
                              pow(residual[row][low_q], -1, gt.Q)) % gt.Q
                    factor = gt.centered(normal * gt.R)
                    for degree in range(4):
                        low_value = rows[row][low_q][degree]
                        high_value = rows[row][high_q][degree]
                        product = mont_interval(*high_value, factor)
                        next_rows[row][low_q][degree] = add(low_value, product)
                        next_rows[row][high_q][degree] = sub(low_value, product)
                    next_residual[row][high_q] = residual[row][low_q]
        rows = next_rows
        residual = next_residual
    row_residual = []
    for row in range(3):
        assert len(set(residual[row])) == 1
        row_residual.append(gt.centered(residual[row][0] * gt.R))
    assert row_residual[0] == gt.centered(gt.R)
    return rows, row_residual


def best_fixed_bias(interval: Interval) -> tuple[int, Interval]:
    midpoint = (interval[0] + interval[1]) / 2.0
    center = round(midpoint / gt.Q)
    choices = []
    for k in range(center - 3, center + 4):
        shifted = interval[0] - k * gt.Q, interval[1] - k * gt.Q
        choices.append((peak(shifted), abs(k), k, shifted))
    _, _, k, shifted = min(choices)
    return k, shifted


def main() -> None:
    branch_records = []
    output_bounds: list[list[int]] = []
    all_intermediate_safe = True
    for branch in range(2):
        rows, residual = branch_rows(branch)
        lane_records = []
        repaired_row0: list[list[Interval]] = []
        for q in range(32):
            repaired_q = []
            for degree in range(4):
                original = rows[0][q][degree]
                k, repaired = best_fixed_bias(original)
                repaired_q.append(repaired)
                lane_records.append({
                    "physical_q": q,
                    "degree": degree,
                    "raw_interval": list(original),
                    "raw_width": original[1] - original[0],
                    "k": k,
                    "bias_kq": k * gt.Q,
                    "repaired_interval": list(repaired),
                    "repaired_abs_bound": peak(repaired),
                })
            repaired_row0.append(repaired_q)

        maxima = [0, 0, 0]
        worst_internal = 0
        for q in range(32):
            for degree in range(4):
                row0 = repaired_row0[q][degree]
                row1 = mont_interval(*rows[1][q][degree], residual[1])
                row2 = mont_interval(*rows[2][q][degree], residual[2])
                difference = sub(row1, row2)
                omega = mont_interval(*difference, -886)
                sum01 = add(row0, row1)
                y0 = add(sum01, row2)
                base1 = sub(row0, row2)
                y1 = add(base1, omega)
                base2 = sub(row0, row1)
                y2 = sub(base2, omega)
                intermediates = (row0, row1, row2, difference, omega,
                                 sum01, y0, base1, y1, base2, y2)
                local_internal = max(peak(value) for value in intermediates)
                worst_internal = max(worst_internal, local_internal)
                all_intermediate_safe &= local_internal <= INT16_LIMIT
                for output, value in enumerate((y0, y1, y2)):
                    maxima[output] = max(maxima[output], peak(value))
        output_bounds.append(maxima)
        branch_records.append({
            "branch": branch,
            "raw_top_interval": list(raw_top_interval(branch)),
            "row_residual_montgomery_factors": residual,
            "lanes": lane_records,
            "distinct_k": sorted(set(record["k"] for record in lane_records)),
            "maximum_repaired_row0_abs_bound": max(
                record["repaired_abs_bound"] for record in lane_records),
            "DFT3_output_abs_bounds": maxima,
            "DFT3_worst_intermediate_abs_bound": worst_internal,
        })

    print("fixed-bias DFT output bounds", output_bounds, flush=True)
    print("fixed-bias DFT int16 safe", all_intermediate_safe, flush=True)
    # The full R1-U/inverse proof is intentionally conditional: if the
    # Forward DFT itself overflows, fixed bias is already eliminated and the
    # much more expensive downstream enumeration provides no new evidence.
    maximum_forward_output = max(max(row) for row in output_bounds)
    within_b3_contract = maximum_forward_output <= 10788
    if all_intermediate_safe and within_b3_contract:
        intervals, r1u = joint_range.derive_r1u_intervals(output_bounds)
        inverse = joint_range.prove_inverse(intervals)
        inverse_safe = inverse["all_frontiers_signed_int16_safe"]
    else:
        r1u = {"maximum_output_abs_bound": None}
        inverse = None
        inverse_safe = False
    composable = all_intermediate_safe and within_b3_contract and inverse_safe
    current_instructions = 16 * 3
    candidate_instructions = 16
    result = {
        "schema": "ntruplus768-gt32-n32-row0-fixed-bias-gate-v1",
        "experiment": "GT-N32-ROW0-FIXED-BIAS-017",
        "question": (
            "Can each typed row-0 packet replace data-dependent center10 "
            "with one fixed lane-wise subtraction x-kq?"
        ),
        "method": (
            "Exact signed-word Montgomery enumeration over conservative "
            "per-lane intervals from small input [-3,4], followed by exact "
            "interval DFT3 and existing R1-U/native-inverse proof"
        ),
        "branches": branch_records,
        "output_abs_bounds_by_branch_k3": output_bounds,
        "maximum_forward_output_abs_bound": maximum_forward_output,
        "within_existing_B3_10788_contract": within_b3_contract,
        "R1U_max_abs_bound": r1u["maximum_output_abs_bound"],
        "inverse": None if inverse is None else {
            "IDFT3_internal_abs_bound": inverse[
                "global_IDFT3_internal_addsub_abs_bound"],
            "IDFT3_output_abs_bound": inverse[
                "global_IDFT3_output_abs_bound"],
            "stage_abs_bounds": [record["max_output_abs_bound"]
                                 for record in inverse[
                                     "global_stage_output_abs_bounds"]],
            "all_frontiers_signed_int16_safe": inverse_safe,
        },
        "static_cost": {
            "current_center10_instructions": current_instructions,
            "fixed_bias_instructions": candidate_instructions,
            "instructions_removed": current_instructions - candidate_instructions,
        },
        "decision": (
            "pass-emit-fixed-bias-assembly" if composable
            else "static-stop-fixed-bias-does-not-close-BM-inverse-range"
        ),
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUT)
    print("output bounds", output_bounds)
    print("R1U", r1u["maximum_output_abs_bound"])
    print("inverse safe", inverse_safe)
    print(result["decision"])


if __name__ == "__main__":
    main()
