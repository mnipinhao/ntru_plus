#!/usr/bin/env python3
"""Run fresh pinned paired launches for the two M3C3 full-D4 reducers."""

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

BARRETT = "signed-Barrett"
MONTGOMERY = "Montgomery-identity"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--cpu", type=int, required=True)
    parser.add_argument("--launches", type=int, default=9)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--proof", type=Path, required=True)
    parser.add_argument("--asm-source", type=Path, required=True)
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
            if record["comparison"] == "full-D4-reduction":
                grouped[record["implementation"]].append(record["median_cycles"])
        for implementation in (BARRETT, MONTGOMERY):
            by_launch[implementation].append(
                statistics.median(grouped[implementation]))

    barrett_values = by_launch[BARRETT]
    montgomery_values = by_launch[MONTGOMERY]
    deltas = [montgomery - barrett
              for barrett, montgomery in zip(barrett_values, montgomery_values)]
    median_delta = statistics.median(deltas)
    barrett_median = statistics.median(barrett_values)
    montgomery_median = statistics.median(montgomery_values)
    winner = MONTGOMERY if median_delta < 0 else BARRETT if median_delta > 0 else "tie"
    audit = json.loads(args.audit.read_text())
    proof = json.loads(args.proof.read_text())
    report = {
        "schema": "gt-g1c-m3c3-reduction-paired/v1",
        "benchmark_class": (
            "repository-local-g1c-m3c3-reduction-paired-not-for-promotion"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "cpu": args.cpu,
        "cpu_model": next((line.split(":", 1)[1].strip()
                           for line in Path("/proc/cpuinfo").read_text().splitlines()
                           if line.lower().startswith("model name")), "unknown"),
        "hostname": platform.node(),
        "kernel": platform.release(),
        "compiler": args.compiler,
        "cflags": args.cflags,
        "binary_sha256": digest(args.binary),
        "launches": args.launches,
        "blocks_per_launch": documents[0]["blocks"],
        "observations_per_slot": documents[0]["observations_per_slot"],
        "inner_calls_per_observation": documents[0]["inner_calls"],
        "same_input_residency_and_output_address": True,
        "barrett": {"name": BARRETT, "cycles_by_launch": barrett_values,
                    "median_cycles": barrett_median,
                    "proved_output_range": [-1728, 1728]},
        "montgomery_identity": {
            "name": MONTGOMERY, "cycles_by_launch": montgomery_values,
            "median_cycles": montgomery_median,
            "proved_output_range": [-1794, 1802]},
        "paired": {
            "montgomery_minus_barrett_by_launch": deltas,
            "median_montgomery_minus_barrett_cycles": median_delta,
            "montgomery_over_barrett": montgomery_median / barrett_median,
            "montgomery_faster_launches": sum(delta < 0 for delta in deltas),
        },
        "winner": winner,
        "interpretation": (
            "isolated full-array control price only; a fused D4 tail has "
            "different load/store and scheduling costs"),
        "static_audit": audit,
        "localized_proof_decision": proof["decision"],
        "source_sha256": {
            "audit": digest(args.audit), "proof": digest(args.proof),
            "asm": digest(args.asm_source), "bench": digest(args.bench_source)},
        "upstream": json.loads((args.upstream / "UPSTREAM.json").read_text()),
        "promotion_eligible": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
