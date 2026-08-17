#!/usr/bin/env python3
"""Run the GT32 persistent-SoA dot/REDC16 BaseMul short gate."""

from __future__ import annotations

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
    correctness = False
    raw: dict[str, dict[str, list[float]]] = {}
    for line in process.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "META":
            correctness = "correctness=modq-pass" in line
        elif fields[0] == "SAMPLE":
            gate = raw.setdefault(fields[1], {"control": [],
                                               "candidate": [], "delta": []})
            gate["control"].append(float(fields[3]))
            gate["candidate"].append(float(fields[4]))
            gate["delta"].append(float(fields[5]))
    if not correctness or any(len(gate["delta"]) != 20 for gate in raw.values()):
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
    parser.add_argument("--reversed-binary", required=True, type=Path)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    placements = {"normal": run(args.binary, args.iterations),
                  "reversed": run(args.reversed_binary, args.iterations)}
    eligible = any(all(
        -placement[gate]["paired_candidate_minus_control"]["median_tsc"] >= 15
        and placement[gate]["candidate_wins"] >= 18
        for placement in placements.values()) for gate in ("arithmetic", "full"))
    decision = ("short-pass-continue-to-general-e0"
                if eligible else
                "hard-stop-SoA-dot-REDC16-private-kernel")
    result = {
        "schema": "ntruplus768-gt32-bm-soa-dot-redc16-short-v1",
        "experiment": "GT32-BM-SOA-DOT-REDC16-001",
        "mode": "short",
        "benchmark": {"iterations": args.iterations, "samples": 20,
                      "warmups": 2, "cpu": 1,
                      "unit": "TSC ticks per kernel/region"},
        "correctness": {"status": "pass", "trials": 1000,
                        "checks": ["SoA-arithmetic-mod-q",
                                   "current-I1-input-mod-q", "I1", "T9"]},
        "placements": placements,
        "gate": {"minimum_saving_tsc": 15,
                 "minimum_wins_each_placement": 18},
        "decision": decision,
        "general_e0_implemented": False,
        "production_integration": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for placement_name, placement in placements.items():
        print(placement_name)
        for gate_name, gate in placement.items():
            delta = gate["paired_candidate_minus_control"]
            print(f"  {gate_name}: control={gate['control']['median_tsc']:.3f}, "
                  f"dot={gate['candidate']['median_tsc']:.3f}, "
                  f"delta={delta['median_tsc']:.3f}, "
                  f"MAD={delta['mad_tsc']:.3f}, "
                  f"wins={gate['candidate_wins']}/20")
    print(f"decision={decision}")


if __name__ == "__main__":
    main()
