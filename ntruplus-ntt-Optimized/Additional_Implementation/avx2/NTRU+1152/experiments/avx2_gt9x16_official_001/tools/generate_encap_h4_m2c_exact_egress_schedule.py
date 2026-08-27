#!/usr/bin/env python3
"""Lower Natural-Q canonical scratch to an exact wire-keyed H4 egress schedule."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path


UNPACK_LOW = (0, 1, 2, 3, 8, 9, 10, 11)
UNPACK_HIGH = (4, 5, 6, 7, 12, 13, 14, 15)
PACK24_SHUF = (0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14,
               0x80, 0x80, 0x80, 0x80)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, document: dict, check: bool) -> None:
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if check:
        if not path.is_file() or path.read_text() != rendered:
            raise SystemExit(f"generated file is stale: {path}")
    else:
        path.write_text(rendered)


def pair_byte_records(pair: int) -> list[dict]:
    low = 2 * pair
    high = low + 1
    return [
        {"byte": 3 * pair, "pair": pair, "owners": [
            {"wire_coefficient": low, "coefficient_bits": [0, 7],
             "byte_bits": [0, 7]},
        ]},
        {"byte": 3 * pair + 1, "pair": pair, "owners": [
            {"wire_coefficient": low, "coefficient_bits": [8, 11],
             "byte_bits": [0, 3]},
            {"wire_coefficient": high, "coefficient_bits": [0, 3],
             "byte_bits": [4, 7]},
        ]},
        {"byte": 3 * pair + 2, "pair": pair, "owners": [
            {"wire_coefficient": high, "coefficient_bits": [4, 11],
             "byte_bits": [0, 7]},
        ]},
    ]


def sort_record(pair_ids: list[int], source_name: str) -> dict:
    permutation = sorted(range(8), key=lambda index: pair_ids[index])
    sorted_ids = [pair_ids[index] for index in permutation]
    return {
        "source": source_name,
        "pair_ids_before_vpermd": pair_ids,
        "vpermd_output_to_input_dword": permutation,
        "pair_ids_after_vpermd": sorted_ids,
        "vpermd_required": permutation != list(range(8)),
    }


def tile_schedule(tile: str, vectors: dict[int, dict]) -> dict:
    if set(vectors) != {0, 1, 2, 3}:
        raise SystemExit(f"tile {tile} lacks four coefficient planes")
    pair32 = []
    for low_plane in (0, 2):
        low = vectors[low_plane]
        high = vectors[low_plane + 1]
        if high["terminal_vector"] != low["terminal_vector"] + 1:
            raise SystemExit(f"tile {tile} pair endpoints are not adjacent vectors")
        low_pairs = [entry["wire_pair"] for entry in low["lanes"]]
        high_pairs = [entry["wire_pair"] for entry in high["lanes"]]
        if low_pairs != high_pairs:
            raise SystemExit(f"tile {tile} pair endpoints do not share lanes")
        for half, indices in (("unpack-low", UNPACK_LOW),
                              ("unpack-high", UNPACK_HIGH)):
            ids = [low_pairs[index] for index in indices]
            record = sort_record(ids, f"plane{low_plane}-{half}")
            record.update({
                "low_terminal_vector": low["terminal_vector"],
                "high_terminal_vector": high["terminal_vector"],
                "source_lanes": list(indices),
                "pair_formation": [
                    f"vpunpck{'l' if half == 'unpack-low' else 'h'}wd",
                    "vpmaddwd [1,4096]",
                ],
            })
            pair32.append(record)

    # Match the even/odd parity vectors that cover the same two 8-pair spans.
    interval_sources: dict[tuple[int, int], list[int]] = defaultdict(list)
    for index, source in enumerate(pair32):
        values = source["pair_ids_after_vpermd"]
        intervals = []
        for chunk in (values[:4], values[4:]):
            if any(right != left + 2 for left, right in zip(chunk, chunk[1:])):
                raise SystemExit(f"tile {tile} pair32 chunk is not a parity stream")
            interval = chunk[0] // 8
            if chunk[-1] // 8 != interval:
                raise SystemExit(f"tile {tile} pair32 chunk crosses a wire group")
            intervals.append(interval)
        interval_sources[tuple(intervals)].append(index)

    parity_networks = []
    wire_groups = []
    for intervals, sources in sorted(interval_sources.items()):
        if len(sources) != 2:
            raise SystemExit(f"tile {tile} lacks an even/odd parity companion")
        left = pair32[sources[0]]["pair_ids_after_vpermd"]
        right = pair32[sources[1]]["pair_ids_after_vpermd"]
        groups = []
        for half, interval in enumerate(intervals):
            merged = sorted(left[4 * half:4 * half + 4] +
                            right[4 * half:4 * half + 4])
            expected = list(range(8 * interval, 8 * interval + 8))
            if merged != expected:
                raise SystemExit(f"tile {tile} parity network misses wire order")
            groups.append(expected)
            wire_groups.append(expected)
        parity_networks.append({
            "sources": sources,
            "source_pair_ids": [left, right],
            "instructions": [
                "vpunpckldq even,odd",
                "vpunpckhdq even,odd",
                "vperm2i128 low-halves",
                "vperm2i128 high-halves",
            ],
            "wire_groups": groups,
        })
    wire_groups.sort(key=lambda group: group[0])
    if len(wire_groups) != 4:
        raise SystemExit(f"tile {tile} does not own four wire groups")
    first_pair = wire_groups[0][0]
    if wire_groups != [list(range(first_pair + 8 * group,
                                  first_pair + 8 * group + 8))
                       for group in range(4)]:
        raise SystemExit(f"tile {tile} does not own 32 consecutive wire pairs")

    output_offset = 3 * first_pair
    byte_owners = []
    for group in wire_groups:
        for pair in group:
            byte_owners.extend(pair_byte_records(pair))
    if [entry["byte"] for entry in byte_owners] != list(
            range(output_offset, output_offset + 96)):
        raise SystemExit(f"tile {tile} byte replay is not contiguous")

    index_maps = [tuple(source["vpermd_output_to_input_dword"])
                  for source in pair32 if source["vpermd_required"]]
    return {
        "tile": tile,
        "scratch_terminal_vectors": [vectors[plane]["terminal_vector"]
                                     for plane in range(4)],
        "scratch_load_instructions": 4,
        "pair32_sources": pair32,
        "pair_formation_instructions": 8,
        "vpermd_instructions": len(index_maps),
        "vpermd_index_loads_within_tile_reuse": len(set(index_maps)),
        "parity_networks": parity_networks,
        "parity_interleave_instructions": 8,
        "wire_pair_groups": wire_groups,
        "pack24": {
            "vpshufb_mask_per_128bit_half": list(PACK24_SHUF),
            "first_48_bytes": "wire groups 0/1 -> A0,A1,A2",
            "second_48_bytes": "wire groups 2/3 -> B0,B1,B2",
            "pack48_instructions_each": [
                "2 vpshufb", "2 vextracti128", "5 shifts", "3 vpor"
            ],
            "final_vectors": ["A0|A1", "A2|B0", "B1|B2"],
            "route_instructions": 27,
        },
        "ciphertext_store_offsets": [output_offset, output_offset + 32,
                                     output_offset + 64],
        "ciphertext_store_instructions": 3,
        "byte_ownership_replay": byte_owners,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--m2b", type=Path, required=True)
    parser.add_argument("--m2-historical", type=Path, required=True)
    parser.add_argument("--m3-contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    m2b = json.loads(args.m2b.read_text())
    historical = json.loads(args.m2_historical.read_text())
    m3 = json.loads(args.m3_contract.read_text())
    if m2b["decision"]["selected_for_exact_schedule"] != "bitperm-3210-xor-0":
        raise SystemExit("M2B no longer selects Natural-Q")
    if m2b["wire_pair_classification"][
            "same_lane_cross_terminal_vector"] != 576:
        raise SystemExit("M2B wire-pair graph changed")
    if m3["abi"]["scratch"]["representation"] != (
            "canonical i16 Natural-Q MA2 planes"):
        raise SystemExit("M3 scratch ABI changed")

    by_tile: dict[str, dict[int, dict]] = defaultdict(dict)
    for cell in m2b["exact_cell_map"]:
        terminal = cell["terminal"]
        tile = terminal["tile"]
        plane = terminal["coefficient_plane"]
        record = by_tile[tile].setdefault(plane, {
            "terminal_vector": terminal["vector"], "lanes": [None] * 16})
        if record["terminal_vector"] != terminal["vector"]:
            raise SystemExit(f"tile {tile} plane {plane} has multiple vectors")
        lane = terminal["lane"]
        if record["lanes"][lane] is not None:
            raise SystemExit(f"duplicate tile {tile} plane {plane} lane {lane}")
        record["lanes"][lane] = {
            "wire_coefficient": cell["wire_coefficient"],
            "wire_pair": cell["wire_pair"],
            "wire_role": cell["wire_role"],
        }
    if len(by_tile) != 18:
        raise SystemExit("exact egress no longer has 18 tiles")
    for tile, planes in by_tile.items():
        for plane, record in planes.items():
            if any(entry is None for entry in record["lanes"]):
                raise SystemExit(f"tile {tile} plane {plane} is incomplete")

    tiles = [tile_schedule(tile, planes) for tile, planes in by_tile.items()]
    tiles.sort(key=lambda tile: tile["ciphertext_store_offsets"][0])
    if [tile["ciphertext_store_offsets"][0] for tile in tiles] != [
            96 * index for index in range(18)]:
        raise SystemExit("tile egress order does not cover ciphertext sequentially")

    all_pairs = [pair for tile in tiles for group in tile["wire_pair_groups"]
                 for pair in group]
    if all_pairs != list(range(576)):
        raise SystemExit("wire-pair replay is not exact global order")
    all_bytes = [entry["byte"] for tile in tiles
                 for entry in tile["byte_ownership_replay"]]
    if all_bytes != list(range(1728)):
        raise SystemExit("ciphertext-byte replay is not exact global order")
    replay_owners = {
        entry["byte"]: sorted(entry["owners"],
                              key=lambda owner: owner["byte_bits"])
        for tile in tiles for entry in tile["byte_ownership_replay"]
    }
    expected_owners: dict[int, list[dict]] = defaultdict(list)
    for cell in m2b["exact_cell_map"]:
        for contribution in cell["wire_byte_contributions"]:
            expected_owners[contribution["byte_index"]].append({
                "wire_coefficient": cell["wire_coefficient"],
                "coefficient_bits": contribution["coefficient_bits"],
                "byte_bits": contribution["byte_bits"],
            })
    expected_owners = {
        byte: sorted(owners, key=lambda owner: owner["byte_bits"])
        for byte, owners in expected_owners.items()
    }
    if replay_owners != expected_owners:
        raise SystemExit("scheduled pack byte-bit ownership differs from M2B")

    egress = {
        "scratch_data_loads": sum(tile["scratch_load_instructions"]
                                  for tile in tiles),
        "pair_unpack_routes": 4 * 18,
        "pair_madd_arithmetic": 4 * 18,
        "pair_formation_instructions": sum(
            tile["pair_formation_instructions"] for tile in tiles),
        "vpermd_sort_routes": sum(tile["vpermd_instructions"] for tile in tiles),
        "vpermd_index_loads": sum(
            tile["vpermd_index_loads_within_tile_reuse"] for tile in tiles),
        "parity_interleave_routes": sum(
            tile["parity_interleave_instructions"] for tile in tiles),
        "pack24_routes": sum(tile["pack24"]["route_instructions"]
                             for tile in tiles),
        "ciphertext_stores": sum(tile["ciphertext_store_instructions"]
                                 for tile in tiles),
    }
    egress["total_instructions"] = sum(egress.values()) - (
        egress["pair_unpack_routes"] + egress["pair_madd_arithmetic"])
    # pair_unpack/pair_madd are a taxonomy split of pair_formation, not extra.
    if egress != {
        "scratch_data_loads": 72,
        "pair_unpack_routes": 72,
        "pair_madd_arithmetic": 72,
        "pair_formation_instructions": 144,
        "vpermd_sort_routes": 72,
        "vpermd_index_loads": 26,
        "parity_interleave_routes": 144,
        "pack24_routes": 486,
        "ciphertext_stores": 54,
        "total_instructions": 998,
    }:
        raise SystemExit(f"exact egress ledger changed: {egress}")

    terminal = {
        "barrett_instructions": 216,
        "sign_canonicalization_instructions": 216,
        "canonical_scratch_stores": 72,
        "total_instructions": 504,
    }
    full_total = terminal["total_instructions"] + egress["total_instructions"]
    historical_natural = next(profile for profile in historical["profiles"]
                              if profile["presentation"] ==
                              "bitperm-3210-xor-0")
    old_total = historical_natural["families"][
        "M2-S2-canonical-i16"]["ledger"]["total_instructions"]
    if full_total != 1502 or old_total != full_total:
        raise SystemExit("exact schedule does not reconcile the historical ledger")

    document = {
        "schema": "encap-h4-m2c-exact-egress-schedule/v1",
        "checkpoint": "H4-M2C-NATURAL-Q-EXACT-WIRE-EGRESS-SCHEDULE",
        "boundary": (
            "canonical Natural-Q scale-1 i16 scratch to exact 1728-byte wire"),
        "source_sha256": {
            "m2b": sha256(args.m2b),
            "m2_historical": sha256(args.m2_historical),
            "m3_contract": sha256(args.m3_contract),
        },
        "fixed_contract": {
            "scratch_bytes": 2304,
            "scratch_alignment": 32,
            "scratch_values": "canonical unsigned i16 in [0,3456]",
            "ciphertext_bytes": 1728,
            "ciphertext_pointer_alignment": 1,
            "data_dependent_branches": 0,
            "data_dependent_indices": 0,
        },
        "pair_primitive": {
            "inputs": (
                "adjacent terminal vectors containing low/high wire endpoints "
                "in the same lane"),
            "instructions_per_16_pairs": [
                "vpunpcklwd", "vpunpckhwd", "vpmaddwd", "vpmaddwd"
            ],
            "weight": [1, 4096],
            "identity": "pair32 = low + (high << 12)",
            "signed_dword_range": [0, 3456 + 4096 * 3456],
            "fits_unsigned_24bit": 3456 + 4096 * 3456 < (1 << 24),
            "pre_pair_routes": 0,
        },
        "tiles_in_wire_order": tiles,
        "symbolic_proof": {
            "wire_pairs_replayed_in_order": len(all_pairs),
            "ciphertext_bytes_replayed_in_order": len(all_bytes),
            "ciphertext_bits_covered_once": m2b["bijection_proof"][
                "ciphertext_bits_covered_once"],
            "pair32_low_24_bits": (
                "little-endian bytes are low[7:0], "
                "low[11:8]|high[3:0]<<4, high[11:4]"),
        },
        "register_plan": {
            "peak_ymm": 10,
            "frame_bytes": 0,
            "spill_bytes": 0,
            "per_tile_phases": [
                "load and pair-pack two endpoint-vector pairs into four pair32 YMM",
                "sort four pair32 YMM in place with one reusable index YMM",
                "interleave parity companions into four wire-group YMM",
                "pack groups 0/1 and store first 32 bytes, retain A2 only",
                "pack groups 2/3, combine A2/B0, store remaining 64 bytes",
            ],
            "proof_status": (
                "explicit abstract allocation; linked def/use replay required "
                "after ASM"),
        },
        "instruction_ledger": {
            "terminal_to_scratch": terminal,
            "scratch_to_wire": egress,
            "full_terminal_to_wire_instructions": full_total,
            "historical_1502_reconciled": True,
            "constant_memory_operands": {
                "pair_weight_memory_forms": 72,
                "vpermd_index_loads": 26,
                "pack24_mask_memory_forms": 72,
            },
            "data_memory_instructions": 72 + 54,
            "full_including_canonical_scratch_stores": 72 + 72 + 54,
        },
        "decision": {
            "exact_schedule_complete": True,
            "asm_authorized": True,
            "benchmark_authorized": False,
            "selected": "Natural-Q M2-S2 wire-keyed exact egress",
            "next": (
                "write one namespaced H4-M3B ASM replacing only the H1 fallback; "
                "retain scale1 producer, H3 arithmetic, terminal canonical "
                "scratch, alias contract, and no benchmark until linked closure"),
        },
    }
    write(args.output, document, args.check)
    print("H4-M2C: exact 18-tile pair32/24-bit egress schedule and 1502 ledger passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
