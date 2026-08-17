#!/usr/bin/env python3
import argparse
import json
import statistics
import subprocess
from pathlib import Path


def run(binary: Path, iterations: int) -> dict:
    result = subprocess.run([str(binary), str(iterations)], check=True,
                            text=True, capture_output=True)
    records: dict[str, list[dict[str, float]]] = {}
    correct = False
    for line in result.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "META":
            correct = "correctness=byte-exact-prefix-pass" in line
        elif fields[0] == "PREFIX":
            records.setdefault(fields[1], []).append({
                "sample": int(fields[2]),
                "official_tsc": float(fields[3]),
                "gt_tsc": float(fields[4]),
                "delta_tsc": float(fields[5]),
            })
    if not correct or len(records) != 7:
        raise RuntimeError(f"invalid output from {binary}")
    return {"records": records, "stdout": result.stdout}


def median(values):
    return statistics.median(values)


def mad(values):
    center = median(values)
    return median([abs(value - center) for value in values])


def summarize(launches: list[dict]) -> dict:
    names = list(launches[0]["records"])
    summary = {}
    prior_delta = 0.0
    for name in names:
        launch_deltas = [median([row["delta_tsc"]
                                for row in launch["records"][name]])
                         for launch in launches]
        all_rows = [row for launch in launches for row in launch["records"][name]]
        cumulative = median(launch_deltas)
        summary[name] = {
            "official_median_tsc": median([row["official_tsc"] for row in all_rows]),
            "gt_median_tsc": median([row["gt_tsc"] for row in all_rows]),
            "cumulative_delta_tsc": cumulative,
            "incremental_delta_tsc": cumulative - prior_delta,
            "launch_delta_mad_tsc": mad(launch_deltas),
            "negative_launch_medians": sum(value < 0 for value in launch_deltas),
            "launches": len(launches),
            "raw_launch_delta_tsc": launch_deltas,
        }
        prior_delta = cumulative
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=500)
    parser.add_argument("--launches", type=int, default=8)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    output = {
        "schema": "ntruplus768-gt32-encap-cumulative-v1",
        "iterations_per_sample": args.iterations,
        "launches": args.launches,
        "placements": {},
    }
    for name, binary in (("normal", args.binary),
                         ("reversed", args.reversed_binary)):
        launches = [run(binary, args.iterations) for _ in range(args.launches)]
        output["placements"][name] = {
            "binary": str(binary),
            "prefixes": summarize(launches),
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output["placements"], indent=2))


if __name__ == "__main__":
    main()
