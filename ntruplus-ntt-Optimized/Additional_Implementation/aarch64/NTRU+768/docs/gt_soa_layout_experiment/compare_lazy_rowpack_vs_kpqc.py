#!/usr/bin/env python3
"""Run and summarize KPQC final / production GT / lazy rowpack cycle gates."""

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


def value(metrics: dict[str, float], key: str) -> float | None:
    return metrics.get(key)


def fmt(v: float | None) -> str:
    if v is None:
        return "n/a"
    return f"{v:.3f}"


def delta(candidate: float | None, baseline: float | None) -> str:
    if candidate is None or baseline is None:
        return "n/a"
    d = candidate - baseline
    return f"{d:+.3f}"


def print_table(rows: Sequence[tuple[str, float | None, float | None, float | None]]) -> None:
    headers = (
        "path",
        "KPQC final",
        "production GT",
        "lazy ASM rowpack",
        "rowpack vs KPQC",
        "rowpack vs GT",
    )
    rendered = [
        (
            name,
            fmt(kpqc),
            fmt(gt),
            fmt(rowpack),
            delta(rowpack, kpqc),
            delta(rowpack, gt),
        )
        for name, kpqc, gt, rowpack in rows
    ]
    widths = [
        max(len(headers[i]), *(len(row[i]) for row in rendered))
        for i in range(len(headers))
    ]

    def emit(row: Sequence[str]) -> None:
        print("  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)))

    print("\n## KPQC final / production GT / lazy ASM rowpack")
    emit(headers)
    emit(tuple("-" * w for w in widths))
    for row in rendered:
        emit(row)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kpqc-product", required=True)
    parser.add_argument("--gt-product", required=True)
    parser.add_argument("--rowpack-product", required=True)
    parser.add_argument("--kpqc-add", required=True)
    parser.add_argument("--gt-add", required=True)
    parser.add_argument("--rowpack-add", required=True)
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    kpqc_product = run_bench("kpqc_product", [args.kpqc_product], args.verbose)
    gt_product = run_bench("production_gt_product", [args.gt_product], args.verbose)
    rowpack_product = run_bench(
        "lazy_asm_rowpack_product", [args.rowpack_product], args.verbose
    )
    kpqc_add = run_bench("kpqc_product_add", [args.kpqc_add], args.verbose)
    gt_add = run_bench("production_gt_product_add", [args.gt_add], args.verbose)
    rowpack_add = run_bench(
        "lazy_asm_rowpack_product_add", [args.rowpack_add], args.verbose
    )

    rows = [
        (
            "ntt",
            value(kpqc_product, "poly_ntt"),
            value(gt_product, "poly_ntt"),
            value(rowpack_product, "rowpack_poly_ntt"),
        ),
        (
            "basemul",
            value(kpqc_product, "poly_basemul"),
            value(gt_product, "poly_basemul"),
            value(rowpack_product, "rowpack_poly_basemul"),
        ),
        (
            "basemul_add",
            value(kpqc_add, "poly_basemul_add"),
            value(gt_add, "poly_basemul_add"),
            value(rowpack_add, "rowpack_poly_basemul_add"),
        ),
        (
            "product pipeline",
            value(kpqc_product, "ntt_mul_pipeline"),
            value(gt_product, "ntt_mul_pipeline"),
            value(rowpack_product, "rowpack_ntt_mul_pipeline"),
        ),
        (
            "product-add pipeline",
            value(kpqc_add, "ntt_basemul_add_pipeline"),
            value(gt_add, "ntt_basemul_add_pipeline"),
            value(rowpack_add, "rowpack_ntt_basemul_add_pipeline"),
        ),
        ("kem_dec", None, None, None),
    ]
    print_table(rows)
    print("\nkem_dec: rowpack KEM is not wired for this gate; row shown as n/a.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
