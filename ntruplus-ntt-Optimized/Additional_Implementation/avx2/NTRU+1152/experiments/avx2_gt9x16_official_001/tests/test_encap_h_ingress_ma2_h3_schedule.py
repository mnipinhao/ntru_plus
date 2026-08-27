#!/usr/bin/env python3
"""Evidence checks for the exact H3 decode-to-MA2 schedule."""
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "generated/encap-h-ingress-ma2-h3-schedule.json").read_text())

assert data["schema"] == "encap-h-ingress-ma2-h3-schedule/v1"
assert all(data["gates"].values())
assert data["register_flow"]["peak_ymm"] == 16
assert data["register_flow"]["spill"] == 0
assert data["register_flow"]["frame_scratch"] == 0
assert data["decoder"]["validation"]["schedule_ledger"]["peak_ymm"] == 12
assert data["decoder"]["validation"]["schedule_ledger"]["validation_delta_per_block"] == 6
assert data["formation"]["h_stores"] == 0
assert data["formation"]["h_reloads"] == 0
assert data["formation"]["routes_total"] == {
    "consumer_required": 360, "decoder_intrinsic": 216,
    "pure_h_abi_formation": 0,
}

blocks = data["formation"]["blocks"]
assert len(blocks) == 9
owners = set()
for block in blocks:
    assert len(block["pair_flow"]) == 4
    assert block["tile_a"] != block["tile_b"]
    for coefficient, pair in enumerate(block["pair_flow"]):
        assert pair["coefficient"] == coefficient
        assert pair["decoded_source_vectors"] == [coefficient, coefficient + 4]
        assert pair["route_absorption"]["consumer_required"] == 10
        assert pair["route_absorption"]["pure_h_abi_formation"] == 0
        for tile in ("tile_a", "tile_b"):
            owner = pair[tile]["owner"]
            assert owner["terminal_coefficient"] == coefficient
            owners.add((owner["branch"], owner["p"], coefficient))
assert len(owners) == 72

ledger = data["ma2"]["candidate_ledger"]
assert ledger == data["ma2"]["linked_control_ledger"]
assert ledger == {"c_stores": 72, "h_r2_montgomery": 72,
                  "h_times_r_montgomery": 288, "lambda_montgomery": 54,
                  "m_loads": 72, "r_loads": 72, "tiles": 18}
assert data["movement_delta_vs_h1"]["h_vector_stores"] == -72
assert data["movement_delta_vs_h1"]["h_vector_reloads"] == -72
assert data["decision"]["h3_namespaced_asm"] == "authorized-next"
assert data["decision"]["benchmark"] is False
print("H3 exact schedule evidence: peak16, raw-DAG preserved, zero h boundary")
