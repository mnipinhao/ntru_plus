#!/usr/bin/env python3
"""Run P6-B route and full-normalization allocation frontiers."""

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
SourceLine.__str__ = lambda self: self.to_string(indentation=True, comments=True, tags=True)


def allocate(name: str, start: str, end: str) -> dict[str, object]:
    log_path = HERE / f"slothy-{name}.log"
    out_path = HERE / f"candidate.{name}.alloc.S"
    logger = logging.getLogger(f"p6b-{name}")
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
    s.load_source_from_file(str(HERE / "candidate.sym.S"))
    try:
        s.optimize(start=start, end=end)
    except SlothyException as exc:
        status = "infeasible"
        error = type(exc).__name__
    else:
        s.write_source_to_file(str(out_path))
        status = "allocated"
        error = None
    log = log_path.read_text()
    return {
        "status": status,
        "error": error,
        "solver_infeasible": "INFEASIBLE" in log,
        "spill_tokens": sum(log.lower().count(x) for x in ("spill", "reload")),
        "allocated_output": str(out_path) if out_path.exists() else None,
        "log": str(log_path),
    }


result = {
    "route_frontier": allocate(
        "route",
        "gt864_p6b_route_frontier_slothy_start",
        "gt864_p6b_route_frontier_slothy_end",
    ),
    "full_normalization_frontier": allocate(
        "normalize",
        "gt864_p6b_full_normalize_frontier_slothy_start",
        "gt864_p6b_full_normalize_frontier_slothy_end",
    ),
    "slothy_source": str(Path(__import__("slothy").__file__).resolve()),
    "slothy_arch": str(Path(Arch.__file__).resolve()),
    "slothy_target": str(Path(Target.__file__).resolve()),
    "allow_spills": False,
}
(HERE / "slothy-results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
