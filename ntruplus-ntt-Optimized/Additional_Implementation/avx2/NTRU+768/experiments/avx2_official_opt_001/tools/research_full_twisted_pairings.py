#!/usr/bin/env python3
"""Executable scalar full-factor-tree CT/GS orientation comparison.

The top trinomial split and radix-3 remain exact coefficient-remainder maps.
The five radix-2 layers compare plain CT forward / GS inverse with a
gauge-carrying GS forward / CT inverse.  The latter is a *paid* realization:
high-half preweights are explicit, not assumed free or silently absorbed.
It is a semantic model, not an AVX2 register schedule or a performance claim.
"""

import hashlib
import json
import random
from collections import Counter
from pathlib import Path

from probe_inverse_ct_gauge import Q, R, ROOT

RESULT = ROOT / 'results/yang-full-twisted-tower-pairings-20260923.json'
FACTORS = ROOT / 'results/yang-full-twisted-tower-factor-20260923.json'
Y = 192


def children(roots, n):
    if n == Y:
        exponent = 96
    elif n == 96:
        exponent = 32
    else:
        exponent = n // 2
    grouped = {}
    for lam in roots:
        grouped.setdefault(pow(lam, exponent, Q), []).append(lam)
    expected = 2 if n != 96 else 3
    assert len(grouped) == expected
    assert all(len(v) == exponent for v in grouped.values())
    return sorted(grouped.items())


def invert_matrix(matrix):
    n = len(matrix)
    rows = [[x % Q for x in row] + [int(i == j) for j in range(n)]
            for i, row in enumerate(matrix)]
    for k in range(n):
        pivot = next(i for i in range(k, n) if rows[i][k])
        rows[k], rows[pivot] = rows[pivot], rows[k]
        scale = pow(rows[k][k], -1, Q)
        rows[k] = [x * scale % Q for x in rows[k]]
        for i in range(n):
            if i != k:
                amount = rows[i][k]
                rows[i] = [(a - amount * b) % Q
                           for a, b in zip(rows[i], rows[k])]
    return [row[n:] for row in rows]


INVERSE_CACHE = {}


def forward(poly, roots, gauge, twisted, count):
    n = len(poly)
    assert len(roots) == n
    if n == 1:
        return {roots[0]: (poly[0] % Q, gauge)}
    kids = children(roots, n)
    width = len(kids)
    m = n // width
    parts = [poly[j * m:(j + 1) * m] for j in range(width)]
    result = {}
    if width == 2 and n <= 32:
        a = kids[0][0]
        assert kids[1][0] == (-a) % Q
        for i in range(m):
            low, high = parts[0][i], parts[1][i]
            if twisted:
                # [S,D]=[A+aB, a(A-aB)] where raw parent=[gA,gB].
                weighted = a * high % Q
                parts[0][i] = (low + weighted) % Q
                parts[1][i] = a * (low - weighted) % Q
            else:
                weighted = a * high % Q
                parts[0][i] = (low + weighted) % Q
                parts[1][i] = (low - weighted) % Q
            if a != 1:
                count['radix2_plain_twiddle_scalar' if not twisted
                      else 'radix2_GS_high_preweight_scalar'] += 1
                if twisted:
                    count['radix2_GS_output_twiddle_scalar'] += 1
        for j, (_, leaves) in enumerate(kids):
            child_gauge = gauge * (a if twisted and j else 1) % Q
            result.update(forward(parts[j], leaves, child_gauge, twisted, count))
    else:
        # This includes the exact unequal-root trinomial split and radix-3.
        for (constant, leaves) in kids:
            child = [sum(parts[j][k] * pow(constant, j, Q)
                         for j in range(width)) % Q for k in range(m)]
            result.update(forward(child, leaves, gauge, twisted, count))
    return result


def inverse(values, roots, gauge, twisted, count):
    n = len(roots)
    if n == 1:
        value, actual_gauge = values[roots[0]]
        assert gauge == actual_gauge
        return [value % Q]
    kids = children(roots, n)
    width = len(kids)
    m = n // width
    a = kids[0][0]
    parts = [inverse(values, leaves,
                     gauge * (a if twisted and width == 2 and n <= 32 and j else 1) % Q,
                     twisted, count)
             for j, (_, leaves) in enumerate(kids)]
    if width == 2 and n <= 32:
        half = pow(2, -1, Q)
        ainv = pow(a, -1, Q)
        low, high = [], []
        for u, v in zip(parts[0], parts[1]):
            if twisted:
                # Invert GS using CT-type input twiddle, then undo the
                # high-half gauge needed by the forward GS stage.
                v = v * ainv % Q
                high.append((u - v) * half * ainv % Q)
                if a != 1:
                    count['radix2_CT_input_untwist_scalar'] += 1
                    count['radix2_CT_high_unweight_scalar'] += 1
            else:
                high.append((u - v) * half * ainv % Q)
                if a != 1:
                    count['radix2_GS_inverse_twiddle_scalar'] += 1
            low.append((u + v) * half % Q)
        return low + high
    matrix = [[pow(c, j, Q) for j in range(width)] for c, _ in kids]
    key = tuple(tuple(row) for row in matrix)
    if key not in INVERSE_CACHE:
        INVERSE_CACHE[key] = invert_matrix(matrix)
    inverse_matrix_rows = INVERSE_CACHE[key]
    output = [[sum(inverse_matrix_rows[j][i] * parts[i][k]
                   for i in range(width)) % Q for k in range(m)]
              for j in range(width)]
    return [x for part in output for x in part]


def mapped_poly(all_roots, coefficient, twisted, count):
    # The tower acts on each of the four quartic degree columns identically.
    per_degree = [forward(coefficient[d::4], all_roots, 1, twisted, count)
                  for d in range(4)]
    return per_degree


def recovered_poly(all_roots, mapped, twisted, count):
    per_degree = [inverse(x, all_roots, 1, twisted, count) for x in mapped]
    return [R * per_degree[d][k] % Q for k in range(Y)
            for d in range(4)]


def radix3_first_binary_preweight(all_roots):
    """Cost obstruction for a trivial twiddle-table-only radix-3 absorption.

    Each radix-3 output is a degree-32 polynomial.  Its high 16 coefficients
    need a different first-binary-root preweight for the simple GS butterfly.
    Scaling the whole radix-3 output row changes its constant/A coefficient,
    which is 1 in the existing Vandermonde row.
    """
    result = []
    for top_constant, top_roots in children(all_roots, Y):
        rows = []
        for alpha, radix3_roots in children(top_roots, 96):
            first_binary_a = children(radix3_roots, 32)[0][0]
            rows.append({'radix3_output_constant': alpha,
                         'required_high_half_scale': first_binary_a,
                         'old_A_column_coefficient': 1,
                         'new_A_column_coefficient': first_binary_a})
        assert len({row['required_high_half_scale'] for row in rows}) == 3
        assert all(row['required_high_half_scale'] != 1 for row in rows)
        result.append({'top_constant': top_constant, 'rows': rows})
    return result


def main():
    factor = json.loads(FACTORS.read_text())
    roots = sorted({o['leaf'] for o in factor['physical_owners']})
    rng = random.Random(20260923)
    plain_counts = Counter()
    twisted_counts = Counter()
    inverse_plain_counts = Counter()
    inverse_twisted_counts = Counter()
    crossed_unadapted_mismatch = Counter()
    gauges = None
    for case in range(768 + 100):
        source = ([int(i == case) for i in range(768)] if case < 768
                  else [rng.randrange(-1, 2) for _ in range(768)])
        plain = mapped_poly(roots, source, False, plain_counts)
        twisted = mapped_poly(roots, source, True, twisted_counts)
        for degree in range(4):
            for lam in roots:
                if case < 768:
                    value = pow(lam, case // 4, Q) if case % 4 == degree else 0
                else:
                    value = 0
                    for k in range(Y - 1, -1, -1):
                        value = (value * lam + source[4 * k + degree]) % Q
                p, pg = plain[degree][lam]
                t, tg = twisted[degree][lam]
                assert pg == 1 and p == value
                assert t == value * tg % Q
        current_gauges = {lam: twisted[0][lam][1] for lam in roots}
        assert all(twisted[d][lam][1] == current_gauges[lam]
                   for d in range(4) for lam in roots)
        if gauges is None:
            gauges = current_gauges
        else:
            assert gauges == current_gauges
        assert recovered_poly(roots, plain, False, inverse_plain_counts) == \
            [R * x % Q for x in source]
        assert recovered_poly(roots, twisted, True, inverse_twisted_counts) == \
            [R * x % Q for x in source]

        # The crossed towers close only after an explicit ABI adapter.
        twisted_to_plain = [{lam: (value * pow(gauge, -1, Q) % Q, 1)
                             for lam, (value, gauge) in degree.items()}
                            for degree in twisted]
        plain_to_twisted = [{lam: (value * gauges[lam] % Q, gauges[lam])
                             for lam, (value, _) in degree.items()}
                            for degree in plain]
        assert recovered_poly(roots, twisted_to_plain, False, Counter()) == \
            [R * x % Q for x in source]
        assert recovered_poly(roots, plain_to_twisted, True, Counter()) == \
            [R * x % Q for x in source]

        twisted_as_plain = [{lam: (value, 1)
                             for lam, (value, _) in degree.items()}
                            for degree in twisted]
        plain_as_twisted = [{lam: (value, gauges[lam])
                             for lam, (value, _) in degree.items()}
                            for degree in plain]
        expected_source = [R * x % Q for x in source]
        crossed_unadapted_mismatch['twisted_forward_plain_inverse'] += \
            recovered_poly(roots, twisted_as_plain, False, Counter()) != expected_source
        crossed_unadapted_mismatch['plain_forward_twisted_inverse'] += \
            recovered_poly(roots, plain_as_twisted, True, Counter()) != expected_source

    # Counts above include every test run; one basis run has representative
    # static work because no data-dependent branch changes the schedule.
    cases = 868
    counts = {name: {k: v // cases for k, v in bucket.items()}
              for name, bucket in [('plain_forward', plain_counts),
                                   ('twisted_forward', twisted_counts),
                                   ('plain_inverse', inverse_plain_counts),
                                   ('twisted_inverse', inverse_twisted_counts)]}
    assert all(v % cases == 0 for bucket in
               (plain_counts, twisted_counts, inverse_plain_counts,
                inverse_twisted_counts) for v in bucket.values())
    nonidentity = sum(g != 1 for g in gauges.values())
    assert all(crossed_unadapted_mismatch.values())
    result = {
        'evidence_class': 'executable_scalar_full_factor_tower_orientation_model_not_AVX2_schedule',
        'radix3_and_trinomial': 'same exact remainder maps in both variants',
        'radix2_plain': 'CT forward; GS inverse with fixed normalization',
        'radix2_twisted': 'GS forward with explicit high preweight; CT-type inverse with explicit input untwist and high unweight',
        'all_768_basis_and_100_random_cases': True,
        'plain_forward_plain_inverse_R_identity': True,
        'twisted_forward_twisted_inverse_R_identity': True,
        'cross_pairs_require_explicit_leaf_gauge_adapter': True,
        'cross_pairs_unadapted_mismatch_cases': dict(crossed_unadapted_mismatch),
        'nonidentity_leaf_gauges': nonidentity,
        'quartic_uniform_leaf_gauges': 192,
        'leaf_gauges': [{'lambda': lam, 'gauge': gauges[lam]} for lam in roots],
        'per_transform_scalar_multiply_ledger': counts,
        'gauge_adapter_nonidentity_scalar_coefficients': 4 * nonidentity,
        'radix3_high_half_preweight_obstruction':
            radix3_first_binary_preweight(roots),
        'limitation': 'preweights and unweights are explicitly paid; no radix3 co-design, i16 range proof, 16-YMM schedule, or linked ASM established',
        'source_sha256': {str(p.relative_to(ROOT)):
                          hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in [Path(__file__), FACTORS,
                                    ROOT/'upstream/supercop-avx2/ntt.s',
                                    ROOT/'upstream/supercop-avx2/invntt.s']},
    }
    RESULT.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items()
                      if k not in ('leaf_gauges', 'source_sha256')}, indent=2))


if __name__ == '__main__':
    main()
