#!/usr/bin/env python3
"""Generate the bounded AVX2 physical-execution gate for N32-first."""

from __future__ import annotations

import json

import generate_tile4 as gt


OUT = gt.GENERATED / "tile4_n32_physical_schedule_gate.json"


def main() -> None:
    native = json.loads(
        (gt.GENERATED / "tile4_n32_gt_pfa_native_gate.json").read_text())
    wave = json.loads(
        (gt.GENERATED / "tile4_n32_gt_wave_producer_gate.json").read_text())
    stage1_inputs = [
        branch["stages"][0]["input_abs_bound"]
        for branch in native["range_proof"]["branches"]
    ]
    destructive_double_bound = 2 * max(stage1_inputs)
    assert destructive_double_bound == 3598
    assert destructive_double_bound < 32768
    assert not wave["register_observation_not_lower_bound"][
        "q_or_factor_registers_counted"]

    result = {
        "schema": "ntruplus768-gt32-n32-physical-schedule-v1",
        "experiment": "GT-N32-PHYSICAL-SCHEDULE-005",
        "frozen": {
            "coordinate_B": 33,
            "Montgomery_chains": 160,
            "terminal": "five-blend half-native",
            "BM": "half-native R1-U",
        },
        "q_memory_operand": {
            "AVX2_encoding_valid": True,
            "actual_current_N5_uses_q_register": True,
            "prior_17_YMM_estimate_counted_q_register": False,
            "therefore_solves_prior_estimate_alone": False,
            "role": "required implementation tool for one-temp schedules",
        },
        "destructive_S1": {
            "formula": ["a=a+b", "b=2*b", "b=a-b"],
            "instructions_per_butterfly": 3,
            "temporary_YMM": 0,
            "input_abs_bounds": stage1_inputs,
            "temporary_double_abs_bound": destructive_double_bound,
            "signed_int16_safe": True,
            "same_instruction_count_as_sub-add-move": True,
            "tradeoff": "longer dependency chain",
        },
        "candidates": {
            "R0": {
                "shape": "16 resident plus current Montgomery temp",
                "status": "artificial-cut-not-allocatable-with-current-multiply",
            },
            "R1": {
                "shape": "15 resident plus deferred branch vector",
                "status": "32-byte claim not established",
                "direct_reconstruction": {
                    "source_vectors_needed": ["low", "high"],
                    "extra_source_bytes_per_wave": 64,
                    "extra_source_bytes_per_Forward": 192,
                    "extra_work": "one repeated raw top product plus branch twist",
                },
                "one_high_YMM_alternative":
                    "requires retained sibling state or two fixed-factor products",
            },
            "R2": {
                "shape": "128-bit half spill",
                "status_at_S1_S3_cut": "does-not-free-a-YMM",
                "reason": "the unspilled half still occupies the architectural register; packing two live halves adds a routing operation",
                "reopen": "suffix-only half-typed frontier",
            },
            "R3": {
                "shape": "one full-YMM controlled spill per n3 wave",
                "register_schedule": [
                    "form first seven branch pairs: 14 data YMM",
                    "spill one already formed branch-1 vector: 13 resident",
                    "form final pair with two outputs plus one temp: peak 16",
                    "destructive S1 on branch 0: zero temp",
                    "serial one-temp S2/S3 with q memory operand",
                    "store branch 0 and free eight YMM",
                    "reload spilled branch-1 vector",
                    "parallel S1/S2/S3 on branch 1",
                ],
                "peak_YMM": 16,
                "spill_store_load_instructions_per_wave": 2,
                "spill_bytes_per_wave": 64,
                "spill_bytes_per_Forward": 192,
                "schedule_proved_for_preformed_wave": True,
                "source_formation_full_schedule": "pending generated frontend",
                "assembly_symbol": "gt32_n32_wave_s1s3_c2_asm",
            },
            "R4": {
                "shape": "14-15 resident with more reloads",
                "status": "defer unless R3 serial first-branch cost is prohibitive",
            },
            "R5": {
                "shape": "DFT3 output immediately consumed by R1-U",
                "status": "BM ABI passed; combined allocation pending",
                "potential_boundary_removed_bytes": 3072,
                "warning": "single-vector R1-U must use compact code and memory-sourced masks to coexist with suffix state",
            },
        },
        "wave_microbenchmark": {
            "control": "two materialized 8-YMM branches, parallel S1-S3",
            "candidate": "16 live YMM, one controlled spill, destructive S1, serial first-branch S2/S3, parallel second branch",
            "semantic_endpoint": "identical post-S3 16-vector state",
            "assembly_emitted": True,
            "purpose": "measure register-pressure execution tax, not full Forward",
        },
        "decision": "emit-R3-wave-probe-R1-96B-and-R2-half-spill-not-established",
        "full_island_qualified": False,
        "next": [
            "run exact and short paired wave benchmark",
            "continue full producer only if R3 penalty is small enough to repay the 16-blend 2F saving",
            "then allocate suffix-to-single-vector-R1U immediate consumer",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUT)
    print(result["decision"])


if __name__ == "__main__":
    main()
