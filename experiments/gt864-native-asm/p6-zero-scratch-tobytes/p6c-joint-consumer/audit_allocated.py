#!/usr/bin/env python3
"""Audit physical TBL groups and forbidden spill/register artifacts."""

from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent


def physical_region(path: Path, start: str, end: str) -> str:
    text = path.read_text()
    body = text.split(start + ":", 1)[1].split(end + ":", 1)[0]
    return "\n".join(line.split("//", 1)[0] for line in body.splitlines())


def audit(path: Path, start: str, end: str) -> dict[str, object]:
    body = physical_region(path, start, end)
    groups = []
    for match in re.finditer(r"\btbl\s+v\d+\.16[bB],\s*\{([^}]+)\}", body):
        regs = [int(x) for x in re.findall(r"v(\d+)\.16[bB]", match.group(1))]
        assert len(regs) in (2, 3), regs
        assert all(b == a + 1 for a, b in zip(regs, regs[1:])), regs
        groups.append(regs)
    forbidden = {
        "x18": bool(re.search(r"\bx18\b", body)),
        "x29": bool(re.search(r"\b[wx]29\b", body)),
        "x30": bool(re.search(r"\b[wx]30\b", body)),
        "stack_memory": bool(re.search(r"\[(?:sp|x29)(?:,|\])", body)),
        "symbolic_register": bool(re.search(r"[VQDXW]<", body)),
    }
    assert not any(forbidden.values()), forbidden
    return {
        "tbl_count": len(groups),
        "tbl2_count": sum(len(x) == 2 for x in groups),
        "tbl3_count": sum(len(x) == 3 for x in groups),
        "groups": groups,
        "forbidden": forbidden,
    }


result = {
    "row0": audit(
        HERE / "candidate.row0.alloc.S",
        "gt864_p6c_row0_slothy_start",
        "gt864_p6c_row0_slothy_end",
    ),
    "pack_a": audit(
        HERE / "candidate.pack-a.alloc.S",
        "gt864_p6c_pack_a_slothy_start",
        "gt864_p6c_pack_a_slothy_end",
    ),
    "gate": "PASS_PHYSICAL_ALLOCATION_AUDIT",
}
(HERE / "allocated-audit.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
