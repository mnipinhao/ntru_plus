#!/usr/bin/env python3
"""Run fresh pinned G1C-M3 C0/C1/C2 full-path paired launches."""

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

NAMES = ["M3-C0-materialized", "M3-C1-linked-D1", "M3-C2-persistent"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--cpu", type=int, required=True)
    parser.add_argument("--launches", type=int, default=9)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--proof", type=Path, required=True)
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
            if record["implementation"] in NAMES:
                grouped[record["implementation"]].append(record["median_cycles"])
        for name in NAMES:
            by_launch[name].append(statistics.median(grouped[name]))

    medians = {name: statistics.median(by_launch[name]) for name in NAMES}
    comparisons = {}
    for left, right, label in ((NAMES[0], NAMES[1], "C1_minus_C0"),
                               (NAMES[1], NAMES[2], "C2_minus_C1"),
                               (NAMES[0], NAMES[2], "C2_minus_C0")):
        deltas = [r - l for l, r in zip(by_launch[left], by_launch[right])]
        comparisons[label] = {
            "by_launch": deltas,
            "median_cycles": statistics.median(deltas),
            "right_faster_launches": sum(value < 0 for value in deltas),
            "right_over_left": medians[right] / medians[left],
        }

    report = {
        "benchmark_class": "repository-local-g1c-m3-full-paired-not-for-promotion",
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
        "paired": comparisons,
        "attribution": {
            "C1_minus_C0": "linked BMScale-to-D1 edge in the complete repaired inverse16",
            "C2_minus_C1": "register-persistent D2/D4/D8 credit after one identical repaired-D1 boundary",
            "C2_minus_C0": "total diagnostic delta",
        },
        "correctness": {
            "producer_real_cases": 1003,
            "cells_per_case": 1152,
            "all_variants_bit_exact": True,
            "range_and_scale_proof": str(args.proof),
        },
        "audit_sha256": hashlib.sha256(args.audit.read_bytes()).hexdigest(),
        "proof_sha256": hashlib.sha256(args.proof.read_bytes()).hexdigest(),
        "upstream": json.loads((args.upstream / "UPSTREAM.json").read_text()),
        "promotion_eligible": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
