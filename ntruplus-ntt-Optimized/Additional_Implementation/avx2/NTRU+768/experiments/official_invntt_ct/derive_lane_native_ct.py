#!/usr/bin/env python3
"""Derive canonical inner CT twiddles and unavoidable root-boundary scales."""

import argparse
import re
from pathlib import Path

Q = 3457
R = (1 << 16) % Q


def parse_array(path: Path, name: str) -> list[int]:
    text = path.read_text()
    match = re.search(
        rf"const int16_t {name}\[816\].*?=\s*\{{(.*?)\}};", text, re.S
    )
    if match is None:
        raise ValueError(f"cannot find {name} in {path}")
    return [int(value) for value in re.findall(r"-?\d+", match.group(1))]


def inv(value: int) -> int:
    return pow(value % Q, Q - 2, Q)


def effective_twiddle(stored: int) -> int:
    return (stored % Q) * inv(R) % Q


def stored_twiddle(effective: int) -> int:
    value = effective * R % Q
    return value if value <= Q // 2 else value - Q


def qinv_word(stored: int) -> int:
    value = (stored * 12929) & 0xFFFF
    return value if value < 0x8000 else value - 0x10000


def shift_qword(values: list[int], lanes: int) -> list[int]:
    out = []
    for base in range(0, 16, 4):
        chunk = values[base:base + 4]
        out.extend([0] * lanes + chunk[:4 - lanes])
    return out


def blend(a: list[int], b: list[int], mask: int, width: int) -> list[int]:
    """Intel blend: take b for set mask elements, otherwise a."""
    out = a[:]
    elements = 16 // width
    for element in range(elements):
        # VPBLENDW repeats its eight immediate bits in each 128-bit lane.
        mask_bit = element % 8 if width == 1 else element
        if (mask >> mask_bit) & 1:
            start = element * width
            out[start:start + width] = b[start:start + width]
    return out


def unpack_qword(a: list[int], b: list[int], high: bool) -> list[int]:
    out = []
    for half in range(2):
        base = half * 8 + (4 if high else 0)
        out.extend(a[base:base + 4])
        out.extend(b[base:base + 4])
    return out


def perm2(a: list[int], b: list[int], imm: int) -> list[int]:
    halves = [a[:8], a[8:], b[:8], b[8:]]
    return halves[imm & 3] + halves[(imm >> 4) & 3]


def shuffle_level(regs: list[list[int]], level: int) -> list[list[int]]:
    r11, r12, r13, r14, r7, r8, r9, r10 = regs
    if level == 6:
        a3 = blend(r11, shift_qword(r12, 1), 0xAA, 1)
        a4 = blend(r13, shift_qword(r14, 1), 0xAA, 1)
        a5 = blend(r7, shift_qword(r8, 1), 0xAA, 1)
        a6 = blend(r9, shift_qword(r10, 1), 0xAA, 1)
        sr9 = shift_qword(r9, -1) if False else sum(
            (r9[base + 1:base + 4] + [0] for base in range(0, 16, 4)), []
        )
        sr7 = sum((r7[base + 1:base + 4] + [0] for base in range(0, 16, 4)), [])
        sr13 = sum((r13[base + 1:base + 4] + [0] for base in range(0, 16, 4)), [])
        sr11 = sum((r11[base + 1:base + 4] + [0] for base in range(0, 16, 4)), [])
        a10 = blend(sr9, r10, 0xAA, 1)
        a9 = blend(sr7, r8, 0xAA, 1)
        a8 = blend(sr13, r14, 0xAA, 1)
        a7 = blend(sr11, r12, 0xAA, 1)
        return [a3, a4, a5, a6, a7, a8, a9, a10]
    if level == 5:
        a3 = blend(r11, shift_qword(r12, 2), 0xAA, 2)
        a4 = blend(r13, shift_qword(r14, 2), 0xAA, 2)
        a5 = blend(r7, shift_qword(r8, 2), 0xAA, 2)
        a6 = blend(r9, shift_qword(r10, 2), 0xAA, 2)
        def right2(v: list[int]) -> list[int]:
            return sum((v[base + 2:base + 4] + [0, 0] for base in range(0, 16, 4)), [])
        a10 = blend(right2(r9), r10, 0xAA, 2)
        a9 = blend(right2(r7), r8, 0xAA, 2)
        a8 = blend(right2(r13), r14, 0xAA, 2)
        a7 = blend(right2(r11), r12, 0xAA, 2)
        return [a3, a4, a5, a6, a7, a8, a9, a10]
    if level == 4:
        return [
            unpack_qword(r11, r12, False), unpack_qword(r13, r14, False),
            unpack_qword(r7, r8, False), unpack_qword(r9, r10, False),
            unpack_qword(r11, r12, True), unpack_qword(r13, r14, True),
            unpack_qword(r7, r8, True), unpack_qword(r9, r10, True),
        ]
    if level == 3:
        return [
            perm2(r11, r12, 0x20), perm2(r13, r14, 0x20),
            perm2(r7, r8, 0x20), perm2(r9, r10, 0x20),
            perm2(r11, r12, 0x31), perm2(r13, r14, 0x31),
            perm2(r7, r8, 0x31), perm2(r9, r10, 0x31),
        ]
    raise ValueError(level)


def butterfly(scales: list[list[int]], u: list[int]) -> tuple[list[list[int]], list[list[int]]]:
    top = scales[:4]
    bottom = scales[4:]
    twiddles = []
    outputs = []
    for a, b, roots in zip(top, bottom, u):
        twiddles.append([b[i] * inv(a[i]) % Q for i in range(16)])
        outputs.append(a[:])
        outputs.append([roots[i] * a[i] % Q for i in range(16)])
    # Assembly register order is four tops followed by four bottoms.
    ordered = outputs[0::2] + outputs[1::2]
    return twiddles, ordered


def roots_vector(table: list[int], base: int, level: int) -> list[list[int]]:
    actual_offsets = {6: 16, 5: 208, 4: 400, 3: 592}
    values = table[base + actual_offsets[level]:base + actual_offsets[level] + 16]
    roots = [effective_twiddle(value) for value in values]
    return [roots[:] for _ in range(4)]


def derive(table: list[int]) -> tuple[dict[int, list[list[list[int]]]], list[list[int]]]:
    all_twiddles: dict[int, list[list[list[int]]]] = {level: [] for level in (6, 5, 4, 3, 2)}
    block_scales = []
    for block in range(6):
        scales = [[1] * 16 for _ in range(8)]
        base = block * 32
        for level in (6, 5, 4, 3):
            twiddles, outputs = butterfly(scales, roots_vector(table, base, level))
            all_twiddles[level].append(twiddles)
            scales = shuffle_level(outputs, level)
        block_scales.append(scales)

    # Level 2 pairs the first/second halves in each already-materialized block.
    final_scales = []
    for block, scales in enumerate(block_scales):
        # Official vpbroadcastd tables store [qinv,qinv,zeta,zeta].
        root = effective_twiddle(table[192 + block * 4 + 578])
        twiddles, outputs = butterfly(scales, [[root] * 16 for _ in range(4)])
        all_twiddles[2].append(twiddles)
        final_scales.extend(outputs)
    return all_twiddles, final_scales


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--consts", type=Path, required=True)
    args = parser.parse_args()
    table = parse_array(args.consts, "zetas_inv")
    twiddles, scales = derive(table)
    for level in (6, 5, 4, 3, 2):
        unique = sorted({x for block in twiddles[level] for reg in block for x in reg})
        print(f"level={level} unique-ct-twiddles={len(unique)} values={unique[:12]}")
    print(f"terminal-vectors={len(scales)} unique-scales={len(set(sum(scales, [])))}")
    for group in range(2):
        same = all(
            scales[group * 24 + lane] == scales[group * 24 + 8 + lane]
            == scales[group * 24 + 16 + lane]
            for lane in range(8)
        )
        print(f"dft3-group={group} x-y-z-scales-identical={same}")
    for index, vector in enumerate(scales):
        print(f"scale-vector={index:02d} stored={[stored_twiddle(v) for v in vector]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
