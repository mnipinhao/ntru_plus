#!/usr/bin/env python3
"""Run fresh-launch caged M-Q24 midpoint measurements."""

from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
from pathlib import Path


LINE = re.compile(
    r"region=(\S+) metric=(\S+) control=([-0-9.]+) candidate=([-0-9.]+) "
    r"delta=([-0-9.]+) wins=(\d+)/(\d+)"
)


def run(binary: Path, iterations: int, cpu: int, aslr_off: bool) -> dict:
    command = [str(binary), str(iterations), str(cpu)]
    if aslr_off:
        command = ["setarch", "x86_64", "-R", *command]
    output = subprocess.check_output(command, text=True)
    metrics = {}
    for match in LINE.finditer(output):
        metrics[f"{match.group(1)}.{match.group(2)}"] = {
            "control": float(match.group(3)),
            "candidate": float(match.group(4)),
            "delta": float(match.group(5)),
            "wins": int(match.group(6)),
            "samples": int(match.group(7)),
        }
    if "correctness=pass" not in output:
        raise RuntimeError(f"correctness marker missing: {binary}")
    return {"metrics": metrics, "raw": output}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--launches", type=int, default=8)
    parser.add_argument("--iterations", type=int, default=4000)
    parser.add_argument("--cpu", type=int, default=1)
    args = parser.parse_args()
    payload = {"schema": "gt32-m-q24-midpoint-local-v1", "cpu": args.cpu,
               "launches": args.launches, "iterations": args.iterations, "variants": {}}
    for variant in ["share_a", "share_ad", "share_adb"]:
        binary = (args.build / f"bench_m_q24_{variant}").resolve()
        variant_data = {"binary": str(binary), "settings": {}}
        for setting, aslr_off in [("aslr_on", False), ("aslr_off", True)]:
            launches = [run(binary, args.iterations, args.cpu, aslr_off)
                        for _ in range(args.launches)]
            keys = launches[0]["metrics"]
            summary = {}
            for key in keys:
                values = [launch["metrics"][key]["delta"] for launch in launches]
                summary[key] = {"launch_median_delta": statistics.median(values),
                                "negative_launches": sum(value < 0 for value in values),
                                "deltas": values}
            variant_data["settings"][setting] = {"summary": summary, "launches": launches}
        payload["variants"][variant] = variant_data
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
