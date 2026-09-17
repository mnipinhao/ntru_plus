#!/usr/bin/env python3
"""Generate the P3 native-component-consumer feasibility ledger.

This is deliberately a representation and machine-budget oracle, not a code
generator.  It proves the T_d ownership maps and the exact boundary networks
that are already available, then separates executable candidate families from
ideas that still need a 32-bit reduction schedule.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Optional


BRANCHES = 2
ROWS = 9
Q_LANES = 16
TILES = BRANCHES * ROWS


Token = tuple[int, int]
Lane = Optional[Token]
Vector = list[Lane]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, document: dict, check: bool) -> None:
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if check:
        if not path.is_file() or path.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"generated file is stale: {path}")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")


def packed_vectors(degree: int) -> list[list[Token]]:
    words = [(q, j) for q in range(Q_LANES) for j in range(degree)]
    return [words[offset:offset + 16] for offset in range(0, len(words), 16)]


def plane_vectors(degree: int) -> list[list[Token]]:
    return [[(q, j) for q in range(Q_LANES)] for j in range(degree)]


def halves(vector: list[Token]) -> tuple[list[Token], list[Token]]:
    if len(vector) != 16:
        raise SystemExit("bad vector width")
    return vector[:8], vector[8:]


def pair_halves(low: list[Token], high: list[Token]) -> list[Token]:
    if len(low) != 8 or len(high) != 8:
        raise SystemExit("bad 128-bit half width")
    return low + high


def masked_shuffle(source: Vector, desired: list[Token]) -> Vector:
    """Model one lane-local vpshufb with zeroing bytes.

    The desired vector is only used as an ownership target.  A token is
    selected when it exists in the same 128-bit source half; all other output
    words are zeroed.
    """
    output: Vector = [None] * 16
    for half in range(2):
        source_half = source[8 * half:8 * (half + 1)]
        for lane in range(8):
            token = desired[8 * half + lane]
            if token in source_half:
                output[8 * half + lane] = token
    return output


def merge_masked(parts: list[Vector], desired: list[Token]) -> list[Token]:
    output: list[Token] = []
    for lane, token in enumerate(desired):
        owners = [part[lane] for part in parts if part[lane] is not None]
        if owners != [token]:
            raise SystemExit(f"masked network collision/hole at lane {lane}: {owners}/{token}")
        output.append(token)
    return output


def unpack(a: list[Token], b: list[Token], words: int, high: bool) -> list[Token]:
    output: list[Token] = []
    for half in range(2):
        aa = a[8 * half:8 * (half + 1)]
        bb = b[8 * half:8 * (half + 1)]
        start = 4 if high else 0
        for index in range(start, start + 4, words):
            output.extend(aa[index:index + words])
            output.extend(bb[index:index + words])
    if len(output) != 16:
        raise SystemExit("bad unpack network width")
    return output


def permq_d8(vector: list[Token]) -> list[Token]:
    qwords = [vector[4 * index:4 * (index + 1)] for index in range(4)]
    return sum((qwords[index] for index in (0, 2, 1, 3)), [])


def d4_aos_to_planes() -> tuple[list[list[Token]], dict]:
    vectors = packed_vectors(4)
    a0 = unpack(vectors[0], vectors[1], 1, False)
    a1 = unpack(vectors[0], vectors[1], 1, True)
    a2 = unpack(vectors[2], vectors[3], 1, False)
    a3 = unpack(vectors[2], vectors[3], 1, True)
    b0 = unpack(a0, a1, 2, False)
    b1 = unpack(a0, a1, 2, True)
    b2 = unpack(a2, a3, 2, False)
    b3 = unpack(a2, a3, 2, True)
    result = [
        permq_d8(unpack(b0, b2, 4, False)),
        permq_d8(unpack(b0, b2, 4, True)),
        permq_d8(unpack(b1, b3, 4, False)),
        permq_d8(unpack(b1, b3, 4, True)),
    ]
    for j, vector in enumerate(result):
        if sorted(vector) != plane_vectors(4)[j]:
            raise SystemExit("d4 forward network is not a coefficient plane")
    return result, {
        "vpunpckwd": 4,
        "vpunpckdq": 4,
        "vpunpckqdq": 4,
        "vpermq": 4,
        "routing_total": 16,
    }


def d4_planes_to_aos() -> tuple[list[list[Token]], dict]:
    planes = plane_vectors(4)
    t0 = unpack(planes[0], planes[1], 1, False)
    t1 = unpack(planes[0], planes[1], 1, True)
    t2 = unpack(planes[2], planes[3], 1, False)
    t3 = unpack(planes[2], planes[3], 1, True)
    u0 = unpack(t0, t2, 2, False)
    u1 = unpack(t0, t2, 2, True)
    u2 = unpack(t1, t3, 2, False)
    u3 = unpack(t1, t3, 2, True)
    result = [u0[:8] + u1[:8], u2[:8] + u3[:8],
              u0[8:] + u1[8:], u2[8:] + u3[8:]]
    if result != packed_vectors(4):
        raise SystemExit("d4 inverse network is not exact")
    return result, {
        "vpunpckwd": 4,
        "vpunpckdq": 4,
        "vperm2i128": 4,
        "routing_total": 12,
        "runtime_baseline": False,
    }


def d3_packed_to_planes() -> tuple[list[list[Token]], dict]:
    vectors = packed_vectors(3)
    source_halves = [half for vector in vectors for half in halves(vector)]
    # Pair q=0..7 source fragments with their q=8..15 counterparts.  These
    # three pairs are the three vperm2i128 inputs to nine masked shuffles.
    paired = [pair_halves(source_halves[0], source_halves[3]),
              pair_halves(source_halves[1], source_halves[4]),
              pair_halves(source_halves[2], source_halves[5])]
    result = []
    for desired in plane_vectors(3):
        result.append(merge_masked([masked_shuffle(source, desired)
                                    for source in paired], desired))
    if result != plane_vectors(3):
        raise SystemExit("d3 packed-to-plane network is not exact")
    return result, {
        "vperm2i128": 3,
        "vpshufb": 9,
        "vpor": 6,
        "routing_total": 18,
    }


def d3_planes_to_packed() -> tuple[list[list[Token]], dict]:
    planes = plane_vectors(3)
    packed = packed_vectors(3)
    packed_halves = [half for vector in packed for half in halves(vector)]
    # Build (S0,S3), (S1,S4), (S2,S5) in parallel.  Each vector uses three
    # masked lane-local shuffles and two ORs.  Three vperm2i128 operations then
    # reassemble (S0,S1), (S2,S3), (S4,S5).
    half_pairs = [(0, 3), (1, 4), (2, 5)]
    temporary = []
    for low_index, high_index in half_pairs:
        desired = pair_halves(packed_halves[low_index], packed_halves[high_index])
        temporary.append(merge_masked([masked_shuffle(plane, desired)
                                       for plane in planes], desired))
    result = [temporary[0][:8] + temporary[1][:8],
              temporary[2][:8] + temporary[0][8:],
              temporary[1][8:] + temporary[2][8:]]
    if result != packed:
        raise SystemExit("d3 plane-to-packed network is not exact")
    return result, {
        "vpshufb": 9,
        "vpor": 6,
        "vperm2i128": 3,
        "routing_total": 18,
        "runtime_baseline": False,
    }


def ownership(degree: int) -> list[dict]:
    cells = []
    for branch in range(BRANCHES):
        for row in range(ROWS):
            for q in range(Q_LANES):
                for j in range(degree):
                    word = degree * q + j
                    cells.append({
                        "owner": {"branch": branch, "p_row": row, "q": q, "j": j},
                        "tile": f"T{degree}.b{branch}.p{row}",
                        "native": {"vector": word // 16, "lane": word % 16},
                        "plane": {"vector": j, "lane": q},
                    })
    expected = BRANCHES * ROWS * Q_LANES * degree
    if len(cells) != expected:
        raise SystemExit("incomplete T_d ownership")
    return cells


def d4_report(aos_schedule: Path) -> dict:
    schedule = json.loads(aos_schedule.read_text(encoding="utf-8"))
    selected = schedule["step_C_networks"]["C1_live_d1_to_transpose"]
    if selected["per_tile"]["routing_total"] != 32:
        raise SystemExit("selected 1152 C1 route ledger changed")
    _, forward = d4_aos_to_planes()
    _, constructive_inverse = d4_planes_to_aos()
    return {
        "parameter": 1152,
        "degree": 4,
        "native_tile": "four YMM; each YMM contains four q components x four j words",
        "actual_selected_boundary": {
            "forward_native_to_plane_routes_per_tile": forward["routing_total"],
            "forward_native_to_plane_routes_full": forward["routing_total"] * TILES,
            "plane_basemul_to_inverse_conversion_routes": 0,
            "reason": "the selected coefficient-plane component ABI is already an inverse-native semantic input",
            "credit_available_to_P3_per_tile": forward["routing_total"],
        },
        "constructive_but_not_current_runtime": {
            "plane_to_aos": constructive_inverse,
            "warning": "do not add this 12-route network to the available credit; P^-1 is not executed by the selected baseline",
        },
        "candidate_families": [
            {
                "id": "D4-FULL-TRANSPOSE-WRAPPER",
                "base_field_chains_per_tile": 19,
                "input_routes_per_tile": 16,
                "output_abi": "coefficient planes",
                "decision": "reject",
                "reason": "exactly recreates the existing P before unchanged MA2/BaseMul arithmetic",
            },
            {
                "id": "D4-QLOCAL-BROADCAST",
                "q_packets_per_tile": 4,
                "montgomery_chains_per_tile": 76,
                "input_broadcast_routes_per_tile": 32,
                "minimum_output_pack_routes_per_tile": 12,
                "routing_total_per_tile": 44,
                "decision": "reject",
                "reason": "four-q SIMD duplicates each coefficient product across a component; +57 chains and +28 routes before inverse pricing",
            },
            {
                "id": "D4-PACKED-FOUR-PRODUCT",
                "base_product_chains_per_tile": 16,
                "b_rotation_vpshufb_per_tile": 12,
                "weighted_wrap_chains_lower_bound": 4,
                "montgomery_chains_lower_bound": 20,
                "output_aggregation_routes_lower_bound": 4,
                "routing_lower_bound": 16,
                "decision": "stop_before_asm",
                "reason": "even the optimistic lower bound only ties the 16-route deleted P and already adds one Montgomery chain; an exact aggregation/inverse schedule could only worsen or, at best, tie this family",
            },
            {
                "id": "D4-VPMADDWD-32",
                "decision": "separate_arithmetic_research_only",
                "reason": "may change the product/reduction cost model, but has no exact signed-32 modular reduction, range, scale, or inverse-handoff schedule yet",
            },
        ],
        "p3_asm_authorized": False,
        "next_reopen_condition": "a non-q-local bilinear schedule must beat 16 routes per tile including output aggregation, add no uncompensated multiplication chains, and price the AoS inverse first stage against the current plane inverse",
    }


def d3_report() -> dict:
    _, forward = d3_packed_to_planes()
    _, constructive_inverse = d3_planes_to_packed()
    return {
        "parameter": 864,
        "degree": 3,
        "native_tile": "three YMM containing one contiguous q-major,j-minor 48-word macro-tile",
        "actual_selected_boundary": {
            "forward_native_to_plane_routes_per_tile": forward["routing_total"],
            "forward_native_to_plane_routes_full": forward["routing_total"] * TILES,
            "plane_basemul_to_inverse_conversion_routes": 0,
            "credit_available_to_P3_per_tile": forward["routing_total"],
            "network": forward,
        },
        "constructive_but_not_current_runtime": {
            "plane_to_packed": constructive_inverse,
            "warning": "this proves representation feasibility only; the selected baseline does not pay P^-1",
        },
        "candidate_families": [
            {
                "id": "D3-FULL-DEINTERLEAVE-WRAPPER",
                "montgomery_chains_per_tile": 11,
                "input_routes_per_tile": 18,
                "decision": "reject",
                "reason": "moves the exact packed-to-plane network inside BaseMul and removes no work",
            },
            {
                "id": "D3-QLOCAL-16BIT",
                "decision": "reject",
                "reason": "48-bit components cross 64/128-bit boundaries; a q-local coefficient broadcast is not a uniform three-YMM SIMD schedule and falls back to the full deinterleave",
            },
            {
                "id": "D3-VPMADDWD-PAIR-SUM",
                "candidate_pair_sums": ["a1*b2+a2*b1", "a0*b1+a1*b0", "a0*b2+a2*b0"],
                "remaining_single_products": ["a0*b0", "a1*b1", "a2*b2"],
                "remaining_fixed_zeta_products": 2,
                "decision": "separate_arithmetic_research_only",
                "reason": "the packed geometry exposes real paired products, but no exact 32-bit modular-reduction and repacking schedule yet proves routing below the 18-route deleted P",
            },
        ],
        "p3_asm_authorized": False,
        "next_reopen_condition": "an exact vpmaddwd plus signed-32 reduction/repack schedule must beat the 18-route input boundary after counting all cross-half triple alignment and inverse-entry work",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parameter", type=int, choices=(864, 1152), required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--basemul-source", type=Path, required=True)
    parser.add_argument("--invntt-source", type=Path, required=True)
    parser.add_argument("--aos-schedule", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    degree = 3 if args.parameter == 864 else 4
    model = json.loads(args.model.read_text(encoding="utf-8"))
    if (model.get("parameter"), model.get("component_degree"), model.get("lanes")) != (
            args.parameter, degree, Q_LANES):
        raise SystemExit("shared GT9x16 model no longer matches P3")
    basemul = args.basemul_source.read_text(encoding="utf-8")
    invntt = args.invntt_source.read_text(encoding="utf-8")
    if ".global poly_basemul" not in basemul or ".global poly_invntt_scale" not in invntt:
        raise SystemExit("pinned BaseMul/inverse source identity changed")
    if args.parameter == 1152:
        if args.aos_schedule is None:
            raise SystemExit("1152 requires --aos-schedule")
        parameter_report = d4_report(args.aos_schedule)
    else:
        parameter_report = d3_report()

    document = {
        "schema": "gt9x16-native-component-consumer/v1",
        "checkpoint": "P3-NATIVE-COMPONENT-CONSUMER-A",
        "question": "can BaseMul(+Add) consume T_d and return an inverse-native T_d without merely relocating P?",
        "common_contract": {
            "semantic_owner": "(branch,p_row,q,j)",
            "tiles": TILES,
            "q_lanes": Q_LANES,
            "degree": degree,
            "words_per_tile": Q_LANES * degree,
            "ymm_per_tile": degree,
            "input_output_scale": "unchanged",
            "montgomery_domain": "unchanged",
            "baseinv": "deferred",
        },
        "accounting_correction": {
            "P_runtime": "present at the forward-native to coefficient-plane boundary",
            "P_inverse_runtime": "zero in the selected current pipeline",
            "rule": "only instructions actually executed by the baseline are available as structural credit",
        },
        "parameter_report": parameter_report,
        "ownership_cells": ownership(degree),
        "source_sha256": {
            "model": sha256(args.model),
            "pinned_basemul_s": sha256(args.basemul_source),
            "pinned_invntt_s": sha256(args.invntt_source),
            **({"prod3_aos_schedule": sha256(args.aos_schedule)}
               if args.aos_schedule is not None else {}),
        },
        "decision": {
            "linked_asm_authorized": False,
            "benchmark_authorized": False,
            "p2_wavefront_opened": False,
            "reason": "the exact 16-bit candidate families do not beat the actual one-sided conversion boundary; vpmaddwd changes arithmetic and still lacks an exact reduction/repack schedule",
        },
    }
    write(args.output, document, args.check)
    print(f"P3-A {args.parameter} passed: T{degree} ownership exact; no linked ASM authorized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
