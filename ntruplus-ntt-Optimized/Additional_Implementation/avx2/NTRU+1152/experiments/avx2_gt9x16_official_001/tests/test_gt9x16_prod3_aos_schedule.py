#!/usr/bin/env python3
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "generated/gt9x16-prod3-aos-schedule.json").read_text())

assert data["checkpoint"] == "GT9X16-PROD3-AOS-SCHED"
assert data["frozen_contract"]["cross_axis_wavefront"] is False
assert data["frozen_contract"]["twist_absorption"] is False

step_a = data["step_A_aos_ntt9"]
assert step_a["vector_streams"] == 8
assert step_a["montgomery_chains"] == 80
assert step_a["barrett_vectors"] == 72
assert step_a["routing"] == 0

step_b = data["step_B_aos_d8_d4"]
assert step_b["distance8_montgomery_chains"] == 36
assert step_b["distance4_montgomery_chains"] == 36
assert step_b["routing"] == 0

step_c = data["step_C_networks"]
assert step_c["lane_coverage_proof"] == {
    "distance1": 576, "distance2": 576, "ma2_cells": 1152}
assert step_c["C0_materialized_post_d1"]["full_forward_routing"] == 432
assert step_c["C0_materialized_post_d1"]["full_forward_boundary_stores"] == 72
assert step_c["C1_live_d1_to_transpose"]["full_forward_routing"] == 432
assert step_c["C1_live_d1_to_transpose"]["full_forward_boundary_stores"] == 0
assert step_c["C1_live_d1_to_transpose"]["selected"] is True
assert step_c["C2_early_plane_orientation"]["full_forward_routing"] == 792
assert step_c["C2_early_plane_orientation"]["selected"] is False

twist = data["step_D_twist_ledger"]
assert twist["T0_control"]["pre_twist_montgomery_chains"] == 72
assert twist["T1_h_factor_into_ntt9"]["one_montgomery_multiplication_removed_proved"] is False
assert twist["T2_q_factor_into_ntt16"]["one_montgomery_multiplication_removed_proved"] is False

ledger = data["apples_to_apples_ledger"]
assert ledger["routing_taxonomy_reconciliation"] == {
    "explanation": "648 was the MAP checkpoint's deliberately incomplete known-boundary count; 936 adds the 288 linked adjusted-NTT16 internal routes so both control and C1 include their radix-2 routing",
    "full_linked_control_total": 936,
    "map_excluded_open_variable": {
        "adjusted_ntt16_internal_D8_D4_D2_D1": 288},
    "map_included": {"P2B_epilogue": 72, "early_formation": 576},
    "map_known_total": 648,
}
assert ledger["G0_P2B"]["routing_total"] == 936
assert ledger["AOS_C1"]["routing_total"] == 432
assert ledger["AOS_C1_minus_G0"] == {
    "barrett_vectors": 0,
    "data_loads_after_top_split": -72,
    "data_stores_after_top_split": 0,
    "montgomery_chains": 0,
    "routing_total": -504,
}

decision = data["decision"]
assert decision["selected_network"] == "C1_live_d1_to_transpose"
assert decision["asm_authorized"] is False
assert decision["full_producer_asm_authorized"] is False
assert decision["benchmark_authorized"] is False
assert decision["cross_axis_wavefront_authorized"] is False
assert decision["twist_absorption_authorized"] is False
assert decision["native_kem_authorized"] is False
print("GT9X16-PROD3-AOS-SCHED evidence passed")
