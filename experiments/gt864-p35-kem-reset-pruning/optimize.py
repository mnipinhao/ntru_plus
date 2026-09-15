#!/usr/bin/env python3
"""Allocate or timing-schedule one P35 helper using local Cortex-A76 Slothy."""
import argparse
import logging
from pathlib import Path
from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch, cortex_a76 as Target

P = Path(__file__).resolve().parent
ap = argparse.ArgumentParser()
ap.add_argument("helper", choices=("main", "tail"))
ap.add_argument("--timing", action="store_true")
args = ap.parse_args()
stem = "candidate-" + args.helper
label = "p35_i16" if args.helper == "main" else "p35_itail"
log = P / f"slothy-{args.helper}-{'timing' if args.timing else 'ra'}.log"
logging.basicConfig(level=logging.INFO, handlers=[logging.FileHandler(log, mode="w")])
s = Slothy(Arch, Target, logger=logging.getLogger("p35-" + args.helper))
s.config.selftest = False
s.config.inputs_are_outputs = True
s.config.constraints.allow_spills = False
s.config.reserved_regs = [f"x{i}" for i in range(18,31)] + ["sp", "xzr"]
s.config.timeout = 30 if args.timing else 240
s.config.variable_size = False
if args.timing:
    s.config.constraints.functional_only = False
    s.config.constraints.allow_reordering = True
    s.config.constraints.allow_renaming = False
    s.config.split_heuristic = True
    s.config.split_heuristic_estimate_performance = False
    s.config.split_heuristic_factor = 16
    s.config.split_heuristic_stepsize = 0.04
    src, dst = stem + ".alloc.S", stem + ".opt.S"
else:
    s.config.constraints.functional_only = True
    s.config.constraints.allow_reordering = False
    s.config.constraints.allow_renaming = True
    src, dst = stem + ".sym.S", stem + ".alloc.S"
s.load_source_from_file(str(P / src))
s.optimize(start=label + "_slothy_start", end=label + "_slothy_end")
s.write_source_to_file(str(P / dst))
