#!/usr/bin/env python3
"""Regression checks for ENCAP-CALLER-ATTRIBUTION-V2 evidence."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (ROOT / "results/gt9x16-prod3-encap-attribution-v2-"
           "intel155h-20260827-001/summary.json")


def main() -> None:
    report = json.loads(SUMMARY.read_text())
    assert report["benchmark_class"] == (
        "supercop-derived-gt9x16-prod3-encap-attribution-v2")
    assert report["selected_placement"] == "normal"
    assert report["headline_setting"] == "normal-aslr-on"
    assert report["decision"] == "attack-largest-component:h_ma2_ciphertext_tail"
    assert report["largest_component_by_absolute_median"] == (
        "h_ma2_ciphertext_tail")
    assert not report["native_kem_result"]
    assert report["corrected_single_inv4_qorder_sidecar"].startswith("not-run:")
    for name, setting in report["settings"].items():
        assert setting["unique_runtime_address_tuples"] == (
            1 if name.endswith("aslr-off") else 9)
        for boundary in ("producer_r", "producer_m", "dual_r", "tail"):
            evidence = setting["evidence"][boundary]
            assert evidence["gt_faster_launches"] == 0
            assert evidence["gt_slower_launches"] == 9
            assert evidence["median_gt_minus_official_cycles"] > 0
            assert evidence["bootstrap_95pct_ci_median_delta"][0] > 0
            assert setting["combined"][f"{boundary}_official"]["observations"] == 1728
            assert setting["combined"][f"{boundary}_gt"]["observations"] == 1728
        assert setting["evidence"]["rough_modeled_debt_cycles"][
            "bootstrap_95pct_ci_median"][0] > 0
    components = report["headline_component_balance"]
    assert components == {
        "r_producer": 78.8125,
        "m_producer": 76.10416666666674,
        "r_excess_hash_fanout": 226.70833333333348,
        "h_ma2_ciphertext_tail": 605.3958333333333,
    }
    assert report["headline_rough_modeled_debt_cycles"] == 987.4166666666667
    assert abs(report["cross_campaign_residual_cycles"]) < 5
    print("ENCAP attribution V2: +992 native gap is localized; MA2 tail is largest")


if __name__ == "__main__":
    main()
