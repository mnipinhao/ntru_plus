#!/usr/bin/env python3
"""Lock the ITAIL-D0 pre-assembly liveness and cross-boundary range proof."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
proof = json.loads((ROOT / "generated/g1c-inverse-tail-d0-proof.json").read_text())

assert proof["decision"]["proof_passed"]
assert proof["decision"]["linked_asm_authorized"]
assert proof["wavefront"]["physical_p_triads"] == [[0, 3, 6], [1, 4, 7], [8, 2, 5]]
assert proof["wavefront"]["physical_row_index_triads"] == [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
assert proof["wavefront"]["same_arithmetic_dag"]
assert proof["wavefront"]["removed_boundary_if_linked"] == {
    "d8_stores": 72, "b1_reloads": 72}
assert proof["range_chain"]["d8_output_union"] == [-17377, 17377]
assert proof["range_chain"]["d8_output_union"] == proof["range_chain"]["b1_input_contract"]
assert proof["range_chain"]["b1_all_pre_operations_fit_signed_i16"]
assert proof["range_chain"]["scale_in"] == "R^-1"
registers = proof["register_contract"]
assert registers["proved_peak_live_ymm"] <= registers["architectural_ymm"] == 16
assert not registers["spill_required"]
assert len(registers["instruction_by_instruction"]) == registers["instruction_count_one_wavefront"]
assert all(len(item["live_before"]) <= 16 and len(item["live_after"]) <= 16
           for item in registers["instruction_by_instruction"])
print(f"ITAIL-D0 proof: same DAG, exact range chain, peak {registers['proved_peak_live_ymm']}/16 YMM passed")
