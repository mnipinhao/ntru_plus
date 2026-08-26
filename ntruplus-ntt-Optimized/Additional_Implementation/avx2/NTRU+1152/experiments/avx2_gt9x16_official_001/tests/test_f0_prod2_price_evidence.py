#!/usr/bin/env python3
"""Check frozen F0-PROD2-MA2-PRICE SUPERCOP-derived evidence."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = (ROOT / "results/f0-prod2-price-supercop-derived-intel155h-20260826-001"
          / "supercop-f0-prod2-serious")
summary = json.loads((RESULT / "stq-summary.json").read_text())
metadata = json.loads((RESULT / "metadata.json").read_text())
audit = summary["linked_movement_audit"]

assert metadata["benchmark_class"] == "supercop-derived-poly-f0-prod2-boundary"
assert metadata["compiler_policy"] == "native-supercop-selection"
assert metadata["frequency_control"]["formal_policy_passed"] is True
assert metadata["fresh_process_launches"] == 9
assert metadata["measure_elf_sha256"] == (
    "a65a884e481ad94a0b80ba313ad8497fdc9683a702ea2fe599d1bbd03862d0b7")

combined = summary["balanced_combined_operations"]
for width in ("1x", "2x"):
    control = combined[f"f0_prod2_{width}_control_cycles"]
    candidate = combined[f"f0_prod2_{width}_candidate_cycles"]
    assert control["observations"] == candidate["observations"] == 1728
    assert candidate["stq2"] < control["stq2"]

paired = summary["balanced_paired_launches"]
assert paired["candidate_1x_faster_launches"] == 9
assert paired["candidate_1x_slower_launches"] == 0
assert paired["candidate_2x_faster_launches"] == 9
assert paired["candidate_2x_slower_launches"] == 0
assert paired["median_1x_candidate_minus_control_cycles"] == -20.0
assert paired["median_2x_candidate_minus_control_cycles"] < -100.0
assert summary["decision"] == {
    "consumer_native_materialization_validated": True,
    "headline": "2x exact-MA2-boundary",
    "kem_promotion_result": False,
    "ma2_arithmetic_executed": False,
}

movement = audit["full_linked_candidate_minus_control"]
assert movement["per_operand"] == {
    "aligned_vector_loads": -144,
    "aligned_vector_stores": -72,
    "projection_calls": -1,
    "projection_returns": -1,
    "vperm2i128": 0,
}
assert movement["two_operands"]["aligned_vector_loads"] == -288
assert movement["two_operands"]["aligned_vector_stores"] == -144
assert movement["two_operands"]["vperm2i128"] == 0
assert movement["cross_lane_work_removed"] is False

for name, record in summary["elf_layout"]["symbols"].items():
    assert record["address_mod32"] == 0, name

print("F0-PROD2-MA2-PRICE: consumer-native boundary wins 1X/2X in 9/9 launches")
