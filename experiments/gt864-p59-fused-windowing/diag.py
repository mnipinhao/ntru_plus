#!/usr/bin/env python3
"""Why is a fused window slow to schedule?  Vary one knob at a time."""
import logging, re, sys, time
from pathlib import Path
sys.path.insert(0, '/Users/chenpinhao/slothy')
from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch
from slothy.targets.aarch64 import cortex_a76 as Target

HERE = Path(__file__).resolve().parent
GPR_RESERVED = [f"x{i}" for i in range(18, 31)] + ["sp", "xzr"]
SRC = HERE / sys.argv[1]
CAP = int(sys.argv[2])

def attempt(tag, **kw):
    log = HERE / f"diag-{tag}.log"
    lg = logging.getLogger(tag); lg.handlers.clear()
    lg.setLevel(logging.DEBUG); lg.propagate = False
    lg.addHandler(logging.FileHandler(log, mode="w"))
    s = Slothy(Arch, Target, logger=lg)
    s.config.selftest = False
    s.config.constraints.allow_spills = False
    s.config.reserved_regs = GPR_RESERVED
    s.config.timeout = CAP
    s.config.inputs_are_outputs = kw.pop("inputs_are_outputs", True)
    s.config.variable_size = kw.pop("variable_size", False)
    s.config.constraints.functional_only = kw.pop("functional_only", False)
    s.config.constraints.allow_reordering = kw.pop("allow_reordering", True)
    s.config.constraints.allow_renaming = True
    for k, v in kw.items():
        setattr(s.config, k, v)
    s.load_source_from_file(str(SRC))
    t0 = time.time(); ok, err = True, ""
    try:
        s.optimize(start="fused_start", end="fused_end")
    except Exception as e:
        ok, err = False, type(e).__name__
    dt = time.time() - t0
    cyc = re.findall(r"Expected cycles:\s*(\d+)", log.read_text())
    print(f"  {tag:46s} {dt:7.1f}s  {'OK ' if ok else 'ERR'}  "
          f"cycles={cyc[-1] if cyc else '-':>5}  {err}", flush=True)
    return ok, dt

print(f"source {SRC.name}, solver cap {CAP}s each", flush=True)
attempt("a  baseline (as in P58)")
attempt("b  functional_only: allocation, no timing", functional_only=True, allow_reordering=False)
attempt("c  variable_size (solver minimises stalls)", variable_size=True)
attempt("d  inputs_are_outputs=False", inputs_are_outputs=False)
attempt("e  split_heuristic factor 4", split_heuristic=True, split_heuristic_factor=4)
