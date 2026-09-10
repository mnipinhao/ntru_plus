#!/usr/bin/env python3
"""Bounded-window Cortex-A76 timing only; preserve the proven P3-A allocation."""

import argparse
import json
import logging
import time
from pathlib import Path

from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch
from slothy.targets.aarch64 import cortex_a76 as Target


P = Path(__file__).resolve().parent
KERNELS = {
    "main": ("lazy_i16", 16),
    "tail": ("lazy_itail", 16),
}


parser = argparse.ArgumentParser()
parser.add_argument("variant", choices=KERNELS)
parser.add_argument("--timeout", type=int, default=30, help="seconds per bounded solver window")
args = parser.parse_args()

kernel, factor = KERNELS[args.variant]
work = P / args.variant
log_path = work / "slothy-timing.log"
logging.basicConfig(level=logging.INFO, handlers=[logging.FileHandler(log_path, mode="w")])

assert Path(Arch.__file__).resolve().is_relative_to("/Users/chenpinhao/slothy"), Arch.__file__
s = Slothy(Arch, Target, logger=logging.getLogger(f"p3b-{args.variant}"))
s.config.selftest = False
s.config.inputs_are_outputs = True
s.config.constraints.allow_spills = False
s.config.constraints.functional_only = False
s.config.constraints.allow_reordering = True
s.config.constraints.allow_renaming = False
s.config.variable_size = True
s.config.reserved_regs = [f"x{i}" for i in range(18, 31)] + ["sp", "xzr"]
s.config.timeout = args.timeout
s.config.split_heuristic = True
s.config.split_heuristic_estimate_performance = False
s.config.split_heuristic_factor = factor
s.config.split_heuristic_stepsize = 0.05
s.load_source_from_file(str(work / "candidate.alloc.S"))

started = time.monotonic()
s.optimize(start=kernel + "_slothy_start", end=kernel + "_slothy_end")
s.write_source_to_file(str(work / "candidate.opt.S"))
elapsed = time.monotonic() - started

report = {
    "variant": args.variant,
    "kernel": kernel,
    "allocation": "inherited P3-A allocation plus generator-proven dead-register reuse",
    "allow_renaming": False,
    "allow_spills": False,
    "split_heuristic": True,
    "split_factor": factor,
    "timeout_seconds_per_window": args.timeout,
    "wall_seconds": elapsed,
    "source": str(work / "candidate.alloc.S"),
    "output": str(work / "candidate.opt.S"),
    "log": str(log_path),
    "arch": str(Path(Arch.__file__).resolve()),
    "target": str(Path(Target.__file__).resolve()),
}
(work / "slothy-timing-report.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
