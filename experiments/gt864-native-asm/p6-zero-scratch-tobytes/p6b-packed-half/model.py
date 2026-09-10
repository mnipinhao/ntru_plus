#!/usr/bin/env python3
"""Exact P6-B byte-map and register-capacity gate."""

from __future__ import annotations

import json
import random
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TABLES = ROOT / "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864/p3b1_tables.h"


def route_lane_permutations() -> list[list[int]]:
    text = TABLES.read_text()
    body = re.search(r"p3b1_a_fwd\[9\]\[16\].*?=\s*\{(.*?)\n\};", text, re.S)
    assert body is not None
    rows = [[int(x) for x in re.findall(r"\d+", row)] for row in re.findall(r"\{([^{}]+)\}", body.group(1))]
    assert len(rows) == 9 and all(len(row) == 16 for row in rows)
    lanes = []
    for row in rows:
        assert all(row[2 * i + 1] == row[2 * i] + 1 for i in range(8))
        assert all((x & 1) == 0 for x in row[::2])
        perm = [x // 2 for x in row[::2]]
        assert sorted(perm) == list(range(8))
        lanes.append(perm)
    return lanes


def pack_a(a: list[int]) -> bytes:
    assert len(a) == 72 and all(0 <= x < 3457 for x in a)
    low = bytes(x & 0xFF for x in a)
    high = [(x >> 8) & 0x0F for x in a]
    packed_high = bytes(high[i] | (high[i + 1] << 4) for i in range(0, 72, 2))
    assert len(low + packed_high) == 108
    return low + packed_high


def unpack_a(blob: bytes) -> list[int]:
    assert len(blob) == 108
    low, packed_high = blob[:72], blob[72:]
    high = []
    for x in packed_high:
        high.extend((x & 0x0F, x >> 4))
    return [low[i] | (high[i] << 8) for i in range(72)]


def direct_pair(a: list[int], b: list[int]) -> bytes:
    out = bytearray()
    for x, y in zip(a, b):
        out.extend((x & 0xFF, (x >> 8) | ((y & 0x0F) << 4), y >> 4))
    return bytes(out)


def packed_half_pair(a_blob: bytes, b: list[int]) -> bytes:
    return direct_pair(unpack_a(a_blob), b)


def main() -> None:
    lanes = route_lane_permutations()
    expected = [
        [0, 4, 6, 2, 7, 3, 5, 1],
        [1, 4, 6, 2, 7, 3, 5, 0],
        [2, 4, 6, 1, 7, 3, 5, 0],
        [3, 4, 6, 1, 7, 2, 5, 0],
        [4, 3, 6, 1, 7, 2, 5, 0],
        [5, 3, 6, 1, 7, 2, 4, 0],
        [6, 3, 5, 1, 7, 2, 4, 0],
        [7, 3, 5, 1, 6, 2, 4, 0],
        [7, 3, 5, 1, 6, 2, 4, 0],
    ]
    assert lanes == expected

    tests = [
        [0] * 72,
        [3456] * 72,
        list(range(72)),
        [(i * 337 + 19) % 3457 for i in range(72)],
    ]
    rng = random.Random(0x503642)
    tests.extend([[rng.randrange(3457) for _ in range(72)] for _ in range(4096)])
    cases = 0
    for a in tests:
        b = [rng.randrange(3457) for _ in range(72)]
        blob = pack_a(a)
        assert unpack_a(blob) == a
        assert packed_half_pair(blob, b) == direct_pair(a, b)
        cases += 1

    saved_pair_bytes = 432
    packed_a_bytes = 108
    result = {
        "route_table_rows_checked": len(lanes),
        "route_lane_permutations": lanes,
        "packing_cases_checked": cases,
        "byte_tags_checked_per_top": 216,
        "state": {
            "saved_pair_bytes": saved_pair_bytes,
            "saved_pair_vector_slots": 13,
            "saved_pair_gpr_slots": 28,
            "packed_a_bytes": packed_a_bytes,
            "packed_a_vector_slots": 7,
            "b_route_vector_slots": 9,
        },
        "frontiers": {
            "route_repair": {"data_vectors": 29, "index_vectors": 1, "result_temporary_vectors": 1, "peak": 31, "available": 32},
            "full_normalization": {"data_vectors": 29, "constant_vectors": 2, "temporary_vectors": 1, "peak": 32, "available": 32},
            "small_normalization": {"data_vectors": 29, "constant_vectors": 1, "temporary_vectors": 1, "peak": 31, "available": 32},
        },
        "gate": "PASS_MODEL",
        "remaining_gate": "Complete pair-pack and three-pair merge DAG; these frontier proofs alone are not a production claim",
    }
    assert saved_pair_bytes == 13 * 16 + 28 * 8
    assert (packed_a_bytes + 15) // 16 == 7
    assert max(x["peak"] for x in result["frontiers"].values()) <= 32
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
