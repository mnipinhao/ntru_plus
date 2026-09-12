#!/usr/bin/env python3
"""Build and execute the isolated P11 candidate on Apple arm64."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
BUILD = P / "build"

subprocess.run([sys.executable, str(P / "prepare.py")], check=True)
source = BUILD / "candidate"
mac_source = BUILD / "mac-source"
shutil.copytree(source, mac_source, dirs_exist_ok=True)
baseinv = mac_source / "gt864_native_baseinv_num.S"
if "#define binv_num_pair" not in baseinv.read_text():
    baseinv.write_text("#ifdef __APPLE__\n#define binv_num_pair _binv_num_pair\n#endif\n" + baseinv.read_text())
mac = BUILD / "mac"
subprocess.run([sys.executable, str(ROOT / "experiments/gt864-native-asm/verify-production-mac.py"), str(mac_source), str(mac)], check=True)
objects = [str(path) for path in mac.glob("*.o")]
binary = mac / "p11-test"
subprocess.run([
    "clang", "-O3", "-I" + str(mac_source), str(P / "test.c"), str(BUILD / "probe.S"),
    str(mac_source / "randombytes.c"), *objects, "-o", str(binary),
], check=True)
subprocess.run([str(binary)], check=True)
report = {"status": "pass", "cases": 4096, "exact_alias": "pass", "aapcs_scratch_wipe": "pass"}
(P / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
