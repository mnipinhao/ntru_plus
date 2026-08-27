#!/usr/bin/env python3
"""Generate the H4-M3 scale-1 MA2 terminal and packed ciphertext leaf."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SYMBOL = "ntruplus1152_exp001_encap_h4_m3"
PRODUCER = (
    "ntruplus1152_exp001_gt9x16_prod3_aos_full_natural_q_t0_beta_scale1")
PACK24 = (0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14,
          0x80, 0x80, 0x80, 0x80)


def write(path: Path, value: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text() != value:
            raise SystemExit(f"generated H4-M3 artifact is stale: {path}")
    else:
        path.write_text(value)


def emit_scale1_constants(audit: dict) -> str:
    lines = ["/* H4-M3 caller-wide scale-1 producer constants. */",
             ".section .rodata"]
    sites = audit["producer_scale1"]["alpha_sites"]
    if len(sites) != 18:
        raise SystemExit("scale-1 alpha-site count changed")
    for site in sites:
        branch = site["branch"]
        row = site["physical_row"]
        for suffix, value in (("", site["new_montgomery_signed"]),
                              ("_qinv", site["new_qinv_signed16"])):
            lines += [".p2align 5",
                      f".Lprod3_h4s1_b{branch}_r{row}_alpha{suffix}:",
                      "  .short " + ", ".join([str(value)] * 16)]
    lines.append("")
    return "\n".join(lines)


# Historical M2 lowering helpers below are deliberately not selected.  They
# remain executable documentation of the schedule that the first ASM
# differential rejected; generate_asm() uses canonical_h1_egress instead.
def source_intervals(vector: dict) -> tuple[int, int]:
    values = vector["pair_ids_after_final_sort"]
    return min(values[:4]) // 8, min(values[4:]) // 8


def emit_pack48(x: int, y: int, base: int) -> tuple[list[str], tuple[int, int, int]]:
    """Pack two consecutive eight-pair vectors into three exact XMM chunks."""
    xhi, yhi = base, base + 1
    o0, o1, tmp = base + 2, base + 3, base + 4
    lines = [
        f"  vpshufb ymm{x}, ymm{x}, YMMWORD PTR [rip + .Lh4_pack24]",
        f"  vpshufb ymm{y}, ymm{y}, YMMWORD PTR [rip + .Lh4_pack24]",
        f"  vextracti128 xmm{xhi}, ymm{x}, 1",
        f"  vextracti128 xmm{yhi}, ymm{y}, 1",
        f"  vpslldq xmm{o0}, xmm{xhi}, 12",
        f"  vpor xmm{o0}, xmm{o0}, xmm{x}",
        f"  vpsrldq xmm{o1}, xmm{xhi}, 4",
        f"  vpslldq xmm{tmp}, xmm{y}, 8",
        f"  vpor xmm{o1}, xmm{o1}, xmm{tmp}",
        f"  vpsrldq xmm{x}, xmm{y}, 8",
        f"  vpslldq xmm{tmp}, xmm{yhi}, 4",
        f"  vpor xmm{x}, xmm{x}, xmm{tmp}",
    ]
    return lines, (o0, o1, x)


def emit_tile_egress(tile: dict, scratch_offsets: dict[str, list[int]],
                     mask_labels: dict[tuple[int, ...], str]) -> list[str]:
    offsets = scratch_offsets[tile["tile"]]
    if len(offsets) != 4:
        raise SystemExit(f"bad scratch geometry for {tile['tile']}")
    lines = [f"  /* H4-M3 final egress {tile['tile']}. */"]
    for register, offset in enumerate(offsets):
        lines.append(f"  vmovdqa ymm{register}, YMMWORD PTR [r8 + {offset}]")
    lines += [
        "  vpunpcklwd ymm4, ymm0, ymm1",
        "  vpunpckhwd ymm5, ymm0, ymm1",
        "  vpunpcklwd ymm6, ymm2, ymm3",
        "  vpunpckhwd ymm7, ymm2, ymm3",
    ]
    for register in range(4, 8):
        lines.append(
            f"  vpmaddwd ymm{register}, ymm{register}, "
            "YMMWORD PTR [rip + .Lh4_pair_weight]")

    vectors = tile["scratch_pair32_vectors"]
    for register, vector in zip(range(4, 8), vectors):
        indices = tuple(vector["vpermd_sort_indices"])
        if vector["vpermd_required"]:
            label = mask_labels[indices]
            lines += [f"  vmovdqa ymm0, YMMWORD PTR [rip + {label}]",
                      f"  vpermd ymm{register}, ymm0, ymm{register}"]

    by_intervals: dict[tuple[int, int], list[int]] = {}
    for register, vector in zip(range(4, 8), vectors):
        by_intervals.setdefault(source_intervals(vector), []).append(register)
    groups: dict[int, int] = {}
    temporary = 0
    for intervals, registers in sorted(by_intervals.items()):
        if len(registers) != 2:
            raise SystemExit("parity companion geometry changed")
        left, right = registers
        lines += [f"  vpunpckldq ymm0, ymm{left}, ymm{right}",
                  f"  vpunpckhdq ymm1, ymm{left}, ymm{right}",
                  "  vperm2i128 ymm2, ymm0, ymm1, 0x20",
                  "  vperm2i128 ymm3, ymm0, ymm1, 0x31"]
        groups[intervals[0]] = 2
        groups[intervals[1]] = 3
        # Preserve the first interval pair while the second companion is made.
        if temporary == 0:
            lines += ["  vmovdqa ymm8, ymm2", "  vmovdqa ymm9, ymm3"]
        temporary += 1
    if temporary != 2 or sorted(groups) != [min(groups) + i for i in range(4)]:
        raise SystemExit("tile wire groups are no longer four consecutive intervals")

    # The first companion pair is in ymm8/ymm9 and the second in ymm2/ymm3.
    # Order the two 48-byte halves by their wire interval.
    first_pair = source_intervals(vectors[0])
    # Reconstruct which interval pair was preserved first from sorted keys.
    interval_pairs = sorted(by_intervals)
    preserved = interval_pairs[0]
    later = interval_pairs[1]
    pair_for_interval = {}
    pair_for_interval[preserved[0]] = 8
    pair_for_interval[preserved[1]] = 9
    pair_for_interval[later[0]] = 2
    pair_for_interval[later[1]] = 3
    ordered = [pair_for_interval[index] for index in sorted(pair_for_interval)]

    first_lines, first_chunks = emit_pack48(ordered[0], ordered[1], 4)
    lines += first_lines
    # Save first three chunks in ymm10..ymm12 before reusing the low registers.
    for destination, source in zip((10, 11, 12), first_chunks):
        lines.append(f"  vmovdqa ymm{destination}, ymm{source}")
    second_lines, second_chunks = emit_pack48(ordered[2], ordered[3], 4)
    lines += second_lines
    chunks = (10, 11, 12) + second_chunks
    lines += [
        f"  vinserti128 ymm0, ymm{chunks[0]}, xmm{chunks[1]}, 1",
        f"  vinserti128 ymm1, ymm{chunks[2]}, xmm{chunks[3]}, 1",
        f"  vinserti128 ymm2, ymm{chunks[4]}, xmm{chunks[5]}, 1",
    ]
    output_offset = min(span[0] for span in tile["wire_byte_spans"])
    if max(span[1] for span in tile["wire_byte_spans"]) != output_offset + 95:
        raise SystemExit("tile output is no longer one 96-byte ciphertext span")
    lines += [f"  vmovdqu YMMWORD PTR [rdi + {output_offset}], ymm0",
              f"  vmovdqu YMMWORD PTR [rdi + {output_offset + 32}], ymm1",
              f"  vmovdqu YMMWORD PTR [rdi + {output_offset + 64}], ymm2"]
    return lines


def exact_pair32_blocks(direct: dict) -> list[dict]:
    cells = {(cell["ma2"]["vector"], cell["ma2"]["lane"]):
             cell["official_coefficient"] for cell in direct["coefficient_map"]}
    blocks = []
    destinations = set()
    for source_block in range(144):
        vector = source_block // 2
        lane0 = 8 * (source_block & 1)
        pairs = []
        for lane in range(lane0, lane0 + 8, 2):
            a = cells[(vector, lane)]
            b = cells[(vector, lane + 1)]
            if a // 2 != b // 2 or (a & 1, b & 1) != (1, 0):
                raise SystemExit("Natural-Q adjacent-lane serializer ownership changed")
            pairs.append(a // 2)
        ordered = sorted(pairs)
        if ordered != list(range(ordered[0], ordered[0] + 4)):
            raise SystemExit("one source XMM no longer maps to four consecutive pairs")
        destination = ordered[0] // 4
        if destination in destinations:
            raise SystemExit("pair32 destination block is not bijective")
        destinations.add(destination)
        permutation = [pairs.index(value) for value in ordered]
        immediate = sum(index << (2 * output)
                        for output, index in enumerate(permutation))
        blocks.append({"source": source_block, "destination": destination,
                       "pair_ids": pairs, "vpshufd_immediate": immediate})
    if destinations != set(range(144)):
        raise SystemExit("pair32 block map is not a permutation")
    return blocks


def emit_pair32_cycles(blocks: list[dict]) -> tuple[list[str], dict]:
    by_source = {block["source"]: block for block in blocks}
    unseen = set(by_source)
    cycles = []
    while unseen:
        start = min(unseen)
        cycle = []
        source = start
        while source not in cycle:
            cycle.append(source)
            unseen.remove(source)
            source = by_source[source]["destination"]
        if source != start:
            raise SystemExit("pair32 permutation cycle did not close at its start")
        cycles.append(cycle)

    lines = ["  /* Exact in-place canonical-i16 -> Official-order pair32 permutation. */"]
    loads = stores = shuffles = 0
    for cycle_index, cycle in enumerate(cycles):
        lines += [f"  /* pair32 cycle {cycle_index}, length {len(cycle)}. */",
                  f"  vmovdqa xmm0, XMMWORD PTR [r8 + {16 * cycle[0]}]"]
        loads += 1
        for index, source in enumerate(cycle):
            block = by_source[source]
            destination = block["destination"]
            if index + 1 < len(cycle):
                lines.append(
                    f"  vmovdqa xmm1, XMMWORD PTR [r8 + {16 * destination}]")
                loads += 1
            lines += [
                "  vpmaddwd xmm0, xmm0, XMMWORD PTR [rip + .Lh4_pair_weight_rev]",
                f"  vpshufd xmm0, xmm0, {block['vpshufd_immediate']}",
                f"  vmovdqa XMMWORD PTR [r8 + {16 * destination}], xmm0",
            ]
            shuffles += 1
            stores += 1
            if index + 1 < len(cycle):
                lines.append("  vmovdqa xmm0, xmm1")
    return lines, {"cycles": len(cycles), "loads128": loads,
                   "stores128": stores, "vpmaddwd128": 144,
                   "vpshufd": shuffles}


def emit_sequential_egress() -> list[str]:
    lines = []
    for block in range(18):
        scratch = 128 * block
        output = 96 * block
        lines += [f"  /* Dense pair32 egress block {block}. */",
                  f"  vmovdqa ymm0, YMMWORD PTR [r8 + {scratch}]",
                  f"  vmovdqa ymm1, YMMWORD PTR [r8 + {scratch + 32}]"]
        first, chunks1 = emit_pack48(0, 1, 4)
        lines += first
        for destination, source in zip((10, 11, 12), chunks1):
            lines.append(f"  vmovdqa ymm{destination}, ymm{source}")
        lines += [f"  vmovdqa ymm2, YMMWORD PTR [r8 + {scratch + 64}]",
                  f"  vmovdqa ymm3, YMMWORD PTR [r8 + {scratch + 96}]"]
        second, chunks2 = emit_pack48(2, 3, 4)
        lines += second
        chunks = (10, 11, 12) + chunks2
        lines += [
            f"  vinserti128 ymm0, ymm{chunks[0]}, xmm{chunks[1]}, 1",
            f"  vinserti128 ymm1, ymm{chunks[2]}, xmm{chunks[3]}, 1",
            f"  vinserti128 ymm2, ymm{chunks[4]}, xmm{chunks[5]}, 1",
            f"  vmovdqu YMMWORD PTR [rdi + {output}], ymm0",
            f"  vmovdqu YMMWORD PTR [rdi + {output + 32}], ymm1",
            f"  vmovdqu YMMWORD PTR [rdi + {output + 64}], ymm2",
        ]
    return lines


def canonical_h1_egress(h1: str) -> tuple[list[str], dict]:
    """Reuse exact H1 ownership/routing after terminal canonicalization.

    M2's pair-locality model is false under the exact direct map.  This
    correctness control deliberately keeps H1 coefficient reconstruction but
    removes all inv4 and sign-canonicalization instructions, which H4 already
    performed at the terminal hooks.
    """
    symbol = "ntruplus1152_exp001_prod3_ma2_hash_h1_natural_q"
    body = h1.split(f"{symbol}:", 1)[1].split(f".size {symbol}", 1)[0]
    lines = ["  /* Exact-ownership fallback: canonical scratch -> H1 routing/pack. */"]
    normalization = re.compile(
        r"  vmovdqa ymm13, YMMWORD PTR \[rip \+ \.Lqnat_h1_qinv\]\n"
        r"  vmovdqa ymm14, YMMWORD PTR \[rip \+ \.Lqnat_h1_inv4\]\n"
        r"  vmovdqa ymm15, YMMWORD PTR \[rip \+ \.Lqnat_h1_q\]\n"
        r"(?:  (?:vpmullw|vpmulhw|vpsubw|vpsraw|vpand|vpaddw).*\n){56}")
    kept, removed = normalization.subn("", body)
    if removed != 9:
        raise SystemExit(f"Natural-Q H1 normalization block count changed: {removed}")
    kept = kept.replace("[rsi + ", "[r8 + ")
    kept = kept.replace("  ret\n", "")
    lines.extend(kept.rstrip().splitlines())
    return lines, {
        "blocks": 9, "scratch_data_loads": 272,
        "coefficient_reconstruction_routes": 336,
        "inv4_montgomery_instructions_removed": 288,
        "sign_canonicalization_instructions_removed": 216,
        "pack_transpose_routes": 324, "ciphertext_stores": 54,
    }


def generate_asm(h3: str, h1: str, schedule: dict,
                 direct: dict) -> tuple[str, dict]:
    profile = next(item for item in schedule["profiles"]
                   if item["presentation"] == "bitperm-3210-xor-0")
    selected = profile["families"]["M2-S2-canonical-i16"]
    if selected["ledger"]["total_instructions"] != 1502:
        raise SystemExit("selected H4-M2 schedule changed")

    h3_symbol = "ntruplus1152_exp001_encap_h_ingress_ma2_h3"
    h3 = h3.replace("/* Generated H3-full: PK bytes flow directly into Natural-Q MA2. */",
                    "/* Generated H4-M3: scale-1 H3 terminal -> canonical scratch -> exact ct. */")
    h3 = h3.replace(h3_symbol, SYMBOL)
    h3 = h3.replace("vpmovmskb r8d, ymm15", "vpmovmskb r9d, ymm15")
    h3 = h3.replace("or eax, r8d", "or eax, r9d")

    hook = re.compile(
        r"  H3_TERMINAL_C (b\d+p\d+),(\d),4\n"
        r"  vmovdqa YMMWORD PTR \[rdi \+ (\d+)\], ymm4")
    scratch_offsets: dict[str, list[int]] = {}

    def terminal(match: re.Match[str]) -> str:
        tile, coefficient, offset_text = match.groups()
        coefficient_i = int(coefficient)
        offset = int(offset_text)
        offsets = scratch_offsets.setdefault(tile, [])
        if coefficient_i != len(offsets):
            raise SystemExit(f"terminal plane order changed for {tile}")
        offsets.append(offset)
        return "\n".join([
            f"  /* H4_CANONICAL_STORE_C {tile},{coefficient_i},ymm4. */",
            "  vpmulhrsw ymm15, ymm4, YMMWORD PTR [rip + .Lma1_barrett]",
            "  vpmullw ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]",
            "  vpsubw ymm4, ymm4, ymm15",
            "  vpsraw ymm15, ymm4, 15",
            "  vpand ymm15, ymm15, YMMWORD PTR [rip + .Lma1_q]",
            "  vpaddw ymm4, ymm4, ymm15",
            f"  vmovdqa YMMWORD PTR [r8 + {offset}], ymm4",
        ])

    h3, count = hook.subn(terminal, h3)
    if count != 72 or len(scratch_offsets) != 18:
        raise SystemExit("did not replace all H3 terminal stores")

    # The linked correctness oracle is authoritative over the M2 abstract
    # pair labels.  Prove the mismatch explicitly before lowering the exact
    # H1-ownership fallback.
    cells = {(cell["ma2"]["vector"], cell["ma2"]["lane"]):
             cell["official_coefficient"] for cell in direct["coefficient_map"]}
    if cells[(20, 15)] != 0 or cells[(21, 15)] != 16 or cells[(20, 14)] != 1:
        raise SystemExit("exact serializer ownership sentinel changed")
    fallback, fallback_ledger = canonical_h1_egress(h1)
    egress = ["  /* All PK loads are complete before the first ciphertext store. */"]
    egress += fallback

    needle = "  test eax, eax\n  setne al"
    if h3.count(needle) != 1:
        raise SystemExit("H3 return sequence changed")
    h3 = h3.replace(needle, "\n".join(egress) + "\n" + needle)

    return h3, fallback_ledger


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--h3-source", type=Path, required=True)
    parser.add_argument("--h1-source", type=Path, required=True)
    parser.add_argument("--m2", type=Path, required=True)
    parser.add_argument("--scale-audit", type=Path, required=True)
    parser.add_argument("--direct-map", type=Path, required=True)
    parser.add_argument("--asm", type=Path, required=True)
    parser.add_argument("--producer-constants", type=Path, required=True)
    parser.add_argument("--header", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    schedule = json.loads(args.m2.read_text())
    scale = json.loads(args.scale_audit.read_text())
    if scale["decision"]["selected_for_h4_m1_mapping"] != "M0-C2-caller-wide":
        raise SystemExit("caller-wide scale-1 selection changed")
    direct = json.loads(args.direct_map.read_text())
    asm, fallback_ledger = generate_asm(
        args.h3_source.read_text(), args.h1_source.read_text(), schedule, direct)
    constants = emit_scale1_constants(scale)
    header = f"""\
#ifndef NTRUPLUS1152_EXP001_ENCAP_H4_M3_H
#define NTRUPLUS1152_EXP001_ENCAP_H4_M3_H
#include <stdint.h>
void {PRODUCER}(int16_t state[1152]);
int {SYMBOL}(uint8_t ct[1728], const uint8_t pk[1728],
             const int16_t r_scale1[1152], const int16_t m_scale1[1152],
             int16_t scratch[1152]);
#endif
"""
    contract = {
        "schema": "encap-h4-m3-asm/v1",
        "checkpoint": "ENCAP-MA2-CT-EGRESS-H4-M3-ASM",
        "symbols": {"producer_scale1": PRODUCER, "h4_m3": SYMBOL},
        "abi": {
            "inputs": "PK bytes plus Natural-Q/T0-beta caller-wide scale-1 r/m",
            "scratch": {"bytes": 2304, "alignment": 32,
                        "representation": "canonical i16 Natural-Q MA2 planes"},
            "output": {"bytes": 1728, "alignment": 1,
                       "representation": "exact Official ciphertext bytes"},
            "pk_equals_ct": True,
            "raw_terminal": "scale1; no terminal inv4",
        },
        "expected": {
            "producer_added_montgomery_chains_per_forward": 8,
            "terminal_vectors": 72, "terminal_barrett_instructions": 216,
            "terminal_sign_canonicalization_instructions": 216,
            "scratch_stores": 72, "scratch_reloads": 72,
            "m2_ownership_correction": (
                "exact serializer pairs are adjacent lanes within each plane, "
                "not same-lane values from adjacent planes"),
            "exact_ownership_fallback": fallback_ledger,
            "m2_selected_pair_primitive_realized": False,
            "dense_pack_routes": 486, "ciphertext_stores": 54,
            "inv4_montgomery_vectors": 0, "peak_ymm": 16,
        },
        "decision": {"correctness_authorized": True,
                     "m2_schedule_reopened": True,
                     "benchmark_authorized": False,
                     "native_kem_authorized": False},
    }
    write(args.asm, asm, args.check)
    write(args.producer_constants, constants, args.check)
    write(args.header, header, args.check)
    write(args.contract, json.dumps(contract, indent=2, sort_keys=True) + "\n",
          args.check)
    print("H4-M3 ASM: scale-1 producer and terminal-to-ciphertext leaf generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
