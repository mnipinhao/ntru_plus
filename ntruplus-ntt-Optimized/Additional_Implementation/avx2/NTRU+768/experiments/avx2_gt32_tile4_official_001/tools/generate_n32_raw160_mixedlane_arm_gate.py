#!/usr/bin/env python3
"""Final uniform-e0 raw160 gate with one AVX2 mixed-lane arm slot.

The frozen branch-local factorization saves eight Montgomery chains.  This
gate admits only the remaining low-cost mechanism: within one four-qword
pair-packed operation, select H-form CT for some qwords and the equivalent
L-form CT for the others.  Two vpblendd instructions form the mixed reducing
and nonreducing arms.  Since the operation is repeated for two branches and
three row/k3 streams, one mixed slot costs at least 12 dynamic instructions;
the 20-instruction gate therefore permits at most one such slot.
"""

from __future__ import annotations

import itertools
import json

import generate_n32_bm_inv_joint_range_gate as joint
import generate_n32_branchlocal_scale_placement_gate as uniform
import generate_n32first_gate as split
import generate_tile4 as gt


OUT = gt.GENERATED / "tile4_n32_raw160_mixedlane_arm_gate.json"
Q = gt.Q
R = gt.R
B3_INPUT_BOUND = 10788
INT32_MAX = (1 << 31) - 1

Interval = tuple[int, int]
Schedule = tuple[tuple[int, int, int, int], ...]


def slot_lows() -> dict[int, dict[int, list[int]]]:
    result = {stage: {slot: [] for slot in range(4)}
              for stage in range(2, 6)}
    for stage in range(2, 6):
        for low, _high in uniform.butterfly_pairs(stage):
            result[stage][uniform.operation_slot(stage, low)].append(low)
    assert all(len(lows) == 4 for stage in result.values()
               for lows in stage.values())
    return result


SLOT_LOWS = slot_lows()
HIGH_FOR_LOW = {
    (stage, low): high
    for stage in range(2, 6)
    for low, high in uniform.butterfly_pairs(stage)
}


def uniform_stage_patterns() -> list[tuple[int, int, int, int]]:
    return [tuple(0xF if (bits >> slot) & 1 else 0
                  for slot in range(4))
            for bits in range(16)]


def one_mixed_stage_patterns() -> list[tuple[int, int, int, int]]:
    records = []
    for mixed_slot in range(4):
        for mixed_pattern in range(1, 15):
            for other_bits in range(8):
                pattern = []
                bit = 0
                for slot in range(4):
                    if slot == mixed_slot:
                        pattern.append(mixed_pattern)
                    else:
                        pattern.append(0xF if (other_bits >> bit) & 1 else 0)
                        bit += 1
                records.append(tuple(pattern))
    assert len(records) == 448
    return records


UNIFORM_STAGE = uniform_stage_patterns()
ONE_MIXED_STAGE = one_mixed_stage_patterns()


def lane_orientation(schedule: Schedule, stage: int, low: int) -> str:
    slot = uniform.operation_slot(stage, low)
    lane = SLOT_LOWS[stage][slot].index(low)
    return "L" if (schedule[stage - 2][slot] >> lane) & 1 else "H"


def scale_stage(scales: tuple[int, ...], stage: int,
                patterns: tuple[int, int, int, int]) -> tuple[int, ...]:
    output = list(scales)
    for slot, lows in SLOT_LOWS[stage].items():
        pattern = patterns[slot]
        for lane, low in enumerate(lows):
            high = HIGH_FOR_LOW[stage, low]
            twiddle = uniform.ordinary_twiddle(stage, low)
            value = (scales[high] * pow(twiddle, -1, Q) % Q
                     if (pattern >> lane) & 1 else scales[low])
            output[low] = output[high] = value
    return tuple(output)


def allowed_final_patterns(scales: tuple[int, ...]) \
        -> list[list[int]] | None:
    slots: list[list[int]] = []
    for slot, lows in SLOT_LOWS[5].items():
        patterns = [0]
        for lane, low in enumerate(lows):
            high = HIGH_FOR_LOW[5, low]
            twiddle = uniform.ordinary_twiddle(5, low)
            choices = []
            if scales[low] == 1:
                choices.append(0)
            if scales[high] * pow(twiddle, -1, Q) % Q == 1:
                choices.append(1)
            if not choices:
                return None
            patterns = [pattern | (choice << lane)
                        for pattern in patterns for choice in choices]
        slots.append(patterns)
    return slots


def mixed_slots(schedule: Schedule) -> list[tuple[int, int, int]]:
    return [(stage, slot, pattern)
            for stage, stage_patterns in zip(range(2, 6), schedule)
            for slot, pattern in enumerate(stage_patterns)
            if pattern not in (0, 0xF)]


def enumerate_e0_schedules() -> list[Schedule]:
    """Exhaust all schedules whose <=20-inst route can contain one mixed slot."""
    schedules: set[Schedule] = set()

    # Mixed slot in S2, S3, or S4.  S5 is derived from the exact e=0
    # requirement instead of enumerated blindly.
    for mixed_stage in (2, 3, 4):
        stage_sets = [ONE_MIXED_STAGE if stage == mixed_stage
                      else UNIFORM_STAGE for stage in (2, 3, 4)]
        for p2 in stage_sets[0]:
            s2 = scale_stage((1,) * 32, 2, p2)
            for p3 in stage_sets[1]:
                s3 = scale_stage(s2, 3, p3)
                for p4 in stage_sets[2]:
                    s4 = scale_stage(s3, 4, p4)
                    choices = allowed_final_patterns(s4)
                    if choices is None:
                        continue
                    for p5 in itertools.product(*choices):
                        schedule = (p2, p3, p4, tuple(p5))
                        if len(mixed_slots(schedule)) == 1:
                            schedules.add(schedule)

    # Mixed slot in S5, with S2-S4 uniform.
    for p2 in UNIFORM_STAGE:
        s2 = scale_stage((1,) * 32, 2, p2)
        for p3 in UNIFORM_STAGE:
            s3 = scale_stage(s2, 3, p3)
            for p4 in UNIFORM_STAGE:
                s4 = scale_stage(s3, 4, p4)
                choices = allowed_final_patterns(s4)
                if choices is None:
                    continue
                for p5 in itertools.product(*choices):
                    schedule = (p2, p3, p4, tuple(p5))
                    if len(mixed_slots(schedule)) == 1:
                        schedules.add(schedule)

    # Preserve the 16 uniform controls so the range comparison is explicit.
    viable_uniform, _ = uniform.search_scale_assignments()
    for mask in viable_uniform:
        schedules.add(tuple(
            tuple(0xF if (mask >> (4 * (stage - 2) + slot)) & 1 else 0
                  for slot in range(4))
            for stage in range(2, 6)
        ))
    return sorted(schedules)


def apply_interval_stage(rows: list[list[Interval]], scales: list[int],
                         stage: int, schedule: Schedule) \
        -> tuple[list[list[Interval]], list[int], int]:
    output = [row[:] for row in rows]
    next_scales = scales[:]
    maximum = 0
    for low, high in uniform.butterfly_pairs(stage):
        low_scale, high_scale = scales[low], scales[high]
        twiddle = uniform.ordinary_twiddle(stage, low)
        arm = lane_orientation(schedule, stage, low)
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
                product = uniform.mont_interval(row[high], factor)
                plus = uniform.add(row[low], product)
                minus = uniform.sub(row[low], product)
            else:
                product = uniform.mont_interval(row[low], factor)
                plus = uniform.add(product, row[high])
                minus = uniform.sub(product, row[high])
            output[row_index][low], output[row_index][high] = plus, minus
            maximum = max(maximum, uniform.peak(plus), uniform.peak(minus))
    return output, next_scales, maximum


def evaluate_schedule(schedule: Schedule, keep_intervals: bool = False) \
        -> dict[str, object]:
    branch_records = []
    retained: dict[tuple[int, int, int, int], Interval] = {}
    for branch, scale in enumerate(gt.BRANCH_SCALE):
        initial = uniform.top_intervals()[branch]
        rows: list[list[Interval]] = []
        for row in range(3):
            row_intervals = []
            for q in range(32):
                n = (64 * row + 33 * q) % 96
                factor = gt.centered(pow(scale, -n, Q) * R)
                row_intervals.append(uniform.mont_interval(initial, factor))
            rows.append(row_intervals)
        scales = [1] * 32
        stage_bounds = []

        s1_output = [row[:] for row in rows]
        for low, high in uniform.butterfly_pairs(1):
            for row_index, row in enumerate(rows):
                s1_output[row_index][low] = uniform.add(row[low], row[high])
                s1_output[row_index][high] = uniform.sub(row[low], row[high])
        rows = s1_output
        stage_bounds.append({"stage": 1, "arm": "raw",
                             "max_abs_bound": max(uniform.peak(x)
                                                  for r in rows for x in r)})

        for stage in (2, 3):
            rows, scales, bound = apply_interval_stage(
                rows, scales, stage, schedule)
            stage_bounds.append({"stage": stage,
                                 "patterns_hex": [f"0x{x:x}"
                                                  for x in schedule[stage - 2]],
                                 "max_abs_bound": bound})

        dft_rows = [[(0, 0)] * 32 for _ in range(3)]
        dft_max = 0
        for q in range(32):
            x0, x1, x2 = (rows[row][q] for row in range(3))
            difference = uniform.sub(x1, x2)
            omega = uniform.mont_interval(difference, -886)
            values = (uniform.add(uniform.add(x0, x1), x2),
                      uniform.add(uniform.sub(x0, x2), omega),
                      uniform.sub(uniform.sub(x0, x1), omega))
            for k3, value in enumerate(values):
                dft_rows[k3][q] = value
                dft_max = max(dft_max, uniform.peak(value))
        rows = dft_rows

        for stage in (4, 5):
            rows, scales, bound = apply_interval_stage(
                rows, scales, stage, schedule)
            stage_bounds.append({"stage": stage,
                                 "patterns_hex": [f"0x{x:x}"
                                                  for x in schedule[stage - 2]],
                                 "max_abs_bound": bound})
        assert scales == [1] * 32
        output_bounds = [max(uniform.peak(value) for value in row)
                         for row in rows]
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
    record: dict[str, object] = {
        "patterns_S2_to_S5": [[f"0x{x:x}" for x in stage]
                               for stage in schedule],
        "mixed_slots": [{"stage": stage, "slot": slot,
                         "lane_L_mask_hex": f"0x{pattern:x}"}
                        for stage, slot, pattern in mixed_slots(schedule)],
        "route_instruction_lower_bound": 12 * len(mixed_slots(schedule)),
        "branch_records": branch_records,
        "max_output_abs_bound": max(record["max_output_abs_bound"]
                                    for record in branch_records),
    }
    if keep_intervals:
        record["intervals"] = retained
    return record


def candidate_transform(values: list[int], scale: int,
                        schedule: Schedule) -> list[int]:
    rows = [[0] * 32 for _ in range(3)]
    scales = [1] * 32
    for row in range(3):
        for q in range(32):
            n = (64 * row + 33 * q) % 96
            rows[row][q] = values[32 * row + q] * pow(scale, -n, Q) % Q
    for stage in (1, 2, 3):
        output = [row[:] for row in rows]
        next_scales = scales[:]
        for low, high in uniform.butterfly_pairs(stage):
            twiddle = uniform.ordinary_twiddle(stage, low)
            arm = "H" if stage == 1 else lane_orientation(schedule, stage, low)
            dl, dh = scales[low], scales[high]
            if arm == "H":
                result_scale = dl
                factor = twiddle * result_scale * pow(dh, -1, Q) % Q
                source_index, other_index = high, low
            else:
                result_scale = dh * pow(twiddle, -1, Q) % Q
                factor = result_scale * pow(dl, -1, Q) % Q
                source_index, other_index = low, high
            next_scales[low] = next_scales[high] = result_scale
            for row_index, source in enumerate(rows):
                product = factor * source[source_index] % Q
                other = source[other_index]
                output[row_index][low] = (other + product) % Q
                output[row_index][high] = ((other - product) if arm == "H"
                                           else (product - other)) % Q
        rows, scales = output, next_scales
    tiles = [[0] * 32 for _ in range(3)]
    for q in range(32):
        column = split.dft3([rows[row][q] for row in range(3)])
        for k3 in range(3):
            tiles[k3][q] = column[k3]
    rows = tiles
    for stage in (4, 5):
        output = [row[:] for row in rows]
        next_scales = scales[:]
        for low, high in uniform.butterfly_pairs(stage):
            twiddle = uniform.ordinary_twiddle(stage, low)
            arm = lane_orientation(schedule, stage, low)
            dl, dh = scales[low], scales[high]
            if arm == "H":
                result_scale = dl
                factor = twiddle * result_scale * pow(dh, -1, Q) % Q
                source_index, other_index = high, low
            else:
                result_scale = dh * pow(twiddle, -1, Q) % Q
                factor = result_scale * pow(dl, -1, Q) % Q
                source_index, other_index = low, high
            next_scales[low] = next_scales[high] = result_scale
            for row_index, source in enumerate(rows):
                product = factor * source[source_index] % Q
                other = source[other_index]
                output[row_index][low] = (other + product) % Q
                output[row_index][high] = ((other - product) if arm == "H"
                                           else (product - other)) % Q
        rows, scales = output, next_scales
    assert scales == [1] * 32
    return [value for row in rows for value in row]


def exact_semantic_proof(schedule: Schedule) -> dict[str, object]:
    checks = 0
    for scale in gt.BRANCH_SCALE:
        for basis in range(96):
            vector = [0] * 96
            vector[basis] = 1
            assert candidate_transform(vector, scale, schedule) == \
                split.current_transform(vector, scale)
            checks += 1
    return {"basis_vectors_checked": checks,
            "exact_matrix_equality": True,
            "ordinary_e0_output": True}


def direct_consumer_probe(intervals: dict[tuple[int, int, int, int], Interval]) \
        -> dict[str, object]:
    r1u_intervals = {}
    maximum_accumulator = 0
    for branch in range(2):
        for k3 in range(3):
            for q in range(32):
                bound = max(uniform.peak(intervals[branch, k3, q, degree])
                            for degree in range(4))
                lambda_bound = gt.product_bound(
                    bound, [gt.lambda_montgomery(k3, q, branch)])
                raw_bounds = (bound * bound + 3 * bound * lambda_bound,
                              2 * bound * bound + 2 * bound * lambda_bound,
                              3 * bound * bound + bound * lambda_bound,
                              4 * bound * bound)
                maximum_accumulator = max(maximum_accumulator, *raw_bounds)
                for degree, raw_bound in enumerate(raw_bounds):
                    r1u_intervals[branch, k3, q, degree] = list(
                        joint.reducer_interval(raw_bound))
    signed32_safe = maximum_accumulator <= INT32_MAX
    inverse = joint.prove_inverse(r1u_intervals) if signed32_safe else None
    inverse_safe = bool(inverse is not None
                        and inverse["all_frontiers_signed_int16_safe"])
    return {
        "maximum_raw_accumulator_abs_bound": maximum_accumulator,
        "signed32_safe": signed32_safe,
        "inverse_safe": inverse_safe,
        "inverse_IDFT3_internal_abs_bound": None if inverse is None else
            inverse["global_IDFT3_internal_addsub_abs_bound"],
        "inverse_terminal_abs_bound": None if inverse is None else
            inverse["global_terminal_abs_bound"],
    }


def main() -> None:
    schedules = enumerate_e0_schedules()
    evaluated = [evaluate_schedule(schedule) for schedule in schedules]
    evaluated.sort(key=lambda record: (
        record["max_output_abs_bound"],
        record["route_instruction_lower_bound"],
        record["patterns_S2_to_S5"],
    ))
    best_record = evaluated[0]
    best_schedule = schedules[evaluated.index(best_record)]
    # Re-find by serialized patterns because evaluated was sorted separately.
    best_schedule = next(schedule for schedule in schedules
                         if [[f"0x{x:x}" for x in stage] for stage in schedule]
                         == best_record["patterns_S2_to_S5"])
    detailed = evaluate_schedule(best_schedule, keep_intervals=True)
    intervals = detailed.pop("intervals")
    semantic = exact_semantic_proof(best_schedule)
    consumer = direct_consumer_probe(intervals)
    best_bound = detailed["max_output_abs_bound"]
    route_cost = detailed["route_instruction_lower_bound"]
    natural_pass = best_bound <= B3_INPUT_BOUND
    consumer_pass = consumer["signed32_safe"] and consumer["inverse_safe"]
    assembly_eligible = (route_cost <= 20 and (natural_pass or consumer_pass))

    by_stage = {str(stage): 0 for stage in range(2, 6)}
    uniform_count = 0
    for schedule in schedules:
        mixed = mixed_slots(schedule)
        if not mixed:
            uniform_count += 1
        else:
            by_stage[str(mixed[0][0])] += 1

    result = {
        "schema": "ntruplus768-gt32-n32-raw160-mixedlane-arm-v1",
        "experiment": "GT32-N32-RAW160-MIXEDLANE-ARM-GATE-023",
        "frozen": {
            "ownership": "branch-local peak-13-YMM",
            "factorization": "explicit twist; S1-S3; DFT3; S4-S5",
            "Montgomery_chains": 160,
            "output_ABI": "current half-native uniform e=0",
            "consumer": "current R1-U plus typed inverse",
        },
        "admitted_change": "one pair-packed slot may select H/L per qword",
        "avx2_route_cost_model": {
            "mechanism": "two vpblendd form mixed reducing/nonreducing arms; output plus/minus placement is unchanged",
            "applications_per_slot": "two branches times three row/k3 streams",
            "instructions_per_mixed_slot_lower_bound": 12,
            "budget_instructions": 20,
            "maximum_mixed_slots_under_budget": 1,
            "factor_constants": "regenerated in lane order; no runtime routing",
        },
        "search": {
            "method": "exhaustive over all uniform slots plus at most one of 14 nonuniform four-qword masks",
            "ordinary_e0_schedules": len(schedules),
            "uniform_controls": uniform_count,
            "mixed_schedules_by_stage": by_stage,
            "all_schedules_exact_scale_checked": True,
        },
        "best_schedule": detailed,
        "best_schedule_exact_semantic_proof": semantic,
        "best_natural_output_abs_bound": best_bound,
        "existing_B3_input_abs_bound": B3_INPUT_BOUND,
        "natural_B3_contract_pass": natural_pass,
        "direct_R1U_inverse_probe": consumer,
        "direct_consumer_pass": consumer_pass,
        "register_gate": {
            "existing_peak_YMM": 13,
            "one_additional_blend_temporary": 1,
            "conservative_peak_YMM": 14,
            "fits_AVX2_16_YMM": True,
            "spill_required": False,
        },
        "assembly_eligible": assembly_eligible,
        "assembly_emitted": False,
        "decision": ("assembly-eligible" if assembly_eligible else
                     "mixed-lane-static-hard-stop-before-assembly"),
        "conclusion": (
            f"The <=20-instruction budget permits one mixed slot.  Exhaustive "
            f"uniform-e0 search finds {len(schedules)} schedules, but the best "
            f"representative bound is {best_bound} versus the frozen "
            f"{B3_INPUT_BOUND} B3 limit.  Its direct R1-U/inverse closure is "
            f"{'safe' if consumer_pass else 'unsafe'}."
        ),
        "reopen_only_if": [
            "the uniform e0 output ABI is replaced by a proven nonuniform per-leaf typed-scale ABI",
            "a joint consumer repair costs less than the saved 32 instructions and closes the exact inverse range",
            "a wider-register ISA changes the routing/reduction cost model",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUT)
    print(result["decision"])


if __name__ == "__main__":
    main()
