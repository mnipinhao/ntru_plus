#!/usr/bin/env python3
"""Small model for the decap verify direct-byte finalizer audit.

This is not a performance candidate. It only records the byte contract that a
future basemul-finalizer-to-bytes ASM path must match.
"""

import argparse

Q = 3457
CENTER_MIN = -1728
CENTER_MAX = 1728

# Public serialization order inside one 64-coefficient support-kernel chunk.
PUBLIC_TO_MEMORY = [
    0, 8, 16, 24, 32, 40, 48, 56,
    1, 9, 17, 25, 33, 41, 49, 57,
    2, 10, 18, 26, 34, 42, 50, 58,
    3, 11, 19, 27, 35, 43, 51, 59,
    4, 12, 20, 28, 36, 44, 52, 60,
    5, 13, 21, 29, 37, 45, 53, 61,
    6, 14, 22, 30, 38, 46, 54, 62,
    7, 15, 23, 31, 39, 47, 55, 63,
]


def normalize_centered(x):
    if not CENTER_MIN <= x <= CENTER_MAX:
        raise ValueError(f"centered coefficient out of modeled range: {x}")
    return x + (Q if x < 0 else 0)


def pack_pair(t0, t1):
    if not 0 <= t0 < 4096 or not 0 <= t1 < 4096:
        raise ValueError((t0, t1))
    return bytes([
        t0 & 0xff,
        ((t0 >> 8) | (t1 << 4)) & 0xff,
        (t1 >> 4) & 0xff,
    ])


def unpack_pair(data):
    if len(data) != 3:
        raise ValueError("packed pair must be exactly three bytes")
    t0 = data[0] | ((data[1] & 0x0f) << 8)
    t1 = (data[1] >> 4) | (data[2] << 4)
    return t0, t1


def pack_chunk_support_order(coeffs64):
    if len(coeffs64) != 64:
        raise ValueError("support chunk must contain 64 coefficients")

    ordered = [normalize_centered(coeffs64[i]) for i in PUBLIC_TO_MEMORY]
    out = bytearray()
    for i in range(0, 64, 2):
        out.extend(pack_pair(ordered[i], ordered[i + 1]))
    return bytes(out)


def unpack_chunk_support_order(packed):
    if len(packed) != 96:
        raise ValueError("packed support chunk must contain 96 bytes")

    ordered = []
    for i in range(0, 96, 3):
        ordered.extend(unpack_pair(packed[i:i + 3]))
    return ordered


def check_centered_range():
    for x in range(CENTER_MIN, CENTER_MAX + 1):
        t = normalize_centered(x)
        if not 0 <= t <= Q - 1:
            raise AssertionError((x, t))
        if t >= 4096:
            raise AssertionError((x, t))


def check_edge_pairs():
    edges = [CENTER_MIN, -1, 0, 1, CENTER_MAX]
    for x in edges:
        for y in edges:
            t0 = normalize_centered(x)
            t1 = normalize_centered(y)
            if unpack_pair(pack_pair(t0, t1)) != (t0, t1):
                raise AssertionError((x, y, t0, t1))


def check_layout_mapping():
    coeffs = list(range(64))
    packed = pack_chunk_support_order(coeffs)
    decoded = unpack_chunk_support_order(packed)
    if decoded != PUBLIC_TO_MEMORY:
        raise AssertionError((decoded, PUBLIC_TO_MEMORY))


def check_exhaustive_pairs():
    values = [normalize_centered(x) for x in range(CENTER_MIN, CENTER_MAX + 1)]
    for t0 in values:
        for t1 in values:
            if unpack_pair(pack_pair(t0, t1)) != (t0, t1):
                raise AssertionError((t0, t1))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip-exhaustive-pairs",
        action="store_true",
        help="skip the exhaustive centered coefficient pair round-trip check",
    )
    args = parser.parse_args()

    check_centered_range()
    check_edge_pairs()
    check_layout_mapping()
    if not args.skip_exhaustive_pairs:
        check_exhaustive_pairs()

    print("centered_range_ok=1")
    print("edge_pair_pack_ok=1")
    print("layout_mapping_ok=1")
    print(f"exhaustive_pairs_ok={0 if args.skip_exhaustive_pairs else 1}")


if __name__ == "__main__":
    main()
