#!/usr/bin/env python3
"""Generate the boundary-preserving 8-YMM packet serializer V2."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DATA_MAP = {0: 8, 1: 9, 2: 10, 3: 11, 4: 12, 5: 6, 6: 13, 7: 7}
TEMP_MAP = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5}
REG_MAP = DATA_MAP | TEMP_MAP | {14: 14, 15: 15}


def write(path: Path, value: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text() != value:
            raise SystemExit(f"stale generated artifact: {path}")
    else:
        path.write_text(value)


def official_body(path: Path) -> list[str]:
    lines = path.read_text().splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith("vpmulhrsw %ymm15, %ymm0"))
    end = next(i for i in range(start, len(lines)) if lines[i].startswith("vmovdqu %ymm5, 160(%rdi)"))
    body = lines[start:end + 1]

    def rename(line: str) -> str:
        return re.sub(r"%ymm(1[0-5]|[0-9])",
                      lambda match: f"%ymm{REG_MAP[int(match.group(1))]}", line)

    return [rename(line) for line in body]


def form_official_inputs(low: list[int], high: list[int]) -> list[str]:
    """Form eight stride-8 vectors consumed by Official's pack network."""
    lines = []
    for plane, (low_vector, high_vector) in enumerate(zip(low, high)):
        even = DATA_MAP[plane]
        odd = DATA_MAP[plane + 4]
        lines += [
            f"vmovdqa {32 * low_vector}(%rsi), %ymm0",
            f"vmovdqa {32 * high_vector}(%rsi), %ymm1",
            "vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0",
            "vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1",
            "vpermq $0xd8, %ymm0, %ymm0",
            "vpermq $0xd8, %ymm1, %ymm1",
            f"vperm2i128 $0x20, %ymm1, %ymm0, %ymm{even}",
            f"vperm2i128 $0x31, %ymm1, %ymm0, %ymm{odd}",
        ]
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet-map", type=Path, required=True)
    parser.add_argument("--pack-source", type=Path, required=True)
    parser.add_argument("--asm", type=Path, required=True)
    parser.add_argument("--header", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--symbol", required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    packet_map = json.loads(args.packet_map.read_text())
    body = official_body(args.pack_source)
    lines = ["/* Generated scale-1 serializer V2; preserve the materialized wire boundary. */",
             ".text", ".p2align 5", f".globl {args.symbol}", f".type {args.symbol},@function",
             f"{args.symbol}:", "vmovdqa _16xv(%rip), %ymm15", "vmovdqa _16xq(%rip), %ymm14"]
    for packet in packet_map["packets"]:
        low, high = packet["tile_state_vectors"]
        lines += [f"/* packet {packet['packet']}: coefficients {packet['wire_coefficients'][0]}..{packet['wire_coefficients'][1]} */"]
        lines += form_official_inputs(low, high)
        lines += body
        if packet["packet"] != 8:
            lines += ["add $192, %rdi"]
    lines += ["vzeroupper", "ret", f".size {args.symbol}, .-{args.symbol}",
              '.section .rodata,"a",@progbits', ".p2align 5", ".Lserializer_v2_even_odd:",
              "  .byte 0,1,4,5,8,9,12,13,2,3,6,7,10,11,14,15,"
              "0,1,4,5,8,9,12,13,2,3,6,7,10,11,14,15",
              '.section .note.GNU-stack,"",@progbits', ""]
    contract = {
        "schema": "scale1-r-serializer-v2-asm/v1",
        "symbol": args.symbol,
        "input": "materialized wire-monotone scale-1 state",
        "output": "exact 1728-byte NTRU+1152 wire encoding",
        "packets": 9,
        "expected": {
            "data_loads": 72, "official_input_formation_routes": 216,
            "normalization_instructions": 432, "official_pack_and_stores": 522,
            "constant_loads": 2, "pointer_updates": 8, "vzeroupper": 1, "ret": 1,
            "dynamic_body_instructions": 1254,
            "stack_bytes": 0, "spill": False,
        },
        "register_renaming": {str(k): v for k, v in sorted(REG_MAP.items())},
    }
    header = ("#ifndef SCALE1_R_SERIALIZER_V2_ASM_H\n#define SCALE1_R_SERIALIZER_V2_ASM_H\n"
              "#include <stdint.h>\n"
              f"void {args.symbol}(uint8_t out[1728], const int16_t state[1152]);\n"
              "#endif\n")
    write(args.asm, "\n".join(lines), args.check)
    write(args.header, header, args.check)
    write(args.contract, json.dumps(contract, indent=2, sort_keys=True) + "\n", args.check)
    print("scale-1 serializer V2 ASM: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
