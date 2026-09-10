#!/usr/bin/env python3
"""Exact all-nine-row P6-D register-state/consumer model."""

from __future__ import annotations

import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOGICAL_FOR_PHYSICAL = [0, 3, 6, 1, 4, 7, 2, 5, 8]


def canonical(x: int) -> int:
    return x % 3457


def pair_stream(a: list[int], b: list[int]) -> bytes:
    out = bytearray()
    for x, y in zip(a, b):
        x, y = canonical(x), canonical(y)
        out.extend((x & 255, (x >> 8) | ((y & 15) << 4), y >> 4))
    return bytes(out)


def final_row(pairs: list[bytes]) -> bytes:
    return bytes(pairs[p][3 * lane + byte] for lane in range(8) for p in range(3) for byte in range(3))


def packed_a(rows: list[list[int]]) -> bytes:
    out = bytearray(112)
    for row in range(9):
        values = [canonical(x) for x in rows[row]]
        low_off = 8 * row
        out[low_off:low_off + 8] = bytes(x & 255 for x in values)
        high = bytes((values[2*i] >> 8) | ((values[2*i + 1] >> 8) << 4) for i in range(4))
        if row < 4: out[80 + 4 * row:84 + 4 * row] = high
        elif row < 8: out[96 + 4 * (row - 4):100 + 4 * (row - 4)] = high
        else: out[72:76] = high
    return bytes(out)


def unpack_a(packed: bytes, row: int) -> list[int]:
    low = packed[8 * row:8 * row + 8]
    if row < 4: high = packed[80 + 4 * row:84 + 4 * row]
    elif row < 8: high = packed[96 + 4 * (row - 4):100 + 4 * (row - 4)]
    else: high = packed[72:76]
    return [low[i] | (((high[i // 2] >> (4 * (i & 1))) & 15) << 8) for i in range(8)]


def source_for_d(d: int) -> str:
    if d < 26: return f"saved_q{d // 2}.d[{d & 1}]"
    return f"saved_gpr_slot{d - 26}"


def main() -> None:
    rng = random.Random(0x50364432)
    cases = 0
    for _ in range(4096):
        first = [[pair_stream([rng.randrange(-32768, 32768) for _ in range(8)],
                              [rng.randrange(-32768, 32768) for _ in range(8)]) for _pair in range(2)]
                 for _row in range(9)]
        a = [[rng.randrange(-32768, 32768) for _ in range(8)] for _ in range(9)]
        b = [[rng.randrange(-32768, 32768) for _ in range(8)] for _ in range(9)]
        pa = packed_a(a)
        assert all(unpack_a(pa, r) == [canonical(x) for x in a[r]] for r in range(9))

        dense = b"".join(first[logical][pair] for logical in LOGICAL_FOR_PHYSICAL for pair in range(2))
        assert len(dense) == 432
        streamed = bytearray()
        for physical, logical in enumerate(LOGICAL_FOR_PHYSICAL):
            start = 48 * physical
            p0, p1 = dense[start:start + 24], dense[start + 24:start + 48]
            p2 = pair_stream(unpack_a(pa, logical), b[logical])
            streamed += final_row([p0, p1, p2])
        expected = b"".join(final_row(first[logical] + [pair_stream(a[logical], b[logical])])
                            for logical in LOGICAL_FOR_PHYSICAL)
        assert bytes(streamed) == expected
        cases += 1

    rows = []
    for physical, logical in enumerate(LOGICAL_FOR_PHYSICAL):
        d = list(range(6 * physical, 6 * physical + 6))
        rows.append({
            "physical_row": physical,
            "logical_row": logical,
            "saved_pair_d_positions": d,
            "saved_pair_sources": [source_for_d(x) for x in d],
            "packed_a_low": f"packed_q{logical // 2}.d[{logical & 1}]" if logical < 8 else "packed_q4.d[0]",
            "packed_a_high": (f"packed_q5.bytes[{4*logical}:{4*logical+4}]" if logical < 4 else
                              f"packed_q6.bytes[{4*(logical-4)}:{4*(logical-4)+4}]" if logical < 8 else
                              "packed_q4.bytes[8:12]"),
            "b_vector": f"b{logical}",
            "output_bytes": [72 * physical, 72 * physical + 71],
        })

    result = {
        "cases": cases,
        "logical_rows_in_physical_store_order": LOGICAL_FOR_PHYSICAL,
        "saved_pair_state": {"q_registers": 13, "gpr_registers": 28, "bytes": 432},
        "consumer_rows": rows,
        "final_store_shape_per_top": {"bytes": 648, "str_q": 40, "str_d": 1, "lane_st3": 0},
        "coefficient_scratch_bytes": 0,
        "gate": "PASS_P6D2_ALL_ROW_LAYOUT_MODEL",
        "remaining": "P6-D3 must materialize this schedule in one public full/small assembly wrapper and prove whole-function allocation/correctness.",
    }
    (HERE / "complete-model-results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
