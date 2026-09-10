#!/usr/bin/env python3
"""Allocate P6-C packed-A and worst-row semantic regions."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from slothy import Slothy
from slothy.core.core import SlothyException
from slothy.helper import SourceLine
from slothy.targets.aarch64 import aarch64_neon as Arch
from slothy.targets.aarch64 import cortex_a76 as Target
from tbl3_a76_model import install as install_tbl3

HERE = Path(__file__).resolve().parent
SourceLine.__str__ = lambda self: self.to_string(indentation=True, comments=True, tags=True)
install_tbl3()


def allocate(name: str, start: str, end: str) -> dict[str, object]:
    log_path = HERE / f"slothy-{name}.log"
    out_path = HERE / f"candidate.{name}.alloc.S"
    logger = logging.getLogger(f"p6c-{name}")
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.FileHandler(log_path, mode="w"))
    s = Slothy(Arch, Target, logger=logger)
    s.config.selftest = False
    # Every semantic live-out is made explicit by a store in each allocation
    # slice.  Treating all inputs as outputs would incorrectly preserve the
    # destructively normalized A/B rows.
    s.config.inputs_are_outputs = False
    s.config.constraints.allow_spills = False
    s.config.constraints.functional_only = True
    s.config.constraints.allow_reordering = False
    s.config.constraints.allow_renaming = True
    s.config.variable_size = False
    # x30 is the live link register of these callable leaf regions; x29 is
    # reserved with it so neither can become a renamed scalar temporary.
    s.config.reserved_regs = ["x18", "x29", "x30", "sp", "xzr"]
    s.config.timeout = 180
    s.load_source_from_file(str(HERE / "candidate.sym.S"))
    try:
        s.optimize(start=start, end=end)
    except SlothyException as exc:
        status, error = "infeasible", type(exc).__name__
    else:
        s.write_source_to_file(str(out_path))
        status, error = "allocated", None
    log = log_path.read_text()
    return {
        "status": status,
        "error": error,
        "solver_optimal": "OPTIMAL" in log,
        "solver_infeasible": "INFEASIBLE" in log,
        "spill_or_reload": bool(re.search(r"\b(spill|reload)\b", log, re.I)),
        "allocated_output": str(out_path) if out_path.exists() else None,
        "log": str(log_path),
    }


result = {
    "row0": allocate("row0", "gt864_p6c_row0_slothy_start", "gt864_p6c_row0_slothy_end"),
    "pack_a": allocate("pack-a", "gt864_p6c_pack_a_slothy_start", "gt864_p6c_pack_a_slothy_end"),
    "slothy_source": str(Path(__import__("slothy").__file__).resolve()),
    "slothy_arch": str(Path(Arch.__file__).resolve()),
    "slothy_target": str(Path(Target.__file__).resolve()),
    "allow_spills": False,
}
(HERE / "slothy-results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
