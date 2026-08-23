#!/usr/bin/env python3
"""Gate M3C3 static evidence and the fixed paired primitive price."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
audit_path = ROOT / "generated/g1c-m3c3-reduction-audit.json"
proof_path = ROOT / "generated/g1c-m3c2p-exact-proof.json"
asm_path = ROOT / "asm/g1c_m3c3_reduction.S"
bench_path = ROOT / "bench/bench_g1c_m3c3_reduction_paired.c"
result_path = ROOT / "results/g1c-m3c3-reduction-intel155h-20260823-001/reduction-paired.json"
audit = json.loads(audit_path.read_text())
result = json.loads(result_path.read_text())

assert audit["source_sha256"] == hashlib.sha256(asm_path.read_bytes()).hexdigest()
assert audit["proof_sha256"] == hashlib.sha256(proof_path.read_bytes()).hexdigest()
assert audit["gate"]["fixed_72_vector_loop"] is True
assert audit["gate"]["call_frame_stack_vzeroupper_free"] is True
barrett_static = audit["functions"]["signed-Barrett"]["mnemonics"]
mont_static = audit["functions"]["Montgomery-identity"]["mnemonics"]
assert barrett_static["vpmulhrsw"] == 1
assert barrett_static["vpcmpgtw"] == 2
assert mont_static["vpmullw"] == 1
assert mont_static["vpmulhw"] == 2

assert result["source_sha256"]["audit"] == hashlib.sha256(
    audit_path.read_bytes()).hexdigest()
assert result["source_sha256"]["proof"] == hashlib.sha256(
    proof_path.read_bytes()).hexdigest()
assert result["source_sha256"]["asm"] == hashlib.sha256(
    asm_path.read_bytes()).hexdigest()
assert result["source_sha256"]["bench"] == hashlib.sha256(
    bench_path.read_bytes()).hexdigest()
assert result["barrett"]["proved_output_range"] == [-1728, 1728]
assert result["montgomery_identity"]["proved_output_range"] == [-1794, 1802]
assert result["barrett"]["median_cycles"] == 165.0
assert result["montgomery_identity"]["median_cycles"] == 93.0
assert result["paired"]["median_montgomery_minus_barrett_cycles"] == -72.0
assert result["paired"]["montgomery_faster_launches"] == 9
assert result["winner"] == "Montgomery-identity"
assert result["promotion_eligible"] is False
print("G1C-M3C3: full-array Barrett 165 vs Montgomery identity 93 cycles; "
      "9/9 paired launches select Montgomery; isolated control only")
