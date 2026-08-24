#!/usr/bin/env python3
"""Lock the D0-M2 late-layer register and range proof."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
proof = json.loads((ROOT / "generated/g1c-inverse-tail-d0-m2-proof.json").read_text())

assert proof["checkpoint"] == "G1C-ITAIL-D0-M2"
assert proof["decision"]["proof_passed"]
assert proof["decision"]["linked_asm_authorized"]
assert proof["wavefront"]["same_arithmetic_dag"]
assert proof["wavefront"]["removed_boundary_if_linked"] == {
    "d8_stores": 72, "b1_reloads": 72}
assert proof["range_chain"]["d8_output_union"] == [-17377, 17377]
assert proof["range_chain"]["d8_output_union"] == proof["range_chain"]["b1_input_contract"]
assert proof["range_chain"]["b1_all_pre_operations_fit_signed_i16"]
registers = proof["register_contract"]
assert registers["proved_peak_live_ymm"] == 14
assert registers["proved_peak_live_ymm"] <= registers["architectural_ymm"] == 16
assert not registers["spill_required"]
assert all(len(item["live_before"]) <= 16 and len(item["live_after"]) <= 16
           for item in registers["instruction_by_instruction"])
print("ITAIL-D0-M2 proof: late-layer schedule, exact range chain, peak 14/16 YMM passed")
