#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = (ROOT / "results" /
          "gt9x16-prod3-hash-h1-price-intel155h-20260826-001" /
          "supercop-gt9x16-prod3-hash-h1-price")

summary = json.loads((RESULT / "summary.json").read_text())
assert summary["benchmark_class"] == (
    "supercop-derived-gt9x16-prod3-hash-h1-price")
assert summary["headline_estimator"] == "median per-launch H1-H0"
assert summary["selected_placement"] == "reversed"
assert summary["boundary"] == (
    "materialized scale-4 MA2 planes to exact 1728 bytes")
assert set(summary["settings"]) == {
    "normal-aslr-on", "normal-aslr-off",
    "reversed-aslr-on", "reversed-aslr-off",
}
for setting in summary["settings"].values():
    assert setting["h1_faster_launches"] == 9
    assert setting["h1_slower_launches"] == 0
    assert setting[
        "bootstrap_95pct_ci_median_h1_minus_h0_cycles"][1] < 0
    assert -325 < setting["median_h1_minus_h0_cycles"] < -305

headline = summary["settings"][summary["headline_setting"]]
assert headline["median_h1_minus_h0_cycles"] == -314.64583333333337
assert headline["combined"]["h0"]["stq2"] == 1083.1238425925926
assert headline["combined"]["h1"]["stq2"] == 768.3310185185185

selection = json.loads(
    (RESULT / "selection" / "reversed" / "stq-summary.json").read_text())
audit = selection["linked_hash_h1_price_audit"]
assert audit["producer_executed"] is False
assert audit["ma2_arithmetic_executed"] is False
assert audit["direct_transfers"]["h0"] == [
    "ntruplus1152_exp001_prod3_hash_bytes"]
assert audit["direct_transfers"]["h1"] == [
    "ntruplus1152_exp001_prod3_ma2_hash_h1"]
assert selection["decision"]["candidate_direction_stable"] is True
print("PROD3 H1 PRICE: exact boundary and four-setting 9/9 evidence passed")
