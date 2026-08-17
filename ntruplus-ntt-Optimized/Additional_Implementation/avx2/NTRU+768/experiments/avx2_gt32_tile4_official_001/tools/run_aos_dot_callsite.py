#!/usr/bin/env python3
"""Run the caller-honest GT32 R1-U decapsulation first-product gate."""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
from pathlib import Path


def summarize(values: list[float]) -> dict[str, float]:
    median = statistics.median(values)
    return {
        "median_tsc": median,
        "mad_tsc": statistics.median(abs(value - median) for value in values),
    }


def run_binary(binary: Path, iterations: int) -> dict[str, object]:
    process = subprocess.run(
        [str(binary), str(iterations)], check=True, text=True,
        capture_output=True)
    correctness = False
    metadata = ""
    raw: dict[str, dict[str, list[float]]] = {}
    for line in process.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "META":
            metadata = line
            correctness = "correctness=pass" in fields
        elif fields[0] == "SAMPLE":
            gate = raw.setdefault(fields[1], {
                "baseline": [], "candidate": [], "delta": []})
            gate["baseline"].append(float(fields[3]))
            gate["candidate"].append(float(fields[4]))
            gate["delta"].append(float(fields[5]))
    if not correctness or any(len(values["delta"]) != 20
                              for values in raw.values()):
        raise RuntimeError(f"invalid benchmark output from {binary}")
    return {
        "metadata": metadata,
        "gates": {
            name: {
                "baseline": summarize(values["baseline"]),
                "candidate": summarize(values["candidate"]),
                "paired_candidate_minus_baseline": summarize(values["delta"]),
                "candidate_wins": sum(delta < 0.0
                                      for delta in values["delta"]),
                "raw": values,
            }
            for name, values in raw.items()
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", required=True, type=Path)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    placements = {
        "normal": run_binary(args.binary, args.iterations),
        "reversed": run_binary(args.reversed_binary, args.iterations),
    }
    primary = "decap_state_r1u_vs_ss"
    primary_pass = all(
        -placement["gates"][primary]
        ["paired_candidate_minus_baseline"]["median_tsc"] >= 20.0
        and placement["gates"][primary]["candidate_wins"] >= 18
        for placement in placements.values())
    primary_positive = all(
        placement["gates"][primary]
        ["paired_candidate_minus_baseline"]["median_tsc"] < 0.0
        for placement in placements.values())
    if primary_pass:
        decision = "short-pass-R1-U-decap-first-product-await-serious"
    elif primary_positive:
        decision = "inconclusive-R1-U-decap-first-product"
    else:
        decision = "stop-R1-U-decap-integration-decoder-debt"

    forward_gate = "forward_native_r1u_vs_b3"
    forward_pass = all(
        -placement["gates"][forward_gate]
        ["paired_candidate_minus_baseline"]["median_tsc"] >= 20.0
        and placement["gates"][forward_gate]["candidate_wins"] >= 18
        for placement in placements.values())
    forward_positive = all(
        placement["gates"][forward_gate]
        ["paired_candidate_minus_baseline"]["median_tsc"] < 0.0
        for placement in placements.values())
    if forward_pass:
        forward_decision = "short-pass-Forward-native-R1-U-await-serious"
    elif forward_positive:
        forward_decision = "inconclusive-Forward-native-R1-U"
    else:
        forward_decision = "stop-Forward-native-R1-U"

    accounting = {}
    for name, placement in placements.items():
        gates = placement["gates"]
        decoder_debt = gates["decoder3_mixed_vs_ss"] \
            ["paired_candidate_minus_baseline"]["median_tsc"]
        arithmetic_delta = gates["arithmetic_r1u_vs_ss"] \
            ["paired_candidate_minus_baseline"]["median_tsc"]
        observed = gates[primary]["paired_candidate_minus_baseline"] \
            ["median_tsc"]
        accounting[name] = {
            "mixed_decoder_debt_tsc": decoder_debt,
            "R1U_arithmetic_chain_saving_tsc": -arithmetic_delta,
            "additive_predicted_candidate_minus_control_tsc":
                decoder_debt + arithmetic_delta,
            "observed_candidate_minus_control_tsc": observed,
            "closure_error_tsc": observed - (decoder_debt + arithmetic_delta),
        }

    result = {
        "schema": "ntruplus768-gt32-aos-dot-callsite-v1",
        "experiment": "GT32-AOS-DOT-REDC16-CALLSITE-001",
        "mode": "short",
        "benchmark": {
            "iterations": args.iterations,
            "samples": 20,
            "warmups": 2,
            "cpu": 1,
            "ordering": "ABBA/BAAB",
            "placements": ["normal", "reversed-link-order"],
            "unit": "TSC ticks per region",
        },
        "correctness": {
            "status": "pass",
            "valid_trials": 1000,
            "malformed_positions_per_input": 3,
            "checks": [
                "combined-mixed-decoder-aggregate-rejection",
                "mixed-c-and-f-AoS-deposits-bit-exact-to-AoS-decoder",
                "persistent-hinv-private-SoA-bit-exact",
                "R1-U-first-product-through-I1-T9-crepmod3-exact",
                "two-Forward-R1-U-through-I1-T9-crepmod3-exact",
            ],
        },
        "control": (
            "Decode3(c,f,hinv)->private-SoA; SS scale-B3; "
            "I1; T9; crepmod3"),
        "candidate": (
            "Decode(c,f)->TILE4-AoS and hinv->private-SoA in one decoder; "
            "R1-U; I1; T9; crepmod3"),
        "placements": placements,
        "accounting": accounting,
        "threshold": {
            "minimum_primary_saving_tsc": 20,
            "minimum_wins_each_placement": 18,
        },
        "decision": decision,
        "forward_native_decision": forward_decision,
        "production_integration": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for name, placement in placements.items():
        gate = placement["gates"][primary]
        delta = gate["paired_candidate_minus_baseline"]
        print(
            f"{name}: control={gate['baseline']['median_tsc']:.3f}, "
            f"R1-U={gate['candidate']['median_tsc']:.3f}, "
            f"delta={delta['median_tsc']:.3f}, "
            f"MAD={delta['mad_tsc']:.3f}, "
            f"wins={gate['candidate_wins']}/20")
        print(
            f"  decoder-debt={accounting[name]['mixed_decoder_debt_tsc']:.3f}, "
            f"arithmetic-saving="
            f"{accounting[name]['R1U_arithmetic_chain_saving_tsc']:.3f}")
        forward = placement["gates"][forward_gate]
        print(
            f"  Forward-native: B3={forward['baseline']['median_tsc']:.3f}, "
            f"R1-U={forward['candidate']['median_tsc']:.3f}, "
            f"delta={forward['paired_candidate_minus_baseline']['median_tsc']:.3f}, "
            f"wins={forward['candidate_wins']}/20")
    print(f"decision={decision}")
    print(f"forward-native-decision={forward_decision}")


if __name__ == "__main__":
    main()
