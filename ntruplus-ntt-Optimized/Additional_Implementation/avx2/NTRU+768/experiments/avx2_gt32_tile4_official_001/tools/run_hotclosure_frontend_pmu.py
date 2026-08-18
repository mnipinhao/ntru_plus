#!/usr/bin/env python3
"""Whole-measure fixed-ELF frontend PMU comparison for G0 versus Gc."""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
from pathlib import Path


EVENTS = (
    "cpu_core/cycles/",
    "cpu_core/instructions/",
    "cpu_core/idq.dsb_uops/",
    "cpu_core/idq.mite_uops/",
    "cpu_core/dsb2mite_switches.penalty_cycles/",
    "cpu_core/idq_uops_not_delivered.core/",
)


def measure(binary: Path, cpu: int) -> dict[str, int]:
    command = ["perf", "stat", "-x,", "-e", ",".join(EVENTS), "--", "taskset", "-c", str(cpu), str(binary)]
    completed = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, check=True)
    answer: dict[str, int] = {}
    for line in completed.stderr.splitlines():
        fields = line.split(",")
        if len(fields) >= 3 and fields[0].isdigit():
            answer[fields[2].replace("/u", "/")] = int(fields[0])
    if len(answer) != len(EVENTS):
        raise RuntimeError(f"incomplete perf output: {completed.stderr}")
    return answer


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("g0", type=Path)
    parser.add_argument("gc", type=Path)
    parser.add_argument("--blocks", type=int, default=8)
    parser.add_argument("--cpu", type=int, default=1)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    samples = {"G0": [], "Gc": []}
    for _ in range(args.blocks):
        for label, binary in (("G0", args.g0), ("Gc", args.gc), ("Gc", args.gc), ("G0", args.g0)):
            samples[label].append(measure(binary, args.cpu))
    medians = {
        label: {event: statistics.median(sample[event] for sample in values) for event in EVENTS}
        for label, values in samples.items()
    }
    report = {
        "schema": "gt32-hotclosure-whole-measure-frontend-pmu-v1",
        "scope": "entire SUPERcop measure process; causal corroboration, not per-operation attribution",
        "cpu": args.cpu,
        "blocks": args.blocks,
        "samples_per_image": 2 * args.blocks,
        "medians": medians,
        "gc_minus_g0": {event: medians["Gc"][event] - medians["G0"][event] for event in EVENTS},
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
