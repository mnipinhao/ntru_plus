#!/usr/bin/env python3
"""Two-phase Slothy flow for a fused region.

Phase 1  symbolic -> physical registers.  functional_only, no reordering.
         Fast, and it erases the V<name> forms that make split_heuristic's
         sub-region boundaries untypeable.
Phase 2  physical -> timing schedule, with split_heuristic + naive interleaving
         and variable_size (the two settings P59 found decisive).
"""
import json, logging, re, sys, time
from pathlib import Path
sys.path.insert(0, '/Users/chenpinhao/slothy')
from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch
from slothy.targets.aarch64 import cortex_a76 as Target

HERE = Path(__file__).resolve().parent
GPR_RESERVED = [f"x{i}" for i in range(18, 31)] + ["sp", "xzr"]
CAP = int(sys.argv[1]) if len(sys.argv) > 1 else 60

def mk(tag):
    lg = logging.getLogger(tag); lg.handlers.clear()
    lg.setLevel(logging.DEBUG); lg.propagate = False
    lg.addHandler(logging.FileHandler(HERE / f"tp-{tag}.log", mode="w"))
    s = Slothy(Arch, Target, logger=lg)
    s.config.selftest = False
    s.config.inputs_are_outputs = True
    s.config.constraints.allow_spills = False
    s.config.constraints.allow_renaming = True
    s.config.reserved_regs = GPR_RESERVED
    s.config.timeout = CAP
    return s, HERE / f"tp-{tag}.log"

def cycles(log):
    c = re.findall(r"Expected cycles:\s*(\d+)", log.read_text())
    return int(c[-1]) if c else None

results = []
for src in ("win-32.S", "unfused-32.S"):
    stem = src[:-2]
    n = len([l for l in open(HERE/src) if re.match(r'\s+[a-z]', l)])
    print(f"\n=== {src}  ({n} instructions) ===", flush=True)

    # phase 1: register allocation only
    s, log = mk(f"{stem}-p1")
    s.config.variable_size = False
    s.config.constraints.functional_only = True
    s.config.constraints.allow_reordering = False
    s.load_source_from_file(str(HERE/src))
    t0 = time.time(); ok, err = True, ""
    try:
        s.optimize(start="fused_start", end="fused_end")
        s.write_source_to_file(str(HERE/f"{stem}.alloc.S"))
    except Exception as e:
        ok, err = False, f"{type(e).__name__}: {str(e)[:60]}"
    print(f"  phase 1 allocation          {time.time()-t0:7.1f}s  "
          f"{'OK ' if ok else 'ERR'}  {err}", flush=True)
    if not ok:
        results.append(dict(source=src, phase=1, ok=False, error=err)); continue

    # phase 2: timing schedule on physical registers
    for tag, extra in [("split 8 + zip",  dict(split_heuristic_factor=8,
                          split_heuristic_preprocess_naive_interleaving=True)),
                       ("split 16 + zip", dict(split_heuristic_factor=16,
                          split_heuristic_preprocess_naive_interleaving=True)),
                       ("split 16 + zip + seam 8", dict(split_heuristic_factor=16,
                          split_heuristic_preprocess_naive_interleaving=True,
                          split_heuristic_optimize_seam=8))]:
        key = re.sub(r'\W+', '_', f"{stem}-{tag}")
        s, log = mk(key)
        s.config.variable_size = True
        s.config.constraints.functional_only = False
        s.config.constraints.allow_reordering = True
        s.config.split_heuristic = True
        for k, v in extra.items(): setattr(s.config, k, v)
        s.load_source_from_file(str(HERE/f"{stem}.alloc.S"))
        t0 = time.time(); ok, err = True, ""
        try:
            s.optimize(start="fused_start", end="fused_end")
            s.write_source_to_file(str(HERE/f"{key}.opt.S"))
        except Exception as e:
            ok, err = False, f"{type(e).__name__}: {str(e)[:60]}"
        dt, cy = time.time()-t0, cycles(log)
        results.append(dict(source=src, config=tag, seconds=round(dt,1), ok=ok,
                            cycles=cy, instructions=n, error=err))
        print(f"  phase 2 {tag:24s} {dt:7.1f}s  {'OK ' if ok else 'ERR'}  "
              f"cycles={cy if cy else '-'}  {err}", flush=True)
        (HERE/"twophase-results.json").write_text(json.dumps(results, indent=2))
