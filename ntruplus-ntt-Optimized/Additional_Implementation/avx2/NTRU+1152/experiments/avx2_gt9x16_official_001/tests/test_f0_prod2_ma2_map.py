#!/usr/bin/env python3
"""Check the exact PROD2 D1-output to MA2-native ownership/movement map."""

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
mapping = json.loads((ROOT / "generated/f0-prod2-ma2-map.json").read_text())

assert mapping["schema"] == "gt-f0-prod2-ma2-map/v1"
proof = mapping["bijection_proof"]
assert proof == {
    "all_equal_1152": True,
    "d1_source_cells": 1152,
    "ma2_destination_cells": 1152,
    "plane_count": 72,
    "semantic_owners": 1152,
    "serializer_chunks": 9,
    "tiles": 18,
}

source = set()
destination = set()
owners = set()
plane_lanes = defaultdict(list)
for cell in mapping["d1_to_ma2_cells"]:
    producer = cell["producer"]
    consumer = cell["consumer"]
    owner = cell["semantic_owner"]
    source.add((producer["d1_vector"], producer["d1_packed_lane"]))
    destination.add((consumer["ma2_native_vector"],
                     consumer["ma2_native_packed_lane"]))
    owners.add((owner["branch"], owner["p"], owner["q"],
                owner["terminal_coefficient"]))
    plane_lanes[consumer["ma2_native_vector"]].append(
        (consumer["ma2_native_packed_lane"], producer["physical_q_lane"],
         owner["terminal_coefficient"]))
    assert cell["scale"] == {"montgomery_r_exponent": 0, "transform": 4}
    assert -32768 <= cell["range_i16"][0] <= cell["range_i16"][1] <= 32767

assert len(source) == len(destination) == len(owners) == 1152
expected_lanes = list(range(0, 16, 2)) + list(range(1, 16, 2))
for lanes in plane_lanes.values():
    lanes.sort()
    assert [physical for _, physical, _ in lanes] == expected_lanes
    assert len({coefficient for _, _, coefficient in lanes}) == 1

search = mapping["realization_search"]
assert search["P2-A-store-address-only"]["feasible"] is False
assert search["P2-A-store-address-only"]["whole_d1_vectors_matching_one_ma2_plane"] == 0
assert search["P2-B-local-d1-epilogue"] == {
    "aligned_plane_stores_per_forward": 72,
    "extra_temporary_bytes": 0,
    "feasible": True,
    "same_pair_slots_overwritten_after_both_sources_are_live": True,
    "selected": True,
    "vperm2i128_per_forward": 72,
    "vperm2i128_per_plane": 1,
    "vperm2i128_per_tile": 4,
}
assert search["P2-C-chunk-oriented-schedule"]["selected"] is False

movement = mapping["movement_accounting"]
assert movement["P1-H-generic-F0-to-current-MA2"]["generic_f0_loads_into_ma2"] == 144
assert movement["PROD2-P2-B-to-MA2-native"]["ma2_native_plane_reloads"] == 72
assert movement["P2-B-minus-control"]["generic_f0_loads_into_ma2"] == -144
assert movement["P2-B-minus-control"]["ma2_native_plane_reloads"] == 72
assert movement["net_boundary_instruction_delta_per_operand"] == -72
assert movement["net_boundary_instruction_delta_two_operands"] == -144

assert mapping["transient_storage"]["r2_first_can_reuse_ma2_native_backing"] is True
assert mapping["transient_storage"]["additional_transient_bytes"] == 0
decision = mapping["decision"]
assert decision["selected_realization"] == "P2-B-local-d1-epilogue"
assert decision["asm0_authorized"] is True
assert decision["kem_benchmark_authorized"] is False
assert decision["resident_h_changes_authorized"] is False
assert decision["top_split_fusion_authorized"] is False

print("F0-PROD2-MA2-MAP: 1152-cell P2-B plane map and -144 two-operand load credit passed")
