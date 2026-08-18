#!/usr/bin/env python3
"""Remove non-production function emissions from preprocessed GT assembly."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


GLOBL = re.compile(r"^\s*\.globl\s+([A-Za-z_][A-Za-z0-9_]*)\s*$")
SIZE = re.compile(r"^\s*\.size\s+([A-Za-z_][A-Za-z0-9_]*),")
MACRO_EMIT = re.compile(
    r"^\s*(?:TILE4_[A-Z0-9_]*FUNCTION|FR_[A-Z0-9_]*FUNCTION)\s+"
    r"(gt[A-Za-z0-9_]*)"
)


def prune(path: Path, allowed: set[str]) -> None:
    lines = path.read_text().splitlines(keepends=True)
    output: list[str] = []
    index = 0
    while index < len(lines):
        macro = MACRO_EMIT.match(lines[index])
        if macro and macro.group(1) not in allowed:
            index += 1
            continue
        globl = GLOBL.match(lines[index])
        if globl and globl.group(1) not in allowed:
            symbol = globl.group(1)
            index += 1
            while index < len(lines):
                sized = SIZE.match(lines[index])
                index += 1
                if sized and sized.group(1) == symbol:
                    break
            else:
                raise ValueError(f"missing .size for {symbol} in {path}")
            continue
        output.append(lines[index])
        index += 1
    path.write_text("".join(output))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument("symbols", nargs="+")
    args = parser.parse_args()
    prune(args.path, set(args.symbols))


if __name__ == "__main__":
    main()
