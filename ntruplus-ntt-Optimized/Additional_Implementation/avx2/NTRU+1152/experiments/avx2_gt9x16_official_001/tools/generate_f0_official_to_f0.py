#!/usr/bin/env python3
"""Generate the inverse Official-to-F0 AVX2 layout adapter."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

def write(path: Path, value: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text() != value:
            raise SystemExit(f"generated file is stale: {path}")
    else:
        path.write_text(value)

def byte_mask(words):
    out = []
    for word in words:
        out.extend((128, 128) if word is None else (2 * word, 2 * word + 1))
    return tuple(out)

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--schedule", type=Path, required=True)
    p.add_argument("--asm", type=Path, required=True)
    p.add_argument("--constants", type=Path, required=True)
    p.add_argument("--header", type=Path, required=True)
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--check", action="store_true")
    a = p.parse_args(); raw = a.schedule.read_bytes(); schedule = json.loads(raw)
    official_for_f0 = {}
    for tile in schedule["semantic_tiles"]:
        for plane in tile["planes"]:
            for f0, official in zip(plane["f0_positions_i16"],
                                    plane["resident_h_official_positions_i16"]):
                official_for_f0[f0] = official
    if set(official_for_f0) != set(range(1152)) or \
       set(official_for_f0.values()) != set(range(1152)):
        raise SystemExit("Official/F0 map is not bijective")
    masks = {}; body = []; groups_total = 0
    for vector in range(72):
        halves = []
        for dh in range(2):
            halves.append(sorted({(official_for_f0[16*vector+8*dh+lane]//16,
                                   (official_for_f0[16*vector+8*dh+lane]%16)//8)
                                  for lane in range(8)}))
        groups = max(map(len, halves)); groups_total += groups
        body.append(f"  /* F0 vector {vector}: {groups} Official source-half groups. */")
        for group in range(groups):
            low = halves[0][group] if group < len(halves[0]) else halves[0][0]
            high = halves[1][group] if group < len(halves[1]) else halves[1][0]
            body += [f"  vmovdqa ymm0, YMMWORD PTR [rsi + {32*low[0]}]",
                     f"  vmovdqa ymm1, YMMWORD PTR [rsi + {32*high[0]}]",
                     f"  vperm2i128 ymm2, ymm0, ymm1, 0x{low[1] | ((2+high[1])<<4):02x}"]
            words = []
            for dh, selected in enumerate((low, high)):
                for lane in range(8):
                    source = official_for_f0[16*vector+8*dh+lane]
                    ident = (source//16, (source%16)//8)
                    words.append(source%8 if ident == selected else None)
            mask = byte_mask(words)
            if mask not in masks: masks[mask] = f".Lofficial_to_f0_mask_{len(masks)}"
            body.append(f"  vpshufb ymm2, ymm2, YMMWORD PTR [rip + {masks[mask]}]")
            body.append("  vmovdqa ymm3, ymm2" if group == 0 else "  vpor ymm3, ymm3, ymm2")
        body += ["  vpsllw ymm3, ymm3, 2",
                 f"  vmovdqa YMMWORD PTR [rdi + {32*vector}], ymm3"]
    body.append("  ret")
    symbol = "ntruplus1152_exp001_official_to_f0"
    asm = f""".intel_syntax noprefix
.text
.globl {symbol}
.type {symbol},@function
.p2align 5
{symbol}:
""" + "\n".join(body) + f"\n.size {symbol}, .-{symbol}\n"
    asm += '\n.section .rodata\n#include "generated/f0-official-to-f0-constants.inc"\n'
    asm += '\n.section .note.GNU-stack,"",@progbits\n'
    constants = "/* Generated Official-to-F0 masks. */\n.p2align 5\n"
    for mask, name in masks.items():
        constants += name + ":\n  .byte " + ", ".join(map(str, mask)) + "\n"
    header = f"""#ifndef NTRUPLUS1152_EXP001_OFFICIAL_TO_F0_H
#define NTRUPLUS1152_EXP001_OFFICIAL_TO_F0_H
#include <stdint.h>
void {symbol}(int16_t output_f0[1152], const int16_t input_official[1152]);
#endif
"""
    contract = {"schema":"gt-f0-official-to-f0/v1", "bijection_cells":1152,
                "output_vectors":72, "source_half_groups":groups_total,
                "loads":2*groups_total, "stores":72, "scale_lift":4,
                "required_alignment":32,
                "source_schedule_sha256":hashlib.sha256(raw).hexdigest()}
    write(a.asm, asm, a.check); write(a.constants, constants, a.check)
    write(a.header, header, a.check)
    write(a.contract, json.dumps(contract, indent=2, sort_keys=True)+"\n", a.check)
    return 0
if __name__ == "__main__": raise SystemExit(main())
