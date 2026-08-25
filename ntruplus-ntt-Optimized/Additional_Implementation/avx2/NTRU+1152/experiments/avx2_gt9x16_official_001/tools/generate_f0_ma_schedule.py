#!/usr/bin/env python3
"""Generate correctness-first F0 MulAdd schedules and prototype selection."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from collections import defaultdict
from pathlib import Path

Q = 3457
CENTERED = [-1728, 1728]
P_ORDER = [0, 3, 6, 1, 4, 7, 8, 2, 5]
STREAM_PHYSICAL_LANES = list(range(0, 16, 2)) + list(range(1, 16, 2))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def montgomery_bound(left: list[int], right: list[int]) -> list[int]:
    """Prove a bound for Official's signed high-half Montgomery sequence."""
    products = [left[i] * right[j] for i in range(2) for j in range(2)]
    high_min = math.floor(min(products) / 65536)
    high_max = math.floor(max(products) / 65536)
    correction_min = math.floor((-32768 * Q) / 65536)
    correction_max = math.floor((32767 * Q) / 65536)
    return [high_min - correction_max, high_max - correction_min]


def add_bounds(*ranges: list[int]) -> list[int]:
    return [sum(value[0] for value in ranges),
            sum(value[1] for value in ranges)]


def scale_bound(value: list[int], scalar: int) -> list[int]:
    endpoints = [value[0] * scalar, value[1] * scalar]
    return [min(endpoints), max(endpoints)]


def assert_i16(name: str, bound: list[int]) -> None:
    if bound[0] < -32768 or bound[1] > 32767:
        raise SystemExit(f"{name} exceeds signed i16: {bound}")


def output(path: Path, document: dict, check: bool) -> None:
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if check:
        if not path.is_file() or path.read_text() != rendered:
            raise SystemExit(f"generated file is stale: {path}")
    else:
        path.write_text(rendered)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--consumer-map", type=Path, required=True)
    parser.add_argument("--synthesis", type=Path, required=True)
    parser.add_argument("--poly-header", type=Path, required=True)
    parser.add_argument("--pack-source", type=Path, required=True)
    parser.add_argument("--basemul-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    consumer = json.loads(args.consumer_map.read_text())
    synthesis = json.loads(args.synthesis.read_text())
    poly_header = args.poly_header.read_text()
    pack_source = args.pack_source.read_text()
    basemul_source = args.basemul_source.read_text()
    if consumer["schema"] != "gt-f0-ma-consumer-map/v1":
        raise SystemExit("wrong consumer map schema")
    if synthesis["schema"] != "gt-f0-ma-symbolic-synthesis/v1":
        raise SystemExit("wrong synthesis schema")
    if "poly __attribute__((aligned(32)))" not in poly_header:
        raise SystemExit("pinned poly alignment contract changed")
    if "vmovdqu %ymm0,    (%rdi)" not in pack_source:
        raise SystemExit("pinned serializer byte-output alignment changed")
    if ".p2align 5\n_looptop_poly_tobytes" not in pack_source:
        raise SystemExit("pinned serializer loop alignment changed")
    if ".p2align 5\n_looptop_basemul" not in basemul_source:
        raise SystemExit("pinned BaseMul loop alignment changed")

    owner_lanes: dict[tuple[int, int, int], list[dict]] = defaultdict(list)
    all_owners = set()
    for vector in consumer["f0_vectors"]:
        for lane in vector["lanes"]:
            owner = lane["semantic_owner"]
            key = (owner["branch"], owner["p"], owner["terminal_coefficient"])
            owner_lanes[key].append(lane)
            all_owners.add((owner["branch"], owner["p"], owner["q"],
                            owner["terminal_coefficient"]))
    if len(all_owners) != 1152:
        raise SystemExit("consumer ownership is incomplete")

    tiles = []
    chunk_tiles: dict[int, set[tuple[int, int]]] = defaultdict(set)
    for branch in range(2):
        for physical_row, p in enumerate(P_ORDER):
            planes = []
            tile_positions = set()
            for coefficient in range(4):
                lanes = sorted(owner_lanes[(branch, p, coefficient)],
                               key=lambda lane: STREAM_PHYSICAL_LANES.index(
                                   lane["physical_q_lane"]))
                if [lane["physical_q_lane"] for lane in lanes] != STREAM_PHYSICAL_LANES:
                    raise SystemExit("coefficient plane physical-lane order changed")
                source_vectors = sorted({lane["official_position_i16"] // 16
                                         for lane in lanes})
                source_offsets = [lane["official_position_i16"] % 16 for lane in lanes]
                if len(source_vectors) != 2 or source_offsets[:8] != source_offsets[8:]:
                    raise SystemExit("resident-h two-vector projection shape changed")
                f0_positions = [lane["f0_position_i16"] for lane in lanes]
                pair = coefficient // 2
                half = coefficient % 2
                expected_f0 = []
                for stream in range(2):
                    base = ((((branch * 9 + physical_row) * 2 + pair) * 2 + stream) * 16)
                    expected_f0.extend(base + half * 8 + index for index in range(8))
                if f0_positions != expected_f0:
                    raise SystemExit("F0 local coefficient-plane formation changed")
                positions = [lane["official_position_i16"] for lane in lanes]
                chunks = {position // 128 for position in positions}
                if len(chunks) != 1:
                    raise SystemExit("semantic tile spans multiple serializer chunks")
                chunk = chunks.pop()
                chunk_tiles[chunk].add((branch, p))
                tile_positions.update(positions)
                planes.append({
                    "coefficient": coefficient,
                    "lane_order": "even physical-q lanes then odd physical-q lanes",
                    "physical_q_lanes": STREAM_PHYSICAL_LANES,
                    "semantic_q": [lane["semantic_owner"]["q"] for lane in lanes],
                    "f0_positions_i16": f0_positions,
                    "resident_h_official_positions_i16": positions,
                    "resident_h_source_vectors": source_vectors,
                    "resident_h_source_lane_offsets": source_offsets,
                    "lambda_mod_q": [lane["lambda_mod_q"] for lane in lanes],
                    "f0_exact_ranges_i16": [lane["exact_f0_range_i16"] for lane in lanes],
                })
            tiles.append({
                "tile": {"branch": branch, "physical_p_row": physical_row, "p": p},
                "official_serializer_chunk": chunk,
                "official_positions": sorted(tile_positions),
                "planes": planes,
            })

    if sorted(chunk_tiles) != list(range(9)) or any(len(pair) != 2
                                                    for pair in chunk_tiles.values()):
        raise SystemExit("expected nine two-tile Official chunks")
    if set().union(*chunk_tiles.values()) != {(b, p) for b in range(2) for p in P_ORDER}:
        raise SystemExit("tile/chunk pairing is not a bijection")
    chunks = [{"official_chunk": chunk,
               "official_i16_range": [chunk * 128, chunk * 128 + 127],
               "semantic_tiles": [{"branch": b, "p": p}
                                  for b, p in sorted(chunk_tiles[chunk])],
               "resident_h_projection": {
                   "aligned_vector_loads": 8,
                   "vperm2i128": 8,
                   "vpshufb": 8,
                   "routing_total": 16,
                   "output_planes": 8,
               },
               "serializer_inverse_projection": {
                   "input_planes": 8,
                   "vpshufb": 8,
                   "vperm2i128": 8,
                   "routing_total": 16,
                   "official_vectors": 8,
               }} for chunk in range(9)]

    terms: dict[int, list[tuple[int, int, int]]] = defaultdict(list)
    for left in range(4):
        for right in range(4):
            degree = left + right
            terms[degree % 4].append((left, right, degree // 4))
    native_pairs = {(0, 1), (2, 3)}
    ma1_pairings = []
    routes_per_stream = 0
    for lower_output, upper_output in ((0, 1), (2, 3)):
        best = None
        for permutation in itertools.permutations(terms[upper_output]):
            pairs = list(zip(terms[lower_output], permutation))
            routes = sum((lower[0], upper[0]) not in native_pairs
                         for lower, upper in pairs)
            routes += sum((lower[1], upper[1]) not in native_pairs
                          for lower, upper in pairs)
            if best is None or routes < best[0]:
                best = (routes, pairs)
        assert best is not None
        routes_per_stream += best[0]
        ma1_pairings.append({
            "output_pair": [lower_output, upper_output],
            "minimum_operand_half_routes_per_stream": best[0],
            "paired_terms": [{"lower": list(lower), "upper": list(upper),
                              "h_pair_native": (lower[0], upper[0]) in native_pairs,
                              "r_pair_native": (lower[1], upper[1]) in native_pairs}
                             for lower, upper in best[1]],
        })
    if routes_per_stream != 12:
        raise SystemExit("MA1 exact operand-pair routing changed")
    ma1_bilinear_routes = routes_per_stream * 2 * 18

    product_bound = montgomery_bound(CENTERED, CENTERED)
    pair_sum = [-3456, 3456]
    pair_product_bound = montgomery_bound(pair_sum, pair_sum)
    lambda_bound = CENTERED
    ma2_outputs = []
    term_counts = [(1, 3), (2, 2), (3, 1), (4, 0)]
    for coefficient, (plain_count, wrapped_count) in enumerate(term_counts):
        plain = scale_bound(product_bound, plain_count)
        if wrapped_count:
            wrapped_sum = scale_bound(product_bound, wrapped_count)
            wrapped = montgomery_bound(wrapped_sum, lambda_bound)
        else:
            wrapped_sum = [0, 0]
            wrapped = [0, 0]
        final_precenter = add_bounds(CENTERED, plain, wrapped)
        assert_i16(f"MA2 output {coefficient}", final_precenter)
        ma2_outputs.append({"coefficient": coefficient,
                            "plain_product_count": plain_count,
                            "wrapped_product_count": wrapped_count,
                            "plain_sum_preoperation": plain,
                            "wrapped_sum_pre_lambda": wrapped_sum,
                            "wrapped_after_montgomery_lambda": wrapped,
                            "with_centered_m_addend_pre_final_center": final_precenter,
                            "after_center": CENTERED})

    qmul_first_precenter = add_bounds(product_bound,
                                      montgomery_bound(product_bound, lambda_bound))
    qmul_second_precenter = add_bounds(pair_product_bound,
                                       scale_bound(product_bound, -1),
                                       scale_bound(product_bound, -1))
    cross_precenter = add_bounds(CENTERED, scale_bound(CENTERED, -1),
                                 scale_bound(CENTERED, -1))
    ma3_final = [
        add_bounds(CENTERED, CENTERED, montgomery_bound(CENTERED, lambda_bound)),
        add_bounds(CENTERED, CENTERED),
        add_bounds(CENTERED, CENTERED, CENTERED),
        add_bounds(CENTERED, CENTERED),
    ]
    for name, bound in [("MA3 qmul first", qmul_first_precenter),
                        ("MA3 qmul second", qmul_second_precenter),
                        ("MA3 cross", cross_precenter)]:
        assert_i16(name, bound)
    for index, bound in enumerate(ma3_final):
        assert_i16(f"MA3 output {index}", bound)

    scale_search = {
        "selected": "S0-output-finalizer",
        "variants": [
            {"id": "S0-output-finalizer", "r_scale": 4, "m_scale": 4,
             "h_scale": 1, "muladd_output_scale": 4,
             "runtime_inv4_vector_chains_full_1152": 72,
             "schedule": "four output-plane chains per semantic tile immediately before inverse projection/serialization",
             "reason": "single common output normalization; can be scheduled with serializer but is not claimed zero-cost"},
            {"id": "S1-role-specific-inputs", "r_scale": 4, "m_scale": 1,
             "h_scale": 2593, "muladd_output_scale": 1,
             "runtime_inv4_vector_chains_full_1152": 144,
             "schedule": "72 resident-h projection chains plus 72 F0(m) chains",
             "free_absorption": False,
             "reason": "no existing multiplication has yet been proved to absorb both uniform factors"},
            {"id": "S2-product-plus-addend", "r_scale": 4, "m_scale": 1,
             "h_scale": 1, "muladd_output_scale": 1,
             "runtime_inv4_vector_chains_full_1152": 144,
             "schedule": "72 product-output chains plus 72 F0(m) chains",
             "free_absorption": False,
             "reason": "strictly more normalization chains than S0 under the proved schedule"},
        ],
        "rule": "absorption is free only when an already-required multiplication changes constant without adding a chain",
        "inv4_mod_q": 2593,
    }

    candidates = [
        {"id": "MA0", "role": "Official adapter control",
         "projection_and_serializer": {"f0_to_official_routing": 288,
                                       "minimum_adapter_vector_loads": 144,
                                       "minimum_adapter_vector_stores": 144},
         "prototype": "control-only"},
        {"id": "MA1", "role": "persistent-pair F0-native weighted schoolbook",
         "vector_montgomery_chains_per_tile": 20,
         "routing_full_1152": {"resident_h_pair_projection": 216,
                               "bilinear_operand_pairing": ma1_bilinear_routes,
                               "serializer_inverse_projection": 144,
                               "total": 792},
         "liveness": {"output_accumulators": 4, "operand_pairs": 2,
                      "montgomery_temporaries": 3, "constants": 3,
                      "routing_temporaries": 2, "peak_ymm": 14,
                      "spills": 0},
         "range_schedule": "center h/r/m on consumption; wrapped sums before lambda; center four outputs",
         "prototype": "authorized-first-research-candidate",
         "reason": "retained to price direct F0-basis arithmetic despite higher proved routing"},
        {"id": "MA2", "role": "local coefficient-plane weighted schoolbook",
         "vector_montgomery_chains_per_tile": 19,
         "routing_full_1152": {"f0_r_plane_formation": 72,
                               "f0_m_plane_formation": 72,
                               "resident_h_projection": 144,
                               "serializer_inverse_projection": 144,
                               "total": 432},
         "liveness": {"output_accumulators": 4, "operands": 2,
                      "montgomery_temporaries": 3, "constants": 3,
                      "routing_temporaries": 1, "peak_ymm": 13,
                      "spills": 0},
         "range_schedule": "center h/r/m planes; sum wrapped terms before lambda; center four outputs",
         "prototype": "deferred-after-schedule",
         "reason": "same external geometry as MA3 but six more Montgomery chains per tile"},
        {"id": "MA3", "role": "local coefficient-plane streaming even/odd rank-9",
         "vector_montgomery_chains_per_tile": 13,
         "routing_full_1152": {"f0_r_plane_formation": 72,
                               "f0_m_plane_formation": 72,
                               "resident_h_projection": 144,
                               "serializer_inverse_projection": 144,
                               "total": 432},
         "liveness": {"output_accumulators": 4, "quadratic_operand_halves": 4,
                      "montgomery_temporaries": 3, "constants": 3,
                      "routing_temporaries": 1, "peak_ymm": 15,
                      "spills": 0,
                      "rank_products_live_together": False,
                      "schedule": "EE then OO then TT; each rank product is accumulated and killed immediately"},
         "range_schedule": "center inputs and every quadratic output/cross value before reuse; center final outputs",
         "prototype": "authorized-geometry-challenger",
         "reason": "same proved projection/serializer geometry as MA2, six fewer chains per tile, peak remains below 16"},
    ]

    document = {
        "schema": "gt-f0-ma-schedule/v1",
        "checkpoint": "F0-MA-SCHED",
        "parameter": 1152,
        "decision": {
            "schedule_proof_complete": True,
            "assembly_candidates": ["MA1", "MA3"],
            "control": "MA0",
            "deferred": ["MA2"],
            "assembly_implemented": False,
            "performance_claim": False,
            "primary_future_benchmark": "F0(r)+F0(m)+resident-h projection+MulAdd+inv4 finalizer+poly_tobytes",
        },
        "semantic_tiles": tiles,
        "official_chunk_pairing": chunks,
        "physical_schedule": {
            "tile_count": 18,
            "official_chunk_count": 9,
            "tiles_per_official_chunk": 2,
            "coefficient_plane_lane_order": STREAM_PHYSICAL_LANES,
            "f0_plane_formation_per_operand_per_tile": {"vperm2i128": 4},
            "resident_h_projection_per_tile": {"aligned_loads": 4,
                                               "vperm2i128": 4,
                                               "vpshufb": 4,
                                               "routing_total": 8},
            "serializer_inverse_projection_per_tile": {"vpshufb": 4,
                                                        "vperm2i128": 4,
                                                        "routing_total": 8},
            "zero_copy_objective": False,
        },
        "ma1_pairing_proof": {
            "native_terminal_half_pairs": [[0, 1], [2, 3]],
            "pairings": ma1_pairings,
            "minimum_operand_half_routes_per_stream": routes_per_stream,
            "streams_per_tile": 2,
            "tiles": 18,
            "full_bilinear_operand_routes": ma1_bilinear_routes,
            "resident_h_pair_projection_per_tile": {
                "output_pair_vectors": 4,
                "vpshufb": 8,
                "vperm2i128": 4,
                "routing_total": 12,
            },
        },
        "range_proof": {
            "input_center_contract": CENTERED,
            "f0_precenter_contract": "exact per-lane i16 intervals are attached to every semantic plane",
            "montgomery_product_centered_inputs": product_bound,
            "montgomery_product_pair_sums": pair_product_bound,
            "ma1": {"same_weighted_polynomial_bounds_as_ma2": True,
                    "pair-packed_lambda_vector_chains_per_tile": 4},
            "ma2_outputs": ma2_outputs,
            "ma3": {"quadratic_first_precenter": qmul_first_precenter,
                    "quadratic_second_precenter": qmul_second_precenter,
                    "cross_precenter": cross_precenter,
                    "final_outputs_precenter": ma3_final,
                    "all_preoperations_signed_i16": True},
            "proof_method": "closed integer intervals plus signed-high-half Montgomery correction bounds",
        },
        "scale_gauge_search": scale_search,
        "candidates": candidates,
        "alignment_contract": {
            "asm_entry": ".p2align 5",
            "ymm_constants": ".section .rodata plus .p2align 5",
            "poly_pointer_alignment_bytes": 32,
            "poly_pointer_evidence": "pinned poly type aligned(32); all vector offsets multiples of 32",
            "ciphertext_pointer_alignment": "unconstrained; serializer byte stores remain vmovdqu",
            "p2align6": "placement-only variant requiring paired evidence",
            "linked_elf_audit": ["section alignment", "symbol mod32/mod64",
                                 "padding", "text/rodata size", "ELF SHA-256"],
        },
        "source_sha256": {
            "consumer_map": sha256(args.consumer_map),
            "synthesis": sha256(args.synthesis),
            "poly.h": sha256(args.poly_header),
            "pack.s": sha256(args.pack_source),
            "basemul.s": sha256(args.basemul_source),
        },
    }
    output(args.output, document, args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
