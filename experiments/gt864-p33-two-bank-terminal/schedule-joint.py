#!/usr/bin/env python3
"""P33-S: timing-only A/B terminal scheduling with fixed physical registers."""
import json
import logging
import re
import time
from pathlib import Path

from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch
from slothy.targets.aarch64 import cortex_a76 as Target

HERE = Path(__file__).resolve().parent
ALL_GPRS = [f"x{i}" for i in range(31)] + ["sp", "xzr"]


def run(source, output, t):
    tag = f"joint-t{t}"
    logger = logging.getLogger(tag)
    logger.handlers.clear()
    logger.propagate = False
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.FileHandler(HERE / f"slothy-{tag}.log", mode="w"))
    s = Slothy(Arch, Target, logger=logger)
    s.config.selftest = False
    s.config.inputs_are_outputs = True
    s.config.constraints.allow_spills = False
    s.config.constraints.functional_only = False
    s.config.constraints.allow_reordering = True
    s.config.constraints.allow_renaming = False
    s.config.reserved_regs = ALL_GPRS
    s.config.timeout = 120
    s.config.variable_size = False
    s.load_source_from_file(str(source))
    s.optimize(start=f"p33_i16_pair_t{t}_start", end=f"p33_i16_pair_t{t}_end")
    s.write_source_to_file(str(output))


source = HERE / "candidate-pair.alloc.S"
work = HERE / "candidate-pair.joint-work.S"
text = source.read_text()
# Slothy region parsing does not accept nested labels.  These labels delimit
# the earlier allocation subwindows only and carry no control-flow semantics.
text = re.sub(r"^\s*p33_i16_pair_t\d+_(?:a_end|b_start|b_end):\s*\n", "", text, flags=re.M)
work.write_text(text)
started = time.monotonic()
current = work
for t in range(16):
    output = HERE / "candidate-pair.joint.S"
    run(current, output, t)
    current = output
(HERE / "slothy-joint-result.json").write_text(json.dumps({
    "output": str(current),
    "windows": 16,
    "allow_renaming": False,
    "allow_spills": False,
    "seconds": time.monotonic() - started,
}, indent=2) + "\n")
print((HERE / "slothy-joint-result.json").read_text())
