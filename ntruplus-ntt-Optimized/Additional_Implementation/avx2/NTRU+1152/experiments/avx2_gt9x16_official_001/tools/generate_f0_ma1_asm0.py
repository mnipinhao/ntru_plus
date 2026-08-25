#!/usr/bin/env python3
"""Generate the fixed B0/P0 MA1 ASM0 contract and aligned constants."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

Q = 3457
QINV = 12929
R = 65536 % Q


def signed16(value: int) -> int:
    value &= 0xffff
    return value - 65536 if value >= 32768 else value


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def render(path: Path, text: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text() != text:
            raise SystemExit(f"generated file is stale: {path}")
    else:
        path.write_text(text)


def vector(label: str, values: list[int]) -> str:
    if len(values) != 16:
        raise SystemExit(f"{label}: expected 16 values")
    return f"{label}:\n  .short " + ", ".join(str(value) for value in values) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schedule", type=Path, required=True)
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--asm-constants", type=Path, required=True)
    parser.add_argument("--header", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    schedule = json.loads(args.schedule.read_text())
    if schedule["decision"]["assembly_candidates"] != ["MA1", "MA3"]:
        raise SystemExit("MA1 authorization changed")
    tile = next(tile for tile in schedule["semantic_tiles"]
                if tile["tile"]["branch"] == 0 and tile["tile"]["p"] == 0)
    lambda_mod_q = tile["planes"][0]["lambda_mod_q"]
    if any(plane["lambda_mod_q"] != lambda_mod_q for plane in tile["planes"]):
        raise SystemExit("lambda differs by terminal coefficient")
    lambda_r = [centered(value * R) for value in lambda_mod_q]
    lambda_qinv = [signed16(value * QINV) for value in lambda_r]
    inv4 = pow(4, -1, Q)
    inv4_r = centered(inv4 * R)
    inv4_qinv = signed16(inv4_r * QINV)

    stream_lambda = []
    for stream in range(2):
        half = lambda_r[stream * 8:(stream + 1) * 8]
        half_qinv = lambda_qinv[stream * 8:(stream + 1) * 8]
        stream_lambda.append({"factor": half + half,
                              "factor_qinv": half_qinv + half_qinv})

    word_order = [3, 2, 1, 0, 5, 4, 6, 7]
    shuffle = []
    for word in word_order:
        shuffle.extend([2 * word, 2 * word + 1])
    shuffle = shuffle + shuffle

    contract = {
        "schema": "gt-f0-ma1-asm0/v1",
        "checkpoint": "F0-MA1-ASM0",
        "tile": {"branch": 0, "p": 0, "physical_p_row": 0},
        "abi": {
            "symbol": "ntruplus1152_exp001_f0_ma1_asm0_b0p0",
            "output": "four 16-lane semantic coefficient planes in even-physical-q then odd-physical-q order",
            "r": "64 aligned i16 F0 tile words",
            "m": "64 aligned i16 F0 tile words",
            "h": "full aligned Official resident poly",
            "alias": "output must not alias r, m, or h",
        },
        "montgomery_ledger": {
            "input_r_exponents": {"h": 0, "r": 0, "m": 0},
            "h_r_lift_chains": 4,
            "h_r_lift_constant": {"R2": 867, "R2_qinv": 2787},
            "bilinear_product_chains": 16,
            "lambda_chains": 4,
            "ma1_core_chains": 20,
            "ma1_arithmetic_including_h_lift": 24,
            "inv4_finalizer_chains": 4,
            "total_chains": 28,
            "output_r_exponent": 0,
            "output_transform_scale": 1,
        },
        "inv4": {"mod_q": inv4, "montgomery_factor": inv4_r,
                 "factor_qinv_signed16": inv4_qinv},
        "lambda_streams": stream_lambda,
        "resident_h": {
            "official_source_vector_pairs_by_coefficient":
                [plane["resident_h_source_vectors"] for plane in tile["planes"]],
            "source_lane_offsets": tile["planes"][0]["resident_h_source_lane_offsets"],
            "word_shuffle": word_order,
            "asm0_exact_projection": "combine Official vector halves, shuffle words, exchange lane 7 across 128-bit halves, then form pair vectors",
        },
        "route_accounting": {
            "schedule_792": "semantic route slots only, not executed AVX2 shuffle instructions",
            "machine_classification_source": "generated/f0-ma1-asm0-audit.json",
        },
        "input_bounds": {"r_and_m": [plane["f0_exact_ranges_i16"]
                                      for plane in tile["planes"]],
                         "h": [0, Q - 1]},
        "required_alignment": {"entry": 32, "constants": 32,
                               "poly_and_tile_pointers": 32},
        "source_schedule_sha256": hashlib.sha256(args.schedule.read_bytes()).hexdigest(),
    }
    json_text = json.dumps(contract, indent=2, sort_keys=True) + "\n"

    constants = "/* Generated F0-MA1-ASM0 B0/P0 constants. */\n.p2align 5\n"
    constants += vector(".Lf0_ma1_q", [Q] * 16)
    constants += vector(".Lf0_ma1_qinv", [QINV] * 16)
    constants += vector(".Lf0_ma1_barrett", [9] * 16)
    constants += vector(".Lf0_ma1_half_q", [1728] * 16)
    constants += vector(".Lf0_ma1_negative_half_q", [-1728] * 16)
    constants += vector(".Lf0_ma1_r2", [867] * 16)
    constants += vector(".Lf0_ma1_r2_qinv", [2787] * 16)
    constants += vector(".Lf0_ma1_inv4", [inv4_r] * 16)
    constants += vector(".Lf0_ma1_inv4_qinv", [inv4_qinv] * 16)
    constants += vector(".Lf0_ma1_lambda_s0", stream_lambda[0]["factor"])
    constants += vector(".Lf0_ma1_lambda_s0_qinv", stream_lambda[0]["factor_qinv"])
    constants += vector(".Lf0_ma1_lambda_s1", stream_lambda[1]["factor"])
    constants += vector(".Lf0_ma1_lambda_s1_qinv", stream_lambda[1]["factor_qinv"])
    constants += vector(".Lf0_ma1_low_half", [-1] * 8 + [0] * 8)
    constants += ".Lf0_ma1_h_shuffle:\n  .byte " + ", ".join(str(x) for x in shuffle) + "\n"

    header = """#ifndef NTRUPLUS1152_EXP001_F0_MA1_ASM0_H
#define NTRUPLUS1152_EXP001_F0_MA1_ASM0_H

#include <stdint.h>

void ntruplus1152_exp001_f0_ma1_asm0_b0p0(
    int16_t output[64], const int16_t r_f0_tile[64],
    const int16_t m_f0_tile[64], const int16_t h_official[1152]);

#endif
"""
    render(args.json, json_text, args.check)
    render(args.asm_constants, constants, args.check)
    render(args.header, header, args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
