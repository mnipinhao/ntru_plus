#!/usr/bin/env python3
"""Allocate P28 in two contract-preserving regions, then emit one assembly."""

import logging
import re
from pathlib import Path

from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch
from slothy.targets.aarch64 import cortex_a76 as Target

HERE = Path(__file__).resolve().parent
logging.basicConfig(level=logging.DEBUG, handlers=[logging.FileHandler(HERE / "slothy-main-ra.log", mode="w")])


def allocate(source, output, start, end, logname, outputs=None, keep_inputs=False):
    s = Slothy(Arch, Target, logger=logging.getLogger(logname))
    s.config.selftest = False
    s.config.inputs_are_outputs = keep_inputs
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
    return s


def materialize_late_inputs(path, label, mapping):
    text = path.read_text()
    head, tail = text.split(label + ":", 1)
    for symbolic, physical in sorted(mapping.items(), key=lambda item: -len(item[0])):
        tail = re.sub(rf"([QVDSHBXW])<{re.escape(symbolic)}>",
                      lambda match: physical if match.group(1) in "QVDSHB" else physical,
                      tail)
        tail = tail.replace(f"<{symbolic}>", physical)
    path.write_text(head + label + ":" + tail)


def output_mapping_from_log(path):
    mapping = {}
    pattern = re.compile(r"Output ([A-Za-z0-9_]+) renamed to ([a-z][0-9]+)")
    for match in pattern.finditer(path.read_text()):
        mapping[match.group(1)] = match.group(2)
    return mapping


phase1 = HERE / "candidate-main.phase1.S"
phase1_outputs = (
    [f"a_{r}" for r in ["r24", "r1", "r2", "r3", "r4", "r5", "r6", "r7", "r16", "r17"]]
    + [f"b_{r}" for r in ["r24", "r1", "r2", "r3", "r4", "r5", "r6", "r7",
                              "r16", "r17", "r18", "r19", "r20", "r21", "r22", "r23"]]
    + ["q"] + [f"x{i}" for i in range(5, 17)]
)
prefix = allocate(HERE / "candidate-main.sym.S", phase1,
                  "p28_main_slothy_start", "p28_main_terminal_start", "p28-main-prefix",
                  phase1_outputs)
mapping = output_mapping_from_log(HERE / "slothy-main-ra.log")
missing = sorted(set(phase1_outputs) - set(mapping) - {f"x{i}" for i in range(5, 17)})
if missing:
    raise RuntimeError(f"missing phase-1 output allocation(s): {missing}")
materialize_late_inputs(phase1, "p28_main_terminal_start", mapping)
allocate(phase1, HERE / "candidate-main.alloc.S",
         "p28_main_terminal_start", "p28_main_slothy_end", "p28-main-terminal")
