#!/usr/bin/env python3
"""Lock D0-M2 serious SUPERCOP-derived attribution evidence."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = (ROOT / "results/itail-d0-m2-supercop-derived-intel155h-20260824-001"
          / "supercop-itail-d0-m2-serious")
summary = json.loads((RESULT / "stq-summary.json").read_text())
metadata = json.loads((RESULT / "metadata.json").read_text())

combined = summary["balanced_combined_operations"]
for variant in ("m0", "m1", "m2"):
    assert combined[f"inverse_tail_d0_{variant}_cycles"]["observations"] == 2592
assert combined["inverse_tail_d0_m2_cycles"]["stq2"] > combined["inverse_tail_d0_m0_cycles"]["stq2"]
assert combined["inverse_tail_d0_m2_cycles"]["stq2"] < combined["inverse_tail_d0_m1_cycles"]["stq2"]

paired = summary["balanced_paired_launches"]
assert len(paired["launches"]) == 9
assert paired["m2_slower_than_m0_launches"] == 9
assert paired["m2_faster_than_m0_launches"] == 0
assert paired["m2_faster_than_m1_launches"] == 9
assert paired["median_m2_minus_m0_cycles"] > 150
assert paired["median_m2_minus_m1_cycles"] < -210

assert metadata["benchmark_class"] == "supercop-derived-itail-d0-m2"
assert metadata["version"] == "20260627"
assert metadata["frequency_control"]["formal_policy_passed"]
assert metadata["compiler_policy"] == "fixed-common"
assert (RESULT / "measure").is_file()
print("ITAIL-D0-M2 evidence: M2 loses to M0 9/9 and beats M1 9/9; parent fusion closed")
