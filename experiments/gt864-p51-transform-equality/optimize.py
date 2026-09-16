#!/usr/bin/env python3
"""Fixed-allocation Cortex-A76 timing pass for the P51 equality loop."""

from __future__ import annotations

import hashlib
import json
import logging
import re
import sys
from collections import Counter
from pathlib import Path

from slothy import Slothy
from slothy.helper import SourceLine
from slothy.targets.aarch64 import aarch64_neon as Arch
from slothy.targets.aarch64 import cortex_a76 as Target

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "candidate-equal-wide.S"
MODEL = HERE / "candidate-equal-wide.model.S"
OUTPUT = HERE / "candidate-equal-wide.slothy.S"


def region(path: Path) -> list[str]:
    inside = False
    result: list[str] = []
    for raw in path.read_text().splitlines():
        code = raw.split("//", 1)[0].split("/*", 1)[0].strip()
        if code == "p51_loop_slothy_start:":
            inside = True
            continue
        if code == "p51_loop_slothy_end:":
            break
        if inside and code and not code.startswith(".") and not code.endswith(":"):
            result.append(code)
    return result


def canonical(text: str) -> str:
    parsed = Arch.Instruction.parser(SourceLine(text))
    if len(parsed) != 1:
        raise RuntimeError(text)
    return parsed[0].write().lower()


def main() -> None:
    if not Path(Arch.__file__).resolve().is_relative_to("/Users/chenpinhao/slothy"):
        raise RuntimeError(f"wrong Slothy checkout: {Arch.__file__}")
    # Slothy consumes preprocessed-looking assembly.  Remove only block-comment
    # lines; instruction spelling and the public function remain unchanged.
    MODEL.write_text("\n".join(
        line for line in SOURCE.read_text().splitlines()
        if not line.lstrip().startswith("/*")) + "\n")
    logger = logging.getLogger("p51-equality")
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.FileHandler(HERE / "slothy.log", mode="w"))
    slothy = Slothy(Arch, Target, logger=logger)
    slothy.config.selftest = False
    slothy.config.inputs_are_outputs = True
    slothy.config.constraints.allow_spills = False
    slothy.config.constraints.allow_reordering = True
    slothy.config.constraints.allow_renaming = False
    slothy.config.constraints.functional_only = False
    slothy.config.variable_size = True
    slothy.config.timeout = 120
    slothy.config.reserved_regs = [f"x{i}" for i in range(2, 31)] + ["sp", "xzr"]
    slothy.load_source_from_file(str(MODEL))
    slothy.config.outputs = ["x0", "x1", "v0", "v5", "v6"]
    slothy.optimize(start="p51_loop_slothy_start", end="p51_loop_slothy_end")
    slothy.write_source_to_file(str(OUTPUT))

    before, after = region(MODEL), region(OUTPUT)
    if Counter(map(canonical, before)) != Counter(map(canonical, after)):
        raise RuntimeError("Slothy changed the instruction multiset")
    cycles = [int(value) for value in re.findall(r"Expected cycles:\s*(\d+)", OUTPUT.read_text())]
    report = {
        "mode": "fixed_allocation_timing",
        "target": "cortex_a76",
        "instructions": len(before),
        "instruction_multiset_preserved": True,
        "allow_renaming": False,
        "allow_spills": False,
        "expected_cycles": cycles,
        "interpreter": sys.executable,
        "slothy": str(Path(__import__("slothy").__file__).resolve()),
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "output_sha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
    }
    (HERE / "slothy-results.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
