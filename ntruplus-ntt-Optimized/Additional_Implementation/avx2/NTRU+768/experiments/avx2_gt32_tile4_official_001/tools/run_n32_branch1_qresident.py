#!/usr/bin/env python3
"""Run the isolated N32 Branch-1 q-register-resident gate."""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
from pathlib import Path


def run(binary: Path, iterations: int) -> dict[str, object]:
    completed = subprocess.run(
        [str(binary.resolve()), str(iterations)], check=True,
        text=True, capture_output=True)
    samples = []
    for line in completed.stdout.splitlines():
        fields = line.split(",")
        if len(fields) == 5 and fields[0] == "SAMPLE":
            samples.append({
                "sample": int(fields[1]),
                "qmem_tsc": float(fields[2]),
                "qreg_tsc": float(fields[3]),
                "qreg_minus_qmem_tsc": float(fields[4]),
            })
    assert len(samples) == 20
    deltas = [float(sample["qreg_minus_qmem_tsc"]) for sample in samples]
    median = statistics.median(deltas)
    return {
        "binary": str(binary),
        "samples": samples,
        "median_qmem_tsc": statistics.median(
            float(sample["qmem_tsc"]) for sample in samples),
        "median_qreg_tsc": statistics.median(
            float(sample["qreg_tsc"]) for sample in samples),
        "median_qreg_minus_qmem_tsc": median,
        "qreg_wins": sum(delta < 0.0 for delta in deltas),
        "mad_delta_tsc": statistics.median(abs(delta - median) for delta in deltas),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=10000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = {
        "schema": "ntruplus768-gt32-n32-branch1-qresident-short-v1",
        "experiment": "GT-N32-BRANCH1-QRESIDENT-016",
        "iterations": args.iterations,
        "comparison": (
            "identical three-stage/four-chain DAG; twelve q correction "
            "multiplies use memory-source q or one preloaded YMM register"
        ),
        "placements": {
            "normal": run(args.binary, args.iterations),
            "reversed": run(args.reversed_binary, args.iterations),
        },
    }
    normal = result["placements"]["normal"]
    reversed_result = result["placements"]["reversed"]
    passed = (
        normal["median_qreg_minus_qmem_tsc"] <= -2.0
        and reversed_result["median_qreg_minus_qmem_tsc"] <= -2.0
        and normal["qreg_wins"] >= 18
        and reversed_result["qreg_wins"] >= 18
    )
    result["decision"] = (
        "pass-expand-to-double-spill-production-gate" if passed
        else "stop-branch1-q-register-residency"
    )
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(args.output)
    for placement, record in result["placements"].items():
        print(placement, record["median_qmem_tsc"], record["median_qreg_tsc"],
              record["median_qreg_minus_qmem_tsc"],
              f"{record['qreg_wins']}/20", "MAD", record["mad_delta_tsc"])
    print(result["decision"])


if __name__ == "__main__":
    main()
