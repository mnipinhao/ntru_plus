#!/usr/bin/env python3
"""Verify P30 changes only vector allocation and cross-record ordering."""

from collections import Counter
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
BASELINE = HERE.parent / "gt864-p29-direct-st3" / "candidate-main-route.alloc.S"
CANDIDATE = HERE / "candidate-route.alloc.S"


def instructions(path):
    result = []
    for raw in path.read_text().splitlines():
        line = raw.split("//", 1)[0].strip().lower()
        if not line or line.endswith(":") or line.startswith((".", "#")):
            continue
        result.append(re.sub(r"\s+", " ", line))
    return result


before = instructions(BASELINE)
after = instructions(CANDIDATE)
before_ops = Counter(line.split()[0] for line in before)
after_ops = Counter(line.split()[0] for line in after)
if before_ops != after_ops or len(before) != len(after):
    raise SystemExit(f"instruction mismatch: {before_ops - after_ops=} {after_ops - before_ops=}")


def load_offsets(lines):
    result = Counter()
    for line in lines:
        match = re.fullmatch(r"ldr q\d+, \[x1, #(\d+)\]", line)
        if match:
            result[int(match.group(1))] += 1
    return result


if load_offsets(before) != load_offsets(after) or sum(load_offsets(after).values()) != 96:
    raise SystemExit("scratch load-offset multiset mismatch")

pointer_before = [line for line in before if line.startswith("st3 ") or line == "add x2, x2, #6"]
pointer_after = [line for line in after if line.startswith("st3 ") or line == "add x2, x2, #6"]
pointer_shape = re.compile(r"st3 \{v(\d+)\.4h, v(\d+)\.4h, v(\d+)\.4h\}, \[x2\], #24")
for name, sequence in (("baseline", pointer_before), ("candidate", pointer_after)):
    if len(sequence) != 96:
        raise SystemExit(f"{name}: expected 96 pointer operations")
    for record in range(32):
        chunk = sequence[3 * record:3 * record + 3]
        if chunk[2] != "add x2, x2, #6":
            raise SystemExit(f"{name}: pointer ADD misplaced in record {record}")
        for store in chunk[:2]:
            match = pointer_shape.fullmatch(store)
            if not match:
                raise SystemExit(f"{name}: non-full/concrete ST3: {store}")
            registers = tuple(map(int, match.groups()))
            if registers != tuple(range(registers[0], registers[0] + 3)):
                raise SystemExit(f"{name}: non-consecutive ST3 tuple: {store}")

if any(re.search(r"\bsp\b", line) for line in after):
    raise SystemExit("candidate has a stack reference")
if any(re.search(r"\}\[\d+\]", line) for line in after if line.startswith("st3 ")):
    raise SystemExit("candidate has lane ST3")

cycle_values = list(map(int, re.findall(r"Expected cycles:\s+(\d+)", CANDIDATE.read_text())))
if cycle_values != [2] + [43] * 16:
    raise SystemExit(f"unexpected Slothy cycle windows: {cycle_values}")

result = {
    "status": "pass",
    "instructions": len(after),
    "opcode_multiset_equal": True,
    "scratch_load_offset_multiset_equal": True,
    "pointer_sequence": "32 * (ST3.4h post24, ST3.4h post24, ADD x2,#6)",
    "full_vector_st3": 64,
    "lane_st3": 0,
    "sp_references": 0,
    "p29_expected_route_cycles": 928,
    "p30_expected_route_cycles": 688,
    "expected_route_cycle_delta": -240,
}
(HERE / "static-results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
