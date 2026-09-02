#!/usr/bin/env python3
"""Bounded Slothy driver for four producer-pinned CF5-A consumers."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PARENT = ROOT.parent / "gt_friso2_two_block_boundary_slothy" / "driver_base.py"
SPEC = importlib.util.spec_from_file_location("cf5_consumer_driver", PARENT)
assert SPEC and SPEC.loader
driver = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(driver)

CASES = {"t0c1": 309, "t0c2": 309, "t1c1": 279, "t1c2": 279}


def take_case() -> str:
    if "--case" not in sys.argv:
        raise SystemExit("optimize_consumers.py requires --case t0c1|t0c2|t1c1|t1c2")
    pos = sys.argv.index("--case")
    case = sys.argv[pos + 1]
    del sys.argv[pos:pos + 2]
    if case not in CASES:
        raise SystemExit(f"unknown case {case!r}")
    return case


if __name__ == "__main__":
    case = take_case()
    driver.START = f"gt864_cf5_pair_{case}_slothy_start"
    driver.END = f"gt864_cf5_pair_{case}_slothy_end"
    driver.VECTOR_OUTPUTS = [f"out{i}" for i in range(18)]
    driver.GPR_OUTPUTS = ["x3"]
    driver.OUTPUTS = driver.VECTOR_OUTPUTS + driver.GPR_OUTPUTS
    driver.RESERVED = ["x0", "x1", "x2", *[f"x{i}" for i in range(4, 31)],
                       "sp", "v13", "v14", "v15"]
    driver.EXPECTED_INSTRUCTIONS = CASES[case]
    defaults = (
        ("--input", "gt864_cf5_fixed_livein_consumers.sym.S"),
        ("--alloc-output", f"build/{case}.n1.alloc.S"),
        ("--output", f"build/{case}.n1.opt.S"),
    )
    for option, value in defaults:
        if option not in sys.argv:
            sys.argv.extend([option, value])
    driver.main()
