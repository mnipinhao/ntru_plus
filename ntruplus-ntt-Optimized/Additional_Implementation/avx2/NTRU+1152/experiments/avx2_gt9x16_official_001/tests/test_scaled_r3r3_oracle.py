#!/usr/bin/env python3
"""Regression checks for the F-R3A scaled paper R3xR3 proof artifact."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    oracle = json.loads((ROOT / "generated/gt9x16-scaled-r3r3-oracle.json").read_text())
    assert oracle["pure_cyclic_gate"]["passed"] is True
    assert oracle["variants"]["R0"]["transform_scale"] == 1
    assert oracle["variants"]["R1"]["transform_scale"] == 4
    assert oracle["variants"]["R2"]["transform_scale"] == 4
    assert oracle["variants"]["R2"]["physical_row_to_mathematical_p"] == [
        0, 3, 6, 1, 4, 7, 8, 2, 5]
    assert oracle["variants"]["R0"]["montgomery_chains_per_ntt9"] == 18
    assert oracle["variants"]["R1"]["montgomery_chains_per_ntt9"] == 10
    assert oracle["variants"]["R2"]["montgomery_chains_per_ntt9"] == 10
    assert oracle["variants"]["R2"]["distinct_inter_level_nontrivial_constants"] == 2
    assert oracle["static_full_forward_counts"]["R0_to_R1_or_R2_chain_reduction"] == 64
    assert oracle["scale_ledger"]["base_inv"]["phase1_adjugate_scale"] == 64
    assert oracle["scale_ledger"]["base_inv"]["denominator_scale"] == 256
    assert oracle["scale_ledger"]["keypair_ratio"]["regular_basemul_output_scale"] == 1
    assert oracle["scale_ledger"]["decapsulation_inverse_path"]["pre_normalization_scale"] == 64
    assert oracle["gate_decision"]["scale_closure_without_standalone_pass"] is True
    assert oracle["gate_decision"]["benchmark_available"] is False
    assert oracle["proof"]["total_variant_basis_checks"] == 243
    assert oracle["proof"]["adjusted_ntt16_rows_rekeyed"] == 9
    assert oracle["proof"]["basemul_baseinv_factors_rekeyed"] == 288
    assert len(oracle["paper_basemul_baseinv_factor_rows"]) == 18
    assert oracle["proof"]["scale_homogeneity_checks"] == {
        "basemul_degree2": 288,
        "baseinv_adjugate_degree3": 288,
        "baseinv_denominator_degree4": 288,
    }
    print("scaled R3R3 oracle: pure cyclic, R0/R1/R2 basis, row map, and scale closure passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
