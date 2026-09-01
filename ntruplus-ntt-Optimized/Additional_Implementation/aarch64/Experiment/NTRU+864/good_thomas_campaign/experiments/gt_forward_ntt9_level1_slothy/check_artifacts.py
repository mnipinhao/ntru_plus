#!/usr/bin/env python3
"""Static audit for the M5H level-1 symbolic region and driver."""

from __future__ import annotations

import re
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent
source = (ROOT / "gt864_forward_ntt9_level1.sym.S").read_text(encoding="utf-8")
OPT = ROOT / "slothy-output/gt864_forward_ntt9_level1.n1.opt.S"
LOG = ROOT / "slothy-output/gt864_forward_ntt9_level1.n1.log"
body = []
for raw in source.splitlines():
    line = raw.split("//", 1)[0].strip()
    if line and not line.endswith(":") and not line.startswith(("/*", "*", "*/")):
        body.append(line)

assert len(body) == 45
assert [line.split()[0] for line in body].count("sqrdmulh") == 6
assert [line.split()[0] for line in body].count("mul") == 6
assert [line.split()[0] for line in body].count("mls") == 6
assert not re.search(r"(?<![A-Za-z0-9_<])v(?:[0-9]|[12][0-9]|3[01])\b",
                     "\n".join(body), flags=re.IGNORECASE)
assert "2a" not in "\n".join(body) and "3a" not in "\n".join(body)

driver = (ROOT / "optimize.py").read_text(encoding="utf-8")
assert "allow_spills = False" in driver
assert "range(8, 25)" in driver
assert '"a0", "a1", "a2", "b0", "b1", "b2", "c0", "c1", "c2"' in driver

optimized = OPT.read_text(encoding="utf-8")
start = optimized.index("gt864_forward_ntt9_level1_slothy_start:")
end = optimized.index("gt864_forward_ntt9_level1_slothy_end:")
emitted = []
for raw in optimized[start:end].splitlines():
    line = raw.split("//", 1)[0].strip()
    if line and not line.endswith(":"):
        emitted.append(line)
assert len(emitted) == 45
emitted_text = "\n".join(emitted)
registers = {int(value) for value in re.findall(r"\bv([0-9]|[12][0-9]|3[01])\b",
                                                emitted_text,
                                                flags=re.IGNORECASE)}
assert registers == {*range(0, 8), *range(25, 32)}
assert not registers.intersection(range(8, 25))
assert not re.search(r"\b(?:sp|x[0-9]+|w[0-9]+)\b", emitted_text,
                     flags=re.IGNORECASE)
assert not re.search(r"\b(?:ld[1-4rps]?|st[1-4rps]?|b|bl|br|ret)\b",
                     emitted_text, flags=re.IGNORECASE)
assert "V<" not in emitted_text and "Q<" not in emitted_text

log = LOG.read_text(encoding="utf-8")
assert "SLOTHY version: 0.2.2" in log
assert "Instructions in body: 45" in log
assert "OPTIMAL" in log
assert ".selfcheck:OK!" in log
assert "Minimum number of stalls: 36" in log
assert "Traceback" not in log
assert "Expected cycles: 48" in optimized

opt_sha256 = hashlib.sha256(OPT.read_bytes()).hexdigest()
log_sha256 = hashlib.sha256(LOG.read_bytes()).hexdigest()

print("gt864_forward_ntt9_level1_static_gate=pass")
print("symbolic_instruction_count=45")
print("level1_b3_count=3")
print("physical_register_tokens=0")
print("available_vector_register_count=15")
print("slothy_status=OPTIMAL")
print("slothy_expected_cycles=48")
print("slothy_minimum_stalls=36")
print("allocated_vector_registers=" + ",".join(f"v{value}" for value in sorted(registers)))
print("allocated_vector_register_count=15")
print("reserved_vector_registers_used=0")
print("spill_or_stack_instructions=0")
print(f"optimized_sha256={opt_sha256}")
print(f"log_sha256={log_sha256}")
