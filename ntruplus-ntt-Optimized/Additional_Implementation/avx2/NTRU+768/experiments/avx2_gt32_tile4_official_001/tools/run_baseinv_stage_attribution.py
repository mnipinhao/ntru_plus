#!/usr/bin/env python3
"""Paired normal/reversed PMU attribution for P-J1 BaseInv stages."""

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
    counts = {}
    tsc = None
    # Run each programmable event alone.  Four events together multiplex on
    # this host (about 92% enabled), and scaled counts are too noisy for a
    # stage-level instruction/load/store attribution.
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
            if len(fields) < 3 or not fields[0].strip().isdigit():
                continue
            counts[fields[2].strip().removesuffix("/u")] = (
                int(fields[0].strip()) / iterations)
    return {"tsc": tsc, "pmu": counts}


def ci(values: list[float], seed: int) -> list[float]:
    rng = random.Random(seed)
    samples = sorted(statistics.median(rng.choice(values) for _ in values)
                     for _ in range(10000))
    return [samples[249], samples[9749]]


def summarize(pairs: list[dict]) -> dict:
    result = {}
    metrics = ("cpu_core/cycles", "cpu_core/instructions",
               "cpu_core/mem_inst_retired.all_loads",
               "cpu_core/mem_inst_retired.all_stores")
    for index, metric in enumerate(metrics):
        deltas = [p["candidate"]["pmu"][metric] -
                  p["control"]["pmu"][metric] for p in pairs]
        result[metric] = {"delta_median": statistics.median(deltas),
                          "bootstrap_95_ci": ci(deltas, 0xBACE + index),
                          "negative": sum(x < 0 for x in deltas),
                          "pairs": len(deltas)}
    deltas = [p["candidate"]["tsc"] - p["control"]["tsc"]
              for p in pairs]
    result["tsc"] = {"delta_median": statistics.median(deltas),
                     "bootstrap_95_ci": ci(deltas, 0xBACE + 4),
                     "negative": sum(x < 0 for x in deltas),
                     "pairs": len(deltas)}
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", required=True, type=Path)
    parser.add_argument("--iterations", type=int, default=100000)
    parser.add_argument("--repeats", type=int, default=20)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = {"schema": "gt32-baseinv-stage-attribution-v1",
              "experiment": "GT32-KEYGEN-BASEINV-STAGE-PMU-001",
              "iterations": args.iterations, "repeats": args.repeats,
              "method": "candidate minus matched control",
              "placements": {}}
    for placement, binary in (("normal", args.binary),
                              ("reversed", args.reversed_binary)):
        entry = {"binary": str(binary),
                 "sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
                 "gates": {}}
        for gate in ("prepare", "batch", "finish", "full"):
            pairs = []
            for repeat in range(args.repeats):
                order = ("control", "candidate") if repeat % 2 == 0 else (
                    "candidate", "control")
                record = {}
                for backend in order:
                    record[backend] = run(binary, args.iterations, gate,
                                          backend)
                pairs.append(record)
            entry["gates"][gate] = {"summary": summarize(pairs),
                                     "samples": pairs}
        output["placements"][placement] = entry
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    for placement, entry in output["placements"].items():
        print(placement)
        for gate, gate_data in entry["gates"].items():
            core = gate_data["summary"]["cpu_core/cycles"]
            insn = gate_data["summary"]["cpu_core/instructions"]
            loads = gate_data["summary"]["cpu_core/mem_inst_retired.all_loads"]
            stores = gate_data["summary"]["cpu_core/mem_inst_retired.all_stores"]
            tsc = gate_data["summary"]["tsc"]
            print(f"  {gate}: core={core['delta_median']:+.3f} "
                  f"insn={insn['delta_median']:+.1f} "
                  f"loads={loads['delta_median']:+.1f} "
                  f"stores={stores['delta_median']:+.1f} "
                  f"tsc={tsc['delta_median']:+.3f}")


if __name__ == "__main__":
    main()
