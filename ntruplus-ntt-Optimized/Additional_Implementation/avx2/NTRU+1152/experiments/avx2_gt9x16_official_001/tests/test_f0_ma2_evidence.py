#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
contract = json.loads((root / "generated/f0-ma2-asm.json").read_text())
proof = json.loads((root / "generated/f0-ma2-range.json").read_text())
audit = json.loads((root / "generated/f0-ma2-audit.json").read_text())
result = root / "results/f0-ma2-supercop-derived-intel155h-20260825-001/supercop-f0-ma2-serious"
summary = json.loads((result / "stq-summary.json").read_text())
metadata = json.loads((result / "metadata.json").read_text())

assert contract["full"]["chunks"] == 9
assert contract["full"]["official_vector_intermediate"] is False
assert contract["full"]["pack_barrett"] is False
assert proof["direct_sign_pack_proved"] is True
assert proof["global_pre_inv4"] == [-29899, 29901]
assert proof["global_post_inv4"] == [-2133, 2133]
full = audit["variants"]["FULL"]
assert full["montgomery_chains"] == 486
assert full["instruction_count"] == 4681
assert full["abi"]["peak_ymm"] == 14
assert full["abi"]["calls"] == full["abi"]["branches"] == 0
assert full["alignment"]["object_mod32"] == full["alignment"]["elf_mod32"] == 0
assert metadata["benchmark_class"] == "supercop-derived-poly-f0-ma2"
assert metadata["frequency_control"]["formal_policy_passed"] is True
combined = summary["balanced_combined_operations"]
assert combined["f0_ma0_cycles"]["observations"] == 1728
assert combined["f0_ma2_cycles"]["observations"] == 1728
assert combined["f0_ma2_cycles"]["stq2"] < combined["f0_ma0_cycles"]["stq2"]
paired = summary["balanced_paired_launches"]
assert paired["ma2_faster_than_ma0_launches"] == 9
assert paired["median_ma2_minus_ma0_cycles"] < 0
print("F0-MA2 evidence: full correctness/static contract and 9/9 serious win passed")
