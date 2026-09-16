#!/usr/bin/env python3
"""Capture balanced LBR profiles of the exact Experiment 139 ELFs."""

import json
import subprocess
from pathlib import Path


EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[1]
E139 = ROOT / "experiments/gt32_ql2_production_139"
RAW = EXP / "raw"
BINARIES = {"official": E139 / "build/official", "gt": E139 / "build/gt"}


def main():
    RAW.mkdir(exist_ok=True)
    rows = []
    sequence = 0
    for block in range(1, 65):
        order = ("official", "gt") if block % 2 else ("gt", "official")
        for position, implementation in enumerate(order, 1):
            sequence += 1
            data = RAW / f"{sequence:03d}-{implementation}.data"
            subprocess.run([
                "perf", "record", "-q", "-e", "cpu_core/cycles/u", "-c", "50000",
                "-j", "any_call,any_ret", "-o", str(data), "--",
                "taskset", "-c", "1", str(BINARIES[implementation].resolve())
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            rows.append({"block": block, "position": position,
                         "implementation": implementation,
                         "perf_data": str(data.relative_to(EXP))})
    manifest = {
        "schema": "gt32-ql2-production-profile-140-lbr-capture-v1",
        "event": "cpu_core/cycles/u period=50000 any_call,any_ret",
        "cpu": 1,
        "binaries": {name: {"path": str(path.resolve())}
                     for name, path in BINARIES.items()},
        "rows": rows,
    }
    (EXP / "lbr-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
