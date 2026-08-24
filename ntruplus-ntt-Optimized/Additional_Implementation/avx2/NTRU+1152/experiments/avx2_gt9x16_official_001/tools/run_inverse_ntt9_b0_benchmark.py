#!/usr/bin/env python3
"""Run ITAIL-ASM-B0 pure and optimized A/B paired launches."""

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

A = "A-vector-canonical-repack-plus-B0"
B = "B-direct-physical-P-B0"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--cpu", type=int, required=True)
    parser.add_argument("--launches", type=int, default=9)
    parser.add_argument("--proof", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--bench-source", type=Path, required=True)
    parser.add_argument("--upstream", type=Path, required=True)
    parser.add_argument("--compiler", required=True)
    parser.add_argument("--cflags", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite {args.output}")

    by_launch = defaultdict(list)
    pure = []
    documents = []
    for _ in range(args.launches):
        run = subprocess.run(
            ["taskset", "-c", str(args.cpu), str(args.binary.resolve())],
            check=True, text=True, stdout=subprocess.PIPE)
        document = json.loads(run.stdout)
        documents.append(document)
        pure.append(document["pure_8x_vector_inverse9_median_cycles"])
        grouped = defaultdict(list)
        for record in document["records"]:
            if record["implementation"] in (A, B):
                grouped[record["implementation"]].append(record["median_cycles"])
        for name in (A, B):
            by_launch[name].append(statistics.median(grouped[name]))

    medians = {name: statistics.median(by_launch[name]) for name in (A, B)}
    deltas = [right - left for left, right in zip(by_launch[A], by_launch[B])]
    proof = json.loads(args.proof.read_text())
    audit = json.loads(args.audit.read_text())
    report = {
        "benchmark_class": "repository-local-itail-asm-b0-not-for-promotion",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "cpu": args.cpu,
        "cpu_model": next((line.split(":", 1)[1].strip()
                           for line in Path("/proc/cpuinfo").read_text().splitlines()
                           if line.lower().startswith("model name")), "unknown"),
        "hostname": platform.node(), "kernel": platform.release(),
        "compiler": args.compiler, "cflags": args.cflags,
        "binary_sha256": hashlib.sha256(args.binary.read_bytes()).hexdigest(),
        "launches": args.launches,
        "blocks_per_launch": documents[0]["blocks"],
        "observations_per_slot": documents[0]["observations_per_slot"],
        "pure_8x_vector_inverse9": {
            "cycles_by_launch": pure,
            "median_cycles": statistics.median(pure),
            "input_residency": "precomputed C2 output resident in benchmark storage",
            "includes": "72 B loads, six radix3 per (branch,j), final 72 stores",
        },
        "full_C2_store_to_inverse9": {
            "cycles_by_launch": dict(by_launch), "median_cycles": medians,
            "paired_B_minus_A": {"by_launch": deltas,
                                 "median_cycles": statistics.median(deltas),
                                 "B_faster_launches": sum(value < 0 for value in deltas),
                                 "B_over_A": medians[B] / medians[A]},
            "A_contract": "C2 stores, explicit 72-load+72-store vector natural-P repack, same B0 arithmetic macro",
            "B_contract": "C2 stores, direct physical-P loads, same B0 arithmetic macro",
        },
        "static": {
            "montgomery_chains_per_inverse9": proof["static_counts_per_vector_inverse9"]["montgomery_chains"],
            "montgomery_chains_total": audit["montgomery_chain_count"]["eight_vector_inverse9_body"],
            "peak_live_ymm": audit["liveness"]["peak_live_ymm"],
            "stack_spills": audit["liveness"]["stack_spills"],
        },
        "proof_sha256": hashlib.sha256(args.proof.read_bytes()).hexdigest(),
        "audit_sha256": hashlib.sha256(args.audit.read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256(args.source.read_bytes()).hexdigest(),
        "bench_source_sha256": hashlib.sha256(args.bench_source.read_bytes()).hexdigest(),
        "upstream": json.loads((args.upstream / "UPSTREAM.json").read_text()),
        "interpretation": "optimized representation-edge price; repository-local diagnostic only",
        "promotion_eligible": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
