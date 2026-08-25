#!/usr/bin/env python3
"""Lock the MA3 arithmetic, final-range, ABI, and serious benchmark gates."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
contract = json.loads((ROOT / "generated/f0-ma3-asm.json").read_text())
proof = json.loads((ROOT / "generated/f0-ma3-final-range.json").read_text())
audit = json.loads((ROOT / "generated/f0-ma3-audit.json").read_text())
result_root = (ROOT / "results/f0-ma3-supercop-derived-intel155h-20260825-001"
               / "supercop-f0-ma3-serious")
summary = json.loads((result_root / "stq-summary.json").read_text())
metadata = json.loads((result_root / "metadata.json").read_text())

assert contract["ledger"] == {
    "core_per_tile": 13, "full_total": 378, "h_lift_per_tile": 4,
    "inv4_per_tile": 4, "total_per_tile": 21,
}
assert contract["asm0"]["montgomery_chains"] == 21
assert contract["asm1"]["post_inv4_center"] is False
assert all(item["pack_matches_mod_q_for_every_input"] and
           not item["explicit_center_before_pack_required"]
           for item in proof["proofs"])
assert all(item["post_inv4_inclusive"] == [-1773, 1773]
           for item in proof["proofs"])
assert proof["static_saving_full_path"]["instructions_removed"] == 720

assert audit["variants"]["ASM0"]["montgomery_chains"] == 21
assert audit["variants"]["ASM1"]["montgomery_chains"] == 378
for variant in ("ASM0", "ASM1"):
    abi = audit["variants"][variant]["abi"]
    for key in ("branches", "calls", "spills", "stack_references", "vzeroupper"):
        assert abi[key] == 0
    alignment = audit["variants"][variant]["alignment"]
    assert alignment["object_mod32"] == alignment["elf_mod32"] == 0
assert audit["variants"]["ASM1"]["instruction_count"] == 10891

assert metadata["benchmark_class"] == "supercop-derived-poly-f0-ma3"
assert metadata["version"] == "20260627"
assert metadata["frequency_control"]["formal_policy_passed"]
assert summary["fresh_process_launches"] == 9
combined = summary["balanced_combined_operations"]
assert combined["f0_ma0_cycles"]["observations"] == 1728
assert combined["f0_ma3_cycles"]["observations"] == 1728
assert combined["f0_ma0_cycles"]["stq2"] < combined["f0_ma3_cycles"]["stq2"]
paired = summary["balanced_paired_launches"]
assert paired["ma3_faster_than_ma0_launches"] == 0
assert paired["ma3_slower_than_ma0_launches"] == 9
assert paired["median_ma3_minus_ma0_cycles"] > 1800

print("F0-MA3: exact 378-chain caller passes; final center removed; MA3 loses to MA0 9/9 and reopens MA2")
