#!/usr/bin/env python3
"""Generate the G1C adjusted inverse distance-1 component/twiddle/range oracle."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

Q = 3457
QINV = 12929
R = pow(2, 16, Q)
I16 = (-32768, 32767)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def signed16(value: int) -> int:
    value %= 1 << 16
    return value - (1 << 16) if value >= (1 << 15) else value


def montgomery_reduce(value: int) -> int:
    low = signed16(signed16(value) * QINV)
    return (value - low * Q) >> 16


def montgomery_range(interval: list[int], constant: int) -> list[int]:
    values = [montgomery_reduce(value * constant)
              for value in range(interval[0], interval[1] + 1)]
    return [min(values), max(values)]


def add_range(left: list[int], right: list[int]) -> list[int]:
    return [left[0] + right[0], left[1] + right[1]]


def sub_range(left: list[int], right: list[int]) -> list[int]:
    return [left[0] - right[1], left[1] - right[0]]


def require_i16(label: str, interval: list[int]) -> None:
    if interval[0] < I16[0] or interval[1] > I16[1]:
        raise SystemExit(f"{label} exceeds signed i16: {interval}")


def position(branch: int, row: int, terminal_pair: int, stream: int,
             coefficient_half: int, q_pair: int) -> int:
    return (((((branch * 9 + row) * 2 + terminal_pair) * 2 + stream) * 16)
            + coefficient_half * 8 + q_pair)


def emit_words(label: str, values: list[int]) -> str:
    return f".p2align 5\n{label}:\n  .word " + ", ".join(map(str, values)) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pipeline-layout", type=Path, required=True)
    parser.add_argument("--scaled-oracle", type=Path, required=True)
    parser.add_argument("--g1c-audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--header", type=Path, required=True)
    parser.add_argument("--asm-constants", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    layout = json.loads(args.pipeline_layout.read_text())
    scaled = json.loads(args.scaled_oracle.read_text())
    g1c = json.loads(args.g1c_audit.read_text())
    if g1c["prototype_gate"]["asm_authorized"] is not False:
        raise SystemExit("G1C0 must remain closed until this oracle is generated")
    if layout["candidates"]["persistent_pair_sd"]["inverse_conversion"] != \
            "zero only for a paired adjusted inverse NTT16 proven to consume S/D directly":
        raise SystemExit("persistent-pair inverse contract changed")

    cell_by_key = {
        (cell["branch"], cell["gt_row_physical_trit_reversed"],
         cell["ntt16_lane_physical_bit_reversed"]): cell
        for cell in layout["cells"]
    }
    q_order = layout["physical_lane_to_mathematical_q"]
    rows = []
    butterflies = []
    all_inputs: list[int] = []
    all_outputs: list[int] = []
    asm = "/* Generated G1C adjusted inverse distance-1 constants. */\n.section .rodata\n"
    header_rows = []

    for row_record in scaled["paper_adjusted_ntt16_rows"]:
        row = row_record["physical_row"]
        frequency_p = row_record["frequency_p"]
        forward = row_record["adjusted_ntt16_stages"]["distance1"]["mod_q"]
        inverse = [pow(value, -1, Q) for value in forward]
        inverse_mont = [centered(value * R) for value in inverse]
        inverse_qinv = [signed16(value * QINV) for value in inverse_mont]
        if any((left * right) % Q != 1 for left, right in zip(forward, inverse)):
            raise SystemExit(f"row {row} inverse twiddle failure")
        for zeta, zeta_inverse in zip(forward, inverse):
            forward_matrix = ((1, zeta), (1, -zeta))
            inverse_matrix = ((1, 1), (zeta_inverse, -zeta_inverse))
            product = [[sum(inverse_matrix[i][k] * forward_matrix[k][j]
                            for k in range(2)) % Q for j in range(2)]
                       for i in range(2)]
            if product != [[2, 0], [0, 2]]:
                raise SystemExit(f"row {row} local inverse matrix failure")
        rows.append({
            "physical_row": row,
            "frequency_p": frequency_p,
            "forward_distance1_twiddle_mod_q": forward,
            "inverse_distance1_twiddle_mod_q": inverse,
            "inverse_distance1_twiddle_montgomery_signed": inverse_mont,
            "inverse_distance1_twiddle_qinv_signed16": inverse_qinv,
        })
        expanded_mont = inverse_mont + inverse_mont
        expanded_qinv = inverse_qinv + inverse_qinv
        header_rows.append((expanded_mont, expanded_qinv))
        asm += emit_words(f".Lgt_g1c_row{row}_inverse_distance1_zeta", expanded_mont)
        asm += emit_words(f".Lgt_g1c_row{row}_inverse_distance1_qinv", expanded_qinv)

        for branch in range(2):
            for terminal_pair in range(2):
                for coefficient_half in range(2):
                    coefficient = 2 * terminal_pair + coefficient_half
                    for q_pair in range(8):
                        even_lane = 2 * q_pair
                        odd_lane = even_lane + 1
                        even_cell = cell_by_key[(branch, row, even_lane)]
                        odd_cell = cell_by_key[(branch, row, odd_lane)]
                        input_even = position(branch, row, terminal_pair, 0,
                                              coefficient_half, q_pair)
                        input_odd = position(branch, row, terminal_pair, 1,
                                             coefficient_half, q_pair)
                        output_sum = position(branch, row, terminal_pair, 0,
                                              coefficient_half, q_pair)
                        output_twisted_difference = position(
                            branch, row, terminal_pair, 1, coefficient_half, q_pair)
                        all_inputs.extend((input_even, input_odd))
                        all_outputs.extend((output_sum, output_twisted_difference))
                        butterflies.append({
                            "branch": branch,
                            "physical_row": row,
                            "frequency_p": frequency_p,
                            "terminal_pair": terminal_pair,
                            "terminal_coefficient": coefficient,
                            "packed_coefficient_half": coefficient_half,
                            "q_pair": q_pair,
                            "physical_lanes": [even_lane, odd_lane],
                            "frequency_q": [q_order[even_lane], q_order[odd_lane]],
                            "input_positions_i16": {
                                "forward_even_output": input_even,
                                "forward_odd_output": input_odd,
                            },
                            "output_positions_i16": {
                                "twice_pre_distance1_left": output_sum,
                                "twice_pre_distance1_right": output_twisted_difference,
                            },
                            "official_component_positions_i16": [
                                even_cell["positions"][coefficient]["official"]["position_i16"],
                                odd_cell["positions"][coefficient]["official"]["position_i16"],
                            ],
                            "factor_roots_mod_q": [even_cell["factor_mod_q"],
                                                   odd_cell["factor_mod_q"]],
                            "forward_twiddle_mod_q": forward[q_pair],
                            "inverse_twiddle_mod_q": inverse[q_pair],
                            "local_matrix_identity_mod_q": "I1(z) * F1(z) = 2*I",
                        })

    if sorted(all_inputs) != list(range(1152)) or sorted(all_outputs) != list(range(1152)):
        raise SystemExit("G1C distance-1 mapping does not cover exactly 1,152 cells")
    if len(butterflies) != 576:
        raise SystemExit("G1C distance-1 must contain 576 scalar butterflies")

    range_contracts = {}
    for name, input_range in {
        "BMScale_Rminus1_scale16": [-13824, 13824],
        "BaseInv_R0_scale_quarter": [-3456, 3456],
    }.items():
        sum_interval = add_range(input_range, input_range)
        difference_interval = sub_range(input_range, input_range)
        require_i16(f"{name}.sum", sum_interval)
        require_i16(f"{name}.difference", difference_interval)
        per_row = []
        products = []
        for row in rows:
            row_products = [montgomery_range(difference_interval, constant)
                            for constant in row["inverse_distance1_twiddle_montgomery_signed"]]
            for index, interval in enumerate(row_products):
                require_i16(f"{name}.row{row['physical_row']}.twisted_difference{index}", interval)
            products.extend(row_products)
            per_row.append({"physical_row": row["physical_row"],
                            "twisted_difference_ranges": row_products})
        range_contracts[name] = {
            "input_each_vector": input_range,
            "sum_output": sum_interval,
            "difference_before_montgomery": difference_interval,
            "twisted_difference_overall": [min(value[0] for value in products),
                                            max(value[1] for value in products)],
            "per_row": per_row,
            "all_intermediates_fit_signed_i16": True,
            "extra_reduction_required": False,
        }

    document = {
        "schema": "gt-g1c-adjusted-inverse-head/v1",
        "checkpoint": "G1C1-adjusted-inverse-distance1-oracle",
        "parameter": 1152,
        "factorization_boundary": {
            "official_source_level6_reused": False,
            "reason": "GT reverses its own adjusted NTT16 factorization; source-level Official stage order is not copied",
            "candidate_first_layer": "inverse of adjusted forward distance1",
            "input_layout": "persistent_pair_sd",
            "output_layout": "inverse_distance1_pair: same physical vectors, new twice-pre-distance1 semantics",
            "standalone_conversion": False,
        },
        "butterfly": {
            "forward": ["S = a + z*b", "D = a - z*b"],
            "inverse_head": ["A2 = S + D", "B2 = z^-1*(S - D)"],
            "identity": ["A2 = 2*a", "B2 = 2*b"],
            "division_by_two": False,
            "montgomery_r_exponent_change": 0,
        },
        "scale_transition": {
            "BMScale": {"input_transform_scale": 16, "input_R_exponent": -1,
                         "output_transform_scale": 32, "output_R_exponent": -1},
            "BaseInv": {"input_transform_scale": "1/4", "input_R_exponent": 0,
                        "output_transform_scale": "1/2", "output_R_exponent": 0},
        },
        "rows": rows,
        "butterflies": butterflies,
        "range_contracts": range_contracts,
        "proof": {
            "component_butterflies": 576,
            "input_cells_covered_once": 1152,
            "output_cells_covered_once": 1152,
            "twiddle_inverse_checks": 72,
            "matrix_identity_checks": 72,
            "official_factor_root_identity_attached_to_every_input": True,
            "all_recorded_intervals_fit_signed_i16": True,
        },
        "prototype_gate": {
            "inverse_distance1_asm_authorized": True,
            "linked_BMScale_tail_plus_inverse_head_authorized": False,
            "remaining_before_linked_C2": [
                "define BMScale tail registers in persistent_pair_sd without a standalone converter",
                "differential linked tail+head against canonical BMScale plus scalar inverse-distance1 oracle",
                "audit linked peak YMM, frame, spills, and store/load seam",
            ],
            "cycles": None,
        },
        "source_sha256": {
            "pipeline_layout": sha256(args.pipeline_layout),
            "scaled_oracle": sha256(args.scaled_oracle),
            "g1c_audit": sha256(args.g1c_audit),
        },
    }
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"

    header = """#ifndef NTRUPLUS1152_EXP001_G1C_INVERSE_HEAD_H
#define NTRUPLUS1152_EXP001_G1C_INVERSE_HEAD_H

#include <stdint.h>

"""
    header += "static const int16_t ntruplus1152_exp001_g1c_inverse_d1_zeta[9][16] = {\n"
    for values, _ in header_rows:
        header += "  {" + ", ".join(map(str, values)) + "},\n"
    header += "};\n\nstatic const int16_t ntruplus1152_exp001_g1c_inverse_d1_qinv[9][16] = {\n"
    for _, values in header_rows:
        header += "  {" + ", ".join(map(str, values)) + "},\n"
    header += "};\n\n#endif\n"

    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit("generated G1C adjusted inverse-head oracle is stale")
        if not args.header.is_file() or args.header.read_text() != header:
            raise SystemExit("generated G1C adjusted inverse-head header is stale")
        if not args.asm_constants.is_file() or args.asm_constants.read_text() != asm:
            raise SystemExit("generated G1C adjusted inverse-head ASM constants are stale")
        return 0
    args.output.write_text(rendered)
    args.header.write_text(header)
    args.asm_constants.write_text(asm)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
