#!/usr/bin/env python3
"""Search 160-chain reduction placement for branch-local N32 Forward.

The search keeps the exact explicit-twist, DFT3-after-S3 factorization and the
current AVX2 packet granularity.  Every existing one-chain CT butterfly may
reduce either its high arm (ordinary CT) or its low arm using the exactly
equivalent output-scaled form.  No mixed-lane orientation, extra chain,
checkpoint, layout change, or consumer change is admitted.
"""

from __future__ import annotations

import functools
import itertools
import json

import generate_n32_bm_inv_joint_range_gate as joint
import generate_n32first_gate as split
import generate_tile4 as gt


OUT = gt.GENERATED / "tile4_n32_branchlocal_scale_placement_gate.json"
RAW160 = gt.GENERATED / "tile4_n32_branchlocal_raw160_gate.json"
Q = gt.Q
R = gt.R
INT32_MAX = (1 << 31) - 1

Interval = tuple[int, int]


def add(left: Interval, right: Interval) -> Interval:
    return left[0] + right[0], left[1] + right[1]


def sub(left: Interval, right: Interval) -> Interval:
    return left[0] - right[1], left[1] - right[0]


def peak(interval: Interval) -> int:
    return max(abs(interval[0]), abs(interval[1]))


@functools.lru_cache(maxsize=None)
def mont_interval(interval: Interval, factor: int) -> Interval:
    values = [gt.montgomery_fixed(value, factor)
              for value in range(interval[0], interval[1] + 1)]
    return min(values), max(values)


@functools.lru_cache(maxsize=None)
def centered_interval(interval: Interval) -> Interval:
    values = [value - ((value * 10 + (1 << 14)) >> 15) * Q
              for value in range(interval[0], interval[1] + 1)]
    return min(values), max(values)


def butterfly_pairs(stage: int) -> list[tuple[int, int]]:
    distance = 32 >> stage
    return [(group + lane, group + lane + distance)
            for group in range(0, 32, 2 * distance)
            for lane in range(distance)]


def operation_slot(stage: int, low: int) -> int:
    """Four implementable orientation decisions per pair-packed stage."""
    vector = low // 4
    if stage == 2:
        return {0: 0, 1: 1, 4: 2, 5: 3}[vector]
    if stage == 3:
        return {0: 0, 2: 1, 4: 2, 6: 3}[vector]
    if stage in (4, 5):
        return vector // 2
    raise ValueError(stage)


def orientation(mask: int, stage: int, low: int) -> str:
    bit = 4 * (stage - 2) + operation_slot(stage, low)
    return "L" if (mask >> bit) & 1 else "H"


def ordinary_twiddle(stage: int, low: int) -> int:
    distance = 32 >> stage
    group = (low // (2 * distance)) * (2 * distance)
    return pow(gt.OMEGA32, gt.forward_power(stage, group), Q)


def scale_stage(scales: list[int], stage: int, mask: int) -> list[int]:
    output = scales[:]
    for low, high in butterfly_pairs(stage):
        low_scale, high_scale = scales[low], scales[high]
        twiddle = ordinary_twiddle(stage, low)
        if orientation(mask, stage, low) == "H":
            result_scale = low_scale
        else:
            result_scale = high_scale * pow(twiddle, -1, Q) % Q
        output[low] = output[high] = result_scale
    return output


def search_scale_assignments() -> tuple[list[int], dict[str, object]]:
    viable = []
    stage_rejections = {2: 0, 3: 0, 4: 0, 5: 0}
    for mask in range(1 << 16):
        scales = [1] * 32
        last_nonordinary = None
        for stage in range(2, 6):
            scales = scale_stage(scales, stage, mask)
            if any(value != 1 for value in scales):
                last_nonordinary = stage
        if scales == [1] * 32:
            viable.append(mask)
        elif last_nonordinary is not None:
            stage_rejections[last_nonordinary] += 1
    return viable, {
        "candidate_schedules": 1 << 16,
        "decisions": "four H/L arm placements at each of S2,S3,S4,S5",
        "mixed_lane_or_pair_orientation": "excluded: would require blend/repair",
        "ordinary_e0_output_schedules": len(viable),
        "nonordinary_output_schedules": (1 << 16) - len(viable),
        "rejections_by_last_nonordinary_stage": stage_rejections,
    }


def apply_interval_stage(rows: list[list[Interval]], scales: list[int],
                         stage: int, mask: int) \
        -> tuple[list[list[Interval]], list[int], int]:
    output = [row[:] for row in rows]
    next_scales = scales[:]
    maximum = 0
    for low, high in butterfly_pairs(stage):
        low_scale, high_scale = scales[low], scales[high]
        twiddle = ordinary_twiddle(stage, low)
        arm = orientation(mask, stage, low)
        if arm == "H":
            result_scale = low_scale
            ordinary_factor = (twiddle * result_scale
                               * pow(high_scale, -1, Q)) % Q
        else:
            result_scale = high_scale * pow(twiddle, -1, Q) % Q
            ordinary_factor = result_scale * pow(low_scale, -1, Q) % Q
        factor = gt.centered(ordinary_factor * R)
        next_scales[low] = next_scales[high] = result_scale
        for row_index, row in enumerate(rows):
            if arm == "H":
                product = mont_interval(row[high], factor)
                plus, minus = add(row[low], product), sub(row[low], product)
            else:
                product = mont_interval(row[low], factor)
                plus, minus = add(product, row[high]), sub(product, row[high])
            output[row_index][low], output[row_index][high] = plus, minus
            maximum = max(maximum, peak(plus), peak(minus))
    return output, next_scales, maximum


def top_intervals() -> list[Interval]:
    records = []
    for branch in range(2):
        values = []
        for low in range(-3, 5):
            for high in range(-3, 5):
                values.append(low - 722 * high if branch == 0
                              else low + 723 * high)
        records.append((min(values), max(values)))
    return records


def evaluate_mask(mask: int, keep_intervals: bool = False) -> dict[str, object]:
    branch_records = []
    retained: dict[tuple[int, int, int, int], Interval] = {}
    for branch, scale in enumerate(gt.BRANCH_SCALE):
        initial = top_intervals()[branch]
        rows: list[list[Interval]] = []
        for row in range(3):
            row_intervals = []
            for q in range(32):
                n = (64 * row + 33 * q) % 96
                factor = gt.centered(pow(scale, -n, Q) * R)
                row_intervals.append(mont_interval(initial, factor))
            rows.append(row_intervals)
        scales = [1] * 32
        stage_bounds = []

        # S1 remains the qualified raw identity butterfly.
        s1_output = [row[:] for row in rows]
        for low, high in butterfly_pairs(1):
            for row_index, row in enumerate(rows):
                s1_output[row_index][low] = add(row[low], row[high])
                s1_output[row_index][high] = sub(row[low], row[high])
        rows = s1_output
        stage_bounds.append({"stage": 1, "arm": "raw",
                             "max_abs_bound": max(peak(x) for r in rows for x in r)})

        for stage in (2, 3):
            rows, scales, bound = apply_interval_stage(rows, scales, stage, mask)
            stage_bounds.append({"stage": stage,
                                 "orientation_bits": (mask >> (4 * (stage - 2))) & 15,
                                 "max_abs_bound": bound})

        assert all(rows[0][q] is not None for q in range(32))
        assert all(scales[q] == scales[q] for q in range(32))
        dft_rows = [[(0, 0)] * 32 for _ in range(3)]
        dft_max = 0
        for q in range(32):
            x0, x1, x2 = (rows[row][q] for row in range(3))
            difference = sub(x1, x2)
            omega = mont_interval(difference, -886)
            values = (add(add(x0, x1), x2),
                      add(sub(x0, x2), omega),
                      sub(sub(x0, x1), omega))
            for k3, value in enumerate(values):
                dft_rows[k3][q] = value
                dft_max = max(dft_max, peak(value))
        rows = dft_rows

        for stage in (4, 5):
            rows, scales, bound = apply_interval_stage(rows, scales, stage, mask)
            stage_bounds.append({"stage": stage,
                                 "orientation_bits": (mask >> (4 * (stage - 2))) & 15,
                                 "max_abs_bound": bound})
        assert scales == [1] * 32
        output_bounds = [max(peak(value) for value in row) for row in rows]
        branch_records.append({
            "branch": branch,
            "stage_bounds": stage_bounds,
            "DFT3_max_abs_bound": dft_max,
            "output_abs_bounds_by_k3": output_bounds,
            "max_output_abs_bound": max(output_bounds),
        })
        if keep_intervals:
            for k3 in range(3):
                for q in range(32):
                    for degree in range(4):
                        retained[branch, k3, q, degree] = rows[k3][q]
    result: dict[str, object] = {
        "mask_hex": f"0x{mask:04x}",
        "stage_orientation_nibbles_S2_to_S5": [
            (mask >> (4 * offset)) & 15 for offset in range(4)
        ],
        "branch_records": branch_records,
        "max_output_abs_bound": max(
            record["max_output_abs_bound"] for record in branch_records
        ),
    }
    if keep_intervals:
        result["intervals"] = retained
    return result


def candidate_transform(values: list[int], scale: int, mask: int) -> list[int]:
    rows = [[0] * 32 for _ in range(3)]
    scales = [1] * 32
    for row in range(3):
        for q in range(32):
            n = (64 * row + 33 * q) % 96
            rows[row][q] = values[32 * row + q] * pow(scale, -n, Q) % Q
    for stage in (1, 2, 3):
        output = [row[:] for row in rows]
        next_scales = scales[:]
        for low, high in butterfly_pairs(stage):
            twiddle = ordinary_twiddle(stage, low)
            arm = "H" if stage == 1 else orientation(mask, stage, low)
            dl, dh = scales[low], scales[high]
            if arm == "H":
                p = dl
                factor = twiddle * p * pow(dh, -1, Q) % Q
            else:
                p = dh * pow(twiddle, -1, Q) % Q
                factor = p * pow(dl, -1, Q) % Q
            next_scales[low] = next_scales[high] = p
            for row_index, source in enumerate(rows):
                if arm == "H":
                    product = factor * source[high] % Q
                    plus, minus = source[low] + product, source[low] - product
                else:
                    product = factor * source[low] % Q
                    plus, minus = product + source[high], product - source[high]
                output[row_index][low] = plus % Q
                output[row_index][high] = minus % Q
        rows, scales = output, next_scales
    tiles = [[0] * 32 for _ in range(3)]
    for q in range(32):
        assert len({scales[q] for _ in range(3)}) == 1
        column = split.dft3([rows[row][q] for row in range(3)])
        for k3 in range(3):
            tiles[k3][q] = column[k3]
    rows = tiles
    for stage in (4, 5):
        output = [row[:] for row in rows]
        next_scales = scales[:]
        for low, high in butterfly_pairs(stage):
            twiddle = ordinary_twiddle(stage, low)
            arm = orientation(mask, stage, low)
            dl, dh = scales[low], scales[high]
            if arm == "H":
                p = dl
                factor = twiddle * p * pow(dh, -1, Q) % Q
            else:
                p = dh * pow(twiddle, -1, Q) % Q
                factor = p * pow(dl, -1, Q) % Q
            next_scales[low] = next_scales[high] = p
            for row_index, source in enumerate(rows):
                product = factor * source[high if arm == "H" else low] % Q
                other = source[low if arm == "H" else high]
                output[row_index][low] = (other + product) % Q
                output[row_index][high] = (other - product) % Q
        rows, scales = output, next_scales
    assert scales == [1] * 32
    return [value for row in rows for value in row]


def exact_semantic_proof(masks: list[int]) -> dict[str, object]:
    checked = 0
    for mask in masks:
        for scale in gt.BRANCH_SCALE:
            for basis in range(96):
                vector = [0] * 96
                vector[basis] = 1
                assert candidate_transform(vector, scale, mask) == \
                    split.current_transform(vector, scale)
                checked += 1
    return {
        "eligible_schedules_checked": len(masks),
        "basis_vectors_checked": checked,
        "exact_matrix_equality": True,
    }


def asymmetric_consumer_probe(intervals: dict[tuple[int, int, int, int], Interval]) \
        -> dict[str, object]:
    def idft_internal_bound(r1u: dict[tuple[int, int, int, int], list[int]]) -> int:
        maximum = 0
        for branch in range(2):
            for q in range(32):
                for degree in range(4):
                    r0, r1, r2 = (r1u[branch, k3, q, degree]
                                  for k3 in range(3))
                    internal = (add(tuple(r1), tuple(r2)),
                                sub(tuple(r1), tuple(r2)),
                                sub(tuple(r0), tuple(r1)),
                                sub(tuple(r0), tuple(r2)))
                    maximum = max(maximum, *(peak(value) for value in internal))
        return maximum

    packet_repairs: set[tuple[int, int, int]] = set()
    raw_records = []
    for branch in range(2):
        for k3 in range(3):
            for q in range(32):
                bound = max(peak(intervals[branch, k3, q, degree])
                            for degree in range(4))
                lambda_bound = gt.product_bound(
                    bound, [gt.lambda_montgomery(k3, q, branch)])
                raw_bounds = (bound * bound + 3 * bound * lambda_bound,
                              2 * bound * bound + 2 * bound * lambda_bound,
                              3 * bound * bound + bound * lambda_bound,
                              4 * bound * bound)
                unsafe = max(raw_bounds) > INT32_MAX
                if unsafe:
                    packet_repairs.add((branch, k3, q // 4))
                raw_records.append({"branch": branch, "k3": k3, "q": q,
                                    "input_abs_bound": bound,
                                    "max_raw_accumulator_abs_bound": max(raw_bounds),
                                    "signed32_safe": not unsafe})

    repaired_intervals = {}
    r1u_intervals = {}
    max_accumulator = 0
    for branch in range(2):
        for k3 in range(3):
            for q in range(32):
                repair_a = (branch, k3, q // 4) in packet_repairs
                a_bounds = []
                b_bounds = []
                for degree in range(4):
                    source = intervals[branch, k3, q, degree]
                    a = centered_interval(source) if repair_a else source
                    repaired_intervals[branch, k3, q, degree] = a
                    a_bounds.append(peak(a))
                    b_bounds.append(peak(source))
                a_bound, b_bound = max(a_bounds), max(b_bounds)
                lambda_b = gt.product_bound(
                    b_bound, [gt.lambda_montgomery(k3, q, branch)])
                raw_bounds = (a_bound * b_bound + 3 * a_bound * lambda_b,
                              2 * a_bound * b_bound + 2 * a_bound * lambda_b,
                              3 * a_bound * b_bound + a_bound * lambda_b,
                              4 * a_bound * b_bound)
                max_accumulator = max(max_accumulator, max(raw_bounds))
                for degree, raw_bound in enumerate(raw_bounds):
                    r1u_intervals[branch, k3, q, degree] = list(
                        joint.reducer_interval(raw_bound))
    accumulator_safe = max_accumulator <= INT32_MAX
    quick_internal = (idft_internal_bound(r1u_intervals)
                      if accumulator_safe else None)
    inverse = (joint.prove_inverse(r1u_intervals)
               if quick_internal is not None and quick_internal <= 32767
               else None)

    # Exhaust all six branch/k3 group choices for centering operand A.  One
    # group is eight physical YMM, so this is a useful lower-resolution bound
    # on any packet-selective consumer contract without searching 2^48 masks.
    required_group_mask = 0
    for branch, k3, _packet in packet_repairs:
        required_group_mask |= 1 << (3 * branch + k3)
    candidate_group_masks = [
        mask for mask in range(1 << 6)
        if mask & required_group_mask == required_group_mask
    ]
    group_schedules = []
    for group_mask in candidate_group_masks:
        group_r1u = {}
        group_max_accumulator = 0
        for branch in range(2):
            for k3 in range(3):
                repair_group = bool(group_mask & (1 << (3 * branch + k3)))
                for q in range(32):
                    a_bounds, b_bounds = [], []
                    for degree in range(4):
                        source = intervals[branch, k3, q, degree]
                        operand_a = (centered_interval(source)
                                     if repair_group else source)
                        a_bounds.append(peak(operand_a))
                        b_bounds.append(peak(source))
                    a_bound, b_bound = max(a_bounds), max(b_bounds)
                    lambda_b = gt.product_bound(
                        b_bound, [gt.lambda_montgomery(k3, q, branch)])
                    raw_bounds = (
                        a_bound * b_bound + 3 * a_bound * lambda_b,
                        2 * a_bound * b_bound + 2 * a_bound * lambda_b,
                        3 * a_bound * b_bound + a_bound * lambda_b,
                        4 * a_bound * b_bound,
                    )
                    group_max_accumulator = max(group_max_accumulator,
                                                max(raw_bounds))
                    for degree, raw_bound in enumerate(raw_bounds):
                        group_r1u[branch, k3, q, degree] = list(
                            joint.reducer_interval(raw_bound))
        group_accumulator_safe = group_max_accumulator <= INT32_MAX
        group_internal = (idft_internal_bound(group_r1u)
                          if group_accumulator_safe else None)
        group_inverse = (joint.prove_inverse(group_r1u)
                         if group_internal is not None
                         and group_internal <= 32767 else None)
        group_schedules.append({
            "group_mask_hex": f"0x{group_mask:02x}",
            "repaired_branch_k3_groups": group_mask.bit_count(),
            "repaired_physical_vectors": 8 * group_mask.bit_count(),
            "center10_instructions": 24 * group_mask.bit_count(),
            "maximum_raw_accumulator_abs_bound": group_max_accumulator,
            "signed32_safe": group_accumulator_safe,
            "IDFT3_internal_abs_bound": group_internal,
            "inverse_safe": bool(
                group_inverse is not None
                and group_inverse["all_frontiers_signed_int16_safe"]),
            "inverse_terminal_abs_bound": (
                None if group_inverse is None
                else group_inverse["global_terminal_abs_bound"]),
        })
    passing_groups = [record for record in group_schedules
                      if record["signed32_safe"] and record["inverse_safe"]]
    passing_groups.sort(key=lambda record: (
        record["center10_instructions"], record["group_mask_hex"]))
    return {
        "raw_x_raw": {
            "records": raw_records,
            "unsafe_q_count": sum(not record["signed32_safe"] for record in raw_records),
        },
        "selective_raw_x_centered": {
            "repaired_operand": "A only",
            "repaired_physical_vectors": len(packet_repairs),
            "total_physical_vectors_per_operand": 48,
            "center10_instructions": 3 * len(packet_repairs),
            "packet_repairs": [list(record) for record in sorted(packet_repairs)],
            "maximum_raw_accumulator_abs_bound": max_accumulator,
            "signed32_safe": accumulator_safe,
            "IDFT3_internal_abs_bound": quick_internal,
            "existing_inverse_proof": None if inverse is None else {
                "all_frontiers_signed_int16_safe": inverse[
                    "all_frontiers_signed_int16_safe"],
                "IDFT3_internal_abs_bound": inverse[
                    "global_IDFT3_internal_addsub_abs_bound"],
                "terminal_abs_bound": inverse["global_terminal_abs_bound"],
            },
        },
        "six_group_exhaustive_search": {
            "candidate_masks": 64,
            "accumulator_pruned_masks": 64 - len(candidate_group_masks),
            "inverse_masks_evaluated": len(candidate_group_masks),
            "required_group_mask_hex": f"0x{required_group_mask:02x}",
            "group_definition": "one branch/k3 plane = eight physical YMM",
            "passing_schedule_count": len(passing_groups),
            "minimum_passing_schedule": (
                passing_groups[0] if passing_groups else None),
            "schedules": group_schedules,
        },
        "two_sided_full_center_control": {
            "repaired_physical_vectors": 96,
            "center10_instructions": 288,
            "consumer_contract": (
                "safe by the existing full-centered raw Forward -> R1-U -> inverse proof"
            ),
            "credible_against_32_instruction_chain_credit": False,
        },
    }


def main() -> None:
    raw160 = json.loads(RAW160.read_text())
    assert raw160["exact_transform_proof"]["exact_matrix_equality"]
    viable, search = search_scale_assignments()
    assert len(viable) == 16
    proof = exact_semantic_proof(viable)
    evaluated = [evaluate_mask(mask) for mask in viable]
    evaluated.sort(key=lambda record: (record["max_output_abs_bound"],
                                       record["mask_hex"]))
    best_mask = int(evaluated[0]["mask_hex"], 16)
    best = evaluate_mask(best_mask, keep_intervals=True)
    intervals = best.pop("intervals")
    consumer = asymmetric_consumer_probe(intervals)
    best_bound = best["max_output_abs_bound"]
    scale_pass = best_bound <= 10788
    repair = consumer["selective_raw_x_centered"]
    group_repair = consumer["six_group_exhaustive_search"][
        "minimum_passing_schedule"]
    consumer_pass = bool(
        group_repair is not None and group_repair["center10_instructions"] < 32)
    result = {
        "schema": "ntruplus768-gt32-n32-branchlocal-scale-placement-v1",
        "experiment": "GT32-N32-BRANCHLOCAL-160-SCALE-PLACEMENT-022",
        "frozen": {
            "ownership": "branch-local peak-13-YMM",
            "factorization": "explicit twist; S1-S3; DFT3; S4-S5",
            "Montgomery_chains": 160,
            "output_ABI": "current half-native e=0",
            "consumer": "current R1-U plus typed inverse",
        },
        "arm_relocation_identity": {
            "H_form": "p=dl; p*(L+wH)=stored_L+Mont(stored_H,w*p/dh)",
            "L_form": "p=dh/w; p*(L+wH)=Mont(stored_L,p/dl)+stored_H",
            "one_existing_Montgomery_chain_in_both_forms": True,
        },
        "scale_assignment_search": search,
        "exact_semantic_proof": proof,
        "eligible_schedule_ranges": evaluated,
        "best_schedule": best,
        "scale_placement_pass": scale_pass,
        "consumer_backup_probe": consumer,
        "consumer_backup_pass": consumer_pass,
        "assembly_emitted": False,
        "decision": "assembly-eligible" if scale_pass else
                    "scale-placement-hard-stop-before-assembly",
        "conclusion": (
            f"Only {len(viable)} of 65536 AVX2-uniform H/L schedules return "
            "the existing e=0 output ABI.  All freedom is confined to early "
            f"S2 operations; S3-S5 are forced back to high-arm CT.  The best "
            f"natural output bound is {best_bound}, still above 10788.  Thus "
            "the existing 160 chains cannot be relocated into a final reducing "
            "layer at the current pair-packed granularity."
        ),
        "reopen_only_if": [
            "mixed-lane arm placement is achieved without extra blends or chains",
            "the output ABI permits nonuniform per-leaf diagonal scales",
            "a consumer-native selective repair passes with less than the 32-instruction chain credit",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUT)
    print(result["decision"])


if __name__ == "__main__":
    main()
