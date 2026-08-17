#!/usr/bin/env python3
"""Generator-only GT32 128-bit microtile representation-family gate."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
OUT = GENERATED / "tile4_rep_family_gate.json"

LEAVES = 16
DEGREES = 4
BLOCKS = 12
KEYGEN_OUTPUTS = 3
FORWARD_BOUND = 9586
BASEINV_OUTPUT_BOUND = 3504
I32_MAX = (1 << 31) - 1


def polynomial_product(a: list[int], b: list[int], lam: int) -> list[int]:
    out = [0, 0, 0, 0]
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            degree = i + j
            if degree >= 4:
                degree -= 4
                out[degree] += lam * x * y
            else:
                out[degree] += x * y
    return out


def pair02_product(a: list[int], b: list[int], lam: int) -> list[int]:
    # Ae=(a0,a2), Ao=(a1,a3), z=x^2, z^2=lambda.
    def qmul(u: tuple[int, int], v: tuple[int, int]) -> tuple[int, int]:
        return (u[0] * v[0] + lam * u[1] * v[1],
                u[0] * v[1] + u[1] * v[0])

    ae, ao = (a[0], a[2]), (a[1], a[3])
    be, bo = (b[0], b[2]), (b[1], b[3])
    ee, oo, eo, oe = qmul(ae, be), qmul(ao, bo), qmul(ae, bo), qmul(ao, be)
    return [ee[0] + lam * oo[1], eo[0] + oe[0],
            ee[1] + oo[0], eo[1] + oe[1]]


def representation(name: str, pairs: tuple[tuple[int, int], tuple[int, int]]) -> dict:
    vectors = []
    for leaf_base in (0, 8):
        for pair in pairs:
            words = [(leaf, degree)
                     for leaf in range(leaf_base, leaf_base + 8)
                     for degree in pair]
            assert len(words) == 16
            vectors.append(words)
    flat = [item for vector in vectors for item in vector]
    assert sorted(flat) == [(leaf, degree) for leaf in range(LEAVES)
                            for degree in range(DEGREES)]
    return {
        "name": name,
        "geometry_per_128_bit_half": "4-leaves-x-2-degrees",
        "degree_pairs": pairs,
        "vectors_per_16_leaves": len(vectors),
        "mapping_bijective": True,
        "vectors": vectors,
    }


def main() -> None:
    prior_pair = json.loads((GENERATED / "tile4_pair_native_bm_gate.json").read_text())
    terminal = json.loads((GENERATED / "tile4_terminal_layout_family_gate.json").read_text())

    families = [
        representation("Pair01", ((0, 1), (2, 3))),
        representation("Pair02", ((0, 2), (1, 3))),
        representation("Pair03", ((0, 3), (1, 2))),
    ]

    # Exhaustive small-coefficient semantic proof is sufficient for these
    # bilinear expressions: equality on the basis/sign test set pins every
    # coefficient of the polynomial identity.
    tests = 0
    basis = [[0, 0, 0, 0]]
    for degree in range(4):
        for sign in (-1, 1):
            value = [0, 0, 0, 0]
            value[degree] = sign
            basis.append(value)
    for lam in (-1728, -1, 1, 1728):
        for a in basis:
            for b in basis:
                assert pair02_product(a, b, lam) == polynomial_product(a, b, lam)
                tests += 1

    # One two-term dot over 16 leaves requires two vpmaddwd accumulators.
    # REDC16 is four instructions per accumulator.  Two scalar dot outputs can
    # be paired without compaction using vpslld/vpblendw per 8-leaf group.
    pair_dot_pair = {
        "scalar_outputs": 2,
        "leaves": 16,
        "vpmaddwd": 4,
        "vphaddd": 0,
        "REDC16_accumulators": 4,
        "REDC16_instructions": 16,
        "pair_output_interleave": 4,
        "instruction_floor": 24,
        "full_SoA_two_products_plus_add_floor": 22,
        "pair_floor_minus_full_SoA": 2,
    }

    # BaseInv has nine independent two-term dot expressions: the two initial
    # quadratic forms (four dots), determinant (one), and four adjugate terms.
    # Pairing their scalar outputs costs at least one extra instruction per dot
    # versus the full-SoA Montgomery formulation, before lambda preparation,
    # determinant conversion for batch inversion, or stores.
    baseinv_dot_expressions = 9
    baseinv_extra_per_block = baseinv_dot_expressions
    two_baseinv_extra = 2 * BLOCKS * baseinv_extra_per_block

    # Pair E/O -> wire AoS uses two lane-local word unpacks per eight leaves.
    # Current D2 starts from four planes and pays the 12-shuffle 4x4 transpose.
    wire_pair_ops = 4
    wire_full_soa_ops = 12
    wire_saving_per_block = wire_full_soa_ops - wire_pair_ops
    keygen_wire_saving = wire_saving_per_block * BLOCKS * KEYGEN_OUTPUTS

    terminal_pair02 = next(item for item in
                           terminal["coefficient_pair_and_native_packed_lower_bounds"]
                           if item["layout"] == "coefficient-pair-02|13")
    terminal_full = terminal["current_full_soa_control"]
    landing_penalty_per_block = (
        terminal_pair02["optimistic_layout_shuffles_per_block"]
        - terminal_full["two_forward_terminals_plus_bm_layout_shuffles_per_block"]
    )
    landing_penalty = landing_penalty_per_block * BLOCKS

    # Give Pair02 the strongest possible BM assumption: the persistent pair
    # layout removes all 48 old qword-construction instructions and all input
    # checkpoint cost.  Its direct vpmaddwd/REDC16 BM is allowed to tie B3.
    # This avoids reusing the old hard stop against a genuinely new DAG.
    optimistic_bm_delta = 0
    static_net_instruction_delta = (
        two_baseinv_extra + landing_penalty + optimistic_bm_delta
        - keygen_wire_saving
    )

    max_pair_accumulator = 2 * FORWARD_BOUND * FORWARD_BOUND
    mixed_pair_accumulator = 2 * FORWARD_BOUND * BASEINV_OUTPUT_BOUND
    assert max_pair_accumulator <= I32_MAX
    assert mixed_pair_accumulator <= I32_MAX

    result = {
        "schema": "ntruplus768-gt32-rep-family-v1",
        "experiment": "GT32-REP-FAMILY-001",
        "scope": "generator-only 128-bit microtile family gate",
        "baseline": "qualified progressive-P full-SoA plus D2",
        "families": [
            {"name": "TILE4", "geometry": "2-leaves-x-4-degrees"},
            *families,
            {"name": "FullSoA", "geometry": "8-leaves-x-1-degree"},
        ],
        "family_triage": {
            "TILE4": "existing wire-friendly control; AoS BaseInv/R1-U consumer is already a measured keygen hard stop",
            "Pair01": "wire-adjacent but does not expose the BaseInv even/odd quadratic inputs without degree-pair regrouping",
            "Pair02": "continued: exactly exposes (a0,a2) and (a1,a3), and enables a no-vphaddd two-term dot DAG",
            "Pair03": "wrapped-term-friendly candidate but does not expose the BaseInv even/odd quadratic inputs without degree-pair regrouping",
            "FullSoA": "qualified A+B+C+D2 baseline",
        },
        "semantic_proof": {
            "mapping_bijections": True,
            "Pair02_quadratic_tower_equals_quartic_schoolbook": True,
            "bilinear_basis_sign_tests": tests,
        },
        "typed_contract": {
            "representation": "Pair02-EvenOdd",
            "input_scale_exponent": 0,
            "forward_abs_bound": FORWARD_BOUND,
            "baseinv_output_abs_bound": BASEINV_OUTPUT_BOUND,
            "vpmaddwd_forward_square_pair_abs_bound": max_pair_accumulator,
            "vpmaddwd_forward_x_baseinv_pair_abs_bound": mixed_pair_accumulator,
            "signed_int32_safe": True,
        },
        "BaseInv_static_DAG": {
            "two_term_dot_expressions": baseinv_dot_expressions,
            "pair_dot_pair_primitive": pair_dot_pair,
            "no_vphaddd": True,
            "no_cross_128_required_by_algebra": True,
            "minimum_extra_instructions_per_16_leaves_vs_full_SoA":
                baseinv_extra_per_block,
            "two_keygen_BaseInv_minimum_extra_instructions": two_baseinv_extra,
            "excluded_costs": [
                "lambda-weighted-companion-formation",
                "determinant-packing-for-16-lane-batch-inverse",
                "loads-stores-loop-and-register-moves",
            ],
        },
        "BaseMul_static_DAG": {
            "Pair02_exact": True,
            "no_vphaddd": True,
            "one_dword_is_one_leaf_after_each_vpmaddwd": True,
            "prior_L02_montgomery_chain_count":
                prior_pair["reduction_chains"]["LS5_nested_L02"]["total"],
            "old_pair_native_hard_stop_reused": False,
            "reason": "persistent Pair02 removes the old 48-instruction operand construction and permits a new direct vpmaddwd/REDC16 DAG",
            "optimistic_delta_vs_B3_used_for_gate": optimistic_bm_delta,
        },
        "wire_static_DAG": {
            "atom": "Q12-half-packet",
            "Pair02_lane_local_unpacks_per_16_leaves": wire_pair_ops,
            "FullSoA_D2_transpose_shuffles_per_16_leaves": wire_full_soa_ops,
            "cross_128_merges": 0,
            "three_keygen_outputs_instruction_saving": keygen_wire_saving,
        },
        "forward_landing": {
            "prior_optimistic_pair02_layout_shuffles_per_block":
                terminal_pair02["optimistic_layout_shuffles_per_block"],
            "prior_full_soa_layout_shuffles_per_block":
                terminal_full["two_forward_terminals_plus_bm_layout_shuffles_per_block"],
            "minimum_penalty_per_block": landing_penalty_per_block,
            "keygen_instruction_penalty": landing_penalty,
            "exact_progressive_P_to_Pair02_landing": "not-yet-proved-free",
        },
        "whole_objective_static_filter": {
            "two_BaseInv_minimum_extra": two_baseinv_extra,
            "forward_landing_minimum_extra": landing_penalty,
            "three_wire_outputs_maximum_saving": keygen_wire_saving,
            "BaseMul_optimistic_delta": optimistic_bm_delta,
            "net_instruction_delta_best_case": static_net_instruction_delta,
            "required_polynomial_endpoint_core_cycle_saving": 100,
            "static_instruction_count_is_not_cycle_evidence": True,
        },
        "decision": (
            "bounded-Pair02-one-block-DAG-gate-eligible"
            if static_net_instruction_delta < 0 else
            "static-stop-no-headroom-vs-qualified-full-SoA-D2"
        ),
        "assembly_emitted": False,
        "continuation": {
            "required_before_assembly": [
                "exact Pair02 BaseInv lambda-companion and determinant route",
                "exact Pair02 vpmaddwd-REDC16 BaseMul register schedule",
                "exact progressive Forward landing and range proof",
                "peak YMM <= 16 and no spill",
            ],
            "benchmark_threshold": "at least 100 core cycles vs A+B+C+D2 in both placements",
        },
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "decision": result["decision"],
        "net_instruction_delta_best_case": static_net_instruction_delta,
        "wire_saving": keygen_wire_saving,
        "two_baseinv_minimum_extra": two_baseinv_extra,
        "landing_penalty": landing_penalty,
    }, indent=2))


if __name__ == "__main__":
    main()
