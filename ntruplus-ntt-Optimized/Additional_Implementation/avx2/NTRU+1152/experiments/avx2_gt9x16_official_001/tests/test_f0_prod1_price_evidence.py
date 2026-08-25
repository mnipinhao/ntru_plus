#!/usr/bin/env python3
"""Check frozen F0-PROD1-PRICE SUPERCOP-derived evidence."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = (ROOT / "results/f0-prod1-price-supercop-derived-intel155h-20260825-002"
          / "supercop-f0-prod1-serious")
summary = json.loads((RESULT / "stq-summary.json").read_text())
metadata = json.loads((RESULT / "metadata.json").read_text())

assert metadata["benchmark_class"] == "supercop-derived-poly-f0-prod1"
assert metadata["compiler_policy"] == "native-supercop-selection"
assert metadata["frequency_control"]["formal_policy_passed"] is True
assert metadata["fresh_process_launches"] == 9
assert metadata["measure_elf_sha256"] == (
    "3a2ffd67566fe25e11ef47d7e097507634f5282e80beba343ed539fcfed87294")

combined = summary["balanced_combined_operations"]
for width in ("1x", "2x"):
    legacy = combined[f"f0_prod1_{width}_legacy_cycles"]
    p1h = combined[f"f0_prod1_{width}_p1h_cycles"]
    assert legacy["observations"] == p1h["observations"] == 1728
    assert p1h["stq2"] > legacy["stq2"]

paired = summary["balanced_paired_launches"]
assert paired["p1h_1x_faster_launches"] == 0
assert paired["p1h_1x_slower_launches"] == 9
assert paired["p1h_2x_faster_launches"] == 0
assert paired["p1h_2x_slower_launches"] == 9
assert paired["median_1x_p1h_minus_legacy_cycles"] > 0
assert paired["median_2x_p1h_minus_legacy_cycles"] > 0
assert summary["producer_credit_screen"]["classification"] == (
    "poor-or-insufficient-for-current-ma2-gap")

perf = summary["perf_diagnostics"]["baseline_adjusted_counts_per_operation"]
assert perf["p1h1x"]["instructions:u"] < perf["legacy1x"]["instructions:u"]
assert perf["p1h1x"]["mem_inst_retired.all_loads:u"] > perf["legacy1x"][
    "mem_inst_retired.all_loads:u"]
assert perf["p1h1x"]["mem_inst_retired.all_stores:u"] < perf["legacy1x"][
    "mem_inst_retired.all_stores:u"]

layout = summary["elf_layout"]
assert layout["symbols"]["poly_ntt"]["address_mod32"] == 0
assert layout["symbols"]["poly_ntt"]["size"] == 1728
for name, record in layout["symbols"].items():
    assert record["address_mod32"] == 0, name

print("F0-PROD1-PRICE: same-ELF 1X/2X serious evidence rejects generic F0 P1-H")
