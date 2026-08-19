#!/usr/bin/env python3
"""Search one-diagonal-layer signed factorizations of conjugated DFT3."""

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


def matmul(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    return [[sum(a[i][k] * b[k][j] for k in range(3)) % Q
             for j in range(3)] for i in range(3)]


def inverse3(matrix: list[list[int]]) -> list[list[int]] | None:
    rows = [[matrix[i][j] % Q for j in range(3)] +
            [1 if i == j else 0 for j in range(3)] for i in range(3)]
    for column in range(3):
        pivots = [i for i in range(column, 3) if rows[i][column]]
        if not pivots:
            return None
        pivot = pivots[0]
        rows[column], rows[pivot] = rows[pivot], rows[column]
        factor = inv(rows[column][column])
        rows[column] = [(x * factor) % Q for x in rows[column]]
        for i in range(3):
            if i != column:
                factor = rows[i][column]
                rows[i] = [(rows[i][j] - factor * rows[column][j]) % Q
                           for j in range(6)]
    return [row[3:] for row in rows]


def propagate(scales: list[list[int]]) -> list[list[int]]:
    after = [[0] * 16 for _ in range(48)]
    for k3 in range(3):
        for position, k16 in enumerate(BRV3):
            low = 16*k3+k16
            for destination in (16*k3+2*position, 16*k3+2*position+1):
                after[destination] = scales[low][:]
    scales = after
    for length in (4, 8, 16):
        half = length // 2
        after = [row[:] for row in scales]
        for k3 in range(3):
            for start in range(0, 16, length):
                for index in range(half):
                    low = 16*k3+start+index
                    high = low+half
                    after[low] = scales[low][:]
                    after[high] = scales[low][:]
        scales = after
    return scales


def inverse_chain_trace(scales: list[list[int]], inv_twiddles: list[int]) -> tuple[list[dict], list[list[int]]]:
    trace = []
    after = [[0]*16 for _ in range(48)]
    count = 0
    for k3 in range(3):
        for position, k16 in enumerate(BRV3):
            low = 16*k3+k16
            high = low+8
            modified = [scales[low][j]*inv(scales[high][j]) % Q
                        for j in range(16)]
            count += any(x != 1 for x in modified)
            for destination in (16*k3+2*position, 16*k3+2*position+1):
                after[destination] = scales[low][:]
    trace.append({"stage": "size2", "current": 0, "candidate": count})
    scales = after
    offset = 0
    for length in (4, 8, 16):
        half = length//2
        after = [row[:] for row in scales]
        candidate = 0
        current = 0
        for k3 in range(3):
            for start in range(0, 16, length):
                for index in range(half):
                    low = 16*k3+start+index
                    high = low+half
                    twiddle = 1 if index == 0 else inv_twiddles[offset+index]
                    modified = [twiddle*scales[low][j]*inv(scales[high][j]) % Q
                                for j in range(16)]
                    candidate += any(x != 1 for x in modified)
                    current += index != 0
                    after[low] = scales[low][:]
                    after[high] = scales[low][:]
        trace.append({"stage": f"length{length}", "current": current,
                      "candidate": candidate})
        scales = after
        offset += half
    return trace, scales


def add_cost(matrix: list[list[int]]) -> int:
    return sum(max(sum(x != 0 for x in row)-1, 0) for row in matrix)


def outer(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(a[i] * b[j] for i in range(3) for j in range(3))


def signed_vectors() -> list[tuple[int, ...]]:
    result = []
    for vector in itertools.product((-1, 0, 1), repeat=3):
        if vector == (0, 0, 0):
            continue
        first = next(x for x in vector if x)
        if first == 1:  # quotient the irrelevant simultaneous sign
            result.append(vector)
    return result


def signed_residual(target: tuple[int, ...], terms: list[tuple[int, tuple]]) -> tuple[int, ...] | None:
    values = []
    for index, value in enumerate(target):
        residual = (value - sum(c * pattern[index] for c, pattern in terms)) % Q
        if residual == Q-1:
            values.append(-1)
        elif residual in (0, 1):
            values.append(residual)
        else:
            return None
    return tuple(values)


def circuit_cost(base: tuple[int, ...], terms: list[tuple[int, tuple, tuple, tuple]]) -> int:
    base_matrix = [base[3*i:3*i+3] for i in range(3)]
    cost = add_cost([list(row) for row in base_matrix])
    for _, _, a, b in terms:
        cost += max(sum(x != 0 for x in b)-1, 0)  # source linear form
        cost += sum(x != 0 for x in a)             # distribute/add product
    return cost


def factor_exact(target_matrix: list[list[int]]) -> dict | None:
    target = tuple(x % Q for row in target_matrix for x in row)
    vectors = signed_vectors()
    patterns = [(outer(a, b), a, b) for a in vectors for b in vectors]
    direct = signed_residual(target, [])
    if direct is not None:
        return {"montgomery_chains": 0, "signed_add_cost": circuit_cost(direct, []),
                "base": direct, "updates": []}

    best = None
    for pattern, a, b in patterns:
        position = next(i for i, x in enumerate(pattern) if x)
        for signed in (-1, 0, 1):
            c = ((target[position] - signed) * pattern[position]) % Q
            residual = signed_residual(target, [(c, pattern)])
            if residual is None:
                continue
            terms = [(c, pattern, a, b)]
            score = circuit_cost(residual, terms)
            candidate = {"montgomery_chains": 1, "signed_add_cost": score,
                         "base": residual,
                         "updates": [{"constant": center(c), "output_form": a,
                                      "input_form": b}]}
            if best is None or score < best[0]:
                best = (score, candidate)
    if best is not None:
        return best[1]

    # Complete two-update search.  For every pair of signed rank-one patterns,
    # solve the two constants from two independent matrix entries and enumerate
    # the signed base values at those entries.
    best = None
    for first_index, (p1, a1, b1) in enumerate(patterns):
        for p2, a2, b2 in patterns[first_index:]:
            pivots = None
            for i in range(9):
                for j in range(i+1, 9):
                    determinant = (p1[i]*p2[j] - p1[j]*p2[i]) % Q
                    if determinant:
                        pivots = (i, j, determinant)
                        break
                if pivots:
                    break
            if pivots is None:
                continue
            i, j, determinant = pivots
            determinant_inv = inv(determinant)
            for si in (-1, 0, 1):
                for sj in (-1, 0, 1):
                    yi = (target[i] - si) % Q
                    yj = (target[j] - sj) % Q
                    c1 = (yi*p2[j] - yj*p2[i]) * determinant_inv % Q
                    c2 = (p1[i]*yj - p1[j]*yi) * determinant_inv % Q
                    residual = signed_residual(target, [(c1, p1), (c2, p2)])
                    if residual is None:
                        continue
                    terms = [(c1, p1, a1, b1), (c2, p2, a2, b2)]
                    score = circuit_cost(residual, terms)
                    candidate = {
                        "montgomery_chains": 2,
                        "signed_add_cost": score,
                        "base": residual,
                        "updates": [
                            {"constant": center(c1), "output_form": a1, "input_form": b1},
                            {"constant": center(c2), "output_form": a2, "input_form": b2},
                        ],
                    }
                    if best is None or score < best[0]:
                        best = (score, candidate)
    return None if best is None else best[1]


def main() -> None:
    text = HEADER.read_text()
    flat = table(text, r"round4c_merge_mont\[48\]\[16\]", 48*16)
    inv_mont = table(text, r"round4c_inv16_twiddle_mont\[14\]", 14)
    inv_twiddles = [center(x*RINV) for x in inv_mont]
    weights = [[center(flat[16*v+j]*RINV) for j in range(16)]
               for v in range(48)]
    relation = [[inv(weights[v][j]) if j in HIGH else 1 for j in range(16)]
                for v in range(48)]
    chain_trace, terminal = inverse_chain_trace(relation, inv_twiddles)
    roots = sorted(x for x in range(1, Q) if pow(x, 3, Q) == 1 and x != 1)
    omega = roots[0]
    f = [[1, 1, 1], [1, (-1-omega) % Q, omega],
         [1, omega, (-1-omega) % Q]]
    current = factor_exact(f)
    classes = []
    seen = set()
    for lane in sorted(HIGH):
        rho = tuple(terminal[16*k][lane] % Q for k in range(3))
        if rho in seen:
            continue
        seen.add(rho)
        variants = []
        for tail in itertools.product((1, -1), repeat=2):
            signs = (1,) + tail
            signed = tuple(rho[k]*signs[k] % Q for k in range(3))
            diagonal = [[inv(signed[i]) if i == j else 0
                         for j in range(3)] for i in range(3)]
            g = matmul(f, diagonal)
            factor = factor_exact(g)
            variants.append({"signs": signs,
                             "rho": [center(x) for x in signed],
                             "factorization": factor})
        best = min(variants, key=lambda item: (
            99 if item["factorization"] is None else item["factorization"]["montgomery_chains"],
            99 if item["factorization"] is None else item["factorization"]["signed_add_cost"]))
        classes.append({"lanes": [x for x in sorted(HIGH)
                                   if tuple(terminal[16*k][x] % Q
                                            for k in range(3)) == rho],
                        "best": best, "all_sign_variants": variants})

    best_candidate = max(
        3 if item["best"]["factorization"] is None else
        item["best"]["factorization"]["montgomery_chains"]
        for item in classes)
    current_pre_dft = 48 + sum(item["current"] for item in chain_trace)
    candidate_pre_dft = sum(item["candidate"] for item in chain_trace)
    current_through_dft = current_pre_dft + 16*current["montgomery_chains"]
    candidate_through_dft_lower_bound = candidate_pre_dft + 16*best_candidate
    result = {
        "experiment": "GT32-CONJUGATED-DFT3-SYNTHESIS-028",
        "search_space": {
            "factorization": "signed base + rank-one constant-multiply updates",
            "signed_base_and_forms": [-1, 0, 1],
            "maximum_rank_one_updates_searched": 2,
            "free_merge_sign_variants_per_class": 4,
            "output_must_be_exact": True,
            "optimism": "each lane class may choose its own signed topology; SIMD routing cost is ignored",
        },
        "current_dft3": current,
        "inverse_chain_trace_before_dft3": chain_trace,
        "candidate_classes": classes,
        "worst_candidate_montgomery_chains_per_dft3": best_candidate,
        "candidate_chain_count_is_lower_bound": any(
            item["best"]["factorization"] is None for item in classes),
        "current_montgomery_chains_per_dft3": current["montgomery_chains"],
        "whole_merge_inverse_through_dft3": {
            "current_chains": current_through_dft,
            "candidate_lower_bound_chains": candidate_through_dft_lower_bound,
            "candidate_minus_current_lower_bound":
                candidate_through_dft_lower_bound-current_through_dft,
        },
        "decision": {
            "assembly_eligible": best_candidate <= current["montgomery_chains"],
            "status": ("continue_to_range_register_gate" if
                       best_candidate <= current["montgomery_chains"] else
                       "static_stop_one_diagonal_layer_adds_montgomery_chains"),
            "reason": (
                "The exact conjugated DFT3 needs more diagonal Montgomery "
                "chains than the current one-chain DFT3 in the complete "
                "sparse signed pre/post-add search."
            ),
        },
    }
    out = ROOT / "generated" / "conjugated_dft3_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(out)


if __name__ == "__main__":
    main()
