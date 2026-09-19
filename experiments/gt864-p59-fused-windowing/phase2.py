#!/usr/bin/env python3
"""Validate phase 2: does split_heuristic converge on PHYSICAL code of full size?

Input is P28's shipped allocated producer (841 instructions, physical registers),
which is the size the physical-insertion flow would hand to phase 2.
"""
import json, logging, re, sys, time
from pathlib import Path
sys.path.insert(0, '/private/tmp/claude-501/-Users-chenpinhao-ntruplus/a827c50f-9c4e-40e1-b926-99dea89f0d8e/scratchpad/slothy-patched')
from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch
from slothy.targets.aarch64 import cortex_a76 as Target
HERE = Path(__file__).resolve().parent
SRC = Path('../gt864-p28s-timing/candidate-main.timing.S')
GPR_RESERVED = [f"x{i}" for i in range(18, 31)] + ["sp", "xzr"]
# give the region the labels Slothy needs
# use the producer's own Slothy region labels rather than inserting new ones
# inner marker labels are not parseable inside an optimisation region
src = re.sub(r'^\s*p28_main_terminal_start:\s*$', '', SRC.read_text(), flags=re.M)
(HERE/"phys-841.S").write_text(src)
n = len([l for l in (HERE/'phys-841.S').read_text().splitlines()
         if re.match(r'\s+[a-z]', re.sub(r'//.*','',l))])
print(f"  input: {n} physical instructions", flush=True)
out=[]
for tag, extra in [("split 8 + zip",  dict(split_heuristic_factor=8,
                      split_heuristic_preprocess_naive_interleaving=True)),
                   ("split 16 + zip", dict(split_heuristic_factor=16,
                      split_heuristic_preprocess_naive_interleaving=True))]:
    key = re.sub(r'\W+','_',tag)
    lg = logging.getLogger(key); lg.handlers.clear()
    lg.setLevel(logging.DEBUG); lg.propagate=False
    lg.addHandler(logging.FileHandler(HERE/f"p2-{key}.log", mode="w"))
    s = Slothy(Arch, Target, logger=lg)
    s.config.selftest=False; s.config.inputs_are_outputs=True
    s.config.variable_size=True
    s.config.constraints.allow_spills=False
    s.config.constraints.allow_renaming=True
    s.config.constraints.allow_reordering=True
    s.config.constraints.functional_only=False
    s.config.reserved_regs=GPR_RESERVED
    s.config.timeout=60
    s.config.split_heuristic=True
    for k,v in extra.items(): setattr(s.config,k,v)
    s.load_source_from_file(str(HERE/"phys-841.S"))
    t0=time.time(); ok,err=True,""
    try:
        s.optimize(start="p28_main_slothy_start", end="p28_main_slothy_end")
        s.write_source_to_file(str(HERE/f"phys-841-{key}.opt.S"))
    except Exception as e:
        ok,err=False,f"{type(e).__name__}: {str(e)[:140]}"
    dt=time.time()-t0
    cy=re.findall(r"Expected cycles:\s*(\d+)",(HERE/f"p2-{key}.log").read_text())
    out.append(dict(config=tag,seconds=round(dt,1),ok=ok,cycles=int(cy[-1]) if cy else None,error=err))
    print(f"  {tag:18s} {dt:7.1f}s  {'OK ' if ok else 'ERR'}  "
          f"cycles={cy[-1] if cy else '-'}  {err}", flush=True)
    (HERE/"phase2-results.json").write_text(json.dumps(out,indent=2))
