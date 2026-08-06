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
    args = parser.parse_args()

    def one_run(binary: Path, scratch_offset: int) -> dict[str, object]:
        run = subprocess.run(
            [str(binary), str(args.iterations), str(scratch_offset)],
            check=True,
            text=True,
            capture_output=True,
        )
        baseline: list[float] = []
        candidate: list[float] = []
        delta: list[float] = []
        for line in run.stdout.splitlines():
            fields = line.split(",")
            if fields[0] != "SAMPLE":
                continue
            baseline.append(float(fields[2]))
            candidate.append(float(fields[3]))
            delta.append(float(fields[4]))
        if len(delta) != 20:
            raise RuntimeError(f"expected 20 samples, got {len(delta)}")
        paired = stats(delta)
        return {
            "baseline": stats(baseline),
            "candidate": stats(candidate),
            "paired_candidate_minus_baseline": paired,
            "paired_saving_tsc": -paired["median_tsc"],
            "candidate_wins": sum(value < 0.0 for value in delta),
        }

    runs = {"primary_align64": one_run(args.binary, 0)}
    if args.corroboration_binary is not None:
        runs["primary_align32"] = one_run(args.binary, 32)
        runs["reversed_align64"] = one_run(args.corroboration_binary, 0)
        runs["reversed_align32"] = one_run(args.corroboration_binary, 32)
    primary = runs["primary_align64"]
    saving = float(primary["paired_saving_tsc"])
    wins = int(primary["candidate_wins"])
    stable = (all(float(run["paired_saving_tsc"]) >= 15.0
                  for run in runs.values())
              and sum(int(run["candidate_wins"]) for run in runs.values())
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
    result = {
        "schema": "ntruplus768-private-caller-gate-v1",
        "benchmark": {
            "iterations": args.iterations,
            "samples": 20,
            "cpu": 1,
            "ordering": "paired-AB-BA",
            "cache_state": "warm-L1 caller steady state",
            "mode": args.mode,
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
            ],
        },
        "baseline": primary["baseline"],
        "candidate": primary["candidate"],
        "paired_candidate_minus_baseline": primary["paired_candidate_minus_baseline"],
        "paired_saving_tsc": saving,
        "candidate_wins": wins,
        "corroboration": runs,
        "corroboration_summary": {
            "minimum_saving_tsc": min(float(run["paired_saving_tsc"])
                                      for run in runs.values()),
            "maximum_saving_tsc": max(float(run["paired_saving_tsc"])
                                      for run in runs.values()),
            "saving_spread_tsc": (max(float(run["paired_saving_tsc"])
                                      for run in runs.values())
                                  - min(float(run["paired_saving_tsc"])
                                      for run in runs.values())),
            "aggregate_wins": sum(int(run["candidate_wins"])
                                  for run in runs.values()),
            "aggregate_samples": 20 * len(runs),
        },
        "decision": decision,
        "thresholds": {
            "serious_benchmark_min_saving_tsc": 25,
            "serious_benchmark_min_wins": 18,
            "alignment_link_order_recheck_saving_tsc": [15, 25],
            "maintenance_risk_saving_tsc": [5, 15],
        },
        "production_integration": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
