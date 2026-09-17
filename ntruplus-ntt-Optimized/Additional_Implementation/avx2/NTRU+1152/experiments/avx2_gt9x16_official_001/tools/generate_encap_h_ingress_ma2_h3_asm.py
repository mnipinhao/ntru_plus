#!/usr/bin/env python3
"""Generate the namespaced zero-materialization H3 PK-ingress/MA2 leaf."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import generate_encap_h_decode_natural_q_asm as h1


SYMBOL = "ntruplus1152_exp001_encap_h_ingress_ma2_h3"
CONTROL = "ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4"
DECODER_SOURCES = (11, 12, 13, 14, 7, 8, 9, 10)
H_A_REGS = (6, 11, 12, 13)
H_B_REGS = (7, 8, 9, 10)
WORK_REGS = {8: 4, 9: 5, 10: 14, 11: 15}


def write(path: Path, value: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text() != value:
            raise SystemExit(f"generated H3 ASM artifact is stale: {path}")
    else:
        path.write_text(value)


def tile_bodies(source: str) -> dict[tuple[int, int], str]:
    body = source.split(CONTROL + ":", 1)[1].split(f".size {CONTROL}", 1)[0]
    marker = re.compile(r"  /\* Natural-Q lane-wise MA2 tile b(\d+)p(\d+)\. \*/\n")
    matches = list(marker.finditer(body))
    result = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        result[(int(match.group(1)), int(match.group(2)))] = body[match.end():end]
    if len(result) != 18:
        raise SystemExit("expected 18 Natural-Q MA2 tile bodies")
    return result


def arithmetic_tail(body: str, h_regs: tuple[int, ...], tile: tuple[int, int]) -> list[str]:
    match = re.search(r"^  vmovdqa ymm4, YMMWORD PTR \[rsi \+ \d+\]$", body, re.M)
    if not match:
        raise SystemExit(f"missing r-quartet cut for tile {tile}")
    tail = body[match.start():].rstrip()
    mapping = {**{index: h_regs[index] for index in range(4)},
               **{4 + index: index for index in range(4)}, **WORK_REGS}

    def replace_mont_reg(match: re.Match[str]) -> str:
        values = [mapping[int(match.group(index))] for index in range(1, 5)]
        return "H3_MONT_REG " + ",".join(map(str, values))

    def replace_mont_const(match: re.Match[str]) -> str:
        dst, source, factor, factor_qinv, temporary = match.groups()
        return (f"H3_MONT_CONST {mapping[int(dst)]},{mapping[int(source)]},"
                f"{factor},{factor_qinv},{mapping[int(temporary)]}")

    tail = re.sub(r"MA1_MONT_REG (\d+),(\d+),(\d+),(\d+)",
                  replace_mont_reg, tail)
    tail = re.sub(r"MA1_MONT_CONST (\d+),(\d+),([^,]+),([^,]+),(\d+)",
                  replace_mont_const, tail)

    def replace_register(match: re.Match[str]) -> str:
        old = int(match.group(1))
        if old not in mapping:
            raise SystemExit(f"unexpected ymm{old} in MA2 tile {tile}")
        return f"ymm{mapping[old]}"

    tail = re.sub(r"ymm(\d+)", replace_register, tail)
    tail = tail.replace("[rsi", "[H3_R")
    tail = tail.replace("[rdx", "[H3_M")
    tail = tail.replace("[H3_R", "[rdx")
    tail = tail.replace("[H3_M", "[rcx")
    output = []
    coefficient = 0
    for line in tail.splitlines():
        if line.strip() == "ret":
            continue
        if re.match(r"  vmovdqa YMMWORD PTR \[rdi \+ \d+\], ymm4$", line):
            output.append(f"  H3_TERMINAL_C b{tile[0]}p{tile[1]},{coefficient},4")
            coefficient += 1
        output.append(line)
    if coefficient != 4:
        raise SystemExit(f"tile {tile} does not have four terminal stores")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schedule", type=Path, required=True)
    parser.add_argument("--natural-schedule", type=Path, required=True)
    parser.add_argument("--ma2-source", type=Path, required=True)
    parser.add_argument("--asm", type=Path, required=True)
    parser.add_argument("--header", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--symbol", default=SYMBOL)
    parser.add_argument("--representation", default="Natural-Q")
    parser.add_argument("--constant-include",
                        default="generated/gt9x16-prod3-ma2-qorder-natural-constants.inc")
    parser.add_argument("--constant-label-prefix", default=".Lqnat_lambda_")
    parser.add_argument("--formation-mode", choices=("mask", "pair-unpack"),
                        default="mask")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    symbol = args.symbol
    schedule = json.loads(args.schedule.read_text())
    natural = json.loads(args.natural_schedule.read_text())
    if not all(schedule["gates"].values()):
        raise SystemExit("H3 exact schedule is not authorized")
    plans = natural["resident_h"]["natural_plans"]
    bodies = tile_bodies(args.ma2_source.read_text())

    masks: dict[tuple[int, ...], str] = {}
    def mask_label(group: dict) -> str:
        key = tuple(group["vpshufb_mask"])
        if key not in masks:
            masks[key] = f".Lh3_mask_{len(masks)}"
        return masks[key]

    lines = [
        "/* Generated H3-full: PK bytes flow directly into Natural-Q MA2. */",
        ".intel_syntax noprefix", ".text",
        ".macro H3_MONT_CONST dst,a,factor,factor_qinv,tmp",
        "  vpmullw ymm\\tmp, ymm\\a, YMMWORD PTR [rip + \\factor_qinv]",
        "  vpmulhw ymm\\dst, ymm\\a, YMMWORD PTR [rip + \\factor]",
        "  vpmulhw ymm\\tmp, ymm\\tmp, YMMWORD PTR [rip + .Lma1_q]",
        "  vpsubw ymm\\dst, ymm\\dst, ymm\\tmp", ".endm", "",
        ".macro H3_MONT_REG dst,a,b,tmp",
        "  vpmullw ymm\\tmp, ymm\\a, YMMWORD PTR [rip + .Lma1_qinv]",
        "  vpmullw ymm\\tmp, ymm\\tmp, ymm\\b",
        "  vpmulhw ymm\\dst, ymm\\a, ymm\\b",
        "  vpmulhw ymm\\tmp, ymm\\tmp, YMMWORD PTR [rip + .Lma1_q]",
        "  vpsubw ymm\\dst, ymm\\dst, ymm\\tmp", ".endm", "",
        "/* Zero-instruction attachment point for a future terminal consumer. */",
        ".macro H3_TERMINAL_C tile,coefficient,reg", ".endm", "",
        f".globl {symbol}", f".type {symbol},@function", ".p2align 5", f"{symbol}:",
        "  xor eax, eax",
    ]

    blocks = schedule["formation"]["blocks"]
    for block_entry in blocks:
        block = block_entry["decode_block"]
        lines.append(f"  /* H3 block {block}: decode/validate/dual-form, then two MA2 tiles. */")
        decode_lines = h1.decode_block(block)
        decode_lines = decode_lines[:next(i for i, line in enumerate(decode_lines)
                                         if line.startswith("  vpmaxuw ymm0, ymm11"))]
        pair_by_end = {
            "  vpand ymm7, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]": 0,
            "  vpand ymm8, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]": 1,
            "  vpand ymm9, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]": 2,
            "  vpand ymm10, ymm3, YMMWORD PTR [rip + .Lhdec_low_mask]": 3,
        }

        def emit_formation(coefficient: int) -> list[str]:
            pair = block_entry["pair_flow"][coefficient]
            source_a = DECODER_SOURCES[coefficient]
            source_b = DECODER_SOURCES[coefficient + 4]
            final_a = H_A_REGS[coefficient]
            final_b = H_B_REGS[coefficient]
            plan_a = plans[pair["tile_a"]["natural_vector"]]
            plan_b = plans[pair["tile_b"]["natural_vector"]]
            if [source % 8 for source in plan_a["source_vectors"]] != [coefficient, coefficient + 4]:
                raise SystemExit("tile-A source pair changed")
            if [source % 8 for source in plan_b["source_vectors"]] != [coefficient, coefficient + 4]:
                raise SystemExit("tile-B source pair changed")
            ga0, ga1 = plan_a["groups"]
            gb0, gb1 = plan_b["groups"]
            if args.formation_mode == "pair-unpack":
                # The exact ownership maps show that the two p tiles are the
                # low- and high-128-bit halves of the same decoded source
                # pair.  Form both outputs together: unpack the full vectors
                # once, then select the corresponding half-pair.  This keeps
                # the established MA2 ABI while replacing ten routing
                # instructions with four for each coefficient pair.
                a_immediates = {ga0["vperm2i128_immediate"],
                                ga1["vperm2i128_immediate"]}
                b_immediates = {gb0["vperm2i128_immediate"],
                                gb1["vperm2i128_immediate"]}
                if (len(a_immediates) != 1 or len(b_immediates) != 1 or
                        a_immediates == b_immediates or
                        a_immediates | b_immediates != {"0x20", "0x31"}):
                    raise SystemExit("paired p tiles are not complementary halves")
                immediate_a = next(iter(a_immediates))
                immediate_b = next(iter(b_immediates))
                return [
                    f"  /* Paired formation: both p tiles from decoded d{coefficient}/d{coefficient + 4}. */",
                    f"  vpunpcklwd ymm15, ymm{source_a}, ymm{source_b}",
                    f"  vpunpckhwd ymm{final_a}, ymm{source_a}, ymm{source_b}",
                    f"  vperm2i128 ymm{final_b}, ymm15, ymm{final_a}, {immediate_b}",
                    f"  vperm2i128 ymm{final_a}, ymm15, ymm{final_a}, {immediate_a}",
                ]
            return [
                f"  /* Delayed dual formation: tile A h{coefficient} -> ymm{final_a}. */",
                f"  vperm2i128 ymm{final_a}, ymm{source_a}, ymm{source_a}, {ga0['vperm2i128_immediate']}",
                f"  vpshufb ymm{final_a}, ymm{final_a}, YMMWORD PTR [rip + {mask_label(ga0)}]",
                f"  vperm2i128 ymm15, ymm{source_b}, ymm{source_b}, {ga1['vperm2i128_immediate']}",
                f"  vpshufb ymm15, ymm15, YMMWORD PTR [rip + {mask_label(ga1)}]",
                f"  vpor ymm{final_a}, ymm{final_a}, ymm15",
                f"  /* Tile B h{coefficient} overwrites the dead decoded source pair. */",
                f"  vperm2i128 ymm15, ymm{source_a}, ymm{source_a}, {gb0['vperm2i128_immediate']}",
                f"  vpshufb ymm15, ymm15, YMMWORD PTR [rip + {mask_label(gb0)}]",
                f"  vperm2i128 ymm{source_a}, ymm{source_b}, ymm{source_b}, {gb1['vperm2i128_immediate']}",
                f"  vpshufb ymm{source_a}, ymm{source_a}, YMMWORD PTR [rip + {mask_label(gb1)}]",
                f"  vpor ymm{final_b}, ymm15, ymm{source_a}",
            ]

        for line in decode_lines[1:]:  # replace the H1 block comment with the H3 comment
            lines.append(line)
            if line not in pair_by_end:
                continue
            coefficient = pair_by_end[line]
            source_a = DECODER_SOURCES[coefficient]
            source_b = DECODER_SOURCES[coefficient + 4]
            lines += [
                f"  /* Validate d{coefficient}/d{coefficient + 4}; eax is the public invalid accumulator. */",
                f"  vpmaxuw ymm15, ymm{source_a}, ymm{source_b}",
                "  vpcmpgtw ymm15, ymm15, YMMWORD PTR [rip + .Lh3_qm1]",
                "  vpmovmskb r8d, ymm15", "  or eax, r8d",
            ]
            # The decoder still writes ymm6 while producing d1.  Keep pair 0
            # intact until that write has retired, then run a one-pair-delayed
            # formation pipeline.  This preserves the generated allocation
            # without introducing a seventeenth live YMM value.
            if coefficient >= 1:
                lines += emit_formation(coefficient - 1)

        lines += emit_formation(3)

        lines.append("  /* Same H1 R2 conversion, performed in place for both live quartets. */")
        for register in H_A_REGS + H_B_REGS:
            lines.append(f"  H3_MONT_CONST {register},{register},.Lma1_r2,.Lma1_r2_qinv,15")

        tile_a = (block_entry["tile_a"]["branch"], block_entry["tile_a"]["p"])
        tile_b = (block_entry["tile_b"]["branch"], block_entry["tile_b"]["p"])
        lines += [f"  /* Tile A b{tile_a[0]}p{tile_a[1]}: exact 16/16 YMM cut. */"]
        lines += [line.replace(".Lqnat_lambda_", args.constant_label_prefix)
                  for line in arithmetic_tail(bodies[tile_a], H_A_REGS, tile_a)]
        lines += [f"  /* Tile B b{tile_b[0]}p{tile_b[1]}: tile-A h/r are dead. */"]
        lines += [line.replace(".Lqnat_lambda_", args.constant_label_prefix)
                  for line in arithmetic_tail(bodies[tile_b], H_B_REGS, tile_b)]

    lines += ["  test eax, eax", "  setne al", "  movzx eax, al", "  ret",
              f".size {symbol}, .-{symbol}", "",
              ".section .rodata,\"a\",@progbits", ".p2align 5",
              ".Lhdec_low_mask:", "  .short " + ",".join(["4095"] * 16),
              ".Lh3_qm1:", "  .short " + ",".join(["3456"] * 16)]
    for key, label in masks.items():
        lines += [".p2align 5", f"{label}:", "  .byte " + ",".join(map(str, key))]
    lines += ['#include "generated/f0-ma2-constants.inc"',
              f'#include "{args.constant_include}"',
              "", ".section .note.GNU-stack,\"\",@progbits", ""]
    asm = "\n".join(lines)

    header = (
        "#ifndef NTRUPLUS1152_EXP001_ENCAP_H_INGRESS_MA2_H3_H\n"
        "#define NTRUPLUS1152_EXP001_ENCAP_H_INGRESS_MA2_H3_H\n"
        "#include <stdint.h>\n"
        f"int {symbol}(int16_t out[1152], const uint8_t pk[1728], "
        "const int16_t r_natural_scale4[1152], const int16_t m_natural_scale4[1152]);\n"
        "#endif\n")
    contract = {
        "schema": "encap-h-ingress-ma2-h3-asm/v1",
        "checkpoint": "ENCAP-H-INGRESS-MA2-H3-ASM",
        "symbol": symbol,
        "arguments": ["out_scale4", "pk_bytes", "r_natural_scale4", "m_natural_scale4"],
        "return": "1 iff Official poly_frombytes rejects pk, otherwise 0",
        "valid_output": f"raw bit-exact in the {args.representation} MA2 ABI",
        "alignment": {"entry": 32, "constants": 32, "pk": 1,
                      "out_r_m": 32},
        "expected": {
            "blocks": 9, "pk_loads": 54, "h_stores": 0, "h_reloads": 0,
            "output_stores": 72,
            "consumer_required_routes": 144 if args.formation_mode == "pair-unpack" else 360,
            "pure_h_abi_routes": 0, "h_r2_montgomery": 72,
            "h_times_r_montgomery": 288, "lambda_montgomery": 54,
            "peak_ymm": 16, "stack_bytes": 0,
            "validation_instruction_delta_vs_h1": 54,
            "total_instruction_delta_vs_h1": -91,
        },
        "formation_mode": args.formation_mode,
        "terminal_hook": "H3_TERMINAL_C before every coefficient-plane store",
        "benchmark_authorized": False,
    }
    write(args.asm, asm, args.check)
    write(args.header, header, args.check)
    write(args.contract, json.dumps(contract, indent=2, sort_keys=True) + "\n", args.check)
    print("H3 ASM: nine zero-h-boundary decode/MA2 waves generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
