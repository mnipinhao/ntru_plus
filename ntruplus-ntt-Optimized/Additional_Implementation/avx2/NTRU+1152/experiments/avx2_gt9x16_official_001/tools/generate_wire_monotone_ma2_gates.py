#!/usr/bin/env python3
"""Synthesize and price the shared wire-monotone MA2 physical ABI."""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path


Q0 = (0, 1, 4, 5, 2, 3, 6, 7, 8, 9, 12, 13, 10, 11, 14, 15)


def write(path: Path, value: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text() != value:
            raise SystemExit(f"stale wire-monotone artifact: {path}")
    else:
        path.write_text(value)


def wire_layout(source_to_wire: list[int]) -> tuple[list[int], list[dict]]:
    target = [0] * 1152
    tiles = []
    for vector_base in range(0, 72, 4):
        wires = [source_to_wire[16 * vector + lane]
                 for vector in range(vector_base, vector_base + 4)
                 for lane in range(16)]
        first = min(wires)
        if sorted(wires) != list(range(first, first + 64)):
            raise SystemExit(f"vector quartet {vector_base} is not a wire tile")
        for coefficient in range(4):
            for lane in range(16):
                target[16 * (vector_base + coefficient) + lane] = first + 4 * lane + coefficient
        pi = []
        for lane in range(16):
            wire = first + 4 * lane
            matches = [old_lane for old_lane in range(16)
                       if source_to_wire[16 * vector_base + old_lane] == wire]
            if len(matches) != 1:
                raise SystemExit("wire target is not a per-tile lane permutation")
            pi.append(matches[0])
        for coefficient in range(1, 4):
            if any(source_to_wire[16 * (vector_base + coefficient) + pi[lane]]
                   != first + 4 * lane + coefficient for lane in range(16)):
                raise SystemExit("four coefficient planes do not share one permutation")
        tiles.append({"tile": vector_base // 4, "vector_base": vector_base,
                      "first_wire": first, "natural_to_wire_pi": pi})
    if sorted(target) != list(range(1152)):
        raise SystemExit("wire-monotone layout is not bijective")
    return target, tiles


def route(pi: list[int]) -> tuple[int, list[int], list[int]]:
    """Lower natural lanes -> target lanes to vpermq + one vpshufb."""
    desired_pre = [Q0[pi[lane]] for lane in range(16)]
    for qperm in itertools.permutations(range(4)):
        middle = [4 * qperm[word] + byte for word in range(4) for byte in range(4)]
        mask = []
        valid = True
        for output, source in enumerate(desired_pre):
            half_start = 0 if output < 8 else 8
            try:
                position = middle.index(source, half_start, half_start + 8)
            except ValueError:
                valid = False
                break
            mask.extend((2 * (position - half_start), 2 * (position - half_start) + 1))
        if valid:
            immediate = sum(value << (2 * index) for index, value in enumerate(qperm))
            replay = []
            for output in range(16):
                half_start = 0 if output < 8 else 8
                replay.append(middle[half_start + mask[2 * output] // 2])
            if replay != desired_pre:
                raise SystemExit("routing replay failed")
            return immediate, mask, middle
    raise SystemExit("target permutation is not one vpermq plus one vpshufb")


def constants(tiles: list[dict]) -> str:
    masks: dict[tuple[int, ...], str] = {}
    lines = ["/* Generated wire-monotone terminal routing constants. */"]
    for tile in tiles:
        immediate, mask, _ = route(tile["natural_to_wire_pi"])
        tile["vpermq_immediate"] = f"0x{immediate:02x}"
        key = tuple(mask)
        label = masks.setdefault(key, f".Lwire_mask_{len(masks)}")
        tile["vpshufb_mask"] = label
        branch, row = divmod(tile["tile"], 9)
        lines.append(f".equ .Lwire_qimm_b{branch}p{row}, 0x{immediate:02x}")
        lines.append(f".set .Lwire_mask_b{branch}p{row}, {label}")
    lines += ["", ".section .rodata", ".p2align 5"]
    for mask, label in masks.items():
        lines += [f"{label}:", "  .byte " + ",".join(map(str, mask)), ".p2align 5"]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--machine-wire", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--wire-layout", type=Path, required=True)
    parser.add_argument("--constants", type=Path, required=True)
    parser.add_argument("--c-layout", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    machine = json.loads(args.machine_wire.read_text())
    source = machine["source_to_wire"]
    if len(source) != 1152 or sorted(source) != list(range(1152)):
        raise SystemExit("invalid machine wire map")
    target, tiles = wire_layout(source)
    constants_text = constants(tiles)
    unique_masks = len({tile["vpshufb_mask"] for tile in tiles})

    report = {
        "schema": "wire-monotone-ma2-gates/v1",
        "contract": {
            "vectors": "four coefficient planes per tile",
            "lane_k": "wire coefficients 4*k+j in coefficient plane j",
            "scale": 1,
            "ma2": "lane-wise unchanged; lambda tables offline-reindexed",
        },
        "tiles": tiles,
        "gate1_direct_h1": {
            "vpermd": {"natural_q": 72, "wire_monotone": 0, "delta": -72},
            "index_loads": {"natural_q": 30, "wire_monotone": 0, "delta": -30},
            "parity_and_pack_routes_delta": 0,
            "instruction_delta": -102,
        },
        "gate2_adapter_upper_bound": {
            "routes_per_forward": {"vpshufb_delta": 72, "vpermq_delta": 0},
            "instruction_delta_per_forward": 72,
            "peak_ymm": 16,
            "unique_masks": unique_masks,
            "mask_rodata_bytes": 32 * unique_masks,
            "status": "superseded",
            "superseded_by": "d1-wire-monotone-absorption.json",
            "note": "naive post-epilogue adapter upper bound; not the selected Gate 2 realization",
        },
        "gate3_h3": {
            "routes": {"natural_q": 360, "wire_monotone": 360, "delta": 0},
            "loads_delta": 0, "stores_delta": 0, "instruction_delta": 0,
            "peak_ymm": 16,
            "note": "same two source halves and five-route formation per output vector; masks change only",
        },
        "gate4_preliminary_upper_bound": {
            "two_forwards": 144,
            "h3": 0,
            "direct_h1": -102,
            "m3b": -102,
            "ma2_and_constants": 0,
            "instruction_delta": -60,
            "status": "superseded by wire-monotone-shared-ledger.json",
        },
    }
    layout = {"schema": "h1-machine-wire-layout/v1", "representation": "wire-monotone-ma2",
              "source_to_wire": target}
    write(args.report, json.dumps(report, indent=2) + "\n", args.check)
    write(args.wire_layout, json.dumps(layout, indent=2) + "\n", args.check)
    write(args.constants, constants_text, args.check)
    if args.c_layout:
        target_index = [0] * 1152
        for index, wire in enumerate(target):
            target_index[wire] = index
        current_to_target = [target_index[wire] for wire in source]
        c_layout = "\n".join(
            "  " + ", ".join(str(value) for value in current_to_target[index:index + 16]) + ","
            for index in range(0, 1152, 16)) + "\n"
        write(args.c_layout, c_layout, args.check)
    print(json.dumps(report["gate4_preliminary_upper_bound"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
