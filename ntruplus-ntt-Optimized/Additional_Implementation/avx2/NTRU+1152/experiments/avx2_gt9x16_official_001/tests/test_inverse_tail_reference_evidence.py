#!/usr/bin/env python3
"""Gate inverse-tail reference audit and paired representation evidence."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
audit_path = ROOT / "generated/g1c-inverse-ntt9-reference-audit.json"
map_path = ROOT / "generated/g1c-inverse-tail-consumer-map.json"
source_path = ROOT / "ref/inverse_ntt9_reference.c"
bench_path = ROOT / "bench/bench_inverse_tail_paired.c"
result_path = ROOT / "results/inverse-tail-reference-intel155h-20260824-001/paired.json"

audit = json.loads(audit_path.read_text())
result = json.loads(result_path.read_text())

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert audit["classification"] == \
    "correctness-first-fixed-loop-reference-not-production-ASM"
assert audit["constant_time_scope"][
    "inlined_radix3_lane_core_conditional_branches"] == 0
assert audit["constant_time_scope"][
    "inlined_radix3_lane_core_variable_divisions"] == 0
assert audit["source_sha256"] == sha(source_path)
assert audit["map_sha256"] == sha(map_path)

assert result["audit_sha256"] == sha(audit_path)
assert result["map_sha256"] == sha(map_path)
assert result["reference_source_sha256"] == sha(source_path)
assert result["bench_source_sha256"] == sha(bench_path)
assert result["correctness"]["independent_matrix_oracle"] is True
assert result["correctness"]["canonical_and_direct_bit_exact"] is True
paired = result["paired"]["B_minus_A"]
assert paired["B_faster_launches"] == 9
assert paired["median_cycles"] == -667.5
assert result["median_cycles"] == {
    "A-canonical-repack-reference-inverse9": 27218.5,
    "B-direct-paper-p-reference-inverse9": 26555.5,
}
assert result["promotion_eligible"] is False

print("G1C inverse-tail reference: direct B is bit-exact and saves 667.5 cycles vs canonical A in 9/9 launches")
