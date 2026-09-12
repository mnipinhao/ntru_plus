#!/usr/bin/env python3
"""Authorized local Slothy allocation/scheduling for P10's three regions."""

from __future__ import annotations

import hashlib
import json
import logging
import re
import sys
from pathlib import Path

from slothy import Slothy
from slothy.targets.aarch64 import aarch64_neon as Arch, cortex_a76 as Target

HERE = Path(__file__).resolve().parent
SLOTHY_ROOT = Path("/Users/chenpinhao/slothy")
EXPECTED_INTERPRETER = Path("/Users/chenpinhao/slothy_and_ra/.venv/bin/python")
assert Path(sys.executable).resolve() == EXPECTED_INTERPRETER.resolve()
assert Path(Arch.__file__).resolve().is_relative_to(SLOTHY_ROOT)

regions = [
    ("p10_num_pair", 132, {"q_num": "v30", "qi_num": "v31"}),
    ("p10_finish_tile", 26, {"q_finish": "v30", "qi_finish": "v31"}),
    ("p10_inverse3", 164, {}),
]

source = (HERE / "candidate.sym.S").read_text()
results = {}
for name, expected_instructions, fixed_inputs in regions:
    log_path = HERE / f"slothy-{name}.log"
    logger = logging.getLogger(f"gt864-p10.{name}")
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.FileHandler(log_path, mode="w"))

    slothy = Slothy(Arch, Target, logger=logger)
    slothy.config.selftest = False
    slothy.config.inputs_are_outputs = True
    slothy.config.constraints.allow_spills = False
    slothy.config.constraints.allow_reordering = True
    slothy.config.constraints.functional_only = False
    slothy.config.variable_size = True
    slothy.config.timeout = 240
    slothy.config.reserved_regs = [f"x{i}" for i in range(18, 31)] + ["sp", "xzr"]
    if fixed_inputs:
        rename = {"arch": "static", "symbolic": "any", **fixed_inputs}
        slothy.config.rename_inputs = rename
        slothy.config.rename_outputs = rename
    slothy.load_source_raw(source)
    slothy.optimize(start=f"{name}_slothy_start", end=f"{name}_slothy_end")
    source = slothy.get_source_as_string()

    body = source.split(f"{name}_slothy_start:", 1)[1].split(f"{name}_slothy_end:", 1)[0]
    instruction_match = re.search(r"Instructions:\s+(\d+)", body)
    cycle_match = re.search(r"Expected cycles:\s+(\d+)", body)
    ipc_match = re.search(r"Expected IPC:\s+([0-9.]+)", body)
    assert instruction_match and int(instruction_match.group(1)) == expected_instructions
    assert cycle_match and ipc_match
    code = "\n".join(line.split("//", 1)[0] for line in body.splitlines())
    assert "<" not in code and ">" not in code
    assert not re.search(r"\[sp(?:,|\])", code)
    if fixed_inputs:
        assert "v30." in code and "v31." in code
    results[name] = {
        "instructions": expected_instructions,
        "expected_cycles": int(cycle_match.group(1)),
        "expected_ipc": float(ipc_match.group(1)),
        "log": log_path.name,
        "fixed_inputs": fixed_inputs,
    }

(HERE / "candidate.alloc.S").write_text(source)
result = {
    "status": "allocation-and-scheduling-pass",
    "spills": 0,
    "interpreter": sys.executable,
    "slothy": __import__("slothy").__file__,
    "arch": Arch.__file__,
    "target": Target.__file__,
    "input_sha256": hashlib.sha256((HERE / "candidate.sym.S").read_bytes()).hexdigest(),
    "output_sha256": hashlib.sha256(source.encode()).hexdigest(),
    "regions": results,
}
(HERE / "slothy-result.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
