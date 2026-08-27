#!/usr/bin/env python3
"""Regression checks for the map-only Q-order co-design checkpoint."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "generated/gt9x16-prod3-ma2-qorder-codesign.json").read_text())

assert DATA["schema"] == "gt9x16-prod3-ma2-qorder-codesign/v1"
assert DATA["scope"]["candidate_count"] == 384
assert not DATA["scope"]["arithmetic_changed"]
assert not DATA["scope"]["asm_authorized"]
assert not DATA["scope"]["benchmark_authorized"]

candidates = DATA["candidates"]
orders = {tuple(item["lane_to_semantic_q"]) for item in candidates}
assert len(candidates) == len(orders) == 384
assert all(sorted(order) == list(range(16)) for order in orders)

current = DATA["baselines"]["current"]
natural = DATA["baselines"]["natural_C1"]
assert current["producer"]["routes_per_forward"] == 144
assert current["H1"]["source_half_groups"] == 136
assert current["H1"]["coefficient_routes"] == 336
assert current["H1"]["data_loads"] == 272
assert current["H1"]["pack_transpose_routes"] == 324
assert natural["producer"]["routes_per_forward"] == 0
assert natural["H1"]["coefficient_routes"] == 360
assert natural["H1"]["data_loads"] == 288

assert DATA["linked_current_calibration"]["resident_h_projection_routes"] == 288
assert DATA["pareto"]["current_is_pareto_optimal"]
assert DATA["pareto"]["frontier_count"] == 33
assert len(DATA["pareto"]["cost_profiles"]) == 2
assert not DATA["decision"]["H2_old_256_and_1086_reused"]
assert all(item["H2"]["same_ma2_vector"] == 0 for item in candidates)
assert all(item["H2"]["cross_ma2_vector"] == 576 for item in candidates)
assert all(item["H2"]["h2_96_route_estimate"] is None for item in candidates)

print("GT9x16 PROD3/MA2 Q-order co-design regression: ok")
