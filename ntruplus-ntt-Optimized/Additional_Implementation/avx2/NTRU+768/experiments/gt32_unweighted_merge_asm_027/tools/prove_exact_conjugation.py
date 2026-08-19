#!/usr/bin/env python3
"""Prove whether raw merge differences can reach DFT3 by diagonal conjugation."""

from __future__ import annotations

import itertools
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "avx2_gt16_quadratic_official_001"
HEADER = SOURCE / "generated" / "quadratic-constants.h"
Q = 3457
R = (1 << 16) % Q
RINV = pow(R, -1, Q)
HIGH = {2, 3, 6, 7, 10, 11, 14, 15}
BRV3 = (0, 4, 2, 6, 1, 5, 3, 7)


def center(x: int) -> int:
    x %= Q
    return x - Q if x > Q // 2 else x


def inv(x: int) -> int:
    return pow(x % Q, -1, Q)


def table(text: str, pattern: str, count: int) -> list[int]:
    match = re.search(pattern + r".*?= \{(.*?)\n\};", text, re.S)
    if not match:
        raise RuntimeError(pattern)
    values = [int(x) for x in re.findall(r"-?\d+", match.group(1))]
    if len(values) != count:
        raise RuntimeError((pattern, len(values), count))
    return values


def propagate(scales: list[list[int]]) -> list[list[int]]:
    after = [[0] * 16 for _ in range(48)]
    for k3 in range(3):
        for position, k16 in enumerate(BRV3):
            low = 16 * k3 + k16
            for destination in (16 * k3 + 2 * position,
                                16 * k3 + 2 * position + 1):
                after[destination] = scales[low][:]
    scales = after
    for length in (4, 8, 16):
        half = length // 2
        after = [row[:] for row in scales]
        for k3 in range(3):
            for start in range(0, 16, length):
                for index in range(half):
                    low = 16 * k3 + start + index
                    high = low + half
                    after[low] = scales[low][:]
                    after[high] = scales[low][:]
        scales = after
    return scales


def matmul(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    return [[sum(a[i][k] * b[k][j] for k in range(3)) % Q
             for j in range(3)] for i in range(3)]


def inverse3(matrix: list[list[int]]) -> list[list[int]]:
    rows = [[matrix[i][j] % Q for j in range(3)] +
            [1 if i == j else 0 for j in range(3)] for i in range(3)]
    for column in range(3):
        pivot = next(i for i in range(column, 3) if rows[i][column])
        rows[column], rows[pivot] = rows[pivot], rows[column]
        factor = inv(rows[column][column])
        rows[column] = [(x * factor) % Q for x in rows[column]]
        for i in range(3):
            if i != column:
                factor = rows[i][column]
                rows[i] = [(rows[i][j] - factor * rows[column][j]) % Q
                           for j in range(6)]
    return [row[3:] for row in rows]


def main() -> None:
    text = HEADER.read_text()
    flat = table(text, r"round4c_merge_mont\[48\]\[16\]", 48 * 16)
    weights = [[center(flat[16*v+j] * RINV) for j in range(16)]
               for v in range(48)]
    # z/raw candidate divided by the current weighted representative.
    base = [[inv(weights[v][j]) if j in HIGH else 1 for j in range(16)]
            for v in range(48)]
    terminal = propagate(base)
    roots = sorted(x for x in range(1, Q) if pow(x, 3, Q) == 1)
    characters = [(1, 1, 1), (1, roots[0], roots[1]),
                  (1, roots[1], roots[0])]
    omega = roots[0]
    dft = [[1, 1, 1], [1, (-1-omega) % Q, omega],
           [1, omega, (-1-omega) % Q]]
    dft_inv = inverse3(dft)
    lanes = []
    all_character = True
    for lane in range(16):
        raw = tuple(terminal[16*k][lane] % Q for k in range(3))
        matches = []
        corrections = []
        for tail in itertools.product((1, -1), repeat=2):
            signs = (1,) + tail
            signed = tuple(raw[k] * signs[k] % Q for k in range(3))
            normalized = tuple(x * inv(signed[0]) % Q for x in signed)
            if normalized in characters:
                matches.append({"signs": signs,
                                "character": normalized})
            diagonal = [[inv(signed[i]) if i == j else 0
                         for j in range(3)] for i in range(3)]
            correction = matmul(matmul(dft, diagonal), dft_inv)
            corrections.append({
                "signs": signs,
                "nonzero_coefficients": sum(x != 0 for row in correction
                                              for x in row),
                "matrix": [[center(x) for x in row] for row in correction],
            })
        if not matches:
            all_character = False
        lanes.append({
            "lane": lane,
            "class": "difference" if lane in HIGH else "sum",
            "terminal_candidate_over_current": [center(x) for x in raw],
            "character_sign_matches": matches,
            "minimum_dense_correction": min(
                corrections, key=lambda item: item["nonzero_coefficients"]),
        })
        if lane in HIGH:
            assert not matches
        else:
            assert matches
    assert not all_character
    result = {
        "experiment": "GT32-UNWEIGHTED-MERGE-ASM-027",
        "exact_relation": "candidate/current",
        "cube_root_characters": [[center(x) for x in row]
                                   for row in characters],
        "all_lanes_are_dft3_characters_after_free_signs": all_character,
        "lanes": lanes,
        "decision": {
            "status": "semantic_static_stop_before_cycle_benchmark",
            "reason": (
                "The 026 propagation tracked merge weights rather than the "
                "candidate/current conjugation ratio. Exact propagation leaves "
                "the difference lanes outside every DFT3 character class, so "
                "their terminal correction is not a three-register permutation "
                "and cannot be implemented by 48 blends."
            ),
            "cycle_benchmark_valid": False,
        },
    }
    out = ROOT / "generated" / "exact_conjugation_gate.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(out)


if __name__ == "__main__":
    main()
