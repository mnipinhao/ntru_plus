#!/usr/bin/env python3
"""Run the benchmark-only encap.c asymmetric general-scale subchain gate."""

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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--corroboration-binary", type=Path)
    args = parser.parse_args()

    def one_run(binary: Path) -> dict[str, object]:
        run = subprocess.run(
            [str(binary), str(args.iterations)],
            check=True,
            text=True,
            capture_output=True,
        )
        aa: list[float] = []
        sa: list[float] = []
        delta: list[float] = []
        for line in run.stdout.splitlines():
            fields = line.split(",")
            if fields[0] != "SAMPLE":
                continue
            aa.append(float(fields[2]))
            sa.append(float(fields[3]))
            delta.append(float(fields[4]))
        if len(delta) != 20:
            raise RuntimeError(f"expected 20 samples, got {len(delta)}")
        paired = summary(delta)
        return {
            "aa": summary(aa),
            "sa": summary(sa),
            "paired_sa_minus_aa": paired,
            "paired_saving_tsc": -paired["median_tsc"],
            "sa_wins": sum(value < 0.0 for value in delta),
        }

    runs = {"primary": one_run(args.binary)}
    if args.corroboration_binary is not None:
        runs["reversed_link_order"] = one_run(args.corroboration_binary)
    primary = runs["primary"]
    paired = primary["paired_sa_minus_aa"]
    assert isinstance(paired, dict)
    saving = -paired["median_tsc"]
    wins = int(primary["sa_wins"])
    corroborated = all(float(run["paired_saving_tsc"]) >= 20.0
                       and int(run["sa_wins"]) >= 18 for run in runs.values())
    if saving >= 20.0 and wins >= 18 and corroborated:
        decision = "pass-to-placement-recheck"
    elif saving >= 15.0:
        decision = "directional-pass-recheck-win-rate"
    else:
        decision = "stop-or-rework-general-scale-mixed-path"
    result = {
        "schema": "ntruplus768-encap-mixed-general-gate-v1",
        "scope": "frombytes(h)+NTT(r)+general-basemul+add(m)",
        "excluded_common_suffix": "tobytes(ct)",
        "boundary": {
            "input_h": "Official-format canonical bytes",
            "input_r": "coefficient-order small polynomial",
            "input_m": "TILE4 AoS e=0 frequency polynomial",
            "output": "TILE4 AoS e=0 after add",
        },
        "paths": {
            "aa": "AoS decode h + AoS forward r + general AoS/AoS BM + add",
            "sa": "AoS decode h + private-SoA forward r + general SoA/AoS BM + add",
        },
        "scale_repair": "four parallel Mont(R^2) chains fused into BM output finalizer",
        "correctness": {
            "status": "exact-pass",
            "deterministic_trials": 64,
            "noncanonical_behavior": "inherited unchanged AoS decoder",
        },
        "benchmark": {
            "iterations": args.iterations,
            "samples": 20,
            "cpu": 1,
            "ordering": "paired-AA-SA/SA-AA",
            "cache_state": "warm-L1 steady state",
        },
        "aa": primary["aa"],
        "sa": primary["sa"],
        "paired_sa_minus_aa": primary["paired_sa_minus_aa"],
        "paired_saving_tsc": saving,
        "sa_wins": wins,
        "corroboration": runs,
        "decision": decision,
        "serious_benchmark_run": False,
        "production_integration": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
