#!/usr/bin/env python3
"""Windowing strategy sweep: split_heuristic over a full fused P0-scale region.

Reports, for each configuration, wall-clock solve time and the scheduled cycle
count, so the trade-off between the two is explicit rather than assumed.
"""
import json, logging, re, sys, time
from pathlib import Path
sys.path.insert(0, '/Users/chenpinhao/slothy')
from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch
from slothy.targets.aarch64 import cortex_a76 as Target

HERE = Path(__file__).resolve().parent
GPR_RESERVED = [f"x{i}" for i in range(18, 31)] + ["sp", "xzr"]
SRC = HERE / sys.argv[1]
CAP = int(sys.argv[2]) if len(sys.argv) > 2 else 60
OUTS = json.loads((HERE / sys.argv[1].replace('.S', '.outputs.json')).read_text())
BASE = dict(inputs_are_outputs=False, variable_size=True, outputs=OUTS)

CONFIGS = [
    ("none (one-shot)",             dict()),
    ("split 4",                     dict(split_heuristic=True, split_heuristic_factor=4)),
    ("split 8",                     dict(split_heuristic=True, split_heuristic_factor=8)),
    ("split 8 + zip",               dict(split_heuristic=True, split_heuristic_factor=8,
                                         split_heuristic_preprocess_naive_interleaving=True)),
    ("split 8 + zip + seam 8",      dict(split_heuristic=True, split_heuristic_factor=8,
                                         split_heuristic_preprocess_naive_interleaving=True,
                                         split_heuristic_optimize_seam=8)),
    ("split 12 + zip + seam 8",     dict(split_heuristic=True, split_heuristic_factor=12,
                                         split_heuristic_preprocess_naive_interleaving=True,
                                         split_heuristic_optimize_seam=8)),
    ("split 8 + zip + seam 8 x2",   dict(split_heuristic=True, split_heuristic_factor=8,
                                         split_heuristic_preprocess_naive_interleaving=True,
                                         split_heuristic_optimize_seam=8,
                                         split_heuristic_repeat=2)),
]

results = []
print(f"source {SRC.name}, per-solve cap {CAP}s", flush=True)
for tag, extra in CONFIGS:
    log = HERE / ("strat-" + re.sub(r'\W+', '_', tag) + ".log")
    lg = logging.getLogger(tag); lg.handlers.clear()
    lg.setLevel(logging.DEBUG); lg.propagate = False
    lg.addHandler(logging.FileHandler(log, mode="w"))
    s = Slothy(Arch, Target, logger=lg)
    s.config.selftest = False
    s.config.constraints.allow_spills = False
    s.config.constraints.allow_renaming = True
    s.config.reserved_regs = GPR_RESERVED
    s.config.timeout = CAP
    for k, v in {**BASE, **extra}.items():
        if k in ("functional_only", "allow_reordering"):
            setattr(s.config.constraints, k, v)
        else:
            setattr(s.config, k, v)
    s.load_source_from_file(str(SRC))
    t0 = time.time(); ok, err = True, ""
    try:
        s.optimize(start="fused_start", end="fused_end")
        s.write_source_to_file(str(HERE / ("opt-" + re.sub(r'\W+', '_', tag) + ".S")))
    except Exception as e:
        ok, err = False, f"{type(e).__name__}: {str(e)[:70]}"
    dt = time.time() - t0
    cyc = re.findall(r"Expected cycles:\s*(\d+)", log.read_text())
    results.append(dict(config=tag, seconds=round(dt, 1), ok=ok,
                        cycles=int(cyc[-1]) if cyc else None, error=err))
    print(f"  {tag:30s} {dt:7.1f}s  {'OK ' if ok else 'ERR'}  "
          f"cycles={cyc[-1] if cyc else '-':>5}  {err}", flush=True)
(HERE / "strategy-results.json").write_text(json.dumps(results, indent=2))
