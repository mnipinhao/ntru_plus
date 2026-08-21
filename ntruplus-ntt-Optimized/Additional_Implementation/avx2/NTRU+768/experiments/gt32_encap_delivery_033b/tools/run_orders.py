#!/usr/bin/env python3
"""Interleave fixed-address control/candidate ELFs for each 033B order."""

from __future__ import annotations

import argparse
import json
import os
import random
import statistics
import subprocess
from pathlib import Path


ORDERS = ["current", "transform", "q24", "arithmetic"]


def q2(values: list[int]) -> float:
    expanded = sorted(value for value in values for _ in range(8))
    n = len(values)
    return sum(expanded[3 * n:5 * n]) / (2 * n)


def ci(values: list[float], samples: int = 100000) -> list[float]:
    rng = random.Random(0x033B20260819)
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
        if fields[0] == "cycles":
            result["cycles"] = [int(value) for value in fields[1:]]
        elif fields[0] in {"cpucycles_implementation", "caller_address", "sink"}:
            result[fields[0]] = fields[1]
    if result.get("cpucycles_implementation") != "default-perfevent":
        raise RuntimeError(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", type=Path, required=True)
    parser.add_argument("--launches", type=int, default=48)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cpu = sorted(os.sched_getaffinity(0))[0]
    result: dict[str, object] = {"schema": "gt32-encap-delivery-033b-v1",
                                "cpu": cpu, "orders": {}}
    for order in ORDERS:
        paths = {variant: args.build / f"bench_{order}_{variant}"
                 for variant in ("control", "candidate")}
        entries = []
        for launch in range(args.launches):
            sequence = ["control", "candidate"] if launch % 2 == 0 else ["candidate", "control"]
            measured = {variant: run(paths[variant], cpu) for variant in sequence}
            if measured["control"]["caller_address"] != measured["candidate"]["caller_address"]:
                raise RuntimeError(f"{order}: caller address mismatch")
            if measured["control"]["sink"] != measured["candidate"]["sink"]:
                raise RuntimeError(f"{order}: output mismatch")
            control = q2(measured["control"]["cycles"])
            candidate = q2(measured["candidate"]["cycles"])
            entries.append({"launch": launch + 1, "order": sequence,
                            "control": control, "candidate": candidate,
                            "delta": candidate - control,
                            "caller_address": measured["control"]["caller_address"]})
        deltas = [float(entry["delta"]) for entry in entries]
        median = statistics.median(deltas)
        result["orders"][order] = {
            "paired_launch_median_delta_core_cycles": median,
            "paired_delta_mad_core_cycles": statistics.median(
                abs(value - median) for value in deltas),
            "bootstrap_median_95ci_core_cycles": ci(deltas),
            "candidate_favorable_launches": sum(value < 0 for value in deltas),
            "launches": len(entries),
            "ab_median_delta_core_cycles": statistics.median(deltas[0::2]),
            "ba_median_delta_core_cycles": statistics.median(deltas[1::2]),
            "launch_results": entries,
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({name: {key: value for key, value in data.items()
                             if key != "launch_results"}
                      for name, data in result["orders"].items()},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

