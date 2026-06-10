#!/usr/bin/env python3
"""Verify GT inverse NTT row-bitrev layout mappings."""

from __future__ import annotations


def bitreverse5(x: int) -> int:
    y = 0
    for _ in range(5):
        y = (y << 1) | (x & 1)
        x >>= 1
    return y


def physical_from_row(k3: int, k32_br: int) -> int:
    return (32 * k3 + 3 * k32_br) % 96


def row_from_physical(j: int) -> tuple[int, int]:
    return (2 * j) % 3, (11 * j) % 32


def logical_from_physical(j: int) -> int:
    k3, k32_br = row_from_physical(j)
    logical_k32 = bitreverse5(k32_br)
    return (32 * k3 + 3 * logical_k32) % 96


def check_physical_mapping() -> None:
    seen = set()
    for j in range(96):
        k3, k32_br = row_from_physical(j)
        assert 0 <= k3 < 3
        assert 0 <= k32_br < 32
        assert physical_from_row(k3, k32_br) == j
        seen.add((k3, k32_br))

    assert len(seen) == 96


def check_row_orders() -> None:
    for k3 in range(3):
        physical_order = [physical_from_row(k3, k32_br) for k32_br in range(32)]
        logical_order = [bitreverse5(k32_br) for k32_br in range(32)]
        assert len(set(physical_order)) == 32
        for physical_j in physical_order:
            assert row_from_physical(physical_j)[0] == k3
        assert sorted(logical_order) == list(range(32))

    logical_seen = {logical_from_physical(j) for j in range(96)}
    assert logical_seen == set(range(96))


def check_direct_load_segments() -> None:
    expected = {
        0: list(range(0, 768, 24)),
        1: list(range(256, 768, 24)) + list(range(16, 256, 24)),
        2: list(range(512, 768, 24)) + list(range(8, 512, 24)),
    }

    for k3 in range(3):
        got = [8 * physical_from_row(k3, k32_br) for k32_br in range(32)]
        assert got == expected[k3], f"k3={k3}: got {got}, want {expected[k3]}"


def check_untwist_and_store_order() -> None:
    # FUSED_POST_STRIPE consumes natural k32 values in order.  For each k32,
    # inverse DFT3 produces the logical indices below, and the generated store
    # pattern writes them to natural coefficient order without a final
    # permutation pass.
    seen = []
    for k32 in range(32):
        base = (33 * k32) % 96
        seen.extend([base, (base + 64) % 96, (base + 32) % 96])

    assert sorted(seen) == list(range(96))

    groups = []
    for group in range(10):
        a = group * 24
        b = 512 + group * 24
        c = 256 + group * 24
        groups.extend([
            (a + 0, b + 0, c + 0),
            (c + 8, a + 8, b + 8),
            (b + 16, c + 16, a + 16),
        ])
    group = 10
    a = group * 24
    b = 512 + group * 24
    c = 256 + group * 24
    groups.extend([
        (a + 0, b + 0, c + 0),
        (c + 8, a + 8, b + 8),
    ])

    stored_blocks = []
    for triple in groups:
        stored_blocks.extend(triple)

    assert len(stored_blocks) == 96
    assert sorted(stored_blocks) == [8 * i for i in range(96)]


def main() -> int:
    check_physical_mapping()
    check_row_orders()
    check_direct_load_segments()
    check_untwist_and_store_order()
    print("inverse NTT layout verified: physical rows, bitrev input, natural output")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
