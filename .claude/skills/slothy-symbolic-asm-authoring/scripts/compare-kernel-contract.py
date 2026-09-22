#!/usr/bin/env python3
"""Compare baseline and candidate contracts for preserved integration behavior."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from contractlib import load_flat_yaml


PRESERVED_PREFIXES = (
    "region.live_in",
    "region.live_out",
    "abi.inputs",
    "abi.outputs",
    "abi.clobbers",
    "abi.concrete_gprs_allowed",
    "abi.fixed_vector_registers",
    "memory_contract.",
    "constant_contract.",
    "range_contract.",
    "constant_time_contract.",
)


def comparable_items(data: dict[str, object]) -> dict[str, object]:
    return {
        key: value
        for key, value in data.items()
        if any(key == prefix.rstrip(".") or key.startswith(prefix) for prefix in PRESERVED_PREFIXES)
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline_contract")
    parser.add_argument("candidate_contract")
    parser.add_argument("--allow-contract-change", action="store_true", help="Report differences but do not fail.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    baseline_path = Path(args.baseline_contract)
    candidate_path = Path(args.candidate_contract)
    if not baseline_path.is_file() or not candidate_path.is_file():
        print("compare-kernel-contract: error: both contract files are required", file=sys.stderr)
        return 1

    baseline = comparable_items(load_flat_yaml(baseline_path))
    candidate = comparable_items(load_flat_yaml(candidate_path))
    keys = sorted(set(baseline) | set(candidate))
    diffs = [
        {"field": key, "baseline": baseline.get(key), "candidate": candidate.get(key)}
        for key in keys
        if baseline.get(key) != candidate.get(key)
    ]

    result = {
        "baseline_contract": str(baseline_path),
        "candidate_contract": str(candidate_path),
        "preserved": not diffs,
        "approved_changes": args.allow_contract_change,
        "differences": diffs,
    }

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif diffs:
        for diff in diffs:
            print(f"{diff['field']}: baseline={diff['baseline']!r} candidate={diff['candidate']!r}")
    else:
        print("compare-kernel-contract: preserved contract fields match")

    if diffs and not args.allow_contract_change:
        print("compare-kernel-contract: failed; contract changes require explicit approval", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
