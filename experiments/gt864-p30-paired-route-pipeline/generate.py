#!/usr/bin/env python3
"""Expose adjacent P29 records as sixteen two-record Slothy windows."""

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "gt864-p29-direct-st3" / "candidate-main-route.sym.S"

text = SOURCE.read_text()
for pair in range(16):
    even = 2 * pair
    odd = even + 1
    replacements = {
        f"p29_main_route_q{even}_start:": f"p30_route_pair{pair}_start:",
        f"p29_main_route_q{even}_end:": "",
        f"p29_main_route_q{odd}_start:": "",
        f"p29_main_route_q{odd}_end:": f"p30_route_pair{pair}_end:",
    }
    for old, new in replacements.items():
        if text.count(old) != 1:
            raise RuntimeError(f"expected exactly one label: {old}")
        text = text.replace(old, new)

text = re.sub(
    r"// full-vector ST3\.4h only; six-byte tail holes are skipped with public ADD",
    "// P30: adjacent records share one scheduling window; arithmetic and memory multiset unchanged",
    text,
)
text = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
(HERE / "candidate-route.sym.S").write_text(text)
print({"source": str(SOURCE), "output": "candidate-route.sym.S", "windows": 16})
