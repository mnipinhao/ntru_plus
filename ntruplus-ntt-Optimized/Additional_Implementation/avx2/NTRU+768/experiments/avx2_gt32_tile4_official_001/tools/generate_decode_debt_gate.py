#!/usr/bin/env python3
"""Generate the bounded R1 Decode-debt attribution and D3 static gate."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "generated/tile4_q24_codec.json"
ASM = ROOT / "generated/tile4_decode_debt.inc"
REPORT = ROOT / "generated/tile4_decode_debt_static.json"


def transpose_store(lines: list[str], output: int) -> None:
    lines.extend([
        "\tQ24_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7",
        f"\tvmovdqu %ymm4, {output + 0}(%rdi)",
        f"\tvmovdqu %ymm5, {output + 32}(%rdi)",
        f"\tvmovdqu %ymm6, {output + 64}(%rdi)",
        f"\tvmovdqu %ymm7, {output + 96}(%rdi)",
    ])


def main() -> None:
    packets = json.loads(META.read_text())["packets_detail"]
    assert len(packets) == 48
    lines = [
        "/* Generated benchmark-only R1 Decode-debt probes. */",
        "",
        ".macro Q24_DECODE_SOA_NOVAL_BODY",
    ]
    for group in range(12):
        records = packets[4 * group:4 * group + 4]
        blocks = {int(record["destination_vector"]) // 4
                  for record in records}
        assert len(blocks) == 1
        for record in records:
            reg = int(record["destination_vector"]) % 4
            lines.append(
                "\tQ24_DECODE_REG_NOVAL "
                f"{record['low_load_offset']},{record['high_load_offset']},"
                f"{int(record['low_load_safe12'])},"
                f"{int(record['high_load_safe12'])},"
                f"{record['mask_label']},%ymm{reg},%ymm14"
            )
        transpose_store(lines, 128 * blocks.pop())
    lines.extend([".endm", "", ".macro Q24_DECODE_WIRE_BODY"])
    for packet in range(48):
        lines.append(
            "\tQ24_DECODE_WIRE_PACKET "
            f"{24 * packet},{24 * packet + 12},0,{int(packet == 47)},"
            f"{32 * packet},%ymm{8 + packet % 4}"
        )
    lines.extend([".endm", "", ".macro Q24_ROUTE_WIRE_TO_SOA_BODY"])
    for group in range(12):
        records = packets[4 * group:4 * group + 4]
        blocks = {int(record["destination_vector"]) // 4
                  for record in records}
        assert len(blocks) == 1
        for record in records:
            reg = int(record["destination_vector"]) % 4
            output_sources = [int(value)
                              for value in record["output_source_qwords"]]
            imm = sum(value << (2 * index)
                      for index, value in enumerate(output_sources))
            lines.extend([
                f"\tvmovdqu {32 * int(record['packet'])}(%rsi), %ymm{reg}",
                f"\tvpermq ${imm}, %ymm{reg}, %ymm{reg}",
            ])
        transpose_store(lines, 128 * blocks.pop())
    lines.extend([".endm", ""])
    ASM.write_text("\n".join(lines))

    groups = []
    for group in range(12):
        starts = [24 * (4 * group + packet) + half
                  for packet, half in ((0, 0), (0, 12), (1, 0), (1, 12),
                                       (2, 0), (2, 12), (3, 0), (3, 12))]
        modulo = [start % 16 for start in starts]
        crossing = [start for start in starts if start % 16 > 4]
        assert len(crossing) == 4
        groups.append({
            "group": group,
            "packet_start_mod16": modulo,
            "twelve_byte_windows_crossing_128b": len(crossing),
        })

    control = {
        "loads": 96,
        "cross_128_insert": 48,
        "unpack_vpshufb": 48,
        "transpose_shuffles": 144,
    }
    # Best packet-window factorization found for one 96-byte group:
    #   A=[L0,L1], B=[L2,L3], C=[L4,L5]
    #   G0=[L0,L3], G1=[L1,L4], G2=[L2,L5]   (3 x vperm2i128)
    #   X12=align12(G0,G1) -> [packet1,packet5]
    #   X8 =align8 (G1,G2) -> [packet2,packet6]
    #   four final vperm2i128 merge one aligned crossing lane with its
    #   non-crossing mate.  The ordinary four decode vpshufb then remain.
    lower = {
        "loads": 36,
        "source_lane_gathers": 36,
        "aligned_crossing_vector_formations": 24,
        "lane_select_or_merge": 48,
        "unpack_vpshufb": 48,
        "transpose_shuffles": 144,
        "peak_ymm_lower_bound": 12,
    }
    report = {
        "schema": "ntruplus768-gt32-r1-decode-debt-static-v1",
        "experiment": "R1-DECODE-DEBT-001",
        "d0_control": control,
        "d1": {
            "removed_packet_vpmaxuw": 48,
            "removed_finish_instructions": 6,
            "role": "attribution-only; not canonical-rejection-capable",
        },
        "d2": {
            "unpack_probe": "bytes-to-canonical-wire-order-int16",
            "route_probe": "wire-order-int16-to-current-private-M",
            "warning": "the split materializes 1536 bytes and is attribution only",
        },
        "d3_three_ymm_load_lower_bound": lower,
        "d3_delta_vs_control": {
            "loads": lower["loads"] - control["loads"],
            "pre_unpack_route_or_merge": (
                lower["source_lane_gathers"]
                + lower["aligned_crossing_vector_formations"]
                + lower["lane_select_or_merge"]
                - control["cross_128_insert"]),
            "minimum_total_instruction_delta_before_loop_control": 0,
        },
        "proof": {
            "per_96_byte_group": (
                "three contiguous YMM loads expose six 128-bit lanes; four "
                "of the eight 12-byte coefficient windows cross a 128-bit "
                "boundary.  Each desired output register pairs one crossing "
                "window with one non-crossing window at a different byte "
                "alignment, so a uniform lane-local shuffle cannot form both. "
                "The best packet-window factorization needs three source-lane "
                "gathers, two aligned crossing-window vectors, and four final "
                "lane merges per group."
            ),
            "avx2_constraint": (
                "vpshufb and vpalignr are independently lane-local; "
                "vpalignr applies one immediate to both 128-bit lanes"
            ),
        },
        "eligibility": {
            "load_delta_at_most_minus_48": True,
            "added_shuffle_at_most_36": False,
            "zero_spill_not_disproven": True,
        },
        "decision": "static-hard-stop-d3-added-route-lower-bound-60-exceeds-36",
        "reopen_only_if": [
            "a byte-window instruction can cross 128-bit lanes without a separate merge",
            "a wider ISA provides full-width byte permutes",
            "the consumer accepts a representation that removes the four-way M transpose",
        ],
        "groups": groups,
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
