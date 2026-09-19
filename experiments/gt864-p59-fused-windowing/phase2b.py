#!/usr/bin/env python3
"""Phase 2 on physical code, with outputs declared instead of inputs_are_outputs.

On physical registers there is no typing ambiguity, so the live-out set can be
stated exactly.  The producer delivers through memory, so almost nothing needs to
survive the region -- pinning all 32 registers as live-out over-constrains the
final sub-window.
"""
import json, logging, re, sys, time
from pathlib import Path
S = '/private/tmp/claude-501/-Users-chenpinhao-ntruplus/a827c50f-9c4e-40e1-b926-99dea89f0d8e/scratchpad'
sys.path.insert(0, S + '/slothy-patched')
from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch
from slothy.targets.aarch64 import cortex_a76 as Target
HERE = Path(__file__).resolve().parent
GPR_RESERVED = [f"x{i}" for i in range(18, 31)] + ["sp", "xzr"]
SRC = HERE / "phys-841.S"

out = []
for tag, cfg in [
    ("outputs=[] , split 8 + zip",  dict(factor=8,  outs=[])),
    ("outputs=[] , split 16 + zip", dict(factor=16, outs=[])),
    ("outputs=[] , split 24 + zip", dict(factor=24, outs=[])),
]:
    key = re.sub(r'\W+', '_', tag)
    lg = logging.getLogger(key); lg.handlers.clear()
    lg.setLevel(logging.DEBUG); lg.propagate = False
    lg.addHandler(logging.FileHandler(HERE/f"p2b-{key}.log", mode="w"))
    s = Slothy(Arch, Target, logger=lg)
    s.config.selftest = False
    s.config.inputs_are_outputs = False
    s.config.outputs = cfg["outs"]
    s.config.variable_size = True
    s.config.constraints.allow_spills = False
    s.config.constraints.allow_renaming = True
    s.config.constraints.allow_reordering = True
    s.config.constraints.functional_only = False
    s.config.reserved_regs = GPR_RESERVED
    s.config.timeout = 60
    s.config.split_heuristic = True
    s.config.split_heuristic_factor = cfg["factor"]
    s.config.split_heuristic_preprocess_naive_interleaving = True
    s.load_source_from_file(str(SRC))
    t0 = time.time(); ok, err = True, ""
    try:
        s.optimize(start="p28_main_slothy_start", end="p28_main_slothy_end")
        s.write_source_to_file(str(HERE/f"{key}.opt.S"))
    except Exception as e:
        ok, err = False, f"{type(e).__name__}: {str(e)[:110]}"
    dt = time.time()-t0
    cy = re.findall(r"Expected cycles:\s*(\d+)", (HERE/f"p2b-{key}.log").read_text())
    out.append(dict(config=tag, seconds=round(dt,1), ok=ok,
                    cycles=int(cy[-1]) if cy else None, error=err))
    print(f"  {tag:28s} {dt:7.1f}s  {'OK ' if ok else 'ERR'}  "
          f"cycles={cy[-1] if cy else '-'}  {err}", flush=True)
    (HERE/"phase2b-results.json").write_text(json.dumps(out, indent=2))
