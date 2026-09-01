#!/usr/bin/env python3
"""Audit exact paired-load replacement and its memory boundary."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
baseline = (ROOT / "baseline-region.S").read_text(encoding="utf-8")
candidate = (ROOT / "gt864_forward_one_bank_paired_twist_loads.sym.S").read_text(encoding="utf-8")


def count(text: str) -> int:
    return sum(bool(re.match(r"^\s{4}[a-z][a-z0-9]*\s", line))
               for line in text.splitlines())


assert count(baseline) == 617
start = candidate.index("gt864_forward_one_bank_paired_twist_loads_slothy_start:")
end = candidate.index("gt864_forward_one_bank_paired_twist_loads_slothy_end:")
region = candidate[start:end]
assert count(region) == 601
assert len(re.findall(r"^\s+ldp Q<[^>]+>, Q<[^>]+>, \[x3\], #32", region, re.M)) == 16
assert not re.search(r"^\s+ldr Q<(?:h_)?tw[1-8]p?>, \[x3\], #16$", region, re.M)
for opcode, expected in (("mul", 102), ("sqrdmulh", 102), ("mls", 102)):
    assert len(re.findall(rf"^\s+{opcode}\s", region, re.M)) == expected
assert not re.search(r"^\s+(?:str|st1|stp)\s", region, re.M)
print("candidate_static_gate=pass")
print("baseline_instructions=617")
print("candidate_instructions=601")
print("paired_loads=16")
print("coefficient_stores=0")
print("arithmetic_nodes_unchanged=1")
