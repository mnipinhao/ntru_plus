#!/usr/bin/env python3
"""Record the deterministic producer-real G1C-M3B range probe."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--m3-oracle", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--compiler", required=True)
    parser.add_argument("--cflags", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite {args.output}")

    probe = json.loads(subprocess.run(
        [str(args.binary.resolve())], check=True, text=True,
        stdout=subprocess.PIPE).stdout)
    stages = {stage["distance"]: stage for stage in probe["stages"]}
    if stages[1]["unsafe_sum_count"] or stages[1]["unsafe_difference_count"]:
        raise SystemExit("qualified D1 unexpectedly overflowed")
    if stages[2]["unsafe_sum_count"] or stages[2]["unsafe_difference_count"]:
        raise SystemExit("D2 counterexample found; update M3B classification")
    if stages[4]["unsafe_sum_count"] or stages[4]["unsafe_difference_count"]:
        raise SystemExit("D4 counterexample found; update M3B classification")
    if stages[8]["unsafe_sum_count"] == 0:
        raise SystemExit("expected deterministic D8 counterexample disappeared")

    report = {
        "schema": "gt-g1c-m3b-producer-correlated-range-observation/v1",
        "benchmark_class": "repository-local-deterministic-range-counterexample-search-not-performance",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "hostname": platform.node(),
        "kernel": platform.release(),
        "compiler": args.compiler,
        "cflags": args.cflags,
        "binary_sha256": digest(args.binary),
        "source_sha256": digest(args.source),
        "m3_oracle_sha256": digest(args.m3_oracle),
        "probe": probe,
        "conclusions": {
            "D1": "no counterexample in fixed producer-real corpus; previously proved safe",
            "D2": "no counterexample in fixed producer-real corpus; proof remains open",
            "D4": "no counterexample in fixed producer-real corpus; proof remains open",
            "D8": "current orientation has concrete signed-i16 counterexamples",
            "zero_repair_current_orientation": "rejected-by-counterexample",
            "full_reduction": "not-authorized; search orientation and minimum repair",
        },
        "promotion_eligible": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
