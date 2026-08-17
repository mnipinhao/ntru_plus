#!/usr/bin/env python3
"""Compare Official Main and GT32 R1-U with hardware core cycles."""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import subprocess
from pathlib import Path


def perf_cycles(binary: Path, iterations: int, gate: str,
                backend: str) -> dict[str, float]:
    process = subprocess.run([
        "perf", "stat", "-x", ";", "-e", "cpu_core/cycles/", "--",
        str(binary), str(iterations), gate, backend,
    ], check=True, text=True, capture_output=True)
    for line in process.stderr.splitlines():
        fields = line.split(";")
        if len(fields) < 5 or not fields[0].strip().isdigit():
            continue
        count = int(fields[0].strip())
        if "cycles" not in fields[2]:
            continue
        running_percent = float(fields[4].strip())
        return {
            "raw_count": count,
            "cycles_per_call": count / iterations,
            "time_running_ns": int(fields[3].strip()),
            "running_percent": running_percent,
            "scaling_factor": 100.0 / running_percent,
        }
    raise RuntimeError(f"missing cycles count for {binary} {gate} {backend}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", required=True, type=Path)
    parser.add_argument("--iterations", type=int, default=1000000)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    gates = ("bm", "bm_inverse", "full", "full_crep")
    binaries = {"normal": args.binary, "reversed": args.reversed_binary}
    result = {
        "schema": "ntruplus768-gt32-r1u-vs-official-main-core-cycles-v1",
        "experiment": "GT32-AOS-DOT-REDC16-001-OFFICIAL-CYCLES",
        "unit": "PMU cpu_core/cycles per call",
        "cpu": 1,
        "iterations": args.iterations,
        "repeats": args.repeats,
        "binaries": {},
    }
    for placement, binary in binaries.items():
        placement_result = {
            "path": str(binary),
            "sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
            "gates": {},
        }
        for gate in gates:
            records = {"official": [], "gt32-r1u": []}
            for repeat in range(args.repeats):
                order = (("official", "gt32-r1u") if repeat % 2 == 0
                         else ("gt32-r1u", "official"))
                for backend in order:
                    records[backend].append(
                        perf_cycles(binary, args.iterations, gate, backend))
            official = statistics.median(
                item["cycles_per_call"] for item in records["official"])
            gt = statistics.median(
                item["cycles_per_call"] for item in records["gt32-r1u"])
            placement_result["gates"][gate] = {
                "official": records["official"],
                "gt32_r1u": records["gt32-r1u"],
                "official_median_cycles": official,
                "gt32_r1u_median_cycles": gt,
                "gt32_minus_official_cycles": gt - official,
                "gt32_vs_official_ratio": gt / official,
                "gt32_vs_official_percent": 100.0 * (gt / official - 1.0),
            }
        result["binaries"][placement] = placement_result
    result["decision"] = (
        "GT32-R1U-full-polymul-faster-than-Official-Main"
        if all(entry["gates"]["full"]["gt32_vs_official_ratio"] < 1.0
               for entry in result["binaries"].values())
        else "GT32-R1U-full-polymul-not-stably-faster-than-Official-Main")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for placement, entry in result["binaries"].items():
        print(placement)
        for gate, values in entry["gates"].items():
            print(f"  {gate}: official={values['official_median_cycles']:.3f}, "
                  f"gt32-r1u={values['gt32_r1u_median_cycles']:.3f}, "
                  f"delta={values['gt32_minus_official_cycles']:.3f}, "
                  f"pct={values['gt32_vs_official_percent']:.3f}%")
    print(f"decision={result['decision']}")


if __name__ == "__main__":
    main()
