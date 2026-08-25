#!/usr/bin/env python3
"""Gate the caller-shaped MA1 ASM1 contract and machine audit."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads((ROOT / "generated/f0-ma1-asm1.json").read_text())
AUDIT = json.loads((ROOT / "generated/f0-ma1-asm1-audit.json").read_text())
MA0 = json.loads((ROOT / "generated/f0-ma0-adapter.json").read_text())
MA0_AUDIT = json.loads((ROOT / "generated/f0-ma0-adapter-audit.json").read_text())


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


require(CONTRACT["schema"] == "gt-f0-ma1-asm1/v1", "wrong contract schema")
require("nine serializer chunks" in CONTRACT["boundary"], "wrong caller boundary")
require(CONTRACT["abi"]["output"].startswith("1728"), "wrong ciphertext ABI")
require("non-aliasing" in CONTRACT["abi"]["inputs"], "nonalias contract lost")
require(CONTRACT["alignment"] == {
    "ciphertext": "unaligned vmovdqu stores", "entry_and_constants": 32,
    "poly_and_scratch": 32}, "alignment contract changed")

ledger = CONTRACT["montgomery_ledger"]
for key, value in (("tiles", 18), ("core_product_chains_per_tile", 20),
                   ("h_projection_lift_chains_per_tile", 4),
                   ("output_scale_chains_per_tile", 4),
                   ("total_chains_per_tile", 28),
                   ("core_product_chains_full", 360),
                   ("h_projection_lift_chains_full", 72),
                   ("output_scale_chains_full", 72),
                   ("total_chains_full", 504)):
    require(ledger[key] == value, f"Montgomery ledger changed: {key}")
require(ledger["output_r_exponent"] == 0 and
        ledger["output_transform_scale"] == 1, "output scale changed")
proof = CONTRACT["range_proof"]
require(proof["h_is_centered_before_every_r2_lift"], "h lift lacks centering")
require(proof["r_and_m_are_centered_on_consumption"], "r/m centering lost")
require(proof["all_preoperations_signed_i16"], "i16 proof is not closed")
require(not proof["schedule_reassociation"], "schedule changed arithmetic")
require(CONTRACT["liveness"]["C0_peak_ymm"] == 13, "C0 peak changed")
require(CONTRACT["liveness"]["C1_peak_ymm"] == 16, "C1 peak changed")
require(not CONTRACT["liveness"]["spills_allowed"], "spills became allowed")

require(AUDIT["schema"] == "gt-f0-ma1-asm1-audit/v1", "wrong audit schema")
for variant, distinct, peak, moves in (("C0", list(range(14)), 13, 1152),
                                       ("C1", list(range(16)), 16, 1368)):
    report = AUDIT["variants"][variant]
    arithmetic = report["arithmetic"]
    require(arithmetic == {
        "center_operations": 360, "core_product_chains": 360,
        "inv4_output_chains": 72, "resident_h_lift_chains": 72,
        "total_montgomery_chains": 504}, f"{variant} arithmetic changed")
    abi = report["abi"]
    for key in ("calls", "branches", "frame_instructions", "spills",
                "stack_references", "vzeroupper"):
        require(abi[key] == 0, f"{variant} ABI audit found {key}")
    require(abi["distinct_ymm"] == distinct, f"{variant} YMM set changed")
    require(abi["proved_peak_ymm"] == peak, f"{variant} peak changed")
    require(report["instruction_counts"]["vmovdqa"] == moves,
            f"{variant} move count changed")
    for base, offsets in abi["pointer_offsets"].items():
        require(offsets, f"{variant} has no accesses through {base}")
        if base != "rdi":
            require(all(offset % 32 == 0 for offset in offsets),
                    f"{variant} has unaligned {base} vector offset")
    alignment = report["alignment"]
    require(alignment["object_symbol_mod32"] == 0 and
            alignment["linked_symbol_mod32"] == 0,
            f"{variant} entry is not 32-byte aligned")
    require(alignment["symbol_size"] > 0, f"{variant} is empty")

comparison = AUDIT["comparison"]
require(comparison["same_arithmetic_multiset"], "arithmetic multiset differs")
require(comparison["same_montgomery_chain_ledger"], "chain ledger differs")
require(comparison["same_routing_multiset"], "routing multiset differs")
require(comparison["C1_extra_vmovdqa"] == 216, "C1 move debt changed")
sections = AUDIT["sections"]
require(sections["object_text_alignment"] >= 32 and
        sections["object_rodata_alignment"] >= 32 and
        sections["linked_rodata_alignment"] >= 32,
        "section alignment dropped below 32 bytes")

require(MA0["schema"] == "gt-f0-ma0-adapter/v1", "wrong MA0 contract")
require(MA0["bijection_cells"] == 1152 and MA0["output_vectors"] == 72,
        "MA0 adapter coverage changed")
require(MA0["executed_routing"] == {
    "total": 336, "vperm2i128": 136, "vpor": 64, "vpshufb": 136},
    "MA0 executed route count changed")
require("semantic" in MA0["schedule_288_interpretation"],
        "MA0 semantic/executed distinction lost")
require(MA0_AUDIT["schema"] == "gt-f0-ma0-adapter-audit/v1",
        "wrong MA0 audit schema")
require(MA0_AUDIT["instruction_count"] == 753, "MA0 object changed")
require(MA0_AUDIT["abi"] == {
    "branches": 0, "calls": 0, "distinct_ymm": [0, 1, 2, 3],
    "spills": 0, "stack_references": 0, "vzeroupper": 0},
    "MA0 adapter is not a spill-free leaf")
require(MA0_AUDIT["alignment"]["object_symbol_mod32"] == 0 and
        MA0_AUDIT["alignment"]["linked_symbol_mod32"] == 0,
        "MA0 adapter is not aligned")

print("F0-MA1-ASM1 evidence: full chain/range ledger, C0/C1 ABI, routing, and alignment passed")
