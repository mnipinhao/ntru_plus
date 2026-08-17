#!/usr/bin/env python3
"""Paired PMU/TSC gate for the progressive-P SoA keygen arithmetic island."""

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


def run_perf(binary: Path, iterations: int, gate: str, backend: str) -> dict:
    command = [
        "perf", "stat", "-x", ";", "-e", ",".join(EVENTS), "--",
        "taskset", "-c", "1", str(binary), str(iterations), gate, backend,
        "nocheck",
    ]
    process = subprocess.run(command, check=True, text=True, capture_output=True)
    match = re.search(r"tsc_per_call=([0-9.]+)", process.stdout)
    if match is None:
        raise RuntimeError(f"missing TSC result: {process.stdout}")
    counts: dict[str, float] = {}
    for line in process.stderr.splitlines():
        fields = line.split(";")
        if len(fields) < 3 or not fields[0].strip().isdigit():
            continue
        event = fields[2].strip().removesuffix("/u")
        counts[event] = int(fields[0].strip()) / iterations
    if "cpu_core/cycles" not in counts:
        raise RuntimeError(f"missing PMU counts: {process.stderr}")
    retry_f = re.search(r"retry_f=([0-9.]+)", process.stdout)
    retry_g = re.search(r"retry_g=([0-9.]+)", process.stdout)
    return {
        "tsc_per_call": float(match.group(1)),
        "per_call": counts,
        "retry_f_per_call": float(retry_f.group(1)) if retry_f else None,
        "retry_g_per_call": float(retry_g.group(1)) if retry_g else None,
    }


def bootstrap_median_ci(values: list[float], seed: int = 0x534F41) -> list[float]:
    rng = random.Random(seed)
    medians = []
    for _ in range(10000):
        medians.append(statistics.median(rng.choice(values) for _ in values))
    medians.sort()
    return [medians[249], medians[9749]]


def summarize(pairs: list[dict]) -> dict:
    metrics = ["cpu_core/cycles", "cpu_core/instructions",
               "cpu_core/mem_inst_retired.all_loads",
               "cpu_core/mem_inst_retired.all_stores"]
    result: dict[str, object] = {}
    for metric in metrics:
        deltas = [item["gt"]["per_call"][metric]
                  - item["official"]["per_call"][metric] for item in pairs]
        result[metric] = {
            "official_median": statistics.median(
                item["official"]["per_call"][metric] for item in pairs),
            "gt_median": statistics.median(
                item["gt"]["per_call"][metric] for item in pairs),
            "paired_delta_median": statistics.median(deltas),
            "paired_delta_bootstrap_95_ci": bootstrap_median_ci(deltas),
            "gt_wins": sum(value < 0 for value in deltas),
            "pairs": len(deltas),
        }
    deltas = [item["gt"]["tsc_per_call"] - item["official"]["tsc_per_call"]
              for item in pairs]
    result["tsc"] = {
        "official_median": statistics.median(
            item["official"]["tsc_per_call"] for item in pairs),
        "gt_median": statistics.median(item["gt"]["tsc_per_call"]
                                        for item in pairs),
        "paired_delta_median": statistics.median(deltas),
        "paired_delta_bootstrap_95_ci": bootstrap_median_ci(deltas),
        "gt_wins": sum(value < 0 for value in deltas),
        "pairs": len(deltas),
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", required=True, type=Path)
    parser.add_argument("--iterations", type=int, default=10000)
    parser.add_argument("--repeats", type=int, default=20)
    parser.add_argument("--gt-backend", default="gt32-soa",
                        choices=("gt32-soa", "gt32-half", "gt32-rr",
                                 "gt32-tf1", "gt32-sp1", "gt32-prod",
                                 "gt32-asm", "gt32-pack3", "gt32-p-j1",
                                 "gt32-p-j1-c", "candidate"))
    parser.add_argument("--control-backend", default="official",
                        choices=("official", "gt32-soa", "gt32-half",
                                 "gt32-prod", "gt32-tf1", "gt32-sp1",
                                 "gt32-pack3", "gt32-p-j1", "gt32-p-j1-c",
                                 "control"))
    parser.add_argument("--gates", default="fbi,consumer,island,pack,island-pack,full")
    parser.add_argument("--experiment", default="GT32-KEYGEN-P-Q24-001")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = {
        "schema": "ntruplus768-gt32-keygen-p-q24-pmu-v1",
        "experiment": args.experiment,
        "primary_metric": "cpu_core/cycles per two keygen edges",
        "secondary_metric": "TSC per two keygen edges",
        "iterations": args.iterations,
        "repeats": args.repeats,
        "gt_backend": args.gt_backend,
        "control_backend": args.control_backend,
        "placements": {},
    }
    for placement, binary in (("normal", args.binary),
                              ("reversed", args.reversed_binary)):
        placement_result = {
            "binary": str(binary),
            "sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
            "gates": {},
        }
        for gate in args.gates.split(","):
            pairs = []
            for repeat in range(args.repeats):
                records = {}
                order = ((args.control_backend, args.gt_backend)
                         if repeat % 2 == 0 else
                         (args.gt_backend, args.control_backend))
                for backend in order:
                    records["official" if backend == args.control_backend else "gt"] = \
                        run_perf(binary, args.iterations, gate, backend)
                pairs.append(records)
            placement_result["gates"][gate] = {
                "summary": summarize(pairs), "samples": pairs,
            }
        output["placements"][placement] = placement_result
    gates = args.gates.split(",")
    decision_gate = ("full" if "full" in gates else
                     "island-pack" if "island-pack" in gates else gates[-1])
    selected = [entry["gates"][decision_gate]["summary"]["cpu_core/cycles"]
                for entry in output["placements"].values()]
    output["decision_gate"] = decision_gate
    output["decision"] = (
        "performance-qualified" if all(
            item["paired_delta_bootstrap_95_ci"][1] < 0 for item in selected)
        else "inconclusive-or-stop"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    for placement, entry in output["placements"].items():
        print(placement)
        for gate, gate_data in entry["gates"].items():
            core = gate_data["summary"]["cpu_core/cycles"]
            tsc = gate_data["summary"]["tsc"]
            print(f"  {gate}: core_delta={core['paired_delta_median']:+.3f} "
                  f"CI={core['paired_delta_bootstrap_95_ci']} "
                  f"wins={core['gt_wins']}/{core['pairs']} "
                  f"tsc_delta={tsc['paired_delta_median']:+.3f}")
    print(f"decision={output['decision']}")


if __name__ == "__main__":
    main()
