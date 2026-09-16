#!/usr/bin/env python3
"""Run the exact post-P42 GT production versus selected Official profiler."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "gt864-p37-official-profile" / "run_pi5.py"


def main() -> None:
    spec = importlib.util.spec_from_file_location("p42_profile_run_base", SOURCE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.HERE = HERE
    module.SYNC = HERE / "build/sync"
    module.REMOTE = "/home/pi/supercop-20260831/bench/pinhao/gt864-p42-profile2-20260916"
    module.main()


if __name__ == "__main__":
    main()
