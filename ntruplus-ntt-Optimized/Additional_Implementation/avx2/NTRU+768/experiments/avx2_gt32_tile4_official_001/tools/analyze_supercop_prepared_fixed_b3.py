#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import re
import statistics
from pathlib import Path


LABELS = ("enc_generic", "enc_fixed", "dec_generic", "dec_fixed",
          "prepare_pk_generic", "prepare_pk_fixed",
          "prepare_sk_generic", "prepare_sk_fixed")


def stabilized_q2(values: list[int]) -> float:
    expanded = sorted(value for value in values for _ in range(8))
    n = len(values)
    return sum(expanded[3 * n:5 * n]) / (2 * n)


def parse(path: Path) -> dict[str, float]:
    values = {label: [] for label in LABELS}
    backend = None
    for line in path.read_text().splitlines():
        fields = line.split()
        if fields[:1] == ["cpucycles_implementation"]:
            backend = fields[1]
        for label in LABELS:
            if fields[:2] == [f"{label}_cycles", "-"]:
                base = int(fields[2])
                values[label].extend(base + int(delta)
                                     for delta in re.findall(r"[+-]\d+", fields[3]))
    if backend != "default-perfevent":
        raise ValueError(f"unexpected backend {backend}")
    return {label: stabilized_q2(items) for label, items in values.items()}


def bootstrap_median_ci(values: list[float], samples: int = 100000) -> list[float]:
    rng = random.Random(20260814)
    estimates = sorted(statistics.median(rng.choices(values, k=len(values)))
                       for _ in range(samples))
    return [estimates[int(samples * 0.025)], estimates[int(samples * 0.975)]]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    launches = [{"path": str(path), "q2": parse(path)}
                for path in sorted(args.input_dir.glob("run-*.out"))]
    summary = {}
    for op, generic, fixed, prep_generic, prep_fixed in (
            ("encap", "enc_generic", "enc_fixed",
             "prepare_pk_generic", "prepare_pk_fixed"),
            ("decap", "dec_generic", "dec_fixed",
             "prepare_sk_generic", "prepare_sk_fixed")):
        deltas = [item["q2"][fixed] - item["q2"][generic]
                  for item in launches]
        prep_deltas = [item["q2"][prep_fixed] - item["q2"][prep_generic]
                       for item in launches]
        delta_median = statistics.median(deltas)
        generic_median = statistics.median(
            item["q2"][generic] for item in launches)
        prep_delta = statistics.median(prep_deltas)
        saving = -delta_median
        summary[op] = {
            "generic_p0_median_cycles": generic_median,
            "fixed_b3_median_cycles": statistics.median(
                item["q2"][fixed] for item in launches),
            "fixed_minus_generic_median_cycles": delta_median,
            "fixed_minus_generic_percent": 100.0 * delta_median / generic_median,
            "bootstrap_median_95ci_cycles": bootstrap_median_ci(deltas),
            "favorable_launches": sum(delta < 0 for delta in deltas),
            "launches": len(deltas),
            "prepare_extra_median_cycles": prep_delta,
            "incremental_break_even_calls": (prep_delta / saving
                                                if prep_delta > 0 and saving > 0
                                                else None),
            "deltas_cycles": deltas,
            "prepare_deltas_cycles": prep_deltas,
        }
    result = {
        "schema": "ntruplus768-gt32-prepared-fixed-b3-incremental-v1",
        "cycle_backend": "default-perfevent/PERF_COUNT_HW_CPU_CYCLES",
        "summary": summary,
        "launch_data": launches,
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
