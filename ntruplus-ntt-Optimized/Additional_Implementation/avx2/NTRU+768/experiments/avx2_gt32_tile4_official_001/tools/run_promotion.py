#!/usr/bin/env python3
"""Run independent promotion launches and summarize paired TSC ratios."""

import argparse
import hashlib
import json
import statistics
import subprocess
from pathlib import Path

from report_promotion_symbols import sections, symbols


def percentile(values: list[float], p: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * p
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    fraction = position - low
    return ordered[low] * (1.0 - fraction) + ordered[high] * fraction


def summarize(values: list[float]) -> dict[str, float]:
    median = statistics.median(values)
    deviations = [abs(value - median) for value in values]
    return {
        "median": median,
        "q1": percentile(values, 0.25),
        "q3": percentile(values, 0.75),
        "iqr": percentile(values, 0.75) - percentile(values, 0.25),
        "mad": statistics.median(deviations),
        "min": min(values),
        "max": max(values),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--iterations", type=int, default=100000)
    parser.add_argument("--launches", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    gates: dict[str, list[dict[str, float]]] = {}
    metadata = []
    for launch in range(args.launches):
        process = subprocess.run(
            [str(args.binary), str(args.iterations), str(launch & 1)],
            check=True, text=True, capture_output=True)
        for line in process.stdout.splitlines():
            fields = line.split(",")
            if fields[0] == "META":
                metadata.append({"launch": launch, "line": line})
            elif fields[0] == "SAMPLE":
                gates.setdefault(fields[1], []).append({
                    "launch": launch,
                    "sample": int(fields[2]),
                    "official_tsc": float(fields[3]),
                    "tile4_tsc": float(fields[4]),
                    "ratio": float(fields[5]),
                })
    result = {
        "binary": str(args.binary),
        "binary_sha256": hashlib.sha256(args.binary.read_bytes()).hexdigest(),
        "binary_sections": sections(args.binary),
        "binary_symbols": symbols(args.binary),
        "iterations_per_sample": args.iterations,
        "launches": args.launches,
        "samples_per_launch": 20,
        "unit": "TSC ticks per call",
        "metadata": metadata,
        "gates": {},
    }
    for name, records in gates.items():
        ratios = [record["ratio"] for record in records]
        official = [record["official_tsc"] for record in records]
        tile4 = [record["tile4_tsc"] for record in records]
        launch_ratios = []
        for launch in range(args.launches):
            selected = [record["ratio"] for record in records
                        if record["launch"] == launch]
            launch_ratios.append(statistics.median(selected))
        result["gates"][name] = {
            "official": summarize(official),
            "tile4": summarize(tile4),
            "paired_ratio": summarize(ratios),
            "launch_median_ratios": launch_ratios,
            "launches_tile4_faster": sum(value < 1.0 for value in launch_ratios),
            "samples_tile4_faster": sum(value < 1.0 for value in ratios),
            "sample_count": len(ratios),
        }
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
