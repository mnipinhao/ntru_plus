#!/usr/bin/env python3
"""Run and summarize the repository-local Official-vs-GT transform pairing."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
import statistics
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def interval(values: list[float]) -> list[float]:
    generator = random.Random(0x1152_916)
    medians = []
    for _ in range(10000):
        sample = [values[generator.randrange(len(values))] for _ in values]
        medians.append(statistics.median(sample))
    medians.sort()
    return [medians[249], medians[9749]]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--cpu", type=int, required=True)
    parser.add_argument("--launches", type=int, default=9)
    parser.add_argument("--compiler", required=True)
    parser.add_argument("--cflags", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite {args.output}")
    launches = []
    paired = []
    for launch in range(args.launches):
        completed = subprocess.run(
            ["taskset", "-c", str(args.cpu), str(args.binary.resolve())],
            check=True, text=True, stdout=subprocess.PIPE)
        record = json.loads(completed.stdout)
        record["launch"] = launch + 1
        launches.append(record)
        for block in range(1, record["blocks"] + 1):
            rows = [row for row in record["records"] if row["block"] == block]
            official = statistics.mean(row["median_cycles"] for row in rows
                                       if row["implementation"] == "official")
            candidate = statistics.mean(row["median_cycles"] for row in rows
                                        if row["implementation"] == "gt")
            paired.append(candidate - official)
    official_values = [row["median_cycles"] for launch in launches for row in launch["records"]
                       if row["implementation"] == "official"]
    gt_values = [row["median_cycles"] for launch in launches for row in launch["records"]
                 if row["implementation"] == "gt"]
    cpu_model = next((line.split(":", 1)[1].strip()
                      for line in Path("/proc/cpuinfo").read_text().splitlines()
                      if line.lower().startswith("model name")), "unknown")
    report = {
        "benchmark_class": "repository-local-transform-paired-not-for-promotion",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "cpu": args.cpu,
        "cpu_model": cpu_model,
        "hostname": platform.node(),
        "kernel": platform.release(),
        "compiler": subprocess.run([args.compiler, "--version"], check=True, text=True,
                                   stdout=subprocess.PIPE).stdout.splitlines()[0],
        "cflags": args.cflags,
        "elf_sha256": hashlib.sha256(args.binary.read_bytes()).hexdigest(),
        "launches": args.launches,
        "blocks_per_launch": launches[0]["blocks"],
        "observations_per_slot": launches[0]["observations_per_slot"],
        "input_residency": "same fixed aligned small-input buffer, hot L1; reset outside timing",
        "ordering": "odd O-C-C-O; even C-O-O-C",
        "summary": {
            "official_median_cycles": statistics.median(official_values),
            "gt_correctness_first_median_cycles": statistics.median(gt_values),
            "paired_gt_minus_official_median_cycles": statistics.median(paired),
            "paired_gt_minus_official_bootstrap_95pct": interval(paired),
        },
        "raw_launches": launches,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
