#!/usr/bin/env python3
"""Regression gates for the H4-M0 scale-gauge decision."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
report = json.loads(
    (ROOT / "generated/encap-h4-scale-absorption-audit.json").read_text())

assert report["schema"] == "encap-h4-scale-absorption-audit/v1"
assert report["producer_scale1"]["added_chains_per_forward"] == 8
assert report["producer_scale1"]["all_preoperations_signed_i16"]
assert report["producer_scale1"]["mod_q_basis_inputs"] == 288
assert report["producer_scale1"]["mod_q_output_cells"] == 41472

variants = {variant["id"]: variant for variant in report["variants"]}
assert variants["M0-C0-current-scale4"]["delta_instructions_vs_current"] == 0
assert variants["M0-C1-h4-local"]["delta_instructions_vs_current"] == -40
assert variants["M0-C2-caller-wide"]["delta_instructions_vs_current"] == -80
for variant in variants.values():
    proof = variant["range"]
    assert proof["all_preoperations_signed_i16"]
    lo, hi = proof["global_post_terminal"]
    assert -3457 < lo <= hi < 3457

assert report["selection"]["full_encap_minimum"] == "M0-C2-caller-wide"
assert report["selection"]["mandatory_h4_reduction_vectors"] == 72
assert report["decision"]["m0_complete"]
assert report["decision"]["selected_for_h4_m1_mapping"] == "M0-C2-caller-wide"
assert not report["decision"]["asm_authorized"]
print("H4-M0 scale absorption audit: PASS")
