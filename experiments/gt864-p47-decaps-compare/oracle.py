#!/usr/bin/env python3
"""Exact record and status oracle for P47's fused serializer comparison."""
from __future__ import annotations

import random

Q = 3457


def canonical(x: int) -> int:
    return x % Q


def pack8(values: list[int]) -> bytes:
    assert len(values) == 8
    output = bytearray()
    for i in range(0, 8, 2):
        a = canonical(values[i])
        b = canonical(values[i + 1])
        output.extend((a & 255, ((a >> 8) | (b << 4)) & 255, (b >> 4) & 255))
    return bytes(output)


def fused_compare(records: list[bytes], expected: bytes) -> int:
    mismatch = 0
    offset = 0
    for record in records:
        assert len(record) == 12
        low = int.from_bytes(record[:8], "little") ^ int.from_bytes(expected[offset:offset + 8], "little")
        high = int.from_bytes(record[8:12], "little") ^ int.from_bytes(expected[offset + 8:offset + 12], "little")
        mismatch |= low | high
        offset += 12
    assert offset == len(expected) == 1296
    return int(mismatch != 0)


def main() -> None:
    rng = random.Random(0x5047)
    for trial in range(1000):
        coeffs = [rng.randrange(-32768, 32768) for _ in range(864)]
        records = [pack8(coeffs[i:i + 8]) for i in range(0, 864, 8)]
        wire = b"".join(records)
        assert fused_compare(records, wire) == 0
        for position in (0, 7, 8, 11, 12, 647, 648, 1291, 1295, rng.randrange(1296)):
            bad = bytearray(wire)
            bad[position] ^= 1 << rng.randrange(8)
            assert fused_compare(records, bytes(bad)) == 1
    print("P47 oracle passed: 1000 arbitrary signed-int16 polynomials, exact equality and 10000 fixed/random byte mismatches")


if __name__ == "__main__":
    main()
