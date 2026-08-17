#!/usr/bin/env python3
"""Collect launch-level paired PMU evidence for recovered-r Q24 GT-pack."""

import argparse
import json
import math
import os
import random
import statistics
import subprocess
from pathlib import Path


GROUPS = ("core", "memory")


def bootstrap_median_ci(values: list[float], resamples: int,
                        seed: int) -> dict[str, float | int]:
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


def run_launch(binary: Path, iterations: int, group: str) -> dict[str, object]:
    command = [str(binary), str(iterations), "gtpack-pair"]
    environment = dict(os.environ)
    environment["Q24_SELF_PMU"] = group
    process = subprocess.run(command, check=True, text=True,
                             capture_output=True, env=environment)
    counts: dict[str, dict[str, dict[str, int | float]]] = {
        "unpack-only": {}, "gtpack": {}}
    tsc_deltas = []
    valid = False
    for line in process.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "META":
            valid = ("pmu-region=paired-unpack-only-gtpack" in line
                     and "unpack-only-error=0" in line
                     and "gtpack-error=0" in line)
        elif fields[0] == "GTPACK_PMU_PAIR_SAMPLE":
            tsc_deltas.append(float(fields[4]))
        elif fields[0] == "PMU_COUNT":
            counts[fields[1]][fields[2]] = {
                "raw": int(fields[3]),
                "scaled": float(fields[4]),
                "time_enabled": int(fields[5]),
                "time_running": int(fields[6]),
            }
    if (not valid or len(tsc_deltas) != 20
            or not counts["unpack-only"] or not counts["gtpack"]):
        raise RuntimeError(f"invalid GT-pack PMU output from {binary}")
    calls = 20 * iterations
    per_call = {
        variant: {event: data["scaled"] / calls
                  for event, data in events.items()}
        for variant, events in counts.items()
    }
    common_events = per_call["unpack-only"].keys() & per_call["gtpack"].keys()
    deltas = {event: per_call["gtpack"][event]
                     - per_call["unpack-only"][event]
              for event in common_events}
    result: dict[str, object] = {
        "command": command,
        "group": group,
        "counts": counts,
        "per_call": per_call,
        "gtpack_minus_unpack_only_per_call": deltas,
        "paired_tsc_median": statistics.median(tsc_deltas),
        "paired_tsc_wins": sum(value < 0 for value in tsc_deltas),
        "multiplexed": any(
            data["time_enabled"] != data["time_running"]
            for events in counts.values() for data in events.values()),
    }
    if group == "core":
        result["derived"] = {
            variant: {
                "cycles_per_instruction": (
                    per_call[variant]["cycles"]
                    / per_call[variant]["instructions"]),
                "core_cycles_per_ref_cycle": (
                    per_call[variant]["cycles"]
                    / per_call[variant]["ref-cycles"]),
            }
            for variant in ("unpack-only", "gtpack")
        }
    return result


def summarize(launches: list[dict[str, object]], group: str,
              resamples: int, seed: int) -> dict[str, object]:
    events = launches[0]["gtpack_minus_unpack_only_per_call"].keys()
    event_deltas = {
        event: [launch["gtpack_minus_unpack_only_per_call"][event]
                for launch in launches]
        for event in events
    }
    result: dict[str, object] = {
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
            for variant in ("unpack-only", "gtpack")
        },
        "median_gtpack_minus_unpack_only_per_call": {
            event: statistics.median(values)
            for event, values in event_deltas.items()
        },
        "negative_event_launches": {
            event: sum(value < 0 for value in values)
            for event, values in event_deltas.items()
        },
        "event_bootstrap_median_95ci": {
            event: bootstrap_median_ci(values, resamples,
                                       seed + event_index)
            for event_index, (event, values) in enumerate(
                sorted(event_deltas.items()))
        },
    }
    if group == "core":
        result["median_derived"] = {
            variant: {
                key: statistics.median(
                    launch["derived"][variant][key] for launch in launches)
                for key in ("cycles_per_instruction",
                            "core_cycles_per_ref_cycle")
            }
            for variant in ("unpack-only", "gtpack")
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--launches", type=int, default=32)
    parser.add_argument("--bootstrap-resamples", type=int, default=100000)
    parser.add_argument("--bootstrap-seed", type=int, default=241768)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    placements = {}
    for placement_index, (placement, binary) in enumerate((
            ("normal", args.binary),
            ("reversed", args.reversed_binary))):
        group_data = {}
        for group_index, group in enumerate(GROUPS):
            launches = [run_launch(binary, args.iterations, group)
                        for _ in range(args.launches)]
            group_data[group] = {
                "launch_data": launches,
                "summary": summarize(
                    launches, group, args.bootstrap_resamples,
                    args.bootstrap_seed + 100 * placement_index
                    + 10 * group_index),
            }
        placements[placement] = group_data

    core_pass = all(
        data["core"]["summary"]
            ["median_gtpack_minus_unpack_only_per_call"]["cycles"] < 0.0
        and data["core"]["summary"]["event_bootstrap_median_95ci"]
            ["cycles"]["upper"] < 0.0
        for data in placements.values())
    result = {
        "schema": "ntruplus768-gt32-q24-recovered-r-gtpack-pmu-v1",
        "experiment": "GT32-Q24-RECOVERED-R-GTPACK-PMU-001",
        "benchmark": {
            "iterations_per_sample": args.iterations,
            "samples_per_launch": 20,
            "launches_per_group_placement": args.launches,
            "cpu": 1,
            "counter_scope": "paired full-decapsulation loops only",
            "event_groups": list(GROUPS),
            "bootstrap_resamples": args.bootstrap_resamples,
        },
        "placements": placements,
        "core_cycle_corroboration_gate": {
            "median_cycles_must_be_negative": True,
            "bootstrap_95ci_upper_must_be_negative": True,
            "negative_launch_fraction_is_diagnostic_only": True,
        },
        "core_cycle_corroboration_passed": core_pass,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for placement, data in placements.items():
        core = data["core"]["summary"]
        memory = data["memory"]["summary"]
        delta = core["median_gtpack_minus_unpack_only_per_call"]
        memory_delta = memory["median_gtpack_minus_unpack_only_per_call"]
        ci = core["event_bootstrap_median_95ci"]["cycles"]
        print(f"{placement}: cycles={delta['cycles']:.3f} "
              f"instructions={delta['instructions']:.3f} "
              f"cycle-wins={core['negative_event_launches']['cycles']}/"
              f"{args.launches} cycle-bootstrap95ci=[{ci['lower']:.3f},"
              f"{ci['upper']:.3f}] loads={memory_delta['retired-loads']:.3f} "
              f"stores={memory_delta['retired-stores']:.3f}")
    print(f"core-cycle-corroboration-pass={core_pass}")


if __name__ == "__main__":
    main()
