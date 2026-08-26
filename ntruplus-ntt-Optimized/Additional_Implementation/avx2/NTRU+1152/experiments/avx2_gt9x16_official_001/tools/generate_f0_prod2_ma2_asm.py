#!/usr/bin/env python3
"""Derive the materialized P2-B producer from the frozen P1-H arithmetic."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


OLD_PREFIX = "ntruplus1152_exp001_f0_prod1_p1h"
NEW_PREFIX = "ntruplus1152_exp001_f0_prod2_ma2_p2b"

PAIR_STORES = """  vmovdqa YMMWORD PTR [rdi + (\\rowa)*128], ymm0
  vmovdqa YMMWORD PTR [rdi + (\\rowa)*128 + 32], ymm1
  vmovdqa YMMWORD PTR [rdi + (\\rowb)*128], ymm2
  vmovdqa YMMWORD PTR [rdi + (\\rowb)*128 + 32], ymm3"""

PAIR_NATIVE_STORES = """  /* P2-B: exact MA2 coefficient planes, in the same two slot pairs. */
  vperm2i128 ymm8, ymm0, ymm1, 0x20
  vperm2i128 ymm9, ymm0, ymm1, 0x31
  vmovdqa YMMWORD PTR [rdi + (\\rowa)*128], ymm8
  vmovdqa YMMWORD PTR [rdi + (\\rowa)*128 + 32], ymm9
  vperm2i128 ymm8, ymm2, ymm3, 0x20
  vperm2i128 ymm9, ymm2, ymm3, 0x31
  vmovdqa YMMWORD PTR [rdi + (\\rowb)*128], ymm8
  vmovdqa YMMWORD PTR [rdi + (\\rowb)*128 + 32], ymm9"""

TAIL_STORES = """  vmovdqa YMMWORD PTR [rdi + (\\row)*128], ymm0
  vmovdqa YMMWORD PTR [rdi + (\\row)*128 + 32], ymm1"""

TAIL_NATIVE_STORES = """  /* P2-B tail: exact MA2 coefficient planes, same slot pair. */
  vperm2i128 ymm8, ymm0, ymm1, 0x20
  vperm2i128 ymm9, ymm0, ymm1, 0x31
  vmovdqa YMMWORD PTR [rdi + (\\row)*128], ymm8
  vmovdqa YMMWORD PTR [rdi + (\\row)*128 + 32], ymm9"""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text() != value:
            raise SystemExit(f"generated file is stale: {path}")
    else:
        path.write_text(value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p1h-source", type=Path, required=True)
    parser.add_argument("--map", type=Path, required=True)
    parser.add_argument("--asm", type=Path, required=True)
    parser.add_argument("--header", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    mapping = json.loads(args.map.read_text())
    if mapping["schema"] != "gt-f0-prod2-ma2-map/v1":
        raise SystemExit("wrong PROD2 map schema")
    selected = mapping["realization_search"]["P2-B-local-d1-epilogue"]
    if not selected["selected"] or selected["extra_temporary_bytes"] != 0:
        raise SystemExit("P2-B is not the selected zero-extra-storage realization")

    source = args.p1h_source.read_text()
    if source.count(PAIR_STORES) != 1 or source.count(TAIL_STORES) != 1:
        raise SystemExit("frozen P1-H final redeposit pattern changed")
    if source.count(OLD_PREFIX) != 21:
        raise SystemExit("frozen P1-H public/region symbol set changed")

    asm = source.replace(PAIR_STORES, PAIR_NATIVE_STORES)
    asm = asm.replace(TAIL_STORES, TAIL_NATIVE_STORES)
    asm = asm.replace(OLD_PREFIX, NEW_PREFIX)
    asm = ("/* Generated F0-PROD2 P2-B: P1-H arithmetic is byte-for-byte "
           "preserved outside the final D1 redeposit. */\n" + asm)

    header = """#ifndef NTRUPLUS1152_EXP001_F0_PROD2_MA2_ASM_H
#define NTRUPLUS1152_EXP001_F0_PROD2_MA2_ASM_H
#include <stdint.h>
void ntruplus1152_exp001_f0_prod2_ma2_p2b_pair(
    int16_t output_planes[1152], const int16_t split[1152],
    unsigned int branch, unsigned int terminal_pair);
#endif
"""
    contract = {
        "schema": "gt-f0-prod2-ma2-asm/v1",
        "checkpoint": "F0-PROD2-MA2-ASM0",
        "symbol": NEW_PREFIX + "_pair",
        "semantic_transform": "F0",
        "physical_output_abi": "F0-MA2 coefficient planes",
        "arithmetic_derivation": {
            "source": str(args.p1h_source),
            "unchanged_regions": ["formation_pair0", "formation_pair1",
                                  "r2_second", "D1 arithmetic and routing"],
            "only_replacement": "final D1 generic redeposit -> P2-B plane redeposit",
            "new_reductions": 0,
            "scale_conversions": 0,
        },
        "dynamic_per_forward": {
            "helper_calls": 4,
            "p2b_vperm2i128": 72,
            "aligned_plane_stores": 72,
            "generic_f0_final_stores": 0,
            "extra_temporary_bytes": 0,
            "backing_bytes": 2304,
        },
        "output_contract": {
            "owner": ["branch", "p", "terminal_coefficient"],
            "lane": "physical q leaf",
            "p_order": mapping["frozen_contract"]["physical_p_order"],
            "q_order": mapping["frozen_contract"]["ma2_plane_lane_order"],
            "scale": mapping["frozen_contract"]["transform_scale"],
            "montgomery_r_exponent": mapping["frozen_contract"]["montgomery_r_exponent"],
            "range_i16": mapping["range_and_scale_proof"]["exact_global_i16_envelope"],
            "materialized": True,
        },
        "source_sha256": {
            "p1h_source": sha256(args.p1h_source),
            "map": sha256(args.map),
        },
    }

    write(args.asm, asm, args.check)
    write(args.header, header, args.check)
    write(args.contract, json.dumps(contract, indent=2, sort_keys=True) + "\n",
          args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
