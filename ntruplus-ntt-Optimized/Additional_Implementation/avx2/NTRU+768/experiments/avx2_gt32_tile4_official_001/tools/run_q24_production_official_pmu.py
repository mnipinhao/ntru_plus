#!/usr/bin/env python3
"""Collect paired core cycles for promoted Q24 versus Official Main."""

import argparse
import json
import os
import statistics
import subprocess
from pathlib import Path


def run(binary: Path, iterations: int) -> dict[str, object]:
    command = [str(binary), str(iterations), "official-pair"]
    environment = dict(os.environ)
    environment["Q24_SELF_PMU"] = "core"
    process = subprocess.run(command, check=True, text=True,
                             capture_output=True, env=environment)
    counts = {"official": {}, "q24": {}}
    samples = []
    valid = False
    for line in process.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "META":
            valid = ("pmu-region=paired-official-q24" in line
                     and "official-error=0" in line
                     and "q24-error=0" in line)
        elif fields[0] == "PMU_PAIR_SAMPLE":
            samples.append(float(fields[4]))
        elif fields[0] == "PMU_COUNT":
            counts[fields[1]][fields[2]] = {
                "raw": int(fields[3]),
                "scaled": float(fields[4]),
                "time_enabled": int(fields[5]),
                "time_running": int(fields[6]),
            }
    if not valid or len(samples) != 20:
        raise RuntimeError(f"invalid benchmark output from {binary}")
    calls = 20 * iterations
    per_call = {
        variant: {
            event: data["scaled"] / calls
            for event, data in events.items()
        }
        for variant, events in counts.items()
    }
    return {
        "command": command,
        "counts": counts,
        "per_call": per_call,
        "q24_minus_official": {
            event: per_call["q24"][event] - per_call["official"][event]
            for event in per_call["official"].keys()
                          & per_call["q24"].keys()
        },
        "paired_tsc_median": statistics.median(samples),
        "paired_tsc_wins": sum(value < 0 for value in samples),
        "multiplexed": any(
            data["time_enabled"] != data["time_running"]
            for events in counts.values() for data in events.values()),
    }


def summarize(launches: list[dict[str, object]]) -> dict[str, object]:
    events = launches[0]["q24_minus_official"].keys()
    result = {
        "launches": len(launches),
        "all_nonmultiplexed": not any(launch["multiplexed"]
                                       for launch in launches),
        "median_per_call": {
            variant: {
                event: statistics.median(
                    launch["per_call"][variant][event]
                    for launch in launches)
                for event in events
            }
            for variant in ("official", "q24")
        },
        "median_q24_minus_official_per_call": {
            event: statistics.median(
                launch["q24_minus_official"][event]
                for launch in launches)
            for event in events
        },
        "negative_core_cycle_launches": sum(
            launch["q24_minus_official"]["cycles"] < 0
            for launch in launches),
    }
    official_cycles = result["median_per_call"]["official"]["cycles"]
    result["q24_minus_official_core_cycles_percent"] = (
        100.0 * result["median_q24_minus_official_per_call"]["cycles"]
        / official_cycles)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--launches", type=int, default=4)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    placements = {}
    for name, binary in (("normal", args.binary),
                         ("reversed", args.reversed_binary)):
        launches = [run(binary, args.iterations)
                    for _ in range(args.launches)]
        placements[name] = {
            "launch_data": launches,
            "summary": summarize(launches),
        }
    result = {
        "schema": "ntruplus768-gt32-q24-production-official-pmu-v1",
        "experiment": "GT32-Q24-PRODUCTION-OFFICIAL-PMU-001",
        "benchmark": {
            "iterations_per_sample": args.iterations,
            "samples_per_launch": 20,
            "launches_per_placement": args.launches,
            "cpu": 1,
            "counter_scope": "paired decapsulation loops only",
            "event_group": ["cycles", "ref-cycles", "instructions"],
        },
        "placements": placements,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for name, placement in placements.items():
        summary = placement["summary"]
        medians = summary["median_per_call"]
        delta = summary["median_q24_minus_official_per_call"]
        print(f"{name}: Official={medians['official']['cycles']:.3f} "
              f"core cycles, Q24={medians['q24']['cycles']:.3f}, "
              f"delta={delta['cycles']:.3f} "
              f"({summary['q24_minus_official_core_cycles_percent']:.3f}%), "
              f"negative-launches={summary['negative_core_cycle_launches']}/"
              f"{summary['launches']}")


if __name__ == "__main__":
    main()
