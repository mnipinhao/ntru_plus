#!/usr/bin/env python3
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
proof = json.loads((ROOT / "generated/gt9x16-prod3-aos-branch0.json").read_text())
audit = json.loads((ROOT / "generated/gt9x16-prod3-aos-branch0-audit.json").read_text())

assert proof["checkpoint"] == "GT9X16-PROD3-AOS-BRANCH0"
assert proof["movement"] == {
    "backing_bytes": 1152,
    "data_loads": 72,
    "data_stores": 72,
    "extra_array_bytes": 0,
    "final_stores": 36,
    "intermediate_stores": 36,
    "source_loads": 36,
    "stage_boundary_reloads": 36,
}
assert proof["range_proof"]["all_fit_signed16"] is True
assert proof["range_proof"]["new_reductions"] == 0
assert proof["corrected_static_assumption"]["prior_C1_routes_per_tile"] == 24
assert proof["corrected_static_assumption"]["exact_MA2_routes_per_tile"] == 32

linked = audit["linked"]
assert linked["data_loads"] == linked["data_stores"] == 72
assert linked["routing_total"] == 288
assert linked["montgomery_chains"] == 148
assert linked["barrett_vectors"] == 36
assert linked["calls"] == linked["conditional_branches"] == 0
assert linked["stack_references"] == linked["frame_instructions"] == 0
assert linked["vector_spills"] == linked["vzeroupper"] == 0
assert audit["registers"]["peak_live_ymm"] == 16
assert audit["registers"]["spill_free"] is True
assert audit["overwrite"]["in_place_safe"] is True
assert audit["alignment"]["function_entry_bytes"] == 32
assert audit["alignment"]["rodata_section_alignment_bytes"] >= 32
assert audit["alignment"]["caller_pointer_alignment_required"] is False
assert audit["authorization"] == {
    "benchmark": False,
    "branch0_machine_feasible": True,
    "native_kem": False,
    "second_branch": False,
}
print("GT9X16-PROD3-AOS-BRANCH0 evidence passed")
