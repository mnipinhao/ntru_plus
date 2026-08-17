#!/usr/bin/env python3
"""Run the Q24 Decode3-only full-decapsulation short gate."""

import argparse
import json
import statistics
import subprocess
from pathlib import Path


def median_mad(values: list[float]) -> tuple[float, float]:
    median = statistics.median(values)
    mad = statistics.median(abs(value - median) for value in values)
    return median, mad


def run(binary: Path, iterations: int,
        command_prefix: list[str] | None = None) -> dict[str, object]:
    command = [*(command_prefix or []), str(binary), str(iterations)]
    process = subprocess.run(command, check=True,
                             text=True, capture_output=True)
    correct = False
    records = []
    virtual_addresses = {}
    for line in process.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "VA":
            for field in fields[1:]:
                key, value = field.split("=", 1)
                virtual_addresses[key] = int(value, 0)
        elif fields[0] == "META":
            correct = "correctness=byte-exact-valid-decap" in line
        elif fields[0] == "SAMPLE":
            records.append({
                "sample": int(fields[1]),
                "official_tsc": float(fields[2]),
                "control_tsc": float(fields[3]),
                "q24_tsc": float(fields[4]),
                "q24_minus_control_tsc": float(fields[5]),
                "q24_minus_official_tsc": float(fields[6]),
            })
    if not correct or len(records) != 20:
        raise RuntimeError(f"invalid benchmark output from {binary}")
    result: dict[str, object] = {
        "raw": records,
        "virtual_addresses": virtual_addresses,
        "command": command,
    }
    for field in ("official_tsc", "control_tsc", "q24_tsc",
                  "q24_minus_control_tsc", "q24_minus_official_tsc"):
        median, mad = median_mad([record[field] for record in records])
        result[field] = {"median": median, "mad": mad}
    result["q24_wins_vs_control"] = sum(
        record["q24_minus_control_tsc"] < 0 for record in records)
    result["q24_wins_vs_official"] = sum(
        record["q24_minus_official_tsc"] < 0 for record in records)
    return result


def aggregate(launches: list[dict[str, object]]) -> dict[str, object]:
    records = [record for launch in launches for record in launch["raw"]]
    result: dict[str, object] = {"raw": records}
    for field in ("official_tsc", "control_tsc", "q24_tsc",
                  "q24_minus_control_tsc", "q24_minus_official_tsc"):
        median, mad = median_mad([record[field] for record in records])
        result[field] = {"median": median, "mad": mad}
    result["q24_wins_vs_control"] = sum(
        record["q24_minus_control_tsc"] < 0 for record in records)
    result["q24_wins_vs_official"] = sum(
        record["q24_minus_official_tsc"] < 0 for record in records)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--launches", type=int, default=2)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    placements = {}
    for name, binary in (("normal", args.binary),
                         ("reversed", args.reversed_binary)):
        launches = [run(binary, args.iterations)
                    for _ in range(args.launches)]
        placements[name] = {
            "launches": launches,
            "aggregate": aggregate(launches),
        }
    strong = all(
        -launch["q24_minus_control_tsc"]["median"] >= 120
        and launch["q24_wins_vs_control"] >= 18
        for placement in placements.values()
        for launch in placement["launches"]
    )
    positive = all(
        launch["q24_minus_control_tsc"]["median"] < 0
        for placement in placements.values()
        for launch in placement["launches"]
    )
    decision = ("strong-pass-q24-encoder-gates-next" if strong else
                "placement-sensitive-conditional-pass" if positive else
                "hard-stop-q24-full-decap-decode-only")
    result = {
        "schema": "ntruplus768-gt32-q24-decap-decode-only-short-v1",
        "experiment": "GT32-Q24-DECAP-DECODE-ONLY-001",
        "mode": "short",
        "benchmark": {
            "iterations": args.iterations,
            "samples": 20,
            "warmups": 2,
            "launches": args.launches,
            "cpu": 1,
            "unit": "TSC ticks per decapsulation",
            "order": "paired ABC/CBA",
        },
        "correctness": {
            "valid_byte_exact": True,
            "eight_round_malformed_and_trace_suite": "external-make-check",
        },
        "placements": placements,
        "continuation_gate": {
            "strong_saving_vs_control_tsc": 120,
            "minimum_wins_each_placement": 18,
            "passed": strong,
        },
        "decision": decision,
        "production_integration": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for name, placement in placements.items():
        print(name)
        for index, launch in enumerate(placement["launches"]):
            print(f"  launch{index + 1}: Official="
                  f"{launch['official_tsc']['median']:.3f}, "
                  f"control={launch['control_tsc']['median']:.3f}, "
                  f"Q24={launch['q24_tsc']['median']:.3f}")
            print(f"    Q24-control="
                  f"{launch['q24_minus_control_tsc']['median']:.3f}, "
                  f"MAD={launch['q24_minus_control_tsc']['mad']:.3f}, "
                  f"wins={launch['q24_wins_vs_control']}/20")
            print(f"    Q24-Official="
                  f"{launch['q24_minus_official_tsc']['median']:.3f}, "
                  f"wins={launch['q24_wins_vs_official']}/20")
        summary = placement["aggregate"]
        print(f"  aggregate Q24-control="
              f"{summary['q24_minus_control_tsc']['median']:.3f}, "
              f"wins={summary['q24_wins_vs_control']}/"
              f"{20 * args.launches}")
    print(f"decision={decision}")


if __name__ == "__main__":
    main()
