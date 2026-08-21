#!/usr/bin/env python3
"""Run normal/reversed fixed-ELF SUPERcop-style Q24 measurements."""

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


def bootstrap_ci(values: list[float], samples: int = 100000) -> list[float]:
    rng = random.Random(0x03420260819)
    estimates = sorted(statistics.median(rng.choices(values, k=len(values)))
                       for _ in range(samples))
    return [estimates[int(samples * 0.025)], estimates[int(samples * 0.975)]]


def parse(text: str) -> dict[str, object]:
    result: dict[str, object] = {}
    for line in text.splitlines():
        fields = line.split()
        if not fields:
            continue
        if fields[0].endswith("_cycles"):
            result[fields[0]] = [int(item) for item in fields[1:]]
        elif fields[0] in {"cpucycles_implementation", "control_address",
                           "candidate_address"}:
            result[fields[0]] = fields[1]
    if result.get("cpucycles_implementation") != "default-perfevent":
        raise RuntimeError(f"wrong backend: {result}")
    return result


def summarize(entries: list[dict[str, object]], prefix: str) -> dict[str, object]:
    deltas = [float(entry[f"{prefix}_delta"]) for entry in entries]
    median = statistics.median(deltas)
    return {
        "paired_launch_median_delta_core_cycles": median,
        "paired_delta_mad_core_cycles": statistics.median(
            abs(value - median) for value in deltas),
        "bootstrap_median_95ci_core_cycles": bootstrap_ci(deltas),
        "candidate_favorable_launches": sum(value < 0 for value in deltas),
        "launches": len(entries),
        "ab_median_delta_core_cycles": statistics.median(deltas[0::2]),
        "ba_median_delta_core_cycles": statistics.median(deltas[1::2]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--normal", type=Path, required=True)
    parser.add_argument("--reversed", type=Path, required=True)
    parser.add_argument("--launches", type=int, default=32)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    allowed = sorted(os.sched_getaffinity(0))
    if not allowed:
        raise RuntimeError("no CPU available")
    cpu = allowed[0]
    result: dict[str, object] = {
        "schema": "gt32-q24-canon-minuw-034-v1",
        "cycle_backend": "default-perfevent/PERF_COUNT_HW_CPU_CYCLES",
        "cpu": cpu,
        "placements": {},
    }
    for placement, binary in (("normal", args.normal),
                              ("reversed", args.reversed)):
        entries = []
        for launch in range(args.launches):
            order = "AB" if launch % 2 == 0 else "BA"

            def pin() -> None:
                os.sched_setaffinity(0, {cpu})

            completed = subprocess.run([str(binary.resolve()), order],
                                       check=True, capture_output=True, text=True,
                                       preexec_fn=pin)
            parsed = parse(completed.stdout)
            entry: dict[str, object] = {
                "launch": launch + 1,
                "order": order,
                "control_address": parsed["control_address"],
                "candidate_address": parsed["candidate_address"],
            }
            for region in ("single", "double"):
                control = q2(parsed[f"{region}_control_cycles"])
                candidate = q2(parsed[f"{region}_candidate_cycles"])
                entry[f"{region}_control"] = control
                entry[f"{region}_candidate"] = candidate
                entry[f"{region}_delta"] = candidate - control
            entries.append(entry)
        result["placements"][placement] = {
            "single": summarize(entries, "single"),
            "double": summarize(entries, "double"),
            "launch_results": entries,
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result["placements"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

