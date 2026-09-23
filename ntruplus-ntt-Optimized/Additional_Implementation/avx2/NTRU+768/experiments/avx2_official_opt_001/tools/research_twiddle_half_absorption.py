#!/usr/bin/env python3
"""Mixed-gauge CT schedule: absorb a lower-child half into existing twiddles.

This is an executable scalar/interval schedule screen, not linked inverse ASM.
"""

import hashlib
import json
import random
from collections import Counter
from pathlib import Path

from probe_inverse_ct_gauge import Q, ROOT
from prove_inverse_ct_range import mont_bound
from research_correlated_ct_butterfly import (
    WITNESS_C, WITNESS_F, machine_base_mul_scale, mont_factor, qhalf,
)
from research_full_twisted_pairings import children
from research_yang_true_twist import ZETA32, cyclic_inverse
from research_true_twist_repair_v2 import INPUT, FACTORS, TOWER, verified

RESULT = ROOT / 'results/yang-true-y-twist-twiddle-half-absorption-20260923.json'
INV2 = pow(2, -1, Q)

# U: unchanged scale; H: stored value has one/two factors of 1/2.
# The only q-half butterflies are at H2 and H32.
RECIPE = {
    'U2': ('U1', 'U1', 'plain', 0),
    'U4': ('U2', 'U2', 'plain', 0),
    'H2': ('U1', 'U1', 'half', 1),
    'H4': ('H2', 'U2', 'plain', 1),
    'H8': ('H4', 'U4', 'plain', 1),
    'H16': ('H8', 'H8', 'plain', 1),
    'H32': ('H16', 'H16', 'half', 2),
}


def evaluate(kind, xi, zeta, values, counter, formal=False):
    if kind == 'U1':
        return [values[xi]], 0
    upper_kind, lower_kind, mode, output_scale = RECIPE[kind]
    n = int(kind[1:])
    upper, upper_scale = evaluate(upper_kind, xi, zeta * zeta % Q,
                                  values, counter, formal)
    lower, lower_scale = evaluate(lower_kind, xi * zeta % Q,
                                  zeta * zeta % Q, values, counter, formal)
    assert len(upper) == len(lower) == n // 2
    assert output_scale == upper_scale + (mode == 'half')
    first, second = [], []
    for k, (a, b) in enumerate(zip(upper, lower)):
        original = pow(zeta, -k, Q)
        combined = original * pow(2, lower_scale - upper_scale, Q) % Q
        counter['butterflies'] += 1
        counter[f'{kind}_butterflies'] += 1
        if original == 1 and combined != 1:
            counter['new_identity_multiplications'] += 1
        elif original != 1 and combined != 1 and original != combined:
            counter['existing_twiddles_changed'] += 1
        elif original != 1 and combined == 1:
            counter['existing_twiddles_removed'] += 1
        if combined != 1:
            counter['candidate_fixed_multiplications'] += 1
        if original != 1:
            counter['original_fixed_multiplications'] += 1
        counter['original_constants'].add(original)
        if mode == 'half':
            counter['modular_half_butterflies'] += 1
        counter['candidate_constants'].add(combined)
        if formal:
            t = b if combined == 1 else mont_bound(b, combined)
            bound = max(a, t) + 1728 if mode == 'half' else a + t
            assert bound <= 32767, (kind, xi, k, a, b, combined, bound)
            hi = lo = bound
        else:
            t = b if combined == 1 else mont_factor(b, combined)
            if mode == 'half':
                hi, lo = qhalf(a, t), qhalf(a, -t)
            else:
                hi, lo = a + t, a - t
                assert -32768 <= hi <= 32767, (kind, hi)
                assert -32768 <= lo <= 32767, (kind, lo)
        counter[f'{kind}_max_abs'] = max(counter[f'{kind}_max_abs'],
                                         abs(hi), abs(lo))
        first.append(hi)
        second.append(lo)
    return first + second, output_scale


def main():
    # A fixed lower-operand twiddle alone cannot implement a q-half on both
    # outputs: with b=0, it leaves a unchanged, whereas q-half requires a/2.
    assert 1 != INV2 and (1 + 0) % Q != INV2
    closure, factor, tower = map(verified, (INPUT, FACTORS, TOWER))
    assert tower['materialized_leaf_gauge'] == 1
    bounds = closure['BaseMulScale']['output_lane_bounds']
    owner = {(row['leaf'], row['degree']): row['cell']
             for row in factor['physical_owners']}
    roots = sorted({leaf for leaf, _ in owner})
    cohorts = [group for _, top in children(roots, 192)
               for _, group in children(top, 96)]
    assert len(cohorts) == 6 and len(owner) == len(bounds) == 768
    formal = Counter()
    formal['candidate_constants'] = set()
    formal['original_constants'] = set()
    for group in cohorts:
        for degree in range(4):
            values = {leaf: max(map(abs, bounds[owner[leaf, degree]]))
                      for leaf in group}
            _, scale = evaluate('H32', min(group), ZETA32, values, formal,
                                formal=True)
            assert scale == 2
    rng = random.Random(20260923)
    cases = [([WITNESS_C] * 768, [WITNESS_F] * 768)]
    for _ in range(100):
        cases.append(([rng.randrange(Q) for _ in range(768)],
                      [rng.randrange(Q) for _ in range(768)]))
    actual = Counter()
    actual['candidate_constants'] = set()
    actual['original_constants'] = set()
    for output, _ in machine_base_mul_scale(cases):
        for group in cohorts:
            for degree in range(4):
                values = {leaf: output[owner[leaf, degree]] for leaf in group}
                result, scale = evaluate('H32', min(group), ZETA32,
                                         values, actual)
                reference = cyclic_inverse(values, min(group), 32,
                                           ZETA32, Counter())
                assert scale == 2
                # The independent inverse divides at all five levels. This
                # recipe divides at two levels, so its raw state is 8x that
                # normalized reference (not 1/4 of the reference).
                assert all(got % Q == 8 * want % Q
                           for got, want in zip(result, reference)), (
                               group[0], degree,
                               [(i, got, want) for i, (got, want)
                                in enumerate(zip(result, reference))
                                if got % Q != 8 * want % Q][:4])
    per_block = {key: value // (6 * 4) for key, value in formal.items()
                 if isinstance(value, int) and key.endswith(('butterflies',
                                                                'multiplications',
                                                                'changed',
                                                                'removed'))}
    assert per_block['modular_half_butterflies'] == 20
    assert per_block['new_identity_multiplications'] == 8
    assert per_block['existing_twiddles_changed'] == 16
    result = {
        'evidence_class': 'mixed_gauge_twiddle_absorption_scalar_and_interval_schedule_not_linked_AVX2',
        'identity': '(a/2)+(w*b)/2 = a_half + Mont(b,w/2) (mod q); only the lower-child scale is absorbed',
        'fixed_twiddle_only_no_go': 'with b=0 and a=1, any a+K*b equals 1 but modular half equals inv2; upper operand must already be half-scaled or receive real work',
        'recipe': {key: {'upper': u, 'lower': l, 'merge': mode,
                         'output_half_exponent': scale}
                   for key, (u, l, mode, scale) in RECIPE.items()},
        'formal_checks': 24,
        'actual_BaseMulScale_cases': len(cases),
        'actual_cohort_degree_checks': len(cases) * 24,
        'all_actual_outputs_match_eight_times_normalized_inverse_modq': True,
        'all_actual_and_interval_signed16_operations_safe': True,
        'per_32_leaf_degree_block': per_block,
        'per_full_polynomial': {key: value for key, value in formal.items()
                                if isinstance(value, int) and not key.endswith('_max_abs')},
        'formal_max_abs': {key: value for key, value in formal.items()
                           if key.endswith('_max_abs')},
        'observed_max_abs': {key: value for key, value in actual.items()
                             if key.endswith('_max_abs')},
        'distinct_candidate_constants': len(formal['candidate_constants']),
        'distinct_original_constants': len(formal['original_constants']),
        'new_constant_residues': sorted(formal['candidate_constants'] -
                                        formal['original_constants']),
        'algebraic_final_scale_semantic': (pow(2, 2, Q) *
                                           ((1 << 16) % Q) * pow(192, -1, Q)) % Q,
        'scope_limits': ['no full radix3/trinomial/final scale rewrite',
                         'no 16-YMM def-use or linked constant placement',
                         'new residues do not determine encoded table bytes or load-uops',
                         'no cycle or Decap measurement',
                         'same per-block recipe, not optimized per cell'],
        'source_sha256': {str(path.relative_to(ROOT)):
                          hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in (Path(__file__), INPUT, FACTORS, TOWER,
                                       ROOT / 'tools/research_correlated_ct_butterfly.py',
                                       ROOT / 'upstream/supercop-avx2/basemul.s',
                                       ROOT / 'upstream/supercop-avx2/consts.c')},
    }
    RESULT.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items()
                      if key not in ('recipe', 'source_sha256')}, indent=2))


if __name__ == '__main__':
    main()
