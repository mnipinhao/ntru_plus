#!/usr/bin/env python3
"""Merge independently persisted Round 3 direct-cost candidates."""

import json
from pathlib import Path


def main() -> None:
    costs = {}
    checksum = 0
    metadata = None
    for path in sorted(Path("results").glob("round3-direct-*.json")):
        document = json.loads(path.read_text())
        if metadata is None:
            metadata = document
        costs.update(document["costs"])
        checksum ^= int(document["checksum"], 16)
    if len(costs) != 20 or metadata is None:
        raise SystemExit(f"expected 20 candidates, found {len(costs)}")
    output = {
        "schema_version": 1,
        "candidate": "all",
        "backend_mode": "paired",
        "cpu": metadata["cpu"],
        "iterations_per_sample": metadata["iterations_per_sample"],
        "warmups": metadata["warmups"],
        "samples": metadata["samples"],
        "costs": costs,
        "checksum": f"{checksum:016x}",
        "source_artifacts": "results/round3-direct-*.json",
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
