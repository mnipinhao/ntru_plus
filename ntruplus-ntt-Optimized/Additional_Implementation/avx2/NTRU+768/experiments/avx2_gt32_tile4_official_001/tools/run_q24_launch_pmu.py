#!/usr/bin/env python3
"""Collect same-launch, region-scoped paired PMU data for Q24 decapsulation."""

import argparse
import json
import os
import platform
import statistics
import subprocess
from pathlib import Path

from run_q24_decap import median_mad


GROUPS = ("core", "branches", "frontend", "fetch")


def parse_va(line: str) -> dict[str, int]:
    result = {}
    for field in line.split(",")[1:]:
        key, value = field.split("=", 1)
        result[key] = int(value, 0)
    return result


def run(binary: Path, prefix: list[str], iterations: int,
        group: str) -> dict:
    command = [*prefix, str(binary), str(iterations), "pair"]
    environment = dict(os.environ)
    environment["Q24_SELF_PMU"] = group
    process = subprocess.run(command, check=True, text=True,
                             capture_output=True, env=environment)
    addresses = {}
    samples = []
    counts = {"control": {}, "q24": {}}
    metadata = ""
    for line in process.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "VA":
            addresses = parse_va(line)
        elif fields[0] == "META":
            metadata = line
        elif fields[0] == "PMU_PAIR_SAMPLE":
            samples.append({
                "sample": int(fields[1]),
                "control_tsc": float(fields[2]),
                "q24_tsc": float(fields[3]),
                "q24_minus_control_tsc": float(fields[4]),
            })
        elif fields[0] == "PMU_COUNT":
            counts[fields[1]][fields[2]] = {
                "raw": int(fields[3]),
                "scaled": float(fields[4]),
                "time_enabled": int(fields[5]),
                "time_running": int(fields[6]),
            }
    if (len(samples) != 20
            or "correctness=byte-exact-valid-decap" not in metadata
            or "control-error=0" not in metadata
            or "q24-error=0" not in metadata
            or not counts["control"] or not counts["q24"]):
        raise RuntimeError(f"invalid self-PMU output from {' '.join(command)}")
    total_calls = 20 * iterations
    deltas = {}
    for event in counts["control"].keys() & counts["q24"].keys():
        control = counts["control"][event]["scaled"]
        q24 = counts["q24"][event]["scaled"]
        counts["control"][event]["per_call"] = control / total_calls
        counts["q24"][event]["per_call"] = q24 / total_calls
        deltas[event] = {
            "q24_minus_control_per_call": (q24 - control) / total_calls,
            "q24_minus_control_percent": 100.0 * (q24 - control) / control,
        }
    tsc_values = [sample["q24_minus_control_tsc"] for sample in samples]
    tsc_median, tsc_mad = median_mad(tsc_values)
    result = {
        "command": command,
        "virtual_addresses": addresses,
        "raw_samples": samples,
        "q24_minus_control_tsc": {"median": tsc_median, "mad": tsc_mad},
        "q24_wins_vs_control": sum(value < 0 for value in tsc_values),
        "good_launch": sum(value < 0 for value in tsc_values) >= 18,
        "counts": counts,
        "q24_minus_control": deltas,
        "multiplexed": any(
            event["time_enabled"] != event["time_running"]
            for variant in counts.values() for event in variant.values()),
    }
    if group == "core":
        for variant in ("control", "q24"):
            cycles = counts[variant]["cycles"]["scaled"]
            reference = counts[variant]["ref-cycles"]["scaled"]
            result.setdefault("derived", {}).setdefault(variant, {})[
                "core_cycles_per_ref_cycle"] = cycles / reference
            result["derived"][variant]["ipc"] = (
                counts[variant]["instructions"]["scaled"] / cycles)
    return result


def classified_summary(launches: list[dict]) -> dict:
    result = {}
    for label, members in (
            ("good", [entry for entry in launches if entry["good_launch"]]),
            ("bad", [entry for entry in launches if not entry["good_launch"]])):
        if not members:
            result[label] = {"launches": 0}
            continue
        events = members[0]["q24_minus_control"].keys()
        result[label] = {
            "launches": len(members),
            "median_delta_tsc": statistics.median(
                entry["q24_minus_control_tsc"]["median"]
                for entry in members),
            "median_event_deltas_per_call": {
                event: statistics.median(
                    entry["q24_minus_control"][event][
                        "q24_minus_control_per_call"]
                    for entry in members)
                for event in events
            },
        }
        if "derived" in members[0]:
            result[label]["median_frequency_ratio"] = {
                variant: statistics.median(
                    entry["derived"][variant]["core_cycles_per_ref_cycle"]
                    for entry in members)
                for variant in ("control", "q24")
            }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", type=Path, required=True)
    parser.add_argument("--nonpie-binary", type=Path, required=True)
    parser.add_argument("--nonpie-reversed-binary", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--launches", type=int, default=8)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    machine = platform.machine()
    modes = {
        "pie_aslr_on": ({"normal": args.binary,
                         "reversed": args.reversed_binary}, []),
        "pie_aslr_disabled": ({"normal": args.binary,
                               "reversed": args.reversed_binary},
                              ["setarch", machine, "-R"]),
        "nonpie_fixed_address": ({"normal": args.nonpie_binary,
                                  "reversed": args.nonpie_reversed_binary},
                                 []),
    }
    measurements = {}
    for mode_name, (binaries, prefix) in modes.items():
        mode_data = {}
        for placement, binary in binaries.items():
            group_data = {}
            for group in GROUPS:
                launches = [run(binary, prefix, args.iterations, group)
                            for _ in range(args.launches)]
                group_data[group] = {
                    "launches": launches,
                    "classified": classified_summary(launches),
                    "good_launches": sum(entry["good_launch"]
                                         for entry in launches),
                    "all_nonmultiplexed": not any(
                        entry["multiplexed"] for entry in launches),
                }
            mode_data[placement] = group_data
        measurements[mode_name] = mode_data

    result = {
        "schema": "ntruplus768-gt32-q24-launch-pmu-v1",
        "experiment": "GT32-Q24-LAUNCH-PMU-001",
        "benchmark": {
            "iterations_per_sample": args.iterations,
            "samples_per_launch": 20,
            "launches_per_group_placement_mode": args.launches,
            "cpu": 1,
            "order": "same-process paired AB/BA",
            "counter_scope": "only each measured decapsulation loop",
            "groups": list(GROUPS),
            "aperf_mperf": "unavailable-per-thread; core/ref cycles used",
            "serious_100k": False,
        },
        "measurements": measurements,
        "q24_assembly_modified": False,
        "production_integration": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for mode_name, mode in measurements.items():
        print(mode_name)
        for placement, groups in mode.items():
            core = groups["core"]
            frontend = groups["frontend"]
            print(f"  {placement}: core good={core['good_launches']}/"
                  f"{args.launches}, frontend good="
                  f"{frontend['good_launches']}/{args.launches}")


if __name__ == "__main__":
    main()
