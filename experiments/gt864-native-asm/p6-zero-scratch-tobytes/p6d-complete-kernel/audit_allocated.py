#!/usr/bin/env python3
"""Audit the two physical P6-D1 producer allocations."""

from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent


def region(path: Path, start: str, end: str) -> str:
    text = path.read_text()
    body = text.split(start + ":", 1)[1].split(end + ":", 1)[0]
    return "\n".join(line.split("//", 1)[0] for line in body.splitlines())


def audit(path: Path, start: str, end: str, expected_stack_bytes: int) -> dict[str, object]:
    body = region(path, start, end)
    groups: list[list[int]] = []
    for match in re.finditer(r"\btbl\s+v\d+\.16[bB],\s*\{([^}]+)\}", body):
        regs = [int(x) for x in re.findall(r"v(\d+)\.16[bB]", match.group(1))]
        assert len(regs) in (1, 2, 3), regs
        assert all(b == a + 1 for a, b in zip(regs, regs[1:])), regs
        groups.append(regs)

    stack_refs = [int(x or 0) for x in re.findall(r"\[sp(?:,\s*#(\d+))?\]", body)]
    stack_stores = [int(x or 0) for x in re.findall(r"\bstr\s+(?:q\d+|x\d+),\s*\[sp(?:,\s*#(\d+))?\]", body)]
    failures = {
        "uses_platform_x18": bool(re.search(r"\b[wx]18\b", body)),
        "symbolic_register": bool(re.search(r"[VQDXW]<", body)),
        "non_stack_memory_write": bool(re.search(r"\bstr\s+[^,]+,\s*\[(?!sp\b)", body)),
        "unexpected_stack_extent": bool(stack_refs) and max(stack_refs) >= expected_stack_bytes,
    }
    assert not any(failures.values()), failures
    assert stack_stores, "synthetic live-out stores missing"
    return {
        "instruction_count": sum(
            bool(line.strip()) and not line.lstrip().startswith((".", "//"))
            for line in body.splitlines()
        ),
        "tbl_count": len(groups),
        "tbl3_count": sum(len(x) == 3 for x in groups),
        "tbl_groups_consecutive": True,
        "uses_fixed_coefficient_base_x29": bool(re.search(r"\[x29\b", body)),
        "uses_fixed_public_table_base_x30": bool(re.search(r"\[x30\b", body)),
        "synthetic_stack_store_count": len(stack_stores),
        "synthetic_stack_extent_bytes": max(stack_stores) + 8,
        "failures": failures,
    }


result = {
    "pair0": audit(HERE / "producer.pair0.alloc.S", "gt864_p6d_pair0_start", "gt864_p6d_pair0_end", 216),
    "pair1": audit(HERE / "producer.pair1.alloc.S", "gt864_p6d_pair1_start", "gt864_p6d_pair1_end", 432),
    "note": "Stack accesses are synthetic live-out materialization for the oracle/allocation boundary, not proposed coefficient scratch.",
    "gate": "PASS_P6D1_PHYSICAL_ALLOCATION_AUDIT",
}
(HERE / "allocated-audit.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
