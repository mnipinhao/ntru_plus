#!/usr/bin/env python3
"""Prove the frozen-natural-Q T0 gauge map and exact chain lower bound."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

Q = 3457
QINV = 12929
R = pow(2, 16, Q)
GENERATOR = 7
BRANCH_OFFSETS = (20, 4)
ROOT9_RELABELLED_EXPONENT = 24 * 16 * 5
ROOT16_EXPONENT = 24 * 9
P_ORDER = (0, 3, 6, 1, 4, 7, 8, 2, 5)
FIRST_GROUPS = ((0, 3, 6), (1, 4, 7), (8, 2, 5))
FIRST_DESTINATIONS = ((0, 3, 6), (1, 4, 7), (2, 5, 8))
SECOND_GROUPS = ((0, 1, 2), (3, 4, 5), (6, 7, 8))
INT16 = (-32768, 32767)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, text: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            raise SystemExit(f"generated file is stale: {path}")
    else:
        path.write_text(text, encoding="utf-8")


def signed16(value: int) -> int:
    value &= 0xffff
    return value - 0x10000 if value >= 0x8000 else value


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def montgomery_constant(value: int) -> int:
    return centered(value * R)


def montgomery_reduce(value: int) -> int:
    low = signed16(signed16(value) * QINV)
    return (value - low * Q) >> 16


def mont_range(interval: list[int], constant: int) -> list[int]:
    values = [montgomery_reduce(value * constant)
              for value in range(interval[0], interval[1] + 1)]
    return [min(values), max(values)]


def add(left: list[int], right: list[int]) -> list[int]:
    return [left[0] + right[0], left[1] + right[1]]


def sub(left: list[int], right: list[int]) -> list[int]:
    return [left[0] - right[1], left[1] - right[0]]


def twice(value: list[int]) -> list[int]:
    return [2 * value[0], 2 * value[1]]


def reduce_range(interval: list[int]) -> list[int]:
    values = []
    for value in range(interval[0], interval[1] + 1):
        quotient = (value * 9 + (1 << 14)) >> 15
        values.append(value - quotient * Q)
    return [min(values), max(values)]


def paper_core(a: list[int], b: list[int], c: list[int],
               kappa: int) -> tuple[list[list[int]], dict]:
    sum_bc = add(b, c)
    difference = sub(b, c)
    product = mont_range(difference, kappa)
    twice_a = twice(a)
    base = sub(twice_a, sum_bc)
    outputs = [add(twice_a, twice(sum_bc)),
               add(base, product), sub(base, product)]
    return outputs, {
        "sum_b_plus_c": sum_bc,
        "difference_b_minus_c": difference,
        "kappa_difference": product,
        "twice_a": twice_a,
        "base": base,
    }


def require_i16(label: str, interval: list[int]) -> None:
    if interval[0] < INT16[0] or interval[1] > INT16[1]:
        raise SystemExit(f"{label} exceeds signed i16: {interval}")


def paper_r3_mod(a: int, b: int, c: int, kappa: int) -> tuple[int, int, int]:
    sum_bc = (b + c) % Q
    difference = (b - c) % Q
    product = kappa * difference % Q
    twice_a = 2 * a % Q
    base = (twice_a - sum_bc) % Q
    return ((twice_a + 2 * sum_bc) % Q,
            (base + product) % Q, (base - product) % Q)


def paper_ntt9_mod(values: list[int], kappa: int,
                   rho: int) -> list[int]:
    output = [0] * 9
    for group, destinations in zip(FIRST_GROUPS, FIRST_DESTINATIONS):
        result = paper_r3_mod(*(values[index] for index in group), kappa)
        for destination, value in zip(destinations, result):
            output[destination] = value
    output[0:3] = paper_r3_mod(output[0], output[1], output[2], kappa)
    output[3:6] = paper_r3_mod(
        output[3], rho * output[4] % Q,
        pow(rho, -1, Q) * output[5] % Q, kappa)
    output[6:9] = paper_r3_mod(
        output[6], pow(rho, -1, Q) * output[7] % Q,
        rho * output[8] % Q, kappa)
    return output


def ntt16_mod(values: list[int], row: dict, offset: int,
              absorb_beta: bool) -> list[int]:
    values = values[:]
    for name, distance in (("distance8", 8), ("distance4", 4),
                           ("distance2", 2), ("distance1", 1)):
        before = values[:]
        ratio = pow(GENERATOR, offset * distance, Q) if absorb_beta else 1
        for group, twiddle in enumerate(
                row["adjusted_ntt16_stages"][name]["mod_q"]):
            combined = twiddle * ratio % Q
            for lane in range(distance):
                left = group * 2 * distance + lane
                right = left + distance
                product = combined * before[right] % Q
                values[left] = (before[left] + product) % Q
                values[right] = (before[left] - product) % Q
    return values


def min_profile_repairs(values: list[int], root3: int) -> dict:
    best = 3
    witnesses = []
    for shift in range(3):
        powers = [pow(root3, shift * index, Q) for index in range(3)]
        for anchor in range(3):
            common = values[anchor] * pow(powers[anchor], -1, Q) % Q
            profile = [common * value % Q for value in powers]
            repairs = sum(left != right for left, right in zip(values, profile))
            if repairs < best:
                best, witnesses = repairs, []
            if repairs == best:
                witnesses.append({"shift": shift, "anchor": anchor,
                                  "common_gauge": common,
                                  "target_profile": profile})
    return {"minimum_standalone_normalizations": best,
            "witnesses": witnesses}


def candidate_ranges(offset: int, branch: int, scaled: dict,
                     kappa_mont: int, rho_mont: int,
                     rhoinv_mont: int, input_gauge_mod_q: int = 1) -> dict:
    row_inputs = []
    for row in range(9):
        source_h = 5 * row % 9
        alpha = montgomery_constant(
            pow(GENERATOR, 16 * offset * source_h, Q) * input_gauge_mod_q)
        values = []
        for low in range(-3, 5):
            for high in range(-3, 5):
                split = low + (-722 if branch == 0 else 723) * high
                values.append(split if source_h == 0
                              else montgomery_reduce(split * alpha))
        row_inputs.append([min(values), max(values)])

    first_outputs: list[list[int] | None] = [None] * 9
    first_proof = []
    for group, destinations in zip(FIRST_GROUPS, FIRST_DESTINATIONS):
        outputs, intermediates = paper_core(
            *(row_inputs[index] for index in group), kappa_mont)
        for name, interval in intermediates.items():
            require_i16(f"branch{branch}.first{group}.{name}", interval)
        for index, interval in enumerate(outputs):
            require_i16(f"branch{branch}.first{group}.output{index}", interval)
        reduced = [reduce_range(interval) for interval in outputs]
        for destination, interval in zip(destinations, reduced):
            first_outputs[destination] = interval
        first_proof.append({"rows": list(group), "outputs": outputs,
                            "outputs_after_barrett": reduced,
                            "intermediates": intermediates})
    first = [value for value in first_outputs if value is not None]

    r2_ranges = []
    second_proof = []
    second_twists = ((None, None), (rho_mont, rhoinv_mont),
                     (rhoinv_mont, rho_mont))
    for group_number, group in enumerate(SECOND_GROUPS):
        a = first[group[0]]
        b = first[group[1]]
        c = first[group[2]]
        twist_b, twist_c = second_twists[group_number]
        if twist_b is not None:
            b = mont_range(b, twist_b)
            c = mont_range(c, twist_c)
        outputs, intermediates = paper_core(a, b, c, kappa_mont)
        for name, interval in intermediates.items():
            require_i16(f"branch{branch}.second{group_number}.{name}", interval)
        for index, interval in enumerate(outputs):
            require_i16(f"branch{branch}.second{group_number}.output{index}", interval)
        r2_ranges.extend(outputs)
        second_proof.append({"group": group_number, "inputs": [a, b, c],
                             "outputs": outputs,
                             "intermediates": intermediates})

    ntt16_rows = []
    global_final = [INT16[1], INT16[0]]
    for row in scaled["paper_adjusted_ntt16_rows"]:
        physical = row["physical_row"]
        lanes = [r2_ranges[physical][:] for _ in range(16)]
        stages = []
        for name, distance in (("distance8", 8), ("distance4", 4),
                               ("distance2", 2), ("distance1", 1)):
            next_lanes: list[list[int] | None] = [None] * 16
            ratio = pow(GENERATOR, offset * distance, Q)
            combined_twiddles = []
            for group, twiddle in enumerate(
                    row["adjusted_ntt16_stages"][name]["mod_q"]):
                combined = twiddle * ratio % Q
                combined_twiddles.append(combined)
                constant = montgomery_constant(combined)
                for lane in range(distance):
                    left = group * 2 * distance + lane
                    right = left + distance
                    product = mont_range(lanes[right], constant)
                    next_lanes[left] = add(lanes[left], product)
                    next_lanes[right] = sub(lanes[left], product)
            lanes = [value for value in next_lanes if value is not None]
            overall = [min(value[0] for value in lanes),
                       max(value[1] for value in lanes)]
            require_i16(f"branch{branch}.row{physical}.{name}", overall)
            stages.append({"stage": name, "distance": distance,
                           "beta_ratio_mod_q": ratio,
                           "combined_twiddles_mod_q": combined_twiddles,
                           "overall_output_range": overall})
        final = [min(value[0] for value in lanes),
                 max(value[1] for value in lanes)]
        global_final = [min(global_final[0], final[0]),
                        max(global_final[1], final[1])]
        ntt16_rows.append({"physical_row": physical,
                           "frequency_p": row["frequency_p"],
                           "input_range": r2_ranges[physical],
                           "stages": stages, "final_range": final})
    return {"top_split_and_alpha_input_ranges": row_inputs,
            "first_layer": first_proof, "second_layer": second_proof,
            "r2_physical_output_ranges": r2_ranges,
            "ntt16_rows": ntt16_rows, "global_final_i16": global_final}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--component-oracle", type=Path, required=True)
    parser.add_argument("--scaled-oracle", type=Path, required=True)
    parser.add_argument("--paper-range", type=Path, required=True)
    parser.add_argument("--prod3-schedule", type=Path, required=True)
    parser.add_argument("--natural-schedule", type=Path, required=True)
    parser.add_argument("--qorder-price", type=Path, required=True)
    parser.add_argument("--top-split-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    component = json.loads(args.component_oracle.read_text(encoding="utf-8"))
    scaled = json.loads(args.scaled_oracle.read_text(encoding="utf-8"))
    paper_range = json.loads(args.paper_range.read_text(encoding="utf-8"))
    prod3 = json.loads(args.prod3_schedule.read_text(encoding="utf-8"))
    natural = json.loads(args.natural_schedule.read_text(encoding="utf-8"))
    price = json.loads(args.qorder_price.read_text(encoding="utf-8"))
    top_split = args.top_split_source.read_text(encoding="utf-8")
    if component["branch_offsets"] != list(BRANCH_OFFSETS):
        raise SystemExit("branch offsets changed")
    if price["winner"] != "natural-Q" or not price["all_four_delta_signs_agree"]:
        raise SystemExit("natural-Q is not frozen by four-setting evidence")
    if natural["decision"]["next"] != (
            "implement a namespaced natural-Q ASM candidate with current-Q control; "
            "prove exact planes/H1 bytes and linked ledger before pricing"):
        raise SystemExit("natural-Q schedule contract changed")
    if prod3["apples_to_apples_ledger"]["AOS_C1"]["montgomery_chains"] != 296:
        raise SystemExit("current 296-chain control changed")
    if "_mm256_set1_epi16(-722)" not in top_split or "low, high" not in top_split:
        raise SystemExit("top-split arithmetic changed")
    if not paper_range["proof"]["r2_adjusted_ntt16_all_stages_fit_signed16"]:
        raise SystemExit("control range proof reopened")

    root9 = pow(GENERATOR, ROOT9_RELABELLED_EXPONENT, Q)
    root16 = pow(GENERATOR, ROOT16_EXPONENT, Q)
    root3 = pow(GENERATOR, (Q - 1) // 3, Q)
    kappa_mod = scaled["kappa_mod_q"]
    kappa_mont = scaled["kappa_montgomery_signed"]
    rho = pow(GENERATOR, ROOT9_RELABELLED_EXPONENT, Q)
    rho_mont = montgomery_constant(rho)
    rhoinv_mont = montgomery_constant(pow(rho, -1, Q))

    branches = []
    basis_checks = 0
    output_checks = 0
    lower_bound_per_stream = []
    range_proofs = []
    for branch, offset in enumerate(BRANCH_OFFSETS):
        alpha_rows = [pow(GENERATOR, 16 * offset * (5 * row % 9), Q)
                      for row in range(9)]
        beta = [pow(GENERATOR, offset * q, Q) for q in range(16)]
        factorization_checks = 0
        for row in range(9):
            semantic_h = 5 * row % 9
            for q in range(16):
                direct = pow(GENERATOR, offset * (16 * semantic_h + q), Q)
                if direct != alpha_rows[row] * beta[q] % Q:
                    raise SystemExit(
                        f"T0 factorization failed b{branch} row{row} q{q}")
                factorization_checks += 1
        reindex9 = [shift for shift in range(9)
                    if all(alpha_rows[row] == pow(root9, shift * row, Q)
                           for row in range(9))]
        reindex16 = [shift for shift in range(16)
                     if all(beta[q] == pow(root16, shift * q, Q)
                            for q in range(16))]

        first_profiles = []
        for group in FIRST_GROUPS:
            profile = [alpha_rows[index] for index in group]
            proof = min_profile_repairs(profile, root3)
            first_profiles.append({"rows": list(group), "gauges": profile,
                                   **proof})
        first_minimum = sum(entry["minimum_standalone_normalizations"]
                            for entry in first_profiles)

        group0_minimum = 3
        group0_witness = None
        for pivots in itertools.product(*FIRST_GROUPS):
            profile = [alpha_rows[index] for index in pivots]
            proof = min_profile_repairs(profile, root3)
            repairs = proof["minimum_standalone_normalizations"]
            if repairs < group0_minimum:
                group0_minimum = repairs
                group0_witness = {"pivot_rows": list(pivots),
                                  "gauges": profile,
                                  "profile_proof": proof}
        per_stream = first_minimum + group0_minimum
        if first_minimum != 6 or group0_minimum != 2 or per_stream != 8:
            raise SystemExit("paper-R2 alpha normalization lower bound changed")
        lower_bound_per_stream.append(per_stream)

        # Full linear basis proof: the candidate omits beta from T0 and folds
        # each beta ratio into the already-present radix-2 twiddle chain.
        for source_h in range(9):
            source_row = (2 * source_h) % 9  # inverse of h=(5*row) mod 9
            for source_q in range(16):
                current_rows = [[0] * 16 for _ in range(9)]
                candidate_rows = [[0] * 16 for _ in range(9)]
                current_rows[source_row][source_q] = (
                    alpha_rows[source_row] * beta[source_q]) % Q
                candidate_rows[source_row][source_q] = alpha_rows[source_row]
                current_ntt9 = [[0] * 16 for _ in range(9)]
                candidate_ntt9 = [[0] * 16 for _ in range(9)]
                for q in range(16):
                    current_column = paper_ntt9_mod(
                        [current_rows[row][q] for row in range(9)],
                        kappa_mod, rho)
                    candidate_column = paper_ntt9_mod(
                        [candidate_rows[row][q] for row in range(9)],
                        kappa_mod, rho)
                    for row in range(9):
                        current_ntt9[row][q] = current_column[row]
                        candidate_ntt9[row][q] = candidate_column[row]
                for row_spec in scaled["paper_adjusted_ntt16_rows"]:
                    row = row_spec["physical_row"]
                    current_output = ntt16_mod(
                        current_ntt9[row], row_spec, offset, False)
                    candidate_output = ntt16_mod(
                        candidate_ntt9[row], row_spec, offset, True)
                    if current_output != candidate_output:
                        raise SystemExit(
                            f"basis differential failed b{branch} h{source_h} q{source_q} row{row}")
                    output_checks += 16
                basis_checks += 1

        range_proof = candidate_ranges(offset, branch, scaled, kappa_mont,
                                       rho_mont, rhoinv_mont)
        range_proofs.append({"branch": branch, "offset": offset,
                             **range_proof})
        branches.append({
            "branch": branch, "offset": offset,
            "alpha_row_gauges_mod_q": alpha_rows,
            "beta_q_gauges_mod_q": beta,
            "factorization_checks": factorization_checks,
            "pure_ntt9_frequency_shifts": reindex9,
            "pure_ntt16_frequency_shifts": reindex16,
            "pure_reindex_possible": bool(reindex9 or reindex16),
            "paper_r3_first_layer_lower_bound": first_profiles,
            "paper_r3_first_layer_minimum_normalizations": first_minimum,
            "untwisted_second_group_minimum_repairs": group0_minimum,
            "untwisted_second_group_witness": group0_witness,
            "per_branch_qblock_standalone_lower_bound": per_stream,
            "ntt16_beta_ratios": {
                name: pow(GENERATOR, offset * distance, Q)
                for name, distance in (("distance8", 8), ("distance4", 4),
                                       ("distance2", 2), ("distance1", 1))},
            "terminal_gauge_mod_q": beta[0],
        })

    if basis_checks != 288 or output_checks != 41472:
        raise SystemExit("full basis proof coverage changed")
    global_range = [min(entry["global_final_i16"][0] for entry in range_proofs),
                    max(entry["global_final_i16"][1] for entry in range_proofs)]
    require_i16("candidate.global", global_range)

    document = {
        "schema": "gt9x16-prod3-natural-q-t0-absorption-map/v1",
        "checkpoint": "GT9X16-PROD3-NATURAL-Q-T0-ABSORPTION-MAP",
        "frozen_contract": {
            "qorder": "C1-natural-Q", "transform_scale": 4,
            "montgomery_r_exponent": 0, "top_split_arithmetic_changed": False,
            "paper_R2_arithmetic_changed": False,
            "radix2_butterfly_DAG_changed": False,
            "runtime_qorder_routes_added": 0,
        },
        "factorization": {
            "identity": "g^(offset*(16h+q)) = alpha_h * beta_q",
            "alpha_h": "g^(16*offset*h)", "beta_q": "g^(offset*q)",
            "branches": branches,
            "pure_reindex_result": "rejected for both axes and both branches",
        },
        "selected_candidate": {
            "name": "T0-BETA-TO-RADIX2",
            "input_action": "multiply only alpha_h; h=0 is a raw load",
            "ntt9_action": "unchanged paper-R2; beta_q is a common q-column gauge",
            "ntt16_action": "replace each existing w by w*beta_(q+d)/beta_q = w*g^(offset*d)",
            "terminal_action": "no multiply, repair, reduction, or permutation; beta_0=1",
            "branch_specific_ntt16_constants": True,
            "new_routing": 0, "new_reductions": 0,
        },
        "exact_proofs": {
            "factorization_cells": 2 * 9 * 16,
            "mod_q_basis_inputs": basis_checks,
            "mod_q_output_cells": output_checks,
            "canonicalized_current_vs_candidate_exact": True,
            "raw_representatives_may_differ": True,
            "representative_contract": {
                "same_natural_q_lane_owner": True, "same_scale": 4,
                "same_montgomery_r_exponent": 0,
                "candidate_global_i16": global_range,
                "all_preoperations_signed_i16": True,
            },
        },
        "chain_lower_bound": {
            "method": "frozen paper-R2 DAG; each first R3 needs two gauge normalizations and its untwisted second-layer R3 needs two more; existing four second-layer twiddle chains absorb the other ratios",
            "per_branch_qblock": lower_bound_per_stream,
            "branch_qblocks_per_forward": 8,
            "standalone_minimum_per_forward": 64,
            "lower_bound_attained_by_selected_candidate": True,
        },
        "chain_ledger_per_forward": {
            "current": {"standalone_T0": 72, "NTT9_existing": 80,
                        "NTT16_existing": 144, "new_repair_or_final": 0,
                        "total": 296},
            "candidate": {"standalone_T0_or_normalization": 64,
                          "NTT9_existing": 80, "NTT16_existing": 144,
                          "new_repair_or_final": 0, "total": 288},
            "delta": {"standalone": -8, "NTT9": 0, "NTT16": 0,
                      "repair": 0, "total": -8},
            "encap_two_forward_delta": -16,
        },
        "range_proof": {
            "method": "closed signed intervals with exact constant-Montgomery enumeration; top-split [-3,4] cases exhaustively seed every branch/row",
            "branches": range_proofs, "candidate_global_i16": global_range,
            "control_global_i16": prod3["range_and_register_proof"]["global_final_i16"],
            "new_reductions": 0, "all_preoperations_signed_i16": True,
        },
        "decision": {
            "map_complete": True, "chain_saving_per_forward": 8,
            "chain_saving_per_encap": 16,
            "meets_minimum_schedule_threshold": True,
            "next": "T0-BETA-TO-RADIX2 exact schedule and constants; no ASM",
            "asm_authorized": False, "benchmark_authorized": False,
            "native_kem_authorized": False,
            "qorder_search_reopened": False,
        },
        "source_sha256": {name: sha256(path) for name, path in {
            "component_oracle": args.component_oracle,
            "scaled_oracle": args.scaled_oracle,
            "paper_range": args.paper_range,
            "prod3_schedule": args.prod3_schedule,
            "natural_schedule": args.natural_schedule,
            "qorder_price": args.qorder_price,
            "top_split_source": args.top_split_source,
        }.items()},
    }
    write(args.output, json.dumps(document, indent=2, sort_keys=True) + "\n",
          args.check)
    print("T0 absorption map: exact -8 chains/forward; schedule proof authorized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
