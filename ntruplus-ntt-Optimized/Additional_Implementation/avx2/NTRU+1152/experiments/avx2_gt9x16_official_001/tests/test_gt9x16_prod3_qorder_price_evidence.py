#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = (ROOT / "results" /
          "gt9x16-prod3-qorder-price-intel155h-20260827-001")

summary = json.loads((RESULT / "summary.json").read_text())
assert summary["benchmark_class"] == (
    "supercop-derived-gt9x16-prod3-qorder-price")
assert summary["boundary"] == (
    "two coefficient-domain producers plus resident h, lane-wise MA2, "
    "ciphertext H1, and r hash H1")
assert summary["version"] == "20260627"
assert summary["compiler_policy"] == "fixed-common-O3GC"
assert summary["serious_launches_per_setting"] == 9
assert summary["observations_per_label_per_launch"] == 96
assert summary["placement_selection"] == (
    "none; all four settings are co-equal ABI evidence")
assert summary["native_kem_result"] is False
assert summary["all_four_delta_signs_agree"] is True
assert summary["winner"] == "natural-Q"
assert summary["freeze_policy"] == (
    "freeze winner; do not search more Q-orders")

assert set(summary["settings"]) == {
    "normal-aslr-on", "normal-aslr-off",
    "reversed-aslr-on", "reversed-aslr-off",
}
for name, setting in summary["settings"].items():
    assert len(setting["launches"]) == 9
    assert setting["median_natural_minus_current_cycles"] < 0
    assert setting["bootstrap_95pct_ci_median_delta"][1] < 0
    assert setting["combined"]["current"]["observations"] == 1728
    assert setting["combined"]["natural"]["observations"] == 1728
    expected_tuples = 1 if name.endswith("aslr-off") else 9
    assert setting["unique_runtime_address_tuples"] == expected_tuples
    assert len(list((RESULT / "settings" / name).glob("launch-*.out"))) == 9

assert summary["settings"]["normal-aslr-on"][
    "median_natural_minus_current_cycles"] == -160.0
assert summary["settings"]["normal-aslr-off"][
    "median_natural_minus_current_cycles"] == -166.29166666666697
assert summary["settings"]["reversed-aslr-on"][
    "median_natural_minus_current_cycles"] == -163.83333333333303
assert summary["settings"]["reversed-aslr-off"][
    "median_natural_minus_current_cycles"] == -165.0625

expected_calls = {
    "current": [
        "ntruplus1152_exp001_top_split_small",
        "ntruplus1152_exp001_gt9x16_prod3_aos_full_price",
        "ntruplus1152_exp001_top_split_small",
        "ntruplus1152_exp001_gt9x16_prod3_aos_full_price",
        "ntruplus1152_exp001_f0_ma2_planes_current_q",
        "ntruplus1152_exp001_prod3_ma2_hash_h1",
        "ntruplus1152_exp001_prod3_ma2_hash_h1",
    ],
    "natural": [
        "ntruplus1152_exp001_top_split_small",
        "ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q",
        "ntruplus1152_exp001_top_split_small",
        "ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q",
        "ntruplus1152_exp001_f0_ma2_planes_natural_q",
        "ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q",
        "ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q",
    ],
}
for placement in ("normal", "reversed"):
    build = RESULT / "builds" / placement
    metadata = json.loads((build / "metadata.json").read_text())
    evidence = json.loads((build / "stq-summary.json").read_text())
    assert metadata["frequency_control"]["formal_policy_passed"] is True
    assert metadata["frequency_control"]["scaling_governor"] == "performance"
    assert metadata["frequency_control"]["intel_no_turbo"] == "1"
    audit = evidence["linked_qorder_price_audit"]
    assert audit["direct_transfers"] == expected_calls
    assert audit["two_producers"] is True
    assert audit["resident_h_multiplicity"] == 1
    assert audit["hash_and_ciphertext_H1_multiplicity"] == 2
    assert audit["MA2_arithmetic_identical"] is True
    assert audit["same_input_residency"] is True
    assert audit["same_output_bytes"] is True
    assert audit["static_delta"] == {
        "data_loads": 16, "routing": -192, "total_instructions": -176}

assert summary["builds"]["normal"]["measure_sha256"] != (
    summary["builds"]["reversed"]["measure_sha256"])
assert sum(v["natural_faster_launches"]
           for v in summary["settings"].values()) == 35
assert sum(v["natural_slower_launches"]
           for v in summary["settings"].values()) == 1
print("PROD3 QORDER PRICE: natural-Q wins all four serious settings; Q-order frozen")
