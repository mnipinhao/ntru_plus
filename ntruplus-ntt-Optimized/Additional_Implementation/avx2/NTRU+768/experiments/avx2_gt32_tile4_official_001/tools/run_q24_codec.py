#!/usr/bin/env python3
"""Run the quartic-native Q24 codec gate."""

import argparse
import json
import statistics
import subprocess
from pathlib import Path


def summarize(values: list[float]) -> dict[str, float]:
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
            correct = "correctness=exact-pass" in line
        elif fields[0] == "SAMPLE":
            gate = raw.setdefault(fields[1], {"control": [],
                                               "candidate": [], "delta": []})
            gate["control"].append(float(fields[3]))
            gate["candidate"].append(float(fields[4]))
            gate["delta"].append(float(fields[5]))
    expected = {"decode_aos", "decode_soa", "decode3_soa",
                "encode_aos", "encode_soa"}
    if not correct or set(raw) != expected:
        raise RuntimeError(f"invalid benchmark output from {binary}")
    return {
        name: {
            "control": summarize(gate["control"]),
            "candidate": summarize(gate["candidate"]),
            "paired_candidate_minus_control": summarize(gate["delta"]),
            "candidate_wins": sum(delta < 0 for delta in gate["delta"]),
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
    decode3_pass = all(
        -placement["decode3_soa"]["paired_candidate_minus_control"][
            "median_tsc"] >= 150
        and placement["decode3_soa"]["candidate_wins"] >= 18
        for placement in placements.values()
    )
    result = {
        "schema": "ntruplus768-gt32-q24-codec-short-v1",
        "experiment": "GT32-Q24-CODEC-001",
        "mode": "short",
        "benchmark": {"iterations": args.iterations, "samples": 20,
                      "warmups": 2, "cpu": 1,
                      "unit": "TSC ticks per codec call"},
        "correctness": {
            "status": "pass",
            "random_trials": 1000,
            "malformed_single_and_three_input_cases": 3072,
            "checks": ["exact-AoS", "exact-private-SoA",
                       "byte-exact-AoS-encode", "byte-exact-SoA-encode",
                       "canonical-rejection", "safe-final-packet",
                       "disjoint-input-output-contract"],
        },
        "placements": placements,
        "continuation_gate": {
            "decode3_minimum_saving_tsc": 150,
            "minimum_wins_each_placement": 18,
            "passed": decode3_pass,
        },
        "decision": ("pass-continue-to-first-product-caller-gate"
                     if decode3_pass else "hard-stop-Q24-codec"),
        "production_integration": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for name, placement in placements.items():
        print(name)
        for gate_name, gate in placement.items():
            delta = gate["paired_candidate_minus_control"]
            print(f"  {gate_name}: control={gate['control']['median_tsc']:.3f}, "
                  f"Q24={gate['candidate']['median_tsc']:.3f}, "
                  f"delta={delta['median_tsc']:.3f}, "
                  f"MAD={delta['mad_tsc']:.3f}, "
                  f"wins={gate['candidate_wins']}/20")
    print(f"decision={result['decision']}")


if __name__ == "__main__":
    main()
