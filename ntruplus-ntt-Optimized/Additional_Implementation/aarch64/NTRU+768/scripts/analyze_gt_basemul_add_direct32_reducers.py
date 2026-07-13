#!/usr/bin/env python3
"""Exhaustive reducer search for GT poly_basemul_add P1-A.

This is an analysis-only tool.  It does not generate asm and is intentionally
not wired into the default Makefile.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


Q = 3457
HALF = (Q - 1) // 2
BOUND = 14_931_648
CHUNK = 1_000_000
R1_Q31_C = 621_199
INT16_MIN = -(1 << 15)
INT16_MAX = (1 << 15) - 1
INT32_MIN = -(1 << 31)
INT32_MAX = (1 << 31) - 1


@dataclass(frozen=True)
class Result:
    s: int
    c: int
    y_min: int
    y_max: int
    byte_equivalent: bool
    centered: bool
    positive_correction_needed: bool
    negative_correction_needed: bool


@dataclass(frozen=True)
class SqrdmulhProof:
    c: int
    mismatches: int
    y_min: int
    y_max: int
    t_min: int
    t_max: int
    fits_int16: bool
    poly_tobytes_precondition: bool
    saturation_possible: bool


def round_div_pow2_signed(n: np.ndarray, shift: int) -> np.ndarray:
    half = np.int64(1 << (shift - 1))
    return np.where(n >= 0, (n + half) >> shift, -(((-n) + half) >> shift))


def sqrdmulh_s32_exact(a: np.ndarray, b: int) -> np.ndarray:
    """Exact AArch64 SQrdmulh signed 32-bit semantics for this range.

    For signed 32-bit lanes:

        result = sat_s32((2*a*b + 2^31) >> 32)

    The saturating INT32_MIN*INT32_MIN corner cannot occur here because
    b=621199 and |a| <= 14931648.
    """

    product = a * np.int64(b)
    doubled_rounded = 2 * product + np.int64(1 << 31)
    t = doubled_rounded >> np.int64(32)
    return np.clip(t, INT32_MIN, INT32_MAX)


def centered_reduce_q(x: np.ndarray) -> np.ndarray:
    y = np.mod(x, Q)
    y = np.where(y > HALF, y - Q, y)
    return y


def pack_for_poly_tobytes(y: np.ndarray) -> np.ndarray:
    return np.where(y < 0, y + Q, y)


def candidate_constants(s: int) -> list[int]:
    ideal = (1 << s) / Q
    out = set()
    center = int(round(ideal))
    for delta in range(-2, 3):
        out.add(center + delta)
    out.add(int(math.floor(ideal)))
    out.add(int(math.ceil(ideal)))
    return sorted(c for c in out if c > 0)


def test_candidate(s: int, c: int) -> Result:
    y_min = 10**30
    y_max = -10**30
    byte_equivalent = True

    for lo in range(-BOUND, BOUND + 1, CHUNK):
        hi = min(BOUND, lo + CHUNK - 1)
        x = np.arange(lo, hi + 1, dtype=np.int64)
        t = round_div_pow2_signed(x * np.int64(c), s)
        y = x - t * Q
        y_min = min(y_min, int(y.min()))
        y_max = max(y_max, int(y.max()))

        packed = np.where(y < 0, y + Q, y)
        canonical = np.mod(x, Q)
        if np.any(packed != canonical):
            byte_equivalent = False
            break

    return Result(
        s=s,
        c=c,
        y_min=y_min,
        y_max=y_max,
        byte_equivalent=byte_equivalent,
        centered=y_min >= -HALF and y_max <= HALF,
        positive_correction_needed=y_max > Q - 1,
        negative_correction_needed=y_min < -Q,
    )


def prove_r1_q31_sqrdmulh() -> SqrdmulhProof:
    mismatches = 0
    y_min = 10**30
    y_max = -10**30
    t_min = 10**30
    t_max = -10**30
    saturation_possible = False

    for lo in range(-BOUND, BOUND + 1, CHUNK):
        hi = min(BOUND, lo + CHUNK - 1)
        x = np.arange(lo, hi + 1, dtype=np.int64)
        t = sqrdmulh_s32_exact(x, R1_Q31_C)
        y = x - t * Q
        want = pack_for_poly_tobytes(centered_reduce_q(x))
        got = pack_for_poly_tobytes(y)

        y_min = min(y_min, int(y.min()))
        y_max = max(y_max, int(y.max()))
        t_min = min(t_min, int(t.min()))
        t_max = max(t_max, int(t.max()))
        saturation_possible = saturation_possible or bool(
            np.any(t == INT32_MIN) or np.any(t == INT32_MAX)
        )
        mismatches += int(np.count_nonzero(got != want))

    return SqrdmulhProof(
        c=R1_Q31_C,
        mismatches=mismatches,
        y_min=y_min,
        y_max=y_max,
        t_min=t_min,
        t_max=t_max,
        fits_int16=y_min >= INT16_MIN and y_max <= INT16_MAX,
        poly_tobytes_precondition=y_min >= -Q and y_max <= Q - 1,
        saturation_possible=saturation_possible,
    )


def main() -> int:
    print(f"q={Q}")
    print(f"bound={BOUND}")
    print(f"tested_x_count={2 * BOUND + 1}")
    print(
        "criterion=packed(y)==x_mod_q, where packed(y)=y+q if y<0 else y"
    )

    passing: list[Result] = []
    for s in range(20, 43):
        for c in candidate_constants(s):
            result = test_candidate(s, c)
            if result.byte_equivalent:
                passing.append(result)

    print("byte_equivalent_candidates:")
    print("s,C,y_min,y_max,centered,correction_masks_needed")
    for result in passing:
        masks = int(result.positive_correction_needed) + int(
            result.negative_correction_needed
        )
        print(
            f"{result.s},{result.c},{result.y_min},{result.y_max},"
            f"{int(result.centered)},{masks}"
        )

    q31 = [r for r in passing if r.s == 31]
    centered = [r for r in passing if r.centered]

    if q31:
        best_q31 = min(q31, key=lambda r: max(abs(r.y_min), abs(r.y_max)))
        print(
            "best_q31_sqrdmulh_candidate="
            f"s:{best_q31.s},C:{best_q31.c},"
            f"range:[{best_q31.y_min},{best_q31.y_max}],"
            f"centered:{int(best_q31.centered)}"
        )
    else:
        print("best_q31_sqrdmulh_candidate=none")

    if centered:
        first_centered = min(centered, key=lambda r: (r.s, abs(r.c)))
        print(
            "first_centered_candidate="
            f"s:{first_centered.s},C:{first_centered.c},"
            f"range:[{first_centered.y_min},{first_centered.y_max}]"
        )
    else:
        print("first_centered_candidate=none")

    proof = prove_r1_q31_sqrdmulh()
    print("r1_q31_sqrdmulh_exact_proof:")
    print(f"C={proof.c}")
    print("semantics=((2*x*C + 2^31) >> 32), saturating_s32")
    print(f"x_min={-BOUND}")
    print(f"x_max={BOUND}")
    print(f"t_min={proof.t_min}")
    print(f"t_max={proof.t_max}")
    print(f"y_min={proof.y_min}")
    print(f"y_max={proof.y_max}")
    print(f"packed_mismatches={proof.mismatches}")
    print(f"fits_int16={int(proof.fits_int16)}")
    print(
        "poly_tobytes_one_add_q_precondition="
        f"{int(proof.poly_tobytes_precondition)}"
    )
    print(f"sqrdmulh_saturation_possible={int(proof.saturation_possible)}")

    ok = (
        proof.c == R1_Q31_C
        and proof.mismatches == 0
        and proof.fits_int16
        and proof.poly_tobytes_precondition
        and not proof.saturation_possible
    )
    print(f"r1_q31_regression_pass={int(ok)}")
    print("analysis_status=complete" if ok else "analysis_status=failed")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
