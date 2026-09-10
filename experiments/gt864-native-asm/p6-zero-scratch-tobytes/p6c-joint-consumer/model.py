#!/usr/bin/env python3
"""Exact P6-C byte map, dense saved-state layout, and liveness model."""

from __future__ import annotations

import json
import random
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
MERGE = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864/byte_merge_tables.h"
P = [0, 3, 6, 1, 4, 7, 2, 5, 8]


def merge_indices() -> list[list[int]]:
    text = MERGE.read_text()
    body = re.search(r"gt864_byte_merge_indices\[240\]\s*=\s*\{(.*?)\};", text, re.S)
    assert body is not None
    values = [int(x) for x in re.findall(r"\d+", body.group(1))]
    assert len(values) == 240
    return [values[i:i + 16] for i in range(0, 240, 16)]


def tbl(table: bytes, idx: list[int]) -> bytes:
    return bytes(table[x] if x < len(table) else 0 for x in idx)


def pair_stream(a: list[int], b: list[int]) -> bytes:
    out = bytearray()
    for x, y in zip(a, b):
        out.extend((x & 255, (x >> 8) | ((y & 15) << 4), y >> 4))
    return bytes(out)


def direct_row(pairs: list[bytes]) -> bytes:
    assert all(len(x) == 24 for x in pairs)
    return bytes(pairs[p][3 * k + c] for k in range(8) for p in range(3) for c in range(3))


def table_row(pairs: list[bytes], indices: list[list[int]]) -> bytes:
    p0 = pairs[0] + bytes(8)
    p1_dense = bytes(8) + pairs[1]
    a = [pairs[2][3 * k] for k in range(8)]
    m = [pairs[2][3 * k + 1] for k in range(8)]
    h = [pairs[2][3 * k + 2] for k in range(8)]
    p2 = bytes(a) + bytes(8) + bytes(m) + bytes(8) + bytes(h) + bytes(8)
    out = bytearray()
    for chunk in range(5):
        i0, i1, i2 = indices[3 * chunk:3 * chunk + 3]
        shifted_i1 = [x + 8 if x != 255 else x for x in i1]
        part0 = tbl(p0, i0)
        part1 = tbl(p1_dense, shifted_i1)
        part2 = tbl(p2, i2)
        merged = bytes(x | y | z for x, y, z in zip(part0, part1, part2))
        out.extend(merged if chunk < 4 else merged[:8])
    assert len(out) == 72
    return bytes(out)


def main() -> None:
    indices = merge_indices()
    rng = random.Random(0x503643)
    cases = 0
    for _ in range(4096):
        pairs = []
        for _pair in range(3):
            a = [rng.randrange(3457) for _ in range(8)]
            b = [rng.randrange(3457) for _ in range(8)]
            pairs.append(pair_stream(a, b))
        assert table_row(pairs, indices) == direct_row(pairs)
        cases += 1

    logical_rows = []
    for row in range(9):
        pairs = [bytes(((row * 73 + pair * 29 + i) & 255) for i in range(24)) for pair in range(3)]
        logical_rows.append(direct_row(pairs))
    natural = bytearray(648)
    for logical, physical in enumerate(P):
        natural[72 * physical:72 * (physical + 1)] = logical_rows[logical]
    physical_order = [P.index(i) for i in range(9)]
    streamed = b"".join(logical_rows[i] for i in physical_order)
    assert streamed == bytes(natural)
    q_stores, tail = divmod(len(streamed), 16)
    assert (q_stores, tail) == (40, 8)

    saved_d_chunks = 54
    saved_q_chunks = 26
    saved_x_chunks = saved_d_chunks - saved_q_chunks
    assert saved_x_chunks == 28
    early_complete_rows, early_remainder = divmod(saved_q_chunks, 6)
    assert (early_complete_rows, early_remainder) == (4, 2)

    frontiers = {
        "b_full_normalization": {"data": 29, "q_and_recip": 2, "quotient": 1, "peak": 32},
        "pair2_source_derivation": {"base_after_constants_die": 29, "bhi": 1, "mask": 1, "ahi": 1, "peak": 32},
        "merge_chunk": {"base_with_pair2_sources": 30, "part0": 1, "part1_or_part2": 1, "peak": 32},
        "after_first_row_with_carry": {"upper_bound": 26, "available": 32},
    }
    assert max(x.get("peak", x.get("upper_bound", 0)) for x in frontiers.values()) <= 32

    result = {
        "merge_rows_checked": cases,
        "merge_indices_checked": 15,
        "physical_row_order": physical_order,
        "top_store_shape": {"str_q": q_stores, "str_d": 1, "lane_st3": 0},
        "saved_state": {
            "bytes": 432,
            "d_chunks": saved_d_chunks,
            "q_resident_d_chunks": saved_q_chunks,
            "gpr_resident_d_chunks": saved_x_chunks,
            "complete_early_rows_in_q": early_complete_rows,
            "extra_early_d_chunks_in_q": early_remainder,
            "row0_tbl2_groups": ["Q0,Q1", "Q1,Q2"],
        },
        "frontiers": frontiers,
        "gate": "PASS_MODEL",
        "remaining": "P6-D complete all-nine-row kernel with cross-row carry and public ABI",
    }
    (HERE / "model-results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
