#!/usr/bin/env python3
"""Lock the current T0-beta inter-layer Barrett range audit."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
report = json.loads((ROOT / "generated/gt9x16-forward-reduction-audit.json").read_text())

assert report["schema"] == "gt9x16-forward-reduction-audit/v1"
assert report["forward_rebase_cycles"] == {
    "direction": "GT-minus-Official",
    "m": 76.10416666666674,
    "r": 78.8125,
}
assert report["frozen_contract"]["producer"] == (
    "persistent-AoS + Natural-Q + T0-beta")
assert report["frozen_contract"]["new_asm"] is False
assert report["search"]["masks"] == 512
assert report["search"]["valid_masks"] == 16

minimum = report["minimum"]
assert minimum["retained_per_branch_qblock"] == 5
assert minimum["removed_per_branch_qblock"] == 4
assert minimum["retained_per_forward"] == 40
assert minimum["removed_per_forward"] == 32
assert minimum["valid_minimum_masks"] == 1

selected = minimum["selected"]
assert selected["mask"] == 79
assert selected["kept_registers"] == [7, 8, 15, 10, 13]
assert selected["removed_registers"] == [11, 9, 14, 12]
assert selected["peak_absolute_bound"] == 21333
assert len(selected["branches"]) == 2
for branch in selected["branches"]:
    assert branch["valid"] is True
    assert len(branch["second_radix3"]) == 3
    assert all(group["all_signed_i16"]
               for group in branch["second_radix3"])
    assert len(branch["ntt16_rows"]) == 9
    assert all(stage["all_signed_i16"]
               for row in branch["ntt16_rows"]
               for stage in row["stages"])

decision = report["decision"]
assert decision["asm_authorized"] is False
assert decision["cross_axis_wavefront"] == "not-authorized"
assert decision["ntt9_DAG_change"] == "not-authorized"

print("Forward reduction audit: unique 5/9 keep mask removes 32/72 "
      "Barrett vectors per forward with both T0-beta branches i16-safe")
