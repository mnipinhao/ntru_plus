#!/usr/bin/env python3
"""Emit capped, conservative warnings for AArch64 Neon source patterns."""

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
        "NEON001",
        re.compile(r"\b(arm_sve\.h|svbool_t|svint|svuint|sv[a-zA-Z0-9_]*|SVE2?|SME|__ARM_FEATURE_SVE)\b"),
        "SVE/SVE2/SME token in a Neon-only target; keep scalable/tile extensions out unless explicitly requested.",
    ),
    (
        "NEON002",
        re.compile(r"\b(vtbl|vtbx|vqtbl|vqtbx|tbl|tbx)[a-zA-Z0-9_]*\b"),
        "table/permutation instruction; confirm indices are public and coefficient index mapping is documented.",
    ),
    (
        "NEON003",
        re.compile(r"\b(vzip|vuzp|vtrn|vrev|vext|zip1|zip2|uzp1|uzp2|trn1|trn2|ext)[a-zA-Z0-9_]*\b"),
        "cross-lane or transpose operation; include shuffle cost and tagged-index validation.",
    ),
    (
        "NEON004",
        re.compile(r"\b(vget_lane|vgetq_lane|vset_lane|vsetq_lane|dup\s+v|ins\s+v)[a-zA-Z0-9_.,\s]*"),
        "lane extract/insert/broadcast; check it is not secret-dependent or in a costly inner loop.",
    ),
    (
        "NEON005",
        re.compile(r"\b(vmovn|vqmovn|vshrn|vqshrn|sqxtn|uqxtn|xtn|shrn)[a-zA-Z0-9_]*\b"),
        "narrowing operation; attach a range proof for every narrowed lane.",
    ),
    (
        "NEON006",
        re.compile(r"\b(vqrdmulh|vqdmulh|sqrdmulh|sqdmulh|sqr?dmulh)[a-zA-Z0-9_]*\b"),
        "rounding/high multiply pattern; prove signedness, rounding, and modulus-specific reduction bounds.",
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
            print(f"check-neon-patterns: error: input does not exist: {path}", file=sys.stderr)
            had_error = True
            continue
        if path.is_dir():
            try:
                candidates = [child for child in sorted(path.rglob("*")) if child.is_file() and child.suffix in SOURCE_SUFFIXES]
            except OSError as exc:
                print(f"check-neon-patterns: error: cannot walk {path}: {exc}", file=sys.stderr)
                had_error = True
                continue
            if not candidates:
                print(f"check-neon-patterns: error: no supported source files under: {path}", file=sys.stderr)
                had_error = True
            for candidate in candidates:
                key = candidate.resolve()
                if key not in seen:
                    seen.add(key)
                    files.append(candidate)
            continue
        if not path.is_file():
            print(f"check-neon-patterns: error: input is not a regular file or directory: {path}", file=sys.stderr)
            had_error = True
            continue
        if path.suffix not in SOURCE_SUFFIXES:
            print(f"check-neon-patterns: error: unsupported source file: {path}", file=sys.stderr)
            had_error = True
            continue
        key = path.resolve()
        if key not in seen:
            seen.add(key)
            files.append(path)
    if not files:
        print("check-neon-patterns: error: zero supported files selected", file=sys.stderr)
        had_error = True
    return files, had_error


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit conservative warnings for AArch64 Neon source patterns.")
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
            print(f"check-neon-patterns: error: could not read {path}: {exc}", file=sys.stderr)
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
    print(f"check-neon-patterns: files scanned: {scanned}; warnings: {total}")
    for code in sorted(counts):
        suppressed = counts[code] - shown[code]
        suffix = f"; {suppressed} suppressed" if suppressed else ""
        print(f"check-neon-patterns: {code}: {counts[code]} warning(s); {shown[code]} shown{suffix}")
    if had_error or scanned == 0:
        return INPUT_ERROR
    if args.strict and total:
        return STRICT_WARNINGS
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
