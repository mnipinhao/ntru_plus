#!/usr/bin/env python3
"""Run the whole-YMM forward identity short gate."""

import argparse
import json
import statistics
import subprocess
from pathlib import Path


def summary(values: list[float]) -> dict[str, float]:
    median = statistics.median(values)
    return {"median_tsc": median,
            "mad_tsc": statistics.median(abs(value - median)
                                         for value in values)}


def run(binary: Path, iterations: int) -> dict[str, object]:
    process = subprocess.run([str(binary), str(iterations)], check=True,
                             text=True, capture_output=True)
    correct = False
    raw: dict[str, dict[str, list[float]]] = {}
    for line in process.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "META":
            correct = "correctness=modq-pass" in line
        elif fields[0] == "SAMPLE":
            gate = raw.setdefault(fields[1], {"control": [],
                                               "candidate": [], "delta": []})
            gate["control"].append(float(fields[3]))
            gate["candidate"].append(float(fields[4]))
            gate["delta"].append(float(fields[5]))
    if not correct or set(raw) != {"core", "full", "two_forward", "chain"}:
        raise RuntimeError(f"invalid output from {binary}")
    return {
        name: {
            "control": summary(gate["control"]),
            "candidate": summary(gate["candidate"]),
            "paired_candidate_minus_control": summary(gate["delta"]),
            "candidate_wins": sum(value < 0 for value in gate["delta"]),
            "raw": gate,
        }
        for name, gate in raw.items()
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    placements = {"normal": run(args.binary, args.iterations),
                  "reversed": run(args.reversed_binary, args.iterations)}
    eligible = all(
        -placement["full"]["paired_candidate_minus_control"]["median_tsc"]
        >= 5 and placement["full"]["candidate_wins"] >= 18
        for placement in placements.values()
    )
    result = {
        "schema": "ntruplus768-gt32-forward-identity-lazy-short-v1",
        "experiment": "GT32-FWD-IDENTITY-LAZY-001",
        "candidate": "F3-S2-center10",
        "benchmark": {"iterations": args.iterations, "samples": 20,
                      "warmups": 2, "cpu": 1,
                      "unit": "TSC ticks per region"},
        "correctness": {"status": "pass", "trials": 1000,
                        "checks": ["forward-mod-q", "out-equals-in",
                                   "2F-R1U-I1-T9-mod-q"]},
        "placements": placements,
        "gate": {"minimum_full_forward_saving_tsc": 5,
                 "minimum_wins_each_placement": 18},
        "decision": ("short-pass" if eligible else
                     "hard-stop-forward-identity-lazy"),
        "production_integration": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for name, placement in placements.items():
        print(name)
        for gate_name, gate in placement.items():
            delta = gate["paired_candidate_minus_control"]
            print(f"  {gate_name}: control={gate['control']['median_tsc']:.3f}, "
                  f"candidate={gate['candidate']['median_tsc']:.3f}, "
                  f"delta={delta['median_tsc']:.3f}, "
                  f"MAD={delta['mad_tsc']:.3f}, "
                  f"wins={gate['candidate_wins']}/20")
    print(f"decision={result['decision']}")


if __name__ == "__main__":
    main()
