#!/usr/bin/env python3
"""Lock ITAIL-D0 proof, object audit, and SUPERCOP-derived rejection."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
proof = json.loads((ROOT / "generated/g1c-inverse-tail-d0-proof.json").read_text())
audit = json.loads((ROOT / "generated/g1c-inverse-tail-d0-audit.json").read_text())
result_root = (ROOT / "results/itail-d0-supercop-derived-intel155h-20260824-001"
               / "supercop-itail-d0-serious")
summary = json.loads((result_root / "stq-summary.json").read_text())
metadata = json.loads((result_root / "metadata.json").read_text())

assert proof["decision"]["proof_passed"]
assert proof["register_contract"]["proved_peak_live_ymm"] == 14
assert proof["range_chain"]["d8_output_union"] == [-17377, 17377]
assert proof["range_chain"]["d8_output_union"] == proof["range_chain"]["b1_input_contract"]
assert all(audit["gates"].values())
assert audit["delta_M1_minus_M0"] == {
    "boundary_reloads": -72, "output_stores": -72, "static_instructions": -144}
combined = summary["balanced_combined_operations"]
assert combined["inverse_tail_d0_m0_cycles"]["observations"] == 1728
assert combined["inverse_tail_d0_m1_cycles"]["observations"] == 1728
assert combined["inverse_tail_d0_m1_cycles"]["stq2"] > combined["inverse_tail_d0_m0_cycles"]["stq2"]
paired = summary["balanced_paired_launches"]
assert paired["m1_faster_launches"] == 0
assert paired["m1_slower_launches"] == 9
assert paired["median_m1_minus_m0_cycles"] > 0
assert metadata["benchmark_class"] == "supercop-derived-itail-d0"
assert metadata["compiler_policy"] == "fixed-common"
assert metadata["frequency_control"]["formal_policy_passed"]
assert metadata["version"] == "20260627"
print("ITAIL-D0: 14-YMM proof and exact -144 instructions pass; M1 +365.29 cycles loses 9/9")
