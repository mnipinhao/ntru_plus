#!/usr/bin/env python3
"""Allocate/schedule P11-A1's k-major route with the canonical local Slothy."""

import hashlib
import json
import logging
import re
import sys
import time
from pathlib import Path

from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch, cortex_a76 as Target

P = Path(__file__).resolve().parent
EXPECTED = Path("/Users/chenpinhao/slothy_and_ra/.venv/bin/python")
SLOTHY_ROOT = Path("/Users/chenpinhao/slothy")
assert Path(sys.executable).resolve() == EXPECTED.resolve()
assert Path(Arch.__file__).resolve().is_relative_to(SLOTHY_ROOT)

logger = logging.getLogger("gt864-p11.a1-route32")
logger.setLevel(logging.INFO)
logger.addHandler(logging.FileHandler(P / "slothy-a1.log", mode="w"))
slothy = Slothy(Arch, Target, logger=logger)
slothy.config.selftest = False
slothy.config.inputs_are_outputs = True
slothy.config.constraints.allow_spills = False
slothy.config.constraints.allow_reordering = True
slothy.config.constraints.functional_only = False
slothy.config.variable_size = True
slothy.config.timeout = 120
slothy.config.reserved_regs = ["v0", "v1", "v2", "v3", "x8"] + [f"x{i}" for i in range(18, 31)] + ["sp", "xzr"]
slothy.load_source_from_file(str(P / "candidate-route-a1.sym.S"))
started = time.monotonic()
slothy.optimize(start="p11a1_route32_slothy_start", end="p11a1_route32_slothy_end")
source = slothy.get_source_as_string()
(P / "candidate-route-a1.alloc.S").write_text(source)
body = source.split("p11a1_route32_slothy_start:", 1)[1].split("p11a1_route32_slothy_end:", 1)[0]
instructions = int(re.search(r"Instructions:\s+(\d+)", body).group(1))
cycles = int(re.search(r"Expected cycles:\s+(\d+)", body).group(1))
ipc = float(re.search(r"Expected IPC:\s+([0-9.]+)", body).group(1))
assert instructions == 35
code = "\n".join(line.split("//", 1)[0] for line in body.splitlines())
assert "<" not in code and ">" not in code and not re.search(r"\[sp(?:,|\])", code)
result = {
    "status": "allocation-and-scheduling-pass",
    "seconds": time.monotonic() - started,
    "instructions": instructions,
    "expected_cycles": cycles,
    "expected_ipc": ipc,
    "spills": 0,
    "interpreter": sys.executable,
    "slothy": __import__("slothy").__file__,
    "arch": Arch.__file__,
    "target": Target.__file__,
    "target_extension": None,
    "input_sha256": hashlib.sha256((P / "candidate-route-a1.sym.S").read_bytes()).hexdigest(),
    "output_sha256": hashlib.sha256(source.encode()).hexdigest(),
}
(P / "slothy-a1-result.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
