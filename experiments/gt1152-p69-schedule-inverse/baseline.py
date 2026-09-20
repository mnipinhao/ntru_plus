#!/usr/bin/env python3
"""What does the EXISTING schedule cost, in the same model Slothy optimises in?

No reordering, no renaming: pure timing analysis of the code as it stands.
Without this the optimized figure has nothing to be compared against.
"""
import logging, re, sys
from pathlib import Path
SLOTHY='/private/tmp/claude-501/-Users-chenpinhao-ntruplus/a827c50f-9c4e-40e1-b926-99dea89f0d8e/scratchpad/slothy-patched'
sys.path.insert(0, SLOTHY)
from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch
from slothy.targets.aarch64 import cortex_a76 as Target
HERE=Path(__file__).resolve().parent
for name, sym, used in [("inverse9","packed_i9",{"x0","x2","x3","x5","x6","x8","x10","x11","x15","x17"}),
                        ("inverse16","invntt16_asm",{"x0","x1","x3","x4","x7","x15"})]:
    src = HERE/".."/"gt1152-p10-kem"/f"{name}.S"
    lg=logging.getLogger(f"base-{name}"); lg.handlers.clear(); lg.setLevel(logging.DEBUG); lg.propagate=False
    lg.addHandler(logging.FileHandler(HERE/f"log-base-{name}.log", mode="w"))
    s=Slothy(Arch,Target,logger=lg)
    s.config.selftest=False; s.config.inputs_are_outputs=True
    s.config.variable_size=True
    s.config.constraints.allow_spills=False
    s.config.constraints.allow_renaming=False
    s.config.constraints.allow_reordering=False       # measure, do not optimise
    s.config.reserved_regs=[f"x{i}" for i in range(31) if f"x{i}" not in used]+["sp","xzr"]
    s.config.timeout=300
    s.load_source_from_file(str(src))
    try:
        s.optimize(start=f"{sym}_slothy_start", end=f"{sym}_slothy_end")
        out=HERE/f"{name}.asis.S"; s.write_source_to_file(str(out))
        m=re.findall(r'cycles?\s*[:=]\s*(\d+)', out.read_text())
        print(f"  {name:<10} existing schedule: {m[-1] if m else '?'} cycles", flush=True)
    except Exception as e:
        print(f"  {name:<10} ERR {type(e).__name__}: {str(e)[:70]}", flush=True)
