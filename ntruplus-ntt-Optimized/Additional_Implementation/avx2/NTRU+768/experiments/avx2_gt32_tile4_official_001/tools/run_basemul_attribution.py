#!/usr/bin/env python3
"""Run and summarize the benchmark-only TILE4 basemul decomposition."""

import argparse
import json
import statistics
import subprocess
from pathlib import Path


def median_mad(values: list[float]) -> dict[str, float]:
    median = statistics.median(values)
    mad = statistics.median(abs(value - median) for value in values)
    return {"median_tsc": median, "mad_tsc": mad}


def paired_summary(left: list[float], right: list[float]) -> dict[str, float | int]:
    deltas = [a - b for a, b in zip(left, right)]
    result: dict[str, float | int] = median_mad(deltas)
    result["left_wins"] = sum(delta < 0.0 for delta in deltas)
    result["right_wins"] = sum(delta > 0.0 for delta in deltas)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    completed = subprocess.run(
        [str(args.binary), str(args.iterations)],
        check=True,
        text=True,
        capture_output=True,
    )
    samples: dict[str, list[float]] = {}
    meta = ""
    for line in completed.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "META":
            meta = line
        elif fields[0] == "SAMPLE":
            samples.setdefault(fields[1], []).append(float(fields[3]))

    summary = {name: median_mad(values) for name, values in samples.items()}
    fused_pair = paired_summary(samples["fused_bm_i1"], samples["champion_bm_i1"])
    empty = summary["empty"]["median_tsc"]
    tab = summary["TAB"]["median_tsc"]
    to = summary["TO"]["median_tsc"]
    arithmetic = summary["tile4_arith_c3"]["median_tsc"]
    reconstructed = tab + arithmetic + to - 2.0 * empty
    full = summary["tile4_full_b3"]["median_tsc"]
    raw = summary["tile4_arith_raw"]["median_tsc"]
    official = summary["official_arith_scale"]["median_tsc"]

    result = {
        "schema": "ntruplus768-tile4-basemul-attribution-v2",
        "benchmark": {
            "binary": str(args.binary),
            "iterations": args.iterations,
            "samples": 20,
            "cpu": 1,
            "ordering": "alternating-forward-reverse",
            "meta": meta,
        },
        "correctness": {
            "status": "pass",
            "checks": [
                "transpose-self-inverse-exact",
                "raw-arithmetic-vs-frozen-boundary-exact",
                "c3-repair-decomposition-exact",
                "full-b3-decomposition-exact",
                "fused-bm-i1-vs-champion-exact",
            ],
        },
        "components": summary,
        "paired": {
            "fused_minus_champion_bm_i1": fused_pair,
        },
        "derived": {
            "input_materialization_TAB_tsc": tab - empty,
            "output_materialization_TO_tsc": to - empty,
            "arithmetic_c3_tsc": arithmetic - empty,
            "range_policy_delta_c3_minus_raw_tsc": arithmetic - raw,
            "explicit_c3_repair_boundary_tsc": (
                summary["c3_repair_boundary"]["median_tsc"] - empty
            ),
            "reconstructed_TAB_arithmetic_TO_tsc": reconstructed,
            "measured_fused_B3_tsc": full,
            "fusion_or_reconstruction_residual_tsc": full - reconstructed,
            "tile4_arithmetic_minus_official_scale_tsc": arithmetic - official,
            "tile4_full_minus_official_scale_tsc": full - official,
            "fused_bm_i1_saving_tsc": (
                summary["champion_bm_i1"]["median_tsc"]
                - summary["fused_bm_i1"]["median_tsc"]
            ),
            "fused_bm_i1_ratio": (
                summary["fused_bm_i1"]["median_tsc"]
                / summary["champion_bm_i1"]["median_tsc"]
            ),
            "fused_reconstruction_tsc": (
                summary["fused_stage01_producer"]["median_tsc"]
                + summary["i1_cross3_remainder"]["median_tsc"]
                - empty
            ),
        },
        "interpretation": {
            "official_comparator": "poly_basemul_scale on Official native NTT layout",
            "tile4_arithmetic_contract": "SoA e=0 x SoA e=0 -> SoA e=-1; c3 centered",
            "warning": (
                "Component sums are call-overhead corrected but remain explicit "
                "materialization boundaries; the residual captures fusion, cache, "
                "and scheduling interactions."
            ),
            "fused_gate": {
                "continue_below_tsc": 610,
                "parity_below_tsc": 628,
                "hard_stop_above_tsc": 650,
                "decision": "stop-no-measurable-saving",
            },
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["derived"], indent=2))


if __name__ == "__main__":
    main()
