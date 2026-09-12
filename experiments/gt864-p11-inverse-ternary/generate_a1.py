#!/usr/bin/env python3
"""Create P11-A1's k-major main scratch layout from the proven A0 producers."""

import json
import re
from pathlib import Path

P = Path(__file__).resolve().parent
STORE = re.compile(r"(\s*str d\d+, \[)x1(, #)(\d+)(\] // P11 scratch record k=(\d+))")
source = (P / "candidate-main.S").read_text()
seen = []


def replace(match):
    old, k = int(match.group(3)), int(match.group(5))
    assert old == 8 * k
    seen.append(k)
    return f"{match.group(1)}x0{match.group(2)}{48 * k}{match.group(4)}"


output = STORE.sub(replace, source)
assert sorted(seen) == list(range(32))
(P / "candidate-main-a1.S").write_text(output)
report = {
    "status": "pass",
    "layout": "k-major six-D records",
    "record_bytes": 48,
    "records": 32,
    "producer_instructions_changed": 0,
    "producer_register_contract": "x1 remains the NTT16 input bank; x0 is repurposed as the k-major scratch output base",
    "route_loads_per_record": "3 LDR Q + 1 LDR D instead of 3 LDR D + 3 LDR X + 3 INS + 1 LDR D",
}
(P / "a1-generation.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
