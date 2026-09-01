#!/usr/bin/env python3
"""Static, dependency-free audit of the M5G symbolic Slothy artifacts."""

from __future__ import annotations

import re
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gt864_forward_b3_two_product.sym.S"
OPT = ROOT / "slothy-output/gt864_forward_b3_two_product.n1.opt.S"
LOG = ROOT / "slothy-output/gt864_forward_b3_two_product.n1.log"


def instructions(text: str) -> list[str]:
    result = []
    for raw in text.splitlines():
        line = raw.split("//", 1)[0].strip()
        if (line and not line.endswith(":")
                and not line.startswith(("/*", "*", "*/"))):
            result.append(line)
    return result


source = SOURCE.read_text(encoding="utf-8")
body = instructions(source)
opcodes = [line.split()[0] for line in body]
assert opcodes == [
    "orr", "add", "add",
    "sqrdmulh", "mul", "mls",
    "sqrdmulh", "mul", "mls",
    "add", "add", "sub", "sub", "add", "add",
]
assert len(body) == 15
assert "gt864_forward_b3_slothy_start:" in source
assert "gt864_forward_b3_slothy_end:" in source
assert not re.search(r"(?<![A-Za-z0-9_<])v(?:[0-9]|[12][0-9]|3[01])\b", "\n".join(body),
                     flags=re.IGNORECASE)
assert not re.search(r"\b(?:x(?:[0-9]|[12][0-9]|30)|w(?:[0-9]|[12][0-9]|30)|sp)\b",
                     "\n".join(body), flags=re.IGNORECASE)

dag = (ROOT / "instruction-dag.yml").read_text(encoding="utf-8")
assert len(re.findall(r"^  - \{id: n[0-9]{2}_", dag, flags=re.MULTILINE)) == 15
assert "n14_y2" in dag
assert "3a" not in "\n".join(body)

contract = (ROOT / "candidate-contract.yml").read_text(encoding="utf-8")
assert "candidate_status: investigate" in contract
assert "physical_allocation: v0_and_v24_through_v31" in contract
assert "slothy_result: optimal" in contract

driver = (ROOT / "optimize.py").read_text(encoding="utf-8")
assert "allow_spills = False" in driver
assert "range(1, 24)" in driver
assert "neoverse_n1_experimental" in driver
assert 'optimizer.config.outputs = ["a", "b", "c"]' in driver

optimized = OPT.read_text(encoding="utf-8")
start = optimized.index("gt864_forward_b3_slothy_start:")
end = optimized.index("gt864_forward_b3_slothy_end:")
emitted = instructions(optimized[start:end])
emitted_opcodes = [line.split()[0].lower() for line in emitted]
assert emitted_opcodes == [
    "orr", "sqrdmulh", "add", "mul", "add", "sqrdmulh", "sub", "mls",
    "mul", "mls", "add", "add", "sub", "add", "add",
]
assert len(emitted) == 15
emitted_text = "\n".join(emitted)
registers = {int(value) for value in re.findall(r"\bv([0-9]|[12][0-9]|3[01])\b",
                                                emitted_text,
                                                flags=re.IGNORECASE)}
assert registers == {0, *range(24, 32)}
assert not registers.intersection(range(1, 24))
assert not re.search(r"\b(?:sp|x[0-9]+|w[0-9]+)\b", emitted_text,
                     flags=re.IGNORECASE)
assert not re.search(r"\b(?:ld[1-4rps]?|st[1-4rps]?)\b", emitted_text,
                     flags=re.IGNORECASE)
assert "V<" not in emitted_text and "Q<" not in emitted_text

log = LOG.read_text(encoding="utf-8")
assert "SLOTHY version: 0.2.2" in log
assert "Instructions in body: 15" in log
assert "OPTIMAL" in log
assert ".selfcheck:OK!" in log
assert "Minimum number of stalls: 20" in log
assert "Traceback" not in log
assert "Expected cycles: 24" in optimized

opt_sha256 = hashlib.sha256(OPT.read_bytes()).hexdigest()
log_sha256 = hashlib.sha256(LOG.read_bytes()).hexdigest()

print("gt864_forward_symbolic_artifact_gate=pass")
print("symbolic_instruction_count=15")
print("physical_register_tokens=0")
print("slothy_result_present=1")
print("slothy_status=OPTIMAL")
print("slothy_expected_cycles=24")
print("slothy_minimum_stalls=20")
print("allocated_vector_registers=" + ",".join(f"v{value}" for value in sorted(registers)))
print("allocated_vector_register_count=9")
print("spill_or_stack_instructions=0")
print(f"optimized_sha256={opt_sha256}")
print(f"log_sha256={log_sha256}")
