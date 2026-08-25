#!/usr/bin/env python3
"""Independently gate F0-MA-SCHED topology, ranges, and selection."""

import json
import math
from collections import defaultdict
from pathlib import Path

Q = 3457
ROOT = Path(__file__).resolve().parents[1]
schedule = json.loads((ROOT / "generated/f0-ma-schedule.json").read_text())
consumer = json.loads((ROOT / "generated/f0-ma-consumer-map.json").read_text())

assert schedule["schema"] == "gt-f0-ma-schedule/v1"
assert schedule["decision"] == {
    "assembly_candidates": ["MA1", "MA3"],
    "assembly_implemented": False,
    "control": "MA0",
    "deferred": ["MA2"],
    "performance_claim": False,
    "primary_future_benchmark":
        "F0(r)+F0(m)+resident-h projection+MulAdd+inv4 finalizer+poly_tobytes",
    "schedule_proof_complete": True,
}

expected_pairs = {
    0: {(0, 4), (0, 7)}, 1: {(0, 0), (0, 1)},
    2: {(0, 3), (0, 6)}, 3: {(0, 2), (0, 8)},
    4: {(0, 5), (1, 3)}, 5: {(1, 0), (1, 6)},
    6: {(1, 2), (1, 5)}, 7: {(1, 7), (1, 8)},
    8: {(1, 1), (1, 4)},
}
for chunk in schedule["official_chunk_pairing"]:
    index = chunk["official_chunk"]
    assert {(tile["branch"], tile["p"]) for tile in chunk["semantic_tiles"]} == \
        expected_pairs[index]
    assert chunk["resident_h_projection"]["routing_total"] == 16
    assert chunk["serializer_inverse_projection"]["routing_total"] == 16

owners = defaultdict(dict)
for vector in consumer["f0_vectors"]:
    for lane in vector["lanes"]:
        owner = lane["semantic_owner"]
        owners[(owner["branch"], owner["p"],
                owner["terminal_coefficient"])][lane["physical_q_lane"]] = lane

seen = set()
for tile in schedule["semantic_tiles"]:
    identity = tile["tile"]
    for plane in tile["planes"]:
        key = (identity["branch"], identity["p"], plane["coefficient"])
        expected = [owners[key][lane] for lane in
                    schedule["physical_schedule"]["coefficient_plane_lane_order"]]
        assert plane["f0_positions_i16"] == [lane["f0_position_i16"] for lane in expected]
        assert plane["resident_h_official_positions_i16"] == \
            [lane["official_position_i16"] for lane in expected]
        for lane in expected:
            owner = lane["semantic_owner"]
            seen.add((owner["branch"], owner["p"], owner["q"],
                      owner["terminal_coefficient"]))
assert len(seen) == 1152

pairing = schedule["ma1_pairing_proof"]
assert pairing["native_terminal_half_pairs"] == [[0, 1], [2, 3]]
assert pairing["minimum_operand_half_routes_per_stream"] == 12
assert pairing["full_bilinear_operand_routes"] == 432
assert [item["minimum_operand_half_routes_per_stream"]
        for item in pairing["pairings"]] == [6, 6]
for item in pairing["pairings"]:
    assert len(item["paired_terms"]) == 4
    assert sum(not term["h_pair_native"] for term in item["paired_terms"]) + \
        sum(not term["r_pair_native"] for term in item["paired_terms"]) == 6

def mont(left, right):
    products = [a * b for a in left for b in right]
    hi = [math.floor(min(products) / 65536),
          math.floor(max(products) / 65536)]
    correction = [math.floor((-32768 * Q) / 65536),
                  math.floor((32767 * Q) / 65536)]
    return [hi[0] - correction[1], hi[1] - correction[0]]

ranges = schedule["range_proof"]
assert mont([-1728, 1728], [-1728, 1728]) == [-1774, 1774]
assert mont([-3456, 3456], [-3456, 3456]) == [-1911, 1911]
assert ranges["montgomery_product_centered_inputs"] == [-1774, 1774]
assert ranges["montgomery_product_pair_sums"] == [-1911, 1911]
for item in ranges["ma2_outputs"]:
    low, high = item["with_centered_m_addend_pre_final_center"]
    assert -32768 <= low <= high <= 32767
for bound in [ranges["ma3"]["quadratic_first_precenter"],
              ranges["ma3"]["quadratic_second_precenter"],
              ranges["ma3"]["cross_precenter"],
              *ranges["ma3"]["final_outputs_precenter"]]:
    assert -32768 <= bound[0] <= bound[1] <= 32767

candidates = {candidate["id"]: candidate for candidate in schedule["candidates"]}
assert candidates["MA1"]["liveness"]["peak_ymm"] == 14
assert candidates["MA2"]["routing_full_1152"]["total"] == 432
assert candidates["MA3"]["routing_full_1152"]["total"] == 432
assert candidates["MA2"]["vector_montgomery_chains_per_tile"] == 19
assert candidates["MA3"]["vector_montgomery_chains_per_tile"] == 13
assert candidates["MA3"]["liveness"]["peak_ymm"] == 15
assert candidates["MA3"]["liveness"]["rank_products_live_together"] is False

scale = schedule["scale_gauge_search"]
assert scale["selected"] == "S0-output-finalizer"
assert scale["inv4_mod_q"] == 2593
assert [variant["runtime_inv4_vector_chains_full_1152"]
        for variant in scale["variants"]] == [72, 144, 144]
alignment = schedule["alignment_contract"]
assert alignment["asm_entry"] == ".p2align 5"
assert alignment["poly_pointer_alignment_bytes"] == 32
assert alignment["ciphertext_pointer_alignment"].startswith("unconstrained")

print("F0-MA-SCHED: 9 chunk pairs, 1,152 owners, range/scale/liveness and MA1+MA3 authorization passed")
