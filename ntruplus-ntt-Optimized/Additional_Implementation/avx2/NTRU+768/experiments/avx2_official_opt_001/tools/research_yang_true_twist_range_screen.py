#!/usr/bin/env python3
"""Conservative first signed-i16 gate for true y-twisted CT inverse.

The only assumption is the already-proved ±7644 BaseMulScale entry envelope.
Halving is deferred, as it is in the production inverse. This screen finds
where a no-repair CT realization loses its i16 proof; it does not assert that
the bound is reachable or that a repaired schedule has been allocated.
"""

import hashlib
import json
from pathlib import Path

from probe_inverse_ct_gauge import Q, ROOT
from prove_inverse_ct_range import barrett_bound, mont_bound, mont_worst_bound
from research_yang_true_twist import ZETA32

RESULT = ROOT / 'results/yang-true-y-twist-range-screen-20260923.json'


def screen(n, zeta, entry, events):
    if n == 1:
        return [entry]
    half = n // 2
    upper = screen(half, zeta * zeta % Q, entry, events)
    lower = screen(half, zeta * zeta % Q, entry, events)
    first, second = [], []
    for k, (a, b) in enumerate(zip(upper, lower)):
        constant = pow(zeta, -k, Q)
        product = b if constant == 1 else mont_bound(b, constant)
        output = a + product
        events.append({'node_size': n, 'position': k,
                       'input_a_bound': a, 'input_b_bound': b,
                       'twiddle': constant, 'product_bound': product,
                       'pre_add_bound': output,
                       'i16_proved': output <= 32767})
        first.append(output)
        second.append(output)
    return first + second


def main():
    events = []
    final = screen(32, ZETA32, 7644, events)
    failures = [e for e in events if not e['i16_proved']]
    assert failures and failures[0]['node_size'] == 8
    # A 30,576-bound output from size 4 is valid input to one Barrett, but
    # its unreduced sum at size 8 is not a valid 16-bit operation.
    witness = failures[0]
    assert witness['input_a_bound'] == witness['input_b_bound'] == 30576
    assert witness['pre_add_bound'] == 61152
    runtime_product = ((Q - 1) * (Q - 1)) // 65536 + 1729
    zeta_product = mont_worst_bound(2 * runtime_product)
    plane_entries = [runtime_product + zeta_product,
                     2 * runtime_product + zeta_product,
                     3 * runtime_product + zeta_product,
                     4 * runtime_product]
    plane_screen = []
    for degree, entry in enumerate(plane_entries):
        specific_events = []
        screen(32, ZETA32, entry, specific_events)
        failed = next((e for e in specific_events if not e['i16_proved']), None)
        plane_screen.append({'degree': degree, 'entry_bound': entry,
                             'first_unproved_operation': failed})
    assert [x['entry_bound'] for x in plane_screen] == [3741, 5652, 7563, 7644]
    assert [x['first_unproved_operation']['node_size'] for x in plane_screen] == [16, 8, 8, 8]
    result = {
        'evidence_class': 'conservative_interval_failure_of_no_repair_true_twisted_inverse_not_actual_overflow',
        'BaseMulScale_input_abs_bound': 7644,
        'halving': 'deferred_32x_scale_must_be_closed_at_tail',
        'first_unproved_operation': witness,
        'first_repair_predecessor_bound': 30576,
        'barrett_of_predecessor_bound': barrett_bound(30576),
        'per_quartic_degree_refinement': plane_screen,
        'preoperation_failures_in_one_32_coefficient_degree_column_without_repairs': len(failures),
        'six_nodes_four_quartic_degrees': 24,
        'scope_limit': 'no lane correlation, no repair schedule, no final y32 untwist/radix3/trinomial range closure; failure of interval proof is not reproducible overflow',
        'source_sha256': {str(p.relative_to(ROOT)):
                          hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in [Path(__file__),
                                    ROOT/'tools/research_yang_true_twist.py',
                                    ROOT/'tools/prove_inverse_ct_range.py']},
    }
    RESULT.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
