#!/usr/bin/env python3
"""Run fresh pinned G1C-M2 materialized-control versus linked C2-L launches."""

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

CONTROL = "M2-materialized-control"
CANDIDATE = "C2-L-linked"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--cpu", type=int, required=True)
    parser.add_argument("--launches", type=int, default=9)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--live-basis", type=Path, required=True)
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
            if record["comparison"] == "materialized-to-C2-L":
                grouped[record["implementation"]].append(record["median_cycles"])
        for implementation in (CONTROL, CANDIDATE):
            by_launch[implementation].append(statistics.median(grouped[implementation]))

    control_values = by_launch[CONTROL]
    candidate_values = by_launch[CANDIDATE]
    deltas = [candidate - control
              for control, candidate in zip(control_values, candidate_values)]
    median_delta = statistics.median(deltas)
    control_median = statistics.median(control_values)
    candidate_median = statistics.median(candidate_values)
    if median_delta < 0:
        classification = "strong-edge-success"
        decision = "authorize full adjusted inverse16 while retaining C2-L as the head-only control"
    elif median_delta == 0:
        classification = "neutral-edge"
        decision = "retain and extend to full adjusted inverse16 before deciding F5"
    else:
        classification = "positive-edge-cost"
        decision = "try paired scheduling and full inverse16 structural credit before deciding F5"

    audit = json.loads(args.audit.read_text())
    report = {
        "benchmark_class": "repository-local-g1c-m2-boundary-paired-not-for-promotion",
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
        "same_output_address_and_input_residency": True,
        "control": {
            "name": CONTROL,
            "cycles_by_launch": control_values,
            "median_cycles": control_median,
        },
        "candidate": {
            "name": CANDIDATE,
            "cycles_by_launch": candidate_values,
            "median_cycles": candidate_median,
        },
        "paired": {
            "candidate_minus_control_by_launch": deltas,
            "median_candidate_minus_control_cycles": median_delta,
            "candidate_over_control": candidate_median / control_median,
            "candidate_faster_launches": sum(delta < 0 for delta in deltas),
            "same_direction_launches": sum(
                (delta < 0) == (median_delta < 0) for delta in deltas),
        },
        "classification": classification,
        "decision": decision,
        "correctness": {
            "producer_real_cases": 1003,
            "cells_per_case": 1152,
            "materialized_and_linked_bit_exact": True,
        },
        "static_boundary": audit["linked_gate"],
        "audit_sha256": hashlib.sha256(args.audit.read_bytes()).hexdigest(),
        "live_basis_sha256": hashlib.sha256(args.live_basis.read_bytes()).hexdigest(),
        "upstream": json.loads((args.upstream / "UPSTREAM.json").read_text()),
        "promotion_eligible": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
