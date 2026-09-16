#!/usr/bin/env python3
"""Audit G0 generated proof artifacts and frozen numerical obligations."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
chain = json.loads((HERE / "build/range-chain.json").read_text())
fixed = json.loads((HERE / "build/m5e-fixed-barrett.json").read_text())

assert chain["gate"] == "G0_m5rd_fr0_range_chain_closure"
assert chain["status"] == "pass"
assert chain["forward"]["ntt16_max_abs"] == 9342
assert chain["forward"]["maximum_abs_any_forward_node"] == 25569
assert chain["forward"]["forward_output_union"] == [-25569, 25566]
assert chain["forward"]["unsafe_int16_nodes"] == 0
assert chain["basemul"]["leaf_count"] == 288
assert chain["basemul"]["maximum_abs_operand"] == 25569
assert chain["basemul"]["maximum_abs_int32_accumulator"] == 1961321283
assert chain["basemul"]["maximum_abs_basemul_output"] == 2148
assert chain["basemul"]["maximum_abs_basemul_add_output"] == 2205
assert chain["basemul"]["m5e_inverse_input_bound"] == 2205
assert chain["inverse"]["input_contract"] == [-2205, 2205]
assert chain["inverse"]["maximum_halfword_abs"] == 17220
assert chain["inverse"]["int16_safe"]
assert fixed["gate"] == "gt864_fixed_barrett_algorithm10"
assert fixed["status"] == "pass"
assert fixed["distinct_constants"] == 270
assert fixed["exhaustive_signed_halfword_products"] == 17694720
assert fixed["maximum_output_abs"] == 3444
assert len(chain["source_sha256"]) == 8
assert all(len(value) == 64 for value in chain["source_sha256"].values())

print("g0_range_chain_audit=pass")
print("ntt16_max_abs=9342")
print("m5rd_fr0_output_abs=25569")
print("m5c_basemul_output_abs=2148")
print("m5c_basemul_add_output_abs=2205")
print("m5e_input_abs=2205")
print("m5e_maximum_halfword_abs=17220")
