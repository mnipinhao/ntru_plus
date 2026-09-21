#!/usr/bin/env python3
"""Matched diagnostic PMU counts for NTRU+768 same-ELF named regions."""

from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
from datetime import datetime, timezone
from pathlib import Path

EVENT_GROUPS = {
    "basic": (
        "cpu_core/cycles/u", "cpu_core/instructions/u",
        "cpu_core/mem_inst_retired.all_loads/u",
        "cpu_core/mem_inst_retired.all_stores/u",
    ),
    "frontend": (
        "cpu_core/cycles/u", "cpu_core/idq.dsb_uops/u",
        "cpu_core/idq.mite_uops/u",
        "cpu_core/idq_uops_not_delivered.core/u",
    ),
    "cache": (
        "cpu_core/cycles/u", "cpu_core/frontend_retired.l1i_miss/u",
        "cpu_core/mem_load_retired.l1_miss/u",
        "cpu_core/mem_load_retired.l2_miss/u",
    ),
    "blocks": (
        "cpu_core/cycles/u", "cpu_core/ld_blocks.store_forward/u",
        "cpu_core/ld_blocks.address_alias/u",
        "cpu_core/resource_stalls.sb/u",
    ),
}


def parse_counts(stderr: str, events: tuple[str, ...]) -> tuple[dict[str, int], dict[str, float]]:
    counts: dict[str, int] = {}
    running: dict[str, float] = {}
    for line in stderr.splitlines():
        fields = line.split(";")
        if len(fields) < 5:
            continue
        name = fields[2].strip().removesuffix("/u")
        event = next((item for item in events
                      if item.removesuffix("/u") == name), None)
        raw = fields[0].strip().replace(",", "")
        if event is None or not raw.isdigit():
            continue
        counts[event] = int(raw)
        try:
            running[event] = float(fields[4].strip().rstrip("%")) / 100.0
        except ValueError:
            running[event] = 1.0
    return counts, running


def one(binary: Path, cpu: int, region: str, impl: str, iterations: int,
        events: tuple[str, ...]) -> dict[str, object]:
    command = ["taskset", "-c", str(cpu), "perf", "stat", "-x", ";",
               "-e", ",".join(events), "--", str(binary), "--perf",
               region, impl, str(iterations)]
    process = subprocess.run(command, text=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, check=False,
                             env=os.environ.copy())
    counts, running = parse_counts(process.stderr, events)
    return {"returncode": process.returncode, "stdout": process.stdout,
            "stderr": process.stderr, "counts": counts, "running": running}


def median(values: list[float]) -> float:
    return float(statistics.median(values))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--cpu", type=int, default=1)
    parser.add_argument("--iterations", type=int, default=100000)
    parser.add_argument("--fresh-processes", type=int, default=3)
    parser.add_argument("--region", action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite {args.output}")
    raw_dir = args.output / "raw"
    raw_dir.mkdir(parents=True)
    result: dict[str, object] = {
        "schema": "ntruplus768-region-pmu/v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "binary": str(args.binary.resolve()), "cpu": args.cpu,
        "iterations": args.iterations,
        "fresh_processes": args.fresh_processes,
        "role": "diagnostic-only-not-promotion-headline",
        "contract": (
            "mode selected before the counted loop; one identical process-level "
            "noop run is subtracted; setup is amortized over the stated iterations"
        ),
        "regions": {},
    }
    for region in args.region:
        region_result: dict[str, object] = {}
        for group, events in EVENT_GROUPS.items():
            rows: dict[str, list[dict[str, object]]] = {
                "noop": [], "official": [], "gt32": []}
            for variant, selected_region in (("noop", "noop"),
                                             ("official", region),
                                             ("gt32", region)):
                for launch in range(1, args.fresh_processes + 1):
                    record = one(args.binary, args.cpu, selected_region,
                                 variant, args.iterations, events)
                    stem = raw_dir / f"{region.replace('.', '_')}-{group}-{variant}-{launch}"
                    stem.with_suffix(".out").write_text(str(record["stdout"]))
                    stem.with_suffix(".err").write_text(str(record["stderr"]))
                    rows[variant].append(record)
            medians = {variant: {event: median([
                float(row["counts"][event]) for row in records
                if event in row["counts"]])
                for event in events if all(event in row["counts"] for row in records)}
                for variant, records in rows.items()}
            adjusted: dict[str, dict[str, float]] = {}
            for variant in ("official", "gt32"):
                adjusted[variant] = {
                    event: (medians[variant][event] - medians["noop"][event]) /
                    args.iterations
                    for event in events if event in medians[variant]
                    and event in medians["noop"]
                }
            valid = all(
                row["returncode"] == 0 and len(row["counts"]) == len(events)
                and all(value >= 0.99 for value in row["running"].values())
                for records in rows.values() for row in records)
            deltas = {event: adjusted.get("gt32", {}).get(event, 0.0)
                      - adjusted.get("official", {}).get(event, 0.0)
                      for event in events if event in adjusted.get("gt32", {})
                      and event in adjusted.get("official", {})}
            region_result[group] = {
                "events": list(events), "valid": valid,
                "medians": medians, "per_operation_adjusted": adjusted,
                "gt32_minus_official": deltas,
            }
        result["regions"][region] = region_result
    (args.output / "summary.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result["regions"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
