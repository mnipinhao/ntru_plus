#!/usr/bin/env python3
"""Gate the exact M3 repair-placement result."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "generated/g1c-m3-full-path-proof.json").read_text())

selected = data["selected_D4_tail_plan"]
assert selected["status"] == "rejected-before-fusion"
assert all(row["first_failure"]["distance"] == 2 for row in selected["rows"])
assert selected["first_failure_all_rows"]["interval"] == [-55296, 55296]

alternative = data["proved_conservative_alternative"]
assert alternative["status"] == "range-and-scale-proved"
assert all(row["signed_i16_proved"] for row in alternative["rows"])
assert max(alternative["maximum_absolute_pre_montgomery_by_stage"].values()) < 32768

assert data["authorization"] == {
    "D4_tail_identity_fusion": False,
    "M3_C0_C1_C2_full_path_benchmark": False,
    "next_required": "implement and price the proved D1-large identity placement; do not fuse at D4",
}
print("G1C-M3 full path: D4-only repair rejected at D2; D1-large range closure proved")
