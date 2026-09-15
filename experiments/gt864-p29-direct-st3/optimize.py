#!/usr/bin/env python3
"""Allocate and A76-schedule P29 tail and full-ST3 main-route windows."""

import json
import logging
import re
import sys
import time
from pathlib import Path

from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch
from slothy.targets.aarch64 import cortex_a76 as Target

HERE = Path(__file__).resolve().parent
GPR_RESERVED = [f"x{i}" for i in range(18, 31)] + ["sp", "xzr"]
STATES = ["r24", "r1", "r2", "r3", "r4", "r5", "r6", "r7",
          "r16", "r17", "r18", "r19", "r20", "r21", "r22", "r23"]


def run(source, output, start, end, tag, outputs=None, reserved=(), timing=False, timeout=120):
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


def tail():
    phase1 = HERE / "candidate-tail.phase1.S"
    state_names = [f"t_{state}" for state in STATES] + ["q"]
    states = run(
        HERE / "candidate-tail.sym.S", phase1,
        "p29_tail_slothy_start", "p29_tail_terminal_start", "tail-prefix",
        outputs=state_names, timeout=360,
    )
    missing = sorted(set(state_names) - set(states))
    if missing:
        raise RuntimeError(f"missing tail state allocations: {missing}")
    materialize(phase1, "p29_tail_terminal_start", states)

    phase2 = HERE / "candidate-tail.phase2.S"
    constant_names = ["tern_hi", "tern_lo", "tern_recip", "tern_three"]
    constants = run(
        phase1, phase2, "p29_tail_terminal_start", "p29_tail_0_low_start",
        "tail-setup", outputs=constant_names + ["x5", "x6"],
        reserved=states.values(), timeout=120,
    )
    missing = sorted(set(constant_names) - set(constants))
    if missing:
        raise RuntimeError(f"missing tail constant allocations: {missing}")
    materialize(phase2, "p29_tail_0_low_start", constants)

    current = phase2
    fixed = sorted(set(states.values()) | set(constants.values()))
    for t in range(16):
        for side in ("low", "high"):
            output = HERE / "candidate-tail.alloc.S"
            run(
                current, output, f"p29_tail_{t}_{side}_start", f"p29_tail_{t}_{side}_end",
                f"tail-{t}-{side}", reserved=fixed, timing=True, timeout=60,
            )
            current = output
    return {"output": "candidate-tail.alloc.S", "windows": 32}


def main_route():
    phase1 = HERE / "candidate-main-route.phase1.S"
    constant_names = ["tern_hi", "tern_lo", "tern_recip", "tern_three"]
    constants = run(
        HERE / "candidate-main-route.sym.S", phase1,
        "p29_main_route_slothy_start", "p29_main_route_q0_start", "route-setup",
        outputs=constant_names + ["x0", "x1", "x2"], timeout=120,
    )
    missing = sorted(set(constant_names) - set(constants))
    if missing:
        raise RuntimeError(f"missing route constant allocations: {missing}")
    materialize(phase1, "p29_main_route_q0_start", constants)
    current = phase1
    fixed = sorted(set(constants.values()))
    for window in range(32):
        output = HERE / "candidate-main-route.alloc.S"
        run(
            current, output, f"p29_main_route_q{window}_start", f"p29_main_route_q{window}_end",
            f"route-{window}", reserved=fixed, timing=True, timeout=60,
        )
        current = output
    return {"output": "candidate-main-route.alloc.S", "windows": 32}


if len(sys.argv) != 2 or sys.argv[1] not in {"tail", "route"}:
    raise SystemExit("usage: optimize.py tail|route")
started = time.monotonic()
result = tail() if sys.argv[1] == "tail" else main_route()
result.update({"mode": sys.argv[1], "seconds": time.monotonic() - started})
(HERE / f"slothy-{sys.argv[1]}-result.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
