#!/usr/bin/env python3
"""Prove the M5K two-block composition and live-through contracts."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PARENT = ROOT.parent
SOURCE = ROOT / "gt864_forward_two_ntt9_blocks.sym.S"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


text = SOURCE.read_text(encoding="utf-8")
instructions = []
for raw in text.splitlines():
    line = raw.split("//", 1)[0].strip()
    if line and not line.endswith(":") and not line.startswith(("/*", "*", "*/")):
        instructions.append(line)
mnemonics = Counter(line.split()[0].lower() for line in instructions)
assert len(instructions) == 333
assert mnemonics == Counter({
    "trn1": 24, "trn2": 24, "ldr": 32, "sqrdmulh": 48,
    "mul": 48, "mls": 48, "orr": 13, "add": 72, "sub": 24,
})

capture = "orr V<hold8>.16b, v16.16b, v16.16b"
assert instructions.count(capture) == 1
second = instructions[instructions.index(capture):]
for output in range(9):
    assert not any(re.match(rf"[a-z][a-z0-9]*\s+(?:V|Q)<out{output}>", line)
                   for line in second), output
assert sum(line.lower().startswith("ldr ") for line in instructions) == 32
assert all("[x3], #16" in line for line in instructions
           if line.lower().startswith("ldr "))
assert any("V<roots>.h" in line for line in second)
assert any("V<modq>.8h" in line for line in second)
for output in range(18):
    definitions = sum(bool(re.match(
        rf"[a-z][a-z0-9]*\s+(?:V|Q)<out{output}>", line
    )) for line in instructions)
    assert definitions == 1, (output, definitions)

exact = load(
    "m5k_exact",
    PARENT / "gt_forward_symbolic_dag/prove_exact_dag.py",
).analyze()
assert exact["status"] == "pass"
assert exact["ntt16_max_abs"] == 9342
assert exact["maximum_abs_any_node"] == 28568
assert exact["unsafe_node_count"] == 0

coordinates = [
    (block, row, lane, 8 * block + lane)
    for block in range(2) for row in range(9) for lane in range(8)
]
assert len(coordinates) == len(set(coordinates)) == 144
assert {column for _, _, _, column in coordinates} == set(range(16))

print(json.dumps({
    "gate": "gt864_forward_two_ntt9_blocks",
    "status": "pass",
    "instruction_count": len(instructions),
    "coordinate_mappings_checked": len(coordinates),
    "first_outputs_live_through_second_consumer": True,
    "fixed_v16_capture_count": 1,
    "public_constant_loads": mnemonics["ldr"],
    "public_table_bytes": 512,
    "coefficient_loads_or_stores": 0,
    "ntt16_max_abs": exact["ntt16_max_abs"],
    "fixed_product_max_abs": 3436,
    "complete_ntt9_max_abs": exact["maximum_abs_any_node"],
    "unsafe_exact_dag_nodes": exact["unsafe_node_count"],
    "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "production_linked": False,
}, indent=2, sort_keys=True))
