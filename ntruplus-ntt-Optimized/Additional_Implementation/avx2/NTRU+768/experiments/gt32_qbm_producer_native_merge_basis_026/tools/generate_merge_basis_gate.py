#!/usr/bin/env python3
"""Generate the historical 026 gate (superseded by exact correction 027).

Gate A remains valid.  Gate B's scale propagation is retained for audit only:
it tracks the absolute merge weight instead of the candidate/current ratio and
must not be used as an exact conjugation or performance result.
"""

from __future__ import annotations

import itertools
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "avx2_gt16_quadratic_official_001"
HEADER = SOURCE / "generated" / "quadratic-constants.h"
Q = 3457
R = (1 << 16) % Q
R_INV = pow(R, -1, Q)
QINV = 12929
CENTER = Q // 2
HIGH_LANES = {2, 3, 6, 7, 10, 11, 14, 15}
BITREVERSE3 = (0, 4, 2, 6, 1, 5, 3, 7)


def center(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def inverse(value: int) -> int:
    return pow(value % Q, -1, Q)


def signed16(value: int) -> int:
    value &= 0xFFFF
    return value - 0x10000 if value & 0x8000 else value


def montmul16(value: int, standard_constant: int) -> int:
    mont = center(standard_constant * R)
    qinv = signed16(mont * QINV)
    m = signed16(value * qinv)
    return (value * mont >> 16) - (m * Q >> 16)


def mont_bound(bound: int, constants: set[int]) -> int:
    if bound >= (1 << 15):
        raise AssertionError(f"Montgomery input exceeds int16: {bound}")
    return max(
        abs(montmul16(value, constant))
        for constant in constants
        for value in range(-bound, bound + 1)
    )


def center_value(value: int, iterations: int) -> int:
    for _ in range(iterations):
        if value > CENTER:
            value -= Q
        if value < -CENTER:
            value += Q
    return value


def centered_interval_bound(bound: int, iterations: int) -> int:
    return max(abs(center_value(value, iterations)) for value in range(-bound, bound + 1))


def table(text: str, pattern: str, expected: int) -> list[int]:
    match = re.search(pattern + r".*?= \{(.*?)\n\};", text, re.S)
    if match is None:
        raise RuntimeError(f"table not found: {pattern}")
    values = [int(value) for value in re.findall(r"-?\d+", match.group(1))]
    if len(values) != expected:
        raise RuntimeError(f"{pattern}: expected {expected}, got {len(values)}")
    return values


def matrix_rank2_proof() -> dict:
    # A product of independent producer linear forms is an outer product and
    # has bilinear-matrix rank at most one.  Both requested outputs have
    # nonzero determinant and therefore rank two.
    return {
        "sum_matrix": [[1, 0], [0, 1]],
        "difference_matrix_symbolic": [["w", 0], [0, "-w"]],
        "sum_determinant_mod_q": 1,
        "difference_determinant": "-w^2 != 0",
        "single_component_product_maximum_rank": 1,
        "desired_output_rank": 2,
        "same_two_component_products_without_output_mix_possible": False,
    }


def dft3_matrix(omega: int) -> list[list[int]]:
    return [
        [1, 1, 1],
        [1, (-1 - omega) % Q, omega % Q],
        [1, omega % Q, (-1 - omega) % Q],
    ]


def row_permutation_equivalence(
    matrix: list[list[int]], scales: tuple[int, int, int]
) -> list[dict]:
    scaled = [
        [matrix[row][column] * scales[column] % Q for column in range(3)]
        for row in range(3)
    ]
    matches = []
    for permutation in itertools.permutations(range(3)):
        row_scales = []
        valid = True
        for row in range(3):
            target = matrix[permutation[row]]
            factor = scaled[row][0] * inverse(target[0]) % Q
            if any(
                scaled[row][column] != factor * target[column] % Q
                for column in range(3)
            ):
                valid = False
                break
            row_scales.append(center(factor))
        if valid:
            matches.append({
                "output_permutation": list(permutation),
                "row_scales": row_scales,
            })
    return matches


def normalize_signs_to_character(
    scales: tuple[int, int, int], characters: list[tuple[int, int, int]]
) -> dict | None:
    # A common sign is irrelevant, so fix the first sign to +1.
    for signs_tail in itertools.product((1, -1), repeat=2):
        signs = (1,) + signs_tail
        signed = tuple(scales[index] * signs[index] % Q for index in range(3))
        common = signed[0]
        normalized = tuple(value * inverse(common) % Q for value in signed)
        for character_index, character in enumerate(characters):
            if normalized == character:
                return {
                    "signs": list(signs),
                    "character_index": character_index,
                    "normalized": [center(value) for value in normalized],
                }
    return None


def main() -> None:
    text = HEADER.read_text()
    merge_mont = table(text, r"round4c_merge_mont\[48\]\[16\]", 48 * 16)
    inv16_mont = table(text, r"round4c_inv16_twiddle_mont\[14\]", 14)
    omega_mont = int(re.search(
        r"round4c_inv3_omega_mont = (-?\d+);", text
    ).group(1))
    merge_weight = [
        [center(merge_mont[16 * vector + lane] * R_INV) for lane in range(16)]
        for vector in range(48)
    ]
    inv16_twiddle = [center(value * R_INV) for value in inv16_mont]
    omega = center(omega_mont * R_INV)

    # Candidate alpha is lane-wise +/-1.  Sign changes are implementable by
    # swapping the two vpshufb sources before the existing subtraction.  They
    # do not change whether a butterfly ratio has magnitude one, so count with
    # alpha=+1 and optimize signs only at the DFT3 character boundary.
    scale = [
        [merge_weight[vector][lane] if lane in HIGH_LANES else 1
         for lane in range(16)]
        for vector in range(48)
    ]
    stage_records = []
    modified_constants: dict[str, set[int]] = {}

    after_stage1 = [[0] * 16 for _ in range(48)]
    stage1_new = 0
    stage1_ratios = Counter()
    stage1_constants: set[int] = set()
    for k3 in range(3):
        base = 16 * k3
        for position, k16 in enumerate(BITREVERSE3):
            low = base + k16
            high = low + 8
            ratios = tuple(
                center(scale[high][lane] * inverse(scale[low][lane]))
                for lane in range(16)
            )
            stage1_ratios[ratios] += 1
            stage1_constants.update(ratios)
            if any(value != 1 for value in ratios):
                stage1_new += 1
            after_stage1[base + 2 * position] = scale[low][:]
            after_stage1[base + 2 * position + 1] = scale[low][:]
    scale = after_stage1
    modified_constants["inverse-size2-identity"] = stage1_constants
    stage_records.append({
        "stage": "inverse-size2-identity",
        "current_chains": 0,
        "candidate_chains": stage1_new,
        "new_identity_chains": stage1_new,
        "removed_nonidentity_chains": 0,
    })

    twiddle_offset = 0
    for length in (4, 8, 16):
        half = length // 2
        after = [row[:] for row in scale]
        current_chains = 0
        candidate_chains = 0
        new_identity = 0
        removed_nonidentity = 0
        stage_constants: set[int] = set()
        for k3 in range(3):
            base = 16 * k3
            for start in range(0, 16, length):
                for index in range(half):
                    low = base + start + index
                    high = low + half
                    twiddle = 1 if index == 0 else inv16_twiddle[twiddle_offset + index]
                    modified = [
                        center(twiddle * scale[high][lane] * inverse(scale[low][lane]))
                        for lane in range(16)
                    ]
                    current_has_chain = index != 0
                    candidate_has_chain = any(value != 1 for value in modified)
                    if candidate_has_chain:
                        stage_constants.update(modified)
                    current_chains += current_has_chain
                    candidate_chains += candidate_has_chain
                    new_identity += candidate_has_chain and not current_has_chain
                    removed_nonidentity += current_has_chain and not candidate_has_chain
                    after[low] = scale[low][:]
                    after[high] = scale[low][:]
        stage_records.append({
            "stage": f"inverse-length-{length}",
            "current_chains": current_chains,
            "candidate_chains": candidate_chains,
            "new_identity_chains": new_identity,
            "removed_nonidentity_chains": removed_nonidentity,
        })
        scale = after
        modified_constants[f"inverse-length-{length}"] = stage_constants
        twiddle_offset += half

    # Conservative, mechanically evaluated range trace for the modified
    # constants.  Each stage uses the exact maximum of the signed Montgomery
    # implementation over the complete current input interval.
    range_trace = []
    bound = 4185
    high_bound = mont_bound(bound, modified_constants["inverse-size2-identity"])
    raw_bound = bound + high_bound
    assert raw_bound < (1 << 15)
    bound = centered_interval_bound(raw_bound, 2)
    range_trace.append({
        "stage": "inverse-size2-identity",
        "input_abs": 4185,
        "mont_high_abs": high_bound,
        "raw_output_abs": raw_bound,
        "correction": "existing-center-twice",
        "output_abs": bound,
    })
    for length, correction_iterations in ((4, 0), (8, 1), (16, 0)):
        input_bound = bound
        high_bound = mont_bound(bound, modified_constants[f"inverse-length-{length}"])
        raw_bound = bound + high_bound
        assert raw_bound < (1 << 15)
        bound = (
            centered_interval_bound(raw_bound, correction_iterations)
            if correction_iterations else raw_bound
        )
        range_trace.append({
            "stage": f"inverse-length-{length}",
            "input_abs": input_bound,
            "mont_high_abs": high_bound,
            "raw_output_abs": raw_bound,
            "correction": "existing-center-once" if correction_iterations else "none",
            "output_abs": bound,
        })
    dft3_difference_bound = 2 * bound
    dft3_product_bound = mont_bound(dft3_difference_bound, {omega})
    dft3_raw_bound = max(3 * bound, 2 * bound + dft3_product_bound)
    if dft3_raw_bound >= (1 << 15):
        raise AssertionError(f"DFT3 exceeds int16: {dft3_raw_bound}")
    range_trace.append({
        "stage": "inverse-dft3-before-postweight",
        "input_abs": bound,
        "difference_abs": dft3_difference_bound,
        "omega_product_abs": dft3_product_bound,
        "raw_output_abs": dft3_raw_bound,
        "signed_int16_safe": True,
    })

    # Every output position in a k3 batch now inherits the same scale.  This
    # is required for a compact DFT3 classification.
    for k3 in range(3):
        for lane in range(16):
            assert len({scale[16 * k3 + position][lane] for position in range(16)}) == 1

    dft = dft3_matrix(omega % Q)
    cube_roots = sorted(value for value in range(1, Q) if pow(value, 3, Q) == 1)
    nontrivial = [value for value in cube_roots if value != 1]
    characters = [
        (1, 1, 1),
        (1, nontrivial[0], nontrivial[1]),
        (1, nontrivial[1], nontrivial[0]),
    ]
    lane_classes = []
    class_counter = Counter()
    for lane in range(16):
        raw = tuple(scale[16 * k3][lane] % Q for k3 in range(3))
        normalized = normalize_signs_to_character(raw, characters)
        if normalized is None:
            raise AssertionError((lane, raw))
        character = characters[normalized["character_index"]]
        equivalence = row_permutation_equivalence(dft, character)
        if not equivalence:
            raise AssertionError((lane, character))
        permutation = tuple(equivalence[0]["output_permutation"])
        class_counter[permutation] += 1
        lane_classes.append({
            "lane": lane,
            "degree_class": "difference" if lane in HIGH_LANES else "sum",
            "raw_scale": [center(value) for value in raw],
            "sign_normalization": normalized,
            "dft3_output_permutation": list(permutation),
        })

    permutation_classes = [
        {"permutation": list(permutation), "lanes": count}
        for permutation, count in sorted(class_counter.items())
    ]
    heterogeneous = len(permutation_classes) > 1
    # Three DFT3 outputs must each combine lanes from two source registers.
    # With the existing coefficient-output/branch-merge contract this is one
    # blend per output for each of 16 i16 positions.
    dft3_route_lower_bound = 3 * 16 if heterogeneous else 0

    current_merge_chains = 48
    candidate_new_chains = sum(record["new_identity_chains"] for record in stage_records)
    candidate_removed_existing = sum(
        record["removed_nonidentity_chains"] for record in stage_records
    )
    net_chains_saved = current_merge_chains - candidate_new_chains + candidate_removed_existing
    arithmetic_instruction_credit = 4 * net_chains_saved
    net_instruction_lower_bound = dft3_route_lower_bound - arithmetic_instruction_credit

    result = {
        "schema": "ntruplus768-gt32-qbm-producer-native-merge-basis-026-v1",
        "experiment": "GT32-QBM-PRODUCER-NATIVE-MERGE-BASIS-026",
        "gate_A_separable_basis": matrix_rank2_proof(),
        "gate_B_unweighted_merge_basis": {
            "validity": "invalid_scale_propagation_superseded_by_027",
            "candidate": ["u=p+m", "d=alpha*(p-m), alpha lane-wise +/-1"],
            "merge_montgomery_chains_removed": current_merge_chains,
            "inverse_chain_propagation": stage_records,
            "new_identity_chains": candidate_new_chains,
            "removed_existing_nonidentity_chains": candidate_removed_existing,
            "net_montgomery_chains_saved": net_chains_saved,
            "montgomery_instructions_per_chain": 4,
            "arithmetic_instruction_credit": arithmetic_instruction_credit,
            "range": {
                "qbm_REDC_interval": [-2092, 2093],
                "unweighted_sum_difference_interval": [-4185, 4185],
                "first_new_chain_occurs_before_existing_center_twice": True,
                "new_full_checkpoint_required": False,
                "trace": range_trace,
                "signed_int16_safe": True,
            },
            "dft3": {
                "omega": omega,
                "cube_roots": [center(value) for value in cube_roots],
                "lane_classes": lane_classes,
                "permutation_classes": permutation_classes,
                "heterogeneous_within_ymm": heterogeneous,
                "current_coefficient_output_route_lower_bound": dft3_route_lower_bound,
                "reason": (
                    "sum lanes retain identity k3 order while difference lanes require "
                    "a cyclic DFT3 output permutation"
                ),
            },
            "net_instruction_lower_bound_after_route": net_instruction_lower_bound,
            "assembly_eligible": net_instruction_lower_bound < 0,
        },
        "gate_C_producer_provenance": {
            "executed": False,
            "reason": (
                "Gate B saves only three Montgomery chains before requiring 48 "
                "lane-heterogeneous DFT3 blends under the current coefficient consumer"
            ),
        },
        "decision": {
            "status": "superseded_by_027_exact_conjugation_correction",
            "assembly_emitted": False,
            "closed": [
                "independent producer linear transforms eliminating merge mixing with only two diagonal products",
                "alpha=+/-1 unweighted merge basis with the current coefficient-output inverse contract",
            ],
            "open": [
                "a downstream consumer that natively accepts lane-heterogeneous k3 order",
                "producer scaling only after a merge basis with negative whole-pipeline cost exists",
                "prepared or wider-ISA representations that change the output contract",
            ],
            "next": "close current QBM-to-merge2 architecture unless the inverse output consumer changes",
        },
        "sources": [
            str(SOURCE / "src" / "qbm_intrinsic.c"),
            str(SOURCE / "src" / "inverse_stage1_intrinsic.c"),
            str(SOURCE / "generated" / "quadratic-range-metadata.json"),
            str(HEADER),
        ],
    }
    output = ROOT / "generated" / "merge_basis_gate.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(output)


if __name__ == "__main__":
    main()
