#!/usr/bin/env python3
"""Regression checks for current-Q versus natural-Q exact schedules."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "generated/gt9x16-prod3-ma2-qorder-natural-schedule.json").read_text())

assert DATA["schema"] == "gt9x16-prod3-ma2-qorder-natural-schedule/v1"
assert DATA["scope"]["encap_multiplicity"] == {
    "producer": 2, "resident_h": 1, "H1_hash_r": 1
}
assert not DATA["scope"]["arithmetic_changed"]
assert not DATA["scope"]["asm_implemented"]
assert not DATA["scope"]["benchmark_run"]

producer = DATA["producer"]
assert producer["current"]["routes_per_forward"] == 144
assert producer["current"]["routes_per_encap"] == 288
assert producer["natural"]["routes_per_forward"] == 0
assert producer["natural"]["routes_per_encap"] == 0

current_h = DATA["resident_h"]["current_linked"]
natural_h = DATA["resident_h"]["natural_exact_schedule"]
assert current_h["data_loads"] == natural_h["data_loads"] == 144
assert current_h["routing_total"] == 288
assert natural_h["routing_total"] == 360
assert natural_h["scratch_bytes"] == 0
assert natural_h["full_ma2_peak_ymm_upper_bound"] == 15
assert len(DATA["resident_h"]["natural_plans"]) == 72

current_h1 = DATA["H1"]["current_linked"]
natural_h1 = DATA["H1"]["natural_exact_schedule"]
assert current_h1["data_loads"] == 272
assert current_h1["coefficient_routes"] == 336
assert natural_h1["data_loads"] == 288
assert natural_h1["coefficient_routes"] == 360
assert current_h1["pack_transpose_routes"] == natural_h1["pack_transpose_routes"] == 324
assert len(DATA["H1"]["natural_plans"]) == 72

delta = DATA["caller_weighted"]["natural_minus_current"]
assert delta["producer_routes_per_encap"] == -288
assert delta["resident_h_routes_per_encap"] == 72
assert delta["H1_coefficient_routes_per_encap"] == 24
assert delta["H1_data_loads_per_encap"] == 16
assert delta["all_caller_weighted_routes"] == -192
assert delta["all_caller_weighted_data_loads"] == 16

assert DATA["H2_v1"]["status"] == "rejected"
assert not DATA["H2_v1"]["old_256_cross_half_reused"]
assert not DATA["H2_v1"]["old_72_load_lower_bound_reused"]
assert not DATA["H2_v1"]["old_1086_route_estimate_reused"]
assert DATA["decision"]["Qorder_search_closed"]
assert DATA["decision"]["asm_authorized_next"]
assert not DATA["decision"]["benchmark_authorized"]

print("GT9x16 current-Q/natural-Q exact schedule regression: ok")
