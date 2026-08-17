#!/usr/bin/env python3
"""Range/liveness gate for MLKEM-style distributed N32 suffix updates."""

from __future__ import annotations

import json

import generate_tile4 as gt


OUT = gt.GENERATED / "tile4_n32_suffix_mlkstyle_gate.json"


def high_product_bound(input_bound: int) -> int:
    # |signed high16(x*f)| <= ceil(|x*f|/2^16); use the complete centered
    # residue domain, which is a superset of every generated suffix table.
    return (input_bound * (gt.Q // 2) + 65535) // 65536


def correction_bound(input_bound: int) -> int:
    del input_bound
    # The Montgomery low word is an arbitrary signed int16.
    return ((1 << 15) * gt.Q + 65535) // 65536


def stage_record(stage: int, input_bound: int, output_bound: int) -> dict[str, object]:
    high = high_product_bound(input_bound)
    correction = correction_bound(input_bound)
    pre_update = input_bound + high
    final_distributed = pre_update + correction
    return {
        "stage": stage,
        "input_abs_bound": input_bound,
        "factor_domain": [-(gt.Q // 2), gt.Q // 2],
        "high_product_abs_bound": high,
        "correction_abs_bound": correction,
        "distributed_L_plus_or_minus_high_abs_bound": pre_update,
        "distributed_final_conservative_abs_bound": final_distributed,
        "existing_stage_output_abs_bound": output_bound,
        "all_distributed_intermediates_signed_int16_safe":
            final_distributed <= 32767,
    }


def main() -> None:
    stages = [stage_record(4, 8315, 10244), stage_record(5, 10244, 12189)]
    range_safe = all(record["all_distributed_intermediates_signed_int16_safe"]
                     for record in stages)
    result = {
        "schema": "ntruplus768-gt32-n32-suffix-mlkstyle-gate-v1",
        "experiment": "GT-N32-SUFFIX-MLKSTYLE-018",
        "scope": "post-route S4 + S5 + batched center + dual typed DFT3",
        "frozen": {
            "Montgomery_chains": "unchanged",
            "row0_center_count": "unchanged",
            "external_half_native_ABI": "unchanged",
            "S4_to_S5_route_floor": (
                "four instructions per pair from SUFFIX-RESCHEDULE-015"
            ),
        },
        "distributed_update_identity": {
            "sum": "L + (H-C) == (L+H)-C",
            "difference": "L - (H-C) == (L-H)+C",
        },
        "range": stages,
        "register_liveness": {
            "data_input_output_YMM": 6,
            "three_chains_times_L_H_C_YMM": 9,
            "q_YMM": 1,
            "peak_YMM": 16,
            "spill_required": False,
        },
        "static_delta_vs_existing_three_way": {
            "extra_update_instructions_per_stage_iteration": 3,
            "stage_iterations_per_complete_suffix": 8,
            "S4_and_S5_extra_dynamic_instructions": 48,
            "routing_instructions_removed": 0,
            "reason_to_benchmark_despite_count": (
                "correction multiply latency can overlap L+H/L-H"
            ),
        },
        "decision": (
            "range-liveness-pass-emit-bounded-asm-probe" if range_safe
            else "static-stop-distributed-update-range"
        ),
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUT)
    print(result["decision"])


if __name__ == "__main__":
    main()
