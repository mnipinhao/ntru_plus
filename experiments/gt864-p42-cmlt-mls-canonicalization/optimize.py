#!/usr/bin/env python3
"""Run the proven P23 bounded fixed-allocation timing driver on P42."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
P23_DRIVER = HERE.parent / "gt864-p23-tobytes-global-dag" / "optimize.py"


def main() -> None:
    spec = importlib.util.spec_from_file_location("p42_p23_opt", P23_DRIVER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.HERE = HERE
    module.main()


if __name__ == "__main__":
    main()
