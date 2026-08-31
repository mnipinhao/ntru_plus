#!/usr/bin/env python3
"""Run three rotated-order diagnostic batches and stabilize their quartiles."""

from __future__ import annotations

import json
import platform
import re
import statistics
import subprocess
import sys

BATCHES = 3
TIMING = re.compile(
    r"^timing,name=([^,]+),unit=ns_per_call,q1=([0-9.]+),"
    r"median=([0-9.]+),q3=([0-9.]+),"
)


def main() -> None:
    binary = sys.argv[1] if len(sys.argv) > 1 else "./bench_gt864_boundary"
    raw = []
    by_variant: dict[str, list[dict[str, float]]] = {}
    for batch in range(BATCHES):
        output = subprocess.check_output([binary], text=True)
        raw.append({"batch": batch + 1, "stdout": output})
        for line in output.splitlines():
            match = TIMING.match(line)
            if match:
                name, q1, median, q3 = match.groups()
                by_variant.setdefault(name, []).append({
                    "q1": float(q1),
                    "median": float(median),
                    "q3": float(q3),
                })
    stabilized = {}
    for name, batches in by_variant.items():
        assert len(batches) == BATCHES
        stabilized[name] = {
            field: statistics.median(batch[field] for batch in batches)
            for field in ("q1", "median", "q3")
        }
    fr = stabilized["M4.2_FR-0_full_boundary"]["median"]
    fc = stabilized["M4.2_FC-0_full_boundary"]["median"]
    lane = stabilized["M4.3_FR-lane-0_full_boundary"]["median"]
    payload = {
        "schema": 1,
        "authority": "diagnostic_only_not_SUPERCOP",
        "timer": "mach_continuous_time",
        "execution_order": "sample_rotated",
        "common_input": "P8_plus_tail_896",
        "full_boundary_output": "BaseMul_SoA_864",
        "host": platform.platform(),
        "batches": raw,
        "stabilized_ns_per_call": stabilized,
        "comparisons": {
            "FR0_faster_than_FC0_percent": 100.0 * (fc - fr) / fc,
            "FR_lane0_vs_FR0_percent": 100.0 * (lane - fr) / fr,
        },
        "promotion_claim": False,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
