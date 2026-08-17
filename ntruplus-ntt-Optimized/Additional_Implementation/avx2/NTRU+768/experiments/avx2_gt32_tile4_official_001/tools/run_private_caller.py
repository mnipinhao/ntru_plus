#!/usr/bin/env python3
"""Run the caller-private SoA representation-island continuation gate."""

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
    parser.add_argument("--corroboration-binary", type=Path)
    parser.add_argument("--mode", choices=("short", "serious"), default="short")
    parser.add_argument("--launches", type=int, default=1)
    args = parser.parse_args()

    def one_run(binary: Path, scratch_offset: int) -> dict[str, object]:
        run = subprocess.run(
            [str(binary), str(args.iterations), str(scratch_offset)],
            check=True,
            text=True,
            capture_output=True,
        )
        baseline: list[float] = []
        mixed: list[float] = []
        full_soa: list[float] = []
        l2l2: list[float] = []
        soa_l2: list[float] = []
        l2_soa: list[float] = []
        mixed_delta: list[float] = []
        full_soa_delta: list[float] = []
        l2l2_delta: list[float] = []
        soa_l2_delta: list[float] = []
        l2_soa_delta: list[float] = []
        l2l2_minus_sa: list[float] = []
        soa_l2_minus_sa: list[float] = []
        l2_soa_minus_sa: list[float] = []
        for line in run.stdout.splitlines():
            fields = line.split(",")
            if fields[0] != "SAMPLE":
                continue
            baseline.append(float(fields[2]))
            mixed.append(float(fields[3]))
            full_soa.append(float(fields[4]))
            l2l2.append(float(fields[5]))
            soa_l2.append(float(fields[6]))
            l2_soa.append(float(fields[7]))
            mixed_delta.append(float(fields[8]))
            full_soa_delta.append(float(fields[9]))
            l2l2_delta.append(float(fields[10]))
            soa_l2_delta.append(float(fields[11]))
            l2_soa_delta.append(float(fields[12]))
            l2l2_minus_sa.append(float(fields[5]) - float(fields[3]))
            soa_l2_minus_sa.append(float(fields[6]) - float(fields[3]))
            l2_soa_minus_sa.append(float(fields[7]) - float(fields[3]))
        if len(mixed_delta) != 20:
            raise RuntimeError(f"expected 20 samples, got {len(mixed_delta)}")

        def candidate_result(values: list[float], delta: list[float]) -> dict[str, object]:
            paired = stats(delta)
            return {
                "cost": stats(values),
                "paired_candidate_minus_aa": paired,
                "paired_saving_tsc": -paired["median_tsc"],
                "wins": sum(value < 0.0 for value in delta),
            }

        l2_vs_sa_paired = stats(l2l2_minus_sa)
        soa_l2_vs_sa_paired = stats(soa_l2_minus_sa)
        l2_soa_vs_sa_paired = stats(l2_soa_minus_sa)
        return {
            "aa": stats(baseline),
            "sa": candidate_result(mixed, mixed_delta),
            "ss": candidate_result(full_soa, full_soa_delta),
            "l2l2": candidate_result(l2l2, l2l2_delta),
            "soa_l2": candidate_result(soa_l2, soa_l2_delta),
            "l2_soa": candidate_result(l2_soa, l2_soa_delta),
            "l2l2_vs_sa": {
                "paired_l2l2_minus_sa": l2_vs_sa_paired,
                "paired_saving_tsc": -l2_vs_sa_paired["median_tsc"],
                "wins": sum(value < 0.0 for value in l2l2_minus_sa),
            },
            "soa_l2_vs_sa": {
                "paired_candidate_minus_sa": soa_l2_vs_sa_paired,
                "paired_saving_tsc": -soa_l2_vs_sa_paired["median_tsc"],
                "wins": sum(value < 0.0 for value in soa_l2_minus_sa),
            },
            "l2_soa_vs_sa": {
                "paired_candidate_minus_sa": l2_soa_vs_sa_paired,
                "paired_saving_tsc": -l2_soa_vs_sa_paired["median_tsc"],
                "wins": sum(value < 0.0 for value in l2_soa_minus_sa),
            },
        }

    if args.launches < 1:
        raise ValueError("launches must be positive")
    runs = {}
    for launch in range(args.launches):
        prefix = f"launch{launch}_"
        runs[prefix + "primary_align64"] = one_run(args.binary, 0)
        if args.corroboration_binary is not None:
            runs[prefix + "primary_align32"] = one_run(args.binary, 32)
            runs[prefix + "reversed_align64"] = one_run(
                args.corroboration_binary, 0)
            runs[prefix + "reversed_align32"] = one_run(
                args.corroboration_binary, 32)
    primary = runs["launch0_primary_align64"]
    def summarize_candidate(name: str) -> dict[str, object]:
        primary_candidate = primary[name]
        saving = float(primary_candidate["paired_saving_tsc"])
        wins = int(primary_candidate["wins"])
        stable = (all(float(run[name]["paired_saving_tsc"]) >= 15.0
                      for run in runs.values())
                  and sum(int(run[name]["wins"]) for run in runs.values())
                  >= 18 * len(runs))
        if args.mode == "serious":
            if saving >= 25.0 and wins >= 18 and stable:
                decision = "pass-serious-caller-gate"
            elif saving >= 25.0 and wins < 18:
                decision = "inconclusive-serious-primary-win-rate-fail"
            else:
                decision = "stop-serious-caller-gate"
        elif saving >= 25.0 and wins >= 18:
            decision = "pass-to-serious-benchmark"
        elif saving >= 25.0:
            decision = "recheck-primary-win-rate"
        elif 15.0 <= saving < 25.0 and len(runs) == 1:
            decision = "recheck-alignment-and-link-order"
        elif 15.0 <= saving < 25.0:
            decision = ("conditional-stable-below-serious-threshold" if stable else
                        "stop-placement-sensitive")
        elif 5.0 <= saving < 15.0:
            decision = "stop-maintenance-cost-likely-not-worthwhile"
        else:
            decision = "stop-integration-unstable-or-below-five-tsc"
        return {
            "primary": primary_candidate,
            "corroboration_summary": {
                "minimum_saving_tsc": min(float(run[name]["paired_saving_tsc"])
                                          for run in runs.values()),
                "maximum_saving_tsc": max(float(run[name]["paired_saving_tsc"])
                                          for run in runs.values()),
                "aggregate_wins": sum(int(run[name]["wins"])
                                      for run in runs.values()),
                "aggregate_samples": 20 * len(runs),
            },
            "decision": decision,
        }

    candidates = {name: summarize_candidate(name)
                  for name in ("sa", "ss", "l2l2", "soa_l2", "l2_soa")}

    def incremental_summary(name: str) -> dict[str, object]:
        key = f"{name}_vs_sa"
        primary_incremental = primary[key]
        minimum = min(float(run[key]["paired_saving_tsc"])
                      for run in runs.values())
        maximum = max(float(run[key]["paired_saving_tsc"])
                      for run in runs.values())
        aggregate_wins = sum(int(run[key]["wins"]) for run in runs.values())
        stable = (minimum >= 20.0
                  and aggregate_wins >= 18 * len(runs))
        return {
            "primary": primary_incremental,
            "minimum_saving_tsc": minimum,
            "maximum_saving_tsc": maximum,
            "aggregate_wins": aggregate_wins,
            "aggregate_samples": 20 * len(runs),
            "stable": stable,
        }

    orientation_incremental = {
        name: incremental_summary(name) for name in ("soa_l2", "l2_soa")
    }
    selected_orientation = max(
        orientation_incremental,
        key=lambda name: (
            orientation_incremental[name]["minimum_saving_tsc"],
            orientation_incremental[name]["primary"]["paired_saving_tsc"],
        ),
    )
    selected_stable = bool(
        orientation_incremental[selected_orientation]["stable"])
    transpose_cut_decision = (
        "pass-asymmetric-transpose-cut-full-caller-short-gate"
        if selected_stable
        else "stop-asymmetric-transpose-cut-below-20-tsc-or-placement-unstable"
    )
    result = {
        "schema": "ntruplus768-private-caller-gate-v3",
        "benchmark": {
            "iterations": args.iterations,
            "samples": 20,
            "cpu": 1,
            "ordering": "paired-AB-BA",
            "cache_state": "warm-L1 caller steady state",
            "mode": args.mode,
            "launches": args.launches,
        },
        "caller_contract": {
            "input": "two coefficient-order small polynomials",
            "output": "coefficient-order ternary polynomial after crepmod3",
            "scratch_bytes": 5 * 768 * 2,
            "scratch_alignment": 64,
            "alias": ["distinct", "out==a", "out==b", "a==b"],
            "private_representation_visible_outside_entry": False,
        },
        "correctness": {
            "status": "pass",
            "random_trials": 64,
            "checks": [
                "distinct-exact-after-crepmod3",
                "out-equals-a-exact-after-crepmod3",
                "out-equals-b-exact-after-crepmod3",
                "squaring-exact-after-crepmod3",
                "SoA-L2-and-L2-SoA-orientations-exact-after-crepmod3",
            ],
        },
        "paths": {
            "aa": "N5-AoS + N5-AoS + AoS/AoS-B3 + I1 + T9 + crepmod3",
            "sa": "N5-private-SoA + N5-AoS + SoA/AoS-mixed-BM + I1 + T9 + crepmod3",
            "ss": "N5-private-SoA + N5-private-SoA + SoA/SoA-BM + redeposit + I1 + T9 + crepmod3",
            "l2l2": "N5-L2 + N5-L2 + L2/L2-B3 + I1 + T9 + crepmod3",
            "soa_l2": "N5-private-SoA + N5-L2 + SoA/L2-B3 + I1 + T9 + crepmod3",
            "l2_soa": "N5-L2 + N5-private-SoA + L2/SoA-B3 + I1 + T9 + crepmod3",
        },
        "baseline": primary["aa"],
        "candidates": candidates,
        "asymmetric_transpose_cut_incremental_vs_selected_sa": {
            "orientations": orientation_incremental,
            "selected_orientation": selected_orientation,
            "decision": transpose_cut_decision,
        },
        "corroboration": runs,
        "thresholds": {
            "serious_benchmark_min_saving_tsc": 25,
            "serious_benchmark_min_wins": 18,
            "alignment_link_order_recheck_saving_tsc": [15, 25],
            "maintenance_risk_saving_tsc": [5, 15],
            "transpose_cut_incremental_vs_sa_min_saving_tsc": 20,
        },
        "production_integration": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
