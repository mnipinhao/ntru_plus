#!/usr/bin/env python3
"""Map PROD3 MA2 planes directly to Official 12-bit serialized bytes."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


Q = 3457
N = 1152
POLYBYTES = 1728
INV4_MONTGOMERY = -901
INV4_MONTGOMERY_QINV = 16379
SERIALIZER_BLOCK_COEFFICIENTS = 128


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, document: dict, check: bool) -> None:
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if check:
        if not path.is_file() or path.read_text() != rendered:
            raise SystemExit(f"generated file is stale: {path}")
    else:
        path.write_text(rendered)


def signed16(value: int) -> int:
    value &= 0xFFFF
    return value - 0x10000 if value >= 0x8000 else value


def mulhi_signed16(left: int, right: int) -> int:
    return (signed16(left) * signed16(right)) >> 16


def remove_scale4(value: int) -> int:
    low = signed16(value * INV4_MONTGOMERY_QINV)
    high = mulhi_signed16(value, INV4_MONTGOMERY)
    return signed16(high - mulhi_signed16(low, Q))


def official_barrett(value: int) -> int:
    # Exact non-saturating vpmulhrsw(value, 16), vpmullw(q), vpsubw path.
    quotient = (signed16(value) * 16 + 0x4000) >> 15
    return signed16(value - signed16(quotient * Q))


def official_canonical(value: int) -> int:
    reduced = official_barrett(value)
    return reduced + Q if reduced < 0 else reduced


def direct_canonical(value: int) -> int:
    return value + Q if value < 0 else value


def byte_contributions(coefficient: int) -> list[dict]:
    pair = coefficient // 2
    base = 3 * pair
    if coefficient % 2 == 0:
        return [
            {"byte_index": base, "coefficient_bits": [0, 7], "byte_bits": [0, 7]},
            {"byte_index": base + 1, "coefficient_bits": [8, 11], "byte_bits": [0, 3]},
        ]
    return [
        {"byte_index": base + 1, "coefficient_bits": [0, 3], "byte_bits": [4, 7]},
        {"byte_index": base + 2, "coefficient_bits": [4, 11], "byte_bits": [0, 7]},
    ]


def extract_tobytes(source: str) -> str:
    match = re.search(r"^poly_tobytes:\n(?P<body>.*?\nret)$", source, re.M | re.S)
    if not match:
        raise SystemExit("cannot isolate pinned poly_tobytes body")
    return match.group("body")


def instruction_counts(body: str) -> Counter:
    result: Counter = Counter()
    for line in body.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or line.endswith(":") or line.startswith("."):
            continue
        mnemonic = line.split(None, 1)[0]
        if mnemonic in {"lea", "add", "cmp", "jb", "ret"}:
            continue
        result[mnemonic] += 1
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prod2-map", type=Path, required=True)
    parser.add_argument("--consumer-map", type=Path, required=True)
    parser.add_argument("--ma0-contract", type=Path, required=True)
    parser.add_argument("--pack-source", type=Path, required=True)
    parser.add_argument("--pack-layout", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    prod2 = json.loads(args.prod2_map.read_text())
    consumer = json.loads(args.consumer_map.read_text())
    ma0 = json.loads(args.ma0_contract.read_text())
    pack_source = args.pack_source.read_text()
    pack_layout = json.loads(args.pack_layout.read_text())
    if prod2["schema"] != "gt-f0-prod2-ma2-map/v1":
        raise SystemExit("wrong PROD2 MA2-map schema")
    if consumer["schema"] != "gt-f0-ma-consumer-map/v1":
        raise SystemExit("wrong F0 consumer-map schema")
    if ma0["schema"] != "gt-f0-ma0-adapter/v1":
        raise SystemExit("wrong MA0 adapter schema")
    if pack_layout["schema"] != "official-pack-layout/v1":
        raise SystemExit("wrong Official pack-layout schema")
    physical_to_serialized = pack_layout["physical_to_serialized"]
    if len(physical_to_serialized) != N or sorted(physical_to_serialized) != list(range(N)):
        raise SystemExit("Official pack layout is not a permutation")
    if prod2["bijection_proof"]["ma2_destination_cells"] != N:
        raise SystemExit("MA2 destination map is incomplete")
    if consumer["bijection_proof"]["official_positions"] != N:
        raise SystemExit("Official ownership map is incomplete")

    owner_to_official = {}
    for vector in consumer["f0_vectors"]:
        for lane in vector["lanes"]:
            owner = lane["semantic_owner"]
            key = (owner["branch"], owner["p"], owner["q"],
                   owner["terminal_coefficient"])
            if key in owner_to_official:
                raise SystemExit(f"duplicate semantic owner: {key}")
            owner_to_official[key] = lane["official_position_i16"]
    if sorted(owner_to_official.values()) != list(range(N)):
        raise SystemExit("semantic-owner to Official-position map is not a bijection")

    coefficients = []
    by_official = {}
    by_serialized = {}
    vector_cells: dict[int, list[dict]] = defaultdict(list)
    for cell in prod2["d1_to_ma2_cells"]:
        owner = cell["semantic_owner"]
        key = (owner["branch"], owner["p"], owner["q"],
               owner["terminal_coefficient"])
        official = owner_to_official[key]
        serialized = physical_to_serialized[official]
        consumer_cell = cell["consumer"]
        record = {
            "ma2": {
                "branch": owner["branch"],
                "p": owner["p"],
                "terminal_coefficient_plane": consumer_cell["coefficient_plane"],
                "physical_q": owner["q"],
                "vector": consumer_cell["ma2_native_vector"],
                "lane": consumer_cell["ma2_native_packed_lane"],
                "byte_offset": 32 * consumer_cell["ma2_native_vector"]
                               + 2 * consumer_cell["ma2_native_packed_lane"],
            },
            "semantic_owner": owner,
            "official_coefficient": official,
            "serializer": {
                "serialized_coefficient": serialized,
                "block": serialized // SERIALIZER_BLOCK_COEFFICIENTS,
                "coefficient_in_block": serialized % SERIALIZER_BLOCK_COEFFICIENTS,
                "pair": serialized // 2,
                "pair_parity": "low" if serialized % 2 == 0 else "high",
                "byte_contributions": byte_contributions(serialized),
            },
            "input_range_i16": cell["range_i16"],
            "input_scale": 4,
        }
        if official in by_official:
            raise SystemExit(f"duplicate Official coefficient {official}")
        by_official[official] = record
        by_serialized[serialized] = record
        coefficients.append(record)
        vector_cells[record["ma2"]["vector"]].append(record)
    if (sorted(by_official) != list(range(N)) or
            sorted(by_serialized) != list(range(N)) or len(vector_cells) != 72):
        raise SystemExit("MA2-to-Official coefficient mapping is incomplete")

    pairs = []
    same_vector_pairs = 0
    same_half_pairs = 0
    cross_half_vectors = set()
    for even in range(0, N, 2):
        low = by_serialized[even]
        high = by_serialized[even + 1]
        low_position = low["ma2"]
        high_position = high["ma2"]
        same_vector = low_position["vector"] == high_position["vector"]
        same_half = same_vector and low_position["lane"] // 8 == high_position["lane"] // 8
        if same_vector:
            same_vector_pairs += 1
        if same_half:
            same_half_pairs += 1
        elif same_vector:
            cross_half_vectors.add(low_position["vector"])
        pairs.append({
            "pair": even // 2,
            "serializer_block": even // SERIALIZER_BLOCK_COEFFICIENTS,
            "output_bytes": [3 * (even // 2) + offset for offset in range(3)],
            "low": {"official_coefficient": low["official_coefficient"],
                    "serialized_coefficient": even,
                    "ma2_vector": low_position["vector"],
                    "ma2_lane": low_position["lane"]},
            "high": {"official_coefficient": high["official_coefficient"],
                     "serialized_coefficient": even + 1,
                     "ma2_vector": high_position["vector"],
                     "ma2_lane": high_position["lane"]},
            "same_ma2_vector": same_vector,
            "same_128bit_half": same_half,
        })
    vector_fragments = []
    block_vectors: dict[int, set[int]] = defaultdict(set)
    for vector in range(72):
        cells = vector_cells[vector]
        if len(cells) != 16:
            raise SystemExit(f"MA2 vector {vector} does not own 16 coefficients")
        for cell in cells:
            block_vectors[cell["serializer"]["block"]].add(vector)
    if set(block_vectors) != set(range(9)):
        raise SystemExit("serializer block ownership is incomplete")

    global_low = min(record["input_range_i16"][0] for record in coefficients)
    global_high = max(record["input_range_i16"][1] for record in coefficients)
    post_values = [remove_scale4(value) for value in range(global_low, global_high + 1)]
    congruence = all((4 * remove_scale4(value) - value) % Q == 0
                     for value in range(global_low, global_high + 1))
    canonical_equal = all(
        direct_canonical(remove_scale4(value)) == official_canonical(remove_scale4(value))
        for value in range(global_low, global_high + 1))
    canonical_values = [direct_canonical(value) for value in post_values]
    if not congruence or not canonical_equal:
        raise SystemExit("scale-4 or canonicalization exhaustive proof failed")
    if min(post_values) <= -Q or max(post_values) >= Q:
        raise SystemExit("post-inv4 range requires more than sign canonicalization")
    if min(canonical_values) != 0 or max(canonical_values) != Q - 1:
        raise SystemExit("canonical range is not exactly [0,q)")

    h1_source_half_groups = 0
    for official_vector in range(72):
        half_groups = []
        for destination_half in range(2):
            half_groups.append({
                (by_official[16 * official_vector + 8 * destination_half + lane]
                 ["ma2"]["vector"],
                 by_official[16 * official_vector + 8 * destination_half + lane]
                 ["ma2"]["lane"] // 8)
                for lane in range(8)
            })
        h1_source_half_groups += max(len(groups) for groups in half_groups)
    if h1_source_half_groups != ma0["source_half_groups"]:
        raise SystemExit("direct MA2/Official construction no longer matches the 136-group proof")
    h1_loads = 2 * h1_source_half_groups
    h1_routes = 3 * h1_source_half_groups - 72

    pack_body = extract_tobytes(pack_source)
    pack_counts = instruction_counts(pack_body)
    expected_pack_counts = {
        "vmovdqa": 10, "vpmulhrsw": 8, "vpmullw": 8, "vpsubw": 8,
        "vpsraw": 8, "vpand": 8, "vpaddw": 8, "vpsllw": 6,
        "vpsrlw": 4, "vpxor": 6, "vpslld": 3, "vpsrlq": 6,
        "vpsllq": 3, "vpblendw": 6, "vpblendd": 6,
        "vpunpcklqdq": 3, "vpunpckhqdq": 3, "vperm2i128": 6,
        "vmovdqu": 6,
    }
    if dict(pack_counts) != expected_pack_counts:
        raise SystemExit(f"pinned poly_tobytes instruction shape changed: {dict(pack_counts)}")

    h0 = {
        "status": "exact linked-source ledger",
        "ma2_initial_loads": 72,
        "intermediate_stores": 216,
        "intermediate_reloads": 416,
        "routing_before_pack": 72 + ma0["executed_routing"]["total"],
        "inv4_montgomery_vectors": 72,
        "official_barrett_vectors": 72,
        "sign_canonicalization_vectors": 72,
        "pack_bit_and_transpose_instructions": 9 * 52,
        "byte_vector_stores": 54,
        "temporary_bytes": 4608,
        "derivation": {
            "plane_to_generic": "72 loads + 72 vperm2i128 + 72 stores",
            "generic_to_official": "272 loads + 336 routes + 72 stores",
            "scale4_array_pass": "72 reloads + 72 Montgomery vectors + 72 stores",
            "official_pack": "72 reloads + 72 Barrett + 72 sign canonicalizations + 468 pack instructions + 54 stores",
        },
    }
    h1 = {
        "status": "exact construction upper bound; no intermediate array",
        "ma2_initial_loads": h1_loads,
        "intermediate_stores": 0,
        "intermediate_reloads": 0,
        "routing_before_pack": h1_routes,
        "inv4_montgomery_vectors": 72,
        "official_barrett_vectors": 0,
        "sign_canonicalization_vectors": 72,
        "pack_bit_and_transpose_instructions": 9 * 52,
        "byte_vector_stores": 54,
        "temporary_bytes": 0,
        "peak_ymm_upper_bound": 16,
        "source_half_groups": h1_source_half_groups,
        "proof_note": "the MA2 ownership map independently re-derives the same 136 source-half groups as the proved MA0 adapter; rebuild each eight-vector Official pack block in registers, then fuse inv4, sign-add-q and the pinned pack network",
    }
    h2 = {
        "status": "invalidated by pinned pack-layout probe; redesign deferred",
        "ma2_initial_loads_lower_bound": None,
        "intermediate_stores": 0,
        "intermediate_reloads": 0,
        "serialized_pairs_same_ma2_vector": same_vector_pairs,
        "serialized_pairs_same_128bit_half": same_half_pairs,
        "serialized_pairs_cross_ma2_vector": N // 2 - same_vector_pairs,
        "serialized_pairs_cross_128bit_half": None,
        "vectors_requiring_cross_half_pair_routing": None,
        "cross_half_route_lower_bound": None,
        "fragments": None,
        "fragment_bytes": None,
        "inv4_montgomery_vectors": 72,
        "official_barrett_vectors": 0,
        "sign_canonicalization_vectors": 72,
        "byte_stores": None,
        "temporary_bytes": 0,
        "unresolved_before_asm": [
            "derive a new H2 ownership schedule from probed physical-to-serialized order",
            "price H1 before authorizing that redesign",
        ],
    }

    document = {
        "schema": "gt9x16-prod3-ma2-hash-direct-map/v1",
        "checkpoint": "GT9X16-PROD3-MA2-HASH-DIRECT-MAP",
        "parameter": N,
        "target": {
            "input": "materialized PROD3 MA2 coefficient planes, scale 4",
            "output": "exact pinned Official poly_tobytes byte string",
            "output_bytes": POLYBYTES,
            "forbidden_intermediate": "generic F0 or Official 2304-byte coefficient array",
        },
        "coefficient_map": sorted(coefficients, key=lambda item: item["official_coefficient"]),
        "pair_map": pairs,
        "packing_oriented_vectors": vector_fragments,
        "serializer_blocks": [{
            "block": block,
            "coefficient_range": [128 * block, 128 * block + 127],
            "output_byte_range": [192 * block, 192 * block + 191],
            "ma2_vectors": sorted(block_vectors[block]),
        } for block in range(9)],
        "bijection_and_ownership_proof": {
            "ma2_cells": len(coefficients),
            "official_coefficients": len(by_official),
            "serialized_bytes": len({item["byte_index"]
                                     for record in coefficients
                                     for item in record["serializer"]["byte_contributions"]}),
            "serialized_pairs": len(pairs),
            "all_pairs_same_ma2_vector": same_vector_pairs == N // 2,
            "vectors": len(vector_cells),
            "pairs_per_vector": None,
            "fragments_per_vector": None,
            "fragment_bytes": None,
            "vectors_per_serializer_block": [len(block_vectors[block])
                                                for block in range(9)],
        },
        "scale_and_range_proof": {
            "method": "exhaustive over every signed integer in the global proved PROD3 MA2 input envelope",
            "input_scale": 4,
            "input_range_i16": [global_low, global_high],
            "tested_values": global_high - global_low + 1,
            "inv4_montgomery": INV4_MONTGOMERY,
            "inv4_montgomery_qinv": INV4_MONTGOMERY_QINV,
            "post_inv4_range_i16": [min(post_values), max(post_values)],
            "four_times_output_congruent_to_input": congruence,
            "post_inv4_strictly_inside_minus_q_q": True,
            "official_barrett_is_redundant_after_inv4": canonical_equal,
            "direct_sign_add_q_matches_official_pack": canonical_equal,
            "canonical_range": [min(canonical_values), max(canonical_values)],
            "pack12_safe": max(canonical_values) < 4096,
        },
        "pinned_pack_audit": {
            "loop_count": 9,
            "coefficients_per_loop": 128,
            "bytes_per_loop": 192,
            "static_instruction_counts": dict(pack_counts),
            "dynamic_data_loads": 72,
            "dynamic_byte_vector_stores": 54,
            "dynamic_pack_bit_and_transpose_instructions": 9 * 52,
        },
        "movement_ledger": {"H0-current": h0, "H1-direct-official-block": h1,
                            "H2-packing-oriented": h2},
        "decision": {
            "map_complete": True,
            "direct_serializer_asm_authorized": False,
            "benchmark_authorized": False,
            "selected_first_realization": "H1-direct-official-block",
            "reason": "H1 removes all full-array materializations and follows the probed pinned-pack physical order; the earlier H2 lower bound used an incorrect linear interpretation of Official physical positions and is invalidated",
            "next": "lower and audit H1 only; defer any H2 redesign until after H1 pricing",
        },
        "source_sha256": {
            "prod2_map": sha256(args.prod2_map),
            "consumer_map": sha256(args.consumer_map),
            "ma0_contract": sha256(args.ma0_contract),
            "pinned_pack_s": sha256(args.pack_source),
            "pinned_pack_layout": sha256(args.pack_layout),
        },
    }
    write_json(args.output, document, args.check)
    print("PROD3 MA2 hash map: probed pack permutation applied; "
          f"{same_vector_pairs}/576 serialized pairs stay within one MA2 vector")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
