#!/usr/bin/env python3
"""Allocate the P6-D3 full-ToBytes stage regions without spills."""

from __future__ import annotations

import json
import logging
import re
import subprocess
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


def pair1_gprs() -> list[int]:
    text = (HERE / "producer.pair1.alloc.S").read_text()
    body = text.split("gt864_p6d_pair1_start:", 1)[1].split("gt864_p6d_pair1_end:", 1)[0]
    found = {}
    for reg, off in re.findall(r"\bstr x(\d+), \[sp, #(\d+)\]", body):
        off = int(off)
        if 208 <= off < 432: found[(off-208)//8] = int(reg)
    assert sorted(found) == list(range(28)), found
    result = [found[i] for i in range(28)]
    (HERE / "pair1-state-map.json").write_text(json.dumps({"gpr_slots": result}, indent=2) + "\n")
    return result


def allocate(label: str) -> dict[str, object]:
    log_path = HERE / f"slothy-{label}.log"
    out_path = HERE / f"d3.{label}.alloc.S"
    logger = logging.getLogger("p6d3-" + label); logger.handlers.clear(); logger.setLevel(logging.INFO)
    logger.addHandler(logging.FileHandler(log_path, mode="w"))
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
    s.load_source_from_file(str(HERE / "d3-regions.sym.S"))
    try:
        s.optimize(start=label + "_slothy_start", end=label + "_slothy_end")
    except (SlothyException, Exception) as exc:
        status, error = "infeasible", type(exc).__name__ + ": " + str(exc)
    else:
        s.write_source_to_file(str(out_path)); status, error = "allocated", None
    log = log_path.read_text() if log_path.exists() else ""
    return {"status": status, "error": error, "optimal": "OPTIMAL" in log,
            "infeasible": "INFEASIBLE" in log, "spill_or_reload": bool(re.search(r"\b(spill|reload)\b", log, re.I)),
            "output": str(out_path) if out_path.exists() else None, "log": str(log_path)}


gprs = pair1_gprs()
subprocess.run(["python3", str(HERE / "generate_d3_regions.py")], check=True)
labels = ["gt864_p6d3_route_a", "gt864_p6d3_pack_a", "gt864_p6d3_route_b"] + [f"gt864_p6d3_row{i}" for i in range(9)]
result = {label: allocate(label) for label in labels}
result.update({"pair1_gpr_slots": gprs, "slothy_source": str(Path(__import__("slothy").__file__).resolve()),
               "target": str(Path(Target.__file__).resolve()), "allow_spills": False})
(HERE / "d3-slothy-results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
