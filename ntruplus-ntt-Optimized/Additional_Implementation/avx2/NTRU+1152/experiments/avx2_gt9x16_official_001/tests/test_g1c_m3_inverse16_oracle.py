#!/usr/bin/env python3
"""Gate the generated G1C-M3 three-way inverse16 contract."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "generated/g1c-m3-inverse16-oracle.json").read_text())

assert data["inverse_order"] == [1, 2, 4, 8]
assert set(data["variants"]) == {"M3-C0", "M3-C1", "M3-C2"}
assert data["paired_decomposition"]["C2_minus_C1"].startswith("persistent")
assert data["independent_price_ledger"]["accounting_rule"].startswith(
    "F1 and F5 are orthogonal")
assert data["range_gate"]["asm_authorized"] is False
assert data["range_gate"]["BMScale_first_failure"] == {
    "distance": 2,
    "operation": "sum",
    "physical_lanes": [0, 2],
    "interval": [-55296, 55296],
}
for row in data["rows"]:
    assert [stage["distance"] for stage in row["inverse_stages"]] == [1, 2, 4, 8]
    for stage in row["inverse_stages"]:
        assert len(stage["pairs"]) == 8
        assert sorted(lane for pair in stage["pairs"]
                      for lane in pair["physical_lanes"]) == list(range(16))
    assert row["range"]["BMScale_Rminus1"][
        "first_independent_interval_failure"]["distance"] == 2

print("G1C-M3A: D1/D2/D4/D8 maps and C0/C1/C2 decomposition pass; "
      "independent range envelope blocks lazy ASM at D2")
