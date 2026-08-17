#!/usr/bin/env python3
"""Paired PMU gate for hand-ASM P-J1 batch inversion versus current C."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import statistics
import subprocess
from pathlib import Path

EVENTS = (
    "cpu_core/cycles/",
    "cpu_core/instructions/",
    "cpu_core/mem_inst_retired.all_loads/",
    "cpu_core/mem_inst_retired.all_stores/",
)


def run(binary: Path, iterations: int, gate: str, backend: str) -> dict:
    counts: dict[str, float] = {}
    tsc = None
    for event in EVENTS:
        command = ["perf", "stat", "-x", ";", "-e", event, "--",
                   "taskset", "-c", "1", str(binary), str(iterations), gate,
                   backend, "nocheck"]
        process = subprocess.run(command, check=True, text=True,
                                 capture_output=True)
        match = re.search(r"tsc_per_call=([0-9.]+)", process.stdout)
        if match is None:
            raise RuntimeError(f"missing TSC result: {process.stdout}")
        if tsc is None:
            tsc = float(match.group(1))
        for line in process.stderr.splitlines():
            fields = line.split(";")
            if len(fields) >= 3 and fields[0].strip().isdigit():
                counts[fields[2].strip().removesuffix("/u")] = (
                    int(fields[0].strip()) / iterations)
    return {"tsc": tsc, "pmu": counts}


def bootstrap_ci(values: list[float], seed: int) -> list[float]:
    rng = random.Random(seed)
    samples = sorted(statistics.median(rng.choice(values) for _ in values)
                     for _ in range(10000))
    return [samples[249], samples[9749]]


def summarize(pairs: list[dict], baseline_backend: str,
              asm_backend: str) -> dict:
    result = {}
    metrics = ("cpu_core/cycles", "cpu_core/instructions",
               "cpu_core/mem_inst_retired.all_loads",
               "cpu_core/mem_inst_retired.all_stores")
    for index, metric in enumerate(metrics):
        deltas = [p[asm_backend]["pmu"][metric] -
                  p[baseline_backend]["pmu"][metric] for p in pairs]
        result[metric] = {"delta_median": statistics.median(deltas),
                          "bootstrap_95_ci": bootstrap_ci(
                              deltas, 0xB471 + index),
                          "negative": sum(value < 0 for value in deltas),
                          "pairs": len(deltas)}
    deltas = [p[asm_backend]["tsc"] - p[baseline_backend]["tsc"]
              for p in pairs]
    result["tsc"] = {"delta_median": statistics.median(deltas),
                     "bootstrap_95_ci": bootstrap_ci(deltas, 0xB475),
                     "negative": sum(value < 0 for value in deltas),
                     "pairs": len(deltas)}
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", required=True, type=Path)
    parser.add_argument("--iterations", type=int, default=100000)
    parser.add_argument("--repeats", type=int, default=20)
    parser.add_argument("--asm-backend", default="asm",
                        choices=("asm", "tree", "split"))
    parser.add_argument("--baseline-backend", default="candidate",
                        choices=("candidate", "split"))
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = {"schema": "gt32-p-j1-batch-asm-v1",
              "experiment": "GT32-KEYGEN-P-J1-BATCH-ASM-001",
              "iterations": args.iterations, "repeats": args.repeats,
              "method": (f"{args.asm_backend} minus "
                         f"{args.baseline_backend}"),
              "placements": {}}
    for placement, binary in (("normal", args.binary),
                              ("reversed", args.reversed_binary)):
        entry = {"binary": str(binary),
                 "sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
                 "gates": {}}
        for gate in ("batch", "full"):
            pairs = []
            for repeat in range(args.repeats):
                order = (args.baseline_backend, args.asm_backend) \
                    if repeat % 2 == 0 else (args.asm_backend,
                                              args.baseline_backend)
                record = {}
                for backend in order:
                    record[backend] = run(binary, args.iterations, gate,
                                          backend)
                pairs.append(record)
            entry["gates"][gate] = {"summary": summarize(
                                         pairs, args.baseline_backend,
                                         args.asm_backend),
                                     "samples": pairs}
        output["placements"][placement] = entry
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    for placement, entry in output["placements"].items():
        print(placement)
        for gate, gate_data in entry["gates"].items():
            summary = gate_data["summary"]
            print(f"  {gate}: "
                  f"core={summary['cpu_core/cycles']['delta_median']:+.3f} "
                  f"insn={summary['cpu_core/instructions']['delta_median']:+.1f} "
                  f"loads={summary['cpu_core/mem_inst_retired.all_loads']['delta_median']:+.1f} "
                  f"stores={summary['cpu_core/mem_inst_retired.all_stores']['delta_median']:+.1f} "
                  f"tsc={summary['tsc']['delta_median']:+.3f}")


if __name__ == "__main__":
    main()
