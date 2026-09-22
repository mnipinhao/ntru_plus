#!/usr/bin/env python3
"""Authorized local Slothy scheduling for the P97 repack, four regions.

The hand-written pass recycles x3/x5 every group and emits the groups in strict
order -- on A76's four-wide window that is exactly the shape that cannot
overlap.  397 instructions in one region is past what this repo has ever asked
of Slothy (132/26/164 in P10), so it is cut at four-group boundaries.
"""
import logging, re, sys
from pathlib import Path
sys.path.insert(0, "/Users/chenpinhao/slothy")
from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch, cortex_a76 as Target
assert Path(Arch.__file__).resolve().is_relative_to(Path("/Users/chenpinhao/slothy"))

HERE = Path(__file__).resolve().parent
src  = (HERE / "repack_split.S").read_text()
logger = logging.getLogger("p97.split")
logger.handlers.clear(); logger.setLevel(logging.INFO)
logger.addHandler(logging.FileHandler(HERE / "slothy-split-a76.log", mode="w"))

for r in range(4):
    s = Slothy(Arch, Target, logger=logger)
    s.config.selftest = False
    s.config.inputs_are_outputs = True
    s.config.constraints.allow_spills = False
    s.config.constraints.allow_reordering = True
    s.config.constraints.functional_only = False
    s.config.variable_size = True
    s.config.rename_inputs = {"arch": "static", "symbolic": "any"}
    s.config.timeout = 420
    s.config.reserved_regs = [f"x{i}" for i in range(18, 31)] + ["sp", "xzr"]
    s.load_source_raw(src)
    s.optimize(start=f"rp{r}_slothy_start", end=f"rp{r}_slothy_end")
    src = s.get_source_as_string()
    body = src.split(f"rp{r}_slothy_start:", 1)[1].split(f"rp{r}_slothy_end:", 1)[0]
    code = "\n".join(l.split("//", 1)[0] for l in body.splitlines())
    assert "<" not in code and ">" not in code, f"rp{r}: symbolic registers survived"
    assert not re.search(r"\[sp(?:,|\])", code), f"rp{r}: spilled to the stack"
    got = {k: re.search(rf"{k}:\s+([0-9.]+)", body) for k in
           ("Instructions", "Expected cycles", "Expected IPC")}
    print(f"  rp{r}: " + ", ".join(f"{k} {m.group(1) if m else '?'}" for k, m in got.items()))
(HERE / "repack_sched.S").write_text(src)
print("  已寫出 repack_sched.S")
