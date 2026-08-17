#!/usr/bin/env python3
"""Run the bounded F0 x J1 -> P0 -> Official pack ASM probe."""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
from pathlib import Path


def summary(values: list[float]) -> dict[str, float]:
    median = statistics.median(values)
    return {
        "median_tsc": median,
        "mad_tsc": statistics.median(abs(value - median) for value in values),
    }


def run(binary: Path, iterations: int) -> dict[str, object]:
    process = subprocess.run([str(binary), str(iterations)], check=True,
                             text=True, capture_output=True)
    correctness = False
    values = {"full": {"control": [], "S0": [], "S1": []},
              "route_only": {"control": [], "S0": [], "S1": []}}
    for line in process.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "META":
            correctness = "correctness=bit-exact-pass" in line
        elif fields[0] == "SAMPLE":
            values["full"]["control"].append(float(fields[2]))
            values["full"]["S0"].append(float(fields[3]))
            values["full"]["S1"].append(float(fields[4]))
        elif fields[0] == "ROUTE_SAMPLE":
            values["route_only"]["control"].append(float(fields[2]))
            values["route_only"]["S0"].append(float(fields[3]))
            values["route_only"]["S1"].append(float(fields[4]))
    if not correctness or any(len(item) != 20
                              for region in values.values()
                              for item in region.values()):
        raise RuntimeError(f"invalid output from {binary}")
    result = {}
    for region_name, region in values.items():
        result[region_name] = {name: summary(samples)
                               for name, samples in region.items()}
        for candidate in ("S0", "S1"):
            deltas = [candidate_value - control
                      for candidate_value, control in zip(region[candidate],
                                                           region["control"])]
            result[region_name][candidate]["paired_candidate_minus_control"] = summary(deltas)
            result[region_name][candidate]["wins"] = sum(delta < 0 for delta in deltas)
            result[region_name][candidate]["raw_delta"] = deltas
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", required=True, type=Path)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    placements = {
        "normal": run(args.binary, args.iterations),
        "reversed": run(args.reversed_binary, args.iterations),
    }
    eligible = []
    for candidate in ("S0", "S1"):
        if all(
            -placement["full"][candidate]["paired_candidate_minus_control"]
                ["median_tsc"] >= 15.0
            and placement["full"][candidate]["wins"] >= 18
            for placement in placements.values()
        ):
            eligible.append(candidate)
    decision = (f"short-pass-{eligible[0]}-continue-to-BaseInv-J1-ASM"
                if eligible else
                "hard-stop-bounded-FJ1-to-P0-ASM-no-local-saving")
    result = {
        "schema": "ntruplus768-gt32-keygen-fj1-p0-asm-short-v1",
        "experiment": "GT32-KEYGEN-FJ1-P0-ASM-001",
        "mode": "short",
        "benchmark": {
            "iterations": args.iterations,
            "samples": 20,
            "warmups": 2,
            "cpu": 1,
            "order": "AB/BA paired",
            "unit": "TSC ticks per full F0xJ1->P0->Official-pack edge",
        },
        "control": (
            "J1-AoS->private-SoA; existing e1-SoA x F0-AoS general BM; "
            "AoS->SoA; grouped P0 bridge; unchanged Official pack"),
        "candidates": {
            "S0": "per-R1-source direct two-word P0 fragment redeposit",
            "S1": "four-source half-tile transpose and P0 packet redeposit",
        },
        "correctness": {
            "status": "pass",
            "trials": 1000,
            "checks": ["P0-word-bit-exact", "Official-pack-byte-exact"],
        },
        "placements": placements,
        "gate": {"minimum_saving_tsc": 15, "minimum_wins": 18},
        "eligible": eligible,
        "decision": decision,
        "production_integration": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for placement_name, placement in placements.items():
        full = placement["full"]
        route = placement["route_only"]
        print(f"{placement_name}: control={full['control']['median_tsc']:.3f}")
        for candidate in ("S0", "S1"):
            delta = full[candidate]["paired_candidate_minus_control"]
            route_delta = route[candidate]["paired_candidate_minus_control"]
            print(f"  {candidate}={full[candidate]['median_tsc']:.3f}, "
                  f"delta={delta['median_tsc']:.3f}, "
                  f"MAD={delta['mad_tsc']:.3f}, "
                  f"wins={full[candidate]['wins']}/20; "
                  f"route-only-delta={route_delta['median_tsc']:.3f}")
    print(f"decision={decision}")


if __name__ == "__main__":
    main()
