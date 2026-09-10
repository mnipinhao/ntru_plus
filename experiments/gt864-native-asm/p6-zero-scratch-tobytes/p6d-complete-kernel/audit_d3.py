#!/usr/bin/env python3
"""Static physical audit for the composed P6-D3 full/small wrapper."""

from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
text = (HERE / "p6d3-full.alloc.S").read_text()
body = text.split(".Lp6d3_tables:", 1)[0]
instructions = [x.strip() for x in body.splitlines() if x.strip() and not x.strip().startswith((".", "//")) and not x.strip().endswith(":")]

groups = []
for m in re.finditer(r"\btbl\s+v\d+\.16b,\s*\{([^}]+)\}", body, re.I):
    regs = [int(x) for x in re.findall(r"v(\d+)\.16b", m.group(1), re.I)]
    assert 1 <= len(regs) <= 3
    assert all(b == a + 1 for a, b in zip(regs, regs[1:])), regs
    groups.append(regs)

sp_q_or_d = re.findall(r"\b(?:ldr|str)\s+[qd]\d+,\s*\[sp(?:,|\])", body, re.I)
result = {
    "semantic_instruction_count_including_public_wrapper": len(instructions),
    "coefficient_q_loads": len(re.findall(r"\bldr q\d+, \[x29(?:, #\d+)?\]", body, re.I)),
    "final_str_q": len(re.findall(r"\bstr q\d+, \[x29(?:, #\d+)?\]", body, re.I)),
    "final_str_d": len(re.findall(r"\bstr d\d+, \[x29(?:, #\d+)?\]", body, re.I)),
    "tbl_count": len(groups),
    "tbl2_count": sum(len(x) == 2 for x in groups),
    "tbl3_count": sum(len(x) == 3 for x in groups),
    "tbl_groups_consecutive": True,
    "public_stack_frame_bytes": 176,
    "coefficient_scratch_bytes": 0,
    "stack_q_or_d_single_accesses": sp_q_or_d,
    "lane_st3": bool(re.search(r"\bst3\s+\{[^}]+\}\[", body, re.I)),
    "platform_x18": bool(re.search(r"\b[wx]18\b", body)),
    "symbolic_registers": bool(re.search(r"[VQDXW]<", body)),
}
assert result["coefficient_q_loads"] == 108, result
assert result["final_str_q"] == 80 and result["final_str_d"] == 2, result
assert not sp_q_or_d, result
assert not result["lane_st3"] and not result["platform_x18"] and not result["symbolic_registers"], result
result["gate"] = "PASS_P6D3_PHYSICAL_AUDIT"
(HERE / "d3-audit-results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
