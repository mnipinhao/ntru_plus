#!/usr/bin/env python3
"""Prove the scaled paper R3xR3 variants and their pipeline scale closure."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

Q = 3457
QINV = 12929
R = pow(2, 16, Q)
GENERATOR = 7
ROOT144_EXPONENT = 24
STANDARD_P = [0, 3, 6, 1, 4, 7, 2, 5, 8]
PAPER_P = [0, 3, 6, 1, 4, 7, 8, 2, 5]


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def signed16(value: int) -> int:
    value %= 65536
    return value - 65536 if value >= 32768 else value


def montgomery(value: int) -> int:
    return centered(value * R)


def dft(source: list[int], root: int) -> list[int]:
    return [sum(value * pow(root, source_index * frequency, Q)
                for source_index, value in enumerate(source)) % Q
            for frequency in range(len(source))]


def generic_radix3(source: list[int], zeta1: int, zeta2: int,
                   omega3: int) -> list[int]:
    a, b, c = source
    b = b * zeta1 % Q
    c = c * zeta2 % Q
    t = omega3 * (b - c) % Q
    return [(a + b + c) % Q, (a - c + t) % Q, (a - b - t) % Q]


def r0(source: list[int], rho: int, omega3: int) -> list[int]:
    values = source[:]
    for group in range(3):
        result = generic_radix3(
            [values[group], values[group + 3], values[group + 6]],
            1, 1, omega3)
        for index, value in enumerate(result):
            values[group + 3 * index] = value
    for group in range(3):
        result = generic_radix3(values[3 * group:3 * group + 3],
                                pow(rho, group, Q),
                                pow(rho, 2 * group, Q), omega3)
        values[3 * group:3 * group + 3] = result
    return values


def scaled_radix3(source: list[int], omega3: int) -> list[int]:
    f0, f1, f2 = source
    sum12 = (f1 + f2) % Q
    difference12 = (f1 - f2) % Q
    kappa = (omega3 - pow(omega3, 2, Q)) % Q
    product = kappa * difference12 % Q
    base = (2 * f0 - sum12) % Q
    return [2 * (f0 + sum12) % Q,
            (base + product) % Q,
            (base - product) % Q]


def r1(source: list[int], rho: int, omega3: int) -> list[int]:
    first = [scaled_radix3([source[a], source[a + 3], source[a + 6]],
                           omega3) for a in range(3)]
    output = []
    for c in range(3):
        twisted = [first[a][c] * pow(rho, a * c, Q) % Q for a in range(3)]
        output.extend(scaled_radix3(twisted, omega3))
    return output


def r2(source: list[int], rho: int, omega3: int) -> list[int]:
    first = [
        scaled_radix3([source[0], source[3], source[6]], omega3),
        scaled_radix3([source[1], source[4], source[7]], omega3),
        scaled_radix3([source[8], source[2], source[5]], omega3),
    ]
    twist_exponents = ((0, 0, 0), (0, 1, -1), (0, -1, 1))
    output = []
    for c, exponents in enumerate(twist_exponents):
        twisted = [first[a][c] * pow(rho, exponents[a], Q) % Q
                   for a in range(3)]
        output.extend(scaled_radix3(twisted, omega3))
    return output


def variant_basis_proof(function, row_map: list[int], scale: int,
                        rho: int, omega3: int) -> int:
    checks = 0
    for source_row in range(9):
        source = [int(index == source_row) for index in range(9)]
        natural = dft(source, rho)
        output = function(source, rho, omega3)
        expected = [scale * natural[p] % Q for p in row_map]
        if output != expected:
            raise SystemExit(
                f"{function.__name__} basis mismatch at source row {source_row}")
        checks += len(output)
    return checks


def basemul4(left: list[int], right: list[int], factor: int) -> list[int]:
    product = [0] * 7
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            product[i + j] = (product[i + j] + a * b) % Q
    for degree in range(6, 3, -1):
        product[degree - 4] = (product[degree - 4] +
                               factor * product[degree]) % Q
    return product[:4]


def baseinv_phase1_homogeneous(source: list[int], factor: int) -> tuple[list[int], int]:
    # This is the degree structure implemented by Official poly_baseinv_1.
    a0, a1, a2, a3 = source
    t0 = (a0 * a0 + factor * (a2 * a2 - 2 * a1 * a3)) % Q
    t1 = (2 * a0 * a2 - a1 * a1 - factor * a3 * a3) % Q
    denominator = (t0 * t0 - factor * t1 * t1) % Q
    adjugate = [
        (a0 * t0 - factor * a2 * t1) % Q,
        (a1 * t0 - factor * a3 * t1) % Q,
        (a2 * t0 - a0 * t1) % Q,
        (a3 * t0 - a1 * t1) % Q,
    ]
    return adjugate, denominator


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ntt9-first-oracle", type=Path, required=True)
    parser.add_argument("--pipeline-layout", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    ntt9_first = json.loads(args.ntt9_first_oracle.read_text())
    pipeline = json.loads(args.pipeline_layout.read_text())
    if ntt9_first["ntt9_exponent_convention"] != "+a*p":
        raise SystemExit("paper R3R3 proof requires the audited +a*p convention")
    if ntt9_first["ntt9_row_order"] != "two-trit-reversed; unchanged":
        raise SystemExit("D-B NTT9 physical row convention changed")
    if pipeline["physical_row_to_mathematical_p"] != STANDARD_P:
        raise SystemExit("Checkpoint E standard row map changed")

    rho = ntt9_first["ntt9_root_mod_q"]
    expected_rho = pow(GENERATOR, ROOT144_EXPONENT * 16 * 5, Q)
    if rho != expected_rho:
        raise SystemExit("D-B root is not the pinned pure cyclic ninth root")
    omega3 = pow(rho, 3, Q)
    if pow(rho, 9, Q) != 1 or pow(rho, 3, Q) == 1:
        raise SystemExit("rho does not have order nine")
    if pow(omega3, 3, Q) != 1 or omega3 == 1:
        raise SystemExit("rho^3 does not have order three")
    if omega3 != (-886 * pow(R, -1, Q)) % Q:
        raise SystemExit("paper omega3 does not match the D-A arithmetic root")

    proof_counts = {
        "R0_standard_generic": variant_basis_proof(r0, STANDARD_P, 1, rho, omega3),
        "R1_scaled_standard_twists": variant_basis_proof(r1, STANDARD_P, 4, rho, omega3),
        "R2_scaled_paper_twists": variant_basis_proof(r2, PAPER_P, 4, rho, omega3),
    }

    # D-B already proves that the shear contributes only rho^(-v*p).  Re-key
    # the adjusted NTT16 rows by the paper physical order; linearity preserves
    # the uniform transform scale four.
    db_rows = {row["frequency_p"]: row for row in ntt9_first["rows"]}
    db_twiddles = {row["frequency_p"]: row
                   for row in ntt9_first["adjusted_ntt16_twiddles"]}
    paper_rows = []
    for physical_row, p in enumerate(PAPER_P):
        row = db_rows[p]
        paper_rows.append({
            "physical_row": physical_row,
            "frequency_p": p,
            "phase_base_mod_q": row["phase_base_mod_q"],
            "phase_by_lane_mod_q": row["phase_by_lane_mod_q"],
            "adjusted_ntt16_source_row": row["output_row"],
            "adjusted_ntt16_stages": db_twiddles[p]["stages"],
            "transform_scale": 4,
        })

    source_cells = {(cell["branch"], cell["ntt9_frequency_p"],
                     cell["ntt16_lane_physical_bit_reversed"]): cell
                    for cell in pipeline["cells"]}
    paper_factor_rows = []
    for branch in range(2):
        for physical_row, p in enumerate(PAPER_P):
            factors = []
            for lane in range(16):
                cell = source_cells[(branch, p, lane)]
                factors.append({
                    "physical_lane": lane,
                    "frequency_q": cell["ntt16_frequency_q"],
                    "factor_mod_q": cell["factor_mod_q"],
                    "basemul_factor_montgomery": cell["basemul_factor_montgomery"],
                    "basemul_factor_qinv_signed16": cell["basemul_factor_qinv_signed16"],
                    "baseinv_factor_montgomery": cell["baseinv_factor_montgomery"],
                    "baseinv_factor_qinv_signed16": cell["baseinv_factor_qinv_signed16"],
                    "checkpoint_e_source_physical_row": cell["gt_row_physical_trit_reversed"],
                })
            paper_factor_rows.append({
                "branch": branch,
                "physical_row": physical_row,
                "frequency_p": p,
                "factors": factors,
            })

    homogeneity_checks = {"basemul_degree2": 0,
                          "baseinv_adjugate_degree3": 0,
                          "baseinv_denominator_degree4": 0}
    for row in paper_factor_rows:
        for entry in row["factors"]:
            seed = 1 + row["branch"] * 17 + row["physical_row"] * 5 + entry["physical_lane"]
            left = [(seed + 3 * index) % Q for index in range(4)]
            right = [(2 * seed + 5 * index + 1) % Q for index in range(4)]
            factor = entry["factor_mod_q"]
            normal_product = basemul4(left, right, factor)
            scaled_product = basemul4([4 * value % Q for value in left],
                                      [4 * value % Q for value in right], factor)
            if scaled_product != [16 * value % Q for value in normal_product]:
                raise SystemExit("BaseMul degree-two scale proof failed")
            homogeneity_checks["basemul_degree2"] += 1
            adjugate, denominator = baseinv_phase1_homogeneous(left, factor)
            scaled_adjugate, scaled_denominator = baseinv_phase1_homogeneous(
                [4 * value % Q for value in left], factor)
            if scaled_adjugate != [64 * value % Q for value in adjugate]:
                raise SystemExit("BaseInv adjugate degree-three scale proof failed")
            if scaled_denominator != 256 * denominator % Q:
                raise SystemExit("BaseInv denominator degree-four scale proof failed")
            homogeneity_checks["baseinv_adjugate_degree3"] += 1
            homogeneity_checks["baseinv_denominator_degree4"] += 1

    inv4 = pow(4, -1, Q)
    inv16 = pow(16, -1, Q)
    inv64 = pow(64, -1, Q)
    official_inverse_constant = (-33) % Q
    candidate_inverse_constant = official_inverse_constant * inv64 % Q
    document = {
        "parameter": 1152,
        "checkpoint": "F-R3A-scaled-paper-r3r3-producer-closure",
        "terminology": "two-layer radix-3 Cooley-Tukey; not Good-Thomas-9",
        "q": Q,
        "rho_mod_q": rho,
        "omega3_mod_q": omega3,
        "kappa_mod_q": (omega3 - pow(omega3, 2, Q)) % Q,
        "kappa_montgomery_signed": montgomery(omega3 - pow(omega3, 2, Q)),
        "kappa_qinv_signed16": signed16(
            montgomery(omega3 - pow(omega3, 2, Q)) * QINV),
        "pure_cyclic_gate": {
            "passed": True,
            "transform": "F_p = sum_a R_a rho^(a*p)",
            "weighted_input_factor": "none",
            "evidence": "D-B +a*p root/convention and 9x16 basis oracle",
        },
        "variants": {
            "R0": {
                "radix3_core": "current generic Montgomery radix3",
                "inter_level": "standard R3xR3",
                "physical_row_to_mathematical_p": STANDARD_P,
                "transform_scale": 1,
                "montgomery_chains_per_ntt9": 18,
                "inter_level_multiplications": 4,
                "distinct_inter_level_nontrivial_constants": 3,
                "inter_level_constants": ["rho", "rho^2", "rho^4"],
            },
            "R1": {
                "radix3_core": "paper scaled radix3",
                "inter_level": "standard R3xR3",
                "physical_row_to_mathematical_p": STANDARD_P,
                "transform_scale": 4,
                "montgomery_chains_per_ntt9": 10,
                "inter_level_multiplications": 4,
                "distinct_inter_level_nontrivial_constants": 3,
                "inter_level_constants": ["rho", "rho^2", "rho^4"],
            },
            "R2": {
                "radix3_core": "paper scaled radix3",
                "inter_level": "Figure-9b rotated input/output",
                "physical_row_to_mathematical_p": PAPER_P,
                "transform_scale": 4,
                "montgomery_chains_per_ntt9": 10,
                "inter_level_multiplications": 4,
                "distinct_inter_level_nontrivial_constants": 2,
                "inter_level_constants": ["rho", "rho^-1"],
            },
        },
        "static_full_forward_counts": {
            "ntt9_instances": 8,
            "R0_montgomery_chains": 144,
            "R1_montgomery_chains": 80,
            "R2_montgomery_chains": 80,
            "R0_to_R1_or_R2_chain_reduction": 64,
            "warning": "operation counts are algebraic schedule counts, not instruction or cycle measurements",
        },
        "paper_adjusted_ntt16_rows": paper_rows,
        "paper_basemul_baseinv_factor_rows": paper_factor_rows,
        "scale_ledger": {
            "forward": {
                "paper_radix3_layers": 2,
                "transform_scale": 4,
                "adjusted_ntt16_changes_scale": False,
            },
            "base_mul": {
                "homogeneous_degree": 2,
                "two_forward_operands_scale": [4, 4],
                "output_transform_scale": 16,
            },
            "base_inv": {
                "homogeneous_degree": -1,
                "input_transform_scale": 4,
                "phase1_adjugate_degree": 3,
                "phase1_adjugate_scale": 64,
                "denominator_degree": 4,
                "denominator_scale": 256,
                "batch_inverted_denominator_scale": "1/256",
                "final_output_transform_scale": "1/4",
            },
            "keypair_ratio": {
                "forward_operand_scale": 4,
                "baseinv_operand_scale": "1/4",
                "regular_basemul_output_scale": 1,
                "standalone_scale_pass": False,
            },
            "decapsulation_inverse_path": {
                "ciphertext_transform_scale": 4,
                "secret_forward_scale": 4,
                "scaled_basemul_arithmetic_scale": 16,
                "scaled_inverse_r3r3_factor": 4,
                "pre_normalization_scale": 64,
                "absorption": "fold inv64 into the existing final inverse normalization constant",
                "standalone_scale_pass": False,
            },
            "mod_q_inverses": {"inv4": inv4, "inv16": inv16, "inv64": inv64},
            "official_inverse_ninv_scale_mod_q": official_inverse_constant,
            "paper_decapsulation_ninv_scale_mod_q": candidate_inverse_constant,
            "paper_decapsulation_ninv_scale_centered": centered(candidate_inverse_constant),
            "montgomery_r_exponent_note": "arithmetic transform_scale is independent of Checkpoint E R^0/R^-1 contracts",
        },
        "proof": {
            "variant_linear_basis_checks": proof_counts,
            "total_variant_basis_checks": sum(proof_counts.values()),
            "paper_row_bijection": len(set(PAPER_P)) == 9,
            "adjusted_ntt16_rows_rekeyed": len(paper_rows),
            "basemul_baseinv_factors_rekeyed": sum(
                len(row["factors"]) for row in paper_factor_rows),
            "scale_homogeneity_checks": homogeneity_checks,
        },
        "gate_decision": {
            "scale_closure_without_standalone_pass": True,
            "assembly_authorized_next": True,
            "benchmark_available": False,
            "next": "implement R1 and R2 AVX2 under identical persistent-S/D ABI, then run paired NTT9 diagnostics",
        },
    }
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit("generated scaled R3R3 oracle is stale")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
