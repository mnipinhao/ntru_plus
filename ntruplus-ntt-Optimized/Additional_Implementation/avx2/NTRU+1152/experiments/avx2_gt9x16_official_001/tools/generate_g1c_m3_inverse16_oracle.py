#!/usr/bin/env python3
"""Generate the G1C-M3 inverse16 pairing, range, and three-way cost contract."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

Q = 3457
QINV = 12929
R = pow(2, 16, Q)
I16 = [-32768, 32767]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def signed16(value: int) -> int:
    value %= 1 << 16
    return value - (1 << 16) if value >= 1 << 15 else value


def montgomery_reduce(value: int) -> int:
    low = signed16(signed16(value) * QINV)
    return (value - low * Q) >> 16


def montgomery_range(interval: list[int], constant: int) -> list[int]:
    values = (montgomery_reduce(value * constant)
              for value in range(interval[0], interval[1] + 1))
    first = next(values)
    low = high = first
    for value in values:
        low = min(low, value)
        high = max(high, value)
    return [low, high]


def fits_i16(interval: list[int]) -> bool:
    return I16[0] <= interval[0] and interval[1] <= I16[1]


def propagate_range(row: dict, input_interval: list[int]) -> dict:
    lanes = [input_interval[:] for _ in range(16)]
    stages = []
    first_failure = None
    for distance in (1, 2, 4, 8):
        stage = row["adjusted_ntt16_stages"][f"distance{distance}"]
        inverse = [pow(value, -1, Q) for value in stage["mod_q"]]
        inverse_mont = [centered(value * R) for value in inverse]
        output = [None] * 16
        butterflies = []
        for block, base in enumerate(range(0, 16, 2 * distance)):
            constant = inverse_mont[block]
            for lane_in_half in range(distance):
                left_index = base + lane_in_half
                right_index = left_index + distance
                left, right = lanes[left_index], lanes[right_index]
                sum_interval = [left[0] + right[0], left[1] + right[1]]
                difference = [left[0] - right[1], left[1] - right[0]]
                twisted = montgomery_range(difference, constant)
                output[left_index] = sum_interval
                output[right_index] = twisted
                butterfly = {
                    "physical_lanes": [left_index, right_index],
                    "constant_index": block,
                    "inverse_twiddle_mod_q": inverse[block],
                    "left_input": left,
                    "right_input": right,
                    "sum_output": sum_interval,
                    "difference_before_montgomery": difference,
                    "twisted_difference_output": twisted,
                    "sum_fits_signed_i16": fits_i16(sum_interval),
                    "difference_fits_signed_i16": fits_i16(difference),
                    "twisted_output_fits_signed_i16": fits_i16(twisted),
                }
                butterflies.append(butterfly)
                if first_failure is None:
                    for operation, interval in (("sum", sum_interval),
                                                ("difference", difference)):
                        if not fits_i16(interval):
                            first_failure = {
                                "distance": distance,
                                "operation": operation,
                                "physical_lanes": [left_index, right_index],
                                "interval": interval,
                            }
                            break
        lanes = output
        stages.append({
            "distance": distance,
            "output_intervals_by_physical_lane": lanes,
            "register_state_overall": [
                min(interval[0] for interval in lanes),
                max(interval[1] for interval in lanes),
            ],
            "sum_output_overall": [
                min(item["sum_output"][0] for item in butterflies),
                max(item["sum_output"][1] for item in butterflies),
            ],
            "difference_before_montgomery_overall": [
                min(item["difference_before_montgomery"][0] for item in butterflies),
                max(item["difference_before_montgomery"][1] for item in butterflies),
            ],
            "twisted_difference_output_overall": [
                min(item["twisted_difference_output"][0] for item in butterflies),
                max(item["twisted_difference_output"][1] for item in butterflies),
            ],
            "all_pre_montgomery_operations_fit_signed_i16": all(
                item["sum_fits_signed_i16"] and item["difference_fits_signed_i16"]
                for item in butterflies),
            "all_twisted_outputs_fit_signed_i16": all(
                item["twisted_output_fits_signed_i16"] for item in butterflies),
        })
    return {
        "input_each_lane": input_interval,
        "stages": stages,
        "first_independent_interval_failure": first_failure,
        "full_lazy_i16_authorized_by_independent_intervals": first_failure is None,
        "interpretation": (
            "A failure rejects proof by independent envelopes; it does not prove "
            "producer-real correlated states overflow. No reduction is authorized "
            "until that correlation is measured and mechanically bounded."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scaled-oracle", type=Path, required=True)
    parser.add_argument("--m2-result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--header", type=Path, required=True)
    parser.add_argument("--asm-constants", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    scaled = json.loads(args.scaled_oracle.read_text())
    m2 = json.loads(args.m2_result.read_text())
    if m2["paired"]["median_candidate_minus_control_cycles"] >= 0:
        raise SystemExit("M3 requires a negative M2 linked-boundary delta")

    rows = []
    all_pairs = {}
    inverse_constants = []
    for row in scaled["paper_adjusted_ntt16_rows"]:
        row_index = row["physical_row"]
        stage_records = []
        row_constants = []
        for distance in (1, 2, 4, 8):
            forward = row["adjusted_ntt16_stages"][f"distance{distance}"]["mod_q"]
            inverse = [pow(value, -1, Q) for value in forward]
            expanded_inverse_mont = []
            pairs = []
            for block, base in enumerate(range(0, 16, 2 * distance)):
                for lane_in_half in range(distance):
                    left, right = base + lane_in_half, base + lane_in_half + distance
                    zeta, zeta_inverse = forward[block], inverse[block]
                    expanded_inverse_mont.append(centered(zeta_inverse * R))
                    product = [
                        [(1 + zeta_inverse * zeta) % Q,
                         (zeta - zeta) % Q],
                        [(zeta_inverse - zeta_inverse) % Q,
                         (zeta_inverse * zeta + 1) % Q],
                    ]
                    if product != [[2, 0], [0, 2]]:
                        raise SystemExit(f"row {row_index} distance {distance} inverse failure")
                    pairs.append({
                        "physical_lanes": [left, right],
                        "constant_index": block,
                        "forward_twiddle_mod_q": zeta,
                        "inverse_twiddle_mod_q": zeta_inverse,
                        "local_identity_mod_q": "I_d(z) * F_d(z) = 2*I",
                    })
            if sorted(lane for pair in pairs for lane in pair["physical_lanes"]) != list(range(16)):
                raise SystemExit(f"distance {distance} does not cover 16 lanes")
            stage_records.append({"distance": distance, "pairs": pairs})
            row_constants.append(expanded_inverse_mont)
            all_pairs.setdefault(str(distance), pairs)
        rows.append({
            "physical_row": row_index,
            "frequency_p": row["frequency_p"],
            "inverse_stages": stage_records,
            "range": {
                "BMScale_Rminus1": propagate_range(row, [-13824, 13824]),
                "BaseInv_R0_quarter_scale": propagate_range(row, [-3456, 3456]),
            },
        })
        inverse_constants.append(row_constants)

    document = {
        "schema": "gt-g1c-m3-inverse16-contract/v1",
        "checkpoint": "G1C-M3A-three-way-inverse16-oracle",
        "parameter": 1152,
        "inverse_order": [1, 2, 4, 8],
        "principle": "derive each inverse linear map in current physical q order; do not copy Official textual stage order",
        "dimensions": {
            "inverse_butterfly_pairing": "physical-q lane dimension",
            "terminal_coefficient": "independent dimension",
            "forward_persistent_sd": "separate representation; pair terminology is not interchangeable",
        },
        "rows": rows,
        "pairing_shape_control": all_pairs,
        "variants": {
            "M3-C0": {
                "role": "exact full materialized control",
                "path": "BMScale -> materialized boundary -> inverse D1/D2/D4/D8 with current inter-stage representation",
            },
            "M3-C1": {
                "role": "linked-D1 decomposition control",
                "path": "BMScale live -> linked D1 -> materialized boundary -> current D2/D4/D8",
                "expected_question": "does the M2 edge credit survive a complete inverse16 caller path?",
            },
            "M3-C2": {
                "role": "persistent split-state candidate",
                "path": "BMScale live -> split D1 -> split D2 -> split D4 -> split D8 -> required final boundary",
                "expected_question": "what credit belongs specifically to persistent inverse state?",
            },
        },
        "paired_decomposition": {
            "C1_minus_C0": "linked BMScale-to-D1 boundary credit in the full inverse16 context",
            "C2_minus_C1": "persistent inverse-state routing/scheduling credit",
            "C2_minus_C0": "total edge plus persistent-state delta; not sufficient alone for attribution",
        },
        "required_static_table": [
            "stores", "reloads", "vperm2i128", "vpunpck*", "vpblend*",
            "shifts", "Montgomery_chains", "constant_loads", "peak_live_YMM",
        ],
        "range_gate": {
            "BMScale_first_failure": rows[0]["range"]["BMScale_Rminus1"]["first_independent_interval_failure"],
            "all_rows_same_failure_shape": all(
                row["range"]["BMScale_Rminus1"]["first_independent_interval_failure"]["distance"] == 2
                for row in rows),
            "asm_authorized": False,
            "next_required_evidence": "producer-real correlated register-state oracle through D1/D2/D4/D8; insert no convenience reduction beforehand",
        },
        "independent_price_ledger": {
            "F1_forward_producer_debt_cycles_each": 58.5,
            "F1_two_forward_debt_cycles": 117.0,
            "F5_BMScale_to_inverse_D1_credit_cycles": m2["paired"]["median_candidate_minus_control_cycles"],
            "accounting_rule": "F1 and F5 are orthogonal experiments; do not net them until G2 names a complete path containing both",
            "current_architecture_hypothesis": "retain F0 persistent forward and adapt consumer-specific arithmetic/inverse edges",
        },
        "benchmark_policy": "repository-local diagnostic only; no SUPERCOP or production claim",
        "source_sha256": {
            "scaled_oracle": sha256(args.scaled_oracle),
            "m2_result": sha256(args.m2_result),
        },
    }
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    header_lines = [
        "#ifndef NTRUPLUS1152_EXP001_G1C_M3_INVERSE16_H",
        "#define NTRUPLUS1152_EXP001_G1C_M3_INVERSE16_H",
        "#include <stdint.h>",
        "static const int ntruplus1152_exp001_g1c_m3_distances[4] = {1, 2, 4, 8};",
        "static const int16_t ntruplus1152_exp001_g1c_m3_inverse_mont[9][4][8] = {",
    ]
    for row_constants in inverse_constants:
        header_lines.append("  {")
        for constants in row_constants:
            header_lines.append("    {" + ", ".join(map(str, constants)) + "},")
        header_lines.append("  },")
    header_lines.extend(["};", "#endif", ""])
    header = "\n".join(header_lines)
    asm_lines = [
        "/* Generated M3 inverse16 shuffles, identity, and stage constants. */",
        ".section .rodata",
        ".p2align 5",
        ".Lgt_g1c_m3_swap_d2:",
        "  .byte 4,5,6,7,0,1,2,3,12,13,14,15,8,9,10,11,20,21,22,23,16,17,18,19,28,29,30,31,24,25,26,27",
        ".p2align 5",
        ".Lgt_g1c_m3_swap_d4:",
        "  .byte 8,9,10,11,12,13,14,15,0,1,2,3,4,5,6,7,24,25,26,27,28,29,30,31,16,17,18,19,20,21,22,23",
        ".p2align 5",
        ".Lgt_g1c_m3_identity:",
        "  .rept 16", "  .short -147", "  .endr",
        ".Lgt_g1c_m3_identity_qinv:",
        "  .rept 16", "  .short -19", "  .endr",
    ]
    for row_index, row_constants in enumerate(inverse_constants):
        for stage_index, distance in enumerate((1, 2, 4, 8)):
            zeta_lanes = [0] * 16
            for pair_index, (left, right) in enumerate(
                    (tuple(item["physical_lanes"])
                     for item in rows[row_index]["inverse_stages"][stage_index]["pairs"])):
                constant = row_constants[stage_index][pair_index]
                zeta_lanes[left] = constant
                zeta_lanes[right] = -constant
            qinv_lanes = [signed16(value * QINV) for value in zeta_lanes]
            asm_lines.extend([
                ".p2align 5",
                f".Lgt_g1c_m3_row{row_index}_d{distance}_zeta:",
                "  .short " + ", ".join(map(str, zeta_lanes)),
                f".Lgt_g1c_m3_row{row_index}_d{distance}_qinv:",
                "  .short " + ", ".join(map(str, qinv_lanes)),
            ])
    asm_constants = "\n".join(asm_lines) + "\n"
    if args.check:
        if (not args.output.is_file() or args.output.read_text() != rendered or
                not args.header.is_file() or args.header.read_text() != header or
                not args.asm_constants.is_file() or
                args.asm_constants.read_text() != asm_constants):
            raise SystemExit("generated G1C-M3 inverse16 oracle is stale")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered)
    args.header.write_text(header)
    args.asm_constants.write_text(asm_constants)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
