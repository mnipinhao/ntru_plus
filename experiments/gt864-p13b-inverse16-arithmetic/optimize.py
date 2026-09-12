#!/usr/bin/env python3
"""P13-B: allocate once, then schedule the fixed allocation in small windows."""
import argparse,logging
from pathlib import Path
from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch,cortex_a76 as Target

P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--timing',action='store_true');args=ap.parse_args()
logging.basicConfig(level=logging.INFO,handlers=[logging.FileHandler(P/('slothy-timing.log' if args.timing else 'slothy-ra.log'),mode='w')])
s=Slothy(Arch,Target,logger=logging.getLogger('p13b'))
s.config.selftest=False
s.config.inputs_are_outputs=True
s.config.constraints.allow_spills=False
s.config.reserved_regs=[f'x{i}' for i in range(18,31)]+['sp','xzr']
s.config.timeout=30 if args.timing else 240
s.config.variable_size=False
if args.timing:
    s.config.constraints.functional_only=False
    s.config.constraints.allow_reordering=True
    s.config.constraints.allow_renaming=False
    s.config.split_heuristic=True
    s.config.split_heuristic_estimate_performance=False
    s.config.split_heuristic_factor=16
    s.config.split_heuristic_stepsize=0.04
    src='candidate.alloc.S';dst='candidate.opt.S'
else:
    s.config.constraints.functional_only=True
    s.config.constraints.allow_reordering=False
    s.config.constraints.allow_renaming=True
    src='candidate.sym.S';dst='candidate.alloc.S'
s.load_source_from_file(str(P/src))
s.optimize(start='p13b_i16_slothy_start',end='p13b_i16_slothy_end')
s.write_source_to_file(str(P/dst))
