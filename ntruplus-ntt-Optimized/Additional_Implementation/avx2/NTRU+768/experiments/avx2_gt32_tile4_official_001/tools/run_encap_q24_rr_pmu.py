#!/usr/bin/env python3
"""Paired PMU gate for register-resident Q24 serializer constants."""

from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
from pathlib import Path


GROUPS = {
    "default": ["cycles", "instructions", "retired_loads", "retired_stores"],
    "stalls": ["cycles", "bound_on_loads", "l1d_pending_cycles",
               "backend_bound_slots"],
}
STAGES = ("EDGE_pack_r", "EDGE_pack_ct", "L18_clear_m")


def paired(binary: Path, stage: str, gt_first: bool, iterations: int,
           group: str) -> dict[str, dict[str, float]]:
    environment = dict(os.environ)
    if group == "default":
        environment.pop("ENCAP_PMU_GROUP", None)
    else:
        environment["ENCAP_PMU_GROUP"] = group
    order = "gt-first-rr" if gt_first else "rr-first"
    process = subprocess.run(
        [str(binary), "--paired-pmu", stage, order, str(iterations)],
        check=True, capture_output=True, text=True, env=environment,
    )
    result: dict[str, dict[str, float]] = {}
    for line in process.stdout.splitlines():
        if not line.startswith("SELFPMU,"):
            continue
        fields = line.split(",")
        values = [float(value) for value in fields[3:8]]
        sample = dict(zip(GROUPS[group], values[1:]))
        sample["tsc"] = values[0]
        result[fields[2]] = sample
    if set(result) != {"gt", "gt-fused"}:
        raise RuntimeError(f"missing paired results: {process.stdout}")
    return result


def summarize(samples: list[dict[str, float]]) -> dict[str, object]:
    return {
        key: {
            "median": statistics.median(sample[key] for sample in samples),
            "minimum": min(sample[key] for sample in samples),
            "maximum": max(sample[key] for sample in samples),
            "rr_favorable_pairs": sum(sample[key] < 0 for sample in samples),
        }
        for key in samples[0]
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", required=True, type=Path)
    parser.add_argument("--iterations", type=int, default=20000)
    parser.add_argument("--pairs", type=int, default=20)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    placements: dict[str, object] = {}
    for placement, binary in (("normal", args.binary),
                              ("reversed", args.reversed_binary)):
        groups: dict[str, object] = {}
        for group in GROUPS:
            stage_results: dict[str, object] = {}
            for stage in STAGES:
                deltas = []
                for pair_index in range(args.pairs):
                    sample = paired(binary, stage, pair_index % 2 == 0,
                                    args.iterations, group)
                    deltas.append({
                        key: sample["gt-fused"][key] - sample["gt"][key]
                        for key in sample["gt"]
                    })
                stage_results[stage] = {
                    "rr_minus_control": summarize(deltas),
                    "paired_deltas": deltas,
                }
            groups[group] = stage_results
        placements[placement] = {"binary": str(binary), "groups": groups}

    result = {
        "schema": "ntruplus768-gt32-encap-q24-rr-pmu-v1",
        "iterations": args.iterations,
        "pairs": args.pairs,
        "placements": placements,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        placement: {
            group: {
                stage: data["rr_minus_control"]
                for stage, data in group_data.items()
            }
            for group, group_data in placement_data["groups"].items()
        }
        for placement, placement_data in placements.items()
    }, indent=2))


if __name__ == "__main__":
    main()
