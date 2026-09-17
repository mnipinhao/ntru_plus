#!/usr/bin/env python3
"""Lower the selected D1 sign-orientation witnesses to GAS controls/tables."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def signed16(value: int) -> int:
    value &= 0xFFFF
    return value if value < 0x8000 else value - 0x10000


def parse_words(text: str, label: str) -> list[int]:
    match = re.search(
        rf"^{re.escape(label)}:\n\s*\.word\s+([^\n]+)$", text, re.MULTILINE
    )
    if not match:
        raise SystemExit(f"missing constant label: {label}")
    values = [int(value.strip()) for value in match.group(1).split(",")]
    if len(values) != 16:
        raise SystemExit(f"expected 16 words at {label}")
    return values


def qimm(permutation: list[int]) -> int:
    return sum(value << (2 * index) for index, value in enumerate(permutation))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--v1", type=Path, required=True)
    parser.add_argument("--v2", type=Path, required=True)
    parser.add_argument("--t0-constants", type=Path, required=True)
    parser.add_argument("--controls", type=Path, required=True)
    parser.add_argument("--twiddles", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    v1 = json.loads(args.v1.read_text())
    v2 = json.loads(args.v2.read_text())
    v1_rows = {row["tile"]: row for row in v1["tiles"]}
    v2_rows = {row["tile"]: row for row in v2["tiles"]}

    masks = {}
    control_lines = ["/* Generated D1 sign-orientation v2 terminal controls. */"]
    for tile in range(18):
        branch, row = divmod(tile, 9)
        selected = v2_rows[tile]
        if selected["uses_d1_sign_orientation"]:
            codes = selected["witness"]["unpack_codes"]
            outputs = selected["witness"]["outputs"]
        else:
            codes = v1_rows[tile]["best"]["unpack_codes"]
            outputs = v1_rows[tile]["best"]["outputs"]
        for group, code in enumerate(codes):
            control_lines.append(f".equ .Lwire_abs_b{branch}p{row}_g{group}, {code}")
        for coefficient, output in enumerate(outputs):
            source = output.get("network_output")
            permutation = output.get("vpermq")
            shuffle = output.get("new_shuffle", output.get("shuffle", 0))
            control_lines += [
                f".equ .Lwire_abs_b{branch}p{row}_o{coefficient}_src, {source}",
                f".equ .Lwire_abs_b{branch}p{row}_o{coefficient}_qimm, 0x{qimm(permutation):02x}",
                f".equ .Lwire_abs_b{branch}p{row}_o{coefficient}_shuffle, {shuffle}",
            ]
            if shuffle:
                mask = tuple(output["vpshufb_mask"])
                label = masks.setdefault(mask, f".Ld1v2_wire_mask_{len(masks)}")
                control_lines.append(
                    f".set .Lwire_abs_b{branch}p{row}_o{coefficient}_mask, {label}"
                )
    control_lines += [".section .rodata", ".p2align 5"]
    for mask, label in masks.items():
        control_lines += [label + ":", "  .byte " + ",".join(map(str, mask)), ".p2align 5"]
    controls = "\n".join(control_lines) + "\n"

    table_text = args.t0_constants.read_text()
    twiddle_lines = [
        "/* Generated D1 twiddles with selected lane-wise plus/minus swaps. */",
        ".section .rodata",
        ".p2align 5",
    ]
    for selected in v2["tiles"]:
        branch, row = divmod(selected["tile"], 9)
        negated = {
            (item["d1_pair"], item["lane"])
            for item in selected.get("witness", {}).get("negated_d1_lanes", [])
        }
        for pair, side in enumerate(("lo", "hi")):
            for kind in ("zeta", "qinv"):
                old_label = f".Lprod3_t0b_b{branch}_p{row}_distance1_{side}_{kind}"
                new_label = f".Lprod3_d1v2_b{branch}_p{row}_distance1_{side}_{kind}"
                if not negated:
                    twiddle_lines.append(f".set {new_label}, {old_label}")
                    continue
                values = parse_words(table_text, old_label)
                values = [
                    signed16(-value) if (pair, lane) in negated else value
                    for lane, value in enumerate(values)
                ]
                twiddle_lines += [
                    new_label + ":",
                    "  .word " + ", ".join(map(str, values)),
                    ".p2align 5",
                ]
    twiddles = "\n".join(twiddle_lines) + "\n"

    for path, text in ((args.controls, controls), (args.twiddles, twiddles)):
        if args.check:
            if not path.is_file() or path.read_text() != text:
                raise SystemExit(f"stale generated file: {path}")
        else:
            path.write_text(text)
    print(json.dumps({
        "controls_masks": len(masks),
        "oriented_tiles": v2["summary"]["new_zero_shuffle_tiles"],
        "saved_shuffles": v2["summary"]["saved_shuffles_per_forward"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
