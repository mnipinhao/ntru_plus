#!/usr/bin/env python3
"""Core-cycle gate for bounded S4->S5 wavefront schedules."""

from __future__ import annotations

import argparse
import json
import random
import re
import statistics
import subprocess
from pathlib import Path


def measure(binary: Path, iterations: int, gate: str, backend: str) -> dict:
    process = subprocess.run([
        "perf", "stat", "-x", ";", "-e",
        "cpu_core/cycles/,cpu_core/instructions/", "--",
        str(binary), str(iterations), gate, backend,
    ], check=True, text=True, capture_output=True)
    match = re.search(rf"PMU,{gate},{backend},{iterations},([0-9.]+)",
                      process.stdout)
    if match is None:
        raise RuntimeError(f"missing TSC output: {process.stdout}")
    counts = {}
    for line in process.stderr.splitlines():
        fields = line.split(";")
        if len(fields) >= 3 and fields[0].strip().isdigit():
            counts[fields[2].strip().removesuffix("/u")] = (
                int(fields[0].strip()) / iterations)
    return {"tsc": float(match.group(1)), "counts": counts}


def ci(values: list[float]) -> list[float]:
    rng = random.Random(0x53453435)
    medians = sorted(statistics.median(rng.choice(values) for _ in values)
                     for _ in range(10000))
    return [medians[249], medians[9749]]


def summary(pairs: list[dict], metric: str) -> dict:
    if metric == "tsc":
        delta = [p["candidate"]["tsc"] - p["baseline"]["tsc"]
                 for p in pairs]
    else:
        delta = [p["candidate"]["counts"][metric]
                 - p["baseline"]["counts"][metric] for p in pairs]
    return {"paired_delta_median": statistics.median(delta),
            "bootstrap_95_ci": ci(delta),
            "candidate_wins": sum(x < 0 for x in delta),
            "pairs": len(delta)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--iterations", type=int, default=10000)
    parser.add_argument("--repeats", type=int, default=20)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = {"schema": "ntruplus768-gt32-s45-wavefront-pmu-v1",
              "experiment": "GT32-N5-I1-SUPEROPT-001",
              "placement": "normal-first-necessary-gate",
              "iterations": args.iterations, "repeats": args.repeats,
              "gates": {}}
    for gate in ("forward_core_w1", "forward_core_w2",
                 "two_forward_bm_i1_t9_w1", "two_forward_bm_i1_t9_w2"):
        pairs = []
        for repeat in range(args.repeats):
            pair = {}
            order = (("baseline", "candidate") if repeat % 2 == 0
                     else ("candidate", "baseline"))
            for backend in order:
                pair[backend] = measure(args.binary, args.iterations, gate,
                                        backend)
            pairs.append(pair)
        result["gates"][gate] = {
            "core_cycles": summary(pairs, "cpu_core/cycles"),
            "instructions": summary(pairs, "cpu_core/instructions"),
            "tsc": summary(pairs, "tsc"),
            "samples": pairs,
        }
    result["decision"] = (
        "continue-to-reversed-placement" if any(
            result["gates"][f"forward_core_{variant}"]["core_cycles"]
            ["paired_delta_median"] <= -5 for variant in ("w1", "w2"))
        else "hard-stop-normal-necessary-gate-failed"
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for gate, data in result["gates"].items():
        core = data["core_cycles"]
        print(f"{gate}: core={core['paired_delta_median']:+.3f} "
              f"CI={core['bootstrap_95_ci']} "
              f"wins={core['candidate_wins']}/{core['pairs']} "
              f"tsc={data['tsc']['paired_delta_median']:+.3f}")
    print(f"decision={result['decision']}")


if __name__ == "__main__":
    main()
