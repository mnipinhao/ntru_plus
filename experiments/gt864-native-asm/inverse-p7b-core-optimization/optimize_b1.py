#!/usr/bin/env python3
"""Cortex-A76 timing-only scheduling for the fixed P7-B1 allocation."""

from collections import Counter
from pathlib import Path
import hashlib
import json
import logging
import re
import time

from slothy import Slothy
from slothy.helper import SourceLine
from slothy.targets.aarch64 import aarch64_neon as Arch
from slothy.targets.aarch64 import cortex_a76 as Target


P = Path(__file__).resolve().parent
SOURCE = P / "build/gt864_native_inverse9_b1.S"
OUTPUT = P / "build/candidate.b1.latest.opt.S"
CLEAN = P / "build/candidate.b1.latest.clean.S"
LOG = P / "slothy-b1.log"

assert Path(Arch.__file__).resolve().is_relative_to("/Users/chenpinhao/slothy")
logging.basicConfig(level=logging.INFO, handlers=[logging.FileHandler(LOG, mode="w")])
s = Slothy(Arch, Target, logger=logging.getLogger("gt864-p7b1"))
s.config.selftest = False
s.config.inputs_are_outputs = True
s.config.constraints.allow_spills = False
s.config.constraints.allow_reordering = True
s.config.constraints.allow_renaming = False
s.config.constraints.functional_only = False
s.config.variable_size = True
s.config.timeout = 30
s.config.reserved_regs = [f"x{i}" for i in range(18, 31)] + ["sp", "xzr"]
s.config.split_heuristic = True
s.config.split_heuristic_estimate_performance = False
s.config.split_heuristic_factor = 8
s.config.split_heuristic_stepsize = 0.05
s.load_source_from_file(str(SOURCE))

started = time.monotonic()
s.optimize(start="packed_i9_slothy_start", end="packed_i9_slothy_end")
s.write_source_to_file(str(OUTPUT))
elapsed = time.monotonic() - started

# Slothy retains a commented copy of the input and emits a wide cycle chart.
# Strip only comments/blank lines; the active instruction order is unchanged.
clean_lines = []
for raw in OUTPUT.read_text().splitlines():
    if raw.lstrip().startswith("//"):
        continue
    code = raw.split("//", 1)[0].rstrip()
    if code.strip():
        clean_lines.append(code)
CLEAN.write_text("\n".join(clean_lines) + "\n")


def instructions(path: Path) -> list[str]:
    result = []
    inside = False
    for raw in path.read_text().splitlines():
        code = raw.split("//", 1)[0].strip()
        if code == "packed_i9_slothy_start:":
            inside = True
            continue
        if code == "packed_i9_slothy_end:":
            break
        if inside and code and not code.startswith(".") and not code.endswith(":"):
            result.append(code)
    return result


def canonical(instruction: str) -> str:
    parsed = Arch.Instruction.parser(SourceLine(instruction))
    assert len(parsed) == 1
    return parsed[0].write().lower()


before = instructions(SOURCE)
after = instructions(OUTPUT)
clean = instructions(CLEAN)
assert Counter(map(canonical, before)) == Counter(map(canonical, after))
assert list(map(canonical, after)) == list(map(canonical, clean))
assert not any(re.search(r"\[\s*sp(?:,|\])", item, re.I) for item in after)
expected_cycles = int(re.search(r"Expected cycles:\s*(\d+)", OUTPUT.read_text()).group(1))
result = {
    "status": "timing-only-pass",
    "source_of_truth": str(SOURCE.relative_to(P)),
    "output": str(OUTPUT.relative_to(P)),
    "clean_output": str(CLEAN.relative_to(P)),
    "instructions": len(after),
    "instruction_multiset_preserved": True,
    "allow_renaming": False,
    "allow_spills": False,
    "stack_memory_operations": 0,
    "split_factor": 8,
    "timeout_seconds_per_window": 30,
    "wall_seconds": elapsed,
    "model_expected_cycles": expected_cycles,
    "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "output_sha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
    "clean_output_sha256": hashlib.sha256(CLEAN.read_bytes()).hexdigest(),
    "slothy": str(Path(__import__("slothy").__file__).resolve()),
    "arch": str(Path(Arch.__file__).resolve()),
    "target": str(Path(Target.__file__).resolve()),
}
(P / "p7b1-slothy.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
