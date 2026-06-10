#!/usr/bin/env python3
"""Verify GT inverse NTT ASM constants.

This script checks the normal-centered constants used by
asm/slothy/invntt_opt.s.  These constants are deliberately not Montgomery-form;
GT basemul lambda tables are Montgomery-form and are not accepted here.
"""

from __future__ import annotations

import re
from pathlib import Path


Q = 3457
OMEGA96 = 675
F0 = 2
F1 = 22


ROOT = Path(__file__).resolve().parents[1]
ASM = ROOT / "asm" / "slothy" / "invntt_opt.s"


def centered(x: int) -> int:
    x %= Q
    if x > Q // 2:
        x -= Q
    return x


def inv_mod(x: int) -> int:
    return pow(x % Q, Q - 2, Q)


def precompute(m: int) -> int:
    # Signed nearest integer to m * 2^15 / q.
    num = m * (1 << 15)
    if num >= 0:
        return (num + Q // 2) // Q
    return -((-num + Q // 2) // Q)


def arshift(x: int, shift: int) -> int:
    if x >= 0:
        return x >> shift
    return -(((-x) + (1 << shift) - 1) >> shift)


def sat16(x: int) -> int:
    return max(-32768, min(32767, x))


def wrap16(x: int) -> int:
    x &= 0xFFFF
    if x >= 0x8000:
        x -= 0x10000
    return x


def sqdmulh(a: int, b: int) -> int:
    return sat16(arshift(2 * a * b, 16))


def srshr(a: int, shift: int) -> int:
    return wrap16(arshift(a + (1 << (shift - 1)), shift))


def asm_barrett(a: int, reciprocal: int) -> int:
    t = sqdmulh(wrap16(a), reciprocal)
    t = srshr(t, 11)
    return wrap16(a - t * Q)


def hwords_from(text: str) -> list[int]:
    vals: list[int] = []
    for line in text.splitlines():
        if ".hword" not in line:
            continue
        body = line.split(".hword", 1)[1].split("//", 1)[0]
        for part in body.split(","):
            part = part.strip()
            if part:
                vals.append(int(part, 0))
    return vals


def section(text: str, start: str, end: str) -> str:
    try:
        s = text.index(start)
        e = text.index(end, s + len(start))
    except ValueError as exc:
        raise AssertionError(f"missing section {start!r}..{end!r}") from exc
    return text[s:e]


def check_pre(label: str, m: int, got: int) -> None:
    want = precompute(m)
    assert got == want, f"{label}: precompute got {got}, want {want} for {m}"


def check_inv_consts(text: str) -> None:
    vals = hwords_from(section(text, "inv_consts:", "inv_gather_offsets:"))
    want = [
        Q,
        19412,
        centered(pow(OMEGA96, 32, Q)),  # inverse DFT3 omega3 multiplier
        precompute(centered(pow(OMEGA96, 32, Q))),
        1634,
        precompute(1634),
        centered(inv_mod(192)),
        precompute(centered(inv_mod(192))),
        centered(inv_mod(96)),
        precompute(centered(inv_mod(96))),
        1728,
        -1728,
        0,
        0,
        0,
        0,
    ]
    assert vals == want, f"inv_consts mismatch\n got={vals}\nwant={want}"

    for x in range(-12000, 12001):
        y = asm_barrett(x, vals[1])
        assert (y - x) % Q == 0, f"Barrett reciprocal failed congruence at {x}"
        assert -Q <= y <= Q, f"Barrett reciprocal out of expected range at {x}: {y}"


def check_stage123(text: str) -> None:
    vals = hwords_from(section(text, "invntt32_stage123_consts:", "invntt32_stage45_consts:"))
    root = pow(OMEGA96, -3, Q)
    normal = [
        1,
        centered(pow(root, 8, Q)),
        centered(pow(root, 4, Q)),
        centered(pow(root, 8, Q)),
        centered(pow(root, 12, Q)),
        0,
        0,
        0,
    ]
    pre = [precompute(x) if x else 0 for x in normal]
    want = normal + pre
    assert vals == want, f"stage123 constants mismatch\n got={vals}\nwant={want}"


def check_stage45(text: str) -> None:
    vals = hwords_from(section(text, "invntt32_stage45_consts:", "inv_untwist_vecs:"))
    assert len(vals) == 8 * 16, f"stage45 length got {len(vals)}"
    root = pow(OMEGA96, -3, Q)

    for j in range(8):
        normal = vals[16 * j:16 * j + 8]
        pre = vals[16 * j + 8:16 * j + 16]
        want_normal = [
            centered(pow(root, 2 * j, Q)),
            centered(pow(root, j, Q)),
            centered(pow(root, j + 8, Q)),
            0,
            0,
            0,
            0,
            0,
        ]
        want_pre = [precompute(x) if x else 0 for x in want_normal]
        assert normal == want_normal, f"stage45 normal j={j}: got {normal}, want {want_normal}"
        assert pre == want_pre, f"stage45 pre j={j}: got {pre}, want {want_pre}"


def check_untwist(text: str) -> None:
    body = section(text, "inv_untwist_vecs:", ".purgem BARRETT_REDUCE")
    lines = body.splitlines()
    seen: list[int] = []
    pending_k: int | None = None
    pending_normal: list[int] | None = None

    for line in lines:
        match = re.search(r"// k=(\d+):", line)
        if match:
            pending_k = int(match.group(1))
            pending_normal = None
            continue

        if ".hword" not in line or pending_k is None:
            continue

        vals = hwords_from(line)
        assert len(vals) == 8, f"untwist k={pending_k}: expected vector, got {vals}"

        if pending_normal is None:
            pending_normal = vals
            want = [centered(pow(F0, pending_k, Q))] * 4
            want += [centered(pow(F1, pending_k, Q))] * 4
            assert vals == want, f"untwist normal k={pending_k}: got {vals}, want {want}"
        else:
            want_pre = [precompute(x) for x in pending_normal]
            assert vals == want_pre, f"untwist pre k={pending_k}: got {vals}, want {want_pre}"
            seen.append(pending_k)
            pending_k = None
            pending_normal = None

    assert len(seen) == 96, f"untwist table has {len(seen)} entries"
    assert sorted(seen) == list(range(96)), "untwist table is not a permutation of k=0..95"

    expected_order: list[int] = []
    for k32 in range(32):
        base = (33 * k32) % 96
        expected_order.extend([base, (base + 64) % 96, (base + 32) % 96])
    assert seen == expected_order, "untwist table order does not match inverse DFT3/store order"


def main() -> int:
    text = ASM.read_text()
    check_inv_consts(text)
    check_stage123(text)
    check_stage45(text)
    check_untwist(text)
    print("inverse NTT constants verified: normal-form tables and precomputes ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
