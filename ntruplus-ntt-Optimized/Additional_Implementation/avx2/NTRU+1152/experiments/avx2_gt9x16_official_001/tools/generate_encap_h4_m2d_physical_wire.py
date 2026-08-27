#!/usr/bin/env python3
"""Rebuild H4 staging around the true physical-coefficient wire order."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path


N = 1152
VECTORS = 72
PAIRS = N // 2
BLOCKS = 9


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, document: dict, check: bool) -> None:
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if check:
        if not path.is_file() or path.read_text() != rendered:
            raise SystemExit(f"generated H4-M2D artifact is stale: {path}")
    else:
        path.write_text(rendered)


def qword_permutation(pairs: dict[int, tuple[int, int]]) -> tuple[int, ...]:
    """Find a qword order that makes every pair local to a 128-bit half."""
    for permutation in itertools.permutations(range(4)):
        new_qword = {old: new for new, old in enumerate(permutation)}
        if not all(new_qword[low // 4] // 2 == new_qword[high // 4] // 2
                   for low, high in pairs.values()):
            continue
        return permutation
    raise SystemExit("a physical-wire vector needs more than vpermq+vpshufb")


def vector_record(vector: int, lanes: dict[int, int]) -> dict:
    pairs: dict[int, tuple[int, int]] = {}
    for lane, wire in lanes.items():
        pair = wire // 2
        current = list(pairs.get(pair, (-1, -1)))
        current[wire & 1] = lane
        pairs[pair] = (current[0], current[1])
    if len(pairs) != 8 or any(low < 0 or high < 0
                              for low, high in pairs.values()):
        raise SystemExit(f"vector {vector} does not own eight complete wire pairs")

    adjacent = sum(abs(low - high) == 1 for low, high in pairs.values())
    cross_half = sum(low // 8 != high // 8 for low, high in pairs.values())
    permutation = qword_permutation(pairs)
    new_lane = {}
    for new_qword, old_qword in enumerate(permutation):
        for within in range(4):
            new_lane[4 * old_qword + within] = 4 * new_qword + within

    half_pairs: list[list[int]] = [[], []]
    for pair, (low, high) in pairs.items():
        half = new_lane[low] // 8
        if new_lane[high] // 8 != half:
            raise SystemExit(f"vector {vector} pair remains cross-half")
        half_pairs[half].append(pair)
    for values in half_pairs:
        values.sort()
        if len(values) != 4:
            raise SystemExit(f"vector {vector} half does not own four pairs")

    output_to_post_qword_lane = []
    for half, values in enumerate(half_pairs):
        for pair in values:
            low, high = pairs[pair]
            output_to_post_qword_lane += [new_lane[low], new_lane[high]]
    if any(source // 8 != output // 8
           for output, source in enumerate(output_to_post_qword_lane)):
        raise SystemExit(f"vector {vector} cannot lower with one vpshufb")
    byte_mask = []
    for source in output_to_post_qword_lane:
        byte_mask += [2 * (source & 7), 2 * (source & 7) + 1]

    direct = permutation == (0, 1, 2, 3)
    initial_pair_order = half_pairs[0] + half_pairs[1]
    desired_pair_order = sorted(initial_pair_order)
    post_sort = initial_pair_order != desired_pair_order
    pair32_sort = ([initial_pair_order.index(pair)
                    for pair in desired_pair_order] if post_sort else
                   list(range(8)))
    operations = ([] if direct else ["vpermq"]) + ["vpshufb",
        "vpmaddwd [1,4096]"] + (["vpermd pair32-sort"] if post_sort else [])
    topology = "+".join(operation.split()[0] for operation in operations
                        if not operation.startswith("vpmaddwd"))
    desired_halves = [desired_pair_order[:4], desired_pair_order[4:]]
    if any(values != list(range(values[0], values[0] + 4))
           for values in desired_halves):
        raise SystemExit(f"vector {vector} does not own two four-pair runs")
    return {
        "vector": vector,
        "lane_to_wire_coefficient": [lanes[lane] for lane in range(16)],
        "wire_pairs": [{"wire_pair": pair, "low_lane": low,
                         "high_lane": high,
                         "same_128bit_half": low // 8 == high // 8,
                         "adjacent_lanes": abs(low - high) == 1}
                        for pair, (low, high) in sorted(pairs.items())],
        "adjacent_pair_count": adjacent,
        "cross_128bit_pair_count": cross_half,
        "topology": topology,
        "vpermq_output_to_input_qword": list(permutation),
        "vpshufb_output_to_post_vpermq_byte": byte_mask,
        "pair32_before_sort": initial_pair_order,
        "pair32_vpermd_output_to_input_dword": pair32_sort,
        "pair32_lane_to_wire_pair": desired_pair_order,
        "pair32_half_runs": desired_halves,
        "pair_formation_instructions": operations,
    }


def block_records(vectors: list[dict]) -> list[dict]:
    by_pair = {}
    for vector in vectors:
        for half, run in enumerate(vector["pair32_half_runs"]):
            by_pair[run[0]] = {"vector": vector["vector"], "half": half,
                               "wire_pairs": run}
    blocks = []
    for block in range(BLOCKS):
        first_pair = 64 * block
        groups = []
        chunks = []
        owners = set()
        for group in range(8):
            start = first_pair + 8 * group
            left = by_pair[start]
            right = by_pair[start + 4]
            if left["wire_pairs"] + right["wire_pairs"] != list(
                    range(start, start + 8)):
                raise SystemExit(f"block {block} pair32 group is not contiguous")
            groups.append({"wire_pairs": list(range(start, start + 8)),
                           "low_128": left, "high_128": right,
                           "lowering": "vperm2i128 low/high halves"})
        block_vectors = sorted({source["vector"] for group in groups
                                for source in (group["low_128"],
                                               group["high_128"])})
        if len(block_vectors) != 8:
            raise SystemExit(f"block {block} does not use eight terminal vectors")
        for vector in block_vectors:
            record = next(item for item in vectors if item["vector"] == vector)
            for half, run in enumerate(record["pair32_half_runs"]):
                offset = 3 * run[0]
                chunks.append({"vector": vector, "pair32_half": half,
                               "wire_pairs": run, "scratch_byte_offset": offset,
                               "bytes": 12,
                               "exact_store_lowering": [
                                   "vmovq m64,xmm", "vpextrd m32,xmm,2"]})
                owners.update(range(offset, offset + 12))
        expected = set(range(192 * block, 192 * (block + 1)))
        if owners != expected:
            raise SystemExit(f"block {block} packed24 chunks are not exact")
        chunks.sort(key=lambda item: item["scratch_byte_offset"])
        blocks.append({
            "block": block, "wire_coefficients": [128 * block,
                                                     128 * block + 127],
            "wire_pairs": [first_pair, first_pair + 63],
            "terminal_vectors": block_vectors,
            "pair32_groups": groups,
            "packed24_chunks": chunks,
            "packed24_scratch_bytes": [192 * block, 192 * (block + 1) - 1],
            "final_alias_safe_copy": {
                "loads": 6, "stores": 6, "vector_bytes": 32},
        })
    return blocks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--direct-map", type=Path, required=True)
    parser.add_argument("--h4-map", type=Path, required=True)
    parser.add_argument("--h3-liveness", type=Path, required=True)
    parser.add_argument("--m2b", type=Path, required=True)
    parser.add_argument("--m2c", type=Path, required=True)
    parser.add_argument("--pack-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    direct = json.loads(args.direct_map.read_text())
    h4 = json.loads(args.h4_map.read_text())
    liveness = json.loads(args.h3_liveness.read_text())
    old_m2b = json.loads(args.m2b.read_text())
    old_m2c = json.loads(args.m2c.read_text())
    pack_source = args.pack_source.read_text()
    if "poly_tobytes:" not in pack_source or "poly_frombytes:" not in pack_source:
        raise SystemExit("Official pack source no longer exposes both directions")
    if len(direct["coefficient_map"]) != N or len(h4["terminal_order"]) != VECTORS:
        raise SystemExit("H4-M2D source cardinality changed")

    by_wire = {}
    by_vector: dict[int, dict[int, int]] = defaultdict(dict)
    for cell in direct["coefficient_map"]:
        # Official poly_tobytes/poly_frombytes preserve physical coefficient k
        # at wire position k.  The legacy serializer field is intentionally
        # excluded from the semantic key.
        wire = cell["official_coefficient"]
        if wire in by_wire or wire not in range(N):
            raise SystemExit("physical wire key is not a bijection")
        ma2 = cell["ma2"]
        by_wire[wire] = {
            "wire_coefficient": wire, "wire_pair": wire // 2,
            "wire_role": "low" if wire % 2 == 0 else "high",
            "wire_byte_offset": 3 * (wire // 2),
            "terminal_tile": f"b{ma2['branch']}p{ma2['p']}",
            "terminal_coefficient_plane": ma2["terminal_coefficient_plane"],
            "scratch_vector": ma2["vector"], "scratch_lane": ma2["lane"],
        }
        if ma2["lane"] in by_vector[ma2["vector"]]:
            raise SystemExit("duplicate scratch lane")
        by_vector[ma2["vector"]][ma2["lane"]] = wire
    if sorted(by_wire) != list(range(N)) or sorted(by_vector) != list(range(VECTORS)):
        raise SystemExit("physical-wire ownership is incomplete")

    vectors = [vector_record(vector, by_vector[vector])
               for vector in range(VECTORS)]
    topology = Counter(record["topology"] for record in vectors)
    adjacent_distribution = Counter(record["adjacent_pair_count"]
                                    for record in vectors)
    cross_distribution = Counter(record["cross_128bit_pair_count"]
                                 for record in vectors)
    if sum(record["adjacent_pair_count"] for record in vectors) != 320:
        raise SystemExit("adjacent pair count changed")
    if sum(8 - record["adjacent_pair_count"] for record in vectors) != 256:
        raise SystemExit("non-adjacent pair count changed")

    blocks = block_records(vectors)
    old_mismatches = sum(
        cell["wire_coefficient"] != cell["official_physical_coefficient"]
        for cell in old_m2b["exact_cell_map"])
    if old_mismatches != 1134:
        raise SystemExit(f"historical ownership mismatch changed: {old_mismatches}")

    terminal_normalization = 72 * 6
    orientation_routes = sum(len(record["pair_formation_instructions"]) - 1
                             for record in vectors)
    pair_madd = 72
    block_pair32_assembly = 9 * 8
    compact24_routes = 9 * 54
    ct_stores = 9 * 6
    staging = {
        "S2-prime-canonical-i16": {
            "terminal_normalization": terminal_normalization,
            "canonical_scratch_stores": 72,
            "egress_scratch_loads": 72,
            "pair_orientation_routes": orientation_routes,
            "pair_madd": pair_madd,
            "pair32_block_assembly_routes": block_pair32_assembly,
            "pair32_to_24bit_routes": compact24_routes,
            "ciphertext_stores": ct_stores,
        },
        "S1-prime-pair32": {
            "terminal_normalization": terminal_normalization,
            "pair_orientation_routes": orientation_routes,
            "pair_madd": pair_madd,
            "pair32_scratch_stores": 72,
            "egress_scratch_loads": 72,
            "pair32_block_assembly_routes": block_pair32_assembly,
            "pair32_to_24bit_routes": compact24_routes,
            "ciphertext_stores": ct_stores,
        },
        "S0-prime-packed24": {
            "terminal_normalization": terminal_normalization,
            "pair_orientation_routes": orientation_routes,
            "pair_madd": pair_madd,
            "pair32_half_pack_routes": 72,
            "upper_half_extract_routes": 72,
            "exact_12byte_chunk_stores": 288,
            "final_scratch_loads": 54,
            "ciphertext_stores": 54,
        },
    }
    for record in staging.values():
        record["total_instructions"] = sum(record.values())
    totals = {name: record["total_instructions"]
              for name, record in staging.items()}

    pair_oracle = []
    for pair in range(PAIRS):
        low = by_wire[2 * pair]
        high = by_wire[2 * pair + 1]
        if low["scratch_vector"] != high["scratch_vector"]:
            raise SystemExit(f"wire pair {pair} crosses YMM vectors")
        pair_oracle.append({
            "wire_pair": pair,
            "identity": f"c[{2 * pair}] + (c[{2 * pair + 1}] << 12)",
            "vector": low["scratch_vector"],
            "low_lane": low["scratch_lane"],
            "high_lane": high["scratch_lane"],
        })

    document = {
        "schema": "encap-h4-m2d-physical-wire/v1",
        "checkpoint": "H4-M2D-EXACT-PHYSICAL-WIRE-OWNERSHIP",
        "source_sha256": {name: sha256(path) for name, path in {
            "direct_map": args.direct_map, "h4_map": args.h4_map,
            "h3_liveness": args.h3_liveness, "rejected_m2b": args.m2b,
            "rejected_m2c": args.m2c, "official_pack_source": args.pack_source,
        }.items()},
        "semantic_invariant": {
            "wire_coefficient": "Official physical coefficient k",
            "wire_position": "k for every k in [0,1151]",
            "serialized_coefficient_field_used_as_semantic_key": False,
            "pair32": "c[2i] + (c[2i+1] << 12)",
        },
        "physical_wire_cells": [by_wire[index] for index in range(N)],
        "vector_ownership": vectors,
        "pair32_oracle": pair_oracle,
        "topology_summary": {
            "same_YMM_pairs": 576, "cross_YMM_pairs": 0,
            "adjacent_pairs": 320, "non_adjacent_pairs": 256,
            "adjacent_pairs_per_vector": dict(sorted(adjacent_distribution.items())),
            "cross_128bit_pairs_per_vector": dict(sorted(cross_distribution.items())),
            "lowering_classes": dict(sorted(topology.items())),
            "pair_orientation_routes": orientation_routes,
            "pair_madd_instructions": pair_madd,
        },
        "staging_families": staging,
        "blocks_128_coeff_192_bytes": blocks,
        "linked_h3_liveness": {
            "source_peak_ymm": liveness["peak_live_ymm"],
            "minimum_terminal_free_ymm": liveness["minimum_terminal_free_ymm"],
            "terminal_is_vector_local": True,
            "pair32_cross_terminal_wait_required": False,
            "incremental_frame_bytes": 0,
        },
        "rejected_evidence": {
            "m1_m2_m2c_ownership_derived_results": "REJECTED",
            "old_m2b_wire_vs_physical_mismatches": old_mismatches,
            "old_m2c_total_instructions": old_m2c["instruction_ledger"][
                "full_terminal_to_wire_instructions"],
            "reason": "serialized_coefficient was used as the wire semantic key",
        },
        "decision": {
            "winner_by_abstract_instruction_ledger": "S0-prime-packed24",
            "winner_credit_vs_S1_S2": (
                totals["S0-prime-packed24"] - totals["S1-prime-pair32"]),
            "asm_authorized": False,
            "next": (
                "validate exact 12-byte terminal chunk stores against linked H3 "
                "def/use and build one 8-vector/192-byte executable schedule"),
            "benchmark_authorized": False,
            "native_kem_authorized": False,
        },
    }
    write(args.output, document, args.check)
    print("H4-M2D: physical-wire ownership and three-family reranking complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
