#!/usr/bin/env python3
"""Exact quartic consumer law for any diagonal materialized NTT gauge.

The proof is independent of whether a proposed Forward/inverse tower can
produce the gauge. It is a contract needed before such a tower reaches KEM.
"""

import hashlib
import json
import random
import re
from collections import Counter
from pathlib import Path

from probe_inverse_ct_gauge import Q, RINV, ROOT


def multiply(a, b, lam):
    return [sum(a[i]*b[k]*(lam if i+k>=4 else 1)
                for i in range(4) for k in range(4)
                if (i+k)%4 == degree) % Q for degree in range(4)]


def stored_product(a, b, ga, gb, gc, lam):
    result=[0]*4
    for i in range(4):
        for k in range(4):
            o=(i+k)%4
            coeff=ga[i]*gb[k]*pow(gc[o],-1,Q)%Q
            if i+k>=4:coeff=coeff*lam%Q
            result[o]=(result[o]+coeff*a[i]*b[k])%Q
    return result


def main():
    text=(ROOT/'upstream/supercop-avx2/consts.c').read_text()
    raw=re.search(r'const int16_t zetas\[816\].*?=\s*\{(.*?)\};',text,re.S)
    assert raw
    zetas=[int(x)%Q for x in re.findall(r'-?\d+',raw[1])]
    assert len(zetas)==816
    rng=random.Random(20260923)
    checks=0
    scalar_counts=Counter()
    degree_counts=Counter()
    witness=None
    for tile in range(12):
        for lane in range(16):
            lam=zetas[624+32*(tile//2)+16+lane]*RINV%Q
            if tile%2:lam=(-lam)%Q
            for trial in range(8):
                a=[rng.randrange(Q) for _ in range(4)]
                b=[rng.randrange(Q) for _ in range(4)]
                if trial == 0:
                    ga=gb=gc=[2]*4
                else:
                    ga=[rng.randrange(1,Q) for _ in range(4)]
                    gb=[rng.randrange(1,Q) for _ in range(4)]
                    gc=[rng.randrange(1,Q) for _ in range(4)]
                actual=multiply([x*y%Q for x,y in zip(a,ga)],
                                [x*y%Q for x,y in zip(b,gb)],lam)
                expected=[x*pow(g,-1,Q)%Q for x,g in zip(actual,gc)]
                assert stored_product(a,b,ga,gb,gc,lam)==expected
                if trial==0:
                    # Uniform g across one quartic leaves a single g factor
                    # on every product, suitable for one final correction.
                    coefficients={ga[i]*gb[k]*pow(gc[(i+k)%4],-1,Q)%Q
                                  for i in range(4) for k in range(4)}
                    scalar_counts[len(coefficients)]+=1
                    assert coefficients=={2}
                else:
                    coefficients={ga[i]*gb[k]*pow(gc[(i+k)%4],-1,Q)%Q
                                  for i in range(4) for k in range(4)}
                    degree_counts[len(coefficients)]+=1
                    if witness is None and len(coefficients)>1:
                        witness={'gauge_a':ga,'gauge_b':gb,'gauge_c':gc,
                                 'distinct_pre_lambda_product_coefficients':len(coefficients),
                                 'lambda':lam}
                checks+=1
    result={'evidence_class':'exact_modular_consumer_contract_not_a_tower_candidate',
            'identity':'stored_c[o] = sum_{i+k mod 4=o} stored_a[i]*stored_b[k]*Ga[i]*Gb[k]/Gc[o]*lambda^(i+k>=4)',
            'montgomery_exponent_note':'real AVX2 BaseMul also has R^-1; the unchanged finalizer/domain must be included in any ASM',
            'actual_official_quartic_factors_checked':192,
            'random_cases_checked':checks,
            'uniform_gauge_coefficient_count':dict(scalar_counts),
            'arbitrary_degree_gauge_coefficient_count':dict(degree_counts),
            'example_where_lambda_change_alone_is_insufficient':witness,
            'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                for p in [Path(__file__),ROOT/'upstream/supercop-avx2/consts.c',
                          ROOT/'upstream/supercop-avx2/basemul.s']}}
    (ROOT/'results/yang-gauge-consumer-contract-20260923.json').write_text(
        json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='source_sha256'},indent=2))


if __name__=='__main__':main()
