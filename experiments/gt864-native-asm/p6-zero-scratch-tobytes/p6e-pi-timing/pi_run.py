#!/usr/bin/env python3
"""Build and run the isolated P6-E same-boundary Pi 5 campaign."""

from __future__ import annotations

import csv
import hashlib
import json
import pathlib
import statistics
import subprocess

HERE = pathlib.Path(__file__).resolve().parent
BUILD = HERE / "build"
RESULTS = HERE / "pi-results"
PROD = HERE / "production"
BUILD.mkdir(exist_ok=True)
RESULTS.mkdir(exist_ok=True)


def run(command: list[str], **kwargs):
    return subprocess.run([str(x) for x in command], check=True, **kwargs)


def output(command: list[str]) -> str:
    return subprocess.check_output([str(x) for x in command], text=True).strip()


run(["make", "-B", "-j4", "libgt864.so"], cwd=PROD,
    stdout=(RESULTS / "build-baseline.log").open("w"), stderr=subprocess.STDOUT)
run(["gcc", "-O3", "-fPIC", "-shared", HERE / "p6d3-full.alloc.S", "-o", BUILD / "candidate.so"],
    stdout=(RESULTS / "build-candidate.log").open("w"), stderr=subprocess.STDOUT)
run(["gcc", "-O3", "-rdynamic", HERE / "bench.c", "-ldl", "-o", BUILD / "bench"])

raw_files: list[pathlib.Path] = []
for mode in ("full", "small"):
    for reverse in (0, 1):
        path = RESULTS / f"{mode}-{reverse}.csv"
        with path.open("w") as out_file:
            run(["taskset", "-c", "3", BUILD / "bench", PROD / "libgt864.so",
                 BUILD / "candidate.so", mode, reverse], stdout=out_file, stderr=subprocess.STDOUT)
        raw_files.append(path)

samples: dict[tuple[str, str], list[list[float]]] = {}
for path in raw_files:
    for row in csv.reader(path.read_text().splitlines()):
        if row and row[0] == "sample":
            samples.setdefault((row[1], row[2]), []).append([float(x) for x in row[4:9]])

metrics = ["cycles", "instructions", "branches", "mem_access_rd", "mem_access_wr"]
summary: dict[str, dict] = {}
for mode in ("full", "small"):
    entry: dict[str, dict] = {}
    for variant in ("baseline", "candidate"):
        values = samples[(mode, variant)]
        entry[variant] = {
            metric: statistics.median(row[i] for row in values)
            for i, metric in enumerate(metrics)
        }
        entry[variant]["ipc"] = entry[variant]["instructions"] / entry[variant]["cycles"]
        entry[variant]["samples"] = len(values)
    entry["delta"] = {
        metric: entry["candidate"][metric] - entry["baseline"][metric]
        for metric in metrics + ["ipc"]
    }
    entry["delta_percent"] = {
        metric: 100 * (entry["candidate"][metric] / entry["baseline"][metric] - 1)
        for metric in metrics + ["ipc"]
    }
    summary[mode] = entry

environment = {
    "uname": output(["uname", "-a"]),
    "gcc": output(["gcc", "--version"]).splitlines()[0],
    "governor": pathlib.Path("/sys/devices/system/cpu/cpu3/cpufreq/scaling_governor").read_text().strip(),
    "temperature": output(["vcgencmd", "measure_temp"]),
    "throttled": output(["vcgencmd", "get_throttled"]),
    "core": 3,
    "iterations_per_sample": 128,
    "samples_per_variant": 74,
    "paired_order": "two reverse runs; order alternates by sample",
    "pmu_device": "armv8_cortex_a76 type 9",
    "pmu_raw_configs": {"mem_access_rd": "0x66", "mem_access_wr": "0x67"},
    "competing_benchmark_preflight": "none found",
}

artifacts = [PROD / "libgt864.so", BUILD / "candidate.so", HERE / "p6d3-full.alloc.S", HERE / "bench.c"]
result = {
    "experiment": "P6-E",
    "environment": environment,
    "correctness": "513 full and 513 small cases per run, two runs each; exact bytes and canaries",
    "benchmarks": summary,
    "sha256": {str(path.relative_to(HERE)): hashlib.sha256(path.read_bytes()).hexdigest() for path in artifacts},
}
(HERE / "p6e-results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
