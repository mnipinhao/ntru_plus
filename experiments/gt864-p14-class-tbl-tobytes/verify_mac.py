#!/usr/bin/env python3
import subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
BUILD=HERE/"build"
subprocess.run(["python3",str(HERE/"generate.py")],check=True)
subprocess.run(["clang","-O3","-march=armv8-a+simd","-I",str(HERE),"-I",str(BUILD),
                str(BUILD/"p14_tobytes_full.c"),str(BUILD/"p14_tobytes_small.c"),str(HERE/"test.c"),
                "-o",str(BUILD/"test")],check=True)
subprocess.run([str(BUILD/"test")],check=True)
print("p14_mac_gate=pass")
