#!/usr/bin/env python3
"""Run fixed-core multi-launch N16 measurements and preserve raw samples."""

import argparse
import json
import statistics
import subprocess
from pathlib import Path


NAMES = ["folded", "reuse_one", "reuse_pair", "progressive", "pair"]


def parse(text: str) -> dict[str, object]:
    samples = {name: [] for name in NAMES}
    pmu = {name: {} for name in NAMES}
    for line in text.splitlines():
        fields = line.split(",")
        if fields[0] == "SAMPLE":
            row = dict(zip(fields[2::2], map(float, fields[3::2])))
            for name in NAMES:
                samples[name].append(row[name])
        elif fields[0] == "PMU":
            name, group = fields[1].split(":", 1)
            pmu[name][group] = dict(zip(fields[2::2], map(float, fields[3::2])))
    return {
        "samples": samples,
        "medians": {name: statistics.median(values)
                    for name, values in samples.items()},
        "pmu": pmu,
        "stdout": text,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--launches", type=int, default=8)
    parser.add_argument("--iterations", type=int, default=100000)
    parser.add_argument("--cpu", type=int, default=1)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    launches = []
    for launch in range(args.launches):
        command = [str(args.binary), str(args.iterations), str(args.cpu), "both"]
        result = subprocess.run(command, check=True, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        record = parse(result.stdout)
        record["launch"] = launch
        record["stderr"] = result.stderr
        launches.append(record)
        print("launch", launch, record["medians"])
    aggregate = {}
    for name in NAMES:
        launch_medians = [item["medians"][name] for item in launches]
        core_cycles = [item["pmu"][name]["basic"]["cycles"] for item in launches]
        aggregate[name] = {
            "median_of_launch_tsc_medians": statistics.median(launch_medians),
            "min_launch_tsc_median": min(launch_medians),
            "max_launch_tsc_median": max(launch_medians),
            "median_core_cycles": statistics.median(core_cycles),
            "min_core_cycles": min(core_cycles),
            "max_core_cycles": max(core_cycles),
            "median_instructions": statistics.median(
                item["pmu"][name]["basic"]["instructions"] for item in launches),
            "median_loads": statistics.median(
                item["pmu"][name]["basic"]["loads"] for item in launches),
            "median_stores": statistics.median(
                item["pmu"][name]["basic"]["stores"] for item in launches),
            "median_delivery": {
                event: statistics.median(
                    item["pmu"][name]["delivery"][event] for item in launches)
                for event in ("dsb_uops", "mite_uops", "idq_not_delivered")
            },
            "median_execution": {
                "port_5_11_uops": statistics.median(
                    item["pmu"][name]["execution"]["port_5_11_uops"]
                    for item in launches)
            },
        }
    payload = {
        "experiment": "GT32-PLANE-N16-STOCKHAM-STAGES-007",
        "launches": args.launches,
        "iterations_per_sample": args.iterations,
        "samples_per_launch": 20,
        "cpu": args.cpu,
        "aggregate": aggregate,
        "raw_launches": launches,
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(aggregate, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
