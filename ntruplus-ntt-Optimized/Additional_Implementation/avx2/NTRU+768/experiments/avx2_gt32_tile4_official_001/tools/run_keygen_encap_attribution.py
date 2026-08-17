#!/usr/bin/env python3
import argparse
import json
import statistics
import subprocess
from pathlib import Path


def summarize(values):
    off = [v[0] for v in values]
    gt = [v[1] for v in values]
    delta = [v[2] for v in values]
    med = statistics.median(delta)
    return {
        "official_median_tsc": statistics.median(off),
        "gt32_median_tsc": statistics.median(gt),
        "paired_delta_tsc": med,
        "paired_delta_mad_tsc": statistics.median(abs(x - med) for x in delta),
        "gt32_wins": sum(x < 0 for x in delta),
        "samples": len(values),
    }


def run_once(binary, iterations):
    p = subprocess.run([str(binary), str(iterations)], check=True,
                       capture_output=True, text=True)
    phases = {}
    full = {}
    official_only = {}
    coverage = []
    metadata = []
    for line in p.stdout.splitlines():
        f = line.split(",")
        if f[0] == "META":
            metadata.append(line)
        elif f[0] == "COVERAGE":
            coverage.append(f[1:])
        elif f[0] == "PHASE":
            phases.setdefault(f"{f[1]}.{f[2]}", []).append(
                (float(f[4]), float(f[5]), float(f[6])))
        elif f[0] == "FULL":
            full.setdefault(f[1], []).append(
                (float(f[3]), float(f[4]), float(f[5])))
        elif f[0] == "OFFICIAL_ONLY":
            official_only.setdefault(f"{f[1]}.{f[2]}", []).append(float(f[4]))
    return {
        "metadata": metadata,
        "coverage": coverage,
        "phases": {k: summarize(v) for k, v in phases.items()},
        "full": {k: summarize(v) for k, v in full.items()},
        "official_only": {
            k: {"official_median_tsc": statistics.median(v), "samples": len(v)}
            for k, v in official_only.items()
        },
    }


def run_many(binary, iterations, launches):
    values = [run_once(binary, iterations) for _ in range(launches)]
    phase_names = values[0]["phases"]
    full_names = values[0]["full"]
    official_names = values[0]["official_only"]
    def launch_summary(container, name):
        rows = [value[container][name] for value in values]
        deltas = [row["paired_delta_tsc"] for row in rows]
        med = statistics.median(deltas)
        return {
            "official_median_tsc": statistics.median(
                row["official_median_tsc"] for row in rows),
            "gt32_median_tsc": statistics.median(
                row["gt32_median_tsc"] for row in rows),
            "launch_median_delta_tsc": med,
            "launch_delta_mad_tsc": statistics.median(
                abs(delta - med) for delta in deltas),
            "negative_launch_medians": sum(delta < 0 for delta in deltas),
            "launches": launches,
            "sample_wins": sum(row["gt32_wins"] for row in rows),
            "samples": sum(row["samples"] for row in rows),
            "raw_launch_delta_tsc": deltas,
        }
    return {
        "metadata": values[0]["metadata"],
        "coverage": values[0]["coverage"],
        "phases": {name: launch_summary("phases", name)
                   for name in phase_names},
        "full": {name: launch_summary("full", name) for name in full_names},
        "official_only": {
            name: {
                "official_launch_median_tsc": statistics.median(
                    value["official_only"][name]["official_median_tsc"]
                    for value in values),
                "launches": launches,
                "raw_launch_median_tsc": [
                    value["official_only"][name]["official_median_tsc"]
                    for value in values],
            }
            for name in official_names
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("binary", type=Path)
    ap.add_argument("--reversed-binary", required=True, type=Path)
    ap.add_argument("--iterations", type=int, default=2000)
    ap.add_argument("--launches", type=int, default=8)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    result = {
        "schema": "ntruplus768-gt32-keygen-encap-attribution-v1",
        "mode": "short",
        "iterations_per_sample": args.iterations,
        "launches": args.launches,
        "placements": {
            "normal": run_many(args.binary, args.iterations, args.launches),
            "reversed": run_many(args.reversed_binary, args.iterations,
                                 args.launches),
        },
        "interpretation_guard": (
            "Encap is a complete byte-exact GT32 candidate. Keygen K3-K5 are "
            "Official-only because no GT32 BaseInv J1 implementation/full caller exists; "
            "they must not be reported as Official-vs-GT deltas."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({p: {"full": d["full"], "phases": d["phases"],
                          "official_only": d["official_only"]}
                      for p, d in result["placements"].items()}, indent=2))


if __name__ == "__main__":
    main()
