#!/usr/bin/env python3
"""Generate the QBM i32-to-real-consumer reduction-boundary gate."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "avx2_gt16_quadratic_official_001"
HEADER = SOURCE / "generated" / "quadratic-constants.h"
Q = 3457
R = (1 << 16) % Q
R_INV = pow(R, -1, Q)
INT32_MAX = (1 << 31) - 1
C0_BOUND = 11_943_936
C1_BOUND = 23_887_872


def center(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def signed16(value: int) -> int:
    value &= 0xFFFF
    return value - 0x10000 if value & 0x8000 else value


def redc32(value: int) -> int:
    m = signed16((value & 0xFFFF) * 12929)
    assert (value - m * Q) % (1 << 16) == 0
    return (value - m * Q) // (1 << 16)


def parse_merge_mont() -> list[int]:
    text = HEADER.read_text()
    match = re.search(
        r"round4c_merge_mont\[48\]\[16\].*?= \{(.*?)\n\};",
        text,
        re.S,
    )
    if match is None:
        raise RuntimeError("round4c_merge_mont table not found")
    values = [int(value) for value in re.findall(r"-?\d+", match.group(1))]
    if len(values) != 48 * 16:
        raise RuntimeError(f"unexpected merge table size: {len(values)}")
    return values


def fused_word_decomposition(value: int, weight: int) -> tuple[int, int]:
    low = signed16(value)
    high = signed16(value >> 16)
    carry = int(low < 0)
    k0 = center(weight)
    k1 = center(weight * R)
    pre_redc = low * k0 + high * k1 + carry * k1
    return redc32(pre_redc), pre_redc


def verify_word_decomposition(weights: list[int]) -> dict:
    probes = {
        -2 * C1_BOUND, -2 * C0_BOUND, -(1 << 16) - 1, -(1 << 16),
        -32769, -32768, -32767, -1, 0, 1, 32767, 32768, 32769,
        (1 << 16) - 1, 1 << 16, 2 * C0_BOUND, 2 * C1_BOUND,
    }
    state = 0x9E3779B97F4A7C15
    for _ in range(20_000):
        state ^= (state << 13) & ((1 << 64) - 1)
        state ^= state >> 7
        state ^= (state << 17) & ((1 << 64) - 1)
        probes.add(int(state % (4 * C1_BOUND + 1)) - 2 * C1_BOUND)
    maximum_pre_redc = 0
    maximum_output = 0
    for weight in sorted(set(weights)):
        for value in probes:
            got, pre_redc = fused_word_decomposition(value, weight)
            if (got - value * weight * R_INV) % Q != 0:
                raise AssertionError((value, weight, got))
            maximum_pre_redc = max(maximum_pre_redc, abs(pre_redc))
            maximum_output = max(maximum_output, abs(got))
    conservative_pre_redc = 32768 * max(
        abs(center(weight)) for weight in weights
    ) + (2 * C1_BOUND // (1 << 16) + 2) * max(
        abs(center(weight * R)) for weight in weights
    )
    conservative_output = (
        conservative_pre_redc + 32768 * Q
    ) // (1 << 16) + 1
    return {
        "identity": (
            "REDC(low_s*w+high_s*(wR)+carry*(wR)) == w*x*R^-1 mod q"
        ),
        "random_and_boundary_probes": len(probes) * len(set(weights)),
        "observed_pre_REDC_abs": maximum_pre_redc,
        "observed_output_abs": maximum_output,
        "conservative_pre_REDC_abs": conservative_pre_redc,
        "conservative_output_abs": conservative_output,
        "signed_i32_safe": conservative_pre_redc <= INT32_MAX,
        "signed_i16_output_safe": conservative_output < (1 << 15),
        "known_instruction_sequence": [
            "vpslld-16-expose-low-sign",
            "vpsrad-31-carry-mask",
            "vpmaddwd-[w,wR]-word-decomposition",
            "vpand-carry-correction",
            "vpaddd-carry-correction",
            "vpmullw-qinv",
            "vpand-lowword",
            "vpmaddwd-q",
            "vpsubd",
            "vpsrad-16",
        ],
        "known_instruction_count": 10,
    }


def main() -> None:
    merge_mont = parse_merge_mont()
    weights = [center(value * R_INV) for value in merge_mont]
    maximum_weight = max(abs(value) for value in weights)
    difference_bounds = {
        "c0": 2 * C0_BOUND,
        "c1": 2 * C1_BOUND,
    }
    vpmulld = {}
    for name, bound in difference_bounds.items():
        safe = sum(bound * abs(weight) <= INT32_MAX for weight in weights)
        vpmulld[name] = {
            "difference_bound": bound,
            "maximum_product_abs": bound * maximum_weight,
            "safe_lanes": safe,
            "total_lanes": len(weights),
            "safe_weight_abs_threshold": INT32_MAX // bound,
            "uniformly_legal": safe == len(weights),
        }

    word_decomposition = verify_word_decomposition(weights)
    result = {
        "schema": "ntruplus768-gt32-qbm-wide-consumer-025-v1",
        "experiment": "GT32-QBM-WIDE-CONSUMER-025",
        "actual_consumer": {
            "first_operation": "quadratic-to-quartic merge2",
            "not_first_operation": "inverse NTT twiddle",
            "outputs": [
                "sum = plus + minus",
                "high = Mont(plus - minus, merge_weight_mont)",
            ],
            "next_operation": "identity inverse size-2 butterfly",
        },
        "scale": {
            "qbm_i32_after_REDC": "R^-1",
            "merge_sum": "R^-1",
            "merge_weighted_difference": "R^-1",
        },
        "bounds": {
            "qbm_c0_accumulator_abs": C0_BOUND,
            "qbm_c1_accumulator_abs": C1_BOUND,
            "wide_difference_abs": difference_bounds,
            "signed_i32_difference_safe": max(difference_bounds.values()) <= INT32_MAX,
        },
        "current_boundary_per_original_vector": {
            "REDC32_chains": 2,
            "REDC32_instructions": 10,
            "merge_Montgomery16_chains": 1,
            "merge_Montgomery16_instructions": 4,
            "note": "pack/order and merge routing are separate from these arithmetic chains",
        },
        "delayed_without_weight_fusion": {
            "REDC32_chains": 2,
            "merge_Montgomery16_chains": 1,
            "operation_class_deleted": False,
            "reason": (
                "the invertible sum/difference merge still has the same number of "
                "independent output residues; delaying REDC only moves both reducers"
            ),
        },
        "direct_vpmulld_weight_fusion": {
            "maximum_centered_merge_weight_abs": maximum_weight,
            "per_coordinate": vpmulld,
            "legal_for_full_vector": False,
            "reason": "wide accumulator times the real merge weight overflows signed i32",
        },
        "vpmuldq_64bit": {
            "legal": True,
            "eight_lane_products_require_at_least_two_vectors": True,
            "avx2_packed_64bit_modular_reducer_available": False,
            "operation_class_deleted": False,
        },
        "signed_word_decomposition_fused_reducer": word_decomposition,
        "instruction_comparison_weighted_difference": {
            "current_REDC32_then_Montgomery16": 9,
            "best_known_legal_direct_word_decomposition": 10,
            "credit": -1,
            "critical_chain_shorter": False,
        },
        "decision": {
            "status": "static_stop_direct_wide_consumer_current_merge_contract",
            "assembly_emitted": False,
            "closed": [
                "delay REDC32 while retaining the existing merge2 arithmetic",
                "single-vpmulld direct merge-weight fusion over the proved full range",
                "signed-word-decomposition fusion as an instruction/critical-path win",
            ],
            "open": [
                "producer-native weighted sum/difference dots that delete merge2 work",
                "a changed QBM-to-inverse representation that removes a full merge or reduction boundary",
                "narrowed/nonlinear prepared operands",
                "wider SIMD or ISA with dense 32x32-to-64 and reduction support",
            ],
            "next": "producer-native preweight gate only if it deletes merge2 or one complete reducer",
        },
        "sources": [
            str(SOURCE / "src" / "qbm_intrinsic.c"),
            str(SOURCE / "src" / "inverse_stage1_intrinsic.c"),
            str(SOURCE / "proofs" / "qbm-range-and-schedule.md"),
            str(HEADER),
        ],
    }
    output = ROOT / "generated" / "wide_consumer_gate.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(output)


if __name__ == "__main__":
    main()
