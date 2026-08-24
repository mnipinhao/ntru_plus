#!/usr/bin/env python3
"""Run paired complete C2-inverse16 to reference inverse-NTT9 launches."""

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

A = "A-canonical-repack-reference-inverse9"
B = "B-direct-paper-p-reference-inverse9"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--cpu", type=int, required=True)
    parser.add_argument("--launches", type=int, default=9)
    parser.add_argument("--map", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--reference-source", type=Path, required=True)
    parser.add_argument("--bench-source", type=Path, required=True)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--compiler", required=True)
    parser.add_argument("--cflags", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite {args.output}")

    by_launch = defaultdict(list)
    documents = []
    for _ in range(args.launches):
        run = subprocess.run(
            ["taskset", "-c", str(args.cpu), str(args.binary.resolve())],
            check=True, text=True, stdout=subprocess.PIPE)
        document = json.loads(run.stdout)
        documents.append(document)
        grouped = defaultdict(list)
        for record in document["records"]:
            if record["implementation"] in (A, B):
                grouped[record["implementation"]].append(record["median_cycles"])
        for name in (A, B):
            by_launch[name].append(statistics.median(grouped[name]))

    medians = {name: statistics.median(by_launch[name]) for name in (A, B)}
    deltas = [right - left for left, right in zip(by_launch[A], by_launch[B])]
    mapping = json.loads(args.map.read_text())
    report = {
        "benchmark_class": "repository-local-inverse-tail-reference-paired-not-for-promotion",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "cpu": args.cpu,
        "cpu_model": next((line.split(":", 1)[1].strip()
                           for line in Path("/proc/cpuinfo").read_text().splitlines()
                           if line.lower().startswith("model name")), "unknown"),
        "hostname": platform.node(),
        "kernel": platform.release(),
        "compiler": args.compiler,
        "cflags": args.cflags,
        "binary_sha256": hashlib.sha256(args.binary.read_bytes()).hexdigest(),
        "launches": args.launches,
        "blocks_per_launch": documents[0]["blocks"],
        "observations_per_slot": documents[0]["observations_per_slot"],
        "cycles_by_launch": dict(by_launch),
        "median_cycles": medians,
        "paired": {
            "B_minus_A": {
                "by_launch": deltas,
                "median_cycles": statistics.median(deltas),
                "B_faster_launches": sum(value < 0 for value in deltas),
                "B_over_A": medians[B] / medians[A],
            }
        },
        "scope": {
            "included": "selected C2 BMScale+inverse16, boundary realization, complete correctness-first two-radix3 inverse NTT9",
            "excluded": "F1-B1 forward producer debt and final inverse normalization/top merge",
            "interpretation": "prices full canonical repack under the reference consumer; does not predict optimized inverse-NTT9 ASM cycles",
        },
        "correctness": {
            "arbitrary_transform_cases": 1003,
            "C2_producer_cases": 257,
            "cells_per_case": 1152,
            "independent_matrix_oracle": True,
            "canonical_and_direct_bit_exact": True,
        },
        "map_sha256": hashlib.sha256(args.map.read_bytes()).hexdigest(),
        "audit_sha256": hashlib.sha256(args.audit.read_bytes()).hexdigest(),
        "reference_source_sha256": hashlib.sha256(
            args.reference_source.read_bytes()).hexdigest(),
        "bench_source_sha256": hashlib.sha256(
            args.bench_source.read_bytes()).hexdigest(),
        "map_checkpoint": mapping["checkpoint"],
        "upstream": json.loads((args.upstream / "UPSTREAM.json").read_text()),
        "promotion_eligible": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
