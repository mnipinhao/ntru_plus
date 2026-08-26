#!/usr/bin/env python3
"""Generate the exact D1-output to MA2-native coefficient-plane map."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


P_ORDER = [0, 3, 6, 1, 4, 7, 8, 2, 5]
PLANE_LANES = list(range(0, 16, 2)) + list(range(1, 16, 2))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def output(path: Path, document: dict, check: bool) -> None:
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if check:
        if not path.is_file() or path.read_text() != rendered:
            raise SystemExit(f"generated file is stale: {path}")
    else:
        path.write_text(rendered)


def full_ma2_body(source: str) -> str:
    begin_marker = "ntruplus1152_exp001_f0_ma2_full:"
    end_marker = ".size ntruplus1152_exp001_f0_ma2_full"
    if begin_marker not in source or end_marker not in source:
        raise SystemExit("missing complete MA2 symbol in generated assembly")
    begin = source.index(begin_marker)
    end = source.index(end_marker, begin)
    return source[begin:end]


def aligned_loads(body: str, register: str) -> int:
    return len(re.findall(
        rf"^\s*vmovdqa ymm\d+, YMMWORD PTR \[{register}[^\]]*\]",
        body, re.M))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--consumer-map", type=Path, required=True)
    parser.add_argument("--ma2-schedule", type=Path, required=True)
    parser.add_argument("--prod1-schedule", type=Path, required=True)
    parser.add_argument("--ma2-contract", type=Path, required=True)
    parser.add_argument("--ma2-audit", type=Path, required=True)
    parser.add_argument("--ma2-asm", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    consumer = json.loads(args.consumer_map.read_text())
    ma2 = json.loads(args.ma2_schedule.read_text())
    prod1 = json.loads(args.prod1_schedule.read_text())
    contract = json.loads(args.ma2_contract.read_text())
    audit = json.loads(args.ma2_audit.read_text())
    asm_text = args.ma2_asm.read_text()

    if consumer["schema"] != "gt-f0-ma-consumer-map/v1":
        raise SystemExit("wrong F0 consumer-map schema")
    if ma2["schema"] != "gt-f0-ma-schedule/v1":
        raise SystemExit("wrong MA2 schedule schema")
    if prod1["schema"] != "gt-f0-prod1-schedule/v1":
        raise SystemExit("wrong PROD1 schedule schema")
    if contract["schema"] != "gt-f0-ma2-asm/v1":
        raise SystemExit("wrong MA2 assembly contract schema")
    if audit["schema"] != "gt-f0-ma2-audit/v1":
        raise SystemExit("wrong MA2 audit schema")
    frozen = consumer["frozen_semantic_contract"]
    if frozen["physical_p_order"] != P_ORDER:
        raise SystemExit("physical P order changed")
    if frozen["transform_scale"] != 4 or frozen["montgomery_r_exponent"] != 0:
        raise SystemExit("F0 scale contract changed")
    if prod1["arithmetic_schedule"]["final_materialized_vectors"] != 72:
        raise SystemExit("PROD1 D1 vector count changed")
    if not prod1["range_proof"]["all_intermediate_ranges_signed_i16"]:
        raise SystemExit("PROD1 range proof is not closed")
    if not ma2["range_proof"]["ma3"]["all_preoperations_signed_i16"]:
        raise SystemExit("MA schedule signed-i16 proof changed")
    if contract["representation"] != "fixed coefficient, 16 physical-q leaves per YMM":
        raise SystemExit("MA2 coefficient-plane ABI changed")
    if audit["variants"]["FULL"]["movement"]["f0_r_formation"]["vperm2i128"] != 72:
        raise SystemExit("actual MA2 r-plane formation changed")
    if audit["variants"]["FULL"]["movement"]["f0_m_formation"]["vperm2i128"] != 72:
        raise SystemExit("actual MA2 m-plane formation changed")

    tile_records = {}
    for tile in ma2["semantic_tiles"]:
        key = (tile["tile"]["branch"], tile["tile"]["p"])
        tile_records[key] = tile
    chunk_sides = {}
    for chunk in ma2["official_chunk_pairing"]:
        for index, tile in enumerate(chunk["semantic_tiles"]):
            chunk_sides[(tile["branch"], tile["p"])] = {
                "serializer_chunk": chunk["official_chunk"],
                "tile_index_in_chunk": index,
                "tile_side": "A" if index == 0 else "B",
            }
    if len(tile_records) != 18 or len(chunk_sides) != 18:
        raise SystemExit("MA2 tile/chunk ownership is incomplete")

    vector_by_index = {vector["vector_index"]: vector
                       for vector in consumer["f0_vectors"]}
    if set(vector_by_index) != set(range(72)):
        raise SystemExit("D1 output vectors are not a 72-vector bijection")

    cells = []
    planes = []
    destination_cells = set()
    semantic_cells = set()
    source_cells = set()
    p2a_exact_vector_matches = 0
    for branch in range(2):
        for physical_row, p in enumerate(P_ORDER):
            tile = tile_records[(branch, p)]
            side = chunk_sides[(branch, p)]
            for coefficient in range(4):
                pair = coefficient // 2
                coefficient_half = coefficient % 2
                source_indices = [(((branch * 9 + physical_row) * 2 + pair) * 2) + stream
                                  for stream in range(2)]
                destination_vector = (branch * 9 + physical_row) * 4 + coefficient
                destination_owners = []
                plane_cells = []
                for stream, source_index in enumerate(source_indices):
                    vector = vector_by_index[source_index]
                    selected = vector["lanes"][coefficient_half * 8:(coefficient_half + 1) * 8]
                    for source_lane, lane in enumerate(selected,
                                                       start=coefficient_half * 8):
                        owner = lane["semantic_owner"]
                        destination_lane = stream * 8 + source_lane - coefficient_half * 8
                        if owner != {"branch": branch, "p": p,
                                     "q": owner["q"],
                                     "terminal_coefficient": coefficient}:
                            raise SystemExit("source owner does not match destination plane")
                        if lane["physical_q_lane"] != PLANE_LANES[destination_lane]:
                            raise SystemExit("MA2 plane lane order changed")
                        source_key = (source_index, source_lane)
                        destination_key = (destination_vector, destination_lane)
                        semantic_key = (branch, p, owner["q"], coefficient)
                        source_cells.add(source_key)
                        destination_cells.add(destination_key)
                        semantic_cells.add(semantic_key)
                        destination_owners.append(semantic_key)
                        cell = {
                            "producer": {
                                "branch": branch, "physical_p_row": physical_row,
                                "p": p, "terminal_pair": pair, "stream": stream,
                                "d1_vector": source_index, "d1_packed_lane": source_lane,
                                "physical_q_lane": lane["physical_q_lane"],
                            },
                            "semantic_owner": owner,
                            "consumer": {
                                **side, "coefficient_plane": coefficient,
                                "ma2_native_vector": destination_vector,
                                "ma2_native_packed_lane": destination_lane,
                            },
                            "range_i16": lane["exact_f0_range_i16"],
                            "scale": {"transform": 4, "montgomery_r_exponent": 0},
                        }
                        cells.append(cell)
                        plane_cells.append(cell)
                source_owner_sets = [
                    {(lane["semantic_owner"]["branch"], lane["semantic_owner"]["p"],
                      lane["semantic_owner"]["q"],
                      lane["semantic_owner"]["terminal_coefficient"])
                     for lane in vector_by_index[index]["lanes"]}
                    for index in source_indices
                ]
                if any(owners == set(destination_owners) for owners in source_owner_sets):
                    p2a_exact_vector_matches += 1
                expected_positions = next(
                    plane["f0_positions_i16"] for plane in tile["planes"]
                    if plane["coefficient"] == coefficient)
                actual_positions = [
                    cell["producer"]["d1_vector"] * 16 +
                    cell["producer"]["d1_packed_lane"] for cell in plane_cells]
                if actual_positions != expected_positions:
                    raise SystemExit("producer/MA2 schedule source positions disagree")
                planes.append({
                    "branch": branch, "physical_p_row": physical_row, "p": p,
                    **side, "coefficient_plane": coefficient,
                    "ma2_native_vector": destination_vector,
                    "ma2_native_byte_offset": destination_vector * 32,
                    "source_d1_vectors": source_indices,
                    "source_halves": ["low128" if coefficient_half == 0 else "high128"] * 2,
                    "formation": {
                        "opcode": "vperm2i128", "immediate": "0x20" if coefficient_half == 0 else "0x31",
                        "instructions": 1,
                    },
                    "source_and_destination_slot_set_equal": (
                        set(source_indices) == {destination_vector - coefficient_half,
                                                destination_vector - coefficient_half + 1}),
                })

    if len(cells) != len(source_cells) or len(cells) != len(destination_cells):
        raise SystemExit("source or destination cell map is not injective")
    if len(cells) != 1152 or len(semantic_cells) != 1152:
        raise SystemExit("PROD2 semantic map is not a 1,152-cell bijection")
    if p2a_exact_vector_matches != 0:
        raise SystemExit("P2-A unexpectedly found an exact whole-vector store")
    if not all(plane["source_and_destination_slot_set_equal"] for plane in planes):
        raise SystemExit("P2-B cannot reuse the in-place terminal-pair slots")

    body = full_ma2_body(asm_text)
    actual_r_loads = aligned_loads(body, "rsi")
    actual_m_loads = aligned_loads(body, "rdx")
    if (actual_r_loads, actual_m_loads) != (144, 144):
        raise SystemExit(
            f"actual MA2 generic-F0 load geometry changed: {actual_r_loads}/{actual_m_loads}")
    native_plane_loads = len(planes)
    if native_plane_loads != 72:
        raise SystemExit("expected 72 MA2-native plane loads per operand")

    per_operand_control = {
        "top_split_loads": 144,
        "formation_cross_lane_ops": 576,
        "d1_output_stores": 72,
        "generic_f0_loads_into_ma2": 144,
        "f0_to_plane_permutations": 72,
        "producer_local_plane_permutations": 0,
        "ma2_native_plane_reloads": 0,
    }
    per_operand_p2b = {
        "top_split_loads": 144,
        "formation_cross_lane_ops": 576,
        "d1_output_stores": 72,
        "generic_f0_loads_into_ma2": 0,
        "f0_to_plane_permutations": 0,
        "producer_local_plane_permutations": 72,
        "ma2_native_plane_reloads": 72,
    }
    delta = {key: per_operand_p2b[key] - per_operand_control[key]
             for key in per_operand_control}

    min_range = min(cell["range_i16"][0] for cell in cells)
    max_range = max(cell["range_i16"][1] for cell in cells)
    document = {
        "schema": "gt-f0-prod2-ma2-map/v1",
        "checkpoint": "F0-PROD2-MA2-MAP",
        "parameter": 1152,
        "frozen_contract": {
            "top_split_arithmetic": "unchanged",
            "r2_d1_arithmetic_and_order": "unchanged F0-PROD1",
            "physical_p_order": P_ORDER,
            "ma2_plane_lane_order": PLANE_LANES,
            "transform_scale": 4,
            "montgomery_r_exponent": 0,
            "boundary": "materialized MA2-native coefficient planes",
            "live_d1_to_ma2_fusion": False,
        },
        "d1_to_ma2_cells": cells,
        "ma2_native_planes": planes,
        "bijection_proof": {
            "d1_source_cells": len(source_cells),
            "ma2_destination_cells": len(destination_cells),
            "semantic_owners": len(semantic_cells),
            "all_equal_1152": len(source_cells) == len(destination_cells) == len(semantic_cells) == 1152,
            "plane_count": len(planes),
            "serializer_chunks": len({plane["serializer_chunk"] for plane in planes}),
            "tiles": len({(plane["branch"], plane["p"]) for plane in planes}),
        },
        "range_and_scale_proof": {
            "exact_global_i16_envelope": [min_range, max_range],
            "values_unchanged_by_permutation": True,
            "all_cells_signed_i16": min_range >= -32768 and max_range <= 32767,
            "ma2_preoperation_proof_reused": True,
            "extra_reductions": 0,
        },
        "realization_search": {
            "P2-A-store-address-only": {
                "feasible": False,
                "whole_d1_vectors_matching_one_ma2_plane": p2a_exact_vector_matches,
                "reason": "each D1 vector contains two coefficient halves; each MA2 plane needs both q-parity streams for one coefficient",
            },
            "P2-B-local-d1-epilogue": {
                "feasible": True,
                "selected": True,
                "vperm2i128_per_plane": 1,
                "vperm2i128_per_tile": 4,
                "vperm2i128_per_forward": 72,
                "aligned_plane_stores_per_forward": 72,
                "extra_temporary_bytes": 0,
                "same_pair_slots_overwritten_after_both_sources_are_live": True,
            },
            "P2-C-chunk-oriented-schedule": {
                "feasible": True,
                "selected": False,
                "movement_delta_vs_P2-B": 0,
                "status": "deferred; changes the frozen producer traversal without removing another movement class",
            },
        },
        "transient_storage": {
            "backing_bytes": 2304,
            "r2_first_can_reuse_ma2_native_backing": True,
            "method": "the two generic stream slots of each terminal pair are overwritten by the two coefficient-plane slots of the same pair only after both D1 sources are live",
            "additional_transient_bytes": 0,
            "zero_copy_objective": False,
        },
        "movement_accounting": {
            "unit": "dynamic vector instructions per forward operand, excluding unchanged arithmetic",
            "P1-H-generic-F0-to-current-MA2": per_operand_control,
            "PROD2-P2-B-to-MA2-native": per_operand_p2b,
            "P2-B-minus-control": delta,
            "two_forward_operands_delta": {key: 2 * value for key, value in delta.items()},
            "net_boundary_instruction_delta_per_operand": sum(delta.values()),
            "net_boundary_instruction_delta_two_operands": 2 * sum(delta.values()),
            "interpretation": "P2-B removes 72 duplicated generic-F0 loads per operand; 72 plane permutations move from MA2 into the producer epilogue and plane reloads replace half of the former generic loads",
        },
        "decision": {
            "map_complete": True,
            "selected_realization": "P2-B-local-d1-epilogue",
            "asm0_authorized": True,
            "kem_benchmark_authorized": False,
            "resident_h_changes_authorized": False,
            "top_split_fusion_authorized": False,
            "reason": "exact materialized realization removes 72 loads per operand with no new buffer, but must pass producer-consumer differential and linked movement audit before KEM pricing",
        },
        "source_sha256": {key: sha256(path) for key, path in {
            "consumer_map": args.consumer_map,
            "ma2_schedule": args.ma2_schedule,
            "prod1_schedule": args.prod1_schedule,
            "ma2_contract": args.ma2_contract,
            "ma2_audit": args.ma2_audit,
            "ma2_asm": args.ma2_asm,
        }.items()},
    }
    output(args.output, document, args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
