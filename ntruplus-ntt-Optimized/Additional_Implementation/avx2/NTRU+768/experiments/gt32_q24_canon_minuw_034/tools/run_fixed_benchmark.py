#!/usr/bin/env python3
"""Interleave two fixed-address ELFs differing only in Q24 hot instructions."""

from __future__ import annotations

import argparse
import json
import os
import random
import statistics
import subprocess
from pathlib import Path


def q2(values: list[int]) -> float:
    expanded = sorted(value for value in values for _ in range(8))
    n = len(values)
    return sum(expanded[3 * n:5 * n]) / (2 * n)


def ci(values: list[float], samples: int = 100000) -> list[float]:
    rng = random.Random(0x034F1CED)
    estimates = sorted(statistics.median(rng.choices(values, k=len(values)))
                       for _ in range(samples))
    return [estimates[int(samples * .025)], estimates[int(samples * .975)]]


def run(binary: Path, cpu: int) -> dict[str, object]:
    def pin() -> None:
        os.sched_setaffinity(0, {cpu})
    output = subprocess.run([str(binary.resolve())], check=True,
                            capture_output=True, text=True, preexec_fn=pin).stdout
    result: dict[str, object] = {}
    for line in output.splitlines():
        fields = line.split()
        if fields[0].endswith("_cycles"):
            result[fields[0]] = [int(item) for item in fields[1:]]
        elif fields[0] in {"cpucycles_implementation", "pack_address"}:
            result[fields[0]] = fields[1]
    if result.get("cpucycles_implementation") != "default-perfevent":
        raise RuntimeError(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--control", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--launches", type=int, default=48)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cpu = sorted(os.sched_getaffinity(0))[0]
    entries = []
    for launch in range(args.launches):
        order = ["control", "candidate"] if launch % 2 == 0 else ["candidate", "control"]
        measured = {}
        for variant in order:
            measured[variant] = run(getattr(args, variant), cpu)
        if measured["control"]["pack_address"] != measured["candidate"]["pack_address"]:
            raise RuntimeError("Q24 virtual addresses differ")
        entry: dict[str, object] = {"launch": launch + 1, "order": order,
                                   "pack_address": measured["control"]["pack_address"]}
        for region in ("single", "double"):
            control = q2(measured["control"][region + "_cycles"])
            candidate = q2(measured["candidate"][region + "_cycles"])
            entry[region + "_control"] = control
            entry[region + "_candidate"] = candidate
            entry[region + "_delta"] = candidate - control
        entries.append(entry)
    summaries = {}
    for region in ("single", "double"):
        deltas = [float(entry[region + "_delta"]) for entry in entries]
        median = statistics.median(deltas)
        summaries[region] = {
            "paired_launch_median_delta_core_cycles": median,
            "paired_delta_mad_core_cycles": statistics.median(
                abs(value - median) for value in deltas),
            "bootstrap_median_95ci_core_cycles": ci(deltas),
            "candidate_favorable_launches": sum(value < 0 for value in deltas),
            "launches": len(entries),
        }
    result = {"schema": "gt32-q24-034-fixed-address-v1", "cpu": cpu,
              "summary": summaries, "launch_results": entries}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summaries, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

