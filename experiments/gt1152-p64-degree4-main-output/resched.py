#!/usr/bin/env python3
"""Reschedule the 1152 main invntt16 after the delivery path is deleted.

Reorder-only: the code is already validly allocated, and P60 showed that asking
Slothy to re-allocate as well makes a window infeasible at this pressure.
"""
import logging, re, sys, time
from pathlib import Path
S='/private/tmp/claude-501/-Users-chenpinhao-ntruplus/a827c50f-9c4e-40e1-b926-99dea89f0d8e/scratchpad'
sys.path.insert(0, S+'/slothy-patched')
from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch
from slothy.targets.aarch64 import cortex_a76 as Target
src=Path(S)/'inv1152_D4/inverse16.S'
txt=re.sub(r'^\s*\w*terminal_start:\s*$','',src.read_text(),flags=re.M)
tmp=Path('resched.in.S'); tmp.write_text(txt)
start=re.search(r'^\s*(\w+_slothy_start):',txt,re.M).group(1)
end=re.search(r'^\s*(\w+_slothy_end):',txt,re.M).group(1)
print(f"  region {start} .. {end}",flush=True)
lg=logging.getLogger('r'); lg.setLevel(logging.DEBUG); lg.propagate=False
lg.addHandler(logging.FileHandler('resched_d4.log',mode='w'))
s=Slothy(Arch,Target,logger=lg)
s.config.selftest=False; s.config.inputs_are_outputs=True
s.config.variable_size=True
s.config.constraints.allow_spills=False
s.config.constraints.allow_renaming=False
s.config.constraints.allow_reordering=True
s.config.constraints.functional_only=False
s.config.reserved_regs=[f"x{i}" for i in range(18,31)]+["sp","xzr"]
s.config.timeout=60
s.config.split_heuristic=True
s.config.split_heuristic_factor=16
s.config.split_heuristic_preprocess_naive_interleaving=True
s.load_source_from_file(str(tmp))
t0=time.time()
try:
    s.optimize(start=start,end=end)
    s.write_source_to_file('inverse16.d4resched.S')
    print(f"  OK  {time.time()-t0:.1f}s",flush=True)
except Exception as e:
    print(f"  ERR {time.time()-t0:.1f}s  {type(e).__name__}: {str(e)[:100]}",flush=True)
cy=re.findall(r"Expected cycles:\s*(\d+)",open('resched_d4.log').read())
print(f"  Slothy expected cycles: {cy[-1] if cy else '-'}")
