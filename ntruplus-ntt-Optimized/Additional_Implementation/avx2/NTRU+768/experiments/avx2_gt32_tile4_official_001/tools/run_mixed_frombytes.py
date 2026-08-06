#!/usr/bin/env python3
"""Summarize the short P1 mixed-layout frombytes gate."""

import argparse
import json
import statistics
import subprocess
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    records: dict[str, list[dict[str, float]]] = {}
    metadata = []
    for pattern in (0, 1):
        process = subprocess.run(
            [str(args.binary), str(args.iterations), str(pattern)],
            check=True, text=True, capture_output=True)
        for line in process.stdout.splitlines():
            fields = line.split(",")
            if fields[0] == "META":
                metadata.append(line)
            elif fields[0] == "SAMPLE":
                records.setdefault(fields[1], []).append({
                    "sample": int(fields[2]),
                    "baseline_tsc": float(fields[3]),
                    "mixed_tsc": float(fields[4]),
                    "ratio": float(fields[5]),
                })
    result = {
        "scope": "P1 frombytes(f) plus private basemul plus I1 plus T9",
        "unit": "TSC ticks per call",
        "iterations_per_sample": args.iterations,
        "metadata": metadata,
        "gates": {},
    }
    for gate, values in records.items():
        baseline = [value["baseline_tsc"] for value in values]
        mixed = [value["mixed_tsc"] for value in values]
        ratios = [value["ratio"] for value in values]
        deltas = [candidate - reference
                  for reference, candidate in zip(baseline, mixed)]
        delta_median = statistics.median(deltas)
        result["gates"][gate] = {
            "baseline_median": statistics.median(baseline),
            "mixed_median": statistics.median(mixed),
            "paired_delta_median": delta_median,
            "paired_delta_mad": statistics.median(
                abs(delta - delta_median) for delta in deltas),
            "paired_ratio_median": statistics.median(ratios),
            "paired_mixed_wins": sum(ratio < 1.0 for ratio in ratios),
            "samples": len(values),
            "raw": values,
        }
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
