#!/usr/bin/env python3
"""Compare the production-promoted Q24 GT32 decap with Official Main."""

import argparse
import json
import statistics
import subprocess
from pathlib import Path


def median_mad(values: list[float]) -> tuple[float, float]:
    median = statistics.median(values)
    mad = statistics.median(abs(value - median) for value in values)
    return median, mad


def run_launch(binary: Path, iterations: int) -> dict[str, object]:
    command = [str(binary), str(iterations), "production"]
    process = subprocess.run(command, check=True, text=True,
                             capture_output=True)
    records = []
    addresses = {}
    valid = False
    for line in process.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "VA":
            addresses = {
                key: int(value, 0)
                for key, value in (field.split("=", 1)
                                   for field in fields[1:])
            }
        elif fields[0] == "META":
            valid = ("correctness=byte-exact-valid-decap" in line
                     and "scope=production-promoted-q24-vs-official" in line)
        elif fields[0] == "PRODUCTION_SAMPLE":
            records.append({
                "sample": int(fields[1]),
                "official_tsc": float(fields[2]),
                "promoted_q24_tsc": float(fields[3]),
                "promoted_minus_official_tsc": float(fields[4]),
            })
    if not valid or len(records) != 20:
        raise RuntimeError(f"invalid benchmark output from {binary}")
    result: dict[str, object] = {
        "command": command,
        "virtual_addresses": addresses,
        "raw": records,
    }
    for field in ("official_tsc", "promoted_q24_tsc",
                  "promoted_minus_official_tsc"):
        median, mad = median_mad([record[field] for record in records])
        result[field] = {"median": median, "mad": mad}
    result["promoted_wins"] = sum(
        record["promoted_minus_official_tsc"] < 0 for record in records)
    return result


def summarize(launches: list[dict[str, object]]) -> dict[str, object]:
    records = [record for launch in launches for record in launch["raw"]]
    launch_deltas = [
        launch["promoted_minus_official_tsc"]["median"]
        for launch in launches
    ]
    official_launches = [launch["official_tsc"]["median"]
                         for launch in launches]
    promoted_launches = [launch["promoted_q24_tsc"]["median"]
                         for launch in launches]
    delta_median, delta_mad = median_mad(launch_deltas)
    official_median, official_mad = median_mad(official_launches)
    promoted_median, promoted_mad = median_mad(promoted_launches)
    aggregate_delta, aggregate_delta_mad = median_mad([
        record["promoted_minus_official_tsc"] for record in records])
    return {
        "primary_hierarchical_launch_medians": {
            "official_tsc": {"median": official_median,
                             "mad": official_mad},
            "promoted_q24_tsc": {"median": promoted_median,
                                 "mad": promoted_mad},
            "promoted_minus_official_tsc": {"median": delta_median,
                                             "mad": delta_mad},
            "promoted_minus_official_percent":
                100.0 * delta_median / official_median,
        },
        "pooled_paired_samples": {
            "promoted_minus_official_tsc": {"median": aggregate_delta,
                                             "mad": aggregate_delta_mad},
            "promoted_wins": sum(
                record["promoted_minus_official_tsc"] < 0
                for record in records),
            "samples": len(records),
        },
        "negative_delta_launches": sum(delta < 0 for delta in launch_deltas),
        "launches": len(launches),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--launches", type=int, default=8)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    placements = {}
    for name, binary in (("normal", args.binary),
                         ("reversed", args.reversed_binary)):
        launches = [run_launch(binary, args.iterations)
                    for _ in range(args.launches)]
        placements[name] = {
            "launch_data": launches,
            "summary": summarize(launches),
        }

    all_faster = all(
        placement["summary"]["negative_delta_launches"] == args.launches
        for placement in placements.values())
    result = {
        "schema": "ntruplus768-gt32-q24-production-official-short-v1",
        "experiment": "GT32-Q24-PRODUCTION-OFFICIAL-001",
        "promotion": {
            "candidate_symbol": "crypto_kem_dec_gt32_candidate",
            "decode_contract": "Q24 GT-unpack3 to persistent private SoA",
            "public_backend_default": "Official Main",
            "scope": "GT32 decapsulation candidate only",
        },
        "benchmark": {
            "iterations_per_sample": args.iterations,
            "samples_per_launch": 20,
            "launches_per_placement": args.launches,
            "cpu": 1,
            "unit": "TSC ticks per decapsulation",
            "order": "same-binary paired AB/BA",
            "serious_100k": False,
        },
        "placements": placements,
        "decision": ("promoted-q24-short-faster-than-official"
                     if all_faster else
                     "q24-production-promoted-but-backend-not-faster"),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for name, placement in placements.items():
        summary = placement["summary"]
        primary = summary["primary_hierarchical_launch_medians"]
        print(f"{name}: Official={primary['official_tsc']['median']:.3f} "
              f"Q24={primary['promoted_q24_tsc']['median']:.3f} "
              f"delta={primary['promoted_minus_official_tsc']['median']:.3f} "
              f"({primary['promoted_minus_official_percent']:.3f}%) "
              f"negative-launches={summary['negative_delta_launches']}/"
              f"{summary['launches']}")
    print(f"decision={result['decision']}")


if __name__ == "__main__":
    main()
