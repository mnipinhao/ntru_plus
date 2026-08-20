#!/usr/bin/env python3
"""Run fresh pinned launches of the Checkpoint-C NTT16 diagnostic."""

from __future__ import annotations

import argparse
import json
import platform
import statistics
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--cpu", type=int, required=True)
    parser.add_argument("--launches", type=int, default=9)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite {args.output}")
    raw = []
    for launch in range(args.launches):
        completed = subprocess.run(
            ["taskset", "-c", str(args.cpu), str(args.binary.resolve())],
            check=True, text=True, stdout=subprocess.PIPE)
        record = json.loads(completed.stdout)
        record["launch"] = launch + 1
        raw.append(record)
    variants = sorted(raw[0].keys() - {"benchmark_class", "samples", "launch"})
    summary = {}
    for variant in variants:
        observations = [entry[variant]["cycles_per_transform"] for entry in raw]
        summary[variant] = {
            "cycles_per_transform_by_launch": observations,
            "median_cycles_per_transform": statistics.median(observations),
            "minimum_cycles_per_transform": min(observations),
            "maximum_cycles_per_transform": max(observations),
        }
    cpu_model = "unknown"
    for line in Path("/proc/cpuinfo").read_text(encoding="utf-8", errors="replace").splitlines():
        if line.lower().startswith("model name"):
            cpu_model = line.split(":", 1)[1].strip()
            break
    report = {
        "benchmark_class": "repository-local-diagnostic-not-for-promotion",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "cpu": args.cpu,
        "cpu_model": cpu_model,
        "hostname": platform.node(),
        "kernel": platform.release(),
        "launches": args.launches,
        "samples_per_launch": raw[0]["samples"],
        "summary": summary,
        "assembly_audit": json.loads(args.audit.read_text(encoding="utf-8")),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
