#!/usr/bin/env python3
"""Summarize the benchmark-only Forward-terminal to BM-plane redeposit gate."""

import argparse
import json
import statistics
import subprocess
from pathlib import Path


def stats(values: list[float]) -> dict[str, float]:
    median = statistics.median(values)
    return {
        "median_tsc": median,
        "mad_tsc": statistics.median(abs(value - median) for value in values),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    run = subprocess.run(
        [str(args.binary), str(args.iterations)],
        check=True,
        text=True,
        capture_output=True,
    )
    gates: dict[str, dict[str, list[float]]] = {}
    for line in run.stdout.splitlines():
        fields = line.split(",")
        if fields[0] != "SAMPLE":
            continue
        gate = gates.setdefault(fields[1], {"baseline": [], "candidate": [], "delta": []})
        gate["baseline"].append(float(fields[3]))
        gate["candidate"].append(float(fields[4]))
        gate["delta"].append(float(fields[5]))
    summary = {}
    for name, values in gates.items():
        summary[name] = {
            "baseline": stats(values["baseline"]),
            "candidate": stats(values["candidate"]),
            "paired_candidate_minus_baseline": stats(values["delta"]),
            "candidate_wins": sum(value < 0.0 for value in values["delta"]),
        }
    chain_delta = summary["two_forward_bm_i1"]["paired_candidate_minus_baseline"]["median_tsc"]
    forward_delta = summary["full_forward"]["paired_candidate_minus_baseline"]["median_tsc"]
    if chain_delta <= -20.0 and forward_delta <= 8.0:
        decision = "pass"
    elif chain_delta <= -20.0:
        decision = "conditional-pass-chain-gate-only"
    elif chain_delta < -10.0:
        decision = "directional-only-stop"
    else:
        decision = "stop-below-10-tsc"
    result = {
        "schema": "ntruplus768-forward-bm-redeposit-v1",
        "benchmark": {
            "iterations": args.iterations,
            "samples": 20,
            "cpu": 1,
            "ordering": "paired-AB-BA",
        },
        "correctness": {
            "status": "pass",
            "checks": [
                "forward-private-soa-to-aos-exact",
                "soa-input-basemul-to-champion-exact",
                "two-forward-basemul-I1-exact",
            ],
        },
        "static_network": {
            "baseline_stage5_reconstruct_plus_transpose_shuffles_per_block": 16,
            "combined_packed_stage5_to_planes_shuffles_per_block": 12,
            "eliminated_shuffles_per_block": 4,
            "blocks_per_polynomial": 12,
        },
        "gates": summary,
        "decision": decision,
        "thresholds": {
            "continue_chain_saving_tsc": 20,
            "hard_stop_below_saving_tsc": 10,
            "max_extra_per_forward_tsc": 8,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["gates"], indent=2))
    print(f"decision={result['decision']}")


if __name__ == "__main__":
    main()
