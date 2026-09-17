#!/usr/bin/env python3
"""Generate the namespaced pair-resident D1 plus Serializer V2 prototype."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SYMBOL = "ntruplus1152_exp001_gt9x16_d1_pair_resident_v2_r"

def write(path: Path, text: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text() != text:
            raise SystemExit(f"stale pair-resident artifact: {path}")
    else:
        path.write_text(text)


def official_body(path: Path, reg_map: dict[int, int]) -> list[str]:
    lines = path.read_text().splitlines()
    start = next(i for i, line in enumerate(lines)
                 if line.startswith("vpmulhrsw %ymm15, %ymm0"))
    end = next(i for i in range(start, len(lines))
               if lines[i].startswith("vmovdqu %ymm5, 160(%rdi)"))
    body = lines[start:end + 1]

    def rename(line: str) -> str:
        line = re.sub(r"%ymm(1[0-5]|[0-9])",
                      lambda m: f"%ymm{reg_map[int(m.group(1))]}", line)
        return line.replace("%rdi", "%rsi")

    return [rename(line) for line in body]


def second_tile_macro() -> list[str]:
    return r"""
.macro PAIR_WIRE_OUTPUT branch,row,coefficient,base,source,qimm,shuffle
  .if \source == 0
    vpermq ymm8, ymm8, \qimm
    .if \shuffle
      vpshufb ymm8, ymm8, YMMWORD PTR [rip + .Lwire_abs_b\branch\()p\row\()_o\coefficient\()_mask]
    .endif
    vmovdqu YMMWORD PTR [rdi + (\base) + (\row)*128 + (\coefficient)*32], ymm8
  .elseif \source == 1
    vpermq ymm9, ymm9, \qimm
    .if \shuffle
      vpshufb ymm9, ymm9, YMMWORD PTR [rip + .Lwire_abs_b\branch\()p\row\()_o\coefficient\()_mask]
    .endif
    vmovdqu YMMWORD PTR [rdi + (\base) + (\row)*128 + (\coefficient)*32], ymm9
  .elseif \source == 2
    vpermq ymm10, ymm10, \qimm
    .if \shuffle
      vpshufb ymm10, ymm10, YMMWORD PTR [rip + .Lwire_abs_b\branch\()p\row\()_o\coefficient\()_mask]
    .endif
    vmovdqu YMMWORD PTR [rdi + (\base) + (\row)*128 + (\coefficient)*32], ymm10
  .else
    vpermq ymm11, ymm11, \qimm
    .if \shuffle
      vpshufb ymm11, ymm11, YMMWORD PTR [rip + .Lwire_abs_b\branch\()p\row\()_o\coefficient\()_mask]
    .endif
    vmovdqu YMMWORD PTR [rdi + (\base) + (\row)*128 + (\coefficient)*32], ymm11
  .endif
.endm

.macro PROD3_PASS_B_PAIR_SECOND branch,base,row
  /* ymm4..ymm7 retain the first tile.  The paired input uses ymm0..ymm3. */
  vmovdqu ymm0, YMMWORD PTR [rdi + (\base) + (\row)*128 + 0]
  vmovdqu ymm1, YMMWORD PTR [rdi + (\base) + (\row)*128 + 32]
  vmovdqu ymm2, YMMWORD PTR [rdi + (\base) + (\row)*128 + 64]
  vmovdqu ymm3, YMMWORD PTR [rdi + (\base) + (\row)*128 + 96]

  /* D8/D4: same butterflies, one reusable temporary pair. */
  PROD3_BFLY 0,2,8,9,.Lprod3_t0b_b\branch\()_p\row\()_distance8_zeta,.Lprod3_t0b_b\branch\()_p\row\()_distance8_qinv
  PROD3_BFLY 1,3,8,9,.Lprod3_t0b_b\branch\()_p\row\()_distance8_zeta,.Lprod3_t0b_b\branch\()_p\row\()_distance8_qinv
  PROD3_BFLY 0,1,8,9,.Lprod3_t0b_b\branch\()_p\row\()_distance4_lo_zeta,.Lprod3_t0b_b\branch\()_p\row\()_distance4_lo_qinv
  PROD3_BFLY 2,3,8,9,.Lprod3_t0b_b\branch\()_p\row\()_distance4_hi_zeta,.Lprod3_t0b_b\branch\()_p\row\()_distance4_hi_qinv

  /* D2: form both pairs, then serialize their Montgomery products. */
  vperm2i128 ymm8, ymm0, ymm1, 0x20
  vperm2i128 ymm9, ymm0, ymm1, 0x31
  vperm2i128 ymm10, ymm2, ymm3, 0x20
  vperm2i128 ymm11, ymm2, ymm3, 0x31
  vpmullw ymm0, ymm9, YMMWORD PTR [rip + .Lprod3_t0b_b\branch\()_p\row\()_distance2_lo_qinv]
  vpmulhw ymm1, ymm9, YMMWORD PTR [rip + .Lprod3_t0b_b\branch\()_p\row\()_distance2_lo_zeta]
  vpmulhw ymm0, ymm0, ymm15
  vpsubw ymm0, ymm1, ymm0
  vpsubw ymm9, ymm8, ymm0
  vpaddw ymm8, ymm8, ymm0
  vpmullw ymm0, ymm11, YMMWORD PTR [rip + .Lprod3_t0b_b\branch\()_p\row\()_distance2_hi_qinv]
  vpmulhw ymm1, ymm11, YMMWORD PTR [rip + .Lprod3_t0b_b\branch\()_p\row\()_distance2_hi_zeta]
  vpmulhw ymm0, ymm0, ymm15
  vpsubw ymm0, ymm1, ymm0
  vpsubw ymm11, ymm10, ymm0
  vpaddw ymm10, ymm10, ymm0

  /* D1: identical arithmetic with the same reusable temporary pair. */
  vpunpcklqdq ymm0, ymm8, ymm9
  vpunpckhqdq ymm1, ymm8, ymm9
  vpunpcklqdq ymm2, ymm10, ymm11
  vpunpckhqdq ymm3, ymm10, ymm11
  vpmullw ymm8, ymm1, YMMWORD PTR [rip + .Lprod3_t0b_b\branch\()_p\row\()_distance1_lo_qinv]
  vpmulhw ymm9, ymm1, YMMWORD PTR [rip + .Lprod3_t0b_b\branch\()_p\row\()_distance1_lo_zeta]
  vpmulhw ymm8, ymm8, ymm15
  vpsubw ymm8, ymm9, ymm8
  vpsubw ymm1, ymm0, ymm8
  vpaddw ymm0, ymm0, ymm8
  vpmullw ymm8, ymm3, YMMWORD PTR [rip + .Lprod3_t0b_b\branch\()_p\row\()_distance1_hi_qinv]
  vpmulhw ymm9, ymm3, YMMWORD PTR [rip + .Lprod3_t0b_b\branch\()_p\row\()_distance1_hi_zeta]
  vpmulhw ymm8, ymm8, ymm15
  vpsubw ymm8, ymm9, ymm8
  vpsubw ymm3, ymm2, ymm8
  vpaddw ymm2, ymm2, ymm8

  /* Isomorphic wire transpose: final sources are ymm8..ymm11. */
  PROD3_WIRE_GROUP 8,9,0,1,.Lwire_abs_b\branch\()p\row\()_g0,vpunpcklwd,vpunpckhwd
  PROD3_WIRE_GROUP 10,11,2,3,.Lwire_abs_b\branch\()p\row\()_g1,vpunpcklwd,vpunpckhwd
  PROD3_WIRE_GROUP 0,1,8,9,.Lwire_abs_b\branch\()p\row\()_g2,vpunpckldq,vpunpckhdq
  PROD3_WIRE_GROUP 2,3,10,11,.Lwire_abs_b\branch\()p\row\()_g3,vpunpckldq,vpunpckhdq
  PROD3_WIRE_GROUP 8,9,0,2,.Lwire_abs_b\branch\()p\row\()_g4,vpunpcklqdq,vpunpckhqdq
  PROD3_WIRE_GROUP 10,11,1,3,.Lwire_abs_b\branch\()p\row\()_g5,vpunpcklqdq,vpunpckhqdq
  PAIR_WIRE_OUTPUT \branch,\row,0,\base,.Lwire_abs_b\branch\()p\row\()_o0_src,.Lwire_abs_b\branch\()p\row\()_o0_qimm,.Lwire_abs_b\branch\()p\row\()_o0_shuffle
  PAIR_WIRE_OUTPUT \branch,\row,1,\base,.Lwire_abs_b\branch\()p\row\()_o1_src,.Lwire_abs_b\branch\()p\row\()_o1_qimm,.Lwire_abs_b\branch\()p\row\()_o1_shuffle
  PAIR_WIRE_OUTPUT \branch,\row,2,\base,.Lwire_abs_b\branch\()p\row\()_o2_src,.Lwire_abs_b\branch\()p\row\()_o2_qimm,.Lwire_abs_b\branch\()p\row\()_o2_shuffle
  PAIR_WIRE_OUTPUT \branch,\row,3,\base,.Lwire_abs_b\branch\()p\row\()_o3_src,.Lwire_abs_b\branch\()p\row\()_o3_qimm,.Lwire_abs_b\branch\()p\row\()_o3_shuffle
.endm
""".strip().splitlines()


def parse_sources(path: Path) -> dict[tuple[int, int], list[int]]:
    pattern = re.compile(r"\.equ \.Lwire_abs_b([01])p([0-8])_o([0-3])_src, ([0-3])")
    result = {(b, r): [None] * 4 for b in range(2) for r in range(9)}
    for branch, row, coefficient, source in pattern.findall(path.read_text()):
        result[(int(branch), int(row))][int(coefficient)] = int(source)
    if any(any(v is None for v in row) for row in result.values()):
        raise SystemExit("incomplete terminal source controls")
    return {key: [int(v) for v in row] for key, row in result.items()}


def packet_macros(pack_source: Path, packets, sources):
    lines = []
    maps = []
    for packet in packets:
        index = packet["packet"]
        first = packet["first"]
        second = packet["second"]
        low_sources = sources[(first["branch"], first["row"])]
        high_sources = sources[(second["branch"], second["row"])]
        # The final plane reuses the two source registers freed by plane 0.
        outputs = [(0, 1), (2, 3), (12, 13),
                   (4 + low_sources[0], 8 + high_sources[0])]
        data_regs = [outputs[p][0] for p in range(4)] + [outputs[p][1] for p in range(4)]
        if len(set(data_regs)) != 8 or any(reg >= 14 for reg in data_regs):
            raise SystemExit(f"packet {index}: invalid data allocation {data_regs}")
        temp_regs = [reg for reg in range(14) if reg not in data_regs]
        if len(temp_regs) != 6:
            raise SystemExit(f"packet {index}: invalid temp allocation")
        reg_map = {i: data_regs[i] for i in range(8)}
        reg_map.update({8 + i: temp_regs[i] for i in range(6)})
        reg_map.update({14: 15, 15: 14})
        maps.append({"packet": index, "low_sources": low_sources,
                     "high_sources": high_sources, "reg_map": reg_map})

        lines.append(f".macro PROD3_PAIR_SERIALIZE_V2_{index}")
        for plane, (even, odd) in enumerate(outputs):
            low = 4 + low_sources[plane]
            high = 8 + high_sources[plane]
            lines += [
                f"  vpshufb ymm{low}, ymm{low}, YMMWORD PTR [rip + .Lpair_v2_even_odd]",
                f"  vpshufb ymm{high}, ymm{high}, YMMWORD PTR [rip + .Lpair_v2_even_odd]",
                f"  vpermq ymm{low}, ymm{low}, 0xd8",
                f"  vpermq ymm{high}, ymm{high}, 0xd8",
                f"  vperm2i128 ymm{even}, ymm{low}, ymm{high}, 0x20",
                f"  vperm2i128 ymm{odd}, ymm{low}, ymm{high}, 0x31",
            ]
        lines += ["  .att_syntax prefix"]
        lines += ["  " + line for line in official_body(pack_source, reg_map)]
        lines += ["  .intel_syntax noprefix", ".endm", ""]
    return lines, maps


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schedule", type=Path, required=True)
    parser.add_argument("--pack-source", type=Path, required=True)
    parser.add_argument("--base-source", type=Path, required=True)
    parser.add_argument("--terminal-controls", type=Path, required=True)
    parser.add_argument("--macro-include", type=Path, required=True)
    parser.add_argument("--asm", type=Path, required=True)
    parser.add_argument("--header", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--symbol", default=SYMBOL)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    schedule = json.loads(args.schedule.read_text())
    if not schedule["decision"]["asm_authorized"]:
        raise SystemExit("pair-resident search did not authorize ASM")

    sources = parse_sources(args.terminal_controls)
    packet_bodies, register_maps = packet_macros(
        args.pack_source, schedule["packet_pairs"], sources)
    lines = ["/* Generated pair-resident D1/Serializer V2 macros. */"]
    lines += second_tile_macro() + [""] + packet_bodies
    lines += [".macro PROD3_PAIR_SERIALIZE_V2 packet"]
    for packet in range(9):
        lines += [("  .if" if packet == 0 else "  .elseif") + f" \\packet == {packet}",
                  f"    PROD3_PAIR_SERIALIZE_V2_{packet}"]
    lines += ["  .endif", ".endm", ""]
    lines += [
        ".macro PROD3_PAIR_PACKET packet,b0,base0,row0,b1,base1,row1,last=0",
        "  PROD3_PASS_B \\b0,\\base0,\\row0",
        "  PROD3_PASS_B_PAIR_SECOND \\b1,\\base1,\\row1",
        "  PROD3_PAIR_SERIALIZE_V2 \\packet",
        "  .if \\last == 0",
        "    add rsi, 192",
        "  .endif",
        ".endm", "",
        '.section .rodata,"a",@progbits', ".p2align 5", ".Lpair_v2_even_odd:",
        "  .byte 0,1,4,5,8,9,12,13,2,3,6,7,10,11,14,15,"
        "0,1,4,5,8,9,12,13,2,3,6,7,10,11,14,15", "",
    ]

    base_source = args.base_source.read_text()
    label = "ntruplus1152_exp001_gt9x16_prod3_aos_full:\n"
    size_line = (".size ntruplus1152_exp001_gt9x16_prod3_aos_full, "
                 ".-ntruplus1152_exp001_gt9x16_prod3_aos_full")
    body_start = base_source.index(label) + len(label)
    body_end = base_source.index(size_line, body_start)
    candidate_body = """  /* Exact two-tile Serializer V2 packet ownership. */
  PROD3_PASS_A 0,0,0
  PROD3_PASS_A 0,0,1
  PROD3_PASS_A 0,0,2
  PROD3_PASS_A 0,0,3
  vmovdqa ymm15, YMMWORD PTR [rip + .Lgt_q]
  vmovdqa ymm14, YMMWORD PTR [rip + _16xv]
  PROD3_PAIR_PACKET 0,0,0,5,0,0,4
  PROD3_PAIR_PACKET 1,0,0,3,0,0,0
  PROD3_PAIR_PACKET 2,0,0,2,0,0,1
  PROD3_PAIR_PACKET 3,0,0,7,0,0,6

  PROD3_PASS_A 1,1152,0
  PROD3_PASS_A 1,1152,1
  PROD3_PASS_A 1,1152,2
  PROD3_PASS_A 1,1152,3
  vmovdqa ymm15, YMMWORD PTR [rip + .Lgt_q]
  vmovdqa ymm14, YMMWORD PTR [rip + _16xv]
  PROD3_PAIR_PACKET 4,0,0,8,1,1152,1
  PROD3_PAIR_PACKET 5,1,1152,0,1,1152,2
  PROD3_PAIR_PACKET 6,1,1152,8,1,1152,7
  PROD3_PAIR_PACKET 7,1,1152,6,1,1152,5
  PROD3_PAIR_PACKET 8,1,1152,4,1,1152,3,1
  ret
"""
    candidate_source = (base_source[:body_start] + candidate_body
                        + base_source[body_end:])
    wrapper = f"""/* Generated namespaced pair-resident D1 + Serializer V2 prototype. */
#define PROD3_FULL_ONLY 1
#define PROD3_NATURAL_Q 1
#define PROD3_WIRE_MONOTONE 1
#define PROD3_T0_BETA 1
#define PROD3_SCALE1 1
#define PROD3_LAZY_R2_REDUCTIONS 1
#define ntruplus1152_exp001_gt9x16_prod3_aos_full {args.symbol}
.include "generated/d1-wire-monotone-absorption.inc"
.include "{args.macro_include.as_posix()}"
{candidate_source}
"""
    guard = "NTRUPLUS1152_EXP001_D1_PAIR_RESIDENT_V2_H"
    header = (f"#ifndef {guard}\n#define {guard}\n#include <stdint.h>\n"
              f"void {args.symbol}(int16_t state[1152], uint8_t bytes[1728]);\n"
              "#endif\n")
    contract = {
        "schema": "d1-pair-resident-v2-asm/v1",
        "symbol": args.symbol,
        "input": "in-place 2304-byte top-split scale-1 state",
        "outputs": ["raw exact wire-monotone MA2 state", "exact 1728 wire bytes"],
        "packet_pairs": [[p["first"]["tile"], p["second"]["tile"]]
                         for p in schedule["packet_pairs"]],
        "packet_register_maps": register_maps,
        "expected": {
            "packets": 9, "state_stores": 72, "serializer_state_loads": 0,
            "removed_state_loads_vs_forward_plus_v2": 72,
            "linked_instruction_delta_vs_forward_plus_v2": -74,
            "routing_delta": 0, "arithmetic_delta": 0,
            "stack_bytes": 0, "spill": False,
            "symbol_peak_ymm_bound": 16,
        },
        "decision": {"correctness_authorized": True, "benchmark_authorized": False},
    }
    write(args.macro_include, "\n".join(lines), args.check)
    write(args.asm, wrapper, args.check)
    write(args.header, header, args.check)
    write(args.contract, json.dumps(contract, indent=2, sort_keys=True) + "\n", args.check)
    print("pair-resident D1 + Serializer V2 ASM generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
