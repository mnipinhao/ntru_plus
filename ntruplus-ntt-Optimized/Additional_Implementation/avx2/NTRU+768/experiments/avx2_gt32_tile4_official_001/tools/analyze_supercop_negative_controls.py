#!/usr/bin/env python3
"""Summarize operation-first TF1/SP1 SUPERcop negative controls."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from analyze_supercop_matrix import decode_measurement, stabilized_quartiles


def median(values: list[float]) -> float:
    ordered = sorted(values)
    size = len(ordered)
    middle = size // 2
    return (
        ordered[middle]
        if size % 2
        else (ordered[middle - 1] + ordered[middle]) / 2
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("result_dirs", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    launches = []
    for result_dir in args.result_dirs:
        metadata = dict(
            line.split("=", 1)
            for line in (result_dir / "CONTROL_OPERATION.txt").read_text().splitlines()
        )
        operation = metadata["operation_first"]
        measurements = []
        for line in (result_dir / "data").read_text().splitlines():
            if f" {operation}_cycles " in line:
                measurements.extend(decode_measurement(line))
        launches.append(
            {
                "result_dir": str(result_dir),
                **metadata,
                "observations": len(measurements),
                "q2_cycles": stabilized_quartiles(measurements)[1],
            }
        )

    summary = {}
    for operation in ("enc", "dec"):
        summary[operation] = {}
        for optimization in ("O2", "O3"):
            cell = [
                item
                for item in launches
                if item["operation_first"] == operation
                and item["optimization"] == optimization
            ]
            medians = {}
            for variant in ("tf1", "sp1"):
                values = [item["q2_cycles"] for item in cell if item["variant"] == variant]
                medians[variant] = {
                    "launches": len(values),
                    "launch_q2_cycles": values,
                    "median_launch_q2_cycles": median(values),
                }
            summary[operation][optimization] = {
                "variants": medians,
                "sp1_minus_tf1": (
                    medians["sp1"]["median_launch_q2_cycles"]
                    - medians["tf1"]["median_launch_q2_cycles"]
                ),
            }
            ordered = sorted(cell, key=lambda item: Path(item["result_dir"]).name[-15:])
            if len(ordered) % 4 != 0:
                raise ValueError("ABBA launch count is not divisible by four")
            block_deltas = []
            for start in range(0, len(ordered), 4):
                block = ordered[start : start + 4]
                if [item["variant"] for item in block] != ["tf1", "sp1", "sp1", "tf1"]:
                    raise ValueError("launch order is not ABBA")
                tf1_mean = (block[0]["q2_cycles"] + block[3]["q2_cycles"]) / 2
                sp1_mean = (block[1]["q2_cycles"] + block[2]["q2_cycles"]) / 2
                block_deltas.append(sp1_mean - tf1_mean)
            summary[operation][optimization]["abba_block_deltas"] = block_deltas
            summary[operation][optimization]["median_abba_block_delta"] = median(
                block_deltas
            )

    output = {
        "schema": "gt32-q24-operation-first-controls-v1",
        "estimator": "median of per-launch SUPERcop stabilized Q2",
        "launches": launches,
        "summary": summary,
    }
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
