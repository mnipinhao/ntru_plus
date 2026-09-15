#!/usr/bin/env python3
"""Prepare isolated production, P29, and P30 full-KEM packages."""

import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
P29 = HERE.parent / "gt864-p29-direct-st3"
P29_BUILD = P29 / "build"
BUILD = HERE / "build"

subprocess.run([sys.executable, str(P29 / "prepare-integration.py")], check=True)
if BUILD.exists():
    shutil.rmtree(BUILD)
BUILD.mkdir()

for name in ("production", "p29"):
    shutil.copytree(P29_BUILD / name, BUILD / name)

shutil.copytree(P29_BUILD / "p29", BUILD / "p30")
shutil.copy2(HERE / "candidate-route.alloc.S", BUILD / "p30" / "gt864_p29_main_route.S")
print(BUILD)
