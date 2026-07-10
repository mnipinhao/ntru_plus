#!/usr/bin/env python3
"""Model Track H3 minimal reconstruction state for Stage12 block3.

The model works on semantic values over F_q, not physical q-register names.
For each Stage12 stripe it treats the four raw inputs as A/B/C/D and the four
outputs as Q[s], Q[8+s], Q[16+s], and Q[24+s].  It then asks how many extra
vector-valued linear forms must survive when Q0..Q23 are already available in
order to reconstruct all Q24..Q31.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT_JSON = ROOT / "u01v3_track_h_h3_candidates.json"
OUT_MD = ROOT / "u01v3_track_h_h3_model.md"

Q = 3457
STAGE12_W = -708 % Q
STRIPES = 8
ROWS = 3
RAW_VALUES_PER_STRIPE = 4
E3_LIVE_OUTPUTS = 24
Q0_CONSTANT_REGS = 1
TOTAL_Q_REGS = 32
DATA_CAPABLE_Q_REGS = TOTAL_Q_REGS - Q0_CONSTANT_REGS
G1_BLOCK3_STORES = STRIPES * ROWS
G1_BLOCK3_LOADS = STRIPES * ROWS


def mod_rank(matrix: list[list[int]], modulus: int = Q) -> int:
    """Return Gaussian-elimination rank over the prime field F_modulus."""
    if not matrix:
        return 0
    work = [[value % modulus for value in row] for row in matrix]
    rows = len(work)
    cols = len(work[0])
    rank = 0
    for col in range(cols):
        pivot = next((r for r in range(rank, rows) if work[r][col]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inv = pow(work[rank][col], -1, modulus)
        work[rank] = [(value * inv) % modulus for value in work[rank]]
        for row in range(rows):
            if row == rank or work[row][col] == 0:
                continue
            factor = work[row][col]
            work[row] = [
                (left - factor * right) % modulus
                for left, right in zip(work[row], work[rank])
            ]
        rank += 1
        if rank == rows:
            break
    return rank


def semantic_row(stripe: int, coeffs: tuple[int, int, int, int]) -> list[int]:
    row = [0] * (STRIPES * RAW_VALUES_PER_STRIPE)
    base = stripe * RAW_VALUES_PER_STRIPE
    row[base : base + RAW_VALUES_PER_STRIPE] = [value % Q for value in coeffs]
    return row


def add_rows(*rows: list[int]) -> list[int]:
    return [sum(values) % Q for values in zip(*rows)]


def scale_row(row: list[int], scalar: int) -> list[int]:
    return [(scalar * value) % Q for value in row]


def combine_target_rows(coeffs: list[int], target: list[list[int]]) -> list[int]:
    return add_rows(*(scale_row(row, coeff) for row, coeff in zip(target, coeffs)))


def build_semantic_matrices() -> tuple[list[list[int]], list[list[int]], dict[str, list[list[int]]]]:
    side: list[list[int]] = []
    target: list[list[int]] = []
    low_diff: list[list[int]] = []
    twisted_high_diff: list[list[int]] = []

    # Modulo q, the Stage12 reductions preserve these linear identities:
    #   out0 = (A + C) + (B + D)
    #   out1 = (A + C) - (B + D)
    #   out2 = (A - C) + w(B - D)
    #   out3 = (A - C) - w(B - D)
    for stripe in range(STRIPES):
        side.extend(
            [
                semantic_row(stripe, (1, 1, 1, 1)),
                semantic_row(stripe, (1, -1, 1, -1)),
                semantic_row(stripe, (1, STAGE12_W, -1, -STAGE12_W)),
            ]
        )
        target.append(
            semantic_row(stripe, (1, -STAGE12_W, -1, STAGE12_W))
        )
        low_diff.append(semantic_row(stripe, (1, 0, -1, 0)))
        twisted_high_diff.append(
            semantic_row(stripe, (0, STAGE12_W, 0, -STAGE12_W))
        )

    return side, target, {
        "low_diff_M": low_diff,
        "twisted_high_diff_T": twisted_high_diff,
    }


def reconstruction_check(
    side: list[list[int]], retained: list[list[int]], target: list[list[int]]
) -> dict[str, int | bool]:
    side_rank = mod_rank(side)
    retained_rank = mod_rank(side + retained)
    full_rank = mod_rank(side + retained + target)
    gained = retained_rank - side_rank
    residual = full_rank - retained_rank
    return {
        "side_rank": side_rank,
        "rank_with_retained": retained_rank,
        "rank_with_retained_and_target": full_rank,
        "retained_quotient_rank": gained,
        "unresolved_target_dimensions": residual,
        "basis_reconstructs_all_block3_outputs": residual == 0,
    }


def live_reg_summary(retained_vectors: int) -> dict[str, int | bool]:
    live_data = E3_LIVE_OUTPUTS + retained_vectors
    live_including_q0 = live_data + Q0_CONSTANT_REGS
    return {
        "e3_live_data_vectors": E3_LIVE_OUTPUTS,
        "retained_vectors": retained_vectors,
        "live_data_vectors": live_data,
        "max_live_q_regs_including_q0": live_including_q0,
        "hardware_q_regs": TOTAL_Q_REGS,
        "data_capable_q_regs_with_q0_reserved": DATA_CAPABLE_Q_REGS,
        "register_cardinality_feasible": live_data <= DATA_CAPABLE_Q_REGS,
    }


def h3a_candidates(
    side: list[list[int]], target: list[list[int]]
) -> list[dict[str, object]]:
    candidates: list[dict[str, object]] = []
    for count in range(1, 5):
        checks = [
            reconstruction_check(side, [target[index] for index in subset], target)
            for subset in itertools.combinations(range(STRIPES), count)
        ]
        max_gain = max(int(check["retained_quotient_rank"]) for check in checks)
        min_residual = min(
            int(check["unresolved_target_dimensions"]) for check in checks
        )
        canonical = list(range(24, 24 + count))
        candidates.append(
            {
                "name": f"H3a_retain_{count}_direct_block3_vectors",
                "class": "register_resident_primary_search",
                "retained_vectors": [f"Q{index}" for index in canonical],
                "retained_vector_count": count,
                "subsets_checked": len(checks),
                "best_retained_quotient_rank": max_gain,
                "unresolved_target_dimensions": min_residual,
                "extra_arithmetic_instructions_total_3rows": 0,
                "extra_memory_ops": 0,
                "memory_diagnostic": {
                    "stores": count * ROWS,
                    "loads": count * ROWS,
                    "total": 2 * count * ROWS,
                    "note": "Memory residence does not repair the missing semantic dimensions.",
                },
                "liveness": live_reg_summary(count),
                "basis_reconstructs_all_block3_outputs": False,
                "feasibility": "register cardinality fits, but semantic reconstruction fails",
                "hard_gate_status": "reject_semantic_rank",
            }
        )
    return candidates


def h3b_candidates(
    side: list[list[int]],
    target: list[list[int]],
    reduced: dict[str, list[list[int]]],
) -> list[dict[str, object]]:
    candidates: list[dict[str, object]] = []
    formulas = {
        "low_diff_M": "Q[24+s] = 2*M_s - Q[16+s]",
        "twisted_high_diff_T": "Q[24+s] = Q[16+s] - 2*T_s",
    }
    for basis_name, basis_rows in reduced.items():
        partial = {
            str(count): reconstruction_check(side, basis_rows[:count], target)
            for count in range(1, 5)
        }
        full = reconstruction_check(side, basis_rows, target)
        candidates.append(
            {
                "name": f"H3b_reduced_basis_{basis_name}",
                "class": "register_primary_and_memory_diagnostic",
                "retained_vectors": [f"{basis_name}[stripe{s}]" for s in range(STRIPES)],
                "retained_vector_count": STRIPES,
                "reconstruction_formula": formulas[basis_name],
                "partial_1_to_4_search": partial,
                "full_basis_check": full,
                "extra_arithmetic_instructions_per_row": 2 * STRIPES,
                "extra_arithmetic_instructions_total_3rows": 2 * STRIPES * ROWS,
                "extra_memory_ops_register_resident": 0,
                "memory_diagnostic": {
                    "stores": STRIPES * ROWS,
                    "loads": STRIPES * ROWS,
                    "total": 2 * STRIPES * ROWS,
                    "delta_memory_ops_vs_G1": 0,
                    "expected_instruction_delta_vs_G1": 2 * STRIPES * ROWS,
                    "note": "It can reuse the existing block3 scratch slots, but then preserves the same memory boundary and adds reconstruction arithmetic.",
                },
                "liveness": live_reg_summary(STRIPES),
                "basis_reconstructs_all_block3_outputs": bool(
                    full["basis_reconstructs_all_block3_outputs"]
                ),
                "feasibility": "algebraically complete, but register-resident form exceeds q-register cardinality; memory form is no better than G1",
                "hard_gate_status": "reject_register_cardinality_and_memory_cost",
            }
        )
    return candidates


def h3c_candidates(
    side: list[list[int]], target: list[list[int]]
) -> list[dict[str, object]]:
    pair_sums = [
        add_rows(target[index], target[index + 1])
        for index in range(0, STRIPES, 2)
    ]

    vandermonde_search: dict[str, dict[str, int | bool]] = {}
    for count in range(1, 5):
        retained = [
            combine_target_rows(
                [pow(column + 1, degree, Q) for column in range(STRIPES)],
                target,
            )
            for degree in range(count)
        ]
        vandermonde_search[str(count)] = reconstruction_check(side, retained, target)

    chain_basis = [target[0]] + [
        add_rows(target[index], scale_row(target[index - 1], -1))
        for index in range(1, STRIPES)
    ]
    pair_check = reconstruction_check(side, pair_sums, target)
    chain_check = reconstruction_check(side, chain_basis, target)

    return [
        {
            "name": "H3c_four_pair_sums",
            "class": "register_resident_primary_search",
            "retained_vectors": [
                f"Q{24 + index}+Q{25 + index}" for index in range(0, STRIPES, 2)
            ],
            "retained_vector_count": 4,
            "check": pair_check,
            "extra_arithmetic_instructions_total_3rows": 4 * ROWS,
            "extra_memory_ops": 0,
            "liveness": live_reg_summary(4),
            "basis_reconstructs_all_block3_outputs": False,
            "feasibility": "pair sums retain only one of two independent dimensions per pair",
            "hard_gate_status": "reject_semantic_rank",
        },
        {
            "name": "H3c_general_linear_combinations_k1_to_k4",
            "class": "rank_upper_bound_search",
            "retained_vectors": "Vandermonde-style independent combinations of Q24..Q31",
            "retained_vector_count_range": [1, 4],
            "search": vandermonde_search,
            "proof": "Any k retained vector-valued linear forms add quotient rank at most k. Since the missing quotient rank is 8, every k<=4 family is incomplete regardless of coefficients.",
            "extra_arithmetic_instructions_total_3rows": "at least k combinations per row; exact cost depends on coefficients",
            "extra_memory_ops": 0,
            "max_live_q_regs_including_q0": "26..29",
            "basis_reconstructs_all_block3_outputs": False,
            "feasibility": "algebraically impossible for k<=4",
            "hard_gate_status": "reject_semantic_rank",
        },
        {
            "name": "H3c_full_chain_basis_boundary",
            "class": "register_primary_boundary_and_memory_diagnostic",
            "retained_vectors": ["Q24"]
            + [f"Q{24 + index}-Q{23 + index}" for index in range(1, STRIPES)],
            "retained_vector_count": STRIPES,
            "check": chain_check,
            "extra_arithmetic_instructions_encode_total_3rows": (STRIPES - 1) * ROWS,
            "extra_arithmetic_instructions_decode_total_3rows": (STRIPES - 1) * ROWS,
            "extra_arithmetic_instructions_total_3rows": 2 * (STRIPES - 1) * ROWS,
            "extra_memory_ops_register_resident": 0,
            "memory_diagnostic": {
                "stores": STRIPES * ROWS,
                "loads": STRIPES * ROWS,
                "total": 2 * STRIPES * ROWS,
                "delta_memory_ops_vs_G1": 0,
                "expected_instruction_delta_vs_G1": 2 * (STRIPES - 1) * ROWS,
            },
            "liveness": live_reg_summary(STRIPES),
            "basis_reconstructs_all_block3_outputs": True,
            "feasibility": "invertible but not smaller than direct Q24..Q31; register form hits the same cardinality blocker and memory form adds arithmetic",
            "hard_gate_status": "reject_no_compression",
        },
    ]


def build_model() -> dict[str, object]:
    side, target, reduced = build_semantic_matrices()
    baseline_check = reconstruction_check(side, [], target)
    full_output_rank = mod_rank(side + target)
    transform_rank_per_stripe = mod_rank(
        [
            [1, 1, 1, 1],
            [1, -1, 1, -1],
            [1, STAGE12_W, -1, -STAGE12_W],
            [1, -STAGE12_W, -1, STAGE12_W],
        ]
    )

    h3a = h3a_candidates(side, target)
    h3b = h3b_candidates(side, target, reduced)
    h3c = h3c_candidates(side, target)

    return {
        "artifact": "u01v3_track_h_h3_minimal_block3_reconstruction_state",
        "status": "model_complete_no_physical_candidate",
        "production_default_changed": False,
        "scope": {
            "asm_emitted": False,
            "slothy_run": False,
            "makefile_changed": False,
            "physical_register_inference_used": False,
        },
        "semantic_contract": {
            "field_modulus_q": Q,
            "stage12_twiddle_w_centered": -708,
            "stage12_twiddle_w_mod_q": STAGE12_W,
            "raw_values_per_stripe": ["A_s", "B_s", "C_s", "D_s"],
            "known_side_information": ["Q0..Q7", "Q8..Q15", "Q16..Q23"],
            "target": [f"Q{index}" for index in range(24, 32)],
            "per_stripe_dependency_cone": {
                "L_s": "A_s + C_s",
                "M_s": "A_s - C_s",
                "H_s": "B_s + D_s (identity-reduced mod q)",
                "T_s": "w*(B_s - D_s) mod q",
                "Q[s]": "L_s + H_s",
                "Q[8+s]": "L_s - H_s",
                "Q[16+s]": "M_s + T_s",
                "Q[24+s]": "M_s - T_s",
            },
            "lane_shape": "Each semantic value is one 128-bit Neon vector with eight independent int16 lanes; the rank proof applies lane-wise. Cross-lane packing is outside H3.",
        },
        "rank_proof": {
            "stage12_transform_rank_per_stripe": transform_rank_per_stripe,
            "side_information_rank_all_8_stripes": mod_rank(side),
            "full_stage12_output_rank_all_8_stripes": full_output_rank,
            "conditional_block3_rank_given_q0_q23": full_output_rank - mod_rank(side),
            "baseline_without_retained_state": baseline_check,
            "minimum_retained_vector_valued_dimensions": full_output_rank
            - mod_rank(side),
            "conclusion": "Q24..Q31 contain eight independent vector-valued dimensions after Q0..Q23 are known. Any exact same-lane linear reconstruction basis therefore needs at least eight vectors.",
        },
        "baseline": {
            "G1_block3_q_stores": G1_BLOCK3_STORES,
            "G1_block3_q_loads": G1_BLOCK3_LOADS,
            "E3_live_outputs_per_row": E3_LIVE_OUTPUTS,
            "q0_reserved": True,
            "data_capable_q_regs": DATA_CAPABLE_Q_REGS,
        },
        "candidates": {
            "H3a_retain_1_to_4_minimal_vectors": h3a,
            "H3b_reduced_basis": h3b,
            "H3c_linear_combinations": h3c,
        },
        "decision": {
            "register_resident_primary_candidate": None,
            "emit_physical_asm": False,
            "hard_gate_status": "stop_h3",
            "reason": "Every 1-4 vector candidate is rank-incomplete. Every complete reduced or linear basis needs eight vectors, making 24 E3 outputs plus 8 basis vectors exceed the 31 data-capable q registers with q0 reserved. Memory residence preserves the same 24-store/24-load boundary as G1 and adds reconstruction arithmetic.",
            "track_h_implication": "H3 cannot compress block3 state under the existing same-lane semantic contract. Removing G1 block3 scratch consumption requires H1/H2-style producer/consumer lifetime reordering, not a smaller reconstruction basis.",
        },
    }


def write_markdown(model: dict[str, object]) -> None:
    rank = model["rank_proof"]
    h3a = model["candidates"]["H3a_retain_1_to_4_minimal_vectors"]
    h3b = model["candidates"]["H3b_reduced_basis"]
    h3c = model["candidates"]["H3c_linear_combinations"]

    h3a_lines = "\n".join(
        f"- {item['retained_vector_count']} vectors: checked {item['subsets_checked']} subsets; "
        f"best rank gain {item['best_retained_quotient_rank']}; "
        f"{item['unresolved_target_dimensions']} block3 dimensions remain."
        for item in h3a
    )
    h3b_lines = "\n".join(
        f"- `{item['name']}`: 8 vectors, reconstructs all = "
        f"{str(item['basis_reconstructs_all_block3_outputs']).lower()}, "
        f"max live q regs including q0 = {item['liveness']['max_live_q_regs_including_q0']}, "
        f"extra arithmetic = {item['extra_arithmetic_instructions_total_3rows']}."
        for item in h3b
    )
    h3c_lines = "\n".join(
        f"- `{item['name']}`: reconstructs all = "
        f"{str(item['basis_reconstructs_all_block3_outputs']).lower()}; "
        f"gate = `{item['hard_gate_status']}`."
        for item in h3c
    )

    OUT_MD.write_text(
        "# U01v3 Track H3 Minimal Block3 Reconstruction State\n\n"
        "Status: model-only complete. No ASM emitted, no Slothy run, no Makefile "
        "or production change.\n\n"
        "## Semantic dependency cone\n\n"
        "For each Stage12 stripe `s`, define:\n\n"
        "```text\n"
        "L_s = A_s + C_s\n"
        "M_s = A_s - C_s\n"
        "H_s = B_s + D_s                  (mod q identity reduction)\n"
        "T_s = w * (B_s - D_s) mod q      (w = -708 mod 3457)\n\n"
        "Q[s]    = L_s + H_s\n"
        "Q[8+s]  = L_s - H_s\n"
        "Q[16+s] = M_s + T_s\n"
        "Q[24+s] = M_s - T_s\n"
        "```\n\n"
        "This is a semantic, lane-wise finite-field model. Physical q-register "
        "names do not participate in the proof.\n\n"
        "## Rank result\n\n"
        "```text\n"
        f"Stage12 rank per stripe:                 {rank['stage12_transform_rank_per_stripe']}\n"
        f"rank(Q0..Q23), eight stripes:            {rank['side_information_rank_all_8_stripes']}\n"
        f"rank(Q0..Q31), eight stripes:            {rank['full_stage12_output_rank_all_8_stripes']}\n"
        f"missing rank for Q24..Q31 given Q0..Q23: {rank['conditional_block3_rank_given_q0_q23']}\n"
        "minimum exact reconstruction state:       8 vectors\n"
        "```\n\n"
        "The important point is that the eight stripes are independent. Knowing "
        "the first three outputs of each 4-point Stage12 transform leaves one "
        "independent vector dimension per stripe. Across eight stripes that is "
        "eight vectors, not one shared vector.\n\n"
        "## H3a: retain 1-4 vectors\n\n"
        f"{h3a_lines}\n\n"
        "All H3a candidates fit the simple register-cardinality count, but none "
        "can reconstruct all `Q24..Q31`; they fail the semantic hard gate before "
        "register allocation matters.\n\n"
        "## H3b: reduced basis\n\n"
        "`M_s=A_s-C_s` or `T_s=w(B_s-D_s)` is enough together with `Q[16+s]`, "
        "but one such basis vector is required for every stripe:\n\n"
        f"{h3b_lines}\n\n"
        "A complete register-resident basis creates 24 existing E3 values + 8 "
        "basis values = 32 data vectors while q0 leaves only 31 data-capable q "
        "registers. A memory-resident basis uses the same 24 stores and 24 loads "
        "as G1, then adds 48 reconstruction instructions across three rows.\n\n"
        "## H3c: linear combinations\n\n"
        f"{h3c_lines}\n\n"
        "Cross-stripe sums and differences do not compress independent vector "
        "dimensions. Four pair sums leave four pair-difference dimensions "
        "unknown. An eight-vector invertible chain basis works, but is the same "
        "size as direct `Q24..Q31` and adds encode/decode arithmetic.\n\n"
        "## Decision\n\n"
        "```text\n"
        "register_resident_primary_candidate: none\n"
        "emit_physical_asm: false\n"
        "hard_gate_status: stop_h3\n"
        "```\n\n"
        "H3 cannot replace G1's block3 scratch boundary with a smaller exact "
        "same-lane reconstruction state. The remaining viable Track H direction "
        "is H1/H2 producer-consumer lifetime reordering, where block3 is produced "
        "after earlier outputs have been consumed instead of being compressed.\n"
    )


def main() -> int:
    model = build_model()
    OUT_JSON.write_text(json.dumps(model, indent=2) + "\n")
    write_markdown(model)
    print(OUT_JSON)
    print(OUT_MD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
