#!/usr/bin/env python3
"""Check frozen ITAIL-ASM-B1 proof, audit, and SUPERCOP-derived evidence."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
proof = json.loads((ROOT / "generated/g1c-inverse-ntt9-b1r.json").read_text())
audit = json.loads((ROOT / "generated/g1c-inverse-ntt9-b1-audit.json").read_text())
result_root = (ROOT / "results/itail-asm-b1-supercop-derived-intel155h-20260824-003"
               / "supercop-itail-serious")
summary = json.loads((result_root / "stq-summary.json").read_text())
metadata = json.loads((result_root / "metadata.json").read_text())

assert proof["selection"]["minimum_interstage_barrett_wires"] == [0, 3, 6]
assert proof["selection"]["remove_B0_barrett_wires"] == [1, 2]
assert audit["delta_vs_B0"] == {"vpmulhrsw": -16, "vpmullw": -16, "vpsubw": -16}
assert audit["linked_instruction_count"] == audit["expected_linked_instruction_count"]
assert audit["montgomery_chain_count"]["eight_vector_inverse9_body"] == 80
assert audit["liveness"] == {
    "peak_live_ymm": 15, "stack_spills": 0, "unchanged_vs_B0": True}
assert all(audit["gates"].values())

balanced = summary["balanced_combined_operations"]
assert balanced["inverse_ntt9_b0_cycles"]["observations"] == 1728
assert balanced["inverse_ntt9_b1_cycles"]["observations"] == 1728
assert balanced["inverse_ntt9_b1_cycles"]["stq2"] < balanced["inverse_ntt9_b0_cycles"]["stq2"]
paired = summary["balanced_paired_launches"]
assert paired["b1_faster_launches"] == 9
assert paired["b1_slower_launches"] == 0
assert paired["median_b1_minus_b0_cycles"] < 0
assert metadata["benchmark_class"] == "supercop-derived-itail"
assert metadata["compiler_policy"] == "fixed-common"
assert metadata["frequency_control"]["formal_policy_passed"]
assert metadata["version"] == "20260627"
print("ITAIL-ASM-B1: exact -48-instruction delta and SUPERCOP-derived 9/9 win passed")
