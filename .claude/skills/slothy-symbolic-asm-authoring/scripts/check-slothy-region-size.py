#!/usr/bin/env python3
"""Warn about Slothy region sizes.

This checker emits warnings only. It does not rewrite code and exits with
status 0 even when warnings are emitted.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


SOURCE_SUFFIXES = {".s", ".S", ".asm", ".inc"}
LABEL_RE = re.compile(r"^\s*([A-Za-z_.$][A-Za-z0-9_.$]*):")
INSTR_RE = re.compile(r"^\s*[A-Za-z][A-Za-z0-9_.]*\b")


def iter_files(paths: list[str]):
    for item in paths:
        path = Path(item)
        if path.is_dir():
            for child in sorted(path.rglob("*")):
                if child.is_file() and child.suffix in SOURCE_SUFFIXES:
                    yield child
        elif path.is_file():
            yield path


def strip_comment(line: str) -> str:
    return line.split("//", 1)[0].split("@", 1)[0]


def is_instruction(line: str) -> bool:
    stripped = strip_comment(line).strip()
    if not stripped or stripped.startswith(".") or stripped.endswith(":"):
        return False
    return bool(INSTR_RE.match(stripped))


def main() -> int:
    parser = argparse.ArgumentParser(description="Emit warnings for Slothy optimization region sizes.")
    parser.add_argument("--ideal", type=int, default=50, help="Ideal maximum instruction count. Default: 50.")
    parser.add_argument("--max", type=int, default=150, help="Warning threshold for large regions. Default: 150.")
    parser.add_argument("paths", nargs="+", help="Assembly files or directories to scan.")
    args = parser.parse_args()

    total = 0
    for path in iter_files(args.paths):
        try:
            lines = path.read_text(errors="replace").splitlines()
        except OSError as exc:
            print(f"{path}: warning[REGION000]: could not read file: {exc}")
            total += 1
            continue

        current = None
        count = 0
        found = False
        for lineno, line in enumerate(lines, 1):
            label = LABEL_RE.match(line)
            if label and "slothy_start" in label.group(1):
                current = (label.group(1), lineno)
                count = 0
                found = True
                continue
            if label and "slothy_end" in label.group(1) and current is not None:
                name, start_line = current
                if count < args.ideal:
                    print(f"{path}:{start_line}: info[REGION001]: region '{name}' has {count} instruction(s), ideal for one-pass exploration.")
                elif count <= args.max:
                    print(f"{path}:{start_line}: warning[REGION002]: region '{name}' has {count} instruction(s), consider RA-first then window optimization.")
                    total += 1
                else:
                    print(f"{path}:{start_line}: warning[REGION003]: region '{name}' has {count} instruction(s), split or use macro RA/unfold/window-opt.")
                    total += 1
                current = None
                continue
            if current is not None and is_instruction(line):
                count += 1

        if current is not None:
            name, start_line = current
            print(f"{path}:{start_line}: warning[REGION004]: region '{name}' has no matching slothy_end label.")
            total += 1
        if not found:
            print(f"{path}: warning[REGION005]: no slothy_start label found.")
            total += 1

    if total == 0:
        print("check-slothy-region-size: no warnings emitted")
    else:
        print(f"check-slothy-region-size: emitted {total} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
