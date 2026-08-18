#!/usr/bin/env python3
"""Join static Pareto data and executable measurements into the 007 decision."""

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", type=Path, required=True)
    parser.add_argument("--benchmark", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    gate = json.loads(args.gate.read_text())
    bench = json.loads(args.benchmark.read_text())
    aggregate = bench["aggregate"]
    progressive = aggregate["progressive"]
    best_plane = min(
        ("folded", "reuse_one", "reuse_pair"),
        key=lambda name: aggregate[name]["median_core_cycles"],
    )
    plane = aggregate[best_plane]
    launch_deltas = [
        item["medians"][best_plane] - item["medians"]["progressive"]
        for item in bench["raw_launches"]
    ]
    result = {
        "experiment": gate["experiment"],
        "questions": {
            "Q1_minimum_persistent_permutation_cost": {
                "answer": "48 shuffle instructions per 8-YMM tile",
                "progressive_control": 40,
                "pair_packed_control": 56,
                "mechanism": "8-shuffle unpack-butterfly edges remove reconstruction but S2/S3 each still require an 8-shuffle lane route",
            },
            "Q2_twiddle_reuse": {
                "answer": "physically valid but only a small cycle win",
                "folded_loads": aggregate["folded"]["median_loads"],
                "reuse_pair_loads": aggregate["reuse_pair"]["median_loads"],
                "load_delta": aggregate["reuse_pair"]["median_loads"] - aggregate["folded"]["median_loads"],
                "instruction_delta": aggregate["reuse_pair"]["median_instructions"] - aggregate["folded"]["median_instructions"],
                "core_cycle_delta": aggregate["reuse_pair"]["median_core_cycles"] - aggregate["folded"]["median_core_cycles"],
            },
            "Q3_plane_major_beats_controls": {
                "answer": False,
                "best_plane_policy": best_plane,
                "core_cycle_delta_vs_progressive": plane["median_core_cycles"] - progressive["median_core_cycles"],
                "TSC_delta_vs_progressive": plane["median_of_launch_tsc_medians"] - progressive["median_of_launch_tsc_medians"],
                "progressive_wins_by_launch": sum(delta > 0 for delta in launch_deltas),
                "launches": len(launch_deltas),
            },
        },
        "aggregate": aggregate,
        "decision": "do_not_promote_persistent_plane_radix2_schedule",
        "interpretation": "the new fused edge is real and reuse-pair is the best plane policy, but the old progressive schedule remains the executable N16 champion",
        "hard_stop_scope": "structured affine radix-2 persistent plane-major N16 schedules in this stage library",
        "not_closed": [
            "hybrid terminal selected by a downstream consumer",
            "radix-4 N16 schema (008)",
            "a new AVX2 primitive that removes the S2/S3 lane route",
        ],
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
