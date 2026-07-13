#!/usr/bin/env python3
"""Emit capped, conservative warnings for Cortex-M4 source patterns."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path


SOURCE_SUFFIXES = {".c", ".h", ".cc", ".cpp", ".s", ".S", ".inc"}
INPUT_ERROR = 2
STRICT_WARNINGS = 1

PATTERNS = [
    (
        "M4001",
        re.compile(r"\b(arm_neon\.h|int[0-9]+x[0-9]+_t|uint[0-9]+x[0-9]+_t|vaddq|vsubq|vmulq|vld1q|vst1q|__aarch64__)\b"),
        "AArch64 Neon-looking code in a Cortex-M4 target; do not import Neon lane-layout rules.",
    ),
    (
        "M4002",
        re.compile(r"\b(malloc|calloc|realloc|free|alloca)\s*\("),
        "dynamic allocation or alloca; embedded kernels should use explicit scratch or fixed storage.",
    ),
    (
        "M4003",
        re.compile(r"\b(uint64_t|int64_t|unsigned long long|long long)\b"),
        "64-bit arithmetic/storage; prove it is required and include it in the M4 cost model.",
    ),
    (
        "M4004",
        re.compile(r"[^/%]%[^=%]"),
        "modulo operator; check whether this compiles to expensive division and whether reduction should be explicit.",
    ),
    (
        "M4005",
        re.compile(r"\b(float|double)\b"),
        "floating-point type in integer polynomial arithmetic; confirm this is intentional and portable.",
    ),
    (
        "M4006",
        re.compile(r"\bmemcpy\s*\([^;]*(secret|sk|priv|key)", re.IGNORECASE),
        "secret-looking buffer copy; confirm length and addresses are public and cleanup policy is satisfied.",
    ),
]


def nonnegative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be non-negative")
    return parsed


def collect_files(items: list[str]) -> tuple[list[Path], bool]:
    files: list[Path] = []
    seen: set[Path] = set()
    had_error = False
    for item in items:
        path = Path(item)
        if not path.exists():
            print(f"check-m4-patterns: error: input does not exist: {path}", file=sys.stderr)
            had_error = True
            continue
        if path.is_dir():
            try:
                candidates = [child for child in sorted(path.rglob("*")) if child.is_file() and child.suffix in SOURCE_SUFFIXES]
            except OSError as exc:
                print(f"check-m4-patterns: error: cannot walk {path}: {exc}", file=sys.stderr)
                had_error = True
                continue
            if not candidates:
                print(f"check-m4-patterns: error: no supported source files under: {path}", file=sys.stderr)
                had_error = True
            for candidate in candidates:
                key = candidate.resolve()
                if key not in seen:
                    seen.add(key)
                    files.append(candidate)
            continue
        if not path.is_file():
            print(f"check-m4-patterns: error: input is not a regular file or directory: {path}", file=sys.stderr)
            had_error = True
            continue
        if path.suffix not in SOURCE_SUFFIXES:
            print(f"check-m4-patterns: error: unsupported source file: {path}", file=sys.stderr)
            had_error = True
            continue
        key = path.resolve()
        if key not in seen:
            seen.add(key)
            files.append(path)
    if not files:
        print("check-m4-patterns: error: zero supported files selected", file=sys.stderr)
        had_error = True
    return files, had_error


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit conservative warnings for Cortex-M4 source patterns.")
    parser.add_argument("--strict", action="store_true", help="Exit 1 when warnings are found.")
    parser.add_argument("--verbose", action="store_true", help="Print every finding instead of the capped default.")
    parser.add_argument("--max-per-code", type=nonnegative_int, default=5, help="Maximum findings printed per warning code. Default: 5.")
    parser.add_argument("paths", nargs="+", help="Source files or directories to scan.")
    args = parser.parse_args()

    files, had_error = collect_files(args.paths)
    counts: Counter[str] = Counter()
    shown: Counter[str] = Counter()
    scanned = 0
    for path in files:
        try:
            lines = path.read_text(errors="replace").splitlines()
        except OSError as exc:
            print(f"check-m4-patterns: error: could not read {path}: {exc}", file=sys.stderr)
            had_error = True
            continue
        scanned += 1
        for lineno, line in enumerate(lines, 1):
            for code, pattern, message in PATTERNS:
                if not pattern.search(line):
                    continue
                counts[code] += 1
                if args.verbose or shown[code] < args.max_per_code:
                    print(f"{path}:{lineno}: warning[{code}]: {message}")
                    shown[code] += 1

    total = sum(counts.values())
    print(f"check-m4-patterns: files scanned: {scanned}; warnings: {total}")
    for code in sorted(counts):
        suppressed = counts[code] - shown[code]
        suffix = f"; {suppressed} suppressed" if suppressed else ""
        print(f"check-m4-patterns: {code}: {counts[code]} warning(s); {shown[code]} shown{suffix}")
    if had_error or scanned == 0:
        return INPUT_ERROR
    if args.strict and total:
        return STRICT_WARNINGS
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
