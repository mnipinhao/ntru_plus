#!/usr/bin/env python3
"""Build, validate, and paired-PMU benchmark P3-B on Raspberry Pi 5."""

import csv
import hashlib
import json
import pathlib
import re
import statistics
import subprocess


P = pathlib.Path(__file__).resolve().parent
BUILD = P / "build"
RESULTS = P / "pi-results"
RESULTS.mkdir(exist_ok=True)


def run(command, *, cwd=None, log=None):
    stream = None if log is None else log.open("a")
    try:
        subprocess.run(command, cwd=cwd, check=True, stdout=stream,
                       stderr=subprocess.STDOUT if stream else None)
    finally:
        if stream:
            stream.close()


processes = subprocess.check_output(["ps", "-eo", "args"], text=True)
if re.search(r"(?:^|/)do-part(?: |$)", processes, re.M):
    raise RuntimeError("SUPERCOP benchmark is active; refusing a competing PMU run")

for name in ("p3a", "p3b"):
    package = BUILD / name
    build_log = RESULTS / f"build-{name}.log"
    build_log.write_text("")
    run(["make", "manifest-check"], cwd=package, log=build_log)
    run(["make", "-B", "-j4", "libgt864.so", "test_kem", "PQCgenKAT_kem"], cwd=package, log=build_log)
    run(["./test_kem"], cwd=package, log=RESULTS / f"test-{name}.log")
    run(["./PQCgenKAT_kem"], cwd=package, log=RESULTS / f"kat-{name}.log")

run(["gcc", "-O3", "-rdynamic", str(P / "pi-bench.c"), "-ldl", "-o", str(RESULTS / "pi-bench")])
rows = []
correctness = []
for repetition in range(6):
    output = subprocess.check_output([
        "taskset", "-c", "3", str(RESULTS / "pi-bench"),
        str(BUILD / "p3a/libgt864.so"), str(BUILD / "p3b/libgt864.so"),
        str(repetition % 2),
    ], text=True)
    (RESULTS / f"paired-{repetition}.csv").write_text(output)
    for row in csv.reader(output.splitlines()):
        if row and row[0] == "correctness=pass valid=24 tampered=24 inverse_exact=256 alias=256":
            correctness.append(row[0])
        if row and row[0] in ("full", "component"):
            rows.append((row[0], row[1], row[2], *map(float, row[3:])))

summary = {}
for boundary, operation in (("component", "inverse"), ("full", "keygen"),
                            ("full", "encaps"), ("full", "decaps")):
    summary[operation] = {}
    for implementation in ("p3a", "p3b"):
        values = [row[3:] for row in rows if row[:3] == (boundary, operation, implementation)]
        summary[operation][implementation] = {
            metric: statistics.median(value[index] for value in values)
            for index, metric in enumerate(("cycles", "instructions", "branches"))
        }
    summary[operation]["delta"] = {
        metric: summary[operation]["p3b"][metric] - summary[operation]["p3a"][metric]
        for metric in ("cycles", "instructions", "branches")
    }
    summary[operation]["cycle_delta_percent"] = 100 * (
        summary[operation]["p3b"]["cycles"] / summary[operation]["p3a"]["cycles"] - 1
    )

result = {
    "baseline": "current GT production P3-A",
    "candidate": "P3-B producer-side packed centering",
    "correctness_repetitions": len(correctness),
    "summary": summary,
    "environment": {
        "uname": subprocess.check_output(["uname", "-a"], text=True).strip(),
        "gcc": subprocess.check_output(["gcc", "--version"], text=True).splitlines()[0],
        "governor": pathlib.Path("/sys/devices/system/cpu/cpu3/cpufreq/scaling_governor").read_text().strip(),
        "temperature": subprocess.check_output(["vcgencmd", "measure_temp"], text=True).strip(),
        "supercop_reference_root": "/home/pi/supercop-20260831",
    },
    "hashes": {
        name: hashlib.sha256((BUILD / name / "libgt864.so").read_bytes()).hexdigest()
        for name in ("p3a", "p3b")
    },
}
(P / "pi-results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
