#!/usr/bin/env python3
"""Run bounded Cortex-A76 timing-only Slothy scheduling for P15."""

from __future__ import annotations

from collections import Counter
import argparse
import hashlib
import json
import logging
import re
import time
from pathlib import Path

from slothy import Slothy
from slothy.helper import SourceLine
from slothy.targets.aarch64 import aarch64_neon as Arch
from slothy.targets.aarch64 import cortex_a76 as Target


HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"


def instructions_between(path: Path, start: str, end: str) -> list[str]:
    result = []
    inside = False
    for raw in path.read_text().splitlines():
        code = raw.split("//", 1)[0].strip()
        if code == f"{start}:":
            inside = True
            continue
        if code == f"{end}:":
            break
        if inside and code and not code.startswith(".") and not code.endswith(":"):
            result.append(code)
    return result


def canonical(instruction: str) -> str:
    parsed = Arch.Instruction.parser(SourceLine(instruction))
    if len(parsed) != 1:
        raise RuntimeError(f"unexpected macro instruction: {instruction}")
    return parsed[0].write().lower()


def written_registers(path: Path, start: str, end: str) -> set[str]:
    """Preserve every physical value produced by a bounded splice window.

    A window boundary is an implementation boundary, not a semantic boundary:
    values produced in one window can be consumed by the following unscheduled
    code or window.  Declaring all physical destinations as outputs both makes
    that contract explicit and prevents timing-only scheduling from treating a
    temporarily dead-looking value as disposable.
    """
    outputs: set[str] = set()
    for instruction in instructions_between(path, start, end):
        parsed = Arch.Instruction.parser(SourceLine(instruction))
        if len(parsed) != 1:
            raise RuntimeError(f"unexpected macro instruction: {instruction}")
        outputs.update(parsed[0].args_out)
        outputs.update(parsed[0].args_in_out)
    return outputs


def optimize_mode(mode: str, windows: int, reuse_existing: bool = False) -> dict[str, object]:
    source = BUILD / f"p15-{mode}.input.S"
    output = BUILD / f"p15-{mode}.opt.S"
    log = BUILD / f"slothy-{mode}.log"
    started = time.monotonic()
    reused = reuse_existing and output.exists()
    if not reused:
        logger = logging.getLogger(f"gt864-p15-{mode}")
        logger.handlers.clear()
        logger.setLevel(logging.INFO)
        logger.addHandler(logging.FileHandler(log, mode="w"))
        slothy = Slothy(Arch, Target, logger=logger)
        slothy.config.selftest = False
        slothy.config.inputs_are_outputs = True
        slothy.config.constraints.allow_spills = False
        slothy.config.constraints.allow_reordering = True
        slothy.config.constraints.allow_renaming = False
        slothy.config.constraints.functional_only = False
        slothy.config.variable_size = True
        slothy.config.timeout = 30
        slothy.config.reserved_regs = [f"x{i}" for i in range(18, 31)] + ["sp", "xzr"]
        slothy.config.split_heuristic = True
        slothy.config.split_heuristic_estimate_performance = False
        slothy.config.split_heuristic_factor = 4
        slothy.config.split_heuristic_stepsize = 0.05
        slothy.load_source_from_file(str(source))
        for number in range(windows):
            start = f"p15_{mode}_window_{number}_slothy_start"
            end = f"p15_{mode}_window_{number}_slothy_end"
            slothy.config.outputs = written_registers(source, start, end)
            slothy.optimize(start=start, end=end)
        slothy.write_source_to_file(str(output))
    elapsed = time.monotonic() - started

    before_all = []
    after_all = []
    for number in range(windows):
        start = f"p15_{mode}_window_{number}_slothy_start"
        end = f"p15_{mode}_window_{number}_slothy_end"
        before = instructions_between(source, start, end)
        after = instructions_between(output, start, end)
        if Counter(map(canonical, before)) != Counter(map(canonical, after)):
            raise RuntimeError(f"{mode} window {number}: instruction multiset changed")
        before_all.extend(before)
        after_all.extend(after)
    if len(before_all) != len(after_all):
        raise RuntimeError(f"{mode}: total instruction count changed")
    before_stack = Counter(
        canonical(item)
        for item in before_all
        if re.search(r"\[\s*sp(?:,|\])", item, re.I)
    )
    after_stack = Counter(
        canonical(item)
        for item in after_all
        if re.search(r"\[\s*sp(?:,|\])", item, re.I)
    )
    if before_stack != after_stack:
        raise RuntimeError(f"{mode}: stack-operation multiset changed")

    candidate_cycles = [
        int(value)
        for value in re.findall(r"Expected cycles:\s*(\d+)", output.read_text())
    ]
    if len(candidate_cycles) != windows:
        raise RuntimeError(
            f"{mode}: expected {windows} cycle records, got {candidate_cycles}"
        )
    return {
        "mode": mode,
        "status": "timing-only-pass",
        "windows": windows,
        "instructions": len(after_all),
        "instruction_multiset_preserved": True,
        "allow_renaming": False,
        "allow_spills": False,
        "stack_memory_operations": sum(after_stack.values()),
        "stack_operation_multiset_preserved": True,
        "timeout_seconds_per_window": 30,
        "reused_existing_output": reused,
        "wall_seconds": time.monotonic() - started,
        "window_candidate_model_cycles": candidate_cycles,
        "baseline_model_cycles": None,
        "candidate_model_cycles": sum(candidate_cycles),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reuse-existing", action="store_true")
    args = parser.parse_args()
    preparation = json.loads((HERE / "preparation.json").read_text())
    if not Path(Arch.__file__).resolve().is_relative_to("/Users/chenpinhao/slothy"):
        raise RuntimeError(f"wrong Slothy architecture: {Arch.__file__}")
    result = {
        "interpreter": __import__("sys").executable,
        "slothy": str(Path(__import__("slothy").__file__).resolve()),
        "arch": str(Path(Arch.__file__).resolve()),
        "target": str(Path(Target.__file__).resolve()),
        "modes": {},
    }
    for mode in ("full", "small"):
        result["modes"][mode] = optimize_mode(
            mode, preparation[mode]["windows"], args.reuse_existing
        )
    (HERE / "slothy-results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
