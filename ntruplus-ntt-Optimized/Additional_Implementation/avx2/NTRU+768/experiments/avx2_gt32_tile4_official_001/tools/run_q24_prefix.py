#!/usr/bin/env python3
"""Run the Q24 Decode2/Decode3 first-product composition gate."""

import argparse
import json
import statistics
import subprocess
from pathlib import Path


def summarize(values: list[float]) -> dict[str, float]:
    median = statistics.median(values)
    return {
        "median_tsc": median,
        "mad_tsc": statistics.median(abs(value - median)
                                     for value in values),
    }


def run(binary: Path, iterations: int) -> dict[str, object]:
    process = subprocess.run([str(binary), str(iterations)], check=True,
                             text=True, capture_output=True)
    correct = False
    malformed_cases = 0
    raw: dict[str, dict[str, list[float]]] = {}
    for line in process.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "META":
            correct = "correctness=word-exact-prefix-pass" in line
            for field in fields:
                if field.startswith("malformed_cases="):
                    malformed_cases = int(field.split("=", 1)[1])
        elif fields[0] == "SAMPLE":
            region = raw.setdefault(fields[1], {
                "control": [], "candidate": [], "delta": []})
            region["control"].append(float(fields[3]))
            region["candidate"].append(float(fields[4]))
            region["delta"].append(float(fields[5]))
    expected = {"R0_decode2", "R0_decode3", "R1_prefix2", "R2_prefix3"}
    if not correct or malformed_cases != 2310 or set(raw) != expected:
        raise RuntimeError(f"invalid benchmark output from {binary}")
    return {
        "malformed_cases": malformed_cases,
        "regions": {
            name: {
                "control": summarize(region["control"]),
                "candidate": summarize(region["candidate"]),
                "paired_candidate_minus_control": summarize(region["delta"]),
                "candidate_wins": sum(delta < 0 for delta in region["delta"]),
                "raw": region,
            }
            for name, region in raw.items()
        },
    }


def saving(placement: dict[str, object], region: str) -> float:
    regions = placement["regions"]
    return -regions[region]["paired_candidate_minus_control"]["median_tsc"]


def wins(placement: dict[str, object], region: str) -> int:
    return placement["regions"][region]["candidate_wins"]


def primary_class(placements: dict[str, dict[str, object]]) -> str:
    minimum = min(saving(p, "R2_prefix3") for p in placements.values())
    enough_wins = all(wins(p, "R2_prefix3") >= 18
                      for p in placements.values())
    if minimum >= 140 and enough_wins:
        return "strong-pass-full-decap-decode-only-next"
    if minimum >= 120 and enough_wins:
        return "conditional-pass-full-decap-decode-only-next"
    if minimum >= 100:
        return "composition-loss-requires-pmu-attribution"
    return "hard-stop-q24-prefix-integration"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    placements = {
        "normal": run(args.binary, args.iterations),
        "reversed": run(args.reversed_binary, args.iterations),
    }
    for placement in placements.values():
        s0_2 = saving(placement, "R0_decode2")
        s0_3 = saving(placement, "R0_decode3")
        placement["retention"] = {
            "decode2_prefix_fraction": (
                saving(placement, "R1_prefix2") / s0_2 if s0_2 else None),
            "decode3_prefix_fraction": (
                saving(placement, "R2_prefix3") / s0_3 if s0_3 else None),
        }

    decision = primary_class(placements)
    result = {
        "schema": "ntruplus768-gt32-q24-prefix-short-v1",
        "experiment": "GT32-Q24-PREFIX-COMPOSITION-001",
        "mode": "short",
        "benchmark": {
            "iterations": args.iterations,
            "samples": 20,
            "warmups": 2,
            "cpu": 1,
            "unit": "TSC ticks per region",
            "order": "paired AB/BA",
        },
        "correctness": {
            "status": "pass",
            "valid_prefix_word_exact": True,
            "malformed_prefix_cases": 2310,
            "checks": [
                "canonical-failure-aggregation",
                "c-f-hinv-private-SoA-word-exact",
                "first-product-message-word-exact",
                "scratch-canaries",
                "fixed-work-no-early-return-by-disassembly",
            ],
        },
        "placements": placements,
        "gates": {
            "R1_decode2": {
                "strong_saving_tsc": 90,
                "conditional_saving_tsc": 75,
                "minimum_wins_each_placement": 18,
            },
            "R2_decode3_primary": {
                "strong_saving_tsc": 140,
                "conditional_saving_tsc": 120,
                "attribution_floor_tsc": 100,
                "minimum_wins_each_placement": 18,
            },
        },
        "decision": decision,
        "production_integration": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")

    for name, placement in placements.items():
        print(name)
        for region_name, region in placement["regions"].items():
            delta = region["paired_candidate_minus_control"]
            print(f"  {region_name}: control={region['control']['median_tsc']:.3f}, "
                  f"Q24={region['candidate']['median_tsc']:.3f}, "
                  f"saving={-delta['median_tsc']:.3f}, "
                  f"MAD={delta['mad_tsc']:.3f}, "
                  f"wins={region['candidate_wins']}/20")
        retention = placement["retention"]
        print(f"  retention2={retention['decode2_prefix_fraction']:.3f}, "
              f"retention3={retention['decode3_prefix_fraction']:.3f}")
    print(f"decision={decision}")


if __name__ == "__main__":
    main()
