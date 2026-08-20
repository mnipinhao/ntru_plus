#!/usr/bin/env python3
"""Validate a GT9x16 model and emit stable experiment metadata."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from model import MODELS, SHEAR_STAGES, gt_input_index, gt_output_index


def rendered(parameter: int) -> str:
    model = MODELS[parameter]
    model.validate()
    document = model.as_dict()
    document["coordinate_mapping"] = "coefficient,radix9_digit,lane_block,lane"
    document["gt_input_index"] = [[gt_input_index(u, v) for v in range(16)] for u in range(9)]
    document["gt_output_index"] = [[gt_output_index(p, q) for q in range(16)] for p in range(9)]
    document["row_relabel"] = [(5 * row) % 9 for row in range(9)]
    document["shear_lane_shifts"] = [lane % 9 for lane in range(16)]
    document["shear_stages"] = [
        {"shift": shift, "mask": f"0x{mask:02X}", "cycle": list(cycle)}
        for shift, mask, cycle in SHEAR_STAGES
    ]
    document["post_shear_invariant"] = "Z[a]=Y[a].low||Y[(a+1)%9].high"
    document["status"] = "verified-structural-mapping-no-arithmetic-constants"
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
