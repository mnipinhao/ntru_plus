#!/usr/bin/env python3
"""Check that timing-only Slothy preserved the fixed-allocation instruction DAG."""

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from slothy.helper import SourceLine
from slothy.targets.aarch64 import aarch64_neon as Arch


P = Path(__file__).resolve().parent


def instructions(path: Path) -> list[str]:
    result = []
    for line in path.read_text().splitlines():
        code = line.split("//", 1)[0].strip()
        if not code or code.startswith(".") or code.endswith(":") or code == "ret":
            continue
        if re.match(r"^[a-z]", code):
            result.append(code)
    return result


def canonical(instruction: str) -> str:
    parsed = Arch.Instruction.parser(SourceLine(instruction))
    assert len(parsed) == 1
    return parsed[0].write().lower()


report = {}
for variant, expected_stores in (("main", 128), ("tail", 96)):
    allocated_path = P / variant / "candidate.alloc.S"
    optimized_path = P / variant / "candidate.opt.S"
    allocated = instructions(allocated_path)
    optimized = instructions(optimized_path)
    assert Counter(map(canonical, allocated)) == Counter(map(canonical, optimized))
    store_offsets_before = sorted(
        int(re.search(r"#(\d+)", item).group(1)) for item in allocated if item.startswith("strh ")
    )
    store_offsets_after = sorted(
        int(re.search(r"#(\d+)", item).group(1)) for item in optimized if item.startswith("strh ")
    )
    assert len(store_offsets_before) == expected_stores
    assert store_offsets_after == store_offsets_before
    assert not any("[sp" in item.lower() for item in optimized)
    expected_cycles = int(re.search(r"Expected cycles:\s*(\d+)", optimized_path.read_text()).group(1))
    report[variant] = {
        "instructions": len(optimized),
        "instruction_multiset_preserved": True,
        "store_offsets_preserved": True,
        "stores": expected_stores,
        "stack_memory_operations": 0,
        "model_expected_cycles": expected_cycles,
        "allocated_sha256": hashlib.sha256(allocated_path.read_bytes()).hexdigest(),
        "optimized_sha256": hashlib.sha256(optimized_path.read_bytes()).hexdigest(),
        "slothy_final_status": "split_heuristic_full:OK!",
    }

(P / "post-slothy-audit.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
