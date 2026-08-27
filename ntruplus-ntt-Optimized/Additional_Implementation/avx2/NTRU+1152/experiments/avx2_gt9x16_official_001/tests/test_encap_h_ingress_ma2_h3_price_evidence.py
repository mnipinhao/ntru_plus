#!/usr/bin/env python3
"""Promotion-independent evidence gates for the H3 serious pricing campaign."""
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
summary = json.loads((ROOT / "results/encap-h-ingress-ma2-h3-price-intel155h-20260827-001/summary.json").read_text())
assert summary["benchmark_class"] == "supercop-derived-encap-h-ingress-ma2-h3-price"
assert summary["headline_setting"] == "normal-aslr-on"
assert summary["serious_launches_per_setting"] == 9
assert summary["observations_per_label_per_launch"] == 96
assert summary["raw_observations"] == "settings/*/raw-observations.json"
assert not summary["native_kem_result"]
for name, setting in summary["settings"].items():
    raw = json.loads((ROOT / "results/encap-h-ingress-ma2-h3-price-intel155h-20260827-001/settings" / name / "raw-observations.json").read_text())
    assert len(raw) == 9
    assert all(len(values) == 96 for launch in raw for values in launch["observed"].values())
    assert setting["unique_runtime_address_tuples"] == (1 if name.endswith("aslr-off") else 9)
    for comparison in ("current", "h1"):
        evidence = setting["evidence"][comparison]
        assert evidence["negative_launches"] == 9
        assert evidence["positive_launches"] == 0
        assert evidence["bootstrap_95pct_ci_median"][1] < 0
assert -65 < summary["headline_h3_minus_current_cycles"] < -50
assert -112 < summary["headline_h3_minus_h1_cycles"] < -98
print("H3 serious price: 4/4 settings and 9/9 launches favor streaming H3")
