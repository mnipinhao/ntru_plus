#!/usr/bin/env python3
"""Regression checks for the live-terminal dual-output MAP1 gate."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "generated/scale1-r-dual-output-map1.json").read_text())
assert data["schema"] == "scale1-r-dual-output-map1/v1"
assert len(data["tiles"]) == 18
assert all(data["gates"].values())
assert data["decision"]["asm_authorized"] is True
assert data["decision"]["native_kem_authorized"] is False
assert data["ledger"] == {
    "tiles": 18,
    "state_stores_retained": 72,
    "serializer_reloads": [72, 0],
    "register_moves_added": 0,
    "serializer_arithmetic_delta": 0,
    "serializer_routing_delta": 0,
    "serializer_output_stores_delta": 0,
    "expected_instruction_delta_vs_forward_plus_serializer": -72,
    "peak_ymm": 14,
    "extra_scratch_bytes": 0,
}
covered = []
for tile in data["tiles"]:
    assert sorted(tile["terminal_source_registers"]) == list(range(4))
    assert sorted(tile["serializer_register_rename_0_to_7"]) == list(range(8))
    assert tile["serializer_reloads_removed"] == 4
    assert tile["register_moves_added"] == 0
    covered.extend(range(tile["byte_offset"], tile["byte_offset"] + 96))
assert sorted(covered) == list(range(1728))
print("scale-1 r dual-output MAP1: ok")
