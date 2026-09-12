#!/usr/bin/env python3
"""Build, validate, and measure the isolated P21 bundle on the Pi 5."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
GT = HERE / "gt-source"
BUILD = HERE / "build"
BUILD.mkdir(exist_ok=True)


def run(args: list[str], cwd: Path | None = None, capture: bool = False) -> str:
    result = subprocess.run(args, cwd=cwd, check=True, text=True,
                            stdout=subprocess.PIPE if capture else None,
                            stderr=subprocess.STDOUT if capture else None)
    return result.stdout or ""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


manifest = json.loads((HERE / "p21-source-manifest.json").read_text())
for name, expected in manifest["files"].items():
    path = HERE / name
    if not path.is_file() or sha256(path) != expected:
        raise RuntimeError(f"source manifest mismatch: {name}")

if subprocess.run(["sh", "-c", "ps -eo args | grep '[d]o-part'"],
                  stdout=subprocess.DEVNULL).returncode == 0:
    raise RuntimeError("SUPERCOP do-part active")

before_temp = run(["vcgencmd", "measure_temp"], capture=True).strip()
before_throttle = run(["vcgencmd", "get_throttled"], capture=True).strip()
governor = Path("/sys/devices/system/cpu/cpu3/cpufreq/scaling_governor").read_text().strip()

run(["make", "-j4", "check"], cwd=GT)
kat = GT / "PQCkemKAT_2624.rsp"
kat_digest = sha256(kat)
if kat_digest != "0c91227497480095a43403852b3a46e423356cdd00242d654001c3c1566de61c":
    raise RuntimeError(f"unexpected KAT digest {kat_digest}")

cflags = ["-O3", "-std=c11", "-march=armv8-a+simd", "-D_DEFAULT_SOURCE", "-fPIC"]
for source in ("gt864_native_inverse16_lazy_nostore.S",
               "gt864_native_inverse_tail_lazy_nostore.S"):
    run(["cc", *cflags, "-I", str(GT), "-x", "assembler-with-cpp", "-c",
         source, "-o", str(BUILD / source.replace(".S", ".o"))], cwd=HERE)
run(["cc", "-shared",
     str(BUILD / "gt864_native_inverse16_lazy_nostore.o"),
     str(BUILD / "gt864_native_inverse_tail_lazy_nostore.o"),
     "-o", str(BUILD / "diagnostic.so")])
run(["cc", *cflags, "-I", str(GT), "-rdynamic", "stage-bench.c", "-ldl",
     "-o", str(BUILD / "stage-bench")], cwd=HERE)

logs = []
for process in range(6):
    path = BUILD / f"stage-{process}.csv"
    with path.open("w") as output:
        subprocess.run(["taskset", "-c", "3", str(BUILD / "stage-bench"),
                        str(GT / "libgt864.so"), str(BUILD / "diagnostic.so"),
                        str(process & 1)], check=True, stdout=output)
    logs.append(path)

summary_text = run(["python3", "summarize.py", *map(str, logs)], cwd=HERE, capture=True)
(HERE / "p21-results.json").write_text(summary_text)

after_temp = run(["vcgencmd", "measure_temp"], capture=True).strip()
after_throttle = run(["vcgencmd", "get_throttled"], capture=True).strip()
environment = {
    "experiment": "GT864-P21-INVERSE-DECOMPOSITION-20260912",
    "revision": manifest["revision"],
    "uname": run(["uname", "-a"], capture=True).strip(),
    "gcc": run(["cc", "--version"], capture=True).splitlines()[0],
    "governor": governor,
    "cpu_core": 3,
    "processes": 6,
    "samples_per_process_per_boundary": 43,
    "iterations_per_sample": 64,
    "temperature_before": before_temp,
    "temperature_after": after_temp,
    "throttled_before": before_throttle,
    "throttled_after": after_throttle,
    "bundle_manifest_hash": hashlib.sha256("".join(
        f"{k}:{v}\n" for k, v in sorted(manifest["files"].items())
    ).encode()).hexdigest(),
    "gt_library_sha256": sha256(GT / "libgt864.so"),
    "kat_sha256": kat_digest,
    "diagnostic_sha256": sha256(BUILD / "diagnostic.so"),
    "harness_sha256": sha256(BUILD / "stage-bench"),
    "raw_logs": [path.name for path in logs],
}
(HERE / "environment.json").write_text(json.dumps(environment, indent=2) + "\n")
if before_throttle != "throttled=0x0" or after_throttle != "throttled=0x0":
    raise RuntimeError("Pi 5 throttled during P21")
print(summary_text)
print(json.dumps(environment, indent=2))
