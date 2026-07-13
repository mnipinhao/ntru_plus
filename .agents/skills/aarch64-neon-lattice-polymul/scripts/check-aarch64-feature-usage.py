#!/usr/bin/env python3
"""Warn about optional or out-of-scope AArch64 feature usage."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


SOURCE_SUFFIXES = {".c", ".h", ".cc", ".cpp", ".s", ".S", ".inc"}
INPUT_ERROR = 2
STRICT_WARNINGS = 1

FEATURE_PATTERNS = [
    (
        "FEAT001",
        "SVE/SVE2",
        re.compile(r"\b(arm_sve\.h|svbool_t|svint|svuint|sv[a-zA-Z0-9_]*|__ARM_FEATURE_SVE|SVE2?)\b"),
        "out of scope for Neon-only guidance unless explicitly requested.",
    ),
    (
        "FEAT002",
        "SME",
        re.compile(r"\b(SME|__ARM_FEATURE_SME|__arm_streaming|__arm_inout|za[0-9]?\b|smstart|smstop)\b"),
        "out of scope for Neon-only guidance unless explicitly requested.",
    ),
    (
        "FEAT003",
        "Crypto/PMULL",
        re.compile(r"\b(pmull|pmull2|poly64|poly128|vmull_p|aes[deimc]*|sha1|sha256|__ARM_FEATURE_CRYPTO)\b", re.IGNORECASE),
        "optional feature; gate it and prove the instruction semantics match the coefficient domain.",
    ),
    (
        "FEAT004",
        "Dot product",
        re.compile(r"\b(sdot|udot|usdot|__ARM_FEATURE_DOTPROD)\b"),
        "optional feature; provide a baseline Neon path or explicit build requirement.",
    ),
    (
        "FEAT005",
        "Matrix/BF16/FP16",
        re.compile(r"\b(ummla|smmla|usmmla|bfdot|bfmmla|fmlal|__ARM_FEATURE_MATMUL_INT8|__ARM_FEATURE_BF16|__ARM_FEATURE_FP16)\b"),
        "optional/non-core feature; avoid unless explicitly required and validated.",
    ),
    (
        "FEAT006",
        "CRC",
        re.compile(r"\b(crc32|__ARM_FEATURE_CRC32)\b", re.IGNORECASE),
        "optional feature; should not be needed for polynomial multiplication kernels.",
    ),
]


def collect_files(items: list[str]) -> tuple[list[Path], bool]:
    files: list[Path] = []
    seen: set[Path] = set()
    had_error = False

    for item in items:
        path = Path(item)
        if not path.exists():
            print(f"check-aarch64-feature-usage: error: input does not exist: {path}", file=sys.stderr)
            had_error = True
            continue
        if path.is_dir():
            try:
                candidates = [
                    child
                    for child in sorted(path.rglob("*"))
                    if child.is_file() and child.suffix in SOURCE_SUFFIXES
                ]
            except OSError as exc:
                print(f"check-aarch64-feature-usage: error: cannot walk {path}: {exc}", file=sys.stderr)
                had_error = True
                continue
            if not candidates:
                print(f"check-aarch64-feature-usage: error: no supported source files under: {path}", file=sys.stderr)
                had_error = True
            for candidate in candidates:
                key = candidate.resolve()
                if key not in seen:
                    seen.add(key)
                    files.append(candidate)
            continue
        if not path.is_file():
            print(f"check-aarch64-feature-usage: error: input is not a regular file or directory: {path}", file=sys.stderr)
            had_error = True
            continue
        if path.suffix not in SOURCE_SUFFIXES:
            print(f"check-aarch64-feature-usage: error: unsupported source file: {path}", file=sys.stderr)
            had_error = True
            continue
        key = path.resolve()
        if key not in seen:
            seen.add(key)
            files.append(path)

    if not files:
        print("check-aarch64-feature-usage: error: zero supported files selected", file=sys.stderr)
        had_error = True
    return files, had_error


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit warnings for AArch64 optional feature usage.")
    parser.add_argument("--strict", action="store_true", help="Exit 1 when warnings are found.")
    parser.add_argument("paths", nargs="+", help="Source files or directories to scan.")
    args = parser.parse_args()

    files, had_error = collect_files(args.paths)
    warnings = 0
    scanned = 0
    for path in files:
        try:
            lines = path.read_text(errors="replace").splitlines()
        except OSError as exc:
            print(f"check-aarch64-feature-usage: error: could not read {path}: {exc}", file=sys.stderr)
            had_error = True
            continue
        scanned += 1
        for lineno, line in enumerate(lines, 1):
            for code, feature, pattern, message in FEATURE_PATTERNS:
                if pattern.search(line):
                    print(f"{path}:{lineno}: warning[{code}]: {feature}: {message}")
                    warnings += 1

    print(f"check-aarch64-feature-usage: files scanned: {scanned}; warnings: {warnings}")
    if had_error or scanned == 0:
        return INPUT_ERROR
    if args.strict and warnings:
        return STRICT_WARNINGS
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
