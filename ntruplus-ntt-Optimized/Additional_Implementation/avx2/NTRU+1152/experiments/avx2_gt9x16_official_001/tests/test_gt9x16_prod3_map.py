#!/usr/bin/env python3
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "generated/gt9x16-prod3-map.json").read_text())

assert data["checkpoint"] == "GT9X16-PROD3-MAP"
assert data["research_boundary"]["official_role"].startswith("performance baseline")
assert data["research_boundary"]["assembly_authorized"] is False
assert data["research_boundary"]["kem_benchmark_authorized"] is False

g0 = data["current_control_G0"]
assert g0["movement_per_forward"]["early_aos_to_soa_routing"] == 576
assert g0["movement_per_forward"]["producer_local_ma2_permutations"] == 72
assert g0["known_routing_total"] == 648

g1 = data["persistent_aos_G1"]
assert len(g1["output_cells"]) == 1152
assert g1["bijection_proof"]["all_equal_1152"] is True
assert g1["arithmetic_compatibility"]["terminal_coefficient_is_passive_dimension"] is True
assert g1["conservative_movement_upper_bound_per_forward"]["aligned_top_split_loads"] == 72
assert g1["conservative_movement_upper_bound_per_forward"]["early_aos_to_soa_routing"] == 0
assert g1["known_delta_vs_G0_before_arithmetic_rescheduling"]["routing_upper_bound"] == -72

assert data["axis_relabel_search_G3"]["candidates_checked"] == 6912
assert data["axis_relabel_search_G3"]["movement_classes_distinguished"] == 1
assert data["sixteen_first_G2"]["all_rows_visit_nine_materialized_h_rows"] is True
assert data["sixteen_first_G2"]["current_four_aligned_load_geometry_preserved"] is False
assert data["twist_scale_search_G4"]["checks"] == 288
assert data["twist_scale_search_G4"]["lower_chain_count_proved"] is False

selection = data["selection"]
assert selection["selected_next"] == "GT9X16-PROD3-AOS-SCHED"
assert selection["assembly_authorized"] is False
assert selection["benchmark_authorized"] is False
assert selection["native_kem_authorized"] is False
print("GT9X16-PROD3-MAP evidence passed")
