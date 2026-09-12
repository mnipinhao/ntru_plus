#!/usr/bin/env python3
"""Re-time the frozen physical production tail with P13-C's exact settings."""
import logging
from pathlib import Path
from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch, cortex_a76 as Target

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
SOURCE = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864/gt864_native_inverse_tail_lazy.S"
logging.basicConfig(level=logging.INFO,
                    handlers=[logging.FileHandler(P / "slothy-baseline-timing.log", mode="w")])
s = Slothy(Arch, Target, logger=logging.getLogger("p13c-baseline"))
s.config.selftest = False
s.config.inputs_are_outputs = True
s.config.constraints.allow_spills = False
s.config.reserved_regs = [f"x{i}" for i in range(18, 31)] + ["sp", "xzr"]
s.config.timeout = 30
s.config.variable_size = False
s.config.constraints.functional_only = False
s.config.constraints.allow_reordering = True
s.config.constraints.allow_renaming = False
s.config.split_heuristic = True
s.config.split_heuristic_estimate_performance = False
s.config.split_heuristic_factor = 16
s.config.split_heuristic_stepsize = 0.04
s.load_source_from_file(str(SOURCE))
s.optimize(start="lazy_itail_slothy_start", end="lazy_itail_slothy_end")
s.write_source_to_file(str(P / "baseline.opt.S"))
