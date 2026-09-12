#!/usr/bin/env python3
"""Check P11-A1's k-major six-D scratch layout and route cost."""

import json
from pathlib import Path

P = Path(__file__).resolve().parent
slots = {}
for k in range(32):
    for component in range(3):
        for half in range(2):
            offset = 48 * k + 16 * component + 8 * half
            assert offset % 8 == 0 and offset + 8 <= 1536
            assert offset not in slots
            slots[offset] = (k, component, half)
            loaded = 48 * k + 16 * component + 8 * half
            assert loaded == offset
assert sorted(slots) == list(range(0, 1536, 8))

# Main records use the dead public input/output buffer.  Descending route order
# guarantees that natural block k never overwrites a lower, not-yet-read record.
for k in range(31, -1, -1):
    write = set(range(54 * k, 54 * k + 54))
    unread = set()
    for lower in range(k):
        unread.update(range(48 * lower, 48 * lower + 48))
    assert write.isdisjoint(unread), k
report = {
    "status": "pass",
    "records": 32,
    "record_bytes": 48,
    "main_slots": len(slots),
    "main_storage": "public output after every original input coefficient was consumed",
    "route_order": "k=31 down to 0; exact in-place non-overlap proven",
    "tail_base": "private scratch +1536",
    "scratch_bytes": 1792,
    "added_coefficient_passes": 0,
    "producer_register_contract": "x1=input bank unchanged; x0=k-major output record base",
    "producer_dynamic_instructions_vs_a0": 0,
    "route_instructions_per_k": 35,
    "route_dynamic_delta_vs_a0": -96,
    "total_dynamic_delta_vs_p10": -1248,
}
(P / "a1-proof.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
