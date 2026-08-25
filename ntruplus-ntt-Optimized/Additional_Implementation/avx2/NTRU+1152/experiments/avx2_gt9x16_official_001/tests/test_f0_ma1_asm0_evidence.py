#!/usr/bin/env python3
"""Check the checked-in F0-MA1-ASM0 contract and machine audit."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / "generated/f0-ma1-asm0.json").read_text())
AUDIT = json.loads((ROOT / "generated/f0-ma1-asm0-audit.json").read_text())


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


require(CONTRACT["schema"] == "gt-f0-ma1-asm0/v1", "wrong contract schema")
require(CONTRACT["tile"] == {"branch": 0, "p": 0, "physical_p_row": 0},
        "ASM0 is not the fixed B0/P0 tile")
ledger = CONTRACT["montgomery_ledger"]
require(ledger["h_r_lift_chains"] == 4, "missing common h R-lift")
require(ledger["bilinear_product_chains"] == 16, "wrong bilinear ledger")
require(ledger["lambda_chains"] == 4, "wrong lambda ledger")
require(ledger["ma1_core_chains"] == 20, "wrong MA1 core ledger")
require(ledger["ma1_arithmetic_including_h_lift"] == 24,
        "wrong arithmetic ledger")
require(ledger["inv4_finalizer_chains"] == 4, "wrong inv4 ledger")
require(ledger["total_chains"] == 28, "wrong total Montgomery ledger")
require(ledger["output_r_exponent"] == 0 and
        ledger["output_transform_scale"] == 1, "wrong output scale")
require(CONTRACT["abi"]["alias"] == "output must not alias r, m, or h",
        "alias contract changed")
require(CONTRACT["required_alignment"] == {
    "constants": 32, "entry": 32, "poly_and_tile_pointers": 32},
    "alignment contract changed")
require("lane 7" in CONTRACT["resident_h"]["asm0_exact_projection"],
        "exact resident-h projection lost lane-7 exchange")
require("not executed" in CONTRACT["route_accounting"]["schedule_792"],
        "792 route slots were misclassified")

require(AUDIT["schema"] == "gt-f0-ma1-asm0-audit/v1", "wrong audit schema")
arithmetic = AUDIT["arithmetic"]
for key, value in (("h_r_lift_chains", 4), ("bilinear_chains", 16),
                   ("lambda_chains", 4), ("inv4_chains", 4),
                   ("total_montgomery_chains", 28)):
    require(arithmetic[key] == value, f"audit {key} changed")
counts = arithmetic["instruction_counts"]
for mnemonic, value in (("vpmulhrsw", 16), ("vpmullw", 60),
                        ("vpmulhw", 56), ("vpshufb", 4),
                        ("vpblendw", 4), ("ret", 1)):
    require(counts[mnemonic] == value, f"{mnemonic} count changed")

abi = AUDIT["abi"]
for key in ("calls", "branches", "frame_instructions", "stack_references",
            "vzeroupper"):
    require(abi[key] == 0, f"ABI audit found {key}")
require(abi["distinct_ymm"] == list(range(13)), "YMM set changed")
require(abi["peak_ymm_upper_bound"] == 13, "YMM upper bound changed")
for base, offsets in abi["pointer_offsets"].items():
    require(offsets and all(offset % 32 == 0 for offset in offsets),
            f"unaligned {base} pointer offset")

routes = AUDIT["route_attribution"]
require(routes["R0_load_address_only"]["instructions"] == 0,
        "R0 must remain address-only")
require(routes["R1_register_reuse"]["instructions"] == 0,
        "R1 must remain register reuse")
require(routes["R2_resident_h_projection"]["total"] == 20,
        "resident-h R2 count changed")
require(routes["R2_bilinear_operand_formation"]["total"] == 24,
        "bilinear R2 count changed")
require(routes["R2_semantic_output_formation"]["total"] == 4,
        "output R2 count changed")
require(routes["R2_total"] == 48, "one-tile executed R2 total changed")
require(routes["correctness_first_materialization"] == {
    "reloads": 4, "stores": 4}, "ASM0 materialization changed")
require("must not be reported" in routes["old_792_interpretation"],
        "old 792-route warning missing")

alignment = AUDIT["alignment"]
require(alignment["object_symbol_mod32"] == 0 and
        alignment["linked_symbol_mod32"] == 0, "entry is not aligned")
require(alignment["object_text_alignment"] >= 32 and
        alignment["object_rodata_alignment"] >= 32 and
        alignment["linked_rodata_alignment"] >= 32,
        "section alignment is below 32 bytes")
for key in ("linked_caller_address", "linked_distance_from_caller",
            "linked_rodata_distance_from_symbol", "symbol_size"):
    require(isinstance(alignment[key], int), f"missing placement field {key}")
require(alignment["symbol_size"] > 0, "empty ASM symbol")

print("F0-MA1-ASM0 evidence: scale, chain ledger, routes, ABI, and alignment passed")
