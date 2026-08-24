#!/usr/bin/env python3
"""Gate the post-M3 Hwa compatibility audit."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "generated/hwa-compatibility-audit.json").read_text())

plane = data["semantic_plane_contract"]
assert plane["vectors"] == 72
assert plane["component_checks"] == 1152
assert data["critical_distinction"]["F0_fastest_forward"]["exact_terminal_major_plane"] is False
assert data["critical_distinction"]["F1_B1_M3_producer"]["exact_terminal_major_plane"] is True
assert data["critical_distinction"]["F1_B1_M3_producer"]["producer_debt_cycles"] == 58.5
assert data["m3_price"] == {
    "C0": 1136.0, "C1": 1108.0, "C2": 1099.0,
    "C1_minus_C0": -28.0, "C2_minus_C1": -9.5,
    "C2_minus_C0": -37.5,
}
assert data["decision"]["fork_new_Hwa_candidate_now"] is False
assert data["decision"]["freeze_shared_semantic_plane_contract"] is True
assert data["shared_864_projection"]["864_terminal_degree_and_vectors"] == [3, 54]
print("HWA-A0: semantic coefficient planes confirmed; F0/F1 distinction and next inverse-NTT9 gate fixed")
