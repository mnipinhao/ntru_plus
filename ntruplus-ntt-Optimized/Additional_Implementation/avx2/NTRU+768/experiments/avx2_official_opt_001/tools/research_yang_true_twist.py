#!/usr/bin/env python3
"""Complete y=x^4 twisted GS / CT inverse scalar tower, exact leaf ABI.

Unlike a diagonal-gauge conjugation of fixed butterflies, this applies
Yang's node substitution in y.  Each of the six y^32-alpha nodes is first
mapped to z^32-1; every negative child is then twisted back to a cyclic
node.  All y leaves are linear, so the quartic x^4-lambda ABI is unchanged.
This is executable modular algebra, not an AVX2/range schedule.
"""

import hashlib
import json
import random
from collections import Counter
from pathlib import Path

from probe_inverse_ct_gauge import Q, R, ROOT
from research_full_twisted_pairings import (
    children, invert_matrix, mapped_poly, recovered_poly)

RESULT = ROOT / 'results/yang-true-y-twist-pairings-20260923.json'
FACTORS = ROOT / 'results/yang-full-twisted-tower-factor-20260923.json'
Y = 192


def primitive_32():
    return next(x for x in range(2, Q) if pow(x, 32, Q) == 1 and
                pow(x, 16, Q) == Q - 1)


ZETA32 = primitive_32()


def cyclic_forward(poly, xi, zeta_n, count):
    n = len(poly)
    if n == 1:
        return {xi: poly[0] % Q}
    m = n // 2
    upper = [(a + b) % Q for a, b in zip(poly[:m], poly[m:])]
    lower = []
    for k, (a, b) in enumerate(zip(poly[:m], poly[m:])):
        factor = pow(zeta_n, k, Q)
        lower.append((a - b) * factor % Q)
        if factor != 1:
            count['GS_output_twist'] += 1
    result = cyclic_forward(upper, xi, zeta_n * zeta_n % Q, count)
    result.update(cyclic_forward(lower, xi * zeta_n % Q,
                                 zeta_n * zeta_n % Q, count))
    return result


def cyclic_inverse(values, xi, n, zeta_n, count):
    if n == 1:
        return [values[xi]]
    m = n // 2
    upper = cyclic_inverse(values, xi, m, zeta_n * zeta_n % Q, count)
    lower = cyclic_inverse(values, xi * zeta_n % Q, m,
                           zeta_n * zeta_n % Q, count)
    half = pow(2, -1, Q)
    first, second = [], []
    for k, (a, b) in enumerate(zip(upper, lower)):
        factor = pow(zeta_n, -k, Q)
        b = b * factor % Q
        if factor != 1:
            count['CT_input_untwist'] += 1
        first.append((a + b) * half % Q)
        second.append((a - b) * half % Q)
    return first + second


def evaluate(poly, roots, count):
    n = len(poly)
    if n == 32:
        xi = min(roots)
        assert {xi * pow(ZETA32, k, Q) % Q for k in range(32)} == set(roots)
        weighted = []
        for k, value in enumerate(poly):
            factor = pow(xi, k, Q)
            weighted.append(value * factor % Q)
            if factor != 1:
                count['initial_y32_twist'] += 1
        return cyclic_forward(weighted, xi, ZETA32, count)
    kids = children(roots, n)
    width = len(kids)
    m = n // width
    parts = [poly[j * m:(j + 1) * m] for j in range(width)]
    result = {}
    for constant, leaves in kids:
        child = [sum(parts[j][k] * pow(constant, j, Q)
                     for j in range(width)) % Q for k in range(m)]
        result.update(evaluate(child, leaves, count))
    return result


def reconstruct(values, roots, count):
    n = len(roots)
    if n == 32:
        xi = min(roots)
        raw = cyclic_inverse(values, xi, 32, ZETA32, count)
        result = []
        for k, value in enumerate(raw):
            factor = pow(xi, -k, Q)
            result.append(value * factor % Q)
            if factor != 1:
                count['final_y32_untwist'] += 1
        return result
    kids = children(roots, n)
    width = len(kids)
    m = n // width
    parts = [reconstruct(values, leaves, count) for _, leaves in kids]
    matrix = [[pow(c, j, Q) for j in range(width)] for c, _ in kids]
    rows = invert_matrix(matrix)
    output = [[sum(rows[j][i] * parts[i][k] for i in range(width)) % Q
               for k in range(m)] for j in range(width)]
    return [x for part in output for x in part]


def main():
    factor = json.loads(FACTORS.read_text())
    roots = sorted({o['leaf'] for o in factor['physical_owners']})
    rng = random.Random(20260923)
    fcounts, icounts = Counter(), Counter()
    for case in range(768 + 100):
        source = ([int(i == case) for i in range(768)] if case < 768 else
                  [rng.randrange(-1, 2) for _ in range(768)])
        columns = [evaluate(source[d::4], roots, fcounts) for d in range(4)]
        plain = mapped_poly(roots, source, False, Counter())
        assert all(plain[d][lam] == (columns[d][lam], 1)
                   for d in range(4) for lam in roots)
        for degree, column in enumerate(columns):
            for lam, value in column.items():
                if case < 768:
                    expected = pow(lam, case // 4, Q) if case % 4 == degree else 0
                else:
                    expected = 0
                    for k in range(Y - 1, -1, -1):
                        expected = (expected * lam + source[4 * k + degree]) % Q
                assert value == expected, (case, degree, lam, value, expected)
        recovered = [reconstruct(column, roots, icounts) for column in columns]
        assert [R * recovered[d][k] % Q for k in range(Y)
                for d in range(4)] == [R * x % Q for x in source]
        # Both crossed pairings use the exact same leaf ABI; no gauge adapter.
        assert recovered_poly(roots, [{lam: (value, 1) for lam, value in col.items()}
                                      for col in columns], False, Counter()) == \
            [R * x % Q for x in source]
        plain_into_twisted = [reconstruct({lam: plain[d][lam][0] for lam in roots},
                                          roots, Counter()) for d in range(4)]
        assert [R * plain_into_twisted[d][k] % Q for k in range(Y)
                for d in range(4)] == [R * x % Q for x in source]

    cases = 868
    assert all(v % cases == 0 for bucket in (fcounts, icounts)
               for v in bucket.values())
    counts = {'twisted_forward': {k: v // cases for k, v in fcounts.items()},
              'twisted_inverse': {k: v // cases for k, v in icounts.items()}}
    result = {
        'evidence_class': 'true_y_variable_twisted_tower_scalar_semantics_not_AVX2_schedule',
        'y_substitution': 'at each y^32-alpha node choose xi^32=alpha; twist to z^32-1; recursively twist negative child',
        'primitive_32_root': ZETA32,
        'all_768_basis_plus_100_random_direct_remainder': True,
        'all_768_basis_plus_100_random_inverse_R_identity': True,
        'four_plain_twisted_forward_inverse_pairings_without_adapter': True,
        'materialized_leaf_gauge': 1,
        'quartic_leaf_order': 'same lambda identities as Official; storage placement can use Official physical map',
        'per_transform_scalar_fixed_multiplications': counts,
        'scope_limit': 'top trinomial and radix3 maps unchanged; radix2 y tower genuinely twisted; no AVX2 range, register, or linked schedule',
        'source_sha256': {str(p.relative_to(ROOT)):
                          hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in [Path(__file__), FACTORS,
                                    ROOT/'tools/research_full_twisted_pairings.py']},
    }
    RESULT.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'source_sha256'},
                     indent=2))


if __name__ == '__main__':
    main()
