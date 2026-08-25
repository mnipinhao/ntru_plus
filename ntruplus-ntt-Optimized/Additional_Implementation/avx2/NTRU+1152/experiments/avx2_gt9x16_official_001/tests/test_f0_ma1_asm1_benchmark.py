#!/usr/bin/env python3
"""Lock the serious SUPERCOP-derived MA1 schedule and MA0 control evidence."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEDULE_ROOT = (ROOT / "results/f0-ma1-supercop-derived-intel155h-20260825-002"
                 / "supercop-f0-ma1-serious")
CONTROL_ROOT = (ROOT / "results/f0-ma1-ma0-supercop-derived-intel155h-20260825-002"
                / "supercop-f0-ma1-ma0-serious")
schedule = json.loads((SCHEDULE_ROOT / "stq-summary.json").read_text())
schedule_meta = json.loads((SCHEDULE_ROOT / "metadata.json").read_text())
control = json.loads((CONTROL_ROOT / "stq-summary.json").read_text())
control_meta = json.loads((CONTROL_ROOT / "metadata.json").read_text())

assert schedule_meta["benchmark_class"] == "supercop-derived-poly-f0-ma1"
assert control_meta["benchmark_class"] == "supercop-derived-poly-f0-ma1-ma0"
assert schedule["fresh_process_launches"] == 9
assert control["fresh_process_launches"] == 9
assert schedule_meta["frequency_control"]["formal_policy_passed"]
assert control_meta["frequency_control"]["formal_policy_passed"]
for metadata in (schedule_meta, control_meta):
    assert metadata["version"] == "20260627"
    assert metadata["implementation"] == "avx2-gt9x16-exp001"
    assert metadata["frequency_policy"] == "required"

schedule_combined = schedule["balanced_combined_operations"]
assert schedule_combined["f0_ma1_c0_cycles"]["observations"] == 1728
assert schedule_combined["f0_ma1_c1_cycles"]["observations"] == 1728
assert schedule_combined["f0_ma1_c1_cycles"]["stq2"] < \
       schedule_combined["f0_ma1_c0_cycles"]["stq2"]
schedule_paired = schedule["balanced_paired_launches"]
assert schedule_paired["c1_faster_launches"] == 9
assert schedule_paired["c1_slower_launches"] == 0
assert schedule_paired["median_c1_minus_c0_cycles"] < -250

control_combined = control["balanced_combined_operations"]
for name in ("f0_ma0_cycles", "f0_ma1_c0_cycles", "f0_ma1_c1_cycles"):
    assert control_combined[name]["observations"] == 2592
assert control_combined["f0_ma0_cycles"]["stq2"] < \
       control_combined["f0_ma1_c1_cycles"]["stq2"]
control_paired = control["balanced_paired_launches"]
assert control_paired["c1_faster_than_c0_launches"] == 9
assert control_paired["c1_faster_than_ma0_launches"] == 0
assert control_paired["c1_slower_than_ma0_launches"] == 9
assert control_paired["median_c1_minus_ma0_cycles"] > 1000

print("F0-MA1-ASM1 benchmark: C1 beats C0 9/9 but loses to complete MA0 9/9")
