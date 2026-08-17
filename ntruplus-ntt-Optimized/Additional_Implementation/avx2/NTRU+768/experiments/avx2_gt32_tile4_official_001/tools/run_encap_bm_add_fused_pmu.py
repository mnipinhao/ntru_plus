#!/usr/bin/env python3
"""Paired PMU gate for the bounded Encap B3-finalizer + add(m) fusion."""

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


def one(binary: Path, stage: str, impl: str, iterations: int,
        group: str) -> dict[str, float]:
    environment = dict(os.environ)
    if group == "default":
        environment.pop("ENCAP_PMU_GROUP", None)
    else:
        environment["ENCAP_PMU_GROUP"] = group
    process = subprocess.run(
        [str(binary), "--self-pmu", stage, impl, str(iterations)],
        check=True, capture_output=True, text=True, env=environment,
    )
    line = next(line for line in process.stdout.splitlines()
                if line.startswith("SELFPMU,"))
    fields = line.split(",")
    values = [float(value) for value in fields[3:8]]
    result = dict(zip(GROUPS[group], values[1:]))
    result["tsc"] = values[0]
    return result


def paired(binary: Path, stage: str, order: str, iterations: int,
           group: str) -> dict[str, dict[str, float]]:
    environment = dict(os.environ)
    if group == "default":
        environment.pop("ENCAP_PMU_GROUP", None)
    else:
        environment["ENCAP_PMU_GROUP"] = group
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


def difference(after: dict[str, float],
               before: dict[str, float]) -> dict[str, float]:
    return {key: after[key] - before[key] for key in after}


def summary(samples: list[dict[str, float]]) -> dict[str, object]:
    return {
        key: {
            "median": statistics.median(sample[key] for sample in samples),
            "minimum": min(sample[key] for sample in samples),
            "maximum": max(sample[key] for sample in samples),
            "fused_favorable_pairs": sum(sample[key] < 0 for sample in samples),
        }
        for key in samples[0]
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", required=True, type=Path)
    parser.add_argument("--iterations", type=int, default=10000)
    parser.add_argument("--pairs", type=int, default=12)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    placements: dict[str, object] = {}
    for placement, binary in (("normal", args.binary),
                              ("reversed", args.reversed_binary)):
        groups: dict[str, object] = {}
        for group in GROUPS:
            edge_deltas: list[dict[str, float]] = []
            full_deltas: list[dict[str, float]] = []
            for pair in range(args.pairs):
                order = "gt-first" if pair % 2 == 0 else "fused-first"
                edge_samples = paired(binary, "EDGE_bm_add", order,
                                      args.iterations, group)
                full_samples = paired(binary, "L18_clear_m", order,
                                      args.iterations, group)
                edge_deltas.append({
                    key: edge_samples["gt-fused"][key]
                         - edge_samples["gt"][key]
                    for key in edge_samples["gt"]
                })
                full_deltas.append({
                    key: full_samples["gt-fused"][key]
                         - full_samples["gt"][key]
                    for key in full_samples["gt"]
                })
            groups[group] = {
                "bm_add_edge_fused_minus_control": summary(edge_deltas),
                "full_prefix_fused_minus_control": summary(full_deltas),
                "edge_paired_deltas": edge_deltas,
                "full_paired_deltas": full_deltas,
            }
        placements[placement] = {"binary": str(binary), "groups": groups}

    result = {
        "schema": "ntruplus768-gt32-encap-bm-add-fused-pmu-v1",
        "iterations": args.iterations,
        "pairs": args.pairs,
        "placements": placements,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        placement: {
            group: {
                "edge": data["bm_add_edge_fused_minus_control"],
                "full": data["full_prefix_fused_minus_control"],
            }
            for group, data in placement_data["groups"].items()
        }
        for placement, placement_data in placements.items()
    }, indent=2))


if __name__ == "__main__":
    main()
