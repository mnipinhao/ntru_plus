#!/usr/bin/env python3
"""Allocate and time-schedule the two P32 regions with local Slothy."""
import json
import logging
import sys
import time
from pathlib import Path

from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch
from slothy.targets.aarch64 import cortex_a76 as Target

HERE = Path(__file__).resolve().parent
ALL_GPRS = [f"x{i}" for i in range(31)] + ["sp", "xzr"]


def run(source, output, start, end, tag, *, timing, reserved, timeout=240):
    logger = logging.getLogger(tag)
    logger.handlers.clear()
    logger.propagate = False
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.FileHandler(HERE / f"slothy-{tag}.log", mode="w"))
    s = Slothy(Arch, Target, logger=logger)
    s.config.selftest = False
    s.config.inputs_are_outputs = False
    s.config.outputs = []
    s.config.constraints.allow_spills = False
    s.config.constraints.functional_only = not timing
    s.config.constraints.allow_reordering = timing
    s.config.constraints.allow_renaming = True
    s.config.reserved_regs = list(reserved)
    s.config.timeout = timeout
    s.config.variable_size = False
    s.load_source_from_file(str(source))
    s.optimize(start=start, end=end)
    s.write_source_to_file(str(output))


def prefix():
    alloc = HERE / "candidate-prefix.alloc.S"
    timed = HERE / "candidate-prefix.timing.S"
    run(HERE / "candidate-prefix.sym.S", alloc,
        "p32_i16_prefix_slothy_start", "p32_i16_prefix_slothy_end",
        "prefix-ra", timing=False, reserved=ALL_GPRS, timeout=360)
    run(alloc, timed,
        "p32_i16_prefix_slothy_start", "p32_i16_prefix_slothy_end",
        "prefix-timing", timing=True, reserved=ALL_GPRS, timeout=360)
    return timed


def terminal():
    current = HERE / "candidate-terminal.sym.S"
    for t in range(16):
        for g in range(6):
            output = HERE / "candidate-terminal.timing.S"
            run(current, output,
                f"p32_terminal_{t}_g{g}_start", f"p32_terminal_{t}_g{g}_end",
                f"terminal-{t}-{g}", timing=True,
                reserved=ALL_GPRS + [f"v{i}" for i in range(26, 32)], timeout=60)
            current = output
    return current


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"prefix", "terminal", "all"}:
        raise SystemExit("usage: optimize.py prefix|terminal|all")
    started = time.monotonic()
    result = {}
    if sys.argv[1] in {"prefix", "all"}:
        result["prefix"] = str(prefix())
    if sys.argv[1] in {"terminal", "all"}:
        result["terminal"] = str(terminal())
    result["wall_seconds"] = time.monotonic() - started
    (HERE / "slothy-result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
