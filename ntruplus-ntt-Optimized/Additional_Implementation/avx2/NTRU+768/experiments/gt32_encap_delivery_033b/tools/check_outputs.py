#!/usr/bin/env python3
"""Check deterministic Encap output equality for every ELF pair."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


ORDERS = ["current", "transform", "q24", "arithmetic"]


def sink(binary: Path) -> str:
    output = subprocess.check_output([str(binary.resolve())], text=True)
    for line in output.splitlines():
        if line.startswith("sink "):
            return line.split()[1]
    raise RuntimeError(f"no sink from {binary}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    results = {}
    for order in ORDERS:
        control = sink(args.build / f"bench_{order}_control")
        candidate = sink(args.build / f"bench_{order}_candidate")
        if control != candidate:
            raise SystemExit(f"{order}: output mismatch")
        results[order] = {"sink": control, "byte_exact": True}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    print("033B deterministic output equality: PASS")


if __name__ == "__main__":
    main()

