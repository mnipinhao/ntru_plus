#!/usr/bin/env python3
"""Bounded fixed-allocation A76 timing for P47's 18 three-record windows."""
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


def between(path: Path, start: str, end: str) -> list[str]:
    result, inside = [], False
    for raw in path.read_text().splitlines():
        code = raw.split("//", 1)[0].strip()
        if code == start + ":":
            inside = True
            continue
        if code == end + ":":
            break
        if inside and code and not code.startswith(".") and not code.endswith(":"):
            result.append(code)
    return result


def canonical(text: str) -> str:
    parsed = Arch.Instruction.parser(SourceLine(text))
    if len(parsed) != 1:
        raise RuntimeError(text)
    return parsed[0].write().lower()


def outputs(path: Path, start: str, end: str) -> set[str]:
    result: set[str] = set()
    for text in between(path, start, end):
        parsed = Arch.Instruction.parser(SourceLine(text))[0]
        result.update(parsed.args_out)
        result.update(parsed.args_in_out)
    return result


def main() -> None:
    if not Path(Arch.__file__).resolve().is_relative_to("/Users/chenpinhao/slothy"):
        raise RuntimeError(f"wrong Slothy checkout: {Arch.__file__}")
    source = HERE / "candidate-compare.sym.S"
    model = HERE / "candidate-compare.model.S"
    model_output = HERE / "candidate-compare.model.g3.opt.S"
    output = HERE / "candidate-compare.g3.opt.S"
    # The canonical checkout does not parse scalar LDUR X/W.  Use a reversible
    # timing-only LDR-X surrogate with unique, encodable scaled offsets.  D
    # loads map to 2*offset; W loads map to 4096+2*offset.  After scheduling,
    # restore both original widths and exact addresses before assembly/tests.
    def to_surrogate(match: re.Match[str]) -> str:
        width, base, offset_text = match.groups()
        offset = int(offset_text)
        encoded = 2 * offset + (4096 if width == "w" else 0)
        return f"ldr x2, [{base}, #{encoded}]"

    model_text = re.sub(r"ldur ([xw])2, \[(x[567]), #(\d+)\]", to_surrogate,
                        source.read_text())
    model.write_text(model_text)
    logger = logging.getLogger("p47-compare")
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.FileHandler(HERE / "slothy-compare-g3.log", mode="w"))
    slothy = Slothy(Arch, Target, logger=logger)
    slothy.config.selftest = False
    slothy.config.inputs_are_outputs = True
    slothy.config.constraints.allow_spills = False
    slothy.config.constraints.allow_reordering = True
    slothy.config.constraints.allow_renaming = False
    slothy.config.constraints.functional_only = False
    slothy.config.variable_size = True
    slothy.config.timeout = 30
    slothy.config.reserved_regs = [f"x{i}" for i in range(10, 31)] + ["sp", "xzr"]
    slothy.load_source_from_file(str(model))
    for index in range(18):
        start = f"p47_compare_group3_{index}_start"
        end = f"p47_compare_group3_{index}_end"
        slothy.config.outputs = outputs(model, start, end)
        slothy.optimize(start=start, end=end)
    slothy.write_source_to_file(str(model_output))
    def from_surrogate(match: re.Match[str]) -> str:
        base, encoded_text = match.groups()
        encoded = int(encoded_text)
        if encoded >= 4096:
            return f"ldur w2, [{base}, #{(encoded - 4096) // 2}]"
        return f"ldur x2, [{base}, #{encoded // 2}]"

    restored = re.sub(r"ldr x2, \[(x[567]), #(\d+)\]", from_surrogate,
                      model_output.read_text())
    output.write_text(restored)
    before, after = [], []
    for index in range(18):
        start = f"p47_compare_group3_{index}_start"
        end = f"p47_compare_group3_{index}_end"
        original = between(model, start, end)
        scheduled = between(model_output, start, end)
        if Counter(map(canonical, original)) != Counter(map(canonical, scheduled)):
            raise RuntimeError(f"instruction multiset changed in window {index}")
        before += original
        after += scheduled
    cycles = [int(x) for x in re.findall(r"Expected cycles:\s*(\d+)", output.read_text())]
    if len(cycles) != 18:
        raise RuntimeError(f"expected 18 timing windows, got {len(cycles)}")
    report = {
        "mode": "decaps_full_compare",
        "windows": 18,
        "records_per_window": 3,
        "instructions": len(after),
        "instruction_multiset_preserved": True,
        "inherited_vector_allocation": "P46 v0-v31; x0/x2/x8/x9 fixed compare flow; no spill",
        "allow_renaming": False,
        "allow_spills": False,
        "model_cycles": sum(cycles),
        "window_cycles": cycles,
        "load_model_surrogate": "LDUR X/W mapped bijectively to unique scaled LDR X offsets for timing and exactly restored before assembly",
        "interpreter": sys.executable,
        "slothy": str(Path(__import__("slothy").__file__).resolve()),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
    }
    (HERE / "slothy-compare-g3.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
