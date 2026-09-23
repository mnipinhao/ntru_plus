#!/usr/bin/env python3
"""Screen exact true-y-twist CT leaf lanes using the closed BaseMulScale proof.

This models the no-repair radix-2 tree. It does not assert reachable overflow,
allocate AVX2 registers, or prove the later y32/radix-3/trinomial schedule.
"""

import hashlib
import json
from pathlib import Path

from probe_inverse_ct_gauge import Q, ROOT
from prove_inverse_ct_range import barrett_bound, mont_bound
from research_full_twisted_pairings import children
from research_yang_true_twist import ZETA32

INPUT = ROOT / 'results/yang-closure-schedule-20260923.json'
FACTORS = ROOT / 'results/yang-full-twisted-tower-factor-20260923.json'
TOWER = ROOT / 'results/yang-true-y-twist-pairings-20260923.json'
RESULT = ROOT / 'results/yang-true-y-twist-repair-v2-20260923.json'


def verified(path):
    data = json.loads(path.read_text())
    for name, digest in data['source_sha256'].items():
        actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        assert actual == digest, ('stale proof source', name)
    return data


def screen(n, xi, zeta, entry, events, cohort, degree):
    if n == 1:
        return [entry[xi]]
    half = n // 2
    upper = screen(half, xi, zeta * zeta % Q, entry, events, cohort, degree)
    lower = screen(half, xi * zeta % Q, zeta * zeta % Q,
                   entry, events, cohort, degree)
    first, second = [], []
    for k, (a, b) in enumerate(zip(upper, lower)):
        constant = pow(zeta, -k, Q)
        product = b if constant == 1 else mont_bound(b, constant)
        output = a + product
        events.append({'cohort': cohort, 'degree': degree, 'node_root': xi,
                       'node_size': n, 'position': k,
                       'input_a_bound': a, 'input_b_bound': b,
                       'twiddle': constant, 'product_bound': product,
                       'pre_add_bound': output,
                       'existing_multiply_before_add': constant != 1,
                       'i16_proved': output <= 32767})
        first.append(output)
        second.append(output)
    return first + second


def main():
    closure, factors, tower = map(verified, (INPUT, FACTORS, TOWER))
    assert closure['BaseMulScale']['input'] == [0, Q - 1]
    assert closure['BaseMulScale']['raw_machine_cases'] == 1003
    assert tower['materialized_leaf_gauge'] == 1
    bounds = closure['BaseMulScale']['output_lane_bounds']
    owners = factors['physical_owners']
    assert len(bounds) == len(owners) == 768
    by_owner = {}
    for owner in owners:
        key = (owner['leaf'], owner['degree'])
        assert key not in by_owner and owner['forward_scale'] == 1
        lo, hi = bounds[owner['cell']]
        by_owner[key] = max(abs(lo), abs(hi))
    assert len(by_owner) == 768
    roots = sorted({leaf for leaf, _ in by_owner})
    cohorts = [group for _, top in children(roots, 192)
               for _, group in children(top, 96)]
    assert len(cohorts) == 6 and all(len(group) == 32 for group in cohorts)
    events = []
    for cohort, group in enumerate(cohorts):
        xi = min(group)
        assert {xi * pow(ZETA32, k, Q) % Q for k in range(32)} == set(group)
        for degree in range(4):
            entry = {leaf: by_owner[leaf, degree] for leaf in group}
            screen(32, xi, ZETA32, entry, events, cohort, degree)
    assert len(events) == 6 * 4 * (32 * 5 // 2)
    failures = [event for event in events if not event['i16_proved']]
    assert failures
    first_by_degree = {str(degree): next((event for event in events
                                          if event['degree'] == degree and
                                          not event['i16_proved']), None)
                       for degree in range(4)}
    first_identity = next((event for event in failures
                           if not event['existing_multiply_before_add']), None)
    first_per_group = [next(event for event in events
                            if event['cohort'] == cohort and
                            event['degree'] == degree and not event['i16_proved'])
                       for cohort in range(6) for degree in range(4)]
    assert len(first_per_group) == 24
    result = {
        'evidence_class': 'closed_source_interval_no_repair_screen_not_linked_ASM',
        'input_domain': closure['BaseMulScale']['input'],
        'BaseMulScale_output_abs_bound': closure['BaseMulScale']['maximum_abs'],
        'halving': 'deferred_32x_scale_must_be_closed_at_tail',
        'first_unproved_operation': failures[0],
        'first_unproved_identity_path': first_identity,
        'first_unproved_by_degree': first_by_degree,
        'first_unproved_per_cohort_degree': first_per_group,
        'all_24_first_failures_have_existing_multiply':
            all(event['existing_multiply_before_add'] for event in first_per_group),
        'first_failure_node_sizes': {
            str(size): sum(event['node_size'] == size for event in first_per_group)
            for size in (2, 4, 8, 16, 32)},
        'unproved_count': len(failures),
        'all_node_events': events,
        'proof_inputs_sha256': {str(path.relative_to(ROOT)):
                                hashlib.sha256(path.read_bytes()).hexdigest()
                                for path in (INPUT, FACTORS, TOWER)},
        'source_sha256': {str(Path(__file__).relative_to(ROOT)):
                          hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
        'scope_limit': 'no actual-overflow witness; no correlated repair, y32 untwist, radix3/trinomial, allocation, or cycle claim',
    }
    if first_identity and max(first_identity['input_a_bound'],
                              first_identity['input_b_bound']) <= 32767:
        a, b = first_identity['input_a_bound'], first_identity['input_b_bound']
        result['first_identity_local_repair_options'] = {
            'barrett_a_only': barrett_bound(a) + b,
            'barrett_b_only': a + barrett_bound(b),
            'barrett_both': barrett_bound(a) + barrett_bound(b),
            'montgomery_one_on_a': mont_bound(a, 1) + b,
            'montgomery_one_on_b': a + mont_bound(b, 1),
            'note': 'local add only; later operations and scale still require proof',
        }
    RESULT.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items()
                      if key != 'all_node_events'}, indent=2))


if __name__ == '__main__':
    main()
