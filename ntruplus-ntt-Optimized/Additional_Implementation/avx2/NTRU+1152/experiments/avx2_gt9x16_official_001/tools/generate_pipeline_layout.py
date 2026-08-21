#!/usr/bin/env python3
"""Generate the normalized NTT-domain representation contract and ABI costs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

Q = 3457
R = pow(2, 16, Q)
QINV = 12929


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def signed16(value: int) -> int:
    value %= 65536
    return value - 65536 if value >= 32768 else value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--component-oracle", type=Path, required=True)
    parser.add_argument("--lifecycle-audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cost-output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    source = json.loads(args.component_oracle.read_text())
    lifecycle = json.loads(args.lifecycle_audit.read_text())
    if lifecycle["audit_conclusion"]["standalone_full_layout_passes"] != 0:
        raise SystemExit("Official lifecycle unexpectedly contains a layout pass")
    cells = []
    for branch_entries in source["components"]:
        for entry in branch_entries:
            branch = entry["branch"]
            row = entry["gt_row"]
            lane = entry["ntt16_lane"]
            factor_mont = centered(entry["factor_mod_q"] * R)
            positions = []
            for coefficient, official in enumerate(entry["official_avx2_positions"]):
                official_block, within = divmod(official, 64)
                official_terminal, official_lane = divmod(within, 16)
                if official_terminal != coefficient:
                    raise SystemExit("Official layout probe terminal mismatch")
                positions.append({
                    "terminal_coefficient": coefficient,
                    "official": {
                        "position_i16": official,
                        "basemul_block16": official_block,
                        "basemul_terminal_vector": official_terminal,
                        "basemul_lane": official_lane,
                        "inverse_input_position_i16": official,
                    },
                    "gt_row_terminal_lane": {
                        "position_i16": (((branch * 9 + row) * 4 + coefficient) * 16 + lane),
                        "basemul_block16": branch * 9 + row,
                        "basemul_terminal_vector": coefficient,
                        "basemul_lane": lane,
                        "inverse_input_position_i16": (((branch * 9 + row) * 4 + coefficient) * 16 + lane),
                    },
                    "gt_terminal_row_lane": {
                        "position_i16": (((branch * 4 + coefficient) * 9 + row) * 16 + lane),
                        "basemul_stream": coefficient,
                        "basemul_row": branch * 9 + row,
                        "basemul_lane": lane,
                        "inverse_input_position_i16": (((branch * 4 + coefficient) * 9 + row) * 16 + lane),
                    },
                    "persistent_pair_sd": {
                        "position_i16": (((((branch * 9 + row) * 2 + coefficient // 2) * 2 +
                                           lane % 2) * 16) + (coefficient % 2) * 8 + lane // 2),
                        "terminal_pair": coefficient // 2,
                        "sd_vector": lane % 2,
                        "packed_lane": (coefficient % 2) * 8 + lane // 2,
                        "mathematical_terminal_coefficient": coefficient,
                        "mathematical_q": entry["ntt16_frequency_q"],
                    },
                    "terminal_to_inverse_pair_hybrid": {
                        "forward_and_arithmetic_input_position_i16":
                            (((branch * 9 + row) * 4 + coefficient) * 16 + lane),
                        "arithmetic_output_and_inverse_position_i16":
                            (((((branch * 9 + row) * 2 + coefficient // 2) * 2 +
                               lane % 2) * 16) + (coefficient % 2) * 8 + lane // 2),
                    },
                    "q_major_padded16": {
                        "position_i16": (((branch * 16 + lane) * 4 + coefficient) * 16 + row),
                        "active_lane": row,
                        "padding_lanes_per_vector": 7,
                        "inverse_input_position_i16": (((branch * 16 + lane) * 4 + coefficient) * 16 + row),
                    },
                })
            cells.append({
                "branch": branch,
                "gt_row_physical_trit_reversed": row,
                "ntt9_frequency_p": entry["ntt9_frequency_p"],
                "ntt16_lane_physical_bit_reversed": lane,
                "ntt16_frequency_q": entry["ntt16_frequency_q"],
                "factor_exponent_base_g": entry["factor_exponent_base_g"],
                "factor_mod_q": entry["factor_mod_q"],
                "basemul_factor_montgomery": factor_mont,
                "basemul_factor_qinv_signed16": signed16(factor_mont * QINV),
                "factor_polynomial": {
                    "form": "X^4 - factor",
                    "factor_mod_q": entry["factor_mod_q"],
                    "constant_term_mod_q": (-entry["factor_mod_q"]) % Q,
                },
                "baseinv_factor_montgomery": factor_mont,
                "baseinv_factor_qinv_signed16": signed16(factor_mont * QINV),
                "value_contract_ids": {
                    "forward_output": "kem-small-forward-r0",
                    "resident_ntt_operand": "resident-r0",
                    "regular_basemul_output": "resident-r0",
                    "baseinv_output": "resident-r0",
                    "scaled_basemul_inverse_feed": "inverse-feed-rminus1",
                },
                "positions": positions,
            })
    for layout, storage_i16 in (("official", 1152),
                                ("gt_row_terminal_lane", 1152),
                                ("gt_terminal_row_lane", 1152),
                                ("persistent_pair_sd", 1152),
                                ("q_major_padded16", 2048)):
        mapped = [position[layout]["position_i16"]
                  for cell in cells for position in cell["positions"]]
        if len(mapped) != 1152 or len(set(mapped)) != 1152:
            raise SystemExit(f"{layout} mapping is not injective over active coefficients")
        if min(mapped) < 0 or max(mapped) >= storage_i16:
            raise SystemExit(f"{layout} mapping exceeds its storage contract")
    reduction_outputs = []
    for value in range(-30544, 30545):
        quotient = (value * 9 + (1 << 14)) >> 15
        reduction_outputs.append(value - quotient * Q)
    if (min(reduction_outputs), max(reduction_outputs)) != (-3107, 3107):
        raise SystemExit("Official small-forward final range proof changed")
    value_contracts = {
        "kem-small-forward-r0": {
            "scale_r_exponent": 0,
            "input_contract": "coefficient inputs in [-3,4]",
            "allowed_range_i16": [-3107, 3107],
            "range_basis": "conservative symbolic stage bound <=30544 followed by Official vpmulhrsw(q=3457,v=9) reduction",
            "gt_requirement": "provisional D-B forward must include an equivalent final reduction before BaseMul/BaseInv",
            "general_centered_input": "not yet qualified",
        },
        "resident-r0": {
            "scale_r_exponent": 0,
            "allowed_range_i16": [-3456, 3456],
            "consumer": "regular BaseMul, BaseInv, or later resident NTT-domain arithmetic",
        },
        "inverse-feed-rminus1": {
            "scale_r_exponent": -1,
            "allowed_range_i16_conservative": [-13824, 13824],
            "producer": "scaled BaseMul without the R^2 post-pass",
            "consumer": "adjusted inverse NTT16/inverse normalization matching poly_invntt_scale",
        },
    }
    document = {
        "parameter": 1152,
        "contract_scope": "forward terminal output <-> BaseMul/BaseInv operand <-> inverse input",
        "checkpoint_e_selection": "undecided-until-2F-plus-BM-plus-I-and-F-plus-BI-plus-I",
        "physical_row_to_mathematical_p": [0, 3, 6, 1, 4, 7, 2, 5, 8],
        "physical_lane_to_mathematical_q": [0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15],
        "value_contracts": value_contracts,
        "baseinv_denominator_side_layout": "den[branch*9+physical_p_row][physical_q_lane], 18 YMM total",
        "candidates": {
            "official": {
                "storage_bytes": 2304,
                "forward_conversion": "current GT baseline uses 1152 scalar scatter stores",
                "basemul_conversion": "zero for Official BaseMul",
                "inverse_conversion": "zero for Official inverse; full remap before a GT inverse",
            },
            "gt_row_terminal_lane": {
                "storage_bytes": 2304,
                "forward_conversion": "zero shuffles after vector NTT9; 72 required YMM result stores",
                "basemul_conversion": "zero shuffles; four adjacent terminal YMM vectors per 16-factor row block",
                "inverse_conversion": "zero shuffles into inverse NTT9/NTT16 schedule",
            },
            "persistent_pair_sd": {
                "storage_bytes": 2304,
                "shape": "P[branch][physical_p_row][terminal_pair][S_or_D][packed_lane]",
                "packed_lane_rule": "lower 8 lanes are terminal 2k; upper 8 lanes terminal 2k+1; S/D selects even/odd physical q lane",
                "forward_conversion": "zero only for a terminal-paired adjusted NTT16 that keeps its final S/D vectors",
                "basemul_conversion": "must be absorbed into BaseMul loads; the current explicit unpack schedule uses 8 routing instructions per operand and row",
                "baseinv_conversion": "must be absorbed into BaseInv loads; the current explicit unpack schedule uses 8 routing instructions per row",
                "inverse_conversion": "zero only for a paired adjusted inverse NTT16 proven to consume S/D directly",
            },
            "terminal_to_inverse_pair_hybrid": {
                "storage_bytes": 2304,
                "forward_and_arithmetic_input": "gt_row_terminal_lane",
                "arithmetic_output_and_inverse_input": "persistent_pair_sd",
                "forward_conversion": "zero for terminal-major D-B stores",
                "basemul_baseinv_input_conversion": "zero",
                "arithmetic_output_conversion": "the current explicit pack schedule uses 8 store-side routing instructions per row inside BaseMul/BaseInv",
                "inverse_conversion": "zero only for paired adjusted inverse NTT16",
            },
            "gt_terminal_row_lane": {
                "storage_bytes": 2304,
                "forward_conversion": "zero shuffles when terminal pipelines are stored separately",
                "basemul_conversion": "zero shuffles but four terminal streams are 288 bytes apart",
                "inverse_conversion": "zero shuffles; favors terminal-at-a-time inverse traversal",
            },
            "q_major_padded16": {
                "storage_bytes": 4096,
                "forward_conversion": "requires a 9x16 transpose and padding",
                "basemul_conversion": "seven inactive lanes per vector",
                "inverse_conversion": "transpose-free only for a q-major inverse",
            },
        },
        "cells": cells,
    }
    rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
    cost_document = {
        "parameter": 1152,
        "metric": "static routing-instruction estimates for the current explicit AVX2 pack/unpack schedule at real kernel boundaries; not proved lower bounds; cycles pending prototypes",
        "full_rows": 18,
        "standalone_full_layout_pass_allowed": False,
        "candidates": {
            "A_terminal_major": {
                "forward_output_abi": "gt_row_terminal_lane",
                "arithmetic_input_abi": "gt_row_terminal_lane",
                "arithmetic_output_abi": "gt_row_terminal_lane",
                "inverse_input_abi": "gt_row_terminal_lane",
                "forward_final_routing_per_row": 0,
                "basemul_boundary_routing_per_row": 0,
                "baseinv_boundary_routing_per_row": 0,
                "inverse_entry_routing_per_row": 0,
                "open_question": "independent inverse NTT16 misses any terminal-pair arithmetic sharing",
            },
            "B_persistent_pair": {
                "forward_output_abi": "persistent_pair_sd",
                "arithmetic_input_abi": "persistent_pair_sd",
                "arithmetic_output_abi": "persistent_pair_sd",
                "inverse_input_abi": "persistent_pair_sd",
                "forward_final_routing_per_row": 0,
                "basemul_load_routing_per_operand_per_row": 8,
                "basemul_store_routing_per_row": 8,
                "basemul_boundary_routing_per_row": 24,
                "basemul_boundary_routing_full_transform": 432,
                "baseinv_load_routing_per_row": 8,
                "baseinv_store_routing_per_row": 8,
                "baseinv_boundary_routing_per_row": 16,
                "baseinv_boundary_routing_full_transform": 288,
                "inverse_entry_routing_per_row": 0,
                "open_question": "paired forward/inverse kernels must prove zero boundary routing and shared-chain benefit",
            },
            "C_terminal_to_inverse_pair_hybrid": {
                "forward_output_abi": "gt_row_terminal_lane",
                "arithmetic_input_abi": "gt_row_terminal_lane",
                "arithmetic_output_abi": "persistent_pair_sd",
                "inverse_input_abi": "persistent_pair_sd",
                "forward_final_routing_per_row": 0,
                "basemul_load_routing_per_row": 0,
                "basemul_store_routing_per_row": 8,
                "basemul_boundary_routing_per_row": 8,
                "basemul_boundary_routing_full_transform": 144,
                "baseinv_load_routing_per_row": 0,
                "baseinv_store_routing_per_row": 8,
                "baseinv_boundary_routing_per_row": 8,
                "baseinv_boundary_routing_full_transform": 144,
                "inverse_entry_routing_per_row": 0,
                "open_question": "store-side repack must fit BaseMul/BaseInv register pressure; paired inverse remains unimplemented",
            },
        },
        "selection_benchmarks": ["2F+BaseMul_scale+adjusted_inverse", "F+BaseInv+scale-correct-adjusted-inverse"],
        "selection_rule": "no candidate selected from forward-only or static-routing evidence",
    }
    cost_rendered = json.dumps(cost_document, indent=2, sort_keys=True) + "\n"
    if args.check:
        if (not args.output.is_file() or args.output.read_text() != rendered or
                not args.cost_output.is_file() or args.cost_output.read_text() != cost_rendered):
            raise SystemExit("generated pipeline layout contract is stale")
        return 0
    args.output.write_text(rendered)
    args.cost_output.write_text(cost_rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
