#!/usr/bin/env python3
"""Reject production link closures that reach into experiment directories."""

from __future__ import annotations

import argparse
import re
import shlex
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_SUFFIXES = {".c", ".h", ".s", ".S", ".inc"}
INCLUDE_RE = re.compile(r'(?:#include|\.include)\s+"([^"]+)"')


def is_experiment_path(path: Path) -> bool:
    return any(part in {"experiment", "experiments"} for part in path.parts)


def resolve_include(source: Path, include: str) -> Path:
    root_relative = ROOT / include
    if root_relative.exists():
        return root_relative.resolve()
    return (source.parent / include).resolve()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--keygen-layout", choices=("mixed", "cq"),
                        default="mixed")
    args = parser.parse_args()
    result = subprocess.run(
        ["make", "-n", f"GT_PRODUCTION_KEYGEN_LAYOUT={args.keygen_layout}",
         "test_kem_gt_production_default"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    compile_lines = [line for line in result.stdout.splitlines() if " -o " in line]
    if not compile_lines:
        print("production_layout_error=no compile command found", file=sys.stderr)
        return 1

    tokens = shlex.split(compile_lines[-1])
    pending = []
    for token in tokens:
        candidate = (ROOT / token).resolve()
        if candidate.exists() and candidate.suffix in SOURCE_SUFFIXES:
            pending.append(candidate)

    visited: set[Path] = set()
    violations: list[Path] = []
    while pending:
        source = pending.pop()
        if source in visited:
            continue
        visited.add(source)
        try:
            relative = source.relative_to(ROOT)
        except ValueError:
            continue
        if is_experiment_path(relative):
            violations.append(relative)
        text = source.read_text(errors="ignore")
        for include in INCLUDE_RE.findall(text):
            dependency = resolve_include(source, include)
            if dependency.exists():
                pending.append(dependency)

    print(f"production_layout_keygen={args.keygen_layout}")
    print(f"production_layout_files={len(visited)}")
    if violations:
        for violation in sorted(set(violations)):
            print(f"production_layout_violation={violation}", file=sys.stderr)
        return 1

    print("production_layout_experiment_dependencies=0")
    print("production_layout_pass=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
