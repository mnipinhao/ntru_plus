#!/usr/bin/env python3
"""Long-loop full-Encap PMU comparison for current independent exports."""

from __future__ import annotations

import json
import pathlib
import statistics
import subprocess
import tempfile

EXP = pathlib.Path(__file__).resolve().parents[1]
RESULTS = EXP / "results"
ITERATIONS = 20000
EVENTS = (
    "cpu_core/cycles/",
    "cpu_core/instructions/",
    "cpu_core/mem_inst_retired.all_loads/",
    "cpu_core/mem_inst_retired.all_stores/",
)
BINARIES = {
    "official": EXP / "build/official-encap-loop",
    "gt_clean": EXP / "build/gt-clean-encap-loop",
}


def measure(binary: pathlib.Path) -> dict[str, float]:
    with tempfile.NamedTemporaryFile() as output:
        command = [
            "perf", "stat", "-x,", "-o", output.name,
            "-e", ",".join(EVENTS),
            "taskset", "-c", "1", "setarch", "x86_64", "-R",
            str(binary.resolve()), str(ITERATIONS),
        ]
        completed = subprocess.run(command, stdout=subprocess.DEVNULL,
                                   stderr=subprocess.PIPE, text=True)
        if completed.returncode:
            raise RuntimeError(completed.stderr)
        output.seek(0)
        result = {}
        for line in output.read().decode().splitlines():
            fields = line.split(",")
            if len(fields) >= 3 and fields[0].strip().isdigit():
                event = fields[2].replace("/u", "/")
                result[event] = int(fields[0]) / ITERATIONS
        if set(result) != set(EVENTS):
            raise RuntimeError(result)
        return result


def main() -> None:
    blocks = 8
    rows = []
    for block in range(blocks):
        order = ("official", "gt_clean") if block % 2 == 0 else (
            "gt_clean", "official")
        samples = {}
        for implementation in order:
            samples[implementation] = measure(BINARIES[implementation])
        rows.append({"block": block + 1, "samples": samples})
    summary = {}
    for event in EVENTS:
        official = [row["samples"]["official"][event] for row in rows]
        gt = [row["samples"]["gt_clean"][event] for row in rows]
        deltas = [b - a for a, b in zip(official, gt)]
        summary[event] = {
            "official_per_call": statistics.median(official),
            "gt_per_call": statistics.median(gt),
            "gt_minus_official": statistics.median(deltas),
            "block_deltas": deltas,
        }
    result = {
        "iterations_per_process": ITERATIONS,
        "blocks": blocks,
        "cpu": 1,
        "aslr": "disabled",
        "events": EVENTS,
        "summary": summary,
        "rows": rows,
    }
    destination = RESULTS / "encap_full_loop_pmu.json"
    destination.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
