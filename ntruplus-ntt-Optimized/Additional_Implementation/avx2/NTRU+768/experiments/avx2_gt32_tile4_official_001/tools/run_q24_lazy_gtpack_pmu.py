#!/usr/bin/env python3
"""Paired PMU corroboration for the final-check lazy10788 GT-pack."""

import argparse
import json
import math
import os
import random
import statistics
import subprocess
from pathlib import Path


GROUPS = ("core", "memory")


def bootstrap_ci(values, resamples, seed):
    generator = random.Random(seed)
    count = len(values)
    estimates = sorted(statistics.median(
        values[generator.randrange(count)] for _ in range(count))
        for _ in range(resamples))
    return {
        "confidence": 0.95,
        "resamples": resamples,
        "seed": seed,
        "lower": estimates[max(0, math.floor(0.025 * resamples))],
        "upper": estimates[min(resamples - 1,
                                 math.ceil(0.975 * resamples) - 1)],
    }


def run_launch(binary, iterations, group):
    command = [str(binary), str(iterations), "lazy-pack-pair"]
    environment = dict(os.environ)
    environment["Q24_SELF_PMU"] = group
    process = subprocess.run(command, check=True, text=True,
                             capture_output=True, env=environment)
    counts = {"centered": {}, "lazy": {}}
    tsc_deltas = []
    valid = False
    for line in process.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "META":
            valid = ("pmu-region=paired-centered-lazy-pack" in line
                     and "centered-error=0" in line and "lazy-error=0" in line)
        elif fields[0] == "LAZY_GTPACK_PMU_PAIR_SAMPLE":
            tsc_deltas.append(float(fields[4]))
        elif fields[0] == "PMU_COUNT":
            counts[fields[1]][fields[2]] = {
                "raw": int(fields[3]),
                "scaled": float(fields[4]),
                "time_enabled": int(fields[5]),
                "time_running": int(fields[6]),
            }
    if not valid or len(tsc_deltas) != 20 or not all(counts.values()):
        raise RuntimeError(f"invalid lazy GT-pack PMU output from {binary}")
    calls = 20 * iterations
    per_call = {variant: {event: value["scaled"] / calls
                          for event, value in events.items()}
                for variant, events in counts.items()}
    common = per_call["centered"].keys() & per_call["lazy"].keys()
    return {
        "command": command,
        "group": group,
        "counts": counts,
        "per_call": per_call,
        "lazy_minus_centered_per_call": {
            event: per_call["lazy"][event] - per_call["centered"][event]
            for event in common},
        "paired_tsc_median": statistics.median(tsc_deltas),
        "paired_tsc_wins": sum(value < 0 for value in tsc_deltas),
        "multiplexed": any(value["time_enabled"] != value["time_running"]
                           for events in counts.values()
                           for value in events.values()),
    }


def summarize(launches, resamples, seed):
    events = launches[0]["lazy_minus_centered_per_call"].keys()
    deltas = {event: [launch["lazy_minus_centered_per_call"][event]
                      for launch in launches] for event in events}
    return {
        "launches": len(launches),
        "all_nonmultiplexed": not any(launch["multiplexed"]
                                       for launch in launches),
        "median_per_call": {
            variant: {event: statistics.median(
                launch["per_call"][variant][event] for launch in launches)
                for event in events}
            for variant in ("centered", "lazy")},
        "median_lazy_minus_centered_per_call": {
            event: statistics.median(values) for event, values in deltas.items()},
        "negative_event_launches": {
            event: sum(value < 0 for value in values)
            for event, values in deltas.items()},
        "event_bootstrap_median_95ci": {
            event: bootstrap_ci(values, resamples, seed + index)
            for index, (event, values) in enumerate(sorted(deltas.items()))},
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--launches", type=int, default=32)
    parser.add_argument("--bootstrap-resamples", type=int, default=100000)
    parser.add_argument("--bootstrap-seed", type=int, default=107881)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    placements = {}
    for pindex, (name, binary) in enumerate((
            ("normal", args.binary),
            ("reversed", args.reversed_binary))):
        placements[name] = {}
        for gindex, group in enumerate(GROUPS):
            launches = [run_launch(binary, args.iterations, group)
                        for _ in range(args.launches)]
            placements[name][group] = {
                "launch_data": launches,
                "summary": summarize(launches, args.bootstrap_resamples,
                                     args.bootstrap_seed + 100 * pindex
                                     + 10 * gindex),
            }
    passed = all(
        data["core"]["summary"]["median_lazy_minus_centered_per_call"]
            ["cycles"] < 0
        and data["core"]["summary"]["event_bootstrap_median_95ci"]
            ["cycles"]["upper"] < 0
        for data in placements.values())
    result = {
        "schema": "ntruplus768-gt32-q24-lazy10788-gtpack-pmu-v1",
        "experiment": "GT32-Q24-LAZY10788-GTPACK-PMU-001",
        "benchmark": {
            "iterations_per_sample": args.iterations,
            "samples_per_launch": 20,
            "launches_per_group_placement": args.launches,
            "counter_scope": "paired full-decapsulation loops only",
            "event_groups": list(GROUPS),
            "cpu": 1,
        },
        "placements": placements,
        "core_cycle_corroboration_passed": passed,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for name, data in placements.items():
        core = data["core"]["summary"]
        memory = data["memory"]["summary"]
        delta = core["median_lazy_minus_centered_per_call"]
        md = memory["median_lazy_minus_centered_per_call"]
        ci = core["event_bootstrap_median_95ci"]["cycles"]
        print(f"{name}: cycles={delta['cycles']:.3f} "
              f"instructions={delta['instructions']:.3f} "
              f"cycle-wins={core['negative_event_launches']['cycles']}/"
              f"{args.launches} cycle-bootstrap95ci=[{ci['lower']:.3f},"
              f"{ci['upper']:.3f}] loads={md['retired-loads']:.3f} "
              f"stores={md['retired-stores']:.3f}")
    print(f"core-cycle-corroboration-pass={passed}")


if __name__ == "__main__":
    main()
