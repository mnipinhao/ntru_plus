#!/usr/bin/env python3
"""P22 functional RA, followed by fixed-allocation bounded timing."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import time
from pathlib import Path

from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch, cortex_a76 as Target

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument("--timing", action="store_true")
args = parser.parse_args()
stage = "timing" if args.timing else "ra"
source = HERE / ("candidate.alloc.S" if args.timing else "candidate.sym.S")
output = HERE / ("candidate.opt.S" if args.timing else "candidate.alloc.S")
log_path = HERE / f"slothy-{stage}.log"
logging.basicConfig(level=logging.INFO,
                    handlers=[logging.FileHandler(log_path, mode="w")])

slothy = Slothy(Arch, Target, logger=logging.getLogger("p22"))
slothy.config.selftest = False
slothy.config.inputs_are_outputs = True
slothy.config.constraints.allow_spills = False
slothy.config.reserved_regs = [f"x{i}" for i in range(18, 31)] + ["sp", "xzr"]
slothy.config.timeout = 30 if args.timing else 300
slothy.config.variable_size = False
if args.timing:
    slothy.config.constraints.functional_only = False
    slothy.config.constraints.allow_reordering = True
    slothy.config.constraints.allow_renaming = False
    slothy.config.split_heuristic = True
    slothy.config.split_heuristic_estimate_performance = False
    slothy.config.split_heuristic_factor = 16
    slothy.config.split_heuristic_stepsize = 0.04
else:
    slothy.config.constraints.functional_only = True
    slothy.config.constraints.allow_reordering = False
    slothy.config.constraints.allow_renaming = True

started = time.monotonic()
slothy.load_source_from_file(str(source))
slothy.optimize(start="p22_i16_slothy_start", end="p22_i16_slothy_end")
slothy.write_source_to_file(str(output))
report = {
    "stage": stage,
    "seconds": time.monotonic() - started,
    "source": source.name,
    "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "output": output.name,
    "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
    "slothy_root": str(Path(__import__("slothy").__file__).resolve().parents[1]),
    "target": "cortex_a76",
    "allow_spills": False,
}
(HERE / f"slothy-{stage}.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
