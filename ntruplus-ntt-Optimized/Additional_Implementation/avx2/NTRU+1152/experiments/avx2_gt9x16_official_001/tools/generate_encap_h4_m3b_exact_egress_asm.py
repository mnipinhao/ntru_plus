#!/usr/bin/env python3
"""Generate the machine-probed exact H4-M3B canonical-scratch egress ASM."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SYMBOL = "ntruplus1152_exp001_encap_h4_m3b_exact_egress"
PRODUCER = (
    "ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta_scale1")


def write(path: Path, value: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text() != value:
            raise SystemExit(f"generated H4-M3B artifact is stale: {path}")
    else:
        path.write_text(value)


def emit_pack48(x: int, y: int) -> tuple[list[str], tuple[int, int, int]]:
    """Pack two ordered eight-pair YMMs into three 16-byte chunks."""
    return [
        f"  vpshufb ymm{x}, ymm{x}, YMMWORD PTR [rip + .Lh4_m3b_pack24]",
        f"  vpshufb ymm{y}, ymm{y}, YMMWORD PTR [rip + .Lh4_m3b_pack24]",
        f"  vextracti128 xmm4, ymm{x}, 1",
        f"  vextracti128 xmm5, ymm{y}, 1",
        "  vpslldq xmm6, xmm4, 12",
        f"  vpor xmm6, xmm6, xmm{x}",
        "  vpsrldq xmm7, xmm4, 4",
        f"  vpslldq xmm13, xmm{y}, 8",
        "  vpor xmm7, xmm7, xmm13",
        f"  vpsrldq xmm{x}, xmm{y}, 8",
        "  vpslldq xmm13, xmm5, 4",
        f"  vpor xmm{x}, xmm{x}, xmm13",
    ], (6, 7, x)


def emit_tile(tile: dict, index_labels: dict[tuple[int, ...], str]) -> tuple[list[str], dict]:
    vectors = tile["vectors"]
    lines = [f"  /* Machine-probed exact wire egress for vectors {vectors}. */"]
    for reg, vector in enumerate(vectors):
        lines.append(f"  vmovdqa ymm{reg}, YMMWORD PTR [r8 + {32 * vector}]")
    lines += [
        "  vpunpcklwd ymm4, ymm0, ymm1",
        "  vpunpckhwd ymm5, ymm0, ymm1",
        "  vpunpcklwd ymm6, ymm2, ymm3",
        "  vpunpckhwd ymm7, ymm2, ymm3",
        "  vpmaddwd ymm4, ymm4, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]",
        "  vpmaddwd ymm5, ymm5, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]",
        "  vpmaddwd ymm6, ymm6, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]",
        "  vpmaddwd ymm7, ymm7, YMMWORD PTR [rip + .Lh4_m3b_pair_weight]",
    ]

    by_index: dict[tuple[int, ...], list[int]] = {}
    for reg, source in zip(range(4, 8), tile["pair32_sources"]):
        key = tuple(source["permutation"])
        if key != tuple(range(8)):
            by_index.setdefault(key, []).append(reg)
    for key, registers in by_index.items():
        lines.append(f"  vmovdqa ymm0, YMMWORD PTR [rip + {index_labels[key]}]")
        for reg in registers:
            lines.append(f"  vpermd ymm{reg}, ymm0, ymm{reg}")

    register_by_interval = {}
    for network_index, network in enumerate(tile["networks"]):
        left, right = (4 + source for source in network["sources"])
        out_low, out_high = ((8, 9) if network_index == 0 else (2, 3))
        lines += [
            f"  vpunpckldq ymm0, ymm{left}, ymm{right}",
            f"  vpunpckhdq ymm1, ymm{left}, ymm{right}",
            f"  vperm2i128 ymm{out_low}, ymm0, ymm1, 0x20",
            f"  vperm2i128 ymm{out_high}, ymm0, ymm1, 0x31",
        ]
        register_by_interval[network["groups"][0][0] // 8] = out_low
        register_by_interval[network["groups"][1][0] // 8] = out_high

    intervals = sorted(register_by_interval)
    if intervals != list(range(intervals[0], intervals[0] + 4)):
        raise SystemExit("machine tile groups are not four consecutive intervals")
    ordered = [register_by_interval[interval] for interval in intervals]
    first, first_chunks = emit_pack48(ordered[0], ordered[1])
    lines += first
    for destination, source in zip((10, 11, 12), first_chunks):
        lines.append(f"  vmovdqa ymm{destination}, ymm{source}")
    second, second_chunks = emit_pack48(ordered[2], ordered[3])
    lines += second
    chunks = (10, 11, 12) + second_chunks
    lines += [
        f"  vinserti128 ymm0, ymm{chunks[0]}, xmm{chunks[1]}, 1",
        f"  vinserti128 ymm1, ymm{chunks[2]}, xmm{chunks[3]}, 1",
        f"  vinserti128 ymm2, ymm{chunks[4]}, xmm{chunks[5]}, 1",
    ]
    offsets = [tile["output_offset"] + 32 * index for index in range(3)]
    lines += [
        f"  vmovdqu YMMWORD PTR [rdi + {offsets[0]}], ymm0",
        f"  vmovdqu YMMWORD PTR [rdi + {offsets[1]}], ymm1",
        f"  vmovdqu YMMWORD PTR [rdi + {offsets[2]}], ymm2",
    ]
    return lines, {
        "scratch_loads": 4,
        "pair_unpack": 4,
        "pair_madd": 4,
        "vpermd_index_loads": len(by_index),
        "vpermd": sum(len(registers) for registers in by_index.values()),
        "parity_routes": 8,
        "pack_routes": 27,
        "pack_saves": 3,
        "ciphertext_stores": 3,
    }


def machine_tiles(machine: dict) -> list[dict]:
    source_to_wire = machine["source_to_wire"]
    if (machine.get("schema") != "h1-machine-wire-layout/v1" or
            len(source_to_wire) != 1152 or
            sorted(source_to_wire) != list(range(1152))):
        raise SystemExit("invalid Natural-Q H1 machine wire probe")
    tiles = []
    for vector_base in range(0, 72, 4):
        wires = [source_to_wire[16 * vector + lane]
                 for vector in range(vector_base, vector_base + 4)
                 for lane in range(16)]
        first = min(wires)
        if sorted(wires) != list(range(first, first + 64)):
            raise SystemExit("one vector quartet is not one 64-coefficient wire tile")
        sources = []
        for low_plane in (0, 2):
            for lanes in ((0, 1, 2, 3, 8, 9, 10, 11),
                          (4, 5, 6, 7, 12, 13, 14, 15)):
                pair_ids = []
                for lane in lanes:
                    low_wire = source_to_wire[16 * (vector_base + low_plane) + lane]
                    high_wire = source_to_wire[16 * (vector_base + low_plane + 1) + lane]
                    if high_wire != low_wire + 1 or (low_wire & 1):
                        raise SystemExit("machine wire endpoints are not plane-adjacent pairs")
                    pair_ids.append(low_wire // 2)
                permutation = sorted(range(8), key=lambda index: pair_ids[index])
                sources.append({"pair_ids": [pair_ids[index] for index in permutation],
                                "permutation": permutation})
        interval_sources: dict[tuple[int, int], list[int]] = {}
        for source_index, source in enumerate(sources):
            ids = source["pair_ids"]
            intervals = []
            for half in (ids[:4], ids[4:]):
                if any(b != a + 2 for a, b in zip(half, half[1:])):
                    raise SystemExit("machine pair32 source is not a parity stream")
                intervals.append(half[0] // 8)
            interval_sources.setdefault(tuple(intervals), []).append(source_index)
        networks = []
        for intervals, source_indices in sorted(interval_sources.items()):
            if len(source_indices) != 2:
                raise SystemExit("machine tile lacks one parity companion")
            a, b = source_indices
            left, right = sources[a]["pair_ids"], sources[b]["pair_ids"]
            if left[0] & 1:
                a, b = b, a
                left, right = right, left
            groups = []
            for half_index, interval in enumerate(intervals):
                merged = [item for pair in zip(
                    left[4 * half_index:4 * half_index + 4],
                    right[4 * half_index:4 * half_index + 4]) for item in pair]
                if merged != list(range(8 * interval, 8 * interval + 8)):
                    raise SystemExit("machine parity companion does not yield wire order")
                groups.append(merged)
            networks.append({"sources": [a, b], "groups": groups})
        if len(networks) != 2:
            raise SystemExit("machine tile does not have two parity networks")
        replay = sorted(pair for network in networks for group in network["groups"]
                        for pair in group)
        if replay != list(range(first // 2, first // 2 + 32)):
            raise SystemExit("machine tile pair replay is not exact")
        tiles.append({"vectors": list(range(vector_base, vector_base + 4)),
                      "first_wire": first, "pair32_sources": sources,
                      "networks": networks,
                      "output_offset": 3 * (first // 2)})
    tiles.sort(key=lambda item: item["first_wire"])
    if [tile["first_wire"] for tile in tiles] != [64 * i for i in range(18)]:
        raise SystemExit("machine wire tiles do not cover the output sequentially")
    return tiles


def generate(h3: str, machine: dict) -> tuple[str, dict]:

    h3 = h3.replace(
        "/* Generated H3-full: PK bytes flow directly into Natural-Q MA2. */",
        "/* Generated H4-M3B: H3 canonical scratch -> machine-probed exact wire egress. */")
    h3 = h3.replace(
        "ntruplus1152_exp001_encap_h_ingress_ma2_h3", SYMBOL)
    h3 = h3.replace("vpmovmskb r8d, ymm15", "vpmovmskb r9d, ymm15")
    h3 = h3.replace("or eax, r8d", "or eax, r9d")

    hook = re.compile(
        r"  H3_TERMINAL_C (b\d+p\d+),(\d),4\n"
        r"  vmovdqa YMMWORD PTR \[rdi \+ (\d+)\], ymm4")
    terminal_count = 0

    def terminal(match: re.Match[str]) -> str:
        nonlocal terminal_count
        tile, coefficient, offset = match.groups()
        terminal_count += 1
        return "\n".join([
            f"  /* H4_M3B_CANONICAL_STORE {tile},{coefficient}. */",
            "  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]",
            "  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]",
            "  vpsubw ymm4, ymm4, ymm15",
            "  vpsraw ymm15, ymm4, 15",
            "  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]",
            "  vpaddw ymm4, ymm4, ymm15",
            f"  vmovdqa YMMWORD PTR [r8 + {offset}], ymm4",
        ])

    h3, replacements = hook.subn(terminal, h3)
    if replacements != 72 or terminal_count != 72:
        raise SystemExit("did not replace all H3 terminal stores")

    tiles = machine_tiles(machine)
    index_values = []
    for tile in tiles:
        for source in tile["pair32_sources"]:
            key = tuple(source["permutation"])
            if key != tuple(range(8)) and key not in index_values:
                index_values.append(key)
    index_labels = {value: f".Lh4_m3b_index_{index}"
                    for index, value in enumerate(index_values)}

    egress = ["  /* All PK loads are complete before exact wire stores. */"]
    totals = {key: 0 for key in (
        "scratch_loads", "pair_unpack", "pair_madd", "vpermd_index_loads",
        "vpermd", "parity_routes", "pack_routes", "ciphertext_stores")}
    totals["pack_saves"] = 0
    for tile in tiles:
        tile_lines, counts = emit_tile(tile, index_labels)
        egress += tile_lines
        for key, value in counts.items():
            totals[key] += value
    expected = {
        "scratch_loads": 72, "pair_unpack": 72, "pair_madd": 72,
        "vpermd_index_loads": 30, "vpermd": 72,
        "parity_routes": 144, "pack_routes": 486,
        "pack_saves": 54,
        "ciphertext_stores": 54,
    }
    if totals != expected:
        raise SystemExit(f"M3B egress ledger changed: {totals}")

    needle = "  test eax, eax\n  setne al"
    if h3.count(needle) != 1:
        raise SystemExit("H3 return sequence changed")
    h3 = h3.replace(needle, "\n".join(egress) + "\n" + needle)

    constants = [".section .rodata,\"a\",@progbits"]
    for value, label in index_labels.items():
        constants += [".p2align 5", f"{label}:",
                      "  .long " + ",".join(str(item) for item in value)]
    constants += [
        ".p2align 5", ".Lh4_m3b_pair_weight:",
        "  .short " + ",".join(["1", "4096"] * 8),
        ".p2align 5", ".Lh4_m3b_pack24:",
        "  .byte 0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128,"
        "0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128",
    ]
    note = '.section .note.GNU-stack,"",@progbits'
    if h3.count(note) != 1:
        raise SystemExit("H3 GNU-stack marker changed")
    h3 = h3.replace(note, "\n".join(constants) + "\n\n" + note)
    return h3, totals


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--h3-source", type=Path, required=True)
    parser.add_argument("--machine-wire", type=Path, required=True)
    parser.add_argument("--asm", type=Path, required=True)
    parser.add_argument("--header", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    machine = json.loads(args.machine_wire.read_text())
    asm, counts = generate(args.h3_source.read_text(), machine)
    header = f"""\
#ifndef NTRUPLUS1152_EXP001_ENCAP_H4_M3B_EXACT_EGRESS_H
#define NTRUPLUS1152_EXP001_ENCAP_H4_M3B_EXACT_EGRESS_H
#include <stdint.h>
void {PRODUCER}(int16_t state[1152]);
int {SYMBOL}(uint8_t ct[1728], const uint8_t pk[1728],
             const int16_t r_scale1[1152], const int16_t m_scale1[1152],
             int16_t scratch[1152]);
#endif
"""
    contract = {
        "schema": "encap-h4-m3b-exact-egress-asm/v1",
        "checkpoint": "ENCAP-MA2-CT-EGRESS-H4-M3B-EXACT-EGRESS-ASM",
        "symbols": {"producer_scale1": PRODUCER, "h4_m3b": SYMBOL},
        "source_schedule": "Natural-Q H1 machine basis probe",
        "rejected": {
            "m2c_symbolic_lowering": True,
            "m2d_m2e_same_vector_lowering": True,
            "reason": "both symbolic ownership revisions failed full Official ciphertext differential",
        },
        "abi": {
            "scratch": "2304-byte aligned canonical Natural-Q scale-1 i16",
            "output": "1728 exact pinned-Official ciphertext bytes",
            "pk_equals_ct": True,
        },
        "generator_ledger": counts,
        "expected": {
            "terminal_normalization": 432,
            "terminal_scratch_stores": 72,
            "egress_instructions": 1056,
            "egress_peak_ymm": 14,
            "whole_function_peak_ymm": 16,
            "frame_bytes": 0,
        },
        "decision": {"correctness_authorized": True,
                     "benchmark_authorized": False,
                     "native_kem_authorized": False},
    }
    write(args.asm, asm, args.check)
    write(args.header, header, args.check)
    write(args.contract, json.dumps(contract, indent=2, sort_keys=True) + "\n",
          args.check)
    print("H4-M3B exact machine-probed egress ASM generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
