#!/usr/bin/env python3
"""Generate a direct F0-to-Official AVX2 adapter for the MA0 control."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def write(path: Path, content: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text() != content:
            raise SystemExit(f"generated file is stale: {path}")
    else:
        path.write_text(content)


def byte_mask(words: list[int | None]) -> tuple[int, ...]:
    result = []
    for word in words:
        result.extend((128, 128) if word is None else (2 * word, 2 * word + 1))
    return tuple(result)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schedule", type=Path, required=True)
    parser.add_argument("--asm", type=Path, required=True)
    parser.add_argument("--constants", type=Path, required=True)
    parser.add_argument("--header", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    schedule = json.loads(args.schedule.read_text())
    if schedule["schema"] != "gt-f0-ma-schedule/v1":
        raise SystemExit("wrong schedule schema")

    owner = {}
    for tile in schedule["semantic_tiles"]:
        for plane in tile["planes"]:
            for f0, official in zip(plane["f0_positions_i16"],
                                    plane["resident_h_official_positions_i16"]):
                if official in owner:
                    raise SystemExit("duplicate Official owner")
                owner[official] = f0
    if set(owner) != set(range(1152)) or set(owner.values()) != set(range(1152)):
        raise SystemExit("F0/Official map is not a bijection")

    masks = {}
    body = []
    groups_total = 0
    for vector in range(72):
        halves = []
        for destination_half in range(2):
            halves.append(sorted({
                (owner[16 * vector + 8 * destination_half + lane] // 16,
                 (owner[16 * vector + 8 * destination_half + lane] % 16) // 8)
                for lane in range(8)
            }))
        groups = max(len(item) for item in halves)
        groups_total += groups
        body.append(f"  /* Official vector {vector}: {groups} source-half groups. */")
        for group in range(groups):
            low = halves[0][group] if group < len(halves[0]) else halves[0][0]
            high = halves[1][group] if group < len(halves[1]) else halves[1][0]
            body += [
                f"  vmovdqa ymm0, YMMWORD PTR [rsi + {32 * low[0]}]",
                f"  vmovdqa ymm1, YMMWORD PTR [rsi + {32 * high[0]}]",
                f"  vperm2i128 ymm2, ymm0, ymm1, 0x{low[1] | ((2 + high[1]) << 4):02x}",
            ]
            words = []
            for destination_half, selected in enumerate((low, high)):
                for lane in range(8):
                    source = owner[16 * vector + 8 * destination_half + lane]
                    identity = (source // 16, (source % 16) // 8)
                    words.append(source % 8 if identity == selected else None)
            mask = byte_mask(words)
            if mask not in masks:
                masks[mask] = f".Lma0_mask_{len(masks)}"
            body.append(f"  vpshufb ymm2, ymm2, YMMWORD PTR [rip + {masks[mask]}]")
            if group == 0:
                body.append("  vmovdqa ymm3, ymm2")
            else:
                body.append("  vpor ymm3, ymm3, ymm2")
        body.append(f"  vmovdqa YMMWORD PTR [rdi + {32 * vector}], ymm3")
    body.append("  ret")

    constants = "/* Generated F0-to-Official adapter masks. */\n.p2align 5\n"
    for mask, name in masks.items():
        constants += name + ":\n  .byte " + ", ".join(map(str, mask)) + "\n"
    symbol = "ntruplus1152_exp001_f0_ma0_to_official"
    asm = f""".intel_syntax noprefix
.text
.globl {symbol}
.type {symbol},@function
.p2align 5
{symbol}:
""" + "\n".join(body) + f"\n.size {symbol}, .-{symbol}\n"
    asm += '\n.section .rodata\n#include "generated/f0-ma0-adapter-constants.inc"\n'
    asm += '\n.section .note.GNU-stack,"",@progbits\n'
    header = """#ifndef NTRUPLUS1152_EXP001_F0_MA0_ADAPTER_H
#define NTRUPLUS1152_EXP001_F0_MA0_ADAPTER_H
#include <stdint.h>
void ntruplus1152_exp001_f0_ma0_to_official(
    int16_t output[1152], const int16_t input_f0[1152]);
#endif
"""
    contract = {
        "schema": "gt-f0-ma0-adapter/v1",
        "checkpoint": "F0-MA1-ASM1-MA0-CONTROL",
        "bijection_cells": 1152,
        "output_vectors": 72,
        "source_half_groups": groups_total,
        "executed_routing": {
            "vperm2i128": groups_total,
            "vpshufb": groups_total,
            "vpor": groups_total - 72,
            "total": 3 * groups_total - 72,
        },
        "loads": 2 * groups_total,
        "stores": 72,
        "required_alignment": 32,
        "schedule_288_interpretation": "semantic adapter estimate, not this object's executed instruction count",
        "source_schedule_sha256": hashlib.sha256(args.schedule.read_bytes()).hexdigest(),
    }
    write(args.asm, asm, args.check)
    write(args.constants, constants, args.check)
    write(args.header, header, args.check)
    write(args.contract, json.dumps(contract, indent=2, sort_keys=True) + "\n",
          args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
