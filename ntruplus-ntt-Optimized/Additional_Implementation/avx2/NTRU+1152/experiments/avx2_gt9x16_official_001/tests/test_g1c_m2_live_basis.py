#!/usr/bin/env python3
"""Validate the G1C-M2 live-basis graph and scoped mechanical bound."""

import json
from pathlib import Path

experiment = Path(__file__).resolve().parents[1]
solve = json.loads((experiment / "generated/g1c-m2-live-basis.json").read_text())

assert solve["schema"] == "gt-g1c-m2-live-basis/v1"
graph = solve["live_graph"]
assert graph["early_cutpoint"]["results"] == {
    "ymm5": "c0", "ymm6": "c1", "ymm7": "c2"}
assert graph["late_c3_cutpoint"]["result"] == {"ymm1": "c3"}
assert graph["early_cutpoint"]["cheap_nonfinal_intermediates"] == []
assert "adjacent physical q lanes" in graph["lane_dependency"]["inverse_distance1"]
assert "not the inverse-head" in graph["lane_dependency"]["terminal_coefficient_pairing"]

bound = solve["mechanical_solve"]
assert sum(item["minimum"] for item in bound["required_operations"]) == 8
assert bound["minimum_instructions_per_c_vector"] == 8
assert bound["minimum_instructions_per_row"] == 32
assert bound["current_c2_l_realizes_bound"] is True

alternatives = solve["alternatives"]
assert alternatives["M2-split-after-D1"]["instructions_per_c_vector_before_storage"] == 7
assert alternatives["M2-split-after-D1"]["unpacked_stores_per_row"] == 8
assert alternatives["M2-earlier-partial-products"]["status"] == "rejected-for-head-only"
assert solve["materialized_control"]["extra_memory_instructions_vs_C2_L"] == 144
assert solve["decision"]["full_inverse16_split_state_remains_open"] is True
assert solve["decision"]["cycles"] is None
print("G1C-M2 live basis: lane-separable DAG, scoped 8-instruction bound, split full-inverse path retained")
