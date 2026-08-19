#!/usr/bin/env python3
"""Run the same-ELF SUPERcop-style lifetime gate across fresh launches."""

from __future__ import annotations

import argparse
import json
import os
import random
import statistics
import subprocess
from pathlib import Path


def stabilized_q2(values: list[int]) -> float:
    expanded = sorted(value for value in values for _ in range(8))
    n = len(values)
    return sum(expanded[3 * n:5 * n]) / (2 * n)


def bootstrap_median_ci(values: list[float], samples: int = 100000) -> list[float]:
    rng = random.Random(20260819)
    estimates = sorted(statistics.median(rng.choices(values, k=len(values)))
                       for _ in range(samples))
    return [estimates[int(samples * 0.025)], estimates[int(samples * 0.975)]]


def parse_output(text: str) -> dict[str, object]:
    result: dict[str, object] = {}
    for line in text.splitlines():
        fields = line.split()
        if not fields:
            continue
        if fields[0].endswith("_cycles"):
            result[fields[0]] = [int(value) for value in fields[1:]]
        elif fields[0] in {"cpucycles_implementation", "control_address",
                           "candidate_address", "sink"}:
            result[fields[0]] = fields[1]
    if result.get("cpucycles_implementation") != "default-perfevent":
        raise RuntimeError(f"unexpected cycle backend: {result}")
    for key in ("control_cycles", "candidate_cycles"):
        if len(result.get(key, [])) != 96:
            raise RuntimeError(f"incomplete {key}: {result}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--launches", type=int, default=16)
    args = parser.parse_args()

    allowed = sorted(os.sched_getaffinity(0))
    if not allowed:
        raise RuntimeError("no CPU available for affinity pinning")
    cpu = allowed[0]
    launches = []
    for launch in range(args.launches):
        order = "AB" if launch % 2 == 0 else "BA"

        def pin() -> None:
            os.sched_setaffinity(0, {cpu})

        completed = subprocess.run([str(args.binary.resolve()), order],
                                   check=True, capture_output=True, text=True,
                                   preexec_fn=pin)
        parsed = parse_output(completed.stdout)
        control = stabilized_q2(parsed["control_cycles"])
        candidate = stabilized_q2(parsed["candidate_cycles"])
        launches.append({
            "launch": launch + 1,
            "order": order,
            "control_q2_core_cycles": control,
            "candidate_q2_core_cycles": candidate,
            "candidate_minus_control_core_cycles": candidate - control,
            "control_address": parsed["control_address"],
            "candidate_address": parsed["candidate_address"],
        })

    deltas = [entry["candidate_minus_control_core_cycles"]
              for entry in launches]
    median_delta = statistics.median(deltas)
    control_median = statistics.median(
        entry["control_q2_core_cycles"] for entry in launches)
    summary = {
        "cycle_backend": "default-perfevent/PERF_COUNT_HW_CPU_CYCLES",
        "cpu": cpu,
        "launches": args.launches,
        "observations_per_variant_per_launch": 96,
        "control_median_q2_core_cycles": control_median,
        "candidate_median_q2_core_cycles": statistics.median(
            entry["candidate_q2_core_cycles"] for entry in launches),
        "paired_launch_median_delta_core_cycles": median_delta,
        "paired_launch_median_delta_percent": 100.0 * median_delta / control_median,
        "paired_delta_mad_core_cycles": statistics.median(
            abs(value - median_delta) for value in deltas),
        "bootstrap_median_95ci_core_cycles": bootstrap_median_ci(deltas),
        "candidate_favorable_launches": sum(value < 0 for value in deltas),
        "ab_median_delta_core_cycles": statistics.median(deltas[0::2]),
        "ba_median_delta_core_cycles": statistics.median(deltas[1::2]),
    }
    result = {
        "schema": "gt32-encap-lifetime-031-supercop-style-v1",
        "method": "33 consecutive cpucycles timestamps; 32 adjacent differences; 3 loops; stabilized Q2",
        "fixed_elf": str(args.binary.resolve()),
        "summary": summary,
        "launch_results": launches,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
