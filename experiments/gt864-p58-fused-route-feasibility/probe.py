#!/usr/bin/env python3
"""Slothy convergence probe on fused producer+route windows (Cortex-A76 model)."""
import json, logging, re, sys, time
from pathlib import Path
sys.path.insert(0, '/Users/chenpinhao/slothy')
from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch
from slothy.targets.aarch64 import cortex_a76 as Target

HERE = Path(__file__).resolve().parent
GPR_RESERVED = [f"x{i}" for i in range(18, 31)] + ["sp", "xzr"]
TIMEOUT = int(sys.argv[1]) if len(sys.argv) > 1 else 300
results = []
for n in (2, 4, 6, 8, 12, 16):
    src = HERE / f"window-{n:02d}.S"
    if not src.exists(): continue
    tag = f"w{n:02d}"
    log = HERE / f"slothy-{tag}.log"
    logger = logging.getLogger(tag); logger.handlers.clear()
    logger.setLevel(logging.DEBUG); logger.propagate = False
    logger.addHandler(logging.FileHandler(log, mode="w"))
    s = Slothy(Arch, Target, logger=logger)
    s.config.selftest = False
    s.config.inputs_are_outputs = True
    s.config.constraints.allow_spills = False
    s.config.constraints.functional_only = False   # full timing schedule
    s.config.constraints.allow_reordering = True
    s.config.constraints.allow_renaming = True
    s.config.reserved_regs = GPR_RESERVED
    s.config.timeout = TIMEOUT
    s.config.variable_size = False
    s.load_source_from_file(str(src))
    t0 = time.time(); ok, err = True, ""
    try:
        s.optimize(start="fused_start", end="fused_end")
        s.write_source_to_file(str(HERE / f"window-{n:02d}.opt.S"))
    except Exception as e:
        ok = False; err = type(e).__name__ + ": " + str(e)[:90]
    dt = time.time() - t0
    txt = log.read_text()
    cyc = re.findall(r"Expected cycles:\s*(\d+)", txt)
    ninstr = len(open(src).read().strip().split("\n")) - 8
    results.append(dict(stores=n, instructions=ninstr, seconds=round(dt, 1),
                        converged=ok, cycles=cyc[-1] if cyc else None, error=err))
    print(f"  stores={n:2d}  instr={ninstr:4d}  {dt:7.1f}s  "
          f"{'OK' if ok else 'FAIL'}  cycles={cyc[-1] if cyc else '-'}  {err}")
    if not ok: break
(HERE / "probe-results.json").write_text(json.dumps(results, indent=2))
