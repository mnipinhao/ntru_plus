#!/usr/bin/env python3
"""Search the two bounded reopen mechanisms at the N32 BM/inverse frontier.

Outputs:
* tile4_n32_idft3_l2_fused_gate.json
* tile4_n32_r1u_safe_rep_gate.json

No assembly is emitted unless a candidate both proves every int16 frontier
and reduces the new work to at most 16 instructions over the complete island.
"""

from __future__ import annotations

import itertools
import json

import generate_n32_native_inverse_gate as native
import generate_tile4 as gt


FUSED_OUT = gt.GENERATED / "tile4_n32_idft3_l2_fused_gate.json"
REP_OUT = gt.GENERATED / "tile4_n32_r1u_safe_rep_gate.json"
RANGE_INPUT = gt.GENERATED / "tile4_aos_dot_redc16_gate.json"
NATIVE_GATE = gt.GENERATED / "tile4_n32_native_inverse_gate.json"

Q = gt.Q
INT16_LIMIT = 32767


def exact_idft(intervals: list[list[int]], factor: int = -886) -> list[list[int]]:
    """Exact independent-box IDFT3_V2 output intervals."""
    (l0, h0), (l1, h1), (l2, h2) = intervals
    centered = [native.center10(value)
                for value in range(l1 + l2, h1 + h2 + 1)]
    outputs = [[l0 + min(centered), h0 + max(centered)]]

    factor_qinv = gt.signed16(factor * gt.QINV)

    def mont(value: int) -> int:
        low = gt.signed16(value * factor_qinv)
        return ((value * factor) // (1 << 16)
                - (low * Q) // (1 << 16))

    for row in (1, 2):
        minimum = 1 << 60
        maximum = -(1 << 60)
        for difference in range(l1 - h2, h1 - l2 + 1):
            r1_low = max(l1, l2 + difference)
            r1_high = min(h1, h2 + difference)
            if r1_low > r1_high:
                continue
            product = mont(difference)
            for r1 in {r1_low, r1_high}:
                r2 = r1 - difference
                values = ([l0 - r1 - product, h0 - r1 - product]
                          if row == 1 else
                          [l0 - r2 + product, h0 - r2 + product])
                minimum = min(minimum, *values)
                maximum = max(maximum, *values)
        outputs.append([minimum, maximum])
    return outputs


def abs_bound(interval: list[int]) -> int:
    return max(abs(interval[0]), abs(interval[1]))


def pair_peak(low: list[int], high: list[int]) -> int:
    """Maximum absolute value over both low+high and low-high."""
    return max(
        abs(low[0] + high[0]), abs(low[1] + high[1]),
        abs(low[0] - high[1]), abs(low[1] - high[0]),
    )


def complete_danger_map(r1u: dict[str, object]) -> dict[str, object]:
    rows: dict[tuple[int, int], list[list[int]]] = {}
    for q_record in r1u["q_records"]:
        q = q_record["physical_q"]
        for coefficient in q_record["coefficients"]:
            interval = coefficient["exact_output_interval"]
            rows[q, coefficient["coefficient"]] = exact_idft(
                [interval, interval, interval])

    row_records = []
    unsafe_lane_counts = [0, 0, 0]
    unsafe_q_pairs: list[set[tuple[int, int]]] = [set(), set(), set()]
    row_maxima = [0, 0, 0]
    row_pair_peaks = [0, 0, 0]
    for q in range(32):
        for coefficient in range(4):
            for row in range(3):
                row_maxima[row] = max(
                    row_maxima[row], abs_bound(rows[q, coefficient][row]))
    for low_q in range(0, 32, 2):
        high_q = low_q + 1
        for coefficient in range(4):
            for row in range(3):
                peak = pair_peak(rows[low_q, coefficient][row],
                                 rows[high_q, coefficient][row])
                row_pair_peaks[row] = max(row_pair_peaks[row], peak)
                if peak > INT16_LIMIT:
                    unsafe_lane_counts[row] += 1
                    unsafe_q_pairs[row].add((low_q, high_q))
                    row_records.append({
                        "row": row,
                        "physical_q_pair": [low_q, high_q],
                        "coefficient": coefficient,
                        "raw_length2_abs_bound": peak,
                    })

    assert row_maxima == [12919, 19387, 19387]
    assert unsafe_lane_counts == [0, 17, 17]
    assert [len(value) for value in unsafe_q_pairs] == [0, 16, 16]

    # Row 0 reaches length 2, but without a repair its conservative later
    # length-32 frontier still overflows.  Rows 1/2 need repair immediately.
    row0_l2 = row_pair_peaks[0]
    row0_later = native.inverse_stage_bounds(row0_l2)
    assert row0_l2 == 25838
    assert row0_later[-1]["output_abs_bound"] == 34710

    # Physical granularity: four packed q-group pairs per component.  Rows 1/2
    # exist in both branches: 2 rows * 2 branches * 4 = 16 vector repairs.
    immediate_vectors = 2 * 2 * 4
    immediate_instructions = immediate_vectors * 3
    # Row 0 has two branch components and eventually needs four vector repairs
    # per component at some later frontier.
    deferred_vectors = 1 * 2 * 4
    deferred_instructions = deferred_vectors * 3
    assert immediate_instructions + deferred_instructions == 72

    return {
        "IDFT_row_abs_bounds": row_maxima,
        "raw_length2_row_abs_bounds": row_pair_peaks,
        "unsafe_lane_pairs_per_row": unsafe_lane_counts,
        "unsafe_distinct_q_pairs_per_row": [
            len(value) for value in unsafe_q_pairs],
        "unsafe_records": row_records,
        "physical_repair_granularity": {
            "immediate_row1_row2_high_arm_vectors": immediate_vectors,
            "immediate_center_instructions": immediate_instructions,
            "row0_first_length2_safe": True,
            "row0_no_repair_later_stage_bounds": row0_later,
            "row0_deferred_repair_vectors": deferred_vectors,
            "row0_deferred_center_instructions": deferred_instructions,
            "complete_known_repair_instructions":
                immediate_instructions + deferred_instructions,
        },
    }


def signedness_combinations(modes: dict[str, object]) -> list[dict[str, object]]:
    """Idealized per-k3 U/S selection on the q=30,c3 witness contract."""
    records = []
    for combination in itertools.product(("U", "S"), repeat=3):
        intervals = [
            modes[f"R1-{mode}"]["q_records"][30]["coefficients"][3]
            ["exact_output_interval"]
            for mode in combination
        ]
        outputs = exact_idft(intervals)
        records.append({
            "k3_modes": list(combination),
            "IDFT_row_abs_bounds": [abs_bound(value) for value in outputs],
            "dangerous_rows_at_most_13380":
                all(abs_bound(outputs[row]) <= 13380 for row in (1, 2)),
        })
    assert not any(record["dangerous_rows_at_most_13380"]
                   for record in records)
    return records


def twiddle_representatives(r1u: dict[str, object]) -> list[dict[str, object]]:
    interval = r1u["q_records"][30]["coefficients"][3]
    interval = interval["exact_output_interval"]
    records = []
    for multiple in range(-9, 10):
        factor = -886 + multiple * Q
        if not -32768 <= factor <= 32767:
            continue
        outputs = exact_idft([interval, interval, interval], factor)
        records.append({
            "q_multiple": multiple,
            "signed_factor": factor,
            "factor_qinv": gt.signed16(factor * gt.QINV),
            "IDFT_row_abs_bounds": [abs_bound(value) for value in outputs],
        })
    best = min(records, key=lambda record: max(
        record["IDFT_row_abs_bounds"][1:]))
    assert max(best["IDFT_row_abs_bounds"][1:]) == 19358
    return records


def centered_input_subsets(r1u: dict[str, object]) -> list[dict[str, object]]:
    """Optimistic BM-side center of complete k3 streams."""
    interval = r1u["q_records"][30]["coefficients"][3]
    interval = interval["exact_output_interval"]
    centered_values = [native.center10(value)
                       for value in range(interval[0], interval[1] + 1)]
    centered = [min(centered_values), max(centered_values)]
    records = []
    for mask in range(1, 8):
        inputs = [centered if mask & (1 << index) else interval
                  for index in range(3)]
        outputs = exact_idft(inputs)
        centered_streams = mask.bit_count()
        # One k3 stream spans 2 branches * 8 physical q groups = 16 vectors.
        instructions = centered_streams * 16 * 3
        records.append({
            "centered_k3_rows": [index for index in range(3)
                                  if mask & (1 << index)],
            "IDFT_row_abs_bounds": [abs_bound(value) for value in outputs],
            "estimated_instructions": instructions,
            "dangerous_rows_at_most_13380":
                all(abs_bound(outputs[row]) <= 13380 for row in (1, 2)),
        })
    return records


def main() -> None:
    ranges = json.loads(RANGE_INPUT.read_text())
    prior = json.loads(NATIVE_GATE.read_text())
    r1u = ranges["modes"]["R1-U"]
    danger = complete_danger_map(r1u)
    threshold = INT16_LIMIT - max(danger["IDFT_row_abs_bounds"][1:])
    assert threshold == 13380

    signedness = signedness_combinations(ranges["modes"])
    factors = twiddle_representatives(r1u)
    centered_subsets = centered_input_subsets(r1u)

    fused = {
        "schema": "ntruplus768-gt32-n32-idft3-l2-fused-v1",
        "experiment": "GT-N32-IDFT3-L2-FUSED-008",
        "frozen": prior["frozen_contract"],
        "scope": "half-native-R1U-output-through-IDFT3-and-first-InvNTT32-length2",
        "danger_map": danger,
        "candidates": {
            "F0-current-separated": {
                "shape": "IDFT3-materialize-center-high-arm-raw-L2",
                "known_complete_repair_instructions": 72,
                "route_credit_instructions": 16,
                "net_static_delta": 56,
            },
            "F1-commute-L2-before-IDFT3": {
                "algebraically_exact": True,
                "BM_input_abs_bound": 10560,
                "raw_L2_output_abs_bound": 21120,
                "raw_L2_signed_int16_safe": True,
                "following_IDFT_r1_plus_or_minus_r2_abs_bound": 42240,
                "following_IDFT_frontier_signed_int16_safe": False,
                "decision": "moves-overflow-inside-IDFT3",
            },
            "F2-factor-existing-IDFT-reductions": {
                "existing_centered_sums_reused": 2,
                "existing_Montgomery_differences_reused": 2,
                "extra_Montgomery_chains": 0,
                "result": "row0-reaches-L2-but-row1-row2-output-box-still-overflows",
                "decision": "requires-new-representative-operation",
            },
            "F3-CT-first-butterfly": {
                "property": "reduces-high-arm-before-both-output-addsubs",
                "new_Montgomery_chains": 16,
                "new_instructions_for_immediate_dangerous_rows": 64,
                "row0_deferred_repair_still_required": 24,
                "known_total_new_instructions": 88,
                "decision": "dominated-by-72-instruction-center-schedule",
            },
            "F4-GS-first-butterfly": {
                "property": "only-difference-output-is-reduced",
                "raw_sum_output_still_overflows": True,
                "decision": "range-fail",
            },
            "F5-row-scale-absorbed-by-next-twiddle": {
                "chain_free_row_scales": [1, -1],
                "reason": "every-IDFT-row-has-r0-coefficient-one; any-other-scale-must-multiply-r0-path",
                "plus_or_minus_one_changes_range": False,
                "nontrivial_scale_requires_new_chain": True,
                "decision": "no-zero-chain-range-mechanism",
            },
            "F6-IDFT-twiddle-representative": {
                "representatives": factors,
                "best_dangerous_row_abs_bound": 19358,
                "target_abs_bound": threshold,
                "decision": "all-int16-factor-representatives-fail-witness",
            },
            "F7-branch-swap-output-permutation": {
                "changes_interval_multiset": False,
                "decision": "range-neutral",
            },
        },
        "assembly_eligibility": {
            "extra_Montgomery_chains_must_equal": 0,
            "maximum_extra_instructions": 16,
            "all_intermediates_signed_int16_safe": True,
            "passed": False,
        },
        "assembly_emitted": False,
        "decision": "no-assembly-current-fused-factorizations-do-not-eliminate-range-operation",
        "not_claimed": [
            "a lower bound over every six-input modular circuit",
            "that an SMT/superoptimized circuit cannot share a reduction across tensor axes",
            "that producer-realizable correlations equal the independent interval box",
        ],
        "reopen_only_if": [
            "a six-input circuit reduces row1-row2 without a new chain and keeps every pre-reduction addsub int16-safe",
            "an existing length4-or-later multiplication can be pulled across L2 and eliminates a complete repair frontier",
            "producer-realizable joint ranges prove the interval-box witness unreachable",
        ],
    }

    representative = {
        "schema": "ntruplus768-gt32-n32-r1u-safe-representative-v1",
        "experiment": "GT-N32-R1U-SAFE-REP-009",
        "scope": "R1U-finalizer-only-no-BM-algebra-change",
        "dangerous_arm_target_abs_bound": threshold,
        "zero_instruction_candidates": {
            "unsigned_vs_signed_REDC16_per_k3_idealization": signedness,
            "best_witness_bound": min(
                max(record["IDFT_row_abs_bounds"][1:])
                for record in signedness),
            "target_met": False,
        },
        "constant_q_bias": {
            "residue_preserving": True,
            "can_reduce_interval_width": False,
            "both_L2_sum_and_difference_required": True,
            "decision": "a-constant-shift-moves-sum-and-difference-in-opposite-directions",
        },
        "low_increment_candidates": {
            "center_complete_k3_streams": centered_subsets,
            "single_stream_best_dangerous_bound": 14462,
            "single_stream_target_met": False,
            "two_streams_leave_one_dangerous_row_above_target": True,
            "three_streams_target_met": True,
            "three_stream_instructions": 144,
        },
        "same_DAG_limit": {
            "R1U_c3_interval": [-10560, 7103],
            "R1U_c3_width": 17663,
            "R1S_c3_interval": [-8831, 8831],
            "R1S_c3_width": 17662,
            "interpretation": "signedness changes the q representative but does not perform the second quotient needed to narrow the REDC result",
        },
        "assembly_eligibility": {
            "maximum_extra_instructions": 16,
            "target_met": False,
        },
        "assembly_emitted": False,
        "decision": "no-assembly-no-zero-or-low-increment-safe-R1U-representative",
        "not_claimed": [
            "that a new partial-product schedule cannot reduce the pre-REDC accumulator bound",
            "that a producer-realizable joint-range proof cannot be tighter",
        ],
        "reopen_only_if": [
            "BM partial accumulators are range-shaped before the existing REDC at no new chain",
            "a finalizer computes the second quotient within the existing four-instruction REDC DAG",
            "only one physical stream needs a <=16-instruction correction under a tighter joint-range proof",
        ],
    }

    FUSED_OUT.write_text(json.dumps(fused, indent=2) + "\n")
    REP_OUT.write_text(json.dumps(representative, indent=2) + "\n")
    print(FUSED_OUT)
    print(REP_OUT)
    print(fused["decision"])
    print(representative["decision"])


if __name__ == "__main__":
    main()
