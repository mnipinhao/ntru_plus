#!/usr/bin/env python3
"""Check the frozen ITAIL-ASM-B0 proof, audit, and paired evidence."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
proof = json.loads((ROOT / "generated/g1c-inverse-ntt9-b0-range.json").read_text())
audit = json.loads((ROOT / "generated/g1c-inverse-ntt9-b0-audit.json").read_text())
result = json.loads((ROOT / "results/itail-asm-b0-intel155h-20260824-001/paired.json").read_text())

assert proof["input_contract"]["layout"] == "B physical P [0,3,6,1,4,7,8,2,5]"
assert proof["input_contract"]["scale"] == "R^-1"
assert proof["proof"]["all_pre_operations_fit_signed_i16"]
assert proof["proof"]["final_outputs_centered"]
assert audit["montgomery_chain_count"]["per_vector_inverse9"] == 10
assert audit["montgomery_chain_count"]["eight_vector_inverse9_body"] == 80
assert audit["liveness"]["peak_live_ymm"] == 15
assert audit["liveness"]["stack_spills"] == 0
assert all(audit["gates"].values())
paired = result["full_C2_store_to_inverse9"]["paired_B_minus_A"]
assert paired["median_cycles"] == -16.0
assert paired["B_faster_launches"] == 9
assert result["pure_8x_vector_inverse9"]["median_cycles"] == 490
assert not result["promotion_eligible"]
print("ITAIL-ASM-B0: range, leaf audit, 490-cycle body, and optimized B -16 cycles in 9/9 launches passed")
