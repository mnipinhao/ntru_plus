#!/usr/bin/env python3
"""Compare production GT and lazy ASM rowpack full-chain stage accounting."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections.abc import Sequence


MEDIAN_RE = re.compile(
    r"^(?P<metric>[A-Za-z0-9_]+)_cycles/call .*?\bmedian=(?P<median>[0-9.]+)"
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
        raise SystemExit(f"{label} output did not contain any cycle median rows")
    return medians


def require(metrics: dict[str, float], key: str, label: str) -> float:
    try:
        return metrics[key]
    except KeyError as exc:
        raise SystemExit(f"{label} output missing median row: {key}") from exc


def fmt(v: float) -> str:
    return f"{v:.3f}"


def print_rows(title: str, rows: Sequence[tuple[str, float, float]]) -> None:
    headers = ("stage / component", "production GT", "lazy ASM rowpack", "delta")
    rendered = [
        (name, fmt(gt), fmt(rowpack), fmt(rowpack - gt))
        for name, gt, rowpack in rows
    ]
    widths = [
        max(len(headers[i]), *(len(row[i]) for row in rendered))
        for i in range(len(headers))
    ]

    def emit(row: Sequence[str]) -> None:
        print("  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)))

    print(f"\n## {title}")
    emit(headers)
    emit(tuple("-" * w for w in widths))
    for row in rendered:
        emit(row)


def product_rows(gt: dict[str, float], rowpack: dict[str, float]) -> list[tuple[str, float, float]]:
    gt_ntt = require(gt, "poly_ntt", "production_gt_product")
    gt_basemul = require(gt, "poly_basemul", "production_gt_product")
    gt_invntt = require(gt, "poly_invntt", "production_gt_product")
    gt_pipeline = require(gt, "ntt_mul_pipeline", "production_gt_product")

    rp_ntt = require(rowpack, "rowpack_poly_ntt", "lazy_rowpack_product")
    rp_basemul = require(rowpack, "rowpack_poly_basemul", "lazy_rowpack_product")
    rp_invntt = require(rowpack, "rowpack_poly_invntt", "lazy_rowpack_product")
    rp_pipeline = require(rowpack, "rowpack_ntt_mul_pipeline", "lazy_rowpack_product")

    gt_accounted = 2.0 * gt_ntt + gt_basemul + gt_invntt
    rp_accounted = 2.0 * rp_ntt + rp_basemul + rp_invntt
    return [
        ("forward ntt (single)", gt_ntt, rp_ntt),
        ("forward ntt x2", 2.0 * gt_ntt, 2.0 * rp_ntt),
        ("basemul", gt_basemul, rp_basemul),
        ("invntt", gt_invntt, rp_invntt),
        ("accounted component sum", gt_accounted, rp_accounted),
        ("pipeline product total", gt_pipeline, rp_pipeline),
        ("unaccounted glue", gt_pipeline - gt_accounted, rp_pipeline - rp_accounted),
    ]


def product_add_rows(gt: dict[str, float], rowpack: dict[str, float]) -> list[tuple[str, float, float]]:
    gt_ntt = require(gt, "poly_ntt", "production_gt_product_add")
    gt_basemul_add = require(gt, "poly_basemul_add", "production_gt_product_add")
    gt_invntt = require(gt, "poly_invntt", "production_gt_product_add")
    gt_pipeline = require(gt, "ntt_basemul_add_pipeline", "production_gt_product_add")

    rp_ntt = require(rowpack, "rowpack_poly_ntt", "lazy_rowpack_product_add")
    rp_basemul_add = require(
        rowpack, "rowpack_poly_basemul_add", "lazy_rowpack_product_add"
    )
    rp_invntt = require(rowpack, "rowpack_poly_invntt", "lazy_rowpack_product_add")
    rp_pipeline = require(
        rowpack, "rowpack_ntt_basemul_add_pipeline", "lazy_rowpack_product_add"
    )

    gt_accounted = 3.0 * gt_ntt + gt_basemul_add + gt_invntt
    rp_accounted = 3.0 * rp_ntt + rp_basemul_add + rp_invntt
    return [
        ("forward ntt (single)", gt_ntt, rp_ntt),
        ("forward ntt x3", 3.0 * gt_ntt, 3.0 * rp_ntt),
        ("basemul_add", gt_basemul_add, rp_basemul_add),
        ("invntt", gt_invntt, rp_invntt),
        ("accounted component sum", gt_accounted, rp_accounted),
        ("pipeline add total", gt_pipeline, rp_pipeline),
        ("unaccounted glue", gt_pipeline - gt_accounted, rp_pipeline - rp_accounted),
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gt-product", required=True)
    parser.add_argument("--rowpack-product", required=True)
    parser.add_argument("--gt-add", required=True)
    parser.add_argument("--rowpack-add", required=True)
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    gt_product = run_bench("production_gt_product", [args.gt_product], args.verbose)
    rowpack_product = run_bench(
        "lazy_rowpack_product", [args.rowpack_product], args.verbose
    )
    gt_add = run_bench("production_gt_product_add", [args.gt_add], args.verbose)
    rowpack_add = run_bench("lazy_rowpack_product_add", [args.rowpack_add], args.verbose)

    product = product_rows(gt_product, rowpack_product)
    add = product_add_rows(gt_add, rowpack_add)
    print_rows("Product Fullchain Stage Accounting", product)
    print_rows("Product-Add Fullchain Stage Accounting", add)

    product_glue_delta = product[-1][2] - product[-1][1]
    add_glue_delta = add[-1][2] - add[-1][1]
    print("\n## Interpretation Inputs")
    print(
        "product unaccounted glue delta = actual pipeline delta - accounted component delta "
        f"= {product_glue_delta:+.3f} cycles"
    )
    print(
        "product-add unaccounted glue delta = actual pipeline delta - accounted component delta "
        f"= {add_glue_delta:+.3f} cycles"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
