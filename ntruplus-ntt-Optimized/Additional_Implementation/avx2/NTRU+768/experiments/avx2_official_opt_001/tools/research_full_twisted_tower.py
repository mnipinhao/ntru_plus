#!/usr/bin/env python3
"""Independent scalar factor/CRT oracle for the linked Official 768 tower.

This deliberately does not manufacture an AVX2 candidate.  A different
butterfly orientation is a candidate only after its *whole* gauge, range,
consumer, and register schedule closes.  The linked functions are used to
discover physical ownership; direct polynomial remainder and CRT are the
independent semantic oracles.
"""

import ctypes
import hashlib
import json
import random
import struct
import subprocess
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

from probe_inverse_ct_gauge import Q, R, ROOT

N = 768
Y = 192
SOURCE = ROOT / 'upstream/supercop-avx2'
RESULT = ROOT / 'results/yang-full-twisted-tower-factor-20260923.json'


def aligned_words():
    backing = ctypes.create_string_buffer(2 * N + 31)
    ptr = (ctypes.addressof(backing) + 31) & ~31
    return backing, ptr, (ctypes.c_int16 * N).from_address(ptr)


def linked_functions(temp):
    sources = [SOURCE / name for name in ('ntt.s', 'invntt.s', 'consts.c')]
    so = Path(temp) / 'official-tower.so'
    subprocess.run(['cc', '-shared', '-fPIC', '-mavx2', '-o', str(so),
                    *map(str, sources)], check=True, capture_output=True)
    lib = ctypes.CDLL(str(so))
    forward, inverse = lib.poly_ntt, lib.poly_invntt_scale
    forward.argtypes = inverse.argtypes = [ctypes.c_void_p]
    return forward, inverse, sources


def call_basis(fn, ptr, words, index):
    words[:] = [int(k == index) for k in range(N)]
    fn(ptr)
    return [int(x) % Q for x in words]


def p_of(value):
    return (pow(value, Y, Q) - pow(value, Y // 2, Q) + 1) % Q


def crt_leaf_polynomial(lam):
    """P(y)/((y-lambda)P'(lambda)), coefficients 0..191."""
    p = [0] * (Y + 1)
    p[0], p[Y // 2], p[Y] = 1, Q - 1, 1
    quotient = [0] * Y
    quotient[Y - 1] = p[Y]
    for k in range(Y - 1, 0, -1):
        quotient[k - 1] = (p[k] + lam * quotient[k]) % Q
    assert (p[0] + lam * quotient[0]) % Q == 0
    derivative = (Y * pow(lam, Y - 1, Q) -
                  (Y // 2) * pow(lam, Y // 2 - 1, Q)) % Q
    assert derivative
    inverse = pow(derivative, -1, Q)
    return [x * inverse % Q for x in quotient]


def physical_factor_tree(roots):
    """Count actual field factors, not an assumed table traversal."""
    levels = []
    for power in (96, 32, 16, 8, 4, 2, 1):
        groups = defaultdict(list)
        for lam in roots:
            groups[pow(lam, power, Q)].append(lam)
        expected = Y // power
        assert len(groups) == expected
        assert all(len(members) == power for members in groups.values())
        levels.append({'factor': f'y^{power}-c', 'count': len(groups),
                       'members_per_factor': power,
                       'constants': sorted(groups)})
    # Exact top split: z=y^96, z^2-z+1=(z-a)(z-b).
    top = levels[0]['constants']
    assert len(top) == 2 and (sum(top) % Q, top[0] * top[1] % Q) == (1, 1)
    return levels


def main():
    with tempfile.TemporaryDirectory(prefix='yang-full-tower-') as temp:
        forward, inverse, sources = linked_functions(temp)
        backing, ptr, words = aligned_words()
        first = [call_basis(forward, ptr, words, j) for j in range(8)]
        owners = []
        for physical in range(N):
            degrees = [j for j in range(4) if first[j][physical]]
            assert len(degrees) == 1, (physical, degrees)
            degree = degrees[0]
            scale = first[degree][physical]
            assert scale
            lam = first[degree + 4][physical] * pow(scale, -1, Q) % Q
            assert p_of(lam) == 0, (physical, lam)
            owners.append({'cell': physical, 'leaf': lam, 'degree': degree,
                           'forward_scale': scale})
        leaves = sorted({x['leaf'] for x in owners})
        assert len(leaves) == Y
        assert len(set((x['leaf'], x['degree']) for x in owners)) == N
        field_roots = [x for x in range(Q) if p_of(x) == 0]
        assert leaves == field_roots

        # Independent direct remainders for all 768 coefficient bases.
        forward_digest = hashlib.sha256()
        max_forward_raw = 0
        for index in range(N):
            words[:] = [int(k == index) for k in range(N)]
            forward(ptr)
            actual = [int(x) for x in words]
            max_forward_raw = max(max_forward_raw, *(abs(x) for x in actual))
            degree, exponent = index % 4, index // 4
            for owner, value in zip(owners, actual):
                expected = (owner['forward_scale'] *
                            pow(owner['leaf'], exponent, Q) % Q
                            if owner['degree'] == degree else 0)
                assert value % Q == expected, (index, owner, value, expected)
                forward_digest.update(struct.pack('<H', value % Q))

        # An inverse input unit at one physical cell must reconstruct that
        # quartic's Lagrange polynomial, adjusted for its forward scale.
        crt = {lam: crt_leaf_polynomial(lam) for lam in leaves}
        inverse_digest = hashlib.sha256()
        max_inverse_raw = 0
        for owner in owners:
            cell = owner['cell']
            words[:] = [int(k == cell) for k in range(N)]
            inverse(ptr)
            actual = [int(x) for x in words]
            max_inverse_raw = max(max_inverse_raw, *(abs(x) for x in actual))
            factor = R * pow(owner['forward_scale'], -1, Q) % Q
            for k, value in enumerate(actual):
                expected = (crt[owner['leaf']][k // 4] * factor % Q
                            if k % 4 == owner['degree'] else 0)
                assert value % Q == expected, (cell, k, value, expected)
                inverse_digest.update(struct.pack('<H', value % Q))

        rng = random.Random(20260923)
        for _ in range(100):
            original = [rng.randrange(-1, 2) for _ in range(N)]
            words[:] = original
            forward(ptr)
            inverse(ptr)
            assert all(value % Q == R * source % Q
                       for value, source in zip(words, original))

    per_leaf = defaultdict(list)
    for owner in owners:
        per_leaf[owner['leaf']].append(owner)
    scalar_leaf_gauges = sum(len({o['forward_scale'] for o in group}) == 1
                             for group in per_leaf.values())
    result = {
        'evidence_class': 'linked_physical_ownership_plus_independent_factor_and_CRT_oracles',
        'q': Q, 'R_mod_q': R, 'ring_in_y': 'y^192-y^96+1',
        'top_split_y96_constants': physical_factor_tree(leaves)[0]['constants'],
        'factor_tree': physical_factor_tree(leaves),
        'physical_owners': owners,
        'forward_scales': dict(Counter(x['forward_scale'] for x in owners)),
        'scalar_leaf_gauges': scalar_leaf_gauges,
        'forward_all_768_bases_direct_remainder': True,
        'inverse_all_768_physical_bases_direct_CRT': True,
        'inverse_after_forward_100_small_random_R_identity': True,
        'forward_basis_mod_q_sha256': forward_digest.hexdigest(),
        'inverse_basis_mod_q_sha256': inverse_digest.hexdigest(),
        'max_forward_impulse_raw_abs': max_forward_raw,
        'max_inverse_impulse_raw_abs': max_inverse_raw,
        'source_sha256': {str(p.relative_to(ROOT)):
                          hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sources + [Path(__file__)]},
    }
    RESULT.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items()
                      if k not in ('physical_owners', 'factor_tree', 'source_sha256')},
                     indent=2))


if __name__ == '__main__':
    main()
