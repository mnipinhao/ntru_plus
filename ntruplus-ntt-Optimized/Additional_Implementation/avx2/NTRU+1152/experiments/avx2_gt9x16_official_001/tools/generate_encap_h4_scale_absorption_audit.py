#!/usr/bin/env python3
"""Enumerate exact scale gauges for H3 MA2 -> ciphertext H4."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import generate_gt9x16_prod3_t0_absorption_map as prod3

Q = 3457
QINV = 12929
R16 = 1 << 16
RMOD = R16 % Q
INV4 = pow(4, -1, Q)
INT16 = (-32768, 32767)
CORRECTION = (-1729, 1728)
TERMS = (
    (((0, 0),), ((1, 3), (2, 2), (3, 1))),
    (((0, 1), (1, 0)), ((2, 3), (3, 2))),
    (((0, 2), (1, 1), (2, 0)), ((3, 3),)),
    (((0, 3), (1, 2), (2, 1), (3, 0)), ()),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def signed16(value: int) -> int:
    value &= 0xffff
    return value - 0x10000 if value >= 0x8000 else value


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def montgomery_constant(value: int) -> int:
    return centered(value * RMOD)


def montgomery_reduce(value: int, constant: int) -> int:
    low = signed16(signed16(value * constant) * QINV)
    return (value * constant - low * Q) >> 16


def mont_interval(left: list[int], right: list[int]) -> list[int]:
    products = [a * b for a in left for b in right]
    high = [min(products) // R16, max(products) // R16]
    return [high[0] - CORRECTION[1], high[1] - CORRECTION[0]]


def add(*ranges: list[int]) -> list[int]:
    return [sum(value[0] for value in ranges),
            sum(value[1] for value in ranges)]


def barrett(value: int) -> int:
    quotient = (value * 9 + (1 << 14)) >> 15
    return value - quotient * Q


def exact_reduce_range(interval: list[int], method: str) -> list[int]:
    if method == "barrett":
        values = [barrett(value) for value in range(interval[0], interval[1] + 1)]
    elif method == "inv4-montgomery":
        constant = montgomery_constant(INV4)
        values = [montgomery_reduce(value, constant)
                  for value in range(interval[0], interval[1] + 1)]
    else:
        raise ValueError(method)
    return [min(values), max(values)]


def require_i16(label: str, interval: list[int]) -> None:
    if interval[0] < INT16[0] or interval[1] > INT16[1]:
        raise SystemExit(f"{label} exceeds signed i16: {interval}")


def forward_scale1_proof(t0_map: dict, scaled: dict) -> dict:
    rho = pow(prod3.GENERATOR, prod3.ROOT9_RELABELLED_EXPONENT, Q)
    rho_mont = prod3.montgomery_constant(rho)
    rhoinv_mont = prod3.montgomery_constant(pow(rho, -1, Q))
    ranges = []
    basis_checks = 0
    output_checks = 0
    constant_cases = 0
    alpha_sites = []
    for branch, offset in enumerate(prod3.BRANCH_OFFSETS):
        branch_map = t0_map["factorization"]["branches"][branch]
        alpha = branch_map["alpha_row_gauges_mod_q"]
        scaled_alpha = [value * INV4 % Q for value in alpha]
        for row, factor in enumerate(scaled_alpha):
            constant = montgomery_constant(factor)
            for value in range(-32768, 32768):
                if montgomery_reduce(value, constant) % Q != value * factor % Q:
                    raise SystemExit("scale-1 alpha Montgomery identity failed")
                constant_cases += 1
            alpha_sites.append({
                "branch": branch, "physical_row": row,
                "old_factor_mod_q": alpha[row], "new_factor_mod_q": factor,
                "new_montgomery_signed": constant,
                "new_qinv_signed16": signed16(constant * QINV),
                "was_raw_load": alpha[row] == 1,
            })

        # A full modular basis proof catches the tempting but invalid scheme
        # that scales only radix-2 twiddles: the common gauge must enter every
        # input cell before the linear transform.
        for source_h in range(9):
            source_row = 2 * source_h % 9
            for source_q in range(16):
                scale4_rows = [[0] * 16 for _ in range(9)]
                scale1_rows = [[0] * 16 for _ in range(9)]
                scale4_rows[source_row][source_q] = alpha[source_row]
                scale1_rows[source_row][source_q] = scaled_alpha[source_row]
                for row_spec in scaled["paper_adjusted_ntt16_rows"]:
                    row = row_spec["physical_row"]
                    column4 = []
                    column1 = []
                    for q in range(16):
                        out4 = prod3.paper_ntt9_mod(
                            [scale4_rows[r][q] for r in range(9)],
                            scaled["kappa_mod_q"], rho)
                        out1 = prod3.paper_ntt9_mod(
                            [scale1_rows[r][q] for r in range(9)],
                            scaled["kappa_mod_q"], rho)
                        column4.append(out4[row])
                        column1.append(out1[row])
                    final4 = prod3.ntt16_mod(column4, row_spec, offset, True)
                    final1 = prod3.ntt16_mod(column1, row_spec, offset, True)
                    if final1 != [value * INV4 % Q for value in final4]:
                        raise SystemExit("scale-1 producer basis proof failed")
                    output_checks += 16
                basis_checks += 1

        branch_range = prod3.candidate_ranges(
            offset, branch, scaled, scaled["kappa_montgomery_signed"],
            rho_mont, rhoinv_mont, INV4)
        require_i16(f"scale1 forward branch {branch}",
                    branch_range["global_final_i16"])
        ranges.append({"branch": branch, **branch_range})
    global_range = [min(item["global_final_i16"][0] for item in ranges),
                    max(item["global_final_i16"][1] for item in ranges)]
    return {
        "method": "multiply every post-top-split alpha_h input gauge by inv4; beta-absorbed radix-2 constants remain unchanged",
        "invalid_shortcut_rejected": "multiplying only radix-2 twiddles by inv4 does not scale untwiddled butterfly halves",
        "added_chains_per_forward": 8,
        "reason": "the two branch x four-qblock h=0 raw loads become Montgomery chains; the other 64 alpha chains are only rekeyed",
        "unchanged_existing_chains": 288,
        "new_total_forward_chains": 296,
        "mod_q_basis_inputs": basis_checks,
        "mod_q_output_cells": output_checks,
        "exact_constant_cases": constant_cases,
        "alpha_sites": alpha_sites,
        "branches": ranges,
        "global_i16": global_range,
        "all_preoperations_signed_i16": True,
        "output": "Natural-Q semantic scale1, Montgomery exponent 0",
    }


def h_conversion(factor_scale: int) -> dict:
    # The assembly constant is R^2 times the desired semantic h scale.
    factor_mod_q = RMOD * RMOD % Q * factor_scale % Q
    constant = centered(factor_mod_q)
    values = [montgomery_reduce(value, constant) for value in range(Q)]
    for value, result in enumerate(values):
        if result % Q != value * RMOD * factor_scale % Q:
            raise SystemExit("H3 h conversion identity failed")
    return {
        "semantic_scale": factor_scale, "constant_mod_q": factor_mod_q,
        "constant_signed": constant,
        "qinv_signed16": signed16(constant * QINV),
        "output_range_i16": [min(values), max(values)],
        "exact_input_cases": Q,
        "chain_positions_changed": False,
    }


def ma2_range(name: str, r_range: list[int], m_range: list[int],
              h_range: list[int], output_scale: int,
              f0_schedule: dict) -> dict:
    global_pre = [0, 0]
    coefficient_bounds = []
    for coefficient, (plain, wrapped) in enumerate(TERMS):
        products = [mont_interval(h_range, r_range) for _ in plain]
        wrapped_products = [mont_interval(h_range, r_range) for _ in wrapped]
        accumulator = list(m_range)
        steps = [list(accumulator)]
        for product in products:
            accumulator = add(accumulator, product)
            steps.append(list(accumulator))
        wrapped_sum = [0, 0]
        wrapped_steps = []
        for product in wrapped_products:
            wrapped_sum = add(wrapped_sum, product)
            wrapped_steps.append(list(wrapped_sum))
        if wrapped_products:
            # All lambda lanes are centered lambda*R constants. Use the exact
            # global constant envelope; lane-specific replay is unnecessary
            # for safety and would only tighten this closed proof.
            lambdas = []
            for tile in f0_schedule["semantic_tiles"]:
                lambdas.extend(centered(v * RMOD)
                               for v in tile["planes"][coefficient]["lambda_mod_q"])
            wrapped_scaled = mont_interval(wrapped_sum,
                                            [min(lambdas), max(lambdas)])
            accumulator = add(accumulator, wrapped_scaled)
            steps.append(list(accumulator))
        else:
            wrapped_scaled = [0, 0]
        for index, interval in enumerate(steps + wrapped_steps):
            require_i16(f"{name}.c{coefficient}.step{index}", interval)
        global_pre = [min(global_pre[0], accumulator[0]),
                      max(global_pre[1], accumulator[1])]
        coefficient_bounds.append({
            "coefficient": coefficient, "pre_terminal": accumulator,
            "accumulator_steps": steps, "wrapped_sum_steps": wrapped_steps,
            "wrapped_after_lambda": wrapped_scaled,
        })
    reduction = "inv4-montgomery" if output_scale == 4 else "barrett"
    post = exact_reduce_range(global_pre, reduction)
    if not (-Q < post[0] <= post[1] < Q):
        raise SystemExit(f"{name} one-pass terminal reduction insufficient: {post}")
    return {
        "global_pre_terminal": global_pre,
        "terminal_operation": reduction,
        "global_post_terminal": post,
        "all_preoperations_signed_i16": True,
        "one_terminal_vector_operation_per_plane": True,
        "coefficient_bounds": coefficient_bounds,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--t0-map", type=Path, required=True)
    parser.add_argument("--scaled-oracle", type=Path, required=True)
    parser.add_argument("--f0-schedule", type=Path, required=True)
    parser.add_argument("--ma2-range", type=Path, required=True)
    parser.add_argument("--h3-schedule", type=Path, required=True)
    parser.add_argument("--h4-map", type=Path, required=True)
    parser.add_argument("--hash-audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    t0_map = json.loads(args.t0_map.read_text())
    scaled = json.loads(args.scaled_oracle.read_text())
    f0_schedule = json.loads(args.f0_schedule.read_text())
    current_range = json.loads(args.ma2_range.read_text())
    h3 = json.loads(args.h3_schedule.read_text())
    h4 = json.loads(args.h4_map.read_text())
    hash_audit = json.loads(args.hash_audit.read_text())
    if h3["ma2"]["candidate_ledger"]["h_r2_montgomery"] != 72:
        raise SystemExit("H3 h-R2 chain count changed")
    if len(h4["terminal_order"]) != 72:
        raise SystemExit("H4 terminal vector count changed")
    if hash_audit["scheduled_vs_linked"]["inv4_montgomery_instructions"]["linked"] != 288:
        raise SystemExit("H1 r-hash inv4 count changed")

    scale1 = forward_scale1_proof(t0_map, scaled)
    current_forward = t0_map["range_proof"]["candidate_global_i16"]
    scale1_forward = scale1["global_i16"]
    h1 = h_conversion(1)
    h_quarter = h_conversion(INV4)

    current_ma2 = {
        "global_pre_terminal": current_range["global_pre_inv4"],
        "terminal_operation": "inv4-montgomery",
        "global_post_terminal": current_range["global_post_inv4"],
        "all_preoperations_signed_i16": True,
    }
    local_ma2 = ma2_range("M0-C1", current_forward, scale1_forward,
                          h_quarter["output_range_i16"], 1, f0_schedule)
    caller_ma2 = ma2_range("M0-C2", scale1_forward, scale1_forward,
                           h1["output_range_i16"], 1, f0_schedule)

    variants = [
        {
            "id": "M0-C0-current-scale4", "r_scale": 4, "m_scale": 4,
            "h_semantic_scale": 1, "ma2_output_scale": 4,
            "producer_added_vector_chains_per_encap": 0,
            "h3_rekey_only": False,
            "h4_terminal": {"montgomery_vectors": 72, "barrett_vectors": 0,
                            "instructions": 288},
            "r_hash_terminal": {"montgomery_vectors": 72, "barrett_vectors": 0,
                                "instructions": 288},
            "caller_terminal_plus_added_instructions": 576,
            "range": current_ma2,
        },
        {
            "id": "M0-C1-h4-local", "r_scale": 4, "m_scale": 1,
            "h_semantic_scale": INV4, "ma2_output_scale": 1,
            "producer_added_vector_chains_per_encap": 8,
            "h3_rekey_only": True,
            "h4_terminal": {"montgomery_vectors": 0, "barrett_vectors": 72,
                            "instructions": 216},
            "r_hash_terminal": {"montgomery_vectors": 72, "barrett_vectors": 0,
                                "instructions": 288},
            "caller_terminal_plus_added_instructions": 536,
            "range": local_ma2,
        },
        {
            "id": "M0-C2-caller-wide", "r_scale": 1, "m_scale": 1,
            "h_semantic_scale": 1, "ma2_output_scale": 1,
            "producer_added_vector_chains_per_encap": 16,
            "h3_rekey_only": False,
            "h4_terminal": {"montgomery_vectors": 0, "barrett_vectors": 72,
                            "instructions": 216},
            "r_hash_terminal": {"montgomery_vectors": 0, "barrett_vectors": 72,
                                "instructions": 216},
            "caller_terminal_plus_added_instructions": 496,
            "range": caller_ma2,
        },
    ]
    variants[0]["delta_instructions_vs_current"] = 0
    variants[1]["delta_instructions_vs_current"] = -40
    variants[2]["delta_instructions_vs_current"] = -80

    document = {
        "schema": "encap-h4-scale-absorption-audit/v1",
        "checkpoint": "ENCAP-MA2-CT-EGRESS-H4-M0-SCALE-GAUGE",
        "frozen_contract": {
            "decomposition": "persistent-AoS GT9x16",
            "qorder": "Natural-Q", "t0_beta": True,
            "ma2_formula_changed": False, "lambda_placement_changed": False,
            "terminal_owner_changed": False, "asm_written": False,
        },
        "scale_algebra": {
            "current": "Mont(hR,4r)=4hr; add 4m; terminal Mont(inv4R)",
            "h4_local": "Mont(hR/4,4r)=hr; add m; terminal Barrett",
            "caller_wide": "Mont(hR,r)=hr; add m; terminal Barrett; r-hash also Barrett",
            "lambda": "lambdaR constants preserve the common product scale and cannot alone scale the plain terms or m addend",
            "uniform_scale_rule": "every summand of c=hr+m must have one common scale",
        },
        "producer_scale1": scale1,
        "h3_constants": {"scale1_h": h1, "quarter_scale_h": h_quarter},
        "variants": variants,
        "selection": {
            "h4_local_minimum": "M0-C1-h4-local",
            "full_encap_minimum": "M0-C2-caller-wide",
            "reason": "caller-wide scale1 pays 16 added producer vector chains but replaces both 72-vector inv4 terminals with cheaper Barrett reductions",
            "important_correction": "scale absorption removes inv4 Montgomery chains, not the need to reduce wide lazy representatives before 12-bit packing",
            "minimum_h4_extra_montgomery_vectors": 0,
            "mandatory_h4_reduction_vectors": 72,
        },
        "machine_budget": {
            "montgomery_vector_chain_instructions": 4,
            "barrett_vector_instructions": 3,
            "current_terminal_and_added_instructions": 576,
            "selected_terminal_and_added_instructions": 496,
            "selected_delta_instructions_per_encap": -80,
            "routing_delta": 0, "data_load_store_delta": 0,
            "constant_memory_operand_delta_per_encap": 32,
            "minimum_new_shared_constant_table_bytes": 64,
            "new_temporary_vectors": 0,
            "note": "linked ASM may correct instruction taxonomy; this is a pre-ASM structural budget",
        },
        "decision": {
            "m0_complete": True,
            "scale4_terminal_inv4_is_not_mandatory": True,
            "zero_terminal_reduction_is_rejected": True,
            "selected_for_h4_m1_mapping": "M0-C2-caller-wide",
            "next": "H4-M1 terminal ownership/orientation search under caller-wide scale1; no ASM",
            "asm_authorized": False, "benchmark_authorized": False,
            "native_kem_authorized": False,
        },
        "source_sha256": {name: sha256(path) for name, path in {
            "t0_map": args.t0_map, "scaled_oracle": args.scaled_oracle,
            "f0_schedule": args.f0_schedule, "ma2_range": args.ma2_range,
            "h3_schedule": args.h3_schedule, "h4_map": args.h4_map,
            "hash_audit": args.hash_audit,
        }.items()},
    }
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit(f"generated file is stale: {args.output}")
    else:
        args.output.write_text(rendered)
    print("H4-M0: caller-wide scale1 selected; -144 inv4 vectors +144 Barrett vectors +16 producer chains, predicted -80 instructions/Encap")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
