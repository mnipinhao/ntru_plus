#!/usr/bin/env python3
"""Audit returned M5L assembly, memory shape, ABI, and Slothy evidence."""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from pathlib import Path

from optimize import allocated_liveouts

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gt864_forward_tail_ntt16.sym.S"
ALLOC = ROOT / "slothy-output/gt864_forward_tail_ntt16.n1.alloc.S"
OPT = ROOT / "slothy-output/gt864_forward_tail_ntt16.n1.opt.S"
LOG = ROOT / "slothy-output/gt864_forward_tail_ntt16.n1.log"
START = "gt864_forward_tail_ntt16_slothy_start:"
END = "gt864_forward_tail_ntt16_slothy_end:"
ALLOWED = {*range(0, 8), *range(16, 32)}
FORBIDDEN = set(range(8, 16))
EXPECTED = Counter({
    "ld1": 16, "ldr": 13, "mul": 6, "sqrdmulh": 6, "mls": 6,
    "add": 4, "sub": 4, "trn1": 3, "trn2": 3, "movi": 2, "tbl": 2,
})


def emitted(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    region = text[text.index(START):text.index(END)]
    return [line for raw in region.splitlines()
            if (line := raw.split("//", 1)[0].strip())
            and not line.endswith(":")]


alloc = emitted(ALLOC)
opt = emitted(OPT)
assert len(alloc) == len(opt) == 65
assert Counter(x.split()[0].lower() for x in alloc) == EXPECTED
assert Counter(x.split()[0].lower() for x in opt) == EXPECTED
assert [x.split()[0].lower() for x in alloc] == [
    x.split()[0].lower() for x in emitted(SOURCE)
]

for name, instructions in (("allocated", alloc), ("optimized", opt)):
    text = "\n".join(instructions)
    vectors = {int(x) for x in re.findall(r"\bv([0-9]|[12][0-9]|3[01])\b", text, re.I)}
    assert vectors <= ALLOWED and not vectors & FORBIDDEN, (name, vectors)
    assert set(re.findall(r"\b(?:sp|[xw][0-9]+)\b", text, re.I)) == {"x1", "x2", "x4"}
    lane_loads = [x for x in instructions if x.lower().startswith("ld1 ")]
    assert len(lane_loads) == 16
    assert all(re.fullmatch(r"ld1 \{ v[0-9]+\.h \}\[[0-7]\], \[x1\], x4", x, re.I)
               for x in lane_loads)
    public_loads = [x for x in instructions if x.lower().startswith("ldr ")]
    assert len(public_loads) == 13
    assert all(re.fullmatch(r"ldr q[0-9]+, \[x2\], #16", x, re.I) for x in public_loads)
    assert not re.search(r"\b(?:st[1-4rps]?|b|bl|br|ret)\b", text, re.I)
    assert "V<" not in text and "Q<" not in text

liveouts = allocated_liveouts(ALLOC)
assert liveouts == ["v27", "v7"]
driver = (ROOT / "optimize.py").read_text(encoding="utf-8")
assert 'pattern = "ld1 { <Va>.<dt> }[<index>], [<Xa>], <Xm>"' in driver
assert 'inputs = ["Xm"]' in driver and 'in_outs = ["Va", "Xa"]' in driver
assert "allow_spills = False" in driver
assert "allocated_liveouts(source)" in driver

log = LOG.read_text(encoding="utf-8")
assert log.count("SLOTHY version: 0.2.2") == 2
assert log.count("Instructions in body: 65") == 2
assert "OPTIMAL, wall time: 0.916156 s" in log
assert "slothy.selfcheck:OK!" in log
assert "split.split_heuristic_full:OK!" in log
assert "Traceback" not in log
assert "Expected cycles: 16" in OPT.read_text(encoding="utf-8")

print("gt864_forward_tail_ntt16_static_gate=pass")
print("symbolic_instruction_count=65")
print("exact_coefficient_lane_loads=16")
print("public_constant_loads=13")
print("coefficient_pointer_advance_bytes=256")
print("constant_pointer_advance_bytes=208")
print("ra_status=OPTIMAL")
print("schedule_status=split_heuristic_full_OK")
print("n1_proxy_expected_cycles=16")
print("forbidden_vector_registers_used=0")
print("spill_or_stack_instructions=0")
for label, path in (("allocated", ALLOC), ("optimized", OPT), ("log", LOG)):
    print(f"{label}_sha256={hashlib.sha256(path.read_bytes()).hexdigest()}")
