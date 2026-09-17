#!/usr/bin/env python3
"""Generate the scale-1 wire Forward plus live-terminal serializer ASM."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path


SYMBOL = "ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_scale1_dual_r"


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("h4_m3b", path)
    if spec is None or spec.loader is None:
        raise SystemExit("cannot load serializer generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(path: Path, value: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text() != value:
            raise SystemExit(f"stale dual-output ASM artifact: {path}")
    else:
        path.write_text(value)


def rename_registers(line: str, rename: list[int]) -> str:
    def replace(match: re.Match[str]) -> str:
        kind, number = match.groups()
        old = int(number)
        return f"{kind}{rename[old] if old < 8 else old}"
    return re.sub(r"\b([xy]mm)([0-9]|1[0-5])\b", replace, line)


def normalization(reg: int) -> list[str]:
    # ymm14 is outside emit_tile's 0..13 allocation; ymm15 remains the
    # Forward q constant across all 18 rows.
    return [
        f"  vpmulhrsw ymm14, ymm{reg}, YMMWORD PTR [rip + .Lma1_barrett]",
        "  vpmullw ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]",
        f"  vpsubw ymm{reg}, ymm{reg}, ymm14",
        f"  vpsraw ymm14, ymm{reg}, 15",
        "  vpand ymm14, ymm14, YMMWORD PTR [rip + .Lma1_q]",
        f"  vpaddw ymm{reg}, ymm{reg}, ymm14",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", type=Path, required=True)
    parser.add_argument("--machine-wire", type=Path, required=True)
    parser.add_argument("--serializer-generator", type=Path, required=True)
    parser.add_argument("--macro-include", type=Path, required=True)
    parser.add_argument("--asm", type=Path, required=True)
    parser.add_argument("--header", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--symbol", default=SYMBOL)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    mapping = json.loads(args.map.read_text())
    if not all(mapping["gates"].values()) or not mapping["decision"]["asm_authorized"]:
        raise SystemExit("MAP1 has not authorized ASM")
    module = load_module(args.serializer_generator)
    machine = json.loads(args.machine_wire.read_text())
    machine_tiles = {tuple(tile["vectors"]): tile for tile in module.machine_tiles(machine)}

    index_values = []
    for tile in machine_tiles.values():
        for source in tile["pair32_sources"]:
            key = tuple(source["permutation"])
            if key != tuple(range(8)) and key not in index_values:
                index_values.append(key)
    labels = {value: f".Ldual_r_index_{index}" for index, value in enumerate(index_values)}

    lines = ["/* Generated live-terminal r serializer tiles. */"]
    totals = {key: 0 for key in (
        "scratch_loads", "pair_unpack", "pair_madd", "vpermd_index_loads",
        "vpermd", "parity_routes", "pack_routes", "pack_saves",
        "ciphertext_stores")}
    for item in mapping["tiles"]:
        branch, row = item["branch"], item["row"]
        tile = machine_tiles[tuple(item["state_vectors"])]
        body, counts = module.emit_tile(tile, labels)
        if len(body) < 5 or sum("vmovdqa ymm" in line and "[r8 +" in line
                                for line in body[:5]) != 4:
            raise SystemExit("serializer load prologue changed")
        body = body[5:]  # comment plus the four reloads eliminated by MAP1
        rename = item["serializer_register_rename_0_to_7"]
        emitted = []
        for old_input in range(4):
            emitted += normalization(rename[old_input])
        for line in body:
            line = line.replace("[rdi +", "[rsi +")
            emitted.append(rename_registers(line, rename))
        lines += [f".macro PROD3_R_DUAL_OUTPUT_TILE_{branch}_{row}"]
        lines += emitted
        lines += [".endm", ""]
        for key, value in counts.items():
            totals[key] += value

    lines += [
        ".macro PROD3_R_DUAL_OUTPUT_TILE branch,row",
        "  .if \\branch == 0",
    ]
    for row in range(9):
        lines += [("    .if" if row == 0 else "    .elseif") + f" \\row == {row}",
                  f"      PROD3_R_DUAL_OUTPUT_TILE_0_{row}"]
    lines += ["    .endif", "  .else"]
    for row in range(9):
        lines += [("    .if" if row == 0 else "    .elseif") + f" \\row == {row}",
                  f"      PROD3_R_DUAL_OUTPUT_TILE_1_{row}"]
    lines += ["    .endif", "  .endif", ".endm", "",
              ".section .rodata,\"a\",@progbits"]
    for value, label in labels.items():
        lines += [".p2align 5", f"{label}:",
                  "  .long " + ",".join(map(str, value))]
    lines += [
        ".p2align 5", ".Lh4_m3b_pair_weight:",
        "  .short " + ",".join(["1", "4096"] * 8),
        ".p2align 5", ".Lh4_m3b_pack24:",
        "  .byte 0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128,"
        "0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128",
        '.include "generated/f0-ma2-constants.inc"', "",
    ]

    wrapper = f"""\
/* Generated scale-1 wire Forward with an exact live-terminal r output. */
#define PROD3_FULL_ONLY 1
#define PROD3_NATURAL_Q 1
#define PROD3_WIRE_MONOTONE 1
#define PROD3_T0_BETA 1
#define PROD3_SCALE1 1
#define PROD3_LAZY_R2_REDUCTIONS 1
#define PROD3_R_DUAL_OUTPUT 1
#define ntruplus1152_exp001_gt9x16_prod3_aos_full {args.symbol}
.include "generated/d1-wire-monotone-absorption.inc"
.include "{args.macro_include.as_posix()}"
#include "gt9x16_prod3_aos_branch0.S"
"""
    header_guard = "NTRUPLUS1152_EXP001_SCALE1_R_DUAL_OUTPUT_H"
    header = f"""\
#ifndef {header_guard}
#define {header_guard}
#include <stdint.h>
void {args.symbol}(int16_t state[1152], uint8_t bytes[1728]);
#endif
"""
    contract = {
        "schema": "scale1-r-dual-output-asm/v1",
        "checkpoint": "SCALE1-R-DUAL-OUTPUT-ASM1",
        "symbol": args.symbol,
        "abi": {"rdi": "in-place 2304-byte top-split state; retained wire scale-1 output",
                "rsi": "1728-byte exact serialized r output"},
        "serializer_ledger_before_load_elimination": totals,
        "expected": {"terminal_tiles": 18, "state_stores": 72,
                     "serializer_reloads": 0, "removed_reloads": 72,
                     "register_moves": 0, "extra_scratch_bytes": 0,
                     "peak_ymm": 15},
        "decision": {"correctness_authorized": True,
                     "caller_benchmark_authorized": False,
                     "native_kem_authorized": False},
    }
    write(args.macro_include, "\n".join(lines), args.check)
    write(args.asm, wrapper, args.check)
    write(args.header, header, args.check)
    write(args.contract, json.dumps(contract, indent=2, sort_keys=True) + "\n", args.check)
    print("scale-1 r dual-output ASM generated: 72 serializer reloads removed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
