#!/usr/bin/env python3
"""K3-B paired PMU/TSC gate for Official BaseInv+BM vs J1+R1-U."""

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
    return {"tsc_per_call": float(match.group(1)), "per_call": counts}


def bootstrap_median_ci(values: list[float], seed: int = 0x4B3342) -> list[float]:
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
    tsc_deltas = [item["gt"]["tsc_per_call"]
                  - item["official"]["tsc_per_call"] for item in pairs]
    result["tsc"] = {
        "official_median": statistics.median(
            item["official"]["tsc_per_call"] for item in pairs),
        "gt_median": statistics.median(item["gt"]["tsc_per_call"]
                                        for item in pairs),
        "paired_delta_median": statistics.median(tsc_deltas),
        "paired_delta_bootstrap_95_ci": bootstrap_median_ci(tsc_deltas),
        "gt_wins": sum(value < 0 for value in tsc_deltas),
        "pairs": len(tsc_deltas),
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", required=True, type=Path)
    parser.add_argument("--iterations", type=int, default=10000)
    parser.add_argument("--repeats", type=int, default=20)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = {
        "schema": "ntruplus768-gt32-keygen-j1-k3b-pmu-v1",
        "experiment": "GT32-KEYGEN-BASEINV-J1-K3B-001",
        "primary_metric": "cpu_core/cycles per two keygen edges",
        "secondary_metric": "TSC per two keygen edges",
        "iterations": args.iterations,
        "repeats": args.repeats,
        "placements": {},
    }
    for placement, binary in (("normal", args.binary),
                              ("reversed", args.reversed_binary)):
        placement_result = {
            "binary": str(binary),
            "sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
            "gates": {},
        }
        for gate in ("a0", "consumer", "a1"):
            pairs = []
            for repeat in range(args.repeats):
                records = {}
                order = (("official", "gt32-j1-r1u") if repeat % 2 == 0
                         else ("gt32-j1-r1u", "official"))
                for backend in order:
                    key = "official" if backend == "official" else "gt"
                    records[key] = run_perf(binary, args.iterations, gate,
                                            backend)
                pairs.append(records)
            placement_result["gates"][gate] = {
                "summary": summarize(pairs), "samples": pairs,
            }
        output["placements"][placement] = placement_result
    a1 = [entry["gates"]["a1"]["summary"]["cpu_core/cycles"]
          for entry in output["placements"].values()]
    output["decision"] = (
        "continue-k3c" if all(item["paired_delta_median"] <= -50
                               and item["paired_delta_bootstrap_95_ci"][1] < 0
                               for item in a1)
        else "stop-before-k3c"
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
