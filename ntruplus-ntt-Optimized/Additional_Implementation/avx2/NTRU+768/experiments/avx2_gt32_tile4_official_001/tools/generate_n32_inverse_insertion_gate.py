#!/usr/bin/env python3
"""Exact insertion-point gate for IDFT3 inside the five-stage InvNTT32."""

from __future__ import annotations

import functools
import json

import generate_n32_idft3_l2_fused_gate as fused
import generate_n32_native_inverse_gate as native
import generate_tile4 as gt


OUT = gt.GENERATED / "tile4_n32_inverse_insertion_gate.json"
RANGE_INPUT = gt.GENERATED / "tile4_aos_dot_redc16_gate.json"
R3_RESULT = gt.ROOT / "results" / "tile4-n32-wave-schedule-short.json"

LENGTHS = (2, 4, 8, 16, 32)
INT16_LIMIT = 32767


def add_interval(left: list[int], right: list[int]) -> list[int]:
    return [left[0] + right[0], left[1] + right[1]]


def sub_interval(left: list[int], right: list[int]) -> list[int]:
    return [left[0] - right[1], left[1] - right[0]]


def interval_abs(interval: list[int]) -> int:
    return max(abs(interval[0]), abs(interval[1]))


@functools.lru_cache(maxsize=None)
def mont_interval(low: int, high: int, factor: int) -> tuple[int, int]:
    values = [gt.montgomery_fixed(value, factor)
              for value in range(low, high + 1)]
    return min(values), max(values)


def inverse_stage(intervals: list[list[int]], length: int) -> dict[str, object]:
    output: list[list[int] | None] = [None] * 32
    records = []
    for base in range(0, 32, length):
        for offset in range(length // 2):
            low_index = base + offset
            high_index = low_index + length // 2
            low = intervals[low_index]
            high = intervals[high_index]
            if length == 2:
                product = high
                factor = None
            else:
                factor = gt.mont_root(-offset * (32 // length))
                product = list(mont_interval(high[0], high[1], factor))
            sum_interval = add_interval(low, product)
            difference_interval = sub_interval(low, product)
            output[low_index] = sum_interval
            output[high_index] = difference_interval
            peak = max(interval_abs(sum_interval),
                       interval_abs(difference_interval))
            records.append({
                "low_q": low_index,
                "high_q": high_index,
                "factor": factor,
                "product_interval": product,
                "output_abs_bound": peak,
                "signed_int16_safe": peak <= INT16_LIMIT,
            })
    assert all(value is not None for value in output)
    return {
        "output": [value for value in output if value is not None],
        "max_output_abs_bound": max(record["output_abs_bound"]
                                    for record in records),
        "signed_int16_safe": all(record["signed_int16_safe"]
                                 for record in records),
        "first_unsafe_edge": next(
            (record for record in records
             if not record["signed_int16_safe"]), None),
    }


def idft_stage(rows: list[list[list[int]]]) -> dict[str, object]:
    output = [[None] * 32 for _ in range(3)]
    internal_records = []
    max_internal = 0
    max_output = 0
    safe = True
    for q in range(32):
        inputs = [rows[row][q] for row in range(3)]
        raw_sum = add_interval(inputs[1], inputs[2])
        raw_difference = sub_interval(inputs[1], inputs[2])
        raw_r0_minus_r1 = sub_interval(inputs[0], inputs[1])
        raw_r0_minus_r2 = sub_interval(inputs[0], inputs[2])
        internal_peak = max(interval_abs(value) for value in (
            raw_sum, raw_difference, raw_r0_minus_r1, raw_r0_minus_r2))
        outputs = fused.exact_idft(inputs)
        output_peak = max(interval_abs(value) for value in outputs)
        edge_safe = (internal_peak <= INT16_LIMIT
                     and output_peak <= INT16_LIMIT)
        max_internal = max(max_internal, internal_peak)
        max_output = max(max_output, output_peak)
        safe &= edge_safe
        if not edge_safe:
            internal_records.append({
                "q": q,
                "input_intervals": inputs,
                "raw_sum": raw_sum,
                "raw_difference": raw_difference,
                "raw_r0_minus_r1": raw_r0_minus_r1,
                "raw_r0_minus_r2": raw_r0_minus_r2,
                "internal_abs_bound": internal_peak,
                "output_intervals": outputs,
                "output_abs_bound": output_peak,
            })
        for row in range(3):
            output[row][q] = outputs[row]
    return {
        "output": output,
        "max_internal_addsub_abs_bound": max_internal,
        "max_output_abs_bound": max_output,
        "signed_int16_safe": safe,
        "first_unsafe_q": internal_records[0] if internal_records else None,
    }


def inverse_stage_mod(rows: list[list[int]], length: int) -> None:
    for row in rows:
        for base in range(0, 32, length):
            for offset in range(length // 2):
                low_index = base + offset
                high_index = low_index + length // 2
                factor = (1 if length == 2 else
                          pow(gt.OMEGA32,
                              -offset * (32 // length), gt.Q))
                product = row[high_index] * factor % gt.Q
                low = row[low_index]
                row[low_index] = (low + product) % gt.Q
                row[high_index] = (low - product) % gt.Q


def idft_mod(rows: list[list[int]]) -> list[list[int]]:
    omega = pow(gt.OMEGA96, 32, gt.Q)
    matrix = (
        (1, 1, 1),
        (1, pow(omega, 2, gt.Q), omega),
        (1, omega, pow(omega, 2, gt.Q)),
    )
    return [[sum(matrix[out][source] * rows[source][q]
                 for source in range(3)) % gt.Q
             for q in range(32)] for out in range(3)]


def execute_mod(basis: int, insertion: int) -> list[int]:
    rows = [[0] * 32 for _ in range(3)]
    rows[basis // 32][basis % 32] = 1
    for stage in range(insertion):
        inverse_stage_mod(rows, LENGTHS[stage])
    rows = idft_mod(rows)
    for stage in range(insertion, len(LENGTHS)):
        inverse_stage_mod(rows, LENGTHS[stage])
    return [value for row in rows for value in row]


def exact_commutation_proof() -> dict[str, object]:
    reference = [execute_mod(basis, 0) for basis in range(96)]
    checked = 0
    for insertion in range(6):
        for basis in range(96):
            assert execute_mod(basis, insertion) == reference[basis]
            checked += 1
    return {
        "insertion_points": 6,
        "basis_vectors_per_point": 96,
        "exact_basis_executions": checked,
        "all_equal_mod_q": True,
        "inter_axis_twiddle": False,
    }


def analyze_insertion(coefficient_prefixes: list[list[list[list[int]]]],
                      insertion: int) -> dict[str, object]:
    max_prefix = 0
    max_idft_internal = 0
    max_idft_output = 0
    max_suffix = 0
    prefix_safe = True
    idft_safe = True
    suffix_safe = True
    first_failure = None
    per_coefficient = []

    for coefficient in range(4):
        prefix = coefficient_prefixes[coefficient][insertion]
        max_prefix = max(max_prefix, max(interval_abs(value)
                                         for value in prefix))
        rows = [[list(value) for value in prefix] for _ in range(3)]
        idft = idft_stage(rows)
        max_idft_internal = max(
            max_idft_internal, idft["max_internal_addsub_abs_bound"])
        max_idft_output = max(max_idft_output,
                              idft["max_output_abs_bound"])
        idft_safe &= idft["signed_int16_safe"]
        if first_failure is None and not idft["signed_int16_safe"]:
            first_failure = {
                "frontier": "IDFT3",
                "coefficient": coefficient,
                "detail": idft["first_unsafe_q"],
            }

        rows = idft["output"]
        suffix_records = []
        for stage_index in range(insertion, len(LENGTHS)):
            length = LENGTHS[stage_index]
            for row in range(3):
                stage = inverse_stage(rows[row], length)
                rows[row] = stage["output"]
                max_suffix = max(max_suffix,
                                 stage["max_output_abs_bound"])
                suffix_safe &= stage["signed_int16_safe"]
                suffix_records.append({
                    "row": row,
                    "length": length,
                    "max_output_abs_bound": stage["max_output_abs_bound"],
                    "signed_int16_safe": stage["signed_int16_safe"],
                })
                if first_failure is None and not stage["signed_int16_safe"]:
                    first_failure = {
                        "frontier": f"InvNTT32-length-{length}",
                        "coefficient": coefficient,
                        "row": row,
                        "detail": stage["first_unsafe_edge"],
                    }
        per_coefficient.append({
            "coefficient": coefficient,
            "IDFT_internal_abs_bound":
                idft["max_internal_addsub_abs_bound"],
            "IDFT_output_abs_bound": idft["max_output_abs_bound"],
            "suffix": suffix_records,
        })

    # Prefixes were constructed only while their preceding stages were safe.
    for coefficient in range(4):
        for stage_index in range(insertion):
            intervals = coefficient_prefixes[coefficient][stage_index + 1]
            stage_peak = max(interval_abs(value) for value in intervals)
            prefix_safe &= stage_peak <= INT16_LIMIT

    return {
        "name": f"P{insertion}",
        "stages_before_IDFT3": list(LENGTHS[:insertion]),
        "stages_after_IDFT3": list(LENGTHS[insertion:]),
        "prefix_max_abs_bound": max_prefix,
        "prefix_signed_int16_safe": prefix_safe,
        "IDFT_internal_max_abs_bound": max_idft_internal,
        "IDFT_output_max_abs_bound": max_idft_output,
        "IDFT_signed_int16_safe": idft_safe,
        "suffix_max_abs_bound": max_suffix,
        "suffix_signed_int16_safe": suffix_safe,
        "all_int16_safe": prefix_safe and idft_safe and suffix_safe,
        "first_failure": first_failure,
        "Montgomery_chain_count_change": 0,
        "half_native_k3_reflection_preserved_until_IDFT3": True,
        "lane_typed_IDFT3_runtime_repair": 0,
        "per_coefficient": per_coefficient,
    }


def main() -> None:
    ranges = json.loads(RANGE_INPUT.read_text())
    r1u = ranges["modes"]["R1-U"]
    r3 = json.loads(R3_RESULT.read_text())

    # prefixes[coefficient][completed-stage-count][q]
    prefixes: list[list[list[list[int]]]] = []
    prefix_stage_summary = []
    for coefficient in range(4):
        current = [
            list(r1u["q_records"][q]["coefficients"][coefficient]
                 ["exact_output_interval"])
            for q in range(32)
        ]
        records = [[list(value) for value in current]]
        for length in LENGTHS:
            stage = inverse_stage(current, length)
            current = stage["output"]
            records.append([list(value) for value in current])
            prefix_stage_summary.append({
                "coefficient": coefficient,
                "length": length,
                "max_output_abs_bound": stage["max_output_abs_bound"],
                "signed_int16_safe": stage["signed_int16_safe"],
            })
        prefixes.append(records)

    candidates = [analyze_insertion(prefixes, insertion)
                  for insertion in range(6)]
    assert [candidate["prefix_max_abs_bound"] for candidate in candidates] == [
        10560, 21120, 22535, 24312, 26068, 28053]
    assert [candidate["IDFT_internal_max_abs_bound"]
            for candidate in candidates] == [
        21120, 42240, 45070, 48624, 52136, 56106]
    assert not any(candidate["all_int16_safe"] for candidate in candidates)

    route_proxy = {
        placement: -values["suffix_route"]["paired_candidate_minus_control"]
        ["median_tsc"]
        for placement, values in r3["placements"].items()
    }
    two_forward_debt = {
        placement: 2 * values["three_wave_plus_route_estimate_tsc"]
        for placement, values in r3["placements"].items()
    }

    result = {
        "schema": "ntruplus768-gt32-n32-inverse-insertion-v1",
        "experiment": "GT-N32-INVERSE-INSERTION-010",
        "scope": "place-IDFT3-at-every-InvNTT32-stage-boundary",
        "exact_algebra": exact_commutation_proof(),
        "frozen": {
            "half_native_BM_output": True,
            "R1U_independent_interval_contract": True,
            "InvNTT32_stage_DAG": list(LENGTHS),
            "InvNTT32_twiddles_independent_of_k3_and_branch": True,
            "new_Montgomery_chains": 0,
        },
        "prefix_stage_summary": prefix_stage_summary,
        "candidates": candidates,
        "finding": (
            "The current inverse Montgomery stages reduce only each high arm; "
            "the butterfly low arm continues to accumulate.  Consequently the "
            "independent interval entering IDFT3 grows monotonically as IDFT3 "
            "moves later. P1 moves the first overflow into IDFT3, while P2-P5 "
            "make that IDFT3 frontier progressively wider rather than repairing it."
        ),
        "late_IDFT_performance": {
            "five_vs_six_blend_proxy_TSC": route_proxy,
            "estimated_two_R3_Forward_debt_TSC": two_forward_debt,
            "range_contract_passed": False,
            "performance_break_even_passed": False,
        },
        "joint_reachable_range": {
            "status": "not-proven",
            "current_box_witness_may_ignore_producer_correlations": True,
            "complete_executable_N32_Forward_available": False,
            "random_testing_is_not_a_formal_replacement": True,
        },
        "int16_wrap": {
            "allowed": False,
            "65536_mod_q": (1 << 16) % gt.Q,
            "centered_65536_mod_q": gt.centered(1 << 16),
        },
        "assembly_emitted": False,
        "decision": "no-assembly-all-six-insertion-points-fail-current-independent-range-contract",
        "not_claimed": [
            "that the tensor transforms do not commute",
            "that a tighter producer-realizable joint range cannot pass",
            "that a changed reduction policy cannot make P2/P3 viable",
        ],
        "reopen_only_if": [
            "producer-realizable joint range proves every raw IDFT and butterfly frontier int16-safe",
            "an existing inverse stage is changed so all outputs, not only the high multiplicand, receive a reducing representative",
            "a bounded checkpoint is cheaper than the measured two-Forward debt after physical routing is included",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUT)
    for candidate in candidates:
        print(candidate["name"], candidate["all_int16_safe"],
              candidate["IDFT_internal_max_abs_bound"])
    print(result["decision"])


if __name__ == "__main__":
    main()
