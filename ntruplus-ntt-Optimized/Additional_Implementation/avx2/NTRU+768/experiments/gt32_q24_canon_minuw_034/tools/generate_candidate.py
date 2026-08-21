#!/usr/bin/env python3
"""Derive the 034 vpminuw candidate from the production pack source."""

from __future__ import annotations

import argparse
from pathlib import Path


OLD = """ vpsraw $15, \\src, %ymm14
 vpand %ymm15, %ymm14, %ymm14
 vpaddw %ymm14, \\src, \\src
"""

NEW = """ vpaddw %ymm15, \\src, %ymm14
 vpminuw %ymm14, \\src, \\src
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    source = args.input.read_text()
    begin = source.index(".macro Q24_ENCODE_CANONICAL_REG_PACKET")
    end = source.index(".endm", begin)
    macro = source[begin:end]
    if macro.count(OLD) != 1:
        raise SystemExit("production canonical macro no longer matches 034 gate")
    candidate = source[:begin] + macro.replace(OLD, NEW, 1) + source[end:]
    if candidate.count("vpminuw %ymm14, \\src, \\src") != 1:
        raise SystemExit("candidate replacement count is not one")
    if args.check:
        if not args.output.exists() or args.output.read_text() != candidate:
            raise SystemExit("generated candidate is stale")
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(candidate)


if __name__ == "__main__":
    main()
