#!/usr/bin/env python3
"""Exact/static gate for the GT32 NTT32-first split-twist proposal.

This deliberately emits no assembly.  It proves the conjugated transform,
propagates conservative signed-int16 bounds, and compares the unavoidable
Montgomery-chain and register/materialization costs with qualified N5.
"""

import json
from pathlib import Path

import generate_tile4 as gt


OUT = gt.GENERATED / "tile4_n32first_split_twist_gate.json"
OMEGA3_FACTOR = (-886 * pow(gt.R, -1, gt.Q)) % gt.Q


def dft3(values: list[int]) -> list[int]:
    """The exact three-point formula used by DFT3_WIDE_STORE, mod q."""
    x0, x1, x2 = values
    product = OMEGA3_FACTOR * (x1 - x2)
    return [
        (x0 + x1 + x2) % gt.Q,
        (x0 - x2 + product) % gt.Q,
        (x0 - x1 - product) % gt.Q,
    ]


def ntt32(values: list[int]) -> list[int]:
    """Qualified plain CT network."""
    data = [value % gt.Q for value in values]
    for stage in range(1, 6):
        distance = 32 >> stage
        for group in range(0, 32, 2 * distance):
            factor = pow(
                gt.OMEGA32, gt.forward_power(stage, group), gt.Q
            )
            for lane in range(distance):
                low_index = group + lane
                high_index = low_index + distance
                low = data[low_index]
                product = factor * data[high_index] % gt.Q
                data[low_index] = (low + product) % gt.Q
                data[high_index] = (low - product) % gt.Q
    return data


def conjugated_ntt32(values: list[int], weights: list[int]) -> tuple[list[int], int]:
    """Fold an arbitrary row-diagonal twist into every CT butterfly.

    If current data is residual[i] * candidate[i], a butterfly can factor the
    low residual and use zeta*residual[high]/residual[low] on its high arm.
    After five stages one scalar residual remains on every output.
    """
    data = [value % gt.Q for value in values]
    residual = [weight % gt.Q for weight in weights]
    for stage in range(1, 6):
        distance = 32 >> stage
        next_residual = residual[:]
        for group in range(0, 32, 2 * distance):
            zeta = pow(gt.OMEGA32, gt.forward_power(stage, group), gt.Q)
            for lane in range(distance):
                low_index = group + lane
                high_index = low_index + distance
                factor = (
                    zeta * residual[high_index]
                    * pow(residual[low_index], -1, gt.Q)
                ) % gt.Q
                low = data[low_index]
                product = factor * data[high_index] % gt.Q
                data[low_index] = (low + product) % gt.Q
                data[high_index] = (low - product) % gt.Q
                next_residual[low_index] = residual[low_index]
                next_residual[high_index] = residual[low_index]
        residual = next_residual
    assert len(set(residual)) == 1
    return data, residual[0]


def current_transform(values: list[int], branch_scale: int) -> list[int]:
    """Current T3*T32 twist -> DFT3 -> qualified NTT32."""
    rows = [[0] * 32 for _ in range(3)]
    for n3 in range(3):
        for n32 in range(32):
            n = (64 * n3 + 33 * n32) % 96
            rows[n3][n32] = values[32 * n3 + n32] * pow(
                branch_scale, -n, gt.Q
            ) % gt.Q
    tiles = [[0] * 32 for _ in range(3)]
    for n32 in range(32):
        column = dft3([rows[n3][n32] for n3 in range(3)])
        for k3 in range(3):
            tiles[k3][n32] = column[k3]
    return [value for tile in tiles for value in ntt32(tile)]


def candidate_transform(values: list[int], branch_scale: int) -> list[int]:
    """Twisted NTT32 -> T3/twisted DFT3, with no repair permutation."""
    rows = []
    row_residuals = []
    for n3 in range(3):
        row = values[32 * n3:32 * (n3 + 1)]
        weights = [
            pow(branch_scale, -((64 * n3 + 33 * n32) % 96), gt.Q)
            for n32 in range(32)
        ]
        transformed, residual = conjugated_ntt32(row, weights)
        rows.append(transformed)
        row_residuals.append(residual)
    tiles = [[0] * 32 for _ in range(3)]
    for q_index in range(32):
        column = [
            rows[n3][q_index] * row_residuals[n3] % gt.Q
            for n3 in range(3)
        ]
        transformed = dft3(column)
        for k3 in range(3):
            tiles[k3][q_index] = transformed[k3]
    return [value for tile in tiles for value in tile]


def exact_matrix_proof() -> dict:
    naive_split = []
    for scale in gt.BRANCH_SCALE:
        mismatches = 0
        carry_factors = set()
        for n3 in range(3):
            for n32 in range(32):
                unreduced = 64 * n3 + 33 * n32
                reduced = unreduced % 96
                lhs = pow(scale, -reduced, gt.Q)
                rhs = (
                    pow(scale, -64 * n3, gt.Q)
                    * pow(scale, -33 * n32, gt.Q)
                ) % gt.Q
                mismatches += lhs != rhs
                carry_factors.add(lhs * pow(rhs, -1, gt.Q) % gt.Q)
        naive_split.append({
            "scale": scale,
            "scale_pow_96": pow(scale, 96, gt.Q),
            "mismatching_coordinates": mismatches,
            "carry_factor_count": len(carry_factors),
            "naive_split_valid": mismatches == 0,
        })
    branch_results = []
    for branch, scale in enumerate(gt.BRANCH_SCALE):
        equal = True
        for basis in range(96):
            vector = [0] * 96
            vector[basis] = 1
            if current_transform(vector, scale) != candidate_transform(vector, scale):
                equal = False
                break
        branch_results.append({
            "branch": branch,
            "scale": scale,
            "all_96_basis_vectors_equal": equal,
        })
    return {
        "crt_index": "n=(64*n3+33*n32) mod 96",
        "naive_split_claim": "s^-((64*n3+33*n32) mod 96) = s^(-64*n3)*s^(-33*n32)",
        "naive_split_results": naive_split,
        "naive_split_valid": all(item["naive_split_valid"] for item in naive_split),
        "correction": (
            "the mod-96 carry contributes powers of s^96 because branch scales "
            "have order 576; use exact row weights and CT residual ratios"
        ),
        "exact_twisted_stage_factor": (
            "omega32^forward_power(stage,group) * row_weight[high] / row_weight[low]"
        ),
        "output_order": "k3-major, qualified NTT32 bit-reversed Q order",
        "branches": branch_results,
        "exact_matrix_equality": all(
            result["all_96_basis_vectors_equal"] for result in branch_results
        ),
    }


def candidate_ranges() -> dict:
    # Qualified small-input raw top split is bounded by 2896.
    top_bound = 2896
    branches = []
    for branch, scale in enumerate(gt.BRANCH_SCALE):
        row_records = []
        row_bounds = []
        t3_factors = []
        for n3 in range(3):
            bound = top_bound
            residual = [
                pow(scale, -((64 * n3 + 33 * n32) % 96), gt.Q)
                for n32 in range(32)
            ]
            stages = []
            for stage in range(1, 6):
                distance = 32 >> stage
                factors = []
                next_residual = residual[:]
                for group in range(0, 32, 2 * distance):
                    zeta = pow(gt.OMEGA32, gt.forward_power(stage, group), gt.Q)
                    for lane in range(distance):
                        low = group + lane
                        high = low + distance
                        normal = (
                            zeta * residual[high]
                            * pow(residual[low], -1, gt.Q)
                        ) % gt.Q
                        factors.append(gt.centered(normal * gt.R))
                        next_residual[low] = residual[low]
                        next_residual[high] = residual[low]
                product = gt.product_bound(bound, factors)
                stages.append({
                    "stage": stage,
                    "distance": distance,
                    "input_abs_bound": bound,
                    "factor_count": len(set(factors)),
                    "identity_lane_count": sum(
                        factor == gt.centered(gt.R) for factor in factors
                    ),
                    "product_abs_bound": product,
                    "output_abs_bound": bound + product,
                })
                bound += product
                residual = next_residual
            assert len(set(residual)) == 1
            residual_factor = gt.centered(residual[0] * gt.R)
            t3_factors.append(residual_factor)
            row_bounds.append(bound)
            row_records.append({
                "n3": n3,
                "ntt32_stages": stages,
                "pre_dft3_abs_bound": bound,
                "residual_montgomery_factor": residual_factor,
            })

        t3_bounds = [gt.product_bound(bound, [factor])
                     for bound, factor in zip(row_bounds, t3_factors)]
        difference = t3_bounds[1] + t3_bounds[2]
        omega_product = gt.product_bound(difference, [-886])
        output_bounds = [
            sum(t3_bounds),
            t3_bounds[0] + t3_bounds[2] + omega_product,
            t3_bounds[0] + t3_bounds[1] + omega_product,
        ]
        branches.append({
            "branch": branch,
            "scale": scale,
            "rows": row_records,
            "t3_montgomery_factors": t3_factors,
            "t3_scaled_abs_bounds": t3_bounds,
            "dft3_omega_product_abs_bound": omega_product,
            "output_abs_bounds": output_bounds,
            "max_output_abs_bound": max(output_bounds),
            "signed_int16_safe": max(
                [stage["output_abs_bound"]
                 for row in row_records for stage in row["ntt32_stages"]]
                + output_bounds
            ) < 32768,
            "within_existing_B3_10788_contract": max(output_bounds) <= 10788,
        })
    return {
        "method": "exhaustive fixed-factor Montgomery bound plus triangle inequality",
        "raw_top_split_abs_bound": top_bound,
        "branches": branches,
        "all_signed_int16_safe": all(b["signed_int16_safe"] for b in branches),
        "all_within_existing_B3_contract": all(
            b["within_existing_B3_10788_contract"] for b in branches
        ),
    }


def cost_gate() -> dict:
    current = {
        "full_T3xT32_twist_chains": 2 * 3 * 8,
        "DFT3_chains": 2 * 8,
        "NTT32_chains": 6 * 4 * 4,
    }
    current["total_chains"] = sum(current.values())
    candidate = {
        "twisted_NTT32_chains": 6 * 5 * 4,
        "T3_nonidentity_scale_chains": 2 * 2 * 8,
        "DFT3_chains": 2 * 8,
    }
    candidate["total_chains"] = sum(candidate.values())
    extra_chains = candidate["total_chains"] - current["total_chains"]
    return {
        "qualified_N5": current,
        "N32_first_known_exact_schedule": candidate,
        "delta_full_width_Montgomery_chains": extra_chains,
        "delta_vector_instructions_at_four_instruction_chain_floor": 4 * extra_chains,
        "why": [
            "current full twist pays T3 and T32 in one Montgomery chain",
            "exact row conjugation makes every former raw stage-1 chain nonidentity",
            "T3 row 0 is identity, but rows 1 and 2 still need two chains per branch/group",
        ],
        "register_and_materialization": {
            "vectors_per_NTT32_row": 8,
            "rows_needed_by_DFT3": 3,
            "simultaneous_data_YMM_for_zero_debt": 24,
            "architectural_AVX2_YMM": 16,
            "temporaries_not_included_in_24": True,
            "zero_materialization_possible": False,
            "compact_reusable_schedule": (
                "GT/top-split rows -> store -> twisted NTT32 -> store -> T3/DFT3"
            ),
            "extra_full_boundary_vs_N5_vectors": {
                "stores": 48,
                "loads": 48,
                "bytes_each_direction": 1536,
            },
        },
        "optimistic_reopen_case": {
            "requirement": (
            "an exact two-chain residual-T3+DFT3 circuit and a schedule that does not add "
                "a row materialization"
            ),
            "two_chain_T3_DFT3_total_candidate_chains": 152,
            "delta_vs_N5_chains": -8,
            "status": "not found; not used as evidence",
        },
    }


def main() -> None:
    proof = exact_matrix_proof()
    ranges = candidate_ranges()
    costs = cost_gate()
    assert proof["exact_matrix_equality"]
    assert ranges["all_signed_int16_safe"]
    assert ranges["all_within_existing_B3_contract"]
    decision = (
        "static-hard-stop-before-assembly"
        if costs["delta_full_width_Montgomery_chains"] >= 0
        and not costs["register_and_materialization"]["zero_materialization_possible"]
        else "assembly-eligible"
    )
    result = {
        "schema": "ntruplus768-gt32-n32first-split-twist-gate-v1",
        "experiment": "GT32-N32FIRST-SPLIT-TWIST-001",
        "question": (
            "Can NTT32-first plus row-conjugated twisting beat qualified "
            "DFT3-first N5 without changing leaf semantics?"
        ),
        "exact_transform_proof": proof,
        "range_proof": ranges,
        "static_cost_gate": costs,
        "assembly_emitted": False,
        "decision": decision,
        "conclusion": (
            "The proposed simple T32/T3 split is not an identity because mod-96 "
            "CRT carries are visible to order-576 branch scales.  Exact row "
            "conjugation repairs the mathematics and is range-safe, but the known "
            "AVX2 schedule adds eight full-width Montgomery chains and requires "
            "an additional row materialization because 3x8 data YMM exceed the "
            "register file.  It does not beat N5's static gate."
        ),
        "reopen_only_if": [
            "exact T3+DFT3 uses at most two full-width Montgomery chains per branch/group",
            "producer schedule removes the extra NTT32-row materialization",
            "target ISA provides at least 24 data vector registers plus temporaries",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUT)
    print(decision)


if __name__ == "__main__":
    main()
