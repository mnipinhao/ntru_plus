"""Timing-schedule the fixed, loop-safe center864 allocation."""

import hashlib
import json
import logging
from pathlib import Path

from slothy import Config
from slothy.core.heuristics import Heuristics
from slothy.helper import SourceLine
from slothy.targets.aarch64 import aarch64_neon as Arch, cortex_a76 as Target


P = Path(__file__).resolve().parent
assert Path(Arch.__file__).resolve().is_relative_to("/Users/chenpinhao/slothy")

source_path = P / "candidate.alloc.S"
source = source_path.read_text()
body = []
inside = False
for line in source.splitlines():
    if line.strip() == "center864_body_slothy_start:":
        inside = True
        continue
    if line.strip() == "center864_body_slothy_end:":
        break
    instruction = line.split("//", 1)[0].strip()
    if inside and instruction and not instruction.endswith(":"):
        body.append(instruction)
assert len(body) == 40

logger = logging.getLogger("gt864-p3-center")
logger.setLevel(logging.INFO)
logger.addHandler(logging.FileHandler(P / "slothy.log", mode="w"))
config = Config(Arch, Target, logger)
config.selftest = False
config.inputs_are_outputs = True
config.outputs = ["x0", "v0", "v1", "v2"]
config.constraints.allow_spills = False
config.constraints.allow_reordering = True
config.constraints.allow_renaming = False
config.constraints.functional_only = False
config.variable_size = True
config.timeout = 120
config.reserved_regs = [f"x{i}" for i in range(18, 31)] + ["sp", "xzr"]

result = Heuristics.linear(SourceLine.read_multiline("\n".join(body)), logger, config)
assert result.success
scheduled = [line.text for line in result.code_raw]
assert len(scheduled) == 40

output = []
inside = False
for line in source.splitlines():
    if line.strip() == "center864_body_slothy_start:":
        output.append(line)
        output.extend("    " + instruction.strip() for instruction in scheduled)
        inside = True
        continue
    if line.strip() == "center864_body_slothy_end:":
        inside = False
        output.append(line)
        continue
    if not inside:
        output.append(line)
output_text = "\n".join(output) + "\n"
(P / "candidate.opt.S").write_text(output_text)

# All four loads must remain before the first overlapping store.
scheduled_ops = [instruction.strip().split()[0] for instruction in scheduled]
first_store = min(i for i, op in enumerate(scheduled_ops) if op == "str")
last_load = max(i for i, op in enumerate(scheduled_ops) if op == "ldr")
assert last_load < first_store
assert not any("sp" in instruction for instruction in scheduled)

report = {
    "status": "fixed-allocation-timing-pass",
    "instructions_per_iteration": len(scheduled),
    "modeled_cycles_per_iteration": result.cycles,
    "spills": 0,
    "allow_renaming": False,
    "constant_registers": {"q": "v0", "reciprocal9": "v1", "halfq": "v2"},
    "data_registers": ["v3", "v4", "v5", "v6"],
    "temporary_registers": ["v7", "v8", "v9", "v10"],
    "interpreter": __import__("sys").executable,
    "slothy": __import__("slothy").__file__,
    "input_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
    "output_sha256": hashlib.sha256(output_text.encode()).hexdigest(),
}
(P / "slothy-result.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
