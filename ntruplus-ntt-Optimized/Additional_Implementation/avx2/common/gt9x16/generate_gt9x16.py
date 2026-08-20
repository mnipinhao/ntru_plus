#!/usr/bin/env python3
"""Validate a GT9x16 model and emit stable experiment metadata."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from model import MODELS


def rendered(parameter: int) -> str:
    model = MODELS[parameter]
    model.validate()
    document = model.as_dict()
    document["mapping"] = "coefficient,radix9_digit,lane_block,lane"
    document["status"] = "structural-only-no-arithmetic-constants"
    return json.dumps(document, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parameter", type=int, choices=sorted(MODELS), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = rendered(args.parameter)
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != expected:
            raise SystemExit(f"generated file is stale: {args.output}")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(expected, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
