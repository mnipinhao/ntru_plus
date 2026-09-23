#!/usr/bin/env python3
"""Select uniform CT half stages with closed BaseMulScale leaf intervals.

The selection is an interval schedule screen, not a linked AVX2 realization.
"""

import hashlib
import json
from itertools import combinations
from pathlib import Path

from probe_inverse_ct_gauge import Q, ROOT
from prove_inverse_ct_range import mont_bound
from research_full_twisted_pairings import children
from research_true_twist_repair_v2 import INPUT, FACTORS, TOWER, verified
from research_yang_true_twist import ZETA32

RESULT = ROOT / 'results/yang-true-y-twist-half-stage-search-20260923.json'
STAGES = (2, 4, 8, 16, 32)
R = (1 << 16) % Q
PLAIN_SEMANTIC_FINAL = R * pow(192, -1, Q) % Q


def screen(n, xi, zeta, entry, halves, failures, maximum):
    if n == 1:
        return [entry[xi]]
    half = n // 2
    upper = screen(half, xi, zeta * zeta % Q, entry, halves,
                   failures, maximum)
    lower = screen(half, xi * zeta % Q, zeta * zeta % Q,
                   entry, halves, failures, maximum)
    first, second = [], []
    for k, (a, b) in enumerate(zip(upper, lower)):
        twiddle = pow(zeta, -k, Q)
        if b > 32767:
            failures.append({'stage': n, 'reason': 'Montgomery input',
                             'value': b, 'position': k})
        product = b if twiddle == 1 else mont_bound(b, twiddle)
        if n in halves:
            # Signed biased vpavgw computes ceil((a±product)/2) with no
            # overflow. The shared odd-parity correction is at most +1728.
            output = max(a, product) + 1728
        else:
            output = a + product
        if output > 32767:
            failures.append({'stage': n, 'reason': 'output i16',
                             'value': output, 'position': k,
                             'identity_twiddle': twiddle == 1})
        maximum[n] = max(maximum[n], output)
        first.append(output)
        second.append(output)
    return first + second


def main():
    closure, factor, tower = map(verified, (INPUT, FACTORS, TOWER))
    assert tower['materialized_leaf_gauge'] == 1
    bounds = closure['BaseMulScale']['output_lane_bounds']
    owner = {(row['leaf'], row['degree']): row['cell']
             for row in factor['physical_owners']}
    assert len(owner) == len(bounds) == 768
    roots = sorted({leaf for leaf, _ in owner})
    cohorts = [group for _, top in children(roots, 192)
               for _, group in children(top, 96)]
    choices = []
    for count in range(6):
        for halves in combinations(STAGES, count):
            failures = []
            maximum = {n: 0 for n in STAGES}
            for group in cohorts:
                xi = min(group)
                for degree in range(4):
                    entry = {}
                    for leaf in group:
                        lo, hi = bounds[owner[leaf, degree]]
                        entry[leaf] = max(abs(lo), abs(hi))
                    screen(32, xi, ZETA32, entry, halves, failures, maximum)
            choice = {'half_stages': list(halves), 'safe': not failures,
                      'first_failure': failures[0] if failures else None,
                      'max_abs_by_stage': {str(k): v for k, v in maximum.items()},
                      'deferred_divisor': 2 ** (5 - count),
                      'algebraic_final_scale_semantic':
                      PLAIN_SEMANTIC_FINAL * (2 ** count) % Q,
                      'algebraic_final_scale_montgomery_word':
                      (PLAIN_SEMANTIC_FINAL * (2 ** count) * R) % Q,
                      'scalar_half_butterflies': 6 * 4 * 16 * count,
                      'ideal_16_lane_groups': 6 * 4 * count}
            choices.append(choice)
    safe = [choice for choice in choices if choice['safe']]
    minimum = min(len(choice['half_stages']) for choice in safe)
    minimum_choices = [choice for choice in safe
                       if len(choice['half_stages']) == minimum]
    result = {
        'evidence_class': 'per_cell_interval_stage_selection_not_full_AVX2_allocation',
        'choices': choices,
        'safe_count': len(safe),
        'minimum_halved_stages': minimum,
        'minimum_choices': minimum_choices,
        'cost_scope': 'ideal vector groups ignore stage routing, twiddle loads, sign-bias constants, tail and register pressure',
        'scale_scope': 'algebraic replacement for the old R/192 final factor only; full radix3/trinomial and machine constant regeneration not done',
        'source_sha256': {str(path.relative_to(ROOT)):
                          hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in (Path(__file__), INPUT, FACTORS, TOWER)},
    }
    RESULT.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items()
                      if key != 'choices'}, indent=2))


if __name__ == '__main__':
    main()
