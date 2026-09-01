#!/usr/bin/env python3
"""Remote Slothy driver for the 601-instruction M5S-A candidate."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

PARENT_DRIVER = (Path(__file__).resolve().parent.parent /
                 "gt_forward_full_register_pass2_dag" / "optimize.py")
SPEC = importlib.util.spec_from_file_location("m5r_optimize", PARENT_DRIVER)
assert SPEC is not None and SPEC.loader is not None
driver = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(driver)

driver.START = "gt864_forward_one_bank_paired_twist_loads_slothy_start"
driver.END = "gt864_forward_one_bank_paired_twist_loads_slothy_end"
driver.GPR_OUTPUTS = ["x0", "x1", "x2", "x3"]
driver.OUTPUTS = driver.VECTOR_OUTPUTS + driver.GPR_OUTPUTS
driver.RESERVED = [*[f"x{i}" for i in range(5, 31)], "sp",
                   "v13", "v14", "v15", "v16", "v17"]
driver.EXPECTED_INSTRUCTIONS = 601


if __name__ == "__main__":
    defaults = (
        ("--input", "gt864_forward_one_bank_paired_twist_loads.sym.S"),
        ("--alloc-output", "build/gt864_forward_one_bank_paired_twist_loads.n1.alloc.S"),
        ("--output", "build/gt864_forward_one_bank_paired_twist_loads.n1.opt.S"),
    )
    for option, value in defaults:
        if option not in sys.argv:
            sys.argv.extend([option, value])
    driver.main()
