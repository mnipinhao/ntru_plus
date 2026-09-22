#!/usr/bin/env python3
"""Extract an exact Slothy/source region by labels."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def extract(lines: list[str], start: str, end: str, include_labels: bool) -> list[str]:
    out: list[str] = []
    in_region = False
    saw_start = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(start + ":"):
            in_region = True
            saw_start = True
            if include_labels:
                out.append(line)
            continue
        if stripped.startswith(end + ":") and in_region:
            if include_labels:
                out.append(line)
            return out
        if in_region:
            out.append(line)
    if not saw_start:
        raise ValueError(f"start label not found: {start}")
    raise ValueError(f"end label not found after {start}: {end}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="Assembly source file.")
    parser.add_argument("--start", required=True, help="Start label without colon.")
    parser.add_argument("--end", required=True, help="End label without colon.")
    parser.add_argument("--output", help="Write extracted region to this file.")
    parser.add_argument("--no-labels", action="store_true", help="Omit start/end labels.")
    args = parser.parse_args()

    path = Path(args.source)
    try:
        region = extract(path.read_text(errors="replace").splitlines(), args.start, args.end, not args.no_labels)
    except (OSError, ValueError) as exc:
        print(f"extract-slothy-region: error: {exc}", file=sys.stderr)
        return 1

    text = "\n".join(region) + "\n"
    if args.output:
        Path(args.output).write_text(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
