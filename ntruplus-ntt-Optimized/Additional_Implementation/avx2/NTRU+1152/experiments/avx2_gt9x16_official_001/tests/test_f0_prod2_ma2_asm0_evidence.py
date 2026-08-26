#!/usr/bin/env python3
"""Check the frozen F0-PROD2 materialized P2-B ASM0 evidence."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
contract = json.loads((ROOT / "generated/f0-prod2-ma2-asm.json").read_text())
audit = json.loads((ROOT / "generated/f0-prod2-ma2-audit.json").read_text())
ma2 = json.loads((ROOT / "generated/f0-ma2-asm.json").read_text())

assert contract["schema"] == "gt-f0-prod2-ma2-asm/v1"
assert contract["physical_output_abi"] == "F0-MA2 coefficient planes"
assert contract["arithmetic_derivation"]["new_reductions"] == 0
assert contract["arithmetic_derivation"]["scale_conversions"] == 0
assert contract["dynamic_per_forward"] == {
    "aligned_plane_stores": 72,
    "backing_bytes": 2304,
    "extra_temporary_bytes": 0,
    "generic_f0_final_stores": 0,
    "helper_calls": 4,
    "p2b_vperm2i128": 72,
}
assert contract["output_contract"]["scale"] == 4
assert contract["output_contract"]["montgomery_r_exponent"] == 0
assert contract["output_contract"]["range_i16"] == [-20751, 20753]

assert audit["schema"] == "gt-f0-prod2-ma2-audit/v1"
assert audit["arithmetic_identity"] == {
    "d1_delta": {"vperm2i128": 18},
    "formation_and_r2_opcode_ledgers_equal_p1h": True,
    "new_reductions": 0,
    "scale_conversions": 0,
}
boundary = audit["materialized_boundary"]
assert boundary["generic_f0_final_stores"] == 0
assert boundary["p2b_vperm2i128_per_forward"] == 72
assert boundary["aligned_plane_stores_per_forward"] == 72
assert boundary["extra_temporary_bytes"] == 0
assert boundary["backing_bytes"] == 2304
assert boundary["all_18_static_slots_safe"] is True
assert len(boundary["last_use_overwrite"]) == 18
assert all(item["first_write_instruction"] > item["last_read_instruction"]
           for item in boundary["last_use_overwrite"])

consumer = audit["ma2_native_consumer"]
assert consumer["r_plane_loads"] == consumer["m_plane_loads"] == 72
assert consumer["generic_projection_permutations"] == 0
assert consumer["conditional_branches"] == 0
assert consumer["opcode_delta_vs_generic_ma2"] == {
    "vmovdqa": -144,
    "vperm2i128": -144,
}
assert consumer["arithmetic_and_serializer_equal"] is True
assert ma2["native_full"]["arithmetic_and_serializer"] == "identical to full"
assert audit["decision"]["producer_boundary_benchmark_authorized"] is True
assert audit["decision"]["kem_benchmark_authorized"] is False

print("F0-PROD2 P2-B ASM0 evidence: exact arithmetic identity, 18-slot "
      "overwrite safety, 72-plane native MA2 loads, and alignment/ABI passed")
