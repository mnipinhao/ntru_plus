#!/usr/bin/env python3
"""Retarget the proven H3 formation and lambda tables to wire-monotone lanes."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def write(path: Path, value: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text() != value:
            raise SystemExit(f"stale wire H3 artifact: {path}")
    else:
        path.write_text(value)


def transform_group(group: dict, pi: list[int]) -> dict:
    old_mask = group["vpshufb_mask"]
    old_imm = int(group["vperm2i128_immediate"], 16)
    origins = []
    for old_lane in range(16):
        output_half = old_lane // 8
        selector = (old_imm >> (4 * output_half)) & 3
        source_half = selector & 1
        pair = old_mask[2 * old_lane:2 * old_lane + 2]
        origins.append(None if pair[0] == 128 else (source_half, pair))
    selected = [origins[old_lane] for old_lane in pi]
    halves = []
    mask = []
    for output_half in range(2):
        active = {origin[0] for origin in selected[8 * output_half:8 * output_half + 8]
                  if origin is not None}
        if len(active) > 1:
            raise SystemExit("wire H3 group needs two source halves in one output half")
        halves.append(next(iter(active), 0))
        for origin in selected[8 * output_half:8 * output_half + 8]:
            mask.extend((128, 128) if origin is None else origin[1])
    result = dict(group)
    result["vperm2i128_immediate"] = f"0x{((2 + halves[1]) << 4) | halves[0]:02x}"
    result["vpshufb_mask"] = mask
    return result


def lambda_constants(source: str, tiles: list[dict], plans: list[dict]) -> str:
    physical_by_name = {f"b{plan['branch']}p{plan['p']}": plan["tile"]
                        for plan in plans if plan["coefficient"] == 0}
    tile_by_name = {name: tiles[physical] for name, physical in physical_by_name.items()}
    pattern = re.compile(r"\.Lqnat_lambda_(b\d+p\d+)(_qinv)?:\n  \.short ([^\n]+)")
    entries = []
    for match in pattern.finditer(source):
        name, suffix, values_text = match.groups()
        values = [int(value.strip()) for value in values_text.split(",")]
        pi = tile_by_name[name]["natural_to_wire_pi"]
        if len(values) != 16:
            raise SystemExit("lambda vector does not have 16 lanes")
        entries += [".p2align 5", f".Lqwire_lambda_{name}{suffix or ''}:",
                    "  .short " + ", ".join(str(values[index]) for index in pi)]
    if len(entries) != 18 * 2 * 3:
        raise SystemExit("did not find all lambda/qinv vectors")
    return "/* Generated wire-monotone lambda constants. */\n" + "\n".join(entries) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gates", type=Path, required=True)
    parser.add_argument("--natural-schedule", type=Path, required=True)
    parser.add_argument("--natural-constants", type=Path, required=True)
    parser.add_argument("--schedule", type=Path, required=True)
    parser.add_argument("--constants", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    gates = json.loads(args.gates.read_text())
    natural = json.loads(args.natural_schedule.read_text())
    tiles = gates["tiles"]
    plans = natural["resident_h"]["natural_plans"]
    for plan in plans:
        tile = plan["tile"]
        pi = tiles[tile]["natural_to_wire_pi"]
        plan["groups"] = [transform_group(group, pi) for group in plan["groups"]]
    natural["checkpoint"] = "GT9X16-PROD3-MA2-WIRE-MONOTONE-H3-SCHEDULE"
    natural["resident_h"]["representation"] = "wire-monotone-ma2"
    natural["resident_h"]["wire_monotone_plans"] = plans
    natural["gate3_delta"] = gates["gate3_h3"]
    write(args.schedule, json.dumps(natural, indent=2) + "\n", args.check)
    write(args.constants, lambda_constants(args.natural_constants.read_text(), tiles, plans), args.check)
    print("wire H3: 72 vectors, unchanged 360-route realization")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
