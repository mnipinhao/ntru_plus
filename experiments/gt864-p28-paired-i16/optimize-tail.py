#!/usr/bin/env python3
"""Two-region no-spill allocation for the P28 dense tail."""

import logging
import re
from pathlib import Path

from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch
from slothy.targets.aarch64 import cortex_a76 as Target

HERE = Path(__file__).resolve().parent
LOG = HERE / "slothy-tail-ra.log"
logging.basicConfig(level=logging.DEBUG, handlers=[logging.FileHandler(LOG, mode="w")])


def allocate(source, output, start, end, outputs=None):
    s = Slothy(Arch, Target, logger=logging.getLogger(start))
    s.config.selftest = False
    s.config.inputs_are_outputs = False
    s.config.constraints.allow_spills = False
    s.config.constraints.functional_only = True
    s.config.constraints.allow_reordering = False
    s.config.constraints.allow_renaming = True
    s.config.reserved_regs = [f"x{i}" for i in range(18, 31)] + ["sp", "xzr"]
    s.config.timeout = 360
    s.config.variable_size = False
    if outputs is not None:
        s.config.outputs = outputs
    s.load_source_from_file(str(source))
    s.optimize(start=start, end=end)
    s.write_source_to_file(str(output))


def mapping():
    result = {}
    for name, register in re.findall(r"Output ([A-Za-z0-9_]+) renamed to ([a-z][0-9]+)", LOG.read_text()):
        result[name] = register
    return result


def materialize(path, label, names):
    text = path.read_text()
    head, tail = text.split(label + ":", 1)
    assigned = mapping()
    missing = sorted(set(names) - set(assigned))
    if missing:
        raise RuntimeError(f"missing tail interface allocation(s): {missing}")
    for name in sorted(names, key=len, reverse=True):
        tail = re.sub(rf"([QVDSHB])<{re.escape(name)}>", assigned[name], tail)
    path.write_text(head + label + ":" + tail)


states = ["r24", "r1", "r2", "r3", "r4", "r5", "r6", "r7",
          "r16", "r17", "r18", "r19", "r20", "r21", "r22", "r23"]
outputs = [f"t_{name}" for name in states] + ["q"]
phase1 = HERE / "candidate-tail.phase1.S"
allocate(HERE / "candidate-tail.sym.S", phase1,
         "p28_tail_slothy_start", "p28_tail_terminal_start", outputs)
materialize(phase1, "p28_tail_terminal_start", outputs)
allocate(phase1, HERE / "candidate-tail.alloc.S",
         "p28_tail_terminal_start", "p28_tail_slothy_end")
