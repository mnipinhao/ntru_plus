#!/usr/bin/env python3
"""Balanced whole-measure PMU control for the two clearest relocation pairs."""

from __future__ import annotations

import json
import pathlib
import statistics
import subprocess
import tempfile

EXP = pathlib.Path(__file__).resolve().parents[1]
BUILD = EXP / "build"
RESULTS = EXP / "results"
EVENTS = (
    "cpu_core/cycles/",
    "cpu_core/instructions/",
    "cpu_core/idq.dsb_uops/",
    "cpu_core/idq.mite_uops/",
)
PAIRS = {
    "frontend_n5": (
        "cluster-e1_frontend_n5-pad-0000-measure",
        "cluster-e1_frontend_n5-pad-0400-measure",
    ),
    "general_b3_q24": (
        "cluster-e3_b3_q24-pad-0000-measure",
        "cluster-e3_b3_q24-pad-0400-measure",
    ),
}


def measure(binary: pathlib.Path) -> dict[str, int]:
    with tempfile.NamedTemporaryFile() as output:
        command = [
            "perf", "stat", "-x,", "-o", output.name,
            "-e", ",".join(EVENTS),
            "taskset", "-c", "1", "setarch", "x86_64", "-R",
            str(binary.resolve()),
        ]
        completed = subprocess.run(command, stdout=subprocess.DEVNULL,
                                   stderr=subprocess.PIPE, text=True)
        if completed.returncode:
            raise RuntimeError(" ".join(command) + "\n" + completed.stderr)
        result = {}
        output.seek(0)
        for encoded in output.read().decode().splitlines():
            fields = encoded.split(",")
            if len(fields) >= 3 and fields[0].strip().isdigit():
                event = fields[2].replace("/u", "/")
                result[event] = int(fields[0])
        if set(result) != set(EVENTS):
            raise RuntimeError(f"missing PMU events: {result}")
        return result


def main() -> None:
    blocks = 8
    report = {"blocks": blocks, "events": EVENTS, "pairs": {}}
    for name, filenames in PAIRS.items():
        binaries = [BUILD / filename for filename in filenames]
        raw = []
        for block in range(blocks):
            order = (0, 1) if block % 2 == 0 else (1, 0)
            samples = {}
            for index in order:
                samples[index] = measure(binaries[index])
            raw.append({"block": block, "samples": samples})
        summary = {}
        for event in EVENTS:
            deltas = [entry["samples"][1][event]
                      - entry["samples"][0][event] for entry in raw]
            summary[event] = {
                "median_delta": statistics.median(deltas),
                "deltas": deltas,
            }
        report["pairs"][name] = {
            "control": str(binaries[0]),
            "candidate": str(binaries[1]),
            "summary": summary,
        }
    destination = RESULTS / "frontend_pmu_pairs.json"
    destination.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
