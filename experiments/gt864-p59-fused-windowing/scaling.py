#!/usr/bin/env python3
"""How large a fused region can each Slothy phase actually handle?

Phase 1 (allocation) runs on symbolic code and cannot use split_heuristic,
because sub-region boundaries carrying V<name> values cannot be typed.  So its
limit is the one that bounds the whole flow.
"""
import json, logging, re, sys, time
from pathlib import Path
sys.path.insert(0, '/Users/chenpinhao/slothy')
from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch
from slothy.targets.aarch64 import cortex_a76 as Target
HERE = Path(__file__).resolve().parent
GPR_RESERVED = [f"x{i}" for i in range(18, 31)] + ["sp", "xzr"]
CAP = int(sys.argv[1]) if len(sys.argv) > 1 else 600
out = []
for src in ("win-04.S", "win-08.S", "win-16.S", "win-32.S"):
    n = len([l for l in open(HERE/src) if re.match(r'\s+[a-z]', l)])
    tag = src[:-2] + "-alloc"
    lg = logging.getLogger(tag); lg.handlers.clear()
    lg.setLevel(logging.DEBUG); lg.propagate = False
    lg.addHandler(logging.FileHandler(HERE/f"sc-{tag}.log", mode="w"))
    s = Slothy(Arch, Target, logger=lg)
    s.config.selftest = False
    s.config.inputs_are_outputs = True
    s.config.variable_size = False
    s.config.constraints.functional_only = True
    s.config.constraints.allow_reordering = False
    s.config.constraints.allow_spills = False
    s.config.constraints.allow_renaming = True
    s.config.reserved_regs = GPR_RESERVED
    s.config.timeout = CAP
    s.load_source_from_file(str(HERE/src))
    t0 = time.time(); ok, err = True, ""
    try:
        s.optimize(start="fused_start", end="fused_end")
        s.write_source_to_file(str(HERE/(src[:-2] + ".alloc.S")))
    except Exception as e:
        ok, err = False, type(e).__name__
    dt = time.time()-t0
    v = re.findall(r"(OPTIMAL|INFEASIBLE|UNKNOWN|FEASIBLE)", (HERE/f"sc-{tag}.log").read_text())
    out.append(dict(source=src, instructions=n, seconds=round(dt,1), ok=ok,
                    verdict=v[-1] if v else None, error=err))
    print(f"  {src:12s} {n:4d} instr  {dt:7.1f}s  {'OK ' if ok else 'ERR'}  "
          f"{v[-1] if v else '-':10s} {err}", flush=True)
    (HERE/"scaling-results.json").write_text(json.dumps(out, indent=2))
