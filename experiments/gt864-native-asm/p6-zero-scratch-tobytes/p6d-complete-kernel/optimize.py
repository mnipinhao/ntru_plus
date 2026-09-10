#!/usr/bin/env python3
"""Allocation-only P6-D1 producer proof; timing windows come after full DAG."""

from __future__ import annotations

import json
import logging
import re
import sys
from pathlib import Path

from slothy import Slothy
from slothy.core.core import SlothyException
from slothy.helper import SourceLine
from slothy.targets.aarch64 import aarch64_neon as Arch
from slothy.targets.aarch64 import cortex_a76 as Target

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "p6c-joint-consumer"))
from tbl3_a76_model import install  # noqa: E402
SourceLine.__str__ = lambda self: self.to_string(indentation=True, comments=True, tags=True)
install()


def allocate(name: str, start: str, end: str) -> dict[str, object]:
    log = HERE / f"slothy-{name}.log"; output = HERE / f"producer.{name}.alloc.S"
    logger = logging.getLogger("p6d-" + name); logger.handlers.clear(); logger.setLevel(logging.INFO); logger.addHandler(logging.FileHandler(log, mode="w"))
    s = Slothy(Arch, Target, logger=logger)
    s.config.selftest = False
    s.config.inputs_are_outputs = False
    s.config.constraints.allow_spills = False
    s.config.constraints.functional_only = True
    s.config.constraints.allow_reordering = False
    s.config.constraints.allow_renaming = True
    s.config.variable_size = False
    s.config.reserved_regs = ["x18", "x29", "x30", "sp", "xzr"]
    s.config.timeout = 240
    s.load_source_from_file(str(HERE / "producer.sym.S"))
    try:
        s.optimize(start=start, end=end)
    except SlothyException as exc:
        status, error = "infeasible", type(exc).__name__
    else:
        s.write_source_to_file(str(output)); status, error = "allocated", None
    text = log.read_text()
    return {"status": status, "error": error, "optimal": "OPTIMAL" in text, "infeasible": "INFEASIBLE" in text,
            "spill_or_reload": bool(re.search(r"\b(spill|reload)\b", text, re.I)), "output": str(output) if output.exists() else None, "log": str(log)}


result = {"pair0": allocate("pair0", "gt864_p6d_pair0_start", "gt864_p6d_pair0_end"),
          "pair1": allocate("pair1", "gt864_p6d_pair1_start", "gt864_p6d_pair1_end"),
          "slothy_source": str(Path(__import__("slothy").__file__).resolve()), "target": str(Path(Target.__file__).resolve()), "allow_spills": False}
(HERE / "slothy-results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
