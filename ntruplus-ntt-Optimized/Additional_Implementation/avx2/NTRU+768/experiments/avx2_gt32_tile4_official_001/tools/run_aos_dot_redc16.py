#!/usr/bin/env python3
"""Run the bounded short GT32 AoS-dot REDC16 experiment."""

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


def run_binary(binary: Path, iterations: int) -> dict[str, dict]:
    run = subprocess.run(
        [str(binary), str(iterations)], check=True, text=True,
        capture_output=True)
    correctness = False
    raw: dict[str, dict[str, list[float]]] = {}
    for line in run.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "META":
            correctness = "correctness=pass" in fields
        elif fields[0] == "SAMPLE":
            gate = raw.setdefault(fields[1], {
                "baseline": [], "candidate": [], "delta": []})
            gate["baseline"].append(float(fields[3]))
            gate["candidate"].append(float(fields[4]))
            gate["delta"].append(float(fields[5]))
    if not correctness or not raw:
        raise RuntimeError(f"missing correctness/sample output from {binary}")
    return {
        name: {
            "baseline": summarize(values["baseline"]),
            "candidate": summarize(values["candidate"]),
            "paired_candidate_minus_baseline": summarize(values["delta"]),
            "candidate_wins": sum(value < 0.0 for value in values["delta"]),
        }
        for name, values in raw.items()
    }


def variant_status(placements: dict[str, dict], variant: str) -> dict:
    a1_bm = f"a1_vs_{variant}_bm"
    b3_bm = f"b3_vs_{variant}_bm"
    b3_i1 = f"b3_vs_{variant}_i1"
    saving_gate = all(
        -run[a1_bm]["paired_candidate_minus_baseline"]["median_tsc"] >= 70.0
        and run[a1_bm]["candidate_wins"] >= 18
        for run in placements.values())
    family_gate = all(
        run[a1_bm]["candidate"]["median_tsc"] <= 450.0
        for run in placements.values())
    forward_terminal_gate = all(
        run[a1_bm]["candidate"]["median_tsc"] <= 430.0
        for run in placements.values())
    same_binary_production_comparison = all(
        (run[b3_bm]["candidate"]["median_tsc"]
         < run[b3_bm]["baseline"]["median_tsc"])
        or (run[b3_i1]["candidate"]["median_tsc"]
            < run[b3_i1]["baseline"]["median_tsc"])
        for run in placements.values())
    historical_bm_gate = all(
        run[a1_bm]["candidate"]["median_tsc"] < 397.222
        for run in placements.values())
    historical_i1_gate = all(
        run[f"a1_vs_{variant}_i1"]["candidate"]["median_tsc"] < 628.798
        for run in placements.values())
    return {
        "saves_at_least_70_tsc_with_18_of_20_wins": saving_gate,
        "family_continue_at_or_below_450_tsc": family_gate,
        "forward_terminal_extension_at_or_below_430_tsc":
            forward_terminal_gate,
        "beats_same_binary_B3_or_B3_plus_I1":
            same_binary_production_comparison,
        "historical_BM_below_397_222_all_placements": historical_bm_gate,
        "historical_BM_plus_I1_below_628_798_all_placements":
            historical_i1_gate,
        "historical_production_gate": historical_bm_gate or historical_i1_gate,
        "passes_continuation_gates": (
            saving_gate and family_gate and forward_terminal_gate
            and same_binary_production_comparison),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", required=True, type=Path)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--mode", choices=("short", "serious"),
                        default="short")
    parser.add_argument("--static-gate", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    placements = {
        "normal": run_binary(args.binary, args.iterations),
        "reversed": run_binary(args.reversed_binary, args.iterations),
    }
    statuses = {
        "R1-U": variant_status(placements, "r1u"),
        "R1-S": variant_status(placements, "r1s"),
    }
    eligible = [name for name, status in statuses.items()
                if status["passes_continuation_gates"]]
    # R1-U is preferred on a tie because it preserves A1 representatives.
    champion = "R1-U" if "R1-U" in eligible else (
        "R1-S" if "R1-S" in eligible else None)
    if champion is None:
        decision = "stop-AoS-dot-REDC16-family"
    else:
        # This harness proves the AoS scale-BM primitive and its private
        # inverse consumer.  KEM selection additionally depends on operand
        # provenance (Decodeq/Forward layout), so never label this result as
        # production-eligible by itself.
        decision = (f"pass-serious-{champion}-AoS-scale-BM-primitive-"
                    "qualified-not-KEM-selected"
                    if args.mode == "serious" else
                    f"pass-short-{champion}-AoS-scale-BM-primitive-"
                    "await-serious-authorization")
    static_gate = json.loads(args.static_gate.read_text())
    result = {
        "schema": "ntruplus768-gt32-aos-dot-redc16-benchmark-v1",
        "experiment": "GT32-AOS-DOT-REDC16-001",
        "benchmark": {
            "iterations": args.iterations,
            "samples": 20,
            "warmups": 2,
            "cpu": 1,
            "ordering": "paired-AB-BA",
            "placements": ["normal", "reversed-link-order"],
            "mode": args.mode,
            "serious_benchmark": args.mode == "serious",
        },
        "correctness": {
            "status": "pass",
            "random_and_boundary_trials_per_binary": 1000,
            "checks": [
                "R1-U-intrinsic-and-assembly-bit-exact-to-R0",
                "R1-S-intrinsic-and-assembly-bit-exact",
                "R1-S-minus-R0-is-zero-or-q",
                "canonical-mod-q-equivalence",
                "out-equals-a-and-out-equals-b-alias",
                "I1-mod-q-equivalence",
                "T9-mod-q-equivalence",
                "crepmod3-exact-equivalence",
            ],
        },
        "static_proof": static_gate,
        "placements": placements,
        "thresholds": {
            "minimum_saving_vs_A1_tsc": 70,
            "minimum_wins_per_placement": 18,
            "family_stop_above_tsc": 450,
            "forward_terminal_extension_at_or_below_tsc": 430,
            "production_comparison": "same-binary B3 or B3+I1",
        },
        "variant_decisions": statuses,
        "champion": champion,
        "decision": decision,
        "production_integration": False,
        "serious_run": args.mode == "serious",
        "pmu_run": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for placement, runs in placements.items():
        for variant in ("r1u", "r1s"):
            bm = runs[f"a1_vs_{variant}_bm"]
            b3 = runs[f"b3_vs_{variant}_bm"]
            i1 = runs[f"b3_vs_{variant}_i1"]
            print(
                f"{placement}/{variant}: "
                f"BM={bm['candidate']['median_tsc']:.3f}, "
                f"save-vs-A1={-bm['paired_candidate_minus_baseline']['median_tsc']:.3f}, "
                f"wins={bm['candidate_wins']}/20, "
                f"vs-B3={b3['paired_candidate_minus_baseline']['median_tsc']:.3f}, "
                f"BM+I1-vs-B3={i1['paired_candidate_minus_baseline']['median_tsc']:.3f}")
    print(f"decision={decision}")


if __name__ == "__main__":
    main()
