#!/usr/bin/env python3
"""Run fresh pinned F-R3B R0/R1/R2 paired NTT9 launches."""

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
    for launch in range(1, args.launches + 1):
        result = subprocess.run(
            ["taskset", "-c", str(args.cpu), str(args.binary.resolve())],
            check=True, text=True, stdout=subprocess.PIPE)
        document = json.loads(result.stdout)
        documents.append(document)
        launch_groups = defaultdict(list)
        for record in document["records"]:
            if record["comparison"] == "sink":
                continue
            key = (record["comparison"], record["implementation"])
            launch_groups[key].append(record["median_cycles"])
        for key, values in launch_groups.items():
            grouped[key].append(statistics.median(values))
    comparisons = {}
    pair_names = {
        "R0-to-R1": ("R0", "R1"),
        "R1-to-R2-memory": ("R1", "R2-memory"),
        "R1-to-R2-cached": ("R1", "R2-cached"),
        "R2-memory-to-cached": ("R2-memory", "R2-cached"),
    }
    summary = {}
    for (comparison, implementation), values in sorted(grouped.items()):
        median = statistics.median(values)
        summary[f"{comparison}:{implementation}"] = {
            "cycles_eight_ntt9_by_launch": values,
            "median_cycles_eight_ntt9": median,
            "median_cycles_per_ntt9": median / documents[0]["ntt9_instances_per_observation"],
            "minimum": min(values), "maximum": max(values),
        }
    for comparison, (left, right) in pair_names.items():
        left_values = grouped[(comparison, left)]
        right_values = grouped[(comparison, right)]
        deltas = [r - l for l, r in zip(left_values, right_values)]
        left_median = statistics.median(left_values)
        right_median = statistics.median(right_values)
        comparisons[comparison] = {
            "left": left, "right": right,
            "right_minus_left_cycles_eight_ntt9_by_launch": deltas,
            "median_right_minus_left_cycles_eight_ntt9": statistics.median(deltas),
            "right_over_left": right_median / left_median,
        }
    audit = json.loads(args.audit.read_text())
    function_names = {
        "R0": "ntruplus1152_exp001_gt9x16_ntt9_d_a",
        "R1": "ntruplus1152_exp001_gt9x16_ntt9_r1",
        "R2-memory": "ntruplus1152_exp001_gt9x16_ntt9_r2_memory",
        "R2-cached": "ntruplus1152_exp001_gt9x16_ntt9_r2_cached",
    }
    static = {name: audit["functions"][function]
              for name, function in function_names.items()}
    static["R0"]["distinct_inter_level_twist_constants"] = 3
    static["R1"]["distinct_inter_level_twist_constants"] = 3
    static["R2-memory"]["distinct_inter_level_twist_constants"] = 2
    static["R2-cached"]["distinct_inter_level_twist_constants"] = 2
    model = next((line.split(":", 1)[1].strip()
                  for line in Path("/proc/cpuinfo").read_text().splitlines()
                  if line.lower().startswith("model name")), "unknown")
    report = {
        "benchmark_class": "repository-local-f-r3b-paired-not-for-promotion",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "cpu": args.cpu, "cpu_model": model, "hostname": platform.node(),
        "kernel": platform.release(), "compiler": args.compiler, "cflags": args.cflags,
        "binary_sha256": hashlib.sha256(args.binary.read_bytes()).hexdigest(),
        "launches": args.launches, "blocks_per_launch": documents[0]["blocks"],
        "observations_per_slot": documents[0]["observations_per_slot"],
        "ntt9_instances_per_observation": documents[0]["ntt9_instances_per_observation"],
        "summary": summary, "comparisons": comparisons, "static": static,
        "range_proof": json.loads(args.range_path.read_text()),
        "upstream": json.loads((args.upstream / "UPSTREAM.json").read_text()),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
