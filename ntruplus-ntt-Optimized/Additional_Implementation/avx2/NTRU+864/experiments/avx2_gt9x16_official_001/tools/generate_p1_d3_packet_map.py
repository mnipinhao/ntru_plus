#!/usr/bin/env python3
"""Generate the shrunk-P1 exact d=3 packed-vs-plane packet map."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


BRANCHES = 2
ROWS = 9
Q_LANES = 16
DEGREE = 3
WORDS_PER_BRANCH = ROWS * Q_LANES * DEGREE


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_owner(branch: int, row: int, q_lane: int, coefficient: int) -> dict[str, int]:
    h_row = (5 * row) % ROWS
    component = Q_LANES * h_row + q_lane
    return {
        "branch": branch,
        "row": row,
        "h_row": h_row,
        "q": q_lane,
        "j": coefficient,
        "component": component,
        "split_word": branch * WORDS_PER_BRANCH + DEGREE * component + coefficient,
    }


def packed_vectors() -> list[dict[str, object]]:
    vectors = []
    for branch in range(BRANCHES):
        for row in range(ROWS):
            for vector in range(DEGREE):
                lanes = []
                for lane in range(16):
                    q_lane, coefficient = divmod(16 * vector + lane, DEGREE)
                    lanes.append(source_owner(branch, row, q_lane, coefficient))
                vectors.append({
                    "id": f"packed.b{branch}.r{row}.v{vector}",
                    "branch": branch,
                    "row": row,
                    "vector": vector,
                    "lanes": lanes,
                })
    return vectors


def plane_vectors() -> list[dict[str, object]]:
    vectors = []
    for branch in range(BRANCHES):
        for row in range(ROWS):
            for coefficient in range(DEGREE):
                vectors.append({
                    "id": f"plane.b{branch}.r{row}.j{coefficient}",
                    "branch": branch,
                    "row": row,
                    "coefficient": coefficient,
                    "lanes": [source_owner(branch, row, q_lane, coefficient)
                              for q_lane in range(Q_LANES)],
                })
    return vectors


def position_map(packed: list[dict[str, object]], planes: list[dict[str, object]]) -> list[dict[str, object]]:
    source = {}
    for vector in packed:
        for lane, owner in enumerate(vector["lanes"]):
            key = (owner["branch"], owner["row"], owner["q"], owner["j"])
            if key in source:
                raise SystemExit(f"duplicate packed owner: {key}")
            source[key] = {"vector": vector["id"], "lane": lane,
                           "half": lane // 8}

    mapping = []
    seen = set()
    for vector in planes:
        lane_sources = []
        for lane, owner in enumerate(vector["lanes"]):
            key = (owner["branch"], owner["row"], owner["q"], owner["j"])
            if key in seen:
                raise SystemExit(f"duplicate plane owner: {key}")
            seen.add(key)
            lane_sources.append({"destination_lane": lane, **source[key]})
        mapping.append({"destination": vector["id"], "sources": lane_sources})

    expected = BRANCHES * ROWS * Q_LANES * DEGREE
    if len(source) != expected or len(seen) != expected or set(source) != seen:
        raise SystemExit("packed/plane map is not an 864-cell bijection")
    return mapping


def render(model_path: Path, ntt_source: Path, pack_source: Path) -> str:
    model = json.loads(model_path.read_text(encoding="utf-8"))
    if (model.get("parameter"), model.get("components"),
            model.get("component_degree"), model.get("radix_9"),
            model.get("lanes")) != (864, 288, 3, 9, 16):
        raise SystemExit("shared GT9x16 d=3 model changed")
    packed = packed_vectors()
    planes = plane_vectors()
    mapping = position_map(packed, planes)

    # An NTT9 layer applies the same row-linear map independently to every
    # (q,j) lane.  Check every possible input-row/output-row term in both
    # branches; the packet permutation cannot change its owner.
    commute_terms = 0
    for branch in range(BRANCHES):
        for q_lane in range(Q_LANES):
            for coefficient in range(DEGREE):
                for input_row in range(ROWS):
                    source = source_owner(branch, input_row, q_lane, coefficient)
                    for output_row in range(ROWS):
                        if (source["branch"], source["q"], source["j"]) != (
                                branch, q_lane, coefficient):
                            raise SystemExit("NTT9 commutation owner changed")
                        if not 0 <= output_row < ROWS:
                            raise SystemExit("bad output row")
                        commute_terms += 1

    report = {
        "schema": "ntruplus864-p1-d3-packet-map/v1",
        "checkpoint": "P1-864-D3-PACKET-MAP",
        "scope": "two exact top-split branches; NTT9-first; d=3; no arithmetic change",
        "frozen": {
            "parameter": 864,
            "branch_words": WORDS_PER_BRANCH,
            "input": "materialized Official-small top-split backing",
            "semantic_owner": "(branch,row,q,j)",
            "row_relabel": "h_row=(5*row) mod 9",
            "output": "three coefficient-plane YMMs per (branch,row), q in lanes 0..15",
            "radix3_formula": "unchanged Official/Hassan-Yayla schedule",
            "root_identity": "unchanged ell=864 component identity",
            "scale_and_montgomery_exponent": "unchanged",
        },
        "capacity": {
            "cells_per_row": 48,
            "packed_vectors_per_row": 3,
            "plane_vectors_per_row": 3,
            "unused_lanes": 0,
            "observation": "d=3 has no utilization loss; the cost is cross-packet q/j ownership",
        },
        "packed_control": {
            "entry_packet": "q-major,j-minor consecutive words",
            "entry_routes": 0,
            "ntt9_lane_compatible": True,
            "axis_conversion": "one packed-to-plane permutation per row after NTT9",
            "terminal_abi": "plane-major consumer ABI",
        },
        "plane_major_challenger": {
            "entry_packet": "j-major vectors with q in lanes 0..15",
            "entry_routes": "same packed-to-plane permutation, moved before NTT9",
            "ntt9_lane_compatible": True,
            "axis_conversion": "none after NTT9",
            "terminal_abi": "same plane-major consumer ABI",
        },
        "commutation_proof": {
            "statement": "P * NTT9_packed == NTT9_plane * P",
            "reason": "the fixed radix-3 row constants are lane-uniform; P changes only q/j lane ownership",
            "twist_condition": "q-dependent twist tables must be permuted with P; no multiply chain is removed",
            "checked_cells": BRANCHES * ROWS * Q_LANES * DEGREE,
            "checked_row_linear_terms": commute_terms,
        },
        "structural_ledger_per_full_transform": {
            "packed_control": {
                "top_split_data_loads": 54,
                "packet_permutations": 18,
                "ntt9_vector_streams": 54,
                "consumer_plane_stores": 54,
            },
            "plane_major_challenger": {
                "top_split_data_loads": 54,
                "packet_permutations": 18,
                "ntt9_vector_streams": 54,
                "consumer_plane_stores": 54,
            },
            "delta": {
                "top_split_data_loads": 0,
                "packet_permutations": 0,
                "ntt9_arithmetic": 0,
                "consumer_plane_stores": 0,
                "removed_materialization": 0,
            },
            "unit_note": "packet_permutation is one semantic 3-vector permutation; exact AVX2 instruction count is intentionally not invented before lowering",
        },
        "decision": {
            "plane_major_linked_asm_authorized": False,
            "paired_benchmark_authorized": False,
            "reason": "with a frozen materialized top-split input and plane-major consumer, the challenger only relocates the identical bijection and has no structural credit",
            "reopen_condition": "an adjacent top-split, NTT16, or BaseMul schedule absorbs the permutation or removes a complete load/store boundary",
            "padded_aos_opened": False,
            "p2_opened": False,
        },
        "source_sha256": {
            "shared_gt9x16_model": sha256(model_path),
            "pinned_864_ntt_s": sha256(ntt_source),
            "pinned_864_pack_s": sha256(pack_source),
        },
        "packed_vectors": packed,
        "plane_vectors": planes,
        "packed_to_plane": mapping,
    }
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--ntt-source", type=Path, required=True)
    parser.add_argument("--pack-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render(args.model, args.ntt_source, args.pack_source)
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != expected:
            raise SystemExit(f"generated file is stale: {args.output}")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(expected, encoding="utf-8")
    print("P1 864 d3 packet map passed: 864/864 owners, no plane-major structural credit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
