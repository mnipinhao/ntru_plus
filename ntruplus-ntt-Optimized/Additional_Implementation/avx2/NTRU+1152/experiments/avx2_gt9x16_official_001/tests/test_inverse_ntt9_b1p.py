#!/usr/bin/env python3
"""Gate the exhaustive ITAIL-B1P phase/orientation result."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "generated/g1c-inverse-ntt9-b1p.json").read_text())

assert data["schema"] == "ntruplus1152-itail-b1p/v1"
assert data["forward_gauge"]["depends_only_on_p"]
assert data["forward_gauge"]["independent_of_q_and_terminal_j"]
assert data["forward_gauge"]["identity"]
assert data["forward_gauge"]["base_mul_squared_exponents"] == [0] * 9
assert data["search"]["candidate_count"] == 729
assert len(data["search"]["cases"]) == 729
assert data["search"]["exact_natural_output_candidates"] == 27
assert data["search"]["bmscale_exact_output_candidates"] == 27
assert data["lower_bound"]["minimum_nontrivial_interstage_chains"] == 4
assert data["lower_bound"]["minimum_total_montgomery_chains"] == 10
assert data["lower_bound"]["minimum_distinct_interstage_constants"] == 2
assert data["lower_bound"]["proved_over_all_729_with_output_gauge_allowed"]
assert len(data["shortlist_for_B1R"]) == 3
assert data["decision"]["selected_control"] == [0, 0, 0, 0, 0, 0]
assert not data["decision"]["assembly_authorized"]

for candidate in data["shortlist_for_B1R"]:
    p1 = candidate["P1_inverse_constants_exact_output"]
    assert candidate["zero_runtime_permutation"]
    assert p1["interstage_nontrivial_chains"] == 4
    assert p1["distinct_interstage_nontrivial_constants"] == 2
    assert p1["montgomery_chains_including_six_kappa"] == 10
    assert p1["estimated_peak_ymm_if_B0_schedule_is_retained"] == 15
    assert p1["runtime_lane_or_register_permutations"] == 0
    assert p1["exact_range_status"] == "deferred-to-ITAIL-B1R"

print("ITAIL-B1P: identity Forward gauge, 729 orientations, four-chain lower bound, and three-way B1R shortlist passed")
