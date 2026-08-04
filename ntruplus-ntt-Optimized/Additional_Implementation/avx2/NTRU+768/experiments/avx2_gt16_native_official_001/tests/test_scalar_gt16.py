#!/usr/bin/env python3
"""Scalar correctness gates for the Round 4 weighted GT(3,16) layout."""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "tools"))
import generate_gt16 as gt  # noqa: E402


def canonical(x: int) -> int:
    return x % gt.Q


def word(branch: int, k3: int, degree: int, k16: int) -> int:
    return ((branch * 3 + k3) * 4 + degree) * 16 + k16


def load_contract() -> tuple[list[dict[str, int]], list[dict[str, int]]]:
    branches = json.loads((HERE / "generated/gt16-branches.json").read_text())["branches"]
    components = json.loads((HERE / "generated/gt16-factorization.json").read_text())["components"]
    return branches, components


def dft3(values: list[int], inverse: bool) -> list[int]:
    root = gt.mod_inv(gt.OMEGA3) if inverse else gt.OMEGA3
    scale = gt.mod_inv(3) if inverse else 1
    return [sum(values[n] * pow(root, n * k, gt.Q) for n in range(3))
            * scale % gt.Q for k in range(3)]


def dft16(values: list[int], inverse: bool) -> list[int]:
    root = gt.mod_inv(gt.OMEGA16) if inverse else gt.OMEGA16
    scale = gt.mod_inv(16) if inverse else 1
    return [sum(values[n] * pow(root, n * k, gt.Q) for n in range(16))
            * scale % gt.Q for k in range(16)]


def transform48(values: list[int], order: str, inverse: bool) -> list[list[int]]:
    matrix = [[0] * 16 for _ in range(3)]
    if not inverse:
        for i3 in range(3):
            for i16 in range(16):
                matrix[i3][i16] = values[gt.input_crt(i3, i16)]
        if order == "DFT3-first":
            after3 = [[0] * 16 for _ in range(3)]
            for i16 in range(16):
                column = dft3([matrix[i3][i16] for i3 in range(3)], False)
                for k3 in range(3):
                    after3[k3][i16] = column[k3]
            return [dft16(after3[k3], False) for k3 in range(3)]
        after16 = [dft16(matrix[i3], False) for i3 in range(3)]
        output = [[0] * 16 for _ in range(3)]
        for k16 in range(16):
            column = dft3([after16[i3][k16] for i3 in range(3)], False)
            for k3 in range(3):
                output[k3][k16] = column[k3]
        return output

    # Inverse input is indexed [k3][k16], output is returned in natural order.
    if order == "DFT3-first":
        after3 = [[0] * 16 for _ in range(3)]
        for k16 in range(16):
            column = dft3([values[k3][k16] for k3 in range(3)], True)  # type: ignore[index]
            for i3 in range(3):
                after3[i3][k16] = column[i3]
        after16 = [dft16(after3[i3], True) for i3 in range(3)]
    else:
        after16_k = [dft16(values[k3], True) for k3 in range(3)]  # type: ignore[index]
        after16 = [[0] * 16 for _ in range(3)]
        for i16 in range(16):
            column = dft3([after16_k[k3][i16] for k3 in range(3)], True)
            for i3 in range(3):
                after16[i3][i16] = column[i3]
    natural = [0] * 48
    for i3 in range(3):
        for i16 in range(16):
            natural[gt.input_crt(i3, i16)] = after16[i3][i16]
    return natural  # type: ignore[return-value]


def forward(poly: list[int], order: str, branches: list[dict[str, int]]) -> list[int]:
    output = [0] * gt.N
    top = [[[0] * 96 for _ in range(4)] for _ in range(2)]
    for top_branch, gamma in enumerate((gt.PHI, gt.PHI_INV)):
        for degree in range(4):
            for n in range(96):
                top[top_branch][degree][n] = (
                    poly[4 * n + degree]
                    + gamma * poly[4 * (n + 96) + degree]
                ) % gt.Q
    for spec in branches:
        branch = spec["branch"]
        beta = spec["beta"]
        factor = spec["F"]
        for degree in range(4):
            residue = [(top[spec["top"]][degree][n]
                        + beta * top[spec["top"]][degree][n + 48]) % gt.Q
                       for n in range(48)]
            weighted = [residue[n] * pow(factor, -n, gt.Q) % gt.Q
                        for n in range(48)]
            transformed = transform48(weighted, order, False)
            for k3 in range(3):
                for k16 in range(16):
                    output[word(branch, k3, degree, k16)] = transformed[k3][k16]
    return output


def inverse(values: list[int], order: str, branches: list[dict[str, int]]) -> list[int]:
    residues = [[[0] * 48 for _ in range(4)] for _ in range(4)]
    for spec in branches:
        branch = spec["branch"]
        factor = spec["F"]
        for degree in range(4):
            matrix = [[values[word(branch, k3, degree, k16)]
                       for k16 in range(16)] for k3 in range(3)]
            weighted = transform48(matrix, order, True)
            residues[branch][degree] = [
                weighted[n] * pow(factor, n, gt.Q) % gt.Q for n in range(48)
            ]

    top = [[[0] * 96 for _ in range(4)] for _ in range(2)]
    inv2 = gt.mod_inv(2)
    for top_branch in range(2):
        plus = branches[2 * top_branch]
        minus = branches[2 * top_branch + 1]
        assert (plus["beta"] + minus["beta"]) % gt.Q == 0
        inv2beta = gt.mod_inv(2 * plus["beta"] % gt.Q)
        for degree in range(4):
            for n in range(48):
                p = residues[plus["branch"]][degree][n]
                m = residues[minus["branch"]][degree][n]
                top[top_branch][degree][n] = (p + m) * inv2 % gt.Q
                top[top_branch][degree][n + 48] = (p - m) * inv2beta % gt.Q

    output = [0] * gt.N
    inv_delta = gt.mod_inv(gt.PHI - gt.PHI_INV)
    for degree in range(4):
        for n in range(96):
            high = (top[0][degree][n] - top[1][degree][n]) * inv_delta % gt.Q
            low = (top[0][degree][n] - gt.PHI * high) % gt.Q
            output[4 * n + degree] = low
            output[4 * (n + 96) + degree] = high
    return output


def direct_components(poly: list[int], components: list[dict[str, int]]) -> list[int]:
    output = [0] * gt.N
    for component in components:
        alpha = component["alpha"] % gt.Q
        for degree in range(4):
            value = 0
            power = 1
            for n in range(192):
                value = (value + poly[4 * n + degree] * power) % gt.Q
                power = power * alpha % gt.Q
            output[word(component["branch"], component["k3"], degree,
                        component["k16"])] = value
    return output


def component_mul(a: list[int], b: list[int], components: list[dict[str, int]]) -> list[int]:
    output = [0] * gt.N
    for component in components:
        base = word(component["branch"], component["k3"], 0, component["k16"])
        aa = [a[base + 16 * degree] for degree in range(4)]
        bb = [b[base + 16 * degree] for degree in range(4)]
        alpha = component["alpha"] % gt.Q
        conv = [0] * 7
        for i in range(4):
            for j in range(4):
                conv[i + j] += aa[i] * bb[j]
        for degree in range(6, 3, -1):
            conv[degree - 4] += alpha * conv[degree]
        for degree in range(4):
            output[base + 16 * degree] = conv[degree] % gt.Q
    return output


def schoolbook(a: list[int], b: list[int]) -> list[int]:
    conv = [0] * (2 * gt.N - 1)
    for i, left in enumerate(a):
        if left:
            for j, right in enumerate(b):
                if right:
                    conv[i + j] += left * right
    for degree in range(2 * gt.N - 2, gt.N - 1, -1):
        value = conv[degree]
        conv[degree - 384] += value
        conv[degree - 768] -= value
    return [x % gt.Q for x in conv[:gt.N]]


def patterns() -> list[list[int]]:
    result = [[0] * gt.N]
    for index in (0, 1, 3, 4, 383, 384, 767):
        value = [0] * gt.N
        value[index] = 1
        result.append(value)
    result.append([(-1 if i & 1 else 1) % gt.Q for i in range(gt.N)])
    rng = random.Random(0x47543136)
    for _ in range(8):
        result.append([rng.randrange(-3, 5) % gt.Q for _ in range(gt.N)])
    return result


def main() -> int:
    branches, components = load_contract()
    cases = patterns()
    for case_index, poly in enumerate(cases):
        direct = direct_components(poly, components)
        first = forward(poly, "DFT3-first", branches)
        second = forward(poly, "NTT16-first", branches)
        assert first == direct, f"DFT3-first forward mismatch case={case_index}"
        assert second == direct, f"NTT16-first forward mismatch case={case_index}"
        assert inverse(first, "DFT3-first", branches) == poly, (
            f"DFT3-first roundtrip mismatch case={case_index}"
        )
        assert inverse(second, "NTT16-first", branches) == poly, (
            f"NTT16-first roundtrip mismatch case={case_index}"
        )

    rng = random.Random(0x504F4C59)
    for case_index in range(4):
        a = [rng.randrange(-3, 5) % gt.Q for _ in range(gt.N)]
        b = [rng.randrange(-3, 5) % gt.Q for _ in range(gt.N)]
        transformed = component_mul(forward(a, "DFT3-first", branches),
                                    forward(b, "NTT16-first", branches),
                                    components)
        product = inverse(transformed, "DFT3-first", branches)
        assert product == schoolbook(a, b), f"polymul mismatch case={case_index}"

    print("gt16-scalar forward_cases=%d polymul_cases=4 failures=0" % len(cases))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
