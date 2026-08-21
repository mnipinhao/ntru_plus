#!/usr/bin/env python3
"""Run fresh pinned launches of the Official-stage/D-A/C4 paired diagnostic."""

import argparse
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
    parser.add_argument("--compiler", required=True)
    parser.add_argument("--cflags", required=True)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite {args.output}")
    grouped = defaultdict(list)
    for launch in range(1, args.launches + 1):
        result = subprocess.run(
            ["taskset", "-c", str(args.cpu), str(args.binary.resolve())],
            check=True, text=True, stdout=subprocess.PIPE)
        document = json.loads(result.stdout)
        launch_groups = defaultdict(list)
        for record in document["records"]:
            key = (record["partition"], record["implementation"])
            launch_groups[key].append(record["median_cycles"])
        for key, values in launch_groups.items():
            grouped[key].append(statistics.median(values))
    summary = {}
    for (partition, implementation), values in sorted(grouped.items()):
        summary[f"{partition}:{implementation}"] = {
            "cycles_by_launch": values,
            "median_cycles": statistics.median(values),
            "minimum": min(values),
            "maximum": max(values),
        }
    comparisons = {}
    for partition, candidate in (("T3x3", "gt-d-a"),
                                 ("T2x4", "gt-c4-from-z"),
                                 ("T2x4-natural", "gt-c4-natural")):
        official = grouped[(partition, "official")]
        alternative = grouped[(partition, candidate)]
        deltas = [right - left for left, right in zip(official, alternative)]
        official_median = statistics.median(official)
        candidate_median = statistics.median(alternative)
        comparisons[partition] = {
            "candidate": candidate,
            "candidate_minus_official_by_launch": deltas,
            "median_candidate_minus_official_cycles": statistics.median(deltas),
            "candidate_over_official": candidate_median / official_median,
        }
    model = next((line.split(":", 1)[1].strip()
                  for line in Path("/proc/cpuinfo").read_text().splitlines()
                  if line.lower().startswith("model name")), "unknown")
    upstream = json.loads((args.upstream / "UPSTREAM.json").read_text())
    report = {
        "benchmark_class": "repository-local-official-stage-paired-not-for-promotion",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "cpu": args.cpu,
        "cpu_model": model,
        "hostname": platform.node(),
        "kernel": platform.release(),
        "compiler": args.compiler,
        "cflags": args.cflags,
        "launches": args.launches,
        "blocks_per_launch": document["blocks"],
        "observations_per_slot": document["observations_per_slot"],
        "upstream": upstream,
        "summary": summary,
        "comparisons": comparisons,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
