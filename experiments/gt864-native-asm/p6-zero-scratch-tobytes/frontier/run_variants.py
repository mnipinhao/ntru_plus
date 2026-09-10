"""Run exact and two attribution controls for the P6 vector frontier."""
from __future__ import annotations

import json
import logging
from pathlib import Path

from slothy import Slothy
from slothy.core.core import SlothyException
from slothy.helper import SourceLine
from slothy.targets.aarch64 import aarch64_neon as Arch
from slothy.targets.aarch64 import cortex_a76 as Target

HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"
BUILD.mkdir(exist_ok=True)
SourceLine.__str__ = lambda self: self.to_string(
    indentation=True, comments=True, tags=True
)


def allocate(name: str, text: str) -> dict[str, object]:
    source = BUILD / f"{name}.sym.S"
    allocated = BUILD / f"{name}.alloc.S"
    log_path = HERE / f"slothy-{name}.log"
    source.write_text(text)
    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.FileHandler(log_path, mode="w"))
    s = Slothy(Arch, Target, logger=logger)
    s.config.selftest = False
    s.config.inputs_are_outputs = True
    s.config.constraints.allow_spills = False
    s.config.constraints.functional_only = True
    s.config.constraints.allow_reordering = False
    s.config.constraints.allow_renaming = True
    s.config.variable_size = False
    s.config.reserved_regs = ["x18", "sp", "xzr"]
    s.config.timeout = 120
    s.load_source_from_file(str(source))
    try:
        s.optimize(
            start="gt864_p6_register_frontier_slothy_start",
            end="gt864_p6_register_frontier_slothy_end",
        )
    except SlothyException:
        status = "infeasible"
    else:
        s.write_source_to_file(str(allocated))
        status = "allocated"
    log = log_path.read_text()
    return {
        "status": status,
        "solver_infeasible": "INFEASIBLE" in log,
        "allocated_output": str(allocated) if allocated.exists() else None,
        "log": str(log_path),
    }


base = (HERE / "candidate.sym.S").read_text()
minus_one = base.replace("    ldr Q<h12>, [x3, #192]\n", "")
minus_one = minus_one.replace("    str Q<h12>, [x4, #192]\n", "")
no_index = base.replace("    ldr Q<idx0>, [x2]\n", "")
no_index = no_index.replace(
    "    tbl V<row0>.16b, {V<row0>.16b}, V<idx0>.16b\n", ""
)

result = {
    "exact_31_plus_row_plus_index": allocate("exact", base),
    "control_30_plus_row_plus_index": allocate("minus-one-held", minus_one),
    "control_31_plus_row_no_index": allocate("no-index", no_index),
    "slothy_arch": str(Path(Arch.__file__).resolve()),
    "slothy_target": str(Path(Target.__file__).resolve()),
    "allow_spills": False,
}
(HERE / "frontier-results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
