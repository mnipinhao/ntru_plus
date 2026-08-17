#!/usr/bin/env python3
"""Closure gate for the branch-local, explicit-twist 160-chain Forward.

This is deliberately a generator-only architecture gate.  It proves the
proposed stage order against the qualified transform and then audits the
existing representative/range ABI before any new assembly is emitted.
"""

from __future__ import annotations

import json

import generate_n32first_gate as split
import generate_tile4 as gt


OUT = gt.GENERATED / "tile4_n32_branchlocal_raw160_gate.json"
FORWARD_ASM_GATE = gt.GENERATED / "tile4_n32_forward_asm_gate.json"
PFA_GATE = gt.GENERATED / "tile4_n32_gt_pfa_joint_gate.json"
B3_INPUT_BOUND = 10788


def apply_ntt32_stages(values: list[int], first: int, last: int) -> list[int]:
    data = [value % gt.Q for value in values]
    for stage in range(first, last + 1):
        distance = 32 >> stage
        for group in range(0, 32, 2 * distance):
            factor = pow(gt.OMEGA32, gt.forward_power(stage, group), gt.Q)
            for lane in range(distance):
                low_index = group + lane
                high_index = low_index + distance
                low = data[low_index]
                product = factor * data[high_index] % gt.Q
                data[low_index] = (low + product) % gt.Q
                data[high_index] = (low - product) % gt.Q
    return data


def branchlocal_raw160_transform(values: list[int], scale: int) -> list[int]:
    """Explicit T3xT32 twist, raw S1, S2/S3, DFT3, then S4/S5."""
    rows = [[0] * 32 for _ in range(3)]
    for n3 in range(3):
        for n32 in range(32):
            n = (64 * n3 + 33 * n32) % 96
            rows[n3][n32] = (
                values[32 * n3 + n32] * pow(scale, -n, gt.Q)
            ) % gt.Q
        rows[n3] = apply_ntt32_stages(rows[n3], 1, 3)

    tiles = [[0] * 32 for _ in range(3)]
    for q in range(32):
        column = split.dft3([rows[n3][q] for n3 in range(3)])
        for k3 in range(3):
            tiles[k3][q] = column[k3]
    return [
        value
        for tile in tiles
        for value in apply_ntt32_stages(tile, 4, 5)
    ]


def exact_transform_proof() -> dict[str, object]:
    branches = []
    for branch, scale in enumerate(gt.BRANCH_SCALE):
        mismatch = None
        for basis in range(96):
            vector = [0] * 96
            vector[basis] = 1
            reference = split.current_transform(vector, scale)
            candidate = branchlocal_raw160_transform(vector, scale)
            if reference != candidate:
                mismatch = basis
                break
        branches.append({
            "branch": branch,
            "scale": scale,
            "all_96_basis_vectors_equal": mismatch is None,
            "first_mismatching_basis": mismatch,
        })
    return {
        "candidate_order": "explicit-twist -> S1-S3 -> DFT3 -> S4-S5",
        "reference_order": "explicit-twist -> DFT3 -> S1-S5",
        "reason_axes_commute": (
            "DFT3 acts on n3/k3 while every NTT32 stage acts on n32/q"
        ),
        "scale": "ordinary e=0 in and e=0 out",
        "logical_output_order": "k3-major qualified NTT32 Q order",
        "physical_output_ABI": (
            "unchanged current group-major half-native [0,1,2]/[0,2,1] redeposit"
        ),
        "quartic_leaf_mapping": "unchanged current B=33 Good coordinate",
        "branches": branches,
        "exact_matrix_equality": all(
            record["all_96_basis_vectors_equal"] for record in branches
        ),
    }


def chain_accounting() -> dict[str, object]:
    candidate = {
        "explicit_twist": 2 * 3 * 8,
        "raw_S1": 0,
        "S2_S5": 2 * 3 * 4 * 4,
        "DFT3_omega": 2 * 8,
    }
    candidate["total"] = sum(candidate.values())
    current = {
        "row_conjugated_forward": 168,
        "candidate_raw160": candidate["total"],
        "saved_chains": 168 - candidate["total"],
        "saved_vector_instructions_at_four_instruction_chain": (
            4 * (168 - candidate["total"])
        ),
    }
    assert candidate["total"] == 160
    return {"candidate": candidate, "comparison": current}


def register_and_materialization_gate() -> dict[str, object]:
    phases = [
        {
            "phase": "shared top split",
            "active_data_YMM": 8,
            "temporaries_and_constants_YMM": 2,
            "peak_YMM": 10,
        },
        {
            "phase": "four-way explicit twist or S2/S3",
            "active_data_YMM": 8,
            "temporaries_and_constants_YMM": 5,
            "peak_YMM": 13,
        },
        {
            "phase": "DFT3/S4/S5 current suffix",
            "active_data_YMM": 6,
            "temporaries_and_constants_YMM": 6,
            "peak_YMM": 12,
        },
    ]
    peak = max(record["peak_YMM"] for record in phases)
    return {
        "ownership": "one active eight-YMM branch; inactive sibling in scratch",
        "phases": phases,
        "peak_YMM": peak,
        "fits_AVX2_16_YMM": peak <= 16,
        "spill_required": False,
        "scratch": {
            "bytes": 1536,
            "reuses_current_forward_scratch": True,
            "new_full_polynomial_materialization": False,
        },
        "static_delta_vs_current_branch_at_time_168": {
            "removed_Montgomery_instructions": 32,
            "removed_row0_center_instructions_if_zero_checkpoint_closed": 48,
            "extra_branch_materialization_memory_instructions": 42,
            "optimistic_net_instructions": -38,
        },
    }


def range_and_consumer_gate() -> dict[str, object]:
    forward = json.loads(FORWARD_ASM_GATE.read_text())
    pfa = json.loads(PFA_GATE.read_text())
    s3 = next(
        item for item in pfa["stage_order_range"]
        if item["DFT3_after_stage"] == 3
    )
    raw_bounds = [
        record["final_abs_bound"] for record in s3["branches"]
    ]
    assert raw_bounds == forward["representative_closure"][
        "R3_raw_conservative_output_abs_bounds_by_branch"
    ]
    int16_safe = all(record["safe"] for record in s3["branches"])
    b3_safe = max(raw_bounds) <= B3_INPUT_BOUND
    return {
        "method": (
            "exhaustive fixed-factor Montgomery product bounds plus interval add/sub; "
            "cross-checked against the emitted R3 raw Forward gate"
        ),
        "pre_DFT3_abs_bounds": [
            record["pre_DFT3"] for record in s3["branches"]
        ],
        "DFT3_output_abs_bounds": [
            record["DFT3_outputs"] for record in s3["branches"]
        ],
        "final_raw_abs_bounds_by_branch": raw_bounds,
        "signed_int16_safe": int16_safe,
        "existing_B3_input_abs_bound": B3_INPUT_BOUND,
        "within_existing_B3_input_contract": b3_safe,
        "R1U_and_existing_inverse_safe": False,
        "failure_frontier": "Forward output -> existing B3/R1-U input ABI",
        "reason": (
            f"raw representative reaches {max(raw_bounds)}, above the frozen "
            f"B3/R1-U producer limit {B3_INPUT_BOUND}"
        ),
        "known_repairs": {
            "full_output_center10": {
                "vectors": 48,
                "instructions": 144,
                "result_abs_bound": forward["representative_closure"][
                    "single_final_center10_abs_bound"
                ],
            },
            "row0_only_center": {
                "applies_to": "168-chain row-conjugated representative, not raw160",
                "vectors": forward["conjugated_proof_audit"]["row0_center_vectors"],
                "instructions": forward["conjugated_proof_audit"][
                    "row0_center_instructions"
                ],
            },
        },
        "no_row0_or_global_checkpoint": False,
    }


def main() -> None:
    proof = exact_transform_proof()
    chains = chain_accounting()
    registers = register_and_materialization_gate()
    ranges = range_and_consumer_gate()
    assert proof["exact_matrix_equality"]
    assert ranges["signed_int16_safe"]

    eligibility = {
        "exactly_160_chains": chains["candidate"]["total"] == 160,
        "exact_transform_scale_leaf_mapping": proof["exact_matrix_equality"],
        "no_row0_or_global_checkpoint": ranges["no_row0_or_global_checkpoint"],
        "peak_YMM_at_most_16": registers["peak_YMM"] <= 16,
        "reuses_current_1536B_scratch": registers["scratch"][
            "reuses_current_forward_scratch"
        ],
        "existing_R1U_and_inverse_range_safe": ranges[
            "R1U_and_existing_inverse_safe"
        ],
    }
    assembly_eligible = all(eligibility.values())
    result = {
        "schema": "ntruplus768-gt32-n32-branchlocal-raw160-gate-v1",
        "experiment": "GT32-N32-BRANCHLOCAL-RAW160-019",
        "question": (
            "Can branch-local ownership make the exact 160-chain raw NTT32-first "
            "Forward directly composable with the frozen half-native BM/inverse ABI?"
        ),
        "frozen": [
            "B=33 Good coordinate and current three physical waves",
            "half-native [0,1,2]/[0,2,1] output ABI",
            "R1-U BaseMul and typed native inverse",
            "current DFT3/S4/S5 suffix mathematics",
        ],
        "exact_transform_proof": proof,
        "Montgomery_chain_accounting": chains,
        "register_and_materialization": registers,
        "range_and_consumer_contract": ranges,
        "assembly_eligibility_checks": eligibility,
        "assembly_emitted": False,
        "decision": (
            "assembly-eligible" if assembly_eligible
            else "static-hard-stop-before-assembly"
        ),
        "conclusion": (
            "Branch-local ownership solves the 17th-register problem and the exact "
            "factorization has 160 chains, but it recreates the already-emitted raw "
            "R3 representative.  That representative is int16-safe yet reaches "
            f"{max(ranges['final_raw_abs_bounds_by_branch'])}, so it cannot directly "
            f"enter the frozen {B3_INPUT_BOUND}-bound B3/R1-U/inverse chain.  The "
            "required checkpoint removes the proposed zero-checkpoint mechanism; no "
            "new assembly is justified."
        ),
        "reopen_only_if": [
            "a producer-correlated proof closes raw160 -> R1-U -> inverse without a checkpoint",
            "a changed BM/inverse representative contract safely accepts the raw160 envelope",
            "a selective repair for raw160 costs less than the eight-chain/32-instruction saving",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUT)
    print(result["decision"])


if __name__ == "__main__":
    main()
