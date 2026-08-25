#!/usr/bin/env python3
"""Independent invariants for the generated F0-PROD1 schedule."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "generated/f0-prod1-schedule.json").read_text())

assert data["schema"] == "gt-f0-prod1-schedule/v1"
assert data["checkpoint"] == "F0-PROD1-SCHED"
assert data["frozen_contract"] == {
    "montgomery_r_exponent": 0,
    "physical_p_order": [0, 3, 6, 1, 4, 7, 8, 2, 5],
    "physical_q_order": [0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15],
    "standalone_scale_pass": False,
    "transform_scale": 4,
}

boundary = data["boundary"]
assert boundary["top_split_materialization_bytes"] == 2304
assert boundary["actual_input_alignment_bytes"] == 32
for key in ("official_abi_crossings", "scalar_adapter_calls", "coefficient_adapter_bytes",
            "pair_input_bytes", "pair_output_bytes", "internal_vzeroupper"):
    assert boundary[key] == 0

route = data["direct_load_route"]
assert route["load_map_count"] == 36
assert len(route["load_maps"]) == 36
assert route["loads_per_map"] == 4
assert route["instructions_per_map"]["routing_total"] == 16
assert all(proof["expected_exact"] for proof in route["route_proofs"])
keys = {(row["branch"], row["terminal_pair"], row["input_gt_row"])
        for row in route["load_maps"]}
assert keys == {(branch, pair, row)
                for branch in range(2) for pair in range(2) for row in range(9)}
for row in route["load_maps"]:
    assert row["source_h_row"] == (5 * row["input_gt_row"]) % 9
    assert row["split_base_i16"] % 16 == 0
    assert row["aligned_load_offsets_i16"] == [0, 16, 32, 48]
slots = [slot for row in route["load_maps"] for slot in row["transient_f0_vectors"]]
assert sorted(slots) == list(range(72))

arithmetic = data["arithmetic_schedule"]
assert arithmetic["r2_first_writes_transient_f0"]
assert arithmetic["r2_second_and_d1_overwrite_in_place"]
assert arithmetic["final_materialized_vectors"] == 72
assert arithmetic["d1"]["adjacent_physical_row_pairs"] == [[0, 1], [2, 3], [4, 5], [6, 7]]
assert arithmetic["d1"]["tail_row"] == 8

ranges = data["range_proof"]
assert ranges["actual_coefficient_domain"] == [-1, 1]
assert ranges["domain_subset"] and ranges["unchanged_arithmetic_schedule"]
assert ranges["all_intermediate_ranges_signed_i16"]
assert ranges["ma2_all_preoperations_signed_i16"]
assert ranges["extra_reductions"] == 0

plan = data["register_and_stack_plan"]
assert plan["required_stack_bytes"] == 2304
assert plan["stack_frame_target_max_bytes"] == 2432
assert max(plan["formation_peak_ymm"], plan["r2_cached_peak_ymm"], plan["d1_peak_ymm"]) <= 16
assert plan["spill_target"] == 0
assert plan["leaf_entry_alignment_bytes"] >= 32
assert plan["constant_alignment_bytes"] >= 32
assert data["decision"]["authorized_next"] == "F0-PROD1-ASM P1-H"
assert not data["decision"]["assembly_implemented"]
assert not data["decision"]["kem_benchmark_authorized"]

constants = (ROOT / "generated/f0-prod1-constants.inc").read_text()
assert constants.count(".p2align 5") == 37
assert ".align " not in constants
assert constants.count("_twist:") == 18
assert constants.count("_twist_qinv:") == 18
print("F0-PROD1-SCHED: 36 direct-load maps, 72 transient slots, range/ABI plan passed")
