#!/usr/bin/env python3
"""Prepare an exact-commit post-P42 production profiler bundle."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "gt864-p37-official-profile" / "prepare.py"


def main() -> None:
    spec = importlib.util.spec_from_file_location("p42_profile_prepare_base", SOURCE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.HERE = HERE
    module.SYNC = HERE / "build/sync"
    module.EXPECTED_REVISION = "34d2c758"
    module.EXPERIMENT = "GT864-P42-PRODUCTION-PROFILE-20260916"
    module.main()


if __name__ == "__main__":
    main()
