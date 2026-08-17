#!/usr/bin/env python3
"""Producer-specific range gate for half-native R1-U -> native inverse.

The older P0--P5 gate deliberately used the reusable N5/B3 input envelope.
This gate binds the same physical and scale ABI to the exact row-conjugated
N32-first producer's much tighter generated representative bounds.  It first
derives exact R1-U intervals, then exhausts typed IDFT3 interval arithmetic and
all five inverse NTT32 stages.  No cross-leaf correlation is assumed.
"""

from __future__ import annotations

import functools
import json

import generate_aos_dot_redc16 as aos
import generate_n32_idft3_l2_fused_gate as fused
import generate_n32_inverse_insertion_gate as insertion
import generate_tile4 as gt


OUT = gt.GENERATED / "tile4_n32_bm_inv_joint_range_gate.json"
PRODUCER = gt.GENERATED / "tile4_n32first_split_twist_gate.json"
GENERIC = gt.GENERATED / "tile4_n32_native_inverse_gate.json"
SEARCH = gt.GENERATED / "tile4_n32_bm_inv_joint_range_search.json"
INT16_LIMIT = 32767
LENGTHS = (2, 4, 8, 16, 32)


@functools.lru_cache(maxsize=None)
def reducer_interval(bound: int) -> tuple[int, int]:
    return aos.reducer_interval(bound, False)


@functools.lru_cache(maxsize=None)
def lambda_product_bound(bound: int, factor: int) -> int:
    return gt.product_bound(bound, [factor])


def derive_r1u_intervals(producer_bounds: list[list[int]]) -> tuple[
        dict[tuple[int, int, int, int], list[int]], dict[str, object]]:
    intervals: dict[tuple[int, int, int, int], list[int]] = {}
    records = []
    maximum = 0
    worst = None
    for branch in range(2):
        for k3 in range(3):
            bound = producer_bounds[branch][k3]
            for q in range(32):
                factor = gt.lambda_montgomery(k3, q, branch)
                lambda_bound = lambda_product_bound(bound, factor)
                raw_bounds = (
                    bound * bound + 3 * bound * lambda_bound,
                    2 * bound * bound + 2 * bound * lambda_bound,
                    3 * bound * bound + bound * lambda_bound,
                    4 * bound * bound,
                )
                coefficient_records = []
                for coefficient, raw_bound in enumerate(raw_bounds):
                    interval = list(reducer_interval(raw_bound))
                    output_bound = max(abs(value) for value in interval)
                    intervals[branch, k3, q, coefficient] = interval
                    record = {
                        "coefficient": coefficient,
                        "raw_accumulator_abs_bound": raw_bound,
                        "exact_R1U_output_interval": interval,
                        "output_abs_bound": output_bound,
                    }
                    coefficient_records.append(record)
                    if output_bound > maximum:
                        maximum = output_bound
                        worst = {
                            "branch": branch,
                            "k3": k3,
                            "physical_q": q,
                            **record,
                        }
                records.append({
                    "branch": branch,
                    "k3": k3,
                    "physical_q": q,
                    "producer_input_abs_bound": bound,
                    "lambda_factor": factor,
                    "lambda_product_abs_bound": lambda_bound,
                    "coefficients": coefficient_records,
                })
    assert worst is not None
    return intervals, {
        "records": records,
        "maximum_output_abs_bound": maximum,
        "worst_record": worst,
        "current_unsigned_REDC16_unchanged": True,
    }


def prove_inverse(intervals: dict[tuple[int, int, int, int], list[int]]) \
        -> dict[str, object]:
    records = []
    global_idft_internal = 0
    global_idft = 0
    global_stage = {length: 0 for length in LENGTHS}
    all_safe = True
    for branch in range(2):
        for coefficient in range(4):
            input_rows = [[intervals[branch, k3, q, coefficient]
                           for q in range(32)] for k3 in range(3)]
            idft = insertion.idft_stage(input_rows)
            rows = idft["output"]
            idft_internal = idft["max_internal_addsub_abs_bound"]
            idft_max = idft["max_output_abs_bound"]
            global_idft_internal = max(global_idft_internal, idft_internal)
            global_idft = max(global_idft, idft_max)
            stage_records = []
            for length in LENGTHS:
                stage_max = 0
                stage_safe = True
                for row in range(3):
                    stage = insertion.inverse_stage(rows[row], length)
                    rows[row] = stage["output"]
                    stage_max = max(stage_max,
                                    stage["max_output_abs_bound"])
                    stage_safe &= stage["signed_int16_safe"]
                global_stage[length] = max(global_stage[length], stage_max)
                all_safe &= stage_safe
                stage_records.append({
                    "length": length,
                    "max_output_abs_bound": stage_max,
                    "signed_int16_safe": stage_safe,
                })
            records.append({
                "branch": branch,
                "coefficient": coefficient,
                "IDFT3_internal_addsub_abs_bound": idft_internal,
                "IDFT3_output_abs_bound": idft_max,
                "IDFT3_signed_int16_safe": idft["signed_int16_safe"],
                "inverse_stages": stage_records,
            })
            all_safe &= idft["signed_int16_safe"]
    return {
        "branch_coefficient_records": records,
        "global_IDFT3_internal_addsub_abs_bound": global_idft_internal,
        "global_IDFT3_output_abs_bound": global_idft,
        "global_stage_output_abs_bounds": [
            {"length": length,
             "max_output_abs_bound": global_stage[length],
             "signed_int16_safe": global_stage[length] <= INT16_LIMIT}
            for length in LENGTHS
        ],
        "global_terminal_abs_bound": global_stage[32],
        "all_frontiers_signed_int16_safe": all_safe,
    }


def main() -> None:
    producer = json.loads(PRODUCER.read_text())
    generic = json.loads(GENERIC.read_text())
    search = json.loads(SEARCH.read_text())
    assert producer["exact_transform_proof"]["exact_matrix_equality"]
    assert producer["range_proof"]["all_signed_int16_safe"]
    producer_bounds = [
        branch["output_abs_bounds"]
        for branch in producer["range_proof"]["branches"]
    ]
    assert producer_bounds == [[5373, 5367, 5295], [5522, 5341, 5488]]

    intervals, r1u = derive_r1u_intervals(producer_bounds)
    inverse = prove_inverse(intervals)
    assert r1u["maximum_output_abs_bound"] == 5318
    assert inverse["global_IDFT3_internal_addsub_abs_bound"] == 10493
    assert inverse["global_IDFT3_output_abs_bound"] == 8880
    assert [record["max_output_abs_bound"]
            for record in inverse["global_stage_output_abs_bounds"]] == [
                17760, 19581, 21637, 23752, 26043]
    assert inverse["all_frontiers_signed_int16_safe"]
    assert not search["signed_int16_overflow_witness_found"]
    assert search["best"]["absolute"] <= 17760

    result = {
        "schema": "ntruplus768-gt32-n32-bm-inv-joint-range-v1",
        "experiment": "GT-N32-BM-INV-JOINT-RANGE-011",
        "question": (
            "Does the current half-native R1-U representative become "
            "inverse-safe when bound to the exact N32-first producer contract?"
        ),
        "frozen_ABI": {
            "physical_layout": "half-native quartic AoS",
            "low_128_k3_order": [0, 1, 2],
            "high_128_k3_order": [0, 2, 1],
            "BM_scale": "e0-times-e0-to-e-minus1",
            "BM_finalizer": "current unsigned-low-word R1-U REDC16",
            "inverse_order": "typed-IDFT3-before-length2/4/8/16/32",
        },
        "generic_envelope_control": {
            "source": str(GENERIC.relative_to(gt.ROOT)),
            "N5_B3_producer_input_abs_bound": 10788,
            "R1U_IDFT3_abs_bound": generic["range_gate"]["R1-U"]
                ["exact_max_output_abs_bound"],
            "raw_length2_abs_bound": generic["range_gate"]
                ["raw_length2_contract_witness"]["raw_sum_abs_value"],
            "decision": "unsafe-but-not-the-N32-producer-contract",
        },
        "N32_producer": {
            "source": str(PRODUCER.relative_to(gt.ROOT)),
            "exact_matrix_equality": True,
            "representative_schedule": (
                "row-conjugated signed-word Montgomery NTT32, residual "
                "Montgomery row scaling, then DFT3"
            ),
            "output_abs_bounds_by_branch_k3": producer_bounds,
            "complete_executable_AVX2_Forward_available": False,
            "proof_is_conditional_on_this_exact_reduction_policy": True,
        },
        "producer_specific_R1U": r1u,
        "inverse_proof": inverse,
        "correlation_result": {
            "producer_realizable_joint_correlation_required": False,
            "reason": (
                "The tighter producer-specific independent interval box "
                "already proves every IDFT3 and InvNTT32 frontier safe."
            ),
            "runtime_cost": 0,
            "new_reduction_checkpoints": 0,
            "new_Montgomery_chains": 0,
            "representative_change_required": False,
        },
        "bounded_concrete_search": {
            "source": str(SEARCH.relative_to(gt.ROOT)),
            "search": search["search"],
            "best": search["best"],
            "overflow_witness_found": False,
            "used_as_safety_proof": False,
        },
        "assembly_emitted": False,
        "decision": (
            "range-pass-current-R1U-representative-is-safe-for-the-exact-"
            "N32-producer-contract-native-inverse-assembly-next"
        ),
        "not_claimed": [
            "that the reusable N5/B3 10788 envelope is safe",
            "that every alternative N32 representative schedule is safe",
            "that the incomplete N32 Forward has passed an executable cycle gate",
        ],
        "reopen_representative_only_if": [
            "the executable N32 Forward exceeds the generated branch/k3 bounds",
            "the producer reduction policy changes",
            "a later consumer requires a tighter bound than 26043",
        ],
        "next": [
            "emit the typed half-native IDFT3 plus InvNTT32 assembly using the proved schedule",
            "keep current R1-U finalizer unchanged",
            "benchmark only after a complete executable N32 Forward exists",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUT)
    print("producer_bounds", producer_bounds)
    print("R1U", r1u["maximum_output_abs_bound"])
    print("IDFT3 internal", inverse["global_IDFT3_internal_addsub_abs_bound"])
    print("IDFT3", inverse["global_IDFT3_output_abs_bound"])
    print("stages", [record["max_output_abs_bound"]
                     for record in inverse["global_stage_output_abs_bounds"]])
    print(result["decision"])


if __name__ == "__main__":
    main()
