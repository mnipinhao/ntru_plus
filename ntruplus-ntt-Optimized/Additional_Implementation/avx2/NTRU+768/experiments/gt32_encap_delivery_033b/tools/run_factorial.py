#!/usr/bin/env python3
"""Run the predeclared A/B/C confirmation under the selected transform order."""

from __future__ import annotations

import argparse
import json
import os
import random
import statistics
import subprocess
from pathlib import Path

VARIANTS = ["a", "b", "c"]

def q2(values: list[int]) -> float:
    expanded = sorted(value for value in values for _ in range(8))
    n = len(values)
    return sum(expanded[3*n:5*n]) / (2*n)

def ci(values: list[float], seed: int, samples: int = 100000) -> list[float]:
    rng = random.Random(seed)
    estimates = sorted(statistics.median(rng.choices(values, k=len(values)))
                       for _ in range(samples))
    return [estimates[int(.025*samples)], estimates[int(.975*samples)]]

def run(path: Path, cpu: int) -> tuple[float, str]:
    def pin() -> None:
        os.sched_setaffinity(0, {cpu})
    output = subprocess.run([str(path.resolve())], check=True, capture_output=True,
                            text=True, preexec_fn=pin).stdout.splitlines()
    cycles = [int(x) for line in output if line.startswith("cycles ")
              for x in line.split()[1:]]
    sink = next(line.split()[1] for line in output if line.startswith("sink "))
    return q2(cycles), sink

def summarize(values: list[float], seed: int) -> dict[str, object]:
    median = statistics.median(values)
    return {"median_delta_core_cycles": median,
            "favorable_launches": sum(x < 0 for x in values),
            "launches": len(values),
            "mad_core_cycles": statistics.median(abs(x-median) for x in values),
            "bootstrap_median_95ci_core_cycles": ci(values, seed)}

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", type=Path, required=True)
    parser.add_argument("--launches", type=int, default=48)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cpu = sorted(os.sched_getaffinity(0))[0]
    paths = {v: args.build / "factorial" / v / "bench" for v in VARIANTS}
    entries = []
    rotations = [VARIANTS, ["b", "c", "a"], ["c", "a", "b"]]
    for launch in range(args.launches):
        order = rotations[launch % len(rotations)]
        measured = {v: run(paths[v], cpu) for v in order}
        if len({measured[v][1] for v in VARIANTS}) != 1:
            raise RuntimeError("factorial output mismatch")
        entries.append({"launch": launch+1, "order": order,
                        "cycles": {v: measured[v][0] for v in VARIANTS},
                        "b_minus_a": measured["b"][0]-measured["a"][0],
                        "c_minus_b": measured["c"][0]-measured["b"][0]})
    ba = [float(x["b_minus_a"]) for x in entries]
    cb = [float(x["c_minus_b"]) for x in entries]
    result = {"schema": "gt32-encap-delivery-033b-factorial-v1", "cpu": cpu,
              "comparison": {"b_minus_a": summarize(ba, 0x033BA),
                             "c_minus_b": summarize(cb, 0x033BC)},
              "launch_results": entries}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps(result["comparison"], indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
