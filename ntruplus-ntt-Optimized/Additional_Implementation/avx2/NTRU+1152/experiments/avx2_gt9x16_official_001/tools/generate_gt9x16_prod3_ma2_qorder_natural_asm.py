#!/usr/bin/env python3
"""Generate namespaced natural-Q resident-h, MA2-plane, and H1 AVX2 objects."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import generate_f0_ma1_asm1 as ma1
import generate_f0_ma2_asm as ma2
import generate_gt9x16_prod3_ma2_hash_h1_asm as h1


def write(path: Path, data: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text() != data:
            raise SystemExit(f"generated file is stale: {path}")
    else:
        path.write_text(data)


def label(mask: tuple[int, ...], masks: dict[tuple[int, ...], str], stem: str) -> str:
    if mask not in masks:
        masks[mask] = f".{stem}_mask_{len(masks)}"
    return masks[mask]


def natural_h(plan: dict, destination: int,
              masks: dict[tuple[int, ...], str]) -> list[str]:
    vectors = plan["source_vectors"]
    if len(vectors) != 2:
        raise SystemExit("natural h must use exactly two source vectors")
    out = [f"  vmovdqa ymm8, YMMWORD PTR [rcx + {32*vectors[0]}]",
           f"  vmovdqa ymm9, YMMWORD PTR [rcx + {32*vectors[1]}]"]
    for index, group in enumerate(plan["groups"]):
        sources = {vectors[0]: 8, vectors[1]: 9}
        lo = sources[group["low_source"]["vector"]]
        hi = sources[group["high_source"]["vector"]]
        out.append(f"  vperm2i128 ymm10, ymm{lo}, ymm{hi}, {group['vperm2i128_immediate']}")
        mask = label(tuple(group["vpshufb_mask"]), masks, "Lqnat_h")
        if index == 0:
            out.append(f"  vpshufb ymm{destination}, ymm10, YMMWORD PTR [rip + {mask}]")
        else:
            out += [f"  vpshufb ymm10, ymm10, YMMWORD PTR [rip + {mask}]",
                    f"  vpor ymm{destination}, ymm{destination}, ymm10"]
    return out


def natural_tile(tile: dict, plan_by_key: dict, masks: dict,
                 output_pointer: str) -> list[str]:
    name = ma1.label_tile(tile)
    base = ma2.tile_base(tile)
    out = [f"  /* Natural-Q lane-wise MA2 tile {name}. */"]
    for coefficient in range(4):
        out += natural_h(plan_by_key[(tile['tile']['branch'], tile['tile']['p'], coefficient)],
                         coefficient, masks)
        out.append(f"  MA1_MONT_CONST {coefficient},{coefficient},.Lma1_r2,.Lma1_r2_qinv,11")
    for coefficient in range(4):
        out += ma2.emit_native_plane("rsi", base, coefficient, 4 + coefficient)
    for coefficient, (plain, wrapped) in enumerate(ma2.TERMS):
        out += ma2.emit_native_plane("rdx", base, coefficient, 8)
        for h_index, r_index in plain:
            out += [f"  MA1_MONT_REG 10,{h_index},{4+r_index},11",
                    "  vpaddw ymm8, ymm8, ymm10"]
        for term_index, (h_index, r_index) in enumerate(wrapped):
            out.append(f"  MA1_MONT_REG 10,{h_index},{4+r_index},11")
            out.append("  vmovdqa ymm9, ymm10" if term_index == 0 else
                       "  vpaddw ymm9, ymm9, ymm10")
        if wrapped:
            out += [f"  MA1_MONT_CONST 10,9,.Lqnat_lambda_{name},.Lqnat_lambda_{name}_qinv,11",
                    "  vpaddw ymm8, ymm8, ymm10"]
        out += ["  MA1_MONT_CONST 8,8,.Lma1_inv4,.Lma1_inv4_qinv,11",
                f"  vmovdqa YMMWORD PTR [{output_pointer} + {base + 32*coefficient}], ymm8"]
    return out


def emit_h_projector(symbol: str, plans: list[dict], masks: dict) -> list[str]:
    out = [f".globl {symbol}", f".type {symbol},@function", ".p2align 5", f"{symbol}:",
           "  mov rcx, rsi"]
    for plan in plans:
        out += natural_h(plan, 0, masks)
        out.append(f"  vmovdqa YMMWORD PTR [rdi + {32*plan['destination_vector']}], ymm0")
    out += ["  ret", f".size {symbol}, .-{symbol}"]
    return out


def emit_natural_h1(schedule: dict, masks: dict) -> list[str]:
    symbol = "ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q"
    out = [f".globl {symbol}", f".type {symbol},@function", ".p2align 5", f"{symbol}:"]
    plans = schedule["H1"]["natural_plans"]
    for block in range(9):
        for register, plan in enumerate(plans[8*block:8*block+8]):
            for group_index, group in enumerate(plan["groups"]):
                out += [f"  vmovdqu ymm8, YMMWORD PTR [rsi + {32*group['low_source']['vector']}]",
                        f"  vmovdqu ymm9, YMMWORD PTR [rsi + {32*group['high_source']['vector']}]",
                        f"  vperm2i128 ymm10, ymm8, ymm9, {group['vperm2i128_immediate']}"]
                mask = label(tuple(group["vpshufb_mask"]), masks, "Lqnat_h1")
                if group_index == 0:
                    out.append(f"  vpshufb ymm{register}, ymm10, YMMWORD PTR [rip + {mask}]")
                else:
                    out += [f"  vpshufb ymm10, ymm10, YMMWORD PTR [rip + {mask}]",
                            f"  vpor ymm{register}, ymm{register}, ymm10"]
        out += ["  vmovdqa ymm13, YMMWORD PTR [rip + .Lqnat_h1_qinv]",
                "  vmovdqa ymm14, YMMWORD PTR [rip + .Lqnat_h1_inv4]",
                "  vmovdqa ymm15, YMMWORD PTR [rip + .Lqnat_h1_q]"]
        for register in range(8):
            out += [f"  vpmullw ymm11, ymm{register}, ymm13",
                    f"  vpmulhw ymm{register}, ymm{register}, ymm14",
                    "  vpmulhw ymm11, ymm11, ymm15",
                    f"  vpsubw ymm{register}, ymm{register}, ymm11",
                    f"  vpsraw ymm11, ymm{register}, 15",
                    "  vpand ymm11, ymm11, ymm15",
                    f"  vpaddw ymm{register}, ymm{register}, ymm11"]
        out += h1.PACK.rstrip().splitlines()
        out += h1.emit_store(192 * block)
    out += ["  ret", f".size {symbol}, .-{symbol}"]
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ma-schedule", type=Path, required=True)
    parser.add_argument("--natural-schedule", type=Path, required=True)
    parser.add_argument("--asm", type=Path, required=True)
    parser.add_argument("--constants", type=Path, required=True)
    parser.add_argument("--header", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    ma = json.loads(args.ma_schedule.read_text())
    natural = json.loads(args.natural_schedule.read_text())
    order = natural["contracts"]["natural_lane_to_semantic_q"]
    plans = natural["resident_h"]["natural_plans"]
    for plan in plans:
        plan["destination_vector"] = (ma2.tile_base(ma["semantic_tiles"][plan["tile"]]) // 32 +
                                      plan["coefficient"])
    plan_by_key = {(x["branch"], x["p"], x["coefficient"]): x for x in plans}
    masks: dict[tuple[int, ...], str] = {}

    current_masks: dict[tuple[int, ...], str] = {}
    current_h_specs = {}
    for tile in ma["semantic_tiles"]:
        name = ma1.label_tile(tile)
        for coefficient in range(4):
            spec = ma1.h_projection(tile, coefficient)
            current_h_specs[(name, coefficient)] = spec
            label(spec.shuffle, current_masks, "Lma2")
    if list(current_masks.values()) != [f".Lma2_mask_{i}" for i in range(len(current_masks))]:
        raise SystemExit("current MA2 mask numbering changed")

    lines = ["/* Generated natural-Q ASM0 machine objects. */", ".intel_syntax noprefix", ".text",
             ma1.emit_common_macros()]
    lines += emit_h_projector("ntruplus1152_exp001_project_h_natural_q", plans, masks)
    current_symbol = "ntruplus1152_exp001_f0_ma2_planes_current_q"
    lines += [f".globl {current_symbol}", f".type {current_symbol},@function", ".p2align 5", f"{current_symbol}:"]
    for tile in ma["semantic_tiles"]:
        base = ma2.tile_base(tile)
        lines += ma2.emit_tile(tile, current_h_specs, current_masks, base, base,
                               base, "rdi", native_inputs=True)
    lines += ["  ret", f".size {current_symbol}, .-{current_symbol}"]
    ma2_symbol = "ntruplus1152_exp001_f0_ma2_planes_natural_q"
    lines += [f".globl {ma2_symbol}", f".type {ma2_symbol},@function", ".p2align 5", f"{ma2_symbol}:"]
    for tile in ma["semantic_tiles"]:
        lines += natural_tile(tile, plan_by_key, masks, "rdi")
    lines += ["  ret", f".size {ma2_symbol}, .-{ma2_symbol}"]
    lines += emit_natural_h1(natural, masks)
    lines += ["", '.section .rodata,"a",@progbits',
              '#include "generated/f0-ma2-constants.inc"']
    constants = ["/* Generated natural-Q constants; all lane reindexing is offline. */"]
    for tile in ma["semantic_tiles"]:
        name = ma1.label_tile(tile)
        plane = tile["planes"][0]
        by_q = dict(zip(plane["semantic_q"], plane["lambda_mod_q"]))
        factors = [ma1.centered(by_q[q] * ma1.R) for q in order]
        constants += [".p2align 5", ma1.vec16(f".Lqnat_lambda_{name}", factors).rstrip(),
                      ".p2align 5", ma1.vec16(f".Lqnat_lambda_{name}_qinv", [ma1.signed16(x*ma1.QINV) for x in factors]).rstrip()]
    constants += [".p2align 5", ma1.vec16(".Lqnat_h1_qinv", [h1.INV4_QINV]*16).rstrip(),
                  ".p2align 5", ma1.vec16(".Lqnat_h1_inv4", [h1.INV4]*16).rstrip(),
                  ".p2align 5", ma1.vec16(".Lqnat_h1_q", [h1.Q]*16).rstrip()]
    for mask, name in masks.items():
        constants += [".p2align 5", ma1.bytes32(name, list(mask)).rstrip()]
    lines += ['#include "generated/gt9x16-prod3-ma2-qorder-natural-constants.inc"',
              '', '.section .note.GNU-stack,"",@progbits', '']
    current_order = natural["contracts"]["current_lane_to_semantic_q"]
    nat_from_current = [current_order.index(q) for q in order]
    h_source = [None] * 1152
    for tile in ma["semantic_tiles"]:
        base_vector = ma2.tile_base(tile) // 32
        for coefficient, plane in enumerate(tile["planes"]):
            by_q = dict(zip(plane["semantic_q"],
                            plane["resident_h_official_positions_i16"]))
            for lane, q in enumerate(order):
                h_source[16*(base_vector+coefficient)+lane] = by_q[q]
    if any(value is None for value in h_source):
        raise SystemExit("natural h source table is incomplete")
    table = lambda values, width: "\n".join(
        "  " + ", ".join(str(x) for x in values[i:i+width]) + ","
        for i in range(0, len(values), width))
    header = """#ifndef NTRUPLUS1152_EXP001_QORDER_NATURAL_ASM_H
#define NTRUPLUS1152_EXP001_QORDER_NATURAL_ASM_H
#include <stdint.h>
void ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q(int16_t x[1152]);
void ntruplus1152_exp001_project_h_natural_q(int16_t out[1152], const int16_t h[1152]);
void ntruplus1152_exp001_f0_ma2_planes_current_q(int16_t out[1152], const int16_t r[1152], const int16_t m[1152], const int16_t h[1152]);
void ntruplus1152_exp001_f0_ma2_planes_natural_q(int16_t out[1152], const int16_t r[1152], const int16_t m[1152], const int16_t h[1152]);
void ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q(uint8_t out[1728], const int16_t in[1152]);
static const uint8_t ntruplus1152_exp001_qnat_lane_from_current[16] = {
""" + table(nat_from_current, 16) + "\n};\n" + \
"static const uint16_t ntruplus1152_exp001_qnat_h_source[1152] = {\n" + \
table(h_source, 16) + "\n};\n" + """
#endif
"""
    contract = {"schema": "gt9x16-prod3-ma2-qorder-natural-asm/v1",
                "checkpoint": "GT9X16-PROD3-MA2-QORDER-NATURAL-ASM0",
                "symbols": {"producer": "ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q",
                            "resident_h": "ntruplus1152_exp001_project_h_natural_q",
                            "ma2_planes_control": current_symbol,
                            "ma2_planes": ma2_symbol,
                            "H1": "ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q"},
                "offline_lambda_reindex": True, "runtime_lambda_routes": 0,
                "arithmetic_changed": False, "T0_changed": False,
                "benchmark_authorized": False,
                "source_sha256": {"ma_schedule": hashlib.sha256(args.ma_schedule.read_bytes()).hexdigest(),
                                  "natural_schedule": hashlib.sha256(args.natural_schedule.read_bytes()).hexdigest()}}
    write(args.asm, "\n".join(lines), args.check)
    write(args.constants, "\n".join(constants) + "\n", args.check)
    write(args.header, header, args.check)
    write(args.contract, json.dumps(contract, indent=2, sort_keys=True)+"\n", args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
