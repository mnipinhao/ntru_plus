#!/usr/bin/env python3
"""Generate a direct scale-1 MA2-plane to exact wire serializer."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


def load_m3b(path: Path):
    spec = importlib.util.spec_from_file_location("m3b_generator", path)
    if spec is None or spec.loader is None:
        raise SystemExit("cannot load M3B generator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write(path: Path, value: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text() != value:
            raise SystemExit(f"stale serializer artifact: {path}")
    else:
        path.write_text(value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generator", type=Path, required=True)
    parser.add_argument("--machine-wire", type=Path, required=True)
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--asm", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    m3b = load_m3b(args.generator)
    machine = json.loads(args.machine_wire.read_text())
    tiles = m3b.machine_tiles(machine)
    index_values = []
    for tile in tiles:
        for source in tile["pair32_sources"]:
            key = tuple(source["permutation"])
            if key != tuple(range(8)) and key not in index_values:
                index_values.append(key)
    labels = {value: f".Lwire_ser_index_{index}" for index, value in enumerate(index_values)}
    lines = ["/* Generated direct scale-1 exact-wire serializer. */",
             ".intel_syntax noprefix", ".text", ".p2align 5",
             f".globl {args.symbol}", f".type {args.symbol},@function", f"{args.symbol}:"]
    totals = {key: 0 for key in ("scratch_loads", "pair_unpack", "pair_madd",
              "vpermd_index_loads", "vpermd", "parity_routes", "pack_routes",
              "pack_saves", "ciphertext_stores")}
    for tile in tiles:
        tile_lines, counts = m3b.emit_tile(tile, labels)
        # emit_tile uses r8 as its source base; direct serializer uses rsi.
        tile_lines = [line.replace("[r8 +", "[rsi +") for line in tile_lines]
        insertion = 1 + 4  # comment plus four loads
        normalize = []
        for reg in range(4):
            normalize += [
                f"  vpmulhrsw ymm15, ymm{reg}, YMMWORD PTR [rip + .Lma1_barrett]",
                "  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]",
                f"  vpsubw ymm{reg}, ymm{reg}, ymm15",
                f"  vpsraw ymm15, ymm{reg}, 15",
                "  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]",
                f"  vpaddw ymm{reg}, ymm{reg}, ymm15",
            ]
        lines += tile_lines[:insertion] + normalize + tile_lines[insertion:]
        for key, value in counts.items(): totals[key] += value
    lines += ["  ret", f".size {args.symbol}, .-{args.symbol}",
              ".section .rodata,\"a\",@progbits"]
    for value, label in labels.items():
        lines += [".p2align 5", f"{label}:", "  .long " + ",".join(map(str, value))]
    lines += [".p2align 5", ".Lh4_m3b_pair_weight:",
              "  .short " + ",".join(["1", "4096"] * 8),
              ".p2align 5", ".Lh4_m3b_pack24:",
              "  .byte 0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128,"
              "0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128",
              '#include "generated/f0-ma2-constants.inc"',
              ".section .note.GNU-stack,\"\",@progbits", ""]
    contract = {"schema": "wire-monotone-direct-serializer/v1", "symbol": args.symbol,
                "generator_ledger": totals,
                "normalization_instructions": 432,
                "total_expected_instructions": sum(totals.values()) + 432 + 1,
                "frame_bytes": 0}
    write(args.asm, "\n".join(lines), args.check)
    write(args.contract, json.dumps(contract, indent=2, sort_keys=True) + "\n", args.check)
    print(json.dumps(contract, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
