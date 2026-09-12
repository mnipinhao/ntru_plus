#!/usr/bin/env python3
import subprocess
from pathlib import Path

here=Path(__file__).resolve().parent
build=here/"build"
subprocess.run(["python3",str(here/"generate.py")],check=True)
subprocess.run(["clang","-O3","-march=armv8-a+simd","-I",str(here),"-I",str(build),
                str(build/"p18_tobytes_full.S"),str(build/"p18_tobytes_small.S"),
                str(here/"test.c"),"-o",str(build/"test")],check=True)
subprocess.run([str(build/"test")],check=True)
print("p18_mac_gate=pass")
