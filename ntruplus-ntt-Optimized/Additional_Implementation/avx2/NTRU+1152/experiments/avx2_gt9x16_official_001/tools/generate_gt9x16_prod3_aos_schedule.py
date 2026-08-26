#!/usr/bin/env python3
"""Generate the staged persistent-AoS GT9x16 schedule and lane proofs."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


P_ORDER = [0, 3, 6, 1, 4, 7, 8, 2, 5]
Q_ORDER = [0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15]
WORD_SHUFFLE = [0, 2, 4, 6, 1, 3, 5, 7]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, text: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            raise SystemExit(f"generated file is stale: {path}")
    else:
        path.write_text(text, encoding="utf-8")


def vector_words(values: list[int]) -> str:
    return ", ".join(str(value) for value in values)


def aos_tile_constants(scaled: dict) -> str:
    row = scaled["paper_adjusted_ntt16_rows"][0]
    if row["physical_row"] != 0 or row["frequency_p"] != 0:
        raise SystemExit("physical row zero is no longer the ASM0 tile control")
    d2 = row["adjusted_ntt16_stages"]["distance2"]
    d1 = row["adjusted_ntt16_stages"]["distance1"]

    def repeated(values: list[int]) -> list[int]:
        return [value for value in values for _ in range(4)]

    vectors = {
        ".Lprod3_aos_q": [3457] * 16,
        ".Lprod3_aos_d2_lo_qinv": ([d2["qinv_signed"][0]] * 8 +
                                     [d2["qinv_signed"][1]] * 8),
        ".Lprod3_aos_d2_lo_zeta": ([d2["montgomery_signed"][0]] * 8 +
                                     [d2["montgomery_signed"][1]] * 8),
        ".Lprod3_aos_d2_hi_qinv": ([d2["qinv_signed"][2]] * 8 +
                                     [d2["qinv_signed"][3]] * 8),
        ".Lprod3_aos_d2_hi_zeta": ([d2["montgomery_signed"][2]] * 8 +
                                     [d2["montgomery_signed"][3]] * 8),
        ".Lprod3_aos_d1_lo_qinv": repeated(d1["qinv_signed"][:4]),
        ".Lprod3_aos_d1_lo_zeta": repeated(d1["montgomery_signed"][:4]),
        ".Lprod3_aos_d1_hi_qinv": repeated(d1["qinv_signed"][4:]),
        ".Lprod3_aos_d1_hi_zeta": repeated(d1["montgomery_signed"][4:]),
    }
    lines = [
        "/* Generated GT9X16-PROD3-AOS-ASM0 row-0 tile constants. */",
        ".section .rodata",
    ]
    for label, values in vectors.items():
        if len(values) != 16:
            raise SystemExit(f"bad generated YMM constant width for {label}")
        lines.extend((".p2align 5", f"{label}:", f"  .word {vector_words(values)}"))
    return "\n".join(lines) + "\n"


def perm2x128(a: list[tuple[int, int]], b: list[tuple[int, int]], imm: int) -> list[tuple[int, int]]:
    if imm == 0x20:
        return a[:8] + b[:8]
    if imm == 0x31:
        return a[8:] + b[8:]
    raise ValueError(f"unsupported vperm2i128 immediate {imm:#x}")


def unpack(a: list[tuple[int, int]], b: list[tuple[int, int]], words: int,
           high: bool) -> list[tuple[int, int]]:
    output = []
    for half in range(2):
        aa = a[8 * half:8 * (half + 1)]
        bb = b[8 * half:8 * (half + 1)]
        start = 4 if high else 0
        for index in range(start, start + 4, words):
            output.extend(aa[index:index + words])
            output.extend(bb[index:index + words])
    if len(output) != 16:
        raise SystemExit("bad unpack simulation")
    return output


def permq_d8(vector: list[tuple[int, int]]) -> list[tuple[int, int]]:
    qwords = [vector[4 * index:4 * (index + 1)] for index in range(4)]
    return sum((qwords[index] for index in (0, 2, 1, 3)), [])


def shuffle_words(vector: list[tuple[int, int]]) -> list[tuple[int, int]]:
    return [vector[8 * half + index] for half in range(2) for index in WORD_SHUFFLE]


def transpose_network(vectors: list[list[tuple[int, int]]]) -> list[list[tuple[int, int]]]:
    a0 = unpack(vectors[0], vectors[1], 1, False)
    a1 = unpack(vectors[0], vectors[1], 1, True)
    a2 = unpack(vectors[2], vectors[3], 1, False)
    a3 = unpack(vectors[2], vectors[3], 1, True)
    b0 = unpack(a0, a1, 2, False)
    b1 = unpack(a0, a1, 2, True)
    b2 = unpack(a2, a3, 2, False)
    b3 = unpack(a2, a3, 2, True)
    return [
        permq_d8(unpack(b0, b2, 4, False)),
        permq_d8(unpack(b0, b2, 4, True)),
        permq_d8(unpack(b1, b3, 4, False)),
        permq_d8(unpack(b1, b3, 4, True)),
    ]


def aos_after_d4() -> list[list[tuple[int, int]]]:
    return [[(q, coefficient) for q in range(base, base + 4)
             for coefficient in range(4)] for base in (0, 4, 8, 12)]


def pair_check(left: list[tuple[int, int]], right: list[tuple[int, int]],
               distance: int) -> int:
    checks = 0
    for a, b in zip(left, right):
        if a[1] != b[1] or b[0] - a[0] != distance:
            raise SystemExit(f"bad distance-{distance} AoS butterfly pair: {a}/{b}")
        checks += 1
    return checks


def c1_network() -> tuple[list[list[tuple[int, int]]], dict]:
    x0, x1, x2, x3 = aos_after_d4()

    # D2: two q-blocks fill one YMM chain; constants are repeated by 128-bit half.
    d2a0, d2b0 = perm2x128(x0, x1, 0x20), perm2x128(x0, x1, 0x31)
    d2a1, d2b1 = perm2x128(x2, x3, 0x20), perm2x128(x2, x3, 0x31)
    d2_checks = pair_check(d2a0, d2b0, 2) + pair_check(d2a1, d2b1, 2)
    # Butterfly sum/difference values retain the lower/upper semantic q owners.
    y0, y1, y2, y3 = d2a0, d2b0, d2a1, d2b1

    # D1: qword unpacks pack even and odd q owners from two D2 groups.
    d1a0, d1b0 = unpack(y0, y1, 4, False), unpack(y0, y1, 4, True)
    d1a1, d1b1 = unpack(y2, y3, 4, False), unpack(y2, y3, 4, True)
    d1_checks = pair_check(d1a0, d1b0, 1) + pair_check(d1a1, d1b1, 1)
    post_d1 = [d1a0, d1b0, d1a1, d1b1]
    aos_planes = transpose_network(post_d1)
    aos_expected = [[(q, coefficient) for q in range(16)] for coefficient in range(4)]
    if aos_planes != aos_expected:
        raise SystemExit("C0/C1 D1-to-AoS-plane transpose network is not exact")
    planes = [permq_d8(shuffle_words(vector)) for vector in aos_planes]
    packed_q = list(range(0, 16, 2)) + list(range(1, 16, 2))
    expected = [[(q, coefficient) for q in packed_q] for coefficient in range(4)]
    if planes != expected:
        raise SystemExit("C0/C1 AoS-plane to MA2 packed-lane formation is not exact")
    return planes, {
        "d2_scalar_lane_pairs_per_physical_p_row": d2_checks,
        "d1_scalar_lane_pairs_per_physical_p_row": d1_checks,
        "ma2_output_cells_per_physical_p_row": sum(map(len, planes)),
    }


def c2_early_transpose() -> tuple[list[list[tuple[int, int]]], list[int]]:
    raw = transpose_network(aos_after_d4())
    # The hierarchical network naturally emits this q order for contiguous
    # four-q input blocks.  One lane-local vpshufb per coefficient plane makes
    # the existing canonical physical-q plane ABI explicit.
    natural_order = [q for q, coefficient in raw[0] if coefficient == 0]
    planes = [shuffle_words(vector) for vector in raw]
    expected = [[(q, coefficient) for q in range(16)] for coefficient in range(4)]
    if planes != expected:
        raise SystemExit("C2 early AoS-to-plane transpose is not exact")
    return planes, natural_order


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prod3-map", type=Path, required=True)
    parser.add_argument("--scaled-oracle", type=Path, required=True)
    parser.add_argument("--paper-range", type=Path, required=True)
    parser.add_argument("--ntt9-macro", type=Path, required=True)
    parser.add_argument("--ntt16-macro", type=Path, required=True)
    parser.add_argument("--prod2-audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--asm-constants", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    prod3 = json.loads(args.prod3_map.read_text(encoding="utf-8"))
    scaled = json.loads(args.scaled_oracle.read_text(encoding="utf-8"))
    ranges = json.loads(args.paper_range.read_text(encoding="utf-8"))
    prod2 = json.loads(args.prod2_audit.read_text(encoding="utf-8"))
    ntt9_text = args.ntt9_macro.read_text(encoding="utf-8")
    ntt16_text = args.ntt16_macro.read_text(encoding="utf-8")

    if prod3["selection"]["selected_next"] != "GT9X16-PROD3-AOS-SCHED":
        raise SystemExit("PROD3 map no longer selects the AoS schedule")
    if scaled["static_full_forward_counts"]["R2_montgomery_chains"] != 80:
        raise SystemExit("paper-R2 chain count changed")
    if "PAPER_R2_CACHED_STREAM" not in ntt9_text:
        raise SystemExit("frozen paper-R2 macro disappeared")
    for macro in ("PAPER_D1_ROUTE2", "PAPER_D1_ROUTE1", "PAPER_F1_RECONSTRUCT"):
        if macro not in ntt16_text:
            raise SystemExit(f"frozen route primitive disappeared: {macro}")
    if not ranges["proof"]["r2_adjusted_ntt16_all_stages_fit_signed16"]:
        raise SystemExit("frozen R2/adjusted-NTT16 range proof is no longer closed")
    if prod2["materialized_boundary"]["p2b_vperm2i128_per_forward"] != 72:
        raise SystemExit("P2-B boundary control changed")

    regions = prod2["helper"]["regions"]
    formation_ops = ("vpshufd", "vpermq", "vperm2i128", "vpshufb",
                     "vpunpcklqdq", "vpunpckhqdq")
    formation_routes = {
        name: sum(regions[name].get(opcode, 0) for opcode in formation_ops)
        for name in ("formation_pair0", "formation_pair1")
    }
    if formation_routes != {"formation_pair0": 144, "formation_pair1": 144}:
        raise SystemExit(f"current 36-map route ledger changed: {formation_routes}")
    d1 = regions["d1"]
    d1_routes_per_helper = (
        d1.get("vperm2i128", 0) + d1.get("vpunpcklqdq", 0) +
        d1.get("vpunpckhqdq", 0) + d1.get("vpblendd", 0) +
        d1.get("vpblendw", 0))
    if d1_routes_per_helper != 90:
        raise SystemExit(f"current P2-B D1 route ledger changed: {d1_routes_per_helper}")

    _, c1_checks = c1_network()
    c2_planes, c2_natural_order = c2_early_transpose()
    if len(c2_planes) != 4:
        raise SystemExit("C2 plane count changed")

    # Scale the exact one-row route proof over 9 physical p rows and 2 branches.
    tiles = 18
    scalar_pair_checks = {
        "distance2": c1_checks["d2_scalar_lane_pairs_per_physical_p_row"] * tiles,
        "distance1": c1_checks["d1_scalar_lane_pairs_per_physical_p_row"] * tiles,
        "ma2_cells": c1_checks["ma2_output_cells_per_physical_p_row"] * tiles,
    }
    if scalar_pair_checks != {"distance2": 576, "distance1": 576, "ma2_cells": 1152}:
        raise SystemExit("full-forward C1 lane coverage changed")

    aos_stage = {
        "vector_streams": 8,
        "paper_radix3_butterflies": 48,
        "montgomery_chains": 80,
        "barrett_vectors": 72,
        "data_loads": 72,
        "data_stores": 72,
        "routing": 0,
        "peak_ymm": 16,
        "cutpoints": {
            "input": "72 top-split AoS vectors; four q values x four terminal coefficients",
            "after_round1": "all nine rows remain register-resident within one branch/q-block",
            "after_round2": "72 AoS vectors materialized once in paper physical P order",
        },
    }
    d8_d4 = {
        "physical_p_tiles": tiles,
        "vectors_per_tile": 4,
        "distance8_montgomery_chains": 36,
        "distance4_montgomery_chains": 36,
        "routing": 0,
        "data_loads": 72,
        "data_stores": 0,
        "ownership": "four contiguous physical-q cells per YMM; terminal coefficient remains the innermost word",
    }

    c0_per_tile = {
        "vperm2i128_d2": 4,
        "vpunpck_qword_d1": 4,
        "standalone_transpose": {
            "vpunpckwd": 4, "vpunpckdq": 4,
            "vpunpckqdq": 4, "vpermq": 4,
        },
        "ma2_packed_lane_formation": {"vpshufb": 4, "vpermq": 4},
        "boundary_stores": 4,
        "boundary_reloads": 4,
        "routing_total": 32,
    }
    c1_per_tile = {
        **{key: value for key, value in c0_per_tile.items()
           if key not in ("boundary_stores", "boundary_reloads")},
        "boundary_stores": 0,
        "boundary_reloads": 0,
        "routing_total": 32,
        "fusion": "D1 sum/difference registers feed the first vpunpckwd layer directly",
    }
    c2_per_tile = {
        "early_transpose": {
            "vpunpckwd": 4, "vpunpckdq": 4, "vpunpckqdq": 4,
            "vpermq": 4, "vpshufb_q_order": 4,
        },
        "soa_distance2_routes": 8,
        "soa_distance1_routes": 8,
        "final_plane_reconstruction_routes": 8,
        "boundary_stores": 0,
        "boundary_reloads": 0,
        "routing_total": 44,
        "reused_proven_primitives": ["PAPER_D1_ROUTE2", "PAPER_D1_ROUTE1",
                                      "PAPER_F1_RECONSTRUCT"],
    }

    g0 = {
        "data_loads_after_top_split": 288,
        "data_stores_after_top_split": 216,
        "formation_routing": 2 * sum(formation_routes.values()),
        "adjusted_ntt16_routing": 4 * d1_routes_per_helper - 72,
        "p2b_plane_routing": 72,
        "routing_total": 936,
        "montgomery_chains": 296,
        "barrett_vectors": 72,
    }
    c1 = {
        "data_loads_after_top_split": 144,
        "data_stores_after_top_split": 144,
        "ntt9_routing": 0,
        "d8_d4_routing": 0,
        "d2_d1_to_ma2_routing": c1_per_tile["routing_total"] * tiles,
        "routing_total": c1_per_tile["routing_total"] * tiles,
        "montgomery_chains": 296,
        "barrett_vectors": 72,
        "peak_ymm": 16,
        "extra_temporary_bytes": 0,
    }

    stage_ranges = []
    for row in ranges["adjusted_ntt16_full"]:
        stage_ranges.append({
            "physical_row": row["physical_row"],
            "frequency_p": row["frequency_p"],
            "ntt9_output": row["input_range"],
            "distance8": row["stages"][0]["overall_output_range"],
            "distance4": row["stages"][1]["overall_output_range"],
            "distance2": row["stages"][2]["overall_output_range"],
            "distance1": row["stages"][3]["overall_output_range"],
        })

    document = {
        "schema": "gt9x16-prod3-aos-schedule/v1",
        "checkpoint": "GT9X16-PROD3-AOS-SCHED",
        "parameter": 1152,
        "frozen_contract": {
            "pipeline": ["top-split AoS", "complete paper-R2 NTT9 in AoS",
                         "adjusted D8/D4 in AoS", "adjusted D2/D1",
                         "MA2-native coefficient planes"],
            "physical_p_order": P_ORDER,
            "physical_q_order": Q_ORDER,
            "transform_scale": 4,
            "montgomery_r_exponent": 0,
            "complete_ntt9_materialization_retained": True,
            "cross_axis_wavefront": False,
            "twist_absorption": False,
        },
        "step_A_aos_ntt9": aos_stage,
        "step_B_aos_d8_d4": d8_d4,
        "step_C_networks": {
            "lane_coverage_proof": scalar_pair_checks,
            "C0_materialized_post_d1": {
                "per_tile": c0_per_tile,
                "full_forward_boundary_stores": 72,
                "full_forward_boundary_reloads": 72,
                "full_forward_routing": c0_per_tile["routing_total"] * tiles,
                "selected": False,
            },
            "C1_live_d1_to_transpose": {
                "per_tile": c1_per_tile,
                "full_forward_boundary_stores": 0,
                "full_forward_boundary_reloads": 0,
                "full_forward_routing": c1_per_tile["routing_total"] * tiles,
                "selected": True,
            },
            "C2_early_plane_orientation": {
                "per_tile": c2_per_tile,
                "hierarchical_transpose_natural_q_order": c2_natural_order,
                "lane_local_q_reorder": WORD_SHUFFLE,
                "full_forward_routing": c2_per_tile["routing_total"] * tiles,
                "selected": False,
                "reason": "exact but pays 20 early plane routes plus 24 proved SoA D2/D1/reconstruction routes per tile",
            },
        },
        "step_D_twist_ledger": {
            "separable_identity": "g^(offset*(16h+q)) = g^(16*offset*h) * g^(offset*q)",
            "T0_control": {"pre_twist_montgomery_chains": 72, "selected": True},
            "T1_h_factor_into_ntt9": {
                "algebraically_feasible": True,
                "one_montgomery_multiplication_removed_proved": False,
                "status": "deferred; combined constants and exact chain ledger required",
            },
            "T2_q_factor_into_ntt16": {
                "algebraically_feasible": True,
                "one_montgomery_multiplication_removed_proved": False,
                "status": "deferred; adjusted twiddle/factor/scale proof required",
            },
        },
        "range_and_register_proof": {
            "method": "same arithmetic DAG and representatives; AoS only co-locates four independent terminal coefficients",
            "physical_row_cutpoints": stage_ranges,
            "global_final_i16": [
                min(row["distance1"][0] for row in stage_ranges),
                max(row["distance1"][1] for row in stage_ranges),
            ],
            "all_preoperations_signed_i16": True,
            "extra_reductions": 0,
            "ntt9_peak_ymm": 16,
            "d8_d4_d2_d1_transpose_peak_ymm_upper_bound": 12,
            "phasewise_peak_ymm": 16,
            "spill_target": 0,
        },
        "apples_to_apples_ledger": {
            "unit": "dynamic AVX2 data-memory/routing operations per forward after the common top split",
            "G0_P2B": g0,
            "AOS_C1": c1,
            "AOS_C1_minus_G0": {
                "data_loads_after_top_split": c1["data_loads_after_top_split"] - g0["data_loads_after_top_split"],
                "data_stores_after_top_split": c1["data_stores_after_top_split"] - g0["data_stores_after_top_split"],
                "routing_total": c1["routing_total"] - g0["routing_total"],
                "montgomery_chains": 0,
                "barrett_vectors": 0,
            },
            "constant_loads_excluded_until_asm_register_allocation": True,
            "routing_taxonomy_reconciliation": {
                "map_known_total": prod3["current_control_G0"]["known_routing_total"],
                "map_included": {
                    "early_formation": g0["formation_routing"],
                    "P2B_epilogue": g0["p2b_plane_routing"],
                },
                "map_excluded_open_variable": {
                    "adjusted_ntt16_internal_D8_D4_D2_D1": g0["adjusted_ntt16_routing"],
                },
                "full_linked_control_total": g0["routing_total"],
                "explanation": "648 was the MAP checkpoint's deliberately incomplete known-boundary count; 936 adds the 288 linked adjusted-NTT16 internal routes so both control and C1 include their radix-2 routing",
            },
        },
        "decision": {
            "schedule_complete": True,
            "selected_network": "C1_live_d1_to_transpose",
            "recommended_next_checkpoint": "GT9X16-PROD3-AOS-ASM0",
            "asm_authorized": False,
            "recommended_asm_scope": "one branch/one physical-p tile leaf proving AoS R2, D8/D4, C1 D2/D1-to-plane; no full producer or caller",
            "full_producer_asm_authorized": False,
            "benchmark_authorized": False,
            "cross_axis_wavefront_authorized": False,
            "twist_absorption_authorized": False,
            "native_kem_authorized": False,
        },
        "source_sha256": {
            "prod3_map": sha256(args.prod3_map),
            "scaled_oracle": sha256(args.scaled_oracle),
            "paper_range": sha256(args.paper_range),
            "ntt9_macro": sha256(args.ntt9_macro),
            "ntt16_macro": sha256(args.ntt16_macro),
            "prod2_audit": sha256(args.prod2_audit),
        },
    }
    write(args.output, json.dumps(document, indent=2, sort_keys=True) + "\n", args.check)
    write(args.asm_constants, aos_tile_constants(scaled), args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
