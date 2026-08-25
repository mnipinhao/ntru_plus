#!/usr/bin/env python3
"""Reject accidental Experiment dependencies from an AArch64 production tree."""

from __future__ import annotations

import argparse
import os
from pathlib import Path


PRODUCTION_SETS = {"NTRU+864", "NTRU+1152"}
SOURCE_SUFFIXES = {".c", ".h", ".s", ".S", ".inc", ".mk"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--production", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    production = Path(os.path.abspath(os.fspath(parse_args().production)))
    if production.name not in PRODUCTION_SETS:
        raise SystemExit(
            f"production path must end in NTRU+864 or NTRU+1152: {production}"
        )

    problems: list[str] = []
    for path in sorted(production.rglob("*")):
        relative = path.relative_to(production)
        if "build" in relative.parts:
            continue
        if path.is_symlink():
            target = path.resolve(strict=False)
            if "Experiment" in target.parts:
                problems.append(f"symlink reaches Experiment: {relative} -> {target}")
            continue
        if not path.is_file() or path.suffix not in SOURCE_SUFFIXES:
            continue
        try:
            text = path.read_text(errors="strict")
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(text.splitlines(), 1):
            normalized = line.replace("\\", "/")
            if "/Experiment/" in normalized or normalized.startswith("Experiment/"):
                problems.append(
                    f"source references Experiment: {relative}:{line_number}"
                )

    if problems:
        print("production/experiment boundary check: FAIL")
        for problem in problems:
            print(f"  {problem}")
        return 1

    print(f"production/experiment boundary check: PASS ({production.name})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
