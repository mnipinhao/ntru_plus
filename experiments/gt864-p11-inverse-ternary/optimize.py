#!/usr/bin/env python3
"""Authorized local Cortex-A76 Slothy allocation/scheduling for P11 route32."""

import hashlib
import json
import logging
import re
import sys
import time
from pathlib import Path

from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch, cortex_a76 as Target
from slothy.targets.aarch64.aarch64_neon import vins_d

P = Path(__file__).resolve().parent
EXPECTED = Path("/Users/chenpinhao/slothy_and_ra/.venv/bin/python")
SLOTHY_ROOT = Path("/Users/chenpinhao/slothy")
assert Path(sys.executable).resolve() == EXPECTED.resolve()
assert Path(Arch.__file__).resolve().is_relative_to(SLOTHY_ROOT)

# The architecture parser has GPR->D-lane INS, while the A76 table currently
# omits that class.  It has the same V-pipe/throughput/latency entry as the
# already modeled H-lane INS and vector move.  This run-local extension keeps
# the canonical checkout untouched; Pi 5 timing remains the promotion gate.
Target.execution_units[vins_d] = Target.ExecutionUnit.V()
Target.inverse_throughput[vins_d] = 1
Target.default_latencies[vins_d] = 2

logger = logging.getLogger("gt864-p11.route32")
logger.setLevel(logging.INFO)
logger.addHandler(logging.FileHandler(P / "slothy.log", mode="w"))

slothy = Slothy(Arch, Target, logger=logger)
slothy.config.selftest = False
slothy.config.inputs_are_outputs = True
slothy.config.constraints.allow_spills = False
slothy.config.constraints.allow_reordering = True
slothy.config.constraints.functional_only = False
slothy.config.variable_size = True
slothy.config.timeout = 120
slothy.config.reserved_regs = ["v0", "v1", "v2", "v3", "x8"] + [f"x{i}" for i in range(18, 31)] + ["sp", "xzr"]

slothy.load_source_from_file(str(P / "candidate-route.sym.S"))
started = time.monotonic()
slothy.optimize(start="p11_route32_slothy_start", end="p11_route32_slothy_end")
source = slothy.get_source_as_string()
(P / "candidate-route.alloc.S").write_text(source)

body = source.split("p11_route32_slothy_start:", 1)[1].split("p11_route32_slothy_end:", 1)[0]
instruction_match = re.search(r"Instructions:\s+(\d+)", body)
cycle_match = re.search(r"Expected cycles:\s+(\d+)", body)
ipc_match = re.search(r"Expected IPC:\s+([0-9.]+)", body)
assert instruction_match and int(instruction_match.group(1)) == 38
assert cycle_match and ipc_match
code = "\n".join(line.split("//", 1)[0] for line in body.splitlines())
assert "<" not in code and ">" not in code
assert not re.search(r"\[sp(?:,|\])", code)

result = {
    "status": "allocation-and-scheduling-pass",
    "seconds": time.monotonic() - started,
    "instructions": 38,
    "expected_cycles": int(cycle_match.group(1)),
    "expected_ipc": float(ipc_match.group(1)),
    "spills": 0,
    "interpreter": sys.executable,
    "slothy": __import__("slothy").__file__,
    "arch": Arch.__file__,
    "target": Target.__file__,
    "target_extension": "vins_d: V0/V1, inverse-throughput 1, latency 2 (matched vins_h_lane)",
    "input_sha256": hashlib.sha256((P / "candidate-route.sym.S").read_bytes()).hexdigest(),
    "output_sha256": hashlib.sha256(source.encode()).hexdigest(),
}
(P / "slothy-result.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
