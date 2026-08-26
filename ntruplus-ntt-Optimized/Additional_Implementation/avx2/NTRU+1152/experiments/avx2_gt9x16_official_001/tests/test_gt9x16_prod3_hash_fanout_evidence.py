#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = (ROOT / "results" /
          "gt9x16-prod3-hash-fanout-intel155h-20260826-002")

summary = json.loads((RESULT / "summary.json").read_text())
assert summary["benchmark_class"] == (
    "supercop-derived-gt9x16-prod3-hash-fanout")
assert summary["headline_estimator"] == (
    "median per-launch (C1-C0)-(O1-O0)")
assert summary["selected_placement"] == "normal"
assert set(summary["settings"]) == {
    "normal-aslr-on", "normal-aslr-off",
    "reversed-aslr-on", "reversed-aslr-off",
}
for setting in summary["settings"].values():
    assert setting["positive_excess_tax_launches"] == 9
    assert setting["candidate_complete_slower_launches"] == 9
    assert setting["bootstrap_95pct_ci_median_excess_tax"][0] > 0
    assert setting["bootstrap_95pct_ci_median_complete_delta"][0] > 0
    assert 500 < setting["median_excess_hash_fanout_tax_cycles"] < 560
    assert 680 < setting[
        "median_complete_dual_output_candidate_minus_official_cycles"] < 740

headline = summary["settings"][summary["headline_setting"]]
assert headline["median_excess_hash_fanout_tax_cycles"] == 529.5312500000002
assert headline["median_producer_candidate_minus_official_cycles"] == 181.875
assert headline[
    "median_complete_dual_output_candidate_minus_official_cycles"] == (
        712.8333333333335)

selection = json.loads(
    (RESULT / "selection" / "normal" / "stq-summary.json").read_text())
audit = selection["linked_hash_fanout_audit"]
assert audit["prod3_arithmetic_frozen"] is True
assert audit["same_coefficient_input_residency"] is True
assert audit["direct_transfers"]["o0"] == ["poly_ntt"]
assert audit["direct_transfers"]["o1"] == ["poly_ntt", "poly_tobytes"]
assert audit["direct_transfers"]["c1"][-1] == (
    "ntruplus1152_exp001_prod3_hash_bytes")
print("PROD3 hash fanout: four-way exact boundary and 9/9 excess-tax evidence passed")
