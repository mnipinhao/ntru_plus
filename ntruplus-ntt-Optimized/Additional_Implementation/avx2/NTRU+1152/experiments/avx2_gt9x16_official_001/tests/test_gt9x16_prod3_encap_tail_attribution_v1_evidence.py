#!/usr/bin/env python3
"""Regression checks for ENCAP-TAIL-ATTRIBUTION-V1 evidence."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (ROOT / "results/gt9x16-prod3-encap-tail-attribution-v1-"
           "intel155h-20260827-002/summary.json")


def main() -> None:
    report = json.loads(SUMMARY.read_text())
    assert report["benchmark_class"] == (
        "supercop-derived-gt9x16-prod3-encap-tail-attribution-v1")
    assert report["headline_placement"] == "normal"
    assert report["headline_setting"] == "normal-aslr-on"
    assert report["largest_component_by_absolute_launch_median"] == (
        "resident_h_projection")
    assert report["decision"] == (
        "attack-largest-tail-component:resident_h_projection")
    assert not report["new_asm"]
    assert not report["native_kem_result"]
    assert report["headline_t2_delta_cycles"] == 608.9375
    assert report["headline_component_medians_cycles"] == {
        "resident_h_projection": 248.14583333333334,
        "ma2_arithmetic": 137.4583333333334,
        "ciphertext_serialization": 222.41666666666674,
    }
    for name, setting in report["settings"].items():
        assert setting["unique_runtime_address_tuples"] == (
            1 if name.endswith("aslr-off") else 9)
        assert setting["telescoping"]["max_absolute_residual_cycles"] == 0
        assert (setting["telescoping"]["median_reconstructed_t2_cycles"] ==
                setting["telescoping"]["median_direct_t2_cycles"])
        for boundary in ("t0", "t1", "t2"):
            evidence = setting["boundary_evidence"][boundary]
            assert evidence["negative_launches"] == 0
            assert evidence["positive_launches"] == 9
            assert evidence["bootstrap_95pct_ci_median"][0] > 0
            assert setting["combined"][f"{boundary}_official"]["observations"] == 1728
            assert setting["combined"][f"{boundary}_gt"]["observations"] == 1728
        for component in ("resident_h_projection", "ma2_arithmetic",
                          "ciphertext_serialization"):
            evidence = setting["component_evidence"][component]
            assert evidence["negative_launches"] == 0
            assert evidence["positive_launches"] == 9
            assert evidence["bootstrap_95pct_ci_median"][0] > 0
    print("ENCAP tail V1: +609 cycles decomposed; resident-h is largest")


if __name__ == "__main__":
    main()
