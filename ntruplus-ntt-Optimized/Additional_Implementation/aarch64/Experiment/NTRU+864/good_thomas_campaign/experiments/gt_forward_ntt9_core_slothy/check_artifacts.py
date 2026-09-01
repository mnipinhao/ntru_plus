#!/usr/bin/env python3
"""Static and returned-artifact audit for the M5I complete NTT9 core."""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from pathlib import Path

from optimize import allocated_liveouts


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gt864_forward_ntt9_core.sym.S"
ALLOC = ROOT / "slothy-output/gt864_forward_ntt9_core.n1.alloc.S"
OPT = ROOT / "slothy-output/gt864_forward_ntt9_core.n1.opt.S"
LOG = ROOT / "slothy-output/gt864_forward_ntt9_core.n1.log"
START = "gt864_forward_ntt9_core_slothy_start:"
END = "gt864_forward_ntt9_core_slothy_end:"
ALLOWED = {*range(0, 8), *range(25, 32)}


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
assert len(symbolic) == len(allocated) == len(optimized) == 102
symbolic_mnemonics = [line.split()[0].lower() for line in symbolic]
allocated_mnemonics = [line.split()[0].lower() for line in allocated]
optimized_mnemonics = [line.split()[0].lower() for line in optimized]
expected = Counter({"orr": 6, "add": 36, "sub": 12,
                    "sqrdmulh": 16, "mul": 16, "mls": 16})
assert Counter(symbolic_mnemonics) == expected
assert allocated_mnemonics == symbolic_mnemonics  # RA-only preserves order.
assert Counter(optimized_mnemonics) == expected

assert not re.search(r"(?<![A-Za-z0-9_<])v(?:[0-9]|[12][0-9]|3[01])\b",
                     "\n".join(symbolic), flags=re.IGNORECASE)
assert "2a" not in "\n".join(symbolic) and "3a" not in "\n".join(symbolic)

for name, instructions in (("allocated", allocated), ("optimized", optimized)):
    text = "\n".join(instructions)
    registers = {
        int(value) for value in re.findall(
            r"\bv([0-9]|[12][0-9]|3[01])\b", text, flags=re.IGNORECASE
        )
    }
    assert registers == ALLOWED, (name, registers)
    assert not registers.intersection(range(8, 25))
    assert not re.search(r"\b(?:sp|x[0-9]+|w[0-9]+)\b", text,
                         flags=re.IGNORECASE)
    assert not re.search(r"\b(?:ld[1-4rps]?|st[1-4rps]?|b|bl|br|ret)\b",
                         text, flags=re.IGNORECASE)
    assert "V<" not in text and "Q<" not in text

liveouts = allocated_liveouts(ALLOC)
assert liveouts == ["v0", "v25", "v2", "v7", "v29", "v30", "v3", "v26", "v28"]

driver = (ROOT / "optimize.py").read_text(encoding="utf-8")
assert "functional_only = True" in driver
assert "allow_reordering = False" in driver
assert "allocated_liveouts(source)" in driver
assert "split_heuristic = True" in driver
assert driver.count("allow_spills = False") == 1
assert "range(8, 25)" in driver

log = LOG.read_text(encoding="utf-8")
assert log.count("SLOTHY version: 0.2.2") == 2
assert log.count("Instructions in body: 102") == 2
assert "gt864-forward-ntt9-core-ra" in log and "OPTIMAL" in log
assert "gt864-forward-ntt9-core-ra.gt864_forward_ntt9_core_slothy_start.slothy.selfcheck:OK!" in log
assert "split.split_heuristic_full:OK!" in log
assert "allocated_liveouts=out0:v0,out1:v25,out2:v2,out3:v7,out4:v29,out5:v30,out6:v3,out7:v26,out8:v28" in log
assert "neither used nor declared" not in log
assert "Traceback" not in log
assert "Expected cycles: 25" in OPT.read_text(encoding="utf-8")

print("gt864_forward_ntt9_core_static_gate=pass")
print("symbolic_instruction_count=102")
print("b3_count=6")
print("eta_product_count=4")
print("physical_register_tokens=0")
print("available_vector_register_count=15")
print("ra_status=OPTIMAL")
print("schedule_status=split_heuristic_full_OK")
print("n1_proxy_expected_cycles=25")
print("allocated_vector_registers=" + ",".join(f"v{value}" for value in sorted(ALLOWED)))
print("reserved_vector_registers_used=0")
print("spill_or_stack_instructions=0")
print(f"allocated_sha256={hashlib.sha256(ALLOC.read_bytes()).hexdigest()}")
print(f"optimized_sha256={hashlib.sha256(OPT.read_bytes()).hexdigest()}")
print(f"log_sha256={hashlib.sha256(LOG.read_bytes()).hexdigest()}")
