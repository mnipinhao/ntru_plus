#!/usr/bin/env python3
"""Validate G1C0 sink facts, BaseInv homogeneity, and honest prototype gates."""

import json
from pathlib import Path

experiment = Path(__file__).resolve().parents[1]
audit = json.loads((experiment / "generated/g1c-inverse-sink-audit.json").read_text())

bm = audit["official_bmscale_to_inverse"]
assert bm["store_offsets_bytes"] == [0, 32, 64, 96]
assert bm["block_stride_bytes"] == 128 and bm["blocks"] == 18
assert bm["standalone_converter_count"] == 0
assert bm["C1_store_only_credit_available_against_official"] is False

head = audit["official_inverse_level6_head"]
assert head["input_vectors"] == 8 and head["terminal_blocks_per_iteration"] == 2
assert head["montgomery_difference_chains"] == 4
assert head["barrett_sum_chains"] == 4
assert head["materialized_store_before_level5"] is False

den = audit["baseinv_den18_lifetime"]
assert den["den_vectors"] == 18
assert den["phase_2_sign_pattern"] == [1, -1, 1, -1]
hom = audit["baseinv_homogeneity"]
assert [hom[name] for name in ("adjugate_degree", "denominator_degree",
                                "inverse_denominator_degree", "base_inverse_output_degree")] == [3, 4, -4, -1]

norm = audit["inverse_normalization_mod_q"]
assert norm["official_Rminus1_input"] == 3424
assert norm["resident_R0_input"] == 1764
assert norm["BaseInv_quarter_scale_R0_input"] == 142
assert norm["scalar_normalization_closed"]

gate = audit["prototype_gate"]
assert gate["asm_authorized"] is False and gate["cycles"] is None
assert "pending" in gate["G1C_M_C2"]
print("G1C0 inverse sink: Official zero-conversion, den[18] lifetime, homogeneity and scalar normalization passed")
