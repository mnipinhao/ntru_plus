#!/usr/bin/env python3
"""Check that an experiment still points at the exact pinned upstream tree."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from supercop_workflow import read_lock, sha256_tree


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", type=Path, required=True)
    parser.add_argument("--parameter", choices=("864", "1152"), required=True)
    args = parser.parse_args()
    lock = read_lock()
    upstream = args.experiment / "upstream"
    record = json.loads((upstream / "UPSTREAM.json").read_text(encoding="utf-8"))
    expected = lock[f"ntruplus{args.parameter}_avx2_tree_sha256"]
    actual = sha256_tree(upstream / "supercop-avx2")
    if actual != expected or record.get("source_tree_sha256") != expected:
        raise SystemExit(f"upstream mismatch: {actual} != {expected}")
    print(f"verified NTRU+{args.parameter} experiment upstream {actual}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
