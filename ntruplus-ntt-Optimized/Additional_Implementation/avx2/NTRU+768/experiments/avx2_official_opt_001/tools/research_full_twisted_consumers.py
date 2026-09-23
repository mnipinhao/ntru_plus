#!/usr/bin/env python3
"""Scalar per-leaf consumer contract of the explicit full-tower GS gauge."""

import hashlib
import json
import random
from pathlib import Path

from probe_inverse_ct_gauge import Q, ROOT

PAIRINGS = ROOT / 'results/yang-full-twisted-tower-pairings-20260923.json'
RESULT = ROOT / 'results/yang-full-twisted-tower-consumers-20260923.json'


def quartic_mul(a, b, lam):
    out = [0] * 4
    for i in range(4):
        for j in range(4):
            out[(i + j) % 4] += a[i] * b[j] * (lam if i + j >= 4 else 1)
    return [x % Q for x in out]


def corrected_raw_product(raw_a, raw_b, ga, gb, gc, lam):
    correction = gc * pow(ga * gb % Q, -1, Q) % Q
    return [correction * x % Q for x in quartic_mul(raw_a, raw_b, lam)]


def main():
    pairs = json.loads(PAIRINGS.read_text())
    gauges = {x['lambda']: x['gauge'] for x in pairs['leaf_gauges']}
    assert len(gauges) == 192
    rng = random.Random(20260923)
    for lam, g in gauges.items():
        invg = pow(g, -1, Q)
        for _ in range(8):
            a = [rng.randrange(Q) for _ in range(4)]
            b = [rng.randrange(Q) for _ in range(4)]
            wanted = quartic_mul(a, b, lam)
            # Decap BaseMulScale: two plain operands, output twisted.
            assert corrected_raw_product(a, b, 1, 1, g, lam) == \
                [g * x % Q for x in wanted]
            # Recovery: twisted message and plain hinv, output plain.
            twisted_a = [g * x % Q for x in a]
            assert corrected_raw_product(twisted_a, b, g, 1, 1, lam) == wanted
            # Encap: h plain, r twisted, output twisted; m twisted can add.
            twisted_b = [g * x % Q for x in b]
            assert corrected_raw_product(a, twisted_b, 1, g, g, lam) == \
                [g * x % Q for x in wanted]
            assert [(x + y) % Q for x, y in
                    zip(quartic_mul(a, twisted_b, lam), twisted_a)] == \
                [g * (x + y) % Q for x, y in zip(wanted, a)]
            # BaseInv is a reciprocal per-leaf gauge (modulo its existing
            # Montgomery finalizer); nonzero testing is unchanged by g != 0.
            scalar = rng.randrange(1, Q)
            assert (g * scalar) * (invg * pow(scalar, -1, Q)) % Q == 1
            assert all((invg * x) % Q == y for x, y in
                       zip(twisted_a, a))

    count = sum(g != 1 for g in gauges.values())
    result = {
        'evidence_class': 'modular_scalar_leaf_gauge_consumer_contract_not_linked_or_range',
        'semantic_definition': 'raw_stored=G_leaf*semantic_quartic; Montgomery exponent remains a separate contract',
        'nonidentity_leaves': count,
        'nonidentity_coefficients_per_full_poly': 4 * count,
        'cases': 192 * 8,
        'quartic_identity': 'raw_c=Gc/(Ga*Gb)*Mul(raw_a,raw_b) modulo q for leaf-uniform scalar gauges',
        'decap_edges': [
            {'edge': 'decoded c/f -> BaseMulScale -> candidate inverse',
             'input_gauges': [1, 1], 'output_gauge': 'G',
             'required_factor': 'G', 'status': 'not_implemented_or_absorbed'},
            {'edge': 'inverse -> crepmod3', 'input_gauge': 'G at inverse input',
             'output_gauge': 'coefficient-domain 1',
             'required_factor': 'inverse paired with G; no direct codec change if exact'},
            {'edge': 'message Forward -> recovery BaseMul with plain hinv -> hash bytes',
             'input_gauges': ['G', 1], 'output_gauge': 1,
             'required_factor': 'G^-1', 'status': 'not_implemented_or_absorbed'},
            {'edge': 'regenerated r Forward -> wire equality bytes',
             'input_gauge': 'G', 'output_gauge': 1,
             'required_factor': 'G^-1', 'status': 'not_implemented_or_absorbed'},
        ],
        'encap_edges': [
            {'edge': 'plain decoded h * twisted r + twisted m',
             'required_factor': 1},
            {'edge': 'r hash serialization', 'required_factor': 'G^-1'},
            {'edge': 'ciphertext serialization', 'required_factor': 'G^-1'},
        ],
        'keygen_edges': [
            {'edge': 'twisted f/g -> BaseInv',
             'inverse_output_gauge': 'G^-1',
             'required_zero_test_change': False,
             'status': 'scale_and_range_not_proved'},
            {'edge': 'f materialization -> SK wire',
             'required_factor': 'G^-1'},
        ],
        'candidate_decision': 'No promotion: 3 Decap nontrivial gauge edges plus extra paid butterfly multiplications, without i16 range or 16-YMM machine schedule.',
        'source_sha256': {str(p.relative_to(ROOT)):
                          hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in [Path(__file__), PAIRINGS,
                                    ROOT/'upstream/supercop-avx2/kem.c',
                                    ROOT/'upstream/supercop-avx2/basemul.s',
                                    ROOT/'upstream/supercop-avx2/baseinv.s',
                                    ROOT/'upstream/supercop-avx2/pack.s']},
    }
    RESULT.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'source_sha256'},
                     indent=2))


if __name__ == '__main__':
    main()
