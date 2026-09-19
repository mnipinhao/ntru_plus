#!/usr/bin/env python3
"""Phase 2 on the fused kernels, using the recipe P59 established:
split_heuristic factor 16 + naive interleaving, variable_size, outputs declared,
no ST3 writeback, and a Cortex-A76 model patched to know `vins_d`.
"""
import json, logging, re, sys, time
from pathlib import Path
S='/private/tmp/claude-501/-Users-chenpinhao-ntruplus/a827c50f-9c4e-40e1-b926-99dea89f0d8e/scratchpad'
sys.path.insert(0, S+'/slothy-patched')
from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch
from slothy.targets.aarch64 import cortex_a76 as Target
HERE=Path(__file__).resolve().parent
GPR_RESERVED=[f"x{i}" for i in range(18,31)]+["sp","xzr"]
FACTOR=int(sys.argv[1]) if len(sys.argv)>1 else 16
CAP=int(sys.argv[2]) if len(sys.argv)>2 else 60
out=[]
for name in ('fused_bank0','fused_bank1','fused_bank2'):
    src=HERE/f"{name}.S"
    # inner marker labels cannot appear inside an optimisation region
    txt=re.sub(r'^\s*p28_main_terminal_start:\s*$','',src.read_text(),flags=re.M)
    tmp=HERE/f"{name}.in.S"; tmp.write_text(txt)
    n=len([l for l in txt.splitlines() if re.match(r'\s+[a-z]',re.sub(r'//.*','',l))])
    lg=logging.getLogger(name); lg.handlers.clear()
    lg.setLevel(logging.DEBUG); lg.propagate=False
    lg.addHandler(logging.FileHandler(HERE/f"sched-{name}.log",mode="w"))
    s=Slothy(Arch,Target,logger=lg)
    s.config.selftest=False
    s.config.inputs_are_outputs=False
    s.config.outputs=[]
    s.config.variable_size=True
    s.config.constraints.allow_spills=False
    s.config.constraints.allow_renaming=True
    s.config.constraints.allow_reordering=True
    s.config.constraints.functional_only=False
    s.config.reserved_regs=GPR_RESERVED
    s.config.timeout=CAP
    s.config.split_heuristic=True
    s.config.split_heuristic_factor=FACTOR
    s.config.split_heuristic_preprocess_naive_interleaving=True
    s.load_source_from_file(str(tmp))
    t0=time.time(); ok,err=True,""
    try:
        s.optimize(start="p28_main_slothy_start", end="p28_main_slothy_end")
        s.write_source_to_file(str(HERE/f"{name}.sched.S"))
    except Exception as e:
        ok,err=False,f"{type(e).__name__}: {str(e)[:90]}"
    dt=time.time()-t0
    cy=re.findall(r"Expected cycles:\s*(\d+)",(HERE/f"sched-{name}.log").read_text())
    out.append(dict(kernel=name,instructions=n,seconds=round(dt,1),ok=ok,
                    cycles=int(cy[-1]) if cy else None,error=err))
    print(f"  {name:14s} {n:5d} instr  {dt:7.1f}s  {'OK ' if ok else 'ERR'}  "
          f"cycles={cy[-1] if cy else '-'}  {err}",flush=True)
    (HERE/"schedule-results.json").write_text(json.dumps(out,indent=2))
