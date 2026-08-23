#!/usr/bin/env python3
"""Generate the exact B3-terminal-to-Q24 mapping for experiment 068.

The generator derives the packet schedule from the selected GT Clean pack.s
body.  It does not assume that M memory order resembles wire order.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
from pathlib import Path


def bitreverse5(value: int) -> int:
    return int(f"{value:05b}"[::-1], 2)


def physical_q(q4: int, lane: int) -> int:
    """Selected M lane mapping: lane bits [0..3] carry Q bits [2,3,0,1]."""
    q0 = (lane >> 2) & 1
    q1 = (lane >> 3) & 1
    q2 = lane & 1
    q3 = (lane >> 1) & 1
    return q0 | (q1 << 1) | (q2 << 2) | (q3 << 3) | (q4 << 4)


def unpack_words(a: list[dict], b: list[dict], high: bool) -> list[dict]:
    result: list[dict] = []
    for half in (0, 8):
        start = half + (4 if high else 0)
        for index in range(start, start + 4):
            result.extend((a[index], b[index]))
    return result


def unpack_dwords(a: list[dict], b: list[dict], high: bool) -> list[dict]:
    result: list[dict] = []
    for half in (0, 8):
        start = half + (4 if high else 0)
        result.extend(a[start:start + 2])
        result.extend(b[start:start + 2])
        result.extend(a[start + 2:start + 4])
        result.extend(b[start + 2:start + 4])
    return result


def unpack_qwords(a: list[dict], b: list[dict], high: bool) -> list[dict]:
    result: list[dict] = []
    for half in (0, 8):
        start = half + (4 if high else 0)
        result.extend(a[start:start + 4])
        result.extend(b[start:start + 4])
    return result


def transpose4(vectors: list[list[dict]]) -> list[list[dict]]:
    s0, s1, s2, s3 = vectors
    t0, t1 = unpack_words(s0, s1, False), unpack_words(s0, s1, True)
    t2, t3 = unpack_words(s2, s3, False), unpack_words(s2, s3, True)
    a0, a1 = unpack_dwords(t0, t2, False), unpack_dwords(t0, t2, True)
    a2, a3 = unpack_dwords(t1, t3, False), unpack_dwords(t1, t3, True)
    return [
        unpack_qwords(a0, a2, False),
        unpack_qwords(a0, a2, True),
        unpack_qwords(a1, a3, False),
        unpack_qwords(a1, a3, True),
    ]


def vpermq(words: list[dict], immediate: int) -> list[dict]:
    result: list[dict] = []
    for destination_qword in range(4):
        source_qword = (immediate >> (2 * destination_qword)) & 3
        result.extend(words[4 * source_qword:4 * source_qword + 4])
    return result


def parse_groups(pack: str) -> list[dict]:
    body = pack.split(".macro Q24_ENCODE_SOA_BODY", 1)[1].split(".endm", 1)[0]
    lines = body.splitlines()
    groups: list[dict] = []
    for index, line in enumerate(lines):
        match = re.search(r"vmovdqu\s+(\d+)\(%rsi\),\s+%ymm0", line)
        if not match:
            continue
        source_vector = int(match.group(1)) // 32
        following = "\n".join(lines[index:index + 14])
        packets = [
            {"transpose_output": int(register) - 4,
             "perm": int(perm), "byte_offset": int(offset),
             "safe_store": bool(int(safe))}
            for register, perm, offset, safe in re.findall(
                r"Q24_ENCODE_REG_PACKET\s+%ymm([4567]),%xmm\d+,(\d+),(\d+),(\d+)",
                following)
        ]
        if len(packets) != 4:
            raise ValueError(f"cannot parse four packets after vector {source_vector}")
        groups.append({
            "source_vector": source_vector,
            "block": source_vector // 4,
            "packets": packets,
        })
    if len(groups) != 12:
        raise ValueError(f"expected 12 Q24 groups, got {len(groups)}")
    return groups


def source_vectors(block: int) -> list[list[dict]]:
    tile = block // 2
    q4 = block & 1
    branch = tile & 1
    k3 = tile // 2
    vectors: list[list[dict]] = []
    for degree in range(4):
        vector_index = 4 * block + degree
        vector: list[dict] = []
        for lane in range(16):
            q = physical_q(q4, lane)
            vector.append({
                "block": block,
                "source_vector": vector_index,
                "source_word": 16 * vector_index + lane,
                "message_word": 16 * vector_index + lane,
                "degree": degree,
                "lane": lane,
                "branch": branch,
                "k3": k3,
                "q4": q4,
                "physical_Q": q,
                "logical_k32": bitreverse5(q),
            })
        vectors.append(vector)
    return vectors


def build(pack: str) -> tuple[dict, list[dict]]:
    groups = parse_groups(pack)
    mapping: list[dict] = []
    group_summary: list[dict] = []
    seen_targets: set[int] = set()
    seen_sources: set[int] = set()
    for group in groups:
        block = group["block"]
        transposed = transpose4(source_vectors(block))
        packet_summary: list[dict] = []
        for packet in group["packets"]:
            packet_index = packet["byte_offset"] // 24
            words = vpermq(transposed[packet["transpose_output"]], packet["perm"])
            packet_summary.append({
                "packet": packet_index,
                "byte_offset": packet["byte_offset"],
                "transpose_output": packet["transpose_output"],
                "vpermq_imm": packet["perm"],
                "safe_store": packet["safe_store"],
            })
            for packet_lane, source in enumerate(words):
                target = 16 * packet_index + packet_lane
                if target in seen_targets or source["source_word"] in seen_sources:
                    raise ValueError("mapping is not bijective")
                seen_targets.add(target)
                seen_sources.add(source["source_word"])
                mapping.append({
                    "target_coefficient": target,
                    "packet": packet_index,
                    "packet_lane": packet_lane,
                    **source,
                    "representative": "B3_general_R2_final_e0 + message_M_e0",
                    "next_operation": "signed-int16-v9-reduce-then-canonical-Q24-pack",
                })
        group_summary.append({
            "execution_group": len(group_summary),
            "block": block,
            "source_vector_start": group["source_vector"],
            "tile": block // 2,
            "branch": (block // 2) & 1,
            "k3": (block // 2) // 2,
            "q4": block & 1,
            "packets": packet_summary,
        })
    mapping.sort(key=lambda row: row["target_coefficient"])
    if seen_targets != set(range(768)) or seen_sources != set(range(768)):
        raise ValueError("incomplete B3/Q24 mapping")
    result = {
        "schema": "ntruplus768-gt32-encap-consumer-abi-068-mapping-v1",
        "experiment": "GT32-ENCAP-CONSUMER-ABI-068",
        "derived_from": "selected Q24_ENCODE_SOA_BODY in GT Clean pack.s",
        "contracts": {
            "ring": "Z_3457[x]/(x^768-x^384+1)",
            "representation": "B3 general R2-finalized e=0 plus message Forward e=0",
            "layout_at_retirement": "four M degree-plane YMMs for one 16-leaf block",
            "scale": "e=0",
            "bound": {
                "per_degree_conservative": [20215, 20250, 20285, 20296],
                "maximum": 20296,
                "source": "032 selected-executable DAG proof",
                "reducer": "selected v=9 reducer, proven over all signed int16 inputs by 032R",
            },
            "consumer": "canonical 48-packet Q24 byte stream",
        },
        "ordinary_complete_M_sum_materialized": False,
        "groups": group_summary,
        "mapping_rows": len(mapping),
        "mapping_bijective": True,
        "formation_candidate": {
            "name": "retire-block-direct-Q24",
            "algorithm": [
                "retire c0/c1/c2 through the existing 96-byte B3 internal scratch",
                "R2-finalize c0..c3 and add the matching message planes",
                "apply the selected 4x16 M-to-packet transpose",
                "reduce and pack four packets directly to their canonical byte offsets",
            ],
            "complete_M_store_count": 0,
            "complete_M_reload_count": 0,
            "internal_raw_B3_scratch_bytes": 96,
            "minimum_deleted_vs_032": {
                "final_sum_vector_stores": 48,
                "Q24_input_vector_loads": 48,
                "vector_bytes": 3072,
            },
            "dynamic_work_retained": {
                "message_vector_loads": 48,
                "message_adds": 48,
                "four_plane_transpose_instructions": 144,
                "Q24_reduction_and_pack_math": "unchanged",
            },
            "implementation_specific_costs_to_measure": [
                "twelve direct call/return pairs to a shared B3 block core",
                "per-block source/lambda offset formation",
                "eleven additional v=9 vector loads versus a standalone Q24 body",
            ],
        },
    }
    return result, mapping


def render_csv(rows: list[dict]) -> str:
    fields = [
        "target_coefficient", "packet", "packet_lane", "block",
        "source_vector", "source_word", "message_word", "degree", "lane",
        "branch", "k3", "q4", "physical_Q", "logical_k32",
        "representative", "next_operation",
    ]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows({field: row[field] for field in fields} for row in rows)
    return output.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--csv", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result, rows = build(args.pack.read_text())
    json_text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    csv_text = render_csv(rows)
    if args.check:
        if args.output.read_text() != json_text or args.csv.read_text() != csv_text:
            raise SystemExit("068 mapping artifacts are stale")
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json_text)
    args.csv.write_text(csv_text)


if __name__ == "__main__":
    main()
