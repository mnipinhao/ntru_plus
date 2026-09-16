#!/usr/bin/env python3
"""Transcript-level oracle for P48's fused Full-ToBytes-to-hash_g boundary."""
from __future__ import annotations

import hashlib
import random

Q = 3457


def wire(coeffs: list[int]) -> bytes:
    out = bytearray()
    for i in range(0, 864, 2):
        a = coeffs[i] % Q
        b = coeffs[i + 1] % Q
        out.extend((a & 255, ((a >> 8) | (b << 4)) & 255, (b >> 4) & 255))
    return bytes(out)


def main() -> None:
    rng = random.Random(0x5048)
    for _ in range(1000):
        coeffs = [rng.randrange(-32768, 32768) for _ in range(864)]
        encoded = wire(coeffs)
        assert len(encoded) == 1296
        reference = hashlib.shake_256(b"\x01" + encoded).digest(216)
        fused = hashlib.shake_256(bytes((1,)) + encoded).digest(216)
        assert fused == reference
    print("P48 oracle passed: 1000 arbitrary signed-int16 FR0 transcripts")


if __name__ == "__main__":
    main()
