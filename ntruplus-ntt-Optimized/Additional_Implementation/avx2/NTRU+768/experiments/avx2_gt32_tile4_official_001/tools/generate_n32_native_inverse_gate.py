#!/usr/bin/env python3
"""Exact generator gate for the half-native N32 BM -> inverse boundary.

The gate intentionally treats 2F+B+I as the eventual decision unit, but it
does not emit an inverse assembly candidate unless the current typed R1-U
range contract reaches the raw inverse length-2 butterfly without a new
checkpoint.  Semantic k3 reflection and physical qword movement are accounted
for separately from range repair.
"""

from __future__ import annotations

import json

import generate_tile4 as gt


OUT = gt.GENERATED / "tile4_n32_native_inverse_gate.json"
BM_RANGE = gt.GENERATED / "tile4_aos_dot_redc16_gate.json"
BM_ISLAND = gt.GENERATED / "tile4_n32_gt_bm_island_gate.json"
R3_RESULT = gt.ROOT / "results" / "tile4-n32-wave-schedule-short.json"

Q = gt.Q
INT16_LIMIT = 32767
IDFT_W_FACTOR = -886
IDFT_W_QINV = 13706


def signed16(value: int) -> int:
    value &= 0xFFFF
    return value - 0x10000 if value >= 0x8000 else value


def signed_high16(left: int, right: int) -> int:
    return (left * right) // (1 << 16)


def mont_w(value: int) -> int:
    """Bit-exact scalar model of IDFT3_V2's signed-word Mont chain."""
    low = signed16(value * IDFT_W_QINV)
    return (signed_high16(value, IDFT_W_FACTOR)
            - signed_high16(low, Q))


def center10(value: int) -> int:
    """Exact vpmulhrsw(value,10), vpmullw(q), vpsubw model."""
    quotient = (value * 10 + (1 << 14)) // (1 << 15)
    return value - quotient * Q


def exact_idft_interval(low: int, high: int) -> dict[str, object]:
    """Exact IDFT3_V2 intervals for three independent [low,high] inputs.

    For o1/o2, enumerate the difference and only the two feasible r1
    endpoints: once d=r1-r2 and Mont(d) are fixed, each expression is affine
    in r1 and r0.  This exhausts the interval contract without a cubic search.
    """
    centered = [center10(total) for total in range(2 * low, 2 * high + 1)]
    intervals: list[list[int]] = [
        [low + min(centered), high + max(centered)]
    ]
    witnesses: list[dict[str, object]] = []

    for output in (1, 2):
        minimum = 1 << 60
        maximum = -(1 << 60)
        minimum_witness: tuple[int, ...] | None = None
        maximum_witness: tuple[int, ...] | None = None
        for difference in range(low - high, high - low + 1):
            r1_low = max(low, low + difference)
            r1_high = min(high, high + difference)
            product = mont_w(difference)
            for r1 in {r1_low, r1_high}:
                r2 = r1 - difference
                for r0 in {low, high}:
                    value = (r0 - r1 - product if output == 1
                             else r0 - r2 + product)
                    witness = (r0, r1, r2, difference, product, value)
                    if value < minimum:
                        minimum = value
                        minimum_witness = witness
                    if value > maximum:
                        maximum = value
                        maximum_witness = witness
        assert minimum_witness is not None and maximum_witness is not None
        intervals.append([minimum, maximum])
        witnesses.append({
            "output": output,
            "minimum": {
                "r0_r1_r2_difference_montw_value": list(minimum_witness),
            },
            "maximum": {
                "r0_r1_r2_difference_montw_value": list(maximum_witness),
            },
        })

    return {
        "input_interval": [low, high],
        "output_intervals": intervals,
        "output_1_2_extremum_witnesses": witnesses,
        "max_output_abs_bound": max(
            abs(value) for interval in intervals for value in interval),
    }


def idft_range_contract(mode: dict[str, object]) -> dict[str, object]:
    records = []
    maximum = -1
    worst: dict[str, object] | None = None
    for q_record in mode["q_records"]:
        for coefficient in q_record["coefficients"]:
            proof = exact_idft_interval(*coefficient["exact_output_interval"])
            record = {
                "physical_q": q_record["physical_q"],
                "coefficient": coefficient["coefficient"],
                **proof,
            }
            records.append(record)
            if proof["max_output_abs_bound"] > maximum:
                maximum = proof["max_output_abs_bound"]
                worst = record
    assert worst is not None
    return {
        "independent_interval_contracts_checked": len(records),
        "exact_max_output_abs_bound": maximum,
        "worst_record": worst,
    }


def exact_reflected_idft_proof() -> dict[str, object]:
    omega = pow(gt.OMEGA96, 32, Q)
    inverse_matrix = (
        (1, 1, 1),
        (1, pow(omega, 2, Q), omega),
        (1, omega, pow(omega, 2, Q)),
    )
    reflection = (0, 2, 1)
    checked = 0
    for basis in range(3):
        logical = [int(index == basis) for index in range(3)]
        physical = [logical[index] for index in reflection]
        reference = [
            sum(row[index] * logical[index] for index in range(3)) % Q
            for row in inverse_matrix
        ]
        candidate = []
        for row in inverse_matrix:
            physical_factors = [row[index] for index in reflection]
            candidate.append(sum(
                physical_factors[index] * physical[index]
                for index in range(3)) % Q)
        assert candidate == reference
        checked += 1
    return {
        "low_half_k3_order": [0, 1, 2],
        "high_half_k3_order": [0, 2, 1],
        "high_half_factor_order": [0, 2, 1],
        "exact_basis_vectors_checked": checked,
        "runtime_k3_repair": 0,
        "new_Montgomery_chains": 0,
    }


def five_blend_reverse_route() -> dict[str, object]:
    source = {
        "t0": ["r0q0", "r0q1", "r0q2", "r0q3"],
        "t1": ["r1q0", "r1q1", "r2q2", "r2q3"],
        "t2": ["r2q0", "r2q1", "r1q2", "r1q3"],
    }
    target = {
        "x": ["r0q0", "r1q1", "r2q2", "r0q3"],
        "y": ["r2q0", "r0q1", "r1q2", "r2q3"],
        "z": ["r1q0", "r2q1", "r0q2", "r1q3"],
    }
    source_sets = {
        name: len({next(key for key, packet in source.items()
                        if label in packet) for label in packet})
        for name, packet in target.items()
    }
    assert source_sets == {"x": 2, "y": 3, "z": 3}
    blend_counts = {name: count - 1 for name, count in source_sets.items()}
    assert sum(blend_counts.values()) == 5
    return {
        "physical_IDFT_outputs": source,
        "natural_InvNTT32_inputs": target,
        "blend_instructions": blend_counts,
        "total_blend_instructions_per_component": 5,
        "current_T9_blends_per_component": 6,
        "components": 16,
        "maximum_static_route_credit_instructions": 16,
    }


def inverse_stage_bounds(initial: int) -> list[dict[str, object]]:
    bound = initial
    stages = []
    for length in (4, 8, 16, 32):
        product = gt.product_bound(
            bound,
            [gt.mont_root(-offset * (32 // length))
             for offset in range(length // 2)],
        )
        bound += product
        stages.append({
            "length": length,
            "product_abs_bound": product,
            "output_abs_bound": bound,
            "signed_int16_safe": bound <= INT16_LIMIT,
        })
    return stages


def repair_accounting(idft_bound: int) -> dict[str, object]:
    center_bound = max(abs(center10(value))
                       for value in range(-idft_bound, idft_bound + 1))
    length2 = idft_bound + center_bound
    stages = [{
        "length": 2,
        "low_abs_bound": idft_bound,
        "repaired_high_abs_bound": center_bound,
        "output_abs_bound": length2,
        "signed_int16_safe": length2 <= INT16_LIMIT,
    }, *inverse_stage_bounds(length2)]
    assert all(stage["signed_int16_safe"] for stage in stages)

    high_arms_per_tile = 4
    tiles = 6
    center_instructions = 3
    repair = high_arms_per_tile * tiles * center_instructions
    route_credit = 16
    return {
        "candidate": "center10-pair-packed-high-arm-before-raw-length2",
        "center10_output_abs_bound": center_bound,
        "high_arms_per_tile": high_arms_per_tile,
        "tiles": tiles,
        "instructions_per_high_arm": center_instructions,
        "repair_instructions": repair,
        "range_chain": stages,
        "maximum_five_vs_six_blend_credit": route_credit,
        "net_static_instructions_before_other_boundary_cost": repair - route_credit,
        "identity_Mont_alternative_instructions": high_arms_per_tile * tiles * 4,
    }


def main() -> None:
    ranges = json.loads(BM_RANGE.read_text())
    island = json.loads(BM_ISLAND.read_text())
    r3 = json.loads(R3_RESULT.read_text())

    assert island["typed_layout"]["low_128_r_order"] == [0, 1, 2]
    assert island["typed_layout"]["high_128_r_order"] == [0, 2, 1]
    r1u = idft_range_contract(ranges["modes"]["R1-U"])
    r1s = idft_range_contract(ranges["modes"]["R1-S"])
    assert r1u["exact_max_output_abs_bound"] == 19387
    assert r1s["exact_max_output_abs_bound"] == 19386

    # q=30 and q=31 have the same c3 contract, so the extremum is admissible
    # in both arms of one raw length-2 pair.  This is a typed-contract witness,
    # not a claim that one producer input realizes all interval extrema.
    q30 = ranges["modes"]["R1-U"]["q_records"][30]["coefficients"][3]
    q31 = ranges["modes"]["R1-U"]["q_records"][31]["coefficients"][3]
    assert q30["exact_output_interval"] == q31["exact_output_interval"]
    length2_witness = 2 * r1u["exact_max_output_abs_bound"]
    assert length2_witness > INT16_LIMIT

    r3_tax = {
        placement: values["three_wave_plus_route_estimate_tsc"]
        for placement, values in r3["placements"].items()
    }
    two_forward_debt = {
        placement: 2 * value for placement, value in r3_tax.items()
    }
    suffix_proxy = {
        placement: -values["suffix_route"]["paired_candidate_minus_control"]
        ["median_tsc"]
        for placement, values in r3["placements"].items()
    }

    result = {
        "schema": "ntruplus768-gt32-n32-native-inverse-v1",
        "experiment": "GT-N32-NATIVE-INVERSE-007",
        "decision_unit": "eventual-2F-plus-half-native-R1U-plus-native-inverse",
        "frozen_contract": {
            "BM_input_layout": island["typed_layout"],
            "BM_output_scale_exponent": -1,
            "inverse_twiddle_scale_exponent": 1,
            "final_fused_factor_scale_exponent": 2,
            "final_output_scale_exponent": 0,
            "quartic_basis": "monomial",
            "arithmetic_kernel_changes": False,
        },
        "semantic_proofs": {
            "reflected_high_half_IDFT3": exact_reflected_idft_proof(),
            "reverse_route": five_blend_reverse_route(),
            "InvNTT32": {
                "twiddle_depends_on": "logical-q-edge-and-length",
                "twiddle_independent_of": ["k3-label", "branch-label"],
                "k3_reflection_requires_new_twiddle_table": False,
                "runtime_inverse_permutation_repair": 0,
            },
        },
        "range_gate": {
            "R1-U": r1u,
            "R1-S_control": r1s,
            "raw_length2_contract_witness": {
                "physical_q_pair": [30, 31],
                "coefficient": 3,
                "IDFT_output_abs_value_each_arm":
                    r1u["exact_max_output_abs_bound"],
                "raw_sum_abs_value": length2_witness,
                "signed_int16_safe": False,
                "scope": "admissible-independent-interval-contract-witness",
            },
            "cheapest_known_proof_safe_repair": repair_accounting(
                r1u["exact_max_output_abs_bound"]),
        },
        "economics": {
            "R3_is": "executable-S1-S3-wave-microprobe-not-a-complete-N32-Forward",
            "estimated_R3_debt_TSC_per_Forward": r3_tax,
            "estimated_two_Forward_debt_TSC": two_forward_debt,
            "measured_same_shape_five_vs_six_blend_credit_TSC_per_Forward":
                suffix_proxy,
            "interpretation": (
                "The native label route is exact, but its complete static credit is only "
                "16 blends.  IDFT-first needs at least 72 known repair instructions under "
                "the current typed range contract, or +56 before any other boundary work. "
                "Leaving IDFT late recovers only the measured roughly three-TSC route proxy, "
                "well below the roughly 17.2-TSC two-Forward R3 estimate."
            ),
        },
        "candidates": {
            "I0-IDFT3-before-InvNTT32-raw": {
                "status": "correct-layout-unsafe-range-contract",
                "assembly_eligible": False,
            },
            "I1-IDFT3-before-InvNTT32-center-high-arm": {
                "status": "proof-safe-static-economics-fail",
                "assembly_eligible": False,
            },
            "I2-IDFT3-after-current-I1-half-native-route": {
                "status": "exact-but-route-credit-below-two-Forward-break-even",
                "assembly_eligible": False,
            },
        },
        "assembly_emitted": False,
        "benchmark_2F_B_I_run": False,
        "decision": "no-assembly-native-inverse-range-repair-exceeds-route-credit",
        "not_claimed": [
            "a global lower bound over fused IDFT3-times-length2 circuits",
            "that NTT32-first mathematics is invalid",
            "that a producer-realizable range set equals the independent interval box",
            "that a complete executable R3 Forward already exists",
        ],
        "reopen_only_if": [
            "a fused six-by-six IDFT3-times-length2 circuit absorbs the repair into an existing reduction",
            "BM emits a proof-safe representative without an extra finalizer",
            "a complete N32 Forward removes the measured R3 wave debt by a new execution geometry",
            "a wider register/SIMD ISA changes the range or packet schedule",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUT)
    print(result["decision"])


if __name__ == "__main__":
    main()
