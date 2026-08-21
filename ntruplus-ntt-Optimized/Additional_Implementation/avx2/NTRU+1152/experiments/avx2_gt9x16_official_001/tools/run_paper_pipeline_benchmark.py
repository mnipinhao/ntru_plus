#!/usr/bin/env python3
"""Run fresh pinned F-R3D C/D0/D1 adjusted and combined paired launches."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import statistics
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


PAIRS = {
    "adjusted-C-to-D0": ("adjusted-C", "adjusted-D0"),
    "adjusted-D0-to-D1": ("adjusted-D0", "adjusted-D1"),
    "combined-C-to-D0": ("combined-C", "combined-D0"),
    "combined-D0-to-D1": ("combined-D0", "combined-D1"),
    "official-to-D1": ("Official-T3x3+T2x4", "combined-D1"),
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--cpu", type=int, required=True)
    parser.add_argument("--launches", type=int, default=9)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--range", dest="range_path", type=Path, required=True)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--compiler", required=True)
    parser.add_argument("--cflags", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite {args.output}")
    grouped = defaultdict(list)
    documents = []
    for _ in range(args.launches):
        run = subprocess.run(["taskset", "-c", str(args.cpu), str(args.binary.resolve())],
                             check=True, text=True, stdout=subprocess.PIPE)
        document = json.loads(run.stdout)
        documents.append(document)
        per_launch = defaultdict(list)
        for record in document["records"]:
            if record["comparison"] in PAIRS:
                per_launch[(record["comparison"], record["implementation"])].append(
                    record["median_cycles"])
        for key, values in per_launch.items():
            grouped[key].append(statistics.median(values))
    summary = {}
    comparisons = {}
    for comparison, (left, right) in PAIRS.items():
        left_values = grouped[(comparison, left)]
        right_values = grouped[(comparison, right)]
        left_median = statistics.median(left_values)
        right_median = statistics.median(right_values)
        deltas = [r - l for l, r in zip(left_values, right_values)]
        summary[f"{comparison}:{left}"] = {
            "cycles_by_launch": left_values, "median_cycles": left_median,
            "minimum": min(left_values), "maximum": max(left_values)}
        summary[f"{comparison}:{right}"] = {
            "cycles_by_launch": right_values, "median_cycles": right_median,
            "minimum": min(right_values), "maximum": max(right_values)}
        comparisons[comparison] = {
            "left": left, "right": right,
            "right_minus_left_by_launch": deltas,
            "median_right_minus_left_cycles": statistics.median(deltas),
            "right_over_left": right_median / left_median,
        }
    adjusted_d1 = summary["adjusted-D0-to-D1:adjusted-D1"]["median_cycles"]
    combined_d1 = summary["official-to-D1:combined-D1"]["median_cycles"]
    official = summary["official-to-D1:Official-T3x3+T2x4"]["median_cycles"]
    audit = json.loads(args.audit.read_text())
    functions = audit["functions"]
    report = {
        "benchmark_class": "repository-local-f-r3d-paired-not-for-promotion",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "cpu": args.cpu,
        "cpu_model": next((line.split(":", 1)[1].strip()
                           for line in Path("/proc/cpuinfo").read_text().splitlines()
                           if line.lower().startswith("model name")), "unknown"),
        "hostname": platform.node(), "kernel": platform.release(),
        "compiler": args.compiler, "cflags": args.cflags,
        "binary_sha256": hashlib.sha256(args.binary.read_bytes()).hexdigest(),
        "launches": args.launches, "blocks_per_launch": documents[0]["blocks"],
        "observations_per_slot": documents[0]["observations_per_slot"],
        "summary": summary, "comparisons": comparisons,
        "gates": {
            "adjusted_d1_cycles": adjusted_d1,
            "strong_target_434": adjusted_d1 <= 434,
            "stretch_target_422": adjusted_d1 <= 422,
            "combined_d1_cycles": combined_d1,
            "official_contiguous_cycles": official,
            "combined_d1_minus_official": combined_d1 - official,
            "minimum_success_combined_below_official": combined_d1 < official,
        },
        "static": {
            name: functions[symbol] for name, symbol in {
                "adjusted-D0": "ntruplus1152_exp001_gt9x16_paper_adjusted_ntt16_d0",
                "adjusted-D1": "ntruplus1152_exp001_gt9x16_paper_adjusted_ntt16_d1",
                "combined-D0": "ntruplus1152_exp001_gt9x16_r2_adjusted_forward_body_d0",
                "combined-D1": "ntruplus1152_exp001_gt9x16_r2_adjusted_forward_body_d1",
            }.items()
        },
        "range_proof": json.loads(args.range_path.read_text()),
        "upstream": json.loads((args.upstream / "UPSTREAM.json").read_text()),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
