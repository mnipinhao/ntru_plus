#!/usr/bin/env python3
"""Use the P23 fixed-allocation Cortex-A76 timing driver for P46 Full."""
from __future__ import annotations
import importlib.util,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent; DRIVER=HERE.parent/"gt864-p23-tobytes-global-dag/optimize.py"
def main():
    spec=importlib.util.spec_from_file_location("p46_p23_opt",DRIVER);assert spec and spec.loader
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    module.HERE=HERE;module.main()
if __name__=="__main__":main()
