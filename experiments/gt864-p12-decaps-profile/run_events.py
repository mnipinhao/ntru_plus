#!/usr/bin/env python3
"""Measure retired instructions and branches for every instrumented call site."""

from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"
RAW = HERE / "raw"

subprocess.run([
    "gcc", "-O3", "-std=c11", "-march=armv8-a+simd", "-D_DEFAULT_SOURCE",
    "-rdynamic", HERE / "profile_event_harness.c", "-ldl", "-o", BUILD / "profile_event_harness",
], check=True)

for metric in ("instructions", "branches"):
    for process in range(6):
        order = ("official", "gt") if process % 2 == 0 else ("gt", "official")
        for label in order:
            destination = RAW / f"event-{metric}-{label}-{process}.csv"
            plain = BUILD / f"{label}.so"
            profiled = BUILD / f"{label}-prof.so"
            with destination.open("w") as log:
                subprocess.run([
                    "taskset", "-c", "3", BUILD / "profile_event_harness",
                    label, plain, profiled, metric,
                ], check=True, stdout=log, stderr=subprocess.STDOUT, text=True)
        print(f"completed {metric} process {process + 1}/6", flush=True)
