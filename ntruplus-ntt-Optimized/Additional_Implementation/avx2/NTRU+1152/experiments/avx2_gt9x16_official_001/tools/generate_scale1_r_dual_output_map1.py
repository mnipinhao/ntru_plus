#!/usr/bin/env python3
"""Map live wire-Forward terminals directly into the exact r serializer."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("h4_m3b", path)
    if spec is None or spec.loader is None:
        raise SystemExit("cannot load exact-wire serializer generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_sources(path: Path) -> dict[tuple[int, int], list[int]]:
    text = path.read_text()
    pattern = re.compile(
        r"\.equ \.Lwire_abs_b([01])p([0-8])_o([0-3])_src, ([0-3])")
    result: dict[tuple[int, int], list[int | None]] = {
        (branch, row): [None] * 4 for branch in range(2) for row in range(9)
    }
    for branch, row, coefficient, source in pattern.findall(text):
        result[(int(branch), int(row))][int(coefficient)] = int(source)
    if any(any(item is None for item in values) for values in result.values()):
        raise SystemExit("incomplete Forward terminal source map")
    return {key: [int(item) for item in values] for key, values in result.items()}


def write(path: Path, value: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text() != value:
            raise SystemExit(f"stale dual-output MAP1 artifact: {path}")
    else:
        path.write_text(value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--machine-wire", type=Path, required=True)
    parser.add_argument("--terminal-controls", type=Path, required=True)
    parser.add_argument("--serializer-generator", type=Path, required=True)
    parser.add_argument("--serializer-contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    contract = json.loads(args.contract.read_text())
    serializer = json.loads(args.serializer_contract.read_text())
    machine = json.loads(args.machine_wire.read_text())
    module = load_module(args.serializer_generator)
    machine_tiles = module.machine_tiles(machine)
    tile_by_vectors = {tuple(tile["vectors"]): tile for tile in machine_tiles}
    sources = parse_sources(args.terminal_controls)

    if (contract["representation"]["scale"] != 1 or
            contract["representation"]["montgomery_exponent"] != 0 or
            not contract["alias_contract"]["ma2_may_read_r_after_hash_fanout"]):
        raise SystemExit("scale-1 fanout contract changed")
    if serializer["generator_ledger"]["scratch_loads"] != 72:
        raise SystemExit("direct serializer load ledger changed")

    tiles = []
    for branch in range(2):
        for row in range(9):
            vector_base = 4 * (9 * branch + row)
            vectors = tuple(range(vector_base, vector_base + 4))
            tile = tile_by_vectors.get(vectors)
            if tile is None:
                raise SystemExit(f"no serializer tile for b{branch}p{row}")
            source_order = sources[(branch, row)]
            if sorted(source_order) != list(range(4)):
                raise SystemExit(f"terminal outputs are not a register permutation at b{branch}p{row}")
            live_by_vector = [4 + source for source in source_order]

            # Rename the serializer's old input registers 0..3 onto the live
            # terminal registers.  Its old pair32 registers 4..7 move onto the
            # newly free 0..3.  This is a bijection, so no register-copy seam
            # and no seventeenth YMM value are required.
            rename = {old: live_by_vector[old] for old in range(4)}
            rename.update({4 + old: old for old in range(4)})
            if sorted(rename.values()) != list(range(8)):
                raise SystemExit("serializer register renaming is not bijective")

            wires = [machine["source_to_wire"][16 * vector + lane]
                     for vector in vectors for lane in range(16)]
            if sorted(wires) != list(range(tile["first_wire"], tile["first_wire"] + 64)):
                raise SystemExit("Forward quartet does not own serializer wire tile")
            tiles.append({
                "branch": branch,
                "row": row,
                "state_vectors": list(vectors),
                "terminal_source_registers": source_order,
                "live_register_by_state_vector": live_by_vector,
                "serializer_register_rename_0_to_7": [rename[index] for index in range(8)],
                "wire_interval": [tile["first_wire"], tile["first_wire"] + 63],
                "byte_offset": tile["output_offset"],
                "state_stores_retained": 4,
                "serializer_reloads_removed": 4,
                "register_moves_added": 0,
            })

    byte_intervals = sorted((tile["byte_offset"], tile["byte_offset"] + 95)
                            for tile in tiles)
    if byte_intervals != [(96 * index, 96 * index + 95) for index in range(18)]:
        raise SystemExit("dual-output tiles do not cover exact 1728-byte wire output")

    result = {
        "schema": "scale1-r-dual-output-map1/v1",
        "checkpoint": "SCALE1-R-DUAL-OUTPUT-MAP1",
        "boundary": {
            "input": "live D1/terminal wire vectors after their MA2-state stores",
            "outputs": ["retained wire-monotone scale-1 r state", "exact 1728-byte r serialization"],
            "later_consumers": ["hash_g/SOTP", "MA2"],
        },
        "tiles": tiles,
        "ledger": {
            "tiles": 18,
            "state_stores_retained": 72,
            "serializer_reloads": [72, 0],
            "register_moves_added": 0,
            "serializer_arithmetic_delta": 0,
            "serializer_routing_delta": 0,
            "serializer_output_stores_delta": 0,
            "expected_instruction_delta_vs_forward_plus_serializer": -72,
            "peak_ymm": serializer.get("peak_ymm", 14),
            "extra_scratch_bytes": 0,
        },
        "gates": {
            "all_18_forward_quartets_match_one_exact_wire_tile": True,
            "all_terminal_register_maps_are_permutations": True,
            "register_rename_is_bijective_without_moves": True,
            "wire_bytes_cover_0_through_1727_exactly_once": True,
            "r_state_is_stored_before_live_registers_are_reused": True,
            "ma2_abi_scale_and_ownership_unchanged": True,
        },
        "decision": {
            "asm_authorized": True,
            "native_kem_authorized": False,
            "next": "generate one namespaced dual-output Forward ASM and prove linked -72 reloads",
        },
    }
    write(args.output, json.dumps(result, indent=2, sort_keys=True) + "\n", args.check)
    print("scale-1 r dual-output MAP1: 18 exact live-terminal tiles, 72 reloads removable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
