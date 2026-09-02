#!/usr/bin/env python3
"""Bounded Slothy driver for the frozen CF5-A NTT16 producer."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PARENT = ROOT.parent / "gt_forward_full_register_pass2_dag" / "optimize.py"
SPEC = importlib.util.spec_from_file_location("cf5_producer_driver", PARENT)
assert SPEC and SPEC.loader
driver = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(driver)

driver.START = "gt864_cf5_ntt16_producer_slothy_start"
driver.END = "gt864_cf5_ntt16_producer_slothy_end"
driver.VECTOR_OUTPUTS = ([f"lo_f{i}_raw" for i in range(9)]
                         + [f"hi_f{i}_raw" for i in range(9)])
driver.GPR_OUTPUTS = ["x0", "x1", "x2", "x3"]
driver.OUTPUTS = driver.VECTOR_OUTPUTS + driver.GPR_OUTPUTS
driver.RESERVED = [*[f"x{i}" for i in range(5, 31)], "sp", "v13", "v14", "v15"]
driver.EXPECTED_INSTRUCTIONS = 345

if __name__ == "__main__":
    defaults = (
        ("--input", "gt864_cf5_ntt16_producer.sym.S"),
        ("--alloc-output", "build/producer.n1.alloc.S"),
        ("--output", "build/producer.n1.opt.S"),
    )
    for option, value in defaults:
        if option not in sys.argv:
            sys.argv.extend([option, value])
    driver.main()
