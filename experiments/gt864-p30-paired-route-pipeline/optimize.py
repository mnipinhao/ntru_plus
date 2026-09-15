#!/usr/bin/env python3
"""Allocate and A76-schedule P30 as sixteen adjacent-record windows."""

import json
import logging
import re
import time
from pathlib import Path

from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch
from slothy.targets.aarch64 import cortex_a76 as Target

HERE = Path(__file__).resolve().parent
# All GPRs are concrete ABI/address registers in this region.  In particular,
# x2 carries a chain of post-index ST3 writebacks that the current instruction
# model must not rename across records.  Only Neon registers are allocatable.
GPR_RESERVED = [f"x{i}" for i in range(31)] + ["sp", "xzr"]


def run(source, output, start, end, tag, outputs=None, reserved=(), timing=False, timeout=240):
    log = HERE / f"slothy-{tag}.log"
    logger = logging.getLogger(tag)
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    logger.addHandler(logging.FileHandler(log, mode="w"))
    solver = Slothy(Arch, Target, logger=logger)
    solver.config.selftest = False
    solver.config.inputs_are_outputs = outputs is None
    solver.config.constraints.allow_spills = False
    solver.config.constraints.functional_only = not timing
    solver.config.constraints.allow_reordering = timing
    solver.config.constraints.allow_renaming = True
    solver.config.reserved_regs = GPR_RESERVED + list(reserved)
    solver.config.timeout = timeout
    solver.config.variable_size = False
    if outputs is not None:
        solver.config.outputs = outputs
    solver.load_source_from_file(str(source))
    solver.optimize(start=start, end=end)
    solver.write_source_to_file(str(output))
    mapping = dict(re.findall(
        r"Output ([A-Za-z0-9_]+) renamed to ([a-z][0-9]+)", log.read_text()
    ))
    return mapping


def materialize(path, label, mapping):
    text = path.read_text()
    head, tail = text.split(label + ":", 1)
    for name in sorted(mapping, key=len, reverse=True):
        tail = re.sub(rf"([QVDSHB])<{re.escape(name)}>", mapping[name], tail)
    path.write_text(head + label + ":" + tail)


started = time.monotonic()
phase1 = HERE / "candidate-route.phase1.S"
constant_names = ["tern_hi", "tern_lo", "tern_recip", "tern_three"]
constants = run(
    HERE / "candidate-route.sym.S", phase1,
    "p29_main_route_slothy_start", "p30_route_pair0_start", "setup",
    outputs=constant_names + ["x0", "x1", "x2"], timeout=120,
)
missing = sorted(set(constant_names) - set(constants))
if missing:
    raise RuntimeError(f"missing constant allocations: {missing}")
materialize(phase1, "p30_route_pair0_start", constants)

current = phase1
fixed = sorted(set(constants.values()))
for pair in range(16):
    output = HERE / "candidate-route.alloc.S"
    run(
        current, output,
        f"p30_route_pair{pair}_start", f"p30_route_pair{pair}_end",
        f"pair-{pair}", reserved=fixed, timing=True, timeout=240,
    )
    current = output

result = {
    "output": "candidate-route.alloc.S",
    "windows": 16,
    "records_per_window": 2,
    "seconds": time.monotonic() - started,
    "slothy_root": str(Path(__file__).resolve().parents[3] / "slothy"),
    "target": "cortex_a76",
    "allow_spills": False,
}
(HERE / "slothy-result.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
