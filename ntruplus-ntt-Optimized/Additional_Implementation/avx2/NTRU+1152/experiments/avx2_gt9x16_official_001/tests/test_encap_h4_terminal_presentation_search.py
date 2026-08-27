#!/usr/bin/env python3
"""Regression gates for H4-M1 terminal presentation search."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
report = json.loads(
    (ROOT / "generated/encap-h4-terminal-presentation-search.json").read_text())

assert report["schema"] == "encap-h4-terminal-presentation-search/v1"
edges = report["pairing_graph"]["edge_classes"]
assert edges == {
    "same_vector": 0,
    "same_lane_cross_vector": 576,
    "different_lane_cross_vector": 0,
    "adjacent_terminal": 576,
}
assert report["lower_bounds"] == {
    "R_pair_min": 0,
    "P_max_min_coefficients": 16,
    "Y_buffer_min": 1,
    "terminal_materialization_bytes_min": 0,
    "current_h1_336_coefficient_routes_are_not_a_pair_join_lower_bound": True,
}
planes = report["plane_emission_search"]
assert planes["candidates_exhausted"] == 24
assert len(planes["optimal_orders"]) == 8
assert planes["current_order_is_optimal"]

tiles = report["tile_emission_search"]
assert tiles["candidates_exhausted"] == 512
assert tiles["current_out_of_order_96byte_tile_pairs"] == 6
assert tiles["minimum_out_of_order_96byte_tile_pairs"] == 0

profiles = report["lane_orientation_search"]["profile_frontier"]
assert [item["profile"] for item in profiles] == [
    [0, 512, 16], [72, 492, 16], [144, 376, 16], [216, 36, 16]
]
assert len(report["lane_orientation_search"]
           ["tile_sorted_exact_existence_proofs"]) == 18
assert report["decision"]["m1_complete"]
assert report["decision"]["m1_lane_winner"] is None
assert len(report["decision"]["m2_profile_representatives"]) == 4
assert not report["decision"]["asm_authorized"]
print("H4-M1 terminal presentation search: PASS")
