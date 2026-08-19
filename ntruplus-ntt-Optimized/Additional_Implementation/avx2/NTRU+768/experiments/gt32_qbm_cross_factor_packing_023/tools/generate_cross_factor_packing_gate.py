#!/usr/bin/env python3
"""Cross-factor lane-capacity gate for atomic AVX2 quadratic output."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
EXPERIMENTS = EXPERIMENT.parent
PARENT = EXPERIMENTS / "gt32_qbm_pair_maddwd_022"
ALGEBRA = EXPERIMENTS / "gt32_degree8_incomplete_ntt_018"
GT16 = EXPERIMENTS / "avx2_gt16_quadratic_official_001"
Q = 3457
INPUT_BOUND = 3456
I16_MAX = 32767


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path: Path) -> dict[str, str]:
    return {"path": str(path.resolve()), "sha256": sha256(path)}


def build() -> dict:
    parent_path = PARENT / "generated/qbm_pair_maddwd_gate.json"
    algebra_path = ALGEBRA / "generated/degree8_incomplete_ntt_gate.json"
    ranges_path = GT16 / "generated/quadratic-range-metadata.json"
    parent = json.loads(parent_path.read_text())
    algebra = json.loads(algebra_path.read_text())
    ranges = json.loads(ranges_path.read_text())
    assert parent["decision"]["status"] == \
        "static_reject_current_ABI_atomic_pair_unbenchmarked"
    assert ranges["split_lazy_bound"] == INPUT_BOUND

    # A vpmaddwd destination has eight independent dword lanes.  With one
    # ordinary i32 lane per output coordinate, two coordinates per factor give
    # the exact capacity below; changing factor order cannot alter it.
    coordinate_capacity = []
    for factors in range(1, 9):
        outputs = 2 * factors
        coordinate_capacity.append({
            "factors": factors,
            "required_i32_coordinates": outputs,
            "destination_dword_lanes": 8,
            "one_instruction_feasible": outputs <= 8,
        })
    assert max(item["factors"] for item in coordinate_capacity
               if item["one_instruction_feasible"]) == 4

    # The obvious escape is one mixed-radix dword c0+q*c1.  Canonical reduced
    # values fit in 24 bits, but forming that integer directly is not the same
    # as computing modulo q.  Its bilinear coefficient matrix is
    # [[1,q],[q,r]].  Every i16 linear form valid on the full lazy input cube
    # has coefficient L1 norm <= floor(32767/3456)=9.  A two-product dot of
    # two such forms can create matrix entries of magnitude at most 2*9*9,
    # far below q.
    max_form_l1 = I16_MAX // INPUT_BOUND
    max_two_product_matrix_entry = 2 * max_form_l1 * max_form_l1
    assert max_form_l1 == 9
    assert max_two_product_matrix_entry == 162 < Q

    root_abs_max = max(
        abs(root if root <= Q // 2 else root - Q)
        for record in algebra["exact_algebra"]["records"]
        for root in record["quadratic_roots"])
    direct_u0_bound = (1 + Q) * INPUT_BOUND
    direct_u1_bound = (root_abs_max + Q) * INPUT_BOUND
    assert direct_u0_bound > I16_MAX and direct_u1_bound > I16_MAX

    canonical_encoding_max = Q * Q - 1
    assert canonical_encoding_max < 1 << 24

    return {
        "schema": "ntruplus768-gt32-qbm-cross-factor-packing-023-v1",
        "experiment": "GT32-QBM-CROSS-FACTOR-PACKING-023",
        "production_modified": False,
        "assembly_emitted": False,
        "evidence": [artifact(parent_path), artifact(algebra_path),
                     artifact(ranges_path)],
        "ordinary_i32_coordinate_lane_proof": {
            "vpmaddwd_destination_dword_lanes": 8,
            "independent_outputs_per_quadratic_factor": 2,
            "capacity_table": coordinate_capacity,
            "maximum_factors_per_instruction": 4,
            "cross_factor_permutation_changes_capacity": False,
            "scope": "one independent pre-REDC i32 coordinate per dword lane",
        },
        "packed_two_residue_escape": {
            "canonical_encoding": "c0 + q*c1",
            "canonical_encoding_states": Q * Q,
            "canonical_encoding_max": canonical_encoding_max,
            "fits_24_bits_after_reduction": True,
            "pre_REDC_bilinear_matrix": [[1, Q], [Q, "root"]],
            "lazy_input_bound": INPUT_BOUND,
            "maximum_safe_i16_linear_form_coefficient_L1": max_form_l1,
            "maximum_matrix_entry_from_two_safe_products":
                max_two_product_matrix_entry,
            "required_off_diagonal_matrix_entry": Q,
            "direct_A_form_bounds": {
                "abs_e0_plus_q_e1": direct_u0_bound,
                "abs_root_e1_plus_q_e0": direct_u1_bound,
                "root_abs_max": root_abs_max,
                "fits_signed_i16": False,
            },
            "result": "not_formable_by_one_pre_REDC_vpmaddwd_under_current_lazy_i16_contract",
            "post_REDC_pack_note": (
                "two canonical residues can be packed into one dword only after both "
                "coordinates have already been produced and reduced; this does not cross "
                "the atomic first-result liveness cut"
            ),
        },
        "packing_search_result": {
            "eight_factors_one_instruction_standard_i32_ABI": False,
            "eight_factors_one_instruction_radix_q_escape_current_contract": False,
            "four_factors_one_instruction_expanded_packet": True,
            "interpretation": (
                "the 8-to-4 density drop is structural for current full-range linear i16 "
                "preparation and pre-REDC output, not merely a factor-order choice"
            ),
        },
        "decision": {
            "status": "conditional_packing_stop_current_i16_pre_REDC_contract",
            "emit_ASM": False,
            "scope_closed": [
                "cross-factor permutation with one i32 coordinate per destination lane",
                "direct radix-q packed dual residue using two safe i16 linear products",
            ],
            "not_closed": [
                "the four-factor expanded packet's actual scheduled cycle performance",
                "nonlinear or narrowed-range producer encoding",
                "producer-side preweight and QBM/inverse delayed reduction co-design",
                "post-REDC packed representation for a different consumer",
            ],
            "next_priority": (
                "bounded ASM for selected QBM versus four-factor atomic expanded packet "
                "with matched symbol geometry (024)"
            ),
        },
    }


def main() -> None:
    output = EXPERIMENT / "generated/cross_factor_packing_gate.json"
    output.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n")
    print(output)


if __name__ == "__main__":
    main()
