#!/usr/bin/env python3
"""Compare rowpack Forward NTT overhead against production GT."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections.abc import Sequence


MEDIAN_RE = re.compile(
    r"^(?P<metric>[A-Za-z0-9_]+)_(?:cycles|cntvct_ticks)/call "
    r".*?\bmedian=(?P<median>[0-9.]+)"
)


def run_bench(label: str, argv: Sequence[str], verbose: bool) -> dict[str, float]:
    proc = subprocess.run(
        list(argv),
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if verbose:
        sys.stdout.write(f"\n## raw {label}\n")
        sys.stdout.write(proc.stdout)
    if proc.returncode != 0:
        raise SystemExit(f"{label} failed with exit code {proc.returncode}")

    medians: dict[str, float] = {}
    for line in proc.stdout.splitlines():
        match = MEDIAN_RE.match(line)
        if match:
            medians[match.group("metric")] = float(match.group("median"))

    if not medians:
        raise SystemExit(f"{label} output did not contain any median rows")
    return medians


def require(metrics: dict[str, float], key: str, label: str) -> float:
    try:
        return metrics[key]
    except KeyError as exc:
        raise SystemExit(f"{label} output missing median row: {key}") from exc


def fmt(value: float) -> str:
    return f"{value:.3f}"


def print_table(rows: Sequence[tuple[str, float, str]]) -> None:
    headers = ("path / component", "median cycles", "delta / interpretation")
    rendered = [(name, fmt(value), note) for name, value, note in rows]
    widths = [
        max(len(headers[i]), *(len(row[i]) for row in rendered))
        for i in range(len(headers))
    ]

    def emit(row: Sequence[str]) -> None:
        print("  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)))

    emit(headers)
    emit(tuple("-" * w for w in widths))
    for row in rendered:
        emit(row)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gt-forward", required=True)
    parser.add_argument("--rowpack-forward", required=True)
    parser.add_argument("--probes", required=True)
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    gt = run_bench("production_gt_forward", [args.gt_forward], args.verbose)
    rowpack = run_bench("lazy_rowpack_forward", [args.rowpack_forward], args.verbose)
    probes = run_bench("rowpack_forward_overhead_probes", [args.probes], args.verbose)

    gt_ntt = require(gt, "poly_ntt", "production_gt_forward")
    rowpack_ntt = require(rowpack, "rowpack_poly_ntt", "lazy_rowpack_forward")
    scatter = require(
        probes, "rowpack_forward_scatter_only", "rowpack_forward_overhead_probes"
    )
    lane_store = require(
        probes,
        "rowpack_forward_lane_store_candidate",
        "rowpack_forward_overhead_probes",
    )
    store_ready = require(
        probes, "rowpack_forward_store_ready", "rowpack_forward_overhead_probes"
    )
    zero_store = require(
        probes, "rowpack_forward_zero_store", "rowpack_forward_overhead_probes"
    )
    transpose_no_store = require(
        probes,
        "rowpack_forward_transpose_no_store",
        "rowpack_forward_overhead_probes",
    )
    convert = require(
        probes, "gt_to_rowpack_scalar_convert", "rowpack_forward_overhead_probes"
    )

    rowpack_delta = rowpack_ntt - gt_ntt
    compute_estimate = rowpack_ntt - scatter
    compute_estimate_delta = compute_estimate - gt_ntt
    hybrid_scalar = gt_ntt + convert
    hybrid_scalar_delta_vs_rowpack = hybrid_scalar - rowpack_ntt
    lane_store_delta = lane_store - scatter
    scatter_minus_zero_store = scatter - zero_store
    scatter_minus_store_ready = scatter - store_ready

    print("\n## Forward NTT Overhead Breakdown")
    print_table(
        [
            ("production GT Forward NTT", gt_ntt, "baseline"),
            (
                "current rowpack Forward v2",
                rowpack_ntt,
                f"{rowpack_delta:+.3f} vs production GT",
            ),
            (
                "rowpack scatter/transpose-only",
                scatter,
                "direct Neon probe; excludes NTT arithmetic/reduction",
            ),
            (
                "rowpack lane-store candidate",
                lane_store,
                f"{lane_store_delta:+.3f} vs current scatter/transpose",
            ),
            (
                "rowpack store-ready load+store",
                store_ready,
                "direct lower-bound probe; input already in rowpack plane order",
            ),
            (
                "rowpack zero-store lower bound",
                zero_store,
                "direct lower-bound probe; no source-vector loads",
            ),
            (
                "rowpack transpose-only no-store",
                transpose_no_store,
                "direct lower-bound probe; no rowpack output stores",
            ),
            (
                "rowpack compute-only estimate",
                compute_estimate,
                f"{compute_estimate_delta:+.3f} vs production GT; "
                "rowpack_full - scatter_only",
            ),
            (
                "GT-to-rowpack scalar conversion",
                convert,
                "direct scalar hybrid conversion probe",
            ),
            (
                "production GT + scalar conversion",
                hybrid_scalar,
                f"{hybrid_scalar_delta_vs_rowpack:+.3f} vs current rowpack v2",
            ),
        ]
    )

    print("\n## Gate Inputs")
    print(f"rowpack Forward overhead per NTT = {rowpack_delta:+.3f} cycles")
    print(
        "scatter/transpose-only probe covers "
        f"{scatter:.3f} cycles of rowpack Forward v2"
    )
    print(
        "scatter minus zero-store lower bound = "
        f"{scatter_minus_zero_store:+.3f} cycles"
    )
    print(
        "lane-store candidate delta vs current scatter = "
        f"{lane_store_delta:+.3f} cycles"
    )
    print(
        "scatter minus store-ready load+store = "
        f"{scatter_minus_store_ready:+.3f} cycles"
    )
    print(
        "transpose-only no-store = "
        f"{transpose_no_store:.3f} cycles"
    )
    print(
        "compute-only estimate leaves "
        f"{compute_estimate_delta:+.3f} cycles vs production GT"
    )
    print(
        "hybrid scalar path would be "
        f"{hybrid_scalar_delta_vs_rowpack:+.3f} cycles vs current rowpack v2"
    )
    print("\n## Continue Criteria")
    print("weak continue: find >=100 cycles/NTT recoverable Forward overhead")
    print("strong continue: find >=200 cycles/NTT recoverable Forward overhead")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
