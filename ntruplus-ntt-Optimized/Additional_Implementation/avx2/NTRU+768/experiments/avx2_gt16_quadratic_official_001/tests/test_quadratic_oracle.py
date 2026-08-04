#!/usr/bin/env python3
"""Scalar differential gates for the Round 4C quadratic terminal algebra."""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
HORIZONTAL = HERE.parent / "avx2_gt16_native_official_001"
sys.path.insert(0, str(HERE / "tools"))
sys.path.insert(0, str(HORIZONTAL / "tools"))
sys.path.insert(0, str(HORIZONTAL / "tests"))
import generate_quadratic as gen  # noqa: E402
import test_scalar_gt16 as gt16  # noqa: E402


def split(a: list[int], s: int) -> tuple[list[int], list[int]]:
    return (
        [(a[0] + s * a[2]) % gen.Q, (a[1] + s * a[3]) % gen.Q],
        [(a[0] - s * a[2]) % gen.Q, (a[1] - s * a[3]) % gen.Q],
    )


def merge(plus: list[int], minus: list[int], s: int) -> list[int]:
    inv2 = pow(2, -1, gen.Q)
    inv2s = pow(2 * s, -1, gen.Q)
    return [
        (plus[0] + minus[0]) * inv2 % gen.Q,
        (plus[1] + minus[1]) * inv2 % gen.Q,
        (plus[0] - minus[0]) * inv2s % gen.Q,
        (plus[1] - minus[1]) * inv2s % gen.Q,
    ]


def qmul(a: list[int], b: list[int], r: int) -> list[int]:
    return [(a[0] * b[0] + r * a[1] * b[1]) % gen.Q,
            (a[0] * b[1] + a[1] * b[0]) % gen.Q]


def quartic_mul(a: list[int], b: list[int], alpha: int) -> list[int]:
    conv = [0] * 7
    for i in range(4):
        for j in range(4):
            conv[i + j] += a[i] * b[j]
    for degree in range(6, 3, -1):
        conv[degree - 4] += alpha * conv[degree]
    return [x % gen.Q for x in conv[:4]]


def qinv(a: list[int], r: int) -> tuple[bool, list[int]]:
    norm = (a[0] * a[0] - r * a[1] * a[1]) % gen.Q
    if norm == 0:
        return False, [0, 0]
    inverse = pow(norm, -1, gen.Q)
    return True, [a[0] * inverse % gen.Q, -a[1] * inverse % gen.Q]


def quadratic_component_product(values_a: list[int], values_b: list[int],
                                factors: dict) -> list[int]:
    output = [0] * gt16.gt.N
    components = json.loads(
        (HORIZONTAL / "generated/gt16-factorization.json").read_text()
    )["components"]
    roots = {}
    for factor in factors["factors"]:
        if factor["sign_index"] == 0:
            roots[factor["quartic_slot"]] = factor["sqrt_alpha"] % gen.Q
    for component in components:
        base = gt16.word(component["branch"], component["k3"], 0,
                         component["k16"])
        a = [values_a[base + 16 * degree] % gen.Q for degree in range(4)]
        b = [values_b[base + 16 * degree] % gen.Q for degree in range(4)]
        s = roots[component["slot"]]
        ap, am = split(a, s)
        bp, bm = split(b, s)
        cp = qmul(ap, bp, s)
        cm = qmul(am, bm, -s % gen.Q)
        c = merge(cp, cm, s)
        for degree in range(4):
            output[base + 16 * degree] = c[degree]
    return output


def main() -> int:
    factorization = json.loads(
        (HERE / "generated/quadratic-factorization.json").read_text()
    )
    ranges = json.loads(
        (HERE / "generated/quadratic-range-metadata.json").read_text()
    )
    assert len(factorization["factors"]) == 384
    assert factorization["layout"]["pair_local_to_128_bit_half"]

    rng = random.Random(0x47543143)
    quartic_cases = [
        [0, 0, 0, 0], [1, 0, 0, 0],
        [gen.CENTER, -gen.CENTER, gen.CENTER, -gen.CENTER],
        [-gen.CENTER, gen.CENTER, -gen.CENTER, gen.CENTER],
    ]
    quartic_cases.extend([[rng.randrange(gen.Q) for _ in range(4)]
                           for _ in range(2000)])
    for factor in factorization["factors"][::2]:
        alpha = factor["alpha"] % gen.Q
        s = factor["sqrt_alpha"] % gen.Q
        assert s * s % gen.Q == alpha
        for a in quartic_cases[:20]:
            assert merge(*split(a, s), s) == [x % gen.Q for x in a]
        for _ in range(10):
            a = quartic_cases[rng.randrange(len(quartic_cases))]
            b = quartic_cases[rng.randrange(len(quartic_cases))]
            ap, am = split(a, s)
            bp, bm = split(b, s)
            got = merge(qmul(ap, bp, s), qmul(am, bm, -s % gen.Q), s)
            assert got == quartic_mul(a, b, alpha)

    # Quadratic inversion, including deterministic failure-to-zero behavior.
    for factor in factorization["factors"]:
        r = factor["quadratic_modulus_r"] % gen.Q
        for _ in range(8):
            a = [rng.randrange(gen.Q), rng.randrange(gen.Q)]
            ok, inverse = qinv(a, r)
            if ok:
                assert qmul(a, inverse, r) == [1, 0]
            else:
                assert inverse == [0, 0]
    assert qinv([0, 0], factorization["factors"][0]["quadratic_modulus_r"])[1] == [0, 0]

    # Exact five-op Montgomery-reducer model on endpoints and random range.
    bound = ranges["c1_vpmaddwd_bound"]
    for x in [-bound, -bound + 1, -1, 0, 1, bound - 1, bound]:
        assert gen.mont32(x) * gen.R % gen.Q == x % gen.Q
    for _ in range(100000):
        x = rng.randrange(-bound, bound + 1)
        assert gen.mont32(x) * gen.R % gen.Q == x % gen.Q

    # Full quotient-ring differential through the inherited scalar GT16 map.
    branches, components = gt16.load_contract()
    for _ in range(3):
        a = [rng.randrange(-3, 5) % gen.Q for _ in range(gt16.gt.N)]
        b = [rng.randrange(-3, 5) % gen.Q for _ in range(gt16.gt.N)]
        ta = gt16.forward(a, "DFT3-first", branches)
        tb = gt16.forward(b, "DFT3-first", branches)
        product = quadratic_component_product(ta, tb, factorization)
        got = gt16.inverse(product, "DFT3-first", branches)
        assert got == gt16.schoolbook(a, b)

    print("quadratic terminal factor/split/QBM/merge/baseinv/polymul gates: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
