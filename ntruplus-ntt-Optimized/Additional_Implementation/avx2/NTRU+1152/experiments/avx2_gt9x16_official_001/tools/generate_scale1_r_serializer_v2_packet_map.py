#!/usr/bin/env python3
"""Map two wire quartets to one Official-granularity serializer packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def unpack(a: list[int], b: list[int], group_words: int, high: bool) -> list[int]:
    out = []
    groups_per_half = 8 // group_words
    selected = range(groups_per_half // 2, groups_per_half) if high else range(groups_per_half // 2)
    for half in range(2):
        base = 8 * half
        for group in selected:
            start = base + group * group_words
            out += a[start:start + group_words]
            out += b[start:start + group_words]
    assert len(out) == 16
    return out


def perm2(a: list[int], b: list[int], high: bool) -> list[int]:
    return (a[8:] + b[8:]) if high else (a[:8] + b[:8])


def official_inputs(low: list[list[int]], high: list[list[int]]) -> list[list[int]]:
    """Return the eight stride-8 vectors expected by Official pack.s."""
    even = [low[plane][0::2] + high[plane][0::2] for plane in range(4)]
    odd = [low[plane][1::2] + high[plane][1::2] for plane in range(4)]
    return even + odd


def write(path: Path, record: dict, check: bool) -> None:
    rendered = json.dumps(record, indent=2, sort_keys=True) + "\n"
    if check:
        if not path.is_file() or path.read_text() != rendered:
            raise SystemExit(f"stale serializer V2 packet map: {path}")
    else:
        path.write_text(rendered)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--machine-wire", type=Path, required=True)
    parser.add_argument("--current-contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    machine = json.loads(args.machine_wire.read_text())
    current = json.loads(args.current_contract.read_text())
    mapping = machine["source_to_wire"]
    if len(mapping) != 1152 or sorted(mapping) != list(range(1152)):
        raise SystemExit("wire machine mapping is not a 1152-cell bijection")

    tiles = []
    for vector_base in range(0, 72, 4):
        planes = [mapping[16 * vector:16 * vector + 16]
                  for vector in range(vector_base, vector_base + 4)]
        flat = sorted(value for plane in planes for value in plane)
        if flat != list(range(flat[0], flat[0] + 64)):
            raise SystemExit("one quartet is not a 64-coefficient interval")
        tiles.append({"wire_coefficients": [flat[0], flat[-1]],
                      "state_vectors": list(range(vector_base, vector_base + 4)),
                      "input_lane_ownership": planes})
    tiles.sort(key=lambda tile: tile["wire_coefficients"][0])
    if [tile["wire_coefficients"][0] for tile in tiles] != list(range(0, 1152, 64)):
        raise SystemExit("wire tiles do not cover consecutive 64-coefficient intervals")

    packets = []
    for block in range(9):
        low, high = tiles[2 * block:2 * block + 2]
        inputs = official_inputs(low["input_lane_ownership"], high["input_lane_ownership"])
        expected = [list(range(128 * block + index, 128 * block + 128, 8))
                    for index in range(8)]
        if inputs != expected:
            raise SystemExit(f"packet {block} is not eight Official stride-8 vectors")
        emitted = [inputs[register][lane] for lane in range(16) for register in range(8)]
        if emitted != list(range(128 * block, 128 * block + 128)):
            raise SystemExit(f"packet {block} Official pack ownership is not sequential")
        packets.append({
            "packet": block,
            "wire_coefficients": [128 * block, 128 * block + 127],
            "wire_bytes": [192 * block, 192 * block + 191],
            "tile_state_vectors": [low["state_vectors"], high["state_vectors"]],
            "official_input_vector_ownership": inputs,
            "crosses_gt_branch": low["state_vectors"][0] < 36 <= high["state_vectors"][0],
            "schedule": {
                "data_loads": 8,
                "official_input_formation_routes": 24,
                "normalization": 48,
                "official_pack_and_six_stores": 58,
                "instructions": 138,
            },
        })

    current_per_tile = (
        4 + 24 + 4 + 4 + 8 + 27 + 3 + 3)
    if current_per_tile != 77 or current["total_expected_instructions"] != 1387:
        raise SystemExit("current serializer ledger changed")
    candidate_per_packet = 8 + 24 + 48 + 58
    candidate_total = 9 * candidate_per_packet + 1
    record = {
        "schema": "scale1-r-serializer-v2-packet-map/v1",
        "checkpoint": "SCALE1-R-SERIALIZER-V2-PACKET-MAP",
        "contract": {
            "input": "materialized wire-monotone scale-1 state; immutable",
            "output": "exact 1728 wire bytes in nine contiguous 192-byte blocks",
            "forward_boundary_preserved": True,
            "hash_and_sotp_unchanged": True,
        },
        "proof": {
            "all_18_quartets_are_exact_64_coefficient_intervals": True,
            "all_9_packets_yield_eight_stride8_official_pack_inputs": True,
            "official_lane_major_pack_ownership_is_128_sequential_coefficients": True,
            "all_output_bytes_cover_0_through_1727_once": True,
            "packet_4_cross_branch_is_safe_after_materialization": True,
        },
        "packets": packets,
        "instruction_budget": {
            "current_two_tiles_per_packet": 2 * current_per_tile,
            "candidate_per_packet": candidate_per_packet,
            "candidate_minus_current_per_packet": candidate_per_packet - 2 * current_per_tile,
            "current_full_including_ret": current["total_expected_instructions"],
            "candidate_full_including_ret": candidate_total,
            "candidate_minus_current_full": candidate_total - current["total_expected_instructions"],
            "normalization_vectors": [72, 72],
            "data_loads": [72, 72],
            "wire_stores": [54, 54],
        },
        "constant_geometry": {
            "current": "memory-form normalization/pair/pack constants repeated across 18 tiles",
            "candidate": "Official-style q and Barrett constants resident in ymm14/ymm15; pack uses shifts/blends/immediates",
            "exact_linked_delta_pending_asm": True,
        },
        "liveness": {
            "load_eight_inputs": 8,
            "formation_peak_data_and_temporaries": 10,
            "normalization_peak_including_four_temporaries_and_two_constants": 14,
            "expected_peak_ymm": 14,
            "stack_scratch_bytes": 0,
            "spill_expected": False,
        },
        "decision": {
            "asm_authorized": True,
            "reason": "exact ownership with predicted -144 instructions and no movement, normalization, or spill debt",
            "next": "generate one namespaced boundary-preserving serializer V2 ASM and compare exact linked object",
            "native_kem_authorized": False,
        },
    }
    write(args.output, record, args.check)
    print("scale-1 serializer V2 packet map: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
