#!/usr/bin/env python3
"""Audit returned M5M assembly, one-bank memory traffic, ABI, and logs."""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from pathlib import Path

from optimize import allocated_liveouts

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gt864_forward_one_bank.sym.S"
ALLOC = ROOT / "slothy-output/gt864_forward_one_bank.n1.alloc.S"
OPT = ROOT / "slothy-output/gt864_forward_one_bank.n1.opt.S"
RA_LOG = ROOT / "slothy-output/gt864_forward_one_bank.ra.log"
SCHEDULE_LOG = ROOT / "slothy-output/gt864_forward_one_bank.schedule.log"
START = "gt864_forward_one_bank_slothy_start:"
END = "gt864_forward_one_bank_slothy_end:"
ALLOWED_VECTORS = {*range(0, 8), *range(16, 32)}
FORBIDDEN_VECTORS = set(range(8, 16))
EXPECTED = Counter({
    "add": 108, "mul": 102, "sqrdmulh": 102, "mls": 102,
    "ldr": 72, "sub": 60, "trn1": 27, "trn2": 27,
    "ld1": 16, "orr": 13, "movi": 2, "tbl": 2,
})
EXPECTED_LIVEOUTS = [
    "v26", "v30", "v7", "v25", "v19", "v21", "v3", "v24", "v22",
    "v23", "v2", "v0", "v31", "v28", "v18", "v5", "v29", "v20",
]


def emitted(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    region = text[text.index(START):text.index(END)]
    return [line for raw in region.splitlines()
            if (line := raw.split("//", 1)[0].strip())
            and not line.endswith(":")]


source = emitted(SOURCE)
alloc = emitted(ALLOC)
opt = emitted(OPT)
assert len(source) == len(alloc) == len(opt) == 633
for name, instructions in (("source", source), ("allocated", alloc), ("optimized", opt)):
    assert Counter(x.split()[0].lower() for x in instructions) == EXPECTED, name

# Allocation preserves the source order. Scheduling may reorder, but not add,
# remove, or change the opcode multiset.
assert [x.split()[0].lower() for x in alloc] == [
    x.split()[0].lower() for x in source
]

for name, instructions in (("allocated", alloc), ("optimized", opt)):
    text = "\n".join(instructions)
    vectors = {int(x) for x in re.findall(
        r"\bv([0-9]|[12][0-9]|3[01])\b", text, re.I
    )}
    assert vectors == ALLOWED_VECTORS and not vectors & FORBIDDEN_VECTORS, (
        name, vectors
    )
    assert set(re.findall(r"\b(?:sp|[xw][0-9]+)\b", text, re.I)) == {
        "x0", "x1", "x2", "x3", "x4", "x5"
    }

    lane_loads = [x for x in instructions if x.lower().startswith("ld1 ")]
    assert len(lane_loads) == 16
    assert all(re.fullmatch(
        r"ld1 \{ v[0-9]+\.h \}\[[0-7]\], \[x1\], x4", x, re.I
    ) for x in lane_loads)

    ldrs = [x for x in instructions if x.lower().startswith("ldr ")]
    assert len(ldrs) == 72
    load_forms = Counter(
        re.sub(r"q[0-9]+", "qN", x, flags=re.I) for x in ldrs
    )
    assert load_forms == Counter({
        "ldr qN, [x0], #16": 16,
        "ldr qN, [x2], #16": 22,
        "ldr qN, [x3], #16": 32,
        "ldr qN, [x5], #16": 2,
    }), (name, load_forms)

    assert not re.search(r"\b(?:st[1-4rps]?|b|bl|br|ret)\b", text, re.I)
    assert "V<" not in text and "Q<" not in text

    # v17/v16 are defined by the two tail tbls, then only read by M5K.
    for fixed, expected_uses in ((17, 3), (16, 2)):
        uses = [(i, x) for i, x in enumerate(instructions)
                if re.search(fr"\bv{fixed}\b", x, re.I)]
        assert len(uses) == expected_uses
        assert uses[0][1].lower().startswith(f"tbl v{fixed}.16b,")
        assert all(not re.match(fr"(?:tbl|mov|orr|add|sub|mul|sqrdmulh|mls) v{fixed}\b",
                                x, re.I) for _, x in uses[1:])

assert allocated_liveouts(ALLOC) == EXPECTED_LIVEOUTS
driver = (ROOT / "optimize.py").read_text(encoding="utf-8")
assert 'pattern = "ld1 { <Va>.<dt> }[<index>], [<Xa>], <Xm>"' in driver
assert 'inputs = ["Xm"]' in driver and 'in_outs = ["Va", "Xa"]' in driver
assert "allow_spills = False" in driver
assert "split_heuristic_factor = 32.0" in driver

ra_log = RA_LOG.read_text(encoding="utf-8")
schedule_log = SCHEDULE_LOG.read_text(encoding="utf-8")
assert "SLOTHY version: 0.2.2" in ra_log
assert "Instructions in body: 633" in ra_log
assert "OPTIMAL, wall time: 143.014540 s" in ra_log
assert "slothy.selfcheck:OK!" in ra_log
assert "Traceback" not in ra_log
assert "SLOTHY version: 0.2.2" in schedule_log
assert "Instructions in body: 633" in schedule_log
assert "split.split_heuristic_full:OK!" in schedule_log
assert "Traceback" not in schedule_log
assert "Expected cycles: 158" in OPT.read_text(encoding="utf-8")

print("gt864_forward_one_bank_static_gate=pass")
print("symbolic_instruction_count=633")
print("meaningful_coefficient_halfwords=144")
print("tail_lane_loads=16")
print("main_vector_loads=16")
print("public_constant_loads=56")
print("coefficient_stores=0")
print("ra_status=OPTIMAL")
print("schedule_status=split_heuristic_full_OK")
print("n1_proxy_expected_cycles=158")
print("forbidden_vector_registers_used=0")
print("spill_or_stack_instructions=0")
for label, path in (
    ("allocated", ALLOC), ("optimized", OPT),
    ("ra_log", RA_LOG), ("schedule_log", SCHEDULE_LOG),
):
    print(f"{label}_sha256={hashlib.sha256(path.read_bytes()).hexdigest()}")
