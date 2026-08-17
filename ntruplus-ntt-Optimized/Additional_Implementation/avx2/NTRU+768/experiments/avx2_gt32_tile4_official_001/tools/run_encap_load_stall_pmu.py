#!/usr/bin/env python3
"""Measure cache/load-stall ownership of CleanGT Encap's load-heavy edges."""

from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
from pathlib import Path


GROUPS = {
    "cache": ["cycles", "retired_loads", "l1_misses", "l2_misses"],
    "stalls": ["cycles", "bound_on_loads", "l1d_pending_cycles",
               "backend_bound_slots"],
    "blocks": ["cycles", "store_forward_blocks", "address_alias_blocks",
               "store_buffer_stalls"],
}

EDGES = [
    ("decode_h", None, "L01_decode_h"),
    ("forward_r", "L05_cbd_r", "L06_forward_r"),
    ("serialize_rhat", "L06_forward_r", "L07_serialize_rhat"),
    ("forward_m", "L09_sotp_m", "L10_forward_m"),
    ("basemul", "L10_forward_m", "L11_basemul"),
    ("serialize_ct", "L12_add_m", "L13_serialize_ct"),
]


def median(values: list[float]) -> float:
    return statistics.median(values)


def one(binary: Path, stage: str, impl: str, iterations: int,
        group: str) -> dict[str, float]:
    environment = dict(os.environ)
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
    result["time_enabled"] = float(fields[8])
    result["time_running"] = float(fields[9])
    return result


def subtract(current: dict[str, float],
             previous: dict[str, float] | None) -> dict[str, float]:
    if previous is None:
        return {key: value for key, value in current.items()
                if not key.startswith("time_")}
    return {
        key: value - previous[key]
        for key, value in current.items()
        if not key.startswith("time_")
    }


def summarize(samples: list[dict[str, float]]) -> dict[str, object]:
    keys = samples[0].keys()
    return {
        key: {
            "median": median([sample[key] for sample in samples]),
            "minimum": min(sample[key] for sample in samples),
            "maximum": max(sample[key] for sample in samples),
            "gt_favorable_pairs": sum(sample[key] < 0 for sample in samples),
        }
        for key in keys
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", required=True, type=Path)
    parser.add_argument("--iterations", type=int, default=10000)
    parser.add_argument("--pairs", type=int, default=8)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    placements = {}
    for placement, binary in (("normal", args.binary),
                              ("reversed", args.reversed_binary)):
        group_results = {}
        for group in GROUPS:
            edges = {}
            for label, before, after in EDGES:
                paired = []
                raw = []
                for index in range(args.pairs):
                    order = ("official", "gt") if index % 2 == 0 else ("gt", "official")
                    sample = {}
                    for impl in order:
                        prior = (one(binary, before, impl, args.iterations, group)
                                 if before is not None else None)
                        current = one(binary, after, impl, args.iterations, group)
                        sample[impl] = subtract(current, prior)
                    delta = {
                        key: sample["gt"][key] - sample["official"][key]
                        for key in sample["gt"]
                    }
                    paired.append(delta)
                    raw.append(sample)
                edges[label] = {
                    "before": before,
                    "after": after,
                    "summary_gt_minus_official": summarize(paired),
                    "paired_deltas": paired,
                    "component_counts": raw,
                }
            group_results[group] = edges
        placements[placement] = {
            "binary": str(binary),
            "groups": group_results,
        }

    result = {
        "schema": "ntruplus768-gt32-encap-load-stall-attribution-v1",
        "iterations": args.iterations,
        "pairs": args.pairs,
        "placements": placements,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    concise = {
        placement: {
            group: {
                edge: value["summary_gt_minus_official"]
                for edge, value in edges.items()
            }
            for group, edges in data["groups"].items()
        }
        for placement, data in placements.items()
    }
    print(json.dumps(concise, indent=2))


if __name__ == "__main__":
    main()
