#!/usr/bin/env python3
"""Run paired multi-launch normal/reversed load-to-compute benchmarks."""
from __future__ import annotations
import argparse
import json
import os
import statistics
import subprocess
from pathlib import Path

def run(path: Path, cpu: int) -> dict[str, object]:
    def pin() -> None:
        os.sched_setaffinity(0, {cpu})
    text = subprocess.run([str(path.resolve())], check=True, capture_output=True,
                          text=True, preexec_fn=pin).stdout
    rounds = []
    addresses = {}
    for line in text.splitlines():
        fields = line.split()
        if fields and fields[0] in {"pack_control", "pack_candidate",
                                    "b3_control", "b3_candidate"}:
            addresses[fields[0]] = fields[1]
        if fields and fields[0] == "round":
            row = {fields[i]: fields[i + 1] for i in range(0, len(fields), 2)}
            rounds.append({
                "pack_delta": int(row["pack_candidate"]) - int(row["pack_control"]),
                "b3_delta": int(row["b3_candidate"]) - int(row["b3_control"]),
            })
    return {"addresses": addresses, "rounds": rounds}

def summarize(values: list[float]) -> dict[str, object]:
    median = statistics.median(values)
    return {
        "median_delta_cycles": median,
        "mad_cycles": statistics.median(abs(value - median) for value in values),
        "candidate_favorable": sum(value < 0 for value in values),
        "observations": len(values),
    }

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--normal", type=Path, required=True)
    parser.add_argument("--reversed", type=Path, required=True)
    parser.add_argument("--launches", type=int, default=16)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cpu = sorted(os.sched_getaffinity(0))[0]
    entries = []
    for placement in ("normal", "reversed"):
        for launch in range(args.launches):
            result = run(getattr(args, placement), cpu)
            entries.append({"placement": placement, "launch": launch + 1, **result})
    summary = {}
    for placement in ("normal", "reversed"):
        rows = [entry for entry in entries if entry["placement"] == placement]
        for region in ("pack", "b3"):
            deltas = [statistics.median(
                round_[region + "_delta"] for round_ in row["rounds"]) for row in rows]
            summary[placement + "_" + region] = summarize(deltas)
    output = {"schema": "gt32-load-to-compute-041-benchmark-v1",
              "cpu": cpu, "summary": summary, "launches": entries}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
