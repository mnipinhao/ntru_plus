#!/usr/bin/env python3
"""Audit returned M5K artifacts, fixed-tail lifetime, and physical ABI."""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from pathlib import Path

from optimize import VECTOR_OUTPUTS, allocated_liveouts


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gt864_forward_two_ntt9_blocks.sym.S"
ALLOC = ROOT / "slothy-output/gt864_forward_two_ntt9_blocks.n1.alloc.S"
OPT = ROOT / "slothy-output/gt864_forward_two_ntt9_blocks.n1.opt.S"
LOG = ROOT / "slothy-output/gt864_forward_two_ntt9_blocks.n1.log"
START = "gt864_forward_two_ntt9_blocks_slothy_start:"
END = "gt864_forward_two_ntt9_blocks_slothy_end:"
ALLOWED = {*range(0, 8), *range(16, 32)}
FORBIDDEN = set(range(8, 16))
EXPECTED = Counter({
    "trn1": 24, "trn2": 24, "ldr": 32, "sqrdmulh": 48,
    "mul": 48, "mls": 48, "orr": 13, "add": 72, "sub": 24,
})


def source_instructions(path: Path) -> list[str]:
    lines = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("//", 1)[0].strip()
        if line and not line.endswith(":") and not line.startswith(("/*", "*", "*/")):
            lines.append(line)
    return lines


def emitted(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    region = text[text.index(START):text.index(END)]
    lines = []
    for raw in region.splitlines():
        line = raw.split("//", 1)[0].strip()
        if line and not line.endswith(":"):
            lines.append(line)
    return lines


symbolic = source_instructions(SOURCE)
allocated = emitted(ALLOC)
optimized = emitted(OPT)
assert len(symbolic) == len(allocated) == len(optimized) == 333
symbolic_mnemonics = [line.split()[0].lower() for line in symbolic]
allocated_mnemonics = [line.split()[0].lower() for line in allocated]
optimized_mnemonics = [line.split()[0].lower() for line in optimized]
assert Counter(symbolic_mnemonics) == EXPECTED
assert allocated_mnemonics == symbolic_mnemonics
assert Counter(optimized_mnemonics) == EXPECTED

source_physical = re.findall(
    r"(?<![A-Za-z0-9_<])v([0-9]|[12][0-9]|3[01])\b",
    "\n".join(symbolic), flags=re.IGNORECASE,
)
assert source_physical == ["16", "16"]
assert symbolic.count("orr V<hold8>.16b, v16.16b, v16.16b") == 1

for name, instructions in (("allocated", allocated), ("optimized", optimized)):
    text = "\n".join(instructions)
    registers = {
        int(value) for value in re.findall(
            r"\bv([0-9]|[12][0-9]|3[01])\b", text, flags=re.IGNORECASE
        )
    }
    assert registers == ALLOWED, (name, registers)
    assert not registers.intersection(FORBIDDEN)
    gprs = set(re.findall(r"\b(?:sp|[xw][0-9]+)\b", text, flags=re.IGNORECASE))
    assert gprs == {"x3"}, (name, gprs)
    assert sum(line.lower().startswith("ldr ") for line in instructions) == 32
    assert all(re.fullmatch(r"ldr q[0-9]+, \[x3\], #16", line,
                            flags=re.IGNORECASE)
               for line in instructions if line.lower().startswith("ldr "))
    assert not re.search(r"\b(?:st[1-4rps]?|b|bl|br|ret)\b", text,
                         flags=re.IGNORECASE)
    assert "V<" not in text and "Q<" not in text
    first_v16 = next(line for line in instructions
                     if re.search(r"\bv16\b", line, flags=re.IGNORECASE))
    assert re.fullmatch(r"orr v[0-9]+\.16b, v16\.16b, v16\.16b",
                        first_v16, flags=re.IGNORECASE), (name, first_v16)

liveouts = allocated_liveouts(ALLOC)
expected_liveouts = [
    "v20", "v25", "v5", "v1", "v27", "v22", "v29", "v30", "v19",
    "v24", "v26", "v23", "v28", "v21", "v7", "v3", "v17", "v31",
]
assert VECTOR_OUTPUTS == [f"out{index}" for index in range(18)]
assert liveouts == expected_liveouts

driver = (ROOT / "optimize.py").read_text(encoding="utf-8")
assert "functional_only = True" in driver
assert "allow_reordering = False" in driver
assert "allocated_liveouts(source)" in driver
assert "split_heuristic = True" in driver
assert "split_heuristic_factor = 16.0" in driver
assert driver.count("allow_spills = False") == 1
assert "range(8, 16)" in driver

log = LOG.read_text(encoding="utf-8")
assert log.count("SLOTHY version: 0.2.2") == 2
assert log.count("Instructions in body: 333") == 2
assert "gt864-forward-two-ntt9-blocks-ra" in log
assert "OPTIMAL, wall time: 31.458717 s" in log
assert "gt864_forward_two_ntt9_blocks_slothy_start.slothy.selfcheck:OK!" in log
assert "split.split_heuristic_full:OK!" in log
assert "Traceback" not in log and "neither used nor declared" not in log
assert "Expected cycles: 83" in OPT.read_text(encoding="utf-8")

print("gt864_forward_two_ntt9_blocks_static_gate=pass")
print("symbolic_instruction_count=333")
print("coordinate_transpose_instructions=48")
print("public_constant_loads=32")
print("lane_twist_arithmetic_instructions=48")
print("complete_ntt9_core_instructions=204")
print("fixed_tail_capture_instructions=1")
print("source_fixed_physical_register=v16")
print("available_vector_register_count=24")
print("ra_status=OPTIMAL")
print("schedule_status=split_heuristic_full_OK")
print("n1_proxy_expected_cycles=83")
print("allocated_vector_registers=" + ",".join(f"v{value}" for value in sorted(ALLOWED)))
print("forbidden_vector_registers_used=0")
print("spill_or_stack_instructions=0")
print(f"allocated_sha256={hashlib.sha256(ALLOC.read_bytes()).hexdigest()}")
print(f"optimized_sha256={hashlib.sha256(OPT.read_bytes()).hexdigest()}")
print(f"log_sha256={hashlib.sha256(LOG.read_bytes()).hexdigest()}")
