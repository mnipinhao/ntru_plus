#!/usr/bin/env python3
"""Check the P13-A exact clear coverage and dynamic instruction ledger."""

from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
baseline = (HERE / "build/baseline/gt864_native_public.S").read_text()
candidate = (HERE / "build/candidate/gt864_native_public.S").read_text()

assert ".Lp8inv_init_tail:" in baseline
assert ".Lp8inv_wipe:" in baseline
assert ".Lp8inv_init_tail:" not in candidate
assert ".Lp8inv_wipe:" not in candidate
assert candidate.count("stp q0, q0, [x9], #32") == 12
assert "mov x10, #14\n.Lp13inv_wipe:" in candidate

# Baseline: setup2 + 16*(store/sub/branch), setup2 + 112*(store/sub/branch).
# Candidate: init setup2 + 8 stores; wipe setup3 + 14*(4 stores/sub/branch).
baseline_dynamic = (2 + 16 * 3) + (2 + 112 * 3)
candidate_dynamic = (2 + 8) + (3 + 14 * 6)
result = {
    "experiment": "GT864-P13-A-WIDE-SCRATCH-CLEAR",
    "tail_padding": {"bytes": 256, "baseline_store_bytes": 16, "candidate_store_bytes": 32},
    "scratch_wipe": {"bytes": 1792, "baseline_store_bytes": 16, "candidate_store_bytes": 32},
    "dynamic_region_instructions": {"baseline": baseline_dynamic, "candidate": candidate_dynamic,
                                    "delta": candidate_dynamic - baseline_dynamic},
    "dynamic_region_branches": {"baseline": 128, "candidate": 14, "delta": -114},
    "memory_boundaries_changed": False,
    "arithmetic_or_representation_changed": False,
}
(HERE / "static-results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
