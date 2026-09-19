#!/usr/bin/env python3
"""Schedule the complete fused P0 region (win-32) and its unfused control under
identical settings.  inputs_are_outputs=True sidesteps the typed-output syntax;
both regions are self-contained (0 live-out), so it only over-constrains equally.
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

CONFIGS = [
    ("split 8 + zip",           dict(split_heuristic_factor=8,  split_heuristic_preprocess_naive_interleaving=True)),
    ("split 16 + zip",          dict(split_heuristic_factor=16, split_heuristic_preprocess_naive_interleaving=True)),
    ("split 16 + zip + seam 8", dict(split_heuristic_factor=16, split_heuristic_preprocess_naive_interleaving=True,
                                     split_heuristic_optimize_seam=8)),
    ("split 16, no zip",        dict(split_heuristic_factor=16)),
]
results = []
for src in ("win-32.S", "unfused-32.S"):
    n = len([l for l in open(HERE/src) if re.match(r'\s+[a-z]', l)])
    print(f"\n=== {src}  ({n} instructions) ===", flush=True)
    for tag, extra in CONFIGS:
        key = re.sub(r'\W+', '_', f"{src}-{tag}")
        lg = logging.getLogger(key); lg.handlers.clear()
        lg.setLevel(logging.DEBUG); lg.propagate = False
        lg.addHandler(logging.FileHandler(HERE/f"s32-{key}.log", mode="w"))
        s = Slothy(Arch, Target, logger=lg)
        s.config.selftest = False
        s.config.inputs_are_outputs = True
        s.config.variable_size = True
        s.config.constraints.allow_spills = False
        s.config.constraints.allow_renaming = True
        s.config.constraints.allow_reordering = True
        s.config.reserved_regs = GPR_RESERVED
        s.config.timeout = CAP
        s.config.split_heuristic = True
        for k, v in extra.items(): setattr(s.config, k, v)
        s.load_source_from_file(str(HERE/src))
        t0 = time.time(); ok, err = True, ""
        try:
            s.optimize(start="fused_start", end="fused_end")
            s.write_source_to_file(str(HERE/f"opt-{key}.S"))
        except Exception as e:
            ok, err = False, f"{type(e).__name__}: {str(e)[:60]}"
        dt = time.time()-t0
        cyc = re.findall(r"Expected cycles:\s*(\d+)", (HERE/f"s32-{key}.log").read_text())
        results.append(dict(source=src, config=tag, seconds=round(dt,1), ok=ok,
                            cycles=int(cyc[-1]) if cyc else None, instructions=n, error=err))
        print(f"  {tag:26s} {dt:7.1f}s  {'OK ' if ok else 'ERR'}  "
              f"cycles={cyc[-1] if cyc else '-':>5}  {err}", flush=True)
        (HERE/"sweep32-results.json").write_text(json.dumps(results, indent=2))
