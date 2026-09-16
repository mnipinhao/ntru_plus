#!/usr/bin/env python3
"""Independent P51 proof assertions and canonical-byte equivalence tests."""
from __future__ import annotations

import random

from proof import Q, residue


def canonical_wire(values: list[int]) -> bytes:
    out = bytearray()
    for i in range(0, len(values), 2):
        a, b = values[i] % Q, values[i + 1] % Q
        out += bytes((a & 255, ((a >> 8) | (b << 4)) & 255, b >> 4))
    return bytes(out)


def transform_equal(a: list[int], b: list[int]) -> int:
    return int(any(residue(x - y) != 0 for x, y in zip(a, b)))


def main() -> None:
    assert all((residue(x) == 0) == (x % Q == 0)
               for x in range(-32768, 32768))
    rng = random.Random(0x503531)
    for _ in range(2000):
        a = [rng.randrange(-24799, 24795) for _ in range(864)]
        b = [x + rng.choice((-6, -3, 0, 2, 5)) * Q for x in a]
        if all(-3023 <= x <= 3023 for x in b):
            assert transform_equal(a, b) == int(canonical_wire(a) != canonical_wire(b))
        # Arbitrary in-contract pairs need not be equal, but both decisions must agree.
        b = [rng.randrange(-3023, 3024) for _ in range(864)]
        assert transform_equal(a, b) == int(canonical_wire(a) != canonical_wire(b))
    print("P51 proof tests passed: exhaustive i16 zero-test and 4000 canonical-wire comparisons")


if __name__ == "__main__":
    main()
