#!/usr/bin/env python3
"""Cortex-A76 fixed-allocation timing scheduling for P28-S."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import shutil
import time
from pathlib import Path

from slothy import Slothy
from slothy.helper import SourceLine
from slothy.targets.aarch64 import aarch64_neon as Arch
from slothy.targets.aarch64 import cortex_a76 as Target

HERE = Path(__file__).resolve().parent

# P28 restores Q values parked in two GPRs with `ins vD.d[lane], xN`.
# The parser knows these forms, but the A76 target table currently omits them.
# Model them exactly like the target's existing vector move / halfword INS:
# either vector pipe, one-per-cycle throughput, two-cycle latency.  This is a
# local experiment extension; Pi 5 timing, not this estimate, is authoritative.
Target.execution_units[(Arch.vins_d, Arch.vins_d_force_output)] = Target.ExecutionUnit.V()
Target.inverse_throughput[(Arch.vins_d, Arch.vins_d_force_output)] = 1
Target.default_latencies[(Arch.vins_d, Arch.vins_d_force_output)] = 2


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


def written_registers(path: Path, start: str, end: str) -> set[str]:
    outputs = set()
    for instruction in instructions_between(path, start, end):
        parsed = Arch.Instruction.parser(SourceLine(instruction))
        if len(parsed) != 1:
            raise RuntimeError(f"unexpected macro instruction: {instruction}")
        outputs.update(parsed[0].args_out)
        outputs.update(parsed[0].args_in_out)
    return outputs


def configure(name: str, timeout: int) -> Slothy:
    log = HERE / f"slothy-{name}.log"
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.addHandler(logging.FileHandler(log, mode="w"))
    s = Slothy(Arch, Target, logger=logger)
    s.config.selftest = False
    s.config.inputs_are_outputs = True
    s.config.constraints.allow_spills = False
    s.config.constraints.functional_only = False
    s.config.constraints.allow_reordering = True
    s.config.constraints.allow_renaming = False
    s.config.reserved_regs = [f"x{i}" for i in range(18, 31)] + ["sp", "xzr"]
    s.config.timeout = timeout
    s.config.variable_size = False
    return s


def schedule_whole(mode: str):
    source = HERE / f"baseline-{mode}.alloc.S"
    output = HERE / f"candidate-{mode}.timing.S"
    shutil.copy2(source, output)
    regions = {
        "main": [
            ("p28_main_slothy_start", "p28_main_terminal_start"),
            ("p28_main_terminal_start", "p28_main_slothy_end"),
        ],
        "tail": [
            ("p28_tail_slothy_start", "p28_tail_terminal_start"),
            ("p28_tail_terminal_start", "p28_tail_slothy_end"),
        ],
    }[mode]
    started = time.monotonic()
    for index, labels in enumerate(regions):
        s = configure(f"{mode}-{index}", 30)
        s.config.split_heuristic = True
        s.config.split_heuristic_estimate_performance = False
        s.config.split_heuristic_factor = 16
        s.config.split_heuristic_stepsize = 0.04
        s.load_source_from_file(str(output))
        s.config.outputs = written_registers(output, labels[0], labels[1])
        s.optimize(start=labels[0], end=labels[1])
        s.write_source_to_file(str(output))
    return {"mode": mode, "windows": "two_regions_with_split_heuristic", "seconds": time.monotonic() - started,
            "output": output.name, "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}


def schedule_route():
    source = HERE / "baseline-route.windowed.S"
    output = HERE / "candidate-route.timing.S"
    shutil.copy2(source, output)
    started = time.monotonic()
    for index in range(108):
        s = configure(f"route-{index}", 20)
        s.load_source_from_file(str(output))
        start, end = (f"p28s_route_window_{index}_start",
                      f"p28s_route_window_{index}_end")
        s.config.outputs = written_registers(output, start, end)
        s.optimize(start=start, end=end)
        s.write_source_to_file(str(output))
        if (index + 1) % 12 == 0:
            print(f"route windows {index + 1}/108", flush=True)
    return {"mode": "route", "windows": 108, "seconds": time.monotonic() - started,
            "output": output.name, "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["main", "tail", "route", "all"])
    args = parser.parse_args()
    modes = ["main", "tail", "route"] if args.mode == "all" else [args.mode]
    reports = []
    for mode in modes:
        reports.append(schedule_route() if mode == "route" else schedule_whole(mode))
    (HERE / f"slothy-{args.mode}-result.json").write_text(json.dumps(reports, indent=2) + "\n")
    print(json.dumps(reports, indent=2))


if __name__ == "__main__":
    main()
