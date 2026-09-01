#!/usr/bin/env python3
"""Static, dependency-free audit of the M5G symbolic Slothy artifacts."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "gt864_forward_b3_two_product.sym.S"


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
assert "physical_allocation: none" in contract
assert "slothy_result: missing" in contract

driver = (ROOT / "optimize.py").read_text(encoding="utf-8")
assert "allow_spills = False" in driver
assert "range(1, 24)" in driver
assert "neoverse_n1_experimental" in driver

print("gt864_forward_symbolic_artifact_gate=pass")
print("symbolic_instruction_count=15")
print("physical_register_tokens=0")
print("slothy_result_present=0")
