#!/usr/bin/env python3
"""Extend the component oracle across forward, BaseMul, and inverse layouts."""

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
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    source = json.loads(args.component_oracle.read_text())
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
                "positions": positions,
            })
    for layout, storage_i16 in (("official", 1152),
                                ("gt_row_terminal_lane", 1152),
                                ("gt_terminal_row_lane", 1152),
                                ("q_major_padded16", 2048)):
        mapped = [position[layout]["position_i16"]
                  for cell in cells for position in cell["positions"]]
        if len(mapped) != 1152 or len(set(mapped)) != 1152:
            raise SystemExit(f"{layout} mapping is not injective over active coefficients")
        if min(mapped) < 0 or max(mapped) >= storage_i16:
            raise SystemExit(f"{layout} mapping exceeds its storage contract")
    document = {
        "parameter": 1152,
        "contract_scope": "forward terminal output <-> BaseMul/BaseInv operand <-> inverse input",
        "selected_candidate_for_checkpoint_c": "gt_row_terminal_lane",
        "selected_terminal_abi": "T[branch][physical_trit_reversed_row][terminal_coefficient][physical_bit_reversed_lane]",
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
    if args.check:
        if not args.output.is_file() or args.output.read_text() != rendered:
            raise SystemExit("generated pipeline layout contract is stale")
        return 0
    args.output.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
