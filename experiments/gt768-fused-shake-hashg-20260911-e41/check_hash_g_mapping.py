#!/usr/bin/env python3
"""Prove the fixed hash_g byte/lane mapping against a contiguous stream."""

from __future__ import annotations

import hashlib
import random


RATE = 136
INBYTES = 1152
OUTBYTES = 192


def le64(data: bytes) -> int:
    assert len(data) == 8
    return int.from_bytes(data, "little")


def lanes_to_bytes(lanes: list[int]) -> bytes:
    return b"".join(x.to_bytes(8, "little") for x in lanes)


def mapped_full_block(msg: bytes, block: int) -> list[int]:
    assert len(msg) == INBYTES
    assert 0 <= block < 8
    if block == 0:
        lanes = [le64(bytes([1]) + msg[0:7])]
        lanes.extend(le64(msg[8 * lane - 1 : 8 * lane + 7])
                     for lane in range(1, 17))
        return lanes
    start = RATE * block - 1
    return [le64(msg[start + 8 * lane : start + 8 * lane + 8])
            for lane in range(17)]


def mapped_tail(msg: bytes) -> list[int]:
    assert len(msg) == INBYTES
    tail = bytearray(RATE)
    tail[0:65] = msg[1087:1152]
    tail[65] = 0x1F
    tail[135] |= 0x80
    return [le64(tail[8 * lane : 8 * lane + 8]) for lane in range(17)]


def reference_blocks(msg: bytes) -> tuple[list[list[int]], list[int]]:
    stream = bytes([1]) + msg
    full = [
        [le64(stream[block * RATE + lane * 8:
                     block * RATE + lane * 8 + 8])
         for lane in range(17)]
        for block in range(8)
    ]
    tail = bytearray(RATE)
    remainder = stream[8 * RATE:]
    assert len(remainder) == 65
    tail[:len(remainder)] = remainder
    tail[len(remainder)] = 0x1F
    tail[-1] |= 0x80
    return full, [le64(tail[8 * lane:8 * lane + 8])
                  for lane in range(17)]


def check_one(msg: bytes) -> None:
    expected_full, expected_tail = reference_blocks(msg)
    actual_full = [mapped_full_block(msg, block) for block in range(8)]
    actual_tail = mapped_tail(msg)
    assert actual_full == expected_full
    assert actual_tail == expected_tail

    rebuilt = b"".join(lanes_to_bytes(block) for block in actual_full)
    rebuilt += lanes_to_bytes(actual_tail)
    semantic = bytes([1]) + msg
    expected_padded = semantic + bytes([0x1F])
    expected_padded += bytes(9 * RATE - len(expected_padded) - 1)
    expected_padded += bytes([0x80])
    assert rebuilt == expected_padded

    # The public result remains the standard SHAKE256 result.  This assertion
    # fixes the output size used by all later differential tests.
    assert len(hashlib.shake_256(semantic).digest(OUTBYTES)) == OUTBYTES


def main() -> None:
    vectors = [
        bytes(INBYTES),
        bytes([0xFF]) * INBYTES,
        bytes(i & 0xFF for i in range(INBYTES)),
    ]
    rng = random.Random(0xE41)
    vectors.extend(rng.randbytes(INBYTES) for _ in range(256))
    for msg in vectors:
        check_one(msg)
    print(f"PASS: {len(vectors)} messages; 8 full blocks + padded tail mapping")


if __name__ == "__main__":
    main()
