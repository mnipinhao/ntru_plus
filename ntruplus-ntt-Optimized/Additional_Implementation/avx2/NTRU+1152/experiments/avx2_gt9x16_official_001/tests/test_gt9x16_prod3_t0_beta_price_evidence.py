#!/usr/bin/env python3
"""Regression checks for serious Natural-Q T0-beta paired pricing."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (ROOT / "results/gt9x16-prod3-t0-beta-price-intel155h-20260827-001/"
           "summary.json")


def main() -> None:
    report = json.loads(SUMMARY.read_text())
    assert report["benchmark_class"] == (
        "supercop-derived-gt9x16-prod3-t0-beta-price")
    assert report["selected_placement"] == "normal"
    assert report["headline_setting"] == "normal-aslr-on"
    assert report["decision"] == "promote-to-natural-q-prod3-research-baseline"
    assert report["producer_2x_direction_stable"]
    assert report["caller_direction_stable"]
    assert not report["native_kem_result"]
    assert report["schedule_vs_linked_accounting"] == {
        "schedule_constant_operands": [666, 650],
        "linked_natural_q_constant_operands": [594, 578],
        "schedule_rodata_delta_bytes": 448,
        "linked_rodata_delta_bytes": 416,
        "explanation": (
            "absolute baseline taxonomy and linked retained set differ; "
            "-16 operand direction agrees"),
    }
    for name, setting in report["settings"].items():
        assert setting["unique_runtime_address_tuples"] == (
            1 if name.endswith("aslr-off") else 9)
        for width in ("1x", "2x", "caller"):
            evidence = setting["evidence"][width]
            assert evidence["candidate_faster_launches"] == 9
            assert evidence["candidate_slower_launches"] == 0
            assert evidence["median_candidate_minus_control_cycles"] < 0
            assert evidence["bootstrap_95pct_ci_median_delta"][1] < 0
            assert setting["combined"][f"{width}_control"]["observations"] == 1728
            assert setting["combined"][f"{width}_candidate"]["observations"] == 1728
    headline = report["settings"]["normal-aslr-on"]["evidence"]
    assert headline["1x"]["median_candidate_minus_control_cycles"] == -16.125
    assert headline["2x"]["median_candidate_minus_control_cycles"] == (
        -38.354166666666515)
    assert headline["caller"]["median_candidate_minus_control_cycles"] == (
        -36.41666666666606)
    print("T0-beta PRICE: producer and frozen caller win 9/9 in all four settings")


if __name__ == "__main__":
    main()
